"""Trajets de recherche par salle ; aucun départ réel, aucune orientation.

La moyenne des distances depuis les seuils intérieurs remplace la position.
Les tables métriques sont partagées par géométrie et obstacles crus ; elles
incluent les suppléments des franchissements et l'équipement utile.
"""
import heapq
from itertools import count

from .obstacles import Route, distances, transitions, descriptions_crues, cout_route
from .spatial import _case_interieure, _pas_possibles, _case_libre, _bloquantes, VECTEURS, QUART, a_verifier
from .temps import duree_pas
from .geometrie import cases
from .eau import noyee_crue
from . import pnj, route_admissible


def tables(v, e, salle):
    cle = (salle, e.allure, e.portes if v.metrique(e.allure) else frozenset())
    if cle not in v._locaux:
        v._locaux[cle] = _tables(v, e, salle)
    return v._locaux[cle]


def _tables(v, e, salle):
    cru = v._cru_spatial
    entrees = sorted({_case_interieure(cru, salle, s)
                      for s in v.salles[salle]["sorties"].values()})
    if not entrees:
        entrees = [min(cases(v.salles[salle]))]
    passages = (transitions(cru, v.id, descriptions_crues(v.monde, v.id), e.portes, e.allure)
                if v.metrique(e.allure) else None)
    return [(c, distances(cru, v.id, salle, c, e.portes, e.allure, passages)) for c in entrees]


def moyenne(v, e, salle, cibles, sortie=False):
    """Lecture locale à une Vue figée : corps, équipement utile et obstacles crus
    y sont constants. L'état ne fournit que salle, allure et possessions métriques ;
    faits du plan, positions réelles, horloge et portes prévues ne sont pas lus.
    Chaque reprise contrôlée recalcule aussi les tables locales.
    """
    cle = (salle, frozenset(cibles), sortie, e.allure,
           e.portes if v.metrique(e.allure) else frozenset())
    if cle not in v._moyennes:
        v._moyennes[cle] = _moyenne(v, e, salle, cibles, sortie)
    elif a_verifier():
        assert v._moyennes[cle] == _moyenne(v, e, salle, cibles, sortie, pur=True), "Trajet estimé périmé"
    return v._moyennes[cle]


def _moyenne(v, e, salle, cibles, sortie=False, pur=False):
    """Dixièmes : distance moyenne aux contacts, plus un angle moyen de 90°.

    Pour sortir, on exclut le seuil visé des origines ; avec une seule entrée,
    la moyenne sur tout le sol accessible évite une traversée fictivement nulle.
    """
    valeurs = []
    locales = _tables(v, e, salle) if pur else tables(v, e, salle)
    for origine, table in locales:
        if sortie and origine in cibles:
            continue
        proches = [table[c][0] for c in cibles if c in table]
        if proches:
            valeurs.append(min(proches))
    if not valeurs and sortie:
        table = next((t for c, t in locales if c in cibles), {})
        if pur:
            libres = {c for c in cases(v.salles[salle]) if _case_libre(v._cru_spatial, salle, c)}
        else:
            # Même état cru pendant ce calcul : relever les obstacles une fois,
            # plutôt que parcourir tous les objets pour chaque case du sol.
            libres = cases(v.salles[salle]) - set(_bloquantes(v._cru_spatial, salle))
        if not libres <= table.keys():
            return None  # salle coupée : aucune origine réelle ne peut être supposée
        valeurs = [d for d, _ in table.values()]
    if not valeurs and not sortie and cibles:
        # Un contact dans une composante sans entrée reste une action locale
        # possible. La marche réelle vérifiera la composante de l'acteur.
        cru = v._cru_spatial
        passages = (transitions(cru, v.id, descriptions_crues(v.monde, v.id), e.portes, e.allure)
                    if v.metrique(e.allure) else None)
        table = distances(cru, v.id, salle, min(cibles), e.portes, e.allure, passages)
        valeurs = [d for d, _ in table.values()]
    return sum(valeurs) / len(valeurs) + 2 * QUART if valeurs else None


def parcours(v, e, ouvertes, delai=0, certain=False):
    cru = v._cru_spatial
    cles = [k for k in e.portes if v.objets[k].get("ouvre")]
    ordre = count()
    routes = {e.salle: Route(fin=(e.salle, None))}
    prix = {e.salle: 0}
    file = [(0, next(ordre), e.salle)]
    pas_de = _pas_possibles(cru, True)
    while file:
        cout, _, salle = heapq.heappop(file)
        if cout != prix[salle]:
            continue
        avant = routes[salle]
        for direction, sortie in v.salles[salle]["sorties"].items():
            vers, porte = sortie["vers"], sortie.get("porte")
            # La règle commune juge les durées du préfixe ; son but sera
            # contrôlé par Vue.route (un passage ne vaut pas un séjour).
            if vers not in v.salles or noyee_crue(v.monde, v.id, vers):
                continue
            if (porte and v.verrouille(e, porte) and porte not in ouvertes
                    and not any(porte in v.objets[k].get("ouvre", ()) for k in cles)):
                continue
            seuil = _case_interieure(cru, salle, sortie)
            sens = VECTEURS.get(direction)
            pas = pas_de(salle, seuil, sens) if sens else None
            if pas is None or pas[0][0] != vers:
                continue
            marche = moyenne(v, e, salle, {seuil}, sortie=True)
            if marche is None:
                continue
            gestes = 0
            if porte and porte not in avant.portes:
                DUREES = pnj.DUREES
                gestes = (0 if v.ouvert(e, porte) else DUREES["ouvrir"]
                          + (DUREES["deverrouiller"] if v.verrouille(e, porte) and porte not in ouvertes else 0))
            route = Route([*avant, sortie], fin=(vers, None),
                          sejours=(*avant.sejours, (salle, marche + gestes), (vers, duree_pas(e.allure, sens))),
                          portes=avant.portes | ({porte} if porte else set()), depart=e.salle)
            raison = route_admissible.refus(v, e, route, vers, passage=True, delai=delai, certain=certain,
                                              depart_compris=bool(delai))
            if raison:
                if not delai:
                    v.refus_routes[vers] = raison
                continue
            total = cout_route(route)
            if total < prix.get(vers, float("inf")):
                prix[vers], routes[vers] = total, route
                heapq.heappush(file, (total, next(ordre), vers))
    return routes


def approche(v, e, etape, cibles=None):
    from .pnj import _a_toucher, _contact_vocal_cru
    from .deliberation import SOCIALES
    from .proximite_vocale import vocale
    if vocale(etape):
        duree = moyenne(v, e, e.salle, v.cases_vocales(e, etape['cible']))
        return Route(fin=(e.salle, None), sejours=((e.salle, duree),)) if duree is not None else None
    touches = _a_toucher(v.monde, v.id, etape, e.portes)
    if cibles is None:
        touches = [x for x in touches if v.case_objet(e, x) is not None
                   or not (_contact_vocal_cru(v.monde, v.id, etape, x, e.salle)
                           or etape['operation'] in SOCIALES and x == etape['cible']
                           and e.fait('cherche', x) and v.salle(e, x) == e.salle)]
    cibles = tuple(v.case_objet(e, x) for x in touches) if cibles is None else tuple(cibles)
    centre = etape["operation"] == "inspecter" and not etape.get("attendre_remise")
    # Une case inconnue prépare la même observation au centre que l'exécution ;
    # ce n'est jamais une approche gratuite ni une preuve de présence.
    observation = bool(cibles) and None in cibles
    if observation and any(v.salle(e, x) != e.salle for x in touches):
        return None
    centre = centre or observation
    if centre:
        sol = cases(v.salles[e.salle])
        x, y = sum(c[0] for c in sol) / len(sol), sum(c[1] for c in sol) / len(sol)
        cibles = (min(sol, key=lambda c: ((c[0]-x)**2 + (c[1]-y)**2, c)),)
    if not cibles:
        return Route(fin=(e.salle, None))
    cle = (e.salle, cibles, centre, observation, e.allure, e.portes if v.metrique(e.allure) else frozenset())
    if cle not in v._approches:
        contacts = v.contacts(e.salle, cibles, centre)
        duree = moyenne(v, e, e.salle, contacts)
        if duree is not None and observation:
            duree += pnj.TOUR
        v._approches[cle] = (Route(fin=(e.salle, None), sejours=((e.salle, duree),))
                            if duree is not None else None)
    return v._approches[cle]
