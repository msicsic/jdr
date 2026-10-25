"""Diagnostic P3 sans modifier le moteur : auberge 1985 tirée, tranche 8–12 h.

Deux modes séparés : témoin CPU et comptage des expansions/successeurs.
Les points d'observation sont injectés dans une copie en mémoire de la fonction.
"""
import argparse
import copy
from collections import Counter
import inspect
import json
from pathlib import Path
import time

import empreintes_nuits as empreintes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", required=True)
    parser.add_argument("--compter", action="store_true")
    args = parser.parse_args()
    empreintes._preparer(".", False, 0)
    from donjon import banc_pnj, planification as p
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    banc_pnj.ceder()
    pile, lignes, capture = [], [], {}
    chercher, creer, gestes = p.chercher, banc_pnj.creer, p.gestes

    def courant():
        return pile[-1] if pile and pile[-1]["minute"] >= 480 else None

    def structure(v, e, vises):
        # Ne pas préparer les gestes de la recherche avant son test de but :
        # celui-ci peut encore découvrir la lumière et changer la pertinence.
        v = copy.copy(v)
        v._agissables = {}
        objets, _ = v.agissables(vises or {})
        local = any(o not in e.portes and (v.salle(e, o) == e.salle
                    or o in v.portes_de[e.salle]) for o in objets)
        personne = any(v.salle(e, o) == e.salle for o in v.personnes() if o != v.id)
        raisons = []
        if v.peur or v.peurs_sociales or v.prix_gardes or v.eau:
            raisons.append("pression_variable_possible")
        if v.eau_route:
            raisons.append("admissibilite_eau")
        if any(not v.ouvert(e, o) for o in objets if v.objets[o]["type"] == "porte"):
            raisons.append("effets_portes")
        return local or personne, raisons

    def expansion(v, e, vises):
        r = courant()
        if r is not None:
            r["etats"] += 1
            interesse, raisons = structure(v, e, vises)
            if not interesse:
                r["structure_tous_etats"] += 1
                r["retenus_tous_etats"].update(raisons)
                if not raisons:
                    r["candidats_majorants_tous_etats"] += 1

    def suites(suites, atteint, v, e, vises, etapes):
        r = courant()
        if r is None:
            return
        r["classes"] += 1
        autres = any(isinstance(s, p.SuiteDifferee) or any(
            x["operation"] != "aller" for x in s[2]) for s in suites)
        vide = not autres and not atteint
        r["sans_geste_ni_but"] += int(vide)
        if vide:
            arrive_par_aller = bool(etapes and etapes[1] and
                                   etapes[1][-1]["operation"] == "aller")
            r["vides_apres_aller"] += int(arrive_par_aller)
            interesse, raisons = structure(v, e, vises)
            if not interesse:
                r["vides_structurels"] += 1
                r["vides_structurels_apres_aller"] += int(arrive_par_aller)
                # Majorant d'un filtre conservateur sans pression, eau ni
                # effet de porte connue. Les portes inconnues et les gestes
                # portés demanderaient encore de conserver certains candidats.
                r["retenus_preuve"].update(raisons)
                if not raisons:
                    r["candidats_sans_obstacle_preuve"] += 1
        for s in suites:
            if isinstance(s, p.SuiteDifferee):
                r["suites"]["differee"] += 1
            else:
                r["suites"]["+".join(x["operation"] for x in s[2])] += 1

    def observer_gestes(*a, **k):
        g = gestes(*a, **k)
        while True:
            debut = time.process_time()
            try:
                s = next(g)
            except StopIteration:
                return
            r = courant()
            if r is not None:
                famille = "differee" if isinstance(s, p.SuiteDifferee) else "+".join(x["operation"] for x in s[2])
                r["gestes"][famille] += 1
                r["cpu_gestes"][famille] += time.process_time() - debut
            yield s

    if args.compter:
        source = inspect.getsource(p._explorer_etats)
        ancien = "        examines += 1\n"
        assert source.count(ancien) == 1
        source = source.replace(ancien, ancien + "        _p3_expansion(v, e, vises)\n")
        ancien = "        suites = noeud[3]\n"
        assert source.count(ancien) == 1
        source = source.replace(ancien, ancien + "        _p3_suites(suites, noeud[0], v, e, vises, etapes)\n")
        p.__dict__.update(_p3_expansion=expansion, _p3_suites=suites)
        exec(compile(source, "<diagnostic-p3>", "exec"), p.__dict__)
        p.gestes = observer_gestes

    def observer(monde, qui, *a, **k):
        r = {"minute": monde.data["minutes"], "pnj": qui, "but": k.get("nom", ""),
             "etats": 0, "classes": 0, "sans_geste_ni_but": 0,
             "vides_apres_aller": 0, "vides_structurels": 0, "vides_structurels_apres_aller": 0,
             "candidats_sans_obstacle_preuve": 0, "retenus_preuve": Counter(),
             "structure_tous_etats": 0, "candidats_majorants_tous_etats": 0,
             "retenus_tous_etats": Counter(),
             "suites": Counter(), "gestes": Counter(), "cpu_gestes": Counter()}
        pile.append(r)
        avant = len(p.DIAGNOSTIC or [])
        debut = time.process_time()
        try:
            resultat = chercher(monde, qui, *a, **k)
        finally:
            r["cpu"] = time.process_time() - debut
            pile.pop()
        if not pile and r["minute"] >= 480:
            if p.DIAGNOSTIC is not None and len(p.DIAGNOSTIC) > avant:
                r["diagnostic"] = p.DIAGNOSTIC[-1]
            lignes.append(r)
        return resultat

    def creer_observe(*a, **k):
        capture["monde"] = creer(*a, **k)
        return capture["monde"]

    p.chercher, banc_pnj.creer = observer, creer_observe
    resume = empreintes.nuit(".", "auberge", 1985, 12, "tire")
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    monde = capture["monde"]
    monde.sauver(sortie.with_suffix(".monde.json"))
    recharge = Monde.charger(sortie.with_suffix(".monde.json"))
    controle = {"monde": monde.data == recharge.data,
                "regarder": regarder(monde) == regarder(recharge),
                "scene": scene_percue(monde) == scene_percue(recharge)}
    assert all(controle.values()), controle
    sortie.write_text(json.dumps({"compter": args.compter, "resume": resume,
                                 "recharge": controle, "recherches": lignes},
                                ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({"sortie": str(sortie), "secondes": resume["secondes"],
                      "noeuds": resume["noeuds"], "recharge": controle}), flush=True)


if __name__ == "__main__":
    main()
