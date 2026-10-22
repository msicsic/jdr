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
from .paroles import (REGLES as REGLES_PAROLE, SCHEMA_PAROLE, ParoleImpossible, analyser as analyser_parole,
                      annonce as annonce_parole, contexte as contexte_paroles, preparer_parole)
from .commandes import PERCEPTIONS, est_question, faisabilite
from .connaissances import SCHEMA_SAVOIRS, catalogue as catalogue_savoirs, preparer_savoirs
from .operations import SCHEMA_SEQUENCE
from .config import MODELE_PAR_DEFAUT, DEFAUTS_CONNEXION
from .francais import designer
from .artisanat import (SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE, dossier as dossier_atelier,
                        REGLES as REGLES_ATELIER)
from .harnais import derniere_tentative
from .consignes import INTERPRETATION
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
                               descriptions as descriptions_proposees,
                               controler as controler_portee)
from .coherence_physique import (SCHEMA as SCHEMA_PHYSIQUE,
                                 INSTRUCTIONS as INSTRUCTIONS_PHYSIQUE,
                                 propositions as qualifications_proposees,
                                 controler as controler_physique)
from .moteur import QualificationRequise
from .proximite import HorsDePortee
from .refus import RapportIllisible, RefusDeForme, audit as refus_audit, audit_illisible, depuis_refus
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
aller : cible nord/sud/est/ouest. attendre : cible vide.
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


SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ACTIONS},
        "cible": {"type": "string", "description": "Identifiant exact de la cible visible, direction, ou chaîne vide."},
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
    return prevue(monde, intention) if analyser_parole(monde, intention)["explicite"] else None


def parole_attendue(monde, intention):
    """La saisie est une parole que le moteur peut faire entendre : ni un dialogue du MJ, ni un geste."""
    return "personnage" in (parole_annoncee(monde, intention) or {})


def parole_du_moteur(monde, intention):
    """La parole que le moteur prononce lui-même quand le MJ s'obstine à la raconter : les mots du
    joueur, tels quels, à ceux que le moteur a fixés, sans contenu typé. Sans mots imposés, le joueur
    les donne : le moteur ne les invente pas."""
    from .paroles import _nom_court
    forme, prevue = analyser_parole(monde, intention), parole_annoncee(monde, intention)
    if forme["mots"]:
        return {"mode": "parole_joueur", "texte": "", "faits": [],
                "proposition": {"personnage": prevue["personnage"], "replique": forme["mots"], "contenu": []}}
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


def refus_assure(monde, intention, reponse, deja_renvoyee=False):
    """Pourquoi le moteur refusera cette réponse d'interprétation, quelle qu'en soit la prose, ou "" :
    un dialogue quand la saisie est une parole sans conteste (le moteur la fait entendre), un ajout
    persistant que sa validation écarte (détail d'un objet hors de portée, savoir mal formé…). Les mêmes
    validations, sur copie, que la suite du tour : rien n'est appliqué."""
    mode, p = reponse.get("mode"), reponse.get("proposition")
    if mode == "dialogue" and "_texte_moteur" not in reponse and parole_attendue(monde, intention):
        return "Corvus le dit : c'est une parole."
    if mode == "dialogue" and not deja_renvoyee and renvoi(monde, intention):
        return renvoi(monde, intention)[0]
    preparer = {"etablir_faits": preparer_faits, "enrichir": preparer_complements,
                "enrichir_savoirs": preparer_savoirs}.get(mode)
    if preparer is None or not isinstance(p, dict):
        return ""
    try:
        preparer(monde, p, monde.data["revision"])
    except ErreurMonde as exc:
        return str(exc)
    return ""


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


def expliquer_refus(premier, dernier):
    """Une proposition rejetée ne prouve rien sur les capacités de Corvus."""
    return "Je n'ai pas pu déterminer une manœuvre fidèle à ta demande. Corvus n'a rien tenté."


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
        self._sans_dialogue = False    # un dialogue serait remplacé par le refus du moteur : pas d'audit
        self._faisabilite_renvoyee = False  # « puis-je… ? » déjà renvoyé : un dialogue se contrôle
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
        return self._appeler(INSTRUCTIONS, {"monde": monde.contexte(), "intention": intention},
                             intention, "proposer_action", SCHEMA)

    def _auditer_action(self, intention, plan, revision, monde=None):
        from .couverture_action import (SCHEMA as SCHEMA_COUVERTURE,
                                        INSTRUCTIONS as INSTRUCTIONS_COUVERTURE,
                                        RapportInvalide, entree as entree_couverture,
                                        verifier as verifier_couverture)
        for essai in range(2):
            rapport = self._appeler_brut(
                INSTRUCTIONS_COUVERTURE, entree_couverture(intention, plan, monde),
                "Contrôler la fidélité du plan", "auditer_action", SCHEMA_COUVERTURE)
            if self.observateur:
                self.observateur({"etape": "couverture de l'action", "modele": self.modele,
                                  "revision": revision, "intention": intention,
                                  "rapport": copy.deepcopy(rapport)})
            try:
                verifier_couverture(rapport, plan)
                return
            except RapportInvalide:
                # Une revue illisible ne juge pas la proposition : on la redemande une fois,
                # puis le plan déjà validé par le moteur passe, comme dans le doute.
                if essai:
                    if self.observateur:
                        self.observateur({"etape": "couverture de l'action", "modele": self.modele,
                                          "revision": revision, "intention": intention,
                                          "erreur": "Contre-revue illisible deux fois : plan accepté sans elle."})
                    return

    def raconter_resultat(self, monde, resultat):
        """Narration seule : le résultat est déjà résolu et sauvegardé par la boucle de jeu."""
        return self._echanger(monde, "Raconte la manœuvre qui vient d'être résolue.", None,
                              enrichir=False, resultat_resolu=resultat)

    def echanger(self, monde, intention, proposition_en_attente=None):
        """Complète les abords autorisés avant l'arbitrage, toujours sur copie."""
        from .espace import a_completer, preparer, SCHEMA as SCHEMA_ESPACE
        cadres = a_completer(monde)
        if not cadres:
            return self._echanger_prepare(monde, intention, proposition_en_attente)
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
        reponse = copy.deepcopy(self._echanger_prepare(travail, intention, proposition_en_attente))
        return ajouter_transaction(reponse, "espace", monde.data["revision"], p, debut=True)

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
            elif (reponse["mode"] == "dialogue" and not ({"_audit", "_texte_moteur"} & set(reponse))
                  and renvoi(monde, intention)):
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
                        raise RefusDeForme("Réexamine l'intention entière et les possibilités du moteur avant de "
                                           "conclure qu'elle est impossible.",
                                           "action : le geste que demande la saisie, tel quel (le moteur dit ce qui "
                                           "manque) ; impossible seulement si aucune action du moteur ne le couvre.")
                if p.get("action") in ("clarifier", "impossible"):
                    break
                # Une question sur la faisabilité d'un geste se prépare comme sa demande : la boucle de
                # jeu ne l'exécute pas (``commandes.PERCEPTIONS``) et montre ce qu'il demanderait.
                try:
                    plan = Moteur(monde).preparer(p, "MJ")
                except ErreurMonde as exc:
                    if p.get("action") not in PERCEPTIONS and not isinstance(exc, (QualificationRequise, RefusDeForme)):
                        refus_du_moteur = exc
                    raise
                if (premier_refus and not plan.effets and not plan.information
                        and not any(etape.effets or etape.information for etape in plan.plans)):
                    raise ErreurMonde("La proposition corrigée ne réalise aucun effet de la manœuvre demandée.",
                                      "garde les gestes de l'intention qui changent le monde ; si aucun n'est possible, "
                                      "réponds en dialogue sur l'obstacle.")
                self._auditer_action(intention, plan, revision, monde)
                break
            except ErreurMonde as exc:
                dernier_refus = (p, str(exc))
                if premier_refus is None:
                    premier_refus = dernier_refus
                retour = retour_refus(p, exc, "Corrige uniquement la proposition, sans modifier les faits ni abandonner une partie de l'intention. Sinon explique l'obstacle en dialogue.")
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
                    # Aucune proposition ne rapproche le joueur : on explique sans redemander.
                    correction_utilisee = True
                forme = isinstance(exc, RefusDeForme) and not forme_corrigee and tentative < 2
                if correction_utilisee and not forme and parole_attendue(monde, intention):
                    # Une parole n'est jamais perdue : le moteur prononce lui-même les mots du joueur.
                    reponse = parole_du_moteur(monde, intention)
                    if reponse["mode"] == "dialogue":
                        return reponse
                    break
                if correction_utilisee and not forme and faisabilite and refus_du_moteur is not None:
                    # Rien n'est tenté : le joueur lit pourquoi le monde ne le permet pas, tel quel.
                    return reponse_du_moteur(refus_du_moteur)
                if correction_utilisee and not forme:
                    retour = {"propositions_refusees": [premier_refus, dernier_refus],
                              "consigne": "Aucune action n'a été exécutée. Explique dans la fiction ce qui gêne les gestes envisagés, à partir des faits fournis, sans parler de proposition, de refus, de moteur ni de déclaration. Ne raconte pas le geste comme fait ni commencé, et ne fais parler aucun personnage : c'est toi qui expliques. Ne conclus pas que l'intention entière est impossible."}
                    try:
                        explication = self._echanger(monde, intention, proposition_en_attente,
                                                    enrichir=False, retour_moteur=retour)
                        if explication.get("mode") != "dialogue" or not explication.get("_audit"):
                            raise ErreurMonde("L'explication finale doit être un dialogue contrôlé.")
                        explication["_validation_refusee"] = True
                        return explication
                    except ErreurMonde:
                        pass
                    return {"mode": "dialogue", "texte": expliquer_refus(premier_refus, dernier_refus),
                            "faits": [], "proposition": None, "_validation_refusee": True,
                            "_texte_moteur": True}
                if forme:
                    forme_corrigee = True
                else:
                    correction_utilisee = True
                # Une question dont le geste est refusé par le moteur : seule une proposition corrigée peut
                # encore y répondre ; un dialogue serait remplacé par ce refus, il n'est pas contrôlé.
                self._sans_dialogue = faisabilite and refus_du_moteur is exc
                try:
                    reponse = self._echanger(monde, intention, proposition_en_attente, enrichir=True,
                                             retour_moteur=retour)
                finally:
                    self._sans_dialogue = False
        if (reponse["mode"] == "dialogue" and faisabilite and refus_du_moteur is not None
                and not reponse.get("_validation_refusee")):
            # Corrigée en dialogue après le refus d'un geste demandé en question : la raison du moteur.
            return reponse_du_moteur(refus_du_moteur)
        if (reponse["mode"] == "dialogue" and not reponse.get("_validation_refusee")
                and parole_attendue(monde, intention)):
            # Corrigée en dialogue après un geste refusé (ou repli du contrôle) : la parole reste au moteur.
            reponse = parole_du_moteur(monde, intention)
            if reponse["mode"] == "dialogue":
                return reponse
        if reponse["mode"] == "enrichir_joueur":
            p = reponse["proposition"]
            travail = preparer_profil(monde, p, revision)
            return ajouter_transaction(
                {"mode": "dialogue", "texte": reponse_profil(travail, p), "faits": ["joueur"],
                 "proposition": None, "_texte_moteur": True}, "profil_joueur", revision, p)
        if reponse["mode"] == "etablir_faits":
            p = reponse["proposition"]
            try:
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
                    raise ErreurMonde("La correction des faits narratifs n'a pas abouti.")
                p = reponse["proposition"]
                travail, texte, _ = preparer_faits(monde, p, revision)
            if suite_fait:
                # Un seul groupe de faits par tour : le réexamen ne relance pas l'invention.
                raise ErreurMonde("Le réexamen après un fait établi a proposé d'autres faits.")
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
            for essai in range(3):
                # Des mots imposés par le joueur (guillemets, deux-points, interpellation) sont dits
                # tels quels, sans réécriture.
                complements = {**reponse["proposition"],
                               "replique": (analyser_parole(monde, intention)["mots"]
                                            or reponse["proposition"].get("replique", "")),
                               "_intention": intention[:600]}
                try:
                    travail, rapport = preparer_parole(monde, complements, revision)
                    break
                except ParoleImpossible as exc:
                    # À qui parler, de quelle façon : c'est au joueur de préciser ou de s'approcher.
                    return {"mode": "dialogue", "texte": str(exc), "faits": [], "proposition": None,
                            "_texte_moteur": True, "_validation_refusee": True}
                except ErreurMonde as exc:
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
                                          "Corrige la parole : la réplique ne nomme que ce que Corvus connaît "
                                          "d'après les faits, le message et la conversation.")
                    if self.observateur:
                        self.observateur({"etape": "validation", "modele": self.modele, "intention": intention,
                                          "revision": revision, "tentative": 1, **retour})
                    reponse = self._echanger(monde, intention, proposition_en_attente,
                                             enrichir=True, retour_moteur=retour)
                    if reponse["mode"] != "parole_joueur":
                        if reponse["mode"] == "dialogue":
                            return reponse
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
        objets = contexte["objets_perceptibles"]
        from .pnj import peuvent_se_parler
        for objet in objets:
            # Chaque champ dit ce qu'il mesure : la portée de la main n'est pas celle de la voix.
            if "a_portee" in objet:
                objet["a_portee_de_main"] = objet.pop("a_portee")
            if objet.get("type") == "personnage" and objet.get("id") in monde.objets:
                objet["a_portee_de_voix"] = peuvent_se_parler(monde, "joueur", objet["id"])
        if contexte["mode_cases"]:
            # Le MJ reçoit une seule localisation calculée, sans coordonnées ni ancien
            # identifiant de lieu répété dans chaque objet. Le moteur garde ces données.
            faits["joueur"]["salle"] = faits["salle"]["nom"]
            faits["joueur"].pop("position", None)
            faits.pop("lieux_connus", None)
            for sortie in faits["salle"]["sorties"].values():
                sortie.pop("vers", None)
            # Les sorties qu'il connaît (vues, ou dont il a foulé le seuil) : d'autres peuvent lui échapper.
            faits["salle"]["sorties_connues"] = faits["salle"].pop("sorties")
            for objet in objets:
                parent = monde.objets.get(objet.get("lieu"))
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
        faits.update({"objet:" + o["id"]: o for o in objets})
        schema = {
            "type": "object", "additionalProperties": False,
            "properties": {
                "mode": {"type": "string", "enum": ["dialogue", "action"] + (["enrichir_joueur"] if profil_disponible else []) + (["enrichir"] if disponibles else []) + (["conversation_pnj"] if social else []) + (["parole_joueur"] if parler else []) + (["enrichir_savoirs"] if savoirs_disponibles else []) + (["etablir_faits"] if any(faits_disponibles.values()) else [])},
                "texte": {"type": "string"},
                "faits": {"type": "array", "items": {"type": "string", "enum": list(faits)}},
                "proposition": {"anyOf": [SCHEMA, SCHEMA_SEQUENCE, {"type": "null"}] + ([SCHEMA_PROFIL] if profil_disponible else []) + ([SCHEMA_IMPROVISATION, SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE] if enrichir else []) + ([SCHEMA_COMPLEMENTS] if disponibles else []) + ([SCHEMA_CONVERSATION] if social else []) + ([SCHEMA_PAROLE] if parler else []) + ([SCHEMA_SAVOIRS] if savoirs_disponibles else []) + ([SCHEMA_FAITS] if any(faits_disponibles.values()) else [])},
            },
            "required": ["mode", "texte", "faits", "proposition"],
        }
        instructions = INTERPRETATION
        if atelier:
            instructions += REGLES_ATELIER
        if franchissements:
            instructions += REGLES_FRANCHISSEMENT
        if enrichir and espace:
            instructions += REGLES_ESPACE
        if retour_moteur:
            instructions += ("\nLe retour_moteur est un contrôle fiable : corrige la proposition précédente, ou réponds en dialogue sur l'obstacle, sans exécuter autre chose."
                             "\nSon champ attendu, quand il existe, dit en champs et identifiants ce qu'une proposition corrigée "
                             "doit contenir : suis-le ; il ne s'adresse jamais au joueur."
                             "\nSi tu réponds en dialogue, rien n'a eu lieu : c'est toi qui expliques l'obstacle, aucun "
                             "personnage ne parle ni ne réagit.")
        if parler:
            instructions += REGLES_PAROLE
        if not enrichir:
            instructions = NARRATION
            schema["properties"]["mode"] = {"type": "string", "enum": ["dialogue"]}
            schema["properties"]["texte"] = {"type": "string", "minLength": 1,
                                                "description": "Réponse finale non vide destinée au joueur."}
            schema["properties"]["proposition"] = {"type": "null"}
            if resultat_resolu is not None:
                faits = {k: faits[k] for k in ("joueur", "salle", "perception", "resultat_resolu", "attestations", "ambiance_etablie")}
                schema["properties"]["faits"]["items"]["enum"] = list(faits)
                instructions = """Tu racontes en français et en tutoyant le joueur une manœuvre DÉJÀ RÉSOLUE.
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
            if retour_moteur:
                instructions += "\nLes propositions précédentes ont été refusées avant toute exécution. Explique les conditions pertinentes à partir des faits fournis. Ne présente pas ces refus comme une tentative de Corvus ni comme une preuve que son intention entière est impossible."
        instructions += REGLE_NARRATION
        from .localisation import REGLES as REGLES_LOCALISATION
        instructions += REGLES_LOCALISATION
        if monde.data.get("mode_cases") and enrichir:
            instructions += """\nLe joueur se déplace case par case avec les touches de la carte : une cible trop loin
(a_portee_de_main=false) appelle une invitation à s'approcher, car voir un objet ne suffit pas à le
manipuler ; un personnage hors de portée de main peut être à portée de voix (a_portee_de_voix).
salle.sorties_connues liste les sorties que Corvus connaît : d'autres peuvent lui échapper. La vue s'arrête aux murs, aux portes fermées et à l'obscurité : à distance, Corvus
ne connaît ni les détails, ni ce qui est derrière un mur, et il ne se déplace que par ses pas.
Il voit devant lui (120°) et à ses côtés, pas derrière : ce qui est dans son dos n'est pas dans
objets_perceptibles, mais dans souvenirs_visuels s'il l'a déjà vu. Pour regarder ailleurs sans bouger : action tourner, cible une direction
(nord, sud-est…). Un geste sur un objet qu'il verrait en se tournant le tourne d'abord vers lui.
Ses pas s'entendent de près et font se retourner ; à pas feutrés (action faufiler, cible une
direction), plus lents, ils ne s'entendent que de tout près.
"""
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
        entree = {"faits": faits, "conversation": conversation, "message": intention}
        debut = time.monotonic()
        self.derniere_utilisation = None
        trace = {"modele": self.modele, "revision": monde.data["revision"], "intention": intention,
                 "correction": retour_moteur is not None,
                 "taille_contexte": len(json.dumps(entree, ensure_ascii=False)),
                 "etape": "interprétation" if enrichir else "narration du résultat" if resultat_resolu is not None else "réponse du PNJ" if conversation_validee is not None else "narration après enrichissement",
                 "empreinte_requete": hashlib.sha256(json.dumps(
                     [instructions, entree, schema], sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
        try:
            self._audit_courant = None
            # Le monde sert au contrôle lexical de la prose, jamais à la requête.
            self._monde_controle, self._interpretation = monde, enrichir
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
        # L'audit sémantique de la prose est effectué par _appeler avant ce contrôle de forme.
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
            sortie = self._appeler_brut(*arguments)
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
        for tentative in range(3):
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
            # La saisie s'adresse-t-elle à quelqu'un (« Ilse, … », « à tous ») ? Sans parole que le moteur
            # a fait entendre, personne ne lui répond.
            forme = analyser_parole(monde, intention) if monde is not None else {}
            adresse = bool(forme.get("nomme") or forme.get("groupe"))
            # « Puis-je… ? » n'est renvoyé qu'une fois, au premier appel : ensuite un dialogue se contrôle.
            refus = (refus_assure(monde, intention, reponse, self._faisabilite_renvoyee
                                  or "retour_moteur" in entree.get("faits", {}))
                     if self._interpretation and monde is not None else "")
            if self._sans_dialogue and reponse.get("mode") == "dialogue":
                refus = "Un dialogue ne répond pas à cette question : le refus du moteur y répond."
            if refus:
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
                rapport = None
                for essai in range(2):
                    audit = appeler_brut(
                        INSTRUCTIONS_AUDIT,
                        {"faits": faits, "segments": {str(i): s for i, s in enumerate(decoupage)},
                         "nature": "récit conditionnel d'action" if effets is not None else "réponse du MJ"},
                        "Contrôler chaque segment de la réponse", "auditer_narration",
                        schema_audit(faits, len(decoupage)))
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
                    # Une voix inconnue ne se nomme ni ne nomme personne sans le moteur (déterministe).
                    obstacles.extend(voix_inconnues(monde, rapport["paroles"], faits, texte, nom))
                if nom == "texte" and rapport["obstacles"]:
                    def fautif(morceau, faits=faits):
                        return bool(voix_auteur(morceau)
                                    or (monde is not None and mentions_narratives(monde, morceau, base, paroles))
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
                if ajouts:
                    faits = entree.get("faits", {})
                    contexte = {cle: faits.get(cle) for cle in
                                ("salle", "scenario", "faits_narratifs_proposables",
                                 "descriptions_a_completer", "connaissances_a_completer",
                                 "connaissances_pnj") if cle in faits}
                    audit = appeler_brut(INSTRUCTIONS_PORTEE,
                                        {"descriptions": [{"sujet": a["sujet"], "texte": a["texte"]}
                                                          for a in ajouts], "monde": contexte,
                                         "attestations": faits.get("attestations", [])},
                                        "Contrôler la portée des descriptions proposées",
                                        "auditer_portee", SCHEMA_PORTEE)
                    obstacles.extend(controler_portee(
                        ajouts, audit, faits.get("attestations", [])))
            except (RapportIllisible, ErreurFournisseur) as exc:
                # L'auditeur n'a pas rendu de jugement lisible : rien n'est reproché à la proposition.
                obstacles.append(audit_illisible(str(exc), partie="description"))
            except ErreurMonde as exc:
                obstacles.append(depuis_refus(exc, "description"))
            try:
                qualifications = qualifications_proposees(reponse, entree.get("faits", {}))
                if qualifications:
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
                champs = {"mode", "texte", "faits", "proposition"}
                faits_connus = entree.get("faits", {})
                if isinstance(reponse, dict) and isinstance(reponse.get("faits"), list):
                    reponse["faits"] = [f for f in reponse["faits"] if isinstance(f, str) and f in faits_connus]
                if (not isinstance(reponse, dict) or set(reponse) != champs
                        or not isinstance(reponse["faits"], list)
                        or any(not isinstance(f, str) or f not in faits_connus
                               for f in reponse["faits"])
                        or (reponse["mode"] == "dialogue" and
                            (reponse["proposition"] is not None
                             or not isinstance(reponse["texte"], str)
                             or not reponse["texte"].strip()))):
                    raise ErreurMonde("Réponse du MJ invalide. Aucune action appliquée.")
                return self._repli(entree, intention, rescapes)
            for o in obstacles:
                if o not in refusees:
                    refusees.append(o)
            correction = {**entree, "controle_narratif": refusees}
            reponse = appeler_brut(instructions + INSTRUCTIONS_REVISION, correction,
                                   intention, fonction, schema)
        raise ErreurMonde("Le contrôle narratif n'a pas abouti.")

    def _repli(self, entree, intention, rescapes):
        """Aucune réponse du MJ n'est admise après trois essais. Dans l'ordre : ce que le moteur a
        établi pour le joueur (le résultat résolu, l'issue d'une parole de Corvus), puis les segments
        admis de la réponse qui en garde le plus, puis ce que dit le moteur (``narration.repli``).
        Les faits d'une négociation ou d'un savoir s'adressent au MJ : ils ne s'affichent pas."""
        faits = entree.get("faits", {})
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
        texte = (repli_narratif(monde, faits, entree.get("message", "")) if monde is not None
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
