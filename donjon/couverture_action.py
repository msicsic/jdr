"""Contre-revue de la fidélité d'une proposition à la demande du joueur.

Le moteur valide les effets possibles ; cette revue vérifie que le plan ne perd pas
une partie observable de l'intention. Son avis ne modifie jamais le monde.
"""

from .monde import ErreurMonde
from .refus import RapportIllisible, attendu_audit


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
Les opérations désignent chaque chose par « nom (identifiant) » : le nom est celui que le joueur
emploie, l'identifiant n'est qu'une étiquette technique.
Le plan représente l'état du monde : action, cibles, outil, et changements durables
(objet déplacé, détaché, allumé, marqué, son émis, blessure, usure). La manière du geste
(position des mains, style, intention affichée, caractère d'un son ou d'un air) relève du
récit et n'a pas à figurer dans les opérations ; l'outil et la méthode la portent déjà.
Une question sur la faisabilité d'un geste (« puis-je… ? ») se juge comme la demande de ce geste.
Réponds conforme=false seulement pour un écart d'état net :
- une action ou une cible différente de celle demandée ;
- un changement durable demandé qu'aucune opération ne produit ;
- un changement durable ajouté que le joueur n'a pas demandé.
Une action sans changement durable est conforme si le geste suffit à la demande. Chercher,
fouiller ou inspecter quelque chose (du regard, de l'oreille, des mains) se fait par une action de
perception (examiner, toucher, ecouter, observer, lire) sur ce qu'on fouille : ce qu'elle révèle, ou
ne révèle pas, est le résultat que le moteur décide, et elle couvre la demande. Un geste
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



def _nommer(valeur, monde):
    """Un identifiant devient « nom (identifiant) » : un identifiant nu (« marchand ») se lit
    comme un mot et ne désigne plus le personnage que le joueur nomme (« Gorm »)."""
    if isinstance(valeur, str) and valeur in monde.objets:
        from .noms import public, reference
        return f"{public(monde,monde.objets[valeur]['nom'])} ({reference(monde,valeur)})"
    if isinstance(valeur, (list, tuple)):
        return [_nommer(v, monde) for v in valeur]
    if isinstance(valeur,dict):
        return {k:_nommer(v,monde) for k,v in valeur.items()}
    return valeur


def entree(intention, plan, monde=None):
    """La demande et les opérations du plan, chaque identifiant cité accompagné de son nom."""
    operations = _operations(plan)
    if monde is not None:
        def nommer_plan(op):
            return {**op, **{cle: _nommer(op[cle], monde) for cle in ("effets_reussite", "effets_echec")},
                    "etapes": [nommer_plan(e) for e in op["etapes"]],
                    **({"geste_improvise": {**op["geste_improvise"],
                                            "cibles": _nommer(op["geste_improvise"]["cibles"], monde),
                                            "outil": _nommer(op["geste_improvise"]["outil"], monde)}}
                       if "geste_improvise" in op else {})}
        operations = nommer_plan(operations)
    return {"demande": intention, "plan": operations}


MOTIF_MAX = 300


class RapportInvalide(RapportIllisible):
    """Le rapport de la revue est mal formé : une faute de l'auditeur, pas de la proposition."""


def verifier(rapport, plan=None):
    """Le verdict de la contre-revue. Non conforme : un refus dont ``attendu`` (``refus.attendu_audit``)
    cite le plan reçu, le motif de la revue tel quel, et ce qui serait accepté."""
    if (not isinstance(rapport, dict) or set(rapport) != {"conforme", "motif"}
            or type(rapport["conforme"]) is not bool or not isinstance(rapport["motif"], str)):
        raise RapportInvalide("La contre-revue de la manœuvre est invalide.")
    if not rapport["conforme"]:
        # Le motif n'est qu'une explication transmise au MJ : un motif trop long est abrégé.
        motif = rapport["motif"].strip()
        if len(motif) > MOTIF_MAX:
            motif = motif[:MOTIF_MAX - 1].rstrip() + "…"
        recu = ""
        if plan is not None:
            p = plan.proposition if isinstance(plan.proposition, dict) else {}
            cibles = p.get("cible") or ", ".join(map(str, p.get("cibles") or []))
            recu = f"{plan.titre} (action {p.get('action')}" + (f", cible {cibles}" if cibles else "") + ")"
        raise ErreurMonde("La manœuvre proposée ne couvre pas la demande : " +
                          (motif or "une conséquence demandée manque."),
                          attendu_audit("proposition", recu or "le plan proposé",
                                        "le même geste, dont les changements durables sont ceux de la demande : "
                                        "retire celui qu'elle ne demande pas, ou ajoute l'étape qui manque",
                                        ("non conforme", motif)))
