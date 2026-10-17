"""Esprit des PNJ : ce qu'ils perçoivent, ce qu'ils croient et ce qu'ils retiennent.

Un PNJ perçoit avec les règles du joueur, depuis sa propre case : lumière, ligne de vue,
portes. Ses croyances portent une source, une minute et une confiance ; elles peuvent être
fausses ou périmées. Le moteur seul les révise ; Luna ne les modifie pas.

Croyances : ``croyances[sujet][attribut]``, le sujet étant un objet ou « joueur ».
- ``lieu`` : valeur = lieu direct (salle, porteur ou contenant) ou None si l'objet n'est plus
  là où on l'attendait ; ``salle`` et ``case`` disent où il a été vu.
- ``etat`` : état visible (porte ou contenant ouvert, luminaire allumé).
- ``verrouillee`` : appris par un essai ou un savoir, jamais par la vue.
"""
import copy

from .perception import eclairage

MEMOIRE_MAX = 40
SOURCES = ("vu", "savoir", "essai")
ETATS_VISIBLES = {"porte": ("ouverte",), "contenant": ("ouverte",), "luminaire": ("allume",)}
# Un objet porté par quelqu'un d'autre ne se remarque que s'il est encombrant ou allumé.
MASSE_APPARENTE_KG = 1
LONGUEUR_APPARENTE_CM = 50


def pnjs(monde):
    return [id for id, o in monde.objets.items() if o["type"] == "personnage"]


def lire(monde, id):
    """Esprit en lecture seule : une consultation ne crée rien dans l'état."""
    return monde.data.get("esprits", {}).get(id) or {"croyances": {}, "memoire": [], "intention": None}


def esprit(monde, id):
    e = monde.data.setdefault("esprits", {}).setdefault(id, {})
    e.setdefault("croyances", {})
    e.setdefault("memoire", [])
    e.setdefault("intention", None)
    return e


def installer(monde):
    monde.data.setdefault("esprits", {})
    for id in pnjs(monde):
        e = esprit(monde, id)
        o = monde.objets[id]
        # Anciennes parties : le dernier son et le trajet deviennent mémoire et intention.
        son = o.pop("dernier_son_entendu", None)
        if son and not any(s["type"] == "son" for s in e["memoire"]):
            e["memoire"].append({"type": "son", **son})
        trajet = o.pop("trajet", None)
        if trajet and e["intention"] is None:
            e["intention"] = {"but": {"type": "rejoindre", "lieu": trajet["vers"]},
                              "minutes": trajet["minutes"], "depuis": monde.data["minutes"]}


def _croyance_valide(monde, attribut, c):
    assert (isinstance(c, dict) and c.get("source") in SOURCES and type(c.get("minute")) is int
            and isinstance(c.get("confiance"), (int, float)) and 0 <= c["confiance"] <= 1), "Croyance mal formée"
    if attribut == "lieu":
        # Une croyance peut survivre à son objet (détruit, retiré) ; la perception la purge.
        assert (set(c) >= {"valeur", "salle", "case"}
                and (c["valeur"] is None or isinstance(c["valeur"], str))
                and (c["salle"] is None or c["salle"] in monde.data["salles"])
                and (c["case"] is None or (isinstance(c["case"], list) and len(c["case"]) == 2))), "Croyance de lieu invalide"
    elif attribut == "etat":
        assert isinstance(c.get("valeur"), dict) and all(type(v) is bool for v in c["valeur"].values()), "Croyance d'état invalide"
    else:
        assert attribut == "verrouillee" and type(c.get("valeur")) is bool, "Attribut de croyance inconnu"


def verifier(monde):
    esprits = monde.data.get("esprits", {})
    assert isinstance(esprits, dict), "Esprits invalides"
    for id, e in esprits.items():
        assert id in monde.objets and monde.objets[id]["type"] == "personnage", "Esprit sans personnage"
        assert set(e) == {"croyances", "memoire", "intention"}, "Esprit mal formé"
        for sujet, attributs in e["croyances"].items():
            assert isinstance(sujet, str) and isinstance(attributs, dict), "Sujet de croyance invalide"
            for attribut, c in attributs.items():
                _croyance_valide(monde, attribut, c)
        assert (isinstance(e["memoire"], list) and len(e["memoire"]) <= MEMOIRE_MAX
                and all(isinstance(s, dict) and isinstance(s.get("type"), str) and type(s.get("minute")) is int
                        for s in e["memoire"])), "Mémoire de PNJ invalide"
        i = e["intention"]
        assert i is None or (isinstance(i, dict) and set(i) == {"but", "minutes", "depuis"}
                             and i["but"].get("type") == "rejoindre" and i["but"].get("lieu") in monde.data["salles"]
                             and type(i["minutes"]) is int and i["minutes"] >= 0
                             and type(i["depuis"]) is int), "Intention de PNJ invalide"


def croire(monde, id, sujet, attribut, valeur, source, confiance=1.0, **lieu):
    monde_minute = monde.data["minutes"]
    croyance = {"valeur": valeur, "source": source, "minute": monde_minute, "confiance": confiance, **lieu}
    esprit(monde, id)["croyances"].setdefault(sujet, {})[attribut] = croyance


def memoriser(monde, id, evenement):
    memoire = esprit(monde, id)["memoire"]
    memoire.append({"minute": monde.data["minutes"], **evenement})
    del memoire[:-MEMOIRE_MAX]


def dernier_son(monde, id):
    sons = [s for s in lire(monde, id)["memoire"] if s["type"] == "son"]
    return {k: v for k, v in copy.deepcopy(sons[-1]).items() if k not in ("type", "niveau")} if sons else None


def entendre(monde, id, evenement, niveau):
    """Un PNJ entend un son : souvenir, puis réflexe déclaré s'il y en a un."""
    memoriser(monde, id, {"type": "son", **{k: v for k, v in evenement.items() if k != "auditeurs"}, "niveau": niveau})
    from .pnj import reagir
    reagir(monde, id, evenement["origine"], niveau)


def _porteur(monde, o):
    """Personnage (ou joueur) qui porte l'objet, s'il y en a un."""
    vus, lieu = set(), o["lieu"]
    while lieu in monde.objets and lieu not in vus:
        vus.add(lieu)
        if monde.objets[lieu]["type"] == "personnage":
            return lieu
        lieu = monde.objets[lieu]["lieu"]
    return "joueur" if lieu == "joueur" else None


def _pertinent(monde, acteur, o):
    if (o["id"] == acteur or o.get("detail_local") or o.get("incorpore")
            or o["type"] in ("surface", "partie_corps")):
        return False
    porteur = _porteur(monde, o)
    if porteur is None or porteur == acteur:
        return True
    return bool(o.get("allume") or o.get("masse", 0) >= MASSE_APPARENTE_KG
                or o.get("longueur_cm", 0) >= LONGUEUR_APPARENTE_CM)


def percus(monde, acteur):
    """Entités perçues maintenant par un PNJ et lieux observés : {id: (salle, case)}, champ."""
    from .spatial import porte_par, position_cible
    salle = monde.objets[acteur]["lieu"]
    # Ce qu'il porte lui-même, il le sait sans le voir.
    vus = {id: (None, None) for id, o in monde.objets.items()
           if porte_par(monde, id, acteur) and _pertinent(monde, acteur, o)}
    if salle not in monde.data["salles"]:
        return vus, set()
    if monde.data.get("mode_cases"):
        from .spatial import champ_visible, visible
        champ = champ_visible(monde, acteur)
        for id, o in monde.objets.items():
            if id in vus or not _pertinent(monde, acteur, o) or not visible(monde, id, acteur, champ):
                continue
            vus[id] = next(((s, list(p)) for s in monde.data["salles"]
                            for p in [position_cible(monde, id, s)]
                            if p is not None and (s, p[0], p[1]) in champ), (salle, None))
        j = monde.joueur
        if (j["salle"], *j["position"]) in champ:
            vus["joueur"] = (j["salle"], list(j["position"]))
        return vus, champ
    if eclairage(monde, salle)["niveau"] == 0:
        return vus, set()
    for id, o in monde.objets.items():
        if id not in vus and _pertinent(monde, acteur, o) and monde.present_physique(id, salle=salle):
            vus[id] = (salle, None)
    if monde.joueur["salle"] == salle:
        vus["joueur"] = (salle, None)
    return vus, {salle}


def percoit(monde, acteur, sujet):
    return sujet in percus(monde, acteur)[0]


def _observe(monde, champ, croyance):
    """Le lieu où l'on attendait le sujet est-il sous les yeux du PNJ ?"""
    if croyance["salle"] is None:
        return False
    if not monde.data.get("mode_cases"):
        return croyance["salle"] in champ
    return croyance["case"] is not None and (croyance["salle"], *croyance["case"]) in champ


def percevoir(monde, id):
    """Révise les croyances d'un PNJ d'après ce qu'il perçoit maintenant."""
    vus, champ = percus(monde, id)
    croyances = esprit(monde, id)["croyances"]
    for sujet in [s for s in croyances if s != "joueur" and s not in monde.objets]:
        del croyances[sujet]  # Objet détruit ou consommé : plus rien à croire à son sujet.
    for sujet, (salle, case) in vus.items():
        if sujet == "joueur":
            croire(monde, id, "joueur", "lieu", salle, "vu", salle=salle, case=case)
            continue
        o = monde.objets[sujet]
        if o["type"] != "porte":
            croire(monde, id, sujet, "lieu", o["lieu"], "vu", salle=salle, case=case)
        etats = ETATS_VISIBLES.get(o["type"])
        if etats:
            croire(monde, id, sujet, "etat", {k: bool(o.get(k)) for k in etats}, "vu")
        if o["type"] == "porte" and o.get("ouverte"):
            croire(monde, id, sujet, "verrouillee", False, "vu")
    for sujet, attributs in croyances.items():
        lieu = attributs.get("lieu")
        if sujet in vus or not lieu or lieu["valeur"] is None or not _observe(monde, champ, lieu):
            continue
        contenant = monde.objets.get(lieu["valeur"])
        if contenant and contenant["type"] == "contenant" and not contenant.get("ouverte"):
            continue  # Un contenant fermé peut toujours le cacher.
        if lieu["valeur"] == "joueur" or contenant and contenant["type"] == "personnage":
            continue  # Porté par quelqu'un : son absence de la case ne prouve rien.
        croire(monde, id, sujet, "lieu", None, "vu", salle=None, case=None)
        if sujet != "joueur" and monde.objets[sujet]["type"] != "personnage":
            memoriser(monde, id, {"type": "absence", "objet": sujet, "salle": lieu["salle"]})


def percevoir_tous(monde):
    for id in pnjs(monde):
        percevoir(monde, id)
