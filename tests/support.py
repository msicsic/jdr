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
    """Placement d'auteur : le propriétaire des vivres vient de lui refuser une part, et elle n'a
    pas de quoi la lui payer (``sans_le_sou``).

    Un affamé demande, puis achète s'il le peut, avant de voler ; ces tests portent sur ce qui
    suit le refus quand il ne reste que voler ou attendre.
    """
    from donjon.deliberation import retenir_refus
    retenir_refus(monde, id, par, "demander", "refus", objet="vivres")
    from donjon.esprits import lire
    lire(monde, id)["eveil"] = None  # Le refus est antérieur à cette scène d'auteur.
    return sans_le_sou(monde, id)


def sans_le_sou(monde, *ids):
    """Placement d'auteur : ils n'ont pas une pièce sur eux."""
    for id in ids:
        monde.data["finances_pnj"][id] = 0
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
    for o in monde.objets.values():
        if "liens" in o.get("profil", {}):
            o["profil"]["liens"] = {x: a for x, a in o["profil"]["liens"].items() if x in monde.objets or x == "joueur"}
        if "protege" in o.get("profil", {}):
            o["profil"]["protege"] = [x for x in o["profil"]["protege"] if x in monde.objets]
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


def regarder(monde, qui, vers):
    """Placement d'auteur : ``qui`` (un PNJ ou le joueur) regarde vers un personnage, le joueur, un
    objet ou une case de sa salle."""
    from donjon.spatial import orientation_vers, position_cible
    if qui == "joueur":
        o = {**monde.joueur, "lieu": monde.joueur["salle"]}
        cible = tuple(vers) if not isinstance(vers, str) else position_cible(monde, vers, o["lieu"])
        monde.joueur["orientation"] = orientation_vers(tuple(o["position"]), cible) or monde.joueur.get("orientation")
        return monde
    o = monde.objets[qui]
    if vers == "joueur":
        cible = tuple(monde.joueur["position"])
    elif isinstance(vers, str):
        cible = position_cible(monde, vers, o["lieu"])
    else:
        cible = tuple(vers)
    o["orientation"] = orientation_vers(tuple(o["position"]), cible) or o.get("orientation", "sud")
    return monde


def lier(monde, id, autre, fiable, source="savoir"):
    """Placement d'auteur : un lien chiffré, remplaçant l'ancien savoir booléen des scènes."""
    from donjon import relations
    from donjon.esprits import esprit
    axes = {"confiance": 65 if fiable else 15, "affection": 20 if fiable else 0}
    r = relations._nouvelle(axes, monde.data["minutes"])
    r["source"] = source
    esprit(monde, id)["relations"][autre] = r


def relation(monde, id, autre):
    """Avis dérivé, pour les assertions des anciens contrats de parole (sans croyance stockée)."""
    from donjon import relations
    r = relations.envers(monde, id, autre)
    return {"valeur": relations.fiable(monde, id, autre), "source": r["source"], "minute": r["minute"]}
