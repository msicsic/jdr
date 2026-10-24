"""Rejoue les recherches contre le lot 46, localise la première bifurcation et la complète.

Les cinq méthodes de capacité de la référence sont lues par git, sans modifier de checkout.
Chaque témoin repart à caches vides ; après une bifurcation, on ne compare plus les nuits.
"""
import argparse
import ast
import copy
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import planification as p, pnj
from donjon.monde import Monde
from tools.priorite import ceder

METHODES = ("capacite", "couvre", "capacites_portees", "doublon")


def anciennes(reference="5c2ce81"):
    source = subprocess.run(["git", "show", f"{reference}:donjon/planification.py"],
                            check=True, capture_output=True, encoding="utf-8").stdout
    classe = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == "Vue")
    espace = dict(vars(p))
    for n in classe.body:
        if isinstance(n, ast.FunctionDef) and n.name in METHODES:
            exec(compile(ast.Module(body=[n], type_ignores=[]), "capacites_reference", "exec"), espace)
    return {nom: espace[nom] for nom in METHODES}


def signature(r):
    # Les appelants complètent parfois le plan rendu (dire, refermer) : figer la
    # recherche au retour, avant ces compléments qui ne font pas partie du témoin.
    return None if r is None else [r[0], copy.deepcopy(r[1])]


def verifier(m, minutes, sortie):
    original = p.chercher
    ancien = anciennes()
    resultats = []
    profondeur = 0

    def temoin(a, k, complet=False):
        with ExitStack() as pile:
            pile.enter_context(patch.multiple(p.Vue, **ancien))
            for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                pile.enter_context(patch.object(p, nom, {}))
            with p.diagnostics() as diag:
                r = original(*a, **({**k, "noeuds": p.REFERENCE, "emplois": None} if complet else k))
        return r, diag[-1]

    def observer(*a, **k):
        nonlocal profondeur
        if profondeur:
            return original(*a, **k)
        profondeur += 1
        try:
            with ExitStack() as pile:
                for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                    pile.enter_context(patch.object(p, nom, {}))
                with p.diagnostics() as diag:
                    branche = original(*a, **k)
            # Une reprise peut cacher la première recherche neuve ; tous les résultats
            # restent comparés au même état, sans mémoire du témoin.
            base, db = temoin(a, k)
            different = signature(branche) != signature(base)
            d = {"minute": m.data["minutes"], "pnj": a[1], "but": k.get("nom"),
                 "base": {"resultat": signature(base), "diagnostic": db},
                 "branche": {"resultat": signature(branche), "diagnostic": diag[-1]}}
            reduction = (db["noeuds"] > diag[-1]["noeuds"]
                         and not sortie.with_suffix(".reduction.json").exists())
            if different or db["issue"] == "borne" or minutes == 1 or reduction:
                complete, dc = temoin(a, k, complet=True)
                d["complete"] = {"resultat": signature(complete), "diagnostic": dc}
                d["conforme_complete"] = dc["issue"] != "borne" and signature(branche) == signature(complete)
                if different:
                    d["justifie"] = db["issue"] == "borne" and d["conforme_complete"]
            if reduction:
                sortie.with_suffix(".reduction.json").write_text(json.dumps(m.data, ensure_ascii=False), encoding="utf-8")
            resultats.append(d)
            if different:
                sortie.with_suffix(".monde.json").write_text(json.dumps(m.data, ensure_ascii=False), encoding="utf-8")
                raise Bifurcation()
            return branche
        finally:
            profondeur -= 1

    class Bifurcation(Exception):
        pass

    # On rejoue minute par minute, avec le même avancement du monde que le moteur.
    with patch.object(p, "chercher", observer):
        try:
            for _ in range(minutes):
                m.data["minutes"] += 1
                pnj.avancer(m, 1, [])
        except Bifurcation:
            pass
    sortie.write_text(json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"recherches": len(resultats), "noeuds_base": sum(x["base"]["diagnostic"]["noeuds"] for x in resultats),
                      "noeuds_branche": sum(x["branche"]["diagnostic"]["noeuds"] for x in resultats),
                      "divergences": [x for x in resultats if x["base"]["resultat"] != x["branche"]["resultat"]]},
                     ensure_ascii=False), flush=True)
    return resultats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--minutes", type=int, default=1)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    ceder()
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    data = args.capture.read_bytes()
    m = Monde(json.loads(gzip.decompress(data) if args.capture.suffix == ".gz" else data))
    verifier(m, args.minutes, args.sortie)
