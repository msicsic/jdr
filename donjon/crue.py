"""Scénario de la crue : le Relais des crues, dont l'eau monte (``eau.py``).

Dérivé du Relais (``defi.py``) : mêmes lieux, objets et personnages ; les salles basses sont
sous le refuge, la galerie au-dessus, et le scénario déclare les bornes de la crue.
"""
from pathlib import Path

from .monde import depuis_scenario

ETAT_INITIAL = Path(__file__).with_name("scenario_crue.json")


def nouvelle_crue(seed=1985, depart="tire"):
    return depuis_scenario(ETAT_INITIAL, seed, depart)
