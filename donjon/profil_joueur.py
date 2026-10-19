"""Détails personnels encore libres, établis une fois sans changer les capacités."""
import copy

from .monde import ErreurMonde


CHAMPS = {"taille_cm": (140, 210), "age_ans": (18, 90)}
TRAITS = {"couleur_yeux": ("bruns", "noisette", "bleus", "gris", "verts"),
          "couleur_cheveux": ("noirs", "bruns", "châtains", "blonds", "roux", "gris", "blancs"),
          "corpulence": ("mince", "moyenne", "robuste")}
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"profil_joueur": {"type": "array", "minItems": 1, "maxItems": 5,
              "items": {"type": "object", "additionalProperties": False,
                        "properties": {"champ": {"type": "string", "enum": [*CHAMPS, *TRAITS]},
                                       "valeur": {"anyOf": [{"type": "integer"}, {"type": "string", "enum": sorted(set(v for valeurs in TRAITS.values() for v in valeurs))}]}},
                        "required": ["champ", "valeur"]}}}, "required": ["profil_joueur"]}



def installer(m):
    """Socle d'auteur pour Corvus ; respecte toute identité déjà définie."""
    if m.joueur.get("nom") == "Corvus":
        m.joueur.setdefault("espece", "humain")
        if m.joueur["espece"] == "humain":
            m.joueur.setdefault("stade_vie", "adulte")


def catalogue(m):
    if m.joueur.get("espece") != "humain" or m.joueur.get("stade_vie") != "adulte":
        return {}
    return {**{champ: {"minimum": bornes[0], "maximum": bornes[1]}
               for champ, bornes in CHAMPS.items() if champ not in m.joueur},
            **{champ: {"valeurs": list(valeurs)} for champ, valeurs in TRAITS.items() if champ not in m.joueur}}


def preparer(m, p, revision=None):
    if revision is not None and revision != m.data["revision"]:
        raise ErreurMonde("Le personnage a changé avant l'enregistrement de ce détail.", "re-propose à partir des faits actuels.")
    if not isinstance(p, dict) or set(p) != {"profil_joueur"}:
        recus = sorted(p) if isinstance(p, dict) else type(p).__name__
        raise ErreurMonde("Complément de personnage mal formé.", f"enrichir_joueur a exactement le champ profil_joueur ; reçu : {recus}.")
    ajouts = p["profil_joueur"]
    if not isinstance(ajouts, list) or not 1 <= len(ajouts) <= len(CHAMPS)+len(TRAITS):
        raise ErreurMonde("Nombre de détails personnels invalide.",
                          f"profil_joueur : une liste de 1 à {len(CHAMPS) + len(TRAITS)} éléments {{champ, valeur}}.")
    travail, libres, vus = m.copier(), catalogue(m), set()
    for a in ajouts:
        if (not isinstance(a, dict) or set(a) != {"champ", "valeur"}
                or not isinstance(a["champ"], str) or a["champ"] not in libres
                or a["champ"] in vus):
            recu = a.get("champ") if isinstance(a, dict) else type(a).__name__
            raise ErreurMonde("Ce détail personnel est déjà établi ou n'est pas disponible.",
                              f"chaque élément a exactement champ et valeur ; champ parmi "
                              f"{', '.join(c for c in libres if c not in vus) or 'aucun'}, une seule fois (reçu « {recu} »).")
        champ, valeur = a["champ"], a["valeur"]
        if champ in CHAMPS:
            bas, haut = CHAMPS[champ]
            if type(valeur) is not int or not bas <= valeur <= haut:
                raise ErreurMonde("Cette valeur ne correspond pas au cadre du personnage.",
                                  f"{champ} : entier de {bas} à {haut} (reçu {valeur!r}).")
        elif not isinstance(valeur, str) or valeur not in TRAITS[champ]:
            raise ErreurMonde("Ce trait ne correspond pas au cadre humain du personnage.",
                              f"{champ} parmi {', '.join(TRAITS[champ])} (reçu {valeur!r}).")
        vus.add(champ)
        travail.joueur[champ] = valeur
    travail.data["revision"] += 1
    travail.data.setdefault("enrichissements", []).append({"revision": travail.data["revision"],
        "origine": "profil joueur", "ajouts": copy.deepcopy(ajouts)})
    travail.verifier()
    return travail


def reponse(m, p):
    phrases = []
    for a in p["profil_joueur"]:
        if a["champ"] == "taille_cm":
            cm = m.joueur["taille_cm"]
            phrases.append(f"Tu mesures {cm//100} m {cm%100:02d}.")
        elif a["champ"] == "age_ans":
            phrases.append(f"Tu as {m.joueur['age_ans']} ans.")
        elif a["champ"] == "couleur_yeux":
            phrases.append(f"Tu as les yeux {m.joueur['couleur_yeux']}.")
        elif a["champ"] == "couleur_cheveux":
            phrases.append(f"Tes cheveux sont {m.joueur['couleur_cheveux']}.")
        elif a["champ"] == "corpulence":
            phrases.append(f"Tu es de corpulence {m.joueur['corpulence']}.")
    return " ".join(phrases)
