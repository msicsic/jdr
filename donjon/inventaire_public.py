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


def ressources_publiques(monde, decrire_physique=False):
    """Choix matériels connus, sans capacités, règles ni inventaire d'autrui."""
    from .francais import designer
    from .noms import public
    from .gestes_publics import ressource_connue
    from .moyens_materiels import APTITUDES

    # Les aptitudes ne sont calculées que vers des cibles actuellement vues
    # ou directement portées. Aucun résultat sur une entité cachée ne sort.
    cibles = [o for id, o in monde.objets.items() if ressource_connue(monde, id, exiger_portee=False)]

    biens = []
    for id, o in monde.objets.items():
        if not ressource_connue(monde, id):
            continue
        vu = monde.visible(id)
        bien = {"id": id, "nom": designer(o), "type": o["type"]}
        if not decrire_physique:
            bien["aptitudes"] = {
                nom: [c["id"] for c in cibles if c["id"] != id and regle(c, o)]
                for nom, regle in APTITUDES.items()}
        if decrire_physique:
            from .matiere import decrire
            physique = o.get("physique")
            bien["description_physique"] = (physique["forme"] + " : " + decrire(o) if physique else
                                            "Description physique manquante : forme et dimensions à établir séparément.")
        if vu and o.get("foyer"):
            bien["foyer"] = True
        biens.append(bien)
    return public(monde, biens)
