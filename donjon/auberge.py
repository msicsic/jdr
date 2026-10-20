"""Scénario de l'auberge du Col-Pendu, chargé depuis son état initial déclaré."""
import json
from pathlib import Path

from .monde import Monde

DEPART = "dortoir"
ETAT_INITIAL = Path(__file__).with_name("scenario_auberge.json")


def nouveau_auberge(seed=1985):
    data = json.loads(ETAT_INITIAL.read_text(encoding="utf-8"))
    data["seed"] = seed
    return Monde(data)
