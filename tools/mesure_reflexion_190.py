"""Sonde expérimentale, sans changement du moteur. Un processus par invocation.

--variante complete : nuit témoin ; --apparier échantillonne la première
exploration neuve par heure, PNJ et but, sur une copie de la Vue initiale
et sans graphe repris (avant endurer, pas les choix de but ni REFERENCE).
Les variantes libres conservent les caches et ne changent que la profondeur.
"""
import argparse
import copy
import gzip
import inspect
import json
from pathlib import Path
import sys
import time
from collections import Counter, defaultdict
from contextlib import ExitStack
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj as b, planification as p
from donjon.caractere import caracteristique
from donjon.esprits import lire
from priorite import ceder
import audit_nuits as audit
from empreintes_nuits import _h


def profondeur(monde, ident, motif, variante, maximum):
    if variante == 'complete':
        return maximum
    # INT modulée : les malus corporels réduisent déjà les caractéristiques.
    limite = max(2, min(8, 2 + caracteristique(monde, ident, 'INT') // 3))
    if variante == 'enjeu':
        from donjon.deliberation import DESESPOIR
        besoins = lire(monde, ident)['besoins']
        if motif in ('securite', 'devoir') or besoins.get(motif, 0) >= DESESPOIR:
            return maximum
    return min(maximum, limite)


def richesse(chronique, noms):
    episodes, per, comptes = set(), {i: set() for i in noms}, Counter()
    for c in chronique:
        t = c['texte']
        tests = [('demande', ' demande ' in t and 'de faire en sorte que ' not in t),
                 ('offre', ' propose à ' in t and 'la promesse que ' not in t),
                 ('promesse_contrepartie', ' propose à ' in t and 'la promesse que ' in t),
                 ('delegation', 'de faire en sorte que ' in t),
                 ('travail_paye', ' offre ' in t and ' fasse en sorte que ' in t),
                 ('avis', c.get('avis_exprime')), ('dispute', c.get('dispute')),
                 ('service', c.get('cause') == 'service_rendu'),
                 ('interposition', "s'interpose" in t), ('appel', ' appelle ' in t)]
        for famille, oui in tests:
            if oui:
                auteur = c.get('relation') if famille == 'service' else c['pnj']
                episodes.add((famille, auteur, t))
                per.setdefault(auteur, set()).add(famille)
                comptes[famille] += 1
    return dict(S=len(episodes), F=len(comptes), D={k: len(v) for k, v in per.items()}, occurrences=comptes)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scenario', choices=['mine', 'auberge', 'crue_hameau'], required=True)
    ap.add_argument('--heures', type=float, default=12)
    ap.add_argument('--variante', choices=['complete', 'int', 'enjeu'], default='complete')
    ap.add_argument('--apparier', action='store_true')
    ap.add_argument('--sortie', type=Path, required=True)
    args = ap.parse_args()
    ceder()
    capture, pile, paires, echantillon = {}, [], [], set()
    compte = defaultdict(Counter)
    creer, chercher, explorer, explorer_etats = b.creer, p.chercher, p._explorer, p._explorer_etats
    sig = inspect.signature(chercher)

    def creation(*a, **k):
        capture['monde'] = creer(*a, **k)
        return capture['monde']

    def recherche(*a, **k):
        lie = sig.bind(*a, **k)
        lie.apply_defaults()
        x = lie.arguments
        x['profondeur'] = profondeur(x['monde'], x['id'], x['motif'], args.variante, x['profondeur'])
        cle = (x['id'], x['nom'])
        pile.append((cle, x))
        n = len(p.DIAGNOSTIC)
        debut = time.process_time()
        try:
            r = chercher(**x)
        finally:
            pile.pop()
        diag = p.DIAGNOSTIC[n:]
        c = compte[cle]
        c.update(recherches=1, neuves=int(not diag[-1]['memoire']), graphes=int(diag[-1]['graphe']),
                 certificats=diag[-1].get('preuve_noeuds', 0))
        c['cpu'] += time.process_time() - debut
        return r

    def exploration_etats(*a, **k):
        r = explorer_etats(*a, **k)
        compte[pile[-1][0]]['noeuds'] += r[1]
        return r

    def exploration(v, depart, but, vises, prof, noeuds, faute, tenir=False, graphe=None, **kw):
        # Copie avant toute découverte de lumière/discrétion par le témoin.
        cle_echantillon = (int(v.monde.data['minutes'] // 60), *pile[-1][0])
        sonder = args.apparier and cle_echantillon not in echantillon
        initiale = copy.deepcopy(v) if sonder else None
        if sonder:
            echantillon.add(cle_echantillon)
        r = explorer(v, depart, but, vises, prof, noeuds, faute, tenir, graphe, **kw)
        if initiale is not None:
            cle, x = pile[-1]
            for variante in ('int', 'enjeu'):
                limite = profondeur(v.monde, v.id, x['motif'], variante, prof)
                debut = time.process_time()
                # Appel direct : ne compte pas les ombres dans les compteurs du témoin.
                with patch.object(p, '_explorer_etats', explorer_etats):
                    s = explorer(copy.deepcopy(initiale), depart, but, vises, limite, noeuds, faute, tenir, None, **kw)
                def plan(z):
                    return None if z[0] is None else dict(cout=z[0][0], etapes=[p._degeler_etape(e) for e in z[0][1]])
                paires.append(dict(minute=v.monde.data['minutes'], pnj=v.id, but=cle[1], variante=variante,
                                   profondeur=limite, complete=plan(r), limite=plan(s), noeuds=s[1],
                                   cpu=time.process_time()-debut, reference_bornee=r[1] >= noeuds))
        return r

    releves = []
    oisifs = b._oisifs_urgents
    def observation(monde):
        releves.append(audit._releve(monde))
        return oisifs(monde)

    with ExitStack() as stack:
        for obj, nom, f in [(b, 'creer', creation), (p, 'chercher', recherche),
                            (p, '_explorer', exploration), (p, '_explorer_etats', exploration_etats),
                            (b, '_oisifs_urgents', observation)]:
            stack.enter_context(patch.object(obj, nom, f))
        debut = time.process_time()
        _, mesures, donnees = b.nuit(args.scenario, 1985, args.heures,
                                    'dortoir' if args.scenario == 'auberge' else
                                    'galerie' if args.scenario == 'mine' else 'chambre_cloche',
                                    False, True, None, 'fixe')
        cpu = time.process_time() - debut
    monde = capture['monde']
    n = dict(scenario=args.scenario, graine=1985, heures=args.heures, depart='fixe',
             donnees=donnees, final=audit._final(monde), releves=releves, plantage=None)
    n.update(variante=args.variante, cpu=cpu, paires=paires,
             compteurs=[dict(pnj=i, but=but, **c) for (i, but), c in sorted(compte.items())],
             richesse=richesse(donnees['chronique'], n['final']['noms']),
             audit=audit.analyser_nuit(n), etat=monde.data,
             empreinte_etat=_h(monde.data))
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.sortie, 'wt', encoding='utf-8') as f:
        json.dump(n, f, ensure_ascii=False)
    print(json.dumps(dict(sortie=str(args.sortie), cpu=cpu, recherches=mesures['recherches'],
                         paires=len(paires), richesse=n['richesse']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
