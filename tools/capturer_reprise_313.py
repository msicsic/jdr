"""Capturer une borne propre d'une version figée, sans modifier le worktree courant."""
import argparse
import copy
import gzip
import json
from pathlib import Path
import sys
from unittest.mock import patch


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--racine', type=Path, required=True)
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--scenario', required=True)
    p.add_argument('--graine', type=int, required=True)
    p.add_argument('--minute', type=int, required=True)
    args = p.parse_args()
    racine = args.racine.resolve()
    sys.path[:0] = [str(racine), str(racine / 'tools')]
    from priorite import ceder
    ceder()
    from donjon import banc_pnj as banc
    import audit_nuits
    original = banc._oisifs_urgents

    class CaptureFaite(Exception):
        pass

    def observer(m):
        if m.data['minutes'] == args.minute:
            args.sortie.write_bytes(gzip.compress(json.dumps(copy.deepcopy(m.data),
                ensure_ascii=False).encode('utf8'), mtime=0))
            print(f'Capture à {args.minute * 600} : {args.sortie}', flush=True)
            raise CaptureFaite
        return original(m)

    try:
        with patch.object(banc, '_oisifs_urgents', observer):
            banc.nuit(args.scenario, args.graine, (args.minute + 5) / 60,
                      audit_nuits.JOUEURS[args.scenario], depart='tire')
    except CaptureFaite:
        return
    raise RuntimeError('Borne non rencontrée')


if __name__ == '__main__':
    main()
