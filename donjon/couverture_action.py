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
Le plan représente l'état du monde : action, cibles, outil, et changements durables
(objet déplacé, détaché, allumé, marqué, son émis, blessure, usure). La manière du geste
(position des mains, style, intention affichée, caractère d'un son ou d'un air) relève du
récit et n'a pas à figurer dans les opérations ; l'outil et la méthode la portent déjà.
Réponds conforme=false seulement pour un écart d'état net :
- une action ou une cible différente de celle demandée ;
- un changement durable demandé qu'aucune opération ne produit ;
- un changement durable ajouté que le joueur n'a pas demandé.
Une action sans changement durable est conforme si le geste suffit à la demande. Un geste
improvisé (geste_improvise) accomplit le geste demandé sur ses cibles : sa forme (coup de
pied, poussée, caresse, air sifflé) relève du récit ; juge seulement ses changements durables.
N'exige ni résultat incertain, ni réaction d'un tiers, ni effet non demandé.
La branche d'échec d'un jet peut ne pas atteindre le but ; juge sa cohérence avec le risque.
En cas de doute, réponds conforme=true : le moteur garde l'autorité sur chaque effet.
Le motif désigne seulement l'écart d'état, sans inventer un fait du monde.
Appelle auditer_action une fois.
"""


def _operations(plan):
    improvise = plan.proposition.get("action") == "improviser"
    return {
        "titre": plan.titre,
        **({"geste_improvise": {"approche": plan.proposition.get("approche"),
                                "cibles": plan.proposition.get("cibles", []),
                                "outil": plan.proposition.get("outil", "")}} if improvise else {}),
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
