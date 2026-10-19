"""Transitions d'histoire déclarées par la partie et exécutées par le moteur."""

import copy

from .geometrie import cases
from .deplacement_objet import deplacer
from .monde import ErreurMonde


CHAMPS_CONDITION = ("lieu", "integrite", "ouverte", "verrouillee")
OPERATIONS = ("deplacer", "objectif", "eteindre")


def verifier_effet(monde, effet):
    """Effets communs aux transitions et aux horloges du scénario."""
    assert isinstance(effet, dict) and effet.get("operation") in OPERATIONS, "Effet de transition invalide"
    if effet["operation"] == "eteindre":
        assert (set(effet) == {"operation", "salles"} and isinstance(effet["salles"], list) and effet["salles"]
                and all(salle in monde.data["salles"] for salle in effet["salles"])), "Extinction de scénario invalide"
    elif effet["operation"] == "deplacer":
        assert (set(effet) == {"operation", "objet", "depuis", "lieu", "position"}
                and effet["objet"] in monde.objets
                and monde.objets[effet["objet"]]["mobile"]
                and effet["depuis"] in (*monde.data["salles"], *monde.objets, "joueur")
                and effet["lieu"] in monde.data["salles"]
                and isinstance(effet["position"], list)
                and len(effet["position"]) == 2
                and all(type(v) is int for v in effet["position"])
                and tuple(effet["position"]) in cases(monde.data["salles"][effet["lieu"]])), "Déplacement de scénario invalide"
    else:
        objectif = effet.get("objectif")
        assert (set(effet) == {"operation", "objectif_avant", "objectif", "resume"}
                and effet["objectif_avant"] in monde.objets
                and isinstance(objectif, dict)
                and set(objectif) in ({"objet", "lieu", "message"},
                                      {"objet", "lieu", "salle", "message"})
                and objectif["objet"] in monde.objets
                and objectif["lieu"] in (*monde.data["salles"], *monde.objets, "joueur")
                and ("salle" not in objectif or objectif["salle"] in monde.data["salles"])
                and isinstance(objectif["message"], str) and objectif["message"].strip()
                and len(objectif["message"]) <= 500
                and isinstance(effet["resume"], str) and 3 <= len(effet["resume"]) <= 300), "Objectif de transition invalide"


def verifier(monde):
    transitions = monde.data.get("transitions_scenario", [])
    effectuees = monde.data.get("transitions_effectuees", [])
    assert isinstance(transitions, list) and isinstance(effectuees, list), "Transitions invalides"
    ids = set()
    for transition in transitions:
        assert (isinstance(transition, dict)
                and set(transition) == {"id", "conditions", "effets", "annonce"}
                and isinstance(transition["id"], str) and transition["id"]
                and transition["id"] not in ids
                and isinstance(transition["annonce"], str)
                and 3 <= len(transition["annonce"]) <= 500), "Transition mal formée"
        ids.add(transition["id"])
        conditions, effets = transition["conditions"], transition["effets"]
        assert isinstance(conditions, list) and conditions and isinstance(effets, list) and effets, "Transition vide"
        for condition in conditions:
            assert (isinstance(condition, dict)
                    and set(condition) == {"objet", "champ", "valeur"}
                    and condition["objet"] in monde.objets
                    and condition["champ"] in CHAMPS_CONDITION
                    and condition["champ"] in monde.objets[condition["objet"]]
                    and type(condition["valeur"]) is type(monde.objets[condition["objet"]][condition["champ"]])), "Condition invalide"
        for effet in effets:
            verifier_effet(monde, effet)
    assert (len(effectuees) == len(set(effectuees))
            and all(isinstance(id, str) and id in ids for id in effectuees)), "Historique de transition invalide"


def disponibles(monde):
    return {t["id"]: {"annonce": t["annonce"]}
            for t in monde.data.get("transitions_scenario", [])
            if t["id"] not in monde.data.get("transitions_effectuees", [])
            and all(monde.objets[c["objet"]][c["champ"]] == c["valeur"]
                    and monde.visible(c["objet"])
                    for c in t["conditions"])
            and all(applicable(monde, e) for e in t["effets"])}


def applicable(monde, effet):
    if effet["operation"] == "deplacer":
        return monde.objets[effet["objet"]]["lieu"] == effet["depuis"]
    if effet["operation"] == "objectif":
        return (not monde.data.get("objectif_atteint")
                and (monde.data.get("objectif_partie") or {}).get("objet") == effet["objectif_avant"])
    return True


def appliquer_effet(travail, effet):
    if effet["operation"] == "deplacer":
        deplacer(travail, effet["objet"], effet["lieu"], effet["position"])
    elif effet["operation"] == "objectif":
        travail.data["objectif_partie"] = copy.deepcopy(effet["objectif"])
        travail.data["scenario"]["objectif"] = effet["resume"]
    else:
        from .perception import salle_source
        for o in travail.objets.values():
            if o.get("allume") and salle_source(travail, o) in effet["salles"]:
                o["allume"] = False


def preparer(monde, identifiant):
    if identifiant not in disponibles(monde):
        raise ErreurMonde("Cette évolution du scénario n'est pas établie par l'état actuel.",
                          f"evolution : ancrage parmi les évolutions disponibles ({', '.join(disponibles(monde)) or 'aucune'}), "
                          f"reçu « {identifiant} » ; sinon un autre type de fait.")
    transition = next(t for t in monde.data["transitions_scenario"] if t["id"] == identifiant)
    travail = monde.copier()
    for effet in transition["effets"]:
        if effet["operation"] == "deplacer" and not applicable(travail, effet):
            raise ErreurMonde("L'objet n'est plus à la position prévue par cette évolution.", f"{identifiant} ne s'applique plus : retire-la.")
        if effet["operation"] == "objectif" and travail.data.get("objectif_atteint"):
            raise ErreurMonde("L'objectif de cette partie est déjà accompli.", f"{identifiant} ne s'applique plus : retire-la.")
        if not applicable(travail, effet):
            raise ErreurMonde("L'objectif actuel ne correspond plus à cette évolution.", f"{identifiant} ne s'applique plus : retire-la.")
        appliquer_effet(travail, effet)
    travail.data.setdefault("transitions_effectuees", []).append(identifiant)
    travail.verifier()
    return travail, transition["annonce"]
