"""Scénario de la crypte : état initial déclaré hors du moteur commun."""
import json
from pathlib import Path

from .monde import Monde


ETAT_INITIAL = Path(__file__).with_name("scenario_crypte.json")


def nouveau_monde(seed=1985):
    data = json.loads(ETAT_INITIAL.read_text(encoding="utf-8"))
    data["seed"] = seed
    return Monde(data)
