"""Contre-revue de la fidélité d'une proposition à la demande du joueur.

Le moteur valide les effets possibles ; cette revue vérifie que le plan ne perd pas
une partie observable de l'intention. Son avis ne modifie jamais le monde.
"""

import json

from .monde import ErreurMonde
from .refus import RapportIllisible, attendu_audit
from .noms import REGLE_DESIGNATIONS, reperes_designations
from .paroles import SENS_CONTENU, operations_contenu


SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "conforme": {"type": "boolean"},
        "motif": {"type": "string"},
    },
    "required": ["conforme", "motif"],
}

# L'adresse est fixée par le moteur avant la revue ; seul le sens du contenu
# reste à contrôler ici.
SCHEMA_PAROLE = {
    "type": "object", "additionalProperties": False,
    "properties": {"contenu_conforme": {"type": "boolean"}, "motif": {"type": "string"},
        "operations_demandees": {"type": "array", "items": {
            "type": "string", "enum": [t for t in SENS_CONTENU if t != "propos"]},
            "description": "Analyse de la saisie du joueur seule, indépendamment du contenu proposé et de son verdict : opérations qu'elle demande au moteur de trancher. Une parole ordinaire sans opération donne []. Un échange demandé exige proposition, y compris pour un achat. Sens des opérations : "
                + " ".join(f"{t} : {s}" for t, s in SENS_CONTENU.items() if t != "propos")}},
    "required": ["contenu_conforme", "motif", "operations_demandees"],
}


SCHEMA_RAPPORT = {"type": "object", "additionalProperties": False,
    "properties": {"rapport": {"anyOf": [SCHEMA, SCHEMA_PAROLE]}}, "required": ["rapport"]}


def schema(plan=None):
    return SCHEMA_RAPPORT

INSTRUCTIONS = """Tu fais une contre-revue indépendante d'un plan de jeu déjà validé mécaniquement.
Compare la demande entière du joueur aux opérations que le moteur exécutera vraiment.
Le champ parole est le dossier de contenu d'une parole préparée : replique, contenu et
sens_contenu. Compare ces mots et ce contenu à la demande du joueur avant enregistrement.
L'adresse, les auditeurs et les effets mécaniques sont fixés et validés séparément par le
moteur ; ils ne font pas partie de ce dossier ni du sens à contrôler. contenu décrit ce
qui est demandé ou affirmé, pas les opérations de transfert ou de paiement à exécuter.
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
Le champ perception est une opération déclarée par le moteur, même si information et les effets
sont vides : son résultat ne sera calculé qu'à l'exécution. Elle est un geste complet ;
juge sa fidélité à la demande et à sa cible, sans exiger un effet durable ni anticiper son résultat.
Une action sans changement durable est conforme si le geste suffit à la demande. Chercher,
fouiller ou inspecter quelque chose (du regard, de l'oreille, des mains) se fait par une action de
perception sur ce qu'on fouille, ou sur place si l'opération n'a pas de cible : ce qu'elle révèle, ou
ne révèle pas, est le résultat que le moteur décide, et elle couvre la demande. Face à un
agresseur que le titre du plan nomme (« qui t'a agressé »), se défendre se fait en ripostant (le
frapper), en fuyant, en se dégageant ou en se rendant : la cible de cette réaction est cet agresseur,
que le moteur fixe seul quand la demande ne le nomme pas ; ce n'est ni une cible ni une action ajoutée. Un geste
improvisé (geste_improvise) accomplit un geste sur ses cibles : sa forme (coup de
pied, poussée, caresse, air sifflé) relève du récit ; juge seulement ses changements durables.
Il ne déplace pas Corvus : un déplacement demandé exige une opération qui le produit.
N'exige ni résultat incertain, ni réaction d'un tiers, ni effet non demandé.
La branche d'échec d'un jet peut ne pas atteindre le but ; juge sa cohérence avec le risque.
En cas de doute, réponds conforme=true : le moteur garde l'autorité sur chaque effet.
Le motif désigne seulement l'écart d'état, sans inventer un fait du monde.
Pour un plan de parole, rends contenu_conforme : les mots et le contenu typé traduisent-ils
la demande ? Un contenu vide ou propos n'attribue aucun effet mécanique aux mots ; il n'est
pas infidèle par son seul manque de typage. Juge les mots et les effets des seuls contenus
typés présents, sans exiger d'en inventer un pour toute question. Ne juge dans ce booléen ni l'audience fixée par le moteur, ni les conséquences
qu'il a calculées. Pour les autres plans, rends conforme et motif.
Rends le jugement dans rapport. Appelle auditer_action une fois.
"""


INSTRUCTIONS += "\n" + REGLE_DESIGNATIONS


def _operations(plan):
    improvise = plan.proposition.get("action") == "improviser"
    return {
        "titre": plan.titre,
        **({"perception": plan.perception} if plan.perception is not None else {}),
        **({"parole": plan.parole} if plan.parole is not None else {}),
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
        def nommer_parole(p):
            # Les références sont nommées, les mots libres restent littéraux.
            def nommer_contenu(c):
                if c.get("type") == "proposition":
                    return {**c, **{champ: {**c[champ], "objet": _nommer(c[champ]["objet"], monde)}
                                    for champ in ("demande", "contrepartie")
                                    if "objet" in c[champ]}}
                return {**c, **{k: _nommer(c[k], monde) for k in ("sujet", "valeur")
                               if k in c and c.get("type") != "ressource"}}
            return {**p, "contenu": [nommer_contenu(c) for c in p.get("contenu", [])]}
        def nommer_plan(op):
            return {**op, **{cle: _nommer(op[cle], monde) for cle in ("effets_reussite", "effets_echec")},
                    **({"perception": {**op["perception"], "cible": _nommer(op["perception"]["cible"], monde)}}
                       if "perception" in op else {}),
                    **({"parole": nommer_parole(op["parole"])} if "parole" in op else {}),
                    "etapes": [nommer_plan(e) for e in op["etapes"]],
                    **({"geste_improvise": {**op["geste_improvise"],
                                            "cibles": _nommer(op["geste_improvise"]["cibles"], monde),
                                            "outil": _nommer(op["geste_improvise"]["outil"], monde)}}
                       if "geste_improvise" in op else {})}
        operations = nommer_plan(operations)
    entree_ = {"demande": intention, "plan": operations}
    if monde is not None:
        from .noms import public
        # Seulement ce que le joueur peut désigner ; jamais le lexique privé du monde.
        contexte = public(monde, monde.contexte())
        faits = {"objet:" + o["id"]: o for o in contexte["objets_perceptibles"]}
        faits["interlocuteurs"] = contexte["interlocuteurs"]
        entree_["designations"] = reperes_designations(intention, faits) + reperes_designations(
            json.dumps(operations, ensure_ascii=False), faits)
    return entree_


MOTIF_MAX = 300


class RapportInvalide(RapportIllisible):
    """Le rapport de la revue est mal formé : une faute de l'auditeur, pas de la proposition."""


def verifier(rapport, plan=None, operations_demandees=None):
    """Le verdict de la contre-revue. Non conforme : un refus dont ``attendu`` (``refus.attendu_audit``)
    cite le plan reçu, le motif de la revue tel quel, et ce qui serait accepté."""
    if isinstance(rapport, dict) and set(rapport) == {"rapport"}:
        rapport = rapport["rapport"]
    if plan is not None and plan.parole is not None:
        if (not isinstance(rapport, dict)
                or set(rapport) != {"contenu_conforme", "motif", "operations_demandees"}
                or type(rapport["contenu_conforme"]) is not bool or not isinstance(rapport["motif"], str)
                or not isinstance(rapport["operations_demandees"], list)
                or any(not isinstance(t, str) or t not in SENS_CONTENU or t == "propos"
                       for t in rapport["operations_demandees"])):
            raise RapportInvalide("La contre-revue de la parole est invalide.")
        requises = operations_demandees if operations_demandees is not None else set()
        # Une correction du contenu ne peut effacer une demande déjà reconnue.
        requises.update(rapport["operations_demandees"])
        manquantes = requises - operations_contenu(plan.parole["contenu"])
        if manquantes:
            # Une cause à la fois, dans l'ordre commun du protocole :
            # le marché porte aussi sa demande, et précise sa contrepartie.
            operation = next(t for t in SENS_CONTENU if t in manquantes)
            forme = ("proposition {demande, contrepartie}, ou demande/passage avec valeur = prix offert en chiffres positifs"
                     if operation == "proposition" else operation + " : " + SENS_CONTENU[operation])
            raise ErreurMonde("Le contenu proposé ne porte pas ce que tu demandes.",
                attendu_audit("proposition.contenu", json.dumps(plan.parole["contenu"], ensure_ascii=False),
                              forme, ("opération demandée absente", operation)))
        motif = rapport["motif"][:MOTIF_MAX]
        if not rapport["contenu_conforme"]:
            raise ErreurMonde("Les mots ou le contenu proposés ne correspondent pas à ta parole.",
                attendu_audit("proposition.replique et proposition.contenu",
                              json.dumps({k: plan.parole[k] for k in ("replique", "contenu")}, ensure_ascii=False),
                              "les mots et le contenu de la demande, sans changement de sens",
                              ("contenu non conforme", motif)))
        return
    if (not isinstance(rapport, dict) or set(rapport) != {"conforme", "motif"}
            or type(rapport["conforme"]) is not bool or not isinstance(rapport["motif"], str)):
        raise RapportInvalide("La contre-revue de la manœuvre est invalide.")
    if not rapport["conforme"]:
        # Le motif n'est qu'une explication transmise au MJ : un motif trop long est abrégé.
        motif = rapport["motif"].strip()
        if len(motif) > MOTIF_MAX:
            motif = motif[:MOTIF_MAX - 1].rstrip() + "…"
        recu = ""
        partie = "proposition"
        accepte = ("le même geste, dont les changements durables sont ceux de la demande : "
                   "retire celui qu'elle ne demande pas, ou ajoute l'étape qui manque")
        if plan is not None:
            p = plan.proposition if isinstance(plan.proposition, dict) else {}
            cibles = p.get("cible") or ", ".join(map(str, p.get("cibles") or []))
            recu = f"{plan.titre} (action {p.get('action')}" + (f", cible {cibles}" if cibles else "") + ")"
        raise ErreurMonde("La manœuvre proposée ne couvre pas la demande : " +
                          (motif or "une conséquence demandée manque."),
                          attendu_audit(partie, recu or "le plan proposé", accepte,
                                        ("non conforme", motif)))
