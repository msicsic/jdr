"""Plan métrique du petit scénario : une case de sol représente 1 m x 1 m.

La géométrie est celle du plan, pas celle d'un damier : une case voisine en diagonale est à √2 m.
Toute portée en cases (lumière, vue, ouïe, voix) se mesure en distance réelle (``distance``) ; un
pas en diagonale dure √2 fois un pas droit (``temps.duree_pas``). Les deux arrondissent de la même
façon, une fois (``racine``) : en entiers, sans calcul flottant.
"""
from math import isqrt

DIRECTIONS = {"nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0)}


_CASES = {}


def racine(n):
    """La racine carrée de l'entier ``n`` arrondie à l'entier le plus proche, exactement : la
    racine d'un entier qui n'est pas un carré n'est jamais un demi-entier, il n'y a pas d'égalité
    à départager."""
    k = isqrt(n)
    return k + (n > k * k + k)


def distance(a, b):
    """La distance réelle entre deux cases, en cases entières : la distance euclidienne arrondie à
    la case la plus proche. Une case voisine, même en diagonale, est à 1 (au contact) ; deux cases
    en diagonale à 3, trois à 4, quatre à 6. Les portées comparées à cette distance dessinent des
    disques, pas des carrés."""
    dx, dy = a[0] - b[0], a[1] - b[1]
    return racine(dx * dx + dy * dy)


def cases(piece):
    """Les cases de sol d'une pièce, lues une fois par plan (le plan d'une pièce ne change pas
    sans être remplacé)."""
    sol = tuple(piece["plan"]["sol"])
    if sol not in _CASES:
        _CASES[sol] = frozenset((x, y) for y, ligne in enumerate(sol) for x, case in enumerate(ligne) if case == ".")
    return _CASES[sol]


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
