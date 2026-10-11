"""Dialogues situés, offres et engagements persistants ; aucune écriture directe du LLM."""
import copy

from .monde import ErreurMonde, normaliser
from .francais import designer


OPERATIONS = ("discuter", "proposer", "negocier", "accepter", "refuser")
SCHEMA_CONVERSATION = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "personnage": {"type": "string"}, "sujet": {"type": "string"},
        "operation": {"type": "string", "enum": list(OPERATIONS)},
        "mission": {"type": "string"}, "montant_demande": {"type": "integer"},
    },
    "required": ["personnage", "sujet", "operation", "mission", "montant_demande"],
}


def installer(monde):
    d = monde.data
    d.setdefault("engagements", {})
    d.setdefault("dialogues_pnj", {})
    d.setdefault("finances_pnj", {})
    d.setdefault("missions", {})
    if d.get("dialogues_version") == 1:
        return
    d["finances_pnj"].setdefault("marchand", 50)
    d["dialogues_pnj"].setdefault("marchand", {
        "intentions": "Gorm souhaite récupérer l'anneau du veilleur. Il préfère payer pour sa récupération et rester tenir son échoppe.",
        "ton": "Il parle d'une voix grave, brièvement et sans détour. Il peut marchander, mais tient ses engagements.",
    })
    d["missions"].setdefault("anneau_veilleur", {
        "donneur": "marchand", "objet": "anneau", "nom": "Retrouver l'anneau du veilleur",
        "condition": "Remettre l'anneau du veilleur à Gorm dans la pièce où il se trouve.",
        "prime_base": 20, "prime_plafond": 30,
    })
    d["dialogues_version"] = 1


def interlocuteurs(monde):
    # Une voix porte dans la même pièce ; elle ne traverse pas automatiquement les sorties.
    return {id: {"nom": o["nom"], **copy.deepcopy(monde.data["dialogues_pnj"].get(id, {})),
                 "relation_joueur": copy.deepcopy(monde.data["relations_pnj"].get(id, {})),
                 "dernier_son_entendu": copy.deepcopy(o.get("dernier_son_entendu")),
                 "humeur": o.get("humeur", "non précisée")}
            for id, o in monde.objets.items()
            if o["type"] == "personnage" and monde.present_physique(id)
            and (not monde.data.get("mode_cases") or monde.visible(id))}


def contrats_publics(monde):
    return {id: {**copy.deepcopy(e), "donneur": monde.data["missions"][id]["donneur"],
                 "condition": monde.data["missions"][id]["condition"]}
            for id, e in monde.data["engagements"].items()}


def missions_discutables(monde):
    presents = interlocuteurs(monde)
    return {id: {"nom": m["nom"], "donneur": m["donneur"], "condition": m["condition"]}
            for id, m in monde.data["missions"].items() if m["donneur"] in presents}


def disponible(monde, donneur, sauf=None):
    reserves = sum(e["montant"] for id, e in monde.data["engagements"].items()
                   if id != sauf and e["statut"] in ("propose", "accepte")
                   and monde.data["missions"][id]["donneur"] == donneur)
    return monde.data["finances_pnj"].get(donneur, 0) - reserves


def preparer_conversation(monde, p, revision=None):
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant la fin de la conversation.")
    if not isinstance(p, dict) or set(p) != set(SCHEMA_CONVERSATION["required"]):
        raise ErreurMonde("Conversation mal formée.")
    if (any(not isinstance(p[k], str) or len(p[k]) > 600 for k in ("personnage", "sujet", "operation", "mission"))
            or type(p["montant_demande"]) is not int or not 0 <= p["montant_demande"] <= 1_000_000):
        raise ErreurMonde("Conversation mal formée.")
    acteur, op, mission_id = p["personnage"], p["operation"], p["mission"]
    if acteur not in interlocuteurs(monde):
        raise ErreurMonde("Ce personnage n'est pas ici pour te répondre.")
    if op not in OPERATIONS:
        raise ErreurMonde("Cet engagement n'est pas pris en charge.")
    travail = monde.copier()
    rapport = {"personnage": acteur, "sujet": p["sujet"], "operation": op, "faits": []}
    if op == "discuter":
        if mission_id or p["montant_demande"]:
            raise ErreurMonde("Une discussion simple ne modifie pas un accord.")
    else:
        mission = travail.data["missions"].get(mission_id)
        if not mission or mission["donneur"] != acteur:
            raise ErreurMonde("Ce personnage ne propose pas cette mission.")
        if op != "negocier" and p["montant_demande"]:
            raise ErreurMonde("Un montant demandé appartient à une négociation.")
        engagements = travail.data["engagements"]
        accord = engagements.get(mission_id)
        statut = accord["statut"] if accord else None
        if statut == "paye":
            rapport["faits"].append(f"La récompense de {accord['montant']} pièces a déjà été versée. Aucun nouveau paiement.")
        elif statut == "accepte":
            rapport["faits"].append(f"L'accord accepté reste de {accord['montant']} pièces, payables contre la remise de l'objet. Il ne change pas pendant cette discussion.")
        elif op in ("accepter", "refuser"):
            if statut != "propose":
                raise ErreurMonde("Il n'y a aucune offre en attente à accepter ou refuser.")
            accord["statut"] = "accepte" if op == "accepter" else "refuse"
            rapport["faits"].append(f"Offre de {accord['montant']} pièces " + ("acceptée. Le paiement aura lieu à la remise de l'objet." if op == "accepter" else "refusée. Aucun engagement ni paiement."))
        else:
            fonds = disponible(travail, acteur, sauf=mission_id)
            base = mission["prime_base"]
            plafond = min(mission["prime_plafond"], base + max(0, (travail.joueur["stats"]["CHA"] - 10) // 2) * 2, fonds)
            ancien = accord["montant"] if statut == "propose" else 0
            if fonds < base:
                rapport["faits"].append("Il ne dispose pas actuellement de l'argent nécessaire pour une nouvelle offre.")
            else:
                montant = ancien or base
                if op == "negocier":
                    souhait = p["montant_demande"] or plafond
                    montant = max(montant, min(souhait, plafond))
                engagements[mission_id] = {"statut": "propose", "montant": montant}
                rapport["faits"].append(f"Offre de {montant} pièces contre la remise de l'objet. Le joueur ne l'a pas encore acceptée. Aucun paiement immédiat.")
                if op == "negocier" and p["montant_demande"] > montant:
                    rapport["faits"].append(f"Le montant demandé de {p['montant_demande']} pièces est refusé ; la contre-offre est de {montant} pièces.")
                elif op == "negocier" and ancien == montant:
                    rapport["faits"].append("Il maintient son offre précédente.")
        rapport["mission"] = {"id": mission_id, "nom": mission["nom"], "condition": mission["condition"]}
        rapport["engagement"] = copy.deepcopy(engagements.get(mission_id))
    travail.data["revision"] += 1
    travail.data.setdefault("echanges_pnj", []).append({"revision": travail.data["revision"], **copy.deepcopy(rapport)})
    travail.verifier()
    return travail, rapport


def verifier_remise(monde, objet_id, destinataire=""):
    if objet_id not in monde.objets or monde.objets[objet_id]["lieu"] != "joueur":
        raise ErreurMonde("Tu dois porter l'objet pour le remettre.")
    candidats = [(id, m) for id, m in monde.data["missions"].items() if m["objet"] == objet_id
                  and (not destinataire or m["donneur"] == destinataire)]
    candidats = [(id, m) for id, m in candidats if m["donneur"] in interlocuteurs(monde)]
    if len(candidats) != 1:
        raise ErreurMonde("Le destinataire doit être présent ; précise à qui remettre cet objet.")
    id, mission = candidats[0]
    from .proximite import exiger
    exiger(monde, mission["donneur"])
    accord = monde.data["engagements"].get(id)
    if not accord or accord["statut"] != "accepte":
        raise ErreurMonde("Il faut d'abord convenir d'une récompense et accepter l'offre.")
    if monde.data["finances_pnj"].get(mission["donneur"], 0) < accord["montant"]:
        raise ErreurMonde("Le destinataire n'a pas l'argent promis. Aucun objet n'a été remis.")
    return id


def payer_remise(monde, mission_id, lignes):
    mission = monde.data["missions"][mission_id]
    verifier_remise(monde, mission["objet"], mission["donneur"])
    accord = monde.data["engagements"][mission_id]
    destinataire = mission["donneur"]
    objet = monde.objets[mission["objet"]]
    objet["lieu"], objet["proprietaire"] = destinataire, destinataire
    objet.pop("vole_par", None)
    objet.pop("position", None)
    objet.pop("position_salle", None)
    monde.data["finances_pnj"][destinataire] -= accord["montant"]
    monde.joueur["or"] += accord["montant"]
    accord["statut"] = "paye"
    accord["paye_revision"] = monde.data["revision"] + 1
    nom = monde.objets[destinataire]["nom"]
    lignes.append(f"Tu remets {designer(objet)} à {nom}. Tu reçois les {accord['montant']} pièces convenues.")


def commande_sociale(monde, texte):
    """Quelques commandes hors ligne ; les phrases libres restent interprétées par le MJ."""
    texte = normaliser(texte)
    operation, _, cible = texte.partition(" ")
    operations = {"offre": "proposer", "negocier": "negocier", "accepter": "accepter", "refuser": "refuser"}
    if operation not in operations:
        return None
    montant = 0
    if operation == "negocier" and cible.rsplit(" ", 1)[-1].isdigit():
        cible, _, montant_str = cible.rpartition(" ")
        montant = int(montant_str)
    presents = interlocuteurs(monde)
    if cible == "offre" and operation in ("accepter", "refuser"):
        candidats = [(id, mission) for id, mission in monde.data["missions"].items()
                      if mission["donneur"] in presents and monde.data["engagements"].get(id, {}).get("statut") == "propose"]
    else:
        acteurs = [id for id in presents if cible in [normaliser(n) for n in
                  (id, monde.objets[id]["nom"], *monde.objets[id]["aliases"])]]
        candidats = [(id, m) for id, m in monde.data["missions"].items() if m["donneur"] in acteurs]
    if len(candidats) != 1:
        raise ErreurMonde("Précise le personnage présent et son offre : offre marchand, negocier marchand 25, accepter offre.")
    id, mission = candidats[0]
    return {"personnage": mission["donneur"], "sujet": texte, "operation": operations[operation],
            "mission": id, "montant_demande": montant}
