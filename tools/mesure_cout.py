"""Compteurs déterministes sans modifier le moteur ni appeler Luna.

python tools/mesure_cout.py --reference 42bb9c0 --branche integration --verifier \
    --sortie artifacts/cout.json
Deux processus au plus, priorité réduite. Chaque référence est figée en commit.
--verifier rejoue chaque nuit avec sonde, puis sans sonde (empreintes complètes).
Les temps CPU instrumentés sont indicatifs, jamais un critère de cache/identité.
"""
import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
import inspect
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

import references
from empreintes_nuits import JOUEURS, _h


class Compteurs:
    def __init__(self):
        self.lignes = defaultdict(Counter)

    def ajouter(self, minute, pnj, but, **valeurs):
        self.lignes[(int(minute // 60), pnj, but)].update(valeurs)

    def resultat(self, heures):
        total = Counter()
        for c in self.lignes.values():
            total.update(c)
        return dict(total=dict(sorted(total.items())),
                    par_heure={k: v / heures for k, v in sorted(total.items())},
                    lignes=[dict(heure=h, pnj=p, but=b, **dict(sorted(c.items())))
                            for (h, p, b), c in sorted(self.lignes.items())])


def nuit(depot, scenario, graine, heures, depart, instrumenter=True):
    sys.path.insert(0, str(Path(depot).resolve()))
    from donjon import banc_pnj as banc, deliberation as d, planification as p
    from priorite import ceder
    ceder()
    compte, pile, capture = Compteurs(), [], {}
    creer, chercher, gestes, explorer, choisir = banc.creer, p.chercher, p.gestes, p._explorer_etats, d.choisir
    signature = inspect.signature(chercher)

    def creation(*a, **k):
        capture['monde'] = creer(*a, **k)
        return capture['monde']

    def choix(monde, id, *a, **k):
        # Un choix compare plusieurs buts : ne pas l'attribuer arbitrairement au gagnant.
        compte.ajouter(monde.data['minutes'], id, '__choix__', choix=1)
        return choisir(monde, id, *a, **k)

    def recherche(*a, **k):
        lie = signature.bind(*a, **k).arguments
        cle = (lie['monde'].data['minutes'], lie['id'], lie.get('nom', ''))
        avant = len(p.DIAGNOSTIC)
        pile.append(cle)
        try:
            resultat = chercher(*a, **k)
        finally:
            pile.pop()
        diagnostic = p.DIAGNOSTIC[avant:]
        if len(diagnostic) != 1:
            raise RuntimeError('Contrat diagnostic : une entrée par recherche attendu')
        r = diagnostic[0]
        compte.ajouter(*cle, recherches=1, neuves=int(not r.get('memoire')),
                      reprises=int(bool(r.get('memoire'))), graphes=int(bool(r.get('graphe'))),
                      noeuds_certificats=r.get('preuve_noeuds', 0))
        return resultat

    def exploration(*a, **k):
        r = explorer(*a, **k)
        if not pile:
            raise RuntimeError('Exploration hors recherche')
        compte.ajouter(*pile[-1], passes=1, noeuds=r[1])
        return r

    def generation(*a, **k):
        if not pile:
            raise RuntimeError('Génération hors recherche')
        compte.ajouter(*pile[-1], generations=1)
        for g in gestes(*a, **k):
            # Une proposition immédiate ou différée vaut une sortie du générateur.
            compte.ajouter(*pile[-1], gestes=1)
            yield g

    with ExitStack() as patches:
        patches.enter_context(patch.object(banc, 'creer', creation))
        if instrumenter:
            for objet, nom, remplacement in ((d, 'choisir', choix), (p, 'chercher', recherche),
                    (p, '_explorer_etats', exploration), (p, 'gestes', generation)):
                patches.enter_context(patch.object(objet, nom, remplacement))
        debut = time.process_time()
        _, mesures, donnees = banc.nuit(scenario, graine, heures, JOUEURS[scenario], False, True, None, depart)
        cpu = time.process_time() - debut
    empreintes = {k: _h(donnees[k]) for k in ('chronique', 'recit', 'souvenirs', 'empreintes')}
    empreintes.update(etat=_h(capture['monde'].data), mesures=_h(mesures))
    return dict(compteurs=compte.resultat(heures), empreintes=empreintes, secondes_cpu=cpu)


def lancer(depot, config, instrumenter=True):
    commande = [sys.executable, str(Path(__file__).resolve()), '--ouvrier', str(depot),
                '--config', json.dumps(config)]
    if not instrumenter:
        commande.append('--sans-sonde')
    r = subprocess.run(commande, capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout)


def mesurer(racine, reference, configs, verifier=False, sans_cache=False):
    from comparer_bancs import worktree_temporaire
    commit = references.resoudre(racine, reference)
    if not commit:
        raise ValueError(f'Référence git inconnue : {reference}')
    resultats = []
    with ExitStack() as stack:
        arbre = None
        for config in configs:
            cle = dict(format=1, observation=references.empreinte_fichiers(__file__),
                       config=config, verification=verifier)
            chemin = references.dossier(racine) / commit / 'mesure_cout' / (references.empreinte(json.dumps(cle, sort_keys=True)) + '.json')
            cache = None if sans_cache else references.lire(chemin, cle)
            if cache:
                r = cache['contenu']
            else:
                if arbre is None:
                    arbre = stack.enter_context(worktree_temporaire(racine, commit))
                r = lancer(arbre, config)
                if verifier:
                    bis = lancer(arbre, config)
                    temoin = lancer(arbre, config, False)
                    r['verification'] = dict(determinisme=r['compteurs'] == bis['compteurs'],
                        empreintes=r['empreintes'] == bis['empreintes'] == temoin['empreintes'])
                    r['cpu_temoin'] = temoin['secondes_cpu']
                    if not all(r['verification'].values()):
                        raise RuntimeError(f'Contrôle échoué : {config} : {r["verification"]}')
                if not sans_cache:
                    references.ecrire(chemin, cle, r)
            resultats.append(dict(commit=commit, config=config, cache=bool(cache), **r))
            print(f'{commit[:8]} {config}: {r["compteurs"]["total"]}; CPU {r["secondes_cpu"]:.2f}s; cache={bool(cache)}', flush=True)
    return resultats


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', default='42bb9c0')
    ap.add_argument('--branche', default='integration')
    ap.add_argument('--sortie', default='artifacts/cout.json')
    ap.add_argument('--scenario', choices=JOUEURS)
    ap.add_argument('--graine', type=int, default=1985)
    ap.add_argument('--heures', type=float, default=12)
    ap.add_argument('--depart', choices=('fixe', 'tire'), default='fixe')
    ap.add_argument('--verifier', action='store_true')
    ap.add_argument('--sans-cache', action='store_true')
    ap.add_argument('--ouvrier', help=argparse.SUPPRESS)
    ap.add_argument('--config', help=argparse.SUPPRESS)
    ap.add_argument('--sans-sonde', action='store_true', help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.ouvrier:
        print(json.dumps(nuit(args.ouvrier, **json.loads(args.config), instrumenter=not args.sans_sonde)))
        return
    if args.heures <= 0:
        ap.error('--heures doit être positif')
    configs = [dict(scenario=s, graine=args.graine, heures=args.heures, depart=d)
               for s, d in ([(args.scenario, args.depart)] if args.scenario else
                            [('auberge', 'fixe'), ('auberge', 'tire'), ('mine', 'fixe')])]
    racine = Path(__file__).resolve().parents[1]
    resultat = []
    for ref in (args.reference, args.branche):
        resultat.extend(mesurer(racine, ref, configs, args.verifier, args.sans_cache))
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf-8')
    print('CPU indicatif ; les temps en cache proviennent d’autres conditions de charge.')


if __name__ == '__main__':
    main()
