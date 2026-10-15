"""Plan métrique du petit scénario : une case de sol représente 1 m x 1 m."""
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
