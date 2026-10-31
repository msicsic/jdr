"""Contre-revue de la fidélité d'une proposition à la demande du joueur.

Le moteur valide les effets possibles ; cette revue vérifie que le plan ne perd pas
une partie observable de l'intention. Son avis ne modifie jamais le monde.
"""

import json

from .monde import ErreurMonde
from .refus import RapportIllisible, attendu_audit
from .noms import REGLE_DESIGNATIONS, reperes_designations
from .paroles import SENS_CONTENU, operations_contenu, offre, OPERATIONS, SCHEMA_OPERATIONS


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
        "perimetre": {"type": "string", "enum": ["sens", "adresse", "validation_moteur"],
            "description": "Domaine du motif : sens des mots et du contenu ; adresse des paroles ; forme ou conséquences déjà validées par le moteur. Seul sens peut refuser la fidélité."},
        "operations_demandees": SCHEMA_OPERATIONS,
    },
    "required": ["contenu_conforme", "motif", "operations_demandees", "perimetre"],
}


def schema(plan):
    return SCHEMA_PAROLE if plan.parole is not None else SCHEMA

INSTRUCTIONS = """Tu fais une contre-revue indépendante de la fidélité d'un plan de jeu.
Compare la demande entière du joueur aux opérations que le moteur exécutera vraiment.
Le sens_propose de chaque étape donne l'opération, ses paramètres, les contrats canoniques
et la manière proposée. Ce sens est distinct de l'admission mécanique : un plan possible
peut être infidèle et un geste fidèle peut être empêché par le monde. Ne déduis jamais
une omission de son refus ou de sa non-exécution. Compare aussi les clauses transitoires.
precisions_moteur donne le sens affiché par le moteur depuis ses opérations et effets,
indépendamment des textes proposés ; il fait autorité sur leurs conséquences.
Les textes de maniere_proposee sont des propositions, jamais des preuves d'effet :
seuls les effets typés et les opérations du moteur produisent les conséquences.
Le champ parole est le dossier de contenu d'une parole préparée : replique, contenu et
sens_contenu. Compare ces mots et ce contenu à la demande du joueur avant enregistrement.
L'adresse, les auditeurs et les effets mécaniques sont fixés et validés séparément par le
moteur ; ils ne font pas partie de ce dossier ni du sens à contrôler. contenu décrit ce
qui est demandé ou affirmé, pas les opérations de transfert ou de paiement à exécuter.
Les opérations désignent chaque chose par « nom (identifiant) » : le nom est celui que le joueur
emploie, l'identifiant n'est qu'une étiquette technique.
Le plan représente l'état du monde : action, cibles, outil, et conséquences observables
(objet déplacé, détaché, allumé, marqué, son émis, blessure, usure). La manière du geste
(position des mains, style, intention affichée, caractère d'un son ou d'un air) figure dans
les paramètres ou maniere_proposee ; compare-la sans lui attribuer d'effet non typé.
Une question sur la faisabilité d'un geste (« puis-je… ? ») se juge comme la demande de ce geste.
Réponds conforme=false seulement pour un écart net de sens :
- une action ou une cible différente de celle demandée ;
- une conséquence observable demandée qui n'est ni déjà vraie d'après le dossier, ni produite par le plan,
  même temporaire ; le récit, le bruit d'un geste et sa manière ne valent pas un effet typé ;
- une conséquence ajoutée que le joueur n'a pas demandée ;
- une clause ou une forme concrète du geste demandée contredite ou omise par les paramètres
  et la manière proposés ; une nuance cosmétique seule n'exige aucun nouveau paramètre
  d'une opération canonique qui porte déjà le geste.
Compare la demande à l'état final établi par le moteur, en lisant ensemble le titre,
l'information, deplacements, passages, les effets et les étapes. Les déplacements et
effets que le moteur établit pour accomplir le geste font partie de ce geste : ils
ne sont pas des changements ajoutés et n'exigent pas une demande séparée. Cela
n'autorise pas une autre action sur un tiers sans rapport avec le geste demandé.
Un état demandé déjà vrai avant le plan d'après le dossier n'exige aucune opération
pour le rétablir. Distingue cet acquis des changements restant à produire : les
départs et présences connues décrivent l'avant, les arrivées et etat_apres_operation
décrivent l'après de leur opération. Une présence ne prouve pas qu'un passage est
fermé ; ne suppose aucun état ou effet absent du dossier.
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
improvisé (geste_improvise) accomplit un geste sur ses cibles : sa forme proposée reste
à comparer à la demande ; ses conséquences doivent être portées par les effets typés.
Il ne déplace pas Corvus : un déplacement demandé exige une opération qui le produit.
N'exige ni résultat incertain, ni réaction d'un tiers, ni effet non demandé.
La branche d'échec d'un jet peut ne pas atteindre le but ; juge sa cohérence avec le risque.
En cas de doute, réponds conforme=true : le moteur garde l'autorité sur chaque effet.
Le motif désigne un seul écart de sens, en nommant l'opération, le paramètre ou l'effet
typé manquant ou ajouté selon le contrat, sans inventer un fait du monde.
Pour un plan de parole, rends contenu_conforme : les mots et le contenu typé traduisent-ils
la demande ? Un contenu vide ou propos n'attribue aucun effet mécanique aux mots ; il n'est
pas infidèle par son seul manque de typage. Juge les mots et les effets des seuls contenus
typés présents, sans exiger d'en inventer un pour toute question. Ne juge dans ce booléen ni l'audience fixée par le moteur, ni les conséquences
qu'il a calculées. Pour les autres plans, rends conforme et motif.
Appelle auditer_action une fois.
"""


INSTRUCTIONS += "\n" + REGLE_DESIGNATIONS

# Un contrat distinct évite d'appliquer à la parole les critères de cible et
# d'effet durable des gestes. Le périmètre du verdict reste contrôlé à réception.
INSTRUCTIONS_PAROLE = """Tu contrôles le sens d'une parole préparée, avant son enregistrement.
Compare la demande du joueur à replique et au sens exécutable du contenu fourni.
Analyse séparément operations_demandees dans la saisie, même si le contenu proposé les omet.
contenu_conforme juge uniquement une contradiction ou une omission de sens : mots,
biens, quantités, prix, attributs, engagements, clauses et repères temporels.
Les termes exécutables portent le paiement présent et les limites absolues avec leur
durée restante. Compare chaque clause de la demande à ces termes, même si les mots
de la réplique la reproduisent. Une limite absente, déplacée, un maintien converti
en accomplissement ponctuel, un paiement futur converti en paiement présent ou une
alternative réduite à une seule branche sont des omissions ou contradictions de sens.
Une clause sans représentation ne peut pas être abandonnée pour exécuter le reste.
Un contenu propos ne couvre pas une
opération demandée ; le moteur contrôle séparément la couverture des opérations.
L'adresse est déjà décidée par destinataires, y compris le sens des mots qui la
portent : pronoms, indéfinis, vocatifs, groupes. Ces mots ne permettent pas de
refuser le contenu pour l'étendue ou l'identité de son audience. Ils restent dans
la réplique originale ; n'invente aucune autre décision d'adresse.
Le contenu et sens_contenu sont validés par le moteur : juge leur signification,
jamais leur forme technique ni leurs conséquences. Les opérations et le prix
exécutable fournis font autorité, quelle que soit la représentation du contenu.
Une question, une demande et une offre n'annoncent pas l'accord ou la réaction du
destinataire. La réponse, le règlement d'un dû et les transferts relèvent du moteur.
Ne transforme pas ces conséquences en différences de sens avec la saisie.
Rends perimetre=sens pour un écart de sens, adresse pour une objection d'audience,
validation_moteur pour une objection sur la forme ou les conséquences validées.
Seul un écart de sens justifie contenu_conforme=false. En cas de doute, accepte.
Le motif explique un seul écart. Appelle auditer_action une fois.
""" + "\n" + REGLE_DESIGNATIONS


def sens_parole(contenu, monde):
    """Sens public et opérations exécutables : une représentation n'est pas une omission."""
    from .paroles import sens_contenu
    return [{**sens, "operations": sorted(operations_contenu([c])),
             **({"prix_offert": offre(c)} if c.get("type") in ("demande", "passage") else {})}
            for c, sens in zip(contenu, sens_contenu(contenu, monde))]


def _operations(plan, monde=None, parametres=None):
    from .comprehension import sens_propose
    from .deplacement_objet import presenter_effet
    def presenter(effet):
        # La bascule interne « ouverture=False » signifie fermer, pas ouvrir.
        # La revue lit l'opération exécutée, jamais le nom interne du champ.
        if effet[0] == "ouverture":
            return ["ouvrir" if effet[2] else "fermer", effet[1], None]
        return presenter_effet(monde, effet) if monde is not None else list(effet)
    improvise = plan.proposition.get("action") == "improviser"
    return {
        "titre": plan.titre,
        "sens_propose": sens_propose(plan, parametres),
        **({"deplacements": _deplacements(plan, monde)}
           if monde is not None and hasattr(plan, "deplacements") else {}),
        **({"passages": passages} if monde is not None and (passages := _passages(plan, monde)) else {}),
        **({"destination_corps": _nommer(plan.destination_corps, monde)}
           if monde is not None and hasattr(plan, "destination_corps") else {}),
        **({"perception": plan.perception} if plan.perception is not None else {}),
        **({"parole": plan.parole} if plan.parole is not None else {}),
        **({"geste_improvise": {"approche": plan.proposition.get("approche"),
                                "cibles": plan.proposition.get("cibles", []),
                                "outil": plan.proposition.get("outil", "")}} if improvise else {}),
        "effets_reussite": [presenter(e) for e in plan.effets if e[0] != "recit_improvise"],
        "effets_echec": [presenter(e) for e in plan.echec if e[0] != "recit_improvise"],
        "effets_echec_critique": [presenter(e) for e in plan.echec_critique if e[0] != "recit_improvise"],
        "information": plan.information,
        "jet": bool(plan.stat),
        "conditions_execution": {"stat": plan.stat, "difficulte": plan.dd,
                                 "minutes": plan.minutes, "dixiemes": plan.dixiemes,
                                 "bruit": plan.bruit},
        "etapes": [_operations(etape, monde, plan.etapes[i] if i < len(plan.etapes) else None)
                   for i, etape in enumerate(plan.plans)],
    }


def _deplacements(plan, monde):
    """Le trajet validé décrit les pas sans dévoiler la géographie non visitée."""
    connues = set(monde.data.get("visitees", [])) | {monde.joueur["salle"]}
    return [{"acteur": _nommer(d["acteur"], monde),
             **{cle: (_nommer(d[cle], monde) if d[cle]["salle"] in connues
                      else {"passage": "de l'autre côté, lieu non visité"})
                for cle in ("depart", "arrivee")}}
            for d in plan.deplacements]



def _passages(plan, monde):
    """Sens des portes du plan, limité aux lieux et présences déjà perçus."""
    from .tenir import sorties_crues, retenus_apres
    if not any(op in ("ouverture", "verrouiller") for op, _, _ in plan.effets):
        return []
    souvenirs = monde.data.get("souvenirs_visuels", {})
    lieux = {i: s["salle"] for i, s in souvenirs.items() if monde.designable(i)}
    for i in monde.objets:
        if monde.objets[i].get("type") == "personnage" and monde.visible(i):
            lieux[i] = monde.objets[i]["lieu"]
    connus = set(lieux.values()) | {monde.joueur["salle"]}
    resultat = []
    for op, cible, valeur in plan.effets:
        if op not in ("ouverture", "verrouiller") or monde.objets.get(cible, {}).get("type") != "porte":
            continue
        retenus = retenus_apres(monde, "joueur", cible, verrouillee=op == "verrouiller")
        for salle in sorted(connus):
            if salle not in monde.data["salles"]:
                continue
            if not any(s.get("porte") == cible for s in monde.data["salles"][salle].get("sorties", {}).values()):
                continue
            resultat.append({"operation": ("ouvrir" if valeur else "fermer") if op == "ouverture" else op, "porte": cible, "type": "porte", "lieu": salle,
                "lieu_corvus": monde.joueur["salle"],
                "etat_apres_operation": {"ouverte": valeur} if op == "ouverture" else {"verrouillee": True},
                "personnes_retenues_apres_operation": [i for i in retenus.get(salle, []) if monde.designable(i)],
                "personnes_connues": sorted(i for i, lieu in lieux.items() if lieu == salle
                    and monde.objets[i].get("type") == "personnage"),
                "issues_connues_avant": [{"porte": p, "verrouillee": v}
                    for p, v in sorties_crues(monde, "joueur", salle) if p is None or monde.designable(p)]})
    return _nommer(resultat, monde)


def _nommer(valeur, monde):
    """Un identifiant devient « nom (identifiant) » : un identifiant nu (« marchand ») se lit
    comme un mot et ne désigne plus le personnage que le joueur nomme (« Gorm »)."""
    if isinstance(valeur, str) and valeur in monde.data["salles"]:
        return f"{monde.data['salles'][valeur]['nom']} ({valeur})"
    if isinstance(valeur, str) and valeur in monde.objets:
        from .noms import public, reference
        return f"{public(monde,monde.objets[valeur]['nom'])} ({reference(monde,valeur)})"
    if isinstance(valeur, (list, tuple)):
        return [_nommer(v, monde) for v in valeur]
    if isinstance(valeur,dict):
        return {k:_nommer(v,monde) for k,v in valeur.items()}
    return valeur


def _nommer_lieux(valeur, monde):
    """Nomme les références de lieu sans réécrire un nom, une inscription ou une citation."""
    if isinstance(valeur, dict):
        return {k: (_nommer(v, monde) if k in ("lieu", "salle") and isinstance(v, str)
                    else _nommer_lieux(v, monde)) for k, v in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [_nommer_lieux(v, monde) for v in valeur]
    return valeur


def entree(intention, plan, monde=None):
    """La demande et les opérations du plan, chaque identifiant cité accompagné de son nom."""
    operations = _operations(plan, monde)
    if monde is not None:
        def nommer_parametres(c):
            from .noms import CHAMPS_REFERENCES, LISTES_REFERENCES
            if isinstance(c, list):
                return [nommer_parametres(v) for v in c]
            if not isinstance(c, dict) or c.get('type') == 'ressource':
                return c
            return {k: (_nommer(v, monde) if k in CHAMPS_REFERENCES | LISTES_REFERENCES
                        else nommer_parametres(v)) for k, v in c.items()}

        def nommer_parole(p):
            # Les références sont nommées, les mots libres restent littéraux.
            return {**p, "contenu": [nommer_parametres(c) for c in p.get("contenu", [])],
                    **({"comptes_avant": _nommer(p["comptes_avant"], monde)}
                       if "comptes_avant" in p else {})}
        def nommer_plan(op):
            return {**op, **{cle: _nommer(op[cle], monde) for cle in
                            ("effets_reussite", "effets_echec", "effets_echec_critique")},
                    "sens_propose": nommer_parametres(op["sens_propose"]),
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
        entree_["designations"] = [
            {**repere, "faits": _nommer_lieux(repere["faits"], monde)}
            for repere in reperes_designations(intention, faits) + reperes_designations(
                json.dumps(operations, ensure_ascii=False), faits)]
    return entree_


MOTIF_MAX = 300


class RapportInvalide(RapportIllisible):
    """Le rapport de la revue est mal formé : une faute de l'auditeur, pas de la proposition."""


def lire_operations(declaration):
    """Même contrat typé à l'interprétation et à la revue."""
    from .refus import RefusDeForme
    if (not isinstance(declaration, dict) or set(declaration) != set(OPERATIONS)
            or any(type(v) is not bool for v in declaration.values())):
        raise RefusDeForme("Les opérations demandées sont invalides.",
            "operations_demandees : une carte complète de booléens pour " + ", ".join(OPERATIONS)
            + " ; reçu : " + repr(declaration))
    return {t for t, demandee in declaration.items() if demandee}


def verifier_operations(plan, requises):
    """Couverture déterministe, avant tout appel de revue."""
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


def verifier(rapport, plan=None, operations_demandees=None):
    """Le verdict de la contre-revue. Non conforme : un refus dont ``attendu`` (``refus.attendu_audit``)
    cite le plan reçu, le motif de la revue tel quel, et ce qui serait accepté."""
    if plan is not None and plan.parole is not None:
        if (not isinstance(rapport, dict)
                or set(rapport) != {"contenu_conforme", "motif", "operations_demandees", "perimetre"}
                or rapport["perimetre"] not in ("sens", "adresse", "validation_moteur")
                or type(rapport["contenu_conforme"]) is not bool or not isinstance(rapport["motif"], str)
                or not isinstance(rapport["operations_demandees"], dict)
                or set(rapport["operations_demandees"]) != set(OPERATIONS)
                or any(type(v) is not bool for v in rapport["operations_demandees"].values())):
            raise RapportInvalide("La contre-revue de la parole est invalide.")
        requises = operations_demandees if operations_demandees is not None else set()
        # Une correction du contenu ne peut effacer une demande déjà reconnue.
        reconnues = {t for t, demandee in rapport["operations_demandees"].items() if demandee}
        if not rapport["contenu_conforme"] and rapport["perimetre"] == "sens":
            # Les opérations présentes appartiennent au contenu que cette même
            # revue conteste : ce ne sont pas des obligations confirmées. Les
            # opérations absentes, en revanche, signalent une omission à réparer.
            reconnues -= operations_contenu(plan.parole["contenu"])
        requises.update(reconnues)
        verifier_operations(plan, requises)
        motif = rapport["motif"][:MOTIF_MAX]
        if not rapport["contenu_conforme"] and rapport["perimetre"] == "sens":
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
        accepte = ("le même geste, les clauses et la manière demandées, avec leurs conséquences observables "
                   "portées par les opérations et effets typés : retire l'ajout ou ajoute l'opération, "
                   "le paramètre ou l'effet manquant désigné par le motif de revue")
        if plan is not None:
            p = plan.proposition if isinstance(plan.proposition, dict) else {}
            cibles = p.get("cible") or ", ".join(map(str, p.get("cibles") or []))
            recu = f"{plan.titre} (action {p.get('action')}" + (f", cible {cibles}" if cibles else "") + ")"
        raise ErreurMonde("La manœuvre proposée ne couvre pas la demande : " +
                          (motif or "une conséquence demandée manque."),
                          attendu_audit(partie, recu or "le plan proposé", accepte,
                                        ("non conforme", motif)))
