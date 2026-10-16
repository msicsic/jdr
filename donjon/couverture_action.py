"""Contre-revue de la fidélité d'une proposition à la demande du joueur.

Le moteur valide les effets possibles ; cette revue vérifie que le plan ne perd pas
une partie observable de l'intention. Son avis ne modifie jamais le monde.
"""

from .monde import ErreurMonde


SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "conforme": {"type": "boolean"},
        "motif": {"type": "string"},
    },
    "required": ["conforme", "motif"],
}

INSTRUCTIONS = """Tu fais une contre-revue indépendante d'un plan de jeu déjà validé mécaniquement.
Compare la demande entière du joueur aux opérations que le moteur exécutera vraiment.
Signale une action différente, une étape omise ou une conséquence perceptible nécessaire
à l'action demandée qui n'est représentée par aucune opération. Le titre, le récit et
l'enregistrement générique d'un geste ne créent pas à eux seuls une conséquence physique.
Une action sans changement durable peut être conforme si le geste suffit à la demande.
N'exige ni résultat incertain, ni réaction d'un tiers, ni effet non demandé.
La branche d'échec d'un jet peut ne pas atteindre le but ; juge sa cohérence avec le risque.
Réponds conforme=false en cas de doute sérieux. Le motif désigne seulement l'écart
entre demande et plan, sans inventer un fait du monde. Appelle auditer_action une fois.
"""


def _operations(plan):
    return {
        "titre": plan.titre,
        "effets_reussite": [list(e) for e in plan.effets if e[0] != "recit_improvise"],
        "effets_echec": [list(e) for e in plan.echec if e[0] != "recit_improvise"],
        "information": plan.information,
        "jet": bool(plan.stat),
        "etapes": [_operations(etape) for etape in plan.plans],
    }


def entree(intention, plan):
    return {"demande": intention, "plan": _operations(plan)}


def verifier(rapport):
    if (not isinstance(rapport, dict) or set(rapport) != {"conforme", "motif"}
            or type(rapport["conforme"]) is not bool
            or not isinstance(rapport["motif"], str) or len(rapport["motif"]) > 300):
        raise ErreurMonde("La contre-revue de la manœuvre est invalide.")
    if not rapport["conforme"]:
        raise ErreurMonde("La manœuvre proposée ne couvre pas la demande : " +
                          (rapport["motif"].strip() or "une conséquence demandée manque."))
