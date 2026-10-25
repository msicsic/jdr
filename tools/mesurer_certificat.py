"""Diagnostic du lot 66 : le certificat d'absence (``planification._sans_plan``) sur les recherches
neuves d'un PNJ/but, sans changer une décision.

  python tools/mesurer_certificat.py --scenario mine --depart tire --sortie artifacts/certificat/mine.json
  python tools/mesurer_certificat.py --scenario auberge --depart fixe --sortie artifacts/certificat/auberge.json

Pour chaque recherche observée (après --depuis) : son issue, et pour chaque recherche épuisée sans
plan, trois lectures :
- ``moteur`` : l'issue de ``_sans_plan`` quand le moteur l'a tenté (deuxième recherche de suite
  sur les mêmes entrées), avec la cause exacte d'une lacune ;
- ``graphe_des_la_premiere`` : la même preuve si le graphe avait été gardé dès cette recherche ;
- ``complete`` : la preuve si les nœuds manquants avaient été développés (oracle, hors moteur,
  sur un graphe à part ; « indetermine » quand la lumière ou la discrétion seraient découvertes).
Puis la part des recherches neuves qu'un certificat réussi aurait évitées : celles dont une
recherche antérieure de même signature d'absence (``base``, permission de fauter) était prouvée.

Le graphe d'une première recherche est observé sur un dictionnaire à part, comme le moteur le fait
à la deuxième : même chemin de code, mêmes résultats (contrôlé par les mesures de la nuit).
"""
import argparse
from collections import Counter, deque
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj, planification as p


def parcours_cause(v, graphe, depart_, profondeur, faute, tenir, examines=0):
    """``_parcours`` à l'identique, avec la cause d'une lacune."""
    departs = p._departs(v, depart_)
    file, vus, lue = deque((e, 0) for e in departs), set(departs), False
    while file:
        if examines >= p.PREUVE_MAX:
            return False, examines, "borne", lue, None
        e, n = file.popleft()
        examines += 1
        noeud = graphe.get(e)
        if noeud is None:
            return False, examines, "lacune", lue, ("estimation" if e.fait("estimation") else "absent", n)
        if noeud[4] == "but":
            lue = True
            continue
        if noeud[0] and not (tenir and e.salle in v.menacees):
            return False, examines, "but", lue, None
        if n >= profondeur:
            continue
        if noeud[4] == "gestes":
            lue = True
            continue
        if noeud[3] is None:
            return False, examines, "lacune", lue, ("non_developpe", n)
        suites = []
        for s in noeud[3]:
            if isinstance(s, p.SuiteDifferee):
                if s.suites is None:
                    return False, examines, "lacune", lue, ("differee", n)
                suites.extend(s.suites)
            else:
                suites.append(s)
        for fautes, _, _, suivant, *_ in suites:
            if fautes and faute is None or suivant in vus:
                continue
            vus.add(suivant)
            file.append((suivant, n + 1))
    return True, examines, "epuise", lue, None


def sans_plan_cause(v, depart_, but, profondeur, faute, tenir, graphe, voir):
    if voir:
        r = parcours_cause(v, graphe.get("lumiere", {}), depart_, profondeur, faute, tenir)
        return r[0], r[1], r[2], r[4], "lumiere"
    r = parcours_cause(v, graphe.get("sombre", {}), depart_, profondeur, faute, tenir)
    if not r[0] or not r[3]:
        return r[0], r[1], r[2], r[4], "sombre"
    r2 = parcours_cause(v, graphe.get("lumiere", {}), depart_, profondeur, faute, tenir, r[1])
    return r2[0], r2[1], r2[2], r2[4], "lumiere_apres_sombre"


def complete(v, graphe, depart_, but, vises, profondeur, faute, tenir):
    """Oracle : le parcours, les nœuds manquants développés à part (le graphe n'est pas modifié).
    (issue, états examinés, nœuds développés, suites différées développées)."""
    if v._lumiere_lue and not (v.peur or v.eclairer):
        # Le graphe sombre ne se développe plus avec cette vue (elle a découvert la lumière).
        return "indetermine:lumiere_decouverte", 0, 0, 0
    furtif_avant, discretion_avant = v._explore_furtif, v._discretion_lue
    lumiere_avant = v._lumiere_lue
    # Qui emploie la lumière d'office (peur du noir, but d'éclairer) n'a rien à découvrir.
    sombre = not (v.peur or v.eclairer)
    departs = p._departs(v, depart_)
    file, vus = deque((e, 0) for e in departs), set(departs)
    examines = developpes = differees = 0
    try:
        while file:
            if examines >= p.PREUVE_MAX:
                return "borne", examines, developpes, differees
            e, n = file.popleft()
            examines += 1
            if e.fait("estimation"):
                # Une suite terminale estimée : un plan, à ce prix ou à un autre.
                if (e.allure == 15 or e.fait("furtif")) and not (tenir and e.salle in v.menacees):
                    return "but", examines, developpes, differees
                continue
            noeud = graphe.get(e)
            atteint = suites_ = None
            if noeud is not None:
                if noeud[4] and sombre:
                    return "indetermine:lumiere_lue", examines, developpes, differees
                atteint = noeud[0]
                suites_ = noeud[3]
            if atteint is None:
                atteint = but(v, e) and (e.allure == 15 or e.fait("furtif"))
                developpes += 1
            if sombre and v._lumiere_lue != lumiere_avant:
                return "indetermine:lumiere_lue", examines, developpes, differees
            if atteint and not (tenir and e.salle in v.menacees):
                return "but", examines, developpes, differees
            if n >= profondeur:
                continue
            if suites_ is None:
                suites_ = p._suites(v, e, vises, but)
                developpes += 1
                if sombre and v._lumiere_lue != lumiere_avant:
                    return "indetermine:lumiere_lue", examines, developpes, differees
                if v._discretion_lue != discretion_avant and not v._explore_furtif:
                    return "indetermine:discretion", examines, developpes, differees
            suites = []
            for s in suites_:
                if isinstance(s, p.SuiteDifferee):
                    if s.suites is None:
                        gestes_ = s.calcul(v, *s.arguments)
                        differees += 1
                        suites.extend(p._normaliser_suites(v, s.depuis, s.vises, s.but, gestes_)
                                      if s.depuis is not None else [(*g, 0) for g in gestes_])
                    else:
                        suites.extend(s.suites)
                else:
                    suites.append(s)
            for fautes, _, _, suivant, *_ in suites:
                if fautes and faute is None or suivant in vus:
                    continue
                vus.add(suivant)
                file.append((suivant, n + 1))
        return "epuise", examines, developpes, differees
    finally:
        v._explore_furtif, v._discretion_lue, v._lumiere_lue = furtif_avant, discretion_avant, lumiere_avant


@contextmanager
def observer(qui, nom, depuis, releves, oracle=True):
    chercher, explorer, sans_plan = p.chercher, p._explorer, p._sans_plan
    pile = []

    def appeler(monde, id, but, *a, **k):
        cible = not pile and id == qui and k.get("nom") == nom and monde.data["minutes"] >= depuis
        contexte = {"cible": cible}
        pile.append(contexte)
        try:
            resultat = chercher(monde, id, but, *a, **k)
            if cible:
                d = p.DIAGNOSTIC[-1]
                r = {"minute": monde.data["minutes"], "issue": d["issue"], "memoire": d["memoire"],
                     "impossible": d["impossible"], "graphe": d["graphe"], "noeuds": d["noeuds"],
                     "preuve_issue": d["preuve_issue"], **{c: contexte.get(c) for c in (
                         "signature", "voir", "furtif", "lumiere_lue", "premiere", "graphe_des_la_premiere",
                         "complete", "moteur", "cpu_explorer")}}
                releves.append(r)
            return resultat
        finally:
            pile.pop()

    def exploration(v, depart_, but, vises, profondeur, noeuds, faute, tenir=False, graphe=None, **k):
        if not pile or not pile[-1]["cible"] or k:
            return explorer(v, depart_, but, vises, profondeur, noeuds, faute, tenir, graphe, **k)
        c = pile[-1]
        c["voir"] = v.emploie_lumiere
        voir = c["voir"]
        # Avant le lot 66, la première recherche sur des entrées ne gardait aucun nœud ; depuis,
        # le moteur lui passe un graphe de travail : rien à observer à part.
        premiere = graphe is not None and not graphe.get("garder", True)
        c["premiere"] = premiere
        ombre = graphe
        if premiere:
            ombre = {"garder": True, "discretion": graphe.get("discretion")}
        t = time.process_time()
        r = explorer(v, depart_, but, vises, profondeur, noeuds, faute, tenir, ombre)
        c["cpu_explorer"] = time.process_time() - t
        if premiere:
            graphe["discretion"] = ombre["discretion"]
        c["furtif"], c["lumiere_lue"] = v._explore_furtif, v._lumiere_lue
        # La signature d'absence du moteur : ``base`` et la permission de fauter (``chercher``).
        c["signature"] = [hash(p._entrees(v, vises, profondeur, noeuds)), faute is None, v.degat is None,
                          v.desespere]
        if r[0] is None and r[1] < noeuds and ombre is not None:
            prouve, examines, issue, cause, cote = sans_plan_cause(v, p.depart(v.monde, v.id, v), but, profondeur,
                                                                  faute, tenir, ombre, voir)
            c["graphe_des_la_premiere"] = {"prouve": prouve, "examines": examines, "issue": issue,
                                           "cause": cause, "cote": cote}
            if oracle:
                g = ombre.get("lumiere" if voir or v._lumiere_lue else "sombre", {})
                t = time.process_time()
                issue2, ex2, dev, dif = complete(v, g, p.depart(v.monde, v.id, v), but, vises, profondeur,
                                                  faute, tenir)
                c["complete"] = {"issue": issue2, "examines": ex2, "developpes": dev, "differees": dif,
                                 "cpu": time.process_time() - t}
        return r

    def preuve(v, depart_, but, profondeur, faute, tenir, graphe, voir, *a, **k):
        resultat = sans_plan(v, depart_, but, profondeur, faute, tenir, graphe, voir, *a, **k)
        if pile and pile[-1]["cible"]:
            if k.get("completer"):
                # Le certificat complété (lot 66) : son issue telle quelle.
                pile[-1]["moteur"] = {"prouve": resultat[0], "examines": resultat[1], "issue": resultat[2],
                                      "cause": None, "cote": "complete"}
                return resultat
            prouve, examines, issue, cause, cote = sans_plan_cause(v, depart_, but, profondeur, faute, tenir,
                                                                  graphe, voir)
            assert (prouve, examines, issue) == tuple(resultat)
            pile[-1]["moteur"] = {"prouve": prouve, "examines": examines, "issue": issue, "cause": cause,
                                  "cote": cote}
        return resultat

    with patch.object(p, "chercher", appeler), patch.object(p, "_explorer", exploration), \
            patch.object(p, "_sans_plan", preuve):
        yield


def resumer(releves):
    neuves = [r for r in releves if not r["memoire"]]
    epuisees = [r for r in neuves if r["issue"] == "epuise"]
    causes = lambda cle: dict(Counter(
        f'{r[cle]["issue"]}' + (f':{r[cle]["cause"][0]}' if r[cle].get("cause") else "") + f'/{r[cle]["cote"]}'
        for r in epuisees if r.get(cle)))
    # Évitables : une recherche épuisée antérieure de même signature, prouvée par l'oracle.
    prouvees, evitables, evitables_noeuds = set(), 0, 0
    for r in releves:
        sig = json.dumps(r["signature"]) if r["signature"] else None
        if not r["memoire"] and sig in prouvees and r["issue"] == "epuise":
            evitables += 1
            evitables_noeuds += r["noeuds"]
        if r["issue"] == "epuise" and (r.get("complete") or {}).get("issue") == "epuise":
            prouvees.add(sig)
    return {"observees": len(releves), "neuves": len(neuves), "issues": dict(Counter(r["issue"] for r in neuves)),
            "reprises_memoire": sum(r["memoire"] and not r["impossible"] for r in releves),
            "reprises_certificat": sum(bool(r["impossible"]) for r in releves),
            "graphe_repris": sum(bool(r["graphe"]) for r in neuves),
            "noeuds_neuves": sum(r["noeuds"] for r in neuves),
            "moteur": causes("moteur"), "graphe_des_la_premiere": causes("graphe_des_la_premiere"),
            "complete": dict(Counter(r["complete"]["issue"] for r in epuisees if r.get("complete"))),
            "signatures_distinctes": len({json.dumps(r["signature"]) for r in epuisees}),
            "evitables": evitables, "evitables_noeuds": evitables_noeuds,
            "cpu_explorer_neuves": round(sum(r["cpu_explorer"] or 0 for r in neuves), 3),
            "cpu_oracle": round(sum((r.get("complete") or {}).get("cpu", 0) for r in epuisees), 3)}


def mesurer(args):
    releves = []
    qui = args.pnj or ("remy" if args.scenario == "mine" else "joss")
    debut = time.process_time()
    with observer(qui, args.but, args.depuis, releves, oracle=not args.sans_oracle):
        _, mesures, donnees = banc_pnj.nuit(args.scenario, args.graine, args.heures,
                                           "galerie" if args.scenario == "mine" else "dortoir",
                                           diagnostic=True, depart=args.depart)
    resultat = {"scenario": args.scenario, "graine": args.graine, "depart": args.depart, "heures": args.heures,
                "depuis": args.depuis, "pnj": qui, "but": args.but, "cpu": time.process_time() - debut,
                "mesures": mesures, "empreintes": donnees["empreintes"], "releves": releves,
                "resume": resumer(releves)}
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(resultat["resume"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("mine", "auberge", "relais", "crue"), required=True)
    parser.add_argument("--depart", choices=("tire", "fixe"), required=True)
    parser.add_argument("--graine", type=int, default=1985)
    parser.add_argument("--heures", type=float, default=12)
    parser.add_argument("--depuis", type=int, default=480)
    parser.add_argument("--pnj")
    parser.add_argument("--but", default="faim")
    parser.add_argument("--sans-oracle", action="store_true")
    parser.add_argument("--sortie", required=True)
    from tools.priorite import ceder
    ceder()
    mesurer(parser.parse_args())
