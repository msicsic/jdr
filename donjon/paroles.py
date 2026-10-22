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

from . import relations
from .esprits import RECENT, croire, croyance, esprit, lire, memoriser, percevoir
from .francais import complement_de, designer, lieu
from .monde import ErreurMonde, normaliser
from .relations import FIABLE

ATTRIBUTS = ("lieu", "verrouillee", FIABLE)
TYPES = ("propos", "affirmation", "demande", "passage", "aveu", "nom", "qui", "reclamer", "ressource")
BESOINS_DEMANDES = ("faim", "chaleur")   # ce qu'une demande « ressource » cherche (``echanges.enqueter``)
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
chuchoter ou murmurer, un seul, au contact ; un nom détaché par une virgule, où qu'il soit
(« …, X ? »), désigne celui à qui il parle. personnage =
parole_prevue.personnage (un identifiant, tous, ou personne quand nul en vue ne l'entend : il parle
à la cantonade ; qui l'entend sans qu'il le sache là peut répondre à une question, le moteur le dit). Une saisie qui commence par des guillemets, par un verbe de parole (« je
dis… », « je lui dis… », « je demande à Gorm… », « je chuchote… ») ou par « à tous » est une
parole, même si ses mots annoncent un geste : donner un objet se fait par l'action remettre ; ce
qu'elle demande au personnage est son contenu. Une interpellation sans guillemets (« Aubin, … »)
est à interpréter : question, geste ou parole. Les mots
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
  dont Corvus demande une part ; attribut vide ; valeur : vide, ou le nombre de pièces que
  Corvus offre pour la payer (en chiffres, au plus ce qu'il a)} ; payée son prix, c'est un achat ;
- passage {sujet et attribut vides ; valeur : vide, ou les pièces que Corvus offre} : Corvus
  demande au personnage de s'écarter, de se pousser, de le laisser passer. Le moteur décide s'il
  bouge, et s'il prend l'argent, et le dit dans les faits ; sa réplique dit cette issue, sans
  promettre de bouger plus tard ;
- aveu {sujet : un objet qui n'est pas à Corvus ; attribut vide ; valeur : le geste qu'il avoue
  y avoir fait, parmi prendre, poser, ouvrir, fermer, deverrouiller, verrouiller, crocheter,
  forcer, manger, servir, alimenter, allumer, eteindre} ;
- nom {sujet : joueur quand Corvus se nomme, ou le personnage dont il se donne le nom (« C'est moi,
  X » : X) ; attribut et valeur vides} : le nom que disent ses mots ; l'auditeur pèse ce nom
  (il peut connaître la vraie voix) ;
- qui {sujet, attribut et valeur vides} : Corvus demande qui parle (« Qui va là ? ») ;
- reclamer {sujet : vide pour les pièces que le personnage doit à Corvus, ou un objet de Corvus que le
  personnage porte ; attribut et valeur vides} : Corvus réclame son dû ; le moteur dit si le
  personnage rend, ce qu'il rend, ou qu'il ne doit rien ;
- ressource {sujet : faim (de quoi manger) ou chaleur (du bois) ; attribut et valeur vides} : Corvus
  demande au personnage s'il en a, sans savoir ce qu'il a ; le moteur dit ce que le personnage répond ;
- propos {sujet, attribut et valeur vides} pour tout le reste.
Une voix inconnue (interlocuteur voix_<n>) : Corvus l'entend sans savoir à qui elle est ; ce
qu'elle dit d'elle-même n'est que ce qu'elle prétend. Ne lui donne pas d'autre nom que le sien
(« une voix inconnue », « une voix qui se dit … »).
Tous ceux qui en saisissent les mots retiennent une parole à voix haute ; le moteur en a tiré
les conséquences et te renvoie conversation_validee : fais répondre ceux de repondent, et eux
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
    l'auditeur abaisse ou relève et que sa volonté (VOL) élève ; caractéristiques modulées. La
    confiance est celle qu'il porte à qui il croit entendre (``relations.percue``) : une voix qu'il ne
    sait à qui prêter est un étranger, et sa demande pèse moins (``voix.INCONNU``), même nommée."""
    from .caractere import modificateur
    from .relations import confiance, mefiance, percue
    from .voix import INCONNU, identifie
    relation = percue(monde, auditeur, locuteur)
    dd = (dd_base + (-2 if confiance(relation) else 6 if mefiance(relation) else 2)
          + (0 if identifie(monde, auditeur, locuteur) else INCONNU)
          + modificateur(monde, auditeur, "VOL"))
    return monde.d20() + modificateur(monde, locuteur, "CHA") + modificateur(monde, locuteur, "ELO") >= dd, dd


def dementi(monde, auditeur, sujet, attribut, valeur):
    """Ce que l'auditeur a vu ou essayé récemment contredit-il ce qu'on lui dit ? Ne pas avoir
    trouvé un objet là où on l'attendait ne contredit pas qu'il soit ailleurs."""
    actuelle = croyance(monde, auditeur, sujet, attribut)
    return bool(actuelle and actuelle["source"] in ("vu", "essai") and actuelle["valeur"] != valeur
                and not (attribut == "lieu" and actuelle["valeur"] is None)
                and monde.data["minutes"] - actuelle["minute"] <= RECENT)


def _nom(monde, id):
    if id == "joueur":
        return "toi"
    if id in monde.data["salles"]:
        return lieu(monde.data["salles"][id])
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
    if attribut == FIABLE:
        pluriel = "s" if o.get("pluriel") else ""
        return f"{_nom(monde, sujet)} {est} {'digne' + pluriel + ' de confiance' if valeur else 'peu fiable' + pluriel}"
    return ""


def _ouidire(monde, source):
    """D'où il tient une croyance rapportée, nommé seulement si le joueur connaît ce témoin et que
    le personnage savait qui le lui disait."""
    if source == "se_dit":
        return " (une voix le lui a dit d'elle-même)"
    if not source.startswith("dit:"):
        return ""
    from .voix import auteur_dit
    locuteur, inconnue = auteur_dit(source)
    if inconnue:
        return " (une voix inconnue le lui a dit)"
    if locuteur == "joueur":
        return " (tu le lui as dit)"
    if locuteur in monde.objets and _connu_du_joueur(monde, locuteur):
        return f" ({monde.objets[locuteur]['nom'].split(',')[0]} le lui a dit)"
    return " (on le lui a dit)"


def esprits_interlocuteurs(monde, presents):
    """Ce que Luna peut savoir d'un PNJ présent pour lui donner une voix : ses croyances, pas la
    vérité ; sous la désignation du joueur (``voix.designation``). D'une voix que le joueur ne sait
    à qui prêter, rien qui la trahisse : ni traits, ni croyances, seulement ce qu'elle prétend et le
    genre où elle parle d'elle-même (``voix.genre``)."""
    from .deliberation import urgents
    from .voix import designation, genre, nom_pour_joueur
    resultat = {}
    for id in presents:
        cle = designation(monde, id)
        if cle != id:
            resultat[cle] = {"voix_inconnue": nom_pour_joueur(monde, id), "genre": genre(monde, id),
                             "traits": "", "valeurs": {}, "croit": [],
                             "but_actuel": None, "besoins_pressants": [], "engagements": [], "a_entendu": []}
            continue
        e, profil = lire(monde, id), monde.objets[id].get("profil")
        croyances = []
        for sujet, attributs in e["croyances"].items():
            for attribut, c in attributs.items():
                if attribut in ATTRIBUTS and attribut != FIABLE and (sujet == "joueur" or sujet in monde.objets):
                    croyances.append((not c["source"].startswith("dit:"), -c["minute"],
                                      f"croit que {_phrase(monde, sujet, attribut, c['valeur'])}"
                                      + _ouidire(monde, c["source"])))
        # Ce qu'il dirait de chacun, avec d'où il le tient (``relations``).
        for autre in relations.connus(monde, id):
            avis, r = relations.fiable(monde, id, autre), relations.envers(monde, id, autre)
            if avis is not None and (autre == "joueur" or autre in monde.objets):
                croyances.append((not r["source"].startswith("dit:"), -r["minute"],
                                  f"croit que {_phrase(monde, autre, FIABLE, avis)}" + _ouidire(monde, r["source"])))
        resultat[cle] = {
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
        inconnue = s.get("voix_inconnue")  # Il ne savait à qui était cette voix : il ne la nomme pas.
        if all(_connu_du_joueur(monde, x) for x in [*([] if inconnue else [s["locuteur"]]), *a, *s.get("cites", [])]
               if x == "joueur" or x in monde.objets):
            retenues.append({"de": "une voix inconnue" if inconnue else _qui(monde, s["locuteur"])
                             if s["locuteur"] in monde.objets or s["locuteur"] == "joueur" else s["locuteur"],
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
    # Celui qu'il nomme dans son dos : la parole le tournera vers lui, et le MJ le connaît déjà ainsi.
    vers = regard(monde, analyser(monde, intention)) if intention is not None else None
    if vers:
        monde = tourne(monde, vers)
    from .voix import reel
    presents = [reel(monde, d) for d in interlocuteurs(monde)]
    # Une parole sans conteste, ou une question (« il y a quelqu'un ? »), se dit même sans personne en vue :
    # qui l'entend la retient, et y répond s'il le veut (``repondants``).
    from .commandes import est_question
    if not presents and not (intention is not None and (analyser(monde, intention)["explicite"]
                                                        or est_question(intention))):
        return None
    resultat = {"expression_joueur": bande_expression(monde.joueur["stats"]),
                "esprits_interlocuteurs": esprits_interlocuteurs(monde, presents)}
    if intention is not None:
        resultat["parole_prevue"] = {**prevue(monde, intention), **({"regard": vers} if vers else {})}
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
# Verbes de parole qui disent aussi un geste (« je lance la pierre ») : une parole seulement avec un
# destinataire ou un deux-points (« je lance à tous : … »).
GESTES_HOMONYMES = ("lance",)
PRONOMS = {"lui": False, "leur": True}                        # le pronom désigne-t-il un groupe ?
ARTICLES_NOM = ("le ", "la ", "l'", "les ")
JETON = re.compile(r"[^\W\d_](?:[\w'’-]*\w)?|[:,«»\"“”]")


class ParoleImpossible(ErreurMonde):
    """Un refus qui tient à la saisie (à qui parler, chuchoter de loin ou à plusieurs) : le joueur
    précise ou s'approche ; aucune correction du MJ n'y changerait rien, son message lui est rendu."""


def _personnage(monde, fragment, connu=True):
    """Le personnage connu du joueur que ``fragment`` nomme exactement (identifiant, nom, prénom,
    alias, avec ou sans article) ; sinon None. ``connu=False`` : n'importe quel personnage du monde,
    pour un nom que Corvus prononce sans savoir à qui il est (une imposture, un nom inconnu)."""
    texte = normaliser(fragment or "")
    for article in ARTICLES_NOM:
        if texte.startswith(article):
            texte = texte[len(article):]
            break
    if not texte:
        return None
    trouves = {id for id, o in monde.objets.items() if o["type"] == "personnage"
               and texte in {normaliser(n) for n in (id, o["nom"], o["nom"].split(",")[0], *o.get("aliases", []))}
               and (not connu or _connu_du_joueur(monde, id))}
    return trouves.pop() if len(trouves) == 1 else None


# Un nom détaché par une virgule, où qu'il soit dans la phrase, désigne celui à qui l'on parle
# (« Ilse, as-tu… ? », « as-tu de quoi manger, Ilse ? », « dis-moi, Ilse, … ») ; après « moi », c'est
# celui qui parle qui se nomme (« c'est moi, Brune »), pas un vocatif.
CITATION_ENTIERE = re.compile(r"[«\"“][^»\"”]*[»\"”]")
DELIMITEURS = re.compile(r"[,;:!?.…]")


def _vocatifs(texte):
    """Les fragments de ``texte`` qu'une virgule détache (``DELIMITEURS``), seuls entre deux
    ponctuations dont au moins une virgule, hors citation : (fragment, en tête). Un fragment qui suit
    « moi, » est une apposition à celui qui parle. En tête, un deux-points détache aussi (« à tous : »)."""
    texte = CITATION_ENTIERE.sub(lambda m: "\x00" * len(m.group()), texte or "")
    bornes = [(-1, "")] + [(m.start(), m.group()) for m in DELIMITEURS.finditer(texte)] + [(len(texte), "")]
    resultat = []
    for (debut, avant), (fin, apres) in zip(bornes, bornes[1:]):
        fragment = texte[debut + 1:fin].strip()
        tete = debut < 0
        if not fragment or "\x00" in fragment or not ("," in (avant, apres) or tete and apres == ":"):
            continue
        precedent = normaliser(texte[:max(debut, 0)]).split()
        if avant == "," and precedent[-1:] == ["moi"]:
            continue  # « c'est moi, Brune » : il se nomme.
        resultat.append((fragment, tete))
    return resultat


def _interpeller(monde, forme, texte):
    """Une interpellation dans ``texte`` (« Brune, … », « …, Brune ? », « à tous : … ») : le personnage
    nommé ou le groupe ; un nom de personnage que Corvus ne connaît pas (``inconnu``). Renvoie la
    longueur d'une adresse en tête marquée par « à », qui n'est pas dite ; 0 sinon."""
    inconnu = None
    for fragment, tete in _vocatifs(texte):
        mots = fragment.split(None, 1)
        marque = tete and len(mots) == 2 and normaliser(mots[0]) in PREPOSITIONS
        nom = mots[1] if marque else fragment
        if normaliser(nom) in GROUPE:
            forme["groupe"] = True
        elif _personnage(monde, nom):
            forme["nomme"] = _personnage(monde, nom)
        else:
            inconnu = inconnu or (nom if _personnage(monde, nom, connu=False) else None)
            continue
        forme["inconnu"] = None
        return (texte.index(fragment) + len(fragment)) if marque else 0
    if inconnu:
        forme["inconnu"] = inconnu
    return 0


def _groupe_en(mots, i):
    """Nombre de mots d'une désignation du groupe (« tous », « tout le monde ») à partir de ``i``."""
    for g in sorted(GROUPE, key=len, reverse=True):
        if mots[i:i + len(g.split())] == g.split():
            return len(g.split())
    return 0


def analyser(monde, intention):
    """La forme de la parole que la saisie annonce : manière (voix ou chuchotement), personnage
    nommé ou groupe (« à tous »), suite de l'échange (``suite`` : « lui », « leur », ou « echange »
    pour des mots entre guillemets sans interpellation), mots imposés (entre guillemets, après un
    deux-points ou une interpellation), et si elle est sans conteste une parole (``explicite`` :
    elle commence par des guillemets, par un verbe de parole — « je dis… », « je lui dis… », « je
    demande à Gorm… », « je chuchote… » — ou par « à tous »). Une parole sans conteste passe par
    le moteur, qui la fait entendre : le MJ ne la raconte pas lui-même et ne la change pas en geste.
    Une interpellation sans guillemets (« Aubin, viens m'aider ») n'en est pas une : le MJ
    l'interprète librement (question, geste ou parole)."""
    s = (intention or "").strip()
    forme = {"maniere": "voix", "groupe": False, "nomme": None, "inconnu": None, "suite": False, "mots": None,
             "explicite": False}
    if s[:1] in GUILLEMETS:
        forme.update(explicite=True, mots=citation(s) or s.strip("«»\"“” ") or None)
        _interpeller(monde, forme, forme["mots"])
        forme["suite"] = "echange" if not (forme["groupe"] or forme["nomme"]) else False
        return forme
    jetons = list(JETON.finditer(s))
    mots = [normaliser(j.group()) for j in jetons]
    i = 1 if mots[:1] == ["je"] else 0
    if len(mots) > i + 1 and mots[i] in PRONOMS and mots[i + 1] in VERBES_PAROLE:
        forme["groupe"], forme["suite"] = PRONOMS[mots[i]], "leur" if PRONOMS[mots[i]] else "lui"
        i += 1
    if i < len(mots) and mots[i] in VERBES_PAROLE:
        forme["maniere"] = VERBES_PAROLE[mots[i]]
        homonyme = mots[i] in GESTES_HOMONYMES
        i += 1
        if i < len(mots) and mots[i] in PREPOSITIONS:
            n = _groupe_en(mots, i + 1)
            if n:
                forme["groupe"], i = True, i + 1 + n
            else:
                for connu in (True, False):
                    for k in range(min(4, len(jetons) - i - 1), 0, -1):
                        fragment = s[jetons[i + 1].start():jetons[i + k].end()]
                        id = _personnage(monde, fragment, connu)
                        if id and connu:
                            forme["nomme"], i = id, i + 1 + k
                        elif id:
                            # Un nom de personnage que Corvus ne connaît pas : à qui parle-t-il ?
                            forme["inconnu"] = fragment
                        if id:
                            break
                    if forme["nomme"] or forme["inconnu"]:
                        break
        if i < len(jetons) and jetons[i].group() == ":":
            reste = s[jetons[i].end():].strip()
            forme.update(explicite=True, mots=(citation(reste) if reste[:1] in GUILLEMETS else reste) or None)
        # Un verbe de parole en tête (« je dis… », « je demande à Gorm… ») annonce une parole ; seul, sans
        # destinataire ni mots (« je réponds » quand personne n'a appelé), il ne dit encore rien.
        rien = i >= len(jetons) and not (forme["nomme"] or forme["groupe"] or forme["suite"] or forme["inconnu"])
        if (not homonyme or forme["nomme"] or forme["groupe"]) and not rien:
            forme["explicite"] = True
        if forme["mots"] and not (forme["groupe"] or forme["nomme"] or forme["inconnu"]):
            _interpeller(monde, forme, forme["mots"])
    else:
        # Une interpellation sans guillemets (« Brune, pousse-toi ») reste du texte libre : le MJ
        # l'interprète ; s'il en fait une parole, le moteur en fixe le destinataire (nomme).
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


# Héler quelqu'un par son nom : un cri, pas une parole à un destinataire (``pnj.heler``). Les formes
# que l'analyse reconnaît, en un seul endroit : « j'appelle Gorm », « je hèle Gorm », « je crie le
# nom de Gorm », « j'appelle Gorm par son nom », « je crie « Gorm ? » », « crier : Gorm ! », suivies
# au plus d'un « fort » ou « à voix haute ».
VERBES_HELER = ("appelle", "appeler", "hele", "heler", "crie", "crier")
FORT = ("fort", "tres fort", "a voix haute", "a haute voix", "a pleine voix", "a tue-tete", "a pleins poumons",
        "de toutes mes forces")
PONCTUATION = (":", ",", "«", "»", '"', "“", "”")


def hele(monde, intention):
    """Le personnage que la saisie hèle par son nom, s'il est l'un de ceux que Corvus connaît
    (``_personnage``) ; None si elle n'est pas un appel par le nom (« j'appelle à l'aide » est un
    appel à l'aide, « je crie » un cri, une suite qui dit autre chose va au MJ)."""
    mots = [normaliser(j.group()) for j in JETON.finditer(intention or "")]
    if mots[:1] == ["je"]:
        mots = mots[1:]
    elif mots and mots[0].startswith(("j'", "j’")):
        mots = [mots[0][2:], *mots[1:]]
    if not mots or mots[0] not in VERBES_HELER:
        return None
    nom = " ".join(m for m in mots[1:] if m not in PONCTUATION)
    for f in sorted(FORT, key=len, reverse=True):
        if nom.endswith(" " + f):
            nom = nom[:-len(f) - 1]
            break
    if nom.startswith(("le nom de ", "le nom d'")):
        nom = nom[len("le nom d"):].lstrip("e '")
    elif nom.endswith(" par son nom"):
        nom = nom[:-len(" par son nom")]
    return _personnage(monde, nom)


# Répondre à qui vient de héler Corvus par son nom (``pnj.repondre_a``) : les formes que l'analyse
# reconnaît, en un seul endroit. « je réponds », « je lui réponds », « je réponds à Gorm », « je réponds
# à l'appel », suivies au plus des mots d'une réponse ou d'un « fort » ; « je crie « Ici ! » » ; ou les
# seuls mots d'une réponse entre guillemets (« « Ici ! » »).
VERBES_REPONDRE = ("reponds", "repondre")
MOTS_REPONSE = ("je suis ici", "je suis la", "par ici", "me voici", "me voila", "c'est moi", "ici", "present",
                "oui", "moi")
APPEL = ("l'appel", "cet appel", "son appel", "la voix", "cette voix")


def _mots(texte):
    return [m for m in (normaliser(j.group()) for j in JETON.finditer(texte or "")) if m not in PONCTUATION]


def _reponse(mots):
    """Ces mots ne disent rien d'autre qu'une réponse à un appel (« Ici ! », « Oui, je suis là ! »)."""
    reste = " ".join(mots)
    while reste:
        tete = next((r for r in MOTS_REPONSE if reste == r or reste.startswith(r + " ")), None)
        if tete is None:
            return False
        reste = reste[len(tete):].strip()
    return bool(mots)


def repond(monde, intention):
    """Celui à qui la saisie répond, juste après qu'il a hélé Corvus par son nom
    (``ecoute.appels``) ; None si personne ne vient de l'appeler ou si la saisie n'est pas une
    réponse (une parole qui dit autre chose, une autre suite, va au MJ ou à l'analyse des paroles)."""
    from .ecoute import appels
    from .voix import reel
    appelants = appels(monde)
    texte = (intention or "").strip()
    if not appelants or not texte:
        return None
    cite = citation(texte)
    if texte[0] in GUILLEMETS:
        # Les seuls mots d'une réponse, entre guillemets.
        fin = max(texte.rfind(c) for c in "»\"”")
        return appelants[0] if (cite is not None and fin > 0 and not texte[fin + 1:].strip(" .!?")
                                and _reponse(_mots(cite))) else None
    mots = _mots(texte[:texte.find(cite)] if cite is not None else texte)
    if mots[:1] == ["je"]:
        mots = mots[1:]
    elif mots and mots[0].startswith(("j'", "j’")):
        mots = [mots[0][2:], *mots[1:]]
    if mots[:1] in (["lui"], ["leur"]):
        mots = mots[1:]
    if not mots or mots[0] not in (*VERBES_REPONDRE, *VERBES_HELER):
        return None
    verbe, reste = mots[0], " ".join(mots[1:])
    for f in sorted(FORT, key=len, reverse=True):
        if reste == f or reste.endswith(" " + f):
            reste = reste[:-len(f)].strip()
            break
    if cite is not None and not _reponse(_mots(cite)):
        return None  # D'autres mots qu'une réponse : une parole.
    if cite is None and reste and _reponse(reste.split()):
        reste = ""  # « je réponds : ici », « je crie ici »
    elif cite is None and verbe in VERBES_HELER:
        return None  # Un cri sans les mots d'une réponse, ou un appel (``hele``).
    if not reste:
        return appelants[0]
    prep, _, nom = reste.partition(" ")
    if prep not in PREPOSITIONS or not nom:
        return None
    if nom in APPEL:
        return appelants[0]
    vise = _personnage(monde, nom) or reel(monde, nom)
    return vise if vise in appelants else None


def _nom_court(monde, id):
    return monde.objets[id]["nom"].split(",")[0]


def _contact(monde, id):
    """Au contact de Corvus (une case voisine) ; sans cases, quiconque est là."""
    if not monde.data.get("mode_cases"):
        return True
    from .passage import au_contact
    return au_contact(monde, "joueur", id)


def _face(monde, id):
    """(hors de son regard, distance, écart à son regard en huitièmes de tour) : le plus petit est
    celui à qui Corvus fait face ; à même distance, celui qui est droit devant lui plutôt qu'à son
    côté."""
    from .ouie import distance
    from .spatial import dans_le_regard, orientation_vers, quarts
    o, j = monde.objets[id], monde.joueur
    if not monde.data.get("mode_cases") or o.get("position") is None or j.get("position") is None:
        return 0, 0, 0
    regard = dans_le_regard(monde, o["lieu"], tuple(o["position"]), "joueur")
    if o["lieu"] != j["salle"]:
        return (0 if regard else 1), 99, 0
    ecart = quarts(j.get("orientation"), orientation_vers(tuple(j["position"]), tuple(o["position"])))
    return (0 if regard else 1), distance(tuple(o["position"]), tuple(j["position"])), ecart


def regard(monde, forme):
    """Corvus nomme quelqu'un qu'il ne voit pas de face mais verrait en se tournant : il se tourne
    d'abord vers lui, comme pour tout geste (``Moteur.preparer``). La direction, sinon None."""
    from .dialogues import interlocuteurs
    from .spatial import regard_vers
    id = forme.get("nomme")
    if not id or id in interlocuteurs(monde):
        return None
    return regard_vers(monde, id)


def tourne(monde, vers):
    """Une copie du monde où Corvus regarde ``vers``."""
    vu = monde.copier()
    vu.joueur["orientation"] = vers
    return vu


def phrase_regard(vers):
    return "Tu te tournes vers " + ("l'" if vers[0] in "eo" else "le ") + vers + "."


def precedents(monde, candidats, seul=False):
    """Ceux à qui Corvus a parlé en dernier et qui l'entendent encore (parmi ``candidats``) : la
    suite de l'échange. ``seul`` : un seul est admis (« je lui dis », un chuchotement)."""
    derniere = (monde.data.get("paroles_joueur") or [None])[-1]
    if not derniere:
        return []
    auditeurs = [a for a in derniere.get("auditeurs") or [derniere.get("auditeur")] if a in candidats]
    return auditeurs if auditeurs and (len(auditeurs) == 1 or not seul) else []


def en_face(monde, candidats):
    """Celui à qui Corvus parle sans le nommer, parmi ``candidats`` : celui qu'il a sous les yeux,
    le plus proche. À égalité, le joueur précise."""
    from .refus import liste
    from .voix import designation, nom_pour_joueur
    rangs = {id: _face(monde, id) for id in candidats}
    face = sorted(id for id, r in rangs.items() if r == min(rangs.values()))
    if len(face) > 1:
        noms = [nom_pour_joueur(monde, x) for x in face]
        noms = ", ".join(noms[:-1]) + " et " + noms[-1]
        nommable = next((x for x in face if designation(monde, x) == x), None)
        raise ParoleImpossible(f"{noms[0].upper() + noms[1:]} sont aussi près de toi l'un que l'autre : précise à "
                               "qui tu parles" + (f" (« {_nom_court(monde, nommable)}, … »)" if nommable else "")
                               + ", ou parle à tous (« à tous : … »).",
                               f"destinataire ambigu entre {liste([designation(monde, x) for x in face])} : le joueur "
                               "doit le nommer ; réponds en mode dialogue, sans choisir à sa place.")
    return face[0]


def destinataires(monde, forme):
    """Ceux à qui s'adresse la parole que décrit ``forme`` (``analyser``) : celui que le joueur
    nomme, sinon celui qui est en face de lui, à portée de voix ; à tous, tous les présents qui en
    saisiraient les mots ; un chuchotement, un seul, au contact. Une parole sans conteste (à tous,
    entre guillemets…) que nul présent ne saisirait est dite à la cantonade : aucun destinataire,
    qui l'entend la retient. ParoleImpossible si le joueur doit préciser ou s'approcher.

    Les présents comptent ceux dont il entend la voix sans savoir à qui elle est (``voix``) : il peut
    leur parler en face, pas les nommer. Celui qu'il nomme doit être quelqu'un qu'il sait là."""
    from .dialogues import interlocuteurs
    from .ouie import saisissent
    from .refus import liste as liste_
    from .voix import designation, reel

    def liste(ids):
        return liste_([designation(monde, x) for x in ids])
    presents = sorted(reel(monde, d) for d in interlocuteurs(monde))
    chuchote = forme["maniere"] == "chuchote"
    if forme.get("inconnu") and not (forme["nomme"] or forme["groupe"]):
        # Il nomme quelqu'un qu'il ne connaît pas : il ne sait pas s'il est là, et n'en parle pas à un autre.
        nom = " ".join(forme["inconnu"].split())
        raise ParoleImpossible(f"Tu ne connais personne du nom de {nom[:1].upper() + nom[1:]} ici. À la "
                               "cantonade (« à tous : … »), qui t'entend retiendra tes mots.",
                               f"« {nom} » ne désigne aucun personnage que Corvus connaisse : réponds en mode "
                               "dialogue ; ne fais pas parler Corvus à un autre personnage à sa place.")
    # Une parole qu'il ne destine à personne en particulier, et que nul présent ne saisirait, est dite à
    # la cantonade : qui l'entend la retient, et répond s'il le veut (``repondants``).
    cantonade = not forme["nomme"] and not chuchote
    if not presents and not cantonade and not forme["nomme"]:
        raise ParoleImpossible("Tu ne vois personne à qui parler. À la cantonade (« à tous : … »), qui "
                               "t'entend retiendra tes mots.",
                               "aucun interlocuteur perçu : réponds en mode dialogue.")
    if forme["groupe"] and chuchote:
        raise ParoleImpossible("On ne chuchote qu'à une seule personne, à son oreille.",
                               "chuchoter : un seul destinataire, nommé ou en face, au contact ; à plusieurs, "
                               "Corvus parle à voix haute (« à tous : … »).")
    nets = saisissent(monde, "joueur")
    # La règle commune de toute parole échangée (``pnj.peuvent_se_parler``) : il saisit les mots de
    # Corvus, et Corvus saisirait sa réponse. Qu'il sache ou non qui lui parle, il l'entend (une voix
    # qu'il ne connaît pas est un étranger : ``relations.percue``).
    from .pnj import peuvent_se_parler
    entendent = [id for id in presents if id in nets and peuvent_se_parler(monde, "joueur", id)]
    contact = [id for id in presents if _contact(monde, id)]
    if forme["suite"]:
        # La suite de l'échange : à qui il parlait, s'ils l'entendent encore ; sinon la règle commune.
        suite = precedents(monde, contact if chuchote else entendent, seul=chuchote or forme["suite"] == "lui")
        if suite and (forme["suite"] != "leur" or len(suite) > 1):
            forme["groupe"] = len(suite) > 1  # Poursuivre avec plusieurs, c'est leur parler à tous.
            return suite
    if forme["groupe"]:
        return entendent
    id = forme["nomme"]
    if id and (id not in presents or designation(monde, id) != id):
        # Il ne le sait là que par une voix qui porte ce nom (qui s'est dite ainsi, qu'on a appelée ainsi) :
        # c'est à elle qu'il parle, quelle qu'elle soit. Sinon, ce qui lui manque : le voir, donc s'approcher ;
        # à la cantonade, qui l'entend retient ses mots.
        from .voix import porteur_du_nom
        porteur = porteur_du_nom(monde, id, presents)
        if porteur is None:
            raise ParoleImpossible(f"Tu ne vois pas {_nom_court(monde, id)} d'ici : approche-toi pour lui parler. À "
                                   "la cantonade (« à tous : … »), qui t'entend retiendra tes mots.",
                                   f"{id} n'est pas perçu de Corvus : réponds en mode dialogue qu'il ne le voit pas ; "
                                   "ne fais pas parler Corvus à un autre personnage à sa place.")
        id = porteur
    if id:
        from .voix import nom_pour_joueur
        nom = nom_pour_joueur(monde, id)
        nom = nom[:1].upper() + nom[1:]
    if id and chuchote and id not in contact:
        raise ParoleImpossible(f"{nom} est trop loin : approche-toi pour lui chuchoter quoi que ce soit.",
                               f"chuchoter exige le contact (une case voisine) avec {designation(monde, id)} ; au "
                               f"contact de Corvus : {liste(contact)}.")
    if id and not chuchote and id not in nets:
        raise ParoleImpossible(f"{nom} est trop loin pour t'entendre.",
                               f"{designation(monde, id)} ne saisirait pas les mots de Corvus d'ici ; à portée de voix : "
                               f"{liste(entendent)}.")
    if id and not chuchote and id not in entendent:
        raise ParoleImpossible(f"Tu n'entendrais pas {nom_pour_joueur(monde, id)} te répondre d'ici.",
                               f"Corvus ne saisirait pas les mots de {designation(monde, id)} ; à qui Corvus peut "
                               f"parler : {liste(entendent)}.")
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
    return [en_face(monde, candidats)]


def prevue(monde, intention):
    """Ce que le moteur fixe de la parole que la saisie annonce, pour Luna (``parole_prevue``)."""
    forme = analyser(monde, intention)
    vers = regard(monde, forme)
    try:
        dest = destinataires(tourne(monde, vers) if vers else monde, forme)
    except ParoleImpossible as exc:
        return {"impossible": str(exc)}
    from .voix import designation
    return {"personnage": designation(monde, personnage(forme, dest)),
            "destinataires": [designation(monde, x) for x in dest],
            "maniere": "chuchotement" if forme["maniere"] == "chuchote" else "à voix haute",
            **({"mots": forme["mots"]} if forme["mots"] else {})}


def personnage(forme, dest):
    """Le champ personnage qu'attend le moteur : un identifiant, tous, ou personne (à la cantonade)."""
    return "tous" if forme["groupe"] else dest[0] if dest else "personne"


def annonce(monde, rapport):
    """Ce que le joueur lit de sa propre parole : à qui, et comment."""
    verbe = "chuchotes" if rapport.get("maniere") == "chuchotement" else "dis"
    tour = phrase_regard(rapport["regard"]) + "\n" if rapport.get("regard") else ""
    if rapport["personnage"] == "personne":
        return f"{tour}Tu {verbe} : « {rapport['replique_joueur']} »"
    from .voix import nom_pour_joueur, reel
    # Le nom qu'il lui donnait en parlant (``a_qui``), pas celui qu'elle s'est donné en répondant.
    a = ("tous" if rapport["personnage"] == "tous"
         else rapport.get("a_qui") or nom_pour_joueur(monde, reel(monde, rapport["personnage"])))
    return f"{tour}Tu {verbe} à {a} : « {rapport['replique_joueur']} »"


def identites(monde):
    """Les personnages dont Corvus sait qui ils sont, d'après ce qu'il sait d'eux, jamais d'après une
    place : il les a vus (``Monde.identifier``, ``souvenirs_personnages``), il connaît leur voix, ou
    une voix s'est donné leur nom, ou une autre voix l'a appelée ainsi (``voix.nommer``)."""
    from .voix import entendues
    ids = {*monde.data.get("personnages_vus", ()), *monde.data.get("souvenirs_personnages", {}),
           *monde.data.get("voix_connues", ()),
           *(e.get(k) for e in entendues(monde, "joueur").values() for k in ("se_dit", "appelee"))}
    return sorted(id for id in ids if id in monde.objets and monde.objets[id]["type"] == "personnage")


def _connu_du_joueur(monde, id):
    """Le joueur ne parle que de ce dont il a connaissance : perçu, examiné, vu ou entendu nommer.

    Un personnage, il le connaît d'après ce qu'il sait de lui (``identites``) ; qu'il ne soit plus là
    où on l'avait vu n'y change rien : le nommer quand il est absent donne le refus de la parole ou
    du geste (« Tu ne vois pas … d'ici »), pas un inconnu."""
    from . import lexique
    if (id == "joueur" or id in monde.data["visitees"] or id in monde.data["connus"]
            or id in monde.data.get("souvenirs_visuels", {}) or id in identites(monde)):
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


def _nom_dit(monde, sujet):
    """Le personnage qu'un contenu « nom » désigne : Corvus lui-même, ou celui dont il dit porter le
    nom. Un nom se prononce sans connaître celui qui le porte : se dire Brune sans l'avoir jamais vue
    reste se dire Brune (une imposture, que l'auditeur pèse, ``voix.se_nommer``)."""
    if not isinstance(sujet, str) or not sujet.strip():
        return None
    nom = monde.joueur["nom"]
    if normaliser(sujet) in ("joueur", "moi", normaliser(nom), normaliser(nom.split(",")[0])):
        return "joueur"
    id = _personnage(monde, sujet, connu=False) or resoudre(monde, sujet)
    return id if id == "joueur" or id in monde.objets and monde.objets[id]["type"] == "personnage" else None


# Les formes par lesquelles une réplique dit qui parle (texte normalisé) : ce qui suit est le nom que se
# donne celui qui parle. Une règle pour Corvus (``nom_dans``) et pour une voix inconnue
# (``narration.voix_inconnues``).
SE_NOMMER = re.compile(r"\b(?:je suis|je m'appelle|on m'appelle|mon nom est|mon nom,|c'est moi,?|moi,? c'est)"
                       r"\s+((?:\w|['-])+(?:\s+(?:\w|['-])+)?)")


def nom_dans(monde, replique):
    """Le nom que Corvus se donne dans sa réplique (« C'est moi, Brune », « je suis Corvus ») : le joueur,
    un personnage dont il dit porter le nom, ou None. Le moteur le lit dans les mots dits : le contenu
    « nom » ne peut pas en dire un autre."""
    for m in SE_NOMMER.finditer(normaliser(replique or "")):
        mots = m.group(1).split()
        for k in (2, 1):
            if len(mots) >= k:
                id = _nom_dit(monde, " ".join(mots[:k]))
                if id:
                    return id
    return None


def verifier_nom(monde, contenu, replique):
    """Le contenu « nom » dit le nom que la réplique donne à Corvus, s'il s'en donne un. Ce nom est celui que
    disent les mots : le moteur le lit lui-même, il complète un nom non typé et remplace un nom typé
    autrement (se dire quelqu'un d'autre est une imposture qu'il enregistre comme telle). Seul un nom typé
    alors que les mots n'en donnent aucun est refusé, l'élément fautif nommé : ce que le MJ voulait typer
    reste à sa charge."""
    dit = nom_dans(monde, replique)
    if dit is None:
        # « C'est Corvus. » se nomme aussi, mais « c'est X » dit souvent autre chose (« c'est Gorm qui l'a ») :
        # un nom typé que les mots disent ainsi est admis, sans que le moteur le déduise de lui-même.
        possibles = {_nom_dit(monde, " ".join(m.group(1).split()[:k]))
                     for m in re.finditer(r"\bc'est\s+((?:\w|['-])+(?:\s+(?:\w|['-])+)?)", normaliser(replique or ""))
                     for k in (1, 2)}
        for i, c in enumerate(contenu):
            if isinstance(c, dict) and c.get("type") == "nom" and _nom_dit(monde, c.get("sujet")) not in possibles - {None}:
                # Des mots imposés (« Qui est là ? ») qui ne disent aucun nom : Corvus ne s'est pas nommé.
                raise ErreurMonde("Corvus ne se nomme pas dans ce qu'il dit.",
                                  f"contenu[{i}] : retire l'élément nom ; la réplique « {replique} » ne donne aucun "
                                  "nom (« C'est X », « je suis X ») ; reçu sujet « " + str(c.get("sujet", "")) + " » ; "
                                  "une question sur qui parle se type qui.")
        return list(contenu)
    noms = [c for c in contenu if isinstance(c, dict) and c.get("type") == "nom"]
    autres = [c for c in contenu if c not in noms]
    # Un seul nom, celui des mots, à la place du premier nom typé (ou à la fin).
    place = contenu.index(noms[0]) if noms else len(autres)
    return [*autres[:place], {**(noms[0] if noms else {"attribut": "", "valeur": ""}), "type": "nom", "sujet": dit},
            *autres[place:]]


def _typer(monde, c, auditeur=None):
    """Contenu typé exploitable, ou None : ce qui ne peut pas être transmis reste un simple propos."""
    if isinstance(c, dict) and c.get("type") == "qui":
        return {"type": "qui"}
    if isinstance(c, dict) and c.get("type") == "reclamer":
        sujet = (c.get("sujet") or "").strip()
        objet = resoudre(monde, sujet) if sujet else None
        return {"type": "reclamer", "objet": objet} if objet or not sujet else None
    if isinstance(c, dict) and c.get("type") == "ressource":
        sujet = normaliser(c.get("sujet") or "")
        return {"type": "ressource", "besoin": sujet} if sujet in BESOINS_DEMANDES else None
    if isinstance(c, dict) and c.get("type") == "nom":
        sujet = _nom_dit(monde, c.get("sujet"))
        return {"type": "nom", "sujet": sujet} if sujet else None
    if isinstance(c, dict) and c.get("type") == "passage":
        # On demande le passage à celui à qui l'on parle : le sujet, s'il est donné, est lui.
        sujet = c.get("sujet")
        return ({"type": "passage", "prix": offre(c)} if not sujet or resoudre(monde, sujet) == auditeur
                else None)
    if not isinstance(c, dict) or c.get("type") not in ("affirmation", "demande", "aveu"):
        return None
    sujet = resoudre(monde, c.get("sujet"))
    if sujet is None and c["type"] == "demande" and auditeur:
        sujet = part_nommee(monde, auditeur, c.get("sujet"))
    if sujet is None:
        return None
    if c["type"] == "demande":
        return {"type": "demande", "sujet": sujet, "prix": offre(c)}
    if c["type"] == "aveu":
        return aveu(monde, "joueur", sujet, normaliser(c.get("valeur") or ""))
    attribut, valeur = c.get("attribut"), c.get("valeur")
    if attribut == "lieu":
        valeur = resoudre(monde, valeur)
        if valeur is None:
            return None
    elif attribut in ("verrouillee", FIABLE) and valeur in ("oui", "non"):
        valeur = valeur == "oui"
    else:
        return None
    return {"type": "affirmation", "sujet": sujet, "attribut": attribut, "valeur": valeur}


def offre(c):
    """Les pièces qu'une demande ou un passage offre en paiement (``valeur``, en chiffres) ; 0 sans
    offre."""
    valeur = str(c.get("valeur") or "").strip()
    return int(valeur) if valeur.isdigit() else 0


def verifier_offres(monde, contenu):
    """Corvus n'offre pas plus qu'il n'a : une cause par refus, l'élément fautif nommé."""
    total = 0
    for i, c in enumerate(contenu):
        if isinstance(c, dict) and c.get("type") in ("demande", "passage"):
            total += offre(c)
            if total > monde.joueur["or"]:
                raise ErreurMonde(f"Tu n'as que {monde.joueur['or']} pièces.",
                                  f"contenu[{i}].valeur : les pièces offertes, en tout de 0 à {monde.joueur['or']} "
                                  f"(or du joueur) ; reçu {offre(c)}, soit {total} avec les offres précédentes.")


def verifier_contenus(monde, contenu):
    """Une réclamation ou une demande de ressource que le moteur ne saurait trancher est refusée au
    MJ : une cause par refus, l'élément fautif nommé (``attendu``)."""
    for i, c in enumerate(contenu):
        if not isinstance(c, dict):
            continue
        sujet = str(c.get("sujet") or "").strip()
        if c.get("type") == "reclamer" and sujet and resoudre(monde, sujet) is None:
            raise ErreurMonde("Corvus ne sait pas ce qu'il réclame.",
                              f"contenu[{i}].sujet : vide (les pièces que le personnage doit à Corvus) ou un objet "
                              f"que Corvus connaît, en identifiant ; reçu « {sujet} ».")
        if c.get("type") == "ressource" and normaliser(sujet) not in BESOINS_DEMANDES:
            raise ErreurMonde("Corvus ne dit pas ce qu'il cherche.",
                              f"contenu[{i}].sujet : faim (de quoi manger) ou chaleur (du bois) ; reçu « {sujet} ».")


def aveu(monde, locuteur, objet, geste):
    """L'aveu typé d'un geste illicite (``social.GESTES``) fait par ``locuteur`` sur un objet qui
    appartient à un autre, ou None : avouer un geste permis n'apprend rien de lui."""
    from .social import GESTES
    from .vol import proprietaire
    o = monde.objets.get(objet)
    if not o or o["type"] == "personnage" or geste not in GESTES or proprietaire(monde, o) in (None, locuteur):
        return None
    return {"type": "aveu", "evenement": {"type": "vu_agir", "auteur": locuteur, "operation": geste, "objet": objet}}


def _nom_pour(monde, id):
    from .voix import nom_pour_joueur
    return nom_pour_joueur(monde, id) if designation_inconnue(monde, id) else designer(monde.objets[id])


def designation_inconnue(monde, id):
    from .voix import designation
    return designation(monde, id) != id


def _personne(travail, auditeur):
    """(nom, pronom, accord) de l'auditeur tel que le joueur le connaît (``voix.personne_pour_joueur``)."""
    from .voix import personne_pour_joueur
    return personne_pour_joueur(travail, auditeur)


QUI_VA_LA = "{nom} ne sait pas qui lui parle : {il} demande « Qui va là ? » avant toute chose."


def _avouer(travail, auditeur, c, faits):
    from .social import recevoir
    nom, il, _ = _personne(travail, auditeur)
    issue = recevoir(travail, auditeur, "joueur", c)
    faits.append(f"{nom} l'entend : {il} ne te tient plus pour fiable." if issue
                 else f"{nom} le savait déjà.")


def _se_nommer(travail, auditeur, nom_dit, faits):
    """Corvus dit être ``nom_dit`` : l'auditeur pèse ce nom (``voix.se_nommer``)."""
    from .voix import se_nommer
    nom, il, _ = _personne(travail, auditeur)
    lui = "elle" if il == "elle" else "lui"
    issue = se_nommer(travail, auditeur, "joueur", nom_dit)
    dit = travail.joueur["nom"] if nom_dit == "joueur" else travail.objets[nom_dit]["nom"].split(",")[0]
    faits.append({
        "connu": f"{nom} sait déjà qui tu es." if nom_dit == "joueur" else f"{nom} sait bien que tu n'es pas {dit}.",
        "demasque": f"{nom} sait que tu n'es pas {dit} et ne te fait plus confiance.",
        "doute": f"{nom} doute que tu sois {dit}.",
        "crue": f"{nom} te croit sur parole : pour {lui}, c'est {dit} qui parle. Cela ne te vaut pas plus de "
                "confiance qu'à un inconnu.",
    }[issue])


def _qui_est_la(travail, auditeur, faits):
    """Corvus demande qui parle : le personnage se nomme, sauf s'il se méfie de lui."""
    from .relations import mefiance, percue
    from .voix import se_nommer
    nom, il, _ = _personne(travail, auditeur)
    if mefiance(percue(travail, auditeur, "joueur")):
        faits.append(f"{nom} refuse de te dire qui {il} est.")
        return
    vrai = travail.objets[auditeur]["nom"].split(",")[0]
    se_nommer(travail, "joueur", auditeur, auditeur)
    faits.append(f"{nom} se nomme : « {vrai} ».")


def _affirmer(travail, auditeur, sujet, attribut, valeur, faits):
    from .echanges import affirmer
    nom, il, _ = _personne(travail, auditeur)
    issue = affirmer(travail, "joueur", auditeur, sujet, attribut, valeur)
    faits.append({
        "dementi": f"{nom} sait de ses propres yeux que c'est faux et cesse de te croire fiable.",
        "doute": f"{nom} ne te croit pas ({_phrase(travail, sujet, attribut, valeur)}).",
        "decouvert": f"{nom} voit bien que c'est faux et cesse de te croire fiable.",
        "crue": f"{nom} te croit : {il} tient désormais pour vrai que {_phrase(travail, sujet, attribut, valeur)}.",
    }[issue])


def _demander(travail, auditeur, objet, faits, prix=0):
    from .biens import prix as prix_de
    from .echanges import demande_de_part, demander
    from .vol import proprietaire
    nom, il, e = _personne(travail, auditeur)
    from .deliberation import besoin_de_part
    part = demande_de_part(travail, "joueur", auditeur, objet)
    from .spatial import porte_par
    # Un objet à lui qu'il ne porte pas : vendu, il ira le chercher pour le remettre.
    differe = not part and objet in travail.objets and not porte_par(travail, objet, auditeur)
    issue = demander(travail, "joueur", auditeur, objet, prix=prix)
    o = designer(travail.objets[objet]) if objet in travail.objets else ""
    vivres = objet in travail.objets and besoin_de_part(travail.objets[objet]) == "faim"
    # Ce qu'il en demanderait, s'il le vend : une part, ou un objet qui a un prix et qui est à lui.
    vend = (objet in travail.objets and proprietaire(travail, travail.objets[objet]) == auditeur
            and prix_de(travail, objet, part))
    from .echanges import foyer_de
    remise = part and not vivres and foyer_de(travail, auditeur, "joueur", combustible=objet) is None
    servie = (f"{il} te la servira là où sont les vivres." if vivres else
              f"{il} ira chercher une part pour te la remettre." if remise else f"{il} va entretenir le feu.")
    lui = "elle" if il == "elle" else "lui"
    faits.append({
        "absent": f"{nom} n'a pas cet objet sur {lui}.",
        "mefiance": f"{nom} refuse : {il} ne te fait pas confiance.",
        "qui_va_la": QUI_VA_LA.format(nom=nom, il=il),
        "necessaire": f"{nom} refuse de se séparer de {o}, qui lui sert.",
        "pauvre": f"Tu n'as pas les {prix} pièces que tu lui offres.",
        "refus": f"{nom} n'est pas convaincu{e} et garde {o}"
                 + (f" ; {il} en veut {vend} pièce{'s' if vend > 1 else ''}." if vend and prix < vend else "."),
        "remis": f"{nom} te remet " + ("une part " + complement_de(travail.objets[objet]) if part else o)
                 + (f" : {il} te le prête." if any(
            p["objet"] == objet and p["a"] == "joueur" for p in travail.data.get("permissions", ())) else "."),
        "rendu": f"{nom} te rend {o}.",
        "vendu": (_part_vendue(travail, auditeur, objet, nom, il, prix) if part and not vivres
                  else f"{nom} prend tes {prix} pièces et accepte de t'en donner une part : " + servie if part
                  else f"{nom} prend tes {prix} pièces et ira chercher {o} pour te {_le(travail.objets[objet])} "
                       "remettre." if differe else f"{nom} prend tes {prix} pièces et te remet {o}."),
        "promis": (f"{nom} a déjà promis de te remettre {o}." if differe else
                   f"{nom} accepte de t'en donner une part : " + servie),
        "impossible": f"{nom} ne voit pas comment te donner {o}.",
    }[issue])


def _part_vendue(travail, auditeur, lot, nom, il, prix):
    """Une part de combustible que Corvus achète lui est remise (``echanges._remettre_part``) : tout de
    suite, ou quand le vendeur sera allé la chercher."""
    from .francais import complement_de
    part = "une part " + complement_de(travail.objets[lot])
    a_remettre = any(x["condition"].get("remettre") == "joueur" and x.get("lot") == lot
                     for x in esprit(travail, auditeur)["engagements"])
    return (f"{nom} prend tes {prix} pièces et ira chercher {part} pour te la remettre." if a_remettre
            else f"{nom} prend tes {prix} pièces et te remet {part}.")


def _reclamer(travail, auditeur, objet, faits):
    """Corvus réclame son dû : les pièces qu'on lui doit (``biens.reclamer_dette`` : le débiteur rend
    ce qu'il peut, s'il le veut), ou son objet que l'auditeur porte (on le redemande comme son
    propriétaire, ``echanges.demander``). Ce qui n'est pas dû, le personnage le dit."""
    from .biens import dues, reclamer_dette
    from .echanges import accueil, demander
    from .spatial import porte_par
    from .vol import proprietaire
    nom, il, _ = _personne(travail, auditeur)
    lui = "elle" if il == "elle" else "lui"
    if accueil(travail, "joueur", auditeur) == "qui_va_la":
        faits.append(QUI_VA_LA.format(nom=nom, il=il))
        return
    if objet is None:
        dettes = dues(travail, auditeur, "joueur")
        if not dettes:
            faits.append(f"{nom} ne te doit rien.")
            return
        montant = sum(d["montant"] for d in dettes)
        lignes = []
        issues = reclamer_dette(travail, "joueur", auditeur, lignes)
        faits.extend(lignes)
        if "sans_le_sou" in issues and not lignes:
            faits.append(f"{nom} n'a pas de quoi te rendre les {montant} pièce{'s' if montant > 1 else ''} "
                         f"qu'{il} te doit.")
        return
    o = travail.objets.get(objet)
    if o is None or o["type"] == "personnage" or proprietaire(travail, o) != "joueur" \
            or not porte_par(travail, objet, auditeur):
        faits.append(f"{nom} ne te doit pas {designer(o) if o else 'cela'} : {il} ne porte rien à toi de tel."
                     if o and o["type"] != "personnage" else f"{nom} ne te doit rien de tel.")
        return
    issue = demander(travail, "joueur", auditeur, objet)
    faits.append({"rendu": f"{nom} te rend {designer(o)}.",
                  "necessaire": f"{nom} garde {designer(o)} : {il} s'en sert encore.",
                  "qui_va_la": QUI_VA_LA.format(nom=nom, il=il)}.get(
        issue, f"{nom} ne te rend pas {designer(o)}, qu'{il} n'a pas sur {lui}."))


def _enqueter(travail, auditeur, besoin, faits):
    """Corvus demande au personnage s'il a de quoi apaiser ``besoin`` : il répond par ce qu'il a
    vraiment (``echanges.enqueter``)."""
    from .echanges import _ou_dit, enqueter
    nom, il, _ = _personne(travail, auditeur)
    issue, dit = enqueter(travail, "joueur", auditeur, besoin)
    if issue == "dit":
        faits.append(f"{nom} dit avoir " + " et ".join(designer(travail.objets[k]) + _ou_dit(travail, lieu)
                                                     for k, lieu in dit) + ".")
    else:
        faits.append({"qui_va_la": QUI_VA_LA.format(nom=nom, il=il),
                      "mefiance": f"{nom} refuse de te répondre : {il} ne te fait pas confiance.",
                      "rien": f"{nom} dit n'en avoir pas."}[issue])


def _le(o):
    return "les" if o.get("pluriel") else "la" if o.get("genre") == "f" else "le"


def _demander_passage(travail, auditeur, faits, prix=0):
    from .passage import demander_passage
    nom, il, e = _personne(travail, auditeur)
    issue = demander_passage(travail, auditeur, "joueur", [], prix=prix)
    faits.append({
        "qui_va_la": QUI_VA_LA.format(nom=nom, il=il),
        "ecarte": f"{nom} s'écarte d'un pas pour te laisser passer.",
        "paye": f"{nom} prend tes {prix} pièces et s'écarte d'un pas pour te laisser passer.",
        "geste": f"{nom} ne s'écarte pas : {il} est occupé{e} à ce qu'{il} fait là.",
        "mefiance": f"{nom} refuse de s'écarter : {il} ne te fait pas confiance.",
        "place": f"{nom} n'a pas la place de s'écarter.",
        "refus": f"{nom} n'est pas convaincu{e} et reste où {il} est.",
        "inutile": f"{nom} ne te barre pas le passage.",
    }[issue])


# Ce qu'un contenu demande à qui l'entend : il appelle une réponse, comme toute question.
APPELLENT_REPONSE = ("qui", "ressource", "demande", "reclamer", "passage")


def appelle_reponse(replique, contenu):
    """Une parole appelle une réponse : une question (ses mots en portent la marque, « ? »), ou un
    contenu qui demande quelque chose à qui l'entend (qui parle, as-tu…, donne-moi…)."""
    return "?" in (replique or "") or any(isinstance(c, dict) and c.get("type") in APPELLENT_REPONSE
                                          for c in contenu)


def repondants(monde, forme, dest, replique, contenu):
    """Ceux qui répondent à une parole qui ne s'adresse à personne en particulier (à la cantonade, ou à
    tous) sans en être les destinataires : qui en saisit les mots sans que Corvus le sache là, et dont
    Corvus saisirait la réponse (``pnj.peuvent_se_parler``), quand elle appelle une réponse
    (``appelle_reponse``) ; chacun décide pour lui, par la règle de celui qu'on hèle (``voix.repond`` :
    il ne répond pas à une voix dont il se méfie). Ce qu'il répond suit la règle d'un destinataire
    (l'accueil d'une voix inconnue, « Qui va là ? », ses valeurs)."""
    if forme["maniere"] == "chuchote" or not (forme["groupe"] or not dest) or not appelle_reponse(replique, contenu):
        return []
    from .ouie import saisissent
    from .pnj import peuvent_se_parler
    from .voix import repond
    return sorted(id for id in saisissent(monde, "joueur") if id not in dest and monde.objets[id].get("profil")
                  and peuvent_se_parler(monde, "joueur", id) and repond(monde, id, "joueur"))


def entendre_repondant(monde, id):
    """Corvus entend répondre ``id``, qu'il ne savait pas là : il saisit sa voix (``voix.entendre`` :
    il la reconnaît, ou la retient comme une voix inconnue) et peut désormais lui parler
    (``data["entendus"]``, ``dialogues.interlocuteurs``)."""
    from .ouie import _place
    from .voix import entendre
    salle, case = _place(monde, id)
    entendre(monde, "joueur", id, salle, case)
    entendus = monde.data.setdefault("entendus", [])
    if id not in entendus:
        entendus.append(id)


def issue(monde, forme, dest, repondent, temoins, replique):
    """Ce que le moteur a établi de cette parole, en une phrase pour le MJ et l'auditeur : Corvus l'a
    dite, à qui, qui lui répond, qui l'a entendue sans être interpellé ; ce qui n'y est pas n'a pas
    eu lieu (une réponse d'un autre, un silence de qui répond)."""
    from .voix import designation, nom_pour_joueur

    def noms(ids):
        ids = [f"{nom_pour_joueur(monde, x)} ({designation(monde, x)})" for x in ids]
        return ids[0] if len(ids) == 1 else ", ".join(ids[:-1]) + " et " + ids[-1]
    chuchote = forme["maniere"] == "chuchote"
    a = (" à tous" if forme["groupe"] else f" à {noms(dest)}" if dest else ", à la cantonade")
    phrase = f"Tu as {'chuchoté' if chuchote else 'dit à voix haute'}{a} : « {replique} »."
    if repondent:
        un = len(repondent) == 1
        qui = noms(repondent)
        phrase += (f" {qui[:1].upper() + qui[1:]} t'{'a' if un else 'ont'} entendu et te répond{'' if un else 'ent'} : "
                   "ses mots ne sont pas fixés par le moteur, c'est une parole nouvelle, d'après les faits de cette "
                   "parole, ce qu'il croit et ses valeurs.")
    else:
        phrase += " Aucune réponse ne te parvient."
    if temoins:
        qui = noms(temoins)
        un = len(temoins) == 1
        phrase += (f" {qui[:1].upper() + qui[1:]} {'a' if un else 'ont'} aussi entendu ces mots, sans qu'ils "
                   f"{'lui' if un else 'leur'} soient adressés, et se {'tait' if un else 'taisent'}.")
    return phrase


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
    vers = regard(monde, forme)
    if vers:
        # Il se tourne d'abord vers celui qu'il nomme dans son dos.
        monde = tourne(monde, vers)
    dest = destinataires(monde, forme)
    from .deliberation import rejoint
    from .voix import designation, identifie
    # Le MJ désigne une voix que Corvus ne sait à qui prêter comme le joueur : voix_<n>.
    attendu = designation(monde, personnage(forme, dest))
    if p["personnage"] != attendu:
        raise ErreurMonde("Tu t'adresses à tous ceux qui t'entendent." if forme["groupe"]
                          else "Tu ne t'adresses à personne en particulier." if not dest
                          else "Tu t'adresses à " + _nom_pour(monde, dest[0]) + ".",
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
    verifier_offres(monde, p["contenu"])
    verifier_contenus(monde, p["contenu"])
    # Le nom que Corvus se donne est celui que disent ses mots, vrai ou non (une imposture).
    contenu = verifier_nom(monde, p["contenu"], replique)
    from .ouie import _place, retentir, saisissent
    travail = monde.copier()
    chuchote = forme["maniere"] == "chuchote"
    # Ce qu'en retient qui l'entend sans en être le destinataire : ce qui ne s'adresse pas qu'à lui.
    publics = [x for x in (_typer(travail, c) for c in contenu) if x and x["type"] in ("affirmation", "aveu", "nom")]
    # À la cantonade ou à tous, qui l'entend sans que Corvus le sache là répond s'il le veut.
    repondent = repondants(travail, forme, dest, replique, contenu)
    for id in repondent:
        entendre_repondant(travail, id)
    temoins = [] if chuchote else sorted(id for id in saisissent(travail, "joueur")
                                         if id not in dest and id not in repondent and travail.objets[id].get("profil"))
    expression = capacite_transmission(_stats_pnj(travail, "joueur")["INT"])
    faits = []
    for auditeur in [*dest, *repondent]:
        capacite = min(expression, capacite_transmission(_stats_pnj(travail, auditeur)["INT"]))
        transmis = [x for x in (_typer(travail, c, auditeur) for c in contenu) if x]
        for c in transmis[:capacite]:
            if c["type"] == "affirmation":
                _affirmer(travail, auditeur, c["sujet"], c["attribut"], c["valeur"], faits)
            elif c["type"] == "passage":
                _demander_passage(travail, auditeur, faits, c["prix"])
            elif c["type"] == "aveu":
                _avouer(travail, auditeur, c, faits)
            elif c["type"] == "nom":
                _se_nommer(travail, auditeur, c["sujet"], faits)
            elif c["type"] == "qui":
                _qui_est_la(travail, auditeur, faits)
            elif c["type"] == "reclamer":
                _reclamer(travail, auditeur, c["objet"], faits)
            elif c["type"] == "ressource":
                _enqueter(travail, auditeur, c["besoin"], faits)
            else:
                _demander(travail, auditeur, c["sujet"], faits, c["prix"])
        if transmis[capacite:]:
            faits.append(f"{_personne(travail, auditeur)[0]} ne retient pas tout : une partie de ce que tu as dit se perd.")
        rejoint(travail, auditeur, "joueur")  # Il attendait que Corvus le rejoigne : ils se parlent.
        memoriser(travail, auditeur, {"type": "parole", "locuteur": "joueur", "a": list(dest), "texte": replique[:240],
                                      "cites": [], **({} if identifie(travail, auditeur, "joueur")
                                                      else {"voix_inconnue": True})})
    # Sa voix retentit : qui en saisit les mots la retient (``ouie``) ; un chuchotement ne va qu'à son destinataire.
    retentir(travail, "joueur", "chuchoter" if chuchote else "parler", texte=replique, dits=replique,
             parole=None if chuchote else {"a": [*dest, *repondent], "contenu": publics})
    for id in repondent:
        # Sa réponse retentit à son tour : sa voix, d'où il se tient (ses mots sont ceux de sa réplique).
        retentir(travail, id, "parler")
    travail.data["revision"] += 1
    travail.data.setdefault("paroles_joueur", []).append(
        {"revision": travail.data["revision"], "auditeur": personnage(forme, dest), "auditeurs": [*dest, *repondent],
         "texte": replique,
         "minute": travail.data["minutes"]})
    travail.data["paroles_joueur"] = travail.data["paroles_joueur"][-40:]
    travail.verifier()
    from .voix import reel
    presents = {reel(monde, d) for d in interlocuteurs(monde)}
    from .voix import nom_pour_joueur
    temoins_vus = [id for id in temoins if id in presents]
    rapport = {"personnage": attendu, "destinataires": [designation(monde, x) for x in dest],
               **({"a_qui": nom_pour_joueur(monde, dest[0])} if len(dest) == 1 and not forme["groupe"] else {}),
               "repondent": [designation(travail, x) for x in [*dest, *repondent]],
               "temoins": [designation(monde, id) for id in temoins_vus],
               "maniere": "chuchotement" if chuchote else "à voix haute", "sujet": replique,
               "operation": "parole_joueur", "replique_joueur": replique,
               "issue": issue(travail, forme, dest, [*dest, *repondent], temoins_vus, replique), "faits": faits,
               **({"regard": vers} if vers else {})}
    return travail, rapport
