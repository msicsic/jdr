"""Scène d'essai de fabrication, chargée depuis son état initial déclaré."""
import json
from pathlib import Path

from .monde import Monde

ETAT_INITIAL = Path(__file__).with_name("scenario_atelier.json")


def nouveau_atelier(seed=1985):
    data = json.loads(ETAT_INITIAL.read_text(encoding="utf-8"))
    data["seed"] = seed
    return Monde(data)
