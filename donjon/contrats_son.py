"""Sens commun de la famille expression/son, sans interpréter le français.

L'ouïe, la capacité de parler, les objets sonores et les appels en attente
restent jugés par leurs mécaniques. Un bruit ou un récit ne vaut pas émission.
"""
import copy

from .monde import ErreurMonde
from .refus import RefusDeForme


VOIX = {
    "appel": ("Appeler à l'aide.", "Tu cries à l'aide.", 3),
    "cri": ("Pousser un cri.", "Tu pousses un cri.", 3),
    "sifflement": ("Siffler.", "Tu émets un sifflement.", 2),
}
FORMES_SONORES = {
    "indetermine": "Tu produis un son.",
    "voix_melodique": "Tu fais entendre des notes de ta voix.",
    "voix_breve": "Tu fais entendre un son de voix bref.",
    "souffle": "Tu produis un son de souffle.",
    "corps_rythmique": "Tu frappes un rythme avec ton corps.",
    "corps_bref": "Tu produis un bruit bref avec ton corps.",
}
CHAMPS_EMISSION = {"destination": "", "outil": "", "difficulte": 0}
CHAMPS_SON = {"operation": "son", "cible": "joueur", "destination": ""}
SON_IMPROVISE = {
    "sens": "Une émission improvisée exige un effet son : cible joueur, destination vide, "
            "texte = catégorie acoustique, valeur = intensité de 1 à 3. "
            "Le récit, l'approche expression et le champ bruit ne remplacent pas cet effet. "
            "Une expression simple peut se faire sans jet (stat vide, difficulte 0, echec vide) ; "
            "un geste silencieux peut n'avoir aucun effet son.",
    "minimum": 1, "maximum": 3,
}
AUDITION = "La portée du son détermine qui peut l'entendre ; aucune réponse ni venue n'est garantie."
RACCOURCIS_VOCAUX = {
    "crier a l'aide": "appel", "je crie a l'aide": "appel", "appeler a l'aide": "appel",
    "crier au secours": "appel", "je crie au secours": "appel",
    "crier": "cri", "je crie": "cri", "siffler": "sifflement", "je siffle": "sifflement",
}


def emissions():
    from .appel import METHODES, PHRASES
    return {
        **{m: {"sens": titre + " Sans jet. " + AUDITION, "public": AUDITION, "cibles": ["", "joueur"]}
           for m, (titre, _, _) in VOIX.items()},
        "simple": {"sens": "Faire sonner un objet accessible, à portée, intact et de capacité sonore établie. "
                            "Cible = cet objet, sans jet. " + AUDITION, "public": AUDITION},
        "heler": {"sens": "Héler par son nom un personnage connu (cible = ce personnage), même hors de vue. "
                           "Sans jet. " + AUDITION, "public": AUDITION},
        **{m: {"sens": f"Répondre à un appel en attente : « {PHRASES[sorte]} ». "
                       "Cible = la désignation publique de l'appelant, sans jet. " + AUDITION,
               "public": f"Tu réponds : « {PHRASES[sorte]} ». " + AUDITION}
           for m, sorte in METHODES.items()},
    }


def raccourci(cible, methode):
    from .operations import etape, sequence
    return sequence(etape("emettre_son", cible, methode=methode), justification="")


def verifier_emission(e):
    contrats = emissions()
    if e["methode"] not in contrats:
        raise RefusDeForme("Cette méthode ne décrit pas une émission sonore.",
                          f"emettre_son.methode : reçu {e['methode']!r} ; accepté : {', '.join(contrats)}.")
    for champ, valeur in CHAMPS_EMISSION.items():
        if e[champ] != valeur:
            raise RefusDeForme("Une émission sonore n'impose ni destination, ni outil, ni jet.",
                              f"emettre_son.{champ} : reçu {e[champ]!r} ; accepté : {valeur!r}.")
    cibles = contrats[e["methode"]].get("cibles")
    if cibles is not None and e["cible"] not in cibles:
        raise RefusDeForme("Une émission vocale vient du joueur.",
                          f"emettre_son.cible : reçu {e['cible']!r} ; accepté : {cibles!r}.")


def schemas_emissions(schema_etape):
    schemas = []
    for methode, contrat in emissions().items():
        s = copy.deepcopy(schema_etape)
        s["description"] = contrat["sens"]
        for champ, valeur in {"operation": "emettre_son", "methode": methode, **CHAMPS_EMISSION}.items():
            s["properties"][champ] = {"type": "integer" if champ == "difficulte" else "string", "enum": [valeur]}
        s["properties"]["cible"] = ({"type": "string", "enum": contrat["cibles"]} if "cibles" in contrat else
                                     {"type": "string", "minLength": 1, "description": contrat["sens"]})
        schemas.append(s)
    return schemas


def schema_effet_son(schema_effet):
    autres, son = copy.deepcopy(schema_effet), copy.deepcopy(schema_effet)
    autres["properties"]["operation"]["enum"].remove("son")
    son["description"] = SON_IMPROVISE["sens"]
    for champ, valeur in CHAMPS_SON.items():
        son["properties"][champ] = {"type": "string", "enum": [valeur]}
    son["properties"]["texte"] = {"type": "string", "enum": list(FORMES_SONORES)}
    son["properties"]["valeur"] = {"type": "integer", "minimum": SON_IMPROVISE["minimum"],
                                    "maximum": SON_IMPROVISE["maximum"]}
    return {"anyOf": [autres, son]}


def compiler_son_improvise(monde, e):
    """Charge sonore déjà contrôlée en forme par le compilateur d'effets."""
    for champ, valeur in CHAMPS_SON.items():
        if e[champ] != valeur:
            raise RefusDeForme("Un son improvisé vient du joueur, sans destination imposée.",
                              f"son.{champ} : reçu {e[champ]!r} ; accepté : {valeur!r}.")
    intensite, forme = e["valeur"], e["texte"]
    if not SON_IMPROVISE["minimum"] <= intensite <= SON_IMPROVISE["maximum"]:
        raise RefusDeForme("Un son improvisé a une intensité de 1 à 3.",
                          f"son.valeur : reçu {intensite!r} ; accepté : entier de "
                          f"{SON_IMPROVISE['minimum']} à {SON_IMPROVISE['maximum']}.")
    if forme not in FORMES_SONORES:
        raise RefusDeForme("La forme sonore doit être une catégorie acoustique connue.",
                          f"son.texte : reçu {forme!r} ; accepté : {', '.join(FORMES_SONORES)}.")
    if forme.startswith("voix_") and monde.joueur.get("peut_parler") is False:
        raise ErreurMonde("Ta voix ne peut actuellement pas produire ce son.",
                          "le joueur ne peut pas parler : une forme sans voix (souffle, corps_rythmique, corps_bref).")
    return [("son_improvise", "joueur", {"intensite": intensite, "forme": forme})]


def precision_publique(plan, parametres):
    if parametres.get("operation") == "emettre_son":
        return emissions()[parametres["methode"]]["public"]
    sonore = any(op == "son_improvise" for op, _, _ in plan.effets + plan.echec)
    if parametres.get("action") == "improviser" and (parametres["approche"] == "expression" or sonore):
        lignes = []
        for branche, effets in (("réussite", plan.effets), ("échec", plan.echec)):
            sons = [f"{FORMES_SONORES[v['forme']]} Intensité : {v['intensite']}."
                    for op, _, v in effets if op == "son_improvise"]
            if sons or branche == "réussite" or plan.stat:
                prefixe = "En cas de réussite : " if branche == "réussite" else "En cas d'échec : "
                lignes.append(prefixe + (" ".join(sons) if sons else "aucun son prévu parmi les effets du geste."))
        return " ".join(lignes) + (" " + AUDITION if sonore else "")
    return ""
