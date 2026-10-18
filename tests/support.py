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
    """Placement d'auteur : le Relais des jalons A à C, sans Ilse, Aubin, ses planches ni le fanal.

    Ces tests isolent Gorm et Brune ; la vie à quatre PNJ est couverte par test_social.
    """
    for id in ("ilse", "aubin", "planches", "fanal"):
        monde.objets.pop(id, None)
        for table in monde.data.values():
            if isinstance(table, dict):
                table.pop(id, None)
    return monde


def calme(monde, *ids):
    """Placement d'auteur : ces PNJ n'ont aucun besoin pressant et restent où ils sont ; leurs
    rondes viennent d'être faites, la routine ne les fait pas bouger de sitôt."""
    from donjon.esprits import lire
    for id in ids:
        besoins = lire(monde, id)["besoins"]
        for b in besoins:
            besoins[b] = 0.0
        for x in monde.objets[id]["profil"]["pulsions"]:
            if "periode" in x["condition"]:
                lire(monde, id)["visites"][x["condition"]["lieu"]] = monde.data["minutes"]
    return monde
