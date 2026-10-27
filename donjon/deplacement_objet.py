"""Mutation commune du lieu et de la position physique d'un objet existant."""

from .geometrie import placer
from .monde import ErreurMonde


POSITION_DEPOT = "à tes pieds"
SOL_AUX_PIEDS = "au sol, " + POSITION_DEPOT


def destination_depot(monde, destination):
    """Résout le repère public du sol dans l'état de l'étape courante."""
    surface = monde.objets.get(destination, {})
    if destination == "sol" or (surface.get("type") == "surface"
            and surface.get("nom") == "sol"
            and surface.get("lieu") == monde.joueur["salle"]
            and monde.visible(destination)):
        return monde.joueur["salle"]
    return destination


def decrire_depot(monde, identifiant):
    """Sens public du dépôt ; la salle reste un repère de stockage interne."""
    from .francais import designer
    return "Poser " + designer(monde.objets[identifiant]) + " " + SOL_AUX_PIEDS + "."


def presenter_effet(monde, effet):
    """Projection de lecture uniquement : ne change jamais l'effet exécutable."""
    op, cible, destination = effet
    # La validation a fixé la salle de l'étape, qui peut différer du lieu
    # initial d'une séquence. Un transfert vers une salle est un dépôt au sol.
    if op == "transferer" and destination in monde.data["salles"]:
        return [op, cible, {"destination": "sol", "position": POSITION_DEPOT}]
    return list(effet)


def deplacer(monde, identifiant, destination, position=None):
    """Quitte l'ancien support ; la case de contact ne survit pas au déplacement."""
    o = monde.objets[identifiant]
    if o.get("entrave"):
        raise ErreurMonde("Ce lien retient encore une personne.", f"cible={identifiant} : entrave=false requis ; delier la personne avant de déplacer le lien.")
    if destination not in (*monde.data["salles"], *monde.objets, "joueur"):
        raise ErreurMonde("Destination d'objet inconnue.")
    o["lieu"] = destination
    from .biens import clore
    clore(monde, identifiant, destination)  # Revenu à son propriétaire, un objet prêté n'est plus prêté.
    if "attache" in o:
        o["attache"] = False
    if o.get("relation_support"):
        if destination == "joueur":
            o.pop("relation_support")
        else:
            o["relation_support"] = ("contenu" if destination in monde.objets
                                     and monde.objets[destination]["type"] == "contenant" else "pose")
    o.pop("ancrage_carte", None)
    o.pop("position_autonome", None)
    o.pop("ancrage_initial", None)
    if destination in monde.data["salles"]:
        placer(o, destination, position if position is not None else monde.joueur["position"])
    else:
        o.pop("position", None)
        o.pop("position_salle", None)
    return o
