"""Sens des passages typés ; géométrie, jets et accord restent aux mécaniques."""
import copy
import re

from .refus import RefusDeForme


COTES = ("dessous", "dessus")
DIFFICULTES_APPUI_MOBILE = tuple(range(16, 23))
MANIERES = {"ramper": "Ramper sous ", "enjamber": "Enjamber ", "escalader": "Escalader "}
RACCOURCIS = {
    "ramper sous ": "dessous", "je rampe sous ": "dessous",
    "passer sous ": "dessous", "je passe sous ": "dessous",
    "passer par-dessus ": "dessus", "je passe par-dessus ": "dessus",
    "enjamber ": "dessus", "escalader ": "dessus",
}
PASSAGES = {
    "passer_obstacle": {
        "sens": "Passer dessous ou dessus un obstacle physique local ; cible = obstacle, methode = côté. "
                "Le moteur choisit ramper, enjamber ou escalader selon la forme, le corps et l'équipement.",
        "public": "Rejoindre le sol libre en face, dans la même salle. L'obstacle reste en place.",
        "champs": {"destination": [""], "outil": [""], "methode": list(COTES), "difficulte": [0]},
        "requis": ["cible"],
    },
    "franchir": {
        "sens": "Parcourir un assemblage déjà installé : cible = assemblage, sans outil. "
                "Le moteur détermine la montée ou la descente depuis la position actuelle. "
                "Ce n'est pas un passage sous un obstacle.",
        "public": "Emprunter l'assemblage installé vers son autre palier ; le moteur fixe le jet.",
        "champs": {"destination": [""], "outil": [""], "methode": ["simple"], "difficulte": [0]},
        "requis": ["cible"],
    },
    "franchir_obstacle": {
        "sens": "Franchir avec un appui mobile : cible = obstacle, destination = palier relié, outil = appui, "
                "methode appui_mobile, estimation de difficulté 16 à 22. La prise de l'appui est une étape distincte.",
        "public": "Tenter le franchissement avec l'appui mobile ; aucun passage permanent n'est créé.",
        "champs": {"methode": ["appui_mobile"], "difficulte": list(DIFFICULTES_APPUI_MOBILE)},
        "requis": ["cible", "destination", "outil"],
    },
    "pousser": {
        "sens": "Pousser une personne au contact, à mains nues : cible = personne, outil = direction ou vide "
                "pour l'écarter. Le moteur fixe le jet de FOR opposé. Demander de s'écarter est une parole passage.",
        "public": "Tenter de déplacer la personne ; Corvus reste sur place. La bousculade a un coût social même en cas d'échec.",
        "champs": {"methode": ["simple"], "difficulte": [0]},
        "requis": ["cible"],
    },
}
DEMANDE = {
    "sens": "Demander à l'interlocuteur de laisser passer. sujet est vide ou désigne un destinataire de cette parole ; "
            "il ne peut pas désigner un tiers. attribut vide ; valeur = prix offert en pièces, vide sans offre. "
            "Le moteur décide de l'accord et du déplacement ; les mots seuls ne demandent aucun passage.",
    "public": "Le moteur décide si l'interlocuteur s'écarte ; Corvus reste sur place.",
}


def champs(operation):
    c = PASSAGES[operation]["champs"]
    if operation == "pousser":
        from .spatial import VECTEURS
        return {**c, "outil": ["", *VECTEURS]}
    return c


def sens_propose(parametres):
    op = parametres.get("operation", parametres.get("action"))
    contrat = PASSAGES.get(op)
    return contrat["sens"] + " " + contrat["public"] if contrat else ""


def verifier(p):
    op = p.get("operation", p.get("action"))
    if op not in PASSAGES:
        return
    contrat = PASSAGES[op]
    for champ, acceptes in champs(op).items():
        if champ in p and p[champ] not in acceptes:
            raise RefusDeForme("Les paramètres ne correspondent pas à ce passage.",
                              f"{op}.{champ} : reçu {p[champ]!r} ; accepté : {acceptes!r}.")
    for champ in contrat["requis"]:
        if not p.get(champ):
            raise RefusDeForme("Ce passage doit désigner ses appuis et sa cible.",
                              f"{op}.{champ} : reçu {p.get(champ)!r} ; accepté : référence non vide. {contrat['sens']}")


def schemas(schema, discriminant, operations):
    resultat = []
    for op in operations:
        s = copy.deepcopy(schema)
        s["description"] = PASSAGES[op]["sens"] + " " + PASSAGES[op]["public"]
        s["properties"][discriminant] = {"type": "string", "enum": [op]}
        for champ, acceptes in champs(op).items():
            if champ in s["properties"]:
                s["properties"][champ] = {"type": "integer" if champ == "difficulte" else "string", "enum": acceptes}
        for champ in PASSAGES[op]["requis"]:
            s["properties"][champ] = {"type": "string", "minLength": 1, "description": PASSAGES[op]["sens"]}
        resultat.append(s)
    return resultat


def raccourci(operation, cible, *, methode="simple", outil="", destination=""):
    from .operations import etape, sequence
    from .moteur import proposition
    if operation != "passer_obstacle" and destination:
        raise RefusDeForme("Ce passage ne reçoit pas de destination arbitraire.",
                          f"{operation}.destination : reçu {destination!r} ; accepté : vide.")
    return (sequence(etape(operation, cible, destination, outil=outil, methode=methode)) if operation == "passer_obstacle"
            else proposition(operation, cible, outil, methode))


def verifier_demande(c, chemin="passage"):
    for champ in ("sujet", "attribut", "valeur"):
        if not isinstance(c.get(champ, ""), str):
            raise RefusDeForme("Les paramètres de la demande de passage sont mal formés.",
                              f"{chemin}.{champ} : reçu {c.get(champ)!r} ; accepté : chaîne.")
    if c.get("attribut"):
        raise RefusDeForme("La demande de passage ne porte pas d'attribut.",
                          f"{chemin}.attribut : reçu {c['attribut']!r} ; accepté : vide.")
    if not re.fullmatch(r"\s*[0-9]*\s*", c.get("valeur", "")):
        raise RefusDeForme("Le prix proposé doit être exprimé en pièces.",
                          f"{chemin}.valeur : reçu {c['valeur']!r} ; accepté : vide ou entier positif en chiffres.")


def schema_demande(schema):
    s = copy.deepcopy(schema)
    s["description"] = DEMANDE["sens"]
    s["properties"]["attribut"] = {"type": "string", "enum": [""]}
    s["properties"]["valeur"] = {"type": "string", "pattern": r"^\s*[0-9]*\s*$"}
    s["properties"]["sujet"]["description"] = DEMANDE["sens"]
    return s


def typer_demande(monde, c, auditeur):
    from .paroles import resoudre, offre
    sujet = c.get("sujet")
    return ({"type": "passage", "prix": offre(c)} if not sujet or resoudre(monde, sujet) == auditeur
            else None)


def verifier_destinataire(monde, contenu, destinataires):
    from .paroles import resoudre
    for i, c in enumerate(contenu):
        if isinstance(c, dict) and c.get("type") == "passage" and c.get("sujet"):
            if resoudre(monde, c["sujet"]) not in destinataires:
                raise RefusDeForme("Une demande de passage s'adresse à celui qui doit s'écarter.",
                                  f"contenu[{i}].sujet : reçu {c['sujet']!r} ; accepté : vide ou "
                                  f"un destinataire parmi {destinataires!r}.")


def precision_publique(parametres):
    op = parametres.get("operation", parametres.get("action"))
    return PASSAGES[op]["public"] if op in PASSAGES else ""
