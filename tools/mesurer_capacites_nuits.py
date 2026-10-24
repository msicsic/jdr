"""Trois versions ensemble, plafond global de travailleurs et deux nuits par version.

Réutilise exactement les travailleurs d'empreintes_nuits.jouer ; le plafond partagé évite
de lancer six nuits à la fois sur le poste de travail. Les résultats sont sauvés à chaque nuit.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import itertools
import json
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import empreintes_nuits as e
from tools.priorite import ceder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ancien", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--sortie", type=Path, required=True)
    parser.add_argument("--processus", type=int, choices=(3, 4), default=4)
    args = parser.parse_args()
    ceder()
    depots = {"ancien": args.ancien, "base": args.base, "branche": str(Path.cwd())}
    verrous = {v: threading.Semaphore(2) for v in depots}
    sauvegarde = threading.Lock()
    resultats = {v: [] for v in depots}
    args.sortie.mkdir(parents=True, exist_ok=True)
    def jouer(tache):
        cle, version = tache
        with verrous[version]:
            r = e._lancer(str(Path(e.__file__).resolve()), depots[version], cle, 12, False, 0, sys.executable)
        with sauvegarde:
            resultats[version].append(r)
            (args.sortie / f"{version}-12h.json").write_text(
                json.dumps(resultats[version], ensure_ascii=False, indent=1), encoding="utf-8")
            print(version, cle, r.get("secondes", r.get("erreur")), flush=True)
        return r
    cles = itertools.product(("tire", "fixe"), ("mine", "auberge"), (42, 1985))
    taches = [((s, g, d), v) for d, s, g in cles for v in depots]
    with ThreadPoolExecutor(max_workers=args.processus) as pool:
        r = list(pool.map(jouer, taches))
    return int(any("erreur" in x for x in r))


if __name__ == "__main__":
    raise SystemExit(main())
