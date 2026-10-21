"""Esprit des PNJ : ce qu'ils perçoivent, ce qu'ils croient et ce qu'ils retiennent.

Un PNJ perçoit avec les règles du joueur, depuis sa propre case : lumière, ligne de vue,
portes. Ses croyances portent une source, une minute et une confiance ; elles peuvent être
fausses ou périmées. Le moteur seul les révise ; Luna ne les modifie pas.

Croyances : ``croyances[sujet][attribut]``, le sujet étant un objet ou « joueur ».
- ``lieu`` : valeur = lieu direct (salle, porteur ou contenant) ou None si l'objet n'est plus
  là où on l'attendait ; ``salle`` et ``case`` disent où il a été vu.
- ``etat`` : état visible (porte ou contenant ouvert, luminaire allumé ; d'un personnage, ce
  qui presse son corps : ``{"faim", "chaleur", "repos"}``).
- ``verrouillee`` : appris par un essai ou un savoir, jamais par la vue.
- ``eau`` (sujet : une salle) : l'eau qu'il y a vue, en cm (``eau.py``).

Voix : ``voix`` liste ceux qu'il connaît (qu'il a vus, ou entendus parler en les sachant là) : il
reconnaît leur voix quand il en saisit les mots (``ouie.entendre``). Le joueur a la même liste dans
``data["voix_connues"]``.
"""
import copy

from .perception import eclairage

MEMOIRE_MAX = 40
RECENT = 30            # minutes pendant lesquelles ce qu'on a vu, ou ce qu'on vient d'entendre, fait foi
SOURCES = ("vu", "savoir", "essai", "entendu")
ETATS_VISIBLES = {"porte": ("ouverte",), "contenant": ("ouverte",), "luminaire": ("allume", "faible", "charge"),
                  "nourriture": ("disponible",), "consommable": ("disponible",)}
# Un objet porté par quelqu'un d'autre ne se remarque que s'il est encombrant ou allumé.
MASSE_APPARENTE_KG = 1
LONGUEUR_APPARENTE_CM = 50


def pnjs(monde):
    return [id for id, o in monde.objets.items() if o["type"] == "personnage"]


CHAMPS = {"croyances": dict, "memoire": list, "intention": lambda: None,
          "besoins": dict, "pulsions": list, "renoncements": dict, "visites": dict, "engagements": list,
          "libre": int,   # libre : l'instant (dixièmes de seconde) où il aura fini son geste en cours
          "balayage": lambda: None,   # son dernier tour d'horizon : {salle, case, instant}
          "voix": list}   # ceux qu'il connaît, vus ou entendus parler : il reconnaît leur voix
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


CONNAISSANCE = ("vu", "savoir", "essai", "entendu")


def installer(monde):
    monde.data.setdefault("esprits", {})
    personnages = set(pnjs(monde)) | {"joueur"}
    for id in pnjs(monde):
        nouveau = "voix" not in monde.data["esprits"].get(id, {})
        e = esprit(monde, id)
        if nouveau:
            # Scénarios et anciennes parties : il connaît ceux dont il sait quelque chose de
            # première main ou de savoir (pas d'un ouï-dire).
            e["voix"] = sorted(x for x, attributs in e["croyances"].items() if x in personnages and x != id
                               and any(c.get("source") in CONNAISSANCE for c in attributs.values()))
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
    # Le joueur : ceux qu'il a vus de près (portrait retenu) ou dont il a appris l'identité.
    monde.data.setdefault("voix_connues", sorted(
        x for x in {*monde.data.get("souvenirs_personnages", {}), *monde.data.get("connus", [])}
        if x in monde.objets and monde.objets[x]["type"] == "personnage"))


def connait(monde, qui, autre):
    """``qui`` (un PNJ ou le joueur) connaît-il ``autre`` (vu, ou entendu parler) ? Il reconnaît
    alors sa voix."""
    if qui == "joueur":
        return autre in monde.data.get("voix_connues", [])
    return autre in lire(monde, qui)["voix"]


def connaitre(monde, qui, autre):
    """``qui`` connaît désormais ``autre`` : il l'a vu, ou a reconnu sa voix."""
    connus = monde.data.setdefault("voix_connues", []) if qui == "joueur" else esprit(monde, qui)["voix"]
    if autre != qui and autre not in connus:
        connus.append(autre)


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
    elif attribut == "eau":
        # La hauteur vue ; le niveau qu'elle donnait, le repère et la vitesse qu'on en tire.
        assert (type(c.get("valeur")) is int and c["valeur"] >= 0
                and all(c.get(k) is None or type(c[k]) is int for k in ("niveau", "montee"))
                and (c.get("repere") is None or isinstance(c["repere"], list) and len(c["repere"]) == 2
                     and all(type(v) is int for v in c["repere"]))), "Croyance d'eau invalide"
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
        # Satisfaite (True), rompue (False), jamais satisfaite depuis qu'il la connaît (None).
        assert (isinstance(e["pulsions"], list) and len(e["pulsions"]) in (0, len(p["pulsions"]) if p else 0)
                and all(v is None or type(v) is bool for v in e["pulsions"])), "Pulsions de PNJ invalides"
        assert all(type(v) is int for v in e["renoncements"].values()), "Renoncements invalides"
        assert type(e["libre"]) is int and e["libre"] >= 0, "Geste en cours de PNJ invalide"
        b = e["balayage"]
        assert b is None or (isinstance(b, dict) and set(b) == {"salle", "case", "instant"}
                             and b["salle"] in monde.data["salles"] and isinstance(b["case"], list)
                             and len(b["case"]) == 2 and all(type(v) is int for v in b["case"])
                             and type(b["instant"]) is int and b["instant"] >= 0), "Tour d'horizon de PNJ invalide"
        assert all(s in monde.data["salles"] and type(v) is int for s, v in e["visites"].items()), "Visites invalides"
        assert isinstance(e["voix"], list) and all(
            isinstance(x, str) for x in e["voix"]  # Comme une croyance, il survit à qui a quitté la partie.
        ) and len(set(e["voix"])) == len(e["voix"]), "Voix connues invalides"
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
    """Un PNJ entend un son émis (un appel, un cri, le son d'un objet) : souvenir, puis réflexe
    déclaré s'il y en a un. Ce que le bruit lui fait craindre relève de l'ouïe commune (``ouie``)."""
    memoriser(monde, id, {"type": "son", **{k: v for k, v in evenement.items() if k != "auditeurs"}, "niveau": niveau})
    from .pnj import reagir
    reagir(monde, id, evenement["origine"], niveau, evenement.get("auteur"))


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


def _remarquable(acteur, o):
    """Ni lui-même, ni un détail, ni ce qui est incorporé, ni une surface ou une partie du corps."""
    return not (o["id"] == acteur or o.get("detail_local") or o.get("incorpore")
                or o["type"] in ("surface", "partie_corps"))


def _pertinent(monde, acteur, o):
    return _remarquable(acteur, o) and not cache_par_porteur(monde, o, acteur)


def percus(monde, acteur):
    """Entités perçues maintenant par un PNJ et lieux observés : {id: (salle, case)}, champ.

    Pendant la vie des PNJ (``spatial.vue_memorisee``), la perception d'un acteur est gardée tant
    que l'état dont elle dépend n'a pas changé (``spatial.etat_vue``)."""
    from .spatial import _memo_vue, a_verifier, sans_memoire
    memo = _memo_vue(monde) if monde.data.get("mode_cases") else None
    if memo is None:
        return _percus(monde, acteur, None)
    if ("percus", acteur) not in memo:
        memo["percus", acteur] = _percus(monde, acteur, memo)
    vus, champ = memo["percus", acteur]
    if a_verifier():
        with sans_memoire(monde):
            frais = _percus(monde, acteur, None)
        assert frais == (vus, champ), f"Perception mémorisée périmée : {acteur}"
    return {id: (s, None if c is None else list(c)) for id, (s, c) in vus.items()}, set(champ)


def _percus(monde, acteur, memo):
    from .spatial import porte_par, poses as salles_posees
    salle = monde.objets[acteur]["lieu"]
    poses = salles_posees(monde, memo)
    # Ce qu'il porte lui-même, il le sait sans le voir.
    vus = {id: (None, None) for id, o in monde.objets.items()
           if poses[id] in (None, acteur) and porte_par(monde, id, acteur) and _pertinent(monde, acteur, o)}
    if salle not in monde.data["salles"]:
        return vus, set()
    if monde.data.get("mode_cases"):
        from .spatial import _champ, _murs, _position_vue
        champ = _champ(monde, acteur, memo)
        salles_du_champ = {c[0] for c in champ}
        salles_vues = [s for s in monde.data["salles"] if s in salles_du_champ]
        for id, o in monde.objets.items():
            if id in vus or not _remarquable(acteur, o):
                continue
            # ``visible``, sans le cas des surfaces, qui ne sont pas pertinentes : la première place
            # dans le champ, et l'objet accroché au mur n'est vu que si ce mur l'est.
            pose = poses[id]
            if pose is not None and pose not in salles_du_champ:
                continue
            premiere, vu = None, False
            for s in salles_vues if pose is None else (pose,):
                p = _position_vue(monde, memo, id, s)
                if p is None or (s, p[0], p[1]) not in champ:
                    continue
                if premiere is None:
                    premiere = (s, list(p))
                ancrage = o.get("ancrage_carte")
                if ancrage and tuple(ancrage) not in _murs(monde, champ, acteur, memo).get(s, set()):
                    continue
                vu = True
                break
            if vu and not cache_par_porteur(monde, o, acteur):
                vus[id] = premiere
        j = monde.joueur
        if (j["salle"], *j["position"]) in champ:
            vus["joueur"] = (j["salle"], list(j["position"]))
        return vus, set(champ)
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

    Passé ``RECENT`` minutes, le monde a pu changer depuis la parole : elle n'est que périmée. Un
    objet qu'il voit dans les mains de quelqu'un a pu être déplacé depuis : ce n'est pas un démenti.
    """
    ancienne = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    porte = attribut == "lieu" and (valeur == "joueur" or monde.objets.get(valeur or "", {}).get("type") == "personnage")
    if (ancienne and ancienne["source"].startswith("dit:") and ancienne["valeur"] != valeur and not porte
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
    """Croit l'état visible de l'objet tel qu'il est : vu, ou laissé ainsi de sa propre main.
    D'un personnage, joueur compris, se voit ce qui presse son corps : la faim, le froid, la
    fatigue (``corps``), sous les noms des besoins du corps."""
    if sujet == "joueur" or monde.objets[sujet]["type"] == "personnage":
        from .corps import CORPS
        besoins = monde.joueur.get("besoins", {}) if sujet == "joueur" else lire(monde, sujet)["besoins"]
        if besoins:
            croire(monde, id, sujet, "etat",
                   {nom: besoins.get(nom, 0) >= regle["urgence"] for nom, regle in CORPS.items()}, source)
        return
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
    from .spatial import etat_fige
    with etat_fige(monde):  # Percevoir ne révise que son esprit.
        _percevoir(monde, id)


def _percevoir(monde, id):
    vus, champ = percus(monde, id)
    croyances = esprit(monde, id)["croyances"]
    for sujet in [s for s in croyances if s != "joueur" and s not in monde.objets and s not in monde.data["salles"]]:
        del croyances[sujet]  # Objet détruit ou consommé : plus rien à croire à son sujet.
    salle = monde.objets[id]["lieu"]
    if salle in monde.data["salles"]:
        # Il sait si la salle où il se tient est éclairée, même sans en voir la source. C'est le
        # lieu qu'il juge : la lumière qu'on porte, lui ou un autre, n'y compte pas, elle suit
        # son porteur (il sait ce qu'il porte, il voit ce que portent les autres).
        from .perception import eclairage
        position = monde.objets[id].get("position") if monde.data.get("mode_cases") else None
        eclairee = any(c["niveau"] > 0 and not (c["source"] in monde.objets
                                                 and _porteur(monde, monde.objets[c["source"]]) is not None)
                       for c in eclairage(monde, salle, position)["contributions"])
        croire(monde, id, salle, "etat", {"eclairee": eclairee}, "vu")
    from .eau import percevoir as percevoir_eau
    percevoir_eau(monde, id)
    for sujet, (salle, case) in vus.items():
        if sujet == "joueur" or monde.objets[sujet]["type"] == "personnage":
            connaitre(monde, id, sujet)  # Il l'a vu : il saura reconnaître sa voix.
        if sujet == "joueur":
            croire(monde, id, "joueur", "lieu", salle, "vu", salle=salle, case=case)
            constater(monde, id, "joueur", "vu")
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
        if sujet in monde.objets and monde.objets[sujet]["type"] != "personnage" and not monde.objets[sujet].get("mobile"):
            continue  # Un objet fixe fait partie du lieu : ne pas le voir d'ici ne le déplace pas.
        reviser(monde, id, sujet, "lieu", None, salle=None, case=None)
        if sujet != "joueur" and monde.objets[sujet]["type"] != "personnage":
            memoriser(monde, id, {"type": "absence", "objet": sujet, "salle": lieu["salle"]})
            from .vol import proprietaire
            if proprietaire(monde, monde.objets[sujet]) == id:
                from .deliberation import relancer
                relancer(monde, id, "biens", 30)


def percevoir_tous(monde):
    from .spatial import vue_memorisee
    with vue_memorisee(monde):
        for id in pnjs(monde):
            percevoir(monde, id)
