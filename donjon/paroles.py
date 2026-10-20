"""Paroles du joueur aux PNJ : à qui, comment, réplique selon INT et CHA, contenu typé, croyances.

Le joueur écrit ce qu'il veut faire dire à Corvus. Le moteur lit dans sa saisie la forme de la
parole (``analyser``) et en fixe les destinataires (``destinataires``) : celui qu'il nomme, sinon
celui qui est en face de lui ; « à tous », tous ceux qui l'entendent ; un chuchotement, un seul,
au contact. Il fixe la bande d'expression (précision selon l'INT, aisance selon le CHA) ; Luna
écrit la réplique dans cette bande et type son contenu : affirmations (sujet, attribut, valeur),
demandes d'objet, demandes de passage (s'écarter, laisser passer), aveux, simples propos.
Des mots imposés par le joueur (entre guillemets, après un deux-points, une interpellation) sont
dits mot pour mot. L'effet ne dépend jamais des mots choisis par Luna : le moteur le calcule sur
le contenu typé, les caractéristiques, la confiance de l'auditeur et un jet de CHA. Une INT
faible, chez celui qui parle ou chez celui qui écoute, réduit ce qui est transmis. Une
affirmation démentie par ce que le PNJ perçoit ou a vu récemment est rejetée et il cesse de
croire le joueur fiable. Tous ceux qui saisissent les mots d'une parole à voix haute la
retiennent, destinataires ou non (``ouie``, ``social.retenir_parole``) ; seuls ses destinataires
y répondent.
"""
import copy
import re

from .esprits import RECENT, croire, esprit, lire, memoriser, percevoir
from .francais import designer
from .monde import ErreurMonde, normaliser

ATTRIBUTS = ("lieu", "verrouillee", "fiable")
TYPES = ("propos", "affirmation", "demande", "passage", "aveu")
SCHEMA_PAROLE = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "personnage": {"type": "string",
                       "description": "parole_prevue.personnage : le destinataire fixé par le moteur, ou tous."},
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
proposition = {personnage, replique (ce que Corvus prononce), contenu}, texte vide. Le moteur
fixe à qui Corvus parle et te le donne dans parole_prevue, si la saisie est une parole : celui
que le joueur nomme, sinon celui qui est en face de lui ; « à tous », tous ceux qui l'entendent ;
chuchoter ou murmurer, un seul, au contact. personnage = parole_prevue.personnage (un
identifiant, tous, ou personne quand nul en vue ne l'entend : il parle à la cantonade, et
personne ne lui répond). Une saisie entre guillemets, adressée à tous ou chuchotée est une parole,
même si ses mots annoncent un geste : donner un objet se fait par l'action remettre. Les mots
imposés par le joueur (parole_prevue.mots : entre guillemets, après un deux-points ou une
interpellation comme « Gorm, … ») sont dits tels quels. Sinon,
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
- aveu {sujet : un objet qui n'est pas à Corvus ; attribut vide ; valeur : le geste qu'il avoue
  y avoir fait, parmi prendre, poser, ouvrir, fermer, deverrouiller, verrouiller, crocheter,
  forcer, manger, servir, alimenter, allumer, eteindre} ;
- propos {sujet, attribut et valeur vides} pour tout le reste.
Tous ceux qui en saisissent les mots retiennent une parole à voix haute ; le moteur en a tiré
les conséquences et te renvoie conversation_validee : fais répondre ses destinataires, et eux
seuls, d'après ce résultat, leurs croyances, leurs traits et leurs valeurs
(esprits_interlocuteurs, valeurs de 0 à 100) ; les temoins ont entendu sans être interpellés
et se taisent. Ce qu'un personnage croit n'est pas un fait : il peut le dire, se tromper ou le
taire, et n'avoue son intention que si ses traits s'y prêtent ; il ne ment que si son honnêteté
le permet (jamais à 100).
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
            "engagements": engagements_enregistres(monde, id),
            "a_entendu": paroles_retenues(monde, id),
        }
    return resultat


def paroles_retenues(monde, id):
    """Les dernières paroles que ce personnage a entendues, qu'elles lui fussent adressées ou non :
    qui parlait, à qui, ses mots. Elles attestent qu'elles ont été dites, pas qu'elles sont vraies.
    Une parole qui nomme ce que le joueur ne connaît pas reste tue."""
    from .social import _qui
    retenues = []
    for s in reversed(lire(monde, id)["memoire"]):
        if len(retenues) == 4:
            break
        if s["type"] != "parole":
            continue
        a = s.get("a") or [id]
        if all(_connu_du_joueur(monde, x) for x in [s["locuteur"], *a, *s.get("cites", [])]
               if x == "joueur" or x in monde.objets):
            retenues.append({"de": _qui(monde, s["locuteur"]) if s["locuteur"] in monde.objets
                             or s["locuteur"] == "joueur" else s["locuteur"],
                             "a": [_qui(monde, x) for x in a if x == "joueur" or x in monde.objets],
                             "mots": s["texte"]})
    return retenues[::-1]


def engagements_enregistres(monde, id):
    """Ce que le moteur a enregistré que ce personnage fera : les engagements qu'il a pris (une
    part promise, une tâche acceptée), son intention en cours et les accords de mission qu'il a
    proposés ou conclus. Une réplique ne l'engage à agir que sur l'un d'eux : sa parole établit
    qu'elle a été dite, pas qu'il le fera."""
    from .recit_pnj import but_en_mots
    e = lire(monde, id)
    phrases = [f"engagement pris envers {_nom(monde, x['pour'])} : "
               + but_en_mots(monde, {"type": "pulsion", **x["condition"]}) for x in e["engagements"]]
    if e["intention"]:
        phrases.append("intention en cours : " + but_en_mots(monde, e["intention"]["but"]))
    for mission_id, accord in monde.data.get("engagements", {}).items():
        mission = monde.data.get("missions", {}).get(mission_id)
        if mission and mission["donneur"] == id and accord["statut"] in ("propose", "accepte"):
            objet = designer(monde.objets[mission["objet"]]) if mission["objet"] in monde.objets else mission["objet"]
            phrases.append(f"{'accord conclu' if accord['statut'] == 'accepte' else 'offre faite'} : "
                           f"{accord['montant']} pièces à la remise de {objet}")
    return phrases


def contexte(monde, intention=None):
    from .dialogues import interlocuteurs
    presents = list(interlocuteurs(monde))
    # Une parole sans conteste se dit même sans personne en vue : qui l'entend la retient.
    if not presents and not (intention is not None and analyser(monde, intention)["explicite"]):
        return None
    resultat = {"expression_joueur": bande_expression(monde.joueur["stats"]),
                "esprits_interlocuteurs": esprits_interlocuteurs(monde, presents)}
    if intention is not None:
        resultat["parole_prevue"] = prevue(monde, intention)
    return resultat


def citation(intention):
    """Mots que le joueur impose entre guillemets, s'il y en a."""
    m = re.search(r"[«\"“]\s*(.+?)\s*[»\"”]", intention or "")
    return m.group(1) if m else None


# --- À qui Corvus parle, et comment ------------------------------------------------------------
# Les formes de la parole que l'analyse de la saisie reconnaît, en un seul endroit.
GUILLEMETS = "«\"“"
GROUPE = ("tous", "tout le monde", "vous tous")                 # « à tous : … », « tous, … »
PREPOSITIONS = ("a", "au", "aux")
VERBES_PAROLE = {**dict.fromkeys(("dis", "dit", "dire", "demande", "demander", "parle", "parler", "reponds",
                                  "repondre", "lance", "explique", "annonce", "raconte", "avoue", "confie",
                                  "affirme", "repete"), "voix"),
                 **dict.fromkeys(("chuchote", "chuchoter", "murmure", "murmurer"), "chuchote")}
PRONOMS = {"lui": False, "leur": True}                          # le pronom désigne-t-il un groupe ?
ARTICLES_NOM = ("le ", "la ", "l'", "les ")
VOCATIF = re.compile(r"^\s*([^,!?:«»\"“”]{2,40}?)\s*[,:]\s*\S")
JETON = re.compile(r"[^\W\d_](?:[\w'’-]*\w)?|[:,«»\"“”]")


class ParoleImpossible(ErreurMonde):
    """Un refus qui tient à la saisie (à qui parler, chuchoter de loin ou à plusieurs) : le joueur
    précise ou s'approche ; aucune correction du MJ n'y changerait rien, son message lui est rendu."""


def _personnage(monde, fragment):
    """Le personnage connu du joueur que ``fragment`` nomme exactement (identifiant, nom, prénom,
    alias, avec ou sans article) ; sinon None."""
    texte = normaliser(fragment or "")
    for article in ARTICLES_NOM:
        if texte.startswith(article):
            texte = texte[len(article):]
            break
    if not texte:
        return None
    trouves = {id for id, o in monde.objets.items() if o["type"] == "personnage"
               and texte in {normaliser(n) for n in (id, o["nom"], o["nom"].split(",")[0], *o.get("aliases", []))}
               and _connu_du_joueur(monde, id)}
    return trouves.pop() if len(trouves) == 1 else None


def _interpeller(monde, forme, texte):
    """Une interpellation en tête de ``texte`` (« Brune, … », « à tous : … ») : le personnage nommé
    ou le groupe. Renvoie la longueur d'une adresse marquée par « à », qui n'est pas dite ; 0 sinon."""
    m = VOCATIF.match(texte or "")
    if not m:
        return 0
    tete = m.group(1).strip().split(None, 1)
    marque = len(tete) == 2 and normaliser(tete[0]) in PREPOSITIONS
    nom = tete[1] if marque else m.group(1)
    if normaliser(nom) in GROUPE:
        forme["groupe"] = True
    elif _personnage(monde, nom):
        forme["nomme"] = _personnage(monde, nom)
    else:
        return 0
    return m.end(1) if marque else 0


def _groupe_en(mots, i):
    """Nombre de mots d'une désignation du groupe (« tous », « tout le monde ») à partir de ``i``."""
    for g in sorted(GROUPE, key=len, reverse=True):
        if mots[i:i + len(g.split())] == g.split():
            return len(g.split())
    return 0


def analyser(monde, intention):
    """La forme de la parole que la saisie annonce : manière (voix ou chuchotement), personnage
    nommé ou groupe (« à tous »), pronom (« je lui dis »), mots imposés (entre guillemets, après un
    deux-points ou une interpellation), et si elle est sans conteste une parole (``explicite`` :
    entre guillemets, à tous, chuchotée, mots après un deux-points)."""
    s = (intention or "").strip()
    forme = {"maniere": "voix", "groupe": False, "nomme": None, "pronom": False, "mots": None, "explicite": False}
    if s[:1] in GUILLEMETS:
        forme.update(explicite=True, mots=citation(s) or s.strip("«»\"“” ") or None)
        _interpeller(monde, forme, forme["mots"])
        return forme
    jetons = list(JETON.finditer(s))
    mots = [normaliser(j.group()) for j in jetons]
    i = 1 if mots[:1] == ["je"] else 0
    if len(mots) > i + 1 and mots[i] in PRONOMS and mots[i + 1] in VERBES_PAROLE:
        forme["groupe"], forme["pronom"] = PRONOMS[mots[i]], not PRONOMS[mots[i]]
        i += 1
    if i < len(mots) and mots[i] in VERBES_PAROLE:
        forme["maniere"] = VERBES_PAROLE[mots[i]]
        i += 1
        if i < len(mots) and mots[i] in PREPOSITIONS:
            n = _groupe_en(mots, i + 1)
            if n:
                forme["groupe"], i = True, i + 1 + n
            else:
                for k in range(min(4, len(jetons) - i - 1), 0, -1):
                    id = _personnage(monde, s[jetons[i + 1].start():jetons[i + k].end()])
                    if id:
                        forme["nomme"], i = id, i + 1 + k
                        break
        if i < len(jetons) and jetons[i].group() == ":":
            reste = s[jetons[i].end():].strip()
            forme.update(explicite=True, mots=(citation(reste) if reste[:1] in GUILLEMETS else reste) or None)
    else:
        debut = _interpeller(monde, forme, s)
        if forme["groupe"] or forme["nomme"]:
            forme["mots"] = s[debut:].lstrip(" ,:") or None if debut else s
    if forme["mots"] is None and citation(s):
        forme["mots"] = citation(s)
        if not (forme["groupe"] or forme["nomme"]):
            _interpeller(monde, forme, forme["mots"])
    if forme["groupe"] or forme["maniere"] == "chuchote":
        forme["explicite"] = True
    return forme


def _nom_court(monde, id):
    return monde.objets[id]["nom"].split(",")[0]


def _contact(monde, id):
    """Au contact de Corvus (une case voisine) ; sans cases, quiconque est là."""
    if not monde.data.get("mode_cases"):
        return True
    from .passage import au_contact
    return au_contact(monde, "joueur", id)


def _face(monde, id):
    """(hors de son regard, distance) : le plus petit est celui à qui Corvus fait face."""
    from .ouie import distance
    from .spatial import dans_le_regard
    o, j = monde.objets[id], monde.joueur
    if not monde.data.get("mode_cases") or o.get("position") is None or j.get("position") is None:
        return 0, 0
    regard = dans_le_regard(monde, o["lieu"], tuple(o["position"]), "joueur")
    return (0 if regard else 1), (distance(tuple(o["position"]), tuple(j["position"])) if o["lieu"] == j["salle"] else 99)


def en_face(monde, candidats, pronom=False):
    """Celui à qui Corvus parle sans le nommer, parmi ``candidats`` : celui que désigne un pronom
    (« je lui dis »), s'il est le dernier à qui il a parlé ; sinon celui qu'il a sous les yeux, le
    plus proche. À égalité, le joueur précise."""
    from .refus import liste
    derniere = (monde.data.get("paroles_joueur") or [None])[-1]
    if pronom and derniere:
        auditeurs = derniere.get("auditeurs") or [derniere["auditeur"]]
        if len(auditeurs) == 1 and auditeurs[0] in candidats:
            return auditeurs[0]
    rangs = {id: _face(monde, id) for id in candidats}
    face = sorted(id for id, r in rangs.items() if r == min(rangs.values()))
    if len(face) > 1:
        noms = ", ".join(_nom_court(monde, x) for x in face[:-1]) + " et " + _nom_court(monde, face[-1])
        raise ParoleImpossible(f"{noms} sont aussi près de toi l'un que l'autre : précise à qui tu parles "
                               f"(« {_nom_court(monde, face[0])}, … »), ou parle à tous (« à tous : … »).",
                               f"destinataire ambigu entre {liste(face)} : le joueur doit le nommer ; réponds en "
                               "mode dialogue, sans choisir à sa place.")
    return face[0]


def destinataires(monde, forme):
    """Ceux à qui s'adresse la parole que décrit ``forme`` (``analyser``) : celui que le joueur
    nomme, sinon celui qui est en face de lui, à portée de voix ; à tous, tous les présents qui en
    saisiraient les mots ; un chuchotement, un seul, au contact. Une parole sans conteste (à tous,
    entre guillemets…) que nul présent ne saisirait est dite à la cantonade : aucun destinataire,
    qui l'entend la retient. ParoleImpossible si le joueur doit préciser ou s'approcher."""
    from .dialogues import interlocuteurs
    from .ouie import saisissent
    from .refus import liste
    presents = sorted(interlocuteurs(monde))
    chuchote = forme["maniere"] == "chuchote"
    cantonade = forme["explicite"] and not forme["nomme"] and not chuchote
    if not presents and not cantonade:
        raise ParoleImpossible("Il n'y a personne ici pour t'entendre.",
                               "aucun interlocuteur présent : réponds en mode dialogue.")
    if forme["groupe"] and chuchote:
        raise ParoleImpossible("On ne chuchote qu'à une seule personne, à son oreille.",
                               "chuchoter : un seul destinataire, nommé ou en face, au contact ; à plusieurs, "
                               "Corvus parle à voix haute (« à tous : … »).")
    nets = saisissent(monde, "joueur")
    entendent = [id for id in presents if id in nets]
    contact = [id for id in presents if _contact(monde, id)]
    if forme["groupe"]:
        return entendent
    id = forme["nomme"]
    if id and id not in presents:
        raise ParoleImpossible("Ce personnage n'est pas ici pour t'entendre.",
                               f"{id} n'est pas là pour entendre Corvus : réponds en mode dialogue qu'il est trop "
                               "loin ; ne fais pas parler Corvus à un autre personnage à sa place.")
    if id and chuchote and id not in contact:
        raise ParoleImpossible(f"{_nom_court(monde, id)} est trop loin : approche-toi pour lui chuchoter quoi que "
                               "ce soit.", f"chuchoter exige le contact (une case voisine) avec {id} ; au contact de "
                               f"Corvus : {liste(contact)}.")
    if id and not chuchote and id not in entendent:
        raise ParoleImpossible(f"{_nom_court(monde, id)} est trop loin pour t'entendre.",
                               f"{id} ne saisirait pas les mots de Corvus d'ici ; à portée de voix : "
                               f"{liste(entendent)}.")
    if id:
        return [id]
    candidats = contact if chuchote else entendent
    if not candidats and cantonade:
        return []
    if not candidats:
        raise ParoleImpossible("Personne n'est assez près de toi pour que tu lui chuchotes quoi que ce soit."
                               if chuchote else "Personne n'est assez près pour t'entendre.",
                               f"{'au contact' if chuchote else 'à portée de voix'} : personne parmi les présents "
                               f"({liste(presents)}) ; réponds en mode dialogue.")
    return [en_face(monde, candidats, forme["pronom"])]


def prevue(monde, intention):
    """Ce que le moteur fixe de la parole que la saisie annonce, pour Luna (``parole_prevue``)."""
    forme = analyser(monde, intention)
    try:
        dest = destinataires(monde, forme)
    except ParoleImpossible as exc:
        return {"impossible": str(exc)}
    return {"personnage": personnage(forme, dest), "destinataires": dest,
            "maniere": "chuchotement" if forme["maniere"] == "chuchote" else "à voix haute",
            **({"mots": forme["mots"]} if forme["mots"] else {})}


def personnage(forme, dest):
    """Le champ personnage qu'attend le moteur : un identifiant, tous, ou personne (à la cantonade)."""
    return "tous" if forme["groupe"] else dest[0] if dest else "personne"


def annonce(monde, rapport):
    """Ce que le joueur lit de sa propre parole : à qui, et comment."""
    verbe = "chuchotes" if rapport.get("maniere") == "chuchotement" else "dis"
    if rapport["personnage"] == "personne":
        return f"Tu {verbe} : « {rapport['replique_joueur']} »"
    a = "tous" if rapport["personnage"] == "tous" else _nom_court(monde, rapport["personnage"])
    return f"Tu {verbe} à {a} : « {rapport['replique_joueur']} »"


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
    if not isinstance(c, dict) or c.get("type") not in ("affirmation", "demande", "aveu"):
        return None
    sujet = resoudre(monde, c.get("sujet"))
    if sujet is None and c["type"] == "demande" and auditeur:
        sujet = part_nommee(monde, auditeur, c.get("sujet"))
    if sujet is None:
        return None
    if c["type"] == "demande":
        return {"type": "demande", "sujet": sujet}
    if c["type"] == "aveu":
        return aveu(monde, "joueur", sujet, normaliser(c.get("valeur") or ""))
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


def aveu(monde, locuteur, objet, geste):
    """L'aveu typé d'un geste illicite (``social.GESTES``) fait par ``locuteur`` sur un objet qui
    appartient à un autre, ou None : avouer un geste permis n'apprend rien de lui."""
    from .social import GESTES
    from .vol import proprietaire
    o = monde.objets.get(objet)
    if not o or o["type"] == "personnage" or geste not in GESTES or proprietaire(monde, o) in (None, locuteur):
        return None
    return {"type": "aveu", "evenement": {"type": "vu_agir", "auteur": locuteur, "operation": geste, "objet": objet}}


def _avouer(travail, auditeur, c, faits):
    from .social import recevoir
    o = travail.objets[auditeur]
    il = "elle" if o.get("genre") == "f" else "il"
    issue = recevoir(travail, auditeur, "joueur", c)
    faits.append(f"{o['nom']} l'entend : {il} ne te tient plus pour fiable." if issue
                 else f"{o['nom']} le savait déjà.")


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
    # Le moteur fixe à qui Corvus parle : le MJ ne lui substitue personne.
    forme = analyser(monde, p.get("_intention", ""))
    dest = destinataires(monde, forme)
    attendu = personnage(forme, dest)
    if p["personnage"] != attendu:
        raise ErreurMonde("Tu t'adresses à tous ceux qui t'entendent." if forme["groupe"]
                          else "Tu ne t'adresses à personne en particulier." if not dest
                          else "Tu t'adresses à " + designer(monde.objets[attendu]) + ".",
                          f"personnage = {attendu} (parole_prevue.personnage : "
                          + ("tous ceux qui entendent Corvus" if forme["groupe"] else
                             "personne en vue : il parle à la cantonade" if not dest else
                             "celui que le joueur nomme, sinon celui qui est en face de Corvus")
                          + ") ; s'il n'est pas là pour entendre, réponds en mode dialogue, sans parler à un autre "
                          "à sa place.")
    from . import lexique
    replique = p["replique"].strip()
    # La réplique affichée obéit au contrôle des mentions : rien que Corvus ne connaisse.
    fondement = lexique.corpus(monde.contexte(), monde.data.get("conversation", []),
                               monde.data.get("paroles_joueur", []))
    if p.get("_intention"):
        fondement += " " + lexique.corpus(p["_intention"])
    # Une part demandée à son propriétaire se nomme sans avoir été vue.
    for c in p["contenu"]:
        for auditeur in dest:
            part = part_nommee(monde, auditeur, c.get("sujet")) if isinstance(c, dict) and c.get("type") == "demande" \
                else None
            if part:
                o = monde.objets[part]
                fondement += " " + " ".join([o["nom"], *o.get("aliases", [])])
    inconnus = lexique.mentions_sans_fondement(monde, replique, fondement)
    if inconnus:
        raise ErreurMonde("La réplique de Corvus nomme ce qu'il ne connaît pas.",
                          "retire de replique : " + ", ".join(f"« {m['terme']} »" for m in inconnus)
                          + " (Corvus ne l'a ni vu ni entendu nommer) ; garde les mots du joueur.")
    from .ouie import retentir, saisissent
    travail = monde.copier()
    chuchote = forme["maniere"] == "chuchote"
    # Ce qu'en retient qui l'entend sans en être le destinataire : ce qui ne s'adresse pas qu'à lui.
    publics = [x for x in (_typer(travail, c) for c in p["contenu"]) if x and x["type"] in ("affirmation", "aveu")]
    temoins = [] if chuchote else sorted(id for id in saisissent(travail, "joueur")
                                         if id not in dest and travail.objets[id].get("profil"))
    expression = capacite_transmission(_stats_pnj(travail, "joueur")["INT"])
    faits = []
    for auditeur in dest:
        capacite = min(expression, capacite_transmission(_stats_pnj(travail, auditeur)["INT"]))
        transmis = [x for x in (_typer(travail, c, auditeur) for c in p["contenu"]) if x]
        for c in transmis[:capacite]:
            if c["type"] == "affirmation":
                _affirmer(travail, auditeur, c["sujet"], c["attribut"], c["valeur"], faits)
            elif c["type"] == "passage":
                _demander_passage(travail, auditeur, faits)
            elif c["type"] == "aveu":
                _avouer(travail, auditeur, c, faits)
            else:
                _demander(travail, auditeur, c["sujet"], faits)
        if transmis[capacite:]:
            faits.append(f"{travail.objets[auditeur]['nom']} ne retient pas tout : une partie de ce que tu as dit se perd.")
        memoriser(travail, auditeur, {"type": "parole", "locuteur": "joueur", "a": list(dest), "texte": replique[:240],
                                      "cites": []})
    # Sa voix retentit : qui en saisit les mots la retient (``ouie``) ; un chuchotement ne va qu'à son destinataire.
    retentir(travail, "joueur", "chuchoter" if chuchote else "parler", texte=replique,
             parole=None if chuchote else {"a": list(dest), "contenu": publics})
    travail.data["revision"] += 1
    travail.data.setdefault("paroles_joueur", []).append(
        {"revision": travail.data["revision"], "auditeur": attendu, "auditeurs": list(dest), "texte": replique,
         "minute": travail.data["minutes"]})
    travail.data["paroles_joueur"] = travail.data["paroles_joueur"][-40:]
    travail.verifier()
    presents = interlocuteurs(monde)
    rapport = {"personnage": attendu, "destinataires": list(dest),
               "temoins": [id for id in temoins if id in presents],
               "maniere": "chuchotement" if chuchote else "à voix haute", "sujet": replique,
               "operation": "parole_joueur", "replique_joueur": replique, "faits": faits}
    return travail, rapport
