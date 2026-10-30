"""Attribuer les seuls incidents de 61ced73, par méthode et sous-test, sur deux arbres."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

SCRIPT = Path(__file__).resolve()
RACINE = SCRIPT.parents[1]


def ecrire(chemin, objet):
    chemin.write_text(json.dumps(objet, ensure_ascii=False, indent=2), encoding='utf8')


def worker(entree, sortie):
    resultat = {'outil_erreur': None}
    try:
        config = json.loads(entree.read_text(encoding='utf8'))
        arbre = Path(config['arbre']).resolve()
        exclus = {RACINE, SCRIPT.parent, arbre}
        sys.path[:] = [str(arbre), str(arbre / 'tests')] + [p for p in sys.path
            if Path(p or os.curdir).resolve() not in exclus]
        import importlib
        importlib.import_module('tests')
        sys.path.append(str(arbre / 'tools'))
        from priorite import ceder
        ceder()
        import io
        import unittest
        debut = time.perf_counter()
        suite = unittest.TestLoader().loadTestsFromName(config['test'])
        flux = io.StringIO()
        r = unittest.TextTestRunner(stream=flux, verbosity=2).run(suite)
        fichier = arbre / 'tests' / (config['test'].split('.')[1] + '.py')
        resultat.update(test=config['test'], tests=r.testsRun, succes=r.wasSuccessful(),
            secondes=time.perf_counter() - debut, journal=flux.getvalue(),
            sha_test=hashlib.sha256(fichier.read_bytes()).hexdigest(),
            **{k: [(str(t), trace) for t, trace in getattr(r, k)]
               for k in ('failures', 'errors', 'skipped', 'expectedFailures')},
            unexpectedSuccesses=[str(t) for t in r.unexpectedSuccesses])
    except BaseException:
        resultat['outil_erreur'] = traceback.format_exc()
    finally:
        ecrire(sortie, resultat)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--integration', type=Path, required=True)
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--journal', type=Path, required=True)
    p.add_argument('--reference-resultats', type=Path)
    args = p.parse_args()
    dossier = args.sortie.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = {'ok': False, 'debut': time.time()}
    try:
        sys.path[:0] = [str(RACINE), str(RACINE / 'tools')]
        from priorite import ceder
        ceder()
        incidents = []
        for ligne in args.journal.read_text(encoding='utf8').splitlines():
            match = re.match(r'^(FAIL|ERROR): (\w+) \((test_\w+\.\w+\.\w+)\)(.*)$', ligne)
            if match:
                incidents.append({'ordre': len(incidents) + 1, 'type': match[1],
                                  'test': 'tests.' + match[3], 'sous_test': match[4].strip()})
        assert len(incidents) == 23, f'{len(incidents)} incidents au lieu de 23'
        tests = list(dict.fromkeys(i['test'] for i in incidents))
        ecrire(dossier / 'incidents.json', incidents)
        bilan.update(methodes=len(tests), incidents=len(incidents), pythonhashseed='313', variantes={})
        env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONHASHSEED': '313'}
        for variante, arbre in [('integration', args.integration.resolve()), ('313-sans-315', RACINE)]:
            commit = subprocess.check_output(['git', '-C', str(arbre), 'rev-parse', 'HEAD'], text=True).strip()
            if variante == 'integration' and args.reference_resultats:
                cache = json.loads(args.reference_resultats.read_text(encoding='utf8'))
                assert cache['commit'] == commit
                assert [r['test'] for r in cache['resultats']] == tests
                ecrire(dossier / 'integration.json', cache)
                bilan['variantes'][variante] = {'commit': commit, 'cache': str(args.reference_resultats),
                    'methodes': len(cache['resultats']),
                    'failures': sum(len(r.get('failures', [])) for r in cache['resultats']),
                    'errors': sum(len(r.get('errors', [])) for r in cache['resultats']), 'erreurs_outil': 0}
                continue
            print(f'{variante} {commit[:8]} : {len(tests)} méthodes, deux processus réduits', flush=True)

            def lancer(item):
                n, nom = item
                entree = dossier / f'{variante}-{n:02}-entree.json'
                sortie = dossier / f'{variante}-{n:02}.json'
                ecrire(entree, {'arbre': str(arbre), 'test': nom})
                r = subprocess.run([sys.executable, str(SCRIPT), '--_worker', str(entree), str(sortie)],
                    cwd=arbre, env=env, capture_output=True, text=True, encoding='utf8', timeout=1800)
                if not sortie.exists():
                    return {'test': nom, 'outil_erreur': f'Code {r.returncode}\n{r.stdout}\n{r.stderr}'}
                resultat = json.loads(sortie.read_text(encoding='utf8'))
                print(f"{variante} {n:02} : {nom} : {'OK' if resultat.get('succes') else 'ECHEC'}", flush=True)
                return resultat

            with ThreadPoolExecutor(max_workers=2) as pool:
                resultats = list(pool.map(lancer, enumerate(tests)))
            ecrire(dossier / f'{variante}.json', {'commit': commit, 'resultats': resultats})
            bilan['variantes'][variante] = {'commit': commit,
                'methodes': len(resultats), 'failures': sum(len(r.get('failures', [])) for r in resultats),
                'errors': sum(len(r.get('errors', [])) for r in resultats),
                'erreurs_outil': sum(bool(r.get('outil_erreur')) for r in resultats)}
        bilan['ok'] = all(v['erreurs_outil'] == 0 for v in bilan['variantes'].values())
        bilan['signification_ok'] = 'Les rejeux ciblés ont tous produit un résultat, pas nécessairement vert.'
    except BaseException:
        bilan['erreur'] = traceback.format_exc()
        print(bilan['erreur'], file=sys.stderr, flush=True)
    finally:
        bilan['fin'] = time.time()
        ecrire(dossier / 'fin.json', bilan)
    return int(not bilan['ok'])


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--_worker':
        worker(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        raise SystemExit(main())
