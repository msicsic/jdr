"""Dialogues situés, offres et engagements persistants ; aucune écriture directe du LLM."""
from . import agendas
import copy

from .refus import cibles
from .monde import ErreurMonde, normaliser
from .francais import designer, groupe_nominal
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
    agendas.installer_contrats(monde)
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
    seulement ce qu'elle prétend, d'où elle vient et le genre où elle parle d'elle-même (``voix.genre``,
    ce que ses mots font entendre) ; ``reels`` rend les personnages."""
    from .corps import conscient
    from .ouie import s_entendent
    from .voix import designation, genre, nom_pour_joueur
    resultat = {}
    for id, o in monde.objets.items():
        if not (o["type"] == "personnage" and conscient(monde, id) and conscient(monde)):
            continue
        if not (monde.visible(id) or id in monde.data.get("entendus", []) and s_entendent(monde, id, "joueur")):
            continue
        cle = designation(monde, id)
        if cle != id:
            resultat[cle] = {"nom": nom_pour_joueur(monde, id), "voix_inconnue": cle.startswith("voix_"), "personne_inconnue": cle.startswith("personne_"), "entendue": _d_ou(monde, id),
                             "genre": genre(monde, id)}
            continue
        resultat[id] = {"nom": o["nom"], **copy.deepcopy(monde.data["dialogues_pnj"].get(id, {})),
                        "dernier_son_entendu": dernier_son(monde, id),
                        "paroles_entendues": copy.deepcopy([
                            p for p in monde.data.get("paroles_pnj", []) if id in p["auditeurs"]][-4:]),
                        "refuse_ventes_apres_vol": bool(o.get("refuse_ventes_apres_vol")),
                        "signes": []}
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
            for id, e in agendas.contrats(monde).items()}


def missions_discutables(monde):
    presents = interlocuteurs(monde)
    return {id: _mission_publique(monde, id)
            for id, m in monde.data["missions"].items() if m["donneur"] in presents}


def _mission_publique(monde, id):
    m = monde.data["missions"][id]
    return {"nom": m["nom"], "donneur": m["donneur"], "condition": m["condition"],
            "lieu_du_donneur": monde.objets[m["donneur"]]["lieu"], "offre": offre_mission(monde, id)}


def offre_mission(monde, id):
    from .propositions import offre
    mission = monde.data["missions"][id]
    accord = agendas.contrats(monde).get(id, {})
    if accord.get("statut") in ("paye", "refuse"):
        return None
    montant = accord.get("montant", mission["prime_base"])
    if disponible(monde, mission["donneur"], sauf=id) < montant:
        return None
    return offre(mission["donneur"], "joueur", {"type": "objet", "objet": mission["objet"]},
                 {"type": "pieces", "montant": montant})


def disponible(monde, donneur, sauf=None):
    reserves = sum(e["montant"] for id, e in agendas.contrats(monde).items()
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
    from .voix import reel
    acteur, op, mission_id = reel(monde, p["personnage"]), p["operation"], p["mission"]
    presents = reels(monde)
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
        engagements = agendas.contrats(travail)
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
            agendas.repondre_contrat(travail, mission_id, op == "accepter")
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
                agendas.proposer_contrat(travail, mission_id, montant)
                rapport["faits"].append(f"Offre de {montant} pièces contre la remise de l'objet. Le joueur ne l'a pas encore acceptée. Aucun paiement immédiat.")
                if op == "negocier" and p["montant_demande"] > montant:
                    rapport["faits"].append(f"Le montant demandé de {p['montant_demande']} pièces est refusé ; la contre-offre est de {montant} pièces.")
                elif op == "negocier" and ancien == montant:
                    rapport["faits"].append("Il maintient son offre précédente.")
        rapport["mission"] = {"id": mission_id, **_mission_publique(travail, mission_id)}
        rapport["engagement"] = agendas.contrats(travail).get(mission_id)
        rapport["offres"] = [o] if (o := offre_mission(travail, mission_id)) else []
    travail.data["revision"] += 1
    travail.data.setdefault("echanges_pnj", []).append({"revision": travail.data["revision"], **copy.deepcopy(rapport)})
    travail.verifier()
    return travail, rapport


def remise_convenue(monde, objet_id, destinataire=""):
    """La mission dont l'accord accepté attend cet objet, auprès d'un donneur présent ; sinon None."""
    candidats = [id for id, m in monde.data["missions"].items()
                 if m["objet"] == objet_id and (not destinataire or m["donneur"] == destinataire)
                 and m["donneur"] in interlocuteurs(monde)
                 and agendas.contrats(monde).get(id, {}).get("statut") == "accepte"]
    return candidats[0] if len(candidats) == 1 else None


def verifier_don(monde, objet_id, destinataire=""):
    """Donner un objet porté à un personnage présent : le geste ordinaire, sans contrepartie."""
    if objet_id not in monde.objets or monde.objets[objet_id]["lieu"] != "joueur":
        portes = sorted(i for i, o in monde.objets.items() if o["lieu"] == "joueur")
        raise ErreurMonde("Tu dois porter l'objet pour le donner.",
                          f"remettre vise un objet porté, parmi {cibles(monde, portes)} (reçu « {objet_id} »).")
    presents = sorted(interlocuteurs(monde))
    from .voix import designation
    if destinataire in monde.objets and str(designation(monde, destinataire)).startswith("personne_") and designation(monde, destinataire) in presents:
        return destinataire
    if not destinataire and len(presents) == 1:
        destinataire = presents[0]
    from .voix import reel
    if destinataire in presents and reel(monde, destinataire) != destinataire:
        return reel(monde, destinataire)  # Une voix qu'il ne sait à qui prêter, dans le noir.
    if destinataire not in presents:
        # Il ne le sait là que par une voix qui porte ce nom : c'est à elle qu'il le tend (``voix.porteur_du_nom``).
        from .voix import porteur_du_nom
        porteur = porteur_du_nom(monde, destinataire, [reel(monde, d) for d in presents])
        if porteur:
            return porteur
        # Celui qu'il connaît et nomme, il ne le perçoit pas : on le lui dit, qu'il y ait ou non d'autres présents.
        # Ce qu'il en sait, c'est qu'il ne le voit pas, pas qu'il n'est pas là.
        from .paroles import _connu_du_joueur
        nomme = (destinataire in monde.objets and monde.objets[destinataire]["type"] == "personnage"
                 and _connu_du_joueur(monde, destinataire))
        raise ErreurMonde(f"Tu ne vois pas {monde.objets[destinataire]['nom'].split(',')[0]} d'ici : approche-toi "
                          "pour le lui donner."
                          if nomme else "Il n'y a personne ici pour le recevoir." if not presents
                          else "Précise à qui tu le donnes.",
                          f"outil = le personnage qui reçoit, parmi les présents : {cibles(monde, (reel(monde, id) for id in presents))}.")
    return destinataire


def verifier_remise(monde, objet_id, destinataire=""):
    if objet_id not in monde.objets or monde.objets[objet_id]["lieu"] != "joueur":
        portes = sorted(i for i, o in monde.objets.items() if o["lieu"] == "joueur")
        raise ErreurMonde("Tu dois porter l'objet pour le remettre.",
                          f"remettre vise un objet porté, parmi {cibles(monde, portes)} (reçu « {objet_id} »).")
    candidats = [(id, m) for id, m in monde.data["missions"].items() if m["objet"] == objet_id
                  and (not destinataire or m["donneur"] == destinataire)]
    candidats = [(id, m) for id, m in candidats if m["donneur"] in interlocuteurs(monde)]
    if len(candidats) != 1:
        donneurs = sorted({m["donneur"] for m in monde.data["missions"].values() if m["objet"] == objet_id})
        raise ErreurMonde("Le destinataire doit être présent ; précise à qui remettre cet objet.",
                          f"{objet_id} est attendu par {cibles(monde, donneurs)} ; présents : "
                          f"{cibles(monde, reels(monde))}.")
    id, mission = candidats[0]
    from .proximite import exiger
    exiger(monde, mission["donneur"])
    accord = agendas.contrats(monde).get(id)
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
    accord = agendas.contrats(monde)[mission_id]
    destinataire = mission["donneur"]
    objet = monde.objets[mission["objet"]]
    objet["lieu"], objet["proprietaire"] = destinataire, destinataire
    objet.pop("vole_par", None)
    objet.pop("position", None)
    objet.pop("position_salle", None)
    monde.data["finances_pnj"][destinataire] -= accord["montant"]
    monde.joueur["or"] += accord["montant"]
    agendas.payer_contrat(monde, mission_id)
    nom = monde.objets[destinataire]["nom"]
    lignes.append(f"Tu remets {designer(objet)} {groupe_nominal(nom, 'à')}. Tu reçois les {accord['montant']} pièces convenues.")


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
                      if mission["donneur"] in presents and agendas.contrats(monde).get(id, {}).get("statut") == "propose"]
    else:
        acteurs = [id for id in presents if cible in [normaliser(n) for n in
                  (id, monde.objets[id]["nom"], *monde.objets[id]["aliases"])]]
        candidats = [(id, m) for id, m in monde.data["missions"].items() if m["donneur"] in acteurs]
    if len(candidats) != 1:
        raise ErreurMonde("Précise le personnage présent et son offre, ou accepte une offre en attente.")
    id, mission = candidats[0]
    return {"personnage": mission["donneur"], "sujet": texte, "operation": operations[operation],
            "mission": id, "montant_demande": montant}
