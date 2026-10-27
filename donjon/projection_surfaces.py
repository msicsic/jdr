"""Projection paresseuse des surfaces simples ; aucun changement du monde."""
import json

from .lexique import entites_citees
from .monde import normaliser


# Toute propriété supplémentaire conserve la surface : la projection ne doit
# jamais masquer une mécanique qu'elle ne connaît pas.
CHAMPS_SIMPLES = frozenset((
    "id", "nom", "type", "lieu", "aliases", "materiau", "masse", "mobile",
    "integrite", "maximum", "genre", "pluriel", "support_pose", "position",
    "position_salle", "ancrage_carte",
))


def projeter(monde, faits, objets, intention, proposition=None):
    """Retire seulement les surfaces intactes, vides et sans usage ce tour.

    Les références structurées d'un dossier ou d'une proposition sont des usages,
    au même titre que les noms/alias du lexique commun dans la saisie. Les autres
    catalogues restent disponibles : le langage libre n'offre pas de critère sûr
    pour exclure leurs inventions spontanées.
    """
    demandes = entites_citees(monde, intention)
    # Le lexique utilise les alias d'auteur. Une surface nommée au pluriel
    # doit aussi rester ciblable au singulier, sans liste de mots du scénario.
    from .lexique import _motif
    from .noms import appellations
    texte = normaliser(intention)
    demandes.update(id for id, o in monde.objets.items() if o.get("type") == "surface"
                    and any(_motif(normaliser(nom).rstrip("sx")).search(texte)
                            for nom in appellations(o) if normaliser(nom)))
    # Une ambiance ciblée peut exiger un nouvel ancrage ; garder les supports
    # disponibles pour sa matérialisation, sans préjuger de ce que Luna choisira.
    if faits.get("ambiance_ciblee"):
        return set()
    dossiers = {k: v for k, v in faits.items()
                if not k.startswith("objet:") and k not in
                ("perception", "faits_narratifs_proposables")}
    references = json.dumps([dossiers, proposition], ensure_ascii=False)
    omises = set()
    for vue in objets:
        id = vue["id"]
        o = monde.objets.get(id, {})
        if (o.get("type") == "surface" and set(o) <= CHAMPS_SIMPLES
                and not o.get("mobile") and not o.get("masse")
                and o.get("integrite", 0) == o.get("maximum")
                and not monde.enfants(id) and id not in demandes
                and json.dumps(id, ensure_ascii=False) not in references):
            omises.add(id)
    for id in omises:
        faits.pop("objet:" + id, None)
    catalogue = faits.get("faits_narratifs_proposables", {})
    for champ in ("supports", "qualifiables"):
        if champ in catalogue:
            catalogue[champ] = {id: valeur for id, valeur in catalogue[champ].items()
                                if id not in omises}
    # La liste perceptive reste exhaustive, même sans les fiches complètes.
    # Une projection d'écriture ne change jamais une observation du moteur.
    return omises
