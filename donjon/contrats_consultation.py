"""Consultations sociales : charge, compilation et sens public d'un même acte.

L'audience, les croyances du témoin et le règlement d'un dû restent décidés
par les mécaniques de parole. Aucun mot de la réplique ne choisit un acte.
"""
import copy

from .monde import normaliser
from .refus import RefusDeForme


RESSOURCES_DEMANDEES = {"faim": "de quoi manger", "chaleur": "du combustible pour se chauffer"}
BESOINS_DEMANDES = tuple(RESSOURCES_DEMANDEES)
CONSULTATIONS = {
    "qui": {
        "sens": "Demander l'identité de l'interlocuteur.",
        "champs": (), "requis": (),
    },
    "localisation": {
        "sens": "Demander où se trouve une personne connue, désignée par sujet. La réponse transmet la dernière croyance datée de l'interlocuteur, jamais une position cachée.",
        "champs": ("sujet",), "requis": ("sujet",),
    },
    "ressource": {
        "sens": "Demander si l'interlocuteur possède le bien nommé par sujet (nom, alias, matière ou catégorie), sans le prendre ni le payer. Les codes faim et chaleur demandent plus largement de quoi satisfaire ce besoin ; ils ne remplacent pas un bien précis nommé par le joueur.",
        "champs": ("sujet",), "requis": ("sujet",),
    },
    "reclamer": {
        "sens": "Interroger l'interlocuteur sur ce qu'il doit au locuteur, ou réclamer ce dû : les pièces si sujet est vide, sinon l'objet sujet. Le moteur décide du règlement ; le contenu n'impose pas une formulation impérative.",
        "champs": ("sujet",), "requis": (),
    },
}


def verifier(c, chemin="contenu"):
    if c.get("type") not in CONSULTATIONS:
        raise RefusDeForme("Cet acte n'est pas une consultation sociale.",
                          f"{chemin}.type : reçu {c.get('type')!r} ; accepté : {list(CONSULTATIONS)!r}.")
    contrat = CONSULTATIONS[c["type"]]
    for champ in c:
        if champ not in ("type", "sujet", "attribut", "valeur"):
            raise RefusDeForme("Ce champ ne fait pas partie de cette consultation.",
                              f"{chemin}.{champ} : reçu {c[champ]!r} ; accepté : champ absent.")
    for champ in ("sujet", "attribut", "valeur"):
        if champ in c and not isinstance(c[champ], str):
            raise RefusDeForme("Les paramètres de cette consultation sont mal formés.",
                              f"{chemin}.{champ} : reçu {c[champ]!r} ; accepté : chaîne.")
        if champ not in contrat["champs"] and c.get(champ, "") != "":
            raise RefusDeForme("Le contenu de cette parole comporte un champ sans sens pour son type.",
                              f"{chemin}.{champ} : reçu {c[champ]!r} ; accepté : vide pour type {c['type']}.")
    # La charge interdite se refuse avant l'absence d'un sujet : elle ne peut
    # pas être masquée par un second défaut de la même proposition.
    for champ in contrat["requis"]:
        if not normaliser(c.get(champ, "")):
            raise RefusDeForme("Corvus ne dit pas ce qu'il cherche.",
                              f"{chemin}.{champ} : reçu {c.get(champ)!r} ; accepté : sujet non vide. {contrat['sens']}")


def schema_contenu(schema):
    s = copy.deepcopy(schema)
    contrat = CONSULTATIONS[s["properties"]["type"]["enum"][0]]
    s["description"] = contrat["sens"]
    for champ in ("sujet", "attribut", "valeur"):
        s["properties"][champ] = ({"type": "string", "enum": [""]} if champ not in contrat["champs"] else
                                 {"type": "string", "description": contrat["sens"],
                                  **({"pattern": r"[^\s.?!]"} if champ in contrat["requis"] else {})})
    return s


def contenu(acte, sujet=""):
    """Raccourci structuré : aucun champ voisin ne remplace le sujet."""
    c = {"type": acte, "sujet": sujet, "attribut": "", "valeur": ""}
    verifier(c)
    return c


def typer(monde, c):
    from .paroles import resoudre
    verifier(c)
    acte, sujet = c["type"], c.get("sujet", "").strip()
    if acte == "qui":
        return {"type": acte}
    if acte == "ressource":
        return {"type": acte, "besoin": normaliser(sujet)}
    reference = resoudre(monde, sujet) if sujet else None
    if acte == "reclamer":
        return {"type": acte, "objet": reference} if reference or not sujet else None
    return {"type": acte, "sujet": reference} if reference else None


def public(monde, c, *, reference_ressource=False):
    from .comprehension import repere
    from .paroles import resoudre
    acte, s = c["type"], c.get("sujet", "").strip()
    if acte == "qui":
        return "demander l'identité de l'interlocuteur"
    if acte == "ressource":
        # Le libre conserve sa recherche lexicale ; un choix exact du menu
        # conserve sa référence même après l'apprentissage d'un autre objet.
        sujet = repere(monde, s) if reference_ressource and s in monde.objets else RESSOURCES_DEMANDEES.get(normaliser(s), s)
        return "demander si l'interlocuteur possède " + sujet
    sujet = repere(monde, resoudre(monde, s) or s) if s else ""
    return ("demander où se trouve " + sujet if acte == "localisation" else
            "réclamer le dû : " + (sujet or "pièces"))
