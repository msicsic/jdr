"""Vérification détachable du lot 419 ; deux travailleurs réduits au plus."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

from priorite import ceder

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
FICHIERS = [
    'test_recours_prioritaire.py', 'test_propositions_redites.py', 'test_achat_promis_annule.py',
    'test_gardien_detresse.py', 'test_empathie_peur.py', 'test_dynamique_besoins.py',
    'test_signalements.py', 'test_eau.py', 'test_position_hypothese.py', 'test_contact_sous_but.py',
    'test_appels_restes.py', 'test_service_rejoindre.py', 'test_rendre_service.py',
    'test_purete_services.py', 'test_echanges_suite.py', 'test_planification.py',
]


def bilan_banc(rapport):
    """Les appels et retours suspects ne montent dans aucun scénario."""
    resume = {}
    for cote in ('reference', 'branche'):
        for nuit in rapport[cote]['nuits']:
            mesures = (nuit.get('donnees') or {}).get('mesures', {})
            r = resume.setdefault(nuit['scenario'], {}).setdefault(cote, {
                'appels': 0, 'suspects': 0, 'plantages': 0})
            r['appels'] += mesures.get('appels', 0)
            r['suspects'] += (nuit.get('avis') or {}).get('total_non_justifies', 0)
            r['plantages'] += bool(nuit.get('plantage'))
    for r in resume.values():
        r['succes'] = (not r['reference']['plantages'] and not r['branche']['plantages']
                       and all(r['branche'][k] <= r['reference'][k] for k in ('appels', 'suspects')))
    return resume


def attendre_processus(pid):
    """Attente Windows sans sondage ni consommation d'un travailleur."""
    import ctypes
    from ctypes import wintypes
    noyau = ctypes.WinDLL('kernel32', use_last_error=True)
    noyau.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    noyau.OpenProcess.restype = wintypes.HANDLE
    noyau.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    noyau.WaitForSingleObject.restype = wintypes.DWORD
    noyau.CloseHandle.argtypes = (wintypes.HANDLE,)
    processus = noyau.OpenProcess(0x00100000, False, pid)
    if not processus:
        erreur = ctypes.get_last_error()
        if erreur == 87:  # Déjà terminé avant l'ouverture du handle.
            return
        raise ctypes.WinError(erreur)
    try:
        if noyau.WaitForSingleObject(processus, 0xFFFFFFFF) != 0:
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        noyau.CloseHandle(processus)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie', type=Path, required=True)
    parser.add_argument('--reference', required=True)
    parser.add_argument('--attendre-pid', type=int)
    args = parser.parse_args()
    dossier = args.sortie.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = {'debut': time.time(), 'succes': False, 'termine': False}

    def lancer(nom, arguments):
        with (dossier / (nom + '.log')).open('w', encoding='utf8') as log:
            return subprocess.run([sys.executable, *arguments], cwd=RACINE,
                                  stdout=log, stderr=subprocess.STDOUT).returncode

    try:
        ceder()
        if args.attendre_pid:
            (dossier / 'attente.json').write_text(json.dumps({
                'pid': args.attendre_pid, 'depuis': time.time(), 'raison': 'deux travailleurs du lot 416 actifs'}),
                encoding='utf8')
            attendre_processus(args.attendre_pid)
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RACINE, text=True).strip()
        reference = subprocess.check_output(['git', 'rev-parse', args.reference], cwd=RACINE, text=True).strip()
        bilan.update(commit=commit, reference=reference)
        # Le comparateur joue la référence puis la branche ; ses nuits déjà
        # rangées sont réutilisées. Un travailleur de tests et un de banc.
        with ThreadPoolExecutor(max_workers=2) as pool:
            tests = pool.submit(lancer, 'tests-final', [
                'tools/tests.py', '--processus', '1', '--sortie', str(dossier / 'tests-final.json'),
                *['tests/' + f for f in FICHIERS]])
            banc = pool.submit(lancer, 'banc', [
                'tools/comparer_bancs.py', '--reference', reference, '--branche', commit,
                '--scenarios', 'auberge', 'mine', 'crue', '--heures', '4',
                '--graines', '1985', '7', '42', '2024', '--processus', '1',
                '--sortie', str(dossier / 'banc.json')])
            bilan.update(tests_code=tests.result(), banc_code=banc.result())
        if (dossier / 'banc.json').exists():
            rapport = json.loads((dossier / 'banc.json').read_text(encoding='utf8'))
            bilan['banc'] = bilan_banc(rapport)
        # Consolidation par fichier : les contrôles verts de frontière ne
        # sont pas rejoués ; les deux fichiers adaptés ici les remplacent.
        fichiers = {}
        for nom in ('tests-frontiere.json', 'tests-final.json'):
            chemin = dossier / nom
            if chemin.exists():
                for r in json.loads(chemin.read_text(encoding='utf8'))['fichiers']:
                    fichiers[Path(r['fichier']).name] = r
        bilan['tests'] = {'fichiers': len(fichiers), 'tests': sum(r['tests'] for r in fichiers.values()),
                          'rouges': {f: {'failures': r['failures'], 'errors': r['errors']}
                                     for f, r in fichiers.items() if not r['succes']}}
        bilan['succes'] = (bilan['tests_code'] == bilan['banc_code'] == 0
                           and not bilan['tests']['rouges'] and bool(bilan.get('banc'))
                           and all(r['succes'] for r in bilan['banc'].values()))
        bilan['termine'] = True
    except BaseException:
        bilan['erreur'] = traceback.format_exc()
    finally:
        bilan['fin'] = time.time()
        # Le superviseur ne reprend qu'après ce dernier fichier.
        (dossier / 'fin.json').write_text(json.dumps(bilan, ensure_ascii=False, indent=2), encoding='utf8')
    return int(not bilan['succes'])


if __name__ == '__main__':
    raise SystemExit(main())
