"""Contrats canoniques de composition et d'attente, sans analyse du français.

Les autres familles gardent leurs compilateurs et leurs validations actuels.
Une occasion n'est pas un prédicat sur l'état ou les gestes d'un tiers.
"""
import copy

from .monde import ErreurMonde
from .temps import ATTENTE_MAX, MINUTE, dire_duree, lire_duree


COMPOSITION = {
    "minimum": 1, "maximum": 6,
    "sens": "Exécuter les étapes dans l'ordre ; aucune étape n'est une simple manière de la suivante. "
            "Ce contrat ne représente pas de condition libre sur un événement : ne pas la remplacer par une durée ou un geste voisin.",
    "arret": "Arrêt au premier échec ; les étapes déjà réussies restent acquises.",
}
ATTENTES = {
    "bloc": {
        "minutes": 5, "titre": "Attendre cinq minutes.",
        "sens": "Cible vide : cinq minutes en bloc, sans interruption perceptive.",
        "public": "L'attente se déroule en bloc, sans interruption perceptive.",
        "effets": [("calmer", "", 3)],
    },
    "duree": {
        "sens": "Cible : durée en secondes ; arrêt anticipé si quelqu'un paraît ou si un événement sonore réclame l'attention.",
        "public": "Tu cesses d'attendre si quelqu'un paraît ou si un événement sonore réclame ton attention.",
    },
    "occasion": {
        "minutes": 2, "titre": "Guetter une occasion pendant deux minutes.",
        "sens": "Deux minutes à guetter une occasion, sans cible, destination, outil ni jet ; méthode simple. "
                "Ne commande aucun geste à un PNJ et ne garantit aucun événement, orientation ou discrétion.",
        "resultat": "Deux minutes passent à guetter une occasion ; rien ne garantit que le geste passera inaperçu.",
        "public": "Aucun événement ni geste ou changement d'orientation d'un tiers n'est garanti. "
                  "La discrétion du geste suivant n'est pas garantie.",
    },
}
CHAMPS_ATTENTE = {"outil": "", "methode": "simple", "difficulte": 0}
CHAMPS_OCCASION = {"cible": "", "destination": "", **CHAMPS_ATTENTE}
RACCOURCIS_VOL = {
    "simple": {"operations": ("deplacer",), "sens": "Prise discrète directe, sans attente."},
    "finesse": {"operations": ("patienter", "deplacer"),
                "sens": "Guetter une occasion pendant deux minutes puis prendre discrètement ; "
                        "aucune orientation ni réaction d'un tiers n'est garantie."},
}


def verifier_champs(p, valeurs, operation):
    for champ, accepte in valeurs.items():
        if p[champ] != accepte:
            raise ErreurMonde("Ces paramètres ne décrivent pas cette attente.",
                              f"{operation}.{champ} : reçu {p[champ]!r} ; accepté : {accepte!r}.")


def preparer_attente(plan):
    p = plan.proposition
    verifier_champs(p, CHAMPS_ATTENTE, "attendre")
    plan.effort = False
    if not p["cible"]:
        contrat = ATTENTES["bloc"]
        plan.titre, plan.minutes = contrat["titre"], contrat["minutes"]
        plan.effets = copy.deepcopy(contrat["effets"])
        return plan
    dixiemes = lire_duree(p["cible"])
    if dixiemes is None:
        raise ErreurMonde("Dis combien de temps attendre : « attendre 30 s », « attendre 10 min ».",
                          f"attendre.cible : reçu {p['cible']!r} ; accepté : cible vide (cinq minutes) "
                          f"ou une durée en secondes, de 0.1 à {ATTENTE_MAX // 10}.")
    plan.titre = "Attendre " + dire_duree(dixiemes) + "."
    plan.minutes, plan.dixiemes = dixiemes // MINUTE, dixiemes
    return plan


def preparer_occasion(plan, e):
    verifier_champs(e, CHAMPS_OCCASION, "patienter")
    contrat = ATTENTES["occasion"]
    plan.titre, plan.minutes, plan.effort = contrat["titre"], contrat["minutes"], False
    return plan


def developper_vol(cible, methode, etape):
    """Le raccourci finesse conserve l'attente ; simple reste une prise discrète directe."""
    return [etape(op) if op == "patienter" else etape(op, cible, "joueur", methode="discret")
            for op in RACCOURCIS_VOL[methode]["operations"]]


def schema_occasion(schema_etape):
    s = copy.deepcopy(schema_etape)
    s["description"] = ATTENTES["occasion"]["sens"]
    for champ, valeur in {"operation": "patienter", **CHAMPS_OCCASION}.items():
        s["properties"][champ] = {"type": "integer" if champ == "difficulte" else "string", "enum": [valeur]}
    return s


def schemas_actions(schema):
    """Branches disjointes : un outil ou une méthode voisine ne remplace pas une durée."""
    autres, attente = copy.deepcopy(schema), copy.deepcopy(schema)
    autres["properties"]["action"]["enum"].remove("attendre")
    autres["properties"]["methode"]["description"] = "Pour voler : " + " ".join(
        f"{methode} : {contrat['sens']}" for methode, contrat in RACCOURCIS_VOL.items())
    attente["description"] = ATTENTES["bloc"]["sens"] + " " + ATTENTES["duree"]["sens"]
    for champ, valeur in {"action": "attendre", **CHAMPS_ATTENTE}.items():
        attente["properties"][champ] = {"type": "integer" if champ == "difficulte" else "string", "enum": [valeur]}
    attente["properties"]["cible"]["description"] = attente["description"]
    return autres, attente


def precision_publique(parametres):
    if parametres.get("operation") == "patienter":
        return ATTENTES["occasion"]["public"]
    if parametres.get("action") == "attendre":
        return ATTENTES["duree" if parametres["cible"] else "bloc"]["public"]
    return ""


def sens_propose(parametres):
    """Sens du contrat choisi, sans décider de sa fidélité ni de sa faisabilité."""
    op = parametres.get("operation", parametres.get("action"))
    if op == "composer":
        return COMPOSITION["sens"] + " " + COMPOSITION["arret"]
    if op == "patienter":
        return ATTENTES["occasion"]["sens"]
    if op == "attendre":
        return ATTENTES["duree" if parametres.get("cible") else "bloc"]["sens"]
    if op == "voler":
        return RACCOURCIS_VOL.get(parametres.get("methode"), {}).get("sens", "")
    return ""
