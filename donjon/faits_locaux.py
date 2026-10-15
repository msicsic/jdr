"""Faits narratifs typés, validés et appliqués sur une copie du monde."""

import copy

from .francais import designer
from .monde import ErreurMonde, normaliser, objet
from .perception import eclairage


TYPES = ("detail", "inscription", "parole")
SCHEMA_FAITS = {
    "type": "object", "additionalProperties": False,
    "properties": {"ajouts": {"type": "array", "minItems": 1, "maxItems": 3,
        "items": {"type": "object", "additionalProperties": False,
            "properties": {
                "type": {"type": "string", "enum": list(TYPES)},
                "ancrage": {"type": "string"},
                "nom": {"type": "string"},
                "genre": {"type": "string", "enum": ["", "m", "f"]},
                "texte": {"type": "string"},
            },
            "required": ["type", "ancrage", "nom", "genre", "texte"]}}},
    "required": ["ajouts"],
}


def supports(monde):
    """Supports que le joueur peut effectivement détailler maintenant."""
    if eclairage(monde)["niveau"] < 2:
        return {}
    from .spatial import proche
    return {id: {"nom": o["nom"], "salle": monde.joueur["salle"]}
            for id, o in monde.objets.items()
            if o["type"] not in ("personnage", "partie_corps", "motif", "detail")
            and o["integrite"] > 0
            and monde.visible(id)
            and (not monde.data.get("mode_cases") or proche(monde, id))}


def catalogue(monde):
    from .dialogues import interlocuteurs
    return {"supports": supports(monde), "locuteurs": {
        id: {"nom": p["nom"]} for id, p in interlocuteurs(monde).items()}}


def _texte(texte, maximum):
    return (isinstance(texte, str) and 3 <= len(texte.strip()) <= maximum
            and all(ord(c) >= 32 for c in texte))


def preparer_faits(monde, proposition, revision=None):
    """Valide plusieurs faits liés et les applique atomiquement sur une copie."""
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant l'enregistrement des faits.")
    if not isinstance(proposition, dict) or set(proposition) != {"ajouts"}:
        raise ErreurMonde("Faits narratifs mal formés.")
    ajouts = proposition["ajouts"]
    if not isinstance(ajouts, list) or not 1 <= len(ajouts) <= 3:
        raise ErreurMonde("Nombre de faits narratifs invalide.")
    autorises = catalogue(monde)
    travail = monde.copier()
    rendus = []
    etablis = []
    for index, ajout in enumerate(ajouts, 1):
        if (not isinstance(ajout, dict) or set(ajout) != {"type", "ancrage", "nom", "genre", "texte"}
                or any(not isinstance(v, str) for v in ajout.values())):
            raise ErreurMonde("Fait narratif mal formé.")
        nature, ancrage = ajout["type"], ajout["ancrage"]
        nom, genre, texte = ajout["nom"].strip(), ajout["genre"], ajout["texte"].strip()
        if nature not in TYPES or not _texte(texte, 300):
            raise ErreurMonde("Type ou texte du fait narratif invalide.")
        if nature == "parole":
            if nom or genre or ancrage not in autorises["locuteurs"] or len(texte) > 240:
                raise ErreurMonde("Cette parole ne peut pas être attribuée à ce personnage ici.")
            from .sons import auditeurs
            source = travail.joueur["salle"]
            entendants = auditeurs(travail, source, 2)
            if "joueur" not in entendants:
                entendants.append("joueur")
            evenement = {"locuteur": ancrage, "texte": texte, "salle": source,
                         "minute": travail.data["minutes"], "auditeurs": entendants,
                         "revision": monde.data["revision"] + 1}
            travail.data.setdefault("paroles_pnj", []).append(evenement)
            rendus.append(travail.objets[ancrage]["nom"] + " dit : « " + texte + " ».")
            etablis.append({"type": nature, "locuteur": ancrage})
            continue
        if ancrage not in autorises["supports"]:
            raise ErreurMonde("Ce support n'est pas observable d'assez près et sous assez de lumière.")
        support = travail.objets[ancrage]
        if nature == "inscription":
            if nom or genre or len(texte) > 240 or any(e["lieu"] == ancrage and e.get("inscription")
                                              for e in travail.objets.values()):
                raise ErreurMonde("Une inscription est déjà établie sur ce support, ou sa forme est invalide.")
            nom_support = designer(support)
            detail = objet("", "inscription sur " + nom_support, "motif", ancrage,
                           aliases=["inscription", "gravure", "gravure sur " + nom_support],
                           genre="f", materiau=support["materiau"],
                           motif="Des signes sont gravés sur " + nom_support + ".",
                           inscription=texte)
            rendus.append("Tu remarques une inscription gravée sur " + nom_support
                          + " : « " + texte + " ».")
        else:
            if (genre not in ("m", "f") or not _texte(nom, 60)
                    or any(normaliser(e["nom"]) == normaliser(nom)
                                             for e in travail.enfants(ancrage))):
                raise ErreurMonde("Ce détail n'a pas de nom distinct sur son support.")
            detail = objet("", nom, "detail", ancrage, aliases=[nom],
                           genre=genre, materiau="", description_visuelle=texte)
            rendus.append("Tu remarques " + designer(detail, "indefini") + " sur "
                          + designer(support) + ". " + texte)
        id = f'fait_{monde.data["revision"] + 1}_{index}'
        if id in travail.objets:
            raise ErreurMonde("Ce détail existe déjà.")
        detail.update(id=id, origine_description="MJ", detail_local=True, scene_detail=True)
        travail.objets[id] = detail
        travail.data.setdefault("faits_vus", []).append({
            "objet": id, "nom": detail["nom"], "salle": travail.joueur["salle"],
            "description": detail.get("description_visuelle", ""),
            "inscription": detail.get("inscription", "")})
        etablis.append({"type": nature, "support": ancrage, "objet": id})
    travail.data["revision"] += 1
    travail.data.setdefault("enrichissements", []).append({
        "revision": travail.data["revision"], "origine": "MJ",
        "faits": copy.deepcopy(etablis)})
    travail.verifier()
    return travail, " ".join(rendus), etablis


def verifier(monde):
    assert (isinstance(monde.data.get("faits_vus", []), list)
            and all(isinstance(s, dict)
                    and set(s) == {"objet", "nom", "salle", "description", "inscription"}
                    and s["salle"] in monde.data["salles"]
                    and all(isinstance(s[k], str) for k in s)
                    for s in monde.data.get("faits_vus", []))), "Souvenirs de faits invalides"
    for parole in monde.data.get("paroles_pnj", []):
        assert (set(parole) == {"locuteur", "texte", "salle", "minute", "auditeurs", "revision"}
                and parole["locuteur"] in monde.objets
                and monde.objets[parole["locuteur"]]["type"] == "personnage"
                and parole["salle"] in monde.data["salles"]
                and _texte(parole["texte"], 240)
                and isinstance(parole["auditeurs"], list)
                and all(a == "joueur" or a in monde.objets for a in parole["auditeurs"])
                and type(parole["minute"]) is int and parole["minute"] >= 0
                and type(parole["revision"]) is int
                and 0 <= parole["revision"] <= monde.data["revision"]), "Parole de PNJ invalide"
