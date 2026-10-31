"""Passage local sous ou sur un obstacle : même corps, équipement et temps pour tous.

La géométrie est une donnée, jamais une déduction du nom. Un franchissement rejoint
le sol libre d'en face, dans la même salle ; il ne rend pas la case de l'obstacle habitable.
"""
from . import memoire
import copy
import math
import json
import heapq
from collections import OrderedDict

from .monde import ErreurMonde
from .refus import ProprieteInconnue
from .francais import designer
from .temps import PAS_JOUEUR, MINUTE, duree_pas
from .spatial import QUART, quarts, VECTEURS

METHODES = ("dessous", "dessus")
# Les manipulations ordinaires du joueur sont encore des Plan à une minute ;
# les PNJ emploient DUREES. La mesure reçoit le tarif de son exécutant.
DUREES_PORTES_JOUEUR = {"ouvrir": MINUTE, "deverrouiller": MINUTE}
REGLES = """
Ces règles utilisent le dossier passages_obstacles lorsqu’il est présent ; son absence ne fournit aucune ressource ni possibilité.
Passage local : composer avec operation passer_obstacle, cible obstacle, methode dessous ou
dessus, destination et outil vides, difficulte 0. Le moteur choisit ramper, enjamber ou
escalader selon passage (qualification physique), gabarit et équipement ; il fixe durée et jet.
Sans géométrie établie, la raison du refus indique la qualification manquante. Le dossier
passages_obstacles donne possibilités et refus réels. Une question de faisabilité prépare la
même fiche sans agir. Ce passage rejoint le sol libre d'en face dans la même salle ; une
échelle installée et le saut avec appui mobile restent des accès distincts entre lieux.
"""


def gabarit(m, acteur):
    """Conventions humaines de jeu, communes, sans migration des sauvegardes.

    La stature déclarée prévaut ; à défaut 170 cm, 70 kg. La corpulence et la
    masse modulent la carrure ; un auteur peut préciser carrure_cm.
    """
    o = m.joueur if acteur == "joueur" else m.objets[acteur]
    taille, masse = o.get("taille_cm", 170), o.get("masse_kg", 70)
    for k, v, bas, haut in (("taille_cm", taille, 40, 300), ("masse_kg", masse, 5, 500)):
        if type(v) not in (int, float) or not math.isfinite(v) or not bas <= v <= haut:
            raise ErreurMonde("Le gabarit de qui passe doit être établi.",
                              f"{acteur}.{k}={v!r} : accepté {bas}..{haut}.")
    facteur = {"mince": .9, "moyenne": 1, "robuste": 1.1}.get(o.get("corpulence"), 1)
    largeur = o.get("carrure_cm", math.ceil(taille * .27 * (masse / 70) ** .25 * facteur))
    if type(largeur) not in (int, float) or not math.isfinite(largeur) or not 10 <= largeur <= 150:
        raise ErreurMonde("La carrure de qui passe doit être établie.",
                          f"{acteur}.carrure_cm={largeur!r} : accepté 10..150.")
    return taille, masse, largeur, math.ceil(largeur * .65)


def portes(m, acteur):
    from .spatial import porte_par
    return frozenset(i for i in m.objets if porte_par(m, i, acteur))


def conditions(m, cible, methode, acteur="joueur", description=None, equipement=None):
    """Règle pure ; ``description`` est la forme crue, ``equipement`` celui prévu par un plan."""
    from .matiere import valider_passage
    o = m.objets.get(cible, {})
    if not o.get("bloque_passage") or o.get("incorpore"):
        raise ErreurMonde("Ce passage exige un obstacle physique.",
                          f"cible={cible} : accepté un objet bloque_passage=true, incorpore=false.")
    if methode not in METHODES:
        raise ErreurMonde("Précise de quel côté de l'obstacle tu passes.",
                          f"methode={methode!r} : accepté dessous, dessus.")
    p = o.get("passage") if description is None else description
    if p is None:
        raise ProprieteInconnue("Le dégagement sous l'obstacle et sa hauteur ne sont pas encore décrits.",
                          f"{cible}.passage=null : accepté qualification ancrage={cible}, passage avec "
                          "degagement_cm, hauteur_cm, largeur_cm, profondeur_cm, charge_kg, appuis.")
    p = valider_passage(o, p)
    taille, poids, carrure, epaisseur = gabarit(m, acteur)
    if p["largeur_cm"] < carrure:
        raise ErreurMonde("Le passage est trop étroit pour ta carrure.",
                          f"{cible}.passage.largeur_cm={p['largeur_cm']} : accepté >= {carrure:g} ({acteur}.carrure_cm).")
    if methode == "dessous":
        if p["degagement_cm"] < epaisseur:
            raise ErreurMonde("Le dégagement est trop bas pour passer en rampant.",
                              f"{cible}.passage.degagement_cm={p['degagement_cm']} : accepté >= {epaisseur:g} ({acteur}).")
        maniere, facteur, stat, dd = "ramper", 4, "", 0
        masse_max, longueur_max = poids * .25, taille
        nature = "feutre"
    else:
        if p["hauteur_cm"] > taille * .8:
            raise ErreurMonde("L'obstacle est trop haut pour ce franchissement sans matériel.",
                              f"{cible}.passage.hauteur_cm={p['hauteur_cm']} : accepté <= {taille * .8:g} ({acteur}.taille_cm * 0.8).")
        if p["hauteur_cm"] <= taille * .35:
            maniere, facteur, stat, dd = "enjamber", 2, "", 0
            masse_max, longueur_max = poids * .5, taille * 1.5
            nature = "pas"
        else:
            if not p["appuis"]:
                raise ErreurMonde("L'obstacle n'offre pas les prises nécessaires pour l'escalader.",
                                  f"{cible}.passage.appuis=false : accepté true, ou methode=dessous si possible.")
            maniere, facteur, stat, dd = "escalader", 6, "FOR", 10
            masse_max, longueur_max = poids * .15, taille / 2
            nature = "geste"
        if p["charge_kg"] < poids:
            raise ErreurMonde("L'obstacle ne supporte pas ton poids.",
                              f"{cible}.passage.charge_kg={p['charge_kg']} : accepté >= {poids:g} ({acteur}.masse_kg).")
    equipement = portes(m, acteur) if equipement is None else equipement
    charge = sum(m.objets[i].get("masse", 0) for i in equipement)
    if charge > masse_max:
        raise ErreurMonde("Tu portes trop lourd pour passer de cette manière.",
                          f"{acteur}.charge_kg={charge:g} : accepté <= {masse_max:g} pour {maniere}.")
    if methode == "dessus" and poids + charge > p["charge_kg"]:
        raise ErreurMonde("L'obstacle ne supporte pas ton poids avec ton équipement.",
                          f"{cible}.passage.charge_kg={p['charge_kg']} : accepté >= {poids + charge:g} ({acteur}, équipement compris).")
    for i in sorted(equipement):
        x = m.objets[i]
        dimensions = x.get("physique", {}).get("dimensions", {})
        longueur = max([x.get("longueur_cm", 0), *dimensions.values()], default=0)
        # Sans dimension déclarée, l'objet portable tient dans sa case (1 m),
        # convention de jeu et non établissement d'une longueur physique.
        longueur = longueur or 100
        if longueur > longueur_max:
            raise ErreurMonde(designer(x, debut=True) + " est trop encombrant pour passer ainsi.",
                              f"{i}.longueur_cm={longueur:g} : accepté <= {longueur_max:g} pour {maniere} ({acteur}).")
    return {"cible": cible, "methode": methode, "maniere": maniere, "facteur": facteur,
            "stat": stat, "dd": dd, "nature": nature, "charge": charge}


def descriptions_crues(m, acteur):
    from .esprits import lire
    c = memoire.faits_connus(m, acteur)
    return {i: copy.deepcopy(d["passage"]["valeur"]) for i, d in c.items()
            if i in m.objets and "passage" in d}


_GEOMETRIES_CRUES = OrderedDict()
GEOMETRIES_MAX = 128


def cle_carte(m, salle=None):
    """Identité immuable du contenu de la carte, sans sérialiser à chaque lecture.

    Les salles restent des données JSON librement éditables (y compris en place).
    Une copie témoin détecte ces éditions par égalité ; l'ordre des salles et
    sorties, qui départage les parcours, fait aussi partie de l'identité.
    Le texte n'est construit qu'au changement, puis employé directement comme
    composante de clé, jamais réencodé dans le JSON de chaque trajet.
    """
    salles = m.data["salles"]
    contenu = salles if salle is None else salles[salle]
    ordre = (tuple((s, tuple(d["sorties"])) for s, d in salles.items())
             if salle is None else tuple(contenu["sorties"]))
    cache = getattr(m, "_cles_cartes", None)
    if cache is None:
        cache = m._cles_cartes = {}
    ancien = cache.get(salle)
    if ancien is None or ancien[0] != contenu or ancien[1] != ordre:
        texte = json.dumps([contenu, ordre], sort_keys=True, ensure_ascii=False, check_circular=False)
        ancien = cache[salle] = (copy.deepcopy(contenu), ordre, texte)
    return ancien[2]


def metrique_necessaire(m, acteur, allure=PAS_JOUEUR):
    """La marche ordinaire suffit-elle, quels que soient les objets qu'il prévoit porter ?

    Une salle connexe et un détour au plus aussi rapide que chaque franchissement
    permettent de retirer les arêtes de franchissement sans perdre de trajet.
    La distance ordinaire dépend toujours de la case de départ. Le test suppose les mains vides :
    l'équipement ne peut que retirer des franchissements, jamais en accélérer un.
    """
    from .esprits import lire
    formes = descriptions_crues(m, acteur)
    if not formes or not m.data.get("mode_cases"):
        return False
    croyances = memoire.faits_connus(m, acteur)
    # Toutes les lectures du test : géométrie, obstacles crus (sans leurs dates),
    # gabarit. Ni lumière, ni humeur, ni positions des autres personnages.
    obstacles = [(i, o,
                  {k: croyances.get(i, {}).get("lieu", {}).get(k) for k in ("valeur", "salle", "case")},
                  formes.get(i)) for i, o in m.objets.items() if o.get("bloque_passage")]
    cle = (cle_carte(m), json.dumps([obstacles, gabarit(m, acteur), allure], sort_keys=True, ensure_ascii=False))
    from .spatial import a_verifier
    if cle in _GEOMETRIES_CRUES:
        connu = _GEOMETRIES_CRUES[cle]
        _GEOMETRIES_CRUES.move_to_end(cle)
        if a_verifier():
            assert connu == _metrique_necessaire(m, acteur, formes, allure), "Géométrie de trajet crue périmée"
        return connu
    resultat = _metrique_necessaire(m, acteur, formes, allure)
    _GEOMETRIES_CRUES[cle] = resultat
    if len(_GEOMETRIES_CRUES) > GEOMETRIES_MAX:
        _GEOMETRIES_CRUES.popitem(last=False)
    return resultat


def _metrique_necessaire(m, acteur, formes, allure):
    from .spatial import _pas_possibles, _bloquantes, trajet, VECTEURS
    from .geometrie import cases
    cru = monde_cru(m, acteur)
    pas_de = _pas_possibles(cru, True)
    franchissements = transitions(cru, acteur, formes, equipement=frozenset(), allure=allure)
    sens = sorted(set(VECTEURS.values()))
    for salle, piece in cru.data["salles"].items():
        sols = set(cases(piece)) - set(_bloquantes(cru, salle))
        if not sols:
            continue
        # Connexité par le vrai pas, angles compris, sans sortir de la salle.
        premier = min(sols)
        atteintes, file = {premier}, [premier]
        while file:
            ici = file.pop()
            for v in sens:
                pas = pas_de(salle, ici, v)
                if pas is None or pas[0][0] != salle or pas[0][1] in atteintes:
                    continue
                atteintes.add(pas[0][1])
                file.append(pas[0][1])
        if atteintes != sols:
            return True
        # Une arête nouvelle n'améliore pas le graphe si la marche peut la
        # remplacer en au plus son temps. On n'examine qu'un sens par paire.
        for depart in sorted(sols):
            for (s, fin), regle, _, duree in franchissements(salle, depart):
                if fin < depart:
                    continue
                chemin = trajet(cru, salle, depart, lambda s, c: s == salle and c == fin,
                                libre=lambda s, c: s == salle, allure=allure)
                from .temps import duree_pas
                temps = sum(duree_pas(allure, v) for _, _, _, v in chemin or [])
                if chemin is None or temps > duree:
                    return True
    return False


class Parcours(dict):
    """Le contrat des salles, plus leurs routes et distances métriques crues."""
    def __init__(self, depart):
        super().__init__({depart: None})
        self.routes = {depart: []}


class Route(list):
    """Sorties et mesure du même chemin ; même une approche sans sortie a un temps."""
    def __init__(self, sorties=(), *, fin=None, chemin=(), sejours=(), portes=(), depart=None):
        super().__init__(sorties)
        self.fin = fin
        self.chemin = tuple(chemin)
        self.sejours = tuple(sejours)
        self.portes = frozenset(portes)
        self.depart = depart if depart is not None else (fin[0] if fin else None)
        self._sejours = {}
        self._couts = {}

    @classmethod
    def depuis_pas(cls, m, depart, chemin, allure=PAS_JOUEUR, durees_portes=None):
        """Le chemin spatial du joueur porte la même mesure que les routes crues."""
        sejours, franchies = [], set()
        salle = depart
        for vers, _, porte, sens in chemin:
            if isinstance(porte, dict):
                duree = porte["dixiemes"]
            else:
                duree = duree_pas(allure, sens)
                if porte and porte not in franchies:
                    sejours.append((salle, duree_porte(m, porte, durees=durees_portes)))
                    franchies.add(porte)
            sejours.append((vers, duree))
            salle = vers
        return cls(chemin, fin=chemin[-1][:2] if chemin else None, chemin=chemin,
                   sejours=sejours, portes=franchies, depart=depart)


_DISTANCES = OrderedDict()
DISTANCES_MAX = 2048


def duree_porte(m, porte, deverrouillees=(), durees=None):
    """Temps des gestes en chemin, en dixièmes, sur le monde fourni (réel ou cru)."""
    from .pnj import DUREES
    durees = DUREES if durees is None else durees
    o = m.objets[porte]
    return (0 if o.get("ouverte") else durees["ouvrir"]
            + (durees["deverrouiller"] if o.get("verrouillee") and porte not in deverrouillees else 0))


def distances(cru, acteur, salle, depart, equipement, allure, passages):
    """Une table locale par origine ; seuils et cibles partagent la même métrique.

    La clé ne lit que la géométrie et les obstacles de cette salle, la forme du
    corps et l'équipement quand les franchissements peuvent améliorer la marche.
    Ni l'horloge, ni les positions réelles des autres ne sont consultées.
    """
    from .spatial import _pas_possibles, a_verifier, position_cible, VECTEURS
    obstacles = [(i, position_cible(cru, i, salle), o.get("passage")) for i, o in cru.objets.items()
                 if o.get("bloque_passage") and not o.get("incorpore") and o.get("lieu") == salle]
    equip = [(i, cru.objets[i].get("masse", 0), cru.objets[i].get("longueur_cm"),
              cru.objets[i].get("physique", {}).get("dimensions")) for i in sorted(equipement)] if passages else []
    cle = (cle_carte(cru, salle), json.dumps([obstacles, depart, allure,
                      gabarit(cru, acteur) if passages else None, equip], sort_keys=True))

    def calculer():
        pas_de = _pas_possibles(cru, True)
        origine = tuple(depart)
        table, couts, ordre = {}, {origine: 0}, 0
        file = [(0, 0, origine, ())]
        while file:
            cout, _, case, chemin = heapq.heappop(file)
            if case in table:
                continue
            table[case] = (cout, chemin)
            suites = []
            for sens in sorted(set(VECTEURS.values())):
                pas = pas_de(salle, case, sens)
                if pas is not None and pas[0][0] == salle:
                    suites.append((pas[0], pas[1], sens, duree_pas(allure, sens)))
            if passages:
                suites.extend(passages(salle, case))
            for (s, fin), regle, sens, duree in suites:
                if s != salle or fin in table or cout + duree >= couts.get(fin, float("inf")):
                    continue
                couts[fin] = cout + duree
                ordre += 1
                heapq.heappush(file, (cout + duree, ordre, fin, chemin + ((s, fin, regle, sens),)))
        return table

    if cle in _DISTANCES:
        table = _DISTANCES[cle]
        _DISTANCES.move_to_end(cle)
        if a_verifier():
            assert table == calculer(), "Distances locales crues périmées"
        return table
    table = calculer()
    _DISTANCES[cle] = table
    if len(_DISTANCES) > DISTANCES_MAX:
        _DISTANCES.popitem(last=False)
    return table


def monde_cru(m, acteur):
    """Copie de lecture : les positions et formes des obstacles viennent des croyances."""
    from .esprits import lire
    croyances = memoire.faits_connus(m, acteur)
    cru = copy.copy(m)
    # Ce monde de lecture ne sert qu'à la géométrie ; ses tables de pas sont
    # privées et leur clé reste vérifiée par spatial.VERIFICATION.
    cru._cache_vue = {"persistant": {"pas": {}}}
    cru.objets = {i: dict(o) for i, o in m.objets.items()}
    # Ne jamais partager le dictionnaire des objets avec le monde réel.
    cru.data = {**m.data, "objets": cru.objets}
    for i, o in cru.objets.items():
        c = croyances.get(i, {})
        if o.get("bloque_passage"):
            lieu = c.get("lieu", {})
            o["bloque_passage"] = bool(lieu.get("salle") and lieu.get("case") is not None and lieu.get("valeur") is not None)
            if o["bloque_passage"]:
                o.update(lieu=lieu["salle"], position=list(lieu["case"]), position_salle=lieu["salle"])
            if "passage" in c:
                o["passage"] = copy.deepcopy(c["passage"]["valeur"])
            else:
                o.pop("passage", None)
        if o.get("type") == "porte":
            o["ouverte"] = bool(c.get("etat", {}).get("valeur", {}).get("ouverte"))
            o["verrouillee"] = bool(c.get("verrouillee", {}).get("valeur"))
    return cru


_PARCOURS = OrderedDict()
PARCOURS_MAX = 256


def parcours_cru(m, acteur, depart, cles=(), ouvertes=(), equipement=None, *, position=None,
                 allure=PAS_JOUEUR, metrique=None, cru=None):
    """Partage les parcours identiques, sans fusionner les états de recherche.

    La clé conserve l'ordre des salles, sorties et obstacles : il départage les
    chemins de même coût. Positions et portes viennent du monde de lecture cru.
    Les ressources, l'orientation et l'horloge ne changent pas ce parcours ;
    les rotations sont toujours payées ensuite par ``cout_route``.
    """
    from .spatial import a_verifier, position_cible
    from .eau import noyee_crue
    from .pnj import DUREES
    cru = monde_cru(m, acteur) if cru is None else cru
    equipement = portes(m, acteur) if equipement is None else equipement
    cles = frozenset(cles) | frozenset(k for k in equipement if m.objets[k].get("ouvre"))
    metrique = metrique_necessaire(m, acteur, allure) if metrique is None else metrique
    o = m.objets[acteur]
    position = tuple(position) if position is not None else (
        tuple(o["position"]) if depart == o["lieu"] and o.get("position") is not None else None)
    formes = descriptions_crues(m, acteur) if metrique else None
    obstacles = [(i, x.get("lieu"), position_cible(cru, i, x["lieu"]), x.get("passage"))
                 for i, x in cru.objets.items() if x.get("bloque_passage") and not x.get("incorpore")
                 and x.get("lieu") in cru.data["salles"]]
    ids_portes = {s["porte"] for d in m.data["salles"].values()
                  for s in d["sorties"].values() if s.get("porte")}
    portes_sorties = [(i, x.get("ouverte"), x.get("verrouillee")) for i, x in cru.objets.items()
                      if i in ids_portes]
    equip = [(i, cru.objets[i].get("masse", 0), cru.objets[i].get("longueur_cm"),
              cru.objets[i].get("physique", {}).get("dimensions")) for i in sorted(equipement)] if metrique else None
    cle = (cle_carte(m), cle_carte(cru), json.dumps([obstacles, portes_sorties,
                      depart, position, allure, sorted(ouvertes),
                      [(k, m.objets[k].get("ouvre")) for k in sorted(cles)],
                      [s for s in m.data["salles"] if noyee_crue(m, acteur, s)],
                      metrique, formes, gabarit(cru, acteur) if metrique else None, equip,
                      DUREES["ouvrir"], DUREES["deverrouiller"]], check_circular=False))

    def calculer():
        return _parcours_cru(m, acteur, depart, cles, ouvertes, equipement, position=position,
                             allure=allure, metrique=metrique, cru=cru)

    if cle in _PARCOURS:
        resultat = _PARCOURS[cle]
        _PARCOURS.move_to_end(cle)
        if a_verifier():
            neuf = calculer()
            assert _empreinte_parcours(resultat) == _empreinte_parcours(neuf), "Parcours cru périmé"
        return resultat
    resultat = calculer()
    _PARCOURS[cle] = resultat
    if len(_PARCOURS) > PARCOURS_MAX:
        _PARCOURS.popitem(last=False)
    return resultat


def _empreinte_parcours(parcours):
    def route(r):
        if not isinstance(r, Route):
            return list(r)
        return list(r), r.fin, r.chemin, r.sejours, r.portes, r.depart
    return (list(parcours.items()), [(s, route(r)) for s, r in parcours.routes.items()],
            [(k, list(t.items()), route(r)) for k, (t, r) in getattr(parcours, "locaux", {}).items()])


def _parcours_cru(m, acteur, depart, cles=(), ouvertes=(), equipement=None, *, position=None,
                 allure=PAS_JOUEUR, metrique=None, cru=None):
    """Un parcours en cases, partagé par toutes les destinations d'une recherche.

    Chaque seuil atteint garde sa route. Toutes les lectures de position et de
    forme des obstacles sont celles du PNJ, jamais celles du MJ.
    """
    from .spatial import _case_libre, _case_interieure, _pas_possibles, VECTEURS
    from .geometrie import cases
    from .eau import noyee_crue
    cru = monde_cru(m, acteur) if cru is None else cru
    o = m.objets[acteur]
    depart_case = tuple(position) if position is not None else (
        tuple(o["position"]) if depart == o["lieu"] and o.get("position") is not None else None)
    if depart_case is None:
        sols = sorted(cases(m.data["salles"][depart]))
        depart_case = next((c for c in sols if _case_libre(cru, depart, c)), None)
    resultat = Parcours(depart)
    if depart_case is None:
        return resultat
    equipement = portes(m, acteur) if equipement is None else equipement
    cles = frozenset(cles) | frozenset(k for k in equipement if m.objets[k].get("ouvre"))
    metrique = metrique_necessaire(m, acteur, allure) if metrique is None else metrique
    passages = transitions(cru, acteur, descriptions_crues(m, acteur), equipement, allure) if metrique else None
    origine = (depart, depart_case)
    initiale = Route(fin=origine)
    resultat.routes[depart] = initiale
    # Le graphe global ne développe que le départ et les seuils d'entrée. Les
    # distances intérieures, y compris jusqu'aux objets, viennent des tables locales.
    file, prix, ordre = [(0, 0, origine, initiale)], {origine: 0}, 0
    pas_de = _pas_possibles(cru, True)
    resultat.locaux = {}
    while file:
        cout, _, ici, route = heapq.heappop(file)
        if cout != prix[ici]:
            continue
        salle, case = ici
        if salle not in resultat.routes:
            resultat.routes[salle] = route
            avant = route.chemin[-2][0] if len(route.chemin) > 1 else depart
            resultat[salle] = (avant, route[-1])
        table = distances(cru, acteur, salle, case, equipement, allure, passages)
        resultat.locaux[ici] = table, route
        for direction, sortie in m.data["salles"][salle]["sorties"].items():
            vers, porte = sortie["vers"], sortie.get("porte")
            seuil = _case_interieure(cru, salle, sortie)
            if (seuil not in table or vers not in m.data["salles"] or noyee_crue(m, acteur, vers)
                    or porte and porte not in ouvertes and cru.objets[porte].get("verrouillee")
                    and not any(porte in m.objets[k].get("ouvre", ()) for k in cles)):
                continue
            # Le pas du moteur choisit le véritable seuil d'en face, y compris
            # les sorties non contiguës et les escaliers.
            traverses = []
            sens = VECTEURS.get(direction)
            pas = pas_de(salle, seuil, sens) if sens is not None else None
            if pas is not None and pas[0][0] == vers:
                traverses.append((pas[0], sens))
            for fin, sens in traverses:
                marche, chemin = table[seuil]
                geste_porte = duree_porte(cru, porte, ouvertes) if porte and porte not in route.portes else 0
                pas = duree_pas(allure, sens)
                total = cout + marche + geste_porte + pas
                if total >= prix.get(fin, float("inf")):
                    continue
                prix[fin] = total
                sorties = [*route, dict(sortie, duree_trajet=total)]
                suivante = Route(sorties, fin=fin,
                                 chemin=(*route.chemin, *chemin, (fin[0], fin[1], porte, sens)),
                                 sejours=(*route.sejours, (salle, marche + geste_porte), (vers, pas)),
                                 portes=route.portes | ({porte} if porte else set()), depart=depart)
                ordre += 1
                heapq.heappush(file, (total, ordre, fin, suivante))
    return resultat


def sejours_route(route, orientation=None):
    """Les durées de la route et les rotations précédant ses pas, par salle."""
    if orientation in route._sejours:
        return route._sejours[orientation]
    debut = orientation
    sejours = list(route.sejours)
    ici = route.depart
    for salle, _, _, sens in route.chemin:
        vers = next(k for k, v in VECTEURS.items() if v == sens)
        sejours.append((ici, QUART * quarts(orientation, vers)))
        orientation = vers
        ici = salle
    # Agréger par salle évite de repayer la pression à chaque pas d'un même trajet.
    totaux = {}
    for s, d in sejours:
        totaux[s] = totaux.get(s, 0) + d
    route._sejours[debut] = tuple(totaux.items())
    return route._sejours[debut]


def cout_route(route, orientation=None):
    """Temps unique d'un trajet, en minutes ; anciennes parties sans cases : leur horloge."""
    if isinstance(route, Route):
        if orientation not in route._couts:
            route._couts[orientation] = sum(d for _, d in sejours_route(route, orientation)) / MINUTE
        return route._couts[orientation]
    return route[-1]["duree_trajet"] / MINUTE if route and "duree_trajet" in route[-1] else len(route)


def transitions(m, acteur="joueur", crues=None, equipement=None, allure=PAS_JOUEUR, libre=None):
    """Arêtes de deux pas droits, sans arrêt dans l'obstacle, coûtées par la même règle.

    La forme crue est obligatoire pour un PNJ ; aucune lecture de lumière ni
    devinette à partir de la forme réelle n'entre dans la recherche.
    """
    from .spatial import position_cible, _case_libre, _bloque
    formes = ({i: o["passage"] for i, o in m.objets.items() if "passage" in o}
              if crues is None else crues)
    par_case = {}
    for i, p in formes.items():
        o = m.objets.get(i, {})
        salle = o.get("lieu")
        if salle not in m.data["salles"] or not o.get("bloque_passage") or o.get("incorpore"):
            continue
        case = position_cible(m, i, salle)
        if case is not None:
            par_case.setdefault((salle, tuple(case)), []).append((i, p))
    utilisables = {}

    def depuis(salle, depart):
        for sens in ((-1, 0), (0, -1), (0, 1), (1, 0)):
            milieu = (depart[0] + sens[0], depart[1] + sens[1])
            obstacles = par_case.get((salle, milieu), ())
            if len(obstacles) != 1:
                continue
            i, p = obstacles[0]
            if _bloque(m, salle, milieu, sauf=i):
                continue
            fin = (milieu[0] + sens[0], milieu[1] + sens[1])
            case_libre = libre or (lambda s, c: _case_libre(m, s, c))
            # Deux pas droits dans le même sol. Ni mur, ni seuil, ni obstacle
            # superposé n'est escamoté ; les diagonales restent à contourner.
            if not case_libre(salle, fin):
                continue
            from .geometrie import cases
            if milieu not in cases(m.data["salles"][salle]):
                continue
            cle = i
            if cle not in utilisables:
                choix = []
                for methode in METHODES:
                    try:
                        choix.append(conditions(m, i, methode, acteur, p, equipement))
                    except ErreurMonde:
                        pass
                utilisables[cle] = choix
            for regle in utilisables[cle]:
                duree = 2 * duree_pas(PAS_JOUEUR, sens) * regle["facteur"]
                # Un pas feutré peut ralentir, jamais accélérer ce franchissement.
                duree = max(duree, 2 * duree_pas(allure, sens))
                yield (salle, fin), {**regle, "dixiemes": duree}, sens, duree
    return depuis


def compiler(m, e, justification="", origine="règles"):
    from .moteur import Plan
    from .refus import inaccessible
    from .spatial import position_cible
    cible, methode = e["cible"], e["methode"]
    if not m.accessible(cible):
        raise inaccessible(m, cible)
    from .proximite import exiger
    exiger(m, cible)
    if e["outil"]:
        raise ErreurMonde("Ce passage se fait sans outil.", f"outil={e['outil']!r} : accepté vide.")
    if e["destination"]:
        raise ErreurMonde("Ce passage mène au sol libre juste en face.", f"destination={e['destination']!r} : accepté vide.")
    if e["difficulte"]:
        raise ErreurMonde("La difficulté de ce passage est fixée par sa forme.",
                          f"difficulte={e['difficulte']} : accepté 0.")
    regle = conditions(m, cible, methode)
    if not m.data.get("mode_cases"):
        raise ErreurMonde("Ce franchissement exige une position et un sol de réception décrits.",
                          "mode_cases=false : accepté true, avec position et sol de réception.")
    salle, depart = m.joueur["salle"], tuple(m.joueur["position"])
    milieu = position_cible(m, cible, salle)
    if milieu is None or abs(milieu[0] - depart[0]) + abs(milieu[1] - depart[1]) != 1:
        raise ErreurMonde("Approche-toi d'un côté de l'obstacle pour passer de l'autre côté.",
                          f"joueur.position={depart} : accepté une case orthogonale voisine de {cible}, position={milieu}.")
    sens = (milieu[0] - depart[0], milieu[1] - depart[1])
    fin = (milieu[0] + sens[0], milieu[1] + sens[1])
    possibilites = transitions(m)(salle, depart)
    choix = next((r for (s, c), r, v, d in possibilites if r["cible"] == cible and r["methode"] == methode and v == sens), None)
    if choix is None:
        raise ErreurMonde("Il n'y a pas de sol libre où ressortir de l'autre côté.",
                          f"{salle}.reception={fin} : accepté une case de sol libre dans cette salle.")
    from .pnj import occupants
    occupant = occupants(m, "joueur").get((salle, fin))
    if occupant:
        raise ErreurMonde("Quelqu'un occupe l'endroit où tu dois ressortir.",
                          f"{salle}.reception={fin}, occupant={occupant} : accepté case inoccupée.")
    verbes = {"ramper": "Ramper sous ", "enjamber": "Enjamber ", "escalader": "Escalader "}
    p = Plan({"action": "composer", "justification": justification}, m.data["revision"],
             verbes[regle["maniere"]] + designer(m.objets[cible]) + ".", origine=origine)
    p.minutes, p.dixiemes, p.confirmation = 0, choix["dixiemes"], True
    p.stat, p.dd = regle["stat"], regle["dd"]
    p.information = (f"Durée : {p.dixiemes / 10:g} secondes. "
                     + ("Bruit feutré." if regle["nature"] == "feutre" else "Bruit de pas." if regle["nature"] == "pas" else "Bruit de mouvement."))
    p.effets = [("passer_obstacle", cible, {"salle": salle, "position": list(fin), **regle})]
    if p.stat:
        p.risque = "En cas d'échec, tu restes de ce côté ; l'effort et le temps sont dépensés."
    return p


def appliquer(m, acteur, cible, valeur, lignes):
    from .deplacement_objet import placer
    o = m.joueur if acteur == "joueur" else m.objets[acteur]
    if acteur == "joueur":
        o["position"] = list(valeur["position"])
    else:
        placer(o, valeur["salle"], list(valeur["position"]))
    verbe = {"ramper": "passes en rampant sous ", "enjamber": "enjambes ", "escalader": "escalades "}[valeur["maniere"]]
    if acteur == "joueur":
        lignes.append("Tu " + verbe + designer(m.objets[cible]) + " et rejoins le sol de l'autre côté.")
    else:
        from .pnj import _chroniquer
        texte = designer(o, debut=True) + {"ramper": " rampe sous ", "enjamber": " enjambe ", "escalader": " escalade "}[valeur["maniere"]] + designer(m.objets[cible]) + "."
        _chroniquer(m, acteur, texte, "deplacement")
        if m.visible(acteur):
            lignes.append(texte)


def dossier(m):
    from .espace import objets_proches

    resultat = []
    for i, o in objets_proches(m).items():
        if not o.get("bloque_passage"):
            continue
        for methode in METHODES:
            try:
                # Même préparation que le geste : une cible dans le dos est jugée
                # tournée vers elle, sans changer l'état ni exécuter la rotation.
                from .moteur import Moteur
                from .operations import sequence, etape
                p = Moteur(m).preparer(sequence(etape("passer_obstacle", i, methode=methode)))
                p = p.plans[0]
                resultat.append({"cible": i, "methode": methode, "fiche": p.titre + " " + p.information,
                                 "stat": p.stat, "dd": p.dd})
            except ErreurMonde as exc:
                resultat.append({"cible": i, "methode": methode, "refus": str(exc), "attendu": exc.attendu})
    return resultat
