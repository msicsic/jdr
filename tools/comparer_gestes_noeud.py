"""Empreinte ordonnée de chaque successeur produit pendant une recherche réelle.

Le même outil charge le dépôt témoin ou la branche. Les nombres flottants sont
encodés par leurs bits (hex), les suites différées par leur borne et arguments.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch


def relever(p, monde, qui, but, emplois):
    def encoder(x):
        if isinstance(x, p.Etat):
            return ["etat", x.salle, sorted(x.portes), encoder(x.faits), x.allure]
        if isinstance(x, p.SuiteDifferee):
            return ["differe", encoder(x.borne), x.calcul.__name__, encoder(x.arguments),
                    encoder(x.depuis), encoder(x.vises), encoder(x.but)]
        if isinstance(x, float):
            return ["float", x.hex()]
        if isinstance(x, dict):
            return ["dict", sorted([[encoder(k), encoder(v)] for k, v in x.items()], key=repr)]
        if isinstance(x, (set, frozenset)):
            return ["set", sorted([encoder(v) for v in x], key=repr)]
        if isinstance(x, (list, tuple)):
            return [type(x).__name__, [encoder(v) for v in x]]
        if callable(x):
            return ["fonction", x.__name__]
        return x

    suites, empreinte, comptes = p._suites, hashlib.sha256(), [0, 0]
    def observer(v, e, vises, but, conclure=False):
        resultat = suites(v, e, vises, but, conclure)
        donnees = encoder((e, resultat, v._lumiere_lue, v._discretion_lue))
        empreinte.update(json.dumps(donnees, ensure_ascii=False, sort_keys=True).encode())
        comptes[0] += 1
        comptes[1] += len(resultat)
        return resultat
    with patch.object(p, "_suites", observer), patch.object(p, "_MEMOIRE", {}), \
            patch.object(p, "_GRAPHES", {}), patch.object(p, "_IMPOSSIBLES", {}), p.diagnostics() as diagnostics:
        resultat = p.chercher(monde, qui, but, nom=but.__name__, emplois=emplois, motif="faim")
    return {"empreinte": empreinte.hexdigest(), "etats": comptes[0], "successeurs": comptes[1],
            "noeuds": sum(r["noeuds"] for r in diagnostics), "resultat": encoder(resultat)}


def captures(p, racine):
    from donjon.monde import Monde
    resultats = {}
    for scenario, qui, minute in (("mine", "remy", 480), ("auberge", "joss", 480), ("auberge", "joss", 600)):
        fichier = f"{scenario}-1985-{minute}.json.gz"
        for but, emplois in ((p.a_mange, ("manger",)), (p.eclaire, ())):
            monde = Monde(json.loads(gzip.decompress((racine / fichier).read_bytes())))
            resultats[f"{fichier}/{but.__name__}"] = relever(p, monde, qui, but, emplois)
    return resultats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depot", required=True)
    parser.add_argument("--sortie", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.depot).resolve()))
    from donjon import banc_pnj, planification as p
    banc_pnj.ceder()
    donnees = captures(p, Path(__file__).resolve().parents[1] / "tests/data/cout-12h")
    Path(args.sortie).write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf8")
    print({k: {n: x for n, x in v.items() if n != "resultat"} for k, v in donnees.items()})
