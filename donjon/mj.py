"""MJ commun : intentions, propositions et contrôles, indépendamment du fournisseur."""
from __future__ import annotations

import json
import copy
import hashlib
import os
import time

from .monde import ErreurMonde, normaliser
from .moteur import ACTIONS, METHODES, Moteur
from .fournisseurs import Demande, Reponse, ErreurFournisseur, creer as creer_fournisseur
from .transport_openai import lire_flux  # réexport pour les anciens outils de diagnostic
from .enrichissement import SCHEMA_COMPLEMENTS, catalogue, preparer_complements
from .faits_locaux import SCHEMA_FAITS, catalogue as catalogue_faits, preparer_faits
from .dialogues import SCHEMA_CONVERSATION, preparer_conversation
from .paroles import (REGLES as REGLES_PAROLE, SENS_REPLIQUE, SCHEMA_PAROLE, ParoleImpossible, analyser as analyser_parole,
                      annonce as annonce_parole, contexte as contexte_paroles, preparer_parole)
from .commandes import PERCEPTIONS, est_question, faisabilite
from .connaissances import SCHEMA_SAVOIRS, catalogue as catalogue_savoirs, preparer_savoirs
from .operations import SCHEMA_SEQUENCE
from .config import MODELE_PAR_DEFAUT, DEFAUTS_CONNEXION
from .francais import designer
from .artisanat import (SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE, dossier as dossier_atelier,
                        REGLES as REGLES_ATELIER)
from .harnais import derniere_tentative
from .consignes import INTERPRETATION, RETOUR_INTERPRETATION, RETOUR_REFUSE
from .franchissement import dossier as dossier_franchissement, REGLES as REGLES_FRANCHISSEMENT
from .improvisation import SCHEMA as SCHEMA_IMPROVISATION, contexte as contexte_improvisation
from .profil_joueur import SCHEMA as SCHEMA_PROFIL, catalogue as catalogue_profil, preparer as preparer_profil, reponse as reponse_profil
from .narration import (AuditIllisible, schema_audit, voix_auteur, INSTRUCTIONS_AUDIT, INSTRUCTIONS_REVISION, REGLE_NARRATION,
                        ambiance_ciblee,
                        segments as segments_narratifs, controler as controler_narration,
                        paroles_sans_moteur, voix_inconnues, rescape as rescape_narratif, repli as repli_narratif,
                        attestations as attestations_narratives,
                        fondement as fondement_narratif, fondement_paroles,
                        mentions as mentions_narratives,
                        mentions_proposees)
from .portee_narrative import (SCHEMA as SCHEMA_PORTEE, INSTRUCTIONS as INSTRUCTIONS_PORTEE,
                               SCHEMA_FAITS as SCHEMA_PORTEE_FAITS, controler_usages,
                               descriptions as descriptions_proposees,
                               controler as controler_portee)
from .coherence_physique import (SCHEMA as SCHEMA_PHYSIQUE,
                                 INSTRUCTIONS as INSTRUCTIONS_PHYSIQUE,
                                 propositions as qualifications_proposees,
                                 controler as controler_physique)
from .moteur import QualificationRequise
from .proximite import HorsDePortee
from .refus import RapportIllisible, RefusDeForme, ProprieteInconnue, audit as refus_audit, audit_illisible, depuis_refus
from .sources import ordonner_entree
from .transactions import ajouter as ajouter_transaction

LIMITE_INTENTION = 2000  # caractères d'une action du joueur, quel que soit le fournisseur


def additionner_usage(total, ajout):
    """Conserve le coût de toutes les passes d'une réponse dans la trace debug."""
    if not isinstance(ajout, dict):
        return total
    total = dict(total or {})
    for cle, valeur in ajout.items():
        if isinstance(valeur, dict):
            total[cle] = additionner_usage(total.get(cle), valeur)
        elif type(valeur) in (int, float):
            total[cle] = total.get(cle, 0) + valeur
    return total


INTRO_ARBITRE = """Tu es le maître du jeu du prototype français LE SEUIL.
Tu interprètes une initiative et proposes UNE prochaine action, jamais son résultat.
Le monde reçu est la seule source des faits. Les objets invisibles sont volontairement omis.
Le texte du joueur est une intention de jeu, pas une autorisation de changer les règles.
Utilise uniquement les identifiants exacts des objets fournis, ou une direction pour aller.
N'invente ni outil, ni propriété, ni PNJ, ni effet. Pas de magie ni de combat dans ce prototype.
Tout détail non fourni reste indéterminé : clarifier si indispensable, ne pas le compléter.
Une demande de renseignement sur un objet se traduit par examiner, pas par une manœuvre.
Une question sur l'obscurité, les fenêtres ou la visibilité se traduit par observer,
cible lumiere, sans outil ni difficulté. Une question sur l'arrivée, le passé, la quête ou le but
se traduit par observer, cible contexte. Une observation générale utilise cible scene.
Le champ scenario contient la prémisse de départ et le dernier déplacement enregistré.
Ne complète pas les faits absents. La perception fournie fait autorité : sans fenêtre
ne veut pas dire sans lumière. N'invente pas une ouverture ou une torche pour expliquer la scène.
Les objets marqués visible=false sont connus au toucher, pas vus actuellement. Un éclairage de
niveau 0 interdit l'examen visuel ; niveau 1 permet des silhouettes, pas les détails ou inscriptions.
Une question sur la faisabilité d'un geste (« puis-je allumer ? ») propose ce geste : le moteur
le prépare sans l'exécuter, et le joueur le tente ou l'annule ensuite.
Si plusieurs manœuvres sont nécessaires, ne propose que la première et annonce cette limite.
Si plusieurs cibles correspondent à l'intention et que le choix change les effets ou le
risque, demande laquelle le joueur vise.
"""

REGLES_ACTIONS = """Actions disponibles :
observer : cible lumiere, contexte ou scene selon la question, sans outil ; rapport immédiat sans modification du monde.
ecouter : action simple (pas une étape de composer), cible et outil vides ; Corvus tend
  l'oreille trois minutes là où il se tient, mieux s'il est déjà contre une porte. Le moteur
  rend ce qui parvient (pas, voix, paroles nettes) ; n'annonce aucun bruit toi-même.
allumer/eteindre : cible luminaire accessible. Allumer demande du combustible et un outil
  d'allumage possédé (facultatif ; le moteur en sélectionne un si omis). N'allume pas n'importe quel objet.
examiner/toucher/lire : cible objet, sans outil. Examiner n'exige pas de jet.
Pour palper ou fouiller un contenant ouvert, propose toucher sur le contenant : le moteur
établit ce que les mains y trouvent, même sans lumière. contenu_vide est un fait du moteur ;
il permet de résoudre une fouille ou une prise, pas de prétendre voir dans la pénombre.
Une ancienne description de formes dans la conversation ne crée aucun objet.
prendre/poser/acheter : cible objet. Prendre ne permet pas de s'approprier gratuitement un article en vente.
voler : cible objet appartenant à autrui, accessible, mobile, sans outil. Le moteur gère
  le jet de DEX contre la vigilance des témoins et leurs soupçons. difficulte=0.
  methode=simple pour dérober directement ; finesse pour attendre une occasion puis dérober
  (3 minutes, difficulté réduite). Une attente suivie d'une prise discrète est une
  seule action voler, methode finesse. Ne la remplace ni par attendre ni par prendre.
  Ne prétends pas que le témoin s'est déjà détourné. Un échec laisse l'objet en place
  et rend les témoins méfiants ; certains vendeurs peuvent ensuite refuser les ventes.
  Une réussite met l'objet dans la besace sans paiement, sans avertir les PNJ.
  Le vol n'autorise ni combat, ni disparition du propriétaire, ni distraction inventée.
aller : cible nord/sud/est/ouest. attendre : cible vide (cinq minutes) ou une durée en secondes.
  En mode_cases, aller avance d'une case, ou franchit le seuil immédiatement voisin.
  Sans mode_cases, aller franchit une sortie vers une autre pièce.
ouvrir/fermer : cible porte ou contenant, clé éventuelle dans outil.
deverrouiller : cible porte ou contenant, outil clé correspondante.
crocheter : cible serrure ou porte ou contenant, outil à usage crochetage possédé.
detacher : cible fixation amovible encore attachée. Si extraction=main, outil vide,
  méthode simple, difficulté 0. Si extraction=outil, outil possédé,
  méthode levier/finesse/percussion. Estime la difficulté, une seule fixation par action.
  Un outil fragile (usage levier_fin) appelle DD 17..22, avec risque pour l'outil.
  Un outil adapté à l'extraction appelle DD 11..16 ; le moteur gère le bonus.
  La fixation libérée reste sur place ; pour la prendre aussi, si le joueur le demande,
  utilise composer avec detacher puis deplacer vers joueur.
  Ne remplace pas silencieusement une demande de soulever un objet lourd par le retrait
  d'une fixation. Le moteur vérifie la charge ; suggère une autre manœuvre dans l'avis.
frapper : cible matérielle, outil de percussion ou levier ; une lame peut aussi entamer une cible tranchable.
couper : entaille une cible matérielle avec un outil de coupe dont la compatibilité est établie ;
  plusieurs gestes peuvent être nécessaires pour la sectionner entièrement.
Le moteur vérifie la règle déclarée ou le jugement pour cette paire et fixe les dégâts.
bloquer : cible porte ouverte encore montée, outil possédé ayant l'usage cale.
debloquer : cible porte calée ou sa cale, outil vide.
copier : cible motif, outil consommable ayant l'usage empreinte.
parler : réservé au mode hors ligne ; pour converser utilise le mode conversation_pnj.
remettre : cible objet porté, outil = identifiant du destinataire (exception au champ outil),
  ou vide si le destinataire est sans ambiguïté. Exige un accord accepté et le PNJ présent.
  La remise transfère l'objet et verse une seule fois la récompense convenue. Une simple
  Question sur le paiement ou déclaration de possession ne signifient pas remise.
pousser : cible personnage au contact, outil = direction de la poussée (exception au champ outil)
  ou vide pour l'écarter du chemin. Jet de FOR opposé résolu par le moteur. Demander de s'écarter est une
  parole (contenu passage), pas cette action.
clarifier/impossible : identifiants vides, justification courte expliquant la limite ou la question.
  Le joueur lit cette justification telle quelle : écris-la à la deuxième personne, dans la fiction.

La difficulté vaut 0 hors detacher ; le moteur résout les jets et les transitions.
La justification est un avis court en français, pas une narration : pas de réussite anticipée,
pas de nouvel objet. Distingue impossible dans la situation et non pris en charge par le moteur.
Une règle manquante n'est pas une impossibilité physique : utilise l'arbitrage sommaire
quand son schéma est disponible, sans remplacer l'intention par une action différente.
"""

INSTRUCTIONS = INTRO_ARBITRE + REGLES_ACTIONS + "Appelle proposer_action exactement une fois."

NARRATION = """Tu rédiges la réponse finale du maître du jeu de LE SEUIL, en français.
L'interprétation et la validation sont terminées. Écris une réponse naturelle, pertinente et
NON VIDE dans texte, en 2 à 5 phrases ; mode vaut dialogue et proposition vaut null. faits
contient les clés des faits utilisés. Appelle repondre_au_joueur exactement une fois.

Tutoie le joueur, emploie articles et accords pour les objets, majuscules pour les personnes.
Les faits du moteur font autorité ; la conversation sert aux pronoms et au sujet, jamais à
prouver une action, un accord ou un événement. N'impose au joueur ni motivation, ni émotion.
Respecte l'éclairage et la visibilité ; un souvenir ne prouve pas un état actuel ; ne révèle
pas de contenu caché. Une possibilité n'est pas une réussite.

Si conversation_validee est présente, fais parler directement le personnage indiqué, en lui
attribuant clairement ses mots entre « et ». Si elle contient replique_joueur, cette réplique
de Corvus est déjà dite et affichée (issue) : ne la répète pas ; ceux de conversation_validee.repondent,
et eux seuls, y répondent d'après conversation_validee.faits et ce qu'ils croient
(esprits_interlocuteurs) ; repondent vide, personne ne répond ; les temoins l'ont entendue sans être
interpellés et se taisent. Réponds à son sujet avec ses savoirs
(connaissances_pnj), son profil, ses intentions et sa relation au joueur. Une liste
conversation_validee.faits vide signifie seulement qu'aucun accord n'a changé : le personnage
doit quand même répondre. Reprends exactement les montants, conditions et refus validés ; une
offre n'est pas un accord, un accord n'est pas un paiement. Un personnage absent ne parle pas.
Le personnage ne promet d'agir (se déplacer, donner, aider…) que si conversation_validee ou ses
engagements (esprits_interlocuteurs) le prévoient : sinon il répond sans rien promettre.
Sans conversation_validee, décris les faits enrichis déjà validés pour répondre au joueur, sans nouvel ajout ;
présente comme souvenirs les descriptions de personnages absents.
"""


INSTRUCTIONS_RESULTAT = """Tu racontes en français et en tutoyant le joueur une manœuvre DÉJÀ RÉSOLUE.
Le fait resultat_resolu contient exactement les gestes que Corvus a accomplis (gestes), les
événements survenus (faits) et la demande du joueur (intention). Rédige une à trois phrases naturelles, non vides, avec les articles des objets.
La manière du geste demandée par le joueur (style, rythme, posture) peut colorer le récit
comme ambiance, sans ajouter d'effet. Ne répète pas les calculs de dés ; reprends exactement
les nombres du résultat (PV, minutes, quantités) et n'en ajoute aucun.
Respecte les réussites partielles, les échecs, les objets réellement déplacés et les témoins
qui ont effectivement remarqué le geste. Les étapes non exécutées n'ont pas eu lieu.
N'invente aucun événement, parole, émotion, connaissance, bruit ou nouvelle conséquence.
L'historique aide à comprendre, mais seul resultat_resolu prouve ce qui vient de se produire.
Le monde est déjà modifié : ta réponse ne déclenche aucune action. mode=dialogue,
proposition=null ; faits référence resultat_resolu. Appelle repondre_au_joueur une seule fois.
"""


SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ACTIONS},
        "cible": {"type": "string", "description": "Référence publique exacte fournie pour l'entité perçue ou connue, jamais son nom ou une description ; direction ou durée selon l'action, ou chaîne vide. Une correction conserve l'entité visée par la saisie, sans lui substituer une autre cible pour lever un refus."},
        "outil": {"type": "string", "description": "Identifiant d'un outil possédé, ou chaîne vide. Pour remettre : identifiant du PNJ destinataire ; pour pousser : direction de la poussée ou vide."},
        "methode": {"type": "string", "enum": METHODES},
        "difficulte": {"type": "integer", "description": "0 hors détachement ; estimation entre 11 et 22 pour une fixation."},
        "justification": {"type": "string", "description": "Avis d'arbitrage bref ; ne décrire aucun résultat."},
    },
    "required": ["action", "cible", "outil", "methode", "difficulte", "justification"],
    "additionalProperties": False,
}


ATTENDU_PAROLE = ("la saisie est une parole (elle commence par des guillemets, un verbe de parole ou « à tous ») : "
                  "mode parole_joueur, personnage = parole_prevue.personnage, contenu = ce qu'elle demande ou affirme")


def parole_annoncee(monde, intention):
    """Ce que le moteur fixe de la parole que la saisie annonce sans conteste (``paroles.analyser``,
    ``explicite``), ou None. ``impossible`` : le joueur doit préciser ou s'approcher."""
    from .paroles import prevue
    forme = analyser_parole(monde, intention)
    return prevue(monde, intention) if forme["explicite"] or forme["incomplete"] or forme["inconnu"] else None


def parole_attendue(monde, intention):
    """La saisie est une parole que le moteur peut faire entendre : ni un dialogue du MJ, ni un geste."""
    return "personnage" in (parole_annoncee(monde, intention) or {})


def parole_du_moteur(monde, intention):
    """La parole que le moteur prononce lui-même quand le MJ s'obstine à la raconter : les mots du
    joueur, tels quels, à ceux que le moteur a fixés, sans contenu typé. Sans mots imposés, le joueur
    les donne : le moteur ne les invente pas."""
    from .paroles import _nom_court
    from .paroles import mots_dits, prevue as prevoir
    forme, prevue = analyser_parole(monde, intention), prevoir(monde, intention)
    mots = mots_dits(forme, intention)
    if mots:
        return {"mode": "parole_joueur", "texte": "", "faits": [], "_parole_moteur": True,
                "proposition": {"personnage": prevue["personnage"], "replique": mots, "contenu": []}}
    qui = {"tous": " à tous", "personne": ""}.get(prevue["personnage"]) \
        if prevue["personnage"] in ("tous", "personne") else " à " + _nom_court(monde, prevue["personnage"])
    return {"mode": "dialogue", "texte": f"Dis ce que Corvus dit{qui}, entre guillemets ou après un deux-points.",
            "faits": [], "proposition": None, "_texte_moteur": True, "_validation_refusee": True}


ATTENDU_FAISABILITE = ("la saisie demande si Corvus peut faire un geste : mode action, la proposition de ce geste "
                       "telle que s'il le demandait (le moteur la prépare sans l'exécuter, puis montre au joueur ce "
                       "qu'elle demande ou pourquoi elle est impossible) ; clarifier si le geste visé est ambigu")


def geste_en_question(monde, intention):
    """« Puis-je… ? » : une question sur un geste de Corvus (``commandes.faisabilite``), qui n'est pas
    une parole adressée à quelqu'un (« Gorm, est-ce que je peux entrer ? »)."""
    if not faisabilite(intention):
        return False
    forme = analyser_parole(monde, intention)
    return not (forme["explicite"] or forme["nomme"] or forme["groupe"])


def interpellation_entendue(monde, intention):
    """« Gorm, … » sans guillemets ni verbe de parole : une saisie adressée à un personnage (ou à tous) qui
    l'entendrait, à interpréter (``paroles.analyser``). Rien n'est encore dit : le nom de celui qui
    l'entendrait, ou None."""
    from .paroles import _nom_court, prevue
    forme = analyser_parole(monde, intention)
    if forme["explicite"] or not (forme["nomme"] or forme["groupe"]):
        return None
    qui = prevue(monde, intention).get("personnage")
    if qui in (None, "personne"):
        return None
    return "tous" if qui == "tous" else _nom_court(monde, qui)


def renvoi(monde, intention):
    """Un dialogue qui répond à cette saisie avant que le moteur ait agi est renvoyé une fois au MJ, sans
    être contrôlé : (obstacle, attendu), ou None. « Puis-je… ? » : le moteur juge le geste. « Gorm, … »
    (Gorm l'entendrait) : rien n'est encore dit, ni fait ; personne ne répond ni ne réagit à des mots
    que le moteur n'a pas fait entendre. S'il revient, le dialogue est contrôlé comme tout autre."""
    if geste_en_question(monde, intention):
        return "C'est au moteur de dire si Corvus le peut.", ATTENDU_FAISABILITE
    qui = interpellation_entendue(monde, intention)
    if qui:
        return (f"Rien n'a encore été dit à {qui}.",
                f"la saisie s'adresse à {qui}, qui l'entendrait, et rien n'a encore été dit ni fait : "
                "parole_joueur (personnage = parole_prevue.personnage) si Corvus parle ; l'action si c'est un "
                "geste (donner un objet : remettre) ; un dialogue seulement pour ce que Corvus perçoit, sans "
                "que personne lui réponde ni réagisse à ses mots")
    return None


def refus_assure(monde, intention, reponse, deja_renvoyee=False, impossible_admis=False):
    """Pourquoi le moteur refusera cette réponse d'interprétation, quelle qu'en soit la prose, ou "" :
    un dialogue quand la saisie est une parole sans conteste (le moteur la fait entendre), un avis
    (clarifier, impossible) que la boucle de décision écarte avant de le lire, un ajout persistant que
    sa validation écarte (détail d'un objet hors de portée, savoir mal formé…). Les mêmes validations,
    sur copie, que la suite du tour : rien n'est appliqué. ``impossible_admis`` : la boucle de décision
    a déjà demandé un réexamen (``MJ._echanger_prepare``), un « impossible » sera lu."""
    mode, p = reponse.get("mode"), reponse.get("proposition")
    if mode == "dialogue" and "_texte_moteur" not in reponse and parole_attendue(monde, intention):
        return "Corvus le dit : c'est une parole."
    if mode == "action" and isinstance(p, dict) and p.get("action") in ("clarifier", "impossible"):
        # Un avis que personne ne lira : sa justification n'a pas à passer l'audit.
        if parole_attendue(monde, intention):
            return "Corvus le dit ; il ne le fait pas."
        if p.get("action") == "impossible" and not impossible_admis:
            return REEXAMEN
    if mode == "dialogue" and not deja_renvoyee and renvoi(monde, intention):
        return renvoi(monde, intention)[0]
    preparer = {"etablir_faits": preparer_faits, "enrichir": preparer_complements,
                "enrichir_savoirs": preparer_savoirs}.get(mode)
    if preparer is None or not isinstance(p, dict):
        return ""
    try:
        preparer(monde, sans_suite(p) if mode == "etablir_faits" else p, monde.data["revision"])
    except ErreurMonde as exc:
        return str(exc)
    return ""


def sans_suite(proposition):
    """Les faits persistants et leur geste suivant ont deux validations distinctes."""
    if isinstance(proposition, dict) and set(proposition) == {"ajouts", "suite"}:
        return {"ajouts": proposition["ajouts"]}
    return proposition


class ParoleNonConforme(ErreurMonde):
    """Une parole dont la couverture locale ou la contre-revue refuse la fidélité.
    Aucun secours local ne peut la prononcer en contournant ce refus."""


# « impossible » au premier examen : un réexamen est demandé, une fois (``MJ._echanger_prepare``).
REEXAMEN = "Réexamine l'intention entière et les possibilités du moteur avant de conclure qu'elle est impossible."
ATTENDU_REEXAMEN = ("action : le geste que demande la saisie, tel quel, même si sa cible est loin, hors de vue ou "
                    "introuvable (le moteur dit au joueur ce qui manque : s'approcher, la voir, ce qu'elle est) ; "
                    "impossible seulement si aucune action du moteur ne le couvre.")


def retour_refus(proposition, exc, consigne):
    """Ce que la boucle de correction transmet au MJ : le refus, et ce que le moteur accepterait."""
    retour = {"proposition_refusee": proposition, "obstacle": str(exc), "consigne": consigne}
    if getattr(exc, "attendu", ""):
        retour["attendu"] = exc.attendu
    return retour


def reponse_du_moteur(exc):
    """Le refus du moteur, tel qu'il s'adresse au joueur (son ``attendu`` reste au MJ)."""
    return {"mode": "dialogue", "texte": str(exc), "faits": [], "proposition": None,
            "_texte_moteur": True, "_validation_refusee": True}


def verifier_forme_reponse(reponse, schema):
    """L'enveloppe commune est corrigée avant tout audit ou choix de voie.

    Les validateurs de chaque proposition gardent les contraintes de leur contenu.
    Une source inconnue est écartée comme auparavant, sans invalider la réponse.
    """
    champs = {"mode", "texte", "faits", "proposition"}
    if not isinstance(reponse, dict) or set(reponse) != champs:
        raise RefusDeForme("La réponse doit porter les quatre champs attendus.",
                           f"réponse reçue {reponse!r} ; accepté : {sorted(champs)}.")
    modes = schema.get("properties", {}).get("mode", {}).get("enum")
    if modes is not None and reponse["mode"] not in modes:
        raise RefusDeForme("Le mode de réponse ne convient pas.",
                           f"mode reçu {reponse['mode']!r} ; acceptés : {modes!r}.")
    if not isinstance(reponse["faits"], list):
        raise RefusDeForme("Les sources de la réponse doivent être une liste.",
                           f"faits reçu {reponse['faits']!r} ; accepté : une liste de clés des faits fournis.")
    if (not isinstance(reponse["texte"], str) or len(reponse["texte"]) > 4000
            or (reponse["mode"] != "dialogue" and reponse["texte"])):
        raise RefusDeForme("Le texte de la réponse ne convient pas à son mode.",
                           f"texte reçu {reponse['texte']!r} ; accepté : dialogue non vide de 4000 caractères "
                           "au plus ; texte vide pour une proposition typée.")
    if reponse["mode"] == "dialogue" and not reponse["texte"].strip():
        raise RefusDeForme("Le texte est vide : écris dans texte la réponse destinée au joueur.",
                           f"texte reçu {reponse['texte']!r} ; accepté : une réponse non vide.")
    if reponse["mode"] == "dialogue":
        reponse["proposition"] = None
    elif not isinstance(reponse["proposition"], dict):
        raise RefusDeForme("La proposition typée doit être un objet structuré.",
                           f"proposition reçue {reponse['proposition']!r}, mode {reponse['mode']!r} ; "
                           "accepté : un objet conforme au schéma de ce mode, distinct de faits (sources citées).")
    else:
        # L'union du transport expose toutes les branches : le mode doit encore
        # désigner la bonne famille avant tout audit ou accès à son contenu.
        marqueur = {"action": "action", "enrichir_joueur": "profil_joueur",
                    "enrichir": "ajouts", "conversation_pnj": "sujet",
                    "parole_joueur": "replique", "enrichir_savoirs": "savoirs",
                    "etablir_faits": "ajouts"}.get(reponse["mode"])
        if marqueur and marqueur not in reponse["proposition"]:
            raise RefusDeForme("La proposition ne correspond pas au mode de réponse.",
                               f"proposition reçue {reponse['proposition']!r}, mode {reponse['mode']!r} ; "
                               f"accepté : une proposition portant {marqueur!r} pour ce mode.")
        for champ in ("ajouts", "contenu"):
            if champ not in reponse["proposition"]:
                continue
            valeur = reponse["proposition"][champ]
            if not isinstance(valeur, list) or any(not isinstance(v, dict) for v in valeur):
                raise RefusDeForme("Le contenu typé doit être une liste d'objets structurés.",
                                   f"proposition.{champ} reçu {valeur!r} ; accepté : une liste "
                                   "d'objets conformes au schéma, pas une liste de sources citées.")


def verifier_disponibilite(reponse, faits, geste_requis=False):
    """Les possibilités du tour sont des données, jamais des variantes du schéma."""
    disponibles = {
        "dialogue": True, "action": True,
        "enrichir_joueur": bool(faits.get("profil_joueur_a_completer")),
        "enrichir": bool(faits.get("descriptions_a_completer")),
        "conversation_pnj": bool(faits.get("interlocuteurs")),
        "parole_joueur": bool(faits.get("interlocuteurs")) or
                          "personnage" in (faits.get("parole_prevue") or {}),
        "enrichir_savoirs": bool(faits.get("connaissances_a_completer")),
        "etablir_faits": any((faits.get("faits_narratifs_proposables") or {}).values()),
    }
    mode = reponse.get("mode")
    if not disponibles.get(mode, False):
        raise RefusDeForme("Ce mode de réponse n'est pas disponible ici.",
                           f"mode reçu {mode!r} ; acceptés : {[m for m, ok in disponibles.items() if ok]!r}.")
    if mode == "etablir_faits":
        verifier_suite_faits(reponse["proposition"], geste_requis)


def verifier_suite_faits(proposition, geste_requis):
    suite = proposition.get("suite")
    if geste_requis and not isinstance(suite, dict):
        raise RefusDeForme("Le geste demandé doit être précisé avec les faits.",
                           f"proposition.suite reçu {suite!r} ; "
                           "accepté : un geste (action hors clarifier/impossible, séquence ou improvisation).")
    if isinstance(suite, dict) and suite.get("action") in ("clarifier", "impossible"):
        raise RefusDeForme("La suite doit décrire le geste demandé.",
                           f"proposition.suite.action reçu {suite['action']!r} ; "
                           "accepté : une action hors clarifier/impossible, une séquence ou une improvisation.")


def demande_precision():
    """Une proposition mal formée ne prouve rien sur les capacités de Corvus."""
    return "Précise la manœuvre que tu veux tenter. Corvus n'a rien tenté."


class MJ:
    def __init__(self, modele=None, effort=None, timeout=45, connexion="api", *, fournisseur=None):
        defaut_modele, defaut_effort = DEFAUTS_CONNEXION.get(connexion, (os.environ.get("OPENAI_MODEL", MODELE_PAR_DEFAUT), "medium"))
        self.modele = modele or defaut_modele
        self.effort, self.timeout = effort if effort is not None else defaut_effort, timeout
        self.derniere_utilisation = None
        self.connexion = connexion
        self.erreur_auth = None
        self.derniere_sortie = []
        self.observateur = None
        self._audit_courant = None
        self._monde_controle = None
        self._interpretation = False   # l'appel en cours interprète une saisie (et non raconte)
        self._sans_dialogue = False    # dialogue ou avis remplacé par le refus du moteur : pas d'audit
        self._faisabilite_renvoyee = False  # « puis-je… ? » déjà renvoyé : un dialogue se contrôle
        self._impossible_admis = False  # la boucle de décision lira un « impossible » (réexamen déjà demandé)
        self.journal_complet = False   # trace entière de chaque appel (banc, essais de modèles)
        self.reflexion = "libre"       # Claude : réflexion adaptative (défaut), ou « imposee » : outil imposé, sans réflexion
        # Clé de session stable : elle aiguille les appels vers le même cache de prompt, si bien
        # que le préfixe commun (instructions, schéma, faits) n'est pas relu à chaque appel.
        import uuid
        self.cle_cache = str(uuid.uuid4())
        self.fournisseur = fournisseur if fournisseur is not None else creer_fournisseur(connexion)

    def fermer(self):
        self.fournisseur.fermer()

    def proposer(self, monde, intention):
        from .noms import verifier_references, references
        contexte=monde.contexte()
        reponse=self._appeler(INSTRUCTIONS, {"monde": contexte, "intention": intention},
                              intention, "proposer_action", SCHEMA)
        verifier_references(monde,reponse,contexte)
        return references(monde,reponse)

    def _auditer_action(self, intention, plan, revision, monde=None, operations_demandees=None):
        from .couverture_action import (schema as schema_couverture,
                                        INSTRUCTIONS as INSTRUCTIONS_COUVERTURE,
                                        INSTRUCTIONS_PAROLE,
                                        RapportInvalide, entree as entree_couverture,
                                        verifier as verifier_couverture)
        for essai in range(2):
            rapport = self._appeler_brut(
                (INSTRUCTIONS_PAROLE + "\n" + SENS_REPLIQUE) if plan.parole is not None else INSTRUCTIONS_COUVERTURE,
                entree_couverture(intention, plan, monde),
                "Contrôler la fidélité du plan", "auditer_action", schema_couverture(plan))
            if self.observateur:
                self.observateur({"etape": "couverture de l'action", "modele": self.modele,
                                  "revision": revision, "intention": intention,
                                  "rapport": copy.deepcopy(rapport)})
            try:
                verifier_couverture(rapport, plan, operations_demandees)
                return
            except RapportInvalide:
                # Une revue illisible est redemandée une fois. La parole exige
                # son analyse des opérations ; un geste conserve le repli historique.
                if essai:
                    if plan.parole is not None:
                        raise RapportIllisible("Le contenu de ta parole n'a pas pu être vérifié.",
                            f"proposition.contenu reçu {json.dumps(plan.parole['contenu'], ensure_ascii=False)} ; "
                            f"contre-revue reçue {json.dumps(rapport, ensure_ascii=False)} ; "
                            "accepté un contenu couvrant les opérations demandées, "
                            "après une contre-revue lisible (contenu_conforme, motif, operations_demandees, perimetre).")
                    if plan.proposition.get("action") == "improviser" or getattr(plan, 'candidat', False):
                        raise RapportIllisible("La fidélité de la manœuvre n'a pas pu être vérifiée.",
                            "proposition inchangée ; accepté : une contre-revue lisible selon le schéma demandé.")
                    if self.observateur:
                        self.observateur({"etape": "couverture de l'action", "modele": self.modele,
                                          "revision": revision, "intention": intention,
                                          "erreur": "Contre-revue illisible deux fois : plan accepté sans elle."})
                    return

    def _verifier_fidelite_parole(self, monde, intention, complements, rapport, revision,
                                 operations_demandees=None, declaration_connue=True,
                                 operations_declarees=None, operations_a_examiner=None):
        """Couverture locale, puis revue du sens seulement au-delà des mots exacts sans effet."""
        from .couverture_action import sens_parole, verifier_operations
        from .paroles import mots_dits, operations_contenu, forme_rapportee
        from .moteur import Plan
        from .biens import etat_comptes_joueur
        # L'adresse et ses effets sont déjà validés par destinataires. Ils ne
        # font pas partie de la question posée à la revue sémantique du contenu.
        plan = Plan({}, revision, "Contrôler le contenu de la parole préparée.", parole={
            "replique": rapport["replique_joueur"], "contenu": copy.deepcopy(complements["contenu"]),
            "sens_contenu": sens_parole(complements["contenu"], monde),
            # Les termes implicites du contenu se lisent dans l'état d'origine,
            # jamais dans les comptes après règlement de la copie préparée.
            "comptes_avant": etat_comptes_joueur(monde, rapport["destinataires"])})
        try:
            declarees = operations_declarees or set()
            # La déclaration contrôle sa propre proposition, sans devenir une
            # obligation pour la suivante. Seule la revue confirme le sens.
            verifier_operations(plan, (operations_demandees or set()) | declarees)
            a_examiner = operations_a_examiner if operations_a_examiner is not None else set()
            a_examiner.update(declarees)
            mots = mots_dits(analyser_parole(monde, intention), intention)
            if (not operations_demandees and not a_examiner and not declarees
                    and not operations_contenu(complements["contenu"])
                    and (mots or not forme_rapportee(intention))
                    and rapport["replique_joueur"].strip() == (mots or intention).strip()):
                return
            try:
                self._auditer_action(intention, plan, revision, monde, operations_demandees)
            except RapportIllisible:
                # Une revue illisible ne tranche aucune hypothèse restante.
                raise
            except ErreurMonde:
                # La revue lisible a confirmé les obligations ou écarté les types.
                a_examiner.clear()
                raise
            else:
                a_examiner.clear()
        except ErreurMonde as exc:
            raise ParoleNonConforme(str(exc), exc.attendu) from exc

    def raconter_resultat(self, monde, resultat):
        """Narration seule : le résultat est déjà résolu et sauvegardé par la boucle de jeu."""
        return self._echanger(monde, "Raconte la manœuvre qui vient d'être résolue.", None,
                              enrichir=False, resultat_resolu=resultat)

    def echanger(self, monde, intention, proposition_en_attente=None):
        """Complète les abords autorisés avant l'arbitrage, toujours sur copie."""
        from .noms import verifier_saisie
        verifier_saisie(monde, intention)
        from .espace import a_completer, preparer, SCHEMA as SCHEMA_ESPACE
        cadres = a_completer(monde)
        if not cadres:
            return self._admettre_sortie(self._echanger_prepare(monde, intention, proposition_en_attente))
        entree = {"cadres_autorises": cadres,
                  "consigne": "Complète chaque cadre une fois. Choisis uniquement le terrain, sans tenir compte d'une réussite souhaitée. Les dimensions et appuis sont imposés par le moteur."}
        debut = time.monotonic()
        trace = {"modele": self.modele, "revision": monde.data["revision"], "intention": intention,
                 "etape": "complément spatial", "taille_contexte": len(json.dumps(entree)), "correction": False}
        self.derniere_utilisation = None
        try:
            p = self._appeler("Tu complètes un monde de JDR. Choisis un terrain cohérent pour chaque cadre fourni. Aucun personnage, trésor ou passage supplémentaire. Appelle completer_espace une fois.",
                              entree, "Compléter les abords visibles", "completer_espace", SCHEMA_ESPACE)
            travail = preparer(monde, p, monde.data["revision"])
            if a_completer(travail):
                raise ErreurMonde("Les abords visibles n'ont pas tous été précisés.")
            trace["reponse"] = {"mode": "enrichir_espace", "texte": "", "proposition": p}
        except ErreurMonde as exc:
            trace["erreur"] = str(exc)
            raise
        finally:
            if self.observateur:
                trace.update(secondes=round(time.monotonic()-debut, 3), usage=copy.deepcopy(self.derniere_utilisation))
                self.observateur(trace)
        reponse = copy.deepcopy(self._admettre_sortie(self._echanger_prepare(travail, intention, proposition_en_attente)))
        return ajouter_transaction(reponse, "espace", monde.data["revision"], p, debut=True)

    @staticmethod
    def _admettre_sortie(reponse):
        """La préparation ne publie jamais une prose que ses gardes ont écartée.

        Une prévalidation peut court-circuiter l'audit d'une sortie qui sera
        rejetée ensuite. Si une correction abandonne ce chemin, elle ne gagne
        pas pour autant le droit d'afficher cette prose ni ses transactions.
        """
        if reponse.get("mode") == "dialogue" and not reponse.get("_audit") and not reponse.get("_texte_moteur"):
            return reponse_du_moteur(ErreurMonde(demande_precision()))
        return reponse

    def _echanger_prepare(self, monde, intention, proposition_en_attente=None,
                          suite_fait=False, reponse=None, recadre=False):
        """Interprétation, une correction au plus, puis narration si enrichissement.

        ``reponse`` : une réponse déjà obtenue (corrigée après un refus), traitée par le chemin
        de son mode ; ``recadre`` interdit un second recadrage dans le même tour.
        Aucune écriture : seule la boucle de jeu applique les propositions validées.
        """
        revision = monde.data["revision"]
        if (reponse is None and not est_question(intention) and proposition_en_attente is None and
                normaliser(intention) in ("je retente", "je rentente", "je reessaie", "je recommence", "retenter", "reessayer")):
            dernier = derniere_tentative(monde)
            if dernier and not dernier["reussite"]:
                from .moteur import Moteur
                self.derniere_utilisation = None
                p = dernier["proposition_pour_reprise"]
                try:
                    Moteur(monde).preparer(p, "reprise mémorisée")
                    r = {"mode": "action", "texte": "", "faits": ["derniere_tentative"],
                         "proposition": p, "_reprise_locale": True}
                except ErreurMonde as exc:
                    r = {"mode": "dialogue", "texte": "Tu ne peux plus reprendre cette tentative ainsi : " + str(exc),
                         "faits": ["derniere_tentative"], "proposition": None,
                         "_texte_moteur": True}
                if self.observateur:
                    self.observateur({"etape": "reprise locale sans appel LLM", "modele": self.modele,
                                      "revision": revision, "intention": intention, "reponse": copy.deepcopy(r),
                                      "usage": None, "secondes": 0})
                return r
        if reponse is None:
            annoncee = parole_annoncee(monde, intention)
            if annoncee and "impossible" in annoncee:
                # Une parole que le moteur ne peut pas faire entendre (à qui parler, de quelle façon) :
                # le joueur précise ou s'approche ; aucun appel n'y changerait rien.
                return {"mode": "dialogue", "texte": annoncee["impossible"], "faits": [], "proposition": None,
                        "_texte_moteur": True, "_validation_refusee": True}
            reponse = self._echanger(monde, intention, proposition_en_attente, enrichir=True)
            if reponse["mode"] == "dialogue" and parole_attendue(monde, intention):
                # Une parole passe par le moteur, qui la fait entendre avant qu'on la raconte. Après un
                # repli du contrôle narratif (aucune réponse admise), le moteur la prononce sans relance.
                if "_texte_moteur" not in reponse:
                    retour = retour_refus(None, ErreurMonde("Corvus le dit : c'est une parole.", ATTENDU_PAROLE),
                                          "Propose la parole ; ne la raconte pas toi-même.")
                    if self.observateur:
                        self.observateur({"etape": "validation", "modele": self.modele, "intention": intention,
                                          "revision": revision, "tentative": 1, **retour})
                    reponse = self._echanger(monde, intention, proposition_en_attente, enrichir=True,
                                             retour_moteur=retour)
                if reponse["mode"] == "dialogue":
                    # Le MJ s'obstine : le moteur prononce lui-même les mots du joueur.
                    reponse = parole_du_moteur(monde, intention)
                    if reponse["mode"] == "dialogue":
                        return reponse
            elif ((reponse["mode"] == "dialogue" and not ({"_audit", "_texte_moteur"} & set(reponse))
                   and renvoi(monde, intention))
                  or (reponse["mode"] == "parole_joueur" and geste_en_question(monde, intention))):
                # « Puis-je… ? », « Gorm, … » : le dialogue, non contrôlé (``refus_assure``), est renvoyé une
                # fois avec ce qu'attend le moteur. S'il revient, il est contrôlé comme tout autre.
                obstacle, attendu = renvoi(monde, intention)
                retour = retour_refus(None, ErreurMonde(obstacle, attendu),
                                      "Propose ce que le moteur attend ; ne raconte rien qu'il n'ait validé.")
                if self.observateur:
                    self.observateur({"etape": "validation", "modele": self.modele, "intention": intention,
                                      "revision": revision, "tentative": 1, **retour})
                self._faisabilite_renvoyee = True
                try:
                    reponse = self._echanger(monde, intention, proposition_en_attente, enrichir=True,
                                             retour_moteur=retour)
                finally:
                    self._faisabilite_renvoyee = False
        correction_utilisee = False
        # Un refus de forme (``refus.RefusDeForme`` : un champ, une borne, la mauvaise action) reçoit une
        # correction à part : il ne dit rien du monde, et ne se montre jamais au joueur.
        forme_corrigee = False
        premier_refus = None
        # Une question sur la faisabilité d'un geste (« puis-je… ? ») : c'est le moteur qui y répond, par
        # la fiche du geste ou par la raison de son refus (une raison du monde, jamais un refus de forme),
        # jamais une explication libre du MJ.
        faisabilite, refus_du_moteur = est_question(intention), None
        # Les refus du monde, quelle que soit l'action : seul leur message public répond au joueur.
        refus_monde = []
        evenements_demandes = set()
        for tentative in range(3):
            if reponse["mode"] != "action":
                break
            p = reponse["proposition"]
            try:
                from .moteur import Moteur
                if parole_attendue(monde, intention):
                    # Une parole sans conteste (guillemets, « je dis… », à tous…) : Corvus le dit, même si ses mots
                    # annoncent un geste ; le moteur a déjà fixé à qui, il n'y a rien à clarifier.
                    raise ErreurMonde("Corvus le dit ; il ne le fait pas.", ATTENDU_PAROLE
                                      + " ; le geste annoncé attend que le joueur le fasse.")
                if p.get("action") == "impossible":
                    if not (correction_utilisee or forme_corrigee):
                        raise RefusDeForme(REEXAMEN, ATTENDU_REEXAMEN)
                if p.get("action") in ("clarifier", "impossible"):
                    if refus_monde:
                        return reponse_du_moteur(ErreurMonde(" ".join(str(e) for e in refus_monde)))
                    break
                # Une question sur la faisabilité d'un geste se prépare comme sa demande : la boucle de
                # jeu ne l'exécute pas (``commandes.PERCEPTIONS``) et montre ce qu'il demanderait.
                refus_admission = None
                # Préparation pure du dossier : aucune décision publiée et
                # aucun effet. Même pipeline ensuite, qu'elle ait produit un
                # plan ou rencontré un obstacle : sens, puis admission.
                try:
                    plan = Moteur(monde).preparer(p, "MJ")
                except ErreurMonde as exc:
                    refus_admission = exc
                    from .moteur import Plan
                    plan = Plan(p, revision, "Interprétation proposée.")
                    plan.candidat = True
                self._auditer_action(intention, plan, revision, monde, evenements_demandes)
                if refus_admission is not None:
                    exc = refus_admission
                    if isinstance(exc, ProprieteInconnue) and geste_en_question(monde, intention):
                        # Une inconnue physique n'est pas une erreur de saisie du
                        # plan : une fiche répond avec ce qui manque, sans inventer
                        # les préconditions favorables au geste. Une demande de
                        # geste, elle, garde la voie de qualification puis réexamen.
                        if self.observateur:
                            self.observateur({"etape": "validation", "modele": self.modele,
                                "intention": intention, "revision": revision,
                                "tentative": tentative + 1,
                                **retour_refus(p, exc, "Une propriété reste à décrire ; rien n'est tenté.")})
                        return reponse_du_moteur(exc)
                    if not isinstance(exc, (QualificationRequise, RefusDeForme)):
                        # Le sens est contrôlé ; l'admission rend son propre
                        # refus public. Elle ne recompile pas une intention
                        # fidèle et ne déclenche aucune deuxième fidélité.
                        if self.observateur:
                            self.observateur({"etape": "validation", "modele": self.modele,
                                "intention": intention, "revision": revision, "tentative": tentative + 1,
                                **retour_refus(p, exc, "Refus public du moteur ; intention conservée.")})
                        return reponse_du_moteur(exc)
                    raise exc
                if premier_refus and not plan.realise_geste:
                    raise ErreurMonde("La proposition corrigée ne réalise aucun effet de la manœuvre demandée.",
                                      "garde les gestes de l'intention qui changent le monde ou font percevoir ; si aucun n'est possible, "
                                      "réponds en dialogue sur l'obstacle.")
                break
            except ErreurMonde as exc:
                dernier_refus = (p, str(exc))
                if premier_refus is None:
                    premier_refus = dernier_refus
                retour = retour_refus(p, exc, "Corrige uniquement la proposition de la même intention, sans modifier les faits ni abandonner une partie de l'intention. Sinon renvoie-la telle quelle : le moteur dira ce qui manque au joueur.")
                if faisabilite and refus_du_moteur is exc:
                    retour["consigne"] = ("C'est une question de faisabilité : corrige la proposition si elle visait mal "
                                          "(identifiants, champs) d'après attendu ; sinon renvoie-la telle quelle, et le "
                                          "moteur dira lui-même au joueur ce qui manque.")
                if isinstance(exc, QualificationRequise):
                    retour["qualification_requise"] = {"objet": exc.cible,
                                                       "capacite": exc.capacite,
                                                       "moyen": p.get("outil", "")}
                    retour["consigne"] = ("L'action attend une propriété physique encore inconnue. "
                                         "Propose dans etablir_faits un jugement compatible avec les faits. "
                                         "Pour une coupe, renseigne l'objet, le moyen et coupe_possible. "
                                         "La même intention sera réexaminée ensuite.")
                if self.observateur:
                    self.observateur({"etape": "validation", "modele": self.modele, "intention": intention,
                                      "revision": revision, "tentative": tentative + 1, **retour})
                if isinstance(exc, HorsDePortee):
                    # Seuls les pas du joueur lèvent cet obstacle. Le refus est déjà
                    # une réponse publique : aucune explication ni audit à demander.
                    return reponse_du_moteur(ErreurMonde(" ".join(str(e) for e in refus_monde)))
                forme = isinstance(exc, RefusDeForme) and not forme_corrigee and tentative < 2
                if correction_utilisee and not forme and parole_attendue(monde, intention):
                    # Une parole n'est jamais perdue : le moteur prononce lui-même les mots du joueur.
                    reponse = parole_du_moteur(monde, intention)
                    if reponse["mode"] == "dialogue":
                        return reponse
                    break
                if correction_utilisee and not forme:
                    if refus_monde:
                        # Chaque obstacle que le monde a opposé, dans l'ordre, une fois chacun.
                        return reponse_du_moteur(ErreurMonde(" ".join(str(e) for e in refus_monde)))
                    return reponse_du_moteur(ErreurMonde(demande_precision()))
                if forme:
                    forme_corrigee = True
                else:
                    correction_utilisee = True
                # Seule une proposition corrigée peut encore lever l'obstacle ; une explication ou un
                # avis ne sera pas lu, et ne doit donc déclencher aucun audit de prose.
                self._sans_dialogue = bool(refus_monde)
                # Un « impossible » est lu après un premier réexamen : l'audit de sa justification sert.
                admis, self._impossible_admis = self._impossible_admis, True
                try:
                    reponse = self._echanger(monde, intention, proposition_en_attente, enrichir=True,
                                             retour_moteur=retour)
                finally:
                    self._sans_dialogue = False
                    self._impossible_admis = admis
        if reponse["mode"] == "dialogue" and refus_monde:
            return reponse_du_moteur(ErreurMonde(" ".join(str(e) for e in refus_monde)))
        if (reponse["mode"] == "dialogue" and not reponse.get("_validation_refusee")
                and parole_attendue(monde, intention)):
            # Corrigée en dialogue après un geste refusé (ou repli du contrôle) : la parole reste au moteur.
            reponse = parole_du_moteur(monde, intention)
            if reponse["mode"] == "dialogue":
                return reponse
        if reponse["mode"] == "parole_joueur" and geste_en_question(monde, intention):
            # La même frontière s'applique après TOUTES les corrections : une
            # question au MJ n'est pas une réplique adressée à un PNJ voisin.
            # Les refus de préparation ne donnent pas davantage le droit de parler.
            return reponse_du_moteur(refus_du_moteur or ErreurMonde(
                "Je n'ai pas pu déterminer le geste à examiner. Précise ce que tu veux tenter."))
        if reponse["mode"] == "enrichir_joueur":
            p = reponse["proposition"]
            travail = preparer_profil(monde, p, revision)
            return ajouter_transaction(
                {"mode": "dialogue", "texte": reponse_profil(travail, p), "faits": ["joueur"],
                 "proposition": None, "_texte_moteur": True}, "profil_joueur", revision, p)
        if reponse["mode"] == "etablir_faits":
            suite_proposee = reponse["proposition"].get("suite")
            p = sans_suite(reponse["proposition"])
            try:
                verifier_suite_faits(reponse["proposition"], geste_en_question(monde, intention))
                if suite_proposee is not None and not isinstance(suite_proposee, dict):
                    raise RefusDeForme("Le geste suivant doit être précisé.",
                                       f"proposition.suite={suite_proposee!r} : accepté une proposition d'action.")
                travail, texte, _ = preparer_faits(monde, p, revision)
            except ErreurMonde as exc:
                retour = retour_refus(p, exc, "Revois les ancrages et les faits actuels. Ne raconte pas un fait refusé.")
                reponse = self._echanger(monde, intention, proposition_en_attente,
                                         enrichir=True, retour_moteur=retour)
                if reponse["mode"] != "etablir_faits":
                    if reponse["mode"] == "dialogue" and "_audit" not in reponse and parole_attendue(monde, intention):
                        # Un dialogue non contrôlé (``refus_assure``) : la parole reste au moteur.
                        return self._echanger_prepare(monde, intention, proposition_en_attente, suite_fait=suite_fait,
                                                      reponse=parole_du_moteur(monde, intention), recadre=True)
                    if reponse["mode"] == "dialogue":
                        return reponse
                    # Ni fait ni explication : aucun message de la boucle ne va au joueur. Le monde a
                    # déjà dit ce qui manque au geste (sa raison répond) ; sinon le geste revenu suit
                    # le chemin de son mode, une fois ; sinon rien n'est tenté.
                    if refus_monde:
                        return reponse_du_moteur(ErreurMonde(" ".join(str(e) for e in refus_monde)))
                    if reponse["mode"] == "action" and not recadre:
                        return self._echanger_prepare(monde, intention, proposition_en_attente, suite_fait=suite_fait,
                                                      reponse=reponse, recadre=True)
                    return {"mode": "dialogue", "texte": demande_precision(), "faits": [],
                            "proposition": None, "_validation_refusee": True, "_texte_moteur": True}
                suite_proposee = reponse["proposition"].get("suite")
                p = sans_suite(reponse["proposition"])
                verifier_suite_faits(reponse["proposition"], geste_en_question(monde, intention))
                travail, texte, _ = preparer_faits(monde, p, revision)
            if suite_fait:
                # Un seul groupe de faits par tour : le réexamen ne relance pas l'invention.
                raise ErreurMonde("Le réexamen après un fait établi a proposé d'autres faits.")
            if suite_proposee is not None:
                # Une seule interprétation, deux propositions typées : les faits
                # ne valent pas validation du geste. Celui-ci passe par toutes
                # les validations ordinaires, sur la copie où les faits existent.
                suite_proposee = copy.deepcopy(suite_proposee)
                if "justification" in suite_proposee:
                    suite_proposee["justification"] = ""
                suite = self._echanger_prepare(travail, intention, proposition_en_attente,
                    suite_fait=True, reponse={"mode": "action", "texte": "", "faits": [],
                                             "proposition": suite_proposee})
                return ajouter_transaction(suite, "faits", revision, p, debut=True)
            qualification = any(a["type"] == "qualification" for a in p["ajouts"])
            manipulable = any(a["type"] == "objet" for a in p["ajouts"])
            if qualification or (manipulable and not est_question(intention)):
                # L'intention initiale est réexaminée sur le monde qui contient le fait :
                # le joueur n'a pas à la répéter.
                try:
                    suite = self._echanger_prepare(travail, intention,
                                                   proposition_en_attente, suite_fait=True)
                    if suite["mode"] == "action" or (suite["mode"] == "dialogue" and not qualification):
                        return ajouter_transaction(suite, "faits", revision, p, debut=True)
                except ErreurMonde:
                    pass
            return ajouter_transaction({"mode": "dialogue", "texte": texte, "faits": [],
                                        "proposition": None, "_texte_moteur": True},
                                       "faits", revision, p)
        if reponse["mode"] == "action" and reponse["proposition"]["action"] in ("clarifier", "impossible"):
            if "_audit_justification" not in reponse:
                raise ErreurMonde("L'avis du MJ n'a pas été contrôlé.")
            return {"mode": "dialogue", "texte": reponse["proposition"]["justification"],
                    "faits": reponse["faits"], "proposition": None,
                    "_audit": reponse["_audit_justification"]}
        if reponse["mode"] not in ("enrichir", "conversation_pnj", "enrichir_savoirs", "parole_joueur"):
            return reponse
        complements = reponse["proposition"]
        rapport = None
        if reponse["mode"] == "parole_joueur":
            fidelite_refusee = False
            operations_demandees = set()
            operations_a_examiner = set()
            for essai in range(3):
                # Des mots imposés par le joueur (guillemets, deux-points, interpellation) sont dits
                # tels quels, sans réécriture.
                complements = {**reponse["proposition"],
                               "replique": (analyser_parole(monde, intention)["mots"]
                                            or reponse["proposition"].get("replique", "")),
                               "_intention": intention[:600]}
                try:
                    from .couverture_action import lire_operations
                    from .paroles import operations_contenu
                    declaration_connue = not reponse.get("_parole_moteur")
                    operations_declarees = set()
                    if declaration_connue:
                        operations_declarees = lire_operations(complements.pop("operations_demandees", None))
                    # Une omission déclarée doit être examinée même si la
                    # préparation échoue. Un type présent refusé ne l'impose pas.
                    operations_a_examiner.update(
                        operations_declarees - operations_contenu(complements["contenu"]))
                    # Une préparation refusée ne confirme aucune opération de
                    # cette interprétation ; les obligations reconnues restent.
                    travail, rapport = preparer_parole(monde, complements, revision)
                    self._verifier_fidelite_parole(monde, intention, complements, rapport, revision,
                                                   operations_demandees, declaration_connue, operations_declarees,
                                                   operations_a_examiner)
                    break
                except ParoleImpossible as exc:
                    # À qui parler, de quelle façon : c'est au joueur de préciser ou de s'approcher.
                    return {"mode": "dialogue", "texte": str(exc), "faits": [], "proposition": None,
                            "_texte_moteur": True, "_validation_refusee": True}
                except ErreurMonde as exc:
                    fidelite_refusee |= isinstance(exc, ParoleNonConforme)
                    if fidelite_refusee and essai:
                        secours = parole_du_moteur(monde, intention)
                        if secours["mode"] == "parole_joueur":
                            # Le typage refusé ne rend pas les mots du joueur inexploitables.
                            # Repréparer sur l'original : aucun effet des copies refusées ne passe.
                            complements = {**secours["proposition"], "_intention": intention[:600]}
                            travail, rapport = preparer_parole(monde, complements, revision)
                            try:
                                self._verifier_fidelite_parole(monde, intention, complements, rapport, revision,
                                                               operations_demandees, False,
                                                               operations_a_examiner=operations_a_examiner)
                            except ParoleNonConforme:
                                return {"mode": "dialogue", "texte": "Tu n'as encore rien dit : précise ce que tu veux "
                                        "demander ou faire savoir à ton interlocuteur.",
                                        "faits": [], "proposition": None, "_texte_moteur": True,
                                        "_validation_refusee": True}
                            break
                        return {"mode": "dialogue", "texte": "Précise ce que tu veux dire, entre guillemets ou "
                                "après un deux-points.",
                                "faits": [], "proposition": None, "_texte_moteur": True,
                                "_validation_refusee": True}
                    secours = parole_du_moteur(monde, intention) if essai and parole_attendue(monde, intention) else None
                    if secours and secours["mode"] == "parole_joueur" and secours["proposition"] != reponse["proposition"]:
                        # Deux propositions refusées : le moteur prononce lui-même les mots du joueur.
                        reponse = secours
                        continue
                    if essai:
                        # Rien n'est dit : le joueur reformule, sans message technique.
                        return {"mode": "dialogue", "texte": "Corvus cherche ses mots sans parvenir à le dire "
                                "ainsi. Reformule ta réplique avec ce qu'il connaît.", "faits": [],
                                "proposition": None, "_texte_moteur": True, "_validation_refusee": True}
                    retour = retour_refus(reponse["proposition"], exc,
                                          "Corrige les destinataires, les mots et le contenu de la parole pour "
                                          "respecter la saisie ; elle ne nomme que ce que Corvus connaît d'après "
                                          "les faits, le message et la conversation. Rien n'est encore dit.")
                    if self.observateur:
                        self.observateur({"etape": "validation", "modele": self.modele, "intention": intention,
                                          "revision": revision, "tentative": 1, **retour})
                    reponse = self._echanger(monde, intention, proposition_en_attente,
                                             enrichir=True, retour_moteur=retour)
                    if reponse["mode"] != "parole_joueur":
                        if reponse["mode"] == "dialogue":
                            if reponse.get("_audit") or reponse.get("_texte_moteur"):
                                return reponse
                            return reponse_du_moteur(exc)
                        raise ErreurMonde("La correction de la parole n'a pas abouti.")
        else:
            try:
                if reponse["mode"] == "conversation_pnj":
                    if complements.get("operation") in ("accepter", "refuser") and est_question(intention):
                        raise ErreurMonde("Une question ne suffit pas à accepter ou refuser une offre.",
                                          "une question appelle discuter ou proposer, pas accepter ni refuser.")
                    travail, rapport = preparer_conversation(monde, complements, revision)
                elif reponse["mode"] == "enrichir_savoirs":
                    travail = preparer_savoirs(monde, complements, revision)
                    rapport = {"personnage": complements["personnage"], "sujet": intention,
                               "operation": "raconter", "faits": ["Les connaissances proposées sont enregistrées dans connaissances_pnj. Répondre à partir de ces savoirs."]}
                else:
                    travail = preparer_complements(monde, complements, revision)
            except ErreurMonde as exc:
                if recadre:
                    # Un seul recadrage par tour : le second refus remonte, comme avant le recadrage.
                    raise
                retour = retour_refus(reponse["proposition"], exc,
                                      "Corrige la proposition, ou choisis le mode qui convient à la demande "
                                      "(etablir_faits pour décrire un objet, dialogue pour répondre).")
                if self.observateur:
                    self.observateur({"etape": "validation", "modele": self.modele, "intention": intention,
                                      "revision": revision, "tentative": 1, **retour})
                corrigee = self._echanger(monde, intention, proposition_en_attente, enrichir=True, retour_moteur=retour)
                return self._echanger_prepare(monde, intention, proposition_en_attente, suite_fait=suite_fait,
                                              reponse=corrigee, recadre=True)
        narration = self._echanger(travail, intention, proposition_en_attente, enrichir=False, conversation_validee=rapport)
        if narration["mode"] != "dialogue":
            raise ErreurMonde("Le MJ n'a pas terminé la description. Aucun complément enregistré.")
        nature = {"conversation_pnj": "conversation_pnj", "enrichir": "complements",
                  "enrichir_savoirs": "savoirs", "parole_joueur": "parole"}[reponse["mode"]]
        if nature == "parole":
            narration["_prefixe_moteur"] = annonce_parole(travail, rapport)
        return ajouter_transaction(narration, nature, revision, complements,
                                   rapport if reponse["mode"] in ("conversation_pnj", "parole_joueur") else None)

    def _echanger(self, monde, intention, proposition_en_attente, enrichir, conversation_validee=None, resultat_resolu=None, retour_moteur=None):
        contexte = monde.contexte()
        faits = {k: v for k, v in contexte.items() if k != "objets_perceptibles"}
        faits["attestations"] = attestations_narratives(monde, contexte)
        from .biens import etat_comptes_joueur, offres_joueur
        faits["comptes"] = {"etat": etat_comptes_joueur(monde, contexte["interlocuteurs"]),
                            "issue": (conversation_validee or {}).get("comptes", []),
                            "offres_a_dire": (conversation_validee or {}).get("offres", []),
                            "offres": offres_joueur(monde) + (conversation_validee or {}).get("offres", [])}
        # Noms grammaticaux des seuls biens cités par les termes publics :
        # aucune position, possession cachée ni propriété physique ajoutée.
        biens_offres = {c['objet'] for c in faits['comptes']['issue'] if c.get('objet') in monde.objets}
        parts = dict((conversation_validee or {}).get('parts_comptables', {}))
        services = []
        from .agendas import en_cours
        for c in faits['comptes']['issue']:
            if not c.get('objet') or c['debiteur'] not in monde.objets: continue
            for engagement in en_cours(monde, c['debiteur'], objet=c['objet']):
                condition = engagement['condition']
                if condition.get('servir') == 'joueur':
                    parts[c['objet']] = c['objet']
                    services.append(c['objet'])
                elif engagement.get('lot'):
                    parts[c['objet']] = engagement['lot']
        faits['comptes'].update(parts=parts, services=services)
        biens_offres.update(parts.values())
        for offre in faits["comptes"]["offres"]:
            for terme in (offre["condition"], offre["contrepartie"]):
                bien = terme.get("objet") or terme.get("condition", {}).get("objet")
                if bien in monde.objets:
                    biens_offres.add(bien)
        faits["comptes"]["biens_offres"] = {
            bien: {k: copy.deepcopy(monde.objets[bien][k]) for k in
                   ("nom", "type", "genre", "pluriel", "nom_propre", "elision", "aliases")
                   if k in monde.objets[bien]} for bien in biens_offres if bien in monde.objets}
        faits['comptes']['biens_offres'].update((conversation_validee or {}).get('biens_comptables', {}))
        if resultat_resolu is not None:
            from .biens import compte
            from .agendas import contrats
            faits["comptes"]["issue"] = [
                compte(monde.data["missions"][id]["donneur"], "joueur", montant=a["montant"], etat="rendu")
                for id, a in contrats(monde).items()
                if a.get("statut") == "paye" and a.get("paye_revision") == monde.data["revision"]]
            if faits["comptes"]["issue"]:
                # Le rendu et ses comptes viennent de la même résolution du
                # moteur. Conserver ce lien permet de prouver leur couverture
                # par le texte exact, sans extraction sémantique supplémentaire.
                resultat_resolu = {**resultat_resolu,
                                   "comptes": copy.deepcopy(faits["comptes"]["issue"])}
        objets = contexte["objets_perceptibles"]
        # La liste est complète pour la vue actuelle, pas pour la salle ni les contenus
        # cachés. Les affaires accessibles dans le noir ne sont pas nécessairement vues.
        faits["perception"] = {**faits["perception"],
                               "objets_visibles": [o["id"] for o in objets if o["visible"]]}
        from .perception import couverture_vue, non_vus_connus
        faits["perception"]["couverture_vue"] = couverture_vue(monde)
        faits["perception"]["non_vus_connus"] = non_vus_connus(monde)
        faits["perception"]["contributions"] = [
            {**c, "effet_percu": c["niveau"] > 0,
             "source_visible": c["source"] in faits["perception"]["objets_visibles"]}
            for c in faits["perception"]["contributions"]]
        from .pnj import peuvent_se_parler
        from .voix import reel
        for objet in objets:
            # Chaque champ dit ce qu'il mesure : la portée de la main n'est pas celle de la voix.
            if "a_portee" in objet:
                objet["a_portee_de_main"] = objet.pop("a_portee")
            if objet.get("type") == "personnage" and reel(monde, objet.get("id")) in monde.objets:
                objet["a_portee_de_voix"] = peuvent_se_parler(monde, "joueur", reel(monde, objet["id"]))
        if contexte["mode_cases"]:
            # Le MJ reçoit une seule localisation calculée, sans coordonnées ni ancien
            # identifiant de lieu répété dans chaque objet. Le moteur garde ces données.
            faits["joueur"]["salle"] = faits["salle"]["nom"]
            faits["joueur"].pop("position", None)
            faits.pop("lieux_connus", None)
            for sortie in faits["salle"]["sorties"].values():
                sortie.pop("vers", None)
                if sortie.get("case") is not None:
                    from .localisation import relatif
                    sortie["position_relative"] = relatif(monde, monde.joueur["salle"], sortie.pop("case"))[1]
            # Les sorties qu'il connaît (vues, ou dont il a foulé le seuil) : d'autres peuvent lui échapper.
            faits["salle"]["sorties_connues"] = faits["salle"].pop("sorties")
            for objet in objets:
                parent = monde.objets.get(reel(monde, objet.get("lieu")))
                if parent:
                    objet["rattache_a"] = {"id": parent["id"], "nom": parent["nom"]}
                for cle in ("lieu", "position", "position_salle", "case_percue"):
                    objet.pop(cle, None)
                if objet.get("localisation"):
                    objet["localisation"].pop("salle_id", None)
        faits["proposition_en_attente"] = (Moteur._action_journal(monde, proposition_en_attente)
                                           if proposition_en_attente else None)
        if enrichir:
            ciblees = ambiance_ciblee(monde, intention)
            if ciblees:
                faits["ambiance_ciblee"] = ciblees
            faits["derniere_tentative"] = derniere_tentative(monde)
            faits["improvisation"] = contexte_improvisation(monde)
        disponibles = catalogue(monde) if enrichir else {}
        faits["descriptions_a_completer"] = disponibles
        savoirs_disponibles = catalogue_savoirs(monde) if enrichir else {}
        faits_disponibles = catalogue_faits(monde) if enrichir else {"supports": {}, "locuteurs": {}, "evolutions": {}}
        if any(faits_disponibles.values()):
            faits["faits_narratifs_proposables"] = faits_disponibles
        faits["connaissances_a_completer"] = savoirs_disponibles
        profil_disponible = catalogue_profil(monde) if enrichir else {}
        faits["profil_joueur_a_completer"] = profil_disponible
        atelier = dossier_atelier(monde) if enrichir else None
        if atelier:
            faits["atelier"] = atelier
        franchissements = dossier_franchissement(monde) if enrichir else None
        if franchissements:
            faits["franchissements"] = franchissements
        from .obstacles import dossier as dossier_obstacles, REGLES as REGLES_OBSTACLES
        passages = dossier_obstacles(monde) if enrichir else None
        if passages:
            faits["passages_obstacles"] = passages
        from .espace import dossier as dossier_espace, REGLES as REGLES_ESPACE
        espace = dossier_espace(monde)
        if espace:
            faits["espace"] = espace
        if retour_moteur:
            faits["retour_moteur"] = retour_moteur
        # Les effets internes et propositions anciennes ne sont pas utiles à la conversation.
        faits["evenements_recents"] = [{"tour": e["tour"], "faits": e["faits"]}
                                      for e in faits.get("evenements_recents", [])[-3:]]
        if conversation_validee is not None:
            faits["conversation_validee"] = conversation_validee
            # Ce que le moteur a établi de la parole de Corvus (dite, à qui, qui répond) est un fait attesté.
            faits["attestations"].extend([*([conversation_validee["issue"]] if conversation_validee.get("issue") else []),
                                          *conversation_validee.get("faits", [])])
        if resultat_resolu is not None:
            faits["resultat_resolu"] = resultat_resolu
            faits["attestations"].extend(resultat_resolu.get("faits", []))
        social = enrichir and bool(faits["interlocuteurs"])
        paroles = contexte_paroles(monde, intention)
        # Une parole sans conteste se dit même sans personne en vue (``paroles.destinataires``).
        parler = social or (enrichir and "personnage" in (paroles or {}).get("parole_prevue", {}))
        if paroles:
            # Chaque bloc que les règles nomment est un fait citable de premier niveau.
            faits.update(paroles)
        if enrichir:
            # Les noms privés ne servent pas à déduire une identité ou une cible d'action.
            for esprit in faits.get('esprits_interlocuteurs', {}).values():
                esprit.pop('noms_pour_repliques', None)
        faits.update({"objet:" + o["id"]: o for o in objets})
        from .noms import public
        faits = public(monde, faits)
        from .comptes_narratifs import phrases as phrases_comptes
        # Même rendu public pour préparer le MJ et pour afficher l'offre.
        # Les textes techniques d'un échange entre PNJ ne sont pas du récit.
        faits["comptes"]["formulations_offres"] = [
            " ".join(phrases_comptes({**faits, "conversation_validee": {**faits.get("conversation_validee", {}), "offres_conclues": []}, "comptes": {
                **faits["comptes"], "issue": [], "offres": [o], "offres_a_dire": [o]}}))
            for o in faits["comptes"]["offres"]]
        from .narration import echanges_passes
        # Déjà limité aux interlocuteurs publics ; garder les mots historiques
        # tels qu'ils ont été entendus, même après une présentation.
        faits["echanges_passes"] = echanges_passes(monde, faits["interlocuteurs"])
        from .narration import cibles_orientation
        faits["reperes_demandes"] = sorted(cibles_orientation(intention, faits))
        # Une identité privée sert à la réplique finale, jamais au choix d'une cible mécanique.
        # Elle est ajoutée après projection et ne devient pas une attestation du récit.
        for reference, esprit in (faits.get("esprits_interlocuteurs", {}).items() if not enrichir else ()):
            locuteur = reel(monde, reference)
            if locuteur in monde.objets:
                esprit["nom_du_locuteur"] = monde.objets[locuteur]["nom"].split(",")[0]
        from .compilateur import SCHEMA_COMPILATEUR
        schema = copy.deepcopy(SCHEMA_COMPILATEUR)
        consigne_retour = None
        if retour_moteur:
            consigne_retour = RETOUR_INTERPRETATION
        if not enrichir:
            instructions = NARRATION
            schema["properties"]["mode"] = {"type": "string", "enum": ["dialogue"]}
            schema["properties"]["texte"] = {"type": "string", "minLength": 1,
                                                "description": "Réponse finale non vide destinée au joueur."}
            schema["properties"]["proposition"] = {"type": "null"}
            if resultat_resolu is not None:
                faits = {k: faits[k] for k in ("joueur", "salle", "perception", "resultat_resolu", "attestations", "ambiance_etablie", "comptes")}
                instructions = INSTRUCTIONS_RESULTAT
            if retour_moteur:
                consigne_retour = RETOUR_REFUSE
        if not enrichir:
            instructions += REGLE_NARRATION
            from .localisation import REGLES as REGLES_LOCALISATION
            instructions += REGLES_LOCALISATION
        if enrichir:
            from .compilateur import prompt_compilateur
            instructions = prompt_compilateur(self.fournisseur)
        conversation = monde.data["conversation"][-2 if resultat_resolu is not None else -6:]
        if enrichir and not est_question(intention) and proposition_en_attente is None:
            from .commandes import analyser
            try:
                action_explicite = analyser(monde, intention)
            except ErreurMonde:
                action_explicite = None
            if action_explicite and action_explicite["action"] not in ("observer", "parler"):
                # Une commande complète n'a pas besoin des anciennes réponses du MJ.
                conversation = []
        entree = ordonner_entree({"faits": faits, "conversation": conversation, "message": intention})
        if consigne_retour:
            entree["consigne_retour_moteur"] = consigne_retour.strip()
        entree_mesuree = entree
        if enrichir:
            from .compilateur import extraire_contexte
            entree_mesuree = ordonner_entree({**entree, "faits": extraire_contexte(monde, intention, faits=faits),
                                              "compilation": True})
        debut = time.monotonic()
        self.derniere_utilisation = None
        trace = {"modele": self.modele, "revision": monde.data["revision"], "intention": intention,
                 "correction": retour_moteur is not None,
                 "taille_contexte": len(json.dumps(entree_mesuree, ensure_ascii=False)),
                 "etape": "interprétation" if enrichir else "narration du résultat" if resultat_resolu is not None else "réponse du PNJ" if conversation_validee is not None else "narration après enrichissement",
                 "empreinte_requete": hashlib.sha256(json.dumps(
                     [instructions, entree_mesuree, schema], sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
        try:
            self._audit_courant = None
            # Le monde sert au contrôle lexical de la prose, jamais à la requête.
            self._monde_controle, self._interpretation = monde, enrichir
            if enrichir:
                from .compilateur import compiler
                reponse = compiler(self._appeler, self.fournisseur, entree, intention, schema)
            else:
                reponse = self._appeler(instructions, entree, intention, "repondre_au_joueur", schema)
            trace["reponse"] = copy.deepcopy(reponse)
        except ErreurMonde as exc:
            trace["erreur"] = str(exc)
            raise
        finally:
            self._monde_controle, self._interpretation = None, False
            if self.observateur:
                trace["secondes"] = round(time.monotonic() - debut, 3)
                trace["usage"] = copy.deepcopy(self.derniere_utilisation)
                self.observateur(trace)
        if enrichir:
            verifier_disponibilite(reponse, faits, geste_en_question(monde, intention))
        # L'audit sémantique de la prose est effectué par _appeler avant ce contrôle de forme.
        if isinstance(reponse.get("proposition"), dict) and reponse.get("mode") != "parole_joueur":
            from .noms import references
            reponse["proposition"] = references(monde, reponse["proposition"])
        champs_reponse = {"mode", "texte", "faits", "proposition"}
        if isinstance(reponse, dict) and isinstance(reponse.get("faits"), list):
            # Une citation de fait inconnue ne prouve rien : elle est écartée, comme une source
            # inconnue de l'audit, sans invalider la réponse.
            reponse["faits"] = [f for f in reponse["faits"] if isinstance(f, str) and f in faits]
        if (set(reponse) not in (champs_reponse, champs_reponse | {"_texte_moteur"})
                or ("_texte_moteur" in reponse and reponse["mode"] != "dialogue")
                or not isinstance(reponse["texte"], str) or len(reponse["texte"]) > 4000
                or not isinstance(reponse["faits"], list)
                or any(not isinstance(f, str) or f not in faits for f in reponse["faits"])):
            raise ErreurMonde("Réponse du MJ invalide. Aucune action appliquée.")
        if reponse["mode"] == "dialogue":
            # Une proposition jointe à un dialogue n'est jamais exécutée : elle est écartée.
            reponse["proposition"] = None
            if not reponse["texte"].strip():
                raise ErreurMonde("Le MJ a renvoyé un dialogue vide. Aucun changement enregistré.")
        elif not enrichir:
            raise ErreurMonde("Le MJ devait rédiger une réponse finale en mode dialogue. Aucun changement enregistré.")
        elif reponse["mode"] == "action":
            if reponse["texte"] or not isinstance(reponse["proposition"], dict):
                raise ErreurMonde("Proposition du MJ invalide. Aucune action appliquée.")
        elif reponse["mode"] == "enrichir":
            if not disponibles or reponse["texte"] or not isinstance(reponse["proposition"], dict):
                raise ErreurMonde("Complément descriptif invalide. Aucun ajout appliqué.")
        elif reponse["mode"] == "enrichir_joueur":
            if not profil_disponible or reponse["texte"] or not isinstance(reponse["proposition"], dict):
                raise ErreurMonde("Complément de personnage invalide. Aucun ajout enregistré.")
        elif reponse["mode"] == "conversation_pnj":
            if not social or reponse["texte"] or not isinstance(reponse["proposition"], dict):
                raise ErreurMonde("Conversation invalide. Aucun engagement enregistré.")
        elif reponse["mode"] == "parole_joueur":
            if not parler or reponse["texte"] or not isinstance(reponse["proposition"], dict):
                raise ErreurMonde("Parole invalide. Rien n'a été dit.")
        elif reponse["mode"] == "enrichir_savoirs":
            if not savoirs_disponibles or reponse["texte"] or not isinstance(reponse["proposition"], dict):
                raise ErreurMonde("Connaissances invalides. Aucun ajout enregistré.")
        elif reponse["mode"] == "etablir_faits":
            if not any(faits_disponibles.values()) or reponse["texte"] or not isinstance(reponse["proposition"], dict):
                raise ErreurMonde("Faits narratifs invalides. Aucun ajout enregistré.")
        else:
            raise ErreurMonde("Type de réponse du MJ inconnu. Aucune action appliquée.")
        if reponse["mode"] == "dialogue" and self._audit_courant:
            reponse["_audit"] = self._audit_courant
        elif (reponse["mode"] == "action" and reponse["proposition"]["action"] in
              ("clarifier", "impossible") and self._audit_courant):
            reponse["_audit_justification"] = self._audit_courant
        return reponse

    def _appeler(self, instructions, entree, intention, fonction, schema):
        """Contrôle toute narration sortante, indépendamment de son mode d'origine."""
        self._audit_courant = None
        usage_total = None

        def appeler_brut(*arguments):
            nonlocal usage_total
            instructions_appel, entree_appel, *suite = arguments
            if entree_appel.get("compilation") and self._monde_controle is not None:
                from .compilateur import extraire_contexte
                entree_appel = {**entree_appel, "faits": extraire_contexte(
                    self._monde_controle, intention, faits=entree_appel["faits"])}
            sortie = self._appeler_brut(instructions_appel, ordonner_entree(entree_appel), *suite)
            if isinstance(sortie, dict) and "_texte_moteur" in sortie:
                raise ErreurMonde("Le MJ ne peut pas déclarer lui-même un texte comme validé par le moteur.")
            usage_total = additionner_usage(usage_total, self.derniere_utilisation)
            self.derniere_utilisation = usage_total
            return sortie

        reponse = appeler_brut(instructions, entree, intention, fonction, schema)
        if fonction != "repondre_au_joueur":
            return reponse
        # Tout ce qui a été refusé dans ce tour, transmis à chaque relance : une correction ne
        # réintroduit pas ce qu'une précédente avait déjà fait refuser.
        refusees = []
        # Les segments admis de chaque réponse refusée : le dernier recours avant le repli du moteur.
        rescapes = []
        forme_corrigee = False
        for tentative in range(3):
            while True:
                try:
                    verifier_forme_reponse(reponse, schema)
                    if len(schema.get("properties", {}).get("mode", {}).get("enum", [])) > 1:
                        verifier_disponibilite(reponse, entree["faits"],
                            self._monde_controle is not None and geste_en_question(self._monde_controle, intention))
                    break
                except RefusDeForme as exc:
                    if self.observateur:
                        self.observateur({"etape": "validation de forme", "modele": self.modele,
                                          "intention": intention, **retour_refus(reponse, exc,
                                          "Corrige la forme sans abandonner l'intention.")})
                    if forme_corrigee:
                        # Une forme invalide ne détermine pas ce que le joueur demandait.
                        # Garder ce qu'il perçoit de sa cible ; sans réponse perceptible,
                        # l'interprétation attend une précision, sans conclure à l'impossible.
                        return self._repli(entree, intention, rescapes,
                            defaut=demande_precision() if self._interpretation else None)
                    forme_corrigee = True
                    reponse = appeler_brut(instructions, {**entree, "retour_forme":
                        retour_refus(reponse, exc, "Corrige la forme sans abandonner l'intention.")},
                        intention, fonction, schema)
            if self._sans_dialogue and (reponse["mode"] == "dialogue" or
                    (reponse["mode"] == "action" and
                     reponse["proposition"].get("action") in ("clarifier", "impossible"))):
                # La boucle de validation rendra les refus publics déjà recueillis. Cette prose
                # n'est ni admise, ni publiée ; elle ne passe par aucune revue narrative.
                return reponse
            # Les phrases comptables sont ajoutées par le moteur à chaque essai,
            # avant les gardes et la preuve exacte. Elles suivent la transaction
            # et la sauvegarde de toute la réponse, jamais un préfixe hors audit.
            if reponse.get("mode") == "dialogue":
                from .comptes_narratifs import completer, presenter_offres
                entree = {**entree, "faits": presenter_offres(entree.get("faits", {}), reponse.get("texte", ""))}
                reponse = {**reponse, "texte": completer(reponse.get("texte", ""), entree.get("faits", {}))}
            passages = []
            if reponse.get("mode") == "dialogue" and isinstance(reponse.get("texte"), str):
                passages = [("texte", reponse["texte"], None)]
            elif (reponse.get("mode") == "action" and isinstance(reponse.get("proposition"), dict)
                  and reponse["proposition"].get("action") in ("clarifier", "impossible")
                  and isinstance(reponse["proposition"].get("justification"), str)
                  and reponse["proposition"]["justification"]):
                passages = [("justification", reponse["proposition"]["justification"], None)]
            obstacles = []
            audits = {}
            base, paroles = fondement_narratif(entree), fondement_paroles(entree)
            monde = self._monde_controle
            if monde is not None:
                from .noms import verifier_references
                try:
                    verifier_references(monde,reponse.get('proposition'),entree.get('faits',{}))
                except ErreurMonde as exc:
                    obstacles.append(depuis_refus(exc,'proposition'))
            # La saisie s'adresse-t-elle à quelqu'un (« Ilse, … », « à tous ») ? Sans parole que le moteur
            # a fait entendre, personne ne lui répond.
            forme = analyser_parole(monde, intention) if monde is not None else {}
            adresse = bool(forme.get("nomme") or forme.get("groupe"))
            # « Puis-je… ? » n'est renvoyé qu'une fois, au premier appel : ensuite un dialogue se contrôle.
            refus = (refus_assure(monde, intention, reponse, self._faisabilite_renvoyee
                                  or "retour_moteur" in entree.get("faits", {}), self._impossible_admis)
                     if self._interpretation and monde is not None else "")
            if refus and not obstacles:
                # Le moteur refusera cette réponse quelle qu'en soit la prose : son refus, qui dit ce
                # qu'il accepterait, passe avant toute contre-revue sémantique, qui ne serait pas lue.
                if self.observateur:
                    self.observateur({"etape": "prévalidation", "modele": self.modele, "intention": intention,
                                      "mode": reponse.get("mode"), "refus": refus})
                return reponse
            for nom, texte, effets in passages:
                if not texte.strip():
                    # Rien à contrôler : l'audit d'un texte vide ne peut qu'échouer.
                    obstacles.append(refus_audit("Le texte est vide : écris dans texte la réponse destinée au joueur.",
                                                 f"dans {nom}, la réponse destinée au joueur, non vide",
                                                 partie=nom, recu=""))
                    continue
                if monde is not None and self._interpretation:
                    from .narration import clarification_nominale
                    clarification = clarification_nominale(monde, intention, texte, entree.get("faits", {}))
                    if clarification:
                        # Une référence non résolue appelle une précision du joueur,
                        # pas trois rédactions libres de la même absence de lien.
                        return {"mode": "dialogue", "texte": clarification, "faits": [],
                                "proposition": None, "_texte_moteur": True}
                obstacles.extend(voix_auteur(texte, nom))
                if monde is not None:
                    obstacles.extend(mentions_narratives(monde, texte, base, paroles, partie=nom))
                faits = dict(entree.get("faits", {}))
                # Une parole n'a lieu que par le moteur : contrôle déterministe, quelle que soit la voie
                # (action, parole, conversation, faits) et sans dépendre du verdict de l'auditeur.
                obstacles.extend(paroles_sans_moteur(texte, faits, adresse, partie=nom))
                if effets is not None:
                    faits["effets_prevus"] = {"branche": nom, "effets": effets,
                                               "intention": reponse["proposition"].get("intention")}
                decoupage = segments_narratifs(texte)
                from .narration import segments_etablis
                etablis = segments_etablis(texte, faits)
                a_controler = {str(i): s for i, s in enumerate(decoupage) if str(i) not in etablis}
                from .comptes_narratifs import controler as controler_comptes
                refus_comptes = controler_comptes(texte, faits, nom, avant_audit=True)
                if refus_comptes:
                    obstacles.extend(refus_comptes)
                    continue
                rapport = None
                for essai in range(2):
                    from .noms import reperes_designations
                    audit = appeler_brut(
                        INSTRUCTIONS_AUDIT,
                        {"faits": faits, "segments": a_controler,
                         "designations": reperes_designations(" ".join(a_controler.values()), faits),
                         "nature": "récit conditionnel d'action" if effets is not None else "réponse du MJ"},
                        "Contrôler chaque segment de la réponse", "auditer_narration",
                        schema_audit(faits, a_controler)) if a_controler else {"segments": {}}
                    try:
                        rapport = controler_narration(texte, audit, faits, nom)
                        break
                    except AuditIllisible as exc:
                        # Un rapport illisible ne juge pas le texte : l'audit est redemandé une
                        # fois ; ensuite le texte reste non contrôlé, donc refusé.
                        if essai:
                            obstacles.append(audit_illisible(str(exc), partie=nom, texte=texte))
                    except ErreurMonde as exc:
                        # Le texte n'a pas été jugé (appel de l'auditeur manqué) : rien ne lui est reproché.
                        obstacles.append(audit_illisible(str(exc), partie=nom, texte=texte))
                        break
                if rapport is None:
                    continue
                audits[nom] = {**rapport, "faits": faits, "texte_initial": texte, "fondement": base,
                               "fondement_paroles": paroles}
                obstacles.extend(rapport["obstacles"])
                if monde is not None:
                    obstacles.extend(mentions_narratives(monde,texte,base,paroles,partie=nom,
                                                         paroles_validees=rapport['paroles']))
                    # Une voix inconnue ne se nomme ni ne nomme personne sans le moteur (déterministe).
                    obstacles.extend(voix_inconnues(monde, rapport["paroles"], faits, texte, nom))
                if nom == "texte" and rapport["obstacles"]:
                    def fautif(morceau, faits=faits, validees=rapport['paroles']):
                        return bool(voix_auteur(morceau)
                                    or (monde is not None and (mentions_narratives(
                                        monde,morceau,base,paroles,paroles_validees=validees)
                                        or voix_inconnues(monde,validees,faits,morceau)))
                                    or paroles_sans_moteur(morceau, faits, adresse))
                    garde = rescape_narratif(texte, rapport, faits, fautif)
                    if garde:
                        rescapes.append((garde[2], tentative, garde[0],
                                         {**garde[1], "faits": faits, "texte_initial": garde[0],
                                          "fondement": base, "fondement_paroles": paroles}))
            if monde is not None:
                obstacles.extend(mentions_proposees(monde, reponse, base, paroles))
            try:
                ajouts = descriptions_proposees(reponse)
                faits_proposes = (reponse.get("proposition")
                                  if reponse.get("mode") == "etablir_faits" else None)
                if ajouts or faits_proposes is not None:
                    faits = entree.get("faits", {})
                    contexte = {cle: faits.get(cle) for cle in
                                ("salle", "scenario", "faits_narratifs_proposables",
                                 "descriptions_a_completer", "connaissances_a_completer",
                                 "connaissances_pnj") if cle in faits}
                    audit = appeler_brut(INSTRUCTIONS_PORTEE,
                                        {"descriptions": [{"sujet": a["sujet"], "texte": a["texte"]}
                                                          for a in ajouts], "monde": contexte,
                                         "attestations": faits.get("attestations", []),
                                         "demande": intention,
                                         **({"proposition_faits": faits_proposes}
                                            if faits_proposes is not None else {})},
                                        "Contrôler la portée des descriptions proposées",
                                        "auditer_portee", SCHEMA_PORTEE_FAITS
                                        if faits_proposes is not None else SCHEMA_PORTEE)
                    if faits_proposes is not None:
                        obstacles.extend(controler_usages(faits_proposes, audit))
                    obstacles.extend(controler_portee(
                        ajouts, audit, faits.get("attestations", [])))
            except (RapportIllisible, ErreurFournisseur) as exc:
                # L'auditeur n'a pas rendu de jugement lisible : rien n'est reproché à la proposition.
                obstacles.append(audit_illisible(str(exc), partie="description"))
            except ErreurMonde as exc:
                obstacles.append(depuis_refus(exc, "description"))
            try:
                qualifications = qualifications_proposees(reponse, entree.get("faits", {}))
                if qualifications and not obstacles:
                    if monde is not None:
                        # Forme, bornes, masse et propriétés déjà connues sont
                        # jugées par le moteur avant toute appréciation sémantique.
                        preparer_faits(monde, sans_suite(reponse["proposition"]), monde.data["revision"])
                    audit = appeler_brut(INSTRUCTIONS_PHYSIQUE,
                                        {"qualifications": qualifications,
                                         "scenario": entree.get("faits", {}).get("scenario", {})},
                                        "Contrôler les capacités proposées",
                                        "auditer_capacites", SCHEMA_PHYSIQUE)
                    obstacles.extend(controler_physique(qualifications, audit))
            except (RapportIllisible, ErreurFournisseur) as exc:
                # L'auditeur n'a pas rendu de jugement lisible : rien n'est reproché à la proposition.
                obstacles.append(audit_illisible(str(exc), partie="qualification"))
            except ErreurMonde as exc:
                obstacles.append(depuis_refus(exc, "qualification"))
            if not obstacles:
                if "texte" in audits:
                    self._audit_courant = audits["texte"]
                    reponse["texte"] = audits["texte"]["texte_controle"]
                if "justification" in audits:
                    self._audit_courant = audits["justification"]
                    reponse["proposition"]["justification"] = audits["justification"]["texte_controle"]
                elif (reponse.get("mode") == "action"
                      and isinstance(reponse.get("proposition"), dict)
                      and "justification" in reponse["proposition"]):
                    # Ce brouillon n'est ni audité ni affiché : il ne doit pas
                    # non plus entrer dans le journal ou le contexte futur.
                    reponse["proposition"]["justification"] = ""
                return reponse
            if self.observateur:
                self.observateur({"etape": "contrôle narratif", "modele": self.modele,
                                  "revision": entree.get("faits", {}).get("revision", 0),
                                  "intention": intention, "tentative": tentative + 1,
                                  "obstacles": copy.deepcopy(obstacles)})
            if tentative == 2:
                return self._repli(entree, intention, rescapes)
            for o in obstacles:
                if o not in refusees:
                    refusees.append(o)
            correction = ordonner_entree({**entree, "controle_narratif": refusees,
                                          "consigne_revision": INSTRUCTIONS_REVISION.strip()})
            reponse = appeler_brut(instructions, correction,
                                   intention, fonction, schema)
        raise ErreurMonde("Le contrôle narratif n'a pas abouti.")

    def _repli(self, entree, intention, rescapes, *, defaut=None):
        """Aucune réponse du MJ n'est admise après trois essais. Dans l'ordre : ce que le moteur a
        établi pour le joueur (le résultat résolu, l'issue d'une parole de Corvus), puis les segments
        admis de la réponse qui en garde le plus, puis ce que dit le moteur (``narration.repli``).
        Les faits d'une négociation ou d'un savoir s'adressent au MJ : ils ne s'affichent pas."""
        faits = entree.get("faits", {})
        from .comptes_narratifs import phrases, completer
        if phrases(faits):
            # Même après trois refus, les comptes ne dépendent ni de Luna ni
            # d'un drapeau dispensant de la preuve avant enregistrement.
            lignes = []
            for cle in ("resultat_resolu", "conversation_validee"):
                bloc = faits.get(cle) or {}
                if cle == "resultat_resolu" or bloc.get("operation") == "parole_joueur":
                    lignes.extend(s for s in bloc.get("faits", []) if isinstance(s, str) and s.strip())
            texte = completer(" ".join(lignes), faits)
            controle = controler_narration(texte, {"segments": {}}, faits)
            if controle["obstacles"]:
                raise ErreurMonde("Le compte rendu du moteur est incomplet.",
                                  controle["obstacles"][0]["attendu"])
            self._audit_courant = {**controle, "faits": faits, "texte_initial": texte,
                                   "fondement": fondement_narratif(entree),
                                   "fondement_paroles": fondement_paroles(entree)}
            return self._noter_repli(intention, "comptes du moteur",
                                     {"mode": "dialogue", "texte": texte,
                                      "faits": ["comptes"], "proposition": None})
        for cle in ("resultat_resolu", "conversation_validee"):
            bloc = faits.get(cle)
            pour_joueur = isinstance(bloc, dict) and (cle == "resultat_resolu"
                                                      or bloc.get("operation") == "parole_joueur")
            lignes = ([s for s in (bloc.get("faits") or []) if isinstance(s, str) and s.strip()]
                      if pour_joueur else [])
            if lignes:
                return self._noter_repli(intention, cle, {"mode": "dialogue", "texte": " ".join(lignes),
                                                          "faits": [cle], "proposition": None,
                                                          "_texte_moteur": True})
        if rescapes:
            *_, texte, audit = max(rescapes, key=lambda r: (r[0], r[1]))
            self._audit_courant = audit
            sources = sorted({s for ligne in audit["segments"] for s in ligne["sources"]})
            return self._noter_repli(intention, "segments admis",
                                     {"mode": "dialogue", "texte": texte, "faits": sources, "proposition": None})
        monde = self._monde_controle
        texte = (repli_narratif(monde, faits, entree.get("message", ""), defaut=defaut) if monde is not None
                 else "Rien de ce que tu perçois ou sais ne permet d'y répondre avec certitude.")
        return self._noter_repli(intention, "moteur", {"mode": "dialogue", "texte": texte, "faits": [],
                                                       "proposition": None, "_texte_moteur": True})

    def _noter_repli(self, intention, voie, reponse):
        if self.observateur:
            self.observateur({"etape": "repli du contrôle narratif", "modele": self.modele,
                              "intention": intention, "voie": voie, "texte": reponse["texte"]})
        return reponse

    def _appeler_brut(self, instructions, entree, intention, fonction, schema):
        """Un appel au fournisseur. Avec ``journal_complet`` et un observateur, chaque appel laisse
        une trace entière : instructions, entrée, schéma, réponse brute, usage et durée."""
        if self.erreur_auth:
            raise ErreurMonde(self.erreur_auth)
        entree = ordonner_entree(entree)
        debut, brut, erreur = time.monotonic(), None, None
        self.dernier_brut = self.derniere_utilisation = None
        self.derniere_sortie = []
        try:
            # Règle du jeu, commune à tous les fournisseurs : une action tient en 2 000 caractères.
            if len(intention) > LIMITE_INTENTION:
                raise ErreurMonde("Limite ton action à 2 000 caractères.")
            demande = Demande(instructions, copy.deepcopy(entree), intention, fonction,
                              copy.deepcopy(schema), self.modele, self.effort, self.timeout,
                              self.cle_cache, self.reflexion)
            reponse = self.fournisseur.appeler(demande)
            if not isinstance(reponse, Reponse):
                raise ErreurMonde("Réponse du fournisseur mal formée. Aucune action appliquée.")
            brut = self.dernier_brut = reponse.brut
            self.derniere_utilisation = reponse.utilisation
            self.derniere_sortie = reponse.sortie
            if not isinstance(reponse.arguments, dict):
                raise ErreurMonde("Réponse du fournisseur mal formée. Aucune action appliquée.")
            return reponse.arguments
        except ErreurFournisseur as exc:
            brut = self.dernier_brut = exc.brut
            self.derniere_utilisation = exc.utilisation
            self.derniere_sortie = exc.sortie
            self.erreur_auth = exc.erreur_auth
            erreur = str(exc)
            raise
        except ErreurMonde as exc:
            erreur = str(exc)
            raise
        finally:
            if self.observateur and self.journal_complet:
                self.observateur({"etape": "appel", "fonction": fonction, "modele": self.modele,
                                  "connexion": self.connexion, "effort": self.effort,
                                  "intention": intention, "revision": (entree.get("faits") or {}).get("revision", 0),
                                  "instructions": instructions, "entree": copy.deepcopy(entree),
                                  "schema": schema, "brut": brut if brut is not None else self.dernier_brut,
                                  "erreur": erreur,
                                  "usage": copy.deepcopy(self.derniere_utilisation),
                                  "secondes": round(time.monotonic() - debut, 3)})


# Compatibilité des imports des bancs existants ; le MJ ne dépend plus d’OpenAI.
MJOpenAI = MJ
