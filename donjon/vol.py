"""Vol d'objets accessibles et réaction persistante des témoins présents."""
from .francais import designer


def installer(monde):
    monde.data.setdefault("relations_pnj", {})
    for id, o in monde.objets.items():
        if o["type"] == "personnage":
            o.setdefault("vigilance", 14)
            monde.data["relations_pnj"].setdefault(id, {"soupcon": 0, "vols_surpris": 0, "dernier_objet": ""})


def proprietaire(monde, objet):
    if objet.get("proprietaire"):
        return objet["proprietaire"]
    if objet.get("en_vente"):
        return objet.get("vendeur")
    parent = monde.objets.get(objet["lieu"])
    while parent:
        if parent.get("proprietaire"):
            return parent["proprietaire"]
        if parent["type"] == "personnage":
            return parent["id"]
        parent = monde.objets.get(parent["lieu"])
    return None


def mefiance(monde, id):
    """Soupçon envers le joueur : incidents surpris, ou réputation apprise (vue ou rapportée)."""
    fiable = monde.data.get("esprits", {}).get(id, {}).get("croyances", {}).get("joueur", {}).get("fiable")
    return max(monde.data["relations_pnj"][id]["soupcon"], 1 if fiable and not fiable["valeur"] else 0)


def appliquer(monde, effet, lignes):
    op, cible, valeur = effet
    if op == "voler":
        o = monde.objets[cible]
        o.update(proprietaire=valeur, vole_a=valeur, vole_par="joueur", en_vente=False)
        o.pop("vendeur", None)
        lignes.append("Tu dérobes " + designer(o) + " sans être remarqué.")
    else:
        relation = monde.data["relations_pnj"][cible]
        relation["soupcon"] = min(3, relation["soupcon"] + 1)
        relation["vols_surpris"] += 1
        relation["dernier_objet"] = valeur
        from .deliberation import VOL, relancer
        from .esprits import croire, memoriser
        memoriser(monde, cible, {"type": "vol_surpris", "auteur": "joueur", "objet": valeur})
        croire(monde, cible, "joueur", "fiable", False, "vu")
        if proprietaire(monde, monde.objets[valeur]) == cible:
            relancer(monde, cible, "biens", VOL)  # Seule la victime craint pour ses biens.
        monde.objets[cible]["humeur"] = "méfiant"
        lignes.append(monde.objets[cible]["nom"] + " te surprend en train de tenter de dérober "
                      + designer(monde.objets[valeur]) + ". Tu retires la main ; l'objet reste en place.")
        if monde.objets[cible].get("refuse_ventes_apres_vol"):
            lignes.append(monde.objets[cible]["nom"] + " refuse désormais de te vendre ses articles.")


def verifier(monde):
    for o in monde.objets.values():
        for cle in ("proprietaire", "vole_a"):
            if o.get(cle):
                assert o[cle] == "joueur" or (o[cle] in monde.objets and monde.objets[o[cle]]["type"] == "personnage"), "Propriétaire invalide"
        if o.get("vole_par"):
            assert o["vole_par"] == "joueur" and o.get("vole_a") and not o.get("en_vente"), "Possession volée incohérente"
    for id, relation in monde.data["relations_pnj"].items():
        assert id in monde.objets and monde.objets[id]["type"] == "personnage", "Relation sans personnage"
        assert type(relation["soupcon"]) is int and 0 <= relation["soupcon"] <= 3, "Soupçon invalide"
        assert type(relation["vols_surpris"]) is int and relation["vols_surpris"] >= 0, "Nombre de vols invalide"
        assert not relation["dernier_objet"] or relation["dernier_objet"] in monde.objets, "Objet de l'incident inconnu"
        assert type(monde.objets[id]["vigilance"]) is int and 1 <= monde.objets[id]["vigilance"] <= 25, "Vigilance invalide"
