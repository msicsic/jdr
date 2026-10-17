"""Actions des PNJ : le moteur exécute leurs intentions avec les règles physiques du joueur.

Chaque minute, un PNJ doté d'un profil délibère (``deliberation.py``), puis accomplit au
plus un geste de son plan : aller, prendre, poser, ouvrir, fermer, déverrouiller,
verrouiller, crocheter ou manger. Le chemin est cherché sur ce qu'il croit des portes ;
chaque geste est revalidé sur l'état réel et un échec devient une croyance apprise par
l'essai. Une étape `sans_temoin` attend que le PNJ ne perçoive personne ; les témoins
réels sont ceux qui le perçoivent. Le moteur annonce ce que le joueur perçoit et tient une
chronique complète, réservée au débogage et au banc. Luna n'intervient pas.
"""
from collections import deque

from .esprits import croire, esprit, lire, memoriser, percevoir, percoit, percus, pnjs
from .francais import complement_de, designer
from .geometrie import cases, placer, position_entree

CHRONIQUE_MAX = 300
CONTACT = dict.fromkeys(("prendre", "ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "manger"), True)


def verifier(monde):
    for o in monde.objets.values():
        if o["type"] != "personnage":
            continue
        reaction = o.get("reaction_son")
        assert reaction is None or (isinstance(reaction, dict) and set(reaction) == {"seuil"}
                                    and type(reaction["seuil"]) is int
                                    and 1 <= reaction["seuil"] <= 5), "Réaction de PNJ invalide"
    chronique = monde.data.get("chronique", [])
    assert (isinstance(chronique, list) and len(chronique) <= CHRONIQUE_MAX
            and all(isinstance(c, dict) and set(c) == {"minute", "pnj", "texte"} for c in chronique)), "Chronique invalide"


def _etape(operation, cible="", outil="", lieu="", condition=""):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu, "condition": condition}


def reagir(monde, id, origine, niveau):
    """Réflexe déclaré par l'auteur : un son assez fort donne l'intention d'aller voir."""
    pnj = monde.objets[id]
    reaction = pnj.get("reaction_son")
    if reaction and niveau >= reaction["seuil"] and origine != pnj["lieu"]:
        esprit(monde, id)["intention"] = {"but": {"type": "rejoindre", "lieu": origine}, "motif": "alerte",
                                          "plan": [_etape("aller", lieu=origine)],
                                          "depuis": monde.data["minutes"], "attente": 0}


def _porte(monde, objet, id):
    from .spatial import porte_par
    return porte_par(monde, objet, id)


def _cle_portee(monde, id, cible, cles=()):
    return next((c for c, o in monde.objets.items()
                 if (c in cles or _porte(monde, c, id)) and cible in o.get("ouvre", [])), None)


def _verrouillee_crue(monde, id, porte):
    cru = lire(monde, id)["croyances"].get(porte, {}).get("verrouillee")
    return bool(cru and cru["valeur"])


def chemin(monde, id, depart, arrivee, cles=()):
    """Sorties à emprunter selon ce que le PNJ croit des portes ; None si aucun passage cru.

    Le PNJ tente toute porte, sauf celle qu'il sait verrouillée sans en porter (ou prévoir
    d'en porter) la clé.
    """
    precedent, file = {depart: None}, deque([depart])
    while file:
        lieu = file.popleft()
        for sortie in monde.data["salles"][lieu]["sorties"].values():
            vers, porte = sortie["vers"], sortie.get("porte")
            if (vers in precedent or vers not in monde.data["salles"]
                    or porte and _verrouillee_crue(monde, id, porte)
                    and _cle_portee(monde, id, porte, cles) is None):
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


def portes_closes(monde, id, depart, arrivee):
    """Portes crues verrouillées sur la route la plus courte, toutes portes ignorées."""
    precedent, file = {depart: None}, deque([depart])
    while file:
        lieu = file.popleft()
        for sortie in monde.data["salles"][lieu]["sorties"].values():
            if sortie["vers"] not in precedent and sortie["vers"] in monde.data["salles"]:
                precedent[sortie["vers"]] = (lieu, sortie)
                file.append(sortie["vers"])
    portes = []
    while arrivee in precedent and precedent[arrivee]:
        arrivee, sortie = precedent[arrivee]
        if sortie.get("porte") and _verrouillee_crue(monde, id, sortie["porte"]):
            portes.append(sortie["porte"])
    return portes[::-1]


# --- Annonces et chronique ----------------------------------------------------------------

def _chroniquer(monde, id, texte):
    chronique = monde.data.setdefault("chronique", [])
    chronique.append({"minute": monde.data["minutes"], "pnj": id, "texte": texte})
    del chronique[:-CHRONIQUE_MAX]


def _raconter(monde, id, verbe, objet, lignes):
    """« X prend la trousse. » ; un verbe finissant par « de » prend le complément contracté."""
    groupe = verbe[:-3] + " " + complement_de(objet) if verbe.endswith(" de") else verbe + " " + designer(objet)
    texte = designer(monde.objets[id], debut=True) + " " + groupe + "."
    _chroniquer(monde, id, texte)
    if monde.visible(id):
        lignes.append(texte)


def _annoncer_porte(monde, id, porte, verbe, texte_porte, lignes):
    texte = designer(monde.objets[id], debut=True) + " " + verbe + " " + designer(porte) + "."
    _chroniquer(monde, id, texte)
    if monde.visible(id):
        lignes.append(texte)
    elif monde.visible(porte["id"]):
        lignes.append(designer(porte, debut=True) + texte_porte)


def temoins_crus(monde, id):
    """Ceux que le PNJ perçoit : il se croit observé par chacun d'eux."""
    return [s for s in percus(monde, id)[0]
            if s == "joueur" or monde.objets[s]["type"] == "personnage"]


def _temoigner(monde, id, operation, objet):
    """Les PNJ qui perçoivent réellement l'auteur d'un geste illicite s'en souviennent."""
    from .deliberation import VOL, relancer
    from .vol import proprietaire
    victime = proprietaire(monde, monde.objets[objet])
    for autre in pnjs(monde):
        if autre != id and percoit(monde, autre, id):
            memoriser(monde, autre, {"type": "vu_agir", "auteur": id, "operation": operation, "objet": objet})
            croire(monde, autre, id, "fiable", False, "vu")
            if autre == victime:
                relancer(monde, autre, "biens", VOL)


# --- Gestes -------------------------------------------------------------------------------

def _au_seuil(monde, o, sortie):
    """Place le PNJ sur la case intérieure de la sortie, comme le joueur pour l'ouvrir."""
    if "position" not in o or not monde.data.get("mode_cases"):
        return
    from .spatial import _case_interieure, _case_libre
    case = _case_interieure(monde, o["lieu"], sortie)
    if case is not None and _case_libre(monde, o["lieu"], case):
        placer(o, o["lieu"], list(case))


def _approcher(monde, id, cible):
    """Rejoint une case libre au contact de la cible, dans la même salle (une minute)."""
    from .spatial import _case_libre, position_cible, proche
    o = monde.objets[id]
    if not monde.data.get("mode_cases") or proche(monde, cible, id):
        return proche(monde, cible, id) or not monde.data.get("mode_cases")
    p = position_cible(monde, cible, o["lieu"])
    if p is None:
        return False
    depart = tuple(o.get("position", p))
    voisines = sorted((c for c in cases(monde.data["salles"][o["lieu"]])
                       if max(abs(c[0] - p[0]), abs(c[1] - p[1])) == 1 and _case_libre(monde, o["lieu"], c)),
                      key=lambda c: (max(abs(c[0] - depart[0]), abs(c[1] - depart[1])), c))
    for case in voisines:
        placer(o, o["lieu"], list(case))
        if proche(monde, cible, id):
            return True
    placer(o, o["lieu"], list(depart))
    return False


def _accessible(monde, id, objet):
    """L'objet est-il à portée de main du PNJ, hors de tout contenant fermé ?"""
    if _porte(monde, objet, id):
        return True
    salle = monde.objets[id]["lieu"]
    return monde.present_physique(objet, salle=salle) and _approcher(monde, id, objet)


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
    depuis, o["lieu"] = o["lieu"], sortie["vers"]
    if "position" in o:
        placer(o, o["lieu"], position_entree(monde, o["lieu"], depuis))
    _chroniquer(monde, id, designer(o, debut=True) + " passe dans : " + monde.data["salles"][o["lieu"]]["nom"] + ".")


def _rate(monde, id, cible, attribut="lieu", valeur=None):
    """Un geste impossible corrige la croyance qui l'avait motivé."""
    from .esprits import reviser
    if attribut == "lieu":
        reviser(monde, id, cible, "lieu", None, "essai", salle=None, case=None)
    else:
        reviser(monde, id, cible, attribut, valeur, "essai")
    return False


def _crocheter(monde, id, cible, outil):
    from .perception import eclairage
    o = monde.objets[id]
    stats = o["profil"]["caracteristiques"]
    lumiere = eclairage(monde, o["lieu"], o.get("position") if monde.data.get("mode_cases") else None)["niveau"]
    return monde.d20() + (stats["DEX"] - 10) // 2 >= 14 + 4 * (2 - lumiere)


def _executer(monde, id, etape, lignes):
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
    c = monde.objets.get(cible)
    if c is None:
        return False
    if op in ("ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "manger", "prendre"):
        if not _accessible(monde, id, cible):
            return _rate(monde, id, cible)
    if outil and not _porte(monde, outil, id):
        return _rate(monde, id, outil)
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
    elif op == "fermer":
        c["ouverte"] = False
        _raconter(monde, id, "ferme", c, lignes)
    elif op in ("deverrouiller", "verrouiller"):
        if cible not in monde.objets[outil].get("ouvre", []) or c.get("ouverte"):
            return False
        c["verrouillee"] = op == "verrouiller"
        croire(monde, id, cible, "verrouillee", c["verrouillee"], "essai")
        _raconter(monde, id, "déverrouille" if op == "deverrouiller" else "verrouille", c, lignes)
    elif op == "crocheter":
        if not c.get("verrouillee"):
            return _rate(monde, id, cible, "verrouillee", False) or True
        if not _crocheter(monde, id, cible, outil):
            _raconter(monde, id, "s'acharne sur la serrure de", c, lignes)
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
    if faute:
        _temoigner(monde, id, op, cible)
    return True


def agir(monde, id, minute, lignes):
    """Un geste d'une minute selon l'intention courante."""
    from .deliberation import PATIENCE, renoncer
    e = esprit(monde, id)
    intention = e["intention"]
    if not intention:
        return
    etapes, o = intention["plan"], monde.objets[id]
    while etapes and etapes[0]["operation"] == "aller" and etapes[0]["lieu"] == o["lieu"]:
        etapes.pop(0)
    if not etapes:
        if intention["motif"] == "alerte":
            e["intention"] = None
        return
    etape = etapes[0]
    contact = CONTACT.get(etape["operation"])
    if contact and monde.data.get("mode_cases") and etape["cible"] in monde.objets:
        from .spatial import proche
        if (not _porte(monde, etape["cible"], id) and not proche(monde, etape["cible"], id)
                and monde.present_physique(etape["cible"], salle=o["lieu"])):
            # S'approcher prend la minute ; l'absence de témoin se juge ensuite sur place.
            _approcher(monde, id, etape["cible"])
            return
    if etape["condition"] == "sans_temoin" and temoins_crus(monde, id):
        intention["attente"] += 1
        if intention["attente"] > PATIENCE:
            renoncer(monde, id, minute)
        return
    if _executer(monde, id, etape, lignes):
        etapes.pop(0)
        if intention["motif"] == "alerte" and not etapes:
            e["intention"] = None


def avancer(monde, minutes, lignes):
    """Fait vivre les PNJ minute par minute ; renvoie ceux apparus dans la perception du joueur."""
    from .deliberation import deliberer
    fin = monde.data["minutes"]
    ids = pnjs(monde)
    vus = {id: monde.visible(id) for id in ids}
    for k in range(minutes):
        minute = monde.data["minutes"] = fin - minutes + k + 1
        for id in ids:
            if monde.objets[id].get("profil"):
                deliberer(monde, id, minute)
            if lire(monde, id)["intention"]:
                agir(monde, id, minute, lignes)
                percevoir(monde, id)
    monde.data["minutes"] = fin
    apparus = []
    for id in ids:
        o = monde.objets[id]
        if monde.visible(id) and not vus[id]:
            lignes.append(designer(o, debut=True) + " arrive.")
            apparus.append(id)
        elif vus[id] and not monde.visible(id):
            lignes.append(designer(o, debut=True) + " s'éloigne.")
    return apparus
