"""Lot 336 : ciblés puis vingt nuits, deux travailleurs réduits, fin toujours écrite.

Ni Luna ni suite complète. Les références disponibles ne sont jamais rejouées.
"""
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
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

TESTS = ('occasion_protection', 'agendas_socle', 'agendas_naissance', 'agendas_evenement',
         'agendas_pieces', 'agendas_proteger', 'agendas_garder', 'agendas_fins',
         'propositions', 'propositions_redites', 'proposer_recours', 'tache_promise_recours',
         'taches_payees', 'dialogues', 'planification', 'defense', 'empathie_peur',
         'demander_cause', 'contrat_engagement', 'preuve_engagement', 'refus_retenus')


def ecrire(chemin, contenu):
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2), encoding='utf-8')


def jouer_branche(tache):
    from donjon import agendas, pnj_propositions
    from donjon.esprits import lire
    offres, contrats, commencements = [], [], []
    proposer = pnj_propositions.executer
    admettre = agendas.admettre_contrat
    commencer = agendas.commencer_service

    def offre(m, id, autre, contenu, lignes):
        r = proposer(m, id, autre, contenu, lignes)
        if r and contenu.get('contrepartie', {}).get('condition', {}).get('proteger'):
            souvenir = next((s for s in reversed(lire(m, id)['memoire']) if s['type'] == 'proposition'), None)
            if souvenir:
                offres.append(dict(souvenir, acteur=id))
        return r

    def contrat(m, id, engagement):
        r = admettre(m, id, engagement)
        if engagement['condition'].get('proteger'):
            contrats.append(dict(acteur=id, **engagement))
        return r

    def commencement(m, id, cible):
        avant = [x for x in agendas.en_cours(m, id) if x['condition'].get('proteger') and x.get('commence') is not None]
        r = commencer(m, id, cible)
        apres = [x for x in agendas.en_cours(m, id) if x['condition'].get('proteger') and x.get('commence') is not None]
        if len(apres) > len(avant):
            commencements.append(dict(acteur=id, cible=cible, minute=m.data['minutes']))
        return r

    with patch.object(pnj_propositions, 'executer', offre), patch.object(agendas, 'admettre_contrat', contrat), patch.object(agendas, 'commencer_service', commencement):
        resultat = banc.jouer_nuit(tache)
    resultat['occasion_336'] = dict(offres=offres, contrats=contrats, commencements=commencements)
    return resultat


def comparer(sortie, reference):
    config = dict(scenarios=['relais', 'mine', 'auberge', 'crue', 'crue_hameau'],
                  graines=[1985, 7, 42, 2024], heures=4., depart='tire', processus=2,
                  verifier=False, empreintes=False, joueurs=dict(banc.JOUEURS))
    revision = banc.git(RACINE, 'rev-parse', reference)
    cache = banc.references.dossier(RACINE)
    with ExitStack() as pile:
        arbre_ref = None

        def arbre():
            nonlocal arbre_ref
            if arbre_ref is None:
                arbre_ref = pile.enter_context(banc.worktree_temporaire(RACINE, revision))
            return arbre_ref

        avant = banc.nuits_du_cote(arbre, revision, config, sortie, 'reference', cache)
        ecrire(sortie / 'reference.json', avant)
    taches = [(s, g, config) for s, g in banc.taches_du_lot(config)]
    with ProcessPoolExecutor(max_workers=2, max_tasks_per_child=1) as pool:
        apres = list(pool.map(jouer_branche, taches))
    ecrire(sortie / 'banc.json', dict(config=config, reference=revision,
                                    nuits_reference=avant, nuits_branche=apres))
    lignes = []
    for a, b in zip(avant, apres):
        m = (b.get('donnees') or {}).get('mesures', {})
        sonde = b['occasion_336']
        sa, sb = [n.get('avis', {}).get('total_non_justifies') for n in (a, b)]
        lignes.append(dict(scenario=b['scenario'], graine=b['graine'],
            suspects_reference=sa, suspects_branche=sb, plantage_reference=a['plantage'],
            plantage_branche=b['plantage'], usurpations=m.get('usurpations'),
            offres=len(sonde['offres']), acceptations=sum(o['issue'] == 'accepte' for o in sonde['offres']),
            protections_nees=len(sonde['contrats']), protections_commencees=len(sonde['commencements']),
            ok=sa is not None and sb is not None and sb <= sa and not a['plantage']
               and not b['plantage'] and m.get('usurpations') == 0))
    ok = all(l['ok'] for l in lignes)
    ecrire(sortie / 'bilan.json', dict(nuits=lignes, ok=ok,
        references_cache=sum('cache' in n for n in avant),
        limite="Une absence d'offre naturelle ne valide pas le service ; les parcours ciblés l'exercent."))
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie', type=Path, required=True)
    parser.add_argument('--reference', default='d8769d8')
    args = parser.parse_args()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    debut = time.monotonic()
    fin = dict(ok=False, pid=os.getpid(), reference=args.reference)
    try:
        ceder()
        fichiers = [*sorted((RACINE / 'donjon').glob('*.py')), RACINE / __file__,
                    *[RACINE / f'tests/test_{nom}.py' for nom in TESTS]]
        ecrire(sortie / 'debut.json', dict(pid=os.getpid(), cwd=str(RACINE),
            commit=banc.git(RACINE, 'rev-parse', 'HEAD'),
            empreintes={str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in fichiers}))
        commande = [sys.executable, 'tools/tests.py', '--processus', '2',
                    '--sortie', str(sortie / 'tests.json'),
                    *[f'tests/test_{nom}.py' for nom in TESTS]]
        with (sortie / 'tests.log').open('w', encoding='utf-8') as flux:
            fin['tests_code'] = subprocess.run(commande, cwd=RACINE, stdout=flux,
                stderr=subprocess.STDOUT, check=False).returncode
        if fin['tests_code'] != 0:
            return 1
        fin['banc_ok'] = comparer(sortie, args.reference)
        fin['ok'] = fin['banc_ok']
        return int(not fin['ok'])
    except BaseException:
        fin['erreur'] = traceback.format_exc()
        return 1
    finally:
        fin['secondes'] = time.monotonic() - debut
        fin['code_retour'] = int(not fin['ok'])
        ecrire(sortie / 'fin.json', fin)  # Dernière écriture, même en cas d'échec.


if __name__ == '__main__':
    raise SystemExit(main())
