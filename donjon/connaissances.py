"""Savoirs propres aux PNJ : données d'auteur et compléments narratifs persistants."""
import copy

from .monde import ErreurMonde


SUJETS = {
    "apprentissage_metier": "Comment le personnage a appris son métier connu ; aucun pouvoir ni bonus nouveau.",
    "souvenir_personnel": "Un souvenir ordinaire, sans nouveau lieu visitable, PNJ interactif, trésor ou secret.",
    "tradition_locale": "Une coutume ou expression locale sans effet magique ni indice mécanique.",
    "motivation_personnelle": "Une raison personnelle compatible avec ses intentions connues, sans nouvelle mission ni récompense.",
}
SCHEMA_SAVOIRS = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "personnage": {"type": "string"},
        "savoirs": {"type": "array", "minItems": 1, "maxItems": 3,
            "items": {"type": "object", "additionalProperties": False,
                "properties": {"sujet": {"type": "string"}, "texte": {"type": "string"}},
                "required": ["sujet", "texte"]}},
    },
    "required": ["personnage", "savoirs"],
}


def installer(monde):
    d = monde.data
    d.setdefault("savoirs_pnj", {})
    d.setdefault("sujets_savoirs_pnj", {})
    d.setdefault("ajouts_savoirs", [])
    for id, o in monde.objets.items():
        if o["type"] == "personnage":
            d["savoirs_pnj"].setdefault(id, {})
            # Un scénario peut fournir {} pour interdire toute invention à ce PNJ.
            d["sujets_savoirs_pnj"].setdefault(id, copy.deepcopy(SUJETS))


def presents(monde):
    return [id for id, o in monde.objets.items()
            if o["type"] == "personnage" and monde.present_physique(id)
            and (not monde.data.get("mode_cases") or monde.visible(id))]


def contexte(monde):
    return {id: copy.deepcopy(monde.data["savoirs_pnj"].get(id, {})) for id in presents(monde)}


def catalogue(monde):
    resultat = {}
    for id in presents(monde):
        etablis = monde.data["savoirs_pnj"].get(id, {})
        libres = {s: consigne for s, consigne in monde.data["sujets_savoirs_pnj"].get(id, {}).items()
                  if s not in etablis}
        if libres:
            resultat[id] = {"nom": monde.objets[id]["nom"], "sujets": libres}
    return resultat


def preparer_savoirs(monde, proposition, revision=None):
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant l'enregistrement des connaissances.")
    if not isinstance(proposition, dict) or set(proposition) != {"personnage", "savoirs"}:
        raise ErreurMonde("Connaissances mal formées.")
    id, ajouts = proposition["personnage"], proposition["savoirs"]
    autorises = catalogue(monde)
    if not isinstance(id, str) or id not in autorises:
        raise ErreurMonde("Ce personnage n'est pas présent ou n'a aucun savoir à compléter.")
    if not isinstance(ajouts, list) or not 1 <= len(ajouts) <= 3:
        raise ErreurMonde("Nombre de connaissances invalide.")
    travail = monde.copier()
    connus = travail.data["savoirs_pnj"][id]
    revision_suivante = monde.data["revision"] + 1
    for ajout in ajouts:
        if (not isinstance(ajout, dict) or set(ajout) != {"sujet", "texte"}
                or any(not isinstance(v, str) for v in ajout.values())):
            raise ErreurMonde("Connaissance mal formée.")
        sujet, texte = ajout["sujet"], ajout["texte"].strip()
        if sujet not in autorises[id]["sujets"] or sujet in connus:
            raise ErreurMonde("Ce sujet est déjà établi ou n'est pas ouvert à l'invention.")
        if not 3 <= len(texte) <= 600 or any(ord(c) < 32 for c in texte):
            raise ErreurMonde("Texte de connaissance vide, trop long ou contenant des caractères de contrôle.")
        connus[sujet] = {"texte": texte, "origine": "MJ", "revision": revision_suivante}
    travail.data["revision"] = revision_suivante
    travail.data["ajouts_savoirs"].append({"revision": revision_suivante, **copy.deepcopy(proposition)})
    travail.verifier()
    return travail


def verifier(monde):
    for id, savoirs in monde.data["savoirs_pnj"].items():
        assert id in monde.objets and monde.objets[id]["type"] == "personnage", "Savoirs sans personnage"
        assert isinstance(savoirs, dict), "Savoirs invalides"
        for sujet, savoir in savoirs.items():
            assert isinstance(sujet, str) and sujet, "Sujet invalide"
            assert set(savoir) == {"texte", "origine", "revision"}, "Connaissance invalide"
            assert isinstance(savoir["texte"], str) and savoir["texte"].strip(), "Connaissance vide"
            assert savoir["origine"] in ("jeu", "MJ"), "Origine inconnue"
            assert type(savoir["revision"]) is int and 0 <= savoir["revision"] <= monde.data["revision"], "Révision invalide"
    for id, sujets in monde.data["sujets_savoirs_pnj"].items():
        assert id in monde.data["savoirs_pnj"] and isinstance(sujets, dict), "Sujets sans personnage"
        assert all(isinstance(s, str) and s and isinstance(c, str) and c for s, c in sujets.items()), "Sujet invalide"
