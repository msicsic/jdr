"""Compilation du libre : contexte public, contrats typés, aucune réparation de sens.

Les propositions restent celles du moteur actuel. La compilation n'admet ni
effet ni texte : les validateurs et les revues de MJ restent leurs propriétaires.
"""
import copy

from .sources import ordonner_entree
from .paroles import SCHEMA_PAROLE, SCHEMA_OPERATIONS, section_contenu


def schema_compilateur():
    # Imports différés : mj définit encore le contrat des actions simples.
    from .mj import SCHEMA
    from .moteur import SENS_PERCEPTIONS, SENS_CONSULTATIONS
    from .operations import SCHEMA_SEQUENCE
    from .artisanat import SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE
    from .improvisation import schema_proposition
    improvisation = schema_proposition()
    from .dialogues import SCHEMA_CONVERSATION
    from .faits_locaux import SCHEMA_FAITS
    from .enrichissement import SCHEMA_COMPLEMENTS
    from .connaissances import SCHEMA_SAVOIRS
    from .profil_joueur import SCHEMA as profil
    geste = copy.deepcopy(SCHEMA)
    geste["properties"]["action"]["enum"] = [
        a for a in geste["properties"]["action"]["enum"] if a not in ("clarifier", "impossible")]
    faits = copy.deepcopy(SCHEMA_FAITS)
    faits["properties"]["suite"] = {"anyOf": [geste, SCHEMA_SEQUENCE,
        improvisation, SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE, {"type": "null"}]}
    faits["required"].append("suite")
    parole = copy.deepcopy(SCHEMA_PAROLE)
    parole["properties"] = {"operations_demandees": copy.deepcopy(SCHEMA_OPERATIONS),
                             **parole["properties"]}
    parole["required"].insert(0, "operations_demandees")
    simple = copy.deepcopy(SCHEMA)
    simple["properties"]["action"]["description"] = " ".join(f"{op} : {sens}" for op, sens in (SENS_PERCEPTIONS | SENS_CONSULTATIONS).items())
    return {"type": "object", "additionalProperties": False, "properties": {
        "mode": {"type": "string", "enum": ["action", "parole_joueur", "conversation_pnj",
            "etablir_faits", "enrichir", "enrichir_savoirs", "enrichir_joueur", "dialogue"],
            "description": "dialogue : question d'information au MJ sur ce qui est perçu, connu ou déjà lu, sans nouvel acte ni parole. action : geste demandé ou question de faisabilité. parole_joueur : le joueur fait parler Corvus (adresse, guillemets, verbe de parole) ; la présence d'un interlocuteur ou d'une parole_prevue possible ne suffit pas à transformer une question au MJ en parole. conversation_pnj : opération de mission configurée, avant la parole libre."},
        "texte": {"type": "string", "description": "Réponse finale non vide au joueur en dialogue ; jamais analyse du choix de mode. Vide pour les propositions typées."},
        "faits": {"type": "array", "items": {"type": "string"}},
        "proposition": {"anyOf": [simple, SCHEMA_SEQUENCE, improvisation,
            SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE, SCHEMA_CONVERSATION, parole, faits,
            SCHEMA_COMPLEMENTS, SCHEMA_SAVOIRS, profil, {"type": "null"}]}},
        "required": ["mode", "texte", "faits", "proposition"]}


PROMPT_COMPILATEUR = """Tu es le compilateur d'intention de LE SEUIL.
Traduis la saisie en une proposition typée du schéma. Le moteur décide de sa
validité et de ses conséquences. Un appel nominal, aucune réalisation racontée.
Utilise les références publiques exactes du contexte, jamais un identifiant deviné.
Un souvenir ou un nom connu ne prouve ni présence, ni accès actuel.
Préserve toutes les clauses, étapes, cibles, moyens et montants de l'intention.
Une question de faisabilité propose le geste, sans l'exécuter ni inventer son résultat.
Pour une proposition, texte est vide et faits est une liste de clés du contexte.

mode action : action simple, composer (étapes ordonnées), improviser, assembler,
decouper. Le schéma du moteur fixe leurs champs, sans les détourner.
observer vise scene, lumiere, contexte ou un personnage ; examiner, toucher et
lire visent un objet. ecouter n'a pas de cible. aller/marcher/faufiler/chasser
et tourner ont une direction ; attendre peut préciser une durée en secondes.
L'action faufiler est le pas feutré ; chasser garde le regard pendant le pas.
prendre/poser/acheter/ouvrir/fermer/allumer/eteindre visent l'objet exact.
deverrouiller/verrouiller/crocheter/couper/detacher/bloquer/copier indiquent
l'outil porté ; detacher précise la méthode et sa difficulté proposée.
frapper : methode simple ou assommer, outil arme portée ou vide (mains nues).
saisir/pousser/ligoter/delier/trainer/tuer/ranimer ciblent le personnage.
pousser et trainer ont une direction dans outil ; ligoter y indique le lien.
remettre a pour cible l'objet et pour outil le destinataire.
Une suite de gestes passe par composer, avec les opérations exactes du schéma.
Une émission sonore passe par improviser ou composer/emettre_son.
L'atelier et les franchissements donnent les ressources et contraintes publiques.

mode parole_joueur : Corvus parle, sans effectuer le geste qu'il annonce.
Replique au discours direct dans sa bande d'expression, mots imposés conservés.
personnage suit parole_prevue. Analyser operations_demandees depuis la saisie,
puis fournir tous les actes de contenu correspondants. propos ne remplace pas
une opération disponible, même pour une phrase déclarative, négative ou incertaine.

mode conversation_pnj : opérations sur une mission configurée et son offre.
personnage est le donneur public, mission son identifiant, sujet la demande.
prix consulte la prime sans proposition ; proposer présente l'offre de base ; negocier soumet un montant positif ; accepter ou refuser
porte sur l'offre ; discuter n'engage rien (mission vide, montant_demande 0).
La négociation d'une mission relève de ce contrat, y compris sous forme de parole.
Un marché libre utilise parole_joueur/contenu proposition avec ses deux termes.

mode etablir_faits : ajouts typés autorisés par faits_narratifs_proposables ; suite
porte le geste demandé, préparé seulement après admission. Une qualification
manquante n'autorise pas à inventer une propriété favorable.
enrichir, enrichir_savoirs, enrichir_joueur : seulement les catalogues autorisés.
mode dialogue : question au MJ, perception ou clarification ; aucun effet ni
parole nouvelle. Ne remplace pas une intention exprimable par un dialogue vague.
clarifier/impossible sont des avis contrôlés, jamais un moyen d'éviter de proposer
une action existante au premier essai. Un verrou ou une distance est jugé par le moteur.
retour_moteur contient proposition_refusee et attendu : corrige la même intention
sans effacer une clause. Aucun récit de refus ni explication mécanique inventée.
"""


def prompt_compilateur(fournisseur):
    return (PROMPT_COMPILATEUR + ("\nLes variantes de contenu du schéma définissent les actes de parole."
            if getattr(fournisseur, "schema_lu", True) else "\n" + section_contenu()))


# La projection amont porte l'autorité de perception. Garder ses propriétés
# mécaniques (y compris celles qu'ajoutera le moteur), enlever seulement la
# prose destinée au narrateur et les coordonnées remplacées par localisation.
CHAMPS_OBJET_OMIS = frozenset(("portrait", "description_visuelle", "maniere_de_parler",
    "facettes", "position", "position_salle", "case_percue"))


def extraire_contexte(monde, intention="", *, faits=None):
    """Sélection d'une projection publique existante, jamais de parcours du monde privé.

    Les catalogues d'admission sont conservés : réduire le contexte ne signifie
    pas rendre inexprimable un acte valide. Les contrôleurs gardent le dossier
    complet côté moteur, notamment pour auditer la prose transitoire.
    """
    from .noms import public
    from .paroles import analyser
    from .commandes import faisabilite
    if faits is None:
        from . import paroles
        faits = monde.contexte()
        faits.update(paroles.contexte(monde, intention) or {})
        faits.update({"objet:" + o["id"]: o for o in faits.pop("objets_perceptibles")})
    cles = ("salle", "joueur", "mode_cases", "personnages_connus", "noms_entendus",
        "lieux_connus", "souvenirs_visuels", "souvenirs_personnages", "souvenirs_faits",
        "missions_discutables", "engagements", "comptes", "interlocuteurs", "parole_prevue",
        "expression_joueur", "echanges_passes", "proposition_en_attente", "derniere_tentative",
        "atelier", "franchissements", "passages_obstacles", "espace", "improvisation",
        "descriptions_a_completer", "connaissances_a_completer", "profil_joueur_a_completer",
        "faits_narratifs_proposables", "ambiance_ciblee", "retour_moteur",
        "scenario", "attestations", "evenements_recents", "paroles_entendues", "ambiance_etablie")
    ctx = {k: copy.deepcopy(faits[k]) for k in cles if k in faits}
    forme = analyser(monde, intention)
    ctx["saisie"] = {"parole_explicite": bool(forme["explicite"]),
                     "interlocuteur_nomme": bool(forme.get("nomme") or forme.get("groupe")),
                     "question_faisabilite": bool(faisabilite(intention))}
    # La salle garde ses sorties connues et leur état, pas la description d'auteur.
    ctx["salle"] = {k: v for k, v in ctx.get("salle", {}).items()
                    if k in ("id", "nom", "sorties", "sorties_connues", "eau")}
    ctx["joueur"] = {k: v for k, v in ctx.get("joueur", {}).items()
                     if k in ("nom", "or", "corps", "promesses", "dangers_percus", "salle", "orientation")}
    ctx["interlocuteurs"] = {ref: {k: v for k, v in p.items()
        if k in ("nom", "voix_inconnue", "personne_inconnue", "entendue", "genre")}
        for ref, p in ctx.get("interlocuteurs", {}).items()}
    # Le niveau d'éclairage est public, pas l'identité de ses sources invisibles.
    ctx["perception"] = {k: copy.deepcopy(v) for k, v in faits.get("perception", {}).items()
                         if k in ("niveau", "etat", "objets_visibles", "couverture_vue", "non_vus_connus")}
    for cle, o in faits.items():
        if cle.startswith("objet:"):
            ctx[cle] = {k: copy.deepcopy(v) for k, v in o.items() if k not in CHAMPS_OBJET_OMIS}
    return public(monde, ctx)


def normaliser_proposition(proposition, monde=None, intention=""):
    """Copie structurelle uniquement ; aucune cible, méthode ou clause déduite."""
    return copy.deepcopy(proposition)


def compiler(appeler, fournisseur, entree, intention, schema):
    """Un appel nominal ; les corrections et audits restent dans MJ."""
    # Nom de transport historique conservé pour les fournisseurs et les fils
    # rejouables ; la voie de cache distingue explicitement la compilation.
    return normaliser_proposition(appeler(prompt_compilateur(fournisseur),
        ordonner_entree({**entree, "compilation": True}), intention, "repondre_au_joueur", schema))


SCHEMA_COMPILATEUR = schema_compilateur()
