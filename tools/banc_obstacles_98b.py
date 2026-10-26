"""Couples CPU du lot 98 b, deux ouvriers réduits, sans cache de temps.

Archives locales attendues : artifacts/profil-98/ancien (42bb9c0) et
artifacts/obstacles-98b/base (677f4c1). Aucun worktree principal modifié.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dossier', default='artifacts/obstacles-98b/cpu')
    ap.add_argument('--empreintes', action='store_true', help='16 nuits 2 h, archive de base et cache commun')
    args = ap.parse_args()
    racine = Path(__file__).resolve().parents[1]
    dossier = (racine / args.dossier).resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    depots = dict(ancien=racine / 'artifacts/profil-98/ancien',
                  base=racine / 'artifacts/obstacles-98b/base', branche=racine)
    if args.empreintes:
        import comparer_bancs
        @contextmanager
        def archive_base(_, reference):
            assert reference.startswith('677f4c1'), reference
            yield depots['base']
        # Même comparateur et même clé de cache ; la référence absente se joue
        # depuis l'archive, sans créer de worktree ni écrire dans le dépôt principal.
        # Seul le cache partagé autorisé reçoit les références manquantes.
        comparer_bancs.worktree_temporaire = archive_base
        return comparer_bancs.main(['--reference', '677f4c1', '--empreintes',
            '--scenarios', 'relais', 'mine', 'auberge', 'crue', '--processus', '1',
            '--sortie', str(racine / 'artifacts/obstacles-98b/empreintes.json')])
    conditions = dict(debut=time.time(), processus_max=2, priorite='BelowNormal', cache=False,
        sources={nom: {f: hashlib.sha256((depot / 'donjon' / f).read_bytes()).hexdigest()
                       for f in ('planification.py', 'trajet_estime.py', 'spatial.py')
                       if (depot / 'donjon' / f).exists()} for nom, depot in depots.items()})
    (dossier / 'conditions.json').write_text(json.dumps(conditions, indent=2), encoding='utf8')
    for reference in ('ancien', 'base'):
        cohorte = dossier / reference
        cohorte.mkdir(exist_ok=True)
        agregats = {reference: [], 'branche': []}
        for scenario, depart in (('auberge', 'fixe'), ('auberge', 'tire'), ('mine', 'fixe')):
            ouvriers, flux = {}, []
            for nom in agregats:
                fichier = cohorte / f'{nom}-{scenario}-{depart}'
                log = fichier.with_suffix('.log').open('w', encoding='utf8')
                flux.append(log)
                commande = [sys.executable, str(racine / 'tools/mesurer_attente_bornee.py'),
                    '--cout', '--depot', str(depots[nom]), '--scenario', scenario, '--depart', depart,
                    '--heures', '12', '--graine', '1985', '--sortie', str(fichier.with_suffix('.json'))]
                ouvriers[nom] = subprocess.Popen(commande, cwd=racine, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=0x4000 if os.name == 'nt' else 0,
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            codes = {nom: p.wait() for nom, p in ouvriers.items()}
            for log in flux:
                log.close()
            if any(codes.values()):
                raise RuntimeError((reference, scenario, depart, codes))
            for nom in agregats:
                r = json.loads((cohorte / f'{nom}-{scenario}-{depart}.json').read_text(encoding='utf8'))
                assert all(r['recharge'].values()), r['recharge']
                agregats[nom].append(r['resume'])
                (cohorte / f'{nom}-comparer.json').write_text(
                    json.dumps(agregats[nom], ensure_ascii=False, indent=2), encoding='utf8')
            print(reference, scenario, depart,
                  {nom: agregats[nom][-1]['secondes'] for nom in agregats}, flush=True)
        if reference == 'base':
            with (cohorte / 'calcul.log').open('w', encoding='utf8') as log:
                subprocess.run([sys.executable, str(racine / 'tools/empreintes_nuits.py'), 'comparer',
                    str(cohorte / 'base-comparer.json'), str(cohorte / 'branche-comparer.json'), '--calcul'],
                    cwd=racine, stdout=log, stderr=subprocess.STDOUT, check=True,
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    with (dossier / 'repetitions-calcul.log').open('w', encoding='utf8') as log:
        subprocess.run([sys.executable, str(racine / 'tools/empreintes_nuits.py'), 'comparer',
            str(dossier / 'ancien/branche-comparer.json'), str(dossier / 'base/branche-comparer.json'), '--calcul'],
            cwd=racine, stdout=log, stderr=subprocess.STDOUT, check=True,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
