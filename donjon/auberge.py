"""Scénario de l'auberge du Col-Pendu, chargé depuis son état initial déclaré."""
from pathlib import Path

from .monde import depuis_scenario

DEPART = "dortoir"
ETAT_INITIAL = Path(__file__).with_name("scenario_auberge.json")


def nouveau_auberge(seed=1985, depart="tire"):
    return depuis_scenario(ETAT_INITIAL, seed, depart)
