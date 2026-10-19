"""MJ distant : un appel Responses, une proposition typée, aucun accès direct au monde."""
from __future__ import annotations

import json
import copy
import hashlib
import os
import time
import urllib.error
import urllib.request

from .monde import ErreurMonde, normaliser
from .moteur import ACTIONS, METHODES, Moteur
from .connexion import jeton, modeles
from .enrichissement import SCHEMA_COMPLEMENTS, catalogue, preparer_complements
from .faits_locaux import SCHEMA_FAITS, catalogue as catalogue_faits, preparer_faits
from .dialogues import SCHEMA_CONVERSATION, preparer_conversation
from .paroles import REGLES as REGLES_PAROLE, SCHEMA_PAROLE, citation, contexte as contexte_paroles, destinataire_nomme, preparer_parole
from .commandes import est_question
from .connaissances import SCHEMA_SAVOIRS, catalogue as catalogue_savoirs, preparer_savoirs
from .operations import SCHEMA_SEQUENCE
from .config import MODELE_PAR_DEFAUT
from .francais import designer
from .artisanat import SCHEMA_FABRICATION, dossier as dossier_atelier, REGLES as REGLES_ATELIER
from .harnais import derniere_tentative
from .consignes import INTERPRETATION
from .franchissement import dossier as dossier_franchissement, REGLES as REGLES_FRANCHISSEMENT
from .improvisation import SCHEMA as SCHEMA_IMPROVISATION, contexte as contexte_improvisation
from .profil_joueur import SCHEMA as SCHEMA_PROFIL, catalogue as catalogue_profil, preparer as preparer_profil, reponse as reponse_profil
from .narration import (AuditIllisible, schema_audit, voix_auteur, INSTRUCTIONS_AUDIT, INSTRUCTIONS_REVISION, REGLE_NARRATION,
                        ambiance_ciblee,
                        segments as segments_narratifs, controler as controler_narration,
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
from .transactions import ajouter as ajouter_transaction


def lire_flux(reponse):
    """Un succès SSE exige l'événement terminal response.completed, jamais un fragment."""
    bloc = []
    taille = 0
    elements = {}
    types = set()
    for ligne in reponse:
        taille += len(ligne)
        if taille > 4_000_000:
            raise ErreurMonde("Réponse du MJ trop volumineuse. Aucune action appliquée.")
        texte = ligne.decode("utf-8").rstrip("\r\n")
        if texte.startswith("data:"):
            bloc.append(texte[5:].lstrip())
        elif not texte and bloc:
            donnees = "\n".join(bloc)
            bloc = []
            if donnees == "[DONE]":
                break
            evenement = json.loads(donnees)
            types.add(evenement.get("type", "inconnu"))
            if evenement.get("type") == "response.output_item.done":
                elements[evenement["output_index"]] = evenement["item"]
            if evenement.get("type") == "response.completed":
                resultat = evenement["response"]
                # Certains flux n'incluent pas à nouveau les éléments déjà émis dans le terminal.
                if not resultat.get("output") and elements:
                    resultat["output"] = [elements[i] for i in sorted(elements)]
                resultat["_types_evenements"] = sorted(types)
                return resultat
            if evenement.get("type") in ("response.failed", "response.incomplete", "error"):
                raise ErreurMonde("Le MJ ChatGPT n'a pas terminé la réponse (" + raison_interruption(evenement) + ").")
    raise ErreurMonde("Flux du MJ interrompu avant la fin. Aucune action appliquée.")


def raison_interruption(evenement):
    """La raison donnée par l'API d'une réponse en échec ou incomplète, pour le diagnostic."""
    reponse = evenement.get("response") or {}
    erreur = reponse.get("error") or evenement.get("error") or {}
    incomplete = reponse.get("incomplete_details") or {}
    if isinstance(erreur, dict) and (erreur.get("code") or erreur.get("message")):
        raison = " : ".join(str(x) for x in (erreur.get("code"), erreur.get("message")) if x)
    elif incomplete.get("reason"):
        raison = "incomplète : " + str(incomplete["reason"])
    elif evenement.get("message") or evenement.get("code"):
        raison = " : ".join(str(x) for x in (evenement.get("code"), evenement.get("message")) if x)
    else:
        raison = "raison non précisée par l'API, peut-être une limite d'usage"
    if any(mot in raison.lower() for mot in ("rate", "quota", "limit", "usage")):
        raison += " ; vérifiez les limites du forfait dans ChatGPT > Paramètres > Utilisation"
    return raison[:300]


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
Une question n'autorise jamais une action physique : « puis-je allumer ? » doit clarifier ou
observer, pas allumer. Le joueur demandera ensuite l'action explicitement.
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
de Corvus est déjà affichée : ne la répète pas ; le personnage y répond d'après
conversation_validee.faits et ce qu'il croit (esprits_interlocuteurs). Réponds à son sujet avec ses savoirs
(connaissances_pnj), son profil, ses intentions et sa relation au joueur. Une liste
conversation_validee.faits vide signifie seulement qu'aucun accord n'a changé : le personnage
doit quand même répondre. Reprends exactement les montants, conditions et refus validés ; une
offre n'est pas un accord, un accord n'est pas un paiement. Un personnage absent ne parle pas.
Sinon, décris les faits enrichis déjà validés pour répondre au joueur, sans nouvel ajout ;
présente comme souvenirs les descriptions de personnages absents.
"""


SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ACTIONS},
        "cible": {"type": "string", "description": "Identifiant exact de la cible visible, direction, ou chaîne vide."},
        "outil": {"type": "string", "description": "Identifiant d'un outil possédé, ou chaîne vide. Pour remettre seulement : identifiant du PNJ destinataire."},
        "methode": {"type": "string", "enum": METHODES},
        "difficulte": {"type": "integer", "description": "0 hors détachement ; estimation entre 11 et 22 pour une fixation."},
        "justification": {"type": "string", "description": "Avis d'arbitrage bref ; ne décrire aucun résultat."},
    },
    "required": ["action", "cible", "outil", "methode", "difficulte", "justification"],
    "additionalProperties": False,
}


def retour_refus(proposition, exc, consigne):
    """Ce que la boucle de correction transmet au MJ : le refus, et ce que le moteur accepterait."""
    retour = {"proposition_refusee": proposition, "obstacle": str(exc), "consigne": consigne}
    if getattr(exc, "attendu", ""):
        retour["attendu"] = exc.attendu
    return retour


def expliquer_refus(premier, dernier):
    """Une proposition rejetée ne prouve rien sur les capacités de Corvus."""
    return "Je n'ai pas pu déterminer une manœuvre fidèle à ta demande. Corvus n'a rien tenté."


class MJOpenAI:
    def __init__(self, modele=None, effort="medium", timeout=45, connexion="api"):
        self.modele = modele or os.environ.get("OPENAI_MODEL", MODELE_PAR_DEFAUT)
        self.effort, self.timeout = effort, timeout
        self.derniere_utilisation = None
        self.connexion = connexion
        self.erreur_auth = None
        self.catalogue_verifie = False
        self.derniere_sortie = []
        self.observateur = None
        self._audit_courant = None
        self._monde_controle = None
        self.journal_complet = False   # trace entière de chaque appel (banc, essais de modèles)
        self.reflexion = "libre"       # Claude : réflexion adaptative (défaut), ou « imposee » : outil imposé, sans réflexion
        self.sans_strict = set()       # fonctions dont le schéma dépasse la grammaire stricte du fournisseur
        # Clé de session stable : elle aiguille les appels vers le même cache de prompt, si bien
        # que le préfixe commun (instructions, schéma, faits) n'est pas relu à chaque appel.
        import uuid
        self.cle_cache = str(uuid.uuid4())

    def proposer(self, monde, intention):
        return self._appeler(INSTRUCTIONS, {"monde": monde.contexte(), "intention": intention},
                             intention, "proposer_action", SCHEMA)

    def _auditer_action(self, intention, plan, revision):
        from .couverture_action import (SCHEMA as SCHEMA_COUVERTURE,
                                        INSTRUCTIONS as INSTRUCTIONS_COUVERTURE,
                                        RapportInvalide, entree as entree_couverture,
                                        verifier as verifier_couverture)
        for essai in range(2):
            rapport = self._appeler_brut(
                INSTRUCTIONS_COUVERTURE, entree_couverture(intention, plan),
                "Contrôler la fidélité du plan", "auditer_action", SCHEMA_COUVERTURE)
            if self.observateur:
                self.observateur({"etape": "couverture de l'action", "modele": self.modele,
                                  "revision": revision, "intention": intention,
                                  "rapport": copy.deepcopy(rapport)})
            try:
                verifier_couverture(rapport)
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
            reponse = self._echanger(monde, intention, proposition_en_attente, enrichir=True)
        correction_utilisee = False
        premier_refus = None
        for tentative in range(2):
            if reponse["mode"] != "action":
                break
            p = reponse["proposition"]
            try:
                from .moteur import Moteur
                if p.get("action") == "impossible":
                    if not correction_utilisee:
                        raise ErreurMonde("Réexamine l'intention entière et les possibilités du moteur avant de conclure qu'elle est impossible.")
                if p.get("action") in ("clarifier", "impossible"):
                    break
                if est_question(intention) and p.get("action") not in ("observer", "examiner"):
                    raise ErreurMonde("Le joueur pose une question de faisabilité. Réponds en dialogue sans exécuter d'action.",
                                      "mode dialogue : réponds à la question, sans proposition d'action.")
                plan = Moteur(monde).preparer(p, "MJ")
                if (premier_refus and not plan.effets and not plan.information
                        and not any(etape.effets or etape.information for etape in plan.plans)):
                    raise ErreurMonde("La proposition corrigée ne réalise aucun effet de la manœuvre demandée.",
                                      "garde les gestes de l'intention qui changent le monde ; si aucun n'est possible, "
                                      "réponds en dialogue sur l'obstacle.")
                self._auditer_action(intention, plan, revision)
                break
            except ErreurMonde as exc:
                dernier_refus = (p, str(exc))
                if premier_refus is None:
                    premier_refus = dernier_refus
                retour = retour_refus(p, exc, "Corrige uniquement la proposition, sans modifier les faits ni abandonner une partie de l'intention. Sinon explique l'obstacle en dialogue.")
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
                if correction_utilisee:
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
                correction_utilisee = True
                reponse = self._echanger(monde, intention, proposition_en_attente, enrichir=True, retour_moteur=retour)
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
            for essai in range(2):
                # Des mots cités par le joueur sont dits tels quels, sans réécriture.
                complements = {**reponse["proposition"],
                               "replique": (citation(intention)
                                            or (intention.strip() if destinataire_nomme(monde, intention) else None)
                                            or reponse["proposition"].get("replique", "")),
                               "_intention": intention[:600]}
                try:
                    travail, rapport = preparer_parole(monde, complements, revision)
                    break
                except ErreurMonde as exc:
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
            narration["_prefixe_moteur"] = "Tu dis : « " + rapport["replique_joueur"] + " »"
        return ajouter_transaction(narration, nature, revision, complements,
                                   rapport if reponse["mode"] in ("conversation_pnj", "parole_joueur") else None)

    def _echanger(self, monde, intention, proposition_en_attente, enrichir, conversation_validee=None, resultat_resolu=None, retour_moteur=None):
        contexte = monde.contexte()
        faits = {k: v for k, v in contexte.items() if k != "objets_perceptibles"}
        faits["attestations"] = attestations_narratives(monde, contexte)
        objets = contexte["objets_perceptibles"]
        if contexte["mode_cases"]:
            # Le MJ reçoit une seule localisation calculée, sans coordonnées ni ancien
            # identifiant de lieu répété dans chaque objet. Le moteur garde ces données.
            faits["joueur"]["salle"] = faits["salle"]["nom"]
            faits["joueur"].pop("position", None)
            faits.pop("lieux_connus", None)
            for sortie in faits["salle"]["sorties"].values():
                sortie.pop("vers", None)
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
            faits["attestations"].extend(conversation_validee.get("faits", []))
        if resultat_resolu is not None:
            faits["resultat_resolu"] = resultat_resolu
            faits["attestations"].extend(resultat_resolu.get("faits", []))
        social = enrichir and bool(faits["interlocuteurs"])
        paroles = contexte_paroles(monde)
        if paroles:
            # Chaque bloc que les règles nomment est un fait citable de premier niveau.
            faits.update(paroles)
        faits.update({"objet:" + o["id"]: o for o in objets})
        schema = {
            "type": "object", "additionalProperties": False,
            "properties": {
                "mode": {"type": "string", "enum": ["dialogue", "action"] + (["enrichir_joueur"] if profil_disponible else []) + (["enrichir"] if disponibles else []) + (["conversation_pnj", "parole_joueur"] if social else []) + (["enrichir_savoirs"] if savoirs_disponibles else []) + (["etablir_faits"] if any(faits_disponibles.values()) else [])},
                "texte": {"type": "string"},
                "faits": {"type": "array", "items": {"type": "string", "enum": list(faits)}},
                "proposition": {"anyOf": [SCHEMA, SCHEMA_SEQUENCE, {"type": "null"}] + ([SCHEMA_PROFIL] if profil_disponible else []) + ([SCHEMA_IMPROVISATION] if enrichir else []) + ([SCHEMA_FABRICATION] if atelier else []) + ([SCHEMA_COMPLEMENTS] if disponibles else []) + ([SCHEMA_CONVERSATION, SCHEMA_PAROLE] if social else []) + ([SCHEMA_SAVOIRS] if savoirs_disponibles else []) + ([SCHEMA_FAITS] if any(faits_disponibles.values()) else [])},
            },
            "required": ["mode", "texte", "faits", "proposition"],
        }
        instructions = INTERPRETATION
        if atelier and not est_question(intention):
            instructions += REGLES_ATELIER
        if franchissements:
            instructions += REGLES_FRANCHISSEMENT
        if enrichir and espace:
            instructions += REGLES_ESPACE
        if retour_moteur:
            instructions += ("\nLe retour_moteur est un contrôle fiable : corrige la proposition précédente, ou réponds en dialogue sur l'obstacle, sans exécuter autre chose."
                             "\nSon champ attendu, quand il existe, dit en champs et identifiants ce qu'une proposition corrigée "
                             "doit contenir : suis-le ; il ne s'adresse jamais au joueur.")
        if enrichir and social:
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
Le fait resultat_resolu contient exactement les événements survenus et la demande du joueur
(intention). Rédige une à trois phrases naturelles, non vides, avec les articles des objets.
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
(a_portee=false) appelle une invitation à s'approcher, car voir un objet ne suffit pas à le
manipuler. La vue s'arrête aux murs, aux portes fermées et à l'obscurité : à distance, Corvus
ne connaît ni les détails, ni ce qui est derrière un mur, et il ne se déplace que par ses pas.
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
            self._monde_controle = monde
            reponse = self._appeler(instructions, entree, intention, "repondre_au_joueur", schema)
            trace["reponse"] = copy.deepcopy(reponse)
        except ErreurMonde as exc:
            trace["erreur"] = str(exc)
            raise
        finally:
            self._monde_controle = None
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
            if not social or reponse["texte"] or not isinstance(reponse["proposition"], dict):
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
            for nom, texte, effets in passages:
                if not texte.strip():
                    # Rien à contrôler : l'audit d'un texte vide ne peut qu'échouer.
                    obstacles.append({"partie": nom, "segment": None, "texte": "",
                                      "motif": "Le texte est vide : écris dans texte la réponse destinée au joueur."})
                    continue
                obstacles.extend({"partie": nom, **o} for o in voix_auteur(texte))
                if monde is not None:
                    obstacles.extend({"partie": nom, **o} for o in mentions_narratives(monde, texte, base, paroles))
                faits = dict(entree.get("faits", {}))
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
                        rapport = controler_narration(texte, audit, faits)
                        break
                    except AuditIllisible as exc:
                        # Un rapport illisible ne juge pas le texte : l'audit est redemandé une
                        # fois ; ensuite le texte reste non contrôlé, donc refusé.
                        if essai:
                            obstacles.append({"partie": nom, "segment": None, "texte": texte,
                                              "motif": str(exc)})
                    except ErreurMonde as exc:
                        obstacles.append({"partie": nom, "segment": None, "texte": texte,
                                          "motif": str(exc)})
                        break
                if rapport is None:
                    continue
                audits[nom] = {**rapport, "faits": faits, "texte_initial": texte, "fondement": base,
                               "fondement_paroles": paroles}
                retour = faits.get("retour_moteur")
                if isinstance(retour, dict) and "propositions_refusees" in retour and rapport["paroles"]:
                    # Le motif d'un refus vient du moteur : aucun personnage ne le connaît ni ne le dit.
                    obstacles.append({"partie": nom, "segment": None, "texte": texte,
                                      "motif": "Une explication de refus raconte l'obstacle ; elle ne fait parler "
                                               "aucun personnage, qui n'en connaît pas la raison."})
                obstacles.extend({"partie": nom, **o} for o in rapport["obstacles"])
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
            except ErreurMonde as exc:
                obstacles.append({"partie": "description", "segment": None,
                                  "texte": "", "motif": str(exc)})
            try:
                qualifications = qualifications_proposees(reponse, entree.get("faits", {}))
                if qualifications:
                    audit = appeler_brut(INSTRUCTIONS_PHYSIQUE,
                                        {"qualifications": qualifications,
                                         "scenario": entree.get("faits", {}).get("scenario", {})},
                                        "Contrôler les capacités proposées",
                                        "auditer_capacites", SCHEMA_PHYSIQUE)
                    obstacles.extend(controler_physique(qualifications, audit))
            except ErreurMonde as exc:
                obstacles.append({"partie": "qualification", "segment": None,
                                  "texte": "", "motif": str(exc)})
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
                faits = entree.get("faits", {})
                resultat = faits.get("resultat_resolu", {})
                if isinstance(resultat, dict) and isinstance(resultat.get("faits"), list):
                    lignes = [s for s in resultat["faits"] if isinstance(s, str) and s.strip()]
                    if lignes:
                        return {"mode": "dialogue", "texte": " ".join(lignes),
                                "faits": ["resultat_resolu"], "proposition": None,
                                "_texte_moteur": True}
                return {"mode": "dialogue",
                        "texte": "Je ne peux pas encore répondre avec certitude.",
                        "faits": [], "proposition": None, "_texte_moteur": True}
            if self.observateur:
                self.observateur({"etape": "contrôle narratif", "modele": self.modele,
                                  "revision": entree.get("faits", {}).get("revision", 0),
                                  "intention": intention, "tentative": tentative + 1,
                                  "obstacles": copy.deepcopy(obstacles)})
            correction = {**entree, "controle_narratif": obstacles}
            reponse = appeler_brut(instructions + INSTRUCTIONS_REVISION, correction,
                                   intention, fonction, schema)
        raise ErreurMonde("Le contrôle narratif n'a pas abouti.")

    def _appeler_brut(self, instructions, entree, intention, fonction, schema):
        """Un appel au fournisseur. Avec ``journal_complet`` et un observateur, chaque appel laisse
        une trace entière : instructions, entrée, schéma, réponse brute, usage et durée."""
        if self.erreur_auth:
            raise ErreurMonde(self.erreur_auth)
        debut, brut, erreur = time.monotonic(), None, None
        self.dernier_brut = None
        try:
            if self.connexion == "anthropic":
                from .claude import appeler
                p, brut = appeler(self, instructions, entree, fonction, schema)
            else:
                p, brut = self._appeler_openai(instructions, entree, intention, fonction, schema)
            return p
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

    def _appeler_openai(self, instructions, entree, intention, fonction, schema):
        if self.erreur_auth:
            raise ErreurMonde(self.erreur_auth)
        if self.connexion == "chatgpt" and not self.catalogue_verifie:
            disponibles = modeles()
            if self.modele not in [m["slug"] for m in disponibles]:
                raise ErreurMonde("Ce modèle n'est pas disponible sur ce forfait. Lancez python connexion.py modeles, puis choisissez avec --model.")
            self.catalogue_verifie = True
        cle = jeton() if self.connexion == "chatgpt" else os.environ.get("OPENAI_API_KEY")
        if not cle:
            raise ErreurMonde("OPENAI_API_KEY absente. Les commandes hors ligne restent disponibles (aide).")
        if len(intention) > 2000:
            raise ErreurMonde("Limite ton action à 2 000 caractères.")
        payload = {
            "model": self.modele,
            "instructions": instructions,
            "input": [{"role": "user", "content": json.dumps(entree, ensure_ascii=False)}],
            "tools": [{"type": "function", "name": fonction,
                       "description": "Répond au joueur ou soumet une manœuvre au moteur, sans modifier le monde.",
                       "parameters": schema, "strict": True}],
            "tool_choice": {"type": "function", "name": fonction},
            "parallel_tool_calls": False,
            "reasoning": {"effort": self.effort},
            "max_output_tokens": 3000,
            "store": False,
        }
        if self.cle_cache:
            payload["prompt_cache_key"] = self.cle_cache
        if self.connexion == "chatgpt":
            outil = payload["tools"][0]
            payload["tools"] = [{"type": "namespace", "name": "donjon",
                                 "description": "Proposer une action ou une observation au moteur.",
                                 "tools": [outil]}]
            payload["tool_choice"] = "required"
            payload["stream"] = True
            payload.pop("max_output_tokens")  # non accepté par le contrat Sign in with ChatGPT
        requete = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + cle, "Content-Type": "application/json",
                     **({"session_id": self.cle_cache} if self.cle_cache else {})},
            method="POST",
        )
        try:
            with urllib.request.urlopen(requete, timeout=self.timeout) as reponse:
                resultat = lire_flux(reponse) if self.connexion == "chatgpt" else json.load(reponse)
        except urllib.error.HTTPError as exc:
            # Ne jamais afficher les en-têtes ou une clé dans le journal.
            try:
                code = json.loads(exc.read()).get("error", {}).get("code", "erreur_api")
            except (ValueError, AttributeError):
                code = "erreur_api"
            status = exc.code
            exc.close()
            if status == 401:
                conseil = ("Reconnectez le forfait : python connexion.py connecter, puis relancez le jeu."
                           if self.connexion == "chatgpt" else
                           "La clé API est refusée. Remplacez-la localement, ou utilisez python connexion.py connecter pour le forfait ChatGPT.")
                self.erreur_auth = "MJ déconnecté : " + conseil + " Aucun nouvel appel ne sera tenté dans cette session."
                raise ErreurMonde(self.erreur_auth) from None
            raise ErreurMonde(f"MJ indisponible : HTTP {status} ({code}). "
                              "Monde inchangé ; utilisez contexte, lumière, regarder ou journal.") from None
        except ErreurMonde:
            raise
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise ErreurMonde("Le MJ n'a pas répondu correctement (réseau ou délai). "
                              "Aucune action appliquée. Réessayez ou utilisez les commandes locales.") from None
        if not isinstance(resultat, dict) or not isinstance(resultat.get("output"), list):
            raise ErreurMonde("Réponse du MJ mal formée. Aucune action appliquée.")
        self.derniere_utilisation = resultat.get("usage")
        if resultat.get("status") != "completed":
            raise ErreurMonde("Réponse du MJ incomplète. Aucune action appliquée.")
        self.derniere_sortie = [{k: item.get(k) for k in ("type", "name", "namespace", "status")}
                               for item in resultat["output"] if isinstance(item, dict)]
        if not self.derniere_sortie:
            self.derniere_sortie = [{"types_evenements": resultat.get("_types_evenements", [])}]
        appels = [item for item in resultat["output"] if isinstance(item, dict) and item.get("type") == "function_call"]
        if len(appels) != 1 or appels[0].get("name") != fonction:
            raise ErreurMonde("Le MJ n'a pas fourni une proposition unique. Aucune action appliquée.")
        try:
            p = json.loads(appels[0]["arguments"])
            if not isinstance(p, dict):
                raise ValueError("La proposition doit être un objet")
            return p, resultat["output"]
        except (ValueError, KeyError, TypeError):
            raise ErreurMonde("Proposition du MJ illisible. Aucune action appliquée.") from None
