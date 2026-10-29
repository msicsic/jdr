"""Projection publique de la besace et des destinataires, commune aux interfaces."""


def inventaire_public(monde):
    """Les affaires de la besace, sans le contenu caché des contenants portés."""
    from .francais import designer
    from .noms import public, PERSONNES
    biens = []
    for id, o in monde.objets.items():
        if o["lieu"] != "joueur" or o["type"] in PERSONNES:
            continue
        bien = {"id": id, "nom": designer(o), "type": o["type"]}
        # La quantité des affaires portées figure déjà dans le nom de la fiche,
        # même dans le noir ; elle ne dépend pas d'un nouvel examen visuel.
        if "physique" in o:
            bien["pieces"] = o["physique"]["pieces"]
        if monde.visible(id):
            if "allume" in o:
                bien["allume"] = bool(o["allume"])
        biens.append(bien)
    return public(monde, biens)


def destinataires_publics(monde):
    """Présence et portée publiques ; aucune acceptation de don présumée."""
    from .francais import designer
    from .noms import public
    from .spatial import proche
    return public(monde, [{"id": id, "nom": designer(o)} for id, o in monde.objets.items()
                         if o["type"] == "personnage" and monde.visible(id)
                         and (not monde.data.get("mode_cases") or proche(monde, id))])


