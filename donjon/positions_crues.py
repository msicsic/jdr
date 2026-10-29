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


def repere_contact(monde, acteur, etape):
    """Entrées utiles d'un contact interrompu, sans dates ni vérité mobile cachée.

    Une nouvelle localisation, un moyen, la lumière ou une perception positive
    peuvent rouvrir l'observation. Perdre de vue un détail ne suffit pas.
    """
    from .deliberation import _lieu_cru, salle_crue, porte_par
    from .esprits import lire, percus
    from .pnj import _a_toucher, _case_crue
    croyances = lire(monde, acteur)['croyances']
    contacts, supports, salles = [], set(), set()
    for cible in _a_toucher(monde, acteur, etape):
        liens, vus, x = [], set(), cible
        while x not in vus:
            vus.add(x)
            supports.add(x)
            lieu = _lieu_cru(monde, acteur, x)
            c = croyances.get(x, {}).get('lieu') or {}
            liens.append([x, lieu, c.get('salle'), c.get('case')])
            if lieu not in monde.objets and lieu != 'joueur':
                break
            x = lieu
        salle = salle_crue(monde, acteur, cible)
        if salle is not None:
            salles.add(salle)
        case = _case_crue(monde, acteur, cible, salle)
        contacts.append([cible, salle, list(case) if case is not None else None, liens])
    return {'contacts': contacts,
            'lumiere': [[s, (croyances.get(s, {}).get('etat') or {}).get('valeur')]
                        for s in sorted(salles)],
            'portes': [[x, (a.get('etat') or {}).get('valeur'),
                       (a.get('verrouillee') or {}).get('valeur')]
                      for x, a in sorted(croyances.items()) if monde.objets.get(x, {}).get('type') == 'porte'],
            'moyens': [[x, (croyances.get(x, {}).get('etat') or {}).get('valeur')]
                       for x in sorted(monde.objets) if porte_par(monde, x, acteur)],
            'perception': [[x, s, list(c) if c is not None else None]
                           for x, (s, c) in sorted(percus(monde, acteur)[0].items()) if x in supports]}


def contact_interrompu_tient(monde, acteur, cause):
    avant = cause['repere']
    maintenant = repere_contact(monde, acteur, cause['etape'])
    if any(avant[k] != maintenant[k] for k in ('contacts', 'lumiere', 'portes', 'moyens')):
        return False
    return all(p in avant['perception'] for p in maintenant['perception'])
