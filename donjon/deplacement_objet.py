"""Mutation commune du lieu et de la position physique d'un objet existant."""

from .geometrie import placer
from .monde import ErreurMonde


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
