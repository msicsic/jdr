"""Contre revue des capacités et constats physiques d'un objet existant."""

import json

from .monde import ErreurMonde, reference_exacte
from .refus import RapportIllisible, audit


SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {"jugements": {"type": "array", "maxItems": 3,
        "items": {"type": "object", "additionalProperties": False,
                  "properties": {"compatible": {"type": "boolean"},
                                 "motif": {"type": "string"}},
                  "required": ["compatible", "motif"]}}},
    "required": ["jugements"],
}

INSTRUCTIONS = """Tu relis les décisions sur les capacités physiques d'objets EXISTANTS.
Juge chaque qualification à partir de l'objet tel qu'il est déjà décrit, de sa matière,
de son état et des faits du monde. Une capacité ne peut pas contredire une propriété
établie ni rendre trivialement manipulable une chose manifestement plus résistante.
Un jugement de coupe d'un objet existant porte sur l'état de l'objet et le moyen
indiqué. Il peut établir que cet outil peut l'entamer ou qu'il n'y parvient pas.
Il ne prouve rien sur un autre outil. Refuse ce jugement si la matière, la forme,
la description ou les propriétés connues ne le justifient pas. Ne déduis jamais
l'impossibilité du seul fait que la capacité manque dans le contexte.
Les seuils de capacité (coupe, puissance) ne sont déclarés que lors de la création d'un nouvel
objet ; ne les infère pas de la seule matière d'un objet déjà établi. Une description physique
(forme, matière, dimensions, nombre de pièces) peut en revanche décrire un objet existant : juge
si elle correspond à son nom, à sa description et à ce qu'un tel objet est d'ordinaire ; le
moteur vérifie à part qu'elle s'accorde avec sa masse. De même, un contenu proposé (ce que l'objet
contient ou consomme : une lanterne brûle de l'huile) établit un fait encore inconnu : juge
seulement s'il est plausible pour un tel objet, sans le refuser parce qu'il n'était pas déjà
décrit. Une qualification sert précisément à établir ce qui manque. Ne suppose pas que l'intention du joueur rend
la proposition vraie. Si la description est trop vague pour juger, refuse.
Réponds par un jugement pour chaque qualification, dans l'ordre. Aucun récit.
"""


def propositions(reponse, faits):
    if reponse.get("mode") != "etablir_faits":
        return []
    p = reponse.get("proposition")
    if not isinstance(p, dict) or not isinstance(p.get("ajouts"), list):
        return []
    objets = [valeur for cle, valeur in faits.items()
              if cle.startswith("objet:") and isinstance(valeur, dict)]
    entrees = []
    for ajout in p["ajouts"]:
        if not isinstance(ajout, dict) or ajout.get("type") != "qualification":
            continue
        cible_id = reference_exacte(objets, ajout.get("ancrage"))
        cible = faits.get("objet:" + str(cible_id))
        if cible is None:
            raise ErreurMonde("L'objet à qualifier n'existe pas.",
                              f"ancrage : un identifiant parmi les objets fournis (objet:<id>), reçu « {ajout.get('ancrage')} ».")
        moyen_id = reference_exacte(objets, ajout.get("moyen", ""))
        entrees.append({"objet": {cle: cible.get(cle) for cle in
                                    ("id", "nom", "type", "materiau", "masse", "mobile",
                                     "description_visuelle", "integrite", "maximum",
                                     "seuil_coupe", "usages", "puissance",
                                     "constats_capacites")},
                        "capacites_proposees": ajout.get("capacites", []),
                        "constats_proposes": ajout.get("ecartees", []),
                        "coupe_possible": ajout.get("coupe_possible"),
                        "physique_proposee": ajout.get("physique"),
                        "contenu_propose": ajout.get("contenu"),
                        "moyen": faits.get("objet:" + str(moyen_id), {})})
    return entrees


def controler(entrees, rapport):
    jugements = rapport.get("jugements") if isinstance(rapport, dict) else None
    if (not isinstance(jugements, list) or len(jugements) != len(entrees)
            or any(not isinstance(j, dict) or set(j) != {"compatible", "motif"}
                   or type(j["compatible"]) is not bool or not isinstance(j["motif"], str)
                   for j in jugements)):
        raise RapportIllisible("Contre revue physique incomplète.")
    return [audit(j["motif"] or "Propriété incompatible avec l'objet établi.",
                  "une qualification accordée à ce que l'objet est déjà (matière, description, masse, état), "
                  "ou aucune", partie="qualification", segment=i, recu=_propose(entrees[i]),
                  verdict=("incompatible", j["motif"]),
                  lieu=f"qualification {i} (objet {(entrees[i].get('objet') or {}).get('id')})")
            for i, j in enumerate(jugements) if not j["compatible"]]


def _propose(entree):
    """Ce que la qualification propose, en champs : ce que l'auditeur a jugé."""
    champs = {"capacites": entree.get("capacites_proposees"), "ecartees": entree.get("constats_proposes"),
              "coupe_possible": entree.get("coupe_possible"), "physique": entree.get("physique_proposee"),
              "contenu": entree.get("contenu_propose")}
    return "; ".join(f"{k} = {json.dumps(v, ensure_ascii=False)}" for k, v in champs.items()
                     if v not in (None, [], {}, ""))
