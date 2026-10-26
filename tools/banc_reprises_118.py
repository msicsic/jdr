"""Paires CPU nues du lot 118, archives locales, deux ouvriers réduits au plus."""
import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dossier', default='artifacts/reprises-118')
    ap.add_argument('--leviers', action='store_true')
    args = ap.parse_args()
    racine = Path(__file__).resolve().parents[1]
    dossier = (racine / args.dossier).resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    refs = {'ancien': '42bb9c0', 'base': 'c3568ae', 'A3': '2fd4c4a',
            'A2': '5827a31', 'A1': '96350dc'}
    depots = {'branche': racine}
    for nom, ref in refs.items():
        cible = dossier / nom
        depots[nom] = cible
        if not cible.exists():
            cible.mkdir()
            zipfile.ZipFile(io.BytesIO(subprocess.check_output(
                ['git', 'archive', '--format=zip', ref], cwd=racine))).extractall(cible)
    conditions = {'processus_max': 2, 'priorite': 'BelowNormal', 'cache_temps': False,
                  'refs': refs, 'branche': subprocess.check_output(
                      ['git', 'rev-parse', 'HEAD'], cwd=racine, text=True).strip()}
    (dossier / 'conditions-cpu.json').write_text(json.dumps(conditions, indent=2), encoding='utf8')
    paires = []
    if args.leviers:
        paires += [(f'levier-{b}', a, b, [('auberge', 'tire')])
                   for a, b in [('base', 'A3'), ('A3', 'A2'), ('A2', 'A1')]]
    for ref in ('ancien', 'base'):
        paires.append((ref, ref, 'branche', [('auberge', 'fixe'), ('auberge', 'tire'), ('mine', 'fixe')]))
    for groupe, a, b, nuits in paires:
        cohorte = dossier / 'cpu' / groupe
        cohorte.mkdir(parents=True, exist_ok=True)
        resumes = {a: [], b: []}
        for scenario, depart in nuits:
            processus, flux = {}, []
            achevee = all((cohorte / f'{n}-{scenario}-{depart}.json').exists() for n in (a, b))
            for nom in (a, b):
                sortie = cohorte / f'{nom}-{scenario}-{depart}.json'
                if achevee:
                    continue  # reprise du lanceur : une paire achevée n'est pas rejouée
                log = sortie.with_suffix('.log').open('w', encoding='utf8')
                flux.append(log)
                cmd = [sys.executable, str(racine / 'tools/mesurer_attente_bornee.py'), '--cout',
                       '--depot', str(depots[nom]), '--scenario', scenario, '--depart', depart,
                       '--heures', '12', '--graine', '1985', '--sortie', str(sortie)]
                processus[nom] = subprocess.Popen(cmd, cwd=racine, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=0x4000 if os.name == 'nt' else 0,
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            codes = {n: p.wait() for n, p in processus.items()}
            for log in flux:
                log.close()
            if any(codes.values()):
                raise RuntimeError((groupe, scenario, depart, codes))
            for nom in resumes:
                r = json.loads((cohorte / f'{nom}-{scenario}-{depart}.json').read_text(encoding='utf8'))
                assert all(r['recharge'].values())
                resumes[nom].append(r['resume'])
                (cohorte / f'{nom}-comparer.json').write_text(
                    json.dumps(resumes[nom], ensure_ascii=False, indent=2), encoding='utf8')
            print(groupe, scenario, depart, {n: resumes[n][-1]['secondes'] for n in resumes}, flush=True)
        if a != 'ancien':
            with (cohorte / 'calcul.log').open('w', encoding='utf8') as log:
                subprocess.run([sys.executable, str(racine / 'tools/empreintes_nuits.py'), 'comparer',
                    str(cohorte / f'{a}-comparer.json'), str(cohorte / f'{b}-comparer.json'), '--calcul'],
                    cwd=racine, stdout=log, stderr=subprocess.STDOUT, check=True,
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
