"""Lexique des entités du monde, pour repérer une mention sans fondement.

Le MJ ne reçoit que des faits filtrés par la perception. Un nom d'entité qu'il
emploie sans que ce nom figure dans ce qu'il a reçu ne peut venir que d'une
invention ou d'une fuite. Le lexique est dérivé des noms et alias de l'état :
il ne contient aucune liste de mots écrite à la main.
"""
import json
import re

from .monde import normaliser


def _motif(terme):
    # Les pluriels réguliers comptent comme le même terme.
    return re.compile(r"(?<![a-z0-9])" + re.escape(terme) + r"(?:s|x)?(?![a-z0-9])")


def termes(monde):
    """Associe chaque nom ou alias normalisé aux identifiants qui le portent."""
    index = {}
    for o in monde.objets.values():
        for nom in [o.get("nom", ""), *o.get("aliases", [])]:
            terme = normaliser(nom)
            if len(terme) >= 3:
                index.setdefault(terme, set()).add(o["id"])
    for id, salle in monde.data["salles"].items():
        terme = normaliser(salle.get("nom", ""))
        if len(terme) >= 3:
            index.setdefault(terme, set()).add(id)
    return index


def corpus(*elements):
    """Texte normalisé de tout ce qui a été fourni au MJ ou affiché au joueur."""
    morceaux = []
    for e in elements:
        morceaux.append(e if isinstance(e, str) else json.dumps(e, ensure_ascii=False, default=str))
    return normaliser(" ".join(morceaux))


def entites_citees(monde, texte):
    """Identifiants nommés dans un texte, le terme le plus long l'emportant sur ceux qu'il contient."""
    texte = normaliser(texte)
    ids = set()
    for terme, porteurs in sorted(termes(monde).items(), key=lambda t: -len(t[0])):
        if terme not in texte:
            continue  # Son motif exige le terme tel quel : absent du texte, il ne s'y trouve pas.
        texte, trouves = _motif(terme).subn(" ", texte)
        if trouves:
            ids |= porteurs
    return ids


def mentions_sans_fondement(monde, texte, fondement):
    """Termes d'entités présents dans le texte mais absents du fondement normalisé.

    Un terme plus long qui contient un terme plus court (« axe du gond supérieur »
    et « axe ») ne compte qu'une fois : seul le terme le plus long est examiné.
    """
    texte = normaliser(texte)
    trouves = []
    for terme, ids in sorted(termes(monde).items(), key=lambda t: -len(t[0])):
        if terme not in texte:
            continue
        motif = _motif(terme)
        if not motif.search(texte):
            continue
        if not motif.search(fondement):
            trouves.append({"terme": terme, "entites": sorted(ids)})
        texte = motif.sub(" ", texte)
    return trouves
