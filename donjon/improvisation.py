"""Résolution sommaire des initiatives, sans autoriser des écritures arbitraires.

La prose raconte ; seuls les effets typés changent les propriétés du monde.
Une marque est une inscription sur un support réel, pas un fait géographique.
"""
import copy
import hashlib
import json

from .monde import ErreurMonde, objet
from .francais import designer
from .perception import eclairage
from .vol import proprietaire


def effet(operation, cible="", destination="", texte="", valeur=0):
    return dict(operation=operation, cible=cible, destination=destination, texte=texte, valeur=valeur)


def issue(recit, effets=None):
    return {"recit": recit, "effets": effets or []}


def proposition(intention, reussite, echec=None, cibles=None, outil="", approche="expression",
                stat="", difficulte=0, minutes=1, bruit=0):
    return dict(action="improviser", intention=intention, cibles=cibles or [], outil=outil,
                approche=approche, stat=stat, difficulte=difficulte, minutes=minutes, bruit=bruit,
                reussite=reussite, echec=echec or issue(""))


APPROCHES = ("expression", "manipulation", "effort", "adresse", "observation")
STAT = ("", "FOR", "DEX", "INT", "PER", "CHA")
SCHEMA_EFFET = {"type": "object", "additionalProperties": False, "properties": {
    "operation": {"type": "string", "enum": ["marquer", "deplacer", "user", "blesser", "son"]},
    "cible": {"type": "string"}, "destination": {"type": "string"},
    "texte": {"type": "string"}, "valeur": {"type": "integer"}}, "required": list(effet(""))}
SCHEMA_ISSUE = {"type": "object", "additionalProperties": False, "properties": {
    "recit": {"type": "string"}, "effets": {"type": "array", "maxItems": 4, "items": SCHEMA_EFFET}},
    "required": ["recit", "effets"]}
SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "action": {"type": "string", "enum": ["improviser"]}, "intention": {"type": "string"},
    "cibles": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
    "outil": {"type": "string"}, "approche": {"type": "string", "enum": list(APPROCHES)},
    "stat": {"type": "string", "enum": list(STAT)}, "difficulte": {"type": "integer", "minimum": 0, "maximum": 18},
    "minutes": {"type": "integer", "minimum": 0, "maximum": 15},
    "bruit": {"type": "integer", "minimum": 0, "maximum": 3},
    "reussite": SCHEMA_ISSUE, "echec": SCHEMA_ISSUE},
    "required": list(proposition("", issue("")))}

REGLES = """
ARBITRAGE SOMMAIRE : l'absence de règle spécialisée n'est pas une impossibilité physique.
Pour une initiative plausible hors du catalogue, utilise action improviser, sans annoncer
une limite du logiciel. Privilégie les actions spécialisées quand elles résolvent l'intention.
improviser : intention courte, cibles = identifiants existants impliqués (hors joueur), outil
possédé ou vide, approche expression/manipulation/effort/adresse/observation, minutes 0..15,
bruit 0..3. stat vide et difficulte 0 pour les gestes simples ; sinon FOR/DEX/INT/PER/CHA,
difficulte 10..18, proportionnée. Aucun jet pour chanter, s'étirer, frapper un rythme ou
graver un repère grossier dans du bois avec un couteau disponible.
reussite et echec contiennent recit (1-3 phrases) et effets (liste, éventuellement vide).
Le récit est CONDITIONNEL à la branche résolue : il n'est montré qu'après l'action.
Sans jet, echec={recit:"",effets:[]}. Le récit peut décrire un geste volontaire sans changement
durable (s'étirer, essayer de jongler, fredonner). Ne remplace pas tout geste nouveau par un
échec ou « rien ne se passe ». Ne rends pas le joueur muet, ne crée pas de vide mortel.
Les faits établis restent prioritaires. Ne crée dans la prose ni objet, trésor, PNJ, lieu,
accès, savoir secret, réponse de PNJ, guérison, bonus ou état physique non représenté.
Tout changement durable exige un effet typé. Chaque effet a operation,cible,destination,texte,valeur.
- marquer : support existant dans cible, texte = contenu littéral d'une marque/inscription
  courte (par exemple « flèche vers le nord »), valeur 0, destination vide. Exige l'outil
  renseigné capable de graver/marquer. Le moteur crée un détail examinable et persistant.
- deplacer : objet libre et accessible dans cible, destination joueur/sol actuel/contenant
  ouvert. texte vide, valeur 0. Réutilise les contrôles de poids, attaches et propriété.
  N'utilise pas cet effet pour le vol ni pour voyager ; utilise leurs règles.
- son : cible joueur, valeur intensité 1..3, texte et destination vides. Pour un chant, un
  rythme ou autre bruit improvisé ; les PNJ à portée gardent un souvenir, aucune réponse garantie.
- user : cible outil possédé, valeur 1, texte/destination vides ; seulement risque justifié.
- blesser : cible joueur, valeur 1..3, texte/destination vides ; seulement risque physique
  explicite, jamais punition pour une donnée absente. Impossible de tuer via cet arbitrage.
Avec un jet, une branche d'échec doit décrire un résultat plausible, sans ajouter des dangers
gratuits. Les mouvements d'objets doivent y avoir des effets si tu les racontes réellement.
Une question reste un dialogue sans effets. Les inconnues spatiales passent par espace ;
l'improvisation ne permet pas de téléporter le joueur ni de déclarer une construction réussie.
Une incapacité technique initiale doit être réexaminée avec ce schéma. Un refus final doit
expliquer un obstacle concret de la fiction ; aucune liste fermée de verbes n'est une raison.
"""


def texte_valide(s, maxi, vide=False):
    return isinstance(s, str) and (vide or bool(s.strip())) and len(s) <= maxi and all(ord(c) >= 32 for c in s)


def technique(texte):
    from .monde import normaliser
    s = normaliser(texte)
    return any(m in s for m in ("pas pris en charge", "pas prise en charge", "non pris en charge",
        "pas implemente", "pas implementee", "moteur ne permet", "moteur ne gere", "moteur ne sait",
        "hors du moteur", "actions disponibles", "pas simule", "pas simulee"))


def compiler_effets(m, p, branche):
    from .operations import compiler, etape
    from .moteur import Moteur
    simulation, resultat = m.copier(), []
    for e in branche["effets"]:
        if (not isinstance(e, dict) or set(e) != set(effet(""))
                or any(not texte_valide(e[k], 160, vide=True) for k in ("operation", "cible", "destination", "texte"))
                or type(e["valeur"]) is not int):
            raise ErreurMonde("Conséquence d'improvisation mal formée.")
        op, cible, destination, texte, valeur = (e[k] for k in effet(""))
        if cible != "joueur" and cible not in [*p["cibles"], p["outil"]]:
            raise ErreurMonde("La conséquence doit viser une cible annoncée.")
        if op != "marquer" and texte:
            raise ErreurMonde("Un texte libre ne peut pas définir un effet physique.")
        if op != "deplacer" and destination:
            raise ErreurMonde("Cette conséquence n'a pas de destination.")
        effets = []
        if op == "deplacer":
            if valeur:
                raise ErreurMonde("Un déplacement ne modifie aucune quantité.")
            plan = compiler(simulation, etape("deplacer", cible, destination))
            effets = plan.effets
        elif op == "marquer":
            from .proximite import exiger
            exiger(simulation, cible)
            o, t = simulation.objets.get(cible, {}), simulation.objets.get(p["outil"], {})
            if (valeur or not texte.strip() or not simulation.accessible(cible)
                    or o.get("type") not in ("surface", "porte", "contenant", "materiau", "assemblage")
                    or not o.get("integrite") or proprietaire(simulation, o) not in (None, "joueur")):
                raise ErreurMonde("Il faut un support intact et disponible pour y laisser cette marque.")
            if (not t or not simulation.est_porte(p["outil"]) or not t.get("integrite")
                    or not set(t.get("usages", [])) & {"couper", "couper_bois", "marquer", "graver"}):
                raise ErreurMonde("Il faut un outil disponible pour tracer ou graver cette marque.")
            if eclairage(simulation)["niveau"] < 2:
                raise ErreurMonde("Tu ne distingues pas assez bien le support pour y tracer une marque.")
            effets = [("marque_improvisee", cible, {"texte": texte, "outil": p["outil"]})]
        elif op == "user":
            o = simulation.objets.get(cible, {})
            if (cible != p["outil"] or valeur != 1 or not simulation.est_porte(cible)
                    or o.get("type") != "outil" or o.get("integrite", 0) <= 1):
                raise ErreurMonde("Cette usure doit rester limitée à un outil annoncé, porté et en état.")
            effets = [("endommager", cible, 1)]
        elif op == "blesser":
            if cible != "joueur" or not 1 <= valeur <= 3 or simulation.joueur["pv"] <= valeur or p["approche"] not in ("effort", "adresse", "manipulation"):
                raise ErreurMonde("Cette blessure dépasse les conséquences mineures de cet arbitrage.")
            effets = [("blessure_improvisee", "joueur", valeur)]
        elif op == "son":
            if cible != "joueur" or not 1 <= valeur <= 3 or valeur > p["bruit"]:
                raise ErreurMonde("L'intensité du son doit correspondre au bruit annoncé.")
            if p["approche"] == "expression" and simulation.joueur.get("peut_parler") is False:
                raise ErreurMonde("Ta voix ne peut actuellement pas produire ce son.")
            effets = [("son_improvise", "joueur", {"intensite": valeur, "intention": p["intention"]})]
        else:
            raise ErreurMonde("Conséquence non autorisée dans cet arbitrage.")
        for e_interne in effets:
            Moteur._appliquer(simulation, e_interne, [])
        simulation.verifier()
        resultat.extend(effets)
    return resultat


def preparer(m, p, origine):
    from .moteur import Plan
    if not isinstance(p, dict) or set(p) != set(proposition("", issue(""))) or p["action"] != "improviser":
        raise ErreurMonde("Arbitrage sommaire mal formé.")
    if (not texte_valide(p["intention"], 240) or not isinstance(p["outil"], str)
            or p["approche"] not in APPROCHES or p["stat"] not in STAT
            or not isinstance(p["cibles"], list) or len(p["cibles"]) > 6
            or any(not isinstance(id, str) for id in p["cibles"]) or len(set(p["cibles"])) != len(p["cibles"])):
        raise ErreurMonde("Précise l'intention et ses cibles existantes.")
    for champ, mini, maxi in (("minutes", 0, 15), ("bruit", 0, 3), ("difficulte", 10 if p["stat"] else 0, 18 if p["stat"] else 0)):
        if type(p[champ]) is not int or not mini <= p[champ] <= maxi:
            raise ErreurMonde("Durée, bruit ou difficulté hors des limites d'un arbitrage sommaire.")
    if m.joueur["pv"] <= 0:
        raise ErreurMonde("Tu n'es plus en état d'entreprendre ce geste.")
    if any(not m.accessible(id) for id in p["cibles"]):
        raise ErreurMonde("L'une des cibles n'est pas accessible ici.")
    if p["approche"] == "manipulation":
        from .proximite import exiger
        for id in p["cibles"]:
            exiger(m, id)
    if p["outil"] and (not m.accessible(p["outil"]) or not m.est_porte(p["outil"]) or not m.objets[p["outil"]]["integrite"]):
        raise ErreurMonde("L'outil annoncé doit être accessible et porté.")
    for nom in ("reussite", "echec"):
        b = p[nom]
        if (not isinstance(b, dict) or set(b) != {"recit", "effets"}
                or not texte_valide(b["recit"], 600, vide=(nom == "echec" and not p["stat"]))
                or not isinstance(b["effets"], list) or len(b["effets"]) > 4):
            raise ErreurMonde("Issue d'improvisation mal formée.")
        if technique(b["recit"]):
            raise ErreurMonde("Décris le résultat dans la fiction, sans refus technique.")
        if sum(e.get("valeur", 0) for e in b["effets"] if isinstance(e, dict) and e.get("operation") == "blesser" and type(e.get("valeur")) is int) > 3:
            raise ErreurMonde("Le total des blessures doit rester mineur : au plus 3 PV.")
    if not p["stat"] and p["echec"] != issue(""):
        raise ErreurMonde("Un geste sans jet n'a pas de branche d'échec.")
    effets = compiler_effets(m, p, p["reussite"])
    echec = compiler_effets(m, p, p["echec"])
    if any(e[0] == "blessure_improvisee" for e in effets+echec) and not p["stat"]:
        raise ErreurMonde("Un risque de blessure doit être annoncé dans une tentative à confirmer.")
    if any(e[0] == "endommager" for e in effets+echec) and not p["stat"]:
        raise ErreurMonde("Un risque pour l'outil doit être annoncé avant confirmation.")
    plan = Plan(copy.deepcopy(p), m.data["revision"], p["intention"], origine=origine)
    plan.stat, plan.dd, plan.minutes, plan.bruit = p["stat"], p["difficulte"], p["minutes"], p["bruit"]
    # Les descriptions et le DD proposé ne changent pas les contraintes d'une méthode.
    from .monde import normaliser
    signature = {"version": 1, "intention": normaliser(p["intention"]), "approche": p["approche"], "stat": p["stat"],
        "salle": m.joueur["salle"], "outil": p["outil"], "lumiere": eclairage(m)["niveau"],
        "cibles": [{k: m.objets[id].get(k) for k in ("id", "type", "lieu", "materiau", "integrite", "masse", "attache", "verrouillee", "installation", "usages")}
                   for id in sorted(set(p["cibles"]) | ({p["outil"]} if p["outil"] else set()))],
        "effets": [[{k: e[k] for k in ("operation", "cible", "destination", "valeur")} for e in p[b]["effets"]] for b in ("reussite", "echec")]}
    if p["stat"]:
        plan.cle_arbitrage = "improvisation:" + hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
        ancien = m.data["arbitrages"].get(plan.cle_arbitrage)
        if ancien:
            plan.dd, plan.origine = ancien["dd"], "arbitrage mémorisé"
        risques = []
        for nom, branche in (("réussite", p["reussite"]), ("échec", p["echec"])):
            pv = sum(e["valeur"] for e in branche["effets"] if e["operation"] == "blesser")
            usure = sum(e["valeur"] for e in branche["effets"] if e["operation"] == "user")
            risques.append(f"En cas de {nom} : " + branche["recit"] +
                           (f" ({pv} PV perdus)" if pv else "") + (f" (outil : -{usure} intégrité)" if usure else ""))
        plan.risque = "\n".join(risques)
    plan.effets = effets + [("recit_improvise", "", {"texte": p["reussite"]["recit"], "intention": p["intention"], "cibles": p["cibles"]})]
    plan.echec = echec + [("recit_improvise", "", {"texte": p["echec"]["recit"], "intention": p["intention"], "cibles": p["cibles"]})]
    return plan


def appliquer(m, e, lignes):
    op, cible, valeur = e
    if op == "recit_improvise":
        lignes.append(valeur["texte"])
        m.data.setdefault("gestes_improvises", []).append({"tour": m.data["revision"]+1,
            "lieu": m.joueur["salle"], **copy.deepcopy(valeur)})
        m.data["gestes_improvises"] = m.data["gestes_improvises"][-60:]
    elif op == "blessure_improvisee":
        m.joueur["pv"] -= valeur
        lignes.append(f"Tu perds {valeur} PV.")
    elif op == "marque_improvisee":
        numero = m.data.get("numero_marque", 0)+1
        id = "marque_" + str(numero)
        while id in m.objets:
            numero += 1
            id = "marque_" + str(numero)
        m.data["numero_marque"] = numero
        support = m.objets[cible]
        m.objets[id] = objet(id, "marque " + str(numero), "motif", cible,
            aliases=["marque " + str(numero), "marque", "inscription"], genre="f",
            materiau=support["materiau"], motif="Une marque représente : « " + valeur["texte"] + " ».",
            inscription=valeur["texte"], origine_description="geste du joueur", outil=valeur["outil"])
        lignes.append("Une marque reste sur " + designer(support) + " : « " + valeur["texte"] + " ».")
    elif op == "son_improvise":
        from .sons import auditeurs
        ids = auditeurs(m, m.joueur["salle"], valeur["intensite"])
        son = {"tour": m.data["revision"]+1, "minute": m.data["minutes"], "origine": m.joueur["salle"],
               "nature": "geste sonore", "intention": valeur["intention"], "intensite": valeur["intensite"], "auditeurs": ids}
        m.data.setdefault("sons", []).append(son)
        m.data["sons"] = m.data["sons"][-40:]
        for id in ids:
            m.objets[id]["dernier_son_entendu"] = {k: v for k, v in son.items() if k != "auditeurs"}


def contexte(m):
    return {"gestes_recents": [copy.deepcopy(e) for e in m.data.get("gestes_improvises", []) if e["lieu"] == m.joueur["salle"]][-4:],
            "regle": "Les gestes sont des événements passés. Les marques sont des objets persistants ; leur texte n'établit pas la véracité de ce qu'elles affirment."}
