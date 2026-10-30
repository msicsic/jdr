"""Reconstituer la capture 308 absente du poste, avant toute correction."""
import copy
import gzip
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj, pnj
from donjon.temps import instant


class CaptureFaite(Exception):
    pass


def main():
    from priorite import ceder
    ceder()
    original = pnj._approcher

    def observer(m, qui, etape, *args, **kwargs):
        if qui == 'marchand' and etape['operation'] == 'servir' and instant(m) >= 856:
            chemin = Path('tests/captures/contact-313-relais-7.json.gz')
            data = copy.deepcopy(m.data)
            chemin.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False).encode('utf8'), mtime=0))
            print(json.dumps({'instant': instant(m), 'qui': qui, 'etape': etape,
                              'approche': original(m, qui, etape, *args, **kwargs)}, ensure_ascii=False))
            raise CaptureFaite
        return original(m, qui, etape, *args, **kwargs)

    try:
        with patch.object(pnj, '_approcher', observer):
            banc_pnj.nuit('relais', 7, .1, 'chambre_cloche', depart='tire')
    except CaptureFaite:
        return
    raise RuntimeError('Capture non rencontrée')


if __name__ == '__main__':
    main()
