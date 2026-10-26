"""Profil CPU comparé de la tranche 480–720, sans modifier le moteur.

Chaque version joue son propre préfixe afin de conserver ses mémoires privées.
Le profil commence après la capture à 480 et s'arrête à 720, avant le bilan.
"""
import argparse
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
    ap.add_argument('--sans-profil', action='store_true')
    args = ap.parse_args()
    sys.path.insert(0, str(Path(args.depot).resolve()))
    from donjon import banc_pnj, deliberation, planification
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    banc_pnj.ceder()
    sortie = Path(args.sortie).resolve()
    sortie.parent.mkdir(parents=True, exist_ok=True)
    profil = cProfile.Profile(timer=time.process_time)
    relever, creer = banc_pnj._oisifs_urgents, banc_pnj.creer
    capture = {}
    def creation(*a, **k):
        capture['monde'] = creer(*a, **k)
        return capture['monde']
    def observer(monde):
        minute = monde.data['minutes']
        repere = int(minute // 60)
        if repere != capture.get('repere'):
            capture['repere'] = repere
            print(f'{minute:g} min; CPU {time.process_time():.2f} s', flush=True)
        if minute >= 480 and 'debut' not in capture:
            monde.sauver(sortie.with_suffix('.480.json'))
            capture.update(debut=time.process_time(), choix=dict(deliberation.COMPTES),
                           recherches=len(planification.DIAGNOSTIC or []))
            if not args.sans_profil:
                profil.enable()
        if minute >= 720 and 'fin' not in capture:
            profil.disable()
            capture.update(fin=time.process_time(), choix_fin=dict(deliberation.COMPTES),
                           recherches_fin=len(planification.DIAGNOSTIC or []))
        return relever(monde)
    banc_pnj.creer, banc_pnj._oisifs_urgents = creation, observer
    debut = time.process_time()
    _, mesures, donnees = banc_pnj.nuit('auberge', 1985, 12, 'dortoir', False, True, None, args.depart)
    total = time.process_time() - debut
    profil.disable()
    monde = capture['monde']
    monde.sauver(sortie.with_suffix('.720.json'))
    recharge = Monde.charger(sortie.with_suffix('.720.json'))
    controle = dict(monde=monde.data == recharge.data,
                    regarder=regarder(monde) == regarder(recharge),
                    scene=scene_percue(monde) == scene_percue(recharge))
    assert all(controle.values()), controle
    stats = pstats.Stats(profil) if not args.sans_profil else None
    if stats:
        profil.dump_stats(str(sortie.with_suffix('.prof')))
    fonctions = [] if stats is None else [dict(fichier=f, ligne=l, nom=n, primitifs=cc,
        appels=nc, propre=tt, cumule=ct,
        appelants=[dict(fichier=k[0], ligne=k[1], nom=k[2], valeurs=v) for k, v in callers.items()])
        for (f, l, n), (cc, nc, tt, ct, callers) in stats.stats.items()]
    resultat = dict(depot=args.depot, depart=args.depart, profile=stats is not None,
        cpu_total=total, cpu_tranche=capture['fin']-capture['debut'],
        choix={k: v-capture['choix'].get(k, 0) for k, v in capture['choix_fin'].items()},
        recherches=capture['recherches_fin']-capture['recherches'],
        recharge=controle, mesures=mesures, fonctions=fonctions)
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({k:v for k,v in resultat.items() if k not in ('fonctions','mesures')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
