"""Dialogues situés, offres et engagements persistants ; aucune écriture directe du LLM."""
import copy

from .monde import ErreurMonde, normaliser
from .francais import designer
from .esprits import dernier_son


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


def interlocuteurs(monde):
    """Ceux à qui le joueur peut parler, sous le nom qu'il leur connaît (``voix.designation``).

    On parle à qui l'on perçoit : qu'on voit, ou dont on vient d'entendre la voix (une parole nette
    parvenue au joueur pendant son dernier geste : ``ecoute.retenir``), si chacun saisit les mots de
    l'autre (``ouie.s_entendent`` : distance, passages, portes). Qui se tait dans son dos ou dans le
    noir n'est pas là pour lui, ni pour le MJ. Une voix qu'il ne sait à qui prêter est un
    interlocuteur comme un autre, désigné « voix_<n> » : rien de ce qu'il en reçoit ne la trahit,
    seulement ce qu'elle prétend et d'où elle vient (``reels`` rend les personnages)."""
    from .ouie import s_entendent
    from .voix import designation, nom_pour_joueur
    resultat = {}
    for id, o in monde.objets.items():
        if not (o["type"] == "personnage" and monde.present_physique(id)):
            continue
        if not (monde.visible(id) or id in monde.data.get("entendus", []) and s_entendent(monde, id, "joueur")):
            continue
        cle = designation(monde, id)
        if cle != id:
            resultat[cle] = {"nom": nom_pour_joueur(monde, id), "voix_inconnue": True, "entendue": _d_ou(monde, id)}
            continue
        resultat[id] = {"nom": o["nom"], **copy.deepcopy(monde.data["dialogues_pnj"].get(id, {})),
                        "relation_joueur": copy.deepcopy(monde.data["relations_pnj"].get(id, {})),
                        "dernier_son_entendu": dernier_son(monde, id),
                        "paroles_entendues": copy.deepcopy([
                            p for p in monde.data.get("paroles_pnj", []) if id in p["auditeurs"]][-4:]),
                        "refuse_ventes_apres_vol": bool(o.get("refuse_ventes_apres_vol")),
                        "humeur": o.get("humeur", "non précisée")}
    return resultat


def _d_ou(monde, id):
    """D'où le joueur a entendu cette voix en dernier : « tout près », « au nord »…"""
    from .ecoute import _lieu
    dernier = next((b for b in reversed(monde.data.get("bruits", [])) if b["auteur"] == id), None)
    return _lieu(dernier["par"]) if dernier else "tout près"


def reels(monde):
    """Les personnages derrière ``interlocuteurs`` : leurs identifiants, voix inconnues comprises."""
    from .voix import reel
    return [reel(monde, d) for d in interlocuteurs(monde)]


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
        raise ErreurMonde("Le monde a changé avant la fin de la conversation.", "re-propose à partir des faits actuels.")
    champs = SCHEMA_CONVERSATION["required"]
    if not isinstance(p, dict) or set(p) != set(champs):
        recus = sorted(p) if isinstance(p, dict) else type(p).__name__
        raise ErreurMonde("Conversation mal formée.", f"conversation_pnj a exactement les champs {', '.join(champs)} ; reçu : {recus}.")
    if (any(not isinstance(p[k], str) or len(p[k]) > 600 for k in ("personnage", "sujet", "operation", "mission"))
            or type(p["montant_demande"]) is not int or not 0 <= p["montant_demande"] <= 1_000_000):
        raise ErreurMonde("Conversation mal formée.",
                          "personnage, sujet, operation, mission : textes de 600 caractères au plus ; montant_demande : "
                          "entier de 0 à 1 000 000.")
    acteur, op, mission_id = p["personnage"], p["operation"], p["mission"]
    presents = sorted(interlocuteurs(monde))
    if acteur not in presents:
        raise ErreurMonde("Ce personnage n'est pas ici pour te répondre.",
                          f"{acteur} n'est pas là pour répondre : réponds en mode dialogue qu'il est trop loin ; "
                          "ne mène pas la conversation avec un autre personnage à sa place.")
    if op not in OPERATIONS:
        raise ErreurMonde("Cet engagement n'est pas pris en charge.", f"operation parmi {', '.join(OPERATIONS)} (reçu « {op} »).")
    travail = monde.copier()
    rapport = {"personnage": acteur, "sujet": p["sujet"], "operation": op, "faits": []}
    if op == "discuter":
        if mission_id or p["montant_demande"]:
            raise ErreurMonde("Une discussion simple ne modifie pas un accord.",
                              "discuter : mission vide et montant_demande 0 ; pour un accord : proposer, negocier, accepter ou refuser.")
    else:
        mission = travail.data["missions"].get(mission_id)
        if not mission or mission["donneur"] != acteur:
            siennes = sorted(id for id, x in travail.data["missions"].items() if x["donneur"] == acteur)
            raise ErreurMonde("Ce personnage ne propose pas cette mission.",
                              f"mission : une mission de {acteur}, parmi {', '.join(siennes) or 'aucune'} "
                              f"(reçu « {mission_id} »)" + ("" if siennes else " ; sans mission : operation discuter") + ".")
        if op != "negocier" and p["montant_demande"]:
            raise ErreurMonde("Un montant demandé appartient à une négociation.",
                              f"{op} : montant_demande 0 ; pour demander un montant : negocier.")
        engagements = travail.data["engagements"]
        accord = engagements.get(mission_id)
        statut = accord["statut"] if accord else None
        if statut == "paye":
            rapport["faits"].append(f"La récompense de {accord['montant']} pièces a déjà été versée. Aucun nouveau paiement.")
        elif statut == "accepte":
            rapport["faits"].append(f"L'accord accepté reste de {accord['montant']} pièces, payables contre la remise de l'objet. Il ne change pas pendant cette discussion.")
        elif op in ("accepter", "refuser"):
            if statut != "propose":
                raise ErreurMonde("Il n'y a aucune offre en attente à accepter ou refuser.",
                                  f"aucune offre proposée pour {mission_id} : proposer ou negocier d'abord.")
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


def remise_convenue(monde, objet_id, destinataire=""):
    """La mission dont l'accord accepté attend cet objet, auprès d'un donneur présent ; sinon None."""
    candidats = [id for id, m in monde.data["missions"].items()
                 if m["objet"] == objet_id and (not destinataire or m["donneur"] == destinataire)
                 and m["donneur"] in interlocuteurs(monde)
                 and monde.data["engagements"].get(id, {}).get("statut") == "accepte"]
    return candidats[0] if len(candidats) == 1 else None


def verifier_don(monde, objet_id, destinataire=""):
    """Donner un objet porté à un personnage présent : le geste ordinaire, sans contrepartie."""
    if objet_id not in monde.objets or monde.objets[objet_id]["lieu"] != "joueur":
        portes = sorted(i for i, o in monde.objets.items() if o["lieu"] == "joueur")
        raise ErreurMonde("Tu dois porter l'objet pour le donner.",
                          f"remettre vise un objet porté, parmi {', '.join(portes) or 'aucun'} (reçu « {objet_id} »).")
    presents = sorted(interlocuteurs(monde))
    if not destinataire and len(presents) == 1:
        destinataire = presents[0]
    from .voix import reel
    if destinataire in presents and reel(monde, destinataire) != destinataire:
        return reel(monde, destinataire)  # Une voix qu'il ne sait à qui prêter, dans le noir.
    if destinataire not in presents:
        raise ErreurMonde("Il n'y a personne ici pour le recevoir." if not presents else
                          "Précise à qui tu le donnes." if not destinataire else
                          designer(monde.objets[destinataire], debut=True) + " n'est pas là pour le recevoir."
                          if destinataire in monde.objets else "Précise à qui tu le donnes.",
                          f"outil = le personnage qui reçoit, parmi les présents : {', '.join(presents) or 'aucun'}.")
    return destinataire


def verifier_remise(monde, objet_id, destinataire=""):
    if objet_id not in monde.objets or monde.objets[objet_id]["lieu"] != "joueur":
        portes = sorted(i for i, o in monde.objets.items() if o["lieu"] == "joueur")
        raise ErreurMonde("Tu dois porter l'objet pour le remettre.",
                          f"remettre vise un objet porté, parmi {', '.join(portes) or 'aucun'} (reçu « {objet_id} »).")
    candidats = [(id, m) for id, m in monde.data["missions"].items() if m["objet"] == objet_id
                  and (not destinataire or m["donneur"] == destinataire)]
    candidats = [(id, m) for id, m in candidats if m["donneur"] in interlocuteurs(monde)]
    if len(candidats) != 1:
        donneurs = sorted({m["donneur"] for m in monde.data["missions"].values() if m["objet"] == objet_id})
        raise ErreurMonde("Le destinataire doit être présent ; précise à qui remettre cet objet.",
                          f"{objet_id} est attendu par {', '.join(donneurs) or 'personne'} ; présents : "
                          f"{', '.join(sorted(interlocuteurs(monde))) or 'aucun'}.")
    id, mission = candidats[0]
    from .proximite import exiger
    exiger(monde, mission["donneur"])
    accord = monde.data["engagements"].get(id)
    if not accord or accord["statut"] != "accepte":
        raise ErreurMonde("Il faut d'abord convenir d'une récompense et accepter l'offre.",
                          f"mission {id} sans offre acceptée : conversation_pnj (proposer ou negocier, puis accepter) avant remettre.")
    if monde.data["finances_pnj"].get(mission["donneur"], 0) < accord["montant"]:
        raise ErreurMonde("Le destinataire n'a pas l'argent promis. Aucun objet n'a été remis.",
                          f"{mission['donneur']} ne peut pas payer {accord['montant']} pièces : la remise attendra.")
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
        raise ErreurMonde("Précise le personnage présent et son offre, ou accepte une offre en attente.")
    id, mission = candidats[0]
    return {"personnage": mission["donneur"], "sujet": texte, "operation": operations[operation],
            "mission": id, "montant_demande": montant}
