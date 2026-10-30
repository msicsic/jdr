"""Validation bornée 335 : fichiers ciblés, vingt nuits, cache seul, fin même en échec."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
import comparer_bancs as banc
from priorite import ceder

TESTS = ('suivi_vocal', 'agendas_proteger', 'agendas_fins', 'agendas_garder',
         'agendas_activation', 'empathie_peur', 'protection', 'but_protection',
         'planification', 'trajet_estime', 'trajets_reels', 'borne_rester',
         'ouie', 'ouie_commune', 'ouie_temoins')
BASE = '9237e14'


def ecrire(chemin, contenu):
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2), encoding='utf-8')


def comparer(sortie, reference):
    config = dict(scenarios=['relais', 'mine', 'auberge', 'crue', 'crue_hameau'],
                  graines=[1985, 7, 42, 2024], heures=4., depart='tire', processus=1,
                  verifier=False, empreintes=False, joueurs=dict(banc.JOUEURS))
    revision = banc.git(RACINE, 'rev-parse', reference)
    # Réemploi autorisé seulement si moteur ET outils sont identiques à la base.
    banc.git(RACINE, 'diff', '--exit-code', revision, BASE, '--', 'donjon', 'tools')
    def absent():
        raise RuntimeError('Référence absente du cache : aucune nuit de référence relancée.')
    avant = banc.nuits_du_cote(absent, revision, config, sortie, 'reference', banc.references.dossier(RACINE))
    ecrire(sortie / 'reference.json', avant)
    apres = []
    with ProcessPoolExecutor(max_workers=1, max_tasks_per_child=1) as pool:
        for nuit in pool.map(banc.jouer_nuit, [(s, g, config) for s, g in banc.taches_du_lot(config)]):
            apres.append(nuit)
            ecrire(sortie / f"branche-{nuit['scenario']}-{nuit['graine']}.json", nuit)
    ecrire(sortie / 'banc.json', dict(config=config, reference=revision, reference_nuits=avant, branche_nuits=apres))
    lignes = []
    for a, b in zip(avant, apres):
        mesures = (b.get('donnees') or {}).get('mesures', {})
        sa, sb = [(n.get('avis') or {}).get('total_non_justifies') for n in (a, b)]
        # Aucun agenda historique ajouté : état complet et chronique doivent
        # rester identiques, au-delà de l'absence de nouvelles alertes.
        identique = (a.get('etat_final') == b.get('etat_final') and
                     (a.get('donnees') or {}).get('chronique') == (b.get('donnees') or {}).get('chronique') and
                     (a.get('donnees') or {}).get('mesures') == (b.get('donnees') or {}).get('mesures'))
        ok = (sa is not None and sb is not None and sb <= sa and not a['plantage'] and not b['plantage']
              and mesures.get('usurpations') == 0 and identique)
        lignes.append(dict(scenario=b['scenario'], graine=b['graine'], suspects_reference=sa,
                           suspects_branche=sb, plantage=b['plantage'], usurpations=mesures.get('usurpations'),
                           identique=identique, ok=ok))
    resultat = dict(nuits=lignes, references_cache=sum('cache' in n for n in avant),
                    ok=all(n['ok'] for n in lignes),
                    limite='Nuits historiques sans agenda protéger déclaré ; suivi actif éprouvé dans les tests.')
    ecrire(sortie / 'bilan.json', resultat)
    return resultat['ok']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie', type=Path, required=True)
    parser.add_argument('--reference', default='f08ef58')
    parser.add_argument('--tests-seuls', action='store_true')
    args = parser.parse_args()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    debut = time.monotonic()
    fin = dict(ok=False, pid=os.getpid(), base=BASE, reference=args.reference)
    try:
        ceder()
        fichiers = [*sorted((RACINE / 'donjon').glob('*.py')),
                    *[RACINE / f'tests/test_{n}.py' for n in TESTS], Path(__file__).resolve()]
        ecrire(sortie / 'debut.json', dict(pid=os.getpid(), cwd=str(RACINE),
            commit=banc.git(RACINE, 'rev-parse', 'HEAD'),
            empreintes={str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers}))
        commande = [sys.executable, str(RACINE / 'tools/tests.py'), '--processus', '1',
                    '--sortie', str(sortie / 'tests.json'),
                    *[f'tests/test_{n}.py' for n in TESTS]]
        with (sortie / 'tests.log').open('w', encoding='utf-8') as journal:
            tests = subprocess.run(commande, cwd=RACINE, stdout=journal, stderr=subprocess.STDOUT,
                                   env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        fin['code_tests'] = tests.returncode
        if tests.returncode:
            return 1
        fin['ok'] = args.tests_seuls or comparer(sortie, args.reference)
        return int(not fin['ok'])
    except BaseException:
        fin['erreur'] = traceback.format_exc()
        return 1
    finally:
        fin['secondes'] = time.monotonic() - debut
        ecrire(sortie / 'fin.json', fin)  # Dernière écriture, succès comme échec.


if __name__ == '__main__':
    raise SystemExit(main())
