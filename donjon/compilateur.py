"""Compilateur d'intention : traduction rapide de la langue naturelle en proposition mécanique.

Ce composant extrait le contexte local réduit (salle, sorties, objets accessibles, PNJ présents,
missions et accords en cours) et utilise un fournisseur LLM (local ou cloud) avec un schéma
d'intention compact, sans consigne narrative ni double passe d'audit lourd.
"""
import copy
import os
import re

from .agendas import contrats
from .fournisseurs.contrat import Demande
from .improvisation import FORMES_SONORES, effet, issue, proposition as proposition_improviser
from .monde import ErreurMonde, normaliser
from .operations import OPERATIONS as OPERATIONS_COMPOSER
from .paroles import SCHEMA_PAROLE, TYPES as TYPES_PAROLE
from .passage import au_contact
from .refus import RefusDeForme
from .voix import nom_pour_joueur

ACTIONS_AUTORISEES = [
    "observer", "examiner", "toucher", "lire", "ecouter", "aller", "marcher", "faufiler", "chasser", "tourner", "attendre",
    "prendre", "poser", "acheter", "voler", "lister_marchandises", "allumer", "eteindre",
    "ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "detacher",
    "couper", "decouper", "assembler", "installer", "franchir", "desinstaller",
    "bloquer", "debloquer", "copier", "passer_obstacle",
    "frapper", "saisir", "pousser", "ligoter", "delier", "liberer", "degager", "trainer", "tuer", "ranimer",
    "remettre", "etablir_faits", "improviser", "composer", "conversation_pnj", "dialogue", "clarifier", "impossible"
]
METHODES_AUTORISEES = [
    "simple", "soigne", "finesse", "force", "discret", "percussion", "levier", "traction", "assommer",
    "cri", "appel", "sifflement", "heler", "dessous", "dessus", "appui_mobile"
]
OPERATIONS_AUTORISEES = ["proposer", "negocier", "accepter", "refuser", "discuter", ""]
SUJETS_PAROLE = ["", *TYPES_PAROLE]
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
- decouper : couper une barre ou un lien à une longueur donnée. cible = id de la pièce, outil = id outil tranchant (ex: "hache"), difficulte (ou montant_demande) = longueur_cm à couper (ex: 100).
- assembler : fabriquer une échelle (usage echelle) avec 2 montants, 1 barre pour les barreaux, 1 lien et 1 outil tranchant. cible = "montant_1,montant_2,barreaux,lien" (ou "" pour reprendre la suggestion du dossier atelier), outil = id outil (ex: "hache"), methode = "soigne" (sans jet, 2x temps) ou "simple" (rythme normal), montant_demande = longueur_cm (ex: 300, ou 0 pour défaut).
- installer : appuyer un assemblage (échelle) contre un appui vertical. cible = id assemblage, outil = id appui_vertical.
- franchir : monter ou descendre par un assemblage installé. cible = id assemblage installé, outil = "".
- desinstaller : retirer un assemblage de son appui. cible = id assemblage installé, outil = "".
- etablir_faits : établir un fait narratif (détail visuel, inscription, petit objet matérialisé, ou qualification physique d'un objet lorsque retour_moteur le demande).
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
  - prelever : séparer une pièce d'un lot (cible = id lot, destination = "joueur" ou salle, methode = "simple").
  - appuyer / franchir / soulever : installer un assemblage (appuyer: cible=id assemblage, outil=id appui), le franchir (franchir: cible=id assemblage), ou le retirer (soulever: cible=id assemblage).
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
- dialogue : le joueur pose une question ou adresse la parole à un personnage (ou à tous / à la cantonade).
  Une saisie entre guillemets (« ... »), avec un verbe de parole (je dis, je demande, je chuchote...) ou « à tous : ... » est TOUJOURS dialogue (ou conversation_pnj pour négocier une mission), même si ses mots évoquent un geste.
  Renseigne sujet_parole et contenu (liste de 1 à 3 actes de parole typés) selon ce que Corvus dit :
  - "propos" : parole ordinaire, salutation ou question générale -> contenu = [{"type": "propos", "sujet": "", "attribut": "", "valeur": ""}]
  - "qui" : demander qui est l'interlocuteur / son nom -> contenu = [{"type": "qui", "sujet": "", "attribut": "", "valeur": ""}]
  - "nom" : Corvus se présente sous un nom (sujet = "joueur" ou id du personnage dont il prend le nom) -> contenu = [{"type": "nom", "sujet": "joueur", "attribut": "", "valeur": ""}]
  - "localisation" : demander où se trouve une personne connue (sujet = id dans personnages_connus) -> contenu = [{"type": "localisation", "sujet": id_perso, "attribut": "", "valeur": ""}]
  - "ressource" : demander si l'interlocuteur possède un bien ou de quoi satisfaire un besoin sans l'acheter (sujet = nom du bien sans article ex: "bois", "pain", ou besoin général "faim" / "chaleur") -> contenu = [{"type": "ressource", "sujet": "...", "attribut": "", "valeur": ""}]
  - "reclamer" : réclamer ou interroger sur un dû (sujet = "" pour des pièces dues, ou id d'un objet appartenant à Corvus) -> contenu = [{"type": "reclamer", "sujet": "", "attribut": "", "valeur": ""}]
  - "demande" : demander qu'on donne/prête/vende un objet ou une part de ressource (sujet = id objet ou ressource, valeur = "" ou nombre de pièces offertes en chiffres ex: "2") -> contenu = [{"type": "demande", "sujet": id_objet, "attribut": "", "valeur": ""}]
  - "passage" : demander de s'écarter / laisser passer (sujet = "", valeur = "" ou pièces offertes en chiffres) -> contenu = [{"type": "passage", "sujet": "", "attribut": "", "valeur": ""}]
  - "aveu" : avouer un geste fait sur un objet d'autrui (sujet = id objet, valeur = geste parmi prendre, poser, ouvrir, fermer, deverrouiller, verrouiller, crocheter, forcer, manger, servir, alimenter, allumer, eteindre) -> contenu = [{"type": "aveu", "sujet": id_objet, "attribut": "", "valeur": geste}]
  - "affirmation" : affirmer un fait sur un sujet (sujet = id objet/personnage/"joueur", attribut = "lieu"|"verrouillee"|"fiable", valeur = id lieu/porteur ou "oui"/"non") -> contenu = [{"type": "affirmation", "sujet": ..., "attribut": ..., "valeur": ...}]
  - "avis" : prévoir qu'un lieu connu sera menacé ou épargné par l'eau (sujet = id dans salles_connues, attribut = "menace", valeur = "oui"|"non") -> contenu = [{"type": "avis", "sujet": id_salle, "attribut": "menace", "valeur": "oui"}]
  - "proposition" : proposer un échange lié {"type": "proposition", "demande": terme, "contrepartie": terme} où chaque terme est {"type": "objet"|"part", "objet": id}, {"type": "tache", "condition": {"objet": id, "allume": true|"verrouillee": true|"lieu": id_salle|"servir": id_perso}}, {"type": "pieces", "montant": int} ou (en contrepartie) {"type": "rien"}.
  Hors dialogue, sujet_parole = "" et contenu = [].
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
            "description": "Pour action 'dialogue' : type principal de la parole ('propos', 'qui', 'nom', 'localisation', 'ressource', 'reclamer', 'demande', 'passage', 'aveu', 'affirmation', 'avis', 'proposition') ; chaîne vide hors dialogue."
        },
        "contenu": copy.deepcopy(SCHEMA_PAROLE["properties"]["contenu"]),
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
        "texte", "sujet_parole", "contenu", "justification", "personnage", "operation", "mission", "montant_demande", "etapes"
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


def extraire_contexte(monde, intention=""):
    """Extrait le contexte compact strictement nécessaire à l'arbitrage mécanique (~150 jetons)."""
    from . import paroles
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
    personnages_connus = [
        {"id": id, "nom": monde.objets[id]["nom"].split(",")[0]}
        for id in paroles.identites(monde)
    ]
    salles_connues = [
        {"id": s, "nom": monde.data["salles"][s].get("nom", s)}
        for s in sorted(monde.data.get("salles", {}))
        if paroles._connu_du_joueur(monde, s)
    ]
    connus_ids = sorted(set(monde.data.get("connus", [])) | set(monde.data.get("souvenirs_visuels", {})))
    objets_connus = [
        {"id": id, "nom": monde.objets[id]["nom"]}
        for id in connus_ids
        if id in monde.objets and monde.objets[id].get("type") != "personnage" and id not in vus
    ]
    from .biens import etat_comptes_joueur
    comptes = etat_comptes_joueur(monde, [p["id"] for p in pnjs])
    ctx = {
        "salle": salle.get("nom", salle_id),
        "sorties": list(sorties.keys()),
        "objets": objets,
        "inventaire": inventaire,
        "interlocuteurs": pnjs,
        "personnages_connus": personnages_connus,
        "salles_connues": salles_connues,
        "objets_connus": objets_connus,
        "missions": missions,
        "accords": accords,
        "or_joueur": monde.joueur.get("or", 0),
    }
    if comptes:
        ctx["comptes"] = comptes
    from .artisanat import dossier as dossier_atelier
    d_atelier = dossier_atelier(monde)
    if d_atelier:
        ctx["atelier"] = d_atelier
    if intention:
        prev = paroles.prevue(monde, intention)
        if "personnage" in prev:
            ctx["parole_prevue"] = prev
    return ctx


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


def _normaliser_terme_proposition(terme, monde):
    """Résout les noms connus en identifiants dans un terme d'échange (``proposition``)."""
    if not isinstance(terme, dict) or not monde:
        return terme
    from .paroles import resoudre
    copie = copy.deepcopy(terme)
    if "objet" in copie and isinstance(copie["objet"], str) and copie["objet"] not in monde.objets:
        res = resoudre(monde, copie["objet"])
        if res:
            copie["objet"] = res
    if isinstance(copie.get("condition"), dict):
        cond = copie["condition"]
        for cle in ("objet", "lieu", "servir"):
            if cle in cond and isinstance(cond[cle], str):
                res = resoudre(monde, cond[cle])
                if res:
                    cond[cle] = res
    return copie


def _normaliser_contenu_parole(prop, monde=None, intention=""):
    """Construit la liste ``contenu`` de ``parole_joueur`` à partir de ``contenu`` ou ``sujet_parole``."""
    from .paroles import nom_dans
    sp = prop.get("sujet_parole") if prop.get("sujet_parole") in TYPES_PAROLE else "propos"
    brut = prop.get("contenu")
    if isinstance(brut, list) and brut:
        # Si le modèle a laissé un unique propos générique alors que sujet_parole est plus précis, privilégier sujet_parole.
        if len(brut) == 1 and isinstance(brut[0], dict) and brut[0].get("type") == "propos" and sp != "propos":
            brut = []
    if isinstance(brut, list) and brut:
        resultat = []
        for c in brut[:3]:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "proposition":
                item = copy.deepcopy(c)
                if "demande" in item:
                    item["demande"] = _normaliser_terme_proposition(item["demande"], monde)
                if "contrepartie" in item:
                    item["contrepartie"] = _normaliser_terme_proposition(item["contrepartie"], monde)
                resultat.append(item)
            else:
                type_c = c.get("type") if c.get("type") in TYPES_PAROLE else "propos"
                resultat.append({
                    "type": type_c,
                    "sujet": str(c.get("sujet") or ""),
                    "attribut": str(c.get("attribut") or ""),
                    "valeur": str(c.get("valeur") or ""),
                })
        if resultat:
            return resultat

    cible = str(prop.get("cible") or "")
    dest = str(prop.get("destination") or "")
    outil = str(prop.get("outil") or "")
    op = str(prop.get("operation") or "")
    montant = int(prop.get("montant_demande") or 0)
    offre_str = str(montant) if montant > 0 else ""

    if sp in ("propos", "qui"):
        return [{"type": sp, "sujet": "", "attribut": "", "valeur": ""}]
    if sp == "nom":
        sujet = cible or ((nom_dans(monde, intention) if monde else None) or "joueur")
        return [{"type": "nom", "sujet": sujet, "attribut": "", "valeur": ""}]
    if sp in ("localisation", "ressource", "reclamer"):
        return [{"type": sp, "sujet": cible, "attribut": "", "valeur": ""}]
    if sp == "demande":
        return [{"type": "demande", "sujet": cible, "attribut": "", "valeur": offre_str}]
    if sp == "passage":
        return [{"type": "passage", "sujet": "", "attribut": "", "valeur": offre_str}]
    if sp == "aveu":
        return [{"type": "aveu", "sujet": cible, "attribut": "", "valeur": op or outil}]
    if sp == "avis":
        return [{"type": "avis", "sujet": cible or dest, "attribut": "menace", "valeur": "oui"}]
    if sp == "affirmation":
        attr = "lieu" if dest else ""
        return [{"type": "affirmation", "sujet": cible, "attribut": attr, "valeur": dest or outil}]
    return [{"type": "propos", "sujet": "", "attribut": "", "valeur": ""}]


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
        contenu = _normaliser_contenu_parole(prop, monde, intention)
        if any(isinstance(c, dict) and c.get("type") == "qui" for c in contenu):
            sujet_parole = "qui"
        elif contenu and isinstance(contenu[0], dict) and contenu[0].get("type") in TYPES_PAROLE:
            sujet_parole = contenu[0]["type"]
        else:
            sujet_parole = "propos"
        # Invariant : la justification interne du compilateur ne doit jamais être copiée dans le texte joueur.
        return {
            "action": "dialogue",
            "texte": prop.get("texte") or "",
            "sujet_parole": sujet_parole,
            "contenu": contenu,
            "personnage": prop.get("personnage") or "",
            "cible": prop.get("cible") or "",
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

    if action == "etablir_faits":
        return {
            "action": "etablir_faits",
            "ajouts": prop.get("ajouts") if isinstance(prop.get("ajouts"), list) else [],
            "justification": prop.get("justification", ""),
        }

    # 4. Actions simples standard et atelier (decouper, assembler, installer, franchir, desinstaller, etc.)
    cible = prop.get("cible", "")
    outil = prop.get("outil", "")
    methode = prop.get("methode", "simple")

    if action == "assembler":
        from .artisanat import dossier as dossier_atelier, ressources_libres
        pieces_dict = prop.get("pieces")
        if isinstance(pieces_dict, dict) and "montants" in pieces_dict and "barreaux" in pieces_dict:
            montants = list(pieces_dict["montants"])
            barreaux = str(pieces_dict["barreaux"])
            lien = str(prop.get("lien") or "")
        else:
            jetons = [t.strip() for t in (cible or "").replace(";", ",").split(",") if t.strip()]
            montants = jetons[:2] if len(jetons) >= 2 else []
            barreaux = jetons[2] if len(jetons) >= 3 else ""
            lien = jetons[3] if len(jetons) >= 4 else (prop.get("lien") or "")
        if monde:
            d_at = dossier_atelier(monde) or {}
            sugg = (d_at.get("suggestion") or {}).get("proposition") or {}
            perches_libres = ressources_libres(monde, "perche")
            liens_libres = ressources_libres(monde, "lien")
            if len(montants) < 2:
                montants = list(sugg.get("montants") or perches_libres[:2])
                while len(montants) < 2:
                    montants.append("")
            if not barreaux:
                barreaux = str(sugg.get("traverses") or (perches_libres[2] if len(perches_libres) >= 3 else ""))
            if not lien:
                lien = str(sugg.get("lien") or (liens_libres[0] if liens_libres else ""))
            if not outil or outil not in monde.objets:
                adaptes = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and "couper_bois" in o.get("usages", [])]
                outil = str(sugg.get("outil") or (adaptes[0] if adaptes else outil))
        rythme = prop.get("rythme") if prop.get("rythme") in ("normal", "soigne") else (
            "soigne" if methode == "soigne" or any(w in saisie_norm for w in ("soigne", "temps", "presser", "calme")) else "normal"
        )
        m_len_asm = re.search(r"\d+", str(prop.get("longueur_cm") or prop.get("montant_demande") or prop.get("texte") or ""))
        longueur_cm = int(m_len_asm.group(0)) if m_len_asm else 300
        if not 100 <= longueur_cm <= 500:
            longueur_cm = 300
        largeur_cm = int(prop.get("largeur_cm") or 35)
        diff_ass = 0 if rythme == "soigne" else (int(prop.get("difficulte") or 12) if 10 <= int(prop.get("difficulte") or 0) <= 18 else 12)
        return {
            "action": "assembler",
            "usage": str(prop.get("usage") or "echelle"),
            "pieces": {"montants": montants[:2], "barreaux": barreaux},
            "lien": lien,
            "outil": outil,
            "longueur_cm": longueur_cm,
            "largeur_cm": largeur_cm,
            "difficulte": diff_ass,
            "rythme": rythme,
            "justification": prop.get("justification") or "Assembler une échelle.",
        }

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
    if action == "installer" and not outil and prop.get("destination"):
        outil = prop.get("destination", "")
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
                    if o.get("lieu") == "joueur" or (action == "installer" and o.get("appui_vertical")):
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

    # Pour saisir / ranimer / liberer / degager / franchir / desinstaller, outil doit rester vide
    if action in ("saisir", "ranimer", "liberer", "degager", "franchir", "desinstaller"):
        outil = ""
    if action == "liberer" and not cible:
        cible = "joueur"
    if action in ("installer", "franchir", "desinstaller") and monde:
        if not cible or not monde.objets.get(cible, {}).get("assemblage"):
            assemblages = [o_id for o_id, o in monde.objets.items() if o.get("assemblage") and monde.accessible(o_id)]
            if len(assemblages) == 1:
                cible = assemblages[0]
        if action == "installer" and (not outil or outil not in monde.objets):
            appuis = [o_id for o_id, o in monde.objets.items() if o.get("appui_vertical") and monde.accessible(o_id)]
            if len(appuis) == 1:
                outil = appuis[0]

    # Déduction automatique de l'outil requis par l'action si manquant ou non trouvé
    if monde and (not outil or outil not in monde.objets):
        if action == "crocheter":
            adaptes = [o_id for o_id, o in monde.objets.items() if o.get("lieu") == "joueur" and "crochetage" in o.get("usages", [])]
            if adaptes:
                outil = adaptes[0]
        elif action in ("couper", "decouper"):
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

    if action == "decouper":
        m_len_dec = re.search(r"\d+", str(prop.get("longueur_cm") or prop.get("difficulte") or prop.get("montant_demande") or prop.get("texte") or ""))
        longueur_dec = int(m_len_dec.group(0)) if m_len_dec else 0
        return {
            "action": "decouper",
            "cible": cible,
            "outil": outil,
            "longueur_cm": longueur_dec,
            "justification": prop.get("justification", ""),
        }

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


PROMPT_COMPILATEUR_FAITS = """Tu établis des faits narratifs ou des qualifications physiques dans LE SEUIL.
Tu reçois l'intention du joueur, le catalogue `faits_narratifs_proposables` (supports, qualifiables, évolutions, potentiel_invention) et éventuellement `qualification_requise` ou `retour_moteur`.
Propose `ajouts` (1 à 3 éléments) strictement conformes au schéma :
- Si `qualification_requise` demande la capacité "tranchable" d'un objet avec un moyen (outil), utilise un ajout `{"type": "qualification", "ancrage": <objet>, "moyen": <moyen>, "coupe_possible": <true|false>}` d'après le matériau, la masse, la description de l'objet et l'outil.
- Si `qualification_requise` demande une autre capacité ("lumiere", "son", etc.), utilise `{"type": "qualification", "ancrage": <objet>, "capacites": [...]}` si l'objet possède réellement cette capacité, sinon `{"type": "qualification", "ancrage": <objet>, "ecartees": [<capacite>]}`.
- Si un objet doit être décrit physiquement (`physique`), utilise `{"type": "qualification", "ancrage": <objet>, "physique": {"forme": "barre"|"plaque"|"lien"|"bloc"|"etoffe", "matiere": ..., "pieces": ..., "nom_piece": "", "dimensions": {"longueur_cm": ..., "largeur_cm": ..., "epaisseur_cm": ..., "diametre_cm": 0, "hauteur_cm": 0}}}` cohérent avec sa masse et son matériau (une planche ou perche est de forme `"barre"`).
- Si un passage sous obstacle doit être décrit (`passage`), utilise `{"type": "qualification", "ancrage": <objet>, "passage": {"degagement_cm": ..., "hauteur_cm": ..., "largeur_cm": ..., "profondeur_cm": ..., "charge_kg": ..., "appuis": <true|false>}}`.
- Pour un détail visuel ou une inscription sur un support de `supports`, utilise `type: "detail"` ou `"inscription"`.
- Pour matérialiser un petit objet sur un support (dans la limite de `potentiel_invention`), utilise `type: "objet"`.
"""


def compiler_faits(
    fournisseur,
    monde,
    intention,
    modele=None,
    timeout=30,
    effort=None,
    qualification_requise=None,
    retour_moteur=None,
):
    """Appelle le fournisseur pour produire un ajout typé conforme à ``SCHEMA_FAITS``."""
    from .faits_locaux import SCHEMA_FAITS, catalogue as catalogue_faits
    entree = {
        "intention": intention,
        "faits_narratifs_proposables": catalogue_faits(monde),
    }
    if qualification_requise is not None:
        entree["qualification_requise"] = qualification_requise
    if retour_moteur is not None:
        entree["retour_moteur"] = retour_moteur
    modele_choisi = determiner_modele(fournisseur, modele)
    if effort is None:
        cls_nom = fournisseur.__class__.__name__.lower()
        effort = "none" if "local" in cls_nom or "mimo" in cls_nom else "medium"
    demande = Demande(
        instructions=PROMPT_COMPILATEUR_FAITS,
        entree=entree,
        intention=intention,
        fonction="etablir_faits",
        schema=SCHEMA_FAITS,
        modele=modele_choisi,
        effort=effort,
        timeout=timeout,
    )
    reponse = fournisseur.appeler(demande)
    return reponse.arguments, reponse.utilisation


def compiler(fournisseur, monde, intention, modele=None, timeout=30, effort=None, retour_moteur=None):
    """Appelle le fournisseur pour traduire l'intention en proposition mécanique."""
    ctx = extraire_contexte(monde, intention=intention)
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
