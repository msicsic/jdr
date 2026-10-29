"""Lot 332 : vingt nuits, cache commun, verdict par nuit et fichier de fin garanti."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
import json
from pathlib import Path
import sys
import time
import traceback
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparer_bancs as banc
import references
from priorite import ceder


def jouer(tache):
    from donjon import signes
    compte = {'appels_percus': 0, 'cpu_percus': 0.,
              'appels_attention': 0, 'cpu_attention': 0.}

    def mesurer(f, nom):
        def appel(*a, **k):
            debut = time.process_time()
            try:
                return f(*a, **k)
            finally:
                compte['appels_' + nom] += 1
                compte['cpu_' + nom] += time.process_time() - debut
        return appel

    with patch.object(signes, 'percus', mesurer(signes.percus, 'percus')), \
         patch.object(signes, 'regard_a_suivre', mesurer(signes.regard_a_suivre, 'attention')):
        nuit = banc.jouer_nuit(tache)
    # Durées inclusives : attention peut appeler percus ; ne pas les additionner.
    nuit['cout_perception'] = compte
    return nuit


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', required=True)
    p.add_argument('--sortie', type=Path, required=True)
    args = p.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=True)
    ceder()
    debut, code = time.perf_counter(), 1
    try:
        config = {'scenarios': ['relais', 'mine', 'auberge', 'crue', 'crue_hameau'],
                  'graines': [1985, 7, 42, 2024], 'heures': 4, 'depart': 'tire',
                  'processus': 2, 'verifier': False, 'empreintes': False,
                  'joueurs': dict(banc.JOUEURS)}
        racine = banc.RACINE
        commit = references.resoudre(racine, args.reference)
        if not commit:
            raise ValueError('Référence git inconnue')
        with ExitStack() as pile:
            arbres = []
            def arbre():
                if not arbres:
                    arbres.append(pile.enter_context(banc.worktree_temporaire(racine, commit)))
                return arbres[0]
            avant = banc.nuits_du_cote(arbre, commit, config, args.sortie,
                                       'reference', references.dossier(racine))
        (args.sortie / 'reference.json').write_text(json.dumps(avant, ensure_ascii=False), encoding='utf-8')
        print('Référence disponible ; branche : vingt nuits, deux travailleurs réduits.', flush=True)
        apres = []
        with ProcessPoolExecutor(max_workers=2, max_tasks_per_child=1) as pool:
            for nuit in pool.map(jouer, [(s, g, config) for s, g in banc.taches_du_lot(config)]):
                apres.append(nuit)
                (args.sortie / f"{nuit['scenario']}-{nuit['graine']}.json").write_text(
                    json.dumps(nuit, ensure_ascii=False), encoding='utf-8')
                print(nuit['scenario'], nuit['graine'], nuit['secondes_cpu'], flush=True)
        rapport = {'config': config, 'reference': {'commit': commit, 'nuits': avant},
                   'branche': {'commit': banc.git(racine, 'rev-parse', 'HEAD'), 'nuits': apres}}
        (args.sortie / 'comparaison.json').write_text(json.dumps(rapport, ensure_ascii=False), encoding='utf-8')
        lignes = []
        for a, b in zip(rapport['reference']['nuits'], rapport['branche']['nuits']):
            ma, mb = ((n.get('donnees') or {}).get('mesures', {}) for n in (a, b))
            suspects_avant, suspects_apres = (n.get('avis', {}).get('total_non_justifies') for n in (a, b))
            lignes.append({'scenario': b['scenario'], 'graine': b['graine'],
                           'suspects_reference': suspects_avant, 'suspects_branche': suspects_apres,
                           'sans_hausse': (suspects_avant is not None and suspects_apres is not None
                                          and suspects_apres <= suspects_avant),
                           'plantage': b['plantage'], 'usurpations': mb.get('usurpations'),
                           'regards_suivis': mb.get('regards_suivis'),
                           'rotation_attention': mb.get('rotation_attention'),
                           'secondes_cpu_branche': b['secondes_cpu'],
                           'cout_perception': b['cout_perception'],
                           'reference_cache': a.get('cache')})
        valide = (len(lignes) == 20 and all(l['sans_hausse'] and not l['plantage']
                                          and l['usurpations'] == 0 for l in lignes))
        (args.sortie / 'validation.json').write_text(json.dumps(
            {'ok': valide, 'nuits': lignes}, ensure_ascii=False, indent=2), encoding='utf-8')
        code = int(not valide or any(n['plantage'] for n in avant))
    except Exception:
        (args.sortie / 'erreur.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        # Le superviseur ne reprend qu'après cette écriture, même si le banc a échoué.
        (args.sortie / 'fin.json').write_text(json.dumps(
            {'ok': code == 0, 'code': code, 'secondes': time.perf_counter() - debut}), encoding='utf-8')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
