"""Diagnostic sans modification du moteur, fenêtre 480–720, auberge 1985.

Les compteurs de gestes mesurent les générations réelles (hors suites reprises
du graphe), et non les arêtes uniques. Les temps sont des temps CPU.
"""
import argparse
from collections import Counter
import cProfile
import json
from pathlib import Path
import pstats
import sys
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--depot', required=True)
    ap.add_argument('--depart', choices=('fixe', 'tire'), required=True)
    ap.add_argument('--sortie', required=True)
    ap.add_argument('--profil', action='store_true')
    ap.add_argument('--detail', action='store_true', help='Compter toutes les passes et les suites normalisées')
    args = ap.parse_args()
    sys.path.insert(0, str(Path(args.depot).resolve()))
    from donjon import banc_pnj, planification as p
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    banc_pnj.ceder()
    sortie = Path(args.sortie).resolve()
    sortie.parent.mkdir(parents=True, exist_ok=True)
    chercher, gestes, observer = p.chercher, p.gestes, banc_pnj._oisifs_urgents
    actif, pile, lignes, bornes = [False], [], [], {}
    profil = cProfile.Profile(timer=time.process_time)
    explorer, suites = p._explorer_etats, p._suites

    def explorer_etats(*a, **k):
        debut = time.process_time()
        avant = pile[-1]['generations'] if actif[0] and pile else 0
        resultat = explorer(*a, **k)
        if actif[0] and pile:
            pile[-1]['passes'] += 1
            pile[-1]['developpes'] += resultat[1]
            pile[-1]['explorations'].append(dict(noeuds=resultat[1], etats=resultat[2],
                generations=pile[-1]['generations']-avant,
                cpu=time.process_time()-debut, decouvrir=k.get('decouvrir', False),
                furtif=getattr(a[0], '_explore_furtif', False),
                emplois=None if a[0].emplois is None else sorted(a[0].emplois)))
        return resultat

    def normaliser(*a, **k):
        resultat = suites(*a, **k)
        if actif[0] and pile:
            pile[-1]['normalisations'] += 1
            pile[-1]['suites'] += len(resultat)
        return resultat

    def generer(v, e, *a, **k):
        if not actif[0] or not pile:
            yield from gestes(v, e, *a, **k)
            return
        compte = pile[-1]
        compte['generations'] += 1
        for g in gestes(v, e, *a, **k):
            compte['successeurs'] += 1
            if isinstance(g, tuple):
                for etape in g[2]:
                    compte['familles'][etape.get('operation', '?')] += 1
            else:
                compte['familles']['differe'] += 1
            yield g

    def rechercher(monde, id, *a, **k):
        if not actif[0]:
            return chercher(monde, id, *a, **k)
        r = dict(minute=monde.data['minutes'], pnj=id, but=k.get('nom', ''),
                 generations=0, successeurs=0, familles=Counter(),
                 passes=0, developpes=0, normalisations=0, suites=0, explorations=[],
                 salle=monde.objets[id].get('lieu'),
                 portes=[o for o, x in monde.objets.items() if x.get('lieu') == id])
        pile.append(r)
        avant = len(p.DIAGNOSTIC or [])
        debut = time.process_time()
        try:
            return chercher(monde, id, *a, **k)
        finally:
            r['cpu'] = time.process_time() - debut
            pile.pop()
            if p.DIAGNOSTIC is not None and len(p.DIAGNOSTIC) > avant:
                r['diagnostic'] = dict(p.DIAGNOSTIC[-1])
            lignes.append(r)

    def relever(monde):
        minute = monde.data['minutes']
        if minute >= 480 and 'debut' not in bornes:
            monde.sauver(sortie.with_suffix('.480.json'))
            bornes['debut'] = time.process_time()
            actif[0] = True
            if args.profil:
                profil.enable()
        if minute >= 720 and 'fin' not in bornes:
            profil.disable()
            actif[0] = False
            bornes['fin'] = time.process_time()
            monde.sauver(sortie.with_suffix('.720.json'))
            recharge = Monde.charger(sortie.with_suffix('.720.json'))
            bornes['recharge'] = dict(monde=monde.data == recharge.data,
                regarder=regarder(monde) == regarder(recharge),
                scene=scene_percue(monde) == scene_percue(recharge))
            assert all(bornes['recharge'].values())
        return observer(monde)

    p.chercher, p.gestes, banc_pnj._oisifs_urgents = rechercher, generer, relever
    if args.detail:
        p._explorer_etats, p._suites = explorer_etats, normaliser
    debut = time.process_time()
    banc_pnj.nuit('auberge', 1985, 12, 'dortoir', False, True, None, args.depart)
    profil.disable()
    resultat = dict(depot=args.depot, depart=args.depart, profil=args.profil, detail=args.detail,
                    cpu_total=time.process_time()-debut,
                    cpu_tranche=bornes['fin']-bornes['debut'],
                    recharge=bornes['recharge'], recherches=lignes)
    if args.profil:
        profil.dump_stats(str(sortie.with_suffix('.prof')))
        resultat['fonctions'] = [dict(fichier=f, ligne=l, nom=n, appels=nc, propre=tt, cumule=ct)
            for (f, l, n), (cc, nc, tt, ct, callers) in pstats.Stats(profil).stats.items()]
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({k:v for k,v in resultat.items() if k not in ('recherches', 'fonctions')}), flush=True)


if __name__ == '__main__':
    main()
