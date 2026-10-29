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
from .monde import ErreurMonde

from .esprits import (croire, esprit, lire, memoriser, percevoir, percevoir_tous, percoit, percus, pnjs,
                      reconsiderer)
from .francais import complement_de, de, designer, sujet
from .geometrie import cases, distance, placer, position_entree
from .relations import se_fie
from .spatial import VECTEURS

CHRONIQUE_MAX = 300
# Durées en dixièmes de seconde. Un pas d'une case ; les gestes ; ceux qui durent (se reposer,
# se chauffer, s'abriter) et l'attente d'une occasion vont jusqu'à la minute suivante, où il
# délibère de nouveau.
PAS = 15
DUREES = {"prendre": 20, "poser": 20, "ouvrir": 20, "fermer": 20, "deverrouiller": 50, "verrouiller": 50,
          "crocheter": 600, "frapper": 600, "manger": 600, "servir": 300, "alimenter": 100, "allumer": 100, "eteindre": 30,
          "inspecter": 100, "dire": 100, "demander": 100, "acheter": 100, "confier": 100, "remettre": 50,
          "demander_feu": 100, "proposer": 100, "ranimer": 100, "interposer": 100}
DURABLES = ("reposer", "chauffer", "abriter", "rester")
# deplacement : passer une salle, ouvrir une porte en chemin ; geste : agir sur un objet ;
# social : une parole entre PNJ ; decision : un plan choisi ou abandonné par un PNJ ; ouie : se
# retourner au bruit, retenir un bruit inconnu, aller le voir (``ouie``).
NATURES = ("lecture", "deplacement", "geste", "social", "reponse", "decision", "ouie", "compte", "relation", "violence")   # reponse : répondre à qui l'appelle ; compte : dettes et travaux payés
# Un geste touche sa cible, objet ou personne à qui l'on parle (``_a_toucher``), sauf ceux qui
# agissent à distance : se chauffer, c'est recevoir la chaleur du feu dans sa salle (``corps``).
A_DISTANCE = ("chauffer", "se_rendre", "degager", "fuite", "interposer")


def verifier(monde):
    from .ouie import INTENSITES
    # Le réflexe d'alerte est une donnée de l'ouïe commune (profil ``alerte``), plus un réflexe à part.
    assert not any(o["type"] == "personnage" and "reaction_son" in o for o in monde.objets.values()), \
        "Réflexe sonore d'une ancienne partie : le seuil d'alerte est dans le profil (alerte)"
    verifier_places(monde)
    gestes = monde.data.get("gestes_en_cours", [])
    personnages = {id for id, o in monde.objets.items() if o["type"] == "personnage"}
    assert isinstance(gestes, list) and all(
        isinstance(g, dict) and set(g) - {"issue", "porte"} == {"auteur", "operation", "objet", "fin", "nature", "temoins", "entendus",
                                           "se_sait_vu", "exclus"}
        and g["auteur"] in personnages | {"joueur"} and isinstance(g["operation"], str)
        and isinstance(g["objet"], str) and type(g["fin"]) is int and g["fin"] >= 0
        and (g["nature"] is None or g["nature"] in INTENSITES)
        and all(isinstance(g[k], list) for k in ("temoins", "entendus", "se_sait_vu", "exclus"))
        and set(g["se_sait_vu"]) <= set(g["temoins"])
        and set(g["temoins"]) | set(g["entendus"]) | set(g["exclus"]) <= personnages for g in gestes), \
        "Gestes en cours invalides"
    assert all("porte" not in g or g["operation"] == "enfermer" and
               monde.objets.get(g["porte"], {}).get("type") == "porte" for g in gestes), "Porte de contrainte invalide"
    captifs = monde.data.get("captivites_constatees", {})
    assert isinstance(captifs, dict) and all(a in personnages | set(monde.data.get("defunts", {})) and s in monde.data["salles"]
               for a, s in captifs.items()), "Captivité constatée invalide"
    assert all("issue" not in g or (g["operation"] in ("ligoter", "delier", "liberer", "tuer")
               and isinstance(g["issue"], dict) and set(g["issue"]) == {"outil", "lien"}
               and all(isinstance(v, str) for v in g["issue"].values())) or (g["operation"] == "trainer"
               and isinstance(g["issue"], dict) and set(g["issue"]) == {"outil", "depart", "victime"}
               and isinstance(g["issue"]["outil"], str)
               and all(isinstance(g["issue"][k], list) and len(g["issue"][k]) == 2
                       and isinstance(g["issue"][k][0], str)
                       and isinstance(g["issue"][k][1], list) and len(g["issue"][k][1]) == 2
                       and all(type(x) is int for x in g["issue"][k][1]) for k in ("depart", "victime"))) for g in gestes), "Issue de geste invalide"
    chronique = monde.data.get("chronique", [])
    assert (isinstance(chronique, list) and len(chronique) <= CHRONIQUE_MAX
            and all(isinstance(c, dict) and set(c) - {"nature", "instant", "relation", "cause", "bandes", "mefiance_levee", "service", "observation", "lecture", "jet", "marge", "observateur", "psy", "constat_confie", "avis_exprime", "changement_avis", "dispute", "eclat", "dispute_vue", "parti_pris"} == {"minute", "pnj", "texte"}
                    and c.get("nature", "geste") in NATURES and type(c.get("instant", 0)) is int
                    and type(c.get("constat_confie", False)) is bool
                    and type(c.get("avis_exprime", False)) is bool
                    and all(type(c.get(k, False)) is bool for k in ("dispute", "eclat", "dispute_vue", "parti_pris"))
                    and c.get("changement_avis") in (None, "dit")
                    for c in chronique)), "Chronique invalide"
    from .relations import verifier_chronique
    for c in chronique:
        if c.get("nature") == "relation":
            verifier_chronique(c)


def _etape(operation, cible="", outil="", lieu="", condition=""):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu, "condition": condition}


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


def chemin(monde, id, depart, arrivee, cles=(), ouvertes=(), precedents=None, portes=None, metrique=None):
    """Sorties à emprunter selon ce que le PNJ croit des portes et des obstacles ; None si aucun
    passage cru.

    Le PNJ tente toute porte, sauf celle qu'il sait verrouillée sans en porter (ou prévoir
    d'en porter) la clé, ni prévoir de la déverrouiller autrement (``ouvertes`` : crochetée par
    son plan) ; tout passage, sauf celui dont il croit un seuil barré ; et il ne passe pas par une
    salle qu'il a vue noyée. ``precedents`` : le parcours depuis ``depart`` (``parcours``), s'il
    est déjà fait.
    """
    precedent = parcours(monde, id, depart, cles, ouvertes, portes, metrique) if precedents is None else precedents
    if hasattr(precedent, "routes"):
        return precedent.routes.get(arrivee)
    if arrivee not in precedent:
        return None
    etapes = []
    while arrivee != depart:
        lieu, sortie = precedent[arrivee]
        etapes.append(sortie)
        arrivee = lieu
    return etapes[::-1]


def parcours(monde, id, depart, cles=(), ouvertes=(), portes=None, metrique=None):
    """Toutes les salles qu'il croit atteindre depuis ``depart`` (``chemin``) : {salle : (salle
    d'avant, sortie)}, en largeur, le départ à None."""
    from .presence import interieur
    monde = interieur(monde)
    from .eau import noyee_crue
    from .obstacles import metrique_necessaire, parcours_cru
    if metrique is None:
        metrique = metrique_necessaire(monde, id)
    if monde.data.get("mode_cases"):
        return parcours_cru(monde, id, depart, cles, ouvertes, portes, metrique=metrique)
    barrees = _cases_barrees_crues(monde, id) if monde.data.get("mode_cases") else set()
    precedent, file = {depart: None}, deque([depart])
    while file:
        lieu = file.popleft()
        for sortie in monde.data["salles"][lieu]["sorties"].values():
            vers, porte = sortie["vers"], sortie.get("porte")
            if (vers in precedent or vers not in monde.data["salles"] or noyee_crue(monde, id, vers)
                    or porte and porte not in ouvertes and _verrouillee_crue(monde, id, porte)
                    and _cle_portee(monde, id, porte, cles) is None
                    or barrees and _seuil_barre(monde, lieu, sortie, barrees)):
                continue
            precedent[vers] = (lieu, sortie)
            file.append(vers)
    return precedent


# --- Annonces et chronique ----------------------------------------------------------------

def _chroniquer(monde, id, texte, nature="geste"):
    chronique = monde.data.setdefault("chronique", [])
    from .temps import instant
    # L'instant (au dixième) départage ce qui arrive dans une même minute : un but choisi et quitté
    # entre deux minutes garde ses gestes (``recit_pnj``).
    chronique.append({"minute": monde.data["minutes"], "instant": instant(monde), "pnj": id, "texte": texte,
                      "nature": nature})
    del chronique[:-CHRONIQUE_MAX]


def _raconter(monde, id, verbe, objet, lignes, fin=""):
    """« X prend la trousse. » ; un verbe finissant par « de » prend le complément contracté ; ``fin``
    s'ajoute avant le point (« … sans forcer »)."""
    groupe = verbe[:-3] + " " + complement_de(objet) if verbe.endswith(" de") else verbe + " " + designer(objet)
    texte = designer(monde.objets[id], debut=True) + " " + groupe + fin + "."
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
    croyances = lire(monde, id)["croyances"]
    return [s for s in percus(monde, id)[0]
            if (s == "joueur" or monde.objets[s]["type"] == "personnage")
            and croyances.get(s, {}).get("etat", {}).get("valeur", {}).get("conscient") is not False]


def oreilles_crues(monde, id, nature):
    """Ceux qu'il croit, depuis peu, dans sa salle et assez près pour entendre un geste de cette
    ``nature`` (``ouie`` : la distance à la case où il les croit ; sans case, la salle entière) : ils
    sauraient sur quoi il porte (``_temoins_a_l_oreille``), il se croit entendu de chacun d'eux. Un
    geste qu'il veut sans témoin attend qu'ils s'éloignent, comme pour ceux qu'il voit."""
    from .esprits import RECENT
    from .ouie import INTENSITES, SEUIL, perte
    o = monde.objets[id]
    if nature is None or o["lieu"] not in monde.data["salles"]:
        return []
    ici, minute = o.get("position"), monde.data["minutes"]
    crus = []
    for x, a in lire(monde, id)["croyances"].items():
        c = a.get("lieu")
        if (x == id or a.get("etat", {}).get("valeur", {}).get("conscient") is False or not c or c["valeur"] != o["lieu"] or minute - c["minute"] > RECENT
                or not (x == "joueur" or monde.objets.get(x, {}).get("type") == "personnage")):
            continue
        if ici is None or not c.get("case") or INTENSITES[nature] - perte(ici, c["case"]) >= SEUIL:
            crus.append(x)
    return sorted(crus)


TOUR = 40              # dixièmes de seconde : un tour complet sur soi-même, huit fois 45°
CONTACT = 1            # case : au contact (une diagonale voisine comprise, ``geometrie.distance``)
# Gestes contre une personne (``objet`` : elle, joueur compris) : la victime est la personne,
# qui sait ce qu'elle a subi ; ceux qui voient faire en sont témoins comme d'un geste illicite.
CONTRAINTES = ("pousser", "frapper", "assommer", "saisir", "ligoter", "trainer", "enfermer", "tuer")


def est_contrainte(monde, operation, objet):
    return operation in CONTRAINTES and (objet == "joueur" or monde.objets.get(objet, {}).get("type") == "personnage")
# Gestes qui changent la place d'un objet : qui les voit faire voit où l'objet va.
DEPLACEMENTS = ("prendre", "poser")


def commencer_geste(monde, auteur, operation, objet, fin, exclus=(), nature=None):
    """Un geste illicite de ``auteur`` (un PNJ ou le joueur), en cours jusqu'à l'instant ``fin`` :
    il entre au registre commun, et ceux qui le voient faire en sont témoins dès maintenant, ceux
    qui l'entendent et savent sur quoi il porte, témoins par l'ouïe (``_temoins_a_l_oreille``).
    ``nature`` : le bruit qu'il fait tant qu'il dure (``ouie.nature`` ; par défaut, celui de son
    opération) ; ``exclus`` : ceux qui le regardaient déjà et dont le jet du joueur a tranché le
    sort ; ``se_sait_vu`` : les témoins que l'auteur a vus le regarder."""
    from .ouie import nature as nature_de
    geste = {"auteur": auteur, "operation": operation, "objet": objet, "fin": fin,
             "nature": nature or nature_de(operation), "temoins": [], "entendus": [],
             "se_sait_vu": [], "exclus": sorted(exclus)}
    monde.data.setdefault("gestes_en_cours", []).append(geste)
    _temoigner(monde, geste)
    return geste


def finir_gestes(monde, avant, auteur=None):
    """Les gestes achevés avant l'instant ``avant`` (ou à cet instant, pour un ``auteur`` qui en
    commence un autre) quittent le registre."""
    gestes = monde.data.get("gestes_en_cours")
    if gestes:
        termines = [g for g in gestes if (g["fin"] <= avant if "issue" in g else
                    g["fin"] < avant or g["auteur"] == auteur and g["fin"] <= avant)]
        gestes[:] = [g for g in gestes if g not in termines]
        from .tenir import finir
        for g in sorted(termines, key=lambda g: g["fin"]):
            if "issue" in g:
                finir(monde, g)


def temoigner_en_cours(monde):
    """Ceux qui voient maintenant l'auteur d'un geste illicite qu'il n'a pas fini en sont témoins."""
    from .temps import instant
    finir_gestes(monde, instant(monde))
    for geste in monde.data.get("gestes_en_cours", []):
        if ((geste["objet"] in monde.objets or geste["objet"] == "joueur")
                and (geste["auteur"] == "joueur" or geste["auteur"] in monde.objets)):
            _temoigner(monde, geste)


def tour_d_horizon(monde, id):
    """Il regarde tout autour de lui, le temps d'un tour complet : ce qu'il voit devient croyance.
    Renvoie ceux par qui il se croit observé ; il reprend ensuite son orientation."""
    o = monde.objets[id]
    orientation = o.pop("orientation", None)
    # Ce qu'il voit en regardant autour de lui sert la décision en cours : son propre regard ne
    # l'éveille pas (``esprits.reconsiderer``), et ce qu'il garde « en vue » reste son regard ordinaire.
    e = esprit(monde, id)
    en_vue, eveil = e["en_vue"], e["eveil"]
    try:
        percevoir(monde, id)
        temoigner_en_cours(monde)
        return temoins_crus(monde, id)
    finally:
        if orientation is not None:
            o["orientation"] = orientation
        e["en_vue"], e["eveil"] = en_vue, eveil


def _temoigner(monde, geste):
    """Les PNJ qui perçoivent réellement l'auteur d'un geste illicite en cours s'en souviennent.

    Appelé tant que le geste dure, il compte aussi ceux qui arrivent ou se retournent
    entre-temps ; chacun n'en est témoin qu'une fois (``geste["temoins"]``).
    """
    from .vol import proprietaire
    id, operation, objet = geste["auteur"], geste["operation"], geste["objet"]
    if operation in ("delier", "liberer") or (operation == "trainer" and not est_contrainte(monde, operation, objet)):
        return
    victime = objet if est_contrainte(monde, operation, objet) else proprietaire(monde, monde.objets[objet])
    souvenir = {"type": "vu_agir", "auteur": id, "operation": operation, "objet": objet, "victime": victime,
                "preuve": f"geste:{id}:{operation}:{objet}:{geste['fin']}"}
    from .spatial import etat_fige
    with etat_fige(monde):  # Les témoins ne révisent que leur esprit.
        _temoins(monde, geste, souvenir, victime)
        if operation != "pousser":  # La violence entendue suit le même contrat d’attribution.
            _temoins_a_l_oreille(monde, geste, souvenir, victime)


def _temoins(monde, geste, souvenir, victime):
    from .biens import lese_par
    from .deliberation import proteges
    from .deliberation import VOL, inquieter, relancer
    id = geste["auteur"]
    for autre in pnjs(monde):
        if autre != id and autre not in geste["temoins"] and autre not in geste["exclus"] and percoit(monde, autre, id):
            if not est_contrainte(monde, geste['operation'], geste['objet']):
                victime = lese_par(monde, geste['objet'], autre, geste['operation'])
                souvenir = {**souvenir, 'victime': victime}
            geste["temoins"].append(autre)
            if geste["operation"] in ("frapper", "assommer", "tuer") and est_contrainte(monde, geste["operation"], geste["objet"]):
                from .corps import evenement
                evenement(monde, "violence_vue", geste["objet"], auteur=id, temoin=autre)
            lieu = _lieu_vu(monde, autre, geste)
            memoriser(monde, autre, {**souvenir, **({"lieu": lieu} if lieu else {})})
            if lieu:
                from .esprits import reviser
                reviser(monde, autre, geste["objet"], "lieu", lieu["valeur"], "vu",
                        salle=lieu["salle"], case=lieu["case"])
            inquieter(monde, autre, "violence" if geste["operation"] != "pousser" and est_contrainte(monde, geste["operation"], geste["objet"]) else "illicite")
            reconsiderer(monde, autre)  # Un geste illicite sous ses yeux change sa situation.
            if est_contrainte(monde, geste["operation"], geste["objet"]):
                continue  # La victime l'a subi (``passage.subir``) ; ses biens ne sont pas en cause.
            if autre == victime:
                relancer(monde, autre, "biens", VOL)
            elif victime in proteges(monde, autre):
                # Un protégé atteint : son devoir est touché, il ira le prévenir.
                from .deliberation import ATTEINTE
                relancer(monde, autre, "devoir", ATTEINTE)
                memoriser(monde, autre, {"type": "a_prevenir", "victime": victime, "auteur": id, "preuve": souvenir["preuve"]})
    # L'auteur peut remarquer un témoin après le début du geste. Seuls ceux
    # qu'il voit lui-même entrent dans son souvenir, conservé après le geste.
    for autre in geste["temoins"]:
        if autre not in geste["se_sait_vu"] and (monde.visible(autre) if id == "joueur" else percoit(monde, id, autre)):
            geste["se_sait_vu"].append(autre)
            if id != "joueur":
                memoriser(monde, id, {"type": "se_sait_vu", "par": autre,
                                      "objet": geste["objet"], "operation": geste["operation"]})


def _temoins_a_l_oreille(monde, geste, souvenir, victime):
    from .deliberation import proteges
    from .biens import lese_par
    """Témoins par l'ouïe, d'une certitude moindre que la vue : qui entend le geste pendant qu'il
    dure (``ouie.entend`` : sa nature, la distance, son seuil), sans en voir l'auteur, dans la salle
    même (il le situe), et croit tout près de là l'objet en cause ou ce qui le contient
    (``ouie.objet_situe``) : il sait qu'on y touche. Il n'identifie l'auteur que s'il le reconnaît :
    il le croit là d'où vient le bruit (``ouie._crus_la`` : vu ou entendu depuis peu, ses pas ou sa
    voix). Identifié, il en est témoin comme d'un geste vu (``vu_agir`` marqué ``par`` « ouie », sans
    le lieu où va l'objet), et sa méfiance ne vaut que ce que vaut l'ouïe ; sinon il sait seulement
    que quelqu'un touche à ce bien (``entendu_agir``) : la victime s'en émeut comme d'un vol découvert,
    et le bruit, qu'il situe, reste à aller voir (``ouie._bruit_inconnu``) ; tant que ce bruit dure, il ne
    lui apprend rien de plus. Chacun ne l'est qu'une fois par geste."""
    from .deliberation import ATTEINTE, VOL, inquieter, relancer
    from .esprits import RECENT
    from .ouie import _crus_la, _place, entend, objet_situe
    from .social import GESTES, _qui
    id, objet = geste["auteur"], geste["objet"]
    if geste["nature"] is None or objet not in monde.objets:
        return
    salle, case = _place(monde, id)
    for autre in pnjs(monde):
        o = monde.objets[autre]
        if (autre == id or autre == victime and est_contrainte(monde, geste["operation"], objet) or autre in geste["temoins"] or autre in geste["entendus"] or autre in geste["exclus"]
                or not o.get("profil") or o["lieu"] != salle or percoit(monde, autre, id)
                or entend(monde, id, autre, force=geste["nature"]) is None
                or not objet_situe(monde, autre, objet, salle, case)):
            continue
        geste["entendus"].append(autre)
        if not est_contrainte(monde, geste['operation'], objet):
            victime = lese_par(monde, objet, autre, geste['operation'])
            souvenir = {**souvenir, 'victime': victime}
        if est_contrainte(monde, geste["operation"], objet):
            from .corps import evenement
            evenement(monde, "violence_entendue", objet, auteur=id, temoin=autre)
        reconnu = id in _crus_la(monde, autre, salle, case)
        if not reconnu:
            # Quelqu'un touche encore à ce bien, il le sait déjà : rien de nouveau, sinon que ça dure.
            deja = next((x for x in reversed(esprit(monde, autre)["memoire"]) if x["type"] == "entendu_agir"
                         and x["objet"] == objet and monde.data["minutes"] - x["minute"] <= RECENT), None)
            if deja is not None:
                deja["minute"] = monde.data["minutes"]
                continue
        inquieter(monde, autre, "illicite")
        verbe = GESTES.get(geste["operation"], "a touché à")
        quoi = (verbe[:-3] + " " + complement_de(monde.objets[objet]) if verbe.endswith(" de")
                else verbe + " " + designer(monde.objets[objet]))
        if reconnu:
            memoriser(monde, autre, {**souvenir, "par": "ouie"})
            _chroniquer(monde, autre, f"{_qui(monde, autre)} entend {_que(_qui(monde, id))} {quoi}.", "ouie")
        else:
            memoriser(monde, autre, {"type": "entendu_agir", "operation": geste["operation"], "objet": objet})
            _chroniquer(monde, autre, f"{_qui(monde, autre)} entend que quelqu'un {quoi}.", "ouie")
        if autre == victime:
            relancer(monde, autre, "biens", VOL)
        elif reconnu and victime in proteges(monde, autre):
            relancer(monde, autre, "devoir", ATTEINTE)
            memoriser(monde, autre, {"type": "a_prevenir", "victime": victime, "auteur": id, "preuve": souvenir["preuve"]})


def _que(nom):
    from .monde import normaliser
    return ("qu'" if normaliser(nom)[:1] in "aeiouyh" else "que ") + nom


def _lieu_vu(monde, temoin, geste):
    """Où le témoin d'un geste qui déplace un objet le voit aller : {valeur, salle, case}, comme
    une croyance de lieu, et la minute où il l'a vu ; dans les mains de l'auteur, il le sait porté
    sans voir l'objet. None pour un autre geste, ou s'il ne voit pas où l'objet est allé."""
    objet = geste["objet"]
    o = monde.objets.get(objet)
    if geste["operation"] not in DEPLACEMENTS or not o or o["type"] == "personnage":
        return None
    from .esprits import _porteur
    vus = percus(monde, temoin)[0]
    if _porteur(monde, o) == geste["auteur"]:
        return {"valeur": geste["auteur"], "salle": None, "case": None, "minute": monde.data["minutes"]}
    if objet in vus and vus[objet][0] is not None:
        salle, case = vus[objet]
        return {"valeur": o["lieu"], "salle": salle, "case": case, "minute": monde.data["minutes"]}
    return None


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
    if sauf != "joueur" and not j.get("parti") and j.get("position") is not None:
        places[j["salle"], tuple(j["position"])] = "joueur"
    for k, o in monde.objets.items():
        if (o["type"] == "personnage" and not o.get("parti") and k != sauf and o.get("lieu") in monde.data["salles"]
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
    places = [] if monde.joueur.get("parti") else [("joueur", (monde.joueur["salle"], tuple(monde.joueur["position"])))]
    places += [(k, (o["lieu"], tuple(o["position"]))) for k, o in monde.objets.items()
               if o["type"] == "personnage" and not o.get("parti") and o.get("lieu") in monde.data["salles"] and o.get("position") is not None]
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
            placer(o, o["lieu"], list(min(libres, key=lambda c: (distance(c, (x, y)), tuple(c)))))


def _centre(monde, id):
    """La case libre la plus proche du centre de sa salle, d'où la parcourir des yeux."""
    from .spatial import _case_libre
    o = monde.objets[id]
    sol = cases(monde.data["salles"][o["lieu"]])
    cx, cy = sum(x for x, _ in sol) / len(sol), sum(y for _, y in sol) / len(sol)
    libres = [c for c in sol if tuple(c) == tuple(o["position"])
              or _case_libre(monde, o["lieu"], c) and not _occupee(monde, id, o["lieu"], c)]
    return min(libres, key=lambda c: ((c[0] - cx) ** 2 + (c[1] - cy) ** 2, tuple(c))) if libres else None


def _a_portee_de_vue(monde, id, case):
    """La case de sa salle est au contact, ou il la verrait en se tournant (la lumière qui l'éclaire,
    rien qui s'interpose)."""
    from .spatial import _alentour, _memo_vue, _vue
    o = monde.objets[id]
    if distance(o["position"], case) <= CONTACT:
        return True
    origine, lumiere = _vue(monde, id, _memo_vue(monde))
    return any(c == (o["lieu"], *case) for c, _ in _alentour(monde, origine, lumiere))


def _inspecter(monde, id, cherche=None, lignes=None, vers=None):
    """Depuis le centre de la salle (où il a marché), ou d'où il voit l'endroit d'où venait un bruit
    (``vers``), il la parcourt des yeux. S'il y cherche quelqu'un (``cherche``) qu'il ne sait pas là
    (``croit_present`` : il ne l'a pas vu en parcourant la salle des yeux), il l'appelle (``appeler``)."""
    from .ouie import parcouru
    o = monde.objets[id]
    if cherche:
        # Le tour d'horizon peut remplacer le point de départ cru par une absence.
        # L'examen utilise cet indice : le retenir avant de réviser la croyance.
        from .deliberation import consommer_indices_recherche
        consommer_indices_recherche(monde, id, cherche, o["lieu"])
    esprit(monde, id)["visites"][o["lieu"]] = monde.data["minutes"]
    if "orientation" in o:
        tour_d_horizon(monde, id)  # Il parcourt la salle des yeux, tout autour de lui.
    if cherche and (cherche == "joueur" or cherche in monde.objets) and not croit_present(monde, id, cherche):
        from .deliberation import appels_vains
        if o["lieu"] not in appels_vains(monde, id, cherche):
            appeler(monde, id, cherche, [] if lignes is None else lignes)
        if not croit_present(monde, id, cherche):
            from .deliberation import recherche_vaine
            recherche_vaine(monde, id, cherche, o["lieu"])
    bruit = parcouru(monde, id, o["lieu"], vers)
    if bruit:
        from .social import _qui
        _chroniquer(monde, id, f"{_qui(monde, id)} va voir {'de près ' if vers is not None else ''}d'où venait le bruit : "
                               f"{monde.data['salles'][o['lieu']]['nom']}.", "ouie")
    # Une ronde accomplie, un bruit allé voir rassurent : le lieu est tel qu'il doit être.
    if bruit or any(x["condition"].get("lieu") == o["lieu"] and "periode" in x["condition"]
                                for x in (o.get("profil") or {}).get("pulsions", [])):
        from .deliberation import inquieter
        inquieter(monde, id, "ronde", -1)


def appeler(monde, id, qui, lignes):
    """Il cherche ``qui`` sans le voir : il le hèle par son nom. Héler est un cri (``ouie``, nature
    « hele ») : il porte comme un appel, à travers une porte fermée. Un PNJ qui en saisit les mots
    (``ouie.saisit``) sait qu'on le cherche, et d'où : il répond, de la même voix, sauf à une voix
    dont il se méfie (``relations.percue``). Répondre à son nom, c'est se nommer : l'appelant qui
    saisit la réponse croit ``qui`` là d'où elle vient, sûr de lui s'il connaît sa voix, sur sa
    parole sinon (``voix.se_nommer``) ; qui la surprend l'apprend de même. Un appel resté sans
    réponse est retenu (``appel_sans_reponse``) : la salle compte pour parcourue dans cette
    recherche (``deliberation.appels_vains``), il n'y rappelle pas. Qui répond convient avec
    l'appelant de qui vient à qui (``appel`` : « J'arrive ! », « Ici, viens ! », « Qu'est-ce que tu
    veux ? »). Le joueur appelé entend l'appel (``ecoute``) et répond, s'il le veut, par les mêmes
    paroles (``sons``)."""
    from .appel import repondre
    from .corps import conscient
    if not conscient(monde, id):
        return False
    heler(monde, id, qui, lignes)
    repondre(monde, id, qui, lignes)


def heler(monde, id, qui, lignes):
    """``id`` (un PNJ ou le joueur) hèle ``qui`` par son nom : un cri (``ouie``, nature « hele »)."""
    from .corps import conscient
    if not conscient(monde, id):
        return False
    from .ouie import retentir
    from .social import _qui
    a, b = _qui(monde, id), _qui(monde, qui, id)
    texte = f"{a} appelle : « {b} ? »"
    _chroniquer(monde, id, texte, "social")
    if id == "joueur":
        lignes.append(f"Tu appelles : « {b} ? »")
    elif monde.visible(id):
        lignes.append(texte)
    retentir(monde, id, "heler", texte=texte, cites=[qui], vers=[qui])


def _accessible(monde, id, objet):
    """L'objet est-il à portée de main du PNJ, là où il se tient, hors de tout contenant fermé et
    des mains d'autrui ? Il ne se déplace pas pour le vérifier : c'est sa marche qui l'en approche
    (``agir``)."""
    from .spatial import proche
    if objet == "joueur":
        from .passage import au_contact
        return au_contact(monde, id, objet)
    if _porte(monde, objet, id):
        return True
    from .esprits import _porteur
    porteur = _porteur(monde, monde.objets[objet])
    if porteur is not None:
        from .corps import sans_defense
        from .passage import au_contact
        return (sans_defense(monde, porteur) and au_contact(monde, id, porteur)
                and proche(monde, objet, id))
    o = monde.objets[id]
    if monde.data.get("mode_cases") and "position" in o:
        return proche(monde, objet, id)
    return monde.present_physique(objet, salle=o["lieu"])


def _a_toucher(monde, id, etape, portes=None):
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
        if x == "joueur" and op in ("frapper", "assommer", "dans_le_dos", "rester"):
            touches.append(x)
            continue
        if x not in monde.objets or (x in portes if portes is not None else _porte(monde, x, id)):
            continue
        if role == "outil" and (op in SOCIALES or monde.objets[x].get("mobile")):
            continue
        touches.append(x)
    return touches


def _a_reunir(monde, id, etape, portes=None, *, venues=False, contacts=True):
    """Présences nécessaires au geste, distinctes de sa portée de contact.

    Le bénéficiaire d'une part peut être appelé dans la salle sans être
    touché. Il reste un participant requis, même si la cible est le repas.
    ``venues`` tient compte du contrat de venue au lieu du service dans
    l'admission du plan. Il ne prouve pas une présence réelle : le geste
    contrôle encore celle-ci avant de servir. ``contacts=False`` conserve
    l'observation des cibles de contact par l'exécution ordinaire.
    """
    requis = _a_toucher(monde, id, etape, portes) if contacts else []
    if etape["operation"] == "servir":
        pour = etape.get("contenu", {}).get("pour")
        # Une part demandée se prend au lieu des vivres : le demandeur
        # convient d'y venir. Une pulsion de nourrir autrui ne vaut pas accord.
        # L'engagement provisoire du devis porte déjà ce même contrat.
        from . import agendas
        convenue = venues and any(
            x.get("objet") == etape["cible"] and x.get("pour") == pour
            and x["condition"] == {"objet": etape["cible"], "servir": pour}
            and not x.get("annule") for x in agendas.en_cours(monde, id))
        if not convenue:
            requis.append(pour)
    return requis


def _pas(monde, id, sortie, lignes):
    """Un geste d'une minute vers la sortie : ouvrir, déverrouiller, essayer ou passer."""
    actuelles = monde.data["salles"][monde.objets[id]["lieu"]]["sorties"].values()
    if sortie.get("exterieur") is True or not any(
            s.get("exterieur") is not True and all(sortie.get(k) == valeur for k, valeur in s.items())
            for s in actuelles):
        return
    from .tenir import autoriser, lacher
    from .monde import ErreurMonde
    try:
        autoriser(monde, id, "aller")
    except ErreurMonde:
        return
    lacher(monde, id, "aller")
    o = monde.objets[id]
    porte = monde.objets.get(sortie.get("porte") or "")
    if porte and not porte.get("ouverte"):
        _au_seuil(monde, o, sortie)
        if porte.get("verrouillee"):
            cle = _cle_portee(monde, id, porte["id"])
            if cle is None:
                croire(monde, id, porte["id"], "verrouillee", True, "essai")
                from .tenir import constater_enfermement
                constater_enfermement(monde, id)
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
    if attribut == "verrouillee" and valeur is True:
        from .tenir import constater_enfermement
        constater_enfermement(monde, id)
    return False


def _contenant_rencontre(monde, id, objet):
    """Le contenant fermé, à portée de sa main, où il croit l'objet (directement ou plus loin dans
    ce qu'il croit le contenir) : c'est lui que sa main rencontre ; None s'il n'y en a pas."""
    from .deliberation import _lieu_cru
    vus, lieu = {objet}, _lieu_cru(monde, id, objet)
    while lieu in monde.objets and lieu not in vus and monde.objets[lieu]["type"] == "contenant":
        vus.add(lieu)
        c = monde.objets[lieu]
        if not c.get("ouverte") and _accessible(monde, id, lieu):
            return lieu
        lieu = _lieu_cru(monde, id, lieu)
    return None


def _hors_d_atteinte(monde, id, objet):
    """Il ne peut toucher ce qu'il visait : il constate ce que sa main rencontre. Le contenant
    fermé où il le croyait (il l'a essayé : il sait s'il est verrouillé) ; l'objet reste cru
    dedans, rien ne lui montre qu'il n'y est plus. Sinon, l'objet n'est pas là où il le croyait.
    Renvoie False : le geste est manqué."""
    from .esprits import constater, reviser
    contenant = _contenant_rencontre(monde, id, objet)
    if contenant is None:
        return _rate(monde, id, objet)
    constater(monde, id, contenant, "essai")
    reviser(monde, id, contenant, "verrouillee", bool(monde.objets[contenant].get("verrouillee")), "essai")
    return False


def seuil_crochetage(lumiere):
    """Ce que doit atteindre d20 + DEX pour crocheter une serrure : 14 en pleine lumière, 4 de
    plus par niveau qui manque. Le jet (``_crocheter``) et la chance que le PNJ s'y croit
    (``planification.chance_crochetage``) en partent tous deux."""
    return 14 + 4 * (2 - lumiere)


def lumiere_du_geste(monde, id):
    """La lumière qu'il a sur sa case, ce qu'il porte compris : celle du jet d'un geste qui demande
    d'y voir (``_crocheter``)."""
    from .perception import eclairage
    o = monde.objets[id]
    return eclairage(monde, o["lieu"], o.get("position") if monde.data.get("mode_cases") else None)["niveau"]


def _crocheter(monde, id, cible, outil):
    """Le jet : (réussi, de combien il passe le seuil ; None s'il le manque). La marge fait le bruit
    du geste (``ouie.nature_crochetage``)."""
    from .caractere import modificateur
    from .esprits import constater_lumiere_devant
    marge = monde.d20() + modificateur(monde, id, "DEX") - seuil_crochetage(lumiere_du_geste(monde, id))
    if marge >= 0:
        return True, marge
    # La serrure résiste : il constate la lumière dont il disposait là, celle qui fait sa chance.
    constater_lumiere_devant(monde, id, cible)
    return False, None


def _forcer(monde, id, cible, outil, lignes):
    """Un coup, par la règle du joueur (``force``) : d20 + FOR + bonus de l'outil contre ``force.DD``,
    un 1 abîme l'outil ; réussi, la cible perd la puissance de l'outil et la FOR qui aide. Renvoie
    True quand elle est brisée (``force.briser`` : ouverte, ce qu'elle contenait au sol)."""
    from . import force
    from .caractere import modificateur
    c, t = monde.objets[cible], monde.objets.get(outil)
    if not (force.adapte(c, t) or not outil and c["type"] == "porte") or t is not None and not t.get("integrite"):
        return _rate(monde, id, outil, "etat", {"disponible": False})
    jet = monde.d20()
    if jet == 1 or jet + modificateur(monde, id, "FOR") + force.bonus(t) < force.DD:
        if jet == 1 and t is not None:
            t["integrite"] = max(0, t["integrite"] - 1)
        _raconter(monde, id, "frappe en vain", c, lignes)
        return False
    c["integrite"] = max(0, c["integrite"] - force.degats(monde, id, t))
    if c["integrite"] > 0:
        _raconter(monde, id, "frappe", c, lignes)
        return False
    tombes = force.briser(monde, cible, monde.objets[id]["lieu"])
    _raconter(monde, id, "force", c, lignes)
    for objet in tombes:
        from .esprits import constater
        constater(monde, id, objet, "vu")
    return True


def _assez_de_lumiere(monde, id, etape):
    """Avant un geste dont la chance tient à la lumière (``A_VUE``), il la constate là où il
    l'accomplit, et la retient de ce qu'il touche (``esprits.constater_lumiere_devant``). Si elle
    rend le geste impossible, ou moindre que celle sur laquelle son plan comptait (l'étape la
    porte), il n'essaie pas : il reconsidère à la minute suivante, sur ce qu'il vient de voir."""
    from .deliberation import A_VUE
    from .esprits import constater_lumiere_devant
    from .planification import chance_crochetage
    if etape["operation"] not in A_VUE:
        return True
    lumiere = lumiere_du_geste(monde, id)
    prevue = etape.get("contenu", {}).get("lumiere")
    if chance_crochetage(monde, id, lumiere) > 0 and (prevue is None or lumiere >= prevue):
        return True
    constater_lumiere_devant(monde, id, etape["cible"])
    cible = monde.objets.get(etape["cible"])
    _chroniquer(monde, id, f"{designer(monde.objets[id], debut=True)} renonce à crocheter "
                + (designer(cible) if cible else "la serrure") + " : trop sombre, là.", "decision")
    return False


def _executer(monde, id, etape, lignes, gestes):
    from .tenir import autoriser, lacher
    from .monde import ErreurMonde
    try:
        autoriser(monde, id, etape["operation"])
    except ErreurMonde:
        return False
    lacher(monde, id, etape["operation"])
    from . import services
    avant = services.preparer(monde, id, etape['cible'], etape['operation'])
    from .esprits import constats_geste
    with constats_geste(monde, id, etape['cible'], etape['outil']):
        fait = _executer_effet(monde, id, etape, lignes, gestes)
    if fait:
        services.constater(monde, id, etape['cible'], avant)
    return fait


def _executer_effet(monde, id, etape, lignes, gestes):
    """Accomplit une étape ; renvoie True si elle est terminée, False si elle est manquée, None
    pour un geste qui dure et se poursuit (``DURABLES``)."""
    from .deliberation import SATIETE, changer_etat, illicite
    from .deplacement_objet import deplacer
    o = monde.objets[id]
    op, cible, outil = etape["operation"], etape["cible"], etape["outil"]
    if op == "interposer":
        from .defense import avertir_acces
        return avertir_acces(monde, id, etape, lignes)
    if op == "tuer":
        from .tenir import commencer
        from .monde import ErreurMonde
        try:
            commencer(monde, id, op, cible, outil, lignes)
        except ErreurMonde:
            return False
        return True
    if op == "aller":
        route = chemin(monde, id, o["lieu"], etape["lieu"])
        if route:
            _pas(monde, id, route[0], lignes)
        return o["lieu"] == etape["lieu"]
    if op == "inspecter":
        if o["lieu"] != etape["lieu"]:
            return False
        contenu = etape.get("contenu", {})
        _inspecter(monde, id, contenu.get("cherche"), lignes, contenu.get("vers"))
        intention = lire(monde, id)["intention"]
        if intention and intention["but"]["type"] == "proteger":
            secourus = []
            for s in lire(monde, id)["memoire"]:
                if s["type"] == "secours" and s["salle"] == o["lieu"] and not s.get("examine"):
                    s["examine"] = True
                    secourus.append(s["qui"])
            if secourus:
                from .corps import evenement
                evenement(monde, "intervention", id, proteges=sorted(set(secourus)))
        return True
    if op == "reposer":
        return _reposer(monde, id, lignes)
    if op == "abriter":
        return _abriter(monde, id, etape["lieu"], lignes)
    if op == "rester":
        if not _accessible(monde, id, etape["cible"]):
            return False
        e = esprit(monde, id)
        depuis = e["intention"]["depuis"] if e["intention"] else monde.data["minutes"]
        if not any(s["type"] == "compagnie" and s.get("qui") == etape["cible"]
                   and s["minute"] >= depuis for s in e["memoire"]):
            # La présence est revalidée avant toute affirmation de proximité.
            memoriser(monde, id, {"type": "compagnie", "qui": etape["cible"]})
            from .social import _qui
            texte = f"{_qui(monde, id)} reste près {de(_qui(monde, etape['cible']))}."
            _chroniquer(monde, id, texte)
            if monde.visible(id) and (etape["cible"] == "joueur" or monde.visible(etape["cible"])):
                lignes.append(texte)
        return None  # La raison du séjour est revalidée par le choix commun.
    from .deliberation import SOCIALES
    if op in SOCIALES:
        from .echanges import executer
        return executer(monde, id, etape, lignes)
    if op == "dans_le_dos":
        return True
    if op in ("se_rendre", "degager", "fuite"):
        from .defense import executer
        from .monde import ErreurMonde
        try:
            return executer(monde, id, etape, lignes)
        except ErreurMonde:
            return False
    if op == "assommer" or op == "frapper" and (cible == "joueur" or monde.objets.get(cible, {}).get("type") == "personnage"):
        from .combat import frapper, voit
        from .monde import ErreurMonde
        if etape["condition"] == "dans_le_dos" and voit(monde, cible, id):
            return False
        if (etape.get("contenu") or {}).get("defense"):
            from .defense import dangers, protection
            aide = protection(monde, id)
            if cible not in dangers(monde, id) and not (aide and cible in aide[2]):
                return False
            from .corps import conscient
            if not conscient(monde, cible):
                return False
            from .corps import evenement
            evenement(monde, "intervention" if aide and cible in aide[2] else "riposte", id, contre=cible)
        try:
            frapper(monde, id, cible, outil, "assommer" if op == "assommer" else "simple", lignes)
        except ErreurMonde:
            return False
        return True
    c = monde.objets.get(cible)
    if c is None:
        return False
    if op == "ranimer":
        from .corps import ranimer
        from .monde import ErreurMonde
        try:
            ranimer(monde, id, cible)
        except ErreurMonde:
            return False
        _raconter(monde, id, "ranime", c, lignes)
        return True
    if op == "chauffer":
        return _chauffer(monde, id, cible, lignes)
    for objet in _a_toucher(monde, id, etape):
        if not _accessible(monde, id, objet):
            return _hors_d_atteinte(monde, id, objet)
    if outil and not _porte(monde, outil, id) and monde.objets.get(outil, {}).get("mobile", True):
        return _rate(monde, id, outil)  # Un outil mobile s'emploie en main.
    # Il y porte la main : le geste retentit, réussi ou non ; feutré s'il le veut sans témoin. Un
    # crochetage sonne selon son adresse : le jet se fait d'abord (``ouie.nature_crochetage``).
    from .ouie import nature as nature_de, nature_crochetage, retentir
    discret = etape["condition"] == "sans_temoin"
    jet = _crocheter(monde, id, cible, outil) if op == "crocheter" and c.get("verrouillee") else None
    # Le bruit qu'il fait tant que dure son geste (``commencer_geste``).
    bruit = nature_crochetage(jet[1], discret) if jet else nature_de(op, discret)
    retentir(monde, id, op, discret=discret, force=bruit if jet else None)
    faute = illicite(monde, id, cible, op)
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
        changer_etat(monde, id, cible, "ouverte", False)
        _raconter(monde, id, "ouvre", c, lignes)
        _ouvert_par_soi(monde, id, cible)
    elif op == "fermer":
        from .portes import valider_fermeture
        from .monde import ErreurMonde
        try:
            valider_fermeture(monde, cible)
        except ErreurMonde:
            from .esprits import constater
            constater(monde, id, cible, "essai")
            return False
        avant, c["ouverte"] = c.get("ouverte"), False
        changer_etat(monde, id, cible, "ouverte", avant)
        _raconter(monde, id, "ferme", c, lignes)
    elif op in ("deverrouiller", "verrouiller"):
        if op == "verrouiller":
            from .tenir import valider_verrouillage, enfermer
            from .monde import ErreurMonde
            try:
                valider_verrouillage(monde, id, cible, outil)
            except ErreurMonde:
                return _rate(monde, id, cible, "verrouillee", bool(c.get("verrouillee")))
            from .temps import instant
            enfermer(monde, id, cible, instant(monde) + DUREES[op])
        if cible not in monde.objets[outil].get("ouvre", []) or c.get("ouverte"):
            return False
        avant, c["verrouillee"] = c.get("verrouillee"), op == "verrouiller"
        changer_etat(monde, id, cible, "verrouillee", avant)
        croire(monde, id, cible, "verrouillee", c["verrouillee"], "essai")
        _raconter(monde, id, "déverrouille" if op == "deverrouiller" else "verrouille", c, lignes)
        if op == "deverrouiller":
            _ouvert_par_soi(monde, id, cible)
    elif op == "crocheter":
        if not c.get("verrouillee"):
            return _rate(monde, id, cible, "verrouillee", False) or True
        if not jet[0]:
            _raconter(monde, id, "s'acharne sur la serrure de", c, lignes)
            if faute:
                gestes.append((id, "forcer", cible, bruit))
            return False
        c["verrouillee"] = False
        changer_etat(monde, id, cible, "verrouillee", True)
        croire(monde, id, cible, "verrouillee", False, "essai")
        # Réussi, la serrure cède sans qu'il force (``ouie.nature_crochetage``).
        _raconter(monde, id, "crochète la serrure de", c, lignes, "" if bruit == "bruyant" else " sans forcer")
    elif op == "frapper":
        if not c.get("verrouillee") or c["integrite"] == 0:
            return _rate(monde, id, cible, "verrouillee", False) or True
        if not _forcer(monde, id, cible, outil, lignes):
            if faute:
                gestes.append((id, "frapper", cible, bruit))
            return None
        croire(monde, id, cible, "verrouillee", False, "essai")
        if faute:
            gestes.append((id, "briser", cible, bruit))
            faute = False
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
        from .perception import alimenter, recharge
        if not recharge(c, monde.objets[outil]):
            return False
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
        changer_etat(monde, id, cible, "allume", False)
        _raconter(monde, id, "allume", c, lignes)
        # Une flamme portable allumée ou employée pour ce geste : il saura la ménager ensuite.
        for flamme in (cible, outil):
            if monde.objets[flamme].get("mobile") and "allume" in monde.objets[flamme]:
                memoriser(monde, id, {"type": "flamme_employee", "objet": flamme})
    elif op == "eteindre":
        if not c.get("allume"):
            return True
        c["allume"] = False
        changer_etat(monde, id, cible, "allume", True)
        _raconter(monde, id, "éteint", c, lignes)
    # Ce qu'il vient de faire de ses mains, il le sait, même dans le noir.
    from .esprits import constater
    for objet in (cible, outil):
        if objet in monde.objets:
            constater(monde, id, objet, "essai")
    if faute:
        gestes.append((id, op, cible, bruit))  # Au registre des gestes en cours, avec sa durée (``_avancer``).
    return True


def _chauffer(monde, id, foyer, lignes):
    """Une minute près d'un foyer allumé de sa salle ; le geste s'achève (True) quand il est
    réchauffé, se poursuit (None) d'ici là ; False s'il n'y a pas de feu où il le croyait."""
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
    return True if e["besoins"]["chaleur"] <= CHALEUR_FIN else None


def _abriter(monde, id, lieu, lignes):
    """Une minute à l'abri : il y reste tant que la lumière ou une compagnie fiable le rassure ;
    le geste s'achève (True) quand il est rassuré, se poursuit (None) d'ici là ; False si ce
    n'est pas un abri."""
    from .deliberation import SECURITE_FIN, autour
    from .social import _qui
    e = esprit(monde, id)
    if "securite" not in e["besoins"]:
        return True
    if monde.objets[id]["lieu"] != lieu:
        return False
    from .deliberation import abri_valide
    if not abri_valide(monde, id, lieu):
        return False
    a = autour(monde, id)
    depuis = e["intention"]["depuis"] if e["intention"] else monde.data["minutes"]
    if not any(s["type"] == "abrite" and s["minute"] >= depuis for s in e["memoire"]):
        memoriser(monde, id, {"type": "abrite", "lieu": lieu})
        from .relations import envers
        # Le choix du déplacement utilise ses croyances ; le récit du moteur
        # affirme une proximité physique, jamais une ancienne position crue.
        ici = monde.objets[id].get("position")
        positions = {x: (monde.joueur if x == "joueur" else monde.objets[x]).get("position") for x in a["fiables"]}
        proches = sorted((x for x, p in positions.items() if ici is not None and p is not None and distance(ici, p) <= 1),
                         key=lambda x: (-envers(monde, id, x)["affection"], x))
        texte = (f"{_qui(monde, id)} reste près {de(_qui(monde, proches[0]))}." if proches
                 else f"{_qui(monde, id)} reste en compagnie." if a["fiables"]
                 else f"{_qui(monde, id)} reste dans la lumière.")
        _chroniquer(monde, id, texte)
        if monde.visible(id):
            lignes.append(texte)
    return True if e["besoins"]["securite"] <= SECURITE_FIN else None


def _reposer(monde, id, lignes):
    """Une minute de repos ; le geste s'achève (True) quand le PNJ est reposé, se poursuit (None)
    d'ici là."""
    from .deliberation import REPOS_FIN
    besoins, intention = esprit(monde, id)["besoins"], esprit(monde, id)["intention"]
    if "repos" not in besoins:
        return True
    texte = designer(monde.objets[id], debut=True) + " s'assoit pour se reposer."
    minute = monde.data["minutes"]
    # Il s'assoit une fois, même si un événement le fait reconsidérer dans la même minute.
    if intention and intention["depuis"] == minute and not any(
            c["pnj"] == id and c["minute"] == minute and c["texte"] == texte for c in monde.data.get("chronique", ())):
        _chroniquer(monde, id, texte)
        if monde.visible(id):
            lignes.append(texte)
    # Le repos délasse par le corps (``corps.vivre``), tant que ce geste est en cours.
    return True if besoins["repos"] <= REPOS_FIN else None


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
    return bool(intention) and any(x["condition"] in ("sans_temoin", "dans_le_dos") for x in intention["plan"])


def _marcher(monde, id, arrivee, lignes, gestes=None, libre=None):
    """Un pas d'une case vers une case libre où ``arrivee(salle, case)``, ou la porte fermée qu'il
    rencontre en chemin ; renvoie la durée du geste, 0 s'il y est déjà, None s'il ne voit aucun
    passage. Qui prépare un geste qu'il veut sans témoin marche à pas feutrés : plus lent, il ne
    s'entend que de tout près.

    Aucun geste ne s'achève sur une case occupée. On croise les autres en chemin : le pas qui
    mène sur la case de quelqu'un se poursuit, dans le même geste, jusqu'à la case libre qui
    suit. Si une porte fermée l'en empêche, il contourne. Sinon, ou s'il n'atteint ce qu'il vise
    que d'une case occupée, celui qui s'y tient doit lui faire place : avec ``gestes`` (le
    registre de ses gestes illicites), il attend qu'il s'écarte, le lui demande ou le pousse
    (``passage.faire_place``) ; sans, il attend. ``libre`` conserve les contraintes
    du séjour qui a admis le déplacement, y compris dans ses détours."""
    from .presence import interieur
    geometrie = interieur(monde)
    admissible = libre or (lambda salle, case: True)
    from .tenir import autoriser, lacher
    from .monde import ErreurMonde
    try:
        autoriser(monde, id, "marcher")
    except ErreurMonde:
        return None
    lacher(monde, id, "marcher")
    from .spatial import trajet
    from .obstacles import descriptions_crues, transitions, metrique_necessaire, duree_porte
    from .temps import PAS_FEUTRE
    o = monde.objets[id]
    feutre = a_pas_feutres(monde, id)
    allure = PAS_FEUTRE if feutre else PAS
    occupees = occupants(monde, id)
    depart = (o["lieu"], tuple(o["position"]))
    # Il ne cherche pas de chemin par une salle qu'il a vue noyée ; il peut quitter la sienne.
    from .eau import noyee_crue
    noyees = {s for s in monde.data["salles"] if s != o["lieu"] and noyee_crue(monde, id, s)}
    portes_autorisees = None
    from .eau import active, menacee
    if active(monde) and any(menacee(monde, id, s) for s in monde.data["salles"]):
        from .planification import Vue, depart as etat_depart
        from .geometrie import cases
        from .obstacles import cout_route
        vue = Vue(monde, id)
        etat = etat_depart(monde, id, vue).apres(allure=allure)
        destinations = [s for s in vue.salles if any(arrivee(s, c) for c in cases(vue.salles[s]))]
        routes = [(r, s) for s in destinations if (r := vue.route(etat, s)) is not None]
        if not routes:
            raisons = list(vue.refus_routes.values())
            if raisons:
                texte = (designer(o, debut=True) + " reste dans : " + vue.salles[o["lieu"]]["nom"]
                         + " ; " + raisons[0] + ".")
                # Le récit garde la cause, sans répéter la même attente à chaque pas.
                derniere = next((c for c in reversed(monde.data.get("chronique", [])) if c["pnj"] == id), None)
                if not derniere or derniere["texte"] != texte:
                    _chroniquer(monde, id, texte, "geste")
            return None
        route, destination = min(routes, key=lambda r: (cout_route(r[0]), r[1]))
        autorisees = {o["lieu"], *(x["vers"] for x in route)}
        portes_autorisees = {x["porte"] for x in route if x.get("porte")}
        noyees.update(set(vue.salles) - autorisees)
        cible = arrivee
        arrivee = lambda s, c: s == destination and cible(s, c)
    franchissable = lambda porte: (_franchissable(monde, id, porte)
                                   and (portes_autorisees is None or porte in portes_autorisees))
    formes = descriptions_crues(monde, id) if metrique_necessaire(monde, id, allure) else {}
    passages = transitions(monde, id, formes, allure=allure) if formes else None
    cout_porte = lambda p: duree_porte(monde, p)
    chemin_ = trajet(geometrie, *depart, lambda salle, case: arrivee(salle, case) and (salle, case) not in occupees,
                     franchissable=franchissable, libre=lambda salle, case: salle not in noyees and admissible(salle, case),
                     passages=passages, allure=allure, cout_porte=cout_porte)
    if chemin_ is None:
        if gestes is None:
            return None
        # Il n'atteindrait ce qu'il vise que d'une case où quelqu'un se tient.
        plein = trajet(geometrie, *depart, arrivee, franchissable=franchissable,
                       libre=lambda salle, case: salle not in noyees and admissible(salle, case),
                       passages=passages, allure=allure, cout_porte=cout_porte)
        if not plein or plein[-1][:2] not in occupees:
            return None
        from .passage import faire_place
        return faire_place(monde, id, occupees[plein[-1][:2]], [c[:2] for c in plein], lignes, gestes)
    if not chemin_:
        return 0
    n = 0
    while chemin_[n][:2] in occupees:
        n += 1  # La case de quelqu'un : il la traverse sans s'y arrêter.
    if any(porte for _, _, porte, _ in chemin_[1:n + 1]):
        # Une porte à ouvrir juste après la case d'un autre : il ne peut pas s'y arrêter pour l'ouvrir.
        detour = trajet(geometrie, *depart, lambda salle, case: arrivee(salle, case) and (salle, case) not in occupees,
                        franchissable=franchissable,
                        libre=lambda salle, case: (salle, case) not in occupees and salle not in noyees and admissible(salle, case),
                        passages=passages, allure=allure, cout_porte=cout_porte)
        if not detour:
            if gestes is None:
                return PAS  # Il attend qu'on lui laisse le passage.
            k = next(k for k in range(1, n + 1) if chemin_[k][2])
            from .passage import faire_place
            return faire_place(monde, id, occupees[chemin_[k - 1][:2]], [c[:2] for c in chemin_], lignes, gestes)
        chemin_, n = detour, 0
    # Au seuil d'une salle noyée qu'il ne savait pas telle, il voit l'eau et n'y entre pas.
    entree = next((salle for salle, _, _, _ in chemin_[:n + 1] if salle != o["lieu"]), None)
    if entree is not None and _arrete_par_l_eau(monde, id, entree):
        return PAS
    return _avancer_de(monde, id, chemin_[:n + 1], feutre, lignes)


def _noter_fuite(monde, id, depart):
    i = lire(monde, id)["intention"]
    o = monde.objets[id]
    if i and i["but"]["type"] == "fuir" and (o["lieu"], tuple(o["position"])) != depart:
        i.setdefault("attitude", {})["place"] = {"signe": "fuit", "envers": id, "sens": "peur"}


def _avancer_de(monde, id, pas, feutre, lignes):
    """Les pas d'un même geste, chacun précédé de sa rotation et de la durée que lui donne son sens
    (en diagonale, √2 fois un pas droit : ``temps.duree_pas``) ; une porte fermée s'ouvre sur place.
    Ses pas retentissent là où il s'arrête."""
    from .ouie import retentir
    from .spatial import QUART, quarts
    from .temps import PAS_FEUTRE, duree_pas
    o, duree, marche = monde.objets[id], 0, False
    depart = (o["lieu"], tuple(o["position"]))
    for salle, case, porte, sens in pas:
        # Il se tourne d'abord dans le sens du pas : le temps de la rotation s'ajoute.
        vers = next(nom for nom, v in VECTEURS.items() if v == sens)
        duree += QUART * quarts(o.get("orientation"), vers)
        o["orientation"] = vers
        if isinstance(porte, dict):
            # La route croyait ce mouvement possible ; le corps et la forme
            # réelle sont revérifiés au début du geste, comme une porte.
            from .obstacles import conditions, appliquer, transitions
            from .esprits import constater
            try:
                regle = conditions(monde, porte["cible"], porte["methode"], id)
                reel = next((r for (s, c), r, v, d in transitions(monde, id)(o["lieu"], tuple(o["position"]))
                             if s == salle and c == case and r["cible"] == porte["cible"]
                             and r["methode"] == porte["methode"]), None)
                if reel is None:
                    raise ErreurMonde("Le sol de réception n'est plus libre.")
            except ErreurMonde:
                constater(monde, id, porte["cible"], "essai")
                return duree + PAS
            reussite = True
            if regle["stat"]:
                from .caractere import modificateur
                jet = monde.d20()
                reussite = jet != 1 and jet + modificateur(monde, id, regle["stat"]) >= regle["dd"]
            if reussite:
                appliquer(monde, id, porte["cible"], {**regle, "salle": salle, "position": list(case)}, lignes)
                _noter_fuite(monde, id, depart)
            else:
                _chroniquer(monde, id, designer(o, debut=True) + " ne parvient pas à escalader "
                            + designer(monde.objets[porte["cible"]]) + ".", "deplacement")
            retentir(monde, id, regle["maniere"])
            monde._activite = "effort"
            duree += max(reel["dixiemes"], porte["dixiemes"])
            if not reussite:
                return duree
            continue
        if porte:
            if marche:
                retentir(monde, id, "aller", discret=feutre)
            return duree + _ouvrir_en_chemin(monde, id, monde.objets[porte], lignes)
        if salle != o["lieu"]:
            # Revalidation d'un pas préparé avant un changement de carte.
            sortie = monde.data["salles"][o["lieu"]]["sorties"].get(vers, {})
            if sortie.get("exterieur") is True and sortie["vers"] == salle:
                return duree or PAS
            o["lieu"] = salle
            placer(o, salle, list(case))
            _chroniquer(monde, id, designer(o, debut=True) + " passe dans : " + monde.data["salles"][salle]["nom"] + ".",
                        "deplacement")
            from .eau import tremper
            tremper(monde, id)
        else:
            placer(o, salle, list(case))
        duree += duree_pas(PAS_FEUTRE if feutre else PAS, sens)
        marche = True
        _noter_fuite(monde, id, depart)
    if marche:
        retentir(monde, id, "aller", discret=feutre)
        monde._activite = "effort"  # Marcher creuse (``vecu``).
    return duree


def _ouvrir_en_chemin(monde, id, porte, lignes):
    """La porte fermée qu'il rencontre : il l'ouvre, la déverrouille s'il en porte la clé, ou
    l'apprend verrouillée en la poussant."""
    if porte.get("verrouillee"):
        cle = _cle_portee(monde, id, porte["id"])
        if cle is None:
            croire(monde, id, porte["id"], "verrouillee", True, "essai")
            from .tenir import constater_enfermement
            constater_enfermement(monde, id)
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


def _jugement_placement(monde, id, etape):
    """Même séjour, mêmes cibles crues et mêmes pas pour les deux placements.

    Un rapprochement accessoire ne quitte pas le lieu ni la portée du geste
    qu'il accompagne. Le trajet doit exister dans ces contraintes, et un pas
    ne peut défaire le gain social obtenu par le précédent.
    """
    from . import relations, signes
    from .deliberation import salle_crue
    from .presence import interieur
    from .spatial import trajet, _case_libre
    from .obstacles import descriptions_crues, transitions, metrique_necessaire, duree_porte
    from .temps import PAS_FEUTRE
    if not monde.data.get("mode_cases") or etape["operation"] not in DURABLES:
        return None
    if _a_toucher(monde, id, etape):
        # Un séjour ciblé tient déjà sa place par l'approche de sa cible.
        return None
    o, e = monde.objets[id], lire(monde, id)
    ici, depart = o["lieu"], tuple(o["position"])
    foyer = _case_crue(monde, id, etape["cible"]) if etape["operation"] == "chauffer" else None
    possible = lambda s, p: s == ici and (foyer is None or distance(p, foyer) <= 2)
    geometrie = interieur(monde)
    occupees = occupants(monde, id)
    allure = PAS_FEUTRE if a_pas_feutres(monde, id) else PAS
    formes = descriptions_crues(monde, id) if metrique_necessaire(monde, id, allure) else {}
    passages = transitions(monde, id, formes, allure=allure) if formes else None

    def chemin(arrivee, admissible=lambda p: True):
        return trajet(geometrie, ici, depart,
                      lambda s, p: possible(s, p) and (s, p) not in occupees and arrivee(p),
                      franchissable=lambda porte: _franchissable(monde, id, porte),
                      libre=lambda s, p: possible(s, p) and admissible(p), passages=passages, allure=allure,
                      cout_porte=lambda porte: duree_porte(monde, porte))

    contacts = {}
    def contact(p, q):
        cle = (tuple(p), tuple(q))
        if cle not in contacts:
            contacts[cle] = _a_portee_de(monde, ici, p, q)
        return contacts[cle]

    positions, liens = {}, []
    for x in sorted(set(relations.connus(monde, id)) | {x for x, _, _ in signes.actives(monde, id)}):
        if x == id or salle_crue(monde, id, x) != ici:
            continue
        p = _case_crue(monde, id, x)
        if p is None:
            continue
        positions[x] = p
        r = relations.axes(monde, id, x)
        hostile = signes.hostile_cru(monde, id, x)
        if relations.peur(r) or relations.rancune(r) or hostile:
            evite = max(r["peur"], r["rancune"], relations.RANCUNE if hostile else 0)
            lien = (x, p, -evite, "ecart", "crainte" if r["peur"] >= r["rancune"] else "hostilite")
            arrivee = lambda q: distance(q, p) >= 2
        elif relations.vive(r, "affection") or relations.confiance(r) and e["besoins"].get("securite", 0) >= 50:
            lien = (x, p, max(r["affection"], r["confiance"]), "proche",
                    "attachement" if relations.vive(r, "affection") else "dependance")
            arrivee = lambda q: contact(q, p)
        else:
            continue
        if chemin(arrivee) is not None:
            liens.append(lien)

    def score(p):
        return sum((max(0, 3 - distance(p, q)) * (-v) if v < 0
                    else min(3, max(0, distance(p, q) - 1)) * v) for _, q, v, _, _ in liens)

    admissible = lambda s, p: possible(s, p) and score(p) <= score(depart)

    voisins = [(depart[0] + dx, depart[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
    return {"lieu": ici, "depart": depart, "positions": positions, "liens": liens,
            "score": score, "chemin": chemin, "possible": possible, "admissible": admissible,
            "occupees": occupees, "contact": contact,
            "cases": [p for p in [depart, *voisins] if possible(ici, p) and _case_libre(monde, ici, p)]}


def _pas_placement(jugement, arrivee=None):
    """Progresser sur un trajet admissible, sans dégrader le placement social.

    La progression d'un rapprochement est celle du trajet au contact, pas la
    distance en ligne droite (qui peut rester égale devant un obstacle).
    """
    score, depart = jugement["score"], jugement["depart"]
    admissible = lambda p: score(p) <= score(depart)
    if arrivee is not None:
        chemin = jugement["chemin"](
            lambda p: arrivee(p) and (not jugement["liens"] or score(p) < score(depart)), admissible)
        if not chemin:
            return None
        return next(p for s, p, _, _ in chemin if (s, p) not in jugement["occupees"])
    if jugement["cases"]:
        p = min(jugement["cases"], key=lambda p: (score(p), distance(p, depart), p))
        if score(p) < score(depart):
            chemin = jugement["chemin"](lambda q: tuple(q) == p, admissible)
            if chemin:
                return next(q for s, q, _, _ in chemin if (s, q) not in jugement["occupees"])
    return None


def _rejoindre_un_proche(monde, id, lignes, jugement=None):
    """Rejoindre un proche fiable admissible, préféré selon son affection.

    Le recours est accompli au contact d'une compagnie fiable ; une cible
    sans trajet améliorant cède à la suivante, sans bloquer le séjour.
    """
    from .relations import envers
    if jugement is None:
        i = lire(monde, id)["intention"]
        if not i or not i["plan"]:
            return None
        jugement = _jugement_placement(monde, id, i["plan"][0])
    if jugement is None:
        return None
    ici, depart = jugement["lieu"], jugement["depart"]
    proches = []
    for x, p in jugement["positions"].items():
        if se_fie(monde, id, x):
            proches.append((-envers(monde, id, x)["affection"], x, distance(p, depart), p))
    # L'abri demande de la compagnie fiable, pas de changer de compagnon
    # quand le contact est déjà établi. Le placement social peut encore
    # améliorer cette place ; le recours, lui, est alors accompli.
    if not proches or any(jugement["contact"](depart, x[3]) for x in proches):
        return None
    for _, _, _, p in sorted(proches):
        pas = _pas_placement(jugement, arrivee=lambda q: jugement["contact"](q, p))
        if pas is not None:
            return _marcher(monde, id, lambda salle, case: salle == ici and tuple(case) == pas, lignes,
                            libre=jugement["admissible"])
    return None


def _case_crue(monde, id, x, salle=None):
    """La case où il croit trouver ``x`` dans le secteur demandé (le sien par défaut).
    Une porte, un objet
    fixe font partie du lieu (``deliberation._lieu_cru``) : il sait leur place sans les avoir
    revus. None s'il ne sait où."""
    from .spatial import position_cible
    ici, o = salle or monde.objets[id]["lieu"], monde.objets.get(x)
    fixe = o is not None and o["type"] != "personnage" and not o.get("mobile")
    cru = lire(monde, id)["croyances"].get(x, {}).get("lieu")
    porteur = cru.get("valeur") if cru else None
    if porteur in monde.objets and monde.objets[porteur]["type"] == "personnage" and porteur != id:
        etat = lire(monde, id)["croyances"].get(porteur, {}).get("etat", {}).get("valeur", {})
        if etat.get("conscient") is False:
            return _case_crue(monde, id, porteur, ici)
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
    from .spatial import contact_cases
    return contact_cases(monde, salle, case, salle, cible)


def _approcher(monde, id, etape, lignes, gestes=None, compter=True):
    """Il marche vers ce que le geste touche, là où il le croit, jusqu'à l'avoir à portée de main ;
    sur place, le geste constate s'il y est. Renvoie la durée du pas, 0 s'il n'a plus à marcher,
    None s'il ne voit aucun chemin (``trajet``). Celui qui se tient sur la seule case d'où
    l'atteindre doit lui faire place (``_marcher``)."""
    o = monde.objets[id]
    loin = [x for x in _a_toucher(monde, id, etape) if not _accessible(monde, id, x)]
    if not loin:
        return 0
    def places_crues():
        croyances = lire(monde, id)["croyances"]
        places = []
        for x in loin:
            salle = (croyances.get(x, {}).get("lieu") or {}).get("salle") or o["lieu"]
            case = _case_crue(monde, id, x, salle)
            places.append((salle, case) if case is not None else None)
        return places
    crues = places_crues()
    if None in crues:
        # Il le croit dans cette salle sans savoir où : il la parcourt des yeux. Ne le voyant
        # pas, c'est en essayant le geste qu'il constate son absence.
        croyances = lire(monde, id)["croyances"]
        if "orientation" in o and any(c is None and (croyances.get(x, {}).get("lieu") or {}).get("salle") == o["lieu"]
                                      for x, c in zip(loin, crues)):
            tour_d_horizon(monde, id)
            if None not in places_crues():
                return TOUR
        return 0
    from .spatial import contact_cases
    arrivee = lambda salle, case: all(contact_cases(monde, salle, case, s, c, objet=x)
                                     for x, (s, c) in zip(loin, crues))
    pas = _marcher(monde, id, arrivee, lignes, gestes)
    return _impasse(monde, id, etape, arrivee, compter) if pas is None else pas


def _impasse(monde, id, etape, arrivee, compter=True):
    """Aucun chemin en cases vers où il va : c'est un geste manqué. Il apprend ce qui le barre,
    les obstacles du chemin qu'ils coupent (le chemin par salles en tiendra compte), puis la
    réflexe cesse, ou il patiente avant de renoncer. Renvoie None."""
    from .spatial import position_cible, trajet
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
    else:
        from .spatial import cases
        cause = {"type": "passage", "salle": monde.objets[id]["lieu"], "etape": dict(etape),
                 "arrivees": [[s, list(c)] for s, piece in monde.data["salles"].items()
                              for c in cases(piece) if arrivee(s, c)]}
        _patienter(monde, id, intention, compter, cause=cause)
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
    """Assez près pour s'entendre : même salle, à moins de ``ouie.PROCHE`` cases en distance réelle
    (``geometrie.distance`` ; sans cases, la même salle). ``b`` peut être le joueur."""
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
    return distance(pa, pb) <= PROCHE


def croit_present(monde, a, b):
    """``a`` sait ``b`` là, près de lui, pour lui adresser la parole : il le voit, ou l'a vu,
    reconnu à la voix ou entendu se nommer dans sa salle depuis peu (``RECENT``)."""
    if percoit(monde, a, b):
        return True
    from .esprits import RECENT
    c = lire(monde, a)["croyances"].get(b, {}).get("lieu")
    return bool(c and c["valeur"] == monde.objets[a]["lieu"] and c["source"] in ("vu", "entendu", "se_dit")
                and monde.data["minutes"] - c["minute"] <= RECENT)


def peuvent_se_parler(monde, a, b):
    """La règle commune de toute parole échangée, entre PNJ comme avec le joueur : chacun saisit
    les mots de l'autre par l'ouïe commune (``ouie.s_entendent`` : distance réelle, passages,
    portes). Savoir qui parle n'en est pas une condition : une voix qu'on ne sait à qui prêter est
    un étranger (``relations.percue``), à qui l'on peut répondre « Qui va là ? »."""
    from .corps import conscient
    if not conscient(monde, a) or not conscient(monde, b):
        return False
    from .ouie import s_entendent
    return s_entendent(monde, a, b)


def pourraient_se_parler(monde, a, b):
    """``a`` pourrait choisir de parler à ``b`` : il le sait là (``croit_present``, jamais d'après
    sa place réelle), et ils peuvent se parler (``peuvent_se_parler``)."""
    return croit_present(monde, a, b) and peuvent_se_parler(monde, a, b)


def se_parler(monde, a, b):
    """``a``, qui s'adresse à ``b`` là où il le croit, et ``b`` se parlent si chacun saisit les mots
    de l'autre (``peuvent_se_parler``). Sans se voir (le noir, une porte), chacun se tourne vers la
    voix de l'autre et en retient ce qu'elle lui apprend (``voix.entendre`` : une voix connue, il
    croit son porteur là ; une voix inconnue, il la retient sans savoir à qui elle est). ``a``
    s'adressait à ``b`` : la voix qui lui répond se nomme ainsi (``voix.se_nommer``)."""
    from .ouie import _place
    from .voix import entendre as entendre_voix, se_nommer
    if not peuvent_se_parler(monde, a, b):
        return False
    from .deliberation import rejoint
    for x, y in ((a, b), (b, a)):
        if x != "joueur":
            rejoint(monde, x, y)  # Qui attendait l'autre l'a trouvé (``deliberation.attendre``).
        if x == "joueur" or percoit(monde, x, y):
            continue
        sy, py = _place(monde, y)
        if "position" in monde.objets[x] and sy == monde.objets[x]["lieu"]:
            _faire_face(monde, x, y)
            percevoir(monde, x)
        entendre_voix(monde, x, y, sy, list(py) if py is not None and sy == monde.objets[x]["lieu"] else None)
        if x == a:
            se_nommer(monde, a, b, b)
    return True


# Ce que devient un PNJ au sortir de ``agir`` : un geste en cours (``GESTE``), une attente jusqu'à
# la minute qu'un événement abrège (``ATTENTE`` : désœuvré, guettant une occasion, un geste qui
# dure), un plan fini ou abandonné (``FIN``) ou un geste manqué (``MANQUE``), après lesquels il
# choisit aussitôt de nouveau (``_avancer``).
GESTE, ATTENTE, FIN, MANQUE = "geste", "attente", "fin", "manque"


def _geste(etape):
    """Ce qu'est un geste, sans ce que le plan y ajoute (la lumière prévue, une parole) : le même
    geste manqué, replanifié, est reconnu."""
    return {k: etape[k] for k in ("operation", "cible", "outil", "lieu")}


def _patienter(monde, id, intention, compter=True, *, cause):
    """Il attend son occasion, ou que le chemin se libère : une attente commence maintenant
    (``commencer_attente``) ; le temps qu'il y passe se compte en dixièmes de seconde, quel que soit
    le nombre de fois qu'un événement l'a fait reconsidérer. Au-delà de ``PATIENCE`` minutes
    d'attente pour ce but, il renonce. Vrai s'il a renoncé."""
    from .deliberation import PATIENCE, renoncer
    from .temps import MINUTE, instant
    if intention["attente"] > PATIENCE * MINUTE:
        renoncer(monde, id, monde.data["minutes"], cause)
        return True
    commencer_attente(monde, id, instant(monde))
    return False


def commencer_attente(monde, id, t):
    """Il se met à attendre son occasion (ou qu'on lui fasse place) à l'instant ``t``."""
    e = esprit(monde, id)
    if e["patience"] is None:
        e["patience"] = t


def compter_attente(monde, id, t, continuer=False):
    """Le temps passé à attendre jusqu'à ``t`` s'ajoute à l'attente du but en cours
    (``intention["attente"]``, en dixièmes de seconde) : à son geste suivant, l'attente est close ;
    à la frontière de minute (``continuer``), elle est comptée et continue."""
    e = esprit(monde, id)
    if e["patience"] is None:
        return
    if e["intention"] and t > e["patience"]:
        from .signes import attente_sous_regard
        attente_sous_regard(monde, id, t - e["patience"])
        e["intention"]["attente"] += t - e["patience"]
    e["patience"] = t if continuer and e["intention"] else None


def refus_etape(monde, id, etapes):
    """Admissibilité du prochain geste, au choix comme juste avant l'exécution.

    Le contrôle porte sur les présences requises, l'eau crue et les routes déjà contrôlées par la
    marche. Un but sec ne certifie pas un préparatif local dans un péril.
    Aucun effet, aucune observation supplémentaire de la réalité.
    """
    ici = monde.objets[id]["lieu"]
    tete = next((x for x in etapes if x["operation"] != "aller" or x["lieu"] != ici), None)
    if tete is not None and tete["operation"] != "aller":
        from .planification import vue, depart
        v = vue(monde, id)
        e = depart(monde, id, v)
        # Les cibles de contact passent par l'approche et l'observation du
        # geste : les rejeter ici empêcherait d'apprendre leur disparition.
        # Inconnu ne signifie pas absent : le plan doit d'abord préparer
        # le contact, sans dépenser le geste final pour le constater.
        for x in _a_reunir(monde, id, tete, e.portes, venues=True, contacts=False):
            if v.salle(e, x) is None:
                return "participant à localiser"
            if not v.present(e, x):
                return "participant cru absent"
    from .eau import active, en_peril, menacee
    if not active(monde):
        return None
    if tete is None or tete["operation"] != "aller":
        return "séjour en péril d'eau" if en_peril(monde, id) else None
    if any(menacee(monde, id, s) for s in monde.data["salles"]):
        from .planification import Vue, depart
        from .temps import PAS_FEUTRE
        v = Vue(monde, id)
        allure = PAS_FEUTRE if any(x["condition"] in ("sans_temoin", "dans_le_dos") for x in etapes) else PAS
        if v.route(depart(monde, id, v).apres(allure=allure), tete["lieu"]) is None:
            return v.refus_routes.get(tete["lieu"], "route crue inaccessible")
    return None


def agir(monde, id, t, lignes, gestes=None, compter=True):
    """Le geste qui commence à l'instant ``t`` (en dixièmes de seconde) selon l'intention
    courante ; renvoie (durée, issue, étape manquée) : l'issue dit s'il agit (``GESTE``), attend
    jusqu'à la minute (``ATTENTE``), a fini ou abandonné son plan (``FIN``) ou manqué un geste
    (``MANQUE``). ``compter`` : il agit à son heure, et non parce qu'un événement l'a fait
    reconsidérer. Sans le mode cases, un geste prend la minute, comme avant."""
    from .corps import conscient, corps
    if not conscient(monde, id):
        return max(1, corps(monde, id)["inconscient"] - t), ATTENTE, None
    if t < corps(monde, id).get("reprise", 0):
        return corps(monde, id)["reprise"] - t, GESTE, None
    from .deliberation import EFFORTS
    reste = _jusqu_a_la_minute(t)
    en_cases = bool(monde.data.get("mode_cases"))
    gestes = [] if gestes is None else gestes
    e = esprit(monde, id)
    intention = e["intention"]
    from .signes import surveiller
    rotation = surveiller(monde, id)
    intention = e["intention"]
    if rotation:
        return rotation, GESTE, None
    if not intention:
        return reste, ATTENTE, None
    etapes, o = intention["plan"], monde.objets[id]
    while etapes and etapes[0]["operation"] == "aller" and etapes[0]["lieu"] == o["lieu"]:
        etapes.pop(0)
    if not etapes:
        if intention["motif"] == "alerte":
            e["intention"] = None
        return reste, FIN, None
    etape = etapes[0]
    operation = etape["operation"]
    if refus_etape(monde, id, etapes) is not None:
        return reste, MANQUE, etape
    if e["manque"] and e["manque"]["minute"] == monde.data["minutes"] and e["manque"]["etape"] == _geste(etape):
        # Un geste manqué ne se retente pas aussitôt : pas avant la minute suivante, même si un
        # événement l'a fait reconsidérer entre-temps.
        return reste, ATTENTE, None
    en_place = en_cases and "position" in o
    if en_place and operation == "interposer":
        from .defense import interposition
        reaction = interposition(monde, id)
        if not reaction or not reaction[1] or reaction[1][0] != etape:
            return reste, MANQUE, etape
        arrivee = lambda salle, case: salle == etape["lieu"] and list(case) == etape["contenu"]["position"]
        if not arrivee(o["lieu"], o["position"]):
            pas = _marcher(monde, id, arrivee, lignes)
            return (pas, GESTE, None) if pas else (reste, MANQUE, etape)
    if en_place and operation == "aller":
        # Le seul juge du passage est le chemin en cases : sans chemin, c'est un geste manqué.
        lieu = etape["lieu"]
        arrivee = lambda salle, case: salle == lieu
        pas = _marcher(monde, id, arrivee, lignes, gestes)
        if pas is None:
            _impasse(monde, id, etape, arrivee, compter)
            return reste, MANQUE, etape
        return (pas, GESTE, None) if pas else (reste, ATTENTE, None)
    if en_place:
        # Il s'approche pas à pas de ce qu'il va toucher ; l'absence de témoin se juge sur place.
        pas = _approcher(monde, id, etape, lignes, gestes, compter)
        if pas is None:
            return reste, MANQUE, etape
        if pas:
            return pas, GESTE, None
    if etape["condition"] == "dans_le_dos":
        from .combat import approcher_dos
        pas = approcher_dos(monde, id, etape, lignes, gestes, compter)
        if pas is None:
            return reste, MANQUE, etape
        if pas:
            return pas, GESTE, None
    if operation == "inspecter" and en_cases and "position" in o and o["lieu"] == etape["lieu"]:
        vers = (etape.get("contenu") or {}).get("vers")
        ici = o["lieu"]
        if vers is not None:
            # Il va voir l'endroit d'où venait le bruit : il s'en approche pas à pas jusqu'à le voir
            # en se tournant, ou, si rien ne l'éclaire, jusqu'au contact ; sans chemin, il regarde
            # de là où il est.
            if not _a_portee_de_vue(monde, id, vers):
                pas = _marcher(monde, id, lambda salle, case: salle == ici and distance(case, vers) <= CONTACT, lignes)
                if pas:
                    return pas, GESTE, None
        else:
            # Il gagne le centre de la salle pas à pas avant de la parcourir des yeux.
            centre = _centre(monde, id)
            if centre is not None and tuple(centre) != tuple(o["position"]):
                pas = _marcher(monde, id, lambda salle, case: salle == ici and tuple(case) == tuple(centre), lignes)
                if pas:
                    return pas, GESTE, None
    from .signes import place as place_sociale
    jugement = _jugement_placement(monde, id, etape)
    pas_social = place_sociale(monde, id, etape, lignes, jugement=jugement)
    if pas_social:
        return pas_social, GESTE, None
    if operation == "abriter" and en_cases and o["lieu"] == etape["lieu"]:
        # S'abriter, c'est se tenir près de quelqu'un de sûr qu'il croit là, pas sur le seuil.
        pas = _rejoindre_un_proche(monde, id, lignes, jugement=jugement)
        if pas:
            return pas, GESTE, None
    if not _assez_de_lumiere(monde, id, etape):
        return reste, MANQUE, etape
    if etape["condition"] == "sans_temoin" and not desespere(monde, id):
        if en_cases and "orientation" in o:
            # Avant un geste qu'il veut sans témoin, il regarde tout autour de lui ; il n'agit
            # qu'au geste suivant, si personne ne l'a vu entre-temps. Son dernier tour d'horizon
            # est dans son esprit : il ne dépend pas du découpage des actions du joueur.
            ici = {"salle": o["lieu"], "case": list(o["position"])}
            dernier = e["balayage"]
            observe = None
            # Un événement qui l'a fait reconsidérer (``compter`` faux) peut avoir changé qui le voit :
            # il regarde de nouveau autour de lui, au lieu de s'en tenir à ce qu'il a devant lui.
            if (not dernier or {k: dernier[k] for k in ici} != ici or t - dernier["instant"] > 2 * TOUR
                    or not compter):
                e["balayage"] = {**ici, "instant": t}
                observe = tour_d_horizon(monde, id)
                if not observe:
                    return TOUR, GESTE, None
        else:
            observe = None
        from .ouie import nature as nature_de
        from .planification import bruit_crochetage
        # Ceux qu'il croit à portée d'oreille comptent comme ceux qu'il voit : qui entend forcer un
        # coffre tout près sait qu'on y touche (``_temoins_a_l_oreille``). D'un crochetage, il attend
        # le bruit que lui promet son adresse à la lumière qu'il a devant la serrure.
        attendu = (bruit_crochetage(monde, id, lumiere_du_geste(monde, id)) if operation == "crocheter"
                   else nature_de(operation, discret=True))
        from .deliberation import obstacle_patience, salle_crue
        cause = {"type": "temoins", "salle": o["lieu"], "etape": dict(etape), "nature": attendu}
        temoins = sorted(set(obstacle_patience(monde, id, cause)) | set(observe or ()))
        if observe or temoins:
            # Il guette une occasion, jusqu'à la minute suivante ou jusqu'à ce que sa situation change.
            from .signes import dissimule, regarder as regard_social
            cause["temoins"] = {x: salle_crue(monde, id, x) for x in temoins}
            if _patienter(monde, id, intention, compter, cause=cause):
                return reste, FIN, None
            rotation = regard_social(monde, id, intention, etape["cible"], "convoite", "guet",
                                     detourner=dissimule(monde, id, intention=True))
            if rotation:
                return rotation, GESTE, None
            return reste, ATTENTE, None
    # Il se tourne vers ce qu'il touche ou voit, jamais vers ce qu'il ignore.
    cible = etape["cible"]
    tourner = (_faire_face(monde, id, cible) if en_cases and cible and (
        cible in monde.objets and _accessible(monde, id, cible) or percoit(monde, id, cible)) else 0)
    if operation == "assommer" or operation == "frapper" and (cible == "joueur" or monde.objets.get(cible, {}).get("type") == "personnage"):
        from .combat import rotation
        vers, supplement = rotation(monde, id, cible)
        o["orientation"] = vers
        tourner += supplement
    fait = _executer(monde, id, etape, lignes, gestes)
    if fait and operation == "tuer":
        for g in monde.data.get("gestes_en_cours", []):
            if g["auteur"] == id and g["operation"] == operation and "issue" in g:
                g["fin"] += tourner
    if fait is not False:
        # Ce qu'il fait le temps de ce geste : se reposer délasse, un geste d'effort creuse (``vecu``).
        monde._activite = "repos" if operation == "reposer" else "effort" if operation in EFFORTS else None
    if fait:
        etapes.pop(0)
        if intention["motif"] == "alerte" and not etapes:
            e["intention"] = None
    if not en_cases or operation == "aller":
        return reste, GESTE, None
    if operation in DURABLES:
        # Un geste qui dure (se reposer, se chauffer, s'abriter) : jusqu'à la minute, où ses besoins
        # changent ; achevé (son seuil atteint) ou impossible, il choisit aussitôt la suite.
        if fait is None:
            return reste, ATTENTE, None
        return (reste, FIN, None) if fait else (reste, MANQUE, etape)
    if operation == "frapper" and monde.objets.get(cible, {}).get("type") == "porte" and fait is not False:
        return tourner + 30, GESTE, None
    if not fait:
        return reste, MANQUE, etape
    if operation == "assommer" or operation == "frapper" and (cible == "joueur" or monde.objets.get(cible, {}).get("type") == "personnage"):
        from .combat import COUP
        return tourner + COUP, GESTE, None
    if operation == "tuer":
        return tourner + (50 if etape["outil"] else 300), GESTE, None
    return tourner + DUREES.get(operation, 20), GESTE, None


# --- Présences perçues par le joueur -------------------------------------------------------
# Pendant une action du joueur, les PNJ entrent dans son champ de vision et en sortent pas à
# pas. On n'en annonce que le bilan, à la fin de l'action : qui il voit désormais, qui il ne
# voit plus, qui il n'a fait qu'apercevoir. Entrer dans la pièce ou la quitter ne se dit que
# si le joueur a vu le passage ; sinon, il sait seulement qu'il voit, ou ne voit plus, quelqu'un.

def _ouvrir_presences(monde):
    from .spatial import etat_fige, vue_memorisee
    ici, suivi = monde.joueur["salle"], {}
    with vue_memorisee(monde), etat_fige(monde):  # Un relevé : l'état n'est lu qu'une fois.
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
    from . import agendas
    from .spatial import vue_memorisee
    with vue_memorisee(monde):
        resultat = _avancer(monde, minutes, lignes, dixiemes)
        agendas.observer_promesses(monde, lignes)
        return resultat


def _prevu(e):
    """L'instant où il reprend la main de lui-même : la fin de son geste, ou de son attente."""
    return e["libre"] if e["veille"] is None else max(e["libre"], e["veille"])


def _prochain(e):
    """L'instant où il reprend la main : à son heure ; plus tôt si un événement abrège son attente,
    jamais avant la fin d'un geste (ou d'une rotation vers un bruit) en cours."""
    if e["veille"] is None or e["eveil"] is None:
        return _prevu(e)
    return max(e["libre"], min(e["veille"], e["eveil"]))


def _avancer(monde, minutes, lignes, dixiemes):
    """La vie des PNJ par événements : chacun commence un geste dès qu'il a fini le précédent ;
    à chaque minute franchie, le feu se consume et chacun délibère (le filet de ce qui monte peu
    à peu). Entre deux minutes, il choisit de nouveau son but à la fin de son plan, après un geste
    manqué, et après un événement qui change sa situation (``esprits.reconsiderer``) : à la fin de
    son geste en cours, ou aussitôt s'il ne fait qu'attendre. On traite toujours ce qui arrive en
    premier ; quand rien ne bouge, on saute à l'événement suivant. À un même instant, dans l'ordre
    des identifiants ; à des instants distincts, dans l'ordre du temps."""
    from .deliberation import appeler_a_l_aide, choisir, deliberer, menager_flamme
    from .eau import inonder
    from .horloges import declencher as declencher_horloges
    from .perception import avancer_combustion
    from .social import bavarder
    from .signes import percevoir_tous as percevoir_signes
    from .spatial import etat_fige
    from .corps import conscient, corps, reveiller
    from .temps import MINUTE
    from .vecu import minute as vivre_la_minute, noter, solder as solder_vecu
    debut_issues = len(monde.data.get("historique_corps", ()))
    fin_minutes, fin_dixiemes = monde.data["minutes"], monde.data.get("dixiemes", 0)
    fin = fin_minutes * MINUTE + fin_dixiemes
    debut = fin - (minutes * MINUTE if dixiemes is None else dixiemes)
    ids = pnjs(monde)
    en_cases = bool(monde.data.get("mode_cases"))
    monde._agit = None  # Qui agit en ce moment : rien de ce qu'il voit changer de son fait ne l'éveille.
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
    ids = pnjs(monde)  # Une issue peut retirer un esprit pendant ce même laps.
    # L'instant où chacun aura fini son geste, ou son attente, est dans son esprit : un bruit qui
    # le fait se retourner le retarde (``ouie``), un événement abrège son attente.
    esprits_ = {id: esprit(monde, id) for id in ids}
    for e in esprits_.values():
        if e["veille"] is None:
            e["libre"] = max(debut, e["libre"])
        if e["eveil"] is not None and e["eveil"] <= debut and _prochain(e) <= debut:
            # Ce qu'il a perçu au début de l'action du joueur (son résultat), il y réagit pendant
            # cette action : l'instant même de son début appartient encore à l'action précédente,
            # où tout ce qui s'y passe a été traité et entendu (``ecoute.entendus``).
            # Un auteur encore occupé conserve son éveil : découper le laps ne le repousse pas.
            e["eveil"] = debut + 1
    # Les horloges du scénario se déclenchent à leur minute, pendant la vie des PNJ, qui vivent ce
    # qu'elles changent ; une échéance déjà passée au début (la minute 0) se déclenche aussitôt.
    monde.data["minutes"], monde.data["dixiemes"] = divmod(debut, MINUTE)
    declencher_horloges(monde, lignes)
    monde.data["minutes"], monde.data["dixiemes"] = fin_minutes, fin_dixiemes
    t, tours = debut, 0
    while True:
        ids = [id for id in ids if not monde.objets[id].get("parti")]
        esprits_ = {id: esprits_[id] for id in ids}
        frontiere = (t // MINUTE + 1) * MINUTE
        reveil_joueur = corps(monde, "joueur")["inconscient"] or fin + 1
        prochain = min((_prochain(e) for e in esprits_.values()), default=fin + 1)
        echeance = min((g["fin"] for g in monde.data.get("gestes_en_cours", ()) if "issue" in g), default=fin + 1)
        prochain = min(prochain, reveil_joueur, echeance)
        if min(frontiere, prochain) > fin:
            break
        if frontiere <= prochain:
            t, tours = frontiere, 0
            monde.data["minutes"], monde.data["dixiemes"] = divmod(t, MINUTE)
            minute = monde.data["minutes"]
            declencher_horloges(monde, lignes)
            avancer_combustion(monde, 1, lignes)
            inonder(monde, lignes)
            # Le corps du joueur a vécu la minute dans l'état de son action (``vecu``).
            vivre_la_minute(monde, "joueur", t, lignes)
            for id in ids:
                vivre_la_minute(monde, id, t)
                if not conscient(monde, id):
                    continue
                esprits_[id]["manque"] = None  # Une minute a passé : ce qu'il a manqué se retente.
                if monde.objets[id].get("profil"):
                    esprits_[id]["eveil"] = None  # Il délibère : ce qui l'avait éveillé y est pesé.
                    compter_attente(monde, id, t, continuer=True)
                    deliberer(monde, id, minute)
                    menager_flamme(monde, id, minute)
                    appeler_a_l_aide(monde, id, minute)
                    percevoir(monde, id)
            percevoir_tous(monde)  # Ce que la minute a changé (un feu, une flamme ménagée), tous le voient.
            percevoir_signes(monde)
            if monde.data.get("dettes"):
                from .biens import solder
                solder(monde, lignes)  # Qui se retrouvent soldent ce que l'un doit à l'autre.
            if any(p["a"] == "joueur" for p in monde.data.get("permissions", ())):
                from .biens import prets_reclames
                prets_reclames(monde, lignes)  # Un prêt échu réclamé au joueur, et pas rendu.
            continue
        tours = tours + 1 if prochain == t else 0
        assert tours <= 50 * max(1, len(ids)), "La vie des PNJ tourne sur place"
        t = prochain
        monde.data["minutes"], monde.data["dixiemes"] = divmod(t, MINUTE)
        finir_gestes(monde, t)
        ids = [id for id in ids if id in monde.data["esprits"]]
        esprits_ = {id: esprits_[id] for id in ids}
        if reveil_joueur == t:
            reveiller(monde, "joueur")
        for id in ids:
            e = esprits_[id]
            if _prochain(e) != t:
                continue
            if not conscient(monde, id):
                reveiller(monde, id)
                percevoir_tous(monde)
                choisir(monde, id, monde.data["minutes"])
            # À son heure (fin de son geste ou de son attente), ou plus tôt, éveillé par un événement.
            compter = t == _prevu(e)
            e["veille"] = None
            # Son geste précédent est fini : ceux qui l'ont vu jusque-là s'en souviennent.
            finir_gestes(monde, t, id)
            profil = bool(monde.objets[id].get("profil"))
            if profil:
                # Son corps et ses besoins ont vécu jusqu'ici ; son attente, s'il guettait, est comptée.
                solder_vecu(monde, id, t)
                compter_attente(monde, id, t)
            monde._activite = None
            if e["eveil"] is not None and e["eveil"] <= t:
                # Sa situation a changé pendant son geste, ou pendant qu'il attendait : il choisit
                # de nouveau son but avant d'agir, sur ce qu'il croit maintenant.
                e["eveil"] = None
                choisir(monde, id, monde.data["minutes"])
            intention = lire(monde, id)["intention"]
            attend = note = False
            # Désœuvré ou guettant une occasion, il a le temps de confier ce qu'il sait.
            from .tenir import secours
            en_cours = next((g for g in monde.data.get("gestes_en_cours", ()) if g["auteur"] == id and "issue" in g), None)
            secours_duree = en_cours["fin"] - t if en_cours else secours(monde, id, lignes)
            if secours_duree is not None:
                duree = secours_duree
            elif (not intention or intention["attente"] and temoins_crus(monde, id)) and bavarder(monde, id, lignes):
                duree = DUREES["dire"] if en_cases else _jusqu_a_la_minute(t)
            elif intention:
                gestes = []
                monde._agit = id  # Le temps de son geste et de ce qu'on en voit (``esprits._percevoir``).
                duree, issue, rate = agir(monde, id, t, lignes, gestes, compter)
                if monde.objets[id].get("parti"):
                    monde._agit = None
                    percevoir_tous(monde)
                    observer()
                    continue
                if en_cases and issue in (FIN, MANQUE):
                    # Son plan est fini, ou un geste a manqué : il choisit aussitôt la suite, sur ce
                    # que l'essai vient de lui apprendre. Le geste manqué ne se retente pas avant la
                    # minute suivante (``agir``) : le même, il attend.
                    if issue == MANQUE:
                        e["manque"] = {"etape": _geste(rate), "minute": monde.data["minutes"]}
                    e["eveil"] = None
                    choisir(monde, id, monde.data["minutes"])
                    duree, issue, _ = agir(monde, id, t, lignes, gestes, compter)
                    if monde.objets[id].get("parti"):
                        monde._agit = None
                        percevoir_tous(monde)
                        observer()
                        continue
                    if issue != GESTE:
                        duree, issue = _jusqu_a_la_minute(t), ATTENTE
                attend = en_cases and issue == ATTENTE
                for _, operation, objet, *nature in gestes:
                    commencer_geste(monde, id, operation, objet, t + max(1, duree), nature=nature[0] if nature else None)
                # La perception suit l'événement : lui, et quiconque pouvait le voir faire (la vue
                # est en cache). Les croyances ne dépendent pas des instants où le joueur agit.
                # Percevoir, témoigner, relever ce que voit le joueur, noter l'état où il entre (son
                # corps) : des esprits et des corps seulement, l'état n'est lu qu'une fois.
                with etat_fige(monde):
                    percevoir_tous(monde)
                    monde._agit = None
                    temoigner_en_cours(monde)
                    observer()
                    if profil:
                        noter(monde, id, t, monde._activite)
                percevoir_signes(monde)
                note = True
            else:
                duree, attend = _jusqu_a_la_minute(t), en_cases
            if profil and not note:
                # L'état où il entre pour ce geste ou cette attente : son activité, le lieu où il se tient.
                noter(monde, id, t, monde._activite)
            if attend:
                # Il attend la minute : libre dès maintenant, un événement abrège son attente.
                e["libre"], e["veille"] = t, t + duree
            else:
                e["libre"] = t + max(1, duree)
    temoigner_en_cours(monde)
    monde.data["minutes"], monde.data["dixiemes"] = fin_minutes, fin_dixiemes
    observer()
    finir_gestes(monde, fin)  # Ceux qui durent encore attendent l'action suivante du joueur.
    from .tenir import bilan
    bilan(monde, debut_issues, lignes)
    if propre:
        lignes.extend(bilan_presences(monde, suivi))
    return apparus
