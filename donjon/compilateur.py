"""Compilateur d'intention : traduction rapide de la langue naturelle en proposition mécanique.

Ce composant extrait le contexte local réduit (salle, sorties, objets accessibles, PNJ présents,
missions et accords en cours) et utilise un fournisseur LLM (local ou cloud) avec un schéma
d'intention compact, sans consigne narrative ni double passe d'audit lourd.
"""
import os

from .agendas import contrats
from .fournisseurs.contrat import Demande
from .improvisation import FORMES_SONORES, effet, issue, proposition as proposition_improviser
from .monde import ErreurMonde, normaliser
from .operations import OPERATIONS as OPERATIONS_COMPOSER
from .passage import au_contact
from .refus import RefusDeForme
from .voix import nom_pour_joueur

ACTIONS_AUTORISEES = [
    "observer", "examiner", "toucher", "lire", "ecouter", "aller", "marcher", "faufiler", "chasser", "tourner", "attendre",
    "prendre", "poser", "acheter", "voler", "lister_marchandises", "allumer", "eteindre",
    "ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "detacher",
    "couper", "bloquer", "debloquer", "copier", "passer_obstacle",
    "frapper", "saisir", "pousser", "ligoter", "delier", "liberer", "degager", "trainer", "tuer", "ranimer",
    "remettre", "improviser", "composer", "conversation_pnj", "dialogue", "clarifier", "impossible"
]
METHODES_AUTORISEES = [
    "simple", "finesse", "force", "discret", "percussion", "levier", "traction", "assommer",
    "cri", "appel", "sifflement", "heler", "dessous", "dessus", "appui_mobile"
]
OPERATIONS_AUTORISEES = ["proposer", "negocier", "accepter", "refuser", "discuter", ""]
SUJETS_PAROLE = ["", "propos", "qui"]
DESTINATIONS_AUTORISEES = ["joueur", "salle", ""]

PROMPT_COMPILATEUR = """Tu es le compilateur d'intention de LE SEUIL.
Convertis la phrase du joueur en un appel mécanique JSON pour le moteur de jeu.
Ne produis AUCUN texte hors du JSON. Sois direct et concis dans ta pensée (2 à 3 lignes).
IMPORTANT : Les champs 'cible' et 'outil' doivent UNIQUEMENT contenir l'identifiant (id) exact tiré du contexte, une forme sonore autorisée, ou une chaîne vide. Ne mets JAMAIS de phrase, nom verbeux ou explication dans ces champs.

ACTIONS :
- observer : cible "scene", "lumiere", ou "contexte" (ou id d'un personnage pour l'observer).
- ecouter : tendre l'oreille (cible = "").
- examiner, toucher, lire : cible = id objet. Demander le prix d'un objet en vente se traduit par examiner cet objet.
  Ex: "combien coûtent les crochets ?" -> {"action": "examiner", "cible": "crochets"}
- aller / marcher : cible = direction ("nord", "sud", "est", "ouest", "nord-est", "nord-ouest", "sud-est", "sud-ouest").
- faufiler : avancer d'un pas à pas feutrés / discrètement, cible = direction.
- chasser : pas de côté ou à reculons en gardant son regard, cible = direction.
- tourner : se tourner sur place vers une direction, cible = direction.
- attendre : cible = "" ou secondes.
- prendre, poser : cible = id objet.
- acheter : cible = id objet en vente.
- lister_marchandises : le joueur demande ce que le vendeur présent propose (catalogue, articles en vente,
  « que vendez-vous ? »), sans viser un objet précis (cible = ""). Le prix d'un objet précis reste examiner.
- allumer, eteindre : cible = id source lumineuse.
- crocheter : cible = id porte ou serrure, outil = id de l'outil de crochetage dans l'inventaire (ex: "crochets").
- ouvrir, fermer : cible = id porte ou contenant.
- deverrouiller, verrouiller : cible = id porte ou contenant, outil = id de la clé dans l'inventaire.
- frapper : attaquer ou neutraliser au contact. cible = id personnage ou objet, outil = id arme portée ou "" (mains nues), methode = "simple" (frapper/attaquer) ou "assommer" (assommer, étrangler, étouffer, neutraliser sans tuer).
- saisir : agripper/maîtriser un personnage au contact (cible = id personnage, outil = "", methode = "simple").
- pousser : bousculer un personnage au contact (cible = id personnage, outil = direction ou "").
- ligoter : attacher un personnage sans défense ou maintenu (cible = id personnage, outil = id lien porté).
- delier, liberer, degager : défaire les liens d'un personnage (delier), ses propres liens (liberer) ou se dégager d'une prise (degager).
- trainer : tirer un corps sans défense d'une case (cible = id personnage, outil = direction).
- tuer : achever un personnage déjà sans défense (inconscient ou ligoté) (cible = id personnage, outil = id arme ou "").
- ranimer : réveiller un personnage inconscient au contact (cible = id personnage).
- remettre : cible = id de l'objet porté (ex: "anneau"), outil = id du destinataire (ex: "marchand").
  Donner ou remettre un objet convenu est toujours l'action mécanique remettre, pas une conversation.
- improviser : geste expressif ou émission sonore du joueur hors actions spécialisées :
  - chanter, fredonner un air : cible = "voix_melodique"
  - tousser, rire, grognement, raclement de gorge : cible = "voix_breve"
  - soupirer, souffler : cible = "souffle"
  - applaudir, taper dans ses mains ou du pied : cible = "corps_rythmique"
  - claquer des doigts : cible = "corps_bref"
  - geste corporel muet (s'étirer, hocher la tête, sourire...) : cible = ""
- composer : séquence d'étapes pour le vol furtif, émission vocale forte ou manœuvre combinée :
  - patienter : guetter deux minutes (cible="", destination="", outil="", methode="simple", difficulte=0).
  - deplacer : cible = id, destination = "joueur" (prendre) ou salle (poser). Pour voler : methode "discret".
  - emettre_son : cible = "joueur", methode = "cri" | "appel" | "sifflement" (ou cible = id objet sonore, methode = "simple").
  Attendre une occasion pour voler un objet = composer avec :
    étape 1 : patienter
    étape 2 : deplacer (cible = id, destination = "joueur", methode = "discret")
- conversation_pnj : négocier la récompense d'une mission avec un interlocuteur présent.
  {"action": "conversation_pnj", "personnage": id, "operation": "proposer"|"negocier"|"accepter"|"refuser"|"discuter", "mission": id, "montant_demande": int}
  - proposer : s'enquérir d'une prime de mission (montant_demande = 0).
  - negocier : marchander la récompense (montant_demande = entier souhaité).
  - accepter : accepter l'offre convenue (montant_demande = 0).
  - refuser : décliner l'offre de mission (montant_demande = 0).
  - discuter : parler de la mission sans changer d'accord (mission = "", montant_demande = 0).
- dialogue : le joueur pose une question ou adresse la parole à un personnage présent.
  {"action": "dialogue", "texte": "réponse directe dans la fiction (ex: Gorm : « La trousse de crochets coûte 8 pièces. »)"}
  sujet_parole : "qui" si le joueur demande l'identité de l'interlocuteur (son nom, qui il est), "propos" pour toute autre parole ; vide hors dialogue.
- clarifier : l'intention est trop ambiguë entre plusieurs cibles ou actions incompatibles (justification = question brève au joueur, à la 2e personne).
- impossible : aucune action du moteur ne couvre l'intention, ou un retour_moteur montre que le monde empêche réellement le geste. N'utilise JAMAIS impossible au premier essai si une action du moteur existe (propose l'action, même si la cible est verrouillée, fermée ou éloignée : c'est le moteur qui tranche).

CORRECTION SUR RETOUR DU MOTEUR :
Si retour_moteur est présent dans l'entrée, ta proposition précédente (proposition_refusee) a été refusée par le moteur (obstacle). Corrige la proposition en suivant exactement attendu (identifiant exact, outil requis, étape préalable dans composer comme ouvrir ou detacher avant deplacer, ou action demandée). Si aucune correction mécanique ne peut aboutir d'après attendu, utilise action = "impossible".
"""

SCHEMA_COMPILATEUR = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ACTIONS_AUTORISEES,
            "description": "L'action choisie parmi les actions autorisées ou 'conversation_pnj'."
        },
        "cible": {
            "type": "string",
            "description": "Identifiant exact de la cible, direction de sortie, forme sonore pour improviser, ou chaîne vide. Jamais de phrase."
        },
        "destination": {
            "type": "string",
            "enum": DESTINATIONS_AUTORISEES,
            "description": "Destination ('joueur' pour prendre, salle pour poser, ou chaîne vide)."
        },
        "outil": {
            "type": "string",
            "description": "Identifiant exact de l'outil dans l'inventaire ou destinataire pour remettre, ou chaîne vide. Jamais de phrase."
        },
        "methode": {
            "type": "string",
            "enum": METHODES_AUTORISEES,
            "description": "Méthode d'exécution."
        },
        "difficulte": {
            "type": "integer",
            "description": "0 sauf pour détacher une fixation."
        },
        "texte": {
            "type": "string",
            "description": "Réponse ou réplique directe dans la fiction pour action 'dialogue' (chaîne vide sinon). Jamais d'analyse à la 3e personne."
        },
        "sujet_parole": {
            "type": "string",
            "enum": SUJETS_PAROLE,
            "description": "Pour action 'dialogue' : 'qui' si le joueur demande l'identité de l'interlocuteur (son nom, qui il est), 'propos' pour toute autre parole ; chaîne vide hors dialogue."
        },
        "justification": {
            "type": "string",
            "description": "Courte raison interne du choix d'action (non affichée au joueur)."
        },
        "personnage": {
            "type": "string",
            "description": "Identifiant du PNJ pour une conversation, ou chaîne vide."
        },
        "operation": {
            "type": "string",
            "enum": OPERATIONS_AUTORISEES,
            "description": "Pour conversation_pnj : 'proposer', 'negocier', 'accepter', 'refuser', 'discuter', ou chaîne vide."
        },
        "mission": {
            "type": "string",
            "description": "Identifiant de la mission concernée, ou chaîne vide."
        },
        "montant_demande": {
            "type": "integer",
            "description": "Montant en pièces demandé ou convenu, ou 0."
        },
        "etapes": {
            "type": "array",
            "description": "Étapes pour une action composer, ou liste vide.",
            "items": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": list(OPERATIONS_COMPOSER)},
                    "cible": {"type": "string"},
                    "destination": {"type": "string"},
                    "outil": {"type": "string"},
                    "methode": {"type": "string", "enum": METHODES_AUTORISEES},
                    "difficulte": {"type": "integer"},
                },
                "required": ["operation", "cible", "destination", "outil", "methode", "difficulte"],
                "additionalProperties": False,
            }
        },
    },
    "required": [
        "action", "cible", "destination", "outil", "methode", "difficulte",
        "texte", "sujet_parole", "justification", "personnage", "operation", "mission", "montant_demande", "etapes"
    ],
    "additionalProperties": False,
}

_ACTIONS_PERSONNAGE = ("frapper", "saisir", "pousser", "ligoter", "delier", "trainer", "tuer", "ranimer")


def _forme_sonore(cible):
    """La forme acoustique de ``FORMES_SONORES`` désignée par le compilateur, sinon '' (geste muet)."""
    c_norm = normaliser(cible or "").replace(" ", "_")
    return c_norm if c_norm in FORMES_SONORES else ""


def _resoudre_cible_personnage(monde, cible, intention=""):
    """Résout l'identifiant d'un personnage visé par un geste physique (nom dans l'intention, contact, ou vue)."""
    if not monde:
        return cible
    salle_id = monde.joueur["salle"]
    persos = [
        o_id for o_id, o in monde.objets.items()
        if o.get("type") == "personnage" and o_id != "joueur"
    ]
    # 1. Si l'intention nomme explicitement un personnage (par son nom connu, apparence ou alias)
    i_norm = normaliser(intention or "")
    if i_norm:
        for o_id in persos:
            o = monde.objets[o_id]
            noms = [
                o_id,
                normaliser(o.get("nom", "")),
                normaliser(nom_pour_joueur(monde, o_id)),
                normaliser(o.get("apparence", "")),
                *(normaliser(a) for a in o.get("aliases", [])),
            ]
            if any(n and len(n) >= 3 and n in i_norm for n in noms):
                return o_id
    # 2. Si la cible proposée par le compilateur est un personnage au contact ou visible ici
    if cible in persos and (au_contact(monde, "joueur", cible) or monde.objets[cible].get("lieu") == salle_id or monde.visible(cible)):
        return cible
    # 3. Si le joueur est au contact d'un personnage (ex. « je l'étrangle » dans son dos), privilégier celui en face
    contacts = [o_id for o_id in persos if au_contact(monde, "joueur", o_id)]
    if contacts:
        from .geometrie import distance
        from .spatial import orientation_vers
        pos_j = tuple(monde.joueur.get("position") or (0, 0))
        regard = monde.joueur.get("orientation")
        contacts.sort(key=lambda o_id: (
            orientation_vers(pos_j, tuple(monde.objets[o_id].get("position") or pos_j)) != regard,
            distance(pos_j, tuple(monde.objets[o_id].get("position") or pos_j)),
        ))
        return contacts[0]
    # 4. Sinon, personnage visible dans la salle
    presents = [o_id for o_id in persos if monde.objets[o_id].get("lieu") == salle_id and monde.visible(o_id)]
    if len(presents) == 1:
        return presents[0]
    if cible in persos:
        return cible
    return cible


def determiner_modele(fournisseur, modele_souhaite=None):
    """Détermine le modèle adapté au fournisseur selon la configuration."""
    if modele_souhaite:
        return modele_souhaite
    from .config import MODELE_PAR_DEFAUT, MODELE_LOCAL, MODELE_CLAUDE, MODELE_MIMO
    cls_nom = fournisseur.__class__.__name__.lower()
    if "local" in cls_nom:
        return os.environ.get("LOCAL_MODEL", MODELE_LOCAL)
    if "anthropic" in cls_nom:
        return MODELE_CLAUDE
    if "mimo" in cls_nom:
        return MODELE_MIMO
    return os.environ.get("OPENAI_MODEL", MODELE_PAR_DEFAUT)


def extraire_contexte(monde):
    """Extrait le contexte compact strictement nécessaire à l'arbitrage mécanique (~150 jetons)."""
    salle_id = monde.joueur["salle"]
    salle = monde.data["salles"][salle_id]
    sorties = salle.get("sorties", {})
    objets = []
    inventaire = []
    vus = set()
    for id, o in monde.objets.items():
        if o.get("type") == "personnage":
            continue
        if o.get("lieu") in ("joueur", salle_id) or monde.accessible(id) or monde.visible(id):
            if id in vus:
                continue
            vus.add(id)
            item = {
                "id": id,
                "nom": o["nom"],
            }
            if o.get("en_vente"):
                item["en_vente"] = True
                item["prix"] = o.get("prix", 0)
            if o.get("lieu") == "joueur":
                inventaire.append(item)
            else:
                item["lieu"] = "salle"
                objets.append(item)
    pnjs = [
        {
            "id": id,
            "nom": nom_pour_joueur(monde, id),
            **({"au_contact": True} if au_contact(monde, "joueur", id) else {}),
        }
        for id, o in monde.objets.items()
        if o.get("type") == "personnage" and id != "joueur"
        and (o.get("lieu") == salle_id or monde.visible(id) or au_contact(monde, "joueur", id))
    ]
    missions = [
        {"mission": m_id, "objet": m.get("objet"), "donneur": m.get("donneur")}
        for m_id, m in monde.data.get("missions", {}).items()
    ]
    accords = contrats(monde)
    return {
        "salle": salle.get("nom", salle_id),
        "sorties": list(sorties.keys()),
        "objets": objets,
        "inventaire": inventaire,
        "interlocuteurs": pnjs,
        "missions": missions,
        "accords": accords,
        "or_joueur": monde.joueur.get("or", 0),
    }


def _liste_marchandises(monde):
    """Le catalogue de la salle, dit par son vendeur : des faits du moteur (articles, prix), jamais un texte du modèle."""
    en_vente = [o for o in monde.objets.values() if o.get("en_vente") and o.get("lieu") == monde.joueur["salle"]] if monde else []
    if not en_vente:
        raise RefusDeForme("Rien n'est à vendre ici.",
                           "lister_marchandises : aucun objet en_vente dans la salle ; réponds autrement (dialogue).")
    from .francais import quantite
    from .rendu import prix
    pnjs = [i for i, o in monde.objets.items()
            if o.get("type") == "personnage" and o.get("lieu") == monde.joueur["salle"] and i != "joueur"]
    nom_vendeur = nom_pour_joueur(monde, pnjs[0]).capitalize() if len(pnjs) == 1 else "Le marchand"
    articles = [f"{o['nom']} : {quantite(prix(monde, o), 'pièce')}" for o in en_vente]
    return {
        "action": "dialogue",
        "texte": f"{nom_vendeur} : « " + " ; ".join(articles) + ". Tu as de quoi payer ? »",
        "justification": "Liste des articles en vente dans l'échoppe.",
        "_deterministe": True,
    }


def normaliser_proposition(prop, monde=None, intention=""):
    """Harmonise la proposition avec les attentes strictes du moteur."""
    saisie_norm = normaliser(intention or "")
    if prop.get("action") == "lister_marchandises":
        return _liste_marchandises(monde)

    action = prop.get("action", "")
    # Invariant : une parole entre guillemets ou une question adressée (hors faisabilité d'un geste)
    # ne doit pas être transformée en simple observation silencieuse par le compilateur.
    if action != "conversation_pnj":
        from .commandes import faisabilite
        a_guillemets = "«" in (intention or "") or '"' in (intention or "")
        if a_guillemets and action in ("observer", "examiner", "attendre", "improviser"):
            action = "dialogue"
        elif "?" in (intention or "") and action in ("observer", "attendre") and not faisabilite(intention or ""):
            action = "dialogue"

    if action == "dialogue":
        cible_dial = _resoudre_cible_personnage(monde, prop.get("personnage") or prop.get("cible") or "", intention) if monde else (prop.get("personnage") or prop.get("cible") or "")
        # Invariant : la justification interne du compilateur ne doit jamais être copiée dans le texte joueur.
        return {
            "action": "dialogue",
            "texte": prop.get("texte") or "",
            "sujet_parole": prop.get("sujet_parole") if prop.get("sujet_parole") in ("propos", "qui") else "propos",
            "personnage": cible_dial or prop.get("personnage") or "",
            "cible": cible_dial or prop.get("cible") or "",
        }

    if action == "improviser":
        cible_brute = prop.get("cible", "")
        forme = _forme_sonore(cible_brute)
        cibles = []
        if monde and cible_brute and cible_brute not in FORMES_SONORES and cible_brute in monde.objets and monde.accessible(cible_brute):
            cibles = [cible_brute]
        outil = prop.get("outil", "")
        if not (monde and outil in monde.objets and monde.est_porte(outil) and monde.objets[outil].get("integrite")):
            outil = ""
        texte_intention = " ".join((intention or prop.get("justification") or forme or "geste").splitlines()).strip()[:240] or "geste"
        if forme:
            intensite_prop = prop.get("difficulte", 0)
            bruit = intensite_prop if isinstance(intensite_prop, int) and 1 <= intensite_prop <= 3 else (
                2 if forme in ("voix_melodique", "corps_rythmique") else 1
            )
            effets = [effet("son", "joueur", texte=forme, valeur=bruit)]
        else:
            bruit = 0
            effets = []
        return proposition_improviser(
            texte_intention,
            issue("Tu réalises ce geste.", effets),
            cibles=cibles,
            outil=outil,
            approche="expression",
            stat="",
            difficulte=0,
            minutes=1,
            bruit=bruit,
        )

    # 1. Action de remise d'objet
    if action == "remettre":
        salle_id = monde.joueur["salle"] if monde else ""
        presents = [i for i, o in monde.objets.items() if o.get("type") == "personnage" and o.get("lieu") == salle_id and i != "joueur"] if monde else []
        cible = prop.get("cible", "")
        # Un objet mal désigné se retrouve par son nom dans la saisie ; sans désignation, seul l'unique objet
        # porté convient. Jamais « le premier » : ce que le moteur ne peut établir, il le refuse (``preparer``).
        if monde:
            portes = [id for id, o in monde.objets.items() if o.get("lieu") == "joueur"]
            if cible not in portes:
                saisie_norm = normaliser(intention or "")
                nommes = [i for i in portes if i in saisie_norm or normaliser(monde.objets[i]["nom"]) in saisie_norm]
                if len(nommes) == 1:
                    cible = nommes[0]
                elif not cible and len(portes) == 1:
                    cible = portes[0]

        dest = prop.get("outil") or prop.get("personnage") or ""
        if monde and dest not in monde.objets:
            nommes = [i for i in presents if i in dest.lower() or normaliser(monde.objets[i]["nom"]) in normaliser(dest)]
            if len(nommes) == 1:
                dest = nommes[0]
        if not dest and len(presents) == 1:
            dest = presents[0]

        return {
            "action": "remettre",
            "cible": cible,
            "outil": dest,
            "methode": "simple",
            "difficulte": 0,
            "justification": "Remise physique de l'objet convenu.",
        }

    # 2. Opération de conversation
    if action == "conversation_pnj":
        op_brute = prop.get("operation", "proposer").lower()
        if "negoc" in op_brute:
            op = "negocier"
        elif "accept" in op_brute:
            op = "accepter"
        elif "refus" in op_brute:
            op = "refuser"
        elif "discut" in op_brute:
            op = "discuter"
        else:
            op = "proposer"
        perso = prop.get("personnage") or ""
        miss = prop.get("mission") or ""
        if monde:
            perso = _resoudre_cible_personnage(monde, perso, intention) or perso
            if not miss and perso:
                siennes = [m_id for m_id, m in monde.data.get("missions", {}).items() if m.get("donneur") == perso]
                if len(siennes) == 1:
                    miss = siennes[0]

        # Si une mission est mentionnée, ce n'est pas une simple discussion sans objet
        if op == "discuter" and miss:
            op = "proposer"

        montant = int(prop.get("montant_demande") or 0)
        # S'il y a un montant demandé positif en proposant, c'est une négociation
        if op == "proposer" and montant > 0:
            op = "negocier"
        elif op != "negocier":
            # Seule la négociation accepte un montant_demande non nul
            montant = 0

        return {
            "action": "conversation_pnj",
            "personnage": perso,
            "operation": op,
            "mission": miss,
            "montant_demande": montant,
        }

    # 3. Composition (enchaînement, émission sonore ou vol)
    if action == "composer":
        etapes = []
        for e in prop.get("etapes", []):
            op = e.get("operation", "")
            if op == "patienter":
                etapes.append({
                    "operation": "patienter",
                    "cible": "",
                    "destination": "",
                    "outil": "",
                    "methode": "simple",
                    "difficulte": 0,
                })
            elif op == "emettre_son":
                cible_son = e.get("cible", "") or "joueur"
                methode_son = e.get("methode", "cri")
                if cible_son in ("", "joueur") and methode_son not in ("cri", "appel", "sifflement"):
                    methode_son = "cri"
                etapes.append({
                    "operation": "emettre_son",
                    "cible": cible_son,
                    "destination": "",
                    "outil": "",
                    "methode": methode_son,
                    "difficulte": 0,
                })
            elif op == "detacher":
                etapes.append({
                    "operation": "detacher",
                    "cible": e.get("cible", ""),
                    "destination": "",
                    "outil": e.get("outil", ""),
                    "methode": e.get("methode") if e.get("methode") in ("simple", "levier", "finesse", "percussion") else "levier",
                    "difficulte": e.get("difficulte", 0),
                })
            elif op in ("deplacer", "prelever"):
                dest_dep = e.get("destination", "") or "joueur"
                if dest_dep in ("salle", "sol", "ici") and monde:
                    dest_dep = monde.joueur["salle"]
                meth_dep = e.get("methode", "discret")
                if meth_dep not in ("simple", "discret"):
                    meth_dep = "discret"
                etapes.append({
                    "operation": op,
                    "cible": e.get("cible", ""),
                    "destination": dest_dep,
                    "outil": e.get("outil", ""),
                    "methode": meth_dep,
                    "difficulte": 0,
                })
            else:
                etapes.append({
                    "operation": op,
                    "cible": e.get("cible", ""),
                    "destination": e.get("destination", "") if op in ("appuyer", "franchir") else "",
                    "outil": e.get("outil", ""),
                    "methode": e.get("methode") if e.get("methode") in METHODES_AUTORISEES and e.get("methode") != "discret" else "simple",
                    "difficulte": e.get("difficulte", 0) if op == "franchir_obstacle" else 0,
                })
        return {
            "action": "composer",
            "etapes": etapes,
            "justification": prop.get("justification", ""),
        }

    if action in ("clarifier", "impossible"):
        return {
            "action": action,
            "cible": "",
            "outil": "",
            "methode": "simple",
            "difficulte": 0,
            "justification": prop.get("justification", ""),
        }

    # 4. Actions simples standard (examiner, prendre, poser, aller, attendre, acheter, combat, etc.)
    cible = prop.get("cible", "")
    outil = prop.get("outil", "")
    methode = prop.get("methode", "simple")

    if action in _ACTIONS_PERSONNAGE:
        cible = _resoudre_cible_personnage(monde, cible or prop.get("personnage") or "", intention)
    if action in ("aller", "marcher") and (
        methode == "discret"
    ):
        action = "faufiler"

    if (monde and cible and cible not in monde.objets
            and action not in ("aller", "marcher", "faufiler", "chasser", "tourner", "liberer", "degager")
            and not (action == "observer" and cible in ("scene", "lumiere", "contexte"))):
        c_norm = normaliser(cible)
        for o_id, o in monde.objets.items():
            noms = [o_id, normaliser(o.get("nom", ""))] + [normaliser(a) for a in o.get("aliases", [])]
            if c_norm in noms:
                cible = o_id
                break
        else:
            for o_id, o in monde.objets.items():
                noms = [o_id, normaliser(o.get("nom", ""))] + [normaliser(a) for a in o.get("aliases", [])]
                if any(len(n) >= 3 and (n in c_norm or c_norm in n) for n in noms):
                    cible = o_id
                    break

    # Normalisation de outil (sauf pousser / trainer où outil est une direction)
    if action not in ("pousser", "trainer") and monde and outil:
        if outil not in monde.objets:
            o_norm = normaliser(outil)
            for o_id, o in monde.objets.items():
                noms = [o_id, normaliser(o.get("nom", ""))] + [normaliser(a) for a in o.get("aliases", [])]
                if o_norm in noms:
                    outil = o_id
                    break
            else:
                for o_id, o in monde.objets.items():
                    if o.get("lieu") == "joueur":
                        noms = [o_id, normaliser(o.get("nom", ""))] + [normaliser(a) for a in o.get("aliases", [])]
                        if any(len(n) >= 3 and (n in o_norm or o_norm in n) for n in noms):
                            outil = o_id
                            break
                else:
                    outil = ""

    # Pour assommer / étrangler, une lame est interdite par combat.valider (contondant ou mains nues "")
    if action == "frapper" and methode == "assommer" and monde and outil in monde.objets:
        from .combat import arme
        regle = arme(monde.objets[outil])
        if regle is None or regle[0]:
            outil = ""

    # Pour saisir / ranimer / liberer / degager, outil doit rester vide
    if action in ("saisir", "ranimer", "liberer", "degager"):
        outil = ""
    if action == "liberer" and not cible:
        cible = "joueur"

    # Déduction automatique de l'outil requis par l'action si manquant ou non trouvé
    if monde and (not outil or outil not in monde.objets):
        if action == "crocheter":
            adaptes = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and "crochetage" in o.get("usages", [])]
            if adaptes:
                outil = adaptes[0]
        elif action == "couper":
            adaptes = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and set(o.get("usages", [])) & {"couper", "couper_bois"}]
            if adaptes:
                outil = adaptes[0]
        elif action == "bloquer":
            adaptes = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and "cale" in o.get("usages", [])]
            if adaptes:
                outil = adaptes[0]
        elif action == "mouler":
            adaptes = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and "empreinte" in o.get("usages", [])]
            if adaptes:
                outil = adaptes[0]
        elif action == "deverrouiller":
            cles = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and cible in o.get("ouvre", [])]
            if cles:
                outil = cles[0]
        elif action == "ligoter":
            from .tenir import lien_valide
            liens = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and lien_valide(o)]
            if liens:
                outil = liens[0]

    if methode not in ("simple", "finesse", "levier", "percussion", "traction", "assommer"):
        methode = "simple"
    difficulte = prop.get("difficulte", 0) if action == "detacher" else 0

    return {
        "action": action,
        "cible": cible,
        "outil": outil,
        "methode": methode,
        "difficulte": difficulte,
        "justification": prop.get("justification", ""),
    }


def compiler(fournisseur, monde, intention, modele=None, timeout=30, effort=None, retour_moteur=None):
    """Appelle le fournisseur pour traduire l'intention en proposition mécanique."""
    ctx = extraire_contexte(monde)
    entree = {
        "contexte": ctx,
        "intention": intention,
    }
    if retour_moteur is not None:
        entree["retour_moteur"] = retour_moteur
    modele_choisi = determiner_modele(fournisseur, modele)
    if effort is None:
        cls_nom = fournisseur.__class__.__name__.lower()
        effort = "none" if "local" in cls_nom or "mimo" in cls_nom else "medium"
    demande = Demande(
        instructions=PROMPT_COMPILATEUR,
        entree=entree,
        intention=intention,
        fonction="compiler_intention",
        schema=SCHEMA_COMPILATEUR,
        modele=modele_choisi,
        effort=effort,
        timeout=timeout,
    )
    reponse = fournisseur.appeler(demande)
    try:
        proposition = normaliser_proposition(reponse.arguments, monde, intention=intention)
    except ErreurMonde as exc:
        exc.utilisation = reponse.utilisation
        exc.proposition_refusee = reponse.arguments
        raise
    return proposition, reponse.utilisation
