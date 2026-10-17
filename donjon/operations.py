"""Langage borné de manœuvres : intentions composables, effets décidés par le moteur."""
import copy
import hashlib
import json

from .monde import ErreurMonde
from .francais import designer
from .perception import eclairage
from .vol import proprietaire


# Ces actions gardent leurs propres règles ; une séquence les compile comme une action seule.
ACTIONS_COMPOSABLES = ("ouvrir", "fermer", "deverrouiller", "crocheter", "couper", "frapper",
                       "bloquer", "debloquer")
OPERATIONS = ("patienter", "deplacer", "detacher", "allumer", "eteindre", "franchir_obstacle", "emettre_son",
              "soulever", "appuyer", "franchir", "sauter", *ACTIONS_COMPOSABLES)
METHODES = ("simple", "discret", "levier", "finesse", "percussion", "appui_mobile", "appel", "cri", "sifflement")


def etape(operation, cible="", destination="", outil="", methode="simple", difficulte=0):
    return dict(operation=operation, cible=cible, destination=destination,
                outil=outil, methode=methode, difficulte=difficulte)


def sequence(*etapes, justification=""):
    return {"action": "composer", "etapes": list(etapes), "justification": justification}


SCHEMA_SEQUENCE = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": ["composer"]},
        "justification": {"type": "string"},
        "etapes": {"type": "array", "minItems": 1, "maxItems": 6, "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "operation": {"type": "string", "enum": list(OPERATIONS)},
                "cible": {"type": "string"}, "destination": {"type": "string"},
                "outil": {"type": "string"}, "methode": {"type": "string", "enum": list(METHODES)},
                "difficulte": {"type": "integer"},
            }, "required": list(etape("deplacer")),
        }},
    }, "required": ["action", "etapes", "justification"],
}


def traduire(monde, p):
    """Les anciennes commandes sont des raccourcis vers les mêmes opérations."""
    action, cible = p["action"], p["cible"]
    if action in ("allumer", "eteindre"):
        return [etape(action, cible, outil=p["outil"], methode=p["methode"], difficulte=p["difficulte"])]
    if action == "detacher":
        return [etape("detacher", cible, outil=p["outil"], methode=p["methode"], difficulte=p["difficulte"]),
                etape("deplacer", cible, "joueur")]
    if p["outil"]:
        raise ErreurMonde("Ce déplacement se fait à la main, sans outil.")
    if action == "voler":
        if p["methode"] not in ("simple", "finesse"):
            raise ErreurMonde("Le vol se tente directement ou en attendant une occasion (finesse).")
        o = monde.objets.get(cible, {})
        if not o or not proprietaire(monde, o):
            raise ErreurMonde("Aucun propriétaire ne revendique cet objet ; utilise prendre.")
        if proprietaire(monde, o) == "joueur" or o.get("vole_par") == "joueur" or o["lieu"] == "joueur":
            raise ErreurMonde("Cet objet est déjà en ta possession.")
        return ([etape("patienter")] if p["methode"] == "finesse" else []) + [etape("deplacer", cible, "joueur", methode="discret")]
    if action == "poser" and monde.objets.get(cible, {}).get("lieu") != "joueur":
        raise ErreurMonde("Vous ne portez pas cet objet.")
    return [etape("deplacer", cible, "joueur" if action == "prendre" else monde.joueur["salle"])]


def verifier_etape(e):
    if not isinstance(e, dict) or set(e) != set(etape("deplacer")):
        raise ErreurMonde("Étape mal formée ; aucun effet arbitraire n'est accepté.")
    if any(not isinstance(e[k], str) or len(e[k]) > 100 for k in ("operation", "cible", "destination", "outil", "methode")):
        raise ErreurMonde("Identifiants d'étape invalides.")
    if e["operation"] not in OPERATIONS or e["methode"] not in METHODES:
        raise ErreurMonde("Cette opération élémentaire n'est pas prise en charge.")
    if type(e["difficulte"]) is not int or not 0 <= e["difficulte"] <= 25:
        raise ErreurMonde("Difficulté d'étape invalide.")
    if e["operation"] not in ("detacher", "franchir_obstacle") and e["difficulte"]:
        raise ErreurMonde("Seules une extraction ou un franchissement improvisé acceptent une estimation de difficulté.")


def canoniser_appui(monde, e):
    """Ramène les champs redondants d'un geste d'échelle à sa forme exécutable."""
    verifier_etape(e)
    if e["operation"] == "appuyer" and not e["outil"]:
        support = monde.objets.get(e["destination"], {})
        if support.get("appui_vertical") and e["methode"] in ("simple", "appui_mobile"):
            return {**e, "destination": "", "outil": e["destination"], "methode": "simple"}
    if e["operation"] == "franchir" and not e["outil"]:
        installation = monde.objets.get(e["cible"], {}).get("installation") or {}
        if e["destination"] and e["destination"] == installation.get("support"):
            return {**e, "destination": ""}
    return e


def sous_arbre(monde, id):
    ids = {id}
    while True:
        ajout = {o["id"] for o in monde.objets.values() if o["lieu"] in ids} - ids
        if not ajout:
            return ids
        ids.update(ajout)


def compiler(monde, e, precedent=None, justification="", origine="règles"):
    from .moteur import Plan
    verifier_etape(e)
    if e["operation"] == "sauter":
        from .espace import compiler_saut
        return compiler_saut(monde, e, justification, origine)
    if e["operation"] in ("soulever", "appuyer", "franchir"):
        from .artisanat import preparer_usage
        from .moteur import proposition
        op = e["operation"]
        o = monde.objets.get(e["cible"], {})
        if op == "soulever" and not o.get("installation"):
            return compiler(monde, {**e, "operation": "deplacer", "destination": e["destination"] or "joueur"},
                            precedent, justification, origine)
        if e["methode"] != "simple" or e["difficulte"] or e["destination"] not in ("", monde.joueur["salle"] if op == "soulever" else ""):
            raise ErreurMonde("Soulever dépose ici ; appuyer et franchir utilisent l'appui, sans destination arbitraire.")
        return preparer_usage(monde, proposition({"soulever": "desinstaller", "appuyer": "installer", "franchir": "franchir"}[op],
                              e["cible"], outil=e["outil"], justification=justification), origine)
    if e["operation"] == "emettre_son":
        from .sons import compiler as compiler_son
        return compiler_son(monde, e, justification, origine)
    if e["operation"] == "franchir_obstacle":
        from .franchissement import compiler as compiler_franchissement
        return compiler_franchissement(monde, e, justification, origine)
    if e["operation"] in ACTIONS_COMPOSABLES:
        from .moteur import Moteur, METHODES as METHODES_ACTION, proposition
        if e["destination"] or e["methode"] not in METHODES_ACTION:
            raise ErreurMonde("Cette opération n'a pas de destination et garde les méthodes de l'action seule.")
        return Moteur(monde).preparer(proposition(e["operation"], e["cible"], e["outil"], e["methode"],
                                                  e["difficulte"], justification), origine)
    p = Plan({"action": "composer", "justification": justification}, monde.data["revision"], "", origine=origine)
    op, cible, destination, outil, methode = (e[k] for k in ("operation", "cible", "destination", "outil", "methode"))
    if op == "patienter":
        if cible or destination or outil or methode != "simple":
            raise ErreurMonde("Patienter ne peut pas imposer un geste ou un changement d'attention à un PNJ.")
        p.titre, p.minutes = "Guetter une occasion pendant deux minutes.", 2
        return p
    if not monde.accessible(cible):
        raise ErreurMonde("La cible est absente ou inaccessible depuis ici.")
    from .proximite import exiger
    exiger(monde, cible)
    o = monde.objets[cible]
    if op in ("allumer", "eteindre"):
        if destination or methode != "simple":
            raise ErreurMonde("L'allumage et l'extinction n'ont pas de destination et utilisent la méthode simple.")
        if "allume" not in o:
            if op == "allumer":
                if o["integrite"] == 0:
                    raise ErreurMonde(designer(o, debut=True) + " ne peut plus éclairer.")
                from .capacites_objet import statut as statut_capacite, absence as absence_capacite
                etat = statut_capacite(o, "lumiere")
                if etat == "inconnue":
                    from .moteur import QualificationRequise
                    raise QualificationRequise(cible, "lumiere")
                if etat == "ecartee":
                    raise ErreurMonde(absence_capacite(o, "lumiere") + ".")
            raise ErreurMonde("Cet objet n'est pas une source lumineuse modélisée.")
        allumer = op == "allumer"
        if o["allume"] == allumer:
            raise ErreurMonde("Cette source est déjà " + ("allumée." if allumer else "éteinte."))
        t = monde.objets.get(outil) if outil else None
        if allumer:
            if o["integrite"] == 0:
                raise ErreurMonde(designer(o, debut=True) + " ne peut plus éclairer.")
            if o["combustible"] <= 0:
                raise ErreurMonde(designer(o, debut=True) + " n'a plus de combustible.")
            if not outil:
                t = next((e for e in monde.objets.values() if monde.est_porte(e["id"]) and monde.accessible(e["id"])
                          and "allumage" in e.get("usages", []) and e["integrite"] > 0), None)
            if (not t or not monde.est_porte(t["id"]) or not monde.accessible(t["id"])
                    or not t["integrite"] or "allumage" not in t.get("usages", []) or t["id"] == cible):
                raise ErreurMonde("Il faut un outil d'allumage utilisable et accessible dans votre inventaire.")
        elif outil:
            raise ErreurMonde("Éteindre cette source ne demande pas d'outil.")
        p.titre = ("Allumer " if allumer else "Éteindre ") + designer(o) + (" avec " + designer(t) if t else "") + "."
        p.effets = [("allumage", cible, allumer)]
        return p
    if op == "deplacer":
        if outil or methode not in ("simple", "discret"):
            raise ErreurMonde("Déplacer un objet se fait à la main, simplement ou discrètement.")
        if not o["mobile"] or o.get("attache") or o.get("cale_de") or o.get("installation"):
            raise ErreurMonde("Cet objet doit d'abord être détaché ou débloqué.")
        if destination == o["lieu"]:
            raise ErreurMonde("Cet objet se trouve déjà à cette destination.")
        if destination not in ("joueur", monde.joueur["salle"]):
            contenant = monde.objets.get(destination)
            if (not contenant or contenant["type"] != "contenant" or not contenant.get("ouverte")
                    or not monde.accessible(destination)):
                raise ErreurMonde("La destination doit être ta besace, le sol ici ou un contenant ouvert et accessible.")
            exiger(monde, destination)
        ids = sous_arbre(monde, cible)
        if destination in ids:
            raise ErreurMonde("Un objet ne peut pas être placé dans lui-même ou dans son contenu.")
        masse = sum(monde.objets[id]["masse"] for id in ids)
        charge_autres = monde.charge() - sum(monde.objets[id]["masse"] for id in ids if monde.est_porte(id))
        if charge_autres + masse > monde.joueur["capacite"]:
            raise ErreurMonde("Cet objet et son contenu dépassent ta capacité de portage.")
        # Contrôle aussi la destination et le poids imbriqué, sans toucher au monde réel.
        projection = monde.copier()
        from .deplacement_objet import deplacer
        deplacer(projection, cible, destination)
        if projection.charge() > monde.joueur["capacite"]:
            raise ErreurMonde("Ce déplacement dépasse ta capacité de portage.")
        victime = proprietaire(monde, o)
        illicite = victime not in (None, "joueur") and o.get("vole_par") != "joueur"
        if illicite and methode != "discret":
            raise ErreurMonde("Cet objet appartient à autrui. Il faut l'acheter ou annoncer une tentative discrète.")
        p.titre = "Déplacer " + designer(o) + (" dans ta besace." if destination == "joueur" else
                  " au sol." if destination == monde.joueur["salle"] else " dans " + designer(monde.objets[destination]) + ".")
        if destination == "joueur" and o.get("longueur_cm", 0) >= 100:
            p.titre = "Prendre et porter " + designer(o) + "."
        if precedent and precedent["operation"] == "detacher" and precedent["cible"] == cible:
            p.minutes = 0  # Ranger la fixation qu'on vient de libérer fait partie du même geste.
        if methode == "discret":
            # Témoin : un personnage qui perçoit le joueur maintenant, avec les règles du joueur.
            from .esprits import percoit
            temoins = [id for id, t in monde.objets.items() if t["type"] == "personnage"
                       and percoit(monde, id, "joueur")]
            if temoins:
                p.stat = "DEX"
                vigilance = max(monde.objets[id]["vigilance"] + 2 * monde.data["relations_pnj"][id]["soupcon"] for id in temoins)
                occasion = 2 if precedent and precedent["operation"] == "patienter" else 0
                p.dd = min(25, max(2, vigilance + (2 if masse > 1 else 0) + (2 if monde.data["bruit"] >= 6 else 0) - occasion))
                if illicite:
                    p.echec = [("surprendre_vol", id, cible) for id in temoins]
                    p.risque = "En cas d'échec, l'objet reste en place et les témoins deviennent méfiants ; certains vendeurs peuvent refuser leurs ventes."
                else:
                    p.echec = [("remarquer", id, cible) for id in temoins]
                    p.risque = "En cas d'échec, le geste est remarqué et l'objet reste en place."
            if illicite:
                p.effets.append(("voler", cible, victime))
        p.effets.append(("transferer", cible, destination))
        return p
    if destination:
        raise ErreurMonde("Détacher libère la fixation sur place ; ajoute deplacer pour la ranger.")
    if not o.get("attache") or not o.get("amovible"):
        raise ErreurMonde("Cet objet n'est pas une fixation amovible encore attachée.")
    if o.get("extraction", "main") == "main":
        if outil or methode != "simple" or e["difficulte"]:
            raise ErreurMonde("Cette attache se libère à la main, sans outil ni jet.")
        p.titre = "Détacher " + designer(o) + "."
        p.effets = [("liberer", cible, monde.joueur["salle"])]
        return p
    if o["extraction"] != "outil":
        raise ErreurMonde("Mode d'extraction inconnu.")
    if eclairage(monde)["niveau"] < 2:
        raise ErreurMonde("La lumière est insuffisante pour cette manœuvre précise.")
    t = monde.objets.get(outil)
    if not t or t["lieu"] != "joueur" or not t["integrite"]:
        raise ErreurMonde("Il faut posséder un outil utilisable pour cette extraction.")
    usages = t.get("usages", [])
    if methode not in ("levier", "finesse", "percussion") or (methode == "percussion" and "percussion" not in usages) or (methode != "percussion" and not {"levier", "levier_fin"}.intersection(usages)):
        raise ErreurMonde("L'outil et la méthode ne permettent pas cette extraction.")
    fragile = "levier_fin" in usages
    minimum, maximum = (17, 22) if fragile else (11, 16)
    p.stat, p.bonus = ("DEX" if fragile or methode == "finesse" else "FOR"), (0 if fragile else 3)
    p.dd = max(minimum, min(maximum, e["difficulte"] or (18 if fragile else 12)))
    p.minutes, p.bruit = 3, (2 if methode == "percussion" else 1)
    p.titre = "Libérer " + designer(o) + " avec " + designer(t) + "."
    p.effets = [("liberer", cible, monde.joueur["salle"])]
    if fragile:
        p.echec_critique = [("endommager", outil, 1)]
    # Les mots du joueur, le DD suggéré, la révision et les connaissances narratives
    # ne changent pas un arbitrage. Seules les propriétés physiques pertinentes comptent.
    signature = {"version": 1, "cible": {k: o.get(k) for k in ("id", "materiau", "masse", "integrite", "amovible", "resistance", "attache")},
                 "outil": {k: t.get(k) for k in ("id", "materiau", "integrite", "usages", "puissance")}, "methode": methode}
    p.cle_arbitrage = hashlib.sha256(json.dumps(signature, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    ancien = monde.data["arbitrages"].get(p.cle_arbitrage)
    if ancien:
        p.dd, p.origine = ancien["dd"], "arbitrage mémorisé"
        p.proposition["justification"] = ancien["justification"]
    return p


def preparer(monde, proposition, origine):
    from .moteur import Moteur, Plan
    if proposition["action"] == "composer":
        if set(proposition) != {"action", "etapes", "justification"}:
            raise ErreurMonde("Manœuvre mal formée.")
        etapes = proposition["etapes"]
    else:
        etapes = traduire(monde, proposition)
    if (not isinstance(etapes, list) or not 1 <= len(etapes) <= 6
            or not isinstance(proposition.get("justification"), str) or len(proposition["justification"]) > 1000):
        raise ErreurMonde("Une manœuvre contient une à six opérations et une justification courte.")
    simulation, plans, precedent = monde.copier(), [], None
    etapes = copy.deepcopy(etapes)
    for numero, brut in enumerate(etapes):
        e = canoniser_appui(simulation, brut)
        etapes[numero] = e
        p = compiler(simulation, e, precedent, proposition["justification"], origine)
        plans.append(p)
        for effet in p.effets:
            Moteur._appliquer(simulation, effet, [])
        Moteur._terminer_etape(simulation, p, [])
        simulation.verifier()
        precedent = e
    canonique = copy.deepcopy(proposition)
    if canonique["action"] == "composer":
        canonique["etapes"] = copy.deepcopy(etapes)
    resultat = Plan(canonique, monde.data["revision"], "Manœuvre composée.", origine=origine)
    resultat.etapes = copy.deepcopy(etapes)
    resultat.plans = plans
    premier_jet = next((p for p in plans if p.stat), plans[0])
    for champ in ("stat", "dd", "bonus", "cle_arbitrage"):
        setattr(resultat, champ, getattr(premier_jet, champ))
    if premier_jet.origine == "arbitrage mémorisé":
        resultat.origine = premier_jet.origine
    resultat.minutes = sum(p.minutes for p in plans)
    resultat.bruit = sum(p.bruit for p in plans)
    resultat.echec_critique = [effet for p in plans for effet in p.echec_critique]
    return resultat
