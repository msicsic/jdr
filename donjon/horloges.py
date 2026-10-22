"""Horloges d'environnement : événements de scénario déclenchés par le temps écoulé.

Une horloge porte les mêmes effets que les transitions de scénario. Elle se déclenche
une seule fois, à l'instant où la partie atteint sa minute, pendant la vie des PNJ
(``pnj._avancer``) : un geste long du joueur ne la retarde pas, et les PNJ vivent ce qu'elle
change dès cet instant. Un effet devenu sans objet (objet déjà déplacé, objectif accompli)
est simplement ignoré.
L'annonce n'est montrée que si le joueur se trouve dans l'un des lieux qui la perçoivent.
"""
from .transitions_scenario import applicable, appliquer_effet, verifier_effet


def verifier(monde):
    horloges = monde.data.get("horloges", [])
    declenchees = monde.data.get("horloges_declenchees", [])
    assert isinstance(horloges, list) and isinstance(declenchees, list), "Horloges invalides"
    ids = set()
    for h in horloges:
        assert (isinstance(h, dict) and set(h) == {"id", "minute", "effets", "annonce", "lieux"}
                and isinstance(h["id"], str) and h["id"] and h["id"] not in ids
                and type(h["minute"]) is int and h["minute"] >= 0
                and isinstance(h["effets"], list) and h["effets"]
                and isinstance(h["annonce"], str) and 3 <= len(h["annonce"]) <= 500
                and isinstance(h["lieux"], list)
                and all(lieu in monde.data["salles"] for lieu in h["lieux"])), "Horloge mal formée"
        ids.add(h["id"])
        for effet in h["effets"]:
            verifier_effet(monde, effet)
    assert (len(declenchees) == len(set(declenchees))
            and all(id in ids for id in declenchees)), "Historique d'horloge invalide"


def declencher(monde, lignes):
    """Les horloges échues à l'heure courante, dans l'ordre de leur minute (``pnj._avancer`` : à
    chaque minute franchie, et au début pour une échéance déjà passée)."""
    faites = monde.data.setdefault("horloges_declenchees", [])
    for h in sorted(monde.data.get("horloges", []), key=lambda h: h["minute"]):
        if h["id"] in faites or h["minute"] > monde.data["minutes"]:
            continue
        for effet in h["effets"]:
            if applicable(monde, effet):
                appliquer_effet(monde, effet)
        faites.append(h["id"])
        if monde.joueur["salle"] in h["lieux"]:
            lignes.append(h["annonce"])
    if not faites:
        monde.data.pop("horloges_declenchees")
