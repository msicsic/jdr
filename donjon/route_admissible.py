"""Admissibilité crue commune à la recherche et au départ réel.

Une route porte les séjours estimés, portes comprises. Une salle intermédiaire
ne reçoit jamais l'horizon d'un but où l'on reste. Avant une porte incertaine,
le repli doit encore être possible si elle résiste : aucun temps moyen de
crochetage ne peut garantir la sortie d'un piège.
"""
from . import eau
from .obstacles import Route
from .temps import MINUTE


def attendue(v, salle, delai):
    crue, droite, vitesse = v.eau_route[salle]
    return max(crue, droite + vitesse * delai)


def refus(v, e, route, arrivee, passage=False, delai=0, certain=False, depart_compris=False):
    """None, ou une cause en mots ; aucune mutation du monde ni vérité cachée."""
    if not v.eau_route:
        return None
    sejours = route.sejours if isinstance(route, Route) else tuple(
        (x['vers'], MINUTE) for x in route)
    temps = delai
    traverses = []
    for salle, duree in sejours:
        temps += duree / MINUTE
        cm = attendue(v, salle, temps)
        # On peut quitter sa salle déjà perdue ; on ne s'enfonce pas ailleurs.
        if (depart_compris or salle != e.salle) and cm >= eau.NOYEE_CM:
            return f"{v.salles[salle]['nom']} : l'eau est trop haute pendant le passage"
        traverses.append(salle)
    # Une porte inconnue peut résister. Vérifier le retour immédiat, sans
    # supposer qu'une réussite aléatoire, une aide ou une attente le sauvera.
    deja = set()
    for sortie in route:
        porte = sortie.get('porte')
        if porte and v.verrouille(e, porte) and porte not in v.ouvertes(e) and not any(
                porte in v.objets[k].get('ouvre', ()) for k in e.portes):
            return f"{v.objets[porte]['nom']} : porte crue verrouillée sans clé"
        if porte and porte not in deja and not v.ouvert(e, porte):
            certaine = (v.cru(porte, 'verrouillee') is False
                        or any(porte in v.objets[k].get('ouvre', ()) for k in e.portes)
                        or porte in v.ouvertes(e))
            repli = delai + 2 * sum(d for _, d in sejours) / MINUTE
            if not certaine and (certain or any(attendue(v, s, repli) >= eau.NOYEE_CM
                                               for s in traverses)):
                return f"{v.objets[porte]['nom']} : ouverture incertaine et retour coupé par l'eau"
            deja.add(porte)
    if not passage:
        crue, _, _ = v.eau_route[arrivee]
        prevue = attendue(v, arrivee, temps + eau.HORIZON)
        source = attendue(v, e.salle, temps + eau.HORIZON)
        source_crue = v.eau_route[e.salle][0]
        # Quitter un péril pour moins d'eau reste un mouvement de secours.
        # Choisir contrôle séparément le séjour des recours ordinaires ;
        # le certificat de transit exige toujours une destination hors péril.
        amelioration = eau.peril_cru(source_crue, source) and prevue < source
        if eau.peril_cru(crue, prevue) and not amelioration:
            return f"{v.salles[arrivee]['nom']} : séjour en péril d'eau"
    if not passage and v.descente(e.salle, arrivee, v.arrivee(e, arrivee, route)):
        return f"{v.salles[arrivee]['nom']} : séjour ou retour menacé par l'eau"
    return None
