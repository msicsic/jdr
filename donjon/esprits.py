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
RECENT = 30            # minutes pendant lesquelles ce qu'on a vu, ou ce qu'on vient d'entendre, fait foi
SOURCES = ("vu", "savoir", "essai")
ETATS_VISIBLES = {"porte": ("ouverte",), "contenant": ("ouverte",), "luminaire": ("allume", "faible", "charge"),
                  "nourriture": ("disponible",), "consommable": ("disponible",)}
# Un objet porté par quelqu'un d'autre ne se remarque que s'il est encombrant ou allumé.
MASSE_APPARENTE_KG = 1
LONGUEUR_APPARENTE_CM = 50


def pnjs(monde):
    return [id for id, o in monde.objets.items() if o["type"] == "personnage"]


CHAMPS = {"croyances": dict, "memoire": list, "intention": lambda: None,
          "besoins": dict, "pulsions": list, "renoncements": dict, "visites": dict, "engagements": list}
ETAPE = {"operation", "cible", "outil", "lieu", "condition"}
CLES_INTENTION = {"but", "motif", "plan", "depuis", "attente"}


def lire(monde, id):
    """Esprit en lecture seule : une consultation ne crée rien dans l'état."""
    return monde.data.get("esprits", {}).get(id) or {k: f() for k, f in CHAMPS.items()}


def esprit(monde, id):
    e = monde.data.setdefault("esprits", {}).setdefault(id, {})
    for cle, defaut in CHAMPS.items():
        e.setdefault(cle, defaut())
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
            e["intention"] = {"but": {"type": "rejoindre", "lieu": trajet["vers"]}}
        i = e["intention"]
        if i is not None and set(i) != CLES_INTENTION:
            # Intention du jalon A : un réflexe d'alerte, sans plan enregistré.
            e["intention"] = {"but": i["but"], "motif": "alerte", "plan": [
                {"operation": "aller", "cible": "", "outil": "", "lieu": i["but"]["lieu"], "condition": ""}],
                              "depuis": i.get("depuis", monde.data["minutes"]), "attente": 0}
        from .deliberation import installer as installer_besoins
        installer_besoins(monde, id)


def _croyance_valide(monde, attribut, c):
    assert (isinstance(c, dict) and isinstance(c.get("source"), str)
            and (c["source"] in SOURCES or c["source"].startswith("dit:")) and type(c.get("minute")) is int
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
        assert attribut in ("verrouillee", "fiable") and type(c.get("valeur")) is bool, "Attribut de croyance inconnu"


def verifier(monde):
    esprits = monde.data.get("esprits", {})
    assert isinstance(esprits, dict), "Esprits invalides"
    for id, e in esprits.items():
        assert id in monde.objets and monde.objets[id]["type"] == "personnage", "Esprit sans personnage"
        assert set(e) == set(CHAMPS), "Esprit mal formé"
        p = monde.objets[id].get("profil")
        if p is not None:
            from .deliberation import verifier_profil
            verifier_profil(monde, id, p)
        from .deliberation import seuils
        assert (isinstance(e["besoins"], dict) and set(e["besoins"]) <= (set(seuils(monde, id)) if p else set())
                and all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in e["besoins"].values())), "Besoins de PNJ invalides"
        assert (isinstance(e["pulsions"], list) and len(e["pulsions"]) in (0, len(p["pulsions"]) if p else 0)
                and all(type(v) is bool for v in e["pulsions"])), "Pulsions de PNJ invalides"
        assert all(type(v) is int for v in e["renoncements"].values()), "Renoncements invalides"
        assert all(s in monde.data["salles"] and type(v) is int for s, v in e["visites"].items()), "Visites invalides"
        for engagement in e["engagements"]:
            from .deliberation import condition_valide
            assert (isinstance(engagement, dict) and set(engagement) == {"condition", "pour", "minute"}
                    and condition_valide(monde, engagement["condition"]) and "periode" not in engagement["condition"]
                    and (engagement["pour"] == "joueur" or engagement["pour"] in monde.objets)
                    and type(engagement["minute"]) is int), "Engagement de PNJ invalide"
        for sujet, attributs in e["croyances"].items():
            assert isinstance(sujet, str) and isinstance(attributs, dict), "Sujet de croyance invalide"
            for attribut, c in attributs.items():
                _croyance_valide(monde, attribut, c)
        assert (isinstance(e["memoire"], list) and len(e["memoire"]) <= MEMOIRE_MAX
                and all(isinstance(s, dict) and isinstance(s.get("type"), str) and type(s.get("minute")) is int
                        for s in e["memoire"])), "Mémoire de PNJ invalide"
        i = e["intention"]
        assert i is None or (isinstance(i, dict) and set(i) == CLES_INTENTION
                             and isinstance(i["but"], dict) and isinstance(i["but"].get("type"), str)
                             and isinstance(i["motif"], str) and type(i["depuis"]) is int
                             and type(i["attente"]) is int and i["attente"] >= 0
                             and isinstance(i["plan"], list)), "Intention de PNJ invalide"
        if i:
            from .deliberation import OPERATIONS
            for etape in i["plan"]:
                # Un geste social porte son contenu : ce qui est affirmé, ou la tâche confiée.
                assert (isinstance(etape, dict) and set(etape) in (ETAPE, ETAPE | {"contenu"})
                        and etape["operation"] in OPERATIONS and isinstance(etape.get("contenu", {}), dict)
                        and etape["condition"] in ("", "sans_temoin")), "Étape de plan invalide"


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
    if niveau >= 2 and evenement["origine"] != monde.objets[id]["lieu"]:
        # Un bruit fort venu d'ailleurs, dont il ne voit pas la cause, inquiète.
        from .deliberation import inquieter
        inquieter(monde, id, "bruit")
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


def apparent(o):
    """Porté par quelqu'un, un objet ne se remarque que s'il est encombrant ou allumé."""
    return bool(o.get("allume") or o.get("masse", 0) >= MASSE_APPARENTE_KG
                or o.get("longueur_cm", 0) >= LONGUEUR_APPARENTE_CM)


def cache_par_porteur(monde, o, observateur):
    """Vrai pour un objet porté par un autre personnage que l'observateur et trop discret pour être vu."""
    porteur = _porteur(monde, o)
    return (porteur not in (None, observateur) and o["type"] != "partie_corps" and not apparent(o))


def _pertinent(monde, acteur, o):
    if (o["id"] == acteur or o.get("detail_local") or o.get("incorpore")
            or o["type"] in ("surface", "partie_corps")):
        return False
    return not cache_par_porteur(monde, o, acteur)


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
    """Le lieu où l'on attendait le sujet est-il sous les yeux du PNJ ?

    Sans case connue (un lieu qu'on lui a dit), il faut voir au moins la moitié de la salle.
    """
    if croyance["salle"] is None:
        return False
    if not monde.data.get("mode_cases"):
        return croyance["salle"] in champ
    if croyance["case"] is None:
        from .geometrie import cases
        sol = cases(monde.data["salles"][croyance["salle"]])
        return 2 * sum((croyance["salle"], x, y) in champ for x, y in sol) >= len(sol)
    return (croyance["salle"], *croyance["case"]) in champ


def reviser(monde, id, sujet, attribut, valeur, source="vu", **lieu):
    """Ce qu'il constate remplace ce qu'on lui a dit ; une contradiction trahit le locuteur.

    Passé ``RECENT`` minutes, le monde a pu changer depuis la parole : elle n'est que périmée.
    """
    ancienne = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    if (ancienne and ancienne["source"].startswith("dit:") and ancienne["valeur"] != valeur
            and monde.data["minutes"] - ancienne["minute"] <= RECENT):
        locuteur = ancienne["source"][4:]
        memoriser(monde, id, {"type": "mensonge_decouvert", "locuteur": locuteur, "sujet": sujet})
        if locuteur != id:
            croire(monde, id, locuteur, "fiable", False, "vu")
    croire(monde, id, sujet, attribut, valeur, source, **lieu)


def prete(monde, id, objet, a):
    return any(s["type"] == "pret" and s.get("objet") == objet and s.get("a") == a for s in lire(monde, id)["memoire"])


def _vu_porter(monde, id, sujet):
    """Le propriétaire qui voit son bien aux mains d'un autre, sans le lui avoir prêté, découvre un vol."""
    from .vol import proprietaire
    o = monde.objets[sujet]
    porteur = _porteur(monde, o)
    if (porteur in (None, id) or proprietaire(monde, o) != id or prete(monde, id, sujet, porteur)
            or any(s["type"] == "vu_porter" and s["auteur"] == porteur and s["objet"] == sujet
                   for s in lire(monde, id)["memoire"])):
        return
    from .deliberation import VOL, relancer
    memoriser(monde, id, {"type": "vu_porter", "auteur": porteur, "objet": sujet})
    croire(monde, id, porteur, "fiable", False, "vu")
    relancer(monde, id, "biens", VOL)


def constater(monde, id, sujet, source):
    """Croit l'état visible de l'objet tel qu'il est : vu, ou laissé ainsi de sa propre main."""
    o = monde.objets[sujet]
    etats = ETATS_VISIBLES.get(o["type"])
    if etats:
        from .perception import faible
        valeurs = {**o, "disponible": o.get("portions", o.get("charges", 0)) > 0, "faible": faible(o),
                   "charge": o.get("combustible", 0) > 0}
        croire(monde, id, sujet, "etat", {k: bool(valeurs.get(k)) for k in etats}, source)


def _flamme_sous_les_yeux(monde, id, sujet, lieu):
    """La place où il croit la source est-elle sous son regard ? Un objet fixe ne bouge pas."""
    o = monde.objets[sujet]
    if lieu and lieu["valeur"] is not None:
        salle, case = lieu.get("salle"), lieu.get("case")
    elif not o.get("mobile") and o["lieu"] in monde.data["salles"]:
        salle, case = o["lieu"], o.get("position")
    else:
        return False
    if salle is None or salle not in monde.data["salles"]:
        return False
    if not monde.data.get("mode_cases"):
        return monde.objets[id]["lieu"] == salle
    from .spatial import dans_le_regard
    return case is not None and dans_le_regard(monde, salle, case, id)


def percevoir(monde, id):
    """Révise les croyances d'un PNJ d'après ce qu'il perçoit maintenant."""
    vus, champ = percus(monde, id)
    croyances = esprit(monde, id)["croyances"]
    for sujet in [s for s in croyances if s != "joueur" and s not in monde.objets and s not in monde.data["salles"]]:
        del croyances[sujet]  # Objet détruit ou consommé : plus rien à croire à son sujet.
    salle = monde.objets[id]["lieu"]
    if salle in monde.data["salles"]:
        # Il sait si la salle où il se tient est éclairée, même sans en voir la source.
        from .perception import eclairage
        position = monde.objets[id].get("position") if monde.data.get("mode_cases") else None
        croire(monde, id, salle, "etat", {"eclairee": eclairage(monde, salle, position)["niveau"] > 0}, "vu")
    for sujet, (salle, case) in vus.items():
        if sujet == "joueur":
            croire(monde, id, "joueur", "lieu", salle, "vu", salle=salle, case=case)
            continue
        o = monde.objets[sujet]
        if o["type"] != "porte":
            reviser(monde, id, sujet, "lieu", o["lieu"], salle=salle, case=case)
            _vu_porter(monde, id, sujet)
        constater(monde, id, sujet, "vu")
        if o["type"] in ("porte", "contenant") and o.get("ouverte"):
            reviser(monde, id, sujet, "verrouillee", False)  # Ouvert sous ses yeux : pas verrouillé.
    for sujet, attributs in list(croyances.items()):
        etat = attributs.get("etat")
        if (sujet not in vus and sujet in monde.objets and "allume" in monde.objets[sujet]
                and etat and etat["valeur"].get("allume") and _flamme_sous_les_yeux(monde, id, sujet, attributs.get("lieu"))):
            # Une flamme se voit de loin, même dans le noir : là où il regarde, rien ne brille.
            # Ce qui reste à brûler ne se voit pas : un feu vu baisser s'est consumé ; un feu vu
            # vif a pu être éteint, il garde ce qu'il en croyait.
            valeur = etat["valeur"]
            reviser(monde, id, sujet, "etat", {**valeur, "allume": False, "faible": False,
                                               "charge": bool(valeur.get("charge")) and not valeur.get("faible")})
    for sujet, attributs in croyances.items():
        lieu = attributs.get("lieu")
        if sujet in vus or not lieu or lieu["valeur"] is None or not _observe(monde, champ, lieu):
            continue
        contenant = monde.objets.get(lieu["valeur"])
        if contenant and contenant["type"] == "contenant" and not contenant.get("ouverte"):
            continue  # Un contenant fermé peut toujours le cacher.
        if lieu["valeur"] == "joueur" or contenant and contenant["type"] == "personnage":
            continue  # Porté par quelqu'un : son absence de la case ne prouve rien.
        reviser(monde, id, sujet, "lieu", None, salle=None, case=None)
        if sujet != "joueur" and monde.objets[sujet]["type"] != "personnage":
            memoriser(monde, id, {"type": "absence", "objet": sujet, "salle": lieu["salle"]})
            from .vol import proprietaire
            if proprietaire(monde, monde.objets[sujet]) == id:
                from .deliberation import relancer
                relancer(monde, id, "biens", 30)


def percevoir_tous(monde):
    for id in pnjs(monde):
        percevoir(monde, id)
