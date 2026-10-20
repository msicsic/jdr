"""Actions des PNJ : le moteur exécute leurs intentions avec les règles physiques du joueur.

Chaque minute, un PNJ doté d'un profil délibère (``deliberation.py``). Entre-temps, il
accomplit son plan geste après geste, chacun avec sa durée, à la seconde près : un pas d'une
case, ouvrir, prendre, crocheter… (``temps``). Il marche case par case, par les mêmes règles
que le pas du joueur, et franchit les portes en les ouvrant. Le chemin est cherché sur ce
qu'il croit des portes ;
chaque geste est revalidé sur l'état réel et un échec devient une croyance apprise par
l'essai. Une étape `sans_temoin` attend que le PNJ ne perçoive personne ; les témoins
réels sont ceux qui voient l'auteur pendant la durée de son geste, joueur compris
(``data["gestes_en_cours"]``). Tout ce dont dépend la suite est dans ``data`` : le monde ne
dépend pas du découpage des actions du joueur. Le moteur annonce ce que le joueur perçoit et
tient une chronique complète, réservée au débogage et au banc. Luna n'intervient pas.
"""
from collections import deque

from .esprits import croire, esprit, lire, memoriser, percevoir, percevoir_tous, percoit, percus, pnjs
from .francais import complement_de, de, designer, sujet
from .geometrie import cases, placer, position_entree
from .spatial import VECTEURS

CHRONIQUE_MAX = 300
# Durées en dixièmes de seconde. Un pas d'une case ; les gestes ; ceux qui durent (se reposer,
# se chauffer, s'abriter) et l'attente d'une occasion vont jusqu'à la minute suivante, où il
# délibère de nouveau.
PAS = 15
DUREES = {"prendre": 20, "poser": 20, "ouvrir": 20, "fermer": 20, "deverrouiller": 50, "verrouiller": 50,
          "crocheter": 600, "manger": 600, "servir": 300, "alimenter": 100, "allumer": 100, "eteindre": 30,
          "inspecter": 100, "dire": 100, "demander": 100, "confier": 100, "remettre": 50}
DURABLES = ("reposer", "chauffer", "abriter")
# deplacement : passer une salle, ouvrir une porte en chemin ; geste : agir sur un objet ;
# social : une parole entre PNJ ; decision : un plan choisi ou abandonné par un PNJ ; ouie : se
# retourner au bruit, retenir un bruit inconnu, aller le voir (``ouie``).
NATURES = ("deplacement", "geste", "social", "decision", "ouie")
# Un geste touche sa cible, objet ou personne à qui l'on parle (``_a_toucher``), sauf ceux qui
# agissent à distance : se chauffer, c'est recevoir la chaleur du feu dans sa salle (``corps``).
A_DISTANCE = ("chauffer",)


def verifier(monde):
    for o in monde.objets.values():
        if o["type"] != "personnage":
            continue
        reaction = o.get("reaction_son")
        assert reaction is None or (isinstance(reaction, dict) and set(reaction) == {"seuil"}
                                    and type(reaction["seuil"]) is int
                                    and 1 <= reaction["seuil"] <= 5), "Réaction de PNJ invalide"
    verifier_places(monde)
    from .stratege import verifier as verifier_stratege
    verifier_stratege(monde)
    gestes = monde.data.get("gestes_en_cours", [])
    personnages = {id for id, o in monde.objets.items() if o["type"] == "personnage"}
    assert isinstance(gestes, list) and all(
        isinstance(g, dict) and set(g) == {"auteur", "operation", "objet", "fin", "temoins", "se_sait_vu", "exclus"}
        and g["auteur"] in personnages | {"joueur"} and isinstance(g["operation"], str)
        and isinstance(g["objet"], str) and type(g["fin"]) is int and g["fin"] >= 0
        and all(isinstance(g[k], list) for k in ("temoins", "se_sait_vu", "exclus"))
        and set(g["se_sait_vu"]) <= set(g["temoins"])
        and set(g["temoins"]) | set(g["exclus"]) <= personnages for g in gestes), "Gestes en cours invalides"
    chronique = monde.data.get("chronique", [])
    assert (isinstance(chronique, list) and len(chronique) <= CHRONIQUE_MAX
            and all(isinstance(c, dict) and set(c) - {"nature"} == {"minute", "pnj", "texte"}
                    and c.get("nature", "geste") in NATURES for c in chronique)), "Chronique invalide"


def _etape(operation, cible="", outil="", lieu="", condition=""):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu, "condition": condition}


def reagir(monde, id, origine, niveau, auteur=None):
    """Réflexe déclaré par l'auteur : un son assez fort donne l'intention d'aller voir. L'appel
    d'un protégé fait accourir son protecteur."""
    pnj = monde.objets[id]
    reaction = pnj.get("reaction_son")
    protege = auteur in (pnj.get("profil") or {}).get("protege", [])
    if (protege or reaction and niveau >= reaction["seuil"]) and origine != pnj["lieu"]:
        esprit(monde, id)["intention"] = {"but": {"type": "rejoindre", "lieu": origine}, "motif": "alerte",
                                          "plan": [_etape("aller", lieu=origine)],
                                          "depuis": monde.data["minutes"], "attente": 0}


def _porte(monde, objet, id):
    from .spatial import porte_par
    return porte_par(monde, objet, id)


def _cle_portee(monde, id, cible, cles=()):
    return next((c for c, o in monde.objets.items()
                 if cible in o.get("ouvre", []) and (c in cles or _porte(monde, c, id))), None)


def _verrouillee_crue(monde, id, porte):
    cru = lire(monde, id)["croyances"].get(porte, {}).get("verrouillee")
    return bool(cru and cru["valeur"])


def _cases_barrees_crues(monde, id):
    """Les cases où il croit un obstacle qui barre le passage : vu, ou buté dessus (``_impasse``)."""
    barrees = set()
    for sujet, attributs in lire(monde, id)["croyances"].items():
        lieu = attributs.get("lieu")
        if (lieu and lieu["valeur"] is not None and lieu.get("case")
                and monde.objets.get(sujet, {}).get("bloque_passage")):
            barrees.add((lieu["salle"], tuple(lieu["case"])))
    return barrees


def _seuil_barre(monde, salle, sortie, barrees):
    """Un obstacle qu'il croit sur le seuil, d'un côté ou de l'autre, barre ce passage."""
    from .spatial import _case_interieure
    vers = sortie["vers"]
    retour = next((s for s in monde.data["salles"][vers].get("sorties", {}).values()
                   if s.get("vers") == salle and s.get("porte") == sortie.get("porte")), None)
    seuils = {(salle, _case_interieure(monde, salle, sortie))}
    if retour is not None:
        seuils.add((vers, _case_interieure(monde, vers, retour)))
    return bool(seuils & barrees)


def chemin(monde, id, depart, arrivee, cles=()):
    """Sorties à emprunter selon ce que le PNJ croit des portes et des obstacles ; None si aucun
    passage cru.

    Le PNJ tente toute porte, sauf celle qu'il sait verrouillée sans en porter (ou prévoir
    d'en porter) la clé ; tout passage, sauf celui dont il croit un seuil barré ; et il ne passe
    pas par une salle qu'il a vue noyée.
    """
    from .eau import noyee_crue
    barrees = _cases_barrees_crues(monde, id) if monde.data.get("mode_cases") else set()
    precedent, file = {depart: None}, deque([depart])
    while file:
        lieu = file.popleft()
        for sortie in monde.data["salles"][lieu]["sorties"].values():
            vers, porte = sortie["vers"], sortie.get("porte")
            if (vers in precedent or vers not in monde.data["salles"] or noyee_crue(monde, id, vers)
                    or porte and _verrouillee_crue(monde, id, porte)
                    and _cle_portee(monde, id, porte, cles) is None
                    or barrees and _seuil_barre(monde, lieu, sortie, barrees)):
                continue
            precedent[vers] = (lieu, sortie)
            file.append(vers)
    if arrivee not in precedent:
        return None
    etapes = []
    while arrivee != depart:
        lieu, sortie = precedent[arrivee]
        etapes.append(sortie)
        arrivee = lieu
    return etapes[::-1]


# --- Annonces et chronique ----------------------------------------------------------------

def _chroniquer(monde, id, texte, nature="geste"):
    chronique = monde.data.setdefault("chronique", [])
    chronique.append({"minute": monde.data["minutes"], "pnj": id, "texte": texte, "nature": nature})
    del chronique[:-CHRONIQUE_MAX]


def _raconter(monde, id, verbe, objet, lignes):
    """« X prend la trousse. » ; un verbe finissant par « de » prend le complément contracté."""
    groupe = verbe[:-3] + " " + complement_de(objet) if verbe.endswith(" de") else verbe + " " + designer(objet)
    texte = designer(monde.objets[id], debut=True) + " " + groupe + "."
    _chroniquer(monde, id, texte)
    if monde.visible(id):
        lignes.append(texte)


def _annoncer_porte(monde, id, porte, verbe, texte_porte, lignes):
    """Une porte qu'il ouvre, déverrouille ou pousse en chemin : un geste, qui retentit."""
    texte = designer(monde.objets[id], debut=True) + " " + verbe + " " + designer(porte) + "."
    _chroniquer(monde, id, texte, "deplacement")
    if monde.visible(id):
        lignes.append(texte)
    elif monde.visible(porte["id"]):
        lignes.append(designer(porte, debut=True) + texte_porte)
    from .ouie import retentir
    retentir(monde, id, "ouvrir", discret=a_pas_feutres(monde, id))


def temoins_crus(monde, id):
    """Ceux que le PNJ perçoit : il se croit observé par chacun d'eux."""
    return [s for s in percus(monde, id)[0]
            if s == "joueur" or monde.objets[s]["type"] == "personnage"]


TOUR = 40              # dixièmes de seconde : un tour complet sur soi-même, huit fois 45°


def commencer_geste(monde, auteur, operation, objet, fin, exclus=()):
    """Un geste illicite de ``auteur`` (un PNJ ou le joueur), en cours jusqu'à l'instant ``fin`` :
    il entre au registre commun, et ceux qui le voient faire en sont témoins dès maintenant.
    ``exclus`` : ceux qui le regardaient déjà et dont le jet du joueur a tranché le sort ;
    ``se_sait_vu`` : les témoins que l'auteur a vus le regarder."""
    geste = {"auteur": auteur, "operation": operation, "objet": objet, "fin": fin, "temoins": [],
             "se_sait_vu": [], "exclus": sorted(exclus)}
    monde.data.setdefault("gestes_en_cours", []).append(geste)
    _temoigner(monde, geste)
    return geste


def finir_gestes(monde, avant, auteur=None):
    """Les gestes achevés avant l'instant ``avant`` (ou à cet instant, pour un ``auteur`` qui en
    commence un autre) quittent le registre."""
    gestes = monde.data.get("gestes_en_cours")
    if gestes:
        gestes[:] = [g for g in gestes if not (g["fin"] < avant or g["auteur"] == auteur and g["fin"] <= avant)]


def temoigner_en_cours(monde):
    """Ceux qui voient maintenant l'auteur d'un geste illicite qu'il n'a pas fini en sont témoins."""
    from .temps import instant
    finir_gestes(monde, instant(monde))
    for geste in monde.data.get("gestes_en_cours", []):
        if geste["objet"] in monde.objets and (geste["auteur"] == "joueur" or geste["auteur"] in monde.objets):
            _temoigner(monde, geste)


def tour_d_horizon(monde, id):
    """Il regarde tout autour de lui, le temps d'un tour complet : ce qu'il voit devient croyance.
    Renvoie ceux par qui il se croit observé ; il reprend ensuite son orientation."""
    o = monde.objets[id]
    orientation = o.pop("orientation", None)
    try:
        percevoir(monde, id)
        temoigner_en_cours(monde)
        return temoins_crus(monde, id)
    finally:
        if orientation is not None:
            o["orientation"] = orientation


def _temoigner(monde, geste):
    """Les PNJ qui perçoivent réellement l'auteur d'un geste illicite en cours s'en souviennent.

    Appelé tant que le geste dure, il compte aussi ceux qui arrivent ou se retournent
    entre-temps ; chacun n'en est témoin qu'une fois (``geste["temoins"]``).
    """
    from .vol import proprietaire
    id, operation, objet = geste["auteur"], geste["operation"], geste["objet"]
    victime = proprietaire(monde, monde.objets[objet])
    souvenir = {"type": "vu_agir", "auteur": id, "operation": operation, "objet": objet}
    from .spatial import etat_fige
    with etat_fige(monde):  # Les témoins ne révisent que leur esprit.
        _temoins(monde, geste, souvenir, victime)


def _temoins(monde, geste, souvenir, victime):
    from .deliberation import VOL, inquieter, relancer
    id = geste["auteur"]
    for autre in pnjs(monde):
        if autre != id and autre not in geste["temoins"] and autre not in geste["exclus"] and percoit(monde, autre, id):
            geste["temoins"].append(autre)
            if monde.visible(autre) if id == "joueur" else percoit(monde, id, autre):
                geste["se_sait_vu"].append(autre)
            memoriser(monde, autre, souvenir)
            croire(monde, autre, id, "fiable", False, "vu")
            inquieter(monde, autre, "illicite")
            if autre == victime:
                relancer(monde, autre, "biens", VOL)
            elif victime in (monde.objets[autre].get("profil") or {}).get("protege", []):
                # Un protégé atteint : son devoir est touché, il ira le prévenir.
                from .deliberation import ATTEINTE
                relancer(monde, autre, "devoir", ATTEINTE)
                memoriser(monde, autre, {"type": "a_prevenir", "victime": victime, "auteur": id})


# --- Gestes -------------------------------------------------------------------------------

def _au_seuil(monde, o, sortie):
    """Place le PNJ sur la case intérieure de la sortie, comme le joueur pour l'ouvrir."""
    if "position" not in o or not monde.data.get("mode_cases"):
        return
    from .spatial import _case_interieure, _case_libre
    case = _case_interieure(monde, o["lieu"], sortie)
    if case is not None and _case_libre(monde, o["lieu"], case) and not _occupee(monde, o["id"], o["lieu"], case):
        placer(o, o["lieu"], list(case))


def occupants(monde, sauf=None):
    """{(salle, case): qui s'y tient} : le joueur et les personnages placés, hormis ``sauf``."""
    places = {}
    j = monde.joueur
    if sauf != "joueur" and j.get("position") is not None:
        places[j["salle"], tuple(j["position"])] = "joueur"
    for k, o in monde.objets.items():
        if (o["type"] == "personnage" and k != sauf and o.get("lieu") in monde.data["salles"]
                and o.get("position") is not None):
            places.setdefault((o["lieu"], tuple(o["position"])), k)
    return places


def _occupee(monde, id, salle, case):
    """Un autre personnage, ou le joueur, se tient déjà sur la case."""
    return (salle, tuple(case)) in occupants(monde, id)


def verifier_places(monde):
    """Aucun geste ne s'achève sur une case occupée : deux personnages, joueur compris, ne se
    tiennent jamais sur la même case."""
    if not monde.data.get("mode_cases"):
        return
    places = [("joueur", (monde.joueur["salle"], tuple(monde.joueur["position"])))]
    places += [(k, (o["lieu"], tuple(o["position"]))) for k, o in monde.objets.items()
               if o["type"] == "personnage" and o.get("lieu") in monde.data["salles"] and o.get("position") is not None]
    vues = {}
    for k, place in places:
        assert place not in vues, f"Deux personnages sur la même case : {vues.get(place)}/{k}"
        vues[place] = k


def ecarter(monde):
    """Anciennes parties : un personnage arrivé sur une case occupée s'écarte vers la case libre
    la plus proche de sa salle."""
    if not monde.data.get("mode_cases"):
        return
    from .spatial import _case_libre
    for k in pnjs(monde):
        o = monde.objets[k]
        if o.get("lieu") not in monde.data["salles"] or o.get("position") is None:
            continue
        prises = occupants(monde, k)
        if (o["lieu"], tuple(o["position"])) not in prises:
            continue
        x, y = o["position"]
        libres = [c for c in cases(monde.data["salles"][o["lieu"]])
                  if (o["lieu"], tuple(c)) not in prises and _case_libre(monde, o["lieu"], tuple(c))]
        if libres:
            placer(o, o["lieu"], list(min(libres, key=lambda c: (max(abs(c[0] - x), abs(c[1] - y)), tuple(c)))))


def _centre(monde, id):
    """La case libre la plus proche du centre de sa salle, d'où la parcourir des yeux."""
    from .spatial import _case_libre
    o = monde.objets[id]
    sol = cases(monde.data["salles"][o["lieu"]])
    cx, cy = sum(x for x, _ in sol) / len(sol), sum(y for _, y in sol) / len(sol)
    libres = [c for c in sol if tuple(c) == tuple(o["position"])
              or _case_libre(monde, o["lieu"], c) and not _occupee(monde, id, o["lieu"], c)]
    return min(libres, key=lambda c: ((c[0] - cx) ** 2 + (c[1] - cy) ** 2, tuple(c))) if libres else None


def _inspecter(monde, id):
    """Depuis le centre de la salle (où il a marché), il la parcourt des yeux."""
    from .ouie import parcouru
    o = monde.objets[id]
    esprit(monde, id)["visites"][o["lieu"]] = monde.data["minutes"]
    if "orientation" in o:
        tour_d_horizon(monde, id)  # Il parcourt la salle des yeux, tout autour de lui.
    bruit = parcouru(monde, id, o["lieu"])
    if bruit:
        from .social import _qui
        _chroniquer(monde, id, f"{_qui(monde, id)} va voir d'où venait le bruit : {monde.data['salles'][o['lieu']]['nom']}.",
                    "ouie")
    # Une ronde accomplie, un bruit allé voir rassurent : le lieu est tel qu'il doit être.
    if bruit or any(x["condition"].get("lieu") == o["lieu"] and "periode" in x["condition"]
                                for x in (o.get("profil") or {}).get("pulsions", [])):
        from .deliberation import inquieter
        inquieter(monde, id, "ronde", -1)


def _accessible(monde, id, objet):
    """L'objet est-il à portée de main du PNJ, là où il se tient, hors de tout contenant fermé et
    des mains d'autrui ? Il ne se déplace pas pour le vérifier : c'est sa marche qui l'en approche
    (``agir``)."""
    from .spatial import proche
    if _porte(monde, objet, id):
        return True
    from .esprits import _porteur
    if _porteur(monde, monde.objets[objet]) is not None:
        return False
    o = monde.objets[id]
    return (monde.present_physique(objet, salle=o["lieu"])
            and (not monde.data.get("mode_cases") or "position" not in o or proche(monde, objet, id)))


def _a_toucher(monde, id, etape):
    """Ce que le geste touche sans qu'il le porte : il doit l'avoir à portée de main. Un geste
    touche sa cible (objet, ou personne à qui l'on parle), sauf s'il agit à distance ; un outil
    fixe s'emploie sur place, un outil mobile se tient en main (on ne marche pas vers lui)."""
    from .deliberation import SOCIALES
    op = etape["operation"]
    if op in A_DISTANCE:
        return []
    touches = []
    for role in ("cible", "outil"):
        x = etape[role]
        if x not in monde.objets or _porte(monde, x, id):
            continue
        if role == "outil" and (op in SOCIALES or monde.objets[x].get("mobile")):
            continue
        touches.append(x)
    return touches


def _pas(monde, id, sortie, lignes):
    """Un geste d'une minute vers la sortie : ouvrir, déverrouiller, essayer ou passer."""
    o = monde.objets[id]
    porte = monde.objets.get(sortie.get("porte") or "")
    if porte and not porte.get("ouverte"):
        _au_seuil(monde, o, sortie)
        if porte.get("verrouillee"):
            cle = _cle_portee(monde, id, porte["id"])
            if cle is None:
                croire(monde, id, porte["id"], "verrouillee", True, "essai")
                _annoncer_porte(monde, id, porte, "tente d'ouvrir", " résiste à une poussée.", lignes)
                return
            porte["verrouillee"] = False
            croire(monde, id, porte["id"], "verrouillee", False, "essai")
            _annoncer_porte(monde, id, porte, "déverrouille", " se déverrouille.", lignes)
            return
        porte["ouverte"] = True
        croire(monde, id, porte["id"], "verrouillee", False, "essai")
        _annoncer_porte(monde, id, porte, "ouvre", " s'ouvre.", lignes)
        return
    if _arrete_par_l_eau(monde, id, sortie["vers"]):
        return
    depuis, o["lieu"] = o["lieu"], sortie["vers"]
    if "position" in o:
        placer(o, o["lieu"], position_entree(monde, o["lieu"], depuis))
    _chroniquer(monde, id, designer(o, debut=True) + " passe dans : " + monde.data["salles"][o["lieu"]]["nom"] + ".",
                "deplacement")
    from .eau import tremper
    tremper(monde, id)
    from .ouie import retentir
    retentir(monde, id, "aller", discret=a_pas_feutres(monde, id))


def _arrete_par_l_eau(monde, id, salle):
    """Au seuil d'une salle noyée, il voit l'eau et n'y entre pas : il l'apprend par l'essai."""
    from .eau import noyee, observer
    if not noyee(monde, salle):
        return False
    observer(monde, id, salle, "essai")
    return True


def _rate(monde, id, cible, attribut="lieu", valeur=None):
    """Un geste impossible corrige la croyance qui l'avait motivé."""
    from .esprits import reviser
    if attribut == "lieu":
        reviser(monde, id, cible, "lieu", None, "essai", salle=None, case=None)
    else:
        reviser(monde, id, cible, attribut, valeur, "essai")
    return False


def _crocheter(monde, id, cible, outil):
    from .caractere import modificateur
    from .perception import eclairage
    o = monde.objets[id]
    lumiere = eclairage(monde, o["lieu"], o.get("position") if monde.data.get("mode_cases") else None)["niveau"]
    return monde.d20() + modificateur(monde, id, "DEX") >= 14 + 4 * (2 - lumiere)


def _executer(monde, id, etape, lignes, gestes):
    """Accomplit une étape ; renvoie True si elle est terminée."""
    from .deliberation import SATIETE, illicite
    from .deplacement_objet import deplacer
    o = monde.objets[id]
    op, cible, outil = etape["operation"], etape["cible"], etape["outil"]
    if op == "aller":
        route = chemin(monde, id, o["lieu"], etape["lieu"])
        if route:
            _pas(monde, id, route[0], lignes)
        return o["lieu"] == etape["lieu"]
    if op == "inspecter":
        if o["lieu"] != etape["lieu"]:
            return False
        _inspecter(monde, id)
        return True
    if op == "reposer":
        return _reposer(monde, id, lignes)
    if op == "abriter":
        return _abriter(monde, id, etape["lieu"], lignes)
    from .deliberation import SOCIALES
    if op in SOCIALES:
        from .echanges import executer
        return executer(monde, id, etape, lignes)
    c = monde.objets.get(cible)
    if c is None:
        return False
    if op == "chauffer":
        return _chauffer(monde, id, cible, lignes)
    for objet in _a_toucher(monde, id, etape):
        if not _accessible(monde, id, objet):
            return _rate(monde, id, objet)
    if outil and not _porte(monde, outil, id) and monde.objets.get(outil, {}).get("mobile", True):
        return _rate(monde, id, outil)  # Un outil mobile s'emploie en main.
    # Il y porte la main : le geste retentit, réussi ou non ; feutré s'il le veut sans témoin.
    from .ouie import retentir
    retentir(monde, id, op, discret=etape["condition"] == "sans_temoin")
    faute = illicite(monde, id, cible)
    if op == "prendre":
        if not c.get("mobile"):
            return False
        deplacer(monde, cible, id)
        _raconter(monde, id, "prend", c, lignes)
    elif op == "poser":
        if not _porte(monde, cible, id) or o["lieu"] != etape["lieu"]:
            return False
        deplacer(monde, cible, o["lieu"], position=o.get("position"))
        _raconter(monde, id, "pose", c, lignes)
    elif op == "ouvrir":
        if c.get("verrouillee"):
            return _rate(monde, id, cible, "verrouillee", True)
        c["ouverte"] = True
        _raconter(monde, id, "ouvre", c, lignes)
        _ouvert_par_soi(monde, id, cible)
    elif op == "fermer":
        c["ouverte"] = False
        _raconter(monde, id, "ferme", c, lignes)
    elif op in ("deverrouiller", "verrouiller"):
        if cible not in monde.objets[outil].get("ouvre", []) or c.get("ouverte"):
            return False
        c["verrouillee"] = op == "verrouiller"
        croire(monde, id, cible, "verrouillee", c["verrouillee"], "essai")
        _raconter(monde, id, "déverrouille" if op == "deverrouiller" else "verrouille", c, lignes)
        if op == "deverrouiller":
            _ouvert_par_soi(monde, id, cible)
    elif op == "crocheter":
        if not c.get("verrouillee"):
            return _rate(monde, id, cible, "verrouillee", False) or True
        if not _crocheter(monde, id, cible, outil):
            _raconter(monde, id, "s'acharne sur la serrure de", c, lignes)
            if faute:
                gestes.append((id, "forcer", cible))
            return False
        c["verrouillee"] = False
        croire(monde, id, cible, "verrouillee", False, "essai")
        _raconter(monde, id, "crochète la serrure de", c, lignes)
    elif op == "manger":
        if c.get("portions", 0) <= 0:
            croire(monde, id, cible, "etat", {"disponible": False}, "essai")
            return False
        c["portions"] -= 1
        besoins = esprit(monde, id)["besoins"]
        besoins["faim"] = max(0.0, besoins.get("faim", 0) - SATIETE)
        _raconter(monde, id, "mange une part de", c, lignes)
    elif op == "servir":
        from .echanges import servir
        if not servir(monde, id, cible, etape.get("contenu", {}).get("pour"), lignes):
            return False
    elif op == "alimenter":
        from .perception import alimenter
        if not alimenter(monde, cible, outil):
            croire(monde, id, outil, "etat", {"disponible": False}, "essai")
            return False
        _raconter(monde, id, "alimente", c, lignes)
    elif op == "allumer":
        from .perception import flamme
        t = monde.objets[outil]
        if c.get("allume") is not False or c["integrite"] == 0 or outil == cible:
            return False
        from .eau import sous_l_eau
        if sous_l_eau(monde, c):
            return False  # Sous l'eau, aucune flamme ne prend.
        if not flamme(t):
            # La flamme sur laquelle il comptait s'est éteinte : il le constate.
            if "allume" in t:
                return _rate(monde, id, outil, "etat", {"allume": False, "faible": False,
                                                         "charge": t.get("combustible", 0) > 0})
            return False
        if c.get("combustible", 0) <= 0:
            return _rate(monde, id, cible, "etat", {"allume": False, "faible": False, "charge": False})
        c["allume"] = True
        _raconter(monde, id, "allume", c, lignes)
        # Une flamme portable allumée ou employée pour ce geste : il saura la ménager ensuite.
        for flamme in (cible, outil):
            if monde.objets[flamme].get("mobile") and "allume" in monde.objets[flamme]:
                memoriser(monde, id, {"type": "flamme_employee", "objet": flamme})
    elif op == "eteindre":
        if not c.get("allume"):
            return True
        c["allume"] = False
        _raconter(monde, id, "éteint", c, lignes)
    # Ce qu'il vient de faire de ses mains, il le sait, même dans le noir.
    from .esprits import constater
    for objet in (cible, outil):
        if objet in monde.objets:
            constater(monde, id, objet, "essai")
    if faute:
        gestes.append((id, op, cible))  # Au registre des gestes en cours, avec sa durée (``_avancer``).
    return True


def _chauffer(monde, id, foyer, lignes):
    """Une minute près d'un foyer allumé de sa salle ; le geste s'achève quand il est réchauffé."""
    from .deliberation import CHALEUR_FIN
    e, f = esprit(monde, id), monde.objets[foyer]
    if "chaleur" not in e["besoins"]:
        return True
    if not monde.present_physique(foyer, salle=monde.objets[id]["lieu"]):
        return _rate(monde, id, foyer)
    if not f.get("allume"):
        return _rate(monde, id, foyer, "etat", {"allume": False, "faible": False, "charge": f["combustible"] > 0})
    depuis = e["intention"]["depuis"] if e["intention"] else monde.data["minutes"]
    if not any(s["type"] == "se_chauffe" and s["minute"] >= depuis for s in e["memoire"]):
        memoriser(monde, id, {"type": "se_chauffe", "objet": foyer})
        _raconter(monde, id, "se chauffe près de", f, lignes)
    # La chaleur du feu agit d'elle-même dans sa salle (``corps``) : il reste jusqu'à être réchauffé.
    return e["besoins"]["chaleur"] <= CHALEUR_FIN


def _abriter(monde, id, lieu, lignes):
    """Une minute à l'abri : il y reste tant que la lumière ou une compagnie fiable le rassure ;
    le geste s'achève quand il est rassuré."""
    from .deliberation import SECURITE_FIN, autour
    from .social import _qui
    e = esprit(monde, id)
    if "securite" not in e["besoins"]:
        return True
    if monde.objets[id]["lieu"] != lieu:
        return False
    from .eau import menacee
    if menacee(monde, id, lieu):
        return False  # L'eau gagne le lieu, ou va le gagner : ce n'est plus un abri.
    a = autour(monde, id)
    if not a["fiables"] and not a["lumiere"]:
        return False  # Ni lumière ni personne de sûr : ce n'est pas un abri.
    depuis = e["intention"]["depuis"] if e["intention"] else monde.data["minutes"]
    if not any(s["type"] == "abrite" and s["minute"] >= depuis for s in e["memoire"]):
        memoriser(monde, id, {"type": "abrite", "lieu": lieu})
        texte = (f"{_qui(monde, id)} reste près {de(_qui(monde, a['fiables'][0]))}." if a["fiables"]
                 else f"{_qui(monde, id)} reste dans la lumière.")
        _chroniquer(monde, id, texte)
        if monde.visible(id):
            lignes.append(texte)
    return e["besoins"]["securite"] <= SECURITE_FIN


def _reposer(monde, id, lignes):
    """Une minute de repos ; le geste s'achève quand le PNJ est reposé."""
    from .deliberation import REPOS_FIN
    besoins, intention = esprit(monde, id)["besoins"], esprit(monde, id)["intention"]
    if "repos" not in besoins:
        return True
    if intention and intention["depuis"] == monde.data["minutes"]:
        texte = designer(monde.objets[id], debut=True) + " s'assoit pour se reposer."
        _chroniquer(monde, id, texte)
        if monde.visible(id):
            lignes.append(texte)
    # Le repos délasse par le corps (``corps.vivre``), tant que ce geste est en cours.
    return besoins["repos"] <= REPOS_FIN


def _ouvert_par_soi(monde, id, cible):
    """Ce qu'il garde sous clé et ouvre lui-même : il s'en souvient pour le refermer."""
    from .deliberation import garde_sous_cle
    if garde_sous_cle(monde, id, cible):
        memoriser(monde, id, {"type": "ouvert_par_soi", "objet": cible})


def desespere(monde, id):
    """Un besoin à son comble l'emporte sur la crainte d'être vu."""
    from .deliberation import DESESPOIR
    e = lire(monde, id)
    return bool(e["intention"]) and e["besoins"].get(e["intention"]["motif"], 0) >= DESESPOIR


def _jusqu_a_la_minute(t):
    from .temps import MINUTE
    return MINUTE - t % MINUTE


def _franchissable(monde, id, porte):
    """Une porte se tente, sauf celle qu'il sait verrouillée sans en porter la clé."""
    return not (_verrouillee_crue(monde, id, porte) and _cle_portee(monde, id, porte) is None)


def a_pas_feutres(monde, id):
    """Qui prépare un geste qu'il veut sans témoin marche à pas feutrés : cela se lit dans son
    intention, sans autre état."""
    intention = lire(monde, id)["intention"]
    return bool(intention) and any(x["condition"] == "sans_temoin" for x in intention["plan"])


def _marcher(monde, id, arrivee, lignes):
    """Un pas d'une case vers une case libre où ``arrivee(salle, case)``, ou la porte fermée qu'il
    rencontre en chemin ; renvoie la durée du geste, 0 s'il y est déjà, None s'il ne voit aucun
    passage. Qui prépare un geste qu'il veut sans témoin marche à pas feutrés : plus lent, il ne
    s'entend que de tout près.

    Aucun geste ne s'achève sur une case occupée. On croise les autres en chemin : le pas qui
    mène sur la case de quelqu'un se poursuit, dans le même geste, jusqu'à la case libre qui
    suit. Si une porte fermée l'en empêche, il contourne, ou attend qu'on lui laisse le passage."""
    from .spatial import trajet
    o = monde.objets[id]
    feutre = a_pas_feutres(monde, id)
    occupees = occupants(monde, id)
    depart = (o["lieu"], tuple(o["position"]))
    # Il ne cherche pas de chemin par une salle qu'il a vue noyée ; il peut quitter la sienne.
    from .eau import noyee_crue
    noyees = {s for s in monde.data["salles"] if s != o["lieu"] and noyee_crue(monde, id, s)}
    chemin_ = trajet(monde, *depart, lambda salle, case: arrivee(salle, case) and (salle, case) not in occupees,
                     franchissable=lambda porte: _franchissable(monde, id, porte),
                     libre=lambda salle, case: salle not in noyees)
    if chemin_ is None:
        return None
    if not chemin_:
        return 0
    n = 0
    while chemin_[n][:2] in occupees:
        n += 1  # La case de quelqu'un : il la traverse sans s'y arrêter.
    if any(porte for _, _, porte, _ in chemin_[1:n + 1]):
        # Une porte à ouvrir juste après la case d'un autre : il ne peut pas s'y arrêter pour l'ouvrir.
        chemin_ = trajet(monde, *depart, lambda salle, case: arrivee(salle, case) and (salle, case) not in occupees,
                         franchissable=lambda porte: _franchissable(monde, id, porte),
                         libre=lambda salle, case: (salle, case) not in occupees and salle not in noyees)
        if not chemin_:
            return PAS  # Il attend qu'on lui laisse le passage.
        n = 0
    # Au seuil d'une salle noyée qu'il ne savait pas telle, il voit l'eau et n'y entre pas.
    entree = next((salle for salle, _, _, _ in chemin_[:n + 1] if salle != o["lieu"]), None)
    if entree is not None and _arrete_par_l_eau(monde, id, entree):
        return PAS
    return _avancer_de(monde, id, chemin_[:n + 1], feutre, lignes)


def _avancer_de(monde, id, pas, feutre, lignes):
    """Les pas d'un même geste, chacun précédé de sa rotation ; une porte fermée s'ouvre sur place.
    Ses pas retentissent là où il s'arrête."""
    from .ouie import retentir
    from .spatial import QUART, quarts
    from .temps import PAS_FEUTRE
    o, duree, marche = monde.objets[id], 0, False
    for salle, case, porte, sens in pas:
        # Il se tourne d'abord dans le sens du pas : le temps de la rotation s'ajoute.
        vers = next(nom for nom, v in VECTEURS.items() if v == sens)
        duree += QUART * quarts(o.get("orientation"), vers)
        o["orientation"] = vers
        if porte:
            if marche:
                retentir(monde, id, "aller", discret=feutre)
            return duree + _ouvrir_en_chemin(monde, id, monde.objets[porte], lignes)
        if salle != o["lieu"]:
            o["lieu"] = salle
            placer(o, salle, list(case))
            _chroniquer(monde, id, designer(o, debut=True) + " passe dans : " + monde.data["salles"][salle]["nom"] + ".",
                        "deplacement")
            from .eau import tremper
            tremper(monde, id)
        else:
            placer(o, salle, list(case))
        duree += PAS_FEUTRE if feutre else PAS
        marche = True
    if marche:
        retentir(monde, id, "aller", discret=feutre)
    return duree


def _ouvrir_en_chemin(monde, id, porte, lignes):
    """La porte fermée qu'il rencontre : il l'ouvre, la déverrouille s'il en porte la clé, ou
    l'apprend verrouillée en la poussant."""
    if porte.get("verrouillee"):
        cle = _cle_portee(monde, id, porte["id"])
        if cle is None:
            croire(monde, id, porte["id"], "verrouillee", True, "essai")
            _annoncer_porte(monde, id, porte, "tente d'ouvrir", " résiste à une poussée.", lignes)
            return DUREES["ouvrir"]
        porte["verrouillee"] = False
        croire(monde, id, porte["id"], "verrouillee", False, "essai")
        _annoncer_porte(monde, id, porte, "déverrouille", " se déverrouille.", lignes)
        return DUREES["deverrouiller"]
    porte["ouverte"] = True
    croire(monde, id, porte["id"], "verrouillee", False, "essai")
    _annoncer_porte(monde, id, porte, "ouvre", " s'ouvre.", lignes)
    return DUREES["ouvrir"]


def _rejoindre_un_proche(monde, id, lignes):
    """Un pas vers la personne la plus proche qu'il croit fiable et croit dans sa salle ; None
    s'il est déjà près d'elle ou n'en connaît aucune."""
    from .deliberation import _cru, salle_crue
    o = monde.objets[id]
    ici, depart = o["lieu"], tuple(o["position"])
    proches = []
    for x in [*pnjs(monde), "joueur"]:
        if x == id or _cru(monde, id, x, "fiable") is not True or salle_crue(monde, id, x) != ici:
            continue
        p = _case_crue(monde, id, x)  # Là où il l'a vu : il le cherche des yeux en chemin.
        if p is not None:
            proches.append((max(abs(p[0] - depart[0]), abs(p[1] - depart[1])), x, p))
    if not proches or min(proches)[0] <= 1:
        return None
    _, _, p = min(proches)
    return _marcher(monde, id, lambda salle, case: salle == ici and max(abs(case[0] - p[0]), abs(case[1] - p[1])) == 1,
                    lignes)


def _case_crue(monde, id, x):
    """La case où il croit trouver ``x`` dans sa salle : là où il l'a vu. Une porte, un objet
    fixe font partie du lieu (``deliberation._lieu_cru``) : il sait leur place sans les avoir
    revus. None s'il ne sait où."""
    from .spatial import position_cible
    ici, o = monde.objets[id]["lieu"], monde.objets.get(x)
    fixe = o is not None and o["type"] != "personnage" and not o.get("mobile")
    cru = lire(monde, id)["croyances"].get(x, {}).get("lieu")
    if cru and (o is None or o["type"] != "porte"):  # Le joueur n'est pas un objet.
        if cru["valeur"] is None or cru.get("salle") != ici:
            return None
        if cru.get("case"):
            return tuple(cru["case"])
    if not fixe:
        return None
    p = position_cible(monde, x, ici)
    return tuple(p) if p is not None else None


def _a_portee_de(monde, salle, case, cible):
    """De ``case``, la main atteint-elle ``cible`` ? Comme ``spatial.proche`` : une case voisine,
    sans passer en biais entre deux obstacles."""
    from .spatial import _case_libre
    dx, dy = cible[0] - case[0], cible[1] - case[1]
    if max(abs(dx), abs(dy)) > 1:
        return False
    return not (dx and dy) or (_case_libre(monde, salle, (case[0] + dx, case[1]))
                               or _case_libre(monde, salle, (case[0], case[1] + dy)))


def _approcher(monde, id, etape, lignes):
    """Il marche vers ce que le geste touche, là où il le croit, jusqu'à l'avoir à portée de main ;
    sur place, le geste constate s'il y est. Renvoie la durée du pas, 0 s'il n'a plus à marcher,
    None s'il ne voit aucun chemin (``trajet``)."""
    o = monde.objets[id]
    loin = [x for x in _a_toucher(monde, id, etape) if not _accessible(monde, id, x)]
    if not loin:
        return 0
    crues = [_case_crue(monde, id, x) for x in loin]
    if None in crues:
        # Il le croit dans cette salle sans savoir où : il la parcourt des yeux. Ne le voyant
        # pas, c'est en essayant le geste qu'il constate son absence.
        croyances = lire(monde, id)["croyances"]
        if "orientation" in o and any(c is None and (croyances.get(x, {}).get("lieu") or {}).get("salle") == o["lieu"]
                                      for x, c in zip(loin, crues)):
            tour_d_horizon(monde, id)
            if None not in [_case_crue(monde, id, x) for x in loin]:
                return TOUR
        return 0
    ici = o["lieu"]
    arrivee = lambda salle, case: salle == ici and all(_a_portee_de(monde, salle, case, c) for c in crues)
    pas = _marcher(monde, id, arrivee, lignes)
    return _impasse(monde, id, etape, arrivee) if pas is None else pas


def _impasse(monde, id, etape, arrivee):
    """Aucun chemin en cases vers où il va : c'est un geste manqué. Il apprend ce qui le barre,
    les obstacles du chemin qu'ils coupent (le chemin par salles en tiendra compte), puis la
    stratégie tombe, le réflexe cesse, ou il patiente avant de renoncer. Renvoie None."""
    from .deliberation import PATIENCE, renoncer
    from .spatial import position_cible, trajet
    from .stratege import terminer
    o = monde.objets[id]
    occupees = occupants(monde, id)
    obstacles = [k for k, x in monde.objets.items()
                 if x.get("bloque_passage") and not x.get("incorpore") and x.get("lieu") in monde.data["salles"]]
    libre = trajet(monde, o["lieu"], tuple(o["position"]),
                   lambda salle, case: arrivee(salle, case) and (salle, case) not in occupees,
                   franchissable=lambda porte: _franchissable(monde, id, porte), solides=False)
    for salle, case, _, _ in libre or []:
        for k in obstacles:
            if monde.objets[k]["lieu"] == salle and position_cible(monde, k, salle) == case:
                croire(monde, id, k, "lieu", salle, "essai", salle=salle, case=list(case))
    e = esprit(monde, id)
    intention = e["intention"]
    if intention["motif"] == "alerte":
        e["intention"] = None
    elif intention["but"]["type"] == "strategie":
        terminer(monde, id, False, etape)
    else:
        intention["attente"] += 1
        if intention["attente"] > PATIENCE:
            renoncer(monde, id, monde.data["minutes"])
    return None


def _faire_face(monde, id, cible):
    """Il se tourne vers ce qu'il manipule ou vers celui à qui il parle ; renvoie la durée de la
    rotation."""
    from .spatial import QUART, orientation_vers, position_cible, quarts
    o = monde.objets[id]
    if cible == "joueur":
        p = tuple(monde.joueur["position"]) if monde.joueur["salle"] == o["lieu"] else None
    else:
        p = position_cible(monde, cible, o["lieu"]) if cible in monde.objets and not _porte(monde, cible, id) else None
    vers = orientation_vers(tuple(o["position"]), p) if p is not None and "position" in o else None
    if vers is None:
        return 0
    duree = QUART * quarts(o.get("orientation"), vers)
    o["orientation"] = vers
    return duree


def de_pres(monde, a, b):
    """Assez près pour s'entendre : même salle, à moins de ``ouie.PROCHE`` cases (ou sans cases, la
    même salle). ``b`` peut être le joueur."""
    from .ouie import PROCHE
    def place(x):
        if x == "joueur":
            return monde.joueur["salle"], monde.joueur.get("position")
        return monde.objets[x]["lieu"], monde.objets[x].get("position")
    (sa, pa), (sb, pb) = place(a), place(b)
    if sa != sb:
        return False
    if not monde.data.get("mode_cases") or pa is None or pb is None:
        return True
    return max(abs(pa[0] - pb[0]), abs(pa[1] - pb[1])) <= PROCHE


def pourraient_se_parler(monde, a, b):
    """Ils se voient, ou sont assez près pour s'entendre : il suffira de se tourner l'un vers l'autre."""
    return percoit(monde, a, b) and percoit(monde, b, a) or de_pres(monde, a, b)


def se_parler(monde, a, b):
    """Pour se parler, chacun se tourne vers l'autre s'il l'entend sans le voir ; vrai s'ils se
    voient alors (il faut y voir)."""
    if percoit(monde, a, b) and percoit(monde, b, a):
        return True
    if not monde.data.get("mode_cases") or not de_pres(monde, a, b):
        return False
    for x, y in ((a, b), (b, a)):
        if x != "joueur" and "position" in monde.objets[x]:
            _faire_face(monde, x, y)
            percevoir(monde, x)
    return percoit(monde, a, b) and percoit(monde, b, a)


def agir(monde, id, t, lignes, gestes=None):
    """Le geste qui commence à l'instant ``t`` (en dixièmes de seconde) selon l'intention
    courante ; renvoie sa durée. Sans le mode cases, un geste prend la minute, comme avant."""
    from .deliberation import PATIENCE, PROGRESSIFS, renoncer
    from .stratege import terminer
    reste = _jusqu_a_la_minute(t)
    en_cases = bool(monde.data.get("mode_cases"))
    e = esprit(monde, id)
    intention = e["intention"]
    if not intention:
        return reste
    etapes, o = intention["plan"], monde.objets[id]
    strategie = intention["but"]["type"] == "strategie"
    while etapes and etapes[0]["operation"] == "aller" and etapes[0]["lieu"] == o["lieu"]:
        etapes.pop(0)
    if not etapes:
        if intention["motif"] == "alerte":
            e["intention"] = None
        elif strategie:
            terminer(monde, id, True)
        return reste
    etape = etapes[0]
    operation = etape["operation"]
    en_place = en_cases and "position" in o
    if strategie and operation == "aller" and not en_place and chemin(monde, id, o["lieu"], etape["lieu"]) is None:
        terminer(monde, id, False, etape)  # Aucun passage qu'il croie ouvert : la stratégie tombe.
        return reste
    if en_place and operation == "aller":
        # Le seul juge du passage est le chemin en cases : sans chemin, c'est un geste manqué.
        lieu = etape["lieu"]
        arrivee = lambda salle, case: salle == lieu
        pas = _marcher(monde, id, arrivee, lignes)
        if pas is None:
            _impasse(monde, id, etape, arrivee)
        return pas or reste
    if en_place:
        # Il s'approche pas à pas de ce qu'il va toucher ; l'absence de témoin se juge sur place.
        pas = _approcher(monde, id, etape, lignes)
        if pas is None:
            return reste
        if pas:
            return pas
    if operation == "inspecter" and en_cases and "position" in o and o["lieu"] == etape["lieu"]:
        # Il gagne le centre de la salle pas à pas avant de la parcourir des yeux.
        centre = _centre(monde, id)
        if centre is not None and tuple(centre) != tuple(o["position"]):
            ici = o["lieu"]
            pas = _marcher(monde, id, lambda salle, case: salle == ici and tuple(case) == tuple(centre), lignes)
            if pas:
                return pas
    if operation == "abriter" and en_cases and o["lieu"] == etape["lieu"]:
        # S'abriter, c'est se tenir près de quelqu'un de sûr qu'il croit là, pas sur le seuil.
        pas = _rejoindre_un_proche(monde, id, lignes)
        if pas:
            return pas
    if etape["condition"] == "sans_temoin" and not desespere(monde, id):
        if en_cases and "orientation" in o:
            # Avant un geste qu'il veut sans témoin, il regarde tout autour de lui ; il n'agit
            # qu'au geste suivant, si personne ne l'a vu entre-temps. Son dernier tour d'horizon
            # est dans son esprit : il ne dépend pas du découpage des actions du joueur.
            ici = {"salle": o["lieu"], "case": list(o["position"])}
            dernier = e["balayage"]
            observe = None
            if not dernier or {k: dernier[k] for k in ici} != ici or t - dernier["instant"] > 2 * TOUR:
                e["balayage"] = {**ici, "instant": t}
                observe = bool(tour_d_horizon(monde, id))
                if not observe:
                    return TOUR
        else:
            observe = None
        if observe or (observe is None and temoins_crus(monde, id)):
            # Il guette une occasion jusqu'à la minute suivante.
            intention["attente"] += 1
            if intention["attente"] > PATIENCE:
                renoncer(monde, id, monde.data["minutes"])
            return reste
    # Il se tourne vers ce qu'il touche ou voit, jamais vers ce qu'il ignore.
    cible = etape["cible"]
    tourner = (_faire_face(monde, id, cible) if en_cases and cible and (
        cible in monde.objets and _accessible(monde, id, cible) or percoit(monde, id, cible)) else 0)
    fait = _executer(monde, id, etape, lignes, [] if gestes is None else gestes)
    if fait:
        etapes.pop(0)
        if intention["motif"] == "alerte" and not etapes:
            e["intention"] = None
        elif strategie and not etapes:
            terminer(monde, id, True)
    elif strategie and operation not in PROGRESSIFS:
        terminer(monde, id, False, etape)  # Un geste manqué, ou un refus : il n'insiste pas.
    if not en_cases or operation in DURABLES or operation == "aller" or not fait:
        # Un geste manqué ne se retente pas aussitôt : il reconsidère à la minute suivante.
        return reste
    return tourner + DUREES.get(operation, 20)


# --- Présences perçues par le joueur -------------------------------------------------------
# Pendant une action du joueur, les PNJ entrent dans son champ de vision et en sortent pas à
# pas. On n'en annonce que le bilan, à la fin de l'action : qui il voit désormais, qui il ne
# voit plus, qui il n'a fait qu'apercevoir. Entrer dans la pièce ou la quitter ne se dit que
# si le joueur a vu le passage ; sinon, il sait seulement qu'il voit, ou ne voit plus, quelqu'un.

def _ouvrir_presences(monde):
    from .spatial import vue_memorisee
    ici, suivi = monde.joueur["salle"], {}
    with vue_memorisee(monde):
        for id in pnjs(monde):
            visible, lieu = monde.visible(id), monde.objets[id]["lieu"]
            suivi[id] = {"debut": visible, "lieu": lieu, "vu": visible, "passage": None, "dernier": (visible, lieu, ici)}
    return suivi


def suivre_presences(monde):
    """Ouvre le bilan des présences d'une action du joueur, avant tout ce qu'elle change (son
    regard compris). ``bilan_presences`` le clôt ; entre-temps, ``pnj.avancer`` l'alimente."""
    monde._presences = _ouvrir_presences(monde)
    return monde._presences


def _observer_presences(monde, suivi):
    """Ce que le joueur voit à cet instant ; renvoie qui il voit. Entrer dans la salle du joueur
    ou la quitter est un passage perçu s'il le voit franchir le seuil : y être vu en entrant, ou
    y être vu juste avant d'en sortir. Un tel passage qu'il ne voit pas efface le précédent ;
    aller d'une autre salle à une autre n'y change rien."""
    from .spatial import etat_fige
    ici, vus = monde.joueur["salle"], {}
    with etat_fige(monde):  # Rien ne change pendant ce relevé : l'état n'est lu qu'une fois.
        perception = {id: monde.visible(id) for id in suivi if id in monde.objets}
    for id, s in suivi.items():
        if id not in monde.objets:
            continue
        visible, lieu = perception[id], monde.objets[id]["lieu"]
        avant_visible, avant_lieu, avant_ici = s["dernier"]
        if lieu != avant_lieu and lieu == ici:
            s["passage"] = "entree" if visible else None
        elif lieu != avant_lieu and avant_lieu == avant_ici:
            s["passage"] = "sortie" if avant_visible else None
        s["vu"] = s["vu"] or visible
        s["dernier"] = (visible, lieu, ici)
        vus[id] = visible
    return vus


def bilan_presences(monde, suivi=None):
    """Les lignes du bilan perçu depuis ``suivre_presences``, une par personnage concerné."""
    suivi = monde.__dict__.pop("_presences", None) if suivi is None else suivi
    if not suivi:
        return []
    from .spatial import vue_memorisee
    with vue_memorisee(monde):
        vus = _observer_presences(monde, suivi)
    piece = monde.data["salles"].get(monde.joueur["salle"], {})
    entre, quitte = ((" arrive.", " s'en va.") if piece.get("exterieur") else
                     (" entre dans la pièce.", " quitte la pièce."))
    lignes = []
    for id, visible in vus.items():
        s, o = suivi[id], monde.objets[id]
        nom = sujet(o)
        deplace = s["passage"] and o["lieu"] != s["lieu"]
        if visible and (not s["debut"] or deplace) and s["passage"] == "entree":
            lignes.append(nom + entre)
        elif visible and s["debut"] and deplace:
            lignes.append(nom + quitte)  # Il l'a vu sortir et le voit encore, au-delà du passage.
        elif visible and not s["debut"]:
            lignes.append("Tu aperçois " + ("" if o["lieu"] == monde.joueur["salle"] else "au-delà du passage ")
                          + designer(o) + ".")
        elif s["debut"] and not visible:
            lignes.append(nom + quitte if s["passage"] == "sortie" else "Tu ne vois plus " + designer(o) + ".")
        elif not visible and s["vu"]:
            lignes.append("Tu aperçois un instant " + designer(o) + ".")
    return lignes


def avancer(monde, minutes, lignes, dixiemes=None):
    """Fait vivre les PNJ pendant le temps qui vient de s'écouler (``minutes``, ou ``dixiemes``
    à la seconde près), jusqu'à l'heure courante ; renvoie ceux que le joueur a vus à un moment
    de cette période sans les voir à son début (une réponse à son appel, par exemple)."""
    from .spatial import vue_memorisee
    with vue_memorisee(monde):
        return _avancer(monde, minutes, lignes, dixiemes)


def _avancer(monde, minutes, lignes, dixiemes):
    """La vie des PNJ par événements : chacun commence un geste dès qu'il a fini le précédent ;
    à chaque minute franchie, le feu se consume et chacun délibère. On traite toujours ce qui
    arrive en premier ; quand rien ne bouge, on saute à l'événement suivant."""
    from .deliberation import appeler_a_l_aide, deliberer, menager_flamme
    from .eau import inonder
    from .perception import avancer_combustion
    from .social import bavarder
    from .temps import MINUTE
    fin_minutes, fin_dixiemes = monde.data["minutes"], monde.data.get("dixiemes", 0)
    fin = fin_minutes * MINUTE + fin_dixiemes
    debut = fin - (minutes * MINUTE if dixiemes is None else dixiemes)
    ids = pnjs(monde)
    # Le bilan des présences est celui de l'action du joueur, ouvert par le moteur ; appelée
    # seule, la vie des PNJ fait son propre bilan. Les apparus sont ceux que le joueur voit à un
    # moment de cette période sans les avoir vus à son début.
    suivi = getattr(monde, "_presences", None)
    propre = suivi is None
    if propre:
        suivi = _ouvrir_presences(monde)
    vus = _observer_presences(monde, suivi)
    apparus = []

    def observer():
        for id, visible in _observer_presences(monde, suivi).items():
            if visible and not vus.get(id) and id not in apparus:
                apparus.append(id)

    # Les gestes illicites en cours (``data["gestes_en_cours"]``, joueur compris) : quiconque voit
    # leur auteur avant qu'il ait fini en est témoin, même d'une action du joueur à l'autre.
    finir_gestes(monde, debut)
    # L'instant où chacun aura fini son geste est dans son esprit : un bruit qui le fait se
    # retourner le retarde (``ouie``).
    esprits_ = {id: esprit(monde, id) for id in ids}
    for e in esprits_.values():
        e["libre"] = max(debut, e["libre"])
    t = debut
    while True:
        frontiere = (t // MINUTE + 1) * MINUTE
        prochain = min((e["libre"] for e in esprits_.values()), default=fin + 1)
        if min(frontiere, prochain) > fin:
            break
        if frontiere <= prochain:
            t = frontiere
            monde.data["minutes"], monde.data["dixiemes"] = divmod(t, MINUTE)
            minute = monde.data["minutes"]
            avancer_combustion(monde, 1, lignes)
            inonder(monde, lignes)
            for id in ids:
                if monde.objets[id].get("profil"):
                    deliberer(monde, id, minute)
                    menager_flamme(monde, id, minute)
                    appeler_a_l_aide(monde, id, minute)
                    percevoir(monde, id)
            percevoir_tous(monde)  # Ce que la minute a changé (un feu, une flamme ménagée), tous le voient.
            continue
        t = prochain
        monde.data["minutes"], monde.data["dixiemes"] = divmod(t, MINUTE)
        for id in ids:
            if esprits_[id]["libre"] != t:
                continue
            # Son geste précédent est fini : ceux qui l'ont vu jusque-là s'en souviennent.
            finir_gestes(monde, t, id)
            intention = lire(monde, id)["intention"]
            # Désœuvré ou guettant une occasion, il a le temps de confier ce qu'il sait.
            if (not intention or intention["attente"] and temoins_crus(monde, id)) and bavarder(monde, id, lignes):
                duree = DUREES["dire"] if monde.data.get("mode_cases") else _jusqu_a_la_minute(t)
            elif intention:
                gestes = []
                duree = agir(monde, id, t, lignes, gestes)
                for _, operation, objet in gestes:
                    commencer_geste(monde, id, operation, objet, t + max(1, duree))
                # La perception suit l'événement : lui, et quiconque pouvait le voir faire (la vue
                # est en cache). Les croyances ne dépendent pas des instants où le joueur agit.
                percevoir_tous(monde)
                temoigner_en_cours(monde)
                observer()
            else:
                duree = _jusqu_a_la_minute(t)
            esprits_[id]["libre"] = t + max(1, duree)
    temoigner_en_cours(monde)
    monde.data["minutes"], monde.data["dixiemes"] = fin_minutes, fin_dixiemes
    observer()
    finir_gestes(monde, fin)  # Ceux qui durent encore attendent l'action suivante du joueur.
    if propre:
        lignes.extend(bilan_presences(monde, suivi))
    return apparus
