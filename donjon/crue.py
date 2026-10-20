"""Scénario de la crue : le Relais des crues, dont l'eau monte (``eau.py``).

Dérivé du Relais (``defi.py``) : mêmes lieux, objets et personnages ; les salles basses sont
sous le refuge, la galerie au-dessus, et le scénario déclare les bornes de la crue.
"""
import json
from pathlib import Path

from .monde import Monde

ETAT_INITIAL = Path(__file__).with_name("scenario_crue.json")


def nouvelle_crue(seed=1985):
    data = json.loads(ETAT_INITIAL.read_text(encoding="utf-8"))
    data["seed"] = seed
    return Monde(data)
