"""Doubles de test communs aux parcours qui simulent déjà les réponses du MJ."""

from unittest.mock import patch

from donjon.mj import MJOpenAI


def simuler_couverture(test):
    """Les tests des autres contrats fournissent un plan tenu pour fidèle.

    Les refus et corrections réels de cette revue sont exercés dans
    test_improvisation, où les appels bruts sont simulés séparément.
    """
    controle = patch.object(MJOpenAI, "_auditer_action")
    controle.start()
    test.addCleanup(controle.stop)


def sans_budget(monde):
    """Lieu sans budget d'invention : ces tests portent sur les capacités elles-mêmes."""
    for salle in monde.data["salles"].values():
        salle.pop("potentiel_invention", None)
    return monde
