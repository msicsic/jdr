"""Prises et liens : mêmes validations et issues différées pour tous les acteurs."""
from . import corps
from .caractere import modificateur
from .combat import voit, rotation
from .monde import ErreurMonde
from .passage import au_contact
from .temps import instant

DUREES = {"saisir": 20, "ligoter": 300, "delier": 100, "liberer": 6000}
PAROLES = {"dire", "parler", "crier", "cri", "appeler", "siffler", "se_rendre"}
IMMOBILES = {"marcher", "aller", "faufiler", "chasser", "fuir", "fuite", "passer_obstacle", "franchir", "sauter", "franchir_obstacle"}
SANS_MAINS = PAROLES | {"attendre", "patienter", "reposer", "observer", "examiner", "ecouter", "tourner", "degager", "liberer", "emettre_son"}


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
        if op not in ("ligoter", "delier", "liberer", "liberation_manquee", "geste_interrompu"):
            continue
        a, cible = e["auteur"], e["id"]
        if a == "joueur":
            textes = {"ligoter": "La personne est maintenant ligotée.", "delier": "Tu as défait ses liens.",
                      "liberer": "Tu as défait tes liens.", "liberation_manquee": "Tu ne parviens pas à défaire tes liens.",
                      "geste_interrompu": "Les conditions du geste ne tiennent plus ; il n'aboutit pas."}
            lignes.append(textes[op])
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


def commencer(monde, auteur, operation, cible, outil="", lignes=None, rotation_dixiemes=0):
    from .pnj import commencer_geste
    valider(monde, auteur, operation, cible, outil)
    lacher(monde, auteur, operation)
    percu = operation in ("saisir", "ligoter") and corps.conscient(monde, cible) and voit(monde, cible, auteur)
    def enregistrer(fin):
        g = commencer_geste(monde, auteur, operation, cible, fin,
                            exclus=(cible,) if percu and cible != "joueur" and operation in ("saisir", "ligoter") else ())
        if operation in ("saisir", "ligoter"):
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
    duree = 30 if operation == "delier" and outil else DUREES[operation]
    g = enregistrer(instant(monde) + rotation_dixiemes + duree)
    g["issue"] = {"outil": outil, "lien": corps.corps(monde, cible).get("lie", {}).get("lien", "")}
    if lignes is not None and auteur == "joueur":
        lignes.append("Tu commences à " + {"ligoter": "ligoter cette personne.", "delier": "délier cette personne.", "liberer": "défaire tes liens."}[operation])
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
    proteges = monde.objets[auteur].get("profil", {}).get("protege", ())
    for cible in proteges:
        if not corps.vivant(monde, cible) or not percoit(monde, auteur, cible):
            continue
        if not corps.corps(monde, cible).get("lie"):
            continue
        if not au_contact(monde, auteur, cible):
            from .pnj import _marcher, _a_portee_de
            from .passage import place
            salle, case = place(monde, cible)
            duree = _marcher(monde, auteur, lambda s, p: s == salle and _a_portee_de(monde, s, p, case))
            return duree or 1
        return commencer(monde, auteur, "delier", cible)
    return None


def finir(monde, g):
    from .deplacement_objet import deplacer
    auteur, cible, operation = g["auteur"], g["objet"], g["operation"]
    outil = g["issue"]["outil"]
    try:
        valider(monde, auteur, operation, cible, outil)
        if operation != "ligoter" and corps.corps(monde, cible)["lie"]["lien"] != g["issue"]["lien"]:
            return
    except ErreurMonde:
        corps.evenement(monde, "geste_interrompu", cible, auteur=auteur, operation=operation)
        return
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
    from .esprits import percevoir_tous
    percevoir_tous(monde)


def preparer(monde, p, plan):
    from .francais import designer
    operation, cible, outil = p["action"], p["cible"], p["outil"]
    if operation == "liberer":
        cible = "joueur"
    elif not monde.visible(cible):
        from .refus import inaccessible
        raise inaccessible(monde, cible)
    if p["difficulte"]:
        raise ErreurMonde("Le moteur règle ce geste.", f"difficulte={p['difficulte']} : 0 requis.")
    if p["methode"] != "simple":
        raise ErreurMonde("Cette manière n'est pas prévue.", f"methode={p['methode']} : simple requis.")
    valider(monde, "joueur", operation, cible, outil)
    nom = designer(monde.objets[cible]) if cible != "joueur" else "toi"
    plan.titre = {"saisir": f"Saisir {nom} : FOR contre FOR ou DEX, défense 10 par surprise.",
                  "ligoter": f"Ligoter {nom} (30 secondes).", "delier": f"Délier {nom} ({3 if outil else 10} secondes).",
                  "liberer": "Défaire tes liens : DEX contre 18, dix minutes."}[operation]
    plan.minutes, plan.dixiemes, plan.confirmation = 0, (30 if operation == "delier" and outil else DUREES[operation]), True
    tourner = 0
    if cible != "joueur":
        vers, duree = rotation(monde, "joueur", cible)
        plan.regard = vers
        plan.dixiemes += duree
        tourner = duree
    plan.risque = "Le geste peut être interrompu ; son issue n'est acquise qu'à la fin." if operation != "saisir" else "La personne peut résister."
    plan.effets = [("tenir_personne", cible, {"operation": operation, "outil": outil,
                                            "rotation_dixiemes": tourner})]
    return plan
