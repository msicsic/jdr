"""Prises et liens : mêmes validations et issues différées pour tous les acteurs."""
from . import corps
from .caractere import modificateur
from .combat import voit, rotation
from .monde import ErreurMonde
from .passage import au_contact
from .temps import instant

DUREES = {"saisir": 20, "ligoter": 300, "delier": 100, "liberer": 6000, "trainer": 45, "tuer": 300}
PAROLES = {"dire", "parler", "crier", "cri", "appeler", "siffler", "se_rendre"}
IMMOBILES = {"trainer", "marcher", "aller", "faufiler", "chasser", "fuir", "fuite", "passer_obstacle", "franchir", "sauter", "franchir_obstacle"}
SANS_MAINS = PAROLES | {"attendre", "patienter", "reposer", "observer", "examiner", "ecouter", "tourner", "degager", "liberer", "emettre_son"}


def valider_verrouillage(monde, auteur, cible, outil):
    from .spatial import porte_par
    o = monde.objets.get(cible, {})
    if o.get("type") not in ("porte", "contenant"):
        raise ErreurMonde("Il faut viser une porte ou un contenant.", f"cible={cible} : type porte ou contenant requis.")
    if o.get("ouverte"):
        raise ErreurMonde("Il faut d'abord fermer.", f"cible={cible}, ouverte=True : ouverte=False requis.")
    if o.get("verrouillee"):
        raise ErreurMonde("C'est déjà verrouillé.", f"cible={cible}, verrouillee=True : verrouillee=False requis.")
    if not o.get("integrite") or o.get("detachee"):
        raise ErreurMonde("Le battant ne peut plus être verrouillé.", f"cible={cible} : integrite>0 et detachee=False requis.")
    if not outil or not porte_par(monde, outil, auteur):
        raise ErreurMonde("Il faut une clé en main.", f"outil={outil} : clé portée par auteur={auteur} requise.")
    if cible not in monde.objets[outil].get("ouvre", ()):
        raise ErreurMonde("Cette clé n'ouvre pas la serrure.", f"outil={outil} : ouvre contenant cible={cible} requis.")


def sorties_crues(monde, auteur, salle, fermee=None):
    """Issues connues : inconnu ne signifie jamais verrouillé."""
    from .esprits import lire
    sorties = monde.data["salles"][salle].get("sorties", {}).values()
    croyances = lire(monde, auteur)["croyances"] if auteur != "joueur" else {}
    resultat = []
    for s in sorties:
        p = s.get("porte")
        if fermee is not None and p == fermee:
            verrou = True
        elif auteur == "joueur":
            # Le rendu montre le verrou visible ; hors de vue, seule la mémoire répond.
            verrou = (monde.objets[p].get("verrouillee") is True if p and monde.visible(p)
                      else monde.data.get("verrous_joueur", {}).get(p) is True)
        else:
            verrou = croyances.get(p, {}).get("verrouillee", {}).get("valeur") is True
        resultat.append((p, verrou))
    return resultat


def captif(monde, auteur):
    """Liens éprouvés ou toutes les issues crues verrouillées ; jamais les verrous réels."""
    if corps.corps(monde, auteur).get("lie"):
        return True
    salle = monde.joueur["salle"] if auteur == "joueur" else monde.objets[auteur]["lieu"]
    issues = sorties_crues(monde, auteur, salle)
    from .pnj import _cle_portee
    return bool(issues) and all(v and _cle_portee(monde, auteur, p) is None for p, v in issues)


def enfermer(monde, auteur, porte, fin):
    """Le verrouillage qualifié par les seules présences et issues crues de l'auteur."""
    from .esprits import lire
    from .pnj import commencer_geste
    from .spatial import memoriser as memoriser_vue
    if monde.objets[porte]["type"] != "porte":
        return
    if auteur == "joueur":
        memoriser_vue(monde)
        lieux = {i: s["salle"] for i, s in monde.data.get("souvenirs_visuels", {}).items()}
    else:
        lieux = {i: c.get("lieu", {}).get("valeur")
                 for i, c in lire(monde, auteur)["croyances"].items()}
    for salle, piece in monde.data["salles"].items():
        if not any(s.get("porte") == porte for s in piece.get("sorties", {}).values()):
            continue
        issues = sorties_crues(monde, auteur, salle, porte)
        if not issues or not all(v for _, v in issues):
            continue
        for victime, lieu in sorted(lieux.items()):
            if victime != auteur and lieu == salle and corps.vivant(monde, victime):
                g = commencer_geste(monde, auteur, "enfermer", victime, fin, exclus=(victime,) if victime != "joueur" else ())
                g["porte"] = porte
                corps.evenement(monde, "enfermer", victime, auteur=auteur, porte=porte)


def constater_enfermement(monde, auteur):
    """Appelé après un essai de porte ; aucune connaissance de son geôlier n'en découle."""
    from .esprits import memoriser
    salle = monde.objets[auteur]["lieu"]
    issues = sorties_crues(monde, auteur, salle)
    if issues and all(v for _, v in issues):
        captifs = monde.data.setdefault("captivites_constatees", {})
        if captifs.get(auteur) != salle:
            captifs[auteur] = salle
            memoriser(monde, auteur, {"type": "enferme", "salle": salle})
            from .ecoute import appel
            appel(monde, auteur)


def evasion(monde, auteur):
    """Un constat de captivité ouvre un but de sortie dans le graphe ordinaire."""
    from .planification import chercher, _couper
    salle = monde.objets[auteur]["lieu"]
    if monde.data.get("captivites_constatees", {}).get(auteur) != salle:
        monde.data.get("captivites_constatees", {}).pop(auteur, None)
        return None
    issues = sorties_crues(monde, auteur, salle)
    if not issues or not all(v for _, v in issues):
        monde.data["captivites_constatees"].pop(auteur, None)
        return None
    r = chercher(monde, auteur, lambda v, et: et.salle != salle, {"evader": True},
                 nom="evader", memo=["evader", salle], emplois=(), motif="securite")
    if r:
        return {"type": "evader", "lieu": salle}, _couper(r[1])
    return {"type": "evader", "lieu": salle}, []


def autoriser(monde, auteur, operation):
    """Contrat du corps, consulté avant toute action, y compris les déplacements."""
    c = corps.corps(monde, auteur)
    if c.get("lie") and operation not in SANS_MAINS:
        raise ErreurMonde("Les liens t'empêchent de faire ce geste.",
                          f"auteur={auteur}, corps.lie={c['lie']['lien']}, operation={operation} : geste sans mains requis, ou liberer.")
    if c.get("tenu_par") and operation in IMMOBILES:
        raise ErreurMonde("Quelqu'un te retient sur place.",
                          f"auteur={auteur}, corps.tenu_par={c['tenu_par']}, operation={operation} : degager avant un déplacement.")


def bilan(monde, depuis, lignes):
    """Rendre les seules issues achevées et perçues, sans annoncer le succès au départ."""
    from .francais import designer, sujet
    for e in monde.data.get("historique_corps", ())[depuis:]:
        op = e["type"]
        if op not in ("ligoter", "delier", "liberer", "liberation_manquee", "geste_interrompu", "trainer", "tuer"):
            continue
        a, cible = e["auteur"], e["id"]
        if a == "joueur":
            textes = {"tuer": "Tu as tué cette personne.", "trainer": "Tu as traîné le corps d’une case.", "ligoter": "La personne est maintenant ligotée.", "delier": "Tu as défait ses liens.",
                      "liberer": "Tu as défait tes liens.", "liberation_manquee": "Tu ne parviens pas à défaire tes liens.",
                      "geste_interrompu": "Les conditions du geste ne tiennent plus ; il n'aboutit pas."}
            lignes.append(textes[op])
        elif op == "trainer" and voit(monde, "joueur", a) and voit(monde, "joueur", cible):
            lignes.append(sujet(monde.objets[a]) + " a traîné " + ("ton corps" if cible == "joueur" else designer(monde.objets[cible])) + " d’une case.")
        elif op == "tuer" and voit(monde, "joueur", a) and voit(monde, "joueur", cible):
            lignes.append(sujet(monde.objets[a]) + " a tué cette personne.")
        elif op in ("delier", "liberer") and voit(monde, "joueur", a) and voit(monde, "joueur", cible):
            lignes.append(sujet(monde.objets[a]) + (" se libère de ses liens." if a == cible else
                          " a défait les liens de " + designer(monde.objets[cible]) + "."))


def lacher(monde, auteur, operation):
    if operation in PAROLES | {"frapper", "frapper_personne", "assommer", "riposter"}:
        return
    for cible in corps.personnages(monde):
        if corps.corps(monde, cible).get("tenu_par") == auteur:
            corps.corps(monde, cible).pop("tenu_par")


def lien_valide(o):
    p = o.get("physique", {})
    return (o.get("integrite", 1) > 0 and not o.get("entrave") and
            ("lien" in o.get("usages", []) or
             p.get("forme") == "lien" and p.get("dimensions", {}).get("longueur_cm", 0) >= 100))


def disponible(monde, auteur, cible):
    c = corps.corps(monde, cible)
    tenu = c.get("tenu_par")
    return (corps.sans_defense(monde, cible) or bool(c.get("reddition")) or
            bool(tenu and tenu != auteur and corps.conscient(monde, tenu) and au_contact(monde, tenu, cible)))


def valider(monde, auteur, operation, cible, outil=""):
    from .spatial import porte_par
    autoriser(monde, auteur, operation)
    if not corps.conscient(monde, auteur):
        raise ErreurMonde("Tu es sans connaissance.", f"auteur={auteur} : conscient requis.")
    if not corps.vivant(monde, cible):
        raise ErreurMonde("Il faut viser une personne vivante.", f"cible={cible} : personnage vivant requis.")
    if operation == "liberer":
        if cible != auteur:
            raise ErreurMonde("Tu ne peux libérer que tes propres liens ainsi.", f"cible={cible} : {auteur} requis pour liberer.")
    elif cible == auteur:
        raise ErreurMonde("Il faut viser quelqu'un d'autre.", f"cible={cible} : autre que {auteur} requis.")
    elif not au_contact(monde, auteur, cible):
        raise ErreurMonde("Cette personne est hors de portée.", f"cible={cible} : contact avec auteur={auteur} requis.")
    c = corps.corps(monde, cible)
    if operation == "tuer":
        if not corps.sans_defense(monde, cible):
            from .refus import cibles
            admises = [i for i in corps.personnages(monde)
                       if i != auteur and voit(monde, auteur, i) and corps.sans_defense(monde, i)]
            raise ErreurMonde("Cette personne peut se défendre.", f"cible={cible} : cible sans défense parmi {cibles(monde, admises)} requise.")
        if outil:
            from .combat import arme
            if outil not in monde.objets or not porte_par(monde, outil, auteur):
                raise ErreurMonde("L'arme doit être en main.", f"outil={outil} : arme portée par {auteur} requise.")
            if not arme(monde.objets[outil]):
                raise ErreurMonde("Cet objet n'est pas une arme.", f"outil={outil} : arme intacte requise, ou vide pour les mains nues.")
        return
    if operation in ("delier", "liberer"):
        if not c.get("lie"):
            raise ErreurMonde("Cette personne n'est pas ligotée.", f"cible={cible} : corps.lie requis.")
    elif c.get("lie"):
        raise ErreurMonde("Cette personne est déjà ligotée.", f"cible={cible} : corps.lie absent requis.")
    if outil:
        if outil not in monde.objets or not porte_par(monde, outil, auteur):
            raise ErreurMonde("L'outil doit être en main.", f"outil={outil} : objet porté par {auteur} requis.")
    if operation == "ligoter":
        if not disponible(monde, auteur, cible):
            raise ErreurMonde("Cette personne peut encore se débattre.", f"cible={cible} : sans défense, reddition ou tenue par un autre que {auteur} requis.")
        if not outil or not lien_valide(monde.objets[outil]):
            raise ErreurMonde("Il faut un lien utilisable en main.", f"outil={outil} : usage lien ou physique.forme=lien de longueur_cm >= 100, intact, sans entrave.")
    elif operation == "delier" and outil:
        from .combat import arme
        regle = arme(monde.objets[outil])
        if not regle or not regle[0]:
            raise ErreurMonde("Il faut une lame pour couper le lien.", f"outil={outil} : arme tranchante intacte, ou vide pour délier à la main.")
    elif outil:
        raise ErreurMonde("Ce geste se fait sans outil.", f"outil={outil} : vide pour {operation}.")


def valider_trajet(monde, auteur, cible, direction):
    """Une paire de pas physiques : l'auteur avance, la cible rejoint son départ."""
    from .passage import place, sens
    from .spatial import VECTEURS, pas_vers
    from .pnj import occupants
    from .eau import refuser_entree
    autoriser(monde, auteur, "trainer")
    if not corps.conscient(monde, auteur):
        raise ErreurMonde("Tu es sans connaissance.", f"auteur={auteur} : conscient requis.")
    if cible == auteur:
        raise ErreurMonde("Il faut viser quelqu'un d'autre.", f"cible={cible} : autre que auteur={auteur} requis.")
    if cible != "joueur" and monde.objets.get(cible, {}).get("type") not in ("personnage", "depouille"):
        raise ErreurMonde("Il faut viser un corps.", f"cible={cible} : type personnage ou depouille requis.")
    if not au_contact(monde, auteur, cible):
        raise ErreurMonde("Ce corps est hors de portée.", f"cible={cible} : contact avec auteur={auteur} requis.")
    if corps.vivant(monde, cible) and not (corps.sans_defense(monde, cible) or corps.corps(monde, cible).get("reddition")):
        raise ErreurMonde("Cette personne peut encore se débattre.", f"cible={cible} : inconscient, lie ou reddition requis.")
    portes = sorted(i for i, o in monde.objets.items() if o.get("lieu") == auteur
                    and o.get("mobile") and not o.get("entrave"))
    if portes:
        raise ErreurMonde("Il faut libérer tes mains.", f"auteur={auteur}, portes={portes} : aucun objet mobile directement porté requis.")
    if direction not in VECTEURS:
        raise ErreurMonde("Précise la direction du pas.", f"outil={direction} : direction parmi {sorted(VECTEURS)} requise.")
    depart, victime = place(monde, auteur), place(monde, cible)
    try:
        pas = pas_vers(monde, *depart, VECTEURS[direction])
        retour = pas_vers(monde, *victime, sens(monde, victime, depart))
    except ErreurMonde as exc:
        raise ErreurMonde(str(exc), f"auteur={auteur}, cible={cible}, outil={direction} : deux pas communs franchissables requis.") from exc
    if (retour["salle"], tuple(retour["position"])) != depart:
        raise ErreurMonde("Le corps ne peut pas rejoindre ta case.", f"cible={cible} : pas vers {depart} requis.")
    arrivee = pas["salle"], tuple(pas["position"])
    occ = occupants(monde, auteur)
    if arrivee in occ:
        raise ErreurMonde("La case d'arrivée est occupée.", f"arrivee={arrivee}, occupant={occ[arrivee]} : case libre requise.")
    for salle, avant in ((arrivee[0], depart[0]), (depart[0], victime[0])):
        if salle != avant:
            refuser_entree(monde, salle)
    return depart, victime, arrivee


def finir_trajet(monde, g):
    from .deplacement_objet import deplacer
    from .eau import tremper
    a, c, issue = g["auteur"], g["objet"], g["issue"]
    try:
        depart, victime, arrivee = valider_trajet(monde, a, c, issue["outil"])
        if [depart[0], list(depart[1])] != issue["depart"] or [victime[0], list(victime[1])] != issue["victime"]:
            raise ErreurMonde("Le corps a changé de place.")
    except ErreurMonde:
        corps.evenement(monde, "geste_interrompu", c, auteur=a, operation="trainer")
        return
    if a == "joueur":
        monde.joueur.update(salle=arrivee[0], position=list(arrivee[1]))
        if arrivee[0] not in monde.data["visitees"]:
            monde.data["visitees"].append(arrivee[0])
    else:
        deplacer(monde, a, arrivee[0], arrivee[1])
    if c == "joueur":
        monde.joueur.update(salle=depart[0], position=list(depart[1]))
        if depart[0] not in monde.data["visitees"]:
            monde.data["visitees"].append(depart[0])
    else:
        deplacer(monde, c, depart[0], depart[1])
    for acteur in (a, c):
        if corps.vivant(monde, acteur):
            tremper(monde, acteur)
    corps.evenement(monde, "trainer", c, auteur=a)
    from .esprits import percevoir_tous
    percevoir_tous(monde)


def commencer(monde, auteur, operation, cible, outil="", lignes=None, rotation_dixiemes=0):
    from .pnj import commencer_geste
    trajet = valider_trajet(monde, auteur, cible, outil) if operation == "trainer" else None
    if trajet is None:
        valider(monde, auteur, operation, cible, outil)
    if trajet is not None and auteur != "joueur":
        from .spatial import QUART, quarts
        rotation_dixiemes = QUART * quarts(monde.objets[auteur].get("orientation"), outil)
    lacher(monde, auteur, operation)
    percu = operation in ("saisir", "ligoter", "trainer", "tuer") and corps.conscient(monde, cible) and voit(monde, cible, auteur)
    def enregistrer(fin):
        g = commencer_geste(monde, auteur, operation, cible, fin,
                            exclus=(cible,) if percu and cible != "joueur" and operation in ("saisir", "ligoter", "trainer", "tuer") else (),
                            nature="bruyant" if operation == "tuer" and corps.conscient(monde, cible) else None)
        if operation in ("saisir", "ligoter", "trainer", "tuer") and corps.vivant(monde, cible):
            from .defense import noter_coup
            noter_coup(monde, auteur, cible, percu, operation)
            if cible != "joueur" and corps.conscient(monde, cible):
                from .esprits import memoriser
                from .deliberation import inquieter
                memoriser(monde, cible, {"type": "subi", "auteur": auteur if percu else None,
                          "operation": operation, "degats": 0,
                          "preuve": f"geste:{auteur}:{operation}:{cible}:{fin}"})
                inquieter(monde, cible, "violence")
        return g
    if operation == "saisir":
        jet = monde.d20()
        defense = (monde.d20() + max(modificateur(monde, cible, "FOR"), modificateur(monde, cible, "DEX"))
                   if percu else 10)
        succes = jet + modificateur(monde, auteur, "FOR") > defense
        if succes:
            corps.corps(monde, cible)["tenu_par"] = auteur
        enregistrer(instant(monde) + 20)
        corps.evenement(monde, "saisir", cible, auteur=auteur, reussi=succes, jet=jet, defense=defense)
        if lignes is not None and auteur == "joueur":
            lignes.append("Tu saisis cette personne." if succes else "La personne échappe à ta prise.")
        return succes
    if operation == "tuer" and corps.conscient(monde, cible):
        from .ouie import retentir
        retentir(monde, cible, "cri")
    duree = 50 if operation == "tuer" and outil else 30 if operation == "delier" and outil else DUREES[operation]
    if trajet is not None:
        from .temps import duree_pas
        from .spatial import VECTEURS
        duree = duree_pas(duree, VECTEURS[outil])
    g = enregistrer(instant(monde) + rotation_dixiemes + duree)
    if trajet is not None:
        depart, victime, arrivee = trajet
        g["issue"] = {"outil": outil, "depart": [depart[0], list(depart[1])], "victime": [victime[0], list(victime[1])]}
        o = monde.joueur if auteur == "joueur" else monde.objets[auteur]
        o["orientation"] = outil
        return rotation_dixiemes + duree
    g["issue"] = {"outil": outil, "lien": corps.corps(monde, cible).get("lie", {}).get("lien", "")}
    if lignes is not None and auteur == "joueur":
        lignes.append("Tu commences à " + {"tuer": "tuer cette personne.", "ligoter": "ligoter cette personne.", "delier": "délier cette personne.", "liberer": "défaire tes liens."}[operation])
    return rotation_dixiemes + duree


def secours(monde, auteur, lignes):
    """Se défaire de ses liens, ou rejoindre un protégé ligoté que l'on perçoit."""
    from .esprits import percoit
    c = corps.corps(monde, auteur)
    if c.get("lie"):
        return commencer(monde, auteur, "liberer", auteur)
    if c.get("tenu_par"):
        from .defense import degager
        degager(monde, auteur, lignes)
        return 20
    from .deliberation import proteges
    for cible in proteges(monde, auteur):
        if not corps.vivant(monde, cible) or not percoit(monde, auteur, cible):
            continue
        if not corps.corps(monde, cible).get("lie"):
            continue
        if not au_contact(monde, auteur, cible):
            from .pnj import _marcher, _a_portee_de
            from .passage import place
            salle, case = place(monde, cible)
            duree = _marcher(monde, auteur, lambda s, p: s == salle and _a_portee_de(monde, s, p, case), lignes)
            return duree or 1
        return commencer(monde, auteur, "delier", cible)
    return None


def finir(monde, g):
    from .deplacement_objet import deplacer
    auteur, cible, operation = g["auteur"], g["objet"], g["operation"]
    if operation == "trainer":
        return finir_trajet(monde, g)
    outil = g["issue"]["outil"]
    try:
        valider(monde, auteur, operation, cible, outil)
        if operation not in ("ligoter", "tuer") and corps.corps(monde, cible)["lie"]["lien"] != g["issue"]["lien"]:
            return
    except ErreurMonde:
        corps.evenement(monde, "geste_interrompu", cible, auteur=auteur, operation=operation)
        return
    if operation == "tuer":
        corps.mourir(monde, cible, auteur=auteur, cause="tuer")
        corps.evenement(monde, "tuer", cible, auteur=auteur)
        from .esprits import percevoir_tous
        percevoir_tous(monde)
        return
    from .vecu import noter
    activite = corps.corps(monde, cible).get("vecu", {}).get("activite")
    noter(monde, cible, g["fin"], activite)
    c = corps.corps(monde, cible)
    if operation == "ligoter":
        deplacer(monde, outil, cible)
        monde.objets[outil]["entrave"] = True
        c["lie"] = {"lien": outil, "par": auteur, "depuis": g["fin"]}
        c.pop("tenu_par", None)
    else:
        if operation == "liberer" and monde.d20() + modificateur(monde, auteur, "DEX") < 18:
            corps.evenement(monde, "liberation_manquee", cible, auteur=auteur)
            return
        lien = c.pop("lie")["lien"]
        monde.objets[lien].pop("entrave", None)
        deplacer(monde, lien, auteur)
        # L'aide met aussi fin à l'essai personnel devenu sans objet : la victime
        # ne reste pas occupée dix minutes à défaire des liens déjà retirés.
        liberation = any(x["auteur"] == cible and x["operation"] == "liberer"
                         for x in monde.data.get("gestes_en_cours", ()))
        if liberation:
            from .combat import interrompre
            interrompre(monde, cible)
    corps.evenement(monde, operation, cible, auteur=auteur)
    noter(monde, cible, g["fin"], activite)
    from .esprits import percevoir_tous
    percevoir_tous(monde)


def preparer(monde, p, plan):
    from .francais import designer
    operation, cible, outil = p["action"], p["cible"], p["outil"]
    if operation == "liberer":
        cible = "joueur"
    elif not (monde.designable(cible) if operation == "trainer" else monde.visible(cible)):
        from .refus import inaccessible
        raise inaccessible(monde, cible)
    if p["difficulte"]:
        raise ErreurMonde("Le moteur règle ce geste.", f"difficulte={p['difficulte']} : 0 requis.")
    if p["methode"] != "simple":
        raise ErreurMonde("Cette manière n'est pas prévue.", f"methode={p['methode']} : simple requis.")
    if operation == "trainer":
        depart, victime, arrivee = valider_trajet(monde, "joueur", cible, outil)
        def position(place):
            return {"salle": place[0], "position": list(place[1])}
        plan.deplacements = [
            {"acteur": "joueur", "depart": position(depart), "arrivee": position(arrivee)},
            {"acteur": cible, "depart": position(victime), "arrivee": position(depart)},
        ]
        # Repère de lecture calculé sur le même trajet validé ; aucun effet ni état ajouté.
        plan.destination_corps = depart[0]
        plan.information = ("En cas de réussite, le corps rejoint ta case de départ dans "
                            f"{monde.data['salles'][depart[0]]['nom']} ; tu avances d'un pas vers {outil}. "
                            "Ces deux déplacements forment ensemble le pas de traînage.")
    else:
        valider(monde, "joueur", operation, cible, outil)
    nom = designer(monde.objets[cible]) if cible != "joueur" else "toi"
    plan.titre = {"tuer": f"Tuer {nom} ({5 if outil else 30} secondes, sans jet).", "trainer": f"Traîner {nom} vers {outil} (4,5 secondes par case).", "saisir": f"Saisir {nom} : FOR contre FOR ou DEX, défense 10 par surprise.",
                  "ligoter": f"Ligoter {nom} (30 secondes).", "delier": f"Délier {nom} ({3 if outil else 10} secondes).",
                  "liberer": "Défaire tes liens : DEX contre 18, dix minutes."}[operation]
    if operation == "trainer":
        plan.titre += " " + plan.information
    plan.minutes, plan.dixiemes, plan.confirmation = 0, (50 if operation == "tuer" and outil else 30 if operation == "delier" and outil else DUREES[operation]), True
    tourner = 0
    if operation == "trainer":
        from .spatial import QUART, quarts, VECTEURS
        from .temps import duree_pas
        plan.regard = outil
        tourner = QUART * quarts(monde.joueur.get("orientation"), outil)
        plan.dixiemes = duree_pas(DUREES[operation], VECTEURS[outil]) + tourner
    elif cible != "joueur":
        vers, duree = rotation(monde, "joueur", cible)
        plan.regard = vers
        plan.dixiemes += duree
        tourner = duree
    plan.risque = "Le geste peut être interrompu ; son issue n'est acquise qu'à la fin." if operation != "saisir" else "La personne peut résister."
    plan.effets = [("tenir_personne", cible, {"operation": operation, "outil": outil,
                                            "rotation_dixiemes": tourner})]
    return plan
