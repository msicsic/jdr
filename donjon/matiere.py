"""Description physique commune des objets : forme, dimensions, matière, nombre de pièces.

Le MJ (ou l'auteur du scénario) décrit ce qu'est concrètement un objet ; le moteur vérifie la
cohérence de cette description avec la masse connue et en déduit ce qui en découle (longueur
disponible, charge supportée). Les densités et résistances sont des conventions de jeu,
pas un calcul d'ingénierie.
"""
import math

from .francais import quantite
from .monde import ErreurMonde

# Densité en kg/m³ ; flexion et traction en kg de charge de jeu par cm² de section.
MATIERES = {
    "bois": {"densite": 600, "flexion": 5.6, "traction": 60},
    "chene": {"densite": 750, "flexion": 7, "traction": 80},
    "fer": {"densite": 7800, "flexion": 60, "traction": 400},
    "acier": {"densite": 7850, "flexion": 80, "traction": 600},
    "bronze": {"densite": 8700, "flexion": 40, "traction": 250},
    "pierre": {"densite": 2500, "flexion": 2, "traction": 3},
    "fibres": {"densite": 1300, "flexion": 0, "traction": 875},
    "chanvre": {"densite": 1400, "flexion": 0, "traction": 900},
    "cuir": {"densite": 900, "flexion": 0.5, "traction": 150},
    "tissu": {"densite": 1300, "flexion": 0, "traction": 40},
}
# Dimensions attendues par forme, avec leurs bornes en cm. Une barre a soit un diamètre, soit
# une largeur et une épaisseur.
FORMES = {
    "barre": {"longueur_cm": (10, 1500), "diametre_cm": (0.5, 80), "largeur_cm": (0.5, 80), "epaisseur_cm": (0.3, 80)},
    "plaque": {"longueur_cm": (10, 500), "largeur_cm": (10, 300), "epaisseur_cm": (0.2, 30)},
    "lien": {"longueur_cm": (10, 10000), "diametre_cm": (0.1, 5)},
    "bloc": {"longueur_cm": (1, 300), "largeur_cm": (1, 300), "hauteur_cm": (1, 300)},
    "etoffe": {"longueur_cm": (10, 1000), "largeur_cm": (10, 500), "epaisseur_cm": (0.05, 2)},
}
DIMENSIONS = ("longueur_cm", "largeur_cm", "epaisseur_cm", "diametre_cm", "hauteur_cm")
REMPLISSAGE_LIEN = 0.75   # un lien tressé n'est pas plein
ECART_MASSE = (0.5, 2.0)  # tolérance entre masse connue et masse déduite de la description
PIECES_MAX = 100
# Rôle d'une forme dans la fabrication actuelle (``artisanat``) : une donnée déduite.
ROLES = {"barre": "perche", "lien": "lien"}

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "forme": {"type": "string", "enum": list(FORMES)},
        "matiere": {"type": "string", "enum": list(MATIERES)},
        "dimensions": {"type": "object", "additionalProperties": False,
                       "properties": {d: {"type": "number"} for d in DIMENSIONS},
                       "required": list(DIMENSIONS)},
        "pieces": {"type": "integer"},
        "nom_piece": {"type": "string", "description": "Nom d'une pièce d'un lot (« planche de bac »), vide pour un objet seul."},
    },
    "required": ["forme", "matiere", "dimensions", "pieces", "nom_piece"],
}

# L'encombrement dans la case et les vides autour de l'objet, indépendants du volume
# de matière (une table creuse n'est pas un bloc plein de bois).
PASSAGE = {"degagement_cm": (0, 500), "hauteur_cm": (1, 600),
           "largeur_cm": (1, 100), "profondeur_cm": (1, 100), "charge_kg": (0, 2000)}
SCHEMA_PASSAGE = {"type": "object", "additionalProperties": False,
                  "properties": {**{k: {"type": "number"} for k in PASSAGE},
                                 "appuis": {"type": "boolean"}},
                  "required": [*PASSAGE, "appuis"]}
SCHEMA_PASSAGE["properties"]["degagement_cm"]["description"] = "Hauteur du vide sous l'objet, depuis le sol."
SCHEMA_PASSAGE["properties"]["hauteur_cm"]["description"] = (
    "Hauteur du sommet depuis le même sol, strictement supérieure au dégagement sous l'objet.")


def valider_passage(o, passage):
    """Géométrie locale, sans passage permanent ni modification de l'opacité."""
    if not o.get("bloque_passage"):
        raise ErreurMonde("Cet objet ne barre pas le passage.",
                          f"{o['id']}.bloque_passage={o.get('bloque_passage')} : accepté true.")
    if not isinstance(passage, dict) or set(passage) != {*PASSAGE, "appuis"}:
        raise ErreurMonde("La forme du passage est incomplète.",
                          f"{o['id']}.passage={passage!r} : accepté exactement {', '.join(SCHEMA_PASSAGE['required'])}.")
    for k, (bas, haut) in PASSAGE.items():
        v = passage[k]
        if type(v) not in (int, float) or not math.isfinite(v) or not bas <= v <= haut:
            raise ErreurMonde("Une dimension du passage n'est pas plausible.",
                              f"{o['id']}.passage.{k}={v!r} : accepté {bas}..{haut}.")
    if type(passage["appuis"]) is not bool:
        raise ErreurMonde("Les prises doivent être décrites.",
                          f"{o['id']}.passage.appuis={passage['appuis']!r} : accepté true ou false.")
    if passage["degagement_cm"] >= passage["hauteur_cm"]:
        raise ErreurMonde("Le dessous ne peut pas être au-dessus du sommet.",
                          f"{o['id']}.passage.degagement_cm={passage['degagement_cm']} : accepté < hauteur_cm={passage['hauteur_cm']}.")
    return dict(passage)


def decrire_passage(o):
    p = o.get("passage")
    if p is None:
        return ""
    return (f"Dégagement dessous : {p['degagement_cm']:g} cm ; sommet à {p['hauteur_cm']:g} cm du sol ; "
            f"largeur libre : {p['largeur_cm']:g} cm ; profondeur à traverser : {p['profondeur_cm']:g} cm. "
            + ("Des prises permettent de grimper. " if p["appuis"] else "Aucune prise pour grimper. ")
            + f"Charge supportée : {p['charge_kg']:g} kg")


def _dimensions_utiles(forme, dimensions):
    """Les dimensions qui comptent pour cette forme ; 0 marque une dimension sans objet."""
    utiles = {d: v for d, v in dimensions.items() if d in FORMES[forme] and v}
    if forme == "barre":
        if "diametre_cm" in utiles:
            utiles = {d: v for d, v in utiles.items() if d in ("longueur_cm", "diametre_cm")}
        else:
            utiles.pop("diametre_cm", None)
    return utiles


def section_cm2(physique):
    d = physique["dimensions"]
    if "diametre_cm" in d:
        return math.pi * (d["diametre_cm"] / 2) ** 2
    if physique["forme"] == "bloc":
        return d["largeur_cm"] * d["hauteur_cm"]
    return d["largeur_cm"] * d["epaisseur_cm"]


def masse_deduite(physique):
    """Masse d'après la description : volume × densité, pour toutes les pièces."""
    d = physique["dimensions"]
    volume = section_cm2(physique) * d["longueur_cm"]
    if physique["forme"] == "lien":
        volume *= REMPLISSAGE_LIEN
    return volume * MATIERES[physique["matiere"]]["densite"] / 1e6 * physique["pieces"]


def charge_deduite(physique):
    """Charge de jeu d'une pièce : en flexion pour une barre ou une plaque, en traction pour un lien."""
    m = MATIERES[physique["matiere"]]
    if physique["forme"] in ("lien", "etoffe"):
        return round(section_cm2(physique) * m["traction"])
    return round(section_cm2(physique) * m["flexion"])


def valider(o, physique):
    """Refus explicite si la description n'est pas utilisable pour cet objet ; sinon la forme normalisée."""
    if not isinstance(physique, dict) or set(physique) != {"forme", "matiere", "dimensions", "pieces", "nom_piece"}:
        raise ErreurMonde("Description physique mal formée.",
                          "physique : exactement forme, matiere, dimensions, pieces, nom_piece.")
    forme, matiere, pieces = physique["forme"], physique["matiere"], physique["pieces"]
    if forme not in FORMES:
        raise ErreurMonde("Forme inconnue.", f"forme parmi {', '.join(FORMES)} (reçu « {forme} »).")
    if matiere not in MATIERES:
        raise ErreurMonde("Matière inconnue.", f"matiere parmi {', '.join(MATIERES)} (reçu « {matiere} »).")
    if o.get("materiau") in MATIERES and matiere != o["materiau"]:
        raise ErreurMonde("Cette matière contredit l'objet.",
                          f"{o['id']} est en {o['materiau']} : matiere = {o['materiau']}.")
    if type(pieces) is not int or not 1 <= pieces <= PIECES_MAX:
        raise ErreurMonde("Nombre de pièces invalide.", f"pieces : entier de 1 à {PIECES_MAX} (1 pour un objet seul).")
    if "charges" in o and pieces != o["charges"]:
        # Un lot ne se compte que d'une façon : ses pièces sont ses utilisations.
        raise ErreurMonde("Le nombre de pièces contredit ce qu'il reste.",
                          f"{o['id']} compte {o['charges']} unités : pieces = {o['charges']}.")
    nom_piece = physique["nom_piece"].strip() if isinstance(physique["nom_piece"], str) else None
    if nom_piece is None or (pieces > 1 and not 3 <= len(nom_piece) <= 60):
        raise ErreurMonde("Il manque le nom d'une pièce.",
                          "nom_piece : le nom d'une pièce du lot (« planche de bac »), 3 à 60 caractères ; vide pour un objet seul.")
    dims = physique["dimensions"]
    if (not isinstance(dims, dict) or set(dims) - set(DIMENSIONS)
            or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in dims.values())):
        raise ErreurMonde("Dimensions mal formées.",
                          f"dimensions : {', '.join(DIMENSIONS)} en cm, nombres positifs, 0 pour une dimension sans objet.")
    utiles = _dimensions_utiles(forme, dims)
    requises = ({"longueur_cm", "diametre_cm"} if forme == "barre" and "diametre_cm" in utiles else
                {"longueur_cm", "largeur_cm", "epaisseur_cm"} if forme == "barre" else
                set(FORMES[forme]))
    if set(utiles) != requises:
        raise ErreurMonde("Il manque une dimension.",
                          f"{forme} : {', '.join(sorted(requises))} non nuls"
                          + (" (ou longueur_cm et diametre_cm pour une barre ronde)" if forme == "barre" else "") + ".")
    for d, v in utiles.items():
        bas, haut = FORMES[forme][d]
        if not bas <= v <= haut:
            raise ErreurMonde("Une dimension n'est pas plausible.", f"{d} d'une {forme} : de {bas} à {haut} cm (reçu {v:g}).")
    normale = {"forme": forme, "matiere": matiere, "pieces": pieces, "dimensions": utiles}
    if pieces > 1:
        normale["nom_piece"] = nom_piece
    masse = o.get("masse", 0)
    if masse > 0:
        deduite = masse_deduite(normale)
        if not ECART_MASSE[0] <= masse / deduite <= ECART_MASSE[1]:
            raise ErreurMonde("Cette description ne correspond pas au poids de l'objet.",
                              f"{o['id']} pèse {masse:g} kg ; la description donne {deduite:.2g} kg "
                              f"(volume × densité de {matiere}) : ajuste dimensions ou pieces.")
    return normale


def appliquer(o, physique):
    """Enregistre la description et ce que le moteur en déduit."""
    o["physique"] = physique
    deduire(o)


def deduire(o):
    p = o["physique"]
    if p["forme"] in ROLES:
        o["ressource"] = ROLES[p["forme"]]
        o["longueur_cm"] = p["dimensions"]["longueur_cm"]
        o["charge_jeu_kg"] = charge_deduite(p)
        if "diametre_cm" in p["dimensions"]:
            o["diametre_cm"] = p["dimensions"]["diametre_cm"]


def fixer_longueur(o, longueur_cm):
    """Une pièce raccourcie : la description et ce qui en découle suivent."""
    o["longueur_cm"] = longueur_cm
    if "physique" in o:
        o["physique"]["dimensions"]["longueur_cm"] = longueur_cm


def installer(m):
    """Les descriptions fournies par l'auteur reçoivent leurs grandeurs déduites."""
    for o in m.objets.values():
        if "physique" in o and "charge_jeu_kg" not in o and o["physique"]["forme"] in ROLES:
            deduire(o)


def decrire(o):
    """Ce que l'examen montre de la description physique."""
    p = o.get("physique")
    if not p:
        return ""
    d = p["dimensions"]
    def cm(v):
        return (f"{v / 100:g} m" if v >= 100 else f"{v:g} cm").replace(".", ",")
    if "diametre_cm" in d:
        taille = f"{cm(d['longueur_cm'])} de long, {cm(d['diametre_cm'])} de diamètre"
    else:
        taille = " × ".join(cm(d[k]) for k in ("longueur_cm", "largeur_cm", "epaisseur_cm", "hauteur_cm") if k in d)
    return (f"{quantite(p['pieces'], 'pièce')} de {taille} chacune" if p["pieces"] > 1 else taille.capitalize())


def verifier(m):
    for o in m.objets.values():
        if "passage" in o:
            try:
                valider_passage(o, o["passage"])
            except ErreurMonde as exc:
                raise AssertionError(str(exc)) from exc
        if "contenu" in o:
            assert o["contenu"].get("matiere") in SUBSTANCES, "Contenu inconnu"
        if "physique" in o:
            p = o["physique"]
            assert p["forme"] in FORMES and p["matiere"] in MATIERES, "Description physique inconnue"
            assert 1 <= p["pieces"] <= PIECES_MAX, "Nombre de pièces invalide"


# Ce qu'un objet contient ou consomme. La quantité reste celle que le moteur suit déjà
# (minutes de combustible d'une source de lumière) ; seule la nature est décrite ici.
SUBSTANCES = {
    "huile": {"combustible": True, "article": "de l'huile"},
    "suif": {"combustible": True, "article": "du suif"},
    "cire": {"combustible": True, "article": "de la cire"},
    "poix": {"combustible": True, "article": "de la poix"},
    "bois": {"combustible": True, "article": "du bois"},
    "charbon": {"combustible": True, "article": "du charbon"},
    "eau": {"combustible": False, "article": "de l'eau"},
    "vin": {"combustible": False, "article": "du vin"},
    "grain": {"combustible": False, "article": "du grain"},
    "sable": {"combustible": False, "article": "du sable"},
}
SCHEMA_CONTENU = {"type": "object", "additionalProperties": False,
                  "properties": {"matiere": {"type": "string", "enum": list(SUBSTANCES)}},
                  "required": ["matiere"]}


def valider_contenu(o, contenu):
    if not isinstance(contenu, dict) or set(contenu) != {"matiere"}:
        raise ErreurMonde("Contenu mal formé.", "contenu : exactement matiere.")
    matiere = contenu["matiere"]
    if matiere not in SUBSTANCES:
        raise ErreurMonde("Substance inconnue.", f"matiere parmi {', '.join(SUBSTANCES)} (reçu « {matiere} »).")
    if "combustible" in o and not SUBSTANCES[matiere]["combustible"]:
        brulables = ", ".join(s for s, v in SUBSTANCES.items() if v["combustible"])
        raise ErreurMonde("Une source de lumière brûle un combustible.",
                          f"{o['id']} consomme du combustible : matiere parmi {brulables}.")
    return {"matiere": matiere}


def decrire_contenu(o):
    c = o.get("contenu")
    if not c:
        return ""
    from .francais import designer
    verbe = " brûle " if "combustible" in o else " contient "
    return designer(o, debut=True) + verbe + SUBSTANCES[c["matiere"]]["article"]


def retirer_piece(o):
    """Une pièce quitte le lot (prélevée ou brûlée) : sa masse part avec elle."""
    p = o.get("physique")
    if p and p["pieces"] > 1:
        o["masse"] = round(o["masse"] - o["masse"] / p["pieces"], 3)
        p["pieces"] -= 1
        if p["pieces"] == 1:
            # La dernière pièce du lot porte désormais son nom (« planche de bac »), au singulier.
            nom = p.pop("nom_piece", None)
            if nom:
                o["aliases"] = list(dict.fromkeys([*o.get("aliases", []), o["nom"], nom]))
                o["nom"] = nom
                o["pluriel"] = False


def id_piece(m, lot):
    k = 1
    while f"{lot}_{k}" in m.objets:
        k += 1
    return f"{lot}_{k}"


def prelever_piece(m, lot_id, piece_id):
    """Crée une pièce du lot, à sa place, avec sa description ; le lot diminue d'autant."""
    from .monde import objet
    lot = m.objets[lot_id]
    p = lot["physique"]
    nom = p["nom_piece"]
    piece = objet(piece_id, nom, lot["type"], lot["lieu"], aliases=[nom], genre=lot.get("genre", "m"),
                  materiau=lot["materiau"], masse=round(lot["masse"] / p["pieces"], 3), mobile=True,
                  physique={"forme": p["forme"], "matiere": p["matiere"], "pieces": 1,
                            "dimensions": dict(p["dimensions"])})
    for cle in ("usages", "duree_combustion", "proprietaire", "position", "position_salle", "seuil_coupe"):
        if cle in lot:
            piece[cle] = list(lot[cle]) if isinstance(lot[cle], list) else lot[cle]
    if "contenu" in lot:
        # Le contenu décrit la substance, pas une quantité : chaque pièce l'hérite.
        piece["contenu"] = dict(lot["contenu"])
    if "charges" in lot:
        piece["charges"] = 1
        lot["charges"] -= 1
    deduire(piece)
    m.objets[piece_id] = piece
    retirer_piece(lot)
    return piece
