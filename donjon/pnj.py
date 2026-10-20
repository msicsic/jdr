"""Actions des PNJ : le moteur exécute leurs intentions avec les règles physiques du joueur.

Chaque minute, un PNJ doté d'un profil délibère (``deliberation.py``). Entre-temps, il
accomplit son plan geste après geste, chacun avec sa durée, à la seconde près : un pas d'une
case, ouvrir, prendre, crocheter… (``temps``). Il marche case par case, par les mêmes règles
que le pas du joueur, et franchit les portes en les ouvrant. Le chemin est cherché sur ce
qu'il croit des portes ;
chaque geste est revalidé sur l'état réel et un échec devient une croyance apprise par
l'essai. Une étape `sans_temoin` attend que le PNJ ne perçoive personne ; les témoins
réels sont ceux qui le perçoivent. Le moteur annonce ce que le joueur perçoit et tient une
chronique complète, réservée au débogage et au banc. Luna n'intervient pas.
"""
from collections import deque

from .esprits import croire, esprit, lire, memoriser, percevoir, percoit, percus, pnjs
from .francais import complement_de, de, designer
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
                 if (c in cles or _porte(monde, c, id)) and cible in o.get("ouvre", [])), None)


def _verrouillee_crue(monde, id, porte):
    cru = lire(monde, id)["croyances"].get(porte, {}).get("verrouillee")
    return bool(cru and cru["valeur"])


def chemin(monde, id, depart, arrivee, cles=()):
    """Sorties à emprunter selon ce que le PNJ croit des portes ; None si aucun passage cru.

    Le PNJ tente toute porte, sauf celle qu'il sait verrouillée sans en porter (ou prévoir
    d'en porter) la clé ; il ne passe pas par une salle qu'il a vue noyée.
    """
    from .eau import noyee_crue
    precedent, file = {depart: None}, deque([depart])
    while file:
        lieu = file.popleft()
        for sortie in monde.data["salles"][lieu]["sorties"].values():
            vers, porte = sortie["vers"], sortie.get("porte")
            if (vers in precedent or vers not in monde.data["salles"] or noyee_crue(monde, id, vers)
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


# --- Annonces et chronique ----------------------------------------------------------------

def _chroniquer(monde, id, texte, nature="geste"):
    chronique = monde.data.setdefault("chronique", [])
    chronique.append({"minute": monde.data["minutes"], "pnj": id, "texte": texte, "nature": nature})
    del chronique[:-CHRONIQUE_MAX]
    # Un pas, un geste font du bruit ; les paroles le font par ``social.faire_entendre``.
    from .ecoute import NATURES, bruit
    if nature in NATURES:
        bruit(monde, id, NATURES[nature])


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


TOUR = 40              # dixièmes de seconde : un tour complet sur soi-même, huit fois 45°


def temoigner_en_cours(monde):
    """Ceux qui voient maintenant l'auteur d'un geste illicite qu'il n'a pas fini en sont témoins."""
    for gestes in list(monde.__dict__.get("_gestes_en_cours", {}).values()):
        for geste in gestes:
            if geste[2] in monde.objets:
                _temoigner(monde, *geste)


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
            from .deliberation import inquieter
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
    o = monde.objets[id]
    esprit(monde, id)["visites"][o["lieu"]] = monde.data["minutes"]
    if "orientation" in o:
        tour_d_horizon(monde, id)  # Il parcourt la salle des yeux, tout autour de lui.
    # Une ronde accomplie rassure : le lieu qu'il surveille est tel qu'il doit être.
    if any(x["condition"].get("lieu") == o["lieu"] and "periode" in x["condition"]
           for x in (o.get("profil") or {}).get("pulsions", [])):
        from .deliberation import inquieter
        inquieter(monde, id, "ronde", -1)


def _accessible(monde, id, objet):
    """L'objet est-il à portée de main du PNJ, hors de tout contenant fermé et des mains d'autrui ?"""
    if _porte(monde, objet, id):
        return True
    from .esprits import _porteur
    if _porteur(monde, monde.objets[objet]) is not None:
        return False
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
    if _arrete_par_l_eau(monde, id, sortie["vers"]):
        return
    depuis, o["lieu"] = o["lieu"], sortie["vers"]
    if "position" in o:
        placer(o, o["lieu"], position_entree(monde, o["lieu"], depuis))
    _chroniquer(monde, id, designer(o, debut=True) + " passe dans : " + monde.data["salles"][o["lieu"]]["nom"] + ".",
                "deplacement")
    from .eau import tremper
    tremper(monde, id)


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
    if op in ("ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "manger", "servir", "prendre",
              "alimenter", "allumer", "eteindre"):
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
        gestes.append((id, op, cible))
        _temoigner(monde, id, op, cible)
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


def _marcher(monde, id, arrivee, lignes):
    """Un pas d'une case vers une case libre où ``arrivee(salle, case)``, ou la porte fermée qu'il
    rencontre en chemin ; renvoie la durée du geste, None s'il ne voit aucun passage. On croise
    les autres en chemin ; on ne s'arrête pas sur leur case. Qui prépare un geste qu'il veut sans
    témoin marche à pas feutrés : plus lent, il ne s'entend que de tout près."""
    from .spatial import trajet
    from .temps import PAS_FEUTRE
    o = monde.objets[id]
    intention = lire(monde, id)["intention"]
    feutre = bool(intention) and any(x["condition"] == "sans_temoin" for x in intention["plan"])
    monde.__dict__.setdefault("_pas_feutres", {})[id] = feutre
    # Il ne cherche pas de chemin par une salle qu'il a vue noyée ; il peut quitter la sienne.
    from .eau import noyee_crue
    noyees = {s for s in monde.data["salles"] if s != o["lieu"] and noyee_crue(monde, id, s)}
    chemin_ = trajet(monde, o["lieu"], tuple(o["position"]),
                     lambda salle, case: arrivee(salle, case) and not _occupee(monde, id, salle, case),
                     franchissable=lambda porte: _franchissable(monde, id, porte),
                     libre=lambda salle, case: salle not in noyees)
    if not chemin_:
        return None
    salle, case, porte, sens = chemin_[0]
    if salle != o["lieu"] and _arrete_par_l_eau(monde, id, salle):
        return PAS
    # Il se tourne d'abord dans le sens du pas : le temps de la rotation s'ajoute.
    from .spatial import QUART, quarts
    vers = next(nom for nom, v in VECTEURS.items() if v == sens)
    tourner = QUART * quarts(o.get("orientation"), vers)
    o["orientation"] = vers
    if porte:
        return tourner + _ouvrir_en_chemin(monde, id, monde.objets[porte], lignes)
    if salle != o["lieu"]:
        o["lieu"] = salle
        placer(o, salle, list(case))
        _chroniquer(monde, id, designer(o, debut=True) + " passe dans : " + monde.data["salles"][salle]["nom"] + ".",
                    "deplacement")
        from .eau import tremper
        tremper(monde, id)
    else:
        placer(o, salle, list(case))
    return tourner + (PAS_FEUTRE if feutre else PAS)


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
    from .spatial import position_cible
    o = monde.objets[id]
    ici, depart = o["lieu"], tuple(o["position"])
    proches = []
    for x in [*pnjs(monde), "joueur"]:
        if x == id or _cru(monde, id, x, "fiable") is not True or salle_crue(monde, id, x) != ici:
            continue
        p = tuple(monde.joueur["position"]) if x == "joueur" else position_cible(monde, x, ici)
        if p is not None and (monde.joueur["salle"] if x == "joueur" else monde.objets[x]["lieu"]) == ici:
            proches.append((max(abs(p[0] - depart[0]), abs(p[1] - depart[1])), x, p))
    if not proches or min(proches)[0] <= 1:
        return None
    _, _, p = min(proches)
    return _marcher(monde, id, lambda salle, case: salle == ici and max(abs(case[0] - p[0]), abs(case[1] - p[1])) == 1,
                    lignes)


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


OUIE = 6               # cases : un pas, un geste, une voix s'entendent d'aussi près, même dans le dos
OUIE_FEUTRE = 1        # case : un pas feutré ne s'entend que de la case voisine


def de_pres(monde, a, b):
    """Assez près pour s'entendre : même salle, à moins de ``OUIE`` cases (ou sans cases, la
    même salle). ``b`` peut être le joueur."""
    def place(x):
        if x == "joueur":
            return monde.joueur["salle"], monde.joueur.get("position")
        return monde.objets[x]["lieu"], monde.objets[x].get("position")
    (sa, pa), (sb, pb) = place(a), place(b)
    if sa != sb:
        return False
    if not monde.data.get("mode_cases") or pa is None or pb is None:
        return True
    return max(abs(pa[0] - pb[0]), abs(pa[1] - pb[1])) <= OUIE


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


def alerter(monde, auteur, t, libre, portee=OUIE):
    """Ceux qui, tout près, entendent l'auteur (un PNJ ou le joueur) sans le voir se tournent vers
    lui : le temps de la rotation retarde la fin de leur geste en cours (``libre`` pendant la vie
    des PNJ, sinon l'instant mémorisé de chacun)."""
    from .spatial import QUART, orientation_vers, quarts
    if auteur == "joueur":
        salle, position = monde.joueur["salle"], monde.joueur.get("position")
    else:
        salle, position = monde.objets[auteur]["lieu"], monde.objets[auteur].get("position")
    if position is None:
        return
    for id in pnjs(monde):
        o = monde.objets[id]
        if (id == auteur or o["lieu"] != salle or "position" not in o or not o.get("profil")
                or max(abs(o["position"][0] - position[0]), abs(o["position"][1] - position[1])) > portee
                or percoit(monde, id, auteur)):
            continue
        vers = orientation_vers(tuple(o["position"]), tuple(position))
        if vers is None:
            continue
        rotation = QUART * quarts(o.get("orientation"), vers)
        if libre is None:
            e = esprit(monde, id)
            e["libre"] = max(e["libre"], t) + rotation
        else:
            libre[id] = max(libre[id], t) + rotation
        o["orientation"] = vers
        percevoir(monde, id)


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
    if strategie and operation == "aller" and chemin(monde, id, o["lieu"], etape["lieu"]) is None:
        terminer(monde, id, False, etape)  # Aucun passage qu'il croie ouvert : la stratégie tombe.
        return reste
    if en_cases and "position" in o and operation == "aller":
        lieu = etape["lieu"]
        return _marcher(monde, id, lambda salle, case: salle == lieu, lignes) or reste
    if CONTACT.get(operation) and en_cases and etape["cible"] in monde.objets:
        from .spatial import position_cible, proche
        cru = lire(monde, id)["croyances"].get(etape["cible"], {}).get("lieu")
        if (not monde.present_physique(etape["cible"], salle=o["lieu"]) and cru and cru.get("salle") == o["lieu"]
                and cru.get("case") and "position" in o):
            # Il regarde là où il le croyait : s'il n'y est plus, il le constate.
            from .spatial import QUART, orientation_vers, quarts
            vers = orientation_vers(tuple(o["position"]), tuple(cru["case"]))
            if vers and vers != o.get("orientation"):
                duree = QUART * quarts(o.get("orientation"), vers)
                o["orientation"] = vers
                percevoir(monde, id)
                return duree
        if (not _porte(monde, etape["cible"], id) and not proche(monde, etape["cible"], id)
                and monde.present_physique(etape["cible"], salle=o["lieu"])):
            # Il s'approche pas à pas ; l'absence de témoin se juge ensuite sur place.
            p = position_cible(monde, etape["cible"], o["lieu"])
            ici = o["lieu"]
            pas = p is not None and _marcher(monde, id, lambda salle, case: salle == ici and max(
                abs(case[0] - p[0]), abs(case[1] - p[1])) == 1, lignes)
            return pas or reste
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
            # qu'au geste suivant, si personne ne l'a vu entre-temps.
            balayages = monde.__dict__.setdefault("_balayages", {})
            ici = (o["lieu"], tuple(o["position"]))
            dernier = balayages.get(id)
            observe = None
            if not dernier or dernier[0] != ici or t - dernier[1] > 2 * TOUR:
                balayages[id] = (ici, t)
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
    tourner = _faire_face(monde, id, etape["cible"]) if en_cases else 0
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


def avancer(monde, minutes, lignes, dixiemes=None):
    """Fait vivre les PNJ pendant le temps qui vient de s'écouler (``minutes``, ou ``dixiemes``
    à la seconde près), jusqu'à l'heure courante ; renvoie ceux apparus dans la perception du
    joueur."""
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
    vus = {id: monde.visible(id) for id in ids}
    apparus = []
    # Les gestes illicites en cours : quiconque voit leur auteur avant qu'il ait fini en est témoin.
    temoignages = monde.__dict__.setdefault("_gestes_en_cours", {})
    temoignages.clear()
    libre = {id: max(debut, esprit(monde, id)["libre"]) for id in ids}
    t = debut
    while True:
        frontiere = (t // MINUTE + 1) * MINUTE
        prochain = min(libre.values(), default=fin + 1)
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
            continue
        t = prochain
        monde.data["minutes"], monde.data["dixiemes"] = divmod(t, MINUTE)
        for id in ids:
            if libre[id] != t:
                continue
            # Ceux qui l'ont vu pendant son geste précédent s'en souviennent aussi.
            temoignages.pop(id, None)
            intention = lire(monde, id)["intention"]
            # Désœuvré ou guettant une occasion, il a le temps de confier ce qu'il sait.
            if (not intention or intention["attente"] and temoins_crus(monde, id)) and bavarder(monde, id, lignes):
                duree = DUREES["dire"] if monde.data.get("mode_cases") else _jusqu_a_la_minute(t)
            elif intention:
                gestes = []
                avant = (monde.objets[id]["lieu"], list(monde.objets[id].get("position", [])))
                duree = agir(monde, id, t, lignes, gestes)
                temoignages[id] = gestes
                percevoir(monde, id)
                if gestes or avant != (monde.objets[id]["lieu"], monde.objets[id].get("position", [])):
                    # Un pas, un geste font du bruit : qui l'entend de près sans le voir se retourne.
                    feutre = not gestes and monde.__dict__.get("_pas_feutres", {}).pop(id, False)
                    alerter(monde, id, t, libre, OUIE_FEUTRE if feutre else OUIE)
                temoigner_en_cours(monde)
                _annoncer_presences(monde, vus, apparus, lignes)
            else:
                duree = _jusqu_a_la_minute(t)
            libre[id] = t + max(1, duree)
    temoigner_en_cours(monde)
    temoignages.clear()
    for id in ids:
        esprit(monde, id)["libre"] = libre[id]
    monde.data["minutes"], monde.data["dixiemes"] = fin_minutes, fin_dixiemes
    _annoncer_presences(monde, vus, apparus, lignes)
    return apparus
