"""Diagnostic P3 sans changer les transitions ni rappeler un but/gestes.

Deux nuits lourdes, une par invocation (à lancer en priorité réduite) :
  python tools/mesurer_salles_interet.py --scenario mine --depart tire --sortie artifacts/p3/mine.json
  python tools/mesurer_salles_interet.py --scenario auberge --depart fixe --sortie artifacts/p3/auberge.json

Les compteurs portent sur les états effectivement retirés de la file, après
élimination des entrées périmées. Les suites sont celles déjà calculées par
le moteur ; un devis différé reste une possibilité, jamais assimilé au vide.
L'instrumentation du source en mémoire ne change aucun fichier du moteur.
Les temps incluent l'observation : ce ne sont pas des mesures de performance.
"""
import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import inspect
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj, planification as p


def resumer(resultat):
    """Séparer les appels logiques des passes (lumière/discrétion)."""
    groupes = defaultdict(lambda: {"appels": 0, "noeuds": 0, "secondes_observees": 0.0,
                                   "issues": Counter(), "premiere_minute": None, "derniere_minute": None})
    for r in resultat["recherches"]:
        if r["minute"] < resultat["depuis"] or r.get("memoire"):
            continue
        groupe = groupes[(r["pnj"], r["but"])]
        groupe["appels"] += 1
        groupe["noeuds"] += r["noeuds"]
        groupe["secondes_observees"] += r["duree"]
        groupe["issues"][r["issue"]] += 1
        groupe["premiere_minute"] = r["minute"] if groupe["premiere_minute"] is None else min(
            groupe["premiere_minute"], r["minute"])
        groupe["derniere_minute"] = max(groupe["derniere_minute"] or 0, r["minute"])
    comptes, bornes = Counter(), Counter()
    for r in resultat["passes"]:
        comptes.update(r["compteurs"])
        if r["borne"]:
            bornes.update(r["compteurs"])
    return {"scenario": resultat["scenario"], "depuis": resultat["depuis"],
            "passes": len(resultat["passes"]), "compteurs": dict(comptes), "passes_bornees": dict(bornes),
            "recherches": [{"pnj": id, "but": but, **g} for (id, but), g in sorted(
                groupes.items(), key=lambda item: -item[1]["noeuds"])]}


@contextmanager
def instrumenter(observer):
    original = p._explorer_etats
    source = inspect.getsource(p._explorer_etats)
    remplacements = [
        ("    ordre = count()", "    _p3_etats, _p3_suites = [], {}\n    ordre = count()"),
        ("        examines += 1", "        examines += 1\n        _p3_etats.append((e, etapes, n))"),
        ("        suites = noeud[3]", "        suites = noeud[3]\n        _p3_suites[e] = (noeud[0], suites)"),
        ("    return trouve, examines, len(vus), plus_profond",
         "    _observer_p3(locals())\n    return trouve, examines, len(vus), plus_profond"),
    ]
    for ancien, nouveau in remplacements:
        if source.count(ancien) != 1:
            raise RuntimeError("Le source du planificateur a changé : " + ancien)
        source = source.replace(ancien, nouveau)
    with patch.object(p, "_observer_p3", observer, create=True):
        try:
            exec(compile(source, "<diagnostic-p3>", "exec"), p.__dict__)
            yield
        finally:
            p._explorer_etats = original


def mesurer(args):
    releves, contexte = [], []
    chercher = p.chercher

    def envelopper(*a, **k):
        contexte.append(k.get("nom", ""))
        try:
            return chercher(*a, **k)
        finally:
            contexte.pop()

    def observer(l):
        v = l["v"]
        if v.monde.data["minutes"] < args.depuis:
            return
        etats, suites = l["_p3_etats"], l["_p3_suites"]
        comptes, operations, salles = Counter(), Counter(), Counter()
        inventaire_initial = l["depart_"].portes
        ancrages = set()
        # Union des salles où une suite non mobile est réellement offerte.
        # C'est une mesure descriptive, pas un filtre de pertinence proposé.
        for e, (but, ss) in suites.items():
            if but or any(isinstance(s, p.SuiteDifferee) or
                          any(x["operation"] != "aller" for x in s[2]) for s in ss):
                ancrages.add(e.salle)
        for e, etapes, n in etats:
            comptes["examines"] += 1
            if e.portes - inventaire_initial:
                comptes["avec_acquisition"] += 1
            if any(k[0] in ("allume", "charge", "ouvert", "verrou", "acquis", "achete", "faute")
                   for k in e.faits):
                comptes["avec_fait_preparatoire"] += 1
            if not etapes or etapes[-1]["operation"] != "aller":
                continue
            comptes["arrivee_aller"] += 1
            salles[e.salle] += 1
            if len(etapes) > 1 and etapes[-2]["operation"] == "aller":
                comptes["allers_consecutifs"] += 1
            if e.salle not in ancrages:
                comptes["aller_salle_sans_action_observee"] += 1
            if e not in suites:
                comptes["aller_non_developpe"] += 1
                continue
            but, ss = suites[e]
            locaux = [s for s in ss if isinstance(s, p.SuiteDifferee) or
                      any(x["operation"] != "aller" for x in s[2])]
            if not but and not locaux:
                comptes["aller_sans_suite_non_mobile"] += 1
            for s in locaux:
                if isinstance(s, p.SuiteDifferee):
                    operations["devis_differe"] += 1
                else:
                    operations.update(x["operation"] for x in s[2] if x["operation"] != "aller")
        releves.append({"minute": v.monde.data["minutes"], "pnj": v.id,
                        "but": contexte[-1] if contexte else "", "decouverte": l["decouvrir"],
                        "borne": l["examines"] >= l["noeuds"], "compteurs": dict(comptes),
                        "salles_arrivee": dict(salles), "salles_avec_action": sorted(ancrages),
                        "operations_apres_aller": dict(operations)})

    debut = time.process_time()
    with patch.object(p, "chercher", envelopper), instrumenter(observer):
        _, mesures, donnees = banc_pnj.nuit(args.scenario, args.graine, args.heures,
                                           "galerie" if args.scenario == "mine" else "dortoir",
                                           diagnostic=True, depart=args.depart)
    resultat = {"scenario": args.scenario, "graine": args.graine, "depart": args.depart,
                "heures": args.heures, "depuis": args.depuis,
                "cpu_instrumente": time.process_time() - debut,
                "mesures": mesures, "recherches": donnees["diagnostic"]["recherches"],
                "passes": releves}
    resultat["resume"] = resumer(resultat)
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{args.scenario}: {len(releves)} passes observées, {resultat['cpu_instrumente']:.1f} s CPU", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("mine", "auberge"), required=True)
    parser.add_argument("--depart", choices=("tire", "fixe"), required=True)
    parser.add_argument("--graine", type=int, default=1985)
    parser.add_argument("--heures", type=int, default=12)
    parser.add_argument("--depuis", type=int, default=480)
    parser.add_argument("--sortie", required=True)
    from tools.priorite import ceder
    ceder()
    mesurer(parser.parse_args())
