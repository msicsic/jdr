"""Capacités physiques et constats situés sur les objets."""

import hashlib
import json

from .monde import ErreurMonde

USAGES_OUTIL = ("couper", "levier", "allumage")
CAPACITES_REVUE = ("son", "lumiere", "tranchable", *USAGES_OUTIL)


def empreinte(objet, usure=True):
    """L'état physique pertinent ; une aptitude acquise survit à une entaille."""
    champs = ("materiau", "masse", "mobile", "integrite", "maximum",
              "description_visuelle", "forme", "taille", "longueur_cm",
              "diametre_cm", "usages", "puissance")
    donnees = {champ: objet.get(champ) for champ in champs if usure or champ != "integrite"}
    return hashlib.sha256(json.dumps(donnees, sort_keys=True,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def constat(objet, capacite, moyen=None):
    """Constat encore applicable à cet état et à ce moyen."""
    for observation in reversed(objet.get("constats_capacites", [])):
        positive = observation["issue"] == "etablie"
        if (observation["capacite"] == capacite
                and observation["empreinte"] == empreinte(objet, usure=not positive)
                and (not positive or objet.get("integrite", 0) > 0)
                and (capacite != "tranchable" or
                     moyen is not None
                     and moyen.get("id") == observation["moyen_id"]
                     and empreinte(moyen, usure=not positive) == observation["empreinte_moyen"]
                     and (not positive or moyen.get("integrite", 0) > 0))):
            return observation
    return None


def resume_constats(objet, objets=None):
    """Mémoire lisible du MJ, sans empreinte interne."""
    return [{"capacite": c["capacite"], "issue": c["issue"],
             "moyen": c["moyen_nom"],
             "etat_objet_actuel": (c["empreinte"] == empreinte(
                 objet, usure=c["issue"] != "etablie")
                 and (c["issue"] != "etablie" or objet.get("integrite", 0) > 0)),
             "etat_moyen_actuel": (c["moyen_id"] in objets
                 and empreinte(objets[c["moyen_id"]], usure=c["issue"] != "etablie")
                 == c["empreinte_moyen"]
                 and (c["issue"] != "etablie" or objets[c["moyen_id"]].get("integrite", 0) > 0))
             if c["moyen_id"] and objets is not None else not c["moyen_id"]}
            for c in objet.get("constats_capacites", [])]


def statut(objet, capacite, moyen=None):
    """Etat d'une aptitude physique : établie, écartée ou encore inconnue."""
    if capacite not in CAPACITES_REVUE:
        raise ErreurMonde("Capacité physique inconnue.")
    proprietes = {"son": "sonorite", "lumiere": "luminosite",
                  "tranchable": "seuil_coupe"}
    if capacite in proprietes:
        presente = proprietes[capacite] in objet
    else:
        usages = set(objet.get("usages", []))
        equivalences = {"couper": {"couper", "couper_bois"},
                        "levier": {"levier", "levier_fin"},
                        "allumage": {"allumage"}}
        presente = bool(usages & equivalences[capacite])
        if "usages" in objet and not presente:
            return "ecartee"
    if presente:
        return "etablie"
    observation = constat(objet, capacite, moyen)
    return observation["issue"] if observation else "inconnue"


def absence(objet, capacite, observation=None):
    """Phrase réutilisée par l'arbitrage, la description et les attestations."""
    from .francais import designer, pluriel
    suffixes = {
        "tranchable": ("résiste", "résistent", " à cet outil de coupe"),
        "son": ("ne peut pas", "ne peuvent pas", " produire de son audible"),
        "lumiere": ("ne peut pas", "ne peuvent pas", " éclairer"),
        "couper": ("ne peut pas", "ne peuvent pas", " servir à couper"),
        "levier": ("ne peut pas", "ne peuvent pas", " servir de levier"),
        "allumage": ("ne peut pas", "ne peuvent pas", " servir à allumer"),
    }
    if capacite not in suffixes:
        raise ErreurMonde("Capacité physique inconnue.")
    singulier, plusieurs, fin = suffixes[capacite]
    if capacite == "tranchable" and observation:
        fin = " à " + observation["moyen_nom"]
    return designer(objet, debut=True) + " " + (plusieurs if pluriel(objet) else singulier) + fin


def aptitude_coupe(objet, observation):
    from .francais import accorder, designer, pluriel
    verbe = "peuvent" if pluriel(objet) else "peut"
    return (designer(objet, debut=True) + " " + verbe + " être "
            + accorder(objet, "entamé") + " avec " + observation["moyen_nom"])

SCHEMA = {"type": "array", "maxItems": 4, "items": {"anyOf": [
    {"type": "object", "additionalProperties": False,
     "properties": {"nature": {"type": "string", "enum": ["son"]},
                    "intensite": {"type": "integer", "minimum": 1, "maximum": 3}},
     "required": ["nature", "intensite"]},
    {"type": "object", "additionalProperties": False,
     "properties": {"nature": {"type": "string", "enum": ["lumiere"]},
                    "niveau": {"type": "integer", "minimum": 1, "maximum": 2},
                    "combustible": {"type": "integer", "minimum": 1, "maximum": 240}},
     "required": ["nature", "niveau", "combustible"]},
    {"type": "object", "additionalProperties": False,
     "properties": {"nature": {"type": "string", "enum": ["outil"]},
                    "usages": {"type": "array", "minItems": 1, "maxItems": 3,
                               "items": {"type": "string", "enum": list(USAGES_OUTIL)}},
                    "puissance": {"type": "integer", "minimum": 0, "maximum": 7}},
     "required": ["nature", "usages", "puissance"]},
    {"type": "object", "additionalProperties": False,
     "properties": {"nature": {"type": "string", "enum": ["tranchable"]},
                    "seuil": {"type": "integer", "minimum": 1, "maximum": 7},
                    "tenacite": {"type": "integer", "minimum": 1, "maximum": 20}},
     "required": ["nature", "seuil", "tenacite"]},
]}}


def noms(capacites):
    """Même liste de capacités dans la proposition physique et sa contre revue."""
    return [usage for capacite in capacites
            for usage in (capacite.get("usages", []) if capacite.get("nature") == "outil"
                          else [capacite.get("nature")])]


def proprietes(capacites, masse, mobile=True):
    if not isinstance(capacites, list) or len(capacites) > 4:
        raise ErreurMonde("Capacités physiques invalides.")
    resultat = {}
    vues = set()
    for capacite in capacites:
        if not isinstance(capacite, dict):
            raise ErreurMonde("Capacité physique mal formée.")
        nature = capacite.get("nature")
        if not isinstance(nature, str) or nature in vues or masse <= 0:
            raise ErreurMonde("Capacité physique incompatible avec cet objet.")
        vues.add(nature)
        if nature == "son":
            if (set(capacite) != {"nature", "intensite"}
                    or type(capacite["intensite"]) is not int
                    or not 1 <= capacite["intensite"] <= 3):
                raise ErreurMonde("Intensité sonore invalide.")
            resultat["sonorite"] = capacite["intensite"]
        elif nature == "lumiere":
            if (set(capacite) != {"nature", "niveau", "combustible"}
                    or type(capacite["niveau"]) is not int
                    or not 1 <= capacite["niveau"] <= 2
                    or type(capacite["combustible"]) is not int
                    or not 1 <= capacite["combustible"] <= 240):
                raise ErreurMonde("Source lumineuse invalide.")
            resultat.update(allume=False, luminosite=capacite["niveau"],
                            combustible=capacite["combustible"])
        elif nature == "outil":
            usages = capacite.get("usages")
            puissance = capacite.get("puissance")
            if (set(capacite) != {"nature", "usages", "puissance"}
                    or not mobile or not 0.1 <= masse <= 20
                    or not isinstance(usages, list) or not 1 <= len(usages) <= 3
                    or any(u not in USAGES_OUTIL for u in usages)
                    or len(usages) != len(set(usages))
                    or type(puissance) is not int or not 0 <= puissance <= 7
                    or ({"couper", "levier"} & set(usages) and puissance < 1)):
                raise ErreurMonde("Usages physiques de l'outil invalides.")
            resultat.update(usages=usages, puissance=puissance)
        elif nature == "tranchable":
            if (set(capacite) != {"nature", "seuil", "tenacite"}
                    or type(capacite["seuil"]) is not int
                    or not 1 <= capacite["seuil"] <= 7
                    or type(capacite["tenacite"]) is not int
                    or not 1 <= capacite["tenacite"] <= 20):
                raise ErreurMonde("Résistance à la coupe invalide.")
            resultat.update(seuil_coupe=capacite["seuil"],
                            integrite=capacite["tenacite"], maximum=capacite["tenacite"])
        else:
            raise ErreurMonde("Capacité physique inconnue.")
    return resultat
