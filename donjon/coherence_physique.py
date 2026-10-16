"""Contre revue des capacités et constats physiques d'un objet existant."""

from .monde import ErreurMonde, reference_exacte


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
Les seuils numériques ne sont déclarés que lors de la création d'un nouvel objet ;
ne les infère pas de la seule matière d'un objet déjà établi. Ne suppose pas que l'intention du joueur rend
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
            raise ErreurMonde("L'objet à qualifier n'existe pas.")
        moyen_id = reference_exacte(objets, ajout.get("moyen", ""))
        entrees.append({"objet": {cle: cible.get(cle) for cle in
                                    ("id", "nom", "type", "materiau", "masse", "mobile",
                                     "description_visuelle", "integrite", "maximum",
                                     "seuil_coupe", "usages", "puissance",
                                     "constats_capacites")},
                        "capacites_proposees": ajout.get("capacites", []),
                        "constats_proposes": ajout.get("ecartees", []),
                        "coupe_possible": ajout.get("coupe_possible"),
                        "moyen": faits.get("objet:" + str(moyen_id), {})})
    return entrees


def controler(entrees, rapport):
    jugements = rapport.get("jugements") if isinstance(rapport, dict) else None
    if (not isinstance(jugements, list) or len(jugements) != len(entrees)
            or any(not isinstance(j, dict) or set(j) != {"compatible", "motif"}
                   or type(j["compatible"]) is not bool or not isinstance(j["motif"], str)
                   for j in jugements)):
        raise ErreurMonde("Contre revue physique incomplète.")
    return [{"partie": "qualification", "segment": i, "texte": "",
             "motif": j["motif"] or "Propriété incompatible avec l'objet établi."}
            for i, j in enumerate(jugements) if not j["compatible"]]
