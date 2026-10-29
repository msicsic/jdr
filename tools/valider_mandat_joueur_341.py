"""Lot 341 : vérification séquentielle détachée, deux travailleurs réduits au plus."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from priorite import ceder

TESTS = ('mandat_joueur', 'agendas_socle', 'agendas_mandat', 'agendas_jugement_mandat',
         'agendas_compte_rendu', 'agendas_reaffecter', 'agendas_ascendant_evolue', 'agendas_evaluation',
         'agendas_devis_observateur', 'paroles', 'contenus_parole', 'parole_commune',
         'emissions_parole', 'comptes_paroles', 'comptes_issue', 'comprehension', 'noms')


def ecrire(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding='utf-8')


def empreintes():
    fichiers = [*sorted((RACINE / 'donjon').glob('*.py')), Path(__file__),
                RACINE / 'tests/data/bancs/mandat-joueur.json',
                *[RACINE / f'tests/test_{nom}.py' for nom in TESTS]]
    return {str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--reference', default='fff9aab')
    p.add_argument('--tests-valides', type=Path,
                   help='résultats consolidés déjà acquis, avec empreintes exactes des sources')
    args = p.parse_args()
    ceder()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    os.environ['SEUIL_AUTH'] = 'C:/Users/msics/donjon/.seuil-auth'
    depart, sources = time.monotonic(), empreintes()
    fin = {'ok': False, 'pid': os.getpid()}
    def lancer(nom, commande):
        with (sortie / (nom + '.log')).open('w', encoding='utf-8') as flux:
            code = subprocess.run([sys.executable, *commande], cwd=RACINE, stdout=flux,
                                  stderr=subprocess.STDOUT, check=False).returncode
        fin[nom + '_code'] = code
        return code == 0
    try:
        ecrire(sortie / 'debut.json', {'sources': sources, 'pid': os.getpid(), 'reference': args.reference,
            'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RACINE, text=True).strip()})
        if args.tests_valides:
            acquis = json.loads(args.tests_valides.read_text(encoding='utf-8'))
            if acquis['sources'] != sources or not acquis['tests']['succes']:
                raise ValueError('Résultats de tests absents, en échec ou périmés')
            ecrire(sortie / 'tests.json', acquis['tests'])
            fin.update(tests_code=0, tests_reutilises=str(args.tests_valides.resolve()))
        elif not lancer('tests', ['tools/tests.py', '--processus', '2', '--sortie', str(sortie / 'tests.json'),
                                 *[f'tests/test_{nom}.py' for nom in TESTS]]):
            return 1
        if not lancer('empreintes', ['tools/comparer_bancs.py', '--reference', args.reference,
            '--empreintes', '--heures', '2', '--scenarios', 'relais', 'crue_hameau', '--processus', '2',
            '--sortie', str(sortie / 'empreintes.json')]):
            return 1
        if not lancer('luna', ['tools/banc_parties.py', 'tests/data/bancs/mandat-joueur.json',
            '--connexion', 'chatgpt', '--max-appels', '30', '--fil', '--sortie', str(sortie / 'luna')]):
            return 1
        fin['ok'] = True
        return 0
    except BaseException:
        fin['erreur'] = traceback.format_exc()
        return 1
    finally:
        fin['sources_inchangees'] = empreintes() == sources
        fin['ok'] = fin['ok'] and fin['sources_inchangees']
        fin['secondes'] = time.monotonic() - depart
        ecrire(sortie / 'fin.json', fin)


if __name__ == '__main__':
    raise SystemExit(main())
