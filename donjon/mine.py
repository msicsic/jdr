"""Scénario de la mine de Cendrefer, chargé depuis son état initial déclaré.

Un camp de mineurs coupé du monde par un éboulement : sept personnages, des vivres comptés, du bois
sous clé, une paie dans son coffre, des galeries sans lumière. Tout est donnée de scénario ; aucune
règle propre à la mine n'entre dans le moteur.
"""
import json
from pathlib import Path

from .monde import Monde

ETAT_INITIAL = Path(__file__).with_name("scenario_mine.json")


def nouveau_mine(seed=1985):
    data = json.loads(ETAT_INITIAL.read_text(encoding="utf-8"))
    data["seed"] = seed
    return Monde(data)
