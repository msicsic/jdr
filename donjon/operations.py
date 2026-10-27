"""Langage borné de manœuvres : intentions composables, effets décidés par le moteur."""
import copy
import hashlib
import json

from .monde import ErreurMonde
from .francais import designer
from .perception import eclairage
from .vol import proprietaire
from .refus import cibles, inaccessible, portes_avec_usage


# Ces actions gardent leurs propres règles ; une séquence les compile comme une action seule.
ACTIONS_COMPOSABLES = ("ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "couper", "frapper",
                       "bloquer", "debloquer")
OPERATIONS = ("patienter", "deplacer", "prelever", "detacher", "allumer", "eteindre", "alimenter", "manger", "franchir_obstacle", "passer_obstacle", "emettre_son",
              "soulever", "appuyer", "franchir", "sauter", *ACTIONS_COMPOSABLES)
METHODES = ("simple", "discret", "levier", "finesse", "percussion", "assommer", "appui_mobile", "appel", "cri", "sifflement",
            "heler", "repondre", "arriver", "demander_raison", "dessous", "dessus")


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
        # Détacher libère sur place ; prendre la fixation est un geste distinct, s'il est demandé.
        return [etape("detacher", cible, outil=p["outil"], methode=p["methode"], difficulte=p["difficulte"])]
    if p["outil"]:
        raise ErreurMonde("Ce déplacement se fait à la main, sans outil.", f"{action} : outil vide.")
    if action == "voler":
        if p["methode"] not in ("simple", "finesse"):
            raise ErreurMonde("Le vol se tente directement ou en attendant une occasion (finesse).",
                              f"voler : methode simple ou finesse (reçu « {p['methode']} »).")
        o = monde.objets.get(cible, {})
        if not o:
            raise inaccessible(monde, cible)
        if not proprietaire(monde, o):
            raise ErreurMonde("Personne ne revendique " + designer(o) + " : il suffit de le prendre.",
                              f"{cible} n'appartient à personne : composer avec une étape deplacer {cible} vers joueur.")
        if proprietaire(monde, o) == "joueur" or o.get("vole_par") == "joueur" or o["lieu"] == "joueur":
            raise ErreurMonde("Cet objet est déjà en ta possession.", f"{cible} est déjà au joueur : rien à voler.")
        return ([etape("patienter")] if p["methode"] == "finesse" else []) + [etape("deplacer", cible, "joueur", methode="discret")]
    if action == "poser" and monde.objets.get(cible, {}).get("lieu") != "joueur":
        portes = sorted(i for i, x in monde.objets.items() if x["lieu"] == "joueur")
        raise ErreurMonde("Tu ne portes pas cet objet.", f"poser vise un objet porté, parmi {cibles(monde, portes)}.")
    return [etape("deplacer", cible, "joueur" if action == "prendre" else monde.joueur["salle"])]


def verifier_etape(e):
    attendus = set(etape("deplacer"))
    if not isinstance(e, dict) or set(e) != attendus:
        recus = sorted(e) if isinstance(e, dict) else type(e).__name__
        raise ErreurMonde("Étape mal formée ; aucun effet arbitraire n'est accepté.",
                          f"une étape a exactement les champs {', '.join(sorted(attendus))} ; reçu : {recus}.")
    fautifs = [k for k in ("operation", "cible", "destination", "outil", "methode")
               if not isinstance(e[k], str) or len(e[k]) > 100]
    if fautifs:
        raise ErreurMonde("Identifiants d'étape invalides.",
                          f"champ(s) {', '.join(fautifs)} : un identifiant texte de 100 caractères au plus.")
    if e["operation"] not in OPERATIONS:
        raise ErreurMonde("Cette opération élémentaire n'est pas prise en charge.",
                          f"operation « {e['operation']} » inconnue ; opérations : {', '.join(OPERATIONS)}.")
    if e["methode"] not in METHODES:
        raise ErreurMonde("Je ne connais pas cette façon de faire.",
                          f"methode « {e['methode']} » inconnue ; méthodes : {', '.join(METHODES)}.")
    if type(e["difficulte"]) is not int or not 0 <= e["difficulte"] <= 25:
        raise ErreurMonde("Difficulté d'étape invalide.", f"difficulte : un entier de 0 à 25 (reçu {e['difficulte']!r}).")
    if e["operation"] not in ("detacher", "franchir_obstacle") and e["difficulte"]:
        raise ErreurMonde("Seules une extraction ou un franchissement improvisé acceptent une estimation de difficulté.",
                          f"{e['operation']} : difficulte 0 ; le moteur fixe le jet.")


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


def a_portee(monde, id):
    """Porté, ou à portée de main : ce qu'on emploie sans l'emporter (une brassée, une flamme)."""
    if monde.est_porte(id):
        return monde.accessible(id)
    if not monde.accessible(id):
        return False
    from .spatial import proche
    return not monde.data.get("mode_cases") or proche(monde, id)


def compiler(monde, e, precedent=None, justification="", origine="règles"):
    from .moteur import Plan
    verifier_etape(e)
    from .tenir import autoriser
    autoriser(monde, "joueur", e["operation"])
    if e["operation"] == "passer_obstacle":
        from .obstacles import compiler as compiler_passage
        return compiler_passage(monde, e, justification, origine)
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
            raise ErreurMonde("Soulever dépose ici ; appuyer et franchir utilisent l'appui, sans destination arbitraire.",
                              f"{op} : methode simple, difficulte 0, destination "
                              + ("vide ou la salle du joueur" if op == "soulever" else "vide") + " ; l'appui va dans outil.")
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
            raise ErreurMonde("Cette opération n'a pas de destination et garde les méthodes de l'action seule.",
                              f"{e['operation']} dans un composer : destination vide, methode parmi {', '.join(METHODES_ACTION)}.")
        return Moteur(monde).preparer(proposition(e["operation"], e["cible"], e["outil"], e["methode"],
                                                  e["difficulte"], justification), origine)
    p = Plan({"action": "composer", "justification": justification}, monde.data["revision"], "", origine=origine)
    op, cible, destination, outil, methode = (e[k] for k in ("operation", "cible", "destination", "outil", "methode"))
    # Référence publique relative, résolue dans l'état de chaque étape (séquences
    # et effets d'improvisation compris), jamais enregistrée comme un lieu.
    if op in ("deplacer", "prelever") and destination == "sol":
        destination = monde.joueur["salle"]
    if op == "patienter":
        if cible or destination or outil or methode != "simple":
            raise ErreurMonde("Patienter n'a ni cible, ni outil, ni destination.",
                              "patienter : cible, destination et outil vides, methode simple ; attendre ne commande "
                              "aucun geste à un PNJ.")
        p.titre, p.minutes, p.effort = "Guetter une occasion pendant deux minutes.", 2, False
        return p
    if not monde.accessible(cible):
        raise inaccessible(monde, cible)
    from .proximite import exiger
    exiger(monde, cible)
    o = monde.objets[cible]
    if op in ("allumer", "eteindre"):
        if destination or methode != "simple":
            raise ErreurMonde("L'allumage et l'extinction n'ont pas de destination et utilisent la méthode simple.",
                              f"{op} : destination vide, methode simple.")
        if "allume" not in o:
            if op == "allumer":
                if o["integrite"] == 0:
                    raise ErreurMonde(designer(o, debut=True) + " ne peut plus éclairer.", f"{cible} est brisé.")
                from .capacites_objet import statut as statut_capacite, absence as absence_capacite
                etat = statut_capacite(o, "lumiere")
                if etat == "inconnue":
                    from .moteur import QualificationRequise
                    raise QualificationRequise(cible, "lumiere")
                if etat == "ecartee":
                    raise ErreurMonde(absence_capacite(o, "lumiere") + ".",
                                      f"{cible} n'éclaire pas (qualification établie) : ne re-propose pas cet allumage.")
            sources = sorted(i for i, x in monde.objets.items() if "allume" in x and monde.accessible(i))
            raise ErreurMonde(designer(o, debut=True) + " ne s'allume ni ne s'éteint.",
                              f"{op} vise une source lumineuse, parmi {cibles(monde, sources)}.")
        allumer = op == "allumer"
        if o["allume"] == allumer:
            raise ErreurMonde("Cette source est déjà " + ("allumée." if allumer else "éteinte."),
                              f"{cible} est déjà {'allumé' if allumer else 'éteint'} : rien à faire.")
        t = monde.objets.get(outil) if outil else None
        if allumer:
            if o["integrite"] == 0:
                raise ErreurMonde(designer(o, debut=True) + " ne peut plus éclairer.", f"{cible} est brisé.")
            if o["combustible"] <= 0:
                from .perception import brule
                raise ErreurMonde(designer(o, debut=True) + " n'a plus de combustible.",
                                  f"{cible} est épuisé" + (f" : alimenter d'abord avec un combustible ({brule(o)})."
                                                          if brule(o) else " : choisis une autre source."))
            from .eau import NOYEE_CM, sous_l_eau
            if sous_l_eau(monde, o):
                raise ErreurMonde(designer(o, debut=True) + " est sous l'eau : aucune flamme n'y prend.",
                                  f"{cible} est posé dans une salle noyée ({NOYEE_CM} cm d'eau ou plus) : "
                                  "allume une source que tu portes, ou attends que l'eau baisse.")
            from .perception import flamme
            # Un outil d'allumage, ou une autre source allumée : on réunit la flamme et la cible.
            if not outil:
                candidats = sorted((e for e in monde.objets.values() if e["id"] != cible and flamme(e)),
                                   key=lambda e: ("allumage" not in e.get("usages", []), not monde.est_porte(e["id"]), e["id"]))
                t = next((e for e in candidats if a_portee(monde, e["id"])), None)
            if t and t["id"] != cible and flamme(t) and not monde.est_porte(t["id"]) and monde.accessible(t["id"]):
                exiger(monde, t["id"])
            if not t or t["id"] == cible or not flamme(t) or not a_portee(monde, t["id"]):
                flammes = sorted(x["id"] for x in monde.objets.values()
                                 if x["id"] != cible and flamme(x) and a_portee(monde, x["id"]))
                raise ErreurMonde("Il faut un outil d'allumage utilisable, ou une autre flamme, porté ou à portée de main.",
                                  f"outil : un briquet ou une flamme portée ou à portée de main, parmi {cibles(monde, flammes)}"
                                  + (f" ; {outil} ne donne pas de flamme" if outil else "") + ".")
        elif outil:
            raise ErreurMonde("Éteindre cette source ne demande pas d'outil.", "eteindre : outil vide.")
        p.titre = ("Allumer " if allumer else "Éteindre ") + designer(o) + (" avec " + designer(t) if t else "") + "."
        p.effets = [("allumage", cible, allumer)]
        return p
    if op == "alimenter":
        from .matiere import SUBSTANCES
        from .perception import brule, combustible, recharge
        if destination or methode != "simple":
            raise ErreurMonde("Recharger une source n'a pas de destination et se fait simplement.",
                              "alimenter : cible = la source à recharger, outil = le combustible (ou vide), "
                              "destination vide, methode simple.")
        if brule(o) is None:
            sources = sorted(i for i, x in monde.objets.items() if brule(x) and monde.accessible(i))
            raise ErreurMonde(designer(o, debut=True) + " ne se recharge pas.",
                              f"alimenter : cible = un foyer ou une source qui brûle un combustible déclaré, "
                              f"parmi {cibles(monde, sources)} ; le combustible va dans outil.")
        # Une brassée se prend sur le tas : le combustible est porté ou à portée de main.
        t = monde.objets.get(outil) if outil else next(
            (e for e in sorted(monde.objets.values(), key=lambda e: not monde.est_porte(e["id"]))
             if combustible(e) and recharge(o, e) and a_portee(monde, e["id"])), None)
        if t and not monde.est_porte(t["id"]) and monde.accessible(t["id"]):
            exiger(monde, t["id"])
        if t and combustible(t) and not recharge(o, t):
            matiere = brule(o)
            reserves = sorted(x["id"] for x in monde.objets.values()
                              if combustible(x) and recharge(o, x) and a_portee(monde, x["id"]))
            raise ErreurMonde(designer(o, debut=True) + " brûle " + SUBSTANCES[matiere]["article"] + ".",
                              f"{cible} se recharge de {matiere} ; {t['id']} n'en est pas : outil parmi {cibles(monde, reserves)}.")
        if not t or not combustible(t) or not a_portee(monde, t["id"]):
            combustibles = sorted(x["id"] for x in monde.objets.values()
                                  if combustible(x) and recharge(o, x) and a_portee(monde, x["id"]))
            raise ErreurMonde("Il faut porter un combustible dont il reste une charge, ou en avoir un à portée de main.",
                              f"outil : un combustible pour {cible} porté ou à portée de main, parmi {cibles(monde, combustibles)}.")
        victime = proprietaire(monde, t)
        if (not monde.est_porte(t["id"]) and victime not in (None, "joueur")
                and t.get("vole_par") != "joueur"):
            raise ErreurMonde(designer(t, debut=True) + " appartient à autrui : il faut d'abord l'obtenir.",
                              f"{t['id']} appartient à {victime} : obtiens-le d'abord (acheter, parole_joueur, ou voler "
                              "si le joueur l'a voulu).")
        p.titre = "Alimenter " + designer(o) + " avec " + designer(t) + "."
        p.effets = [("alimentation", cible, t["id"])]
        return p
    if op == "manger":
        from .francais import complement_de
        if destination or outil or methode != "simple":
            raise ErreurMonde("Manger se fait simplement, sans destination ni outil.",
                              "manger : destination et outil vides, methode simple.")
        if o["type"] != "nourriture":
            vivres = sorted(i for i, x in monde.objets.items() if x["type"] == "nourriture" and monde.accessible(i))
            raise ErreurMonde(designer(o, debut=True) + " ne se mange pas.",
                              f"manger vise une nourriture, parmi {cibles(monde, vivres)}.")
        if o.get("portions", 0) <= 0:
            raise ErreurMonde("Il ne reste rien " + complement_de(o) + ".", f"{cible} n'a plus de portion.")
        victime = proprietaire(monde, o)
        if victime not in (None, "joueur") and o.get("vole_par") != "joueur" and not monde.est_porte(cible):
            raise ErreurMonde(designer(o, debut=True) + " appartient à autrui.",
                              f"{cible} appartient à {victime} : demande une part en mode parole_joueur, achète-le, "
                              "ou voler si le joueur l'a voulu.")
        p.titre, p.minutes, p.effort = "Manger une part " + complement_de(o) + ".", 5, False
        p.effets = [("manger", cible, 1)]
        return p
    if op == "prelever":
        # Une pièce d'un lot décrit : créée à la place du lot, puis déplacée selon les règles de deplacer.
        from .matiere import id_piece, prelever_piece
        physique = o.get("physique")
        if not physique:
            raise ErreurMonde(designer(o, debut=True) + " n'est pas encore décrit.",
                              f"décris d'abord {cible} (etablir_faits, qualification avec physique, pieces et nom_piece), "
                              "puis prelever.")
        if physique["pieces"] < 2:
            raise ErreurMonde(designer(o, debut=True) + " ne forme qu'une pièce.",
                              f"{cible} est un objet seul : deplacer, pas prelever.")
        piece_id = id_piece(monde, cible)
        avec_piece = monde.copier()
        prelever_piece(avec_piece, cible, piece_id)
        if (destination or "joueur") == avec_piece.objets[piece_id]["lieu"]:
            # Séparer une pièce là où est le lot : rien à déplacer.
            if outil or methode != "simple":
                raise ErreurMonde("Séparer une pièce du lot se fait à la main.", "prelever sur place : outil vide, methode simple.")
            p = Plan({"action": "composer", "justification": justification}, monde.data["revision"], "", origine=origine)
            p.effets = [("prelever_piece", cible, piece_id)]
            if destination == monde.joueur["salle"]:
                # Séparer au sol pose la nouvelle pièce à nos pieds, comme tout dépôt.
                p.effets.append(("transferer", piece_id, destination))
            p.titre = "Prélever " + designer(avec_piece.objets[piece_id], "indefini") + "."
            if destination == monde.joueur["salle"]:
                from .deplacement_objet import decrire_depot
                p.information = decrire_depot(avec_piece, piece_id)
            return p
        p = compiler(avec_piece, etape("deplacer", piece_id, destination or "joueur", methode=methode),
                     precedent, justification, origine)
        p.effets = [("prelever_piece", cible, piece_id)] + p.effets
        # Un vol manqué vise le lot : la pièce n'en a pas été séparée.
        p.echec = [(a, b, cible if c == piece_id else c) for a, b, c in p.echec]
        p.titre = "Prélever " + designer(avec_piece.objets[piece_id], "indefini") + "."
        return p
    from .perception import brule
    if op == "deplacer" and destination in monde.objets and brule(monde.objets[destination]):
        # Mettre un combustible dans ce qui le consomme (du bois au feu, de l'huile dans la
        # lampe), c'est le recharger : le geste d'alimenter.
        foyer = monde.objets[destination]
        if "combustible" not in o.get("usages", []):
            raise ErreurMonde(designer(foyer, debut=True) + " n'est pas un contenant : "
                              "on n'y met qu'un combustible, pour le recharger.",
                              f"{cible} n'est pas un combustible : destination joueur, la salle, ou un contenant ouvert.")
        return compiler(monde, {**e, "operation": "alimenter", "cible": destination,
                                "destination": "", "outil": cible}, precedent, justification, origine)
    if op == "deplacer":
        if outil or methode not in ("simple", "discret"):
            raise ErreurMonde("Déplacer un objet se fait à la main, simplement ou discrètement.",
                              f"deplacer : outil vide, methode simple ou discret (reçu outil « {outil} », methode « {methode} »).")
        if not o["mobile"]:
            raise ErreurMonde(designer(o, debut=True) + " ne se déplace pas.", f"{cible} est fixe : on ne peut pas le déplacer.")
        if o.get("attache"):
            raise ErreurMonde(designer(o, debut=True) + " est encore attaché.",
                              f"etape detacher {cible} avant deplacer, dans le même composer.")
        if o.get("cale_de"):
            raise ErreurMonde(designer(o, debut=True) + " cale " + designer(monde.objets[o["cale_de"]]) + ".",
                              f"debloquer {o['cale_de']} avant deplacer, dans le même composer.")
        if o.get("installation"):
            raise ErreurMonde(designer(o, debut=True) + " est installé.",
                              f"soulever {cible} pour le reprendre (opération soulever).")
        if destination == o["lieu"]:
            raise ErreurMonde("Cet objet se trouve déjà à cette destination.", f"{cible} est déjà dans {destination} : rien à faire.")
        if destination not in ("joueur", monde.joueur["salle"]):
            contenant = monde.objets.get(destination)
            if contenant and contenant["type"] == "personnage":
                raise ErreurMonde("On ne pose pas un objet sur un personnage.",
                                  f"pour donner {cible} à {destination} : action remettre, cible {cible}, outil {destination}.")
            if (not contenant or contenant["type"] != "contenant" or not contenant.get("ouverte")
                    or not monde.accessible(destination)):
                ouverts = sorted(i for i, x in monde.objets.items()
                                 if x["type"] == "contenant" and x.get("ouverte") and monde.accessible(i) and i != cible)
                raise ErreurMonde("La destination doit être ta besace, le sol ici ou un contenant ouvert et accessible.",
                                  f"destination : joueur, sol (ici), ou un contenant ouvert parmi "
                                  f"{cibles(monde, ouverts)} ; reçu « {destination} »"
                                  + (" (fermé : ouvre-le d'abord)" if contenant and contenant["type"] == "contenant"
                                     and not contenant.get("ouverte") else "") + ".")
            exiger(monde, destination)
        ids = sous_arbre(monde, cible)
        if destination in ids:
            raise ErreurMonde("Un objet ne peut pas être placé dans lui-même ou dans son contenu.",
                              f"destination {destination} est {cible} ou son contenu.")
        masse = sum(monde.objets[id]["masse"] for id in ids)
        charge_autres = monde.charge() - sum(monde.objets[id]["masse"] for id in ids if monde.est_porte(id))
        if charge_autres + masse > monde.joueur["capacite"]:
            raise ErreurMonde("Cet objet et son contenu dépassent ta capacité de portage.",
                              f"charge {charge_autres} + masse {masse} > capacité {monde.joueur['capacite']} : "
                              "pose d'abord quelque chose (deplacer vers sol).")
        # Contrôle aussi la destination et le poids imbriqué, sans toucher au monde réel.
        projection = monde.copier()
        from .deplacement_objet import deplacer
        deplacer(projection, cible, destination)
        if projection.charge() > monde.joueur["capacite"]:
            raise ErreurMonde("Ce déplacement dépasse ta capacité de portage.",
                              f"charge après déplacement {projection.charge()} > capacité {monde.joueur['capacite']}.")
        # Le bien d'autrui, hors ce qu'un prêt ou une garde confiée permettent (``biens.permis``).
        from .biens import a_autrui
        victime = a_autrui(monde, cible)
        illicite = victime is not None
        if illicite and methode != "discret":
            raise ErreurMonde("Cet objet appartient à autrui. Il faut l'acheter ou annoncer une tentative discrète.",
                              f"{cible} appartient à {victime} : acheter, ou deplacer methode discret si le joueur a "
                              "voulu le voler.")
        # Porter ne distingue pas la main du sac : le titre n'affirme pas un rangement.
        p.titre = ("Prendre " + designer(o) + "." if destination == "joueur" else
                   "Déplacer " + designer(o) + (" au sol." if destination == monde.joueur["salle"] else
                                                " dans " + designer(monde.objets[destination]) + "."))
        if destination == monde.joueur["salle"]:
            from .deplacement_objet import decrire_depot, SOL_AUX_PIEDS
            p.titre = decrire_depot(monde, cible)
            p.information = "Destination : " + SOL_AUX_PIEDS + "."
        if destination == "joueur" and o.get("longueur_cm", 0) >= 100:
            p.titre = "Prendre et porter " + designer(o) + "."
        if precedent and precedent["operation"] == "detacher" and precedent["cible"] == cible:
            p.minutes = 0  # Ranger la fixation qu'on vient de libérer fait partie du même geste.
        if methode == "discret":
            # Témoin : un personnage qui perçoit le joueur maintenant, avec les règles du joueur.
            from .esprits import percoit
            from .vol import mefiance
            temoins = [id for id, t in monde.objets.items() if t["type"] == "personnage"
                       and percoit(monde, id, "joueur")]
            if temoins:
                p.stat = "DEX"
                # Remarquer relève de la PER : les états du témoin (fatigue) la modulent.
                from .corps import malus
                vigilance = max(monde.objets[id]["vigilance"] + 2 * mefiance(monde, id)
                                + (malus(monde, "PER", id) if monde.objets[id].get("profil") else 0) for id in temoins)
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
        raise ErreurMonde("Détacher libère la fixation sur place ; ajoute deplacer pour la ranger.",
                          f"detacher : destination vide ; puis une étape deplacer {cible} vers joueur.")
    if not o.get("attache") or not o.get("amovible"):
        fixations = sorted(i for i, x in monde.objets.items()
                           if x.get("attache") and x.get("amovible") and monde.accessible(i))
        raise ErreurMonde(designer(o, debut=True) + " n'est pas une fixation amovible encore attachée.",
                          f"detacher vise une fixation amovible attachée, parmi {cibles(monde, fixations)}"
                          + (f" ; {cible} est libre : deplacer suffit" if o["mobile"] and not o.get("attache") else "") + ".")
    if o.get("extraction", "main") == "main":
        if outil or methode != "simple" or e["difficulte"]:
            raise ErreurMonde("Cette attache se libère à la main, sans outil ni jet.",
                              "detacher : outil vide, methode simple, difficulte 0.")
        p.titre = "Détacher " + designer(o) + "."
        p.effets = [("liberer", cible, monde.joueur["salle"])]
        return p
    if o["extraction"] != "outil":
        raise ErreurMonde("Mode d'extraction inconnu.", f"{cible} ne se détache pas.")
    if eclairage(monde)["niveau"] < 2:
        raise ErreurMonde("La lumière est insuffisante pour cette manœuvre précise.",
                          "detacher avec un outil exige une lumière franche : allume d'abord une source.")
    leviers = sorted(set(portes_avec_usage(monde, "levier")) | set(portes_avec_usage(monde, "levier_fin"))
                     | set(portes_avec_usage(monde, "percussion")))
    t = monde.objets.get(outil)
    if not t or t["lieu"] != "joueur" or not t["integrite"]:
        raise ErreurMonde("Il faut posséder un outil utilisable pour cette extraction.",
                          f"outil : un objet en main d'usage levier, levier_fin ou percussion, parmi {cibles(monde, leviers)}"
                          + (f" ; {outil} n'est pas en main ou est brisé" if outil else "") + ".")
    usages = t.get("usages", [])
    if methode not in ("levier", "finesse", "percussion") or (methode == "percussion" and "percussion" not in usages) or (methode != "percussion" and not {"levier", "levier_fin"}.intersection(usages)):
        raise ErreurMonde("L'outil et la méthode ne permettent pas cette extraction.",
                          f"usages de {outil} : {', '.join(usages) or 'aucun'} ; methode levier ou finesse avec un "
                          "outil levier/levier_fin, percussion avec un outil percussion.")
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
            raise ErreurMonde("Manœuvre mal formée.",
                              f"composer a exactement les champs action, etapes, justification ; reçu : {sorted(proposition)}.")
        etapes = proposition["etapes"]
    else:
        etapes = traduire(monde, proposition)
    if (not isinstance(etapes, list) or not 1 <= len(etapes) <= 6
            or not isinstance(proposition.get("justification"), str) or len(proposition["justification"]) > 1000):
        raise ErreurMonde("Une manœuvre contient une à six opérations et une justification courte.",
                          f"etapes : une liste de 1 à 6 étapes (reçu {len(etapes) if isinstance(etapes, list) else type(etapes).__name__}) ; "
                          "justification : texte de 1000 caractères au plus.")
    simulation, plans, precedent = monde.copier(), [], None
    etapes = copy.deepcopy(etapes)
    for numero, brut in enumerate(etapes):
        try:
            e = canoniser_appui(simulation, brut)
            etapes[numero] = e
            p = compiler(simulation, e, precedent, proposition["justification"], origine)
        except ErreurMonde as exc:
            if len(etapes) > 1:
                # Dans une manœuvre, le MJ doit savoir quelle étape corriger.
                nom = brut.get("operation", "?") if isinstance(brut, dict) else "?"
                exc.attendu = f"étape {numero + 1} ({nom}) : " + (exc.attendu or str(exc))
            raise
        plans.append(p)
        for effet in p.effets:
            Moteur._appliquer(simulation, effet, [])
        Moteur._terminer_etape(simulation, p, [], (), e["operation"], e["methode"])
        simulation.verifier()
        precedent = e
    canonique = copy.deepcopy(proposition)
    if canonique["action"] == "composer":
        canonique["etapes"] = copy.deepcopy(etapes)
    resultat = Plan(canonique, monde.data["revision"], "Manœuvre composée.", origine=origine)
    resultat.etapes = copy.deepcopy(etapes)
    resultat.plans = plans
    resultat.confirmation = any(p.confirmation for p in plans)
    premier_jet = next((p for p in plans if p.stat), plans[0])
    for champ in ("stat", "dd", "bonus", "cle_arbitrage"):
        setattr(resultat, champ, getattr(premier_jet, champ))
    if premier_jet.origine == "arbitrage mémorisé":
        resultat.origine = premier_jet.origine
    resultat.minutes = sum(p.minutes for p in plans)
    from .temps import duree
    resultat.dixiemes = sum(duree(p) for p in plans)
    resultat.bruit = sum(p.bruit for p in plans)
    resultat.echec_critique = [effet for p in plans for effet in p.echec_critique]
    return resultat
