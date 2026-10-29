"""Positions de contact, communes au monde cru et aux états projetés du plan."""


def case_contact(monde, objet, salle, lieu, case, vus=()):
    """Suivre uniquement les liens crus ; jamais la position réelle d'un mobile.

    Les callbacks lisent soit les croyances, soit leurs effets projetés. Une
    position du contenu n'est plus valable si son contenant a bougé : la chaîne
    de possession prime donc sur l'ancienne case du contenu.
    """
    if objet in vus:
        return None
    dans = lieu(objet)
    if dans in monde.objets or dans == 'joueur':
        return case_contact(monde, dans, salle, lieu, case, (*vus, objet))
    o = monde.objets.get(objet, {})
    # Une porte a une position dans chacune des salles qu'elle relie.
    if dans != salle and o.get('type') != 'porte':
        return None
    position = case(objet)
    if position is not None:
        return tuple(position)
    from .monde import mobile_par_nature
    if o and not mobile_par_nature(o):
        from .spatial import position_cible
        position = position_cible(monde, objet, salle)
        return tuple(position) if position is not None else None
    return None
