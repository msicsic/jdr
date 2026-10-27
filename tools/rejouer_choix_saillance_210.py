"""Contrôle C/S/REFERENCE à caches froids des captures où S diffère de R.

Sépare un effet de saillance d'un effet du plafond du témoin courant.
"""
import argparse
import copy
from contextlib import ExitStack
import json
import math
from unittest.mock import patch

import mesure_saillance_210 as s
from bilan_saillance_210 import lire


def premieres_divergences(dossier):
    """Complète l'échantillon horaire par les premiers écarts des nuits 12 h.

    Rejoue le témoin jusqu'à cet écart et garde le dernier choix de l'acteur
    qui le précède. Aucune référence git ni sauvegarde utilisateur sollicitée.
    """
    for path in sorted(dossier.glob('*-12h-complete.json.gz')):
        a = lire(path)
        autre = path.with_name(path.name.replace('-complete.', '-saillant.'))
        if not autre.exists():
            continue
        b = lire(autre)
        ecart = next(((x, y) for x, y in zip(a['donnees']['chronique'], b['donnees']['chronique'])
                      if x != y), None)
        if ecart is None:
            continue
        event = ecart[0]
        ident, minute = event['pnj'], event['minute']
        if ident not in a['final']['noms']:
            continue
        sortie = dossier / 'choix' / (path.stem + '-premier-ecart.json.gz')
        if sortie.exists():
            continue
        capt = {}
        choisir = s.d.choisir
        def choix(monde, qui, quand):
            if qui == ident and monde.data['minutes'] <= minute:
                capt.update(etat=copy.deepcopy(monde.data), pnj=qui, minute=quand,
                            divergence=dict(complete=event, saillant=ecart[1]))
            return choisir(monde, qui, quand)
        for cache in (s.p._MEMOIRE, s.p._GRAPHES, s.p._IMPOSSIBLES):
            cache.clear()
        with patch.object(s.d, 'choisir', choix):
            s.b.nuit(a['scenario'], a['graine'], math.ceil(minute + 1)/60,
                     s.JOUEURS[a['scenario']], False, False, None, 'fixe')
        if capt:
            s.sauver(sortie, capt)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=s.Path)
    args = ap.parse_args()
    s.ceder()
    premieres_divergences(args.dossier)
    lignes = []
    for path in sorted((args.dossier / 'choix').glob('*.gz')):
        entree = lire(path)
        ligne = dict(capture=path.name, pnj=entree['pnj'], minute=entree['minute'])
        for mode in ('complete', 'saillant', 'reference'):
            recherches = []
            def chercher(*a, **k):
                x = s.SIGNATURE.bind(*a, **k)
                x.apply_defaults()
                x = dict(x.arguments)
                if mode == 'reference':
                    x.update(noeuds=s.p.REFERENCE, emplois=None)
                r = s.CHERCHER(**x)
                recherches.append(dict(but=x['nom'], plan=s.plan(r)))
                return r
            m = s.Monde(copy.deepcopy(entree['etat']))
            with ExitStack() as stack:
                for nom in ('_MEMOIRE', '_GRAPHES', '_IMPOSSIBLES'):
                    stack.enter_context(patch.object(s.p, nom, {}))
                for obj, nom, val in ((s.p, 'chercher', chercher), (s.p, '_entrees', s.entrees),
                                      (s.p.Vue, 'agissables', s.agissables)):
                    stack.enter_context(patch.object(obj, nom, val))
                stack.enter_context(s.variante(mode))
                diag = stack.enter_context(s.p.diagnostics())
                s.d.choisir(m, entree['pnj'], entree['minute'])
            ligne[mode] = dict(intention=copy.deepcopy(s.lire(m, entree['pnj'])['intention']),
                               recherches=recherches, diagnostics=diag)
        lignes.append(ligne)
        s.sauver(args.dossier.parent / 'rejeux-choix.json.gz', lignes)
        print(json.dumps(dict(capture=path.name,
                              C_S=ligne['complete']['intention'] == ligne['saillant']['intention'],
                              C_R=ligne['complete']['intention'] == ligne['reference']['intention'])), flush=True)


if __name__ == '__main__':
    main()
