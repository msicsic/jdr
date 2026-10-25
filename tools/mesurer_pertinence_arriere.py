"""Diagnostic du lot 75, sans mutation des gestes ni appels supplémentaires au but.

python tools/mesurer_pertinence_arriere.py --sortie artifacts/pertinence-75/diagnostic.json
"""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import force, planification as p
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.perception import recharge


def clauses(v, o):
    if v.emplois is None:
        return ["recherche_complete"]
    x = v.objets[o]
    usages = set(x.get("usages", ()))
    return [nom for nom, vrai in (
        ("cle", bool(x.get("ouvre"))),
        ("contenant", x["type"] == "contenant"),
        ("force_verrou_global", v.verrous and bool(usages & set(force.CHOC + force.COUPE))),
        ("repas", "manger" in v.emplois and x["type"] == "nourriture"),
        ("feu", "feu" in v.emplois and bool(usages & {"combustible", "allumage"} or "allume" in x)),
        ("crochetage_global", "crochetage" in p.profil(v.monde, v.id)["capacites"] and "crochetage" in usages),
        ("lumiere", v.emploie_lumiere and ("allume" in x or "allumage" in usages or
            "combustible" in usages and any(recharge(v.objets[s], x) for s in v.rechargeables))),
    ) if vrai]


def charger(capture):
    m = Monde(json.loads(gzip.decompress(Path(capture).read_bytes())))
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "capture.json"
        m.sauver(chemin)
        m = Monde.charger(chemin)
    return m


def observer_recherche(m, qui, rechercher):
    v = p.Vue(m, qui)
    initial = p.depart(m, qui, v).portes
    comptes, acquisitions, raisons = Counter(), Counter(), {}
    faits, operations = Counter(), Counter()
    candidats, phases = {}, set()
    etats = preparatifs = 0
    gestes = p.gestes

    def observer(v, e, *a, **k):
        nonlocal etats, preparatifs
        etats += 1
        nouveaux = e.portes - initial
        preparatifs += bool(nouveaux)
        comptes.update(nouveaux)
        faits.update({c[0] for c in e.faits})
        # Une fois par vue et phase de lumière, sans refaire les gestes.
        phase = (id(v), v.emploie_lumiere)
        if phase not in phases:
            phases.add(phase)
            for o in v.connus:
                if v.utile[o] and v.pertinent(o, frozenset()):
                    candidats[o] = clauses(v, o)
        for o in nouveaux:
            raisons[o] = clauses(v, o)
        for g in gestes(v, e, *a, **k):
            if not isinstance(g, p.SuiteDifferee):
                operations.update(x["operation"] for x in g[2])
                acquisitions.update(g[3].portes - e.portes)
                for o in g[3].portes - e.portes:
                    raisons[o] = clauses(v, o)
            yield g

    with patch.object(p, "gestes", observer), p.diagnostics() as ds:
        r = rechercher()
    return {"pnj": qui, "diagnostic": ds[-1], "resultat": None if r is None else [r[0], r[1]],
            "etats_developpes": etats, "avec_acquisitions": preparatifs,
            "faits_par_etat": dict(faits), "operations_offertes": dict(operations),
            "candidats_pertinents": candidats,
            "objets": {o: {"etats": comptes[o], "acquisitions_offertes": acquisitions[o], "clauses": raisons[o]}
                       for o in sorted(set(comptes) | set(acquisitions))}}


def mesurer(capture, qui, noeuds=p.NOEUDS):
    m = charger(capture)
    return observer_recherche(m, qui, lambda: p.chercher(
        m, qui, p.a_mange, emplois=("manger",), motif="faim", noeuds=noeuds))


def reprendre(capture, pnjs, minutes):
    """Même moteur que le joueur ; chaque appel logique de faim, même mémorisé.

    Les compteurs de gestes ne comprennent que les développements neufs ; les
    diagnostics donnent séparément les reprises et le nombre final de nœuds.
    """
    m = charger(capture)
    rechercher = p.chercher
    recherches = []
    profondeur = 0

    def observer(*a, **k):
        nonlocal profondeur
        exterieur = profondeur == 0
        profondeur += 1
        try:
            if exterieur and a[1] in pnjs and k.get("nom") == "faim":
                r = None
                def calcul():
                    nonlocal r
                    r = rechercher(*a, **k)
                    return r
                recherches.append(observer_recherche(a[0], a[1], calcul))
                return r
            return rechercher(*a, **k)
        finally:
            profondeur -= 1

    debut = m.data["minutes"]
    with p.diagnostics() as diagnostics, \
            patch.object(p, "chercher", observer), patch.object(p, "_MEMOIRE", {}), \
            patch.object(p, "_GRAPHES", {}), patch.object(p, "_IMPOSSIBLES", {}):
        while m.data["minutes"] < debut + minutes:
            moteur = Moteur(m)
            moteur.executer(moteur.preparer(proposition("attendre")))
    # Les diagnostics ciblés ont leur bloc propre : les réunir au relevé général.
    return {"debut": debut, "fin": m.data["minutes"], "recherches_ciblees": recherches,
            "diagnostics": diagnostics + [r["diagnostic"] for r in recherches]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--capture", default="tests/data/cout-12h/auberge-1985-480.json.gz")
    ap.add_argument("--pnjs", nargs="+", default=["joss", "tilo"])
    ap.add_argument("--noeuds", type=int, default=p.NOEUDS)
    ap.add_argument("--minutes", type=int, default=0, help="Reprendre aussi la partie par des attentes du joueur")
    ap.add_argument("--sortie", required=True)
    args = ap.parse_args()
    resultats = {"initial": [mesurer(args.capture, qui, args.noeuds) for qui in args.pnjs]}
    if args.minutes:
        resultats["reprise"] = reprendre(args.capture, args.pnjs, args.minutes)
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultats, ensure_ascii=False, indent=2))
