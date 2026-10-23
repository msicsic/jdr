"""Un coup, sur l'horloge commune. La décision appartient au joueur ou au planificateur."""
from . import corps
from .caractere import modificateur, prix_faute, valeur, ENJEU
from .esprits import lire, memoriser, percoit
from .francais import designer, sujet
from .monde import ErreurMonde
from .passage import au_contact
from .temps import instant

COUP = 15
RISQUE = 5


def rotation(monde, auteur, cible):
    """Direction et durée pour faire face à la cible, même de part et d'autre d'un seuil."""
    from .passage import place, sens
    from .spatial import VECTEURS, QUART, quarts
    o = monde.joueur if auteur == "joueur" else monde.objets[auteur]
    vecteur = sens(monde, place(monde, auteur), place(monde, cible))
    vers = next((d for d, v in VECTEURS.items() if v == vecteur), o.get("orientation"))
    return vers, QUART * quarts(o.get("orientation"), vers)


def voit(monde, observateur, cible):
    return monde.visible(cible) if observateur == "joueur" else percoit(monde, observateur, cible)


def arme(objet=None):
    """(tranchant, puissance, caractéristique) ; None si cet objet n'est pas une arme."""
    if objet is None:
        return False, 0, "FOR"
    if objet.get("integrite", 1) <= 0:
        return None
    usages = set(objet.get("usages", []))
    if usages & {"percussion", "levier"}:
        return False, objet.get("puissance", 0), "FOR"
    if usages & {"couper", "couper_bois"}:
        return True, objet.get("puissance", 0), "DEX" if objet.get("masse_kg", objet.get("masse", 0)) < .5 else "FOR"
    if objet.get("masse_kg", objet.get("masse", 0)) >= .5:
        return False, 1, "FOR"
    return None


def prix_violence(monde, auteur, motif=None, defense=False):
    """La défense future reste possible à douceur 100 ; aucun but de défense en 4b."""
    if defense and valeur(monde, auteur, "douceur") == 100:
        return 0
    prix = prix_faute(monde, auteur, motif, "douceur")
    total = None if prix is None else prix * (0.5 if defense else 2)
    return total if total is not None and total <= ENJEU else None


def valider(monde, auteur, cible, outil="", methode="simple"):
    from .refus import liste
    from .spatial import porte_par
    if not corps.conscient(monde, auteur):
        raise ErreurMonde("Tu es sans connaissance.", f"auteur={auteur} : auteur conscient requis.")
    if not corps.vivant(monde, cible) or cible == auteur:
        acceptes = [x for x in corps.personnages(monde) if x != auteur]
        raise ErreurMonde("Il faut viser une autre personne vivante.", f"cible={cible} : parmi {liste(acceptes)}.")
    if methode not in ("simple", "assommer"):
        raise ErreurMonde("Cette manière de frapper n'est pas prévue.", f"methode={methode} : simple ou assommer.")
    if not au_contact(monde, auteur, cible):
        raise ErreurMonde("Cette personne est hors de portée.", f"cible={cible} : frapper exige le contact, une case voisine accessible.")
    if outil and not (outil in monde.objets and porte_par(monde, outil, auteur)):
        portes = [x for x in monde.objets if porte_par(monde, x, auteur)]
        raise ErreurMonde("L'arme doit être en main.", f"outil={outil} : objet porté parmi {liste(portes)}, ou vide.")
    regle = arme(monde.objets[outil] if outil else None)
    if regle is None:
        raise ErreurMonde("Cet objet ne convient pas pour frapper.", f"outil={outil} : percussion, levier, couper, couper_bois, objet intact de masse_kg >= 0.5, ou vide.")
    if methode == "assommer" and regle[0]:
        raise ErreurMonde("Assommer demande un contondant.", f"outil={outil} : contondant, ou vide (mains nues).")
    return regle


def preparer(monde, p, plan):
    cible, outil, methode = p["cible"], p["outil"], p["methode"]
    if not monde.visible(cible):
        from .refus import inaccessible
        raise inaccessible(monde, cible)
    regle = valider(monde, "joueur", cible, outil, methode)
    if p["difficulte"]:
        raise ErreurMonde("Le moteur règle ce jet.", f"difficulte={p['difficulte']} : 0 pour frapper une personne.")
    plan.titre = ("Assommer " if methode == "assommer" else "Frapper ") + designer(monde.objets[cible]) + "."
    plan.minutes, plan.dixiemes, plan.bruit = 0, COUP, 3
    vers, tourner = rotation(monde, "joueur", cible)
    if tourner:
        plan.regard = vers
        plan.dixiemes += tourner
    plan.information = (f"Jet de {regle[2]} contre l'esquive (DEX) ; défense 10 par surprise, "
                        "sans jet sur une personne sans défense ou tenue. Égalité à la victime. Durée : 1,5 s. "
                        "Un coup ne tue jamais. "
                        + ("Assommer : 1 PV ; perte de connaissance par surprise, sinon résistance de VOL." if methode == "assommer"
                           else "Dégâts : 1 + puissance // 3 + mod FOR positif, +1 pour une lame, +2 sur 20 naturel."))
    plan.confirmation = True
    plan.risque = "Réussi ou non, ce geste de violence coûte la confiance de qui te voit faire."
    plan.effets = [("frapper_personne", cible, {"outil": outil, "methode": methode})]
    return plan


def interrompre(monde, cible):
    from .vecu import noter, solder
    t = instant(monde)
    solder(monde, cible, t)
    monde.data["gestes_en_cours"] = [g for g in monde.data.get("gestes_en_cours", []) if g["auteur"] != cible]
    if cible != "joueur":
        from .esprits import esprit
        esprit(monde, cible).update(libre=t, veille=None, eveil=t, intention=None, patience=None)
    noter(monde, cible, t, None)


def frapper(monde, auteur, cible, outil="", methode="simple", lignes=None):
    """Résout avant tout affichage ; le bruit du coup ne donne pas une esquive rétroactive."""
    from .pnj import commencer_geste, _chroniquer
    from .ouie import retentir
    from .deliberation import inquieter
    tranchant, puissance, stat = valider(monde, auteur, cible, outil, methode)
    lignes = [] if lignes is None else lignes
    conscient = corps.conscient(monde, cible)
    percu = conscient and voit(monde, cible, auteur)
    surprise = not percu
    tenu_par = corps.corps(monde, cible).get("tenu_par")
    automatique = corps.sans_defense(monde, cible) or bool(tenu_par and tenu_par != auteur)
    vu_auteur = auteur == "joueur" or voit(monde, "joueur", auteur)
    vu_cible = cible == "joueur" or voit(monde, "joueur", cible)
    jet = None if automatique else monde.d20()
    defense = None if automatique else (monde.d20() + modificateur(monde, cible, "DEX") if percu else 10)
    touche = automatique or jet + modificateur(monde, auteur, stat) > defense
    degats = 1 + puissance // 3 + max(0, modificateur(monde, auteur, "FOR")) + int(tranchant) + 2 * (jet == 20)
    perte = min(corps.pv(monde, cible), (1 if methode == "assommer" else degats) if touche else 0)
    assomme = touche and methode == "assommer" and (surprise or automatique or tenu_par or
              monde.d20() + modificateur(monde, cible, "VOL") < 10 + degats)
    operation = "assommer" if methode == "assommer" else "frapper"
    geste = commencer_geste(monde, auteur, operation, cible, instant(monde) + COUP)
    preuve = f"coup:{auteur}:{cible}:{instant(monde)}:{monde.data['jets']}"
    if conscient and cible != "joueur":
        memoriser(monde, cible, {"type": "subi", "auteur": auteur if percu else None,
                  "operation": operation, "degats": perte, "preuve": preuve})
        inquieter(monde, cible, "coup")
    if auteur != "joueur":
        memoriser(monde, auteur, {"type": "a_frappe", "victime": cible, "operation": operation,
                  "degats": perte, "touche": bool(touche), "preuve": preuve})
    if touche:
        interrompre(monde, cible)
        if conscient:
            retentir(monde, cible, "cri")
        corps.perdre(monde, cible, perte)
        if assomme:
            corps.endormir(monde, cible)
    retentir(monde, auteur, operation, force="bruyant")
    resultat = dict(auteur=auteur, cible=cible, outil=outil, methode=methode, surprise=surprise,
                    touche=bool(touche), degats=perte, jet=jet, defense=defense,
                    assomme=bool(assomme), temoins=list(geste["temoins"]))
    corps.evenement(monde, "coup", cible, **resultat)
    a = "Tu" if auteur == "joueur" else sujet(monde.objets[auteur])
    b = "toi" if cible == "joueur" else designer(monde.objets[cible])
    texte = f"{a} {'frappes' if auteur == 'joueur' else 'frappe'} {b}" + (f" avec {designer(monde.objets[outil])}" if outil else " à mains nues")
    issue = " : le coup porte." if touche else " : le coup manque sa cible." if surprise else " : le coup est esquivé."
    _chroniquer(monde, auteur if auteur != "joueur" else cible, texte + issue, "violence")
    if auteur == "joueur":
        lignes.append(texte + issue)
    elif cible == "joueur":
        lignes.append((sujet(monde.objets[auteur]) if vu_auteur else "On") +
                      (f" te frappe : tu perds {perte} PV." if touche else " te manque." if surprise else " tente de te frapper ; tu esquives."))
    elif vu_auteur and vu_cible:
        lignes.append(texte + issue)
    if methode == "assommer" and touche and not assomme and corps.conscient(monde, cible) and vu_cible:
        lignes.append("Tu ne perds pas connaissance." if cible == "joueur" else sujet(monde.objets[cible]) + " ne perd pas connaissance.")
    if cible != "joueur" and vu_cible and conscient and not corps.conscient(monde, cible):
        lignes.append(sujet(monde.objets[cible]) + " s'effondre, sans connaissance.")
    return resultat


def force_crue(monde, auteur, autre):
    """Chance estimée sur les seules blessures et armes connues ; FOR adverse invisible = 10."""
    etat = lire(monde, auteur)["croyances"].get(autre, {}).get("etat", {}).get("valeur", {})
    if etat.get("conscient") is False:
        return 1.0
    connus = lire(monde, auteur)["croyances"]
    adverse = max((arme(monde.objets[x])[1] for x, d in connus.items()
                   if x in monde.objets and d.get("lieu", {}).get("valeur") == autre and arme(monde.objets[x])), default=0)
    propre = max((arme(o)[1] for o in monde.objets.values() if o["lieu"] == auteur and arme(o)), default=0)
    return max(.1, min(.9, .5 + (modificateur(monde, auteur, "FOR") + propre - adverse + 2 * etat.get("blessure", 0)) / 20))


def approcher_dos(monde, id, etape, lignes, gestes, compter):
    """Approche furtive revalidée à chaque pas ; aucune orientation invisible n'est consultée."""
    from .pnj import (_marcher, _case_crue, _a_portee_de, tour_d_horizon,
                      oreilles_crues, _patienter, TOUR, desespere)
    from .spatial import dans_le_cone, _global
    cible = etape["cible"]
    o = monde.objets[id]
    e = lire(monde, id)
    case = _case_crue(monde, id, cible)
    if case is None:
        return None
    if corps.sans_defense(monde, cible):
        return 0
    if not percoit(monde, id, cible):
        return None
    orientation = (monde.joueur if cible == "joueur" else monde.objets[cible]).get("orientation")
    salle = o["lieu"]
    arrivee = lambda s, c: (s == salle and c != case and _a_portee_de(monde, s, c, case)
                            and not dans_le_cone(_global(monde.data["salles"][s], case), orientation,
                                                _global(monde.data["salles"][s], c)))
    if not arrivee(salle, tuple(o["position"])):
        return _marcher(monde, id, arrivee, lignes, gestes)
    if not desespere(monde, id):
        # La victime est la cible de l'embuscade ; les autres regards et oreilles sont des témoins.
        ici = {"salle": salle, "case": list(o["position"])}
        dernier = e["balayage"]
        if not dernier or any(dernier[k] != v for k, v in ici.items()) or instant(monde) - dernier["instant"] > 2 * TOUR:
            e["balayage"] = {**ici, "instant": instant(monde)}
            observe = set(tour_d_horizon(monde, id)) - {cible}
            if not observe:
                return TOUR
        else:
            from .pnj import temoins_crus
            observe = set(temoins_crus(monde, id)) - {cible}
        if observe or set(oreilles_crues(monde, id, "bruyant")) - {cible}:
            if _patienter(monde, id, e["intention"], compter):
                return None
            return max(1, 600 - instant(monde) % 600)
    return 0
