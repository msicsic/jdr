"""Validation bornée du lot 330, deux travailleurs réduits, fin écrite même sur échec.

Ne lance ni Luna ni la suite complète. La référence est résolue en commit,
ses nuits disponibles sont relues du cache commun, les absentes rangées une fois.
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

TESTS = ('demander_cause', 'empathie_peur', 'empathie', 'peur_transmise', 'ou_est_il',
         'refus_retenus', 'echanges_suite', 'echanges_argent', 'social',
         'parole_commune', 'emissions_parole', 'planification', 'defense', 'securite')


def ecrire(chemin, contenu):
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2), encoding='utf-8')


def jouer_branche(tache):
    """Sonde en lecture seule : premier choix suivant une réponse effectivement crue."""
    from donjon import causes, deliberation
    from donjon.esprits import lire
    from donjon.temps import instant
    demandes, reponses, reactions, attendues = [], [], [], {}
    demander, choisir = causes.demander, deliberation.choisir

    def question(m, id, proche, lignes):
        resultat = demander(m, id, proche, lignes)
        cs = m.data.get('chronique', [])
        # Le dernier échange seulement ; une revalidation muette n'est pas une demande.
        nouveaux = [c for c in cs if c.get('demande_cause') and c['pnj'] == id
                    and c.get('instant') == instant(m)]
        if nouveaux:
            cle = (id, proche, instant(m))
            if not any(tuple(d['cle']) == cle for d in demandes):
                demandes.append(dict(cle=cle, issue=nouveaux[-1]['demande_cause']['issue']))
                rs = [c for c in cs if c.get('reponse_cause', {}).get('a') == id
                      and c.get('instant') == instant(m)]
                if rs:
                    r = dict(id=id, locuteur=proche, instant=instant(m), **rs[-1]['reponse_cause'])
                    reponses.append(r)
                    if r['reception'] == 'crue':
                        attendues[id] = r
        return resultat

    def choix(m, id, minute):
        resultat = choisir(m, id, minute)
        if id in attendues:
            r = attendues.pop(id)
            i = lire(m, id)['intention']
            reactions.append(dict(id=id, reponse=r, instant=instant(m),
                                  intention=json.loads(json.dumps(i))))
        return resultat

    with patch.object(causes, 'demander', question), patch.object(deliberation, 'choisir', choix):
        resultat = banc.jouer_nuit(tache)
    resultat['cause_330'] = dict(demandes=demandes, reponses=reponses,
                                 premiers_choix_suivants=reactions,
                                 sans_choix_suivant=list(attendues.values()))
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
        sonde = b['cause_330']
        sa, sb = [n.get('avis', {}).get('total_non_justifies') for n in (a, b)]
        lignes.append(dict(scenario=b['scenario'], graine=b['graine'],
            suspects_reference=sa, suspects_branche=sb,
            plantage_reference=a['plantage'], plantage_branche=b['plantage'],
            usurpations=m.get('usurpations'), demandes=len(sonde['demandes']),
            reponses=len(sonde['reponses']),
            reponses_crues=sum(r['reception'] == 'crue' for r in sonde['reponses']),
            choix_suivants=len(sonde['premiers_choix_suivants']),
            ok=sa is not None and sb is not None and sb <= sa and not a['plantage']
               and not b['plantage'] and m.get('usurpations') == 0))
    ecrire(sortie / 'bilan.json', dict(nuits=lignes, ok=all(l['ok'] for l in lignes),
        references_cache=sum('cache' in n for n in avant),
        limite='Premier choix après réception : succession observée, pas preuve causale.'))
    return all(l['ok'] for l in lignes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie', type=Path, required=True)
    parser.add_argument('--reference', default='f08ef58')
    args = parser.parse_args()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    ceder()
    debut = time.monotonic()
    fin = dict(ok=False, pid=os.getpid(), reference=args.reference)
    try:
        fichiers = [*sorted((RACINE / 'donjon').glob('*.py')),
                    RACINE / 'tests/test_demander_cause.py']
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
        ecrire(sortie / 'fin.json', fin)  # Dernière écriture, succès comme échec.


if __name__ == '__main__':
    raise SystemExit(main())
