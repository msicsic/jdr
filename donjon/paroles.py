"""Paroles du joueur aux PNJ : réplique rendue selon INT et CHA, contenu typé, croyances.

Le joueur écrit ce qu'il veut faire dire à Corvus. Le moteur fixe la bande d'expression
(précision selon l'INT, aisance selon le CHA) ; Luna écrit la réplique dans cette bande et
type son contenu : affirmations (sujet, attribut, valeur), demandes d'objet, simples propos.
Une réplique entre guillemets est dite mot pour mot. L'effet ne dépend jamais des mots
choisis par Luna : le moteur le calcule sur le contenu typé, les caractéristiques, la
confiance de l'auditeur et un jet de CHA. Une INT faible, chez celui qui parle ou chez celui
qui écoute, réduit ce qui est transmis. Une affirmation démentie par ce que le PNJ perçoit ou
a vu récemment est rejetée et il cesse de croire le joueur fiable.
"""
import copy
import re

from .esprits import RECENT, croire, esprit, lire, memoriser, percevoir
from .francais import designer
from .monde import ErreurMonde

ATTRIBUTS = ("lieu", "verrouillee", "fiable")
TYPES = ("propos", "affirmation", "demande")
SCHEMA_PAROLE = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "personnage": {"type": "string"},
        "replique": {"type": "string", "description": "Ce que Corvus prononce, dans la bande d'expression."},
        "contenu": {"type": "array", "maxItems": 3, "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "type": {"type": "string", "enum": list(TYPES)},
                "sujet": {"type": "string"}, "attribut": {"type": "string", "enum": ["", *ATTRIBUTS]},
                "valeur": {"type": "string"},
            },
            "required": ["type", "sujet", "attribut", "valeur"]}},
    },
    "required": ["personnage", "replique", "contenu"],
}

PRECISION = ((7, "très pauvre : mots simples, phrases hachées, termes approximatifs"),
             (9, "pauvre : vocabulaire courant restreint, idées une à une, détails perdus"),
             (12, "courante : phrases simples et claires"),
             (15, "précise : termes justes, idées bien liées"),
             (20, "riche : vocabulaire étendu, nuances et tournures soignées"))
AISANCE = ((7, "très maladroite : hésitations, ton mal choisi, peut froisser"),
           (9, "maladroite : hésitante, peu convaincante"),
           (12, "ordinaire"),
           (15, "assurée : posée, persuasive"),
           (20, "brillante : charme, à-propos, art de convaincre"))

REGLES = """
Mode parole_joueur : le joueur fait parler Corvus à un personnage présent (affirmer, mentir,
demander un objet, ou simplement converser) sans récompense à négocier. proposition =
{"personnage": identifiant, "replique": ce que Corvus prononce, "contenu": [...]}, texte vide.
La réplique traduit l'intention du joueur dans la bande expression_joueur : la précision suit
l'INT, l'aisance le CHA. Une INT faible simplifie et perd des détails, un CHA faible rend
maladroit ; une bande élevée enrichit sans ajouter d'idée. L'écart entre deux bandes doit
s'entendre : très pauvre = quelques mots, hésitations ; riche et brillante = formules
choisies, images, tact. Si le joueur écrit ses mots entre
guillemets, ils sont dits tels quels. contenu type ce que la réplique transmet (3 au plus) :
affirmation {sujet: identifiant d'objet, de personnage ou "joueur", attribut: lieu (valeur =
identifiant de salle ou de porteur), verrouillee (valeur oui/non) ou fiable (valeur oui/non)} ;
demande {sujet: objet que le personnage porte et que Corvus lui demande, attribut "", valeur ""} ;
propos {sujet "", attribut "", valeur ""} pour le reste. Une affirmation peut être fausse :
c'est au personnage d'y croire ou non, et au moteur d'en décider. Le moteur te renvoie
conversation_validee : fais répondre le personnage d'après ce résultat, ses croyances et ses
traits (esprits_interlocuteurs). Ce qu'un personnage croit n'est pas un fait : il peut le
dire, se tromper ou le taire ; il n'avoue son intention que si ses traits s'y prêtent.
"""


def _bande(table, valeur):
    return next(texte for seuil, texte in table if valeur <= seuil)


def bande_expression(stats):
    return {"precision": _bande(PRECISION, stats["INT"]), "aisance": _bande(AISANCE, stats["CHA"])}


def capacite_transmission(intelligence):
    """Nombre d'idées qu'une réplique transmet ou qu'un auditeur retient."""
    return 1 if intelligence <= 9 else 2 if intelligence <= 12 else 3


def _stats_pnj(monde, id):
    if id == "joueur":
        return monde.joueur["stats"]
    profil = monde.objets[id].get("profil")
    return profil["caracteristiques"] if profil else {"FOR": 10, "DEX": 10, "INT": 10, "PER": 10, "CHA": 10}


def jet_persuasion(monde, auditeur, locuteur, dd_base):
    """d20 + CHA du locuteur contre un DD que la confiance de l'auditeur abaisse ou relève."""
    confiance = lire(monde, auditeur)["croyances"].get(locuteur, {}).get("fiable")
    dd = dd_base + (-2 if confiance and confiance["valeur"] else 6 if confiance else 2)
    return monde.d20() + (_stats_pnj(monde, locuteur)["CHA"] - 10) // 2 >= dd, dd


def dementi(monde, auditeur, sujet, attribut, valeur):
    """Ce que l'auditeur a vu ou essayé récemment contredit-il ce qu'on lui dit ?"""
    actuelle = lire(monde, auditeur)["croyances"].get(sujet, {}).get(attribut)
    return bool(actuelle and actuelle["source"] in ("vu", "essai") and actuelle["valeur"] != valeur
                and monde.data["minutes"] - actuelle["minute"] <= RECENT)


def _nom(monde, id):
    if id == "joueur":
        return "toi"
    if id in monde.data["salles"]:
        return monde.data["salles"][id]["nom"]
    return designer(monde.objets[id]) if id in monde.objets else id


def _phrase(monde, sujet, attribut, valeur):
    if attribut == "lieu":
        if valeur is None:
            return f"{_nom(monde, sujet)} n'est plus là où il l'attendait"
        porte = valeur == "joueur" or valeur in monde.objets and monde.objets[valeur]["type"] == "personnage"
        return f"{_nom(monde, sujet)} est {'porté par' if porte else 'dans'} {_nom(monde, valeur)}"
    if attribut == "verrouillee":
        return f"{_nom(monde, sujet)} est {'verrouillé' if valeur else 'déverrouillé'}"
    if attribut == "fiable":
        return f"{_nom(monde, sujet)} est {'digne de confiance' if valeur else 'peu fiable'}"
    return ""


def _ouidire(monde, source):
    """D'où il tient une croyance rapportée, nommé seulement si le joueur connaît ce témoin."""
    if not source.startswith("dit:"):
        return ""
    locuteur = source[4:]
    if locuteur == "joueur":
        return " (tu le lui as dit)"
    if locuteur in monde.objets and _connu_du_joueur(monde, locuteur):
        return f" ({monde.objets[locuteur]['nom'].split(',')[0]} le lui a dit)"
    return " (on le lui a dit)"


def esprits_interlocuteurs(monde, presents):
    """Ce que Luna peut savoir d'un PNJ présent pour lui donner une voix : ses croyances, pas la vérité."""
    resultat = {}
    for id in presents:
        e, profil = lire(monde, id), monde.objets[id].get("profil")
        croyances = []
        for sujet, attributs in e["croyances"].items():
            for attribut, c in attributs.items():
                if attribut in ATTRIBUTS and (sujet == "joueur" or sujet in monde.objets):
                    croyances.append((not c["source"].startswith("dit:"), -c["minute"],
                                      f"croit que {_phrase(monde, sujet, attribut, c['valeur'])}"
                                      + _ouidire(monde, c["source"])))
        resultat[id] = {
            "traits": profil["traits"] if profil else "",
            "croit": [texte for *_, texte in sorted(croyances)[:12]],
            "but_actuel": copy.deepcopy(e["intention"]["but"]) if e["intention"] else None,
            "besoins_pressants": sorted(b for b, v in e["besoins"].items()
                                        if profil and v >= profil["besoins"][b]["urgence"]),
        }
    return resultat


def contexte(monde):
    from .dialogues import interlocuteurs
    presents = list(interlocuteurs(monde))
    if not presents:
        return None
    return {"expression_joueur": bande_expression(monde.joueur["stats"]),
            "esprits_interlocuteurs": esprits_interlocuteurs(monde, presents)}


def citation(intention):
    """Mots que le joueur impose entre guillemets, s'il y en a."""
    m = re.search(r"[«\"“]\s*(.+?)\s*[»\"”]", intention or "")
    return m.group(1) if m else None


def _connu_du_joueur(monde, id):
    """Le joueur ne parle que de ce dont il a connaissance : perçu, examiné, vu ou entendu nommer."""
    from . import lexique
    if (id == "joueur" or id in monde.data["visitees"] or id in monde.data["connus"]
            or id in monde.data.get("souvenirs_visuels", {}) or id in monde.data.get("souvenirs_personnages", {})):
        return True
    if id not in monde.objets and id not in monde.data["salles"]:
        return False
    return id in lexique.entites_citees(monde, lexique.corpus(monde.contexte(), monde.data.get("conversation", [])))


def resoudre(monde, reference):
    """Identifiant désigné par un identifiant ou un nom, parmi ce que Corvus connaît ; sinon None.

    Un nom partiel (« refuge » pour « Refuge du relais ») vaut s'il ne désigne qu'une entité connue.
    """
    from . import lexique
    if not isinstance(reference, str) or not reference.strip():
        return None
    if reference in ("joueur", *monde.data["salles"], *monde.objets):
        return reference if _connu_du_joueur(monde, reference) else None
    cites = {i for i in lexique.entites_citees(monde, reference) if _connu_du_joueur(monde, i)}
    if len(cites) == 1:
        return cites.pop()
    mots = lexique.normaliser(reference).split()
    candidats = set()
    for id, nom in [*((i, s.get("nom", "")) for i, s in monde.data["salles"].items()),
                    *((i, n) for i, o in monde.objets.items() for n in [o["nom"], *o.get("aliases", [])])]:
        noms = lexique.normaliser(nom).split()
        if mots and any(noms[k:k + len(mots)] == mots for k in range(len(noms))) and _connu_du_joueur(monde, id):
            candidats.add(id)
    return candidats.pop() if len(candidats) == 1 else None


def _typer(monde, c):
    """Contenu typé exploitable, ou None : ce qui ne peut pas être transmis reste un simple propos."""
    if not isinstance(c, dict) or c.get("type") not in ("affirmation", "demande"):
        return None
    sujet = resoudre(monde, c.get("sujet"))
    if sujet is None:
        return None
    if c["type"] == "demande":
        return {"type": "demande", "sujet": sujet}
    attribut, valeur = c.get("attribut"), c.get("valeur")
    if attribut == "lieu":
        valeur = resoudre(monde, valeur)
        if valeur is None:
            return None
    elif attribut in ("verrouillee", "fiable") and valeur in ("oui", "non"):
        valeur = valeur == "oui"
    else:
        return None
    return {"type": "affirmation", "sujet": sujet, "attribut": attribut, "valeur": valeur}


def _jet(monde, auditeur, dd_base):
    return jet_persuasion(monde, auditeur, "joueur", dd_base)


def _affirmer(travail, auditeur, sujet, attribut, valeur, clarte, faits):
    e = esprit(travail, auditeur)
    nom = travail.objets[auditeur]["nom"]
    if dementi(travail, auditeur, sujet, attribut, valeur):
        croire(travail, auditeur, "joueur", "fiable", False, "vu")
        memoriser(travail, auditeur, {"type": "mensonge_dementi", "locuteur": "joueur",
                                      "sujet": sujet, "attribut": attribut})
        faits.append(f"{nom} sait de ses propres yeux que c'est faux et cesse de te croire fiable.")
        return
    reussi, dd = _jet(travail, auditeur, 10)
    if not reussi:
        memoriser(travail, auditeur, {"type": "parole_doutee", "sujet": sujet, "attribut": attribut})
        faits.append(f"{nom} ne te croit pas ({_phrase(travail, sujet, attribut, valeur)}).")
        return
    lieu = {"salle": valeur if valeur in travail.data["salles"] else None, "case": None} if attribut == "lieu" else {}
    croire(travail, auditeur, sujet, attribut, valeur, "dit:joueur", round(0.7 * clarte, 2), **lieu)
    memoriser(travail, auditeur, {"type": "parole_crue", "sujet": sujet, "attribut": attribut})
    # Ce qu'il a sous les yeux peut le démentir aussitôt.
    percevoir(travail, auditeur)
    if any(s["type"] == "mensonge_decouvert" and s.get("sujet") == sujet
           for s in e["memoire"][-3:]):
        faits.append(f"{nom} voit bien que c'est faux et cesse de te croire fiable.")
    else:
        faits.append(f"{nom} te croit : il tient désormais pour vrai que {_phrase(travail, sujet, attribut, valeur)}.")


def _necessaire(travail, auditeur, objet):
    """Un objet qui sert son plan en cours ou une de ses pulsions (l'objet, sa clé) n'est pas prêté."""
    intention = lire(travail, auditeur)["intention"]
    if intention and any(objet in (e["cible"], e["outil"]) for e in intention["plan"]):
        return True
    profil = travail.objets[auditeur].get("profil")
    for pulsion in (profil or {}).get("pulsions", []):
        cible = pulsion["condition"].get("objet")
        if cible and (objet == cible or cible in travail.objets[objet].get("ouvre", [])):
            return True
    return False


def _demander(travail, auditeur, objet, faits):
    from .deplacement_objet import deplacer
    from .spatial import porte_par
    nom = travail.objets[auditeur]["nom"]
    if objet not in travail.objets or not porte_par(travail, objet, auditeur):
        faits.append(f"{nom} n'a pas cet objet sur lui.")
        return
    confiance = lire(travail, auditeur)["croyances"].get("joueur", {}).get("fiable")
    if confiance and not confiance["valeur"]:
        faits.append(f"{nom} refuse : il ne te fait pas confiance.")
        return
    if _necessaire(travail, auditeur, objet):
        faits.append(f"{nom} refuse de se séparer de {designer(travail.objets[objet])}, qui lui sert.")
        return
    reussi, _ = _jet(travail, auditeur, 12)
    if not reussi:
        faits.append(f"{nom} n'est pas convaincu et garde {designer(travail.objets[objet])}.")
        return
    deplacer(travail, objet, "joueur")
    memoriser(travail, auditeur, {"type": "pret", "objet": objet, "a": "joueur"})
    faits.append(f"{nom} te remet {designer(travail.objets[objet])}.")


def preparer_parole(monde, p, revision=None):
    from .dialogues import interlocuteurs
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant la fin de la conversation.")
    if (not isinstance(p, dict) or not set(SCHEMA_PAROLE["required"]) <= set(p)
            or not isinstance(p["replique"], str) or not 1 <= len(p["replique"].strip()) <= 400
            or not isinstance(p["contenu"], list) or len(p["contenu"]) > 3
            or set(p) - set(SCHEMA_PAROLE["required"]) - {"_intention"}):
        raise ErreurMonde("Parole mal formée.")
    auditeur = p["personnage"]
    if auditeur not in interlocuteurs(monde):
        raise ErreurMonde("Ce personnage n'est pas ici pour t'entendre.")
    from . import lexique
    replique = p["replique"].strip()
    # La réplique affichée obéit au contrôle des mentions : rien que Corvus ne connaisse.
    fondement = lexique.corpus(monde.contexte(), monde.data.get("conversation", []),
                               monde.data.get("paroles_joueur", []))
    if p.get("_intention"):
        fondement += " " + lexique.corpus(p["_intention"])
    if lexique.mentions_sans_fondement(monde, replique, fondement):
        raise ErreurMonde("La réplique de Corvus nomme ce qu'il ne connaît pas.")
    travail = monde.copier()
    stats_auditeur = _stats_pnj(travail, auditeur)
    capacite = min(capacite_transmission(travail.joueur["stats"]["INT"]),
                   capacite_transmission(stats_auditeur["INT"]))
    clarte = 0.5 if stats_auditeur["INT"] <= 8 else 1.0
    faits = []
    transmis = [x for x in (_typer(travail, c) for c in p["contenu"]) if x]
    perdus = transmis[capacite:]
    for c in transmis[:capacite]:
        if c["type"] == "affirmation":
            _affirmer(travail, auditeur, c["sujet"], c["attribut"], c["valeur"], clarte, faits)
        else:
            _demander(travail, auditeur, c["sujet"], faits)
    if perdus:
        faits.append(f"{travail.objets[auditeur]['nom']} ne retient pas tout : une partie de ce que tu as dit se perd.")
    memoriser(travail, auditeur, {"type": "parole", "locuteur": "joueur", "texte": replique[:240]})
    travail.data["revision"] += 1
    travail.data.setdefault("paroles_joueur", []).append(
        {"revision": travail.data["revision"], "auditeur": auditeur, "texte": replique,
         "minute": travail.data["minutes"]})
    travail.data["paroles_joueur"] = travail.data["paroles_joueur"][-40:]
    travail.verifier()
    rapport = {"personnage": auditeur, "sujet": replique, "operation": "parole_joueur",
               "replique_joueur": replique, "faits": faits}
    return travail, rapport
