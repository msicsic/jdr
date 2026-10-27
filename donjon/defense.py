"""Réagir à une violence perçue, sur l'horloge et les croyances communes.

Ni adversaires omniscients, ni état « en combat » : souvenirs datés, positions crues,
états visibles et paroles effectivement entendues suffisent à choisir et revalider.
"""
from . import corps
from .esprits import lire, memoriser, reconsiderer
from .temps import instant

RECENT = 30
EXPOSITION = 5          # surcoût forfaitaire d'un départ exposé, pondéré par la force crue
PAROLE = 30


def interposition(monde, id):
    """Une approche vue d'une charge : aucun déplacement ni soupçon omniscient.

    La case d'accès est le pas entre la charge et l'approchant. Si elle est déjà
    occupée, on ne déplace personne pour fabriquer une interception rétroactive.
    """
    from .deliberation import profil, periodique, illicite
    from .esprits import percoit, pnjs
    from .relations import se_mefie
    from .signes import intentions_lues
    from .passage import sens
    from .pnj import _etape
    if not monde.data.get("mode_cases"):
        return None
    p = profil(monde, id) or {}
    charges = {x["condition"]["objet"] for x in p.get("pulsions", ())
               if x["besoin"] == "biens" and "objet" in x["condition"]
               and not periodique(x["condition"])
               and not illicite(monde, id, x["condition"]["objet"])}
    charges.update(p.get("protege", ()))
    croyances = lire(monde, id)["croyances"]
    guets = dict(intentions_lues(monde, id))
    personnages = (*pnjs(monde), "joueur")
    ici = monde.objets[id]["lieu"]
    for objet in sorted(charges):
        c = croyances.get(objet, {}).get("lieu", {})
        cible = c.get("case")
        if c.get("valeur") != ici or cible is None:
            continue
        for autre in sorted(personnages):
            if autre == id or autre == objet or not percoit(monde, id, autre):
                continue
            guet = guets.get(autre, {}).get("envers") == objet
            if not (se_mefie(monde, id, autre) or guet):
                continue
            a = croyances.get(autre, {}).get("lieu", {})
            case = a.get("case")
            if a.get("valeur") != ici or case is None:
                continue
            if max(abs(case[n] - cible[n]) for n in (0, 1)) != 2:
                continue
            v = sens(monde, (ici, cible), (ici, case))
            acces = [cible[n] + v[n] for n in (0, 1)]
            if any(x != id and c.get("lieu", {}).get("valeur") == ici
                   and c["lieu"].get("case") == acces
                   for x, c in croyances.items() if x in personnages):
                continue
            contenu = {"objet": objet, "position": acces}
            averti = next((s for s in reversed(lire(monde, id)["memoire"])
                           if s["type"] == "mise_en_garde" and s["a"] == autre
                           and s["objet"] == objet and monde.data["minutes"] - s["minute"] < RECENT), None)
            en_place = monde.objets[id]["position"] == acces
            etapes = [] if averti and en_place else [dict(_etape("interposer", autre, lieu=ici), contenu=contenu)]
            return {"type": "interposer", "qui": autre, "objet": objet, "lieu": ici}, etapes
    return None


def garde_acces(monde, id, autre):
    """Le poste reste occupé devant l'approchant visé, pas devant un tiers sûr."""
    r = interposition(monde, id)
    return bool(r and r[0]["qui"] == autre and not r[1])


def persister(monde, id, autre):
    """Une demande réelle de franchir le poste après avertissement, une épreuve.

    Une simple lecture de chemin ou une préparation refusée n'est pas un acte.
    """
    if garde_acces(monde, id, autre):
        memoriser(monde, id, {"type": "garde_ignoree", "auteur": autre,
                              "preuve": f"garde:{id}:{autre}:{instant(monde)}"})
        return True
    return False


def avertir_acces(monde, id, etape, lignes):
    from .passage import place
    from .ouie import saisit
    from .social import faire_entendre, _qui
    from .pnj import _chroniquer
    r = interposition(monde, id)
    if not r or r[0]["qui"] != etape["cible"] or r[0]["objet"] != etape["contenu"]["objet"]:
        return False
    if place(monde, id) != (etape["lieu"], tuple(etape["contenu"]["position"])):
        return False
    autre, objet = etape["cible"], etape["contenu"]["objet"]
    from .spatial import position_cible
    from .passage import sens
    # Revalidation matérielle de la charge ; la décision n'en avait lu que
    # la dernière position connue. Pas de poste fictif après son déplacement.
    salle = etape["lieu"]
    cible = position_cible(monde, objet, salle)
    if monde.objets[objet]["lieu"] != salle or cible is None:
        return False
    v = sens(monde, (salle, cible), place(monde, autre))
    if [cible[n] + v[n] for n in (0, 1)] != etape["contenu"]["position"]:
        return False
    if not saisit(monde, id, autre, "dire"):
        return False
    # Inscription avant affichage ; aucune accusation de vol n'est établie.
    memoriser(monde, id, {"type": "mise_en_garde", "a": autre, "objet": objet})
    if autre != "joueur":
        memoriser(monde, autre, {"type": "garde_entendue", "de": id, "objet": objet})
    texte = f"{_qui(monde, id)} s'interpose et dit : « N'approche pas davantage. »"
    _chroniquer(monde, id, texte, "social")
    faire_entendre(monde, id, autre, texte, [], lignes, contenu=({"type": "raison", "objet": objet,
                   "raison": "mise_en_garde"},), suites=False)
    return True


def souvenirs(monde, id):
    return monde.data.get("violences_joueur", []) if id == "joueur" else lire(monde, id)["memoire"]


def auteurs(monde, id, protege=None):
    """Violences connues, jamais une identité déduite d'un bruit ou d'une position réelle."""
    if id == "joueur":
        return list(dict.fromkeys(s["auteur"] for s in souvenirs(monde, id)
                                  if not s.get("clos") and monde.data["minutes"] - s["minute"] < RECENT))
    resultat = []
    for a, cs in lire(monde, id)["croyances"].items():
        if a == id or "violence" not in cs:
            continue
        for victime, s in cs["violence"]["valeur"].items():
            if (monde.data["minutes"] - s["minute"] < RECENT and s["menace"] and not s["clos"]
                    and (protege is None or victime == protege)):
                resultat.append(a)
                break
    return resultat


def retenir(monde, id, s):
    """La cause perçue reste une croyance pendant sa durée, hors du récit borné à 40 lignes."""
    from .esprits import croire
    t = s["type"]
    op = "pousser" if t == "pousse" else s.get("operation")
    if t not in ("subi", "pousse", "vu_agir") or op not in ("frapper", "assommer", "pousser"):
        return
    from .pnj import est_contrainte
    if t == "vu_agir" and not est_contrainte(monde, op, s.get("objet")):
        # Forcer une chose emploie aussi ``frapper`` : un geste illicite contre son propriétaire,
        # retenu comme tel (``vu_agir``), pas une violence contre une personne.
        return
    a = s.get("auteur")
    if not a or a == id:
        return
    victime = id if t in ("subi", "pousse") else s.get("victime", s.get("objet"))
    if not victime:
        return
    # La défense n'est reconnue que si l'observateur en a perçu la cause ; une intention
    # privée de l'auteur n'est pas une preuve. Recevoir le coup reste un danger personnel.
    riposte_vue = t == "vu_agir" and victime in auteurs(monde, id)
    ancien = lire(monde, id)["croyances"].get(a, {}).get("violence", {}).get("valeur", {})
    observations = {v: dict(d) for v, d in ancien.items() if monde.data["minutes"] - d["minute"] < RECENT}
    observations[victime] = {"minute": s["minute"], "menace": not riposte_vue, "operation": op, "clos": False}
    croire(monde, id, a, "violence", observations, "entendu" if s.get("par") == "ouie" else "vu")


def constater_fin(monde, id, autre):
    """Un danger vu neutralisé ne se rouvre pas au seul réveil : il faut un nouveau geste."""
    if id == "joueur":
        for s in souvenirs(monde, id):
            if s["auteur"] == autre:
                s["clos"] = True
        return
    c = lire(monde, id)["croyances"].get(autre, {}).get("violence", {})
    for s in c.get("valeur", {}).values():
        s["clos"] = True


def etat_cru(monde, id, autre):
    if id == "joueur":
        return corps.visible(monde, autre) if monde.visible(autre) else {}
    return lire(monde, id)["croyances"].get(autre, {}).get("etat", {}).get("valeur", {})


def dangers(monde, id, protege=None):
    from .deliberation import salle_crue
    ici = monde.joueur["salle"] if id == "joueur" else monde.objets[id]["lieu"]
    def proche(a):
        if id == "joueur":
            return monde.visible(a)
        return salle_crue(monde, id, a) == ici
    return [a for a in actifs(monde, id, protege) if proche(a)]


def actifs(monde, id, protege=None):
    """Auteurs encore dangereux selon les croyances, même hors de la salle actuelle."""
    return [a for a in auteurs(monde, id, protege)
            if etat_cru(monde, id, a).get("conscient") is not False
            and not etat_cru(monde, id, a).get("reddition")
            and not etat_cru(monde, id, a).get("lie")]


def lieux_dangereux(monde, id):
    from .deliberation import salle_crue
    return {s for a in actifs(monde, id) if (s := salle_crue(monde, id, a))}


def dangers_vus(monde):
    """Ce que le joueur a vu de chaque danger perçu : l'auteur, son geste contre lui, depuis quand.
    Un danger sans son fait laisse le MJ conclure que « personne n'attaque » (``Monde.contexte``)."""
    ds = dangers(monde, "joueur")
    faits = {}
    for s in souvenirs(monde, "joueur"):
        if s["auteur"] in ds:
            faits[s["auteur"]] = {"auteur": s["auteur"], "geste": s["operation"], "contre": "joueur",
                                  "il_y_a_minutes": monde.data["minutes"] - s["minute"]}
    return [faits[a] for a in ds if a in faits]


def _agresseur(monde, cible):
    from .francais import designer
    return designer(monde.objets[cible]) + ", qui t'a agressé"


def noter_coup(monde, auteur, cible, percu, operation="frapper"):
    if cible == "joueur" and percu:
        memoire = monde.data.setdefault("violences_joueur", [])
        memoire[:] = [s for s in memoire if s["auteur"] != auteur and monde.data["minutes"] - s["minute"] < RECENT]
        memoire.append(dict(type="subi", auteur=auteur, operation=operation, minute=monde.data["minutes"]))
    # Recevoir un coup rompt la reddition envers son auteur, sans obliger à riposter.
    r = corps.corps(monde, cible).get("reddition")
    if r and r["a"] == auteur and operation in ("frapper", "assommer", "pousser"):
        reprendre(monde, cible)


def reprendre(monde, id):
    corps.corps(monde, id).pop("reddition", None)


def se_rendre(monde, id, autre, lignes):
    from .monde import ErreurMonde
    from .refus import cibles
    from .ouie import retentir, saisissent
    from .combat import voit
    from .francais import sujet
    if not corps.conscient(monde, id):
        raise ErreurMonde("Tu es sans connaissance.", f"auteur={id} : conscient requis.")
    if autre not in dangers(monde, id):
        raise ErreurMonde("Aucun agresseur perçu ne correspond.", f"cible={autre} : parmi {cibles(monde, dangers(monde, id))}, danger perçu requis.")
    corps.corps(monde, id)["reddition"] = {"a": autre, "depuis": instant(monde)}
    entendants = saisissent(monde, id, "dire")
    texte = "Je me rends !"
    # La parole établit seulement qu'il cesse de résister ; elle ne déplace personne.
    retentir(monde, id, "dire", texte=texte, dits=texte)
    for x in entendants:
        if x != "joueur":
            from .voix import reconnaitre, RECONNUE
            if voit(monde, x, id) or reconnaitre(monde, x, id)[1] == RECONNUE:
                memoriser(monde, x, {"type": "reddition", "qui": id, "a": autre})
                reconsiderer(monde, x)
    corps.evenement(monde, "reddition", id, a=autre)
    if id == "joueur":
        lignes.append("Tu dis : « Je me rends ! » Tu cesses de résister.")
    elif voit(monde, "joueur", id):
        lignes.append(sujet(monde.objets[id]) + " se rend.")
    from .pnj import _chroniquer
    _chroniquer(monde, id, ("Tu te rends." if id == "joueur" else sujet(monde.objets[id]) + " se rend."), "violence")


def protection(monde, id):
    """Un protégé agressé vu, ou un cri reconnu : le lieu est celui qu'on a appris."""
    from .deliberation import profil, salle_crue
    p = profil(monde, id) or {}
    e = lire(monde, id)
    for protege in p.get("protege", ()):
        connus = auteurs(monde, id, protege)
        salle = salle_crue(monde, id, protege)
        actifs = [a for a in connus if salle and salle_crue(monde, id, a) == salle
                  and etat_cru(monde, id, a).get("conscient") is not False
                  and not etat_cru(monde, id, a).get("reddition")]
        if actifs:
            return protege, salle, actifs
        for s in reversed(e["memoire"]):
            if (s["type"] == "secours" and s["qui"] == protege and not s.get("examine")
                    and monde.data["minutes"] - s["minute"] < RECENT):
                return protege, s["salle"], []
    return None


def choisir(monde, id):
    """Choix au coût entre les plans réels de fuite et de riposte ; reddition en dernier recours."""
    from .planification import reagir
    ds = dangers(monde, id)
    intention = lire(monde, id)["intention"]
    if not ds and intention and intention["but"]["type"] == "fuir" and intention["plan"]:
        return intention["but"], intention["plan"]
    r = corps.corps(monde, id).get("reddition")
    if r:
        # Rendu, il attend tant que celui à qui il a cédé reste un danger conscient près de lui.
        if r["a"] in ds:
            return {"type": "reddition", "qui": r["a"]}, []
        reprendre(monde, id)
    aide = protection(monde, id)
    if not ds and not aide:
        return None
    if ds and id != "joueur":
        lire(monde, id)["besoins"]["securite"] = 100
    return reagir(monde, id, ds, aide)


def executer(monde, id, etape, lignes):
    op, cible = etape["operation"], etape["cible"]
    if op == "se_rendre":
        se_rendre(monde, id, cible, lignes)
        return True
    if op == "degager":
        return degager(monde, id, lignes)
    if op == "fuite":
        corps.evenement(monde, "fuite", id, de=cible)
        return True
    return False


def degager(monde, id, lignes):
    from .caractere import modificateur
    from .monde import ErreurMonde
    from .passage import au_contact
    tenu = corps.corps(monde, id).get("tenu_par")
    if not tenu:
        raise ErreurMonde("Personne ne te retient.", f"auteur={id} : corps.tenu_par requis pour degager.")
    reussi = (not corps.conscient(monde, tenu) or not au_contact(monde, id, tenu)
              or monde.d20() + max(modificateur(monde, id, "FOR"), modificateur(monde, id, "DEX"))
              > monde.d20() + modificateur(monde, tenu, "FOR"))
    if reussi:
        corps.corps(monde, id).pop("tenu_par", None)
    if id == "joueur":
        lignes.append("Tu te dégages." if reussi else "Tu ne parviens pas à te dégager.")
    return reussi


def chemin_fuite(monde, cible=""):
    """Sortie connue atteignable la plus proche ; les obstacles et occupants suivent le pas commun.

    Un passage sous ou sur un obstacle est un pas de fuite comme pour un PNJ (``obstacles.transitions``,
    même arête de ``spatial.trajet``) : forme établie, carrure et charge portée ; seulement les
    obstacles que le joueur peut désigner, puisqu'il doit savoir qu'ils sont là."""
    from .spatial import trajet, sortie_connue
    from .passage import place
    from .monde import ErreurMonde
    from .obstacles import transitions, duree_porte, Route, DUREES_PORTES_JOUEUR
    salle, case = place(monde, "joueur")
    sorties = [s for d, s in monde.data["salles"][salle]["sorties"].items()
               if sortie_connue(monde, salle, d) and (not cible or cible in (d, s["vers"]))]
    salles = {s["vers"] for s in sorties}
    occupees = {place(monde, x) for x in corps.personnages(monde) if x != "joueur"}
    formes = {i: o["passage"] for i, o in monde.objets.items()
              if "passage" in o and o.get("lieu") == salle and monde.designable(i)}
    chemin = trajet(monde, salle, case, lambda s, c: s in salles,
                    franchissable=lambda p: not monde.objets[p].get("verrouillee"),
                    libre=lambda s, c: (s, c) not in occupees and s in salles | {salle},
                    passages=transitions(monde, "joueur", formes) if formes and monde.data.get("mode_cases") else None,
                    cout_porte=lambda p: duree_porte(monde, p, durees=DUREES_PORTES_JOUEUR))
    if not chemin:
        raise ErreurMonde("Tu ne trouves pas de sortie connue accessible.",
                          f"cible={cible} : sortie connue accessible parmi {sorted(salles)}, ou vide ; portes déverrouillées requises.")
    return Route.depuis_pas(monde, salle, chemin, durees_portes=DUREES_PORTES_JOUEUR)


def preparer_joueur(monde, p, plan):
    from .monde import ErreurMonde
    from .refus import cibles
    from .combat import preparer
    action = p["action"]
    if p["difficulte"]:
        raise ErreurMonde("Le moteur règle cette tentative.", f"difficulte={p['difficulte']} : 0 pour {action}.")
    if p["methode"] != "simple":
        raise ErreurMonde("Cette manière de faire n'est pas prévue.", f"methode={p['methode']} : simple pour {action}.")
    if p["outil"] and action != "riposter":
        raise ErreurMonde("Ce geste se fait sans outil.", f"outil={p['outil']} : vide pour {action}.")
    cible = p["cible"]
    plan.confirmation, plan.minutes = True, 0
    if action == "fuir":
        route = chemin_fuite(monde, cible)
        from .temps import MINUTE
        from .obstacles import cout_route
        plan.dixiemes = round(cout_route(route, monde.joueur.get("orientation")) * MINUTE)
        agresseurs = " et ".join(_agresseur(monde, a) for a in dangers(monde, "joueur"))
        from .francais import designer
        manieres = {"ramper": "en rampant sous ", "enjamber": "en enjambant ", "escalader": "en escaladant "}
        passages = [manieres[porte["maniere"]] + designer(monde.objets[porte["cible"]])
                    for _, _, porte, _ in route if isinstance(porte, dict)]
        plan.titre = ("Fuir " + (agresseurs + ", par " if agresseurs else "par ") + "la sortie connue accessible la plus proche"
                      + (", " + " puis ".join(passages) if passages else "") + ".")
        for porte in [porte for _, _, porte, _ in route if isinstance(porte, dict) and porte["stat"]]:
            plan.titre += (f" Passer {manieres[porte['maniere']]}" + designer(monde.objets[porte["cible"]])
                           + f" demande un jet de {porte['stat']} contre {porte['dd']} ; un échec arrête la fuite de ce côté.")
        plan.risque = "Au pas ordinaire, sans avance garantie : les autres agissent pendant chaque pas. Arrêt si le passage se ferme."
        plan.effets = [("fuir", cible, None)]
        return plan
    if action == "degager":
        if not corps.corps(monde, "joueur").get("tenu_par"):
            raise ErreurMonde("Personne ne te retient.", "auteur=joueur : corps.tenu_par requis pour degager.")
        plan.titre, plan.dixiemes = "Te dégager de qui te retient (FOR ou DEX contre FOR).", 20
    else:
        ds = dangers(monde, "joueur")
        if not cible and len(ds) == 1:
            cible = ds[0]
        if cible not in ds:
            raise ErreurMonde("Précise l'agresseur que tu perçois.", f"cible={cible} : parmi {cibles(monde, ds)}, danger perçu requis.")
        if action == "riposter":
            preparer(monde, {**p, "cible": cible}, plan)
            # La fiche et la contre-revue lisent une défense, pas une agression : contre qui, et pourquoi.
            plan.titre = "Te défendre : riposter contre " + _agresseur(monde, cible) + ", en frappant."
            return plan
        plan.titre = "Te rendre à " + _agresseur(monde, cible) + " : c'est toi qui cesses de résister."
        plan.dixiemes = PAROLE
        plan.risque = "Ta reddition sera entendue par qui est à portée de voix."
    plan.effets = [(action, cible, None)]
    return plan


def _passer_obstacle(monde, regle, vecteur, lignes):
    """Un pas de fuite sous ou sur un obstacle : se tourner vers lui s'il le faut, puis le passage
    commun avec sa fiche, son jet éventuel et sa durée. Renvoie s'il est passé."""
    from .moteur import Moteur, proposition
    from .spatial import VECTEURS
    from .obstacles import compiler
    from .caractere import modificateur
    direction = next(n for n, v in VECTEURS.items() if v == tuple(vecteur))
    if monde.joueur.get("orientation") != direction:
        p = Moteur(monde).preparer(proposition("tourner", direction))
        for effet in p.effets:
            Moteur._appliquer(monde, effet, lignes)
        Moteur._terminer_etape(monde, p, lignes, p.effets, "tourner", "simple")
    position = tuple(monde.joueur["position"])
    p = compiler(monde, {"cible": regle["cible"], "methode": regle["methode"], "destination": "", "outil": "",
                         "difficulte": 0})
    reussite = True
    if p.stat:
        jet = monde.d20()
        mod = (monde.joueur["stats"][p.stat] - 10) // 2
        corps_ = modificateur(monde, "joueur", p.stat) - mod
        total = jet + mod + p.bonus + corps_
        reussite = jet != 1 and total >= p.dd
        lignes.append(f"1d20({jet}) + {p.stat}({mod:+d}) + outil({p.bonus:+d}) "
                      + (f"+ corps({corps_:+d}) " if corps_ else "")
                      + f"= {total} contre {p.dd} : " + ("REUSSITE" if reussite else "ECHEC"))
    effets = p.effets if reussite else p.echec
    for effet in effets:
        Moteur._appliquer(monde, effet, lignes)
    Moteur._terminer_etape(monde, p, lignes, effets, "passer_obstacle", regle["methode"])
    return reussite and tuple(monde.joueur["position"]) != position


def appliquer_joueur(monde, action, cible, valeur, lignes):
    if action == "se_rendre":
        return se_rendre(monde, "joueur", cible, lignes)
    if action == "degager":
        reprendre(monde, "joueur")
        return degager(monde, "joueur", lignes)
    from .moteur import Moteur, proposition
    from .spatial import VECTEURS
    from .monde import ErreurMonde
    route = chemin_fuite(monde, cible)
    reprendre(monde, "joueur")
    depart = monde.joueur["salle"]
    debut_corps = len(monde.data.get("historique_corps", ()))

    def interrompue():
        return any(e["type"] == "inconscience" and e["id"] == "joueur"
                   for e in monde.data.get("historique_corps", ())[debut_corps:])

    for salle, case, porte, vecteur in route:
        if not corps.conscient(monde):
            break
        try:
            if isinstance(porte, dict):
                # Le même passage que la commande, revalidé sur l'état du moment (``obstacles.compiler``).
                if not _passer_obstacle(monde, porte, vecteur, lignes) or interrompue():
                    break
                continue
            if porte:
                p = Moteur(monde).preparer(proposition("ouvrir", porte))
                for effet in p.effets:
                    Moteur._appliquer(monde, effet, lignes)
                Moteur._terminer_etape(monde, p, lignes, p.effets, "ouvrir", "simple")
                if interrompue():
                    break
            direction = next(n for n, v in VECTEURS.items() if v == vecteur)
            p = Moteur(monde).preparer(proposition("marcher", direction))
            for effet in p.effets:
                Moteur._appliquer(monde, effet, lignes)
            Moteur._terminer_etape(monde, p, lignes, p.effets, "marcher", "simple")
        except ErreurMonde as exc:
            lignes.append(str(exc))
            break
        if interrompue():
            break   # Le réveil automatique ne reprend pas une fuite interrompue.
        if monde.joueur["salle"] != salle or tuple(monde.joueur["position"]) != tuple(case):
            break
    if monde.joueur["salle"] != depart and not interrompue():
        corps.evenement(monde, "fuite", "joueur", de=depart)
        lignes.append("Tu as gagné une autre salle.")
        return True
    return False
