"""Plan métrique du petit scénario : une case de sol représente 1 m x 1 m."""
from copy import deepcopy


PLANS = {
    "echoppe": {"origine": [2, 8], "sol": ["....."] * 6, "repere": "E"},
    "antichambre": {"origine": [8, 10], "sol": ["......"] * 4, "repere": "A"},
    "crypte": {"origine": [8, 2], "sol": ["  ....  "] + ["........"] * 6, "repere": "C"},
}
PASSAGES = {"echoppe": {"est": [5, 3]},
            "antichambre": {"ouest": [-1, 1], "nord": [3, -1]},
            "crypte": {"sud": [3, 7]}}
EMPLACEMENTS = {"cle": [3, 2], "torche": [4, 1], "marchand": [1, 1],
                "brasero": [3, 4], "pied_de_biche": [3, 1], "marteau": [3, 2],
                "crochets": [3, 3], "coffre": [4, 2]}
DIRECTIONS = {"nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0)}


def cases(piece):
    return {(x, y) for y, ligne in enumerate(piece["plan"]["sol"])
            for x, case in enumerate(ligne) if case == "."}


def placer(objet, salle, position):
    objet["position_salle"] = salle
    objet["position"] = list(position)


def position_objet(monde, objet):
    salle = objet["lieu"]
    piece = monde.data["salles"].get(salle)
    if not piece:
        return None
    position = tuple(objet.get("position", ()))
    if objet.get("position_salle") == salle and position in cases(piece):
        return position
    # Ancien objet déplacé avant l'installation du plan : emplacement de reprise.
    return position_entree(monde, salle)


def position_entree(monde, salle, depuis=None):
    piece = monde.data["salles"][salle]
    for direction, sortie in piece["sorties"].items():
        if depuis is None or sortie["vers"] == depuis:
            dx, dy = DIRECTIONS[direction]
            x, y = sortie["case"]
            return x - dx, y - dy
    return min(cases(piece), key=lambda p: (p[1], p[0]))


def installer(monde):
    if monde.data.get("geometrie_version") == 1:
        return
    for id, piece in monde.data["salles"].items():
        piece["plan"] = deepcopy(PLANS[id])
        for direction, sortie in piece["sorties"].items():
            sortie["case"] = PASSAGES[id][direction][:]
    monde.joueur["position"] = list(position_entree(monde, monde.joueur["salle"]))
    if monde.joueur["salle"] == "antichambre":
        monde.joueur["position"] = [1, 2]
    for objet in monde.objets.values():
        if objet["lieu"] in monde.data["salles"] and objet["type"] not in ("surface", "porte"):
            # Les emplacements initiaux ne s'appliquent qu'aux objets encore dans leur salle d'origine.
            origine = "antichambre" if objet["id"] in ("cle", "torche") else "crypte" if objet["id"] == "coffre" else "echoppe"
            position = EMPLACEMENTS.get(objet["id"]) if objet["lieu"] == origine else None
            placer(objet, objet["lieu"], position or position_entree(monde, objet["lieu"]))
    monde.data["geometrie_version"] = 1
