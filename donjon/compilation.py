"""Contrat du compilateur libre forme A, commun au nominal et à ses reprises.

Les familles portées et les charges transitoires restent exposées ensemble.
Aucune sélection d'opération, de mode ou de contexte selon le texte du joueur.
"""
import copy

from .moteur import ACTIONS, METHODES
from .enrichissement import SCHEMA_COMPLEMENTS
from .faits_locaux import SCHEMA_FAITS
from .dialogues import SCHEMA_CONVERSATION
from .paroles import SCHEMA_PAROLE
from .connaissances import SCHEMA_SAVOIRS
from .operations import SCHEMA_SEQUENCE
from .fournisseurs.contrat import lier_modes
from .contrats_sequence import schemas_actions
from .contrats_passage import schemas as schemas_passages
from .improvisation import SCHEMA as SCHEMA_IMPROVISATION
from .profil_joueur import SCHEMA as SCHEMA_PROFIL
from .artisanat import SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE


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

# Les familles attente et passage portent leurs contraintes ; les autres actions restent sur
# leur contrat transitoire. Aucune sélection selon la saisie ou le scénario.
SCHEMA = copy.deepcopy(SCHEMA)  # les enums initiaux référencent aussi les listes du moteur
SCHEMAS_PASSAGE = schemas_passages(SCHEMA, "action", ("franchir", "pousser"))
for _action in ("franchir", "pousser"):
    SCHEMA["properties"]["action"]["enum"].remove(_action)
SCHEMA, SCHEMA_ATTENTE = schemas_actions(SCHEMA)
SCHEMA_PROPOSER = {"anyOf": [SCHEMA, *SCHEMAS_PASSAGE, SCHEMA_ATTENTE]}


def schema_reponse(*, enrichir=True):
    """Même grammaire complète pour chaque proposition libre et correction."""
    schema_faits_suite = copy.deepcopy(SCHEMA_FAITS)
    schema_geste = copy.deepcopy(SCHEMA)
    schema_geste["properties"]["action"]["enum"] = [
        a for a in schema_geste["properties"]["action"]["enum"] if a not in ("clarifier", "impossible")]
    schema_faits_suite["properties"]["suite"] = {
        "description": "Le geste demandé, à préparer après validation des ajouts, sans supposer leur acceptation.",
        "anyOf": [schema_geste, *SCHEMAS_PASSAGE, SCHEMA_ATTENTE, SCHEMA_SEQUENCE, SCHEMA_IMPROVISATION, SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE, {"type": "null"}]}
    schema_faits_suite["required"].append("suite")
    from .paroles import SCHEMA_OPERATIONS
    schema_parole = copy.deepcopy(SCHEMA_PAROLE)
    # Le protocole du MJ ne propose plus de date à exécuter. Le contrat
    # moteur E4 reste disponible au choix direct, et les anciennes réponses
    # datées sont interceptées avant leur préparation puis au rejeu U-C.
    for contenu in schema_parole['properties']['contenu']['items']['anyOf']:
        if contenu['properties']['type']['enum'] == ['proposition']:
            for nom in ('demande', 'contrepartie'):
                contenu['properties'][nom]['anyOf'] = [t for t in contenu['properties'][nom]['anyOf']
                                                        if 'limite' not in t['properties']]
    # L'analyse de la saisie précède le choix du contenu : elle ne doit pas
    # être une justification a posteriori des seuls types déjà proposés.
    schema_parole["properties"] = {"operations_demandees": SCHEMA_OPERATIONS,
                                   **schema_parole["properties"]}
    schema_parole["required"] = ["operations_demandees", *schema_parole["required"]]
    from .accords_libres import SCHEMA as SCHEMA_ACCORD
    schema = {
        "type": "object", "additionalProperties": False,
        "properties": {
            "mode": {"type": "string", "enum": ["dialogue", "action", "enrichir_joueur", "enrichir",
                                                   "conversation_pnj", "parole_joueur", "enrichir_savoirs", "etablir_faits", "accord"]},
            "texte": {"type": "string"},
            "faits": {"type": "array", "items": {"type": "string"}},
            "proposition": {"anyOf": [SCHEMA, *SCHEMAS_PASSAGE, SCHEMA_ATTENTE, SCHEMA_SEQUENCE, {"type": "null"}, SCHEMA_PROFIL,
                                      SCHEMA_IMPROVISATION, SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE,
                                      SCHEMA_COMPLEMENTS, SCHEMA_CONVERSATION, schema_parole,
                                      SCHEMA_SAVOIRS, schema_faits_suite, SCHEMA_ACCORD]},
        },
        "required": ["mode", "texte", "faits", "proposition"],
    }
    if not enrichir:
        schema["properties"]["mode"] = {"type": "string", "enum": ["dialogue"]}
        schema["properties"]["texte"] = {"type": "string", "minLength": 1,
                                            "description": "Réponse finale non vide destinée au joueur."}
        schema["properties"]["proposition"] = {"type": "null"}
    schema = lier_modes(schema, {
        "dialogue": {"type": "null"},
        "action": {"anyOf": [SCHEMA, *SCHEMAS_PASSAGE, SCHEMA_ATTENTE, SCHEMA_SEQUENCE,
                              SCHEMA_IMPROVISATION, SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE]},
        "enrichir_joueur": SCHEMA_PROFIL, "enrichir": SCHEMA_COMPLEMENTS,
        "conversation_pnj": SCHEMA_CONVERSATION, "parole_joueur": schema_parole,
        "enrichir_savoirs": SCHEMA_SAVOIRS, "etablir_faits": schema_faits_suite,
        "accord": SCHEMA_ACCORD,
    })
    return schema
