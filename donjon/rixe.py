"""Épreuve de force du Relais, déclarée par données ; le contrôle doux ne change que la douceur."""
from pathlib import Path
from .monde import depuis_scenario


def nouvelle_rixe(seed=1985, depart="tire", douce=False):
    return depuis_scenario(Path(__file__).with_name("scenario_rixe_douce.json" if douce else "scenario_rixe.json"), seed, depart)
