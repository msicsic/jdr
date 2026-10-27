"""Préconditions matérielles des manœuvres, communes à tous les acteurs."""
from .monde import ErreurMonde


def valider_fermeture(monde, cible):
    o = monde.objets[cible]
    if o.get("bloque_par"):
        raise ErreurMonde("Impossible de refermer : le battant est calé.",
                          f"cible={cible}, bloque_par={o['bloque_par']} : bloque_par=None requis ; debloquer d'abord.")
    if o["integrite"] == 0:
        raise ErreurMonde("Impossible de refermer : le battant est brisé.",
                          f"cible={cible}, integrite=0 : integrite>0 requis.")
    if o.get("detachee"):
        raise ErreurMonde("Impossible de refermer : le battant est détaché.",
                          f"cible={cible}, detachee=True : detachee=False requis.")
