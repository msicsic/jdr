"""La crue et deux évacués du hameau ; uniquement des données de scénario."""
from pathlib import Path
from .monde import depuis_scenario


def nouvelle_crue_hameau(seed=1985, depart="tire"):
    return depuis_scenario(Path(__file__).with_name("scenario_crue_hameau.json"), seed, depart)
