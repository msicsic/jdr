"""Paroles du joueur aux PNJ : réplique rendue selon INT et CHA, contenu typé, croyances.

Le joueur écrit ce qu'il veut faire dire à Corvus. Le moteur fixe la bande d'expression
(précision selon l'INT, aisance selon le CHA) ; Luna écrit la réplique dans cette bande et
type son contenu : affirmations (sujet, attribut, valeur), demandes d'objet, demandes de passage
(s'écarter, laisser passer), simples propos.
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
TYPES = ("propos", "affirmation", "demande", "passage")
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
## 7. Faire parler Corvus (parole_joueur)
proposition = {personnage, replique (ce que Corvus prononce), contenu}, texte vide. Le
personnage est celui à qui le joueur s'adresse ; si le joueur écrit ses mots entre guillemets ou
interpelle directement le personnage (« Gorm, … »), ce sont ses mots, dits tels quels. Sinon,
la réplique traduit son intention dans la bande expression_joueur : la précision suit l'INT,
l'aisance le CHA (très pauvre : quelques mots, des hésitations ; brillante : formules choisies,
images, tact ; une bande élevée enrichit sans ajouter d'idée).
contenu (3 éléments au plus) dit ce que la réplique transmet :
- affirmation {sujet : un objet, un personnage ou "joueur" ; attribut : lieu (valeur = une
  salle ou un porteur), verrouillee ou fiable (valeur oui ou non)} ; elle peut être fausse,
  au personnage d'y croire ou non ;
- demande {sujet : un objet que le personnage porte, ou une ressource à lui (vivres, bois)
  dont Corvus demande une part ; attribut et valeur vides} ;
- passage {sujet, attribut et valeur vides} : Corvus demande au personnage de s'écarter, de se
  pousser, de le laisser passer. Le moteur décide s'il bouge et le dit dans les faits ; sa
  réplique dit cette issue, sans promettre de bouger plus tard ;
- propos {sujet, attribut et valeur vides} pour tout le reste.
Le moteur te renvoie conversation_validee : fais répondre le personnage d'après ce résultat,
ses croyances, ses traits et ses valeurs (esprits_interlocuteurs, valeurs de 0 à 100). Ce qu'il
croit n'est pas un fait : il peut le dire, se tromper ou le taire, et n'avoue son intention que
si ses traits s'y prêtent ; il ne ment que si son honnêteté le permet (jamais à 100).
"""


def _bande(table, valeur):
    return next(texte for seuil, texte in table if valeur <= seuil)


def bande_expression(stats):
    return {"precision": _bande(PRECISION, stats["INT"]), "aisance": _bande(AISANCE, stats["CHA"])}


def capacite_transmission(intelligence):
    """Nombre d'idées qu'une réplique transmet ou qu'un auditeur retient."""
    return 1 if intelligence <= 9 else 2 if intelligence <= 12 else 3


def _stats_pnj(monde, id):
    """Les caractéristiques d'un personnage (joueur compris), modulées par ses états."""
    from .caractere import caracteristiques
    return caracteristiques(monde, id)


def jet_persuasion(monde, auditeur, locuteur, dd_base):
    """d20 + présence (CHA) et éloquence (ELO) du locuteur, contre un DD que la confiance de
    l'auditeur abaisse ou relève et que sa volonté (VOL) élève ; caractéristiques modulées."""
    from .caractere import modificateur
    confiance = lire(monde, auditeur)["croyances"].get(locuteur, {}).get("fiable")
    dd = (dd_base + (-2 if confiance and confiance["valeur"] else 6 if confiance else 2)
          + modificateur(monde, auditeur, "VOL"))
    return monde.d20() + modificateur(monde, locuteur, "CHA") + modificateur(monde, locuteur, "ELO") >= dd, dd


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
    if id in monde.objets and monde.objets[id]["type"] == "personnage":
        return monde.objets[id]["nom"].split(",")[0]
    return designer(monde.objets[id]) if id in monde.objets else id


def _phrase(monde, sujet, attribut, valeur):
    o = monde.objets.get(sujet, {})
    est = "sont" if o.get("pluriel") else "est"
    accord = ("e" if o.get("genre") == "f" else "") + ("s" if o.get("pluriel") else "")
    if attribut == "lieu":
        if valeur is None:
            return f"{_nom(monde, sujet)} {'ne sont' if o.get('pluriel') else "n'est"} plus là où il l'attendait"
        porte = valeur == "joueur" or valeur in monde.objets and monde.objets[valeur]["type"] == "personnage"
        return f"{_nom(monde, sujet)} {est} {'porté' + accord + ' par' if porte else 'dans'} {_nom(monde, valeur)}"
    if attribut == "verrouillee":
        return f"{_nom(monde, sujet)} {est} {'verrouillé' if valeur else 'déverrouillé'}{accord}"
    if attribut == "fiable":
        pluriel = "s" if o.get("pluriel") else ""
        return f"{_nom(monde, sujet)} {est} {'digne' + pluriel + ' de confiance' if valeur else 'peu fiable' + pluriel}"
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
    from .deliberation import urgents
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
            "valeurs": dict(profil["valeurs"]) if profil else {},
            "croit": [texte for *_, texte in sorted(croyances)[:12]],
            "but_actuel": copy.deepcopy(e["intention"]["but"]) if e["intention"] else None,
            "besoins_pressants": urgents(monde, id) if profil else [],
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


VOCATIF = re.compile(r"^\s*([^,!?:«»\"“”]{2,40}?)\s*[,:]\s*\S")


def destinataire_nomme(monde, intention):
    """Personnage que le joueur interpelle en tête de son message (« Gorm, … »), s'il le connaît.

    Le message est alors sa réplique, mot pour mot, et ce personnage en est le destinataire."""
    m = VOCATIF.match(intention or "")
    id = resoudre(monde, m.group(1).strip()) if m else None
    return id if id in monde.objets and monde.objets[id]["type"] == "personnage" else None


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


def part_nommee(monde, auditeur, reference):
    """Ressource comptée de l'auditeur que nomme une demande : on peut demander une part de ce
    qu'un autre possède sans l'avoir vu, comme on demande du pain sans connaître l'étagère."""
    from . import lexique
    from .deliberation import besoin_de_part, parts
    from .vol import proprietaire
    if not isinstance(reference, str) or not reference.strip():
        return None
    ids = {reference} if reference in monde.objets else lexique.entites_citees(monde, reference)
    ressources = {i for i in ids if i in monde.objets and besoin_de_part(monde.objets[i])
                  and parts(monde.objets[i]) > 0 and proprietaire(monde, monde.objets[i]) == auditeur}
    return ressources.pop() if len(ressources) == 1 else None


def _typer(monde, c, auditeur=None):
    """Contenu typé exploitable, ou None : ce qui ne peut pas être transmis reste un simple propos."""
    if isinstance(c, dict) and c.get("type") == "passage":
        # On demande le passage à celui à qui l'on parle : le sujet, s'il est donné, est lui.
        sujet = c.get("sujet")
        return {"type": "passage"} if not sujet or resoudre(monde, sujet) == auditeur else None
    if not isinstance(c, dict) or c.get("type") not in ("affirmation", "demande"):
        return None
    sujet = resoudre(monde, c.get("sujet"))
    if sujet is None and c["type"] == "demande" and auditeur:
        sujet = part_nommee(monde, auditeur, c.get("sujet"))
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


def _affirmer(travail, auditeur, sujet, attribut, valeur, faits):
    from .echanges import affirmer
    nom = travail.objets[auditeur]["nom"]
    issue = affirmer(travail, "joueur", auditeur, sujet, attribut, valeur)
    faits.append({
        "dementi": f"{nom} sait de ses propres yeux que c'est faux et cesse de te croire fiable.",
        "doute": f"{nom} ne te croit pas ({_phrase(travail, sujet, attribut, valeur)}).",
        "decouvert": f"{nom} voit bien que c'est faux et cesse de te croire fiable.",
        "crue": f"{nom} te croit : il tient désormais pour vrai que {_phrase(travail, sujet, attribut, valeur)}.",
    }[issue])


def _demander(travail, auditeur, objet, faits):
    from .echanges import demander
    nom = travail.objets[auditeur]["nom"]
    from .deliberation import besoin_de_part
    issue = demander(travail, "joueur", auditeur, objet)
    o = designer(travail.objets[objet]) if objet in travail.objets else ""
    vivres = objet in travail.objets and besoin_de_part(travail.objets[objet]) == "faim"
    faits.append({
        "absent": f"{nom} n'a pas cet objet sur lui.",
        "mefiance": f"{nom} refuse : il ne te fait pas confiance.",
        "necessaire": f"{nom} refuse de se séparer de {o}, qui lui sert.",
        "refus": f"{nom} n'est pas convaincu et garde {o}.",
        "remis": f"{nom} te remet {o}.",
        "promis": (f"{nom} accepte de t'en donner une part : il te la servira là où sont les vivres."
                   if vivres else f"{nom} accepte : il va entretenir le feu."),
        "impossible": f"{nom} ne voit pas comment te donner {o}.",
    }[issue])


def _demander_passage(travail, auditeur, faits):
    from .passage import demander_passage
    o = travail.objets[auditeur]
    nom, il = o["nom"], "elle" if o.get("genre") == "f" else "il"
    e = "e" if o.get("genre") == "f" else ""
    issue = demander_passage(travail, auditeur, "joueur", [])
    faits.append({
        "ecarte": f"{nom} s'écarte d'un pas pour te laisser passer.",
        "geste": f"{nom} ne s'écarte pas : {il} est occupé{e} à ce qu'{il} fait là.",
        "mefiance": f"{nom} refuse de s'écarter : {il} ne te fait pas confiance.",
        "place": f"{nom} n'a pas la place de s'écarter.",
        "refus": f"{nom} n'est pas convaincu{e} et reste où {il} est.",
        "inutile": f"{nom} ne te barre pas le passage.",
    }[issue])


def preparer_parole(monde, p, revision=None):
    from .dialogues import interlocuteurs
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant la fin de la conversation.", "re-propose à partir des faits actuels.")
    if (not isinstance(p, dict) or not set(SCHEMA_PAROLE["required"]) <= set(p)
            or not isinstance(p["replique"], str) or not 1 <= len(p["replique"].strip()) <= 400
            or not isinstance(p["contenu"], list) or len(p["contenu"]) > 3
            or set(p) - set(SCHEMA_PAROLE["required"]) - {"_intention"}):
        recus = sorted(k for k in p if k != "_intention") if isinstance(p, dict) else type(p).__name__
        raise ErreurMonde("Parole mal formée.",
                          f"parole_joueur a exactement les champs {', '.join(SCHEMA_PAROLE['required'])} ; replique de "
                          f"1 à 400 caractères ; contenu : liste de 0 à 3 éléments ; reçu : {recus}.")
    auditeur = p["personnage"]
    nomme = destinataire_nomme(monde, p.get("_intention", ""))
    if nomme and nomme != auditeur:
        # Le joueur choisit à qui Corvus parle : le MJ ne lui substitue personne.
        raise ErreurMonde("Tu t'adresses à " + designer(monde.objets[nomme]) + ".",
                          f"personnage = {nomme}, que le joueur interpelle ; s'il n'est pas là pour entendre, "
                          "réponds en mode dialogue, sans parler à un autre à sa place.")
    presents = sorted(interlocuteurs(monde))
    if auditeur not in presents:
        raise ErreurMonde("Ce personnage n'est pas ici pour t'entendre.",
                          f"{auditeur} n'est pas là pour entendre Corvus : réponds en mode dialogue qu'il est trop "
                          "loin ; ne fais pas parler Corvus à un autre personnage à sa place.")
    from . import lexique
    replique = p["replique"].strip()
    # La réplique affichée obéit au contrôle des mentions : rien que Corvus ne connaisse.
    fondement = lexique.corpus(monde.contexte(), monde.data.get("conversation", []),
                               monde.data.get("paroles_joueur", []))
    if p.get("_intention"):
        fondement += " " + lexique.corpus(p["_intention"])
    # Une part demandée à son propriétaire se nomme sans avoir été vue.
    for c in p["contenu"]:
        if isinstance(c, dict) and c.get("type") == "demande":
            part = part_nommee(monde, auditeur, c.get("sujet"))
            if part:
                o = monde.objets[part]
                fondement += " " + " ".join([o["nom"], *o.get("aliases", [])])
    inconnus = lexique.mentions_sans_fondement(monde, replique, fondement)
    if inconnus:
        raise ErreurMonde("La réplique de Corvus nomme ce qu'il ne connaît pas.",
                          "retire de replique : " + ", ".join(f"« {m['terme']} »" for m in inconnus)
                          + " (Corvus ne l'a ni vu ni entendu nommer) ; garde les mots du joueur.")
    travail = monde.copier()
    stats_auditeur = _stats_pnj(travail, auditeur)
    capacite = min(capacite_transmission(_stats_pnj(travail, "joueur")["INT"]),
                   capacite_transmission(stats_auditeur["INT"]))
    faits = []
    transmis = [x for x in (_typer(travail, c, auditeur) for c in p["contenu"]) if x]
    perdus = transmis[capacite:]
    for c in transmis[:capacite]:
        if c["type"] == "affirmation":
            _affirmer(travail, auditeur, c["sujet"], c["attribut"], c["valeur"], faits)
        elif c["type"] == "passage":
            _demander_passage(travail, auditeur, faits)
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
