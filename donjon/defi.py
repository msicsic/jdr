"""Scénario du Relais des crues, chargé depuis son état initial déclaré."""
import json
from pathlib import Path

from .monde import Monde

REFUGE = "antichambre"
BEFFROI = "chambre_cloche"
PIED_BEFFROI = "beffroi"
OBJECTIF = "Ramener la cloche d'alarme du beffroi au refuge du relais."
ETAT_INITIAL = Path(__file__).with_name("scenario_relais.json")


def nouveau_defi(seed=1985):
    data = json.loads(ETAT_INITIAL.read_text(encoding="utf-8"))
    data["seed"] = seed
    return Monde(data)


def actualiser(m, lignes):
    from .objectifs import actualiser as actualiser_objectif
    return actualiser_objectif(m, lignes)
