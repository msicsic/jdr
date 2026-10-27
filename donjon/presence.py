"""Présence dans les lieux, distincte de la vie et du dernier emplacement."""


def parti(monde, id):
    """Les affaires emportées suivent leur porteur, même dans un contenant."""
    vus = set()
    while id not in vus:
        vus.add(id)
        o = monde.joueur if id == "joueur" else monde.objets.get(id, {})
        if o.get("parti"):
            return True
        id = o.get("lieu")
        if id is None:
            break
    return False


def franchir(monde, id, salle, destination, lignes):
    """Applique une issue déclarée, avant la publication de son franchissement.

    La salle extérieure reste une destination géométrique ordinaire. Le dernier
    emplacement est conservé ; il ne constitue plus une présence dans les lieux.
    """
    issues = [(d, s) for d, s in monde.data["salles"][salle]["sorties"].items()
              if s.get("vers") == destination and s.get("exterieur") is True]
    if not issues:
        return False
    assert len(issues) == 1, "Issue extérieure ambiguë"
    direction, _ = issues[0]
    from .esprits import pnjs, percoit, croire, lire
    temoins = [a for a in pnjs(monde) if a != id and percoit(monde, a, id)]
    if id != "joueur" and monde.visible(id):
        temoins.append("joueur")
    from .temps import instant
    from .tenir import lacher
    from .vecu import solder
    solder(monde, id, instant(monde))
    lacher(monde, id, "marcher")
    o = monde.joueur if id == "joueur" else monde.objets[id]
    o["parti"] = {"salle": salle, "direction": direction,
                  "minute": monde.data["minutes"], "instant": instant(monde)}
    monde.data["gestes_en_cours"] = [g for g in monde.data.get("gestes_en_cours", []) if g["auteur"] != id]
    for a in temoins:
        ancien = lire(monde, a)["croyances"].get(id, {}).get("etat", {}).get("valeur", {})
        croire(monde, a, id, "etat", {**ancien, "parti": True}, "vu")
        croire(monde, a, id, "lieu", None, "vu", salle=None, case=None)
    from .pnj import _chroniquer
    from .francais import designer
    texte = "Tu quittes les lieux." if id == "joueur" else designer(o, debut=True) + " quitte les lieux."
    if id == "joueur":
        monde.data["fin"] = {"cause": "depart", "minute": monde.data["minutes"], "instant": instant(monde)}
        lignes.append(texte)
    else:
        _chroniquer(monde, id, texte, "deplacement")
        if "joueur" in temoins:
            lignes.append(texte)
    return True


def revenir(monde, id):
    """Placement d'auteur par l'issue mémorisée ; aucun agenda ne renaît."""
    from .monde import ErreurMonde
    from .spatial import _case_interieure
    from .pnj import occupants
    o = monde.joueur if id == "joueur" else monde.objets[id]
    p = o.get("parti")
    if not p:
        raise ErreurMonde("Cette personne n'a pas quitté les lieux.",
                          f"retour.personnage : reçu {id!r} ; accepté : un personnage parti.")
    salle = p["salle"]
    sortie = monde.data["salles"][salle]["sorties"][p["direction"]]
    case = _case_interieure(monde, salle, sortie)
    if (salle, tuple(case)) in occupants(monde, id):
        raise ErreurMonde("Le seuil est occupé.",
                          f"retour.case : reçu {case!r} ; accepté : seuil libre de {salle!r}.")
    from .geometrie import placer
    if id == "joueur":
        o.update(salle=salle, position=list(case))
        if monde.data.get("fin", {}).get("cause") == "depart":
            monde.data.pop("fin")
    else:
        placer(o, salle, list(case))
    del o["parti"]
    from .temps import instant
    from .corps import corps
    from .vecu import noter
    # Le séjour hors des lieux n'est pas simulé dans les anciennes conditions
    # du seuil ; reprendre l'horloge corporelle et les gestes au retour.
    corps(monde, id).pop("vecu", None)
    noter(monde, id, instant(monde), None)
    if id != "joueur":
        from .esprits import esprit
        esprit(monde, id).update(libre=instant(monde), veille=None, eveil=None, intention=None)
    from .esprits import percevoir_tous
    percevoir_tous(monde)


def verifier(monde):
    for salle, piece in monde.data["salles"].items():
        destinations = [s["vers"] for s in piece["sorties"].values() if s.get("exterieur") is True]
        assert len(destinations) == len(set(destinations)), "Issue extérieure ambiguë"
        for sortie in piece["sorties"].values():
            if "exterieur" in sortie:
                assert type(sortie["exterieur"]) is bool, "Issue extérieure invalide"
                assert sortie["vers"] != salle, "Issue extérieure sur place"
    for id, o in [("joueur", monde.joueur), *monde.objets.items()]:
        if "parti" not in o:
            continue
        p = o["parti"]
        assert id == "joueur" or o["type"] == "personnage", "Départ sans personnage"
        assert (isinstance(p, dict) and set(p) == {"salle", "direction", "minute", "instant"}
                and p["salle"] in monde.data["salles"]
                and monde.data["salles"][p["salle"]]["sorties"].get(p["direction"], {}).get("exterieur") is True
                and type(p["minute"]) is int and type(p["instant"]) is int), "Départ invalide"
