"""Reprise détachée : mesures figées et captures d'attribution, deux travailleurs au plus."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import gzip
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))


def analyser_captures(dossier):
    """Preuves relisibles : empreintes du rejeu, recharge, rendu et ventilation des appels."""
    sys.path.insert(0, str(RACINE))
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    ancien = json.loads((dossier.parent / 'final/banc-base.json').read_text(encoding='utf8'))
    references = {(n['scenario'], n['graine']): n['donnees']['empreintes']
                  for n in ancien['branche']['nuits']}
    bilan = {'nuits': [], 'captures_rechargees': []}
    for fichier in sorted((dossier / 'avant-captures').glob('*.json')):
        if fichier.name.endswith('-fin.json'):
            continue
        d = json.loads(fichier.read_text(encoding='utf8'))
        assert d['donnees']['empreintes'] == references[d['scenario'], d['graine']], fichier
        appels = []
        for a in d['appels']:
            v = d['verifications'][a['verification']] if a['verification'] is not None else None
            appels.append({**a, 'attribution': ('repetition_sans_entree_nouvelle'
                if v and v['repetition_sans_preuve'] else 'verification_nouvelle'
                if v else 'contact_ou_position_non_expiree'), 'preuve': v})
        bilan['nuits'].append({'scenario': d['scenario'], 'graine': d['graine'],
            'empreintes_ancien_banc_identiques': True, 'appels': appels})
    with tempfile.TemporaryDirectory(prefix='recharge-374-') as tmp:
        sauvegarde = Path(tmp) / 'capture.json'
        for fichier in sorted((dossier / 'avant-captures').glob('*.json.gz')):
            m = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
            m.sauver(sauvegarde)
            n = Monde.charger(sauvegarde)
            assert m.data == n.data and regarder(m) == regarder(n) and scene_percue(m) == scene_percue(n), fichier
            bilan['captures_rechargees'].append({'fichier': fichier.name,
                'monde_rendu_scene_identiques': True,
                'sha256': hashlib.sha256(fichier.read_bytes()).hexdigest()})
    (dossier / 'attribution-rechargee.json').write_text(
        json.dumps(bilan, ensure_ascii=False, indent=2), encoding='utf8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision', required=True)
    p.add_argument('--ancien', required=True, type=Path)
    p.add_argument('--sortie', required=True, type=Path)
    p.add_argument('--fin', required=True, type=Path)
    p.add_argument('--reference', required=True, help='commit integration figé avant le lancement')
    args = p.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=True)
    args.fin.parent.mkdir(parents=True, exist_ok=True)
    bilan = {'revision': args.revision, 'reference': args.reference, 'statut': 'echec', 'etapes': []}

    def tracer(message):
        print(f'{datetime.now().isoformat(timespec="seconds")} {message}', flush=True)

    def lancer(nom, commande, cwd=RACINE):
        tracer(f'Début {nom}')
        with (args.sortie / (nom + '.stdout.txt')).open('w', encoding='utf8') as out, \
                (args.sortie / (nom + '.stderr.txt')).open('w', encoding='utf8') as err:
            processus = subprocess.Popen(commande, cwd=cwd, stdout=out, stderr=err,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})
            tracer(f'{nom} : processus {processus.pid}')
            code = processus.wait()
        tracer(f'Fin {nom} : code {code}')
        return {'nom': nom, 'code': code}

    try:
        from tools.priorite import ceder
        ceder()
        tracer(f'Démarrage réussi, branche {args.revision}, intégration {args.reference}')
        r = lancer('tests-position', [sys.executable, '-m', 'unittest', 'tests.test_position_hypothese', '-q'])
        bilan['etapes'].append(r)
        if r['code']:
            raise RuntimeError('Échec des tests de position après fusion.')
        fichiers = ['test_chercher_appeler', 'test_ou_est_il',
            'test_contact_sous_but', 'test_reprise_contact', 'test_ouie_temoins', 'test_memoire_socle',
            'test_but_protection', 'test_contact_position_inconnue', 'test_localisation_crue',
            'test_localisation', 'test_protection', 'test_appels_restes']
        tests = args.sortie / 'tests-reprise.json'
        r = lancer('tests-reprise', [sys.executable, str(RACINE / 'tools/tests.py'),
            *[str(RACINE / 'tests' / (f + '.py')) for f in fichiers],
            '--processus', '2', '--sortie', str(tests)])
        bilan['etapes'].append(r)
        rapport = json.loads(tests.read_text(encoding='utf8'))
        connus = []
        echecs_base = {
            'test_ilse_capture_141000_pas_de_reprise_par_la_minute': 'self.assertEqual(texte, decoupe)',
            'test_contenant_dans_une_autre_salle': 'self.assertEqual(lignes, decoupees)',
        }
        for f in rapport['fichiers']:
            if f['errors']:
                raise RuntimeError('Erreur dans les tests ciblés.')
            for e in f['failures']:
                if not any(nom in e[0] and assertion in e[1] for nom, assertion in echecs_base.items()):
                    raise RuntimeError('Nouvel échec dans les tests ciblés.')
                connus.append(e)
        bilan['echecs_deja_reproduits_sur_fusion_avant_correctif'] = connus
        # Les captures déjà complètes sont relues, jamais rejouées.
        def capturer(tache):
            scenario, graine = tache
            return lancer(f'attribution-{scenario}-{graine}', [sys.executable,
                str(RACINE / 'tools/attribuer_positions_374.py'), '--scenario', scenario,
                '--graine', str(graine), '--sortie', str(args.sortie / 'avant-captures')], args.ancien)

        taches = [(s, g) for s in ('auberge', 'mine') for g in (1985, 7, 42, 2024)]
        taches += [('crue', g) for g in (1985, 2024, 42)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            captures = list(pool.map(capturer, taches))
        bilan['etapes'].extend(captures)
        if any(e['code'] for e in captures):
            raise RuntimeError('Échec de capture : voir les journaux attribution.')
        tracer('Début rechargement et attribution des captures')
        analyser_captures(args.sortie)
        tracer('Fin rechargement et attribution des captures')
        r = lancer('mesures', [sys.executable, str(RACINE / 'tools/mesurer_position_374.py'),
            '--sortie', str(args.sortie / 'mesures'), '--revision', args.revision,
            '--reference', args.reference, '--historique', str(args.sortie.parent / 'final/banc-base.json')])
        bilan['etapes'].append(r)
        if r['code']:
            raise RuntimeError('Échec du banc : voir mesures.stderr.txt et mesures/.')
        bilan['statut'] = 'calculs_termines_a_analyser'
    except Exception:
        bilan['trace'] = traceback.format_exc()
        tracer(bilan['trace'])
    finally:
        temporaire = args.fin.with_suffix('.tmp')
        temporaire.write_text(json.dumps(bilan, ensure_ascii=False, indent=2), encoding='utf8')
        temporaire.replace(args.fin)
        tracer(f'Fichier de fin : {args.fin} ({bilan["statut"]})')
    return int(bilan['statut'] == 'echec')


if __name__ == '__main__':
    raise SystemExit(main())
