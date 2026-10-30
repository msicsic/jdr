"""Validation finale : tests concernés et seules cinq nuits affectées par les interruptions."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RACINE), str(RACINE / 'tools')]

FICHIERS = ['test_reprise_contact.py', 'test_contact_position_inconnue.py',
            'test_reessai_obstacle.py', 'test_esprits.py', 'test_marche.py',
            'test_planification.py', 'test_service_rejoindre.py',
            'test_contact_sous_but.py', 'test_trajet_estime.py']


def nuit(tache):
    from priorite import ceder
    ceder()
    import comparer_bancs as c
    from donjon import pnj
    scenario, graine, config = tache
    original, violations = pnj._approcher, []

    def observer(m, qui, g, *args, **kwargs):
        refus = pnj.refus_etape(m, qui, [g])
        if refus == 'contact interrompu sans entrée nouvelle':
            from donjon.temps import instant
            violations.append({'pnj': qui, 'instant': instant(m), 'etape': dict(g)})
        return original(m, qui, g, *args, **kwargs)

    with patch.object(pnj, '_approcher', observer):
        resultat = c.jouer_nuit((scenario, graine, config))
    resultat['reprises_sans_entree'] = violations
    resultat['rejouee'] = True
    return resultat


def ecrire(chemin, objet):
    chemin.write_text(json.dumps(objet, ensure_ascii=False, indent=2), encoding='utf8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sortie', type=Path, required=True)
    args = p.parse_args()
    dossier = args.sortie.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = {'ok': False, 'debut': time.time()}
    try:
        from priorite import ceder
        ceder()
        import comparer_bancs as c
        archive = json.loads((dossier.parent / 'comparaison.json').read_text(encoding='utf8'))
        bilan['commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RACINE, text=True).strip()
        print('Tests ciblés, deux travailleurs réduits', flush=True)
        with (dossier / 'tests.log').open('w', encoding='utf8') as log:
            bilan['tests_code'] = subprocess.run([sys.executable, 'tools/tests.py', '--processus', '2',
                *['tests/' + f for f in FICHIERS], '--sortie', str(dossier / 'tests.json')],
                cwd=RACINE, stdout=log, stderr=subprocess.STDOUT).returncode
        config = {**archive['config'], 'processus': 2}
        selection = [n for n in archive['branche']['nuits'] if n['approches_impossibles']]
        print(f'Banc : {len(selection)} nuits de branche, aucune référence rejouée', flush=True)
        with ProcessPoolExecutor(max_workers=2, max_tasks_per_child=1) as pool:
            nouvelles = list(pool.map(nuit, [(n['scenario'], n['graine'], config) for n in selection]))
        remplacement = {(n['scenario'], n['graine']): n for n in nouvelles}
        branche = [remplacement.get((n['scenario'], n['graine']), {**n, 'rejouee': False})
                   for n in archive['branche']['nuits']]
        rapport = {'config': config, 'reference': archive['reference'],
                   'ancienne_branche': archive['branche'],
                   'branche': {'nuits': branche}, 'reference_rejouee': False,
                   'branche_rejouees': len(nouvelles), 'branche_reutilisees': len(branche) - len(nouvelles)}
        ecrire(dossier / 'comparaison-reprise.json', rapport)
        lignes = []
        for a, b in zip(archive['reference']['nuits'], branche):
            ligne = {'scenario': a['scenario'], 'graine': a['graine'], 'rejouee': b['rejouee']}
            for cote, n in [('reference', a), ('branche', b)]:
                ms = (n.get('donnees') or {}).get('mesures', {})
                ligne[cote] = {'refus_contact': ms.get('gestes_refuses_contact'),
                              'interruptions': ms.get('approches_impossibles'),
                              'parts': sum('donne une part' in c['texte'] for c in (n.get('donnees') or {}).get('chronique', [])),
                              'suspects_219': n.get('avis', {}).get('total_non_justifies'),
                              'boucles': n.get('boucles'), 'plantage': n['plantage'],
                              'reprises_sans_entree': n.get('reprises_sans_entree', [])}
            lignes.append(ligne)
        ecrire(dossier / 'mesures.json', lignes)
        bilan.update(branche_rejouees=len(nouvelles), branche_reutilisees=len(branche) - len(nouvelles),
                     reference_rejouee=False,
                     reprises_sans_entree=sum(len(n['reprises_sans_entree']) for n in nouvelles),
                     plantages=sum(n['plantage'] is not None for n in nouvelles))
        bilan['ok'] = bilan['tests_code'] == 0 and bilan['plantages'] == 0 and bilan['reprises_sans_entree'] == 0
    except BaseException:
        bilan['erreur'] = traceback.format_exc()
        print(bilan['erreur'], file=sys.stderr, flush=True)
    finally:
        bilan['fin'] = time.time()
        ecrire(dossier / 'fin.json', bilan)
    return int(not bilan['ok'])


if __name__ == '__main__':
    raise SystemExit(main())
