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


def refusee(monde, id="brune", par="marchand"):
    """Placement d'auteur : le propriétaire des vivres vient de lui refuser une part.

    Un affamé demande avant de voler ; ces tests portent sur ce qui suit le refus.
    """
    from donjon.esprits import memoriser
    memoriser(monde, id, {"type": "refus", "de": par, "operation": "demander", "raison": "refus", "objet": "vivres"})
    return monde


def sans_evacues(monde):
    """Placement d'auteur : le Relais des jalons A à C, sans Ilse, Aubin ni le fanal du refuge.

    Ces tests isolent Gorm et Brune ; la vie à quatre PNJ est couverte par test_social.
    """
    for id in ("ilse", "aubin", "fanal"):
        monde.objets.pop(id, None)
        for table in monde.data.values():
            if isinstance(table, dict):
                table.pop(id, None)
    return monde
