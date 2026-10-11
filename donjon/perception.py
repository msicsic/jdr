"""Eclairage discret : 0 noir, 1 pénombre, 2 assez de lumière pour les détails.

Une ouverture transmet la lumière avec une perte d'un niveau. Un contenant fermé
opaque bloque une source. Le calcul est pur : observer ne consomme pas de temps.
"""
from collections import deque

from .francais import designer


def salle_source(monde, source):
    lieu = source["lieu"]
    vus = set()
    while lieu in monde.objets:
        if lieu in vus:
            return None
        vus.add(lieu)
        parent = monde.objets[lieu]
        if parent["type"] == "contenant" and not parent["ouverte"]:
            return None
        lieu = parent["lieu"]
    return monde.joueur["salle"] if lieu == "joueur" else lieu


def eclairage(monde, salle=None):
    salle = salle or monde.joueur["salle"]
    sources = []
    for o in monde.objets.values():
        if o.get("allume") and o.get("combustible", 0) > 0 and o["integrite"] > 0:
            origine = salle_source(monde, o)
            if origine in monde.data["salles"]:
                sources.append((origine, o["luminosite"], o["id"]))
    for id, piece in monde.data["salles"].items():
        if piece.get("lumiere_naturelle", 0) > 0:
            sources.append((id, piece["lumiere_naturelle"], "jour"))
    contributions = []
    # Parcours depuis l'observateur : la direction initiale explique d'où entre la lueur.
    file = deque([(salle, 0, "")])
    distances = {salle: 0}
    while file:
        courante, distance, direction_initiale = file.popleft()
        for origine, intensite, id in sources:
            if origine == courante and intensite > distance:
                contributions.append({"source": id if distance == 0 else None,
                                      "niveau": min(2, intensite - distance),
                                      "direction": direction_initiale})
        for direction, sortie in monde.data["salles"][courante]["sorties"].items():
            porte = monde.objets.get(sortie["porte"])
            if porte and not porte["ouverte"]:
                continue
            destination = sortie["vers"]
            if destination not in distances:
                distances[destination] = distance + 1
                file.append((destination, distance + 1, direction_initiale or direction))
    niveau = max((c["niveau"] for c in contributions), default=0)
    return {"niveau": niveau, "etat": ["obscurité", "pénombre", "éclairé"][niveau],
            "contributions": contributions}


def avancer_combustion(monde, minutes, lignes):
    for o in monde.objets.values():
        if not o.get("allume"):
            continue
        perceptible = monde.present_physique(o["id"])
        o["combustible"] = max(0, o["combustible"] - minutes)
        if o["combustible"] == 0 or o["integrite"] == 0:
            o["allume"] = False
            if perceptible:
                lignes.append(designer(o, debut=True) + " s'éteint.")
