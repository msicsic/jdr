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
# deplacement : passer une salle, ouvrir une porte en chemin ; geste : agir sur un objet ;
# social : une parole entre PNJ ; decision : un plan choisi ou abandonné par un PNJ.
NATURES = ("deplacement", "geste", "social", "decision")
# Gestes qui demandent d'être au contact de la cible : un objet, ou celui à qui l'on parle.
CONTACT = dict.fromkeys(("prendre", "ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "manger",
                         "alimenter", "allumer", "servir", "remettre", "dire", "demander", "confier"), True)


def verifier(monde):
    for o in monde.objets.values():
        if o["type"] != "personnage":
            continue
        reaction = o.get("reaction_son")
        assert reaction is None or (isinstance(reaction, dict) and set(reaction) == {"seuil"}
                                    and type(reaction["seuil"]) is int
                                    and 1 <= reaction["seuil"] <= 5), "Réaction de PNJ invalide"
    from .stratege import verifier as verifier_stratege
    verifier_stratege(monde)
    chronique = monde.data.get("chronique", [])
    assert (isinstance(chronique, list) and len(chronique) <= CHRONIQUE_MAX
            and all(isinstance(c, dict) and set(c) - {"nature"} == {"minute", "pnj", "texte"}
                    and c.get("nature", "geste") in NATURES for c in chronique)), "Chronique invalide"


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
    texte = designer(monde.objets[id], debut=True) + " " + verbe + " " + designer(porte) + "."
    _chroniquer(monde, id, texte, "deplacement")
    if monde.visible(id):
        lignes.append(texte)
    elif monde.visible(porte["id"]):
        lignes.append(designer(porte, debut=True) + texte_porte)


def temoins_crus(monde, id):
    """Ceux que le PNJ perçoit : il se croit observé par chacun d'eux."""
    return [s for s in percus(monde, id)[0]
            if s == "joueur" or monde.objets[s]["type"] == "personnage"]


def _temoigner(monde, id, operation, objet):
    """Les PNJ qui perçoivent réellement l'auteur d'un geste illicite s'en souviennent.

    Un geste occupe sa minute : appelé de nouveau en fin de minute, il compte aussi ceux qui
    sont arrivés entre-temps, sans doubler le souvenir des premiers.
    """
    from .deliberation import VOL, relancer
    from .vol import proprietaire
    victime = proprietaire(monde, monde.objets[objet])
    souvenir = {"type": "vu_agir", "auteur": id, "operation": operation, "objet": objet}
    for autre in pnjs(monde):
        if autre != id and percoit(monde, autre, id):
            if any(s["minute"] == monde.data["minutes"] and all(s.get(k) == v for k, v in souvenir.items())
                   for s in lire(monde, autre)["memoire"]):
                continue
            memoriser(monde, autre, souvenir)
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


def _occupee(monde, id, salle, case):
    """Un autre personnage, ou le joueur, se tient déjà sur la case."""
    j = monde.joueur
    return (j["salle"] == salle and tuple(j["position"]) == tuple(case)) or any(
        o["type"] == "personnage" and k != id and o["lieu"] == salle and tuple(o.get("position", ())) == tuple(case)
        for k, o in monde.objets.items())


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
                       if max(abs(c[0] - p[0]), abs(c[1] - p[1])) == 1 and _case_libre(monde, o["lieu"], c)
                       and not _occupee(monde, id, o["lieu"], c)),
                      key=lambda c: (max(abs(c[0] - depart[0]), abs(c[1] - depart[1])), c))
    for case in voisines:
        placer(o, o["lieu"], list(case))
        if proche(monde, cible, id):
            return True
    placer(o, o["lieu"], list(depart))
    return False


def _inspecter(monde, id):
    """Gagne la case libre la plus proche du centre de la salle pour la parcourir des yeux."""
    o = monde.objets[id]
    if monde.data.get("mode_cases") and "position" in o:
        from .spatial import _case_libre
        sol = cases(monde.data["salles"][o["lieu"]])
        cx, cy = sum(x for x, _ in sol) / len(sol), sum(y for _, y in sol) / len(sol)
        libres = [c for c in sol if tuple(c) == tuple(o["position"])
                  or _case_libre(monde, o["lieu"], c) and not _occupee(monde, id, o["lieu"], c)]
        if libres:
            placer(o, o["lieu"], list(min(libres, key=lambda c: ((c[0] - cx) ** 2 + (c[1] - cy) ** 2, tuple(c)))))
    esprit(monde, id)["visites"][o["lieu"]] = monde.data["minutes"]


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
    _chroniquer(monde, id, designer(o, debut=True) + " passe dans : " + monde.data["salles"][o["lieu"]]["nom"] + ".",
                "deplacement")


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
    from .deliberation import SOCIALES
    if op in SOCIALES:
        from .echanges import executer
        return executer(monde, id, etape, lignes)
    c = monde.objets.get(cible)
    if c is None:
        return False
    if op == "chauffer":
        return _chauffer(monde, id, cible, lignes)
    if op in ("ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "manger", "servir", "prendre",
              "alimenter", "allumer"):
        if not _accessible(monde, id, cible):
            return _rate(monde, id, cible)
    if outil and not _porte(monde, outil, id):
        # Une flamme fixe ne se déplace pas : on lui apporte, en main, la source à allumer.
        if not (op == "allumer" and _porte(monde, cible, id) and _accessible(monde, id, outil)):
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
                _temoigner(monde, id, "forcer", cible)
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
    if faute:
        gestes.append((id, op, cible))
        _temoigner(monde, id, op, cible)
    return True


def _chauffer(monde, id, foyer, lignes):
    """Une minute près d'un foyer allumé de sa salle ; le geste s'achève quand il est réchauffé."""
    from .deliberation import CHALEUR_FIN, CHALEUR_MINUTE
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
    e["besoins"]["chaleur"] = max(0.0, e["besoins"]["chaleur"] - CHALEUR_MINUTE)
    return e["besoins"]["chaleur"] <= CHALEUR_FIN


def _reposer(monde, id, lignes):
    """Une minute de repos ; le geste s'achève quand le PNJ est reposé."""
    from .deliberation import REPOS_FIN, REPOS_MINUTE
    besoins, intention = esprit(monde, id)["besoins"], esprit(monde, id)["intention"]
    if "repos" not in besoins:
        return True
    if intention and intention["depuis"] == monde.data["minutes"]:
        texte = designer(monde.objets[id], debut=True) + " s'assoit pour se reposer."
        _chroniquer(monde, id, texte)
        if monde.visible(id):
            lignes.append(texte)
    besoins["repos"] = max(0.0, besoins["repos"] - REPOS_MINUTE)
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


def agir(monde, id, minute, lignes, gestes=None):
    """Un geste d'une minute selon l'intention courante."""
    from .deliberation import PATIENCE, renoncer
    e = esprit(monde, id)
    intention = e["intention"]
    if not intention:
        return
    from .stratege import terminer
    etapes, o = intention["plan"], monde.objets[id]
    from .deliberation import PROGRESSIFS
    strategie = intention["but"]["type"] == "strategie"
    while etapes and etapes[0]["operation"] == "aller" and etapes[0]["lieu"] == o["lieu"]:
        etapes.pop(0)
    if not etapes:
        if intention["motif"] == "alerte":
            e["intention"] = None
        elif strategie:
            terminer(monde, id, True)
        return
    etape = etapes[0]
    if strategie and etape["operation"] == "aller" and chemin(monde, id, o["lieu"], etape["lieu"]) is None:
        terminer(monde, id, False, etape)  # Aucun passage qu'il croie ouvert : la stratégie tombe.
        return
    contact = CONTACT.get(etape["operation"])
    if contact and monde.data.get("mode_cases") and etape["cible"] in monde.objets:
        from .spatial import proche
        if (not _porte(monde, etape["cible"], id) and not proche(monde, etape["cible"], id)
                and monde.present_physique(etape["cible"], salle=o["lieu"])):
            # S'approcher prend la minute ; l'absence de témoin se juge ensuite sur place.
            _approcher(monde, id, etape["cible"])
            return
    if etape["condition"] == "sans_temoin" and temoins_crus(monde, id) and not desespere(monde, id):
        intention["attente"] += 1
        if intention["attente"] > PATIENCE:
            renoncer(monde, id, minute)
        return
    if _executer(monde, id, etape, lignes, [] if gestes is None else gestes):
        etapes.pop(0)
        if intention["motif"] == "alerte" and not etapes:
            e["intention"] = None
        elif strategie and not etapes:
            terminer(monde, id, True)
    elif strategie and etape["operation"] not in PROGRESSIFS:
        terminer(monde, id, False, etape)  # Un geste manqué, ou un refus : il n'insiste pas.


def _annoncer_presences(monde, vus, apparus, lignes):
    """Arrivées et départs à la minute où le joueur les perçoit, avant ce qui suit."""
    for id, avant in vus.items():
        maintenant = monde.visible(id)
        if maintenant and not avant:
            lignes.append(designer(monde.objets[id], debut=True) + " arrive.")
            if id not in apparus:
                apparus.append(id)
        elif avant and not maintenant:
            lignes.append(designer(monde.objets[id], debut=True) + " s'éloigne.")
        vus[id] = maintenant


def avancer(monde, minutes, lignes):
    """Fait vivre les PNJ minute par minute ; renvoie ceux apparus dans la perception du joueur."""
    from .deliberation import deliberer
    from .perception import avancer_combustion
    from .social import bavarder
    fin = monde.data["minutes"]
    ids = pnjs(monde)
    vus = {id: monde.visible(id) for id in ids}
    apparus = []
    for k in range(minutes):
        minute = monde.data["minutes"] = fin - minutes + k + 1
        avancer_combustion(monde, 1, lignes)
        gestes = []
        for id in ids:
            if monde.objets[id].get("profil"):
                deliberer(monde, id, minute)
            intention = lire(monde, id)["intention"]
            # Désœuvré ou guettant une occasion, il a le temps de confier ce qu'il sait.
            if (not intention or intention["attente"] and temoins_crus(monde, id)) and bavarder(monde, id, lignes):
                continue
            if intention:
                agir(monde, id, minute, lignes, gestes)
                percevoir(monde, id)
                _annoncer_presences(monde, vus, apparus, lignes)
        for geste in gestes:
            if geste[2] in monde.objets:
                _temoigner(monde, *geste)
    monde.data["minutes"] = fin
    _annoncer_presences(monde, vus, apparus, lignes)
    return apparus
