"""Préconditions matérielles des manœuvres, communes à tous les acteurs."""
from .monde import ErreurMonde


def refermable(fin):
    """Capacité du battant, sur une fin constatée ou simulée, jamais sa position."""
    return fin != "detruit"


def valider_fermeture(monde, cible):
    o = monde.objets[cible]
    if o.get("bloque_par"):
        raise ErreurMonde("Impossible de refermer : le battant est calé.",
                          f"cible={cible}, bloque_par={o['bloque_par']} : bloque_par=None requis ; debloquer d'abord.")
    from .perception import fin_objet
    if not refermable(fin_objet(o)):
        raise ErreurMonde("Impossible de refermer : le battant est brisé.",
                          f"cible={cible}, integrite=0 : integrite>0 requis.")
    if o.get("detachee"):
        raise ErreurMonde("Impossible de refermer : le battant est détaché.",
                          f"cible={cible}, detachee=True : detachee=False requis.")
