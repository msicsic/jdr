"""Compléments descriptifs proposés par le MJ, validés sur une copie du monde."""
import copy

from .monde import ErreurMonde, normaliser, objet
from .perception import eclairage


# Le modèle choisit du texte, jamais une propriété mécanique ou un identifiant neuf.
PARTIES = {
    "visage": ("visage", "m", False, "peau"),
    "cheveux": ("cheveux", "m", True, "cheveux"),
    "yeux": ("yeux", "m", True, "tissu vivant"),
    "barbe": ("barbe", "f", False, "poils"),
    "mains": ("mains", "f", True, "peau"),
}
FACETTES = ("age_apparent", "silhouette", *PARTIES, "voix", "temperament")
SCHEMA_COMPLEMENTS = {
    "type": "object", "additionalProperties": False,
    "properties": {"ajouts": {"type": "array", "minItems": 1, "maxItems": 8,
        "items": {"type": "object", "additionalProperties": False,
            "properties": {"personnage": {"type": "string"},
                           "facette": {"type": "string", "enum": list(FACETTES)},
                           "description": {"type": "string"}},
            "required": ["personnage", "facette", "description"]}}},
    "required": ["ajouts"],
}


def catalogue(monde):
    """Cibles autorisées, sans révéler les personnages jamais rencontrés."""
    resultat = {}
    for id, o in monde.objets.items():
        if o["type"] != "personnage":
            continue
        vu = monde.visible(id) and eclairage(monde)["niveau"] == 2
        if monde.data.get("mode_cases"):
            from .spatial import proche
            vu = vu and proche(monde, id)
        souvenir = monde.data["souvenirs_personnages"].get(id)
        if not vu and souvenir is None:
            continue
        etablies = set(o.get("facettes", {})) | set(o.get("facettes_etablies", []))
        # Compatibilité avec les portraits d'auteur antérieurs aux facettes.
        if o.get("portrait"):
            etablies.update(("age_apparent", "silhouette", "visage"))
        if o.get("maniere_de_parler"):
            etablies.update(("voix", "temperament"))
        for enfant in monde.enfants(id):
            for facette, (nom, *_reste) in PARTIES.items():
                if (enfant.get("facette") == facette
                        or normaliser(enfant["nom"]).startswith(nom + " ")
                        or nom in [normaliser(a) for a in enfant["aliases"]]):
                    etablies.add(facette)
        libres = [f for f in FACETTES if f not in etablies]
        if libres:
            resultat[id] = {"nom": o["nom"], "facettes_disponibles": libres,
                            "perception": "présent et visible" if vu else "souvenir d'une rencontre"}
    return resultat


def preparer_complements(monde, proposition, revision=None):
    """Transaction additive et bornée. Aucun effet sur l'original, même en cas d'échec."""
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant l'enregistrement de la description.", "re-propose à partir des faits actuels.")
    if not isinstance(proposition, dict) or set(proposition) != {"ajouts"}:
        recus = sorted(proposition) if isinstance(proposition, dict) else type(proposition).__name__
        raise ErreurMonde("Complément descriptif mal formé.", f"enrichir a exactement le champ ajouts ; reçu : {recus}.")
    ajouts = proposition["ajouts"]
    if not isinstance(ajouts, list) or not 1 <= len(ajouts) <= 8:
        raise ErreurMonde("Nombre de compléments descriptifs invalide.", "ajouts : une liste de 1 à 8 compléments.")
    autorises = catalogue(monde)
    travail = monde.copier()
    traites = set()
    for ajout in ajouts:
        if (not isinstance(ajout, dict) or set(ajout) != {"personnage", "facette", "description"}
                or any(not isinstance(v, str) for v in ajout.values())):
            raise ErreurMonde("Complément descriptif mal formé.",
                              "chaque ajout a exactement personnage, facette, description (textes).")
        id, facette, texte = ajout["personnage"], ajout["facette"], ajout["description"].strip()
        if id not in autorises:
            objet = monde.objets.get(id)
            if objet is not None and objet["type"] != "personnage":
                raise ErreurMonde("Ce n'est pas un personnage.",
                                  f"« {id} » est un objet : pour le décrire, etablir_faits (detail, ou qualification "
                                  "avec physique pour sa forme et ses dimensions).")
            raise ErreurMonde("Ce personnage ne peut pas être décrit ici.",
                              f"personnage « {id} » : parmi {', '.join(sorted(autorises)) or 'aucun'}.")
        if facette not in autorises[id]["facettes_disponibles"] or (id, facette) in traites:
            raise ErreurMonde("Ce détail est déjà établi.",
                              f"facette « {facette} » de {id} déjà établie ou proposée deux fois ; facettes libres : "
                              f"{', '.join(f for f in autorises[id]['facettes_disponibles'] if (id, f) not in traites) or 'aucune'}.")
        if not 3 <= len(texte) <= 300 or any(ord(c) < 32 for c in texte):
            raise ErreurMonde("Description vide, trop longue ou contenant des caractères de contrôle.",
                              "description : 3 à 300 caractères, sans saut de ligne.")
        traites.add((id, facette))
        p = travail.objets[id]
        if facette in PARTIES:
            nom, genre, pluriel, materiau = PARTIES[facette]
            detail_id = "detail_" + id + "_" + facette
            if detail_id in travail.objets:
                raise ErreurMonde("Ce détail existe déjà.", f"facette {facette} de {id} déjà décrite : retire-la.")
            liaison = "d'" if p["nom"][0].lower() in "aàâeéèêiîoôuûy" else "de "
            travail.objets[detail_id] = objet(
                detail_id, nom + " " + liaison + p["nom"], "partie_corps", id,
                aliases=[nom], genre=genre, pluriel=pluriel, materiau=materiau,
                facette=facette, description_visuelle=texte, origine_description="MJ")
            valeur = {"objet": detail_id}
        else:
            valeur = {"texte": texte}
        p.setdefault("facettes", {})[facette] = valeur
        # Enrichir le souvenir ne copie jamais l'état actuel d'un personnage distant.
        souvenir = travail.data["souvenirs_personnages"].setdefault(id, {
            "nom": p["nom"], "portrait": "", "details": [],
            "source": "Rencontre dans " + travail.data["salles"][travail.joueur["salle"]]["nom"],
        })
        if facette in PARTIES:
            souvenir.setdefault("details", []).append({"nom": travail.objets[detail_id]["nom"],
                                                        "description": texte})
        else:
            souvenir.setdefault("traits", {})[facette] = texte
    travail.actualiser_souvenirs_personnages()
    travail.data["revision"] += 1
    travail.data.setdefault("enrichissements", []).append({
        "revision": travail.data["revision"], "origine": "MJ", "ajouts": copy.deepcopy(ajouts)})
    travail.verifier()
    return travail
