"""Vérifications finales du lot 118, archives locales et cache commun seulement."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--suite', action='store_true', help='suite complète unique après les contrôles')
    args = ap.parse_args()
    racine = Path(__file__).resolve().parents[1]
    dossier = racine / 'artifacts/reprises-118'
    import comparer_bancs
    @contextmanager
    def archive(_, reference):
        assert reference.startswith('c3568ae'), reference
        yield dossier / 'base'
    comparer_bancs.worktree_temporaire = archive
    with (dossier / 'empreintes.log').open('w', encoding='utf8') as log:
        # stdout du comparateur reste dans le fil du lanceur ; résultat complet
        # et provenance des références sont consignés dans empreintes.json.
        code = comparer_bancs.main(['--reference', 'c3568ae', '--empreintes',
            '--scenarios', 'relais', 'mine', 'auberge', 'crue', '--processus', '2',
            '--sortie', str(dossier / 'empreintes.json')])
        log.write(f'code={code}\n')
    if code:
        raise RuntimeError('empreintes différentes')
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    with (dossier / 'verifier.log').open('w', encoding='utf8') as log:
        subprocess.run([sys.executable, str(racine / 'tools/mesurer_attente_bornee.py'),
            '--cout', '--depot', str(racine), '--scenario', 'auberge', '--depart', 'tire',
            '--heures', '2', '--graine', '42', '--verifier', '--verification', '1',
            '--sortie', str(dossier / 'verifier.json')], cwd=racine, stdout=log,
            stderr=subprocess.STDOUT, check=True, env=env,
            creationflags=0x4000 if os.name == 'nt' else 0)
    r = json.loads((dossier / 'verifier.json').read_text(encoding='utf8'))
    assert all(r['recharge'].values())
    print('VERIFIER + spatial 1 : terminé', flush=True)
    if args.suite:
        with (dossier / 'suite.log').open('w', encoding='utf8') as log:
            subprocess.run([sys.executable, str(racine / 'tools/tests.py'), '--processus', '2',
                '--sortie', str(dossier / 'suite.json')], cwd=racine, stdout=log,
                stderr=subprocess.STDOUT, check=True, env=env,
                creationflags=0x4000 if os.name == 'nt' else 0)
        print('suite complète : terminée', flush=True)
    return 0


if __name__ == '__main__':
    main()
