"""Deux versions appariées, au plus deux calculs à priorité réduite.

Créer d'abord l'archive locale 42bb9c0 dans artifacts/recherche-109/ancien.
Les deux phases se lancent successivement : --phase profil puis --phase detail.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--phase', choices=('profil', 'detail'), required=True)
    ap.add_argument('--dossier', type=Path, default=Path('artifacts/recherche-109'))
    args = ap.parse_args()
    racine = Path(__file__).resolve().parents[1]
    dossier = args.dossier.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    for depart in ('tire', 'fixe'):
        jobs = []
        for nom, depot in (('ancien', dossier/'ancien'), ('actuel', racine)):
            prefixe = 'detail-' if args.phase == 'detail' else ''
            fichier = dossier/f'{prefixe}{nom}-{depart}'
            log = fichier.with_suffix('.log').open('w', encoding='utf8')
            cmd = [sys.executable, str(racine/'tools/recherche_tiree_109.py'),
                   '--depot', str(depot), '--depart', depart,
                   '--sortie', str(fichier.with_suffix('.json')), '--'+args.phase]
            p = subprocess.Popen(cmd, cwd=racine, stdout=log, stderr=subprocess.STDOUT,
                creationflags=0x4000 if os.name == 'nt' else 0,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            jobs.append((nom, p, log))
        codes = {}
        for nom, p, log in jobs:
            codes[nom] = p.wait()
            log.close()
        print(depart, codes, flush=True)
        if any(codes.values()):
            raise RuntimeError(codes)


if __name__ == '__main__':
    main()
