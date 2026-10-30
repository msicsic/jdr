"""Validation ciblée du lot 340, deux travailleurs réduits, fin.json écrit en dernier."""
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

TESTS = (
    'agendas_ascendant_evolue', 'agendas_socle', 'agendas_compte_rendu',
    'agendas_jugement_mandat', 'agendas_faire_confier', 'agendas_reaffecter',
    'agendas_evaluation', 'agendas_mandat', 'agendas_amener_fin', 'agendas_activation',
    'agendas_devis_observateur', 'relations_ascendant', 'relations_graduees',
    'relations_socle', 'relations_lectures', 'relations_statuts', 'social',
    'ouie_temoins', 'parole_commune', 'emissions_parole', 'paroles',
    'contenus_parole', 'planification',
)


def ecrire(p, valeur):
    p.write_text(json.dumps(valeur, ensure_ascii=False, indent=2), encoding='utf-8')


def empreintes():
    fichiers = [*sorted((RACINE / 'donjon').glob('*.py')), Path(__file__).resolve(),
                *[RACINE / f'tests/test_{nom}.py' for nom in TESTS]]
    return {str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers}


def analyser(rapport):
    lignes = []
    for a, b in zip(rapport['reference']['nuits'], rapport['branche']['nuits']):
        sa, sb = [n.get('avis', {}).get('total_non_justifies') for n in (a, b)]
        mesures = (b.get('donnees') or {}).get('mesures', {})
        charges = [p for projets in b.get('final', {}).get('projets', {}).values()
                   for p in projets if p['origine']['type'] == 'mandat']
        lignes.append(dict(scenario=b['scenario'], graine=b['graine'],
            suspects_reference=sa, suspects_branche=sb, usurpations=mesures.get('usurpations'),
            plantage_reference=a['plantage'], plantage_branche=b['plantage'],
            mandats=len(charges), mandats_aboutis=sum(p['etat'] == 'atteint' for p in charges),
            ok=sa is not None and sb is not None and sb <= sa and not a['plantage']
               and not b['plantage'] and mesures.get('usurpations') == 0))
    return dict(ok=len(lignes) == 20 and all(l['ok'] for l in lignes), nuits=lignes,
                references_cache=sum('cache' in n for n in rapport['reference']['nuits']),
                limite='Banc passif borné ; temps de référence du cache non comparables.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie', type=Path, required=True)
    parser.add_argument('--reference', default='9f261f9')
    args = parser.parse_args()
    ceder()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    debut, acquises = time.monotonic(), empreintes()
    fin = dict(ok=False, pid=os.getpid())
    try:
        revision = subprocess.check_output(['git', 'rev-parse', args.reference], cwd=RACINE, text=True).strip()
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RACINE, text=True).strip()
        ecrire(sortie / 'debut.json', dict(reference=revision, commit=commit,
                                         cwd=str(RACINE), empreintes=acquises, pid=os.getpid()))
        with (sortie / 'tests.log').open('w', encoding='utf-8') as flux:
            fin['tests_code'] = subprocess.run([sys.executable, 'tools/tests.py', '--processus', '2',
                '--sortie', str(sortie / 'tests.json'), *[f'tests/test_{nom}.py' for nom in TESTS]],
                cwd=RACINE, stdout=flux, stderr=subprocess.STDOUT, check=False).returncode
        if fin['tests_code']:
            return 1
        with (sortie / 'banc.log').open('w', encoding='utf-8') as flux:
            fin['banc_code'] = subprocess.run([sys.executable, 'tools/comparer_bancs.py',
                '--reference', revision, '--heures', '4', '--processus', '2', '--scenarios',
                'relais', 'mine', 'auberge', 'crue', 'crue_hameau', '--sortie', str(sortie / 'comparaison.json')],
                cwd=RACINE, stdout=flux, stderr=subprocess.STDOUT, check=False).returncode
        if (sortie / 'comparaison.json').exists():
            bilan = analyser(json.loads((sortie / 'comparaison.json').read_text(encoding='utf-8')))
            ecrire(sortie / 'bilan.json', bilan)
            fin['banc_ok'] = bilan['ok']
        fin['sources_inchangees'] = empreintes() == acquises
        fin['ok'] = not fin['banc_code'] and fin.get('banc_ok', False) and fin['sources_inchangees']
        return int(not fin['ok'])
    except BaseException:
        fin['erreur'] = traceback.format_exc()
        return 1
    finally:
        fin['secondes'] = time.monotonic() - debut
        ecrire(sortie / 'fin.json', fin)


if __name__ == '__main__':
    raise SystemExit(main())
