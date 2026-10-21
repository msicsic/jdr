"""Scénario du Relais des crues, chargé depuis son état initial déclaré."""
from pathlib import Path

from .monde import depuis_scenario

REFUGE = "antichambre"
BEFFROI = "chambre_cloche"
PIED_BEFFROI = "beffroi"
OBJECTIF = "Ramener la cloche d'alarme du beffroi au refuge du relais."
ETAT_INITIAL = Path(__file__).with_name("scenario_relais.json")


def nouveau_defi(seed=1985, depart="tire"):
    return depuis_scenario(ETAT_INITIAL, seed, depart)


def actualiser(m, lignes):
    from .objectifs import actualiser as actualiser_objectif
    return actualiser_objectif(m, lignes)
