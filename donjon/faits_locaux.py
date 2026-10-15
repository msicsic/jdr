"""Détails écrits situés : le MJ choisit le contenu, le moteur crée la cible."""

from .francais import designer
from .monde import ErreurMonde, objet
from .perception import eclairage


SCHEMA_INSCRIPTION = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "support": {"type": "string"},
        "inscription": {"type": "string"},
    },
    "required": ["support", "inscription"],
}


def supports(monde):
    """Supports matériels que le joueur peut réellement détailler maintenant."""
    if eclairage(monde)["niveau"] < 2:
        return {}
    from .spatial import proche
    return {id: {"nom": o["nom"], "salle": monde.joueur["salle"]}
            for id, o in monde.objets.items()
            if o["type"] in ("surface", "porte", "assemblage")
            and o["integrite"] > 0 and o["lieu"] != "joueur"
            and not any(e["lieu"] == id and e.get("inscription")
                        for e in monde.objets.values())
            and monde.visible(id)
            and (not monde.data.get("mode_cases") or proche(monde, id))}


def preparer_inscription(monde, proposition, revision=None):
    """Prépare une seule inscription sur une copie ; n'écrit rien dans le monde reçu."""
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant l'enregistrement de l'inscription.")
    if (not isinstance(proposition, dict) or set(proposition) != {"support", "inscription"}
            or not all(isinstance(v, str) for v in proposition.values())):
        raise ErreurMonde("Inscription mal formée.")
    support_id = proposition["support"]
    inscription = proposition["inscription"].strip()
    if support_id not in supports(monde):
        raise ErreurMonde("Ce support n'est pas observable d'assez près et sous assez de lumière.")
    if (not 3 <= len(inscription) <= 240
            or any(ord(c) < 32 for c in inscription)):
        raise ErreurMonde("Texte de l'inscription invalide.")
    travail = monde.copier()
    support = travail.objets[support_id]
    id = f'inscription_{support_id}_{travail.data["revision"] + 1}'
    if id in travail.objets:
        raise ErreurMonde("Cette inscription existe déjà.")
    nom_support = designer(support)
    travail.objets[id] = objet(
        id, "inscription sur " + nom_support, "motif", support_id,
        aliases=["inscription", "gravure", "gravure sur " + nom_support],
        genre="f", materiau=support["materiau"],
        motif="Des signes sont gravés sur " + nom_support + ".",
        inscription=inscription, origine_description="MJ",
        detail_local=True, scene_detail=True)
    travail.data["revision"] += 1
    travail.data.setdefault("enrichissements", []).append({
        "revision": travail.data["revision"], "origine": "MJ",
        "type": "inscription", "support": support_id, "objet": id})
    travail.verifier()
    return travail, id
