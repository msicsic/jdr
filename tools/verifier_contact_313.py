"""Validation détachable du lot 313 ; fin.json est toujours écrit en dernier."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))


FICHIERS = [
    'test_contact_position_inconnue.py', 'test_marche.py', 'test_trajets_reels.py',
    'test_trajet_estime.py', 'test_planification.py', 'test_service_rejoindre.py',
    'test_rendre_service.py', 'test_purete_services.py', 'test_contact_sous_but.py',
    'test_comparer_bancs.py', 'test_references.py',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sortie', type=Path, required=True)
    args = parser.parse_args()
    dossier = args.sortie.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = {'ok': False, 'debut': time.time()}

    def lancer(nom, arguments):
        print(f'Démarrage {nom} : {arguments[0]}', flush=True)
        with (dossier / (nom + '.log')).open('w', encoding='utf8') as log:
            code = subprocess.run([sys.executable, *arguments], cwd=RACINE,
                                  stdout=log, stderr=subprocess.STDOUT).returncode
        print(f'Fin {nom} : code {code}', flush=True)
        return code

    try:
        print(f'Démarrage validation 313 : racine={RACINE}, sortie={dossier}', flush=True)
        from priorite import ceder
        ceder()
        bilan['commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RACINE, text=True).strip()
        bilan['tests_code'] = lancer('tests', [
            'tools/tests.py', '--processus', '2', *['tests/' + f for f in FICHIERS],
            '--sortie', str(dossier / 'tests.json')])
        bilan['banc_code'] = lancer('banc', [
            'tools/comparer_bancs.py', '--reference', 'd76f272', '--scenarios', 'relais', 'auberge', 'mine',
            '--heures', '4', '--graines', '1985', '7', '42', '2024', '--processus', '2',
            '--sortie', str(dossier / 'comparaison.json')])
        chemin = dossier / 'comparaison.json'
        if chemin.exists():
            rapport = json.loads(chemin.read_text(encoding='utf8'))
            nuits = []
            for a, b in zip(rapport['reference']['nuits'], rapport['branche']['nuits']):
                ligne = {'scenario': a['scenario'], 'graine': a['graine']}
                for cote, n in [('reference', a), ('branche', b)]:
                    mesures = (n.get('donnees') or {}).get('mesures', {})
                    avis = n.get('avis', {})
                    ligne[cote] = {'plantage': n['plantage'], 'cache': n.get('cache'),
                                   'gestes_refuses_contact': mesures.get('gestes_refuses_contact'),
                                   'approches_impossibles': mesures.get('approches_impossibles'),
                                   'parts_servies': sum('donne une part' in c['texte']
                                                       for c in (n.get('donnees') or {}).get('chronique', [])),
                                   'services': {k: v for k, v in mesures.items() if 'serv' in k or 'portion' in k},
                                   'suspects_219': avis.get('total_non_justifies'), 'boucles': n.get('boucles')}
                nuits.append(ligne)
            (dossier / 'mesures.json').write_text(json.dumps(nuits, ensure_ascii=False, indent=2), encoding='utf8')
        bilan['ok'] = bilan['tests_code'] == 0 and bilan['banc_code'] == 0
    except BaseException:
        bilan['erreur'] = traceback.format_exc()
        print(bilan['erreur'], file=sys.stderr, flush=True)
    finally:
        bilan['fin'] = time.time()
        (dossier / 'fin.json').write_text(json.dumps(bilan, ensure_ascii=False, indent=2), encoding='utf8')
    return int(not bilan['ok'])


if __name__ == '__main__':
    raise SystemExit(main())
