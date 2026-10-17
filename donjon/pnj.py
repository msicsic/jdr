"""Réactions déclarées des PNJ : un son assez fort met le PNJ en route vers sa source.

Le PNJ marche d'un lieu par minute le long des sorties, sans franchir de porte fermée.
Luna ne décide ni de l'alerte ni du déplacement ; elle reçoit la position qui en résulte.
"""
from collections import deque

from .francais import designer
from .geometrie import placer, position_entree


def verifier(monde):
    for o in monde.objets.values():
        if o["type"] != "personnage":
            continue
        reaction = o.get("reaction_son")
        assert reaction is None or (isinstance(reaction, dict) and set(reaction) == {"seuil"}
                                    and type(reaction["seuil"]) is int
                                    and 1 <= reaction["seuil"] <= 5), "Réaction de PNJ invalide"
        trajet = o.get("trajet")
        assert trajet is None or (reaction is not None and isinstance(trajet, dict)
                                  and set(trajet) == {"vers", "minutes"}
                                  and trajet["vers"] in monde.data["salles"]
                                  and o["lieu"] in monde.data["salles"]
                                  and type(trajet["minutes"]) is int
                                  and 0 <= trajet["minutes"]), "Trajet de PNJ invalide"


def reagir(monde, id, origine, niveau):
    """Appelé pour chaque PNJ qui entend un son, avec le niveau reçu dans son lieu."""
    pnj = monde.objets[id]
    reaction = pnj.get("reaction_son")
    if reaction and niveau >= reaction["seuil"] and origine != pnj["lieu"]:
        pnj["trajet"] = {"vers": origine, "minutes": 0}


def chemin(monde, depart, arrivee):
    """Lieux traversés à pied, sorties sans porte ou à porte ouverte ; None si bloqué."""
    precedent, file = {depart: None}, deque([depart])
    while file:
        lieu = file.popleft()
        for sortie in monde.data["salles"][lieu]["sorties"].values():
            porte = monde.objets.get(sortie.get("porte") or "")
            if (porte and not porte.get("ouverte")) or sortie["vers"] in precedent:
                continue
            precedent[sortie["vers"]] = lieu
            file.append(sortie["vers"])
    if arrivee not in precedent:
        return None
    etapes = []
    while arrivee != depart:
        etapes.append(arrivee)
        arrivee = precedent[arrivee]
    return etapes[::-1]


def avancer(monde, minutes, lignes):
    """Renvoie les PNJ apparus dans la perception du joueur pendant ces minutes."""
    apparus = []
    for id, o in monde.objets.items():
        trajet = o.get("trajet")
        if not trajet:
            continue
        budget = trajet["minutes"] + minutes
        vu = monde.visible(id)
        while budget >= 1 and o["lieu"] != trajet["vers"]:
            etapes = chemin(monde, o["lieu"], trajet["vers"])
            if not etapes:
                # Bloqué : il attend sur place, sans accumuler d'avance.
                budget = 0
                break
            depuis, o["lieu"] = o["lieu"], etapes[0]
            if "position" in o:
                placer(o, o["lieu"], position_entree(monde, o["lieu"], depuis))
            budget -= 1
        if o["lieu"] == trajet["vers"]:
            o.pop("trajet")
        else:
            trajet["minutes"] = budget
        if monde.visible(id) and not vu:
            lignes.append(designer(o, debut=True) + " arrive.")
            apparus.append(id)
        elif vu and not monde.visible(id):
            lignes.append(designer(o, debut=True) + " s'éloigne.")
    return apparus
