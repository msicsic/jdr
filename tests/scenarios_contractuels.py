"""Entrées d'auteur des tests de contrats antérieurs aux occasions du lot 186.

Les scénarios de jeu gardent les nouveaux moyens. Ces scènes isolées retrouvent
leur répartition de ressources et leurs observations déclarées, avant que Monde
installe corps, relations et perceptions. Aucun comportement du moteur modifié.
"""
import copy
import json
from pathlib import Path

from donjon.monde import Monde

RACINE = Path(__file__).resolve().parents[1]
CORRECTIONS = json.loads((Path(__file__).with_name('fixtures') /
                         'avant_occasions_186.json').read_text(encoding='utf-8'))['scenarios']


def donnees(nom):
    d = json.loads((RACINE / 'donjon' / ('scenario_' + nom + '.json')).read_text(encoding='utf-8'))
    for correction in CORRECTIONS[nom]:
        noeud = d
        for cle in correction['chemin'][:-1]:
            noeud = noeud[cle]
        cle = correction['chemin'][-1]
        if correction.get('retirer'):
            noeud.pop(cle, None)
        else:
            noeud[cle] = copy.deepcopy(correction['avant'])
    return d


def _nouveau(nom, seed=1985, depart='tire'):
    d = donnees(nom)
    d['seed'] = seed
    d.setdefault('depart', {})['mode'] = depart
    return Monde(d)


def nouveau_defi(seed=1985, depart='tire'):
    return _nouveau('relais', seed, depart)


def nouvelle_crue(seed=1985, depart='tire'):
    return _nouveau('crue', seed, depart)


def nouveau_mine(seed=1985, depart='tire'):
    return _nouveau('mine', seed, depart)


def nouveau_auberge(seed=1985, depart='tire'):
    return _nouveau('auberge', seed, depart)


def creer(scenario, graine=1985, depart='tire'):
    if scenario not in CORRECTIONS:
        from donjon.banc_pnj import creer as creer_courant
        return creer_courant(scenario, graine, depart)
    from donjon.spatial import installer
    m = _nouveau(scenario, graine, depart)
    installer(m)
    return m
