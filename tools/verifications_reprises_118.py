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
    ap.add_argument('--reprendre-empreintes', action='store_true', help='contrôler le rapport déjà produit sans rejouer')
    args = ap.parse_args()
    racine = Path(__file__).resolve().parents[1]
    dossier = racine / 'artifacts/reprises-118'
    import comparer_bancs
    @contextmanager
    def archive(_, reference):
        assert reference.startswith('c3568ae'), reference
        yield dossier / 'base'
    comparer_bancs.worktree_temporaire = archive
    if not args.reprendre_empreintes:
        # stdout du comparateur reste dans le fil du lanceur ; résultat complet
        # et provenance des références sont consignés dans empreintes.json.
        code = comparer_bancs.main(['--reference', 'c3568ae', '--empreintes',
            '--scenarios', 'relais', 'mine', 'auberge', 'crue', '--processus', '2',
            '--sortie', str(dossier / 'empreintes.json')])
        (dossier / 'empreintes.log').write_text(f'code_strict={code}\n', encoding='utf8')
    rapport = json.loads((dossier / 'empreintes.json').read_text(encoding='utf8'))
    ecarts_calcul = []
    avant, apres = rapport['reference']['nuits'], rapport['branche']['nuits']
    assert len(avant) == len(apres) == 16
    for a, b in zip(avant, apres):
        assert (a['scenario'], a['graine']) == (b['scenario'], b['graine'])
        assert not a['plantage'] and not b['plantage']
        assert a['etat_final'] == b['etat_final']
        for k in ('chronique', 'recit', 'souvenirs', 'empreintes'):
            assert a['donnees'].get(k) == b['donnees'].get(k), (a['scenario'], a['graine'], k)
        x, y = a['donnees']['mesures'], b['donnees']['mesures']
        ecarts = {k: [x.get(k), y.get(k)] for k in x.keys() | y.keys() if x.get(k) != y.get(k)}
        # A1/A2 réduisent le travail. Aucune mesure du monde ni signature
        # sauvegardée n'est normalisée ; seule la charge de calcul est séparée.
        assert set(ecarts) <= {'recherches_neuves'}, (a['scenario'], a['graine'], ecarts)
        if ecarts:
            ecarts_calcul.append([a['scenario'], a['graine'], ecarts])
    (dossier / 'empreintes-calcul.json').write_text(json.dumps({
        'nuits_identiques_hors_compteur_calcul': 16, 'ecarts_calcul': ecarts_calcul},
        ensure_ascii=False, indent=2), encoding='utf8')
    print('16 empreintes identiques, seul recherches_neuves séparé :', ecarts_calcul, flush=True)
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
    assert not r['resume']['bornes_verifier'], r['resume']['bornes_verifier']
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
