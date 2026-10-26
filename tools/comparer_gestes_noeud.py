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
import time
from unittest.mock import patch


def relever(p, monde, qui, but, emplois, mesurer=False):
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
    secondes = 0
    def observer(v, e, vises, but, conclure=False):
        nonlocal secondes
        debut = time.process_time() if mesurer else 0
        resultat = suites(v, e, vises, but, conclure)
        if mesurer:
            secondes += time.process_time() - debut
        donnees = encoder((e, resultat, v._lumiere_lue, v._discretion_lue))
        empreinte.update(json.dumps(donnees, ensure_ascii=False, sort_keys=True).encode())
        comptes[0] += 1
        comptes[1] += len(resultat)
        return resultat
    with patch.object(p, "_suites", observer), patch.object(p, "_MEMOIRE", {}), \
            patch.object(p, "_GRAPHES", {}), patch.object(p, "_IMPOSSIBLES", {}), p.diagnostics() as diagnostics:
        resultat = p.chercher(monde, qui, but, nom=but.__name__, emplois=emplois, motif="faim")
    r = {"empreinte": empreinte.hexdigest(), "etats": comptes[0], "successeurs": comptes[1],
         "noeuds": sum(r["noeuds"] for r in diagnostics), "resultat": encoder(resultat)}
    if mesurer:
        r['secondes_suites'] = secondes
        r['us_par_etat'] = secondes * 1e6 / comptes[0] if comptes[0] else None
    return r


def captures(p, racine, mesurer=False):
    from donjon.monde import Monde
    resultats = {}
    for scenario, qui, minute in (("mine", "remy", 480), ("auberge", "joss", 480), ("auberge", "joss", 600)):
        fichier = f"{scenario}-1985-{minute}.json.gz"
        for but, emplois in ((p.a_mange, ("manger",)), (p.eclaire, ())):
            monde = Monde(json.loads(gzip.decompress((racine / fichier).read_bytes())))
            resultats[f"{fichier}/{but.__name__}"] = relever(p, monde, qui, but, emplois, mesurer)
    return resultats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depot", required=True)
    parser.add_argument("--sortie", required=True)
    parser.add_argument("--mesurer", action='store_true')
    parser.add_argument("--repetitions", type=int, default=1)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.depot).resolve()))
    from donjon import banc_pnj, planification as p
    banc_pnj.ceder()
    if args.repetitions < 1 or args.repetitions != 1 and not args.mesurer:
        parser.error('--repetitions positif ; --mesurer requis pour plusieurs passes')
    passes = [captures(p, Path(__file__).resolve().parents[1] / "tests/data/cout-12h", args.mesurer)
              for _ in range(args.repetitions)]
    donnees = passes[0]
    if args.mesurer:
        for cle, r in donnees.items():
            for passe in passes[1:]:
                assert all(r[k] == passe[cle][k] for k in ('empreinte', 'etats', 'successeurs', 'noeuds', 'resultat'))
            temps = [passe[cle]['secondes_suites'] for passe in passes]
            r['secondes_suites_passes'] = temps
            r['secondes_suites'] = sum(temps) / len(temps)
            r['us_par_etat'] = r['secondes_suites'] * 1e6 / r['etats'] if r['etats'] else None
    Path(args.sortie).write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf8")
    print({k: {n: x for n, x in v.items() if n not in ("resultat", "secondes_suites_passes")}
           for k, v in donnees.items()})
