"""Les voix : qui l'on reconnaît à l'oreille, ce qu'une voix inconnue prétend, ce qu'on en croit.

Connaître de vue et connaître une voix sont deux choses. On sait qui l'on voit (aucun déguisement
n'est modélisé). On connaît la voix de quelqu'un quand on l'a entendu parler en sachant qui
parlait : en le voyant parler (``ouie.entendre``, ``ouie._au_joueur``, les répliques que le MJ
prête à un personnage que le joueur voit), ou parce que le scénario le déclare (gens qui se
connaissent déjà : un savoir à son sujet, ``esprits.installer``). Voir quelqu'un sans l'entendre
ne fait pas connaître sa voix.

Le moteur sait à qui est chaque voix : sa signature est l'identifiant de son porteur, jamais
montrée au joueur ni au MJ comme une identité. Un personnage ne relie une voix qu'à ce qu'il en a
lui-même entendu. Il retient les voix inconnues qu'il a entendues (``voix_entendues`` de son
esprit, ``data["voix_entendues"]`` du joueur) : le nom qu'elles se sont donné (``se_dit``), s'il
se méfie d'elles (``mefiance`` : elles ont menti, ou avoué une faute), et pour le joueur le nom
qu'une autre voix leur a donné en s'adressant à elles (``appelee``, ``nommer`` : « une voix qu'on
appelle Gorm », un ouï-dire).

Toute reconnaissance d'une voix passe par ``reconnaitre`` : qui l'auditeur croit entendre, et avec
quelle certitude. L'imitation d'une voix, ou la méfiance envers une voix connue quand on sait
qu'un imitateur rôde, s'y brancheront sans toucher ses appelants.

Se nommer est une affirmation pesée, jamais une identité acquise (``se_nommer``) :
- l'auditeur connaît la vraie voix du nommé : ce n'est pas elle, le mensonge est démasqué ; il se
  méfie de cette voix, et de son porteur s'il sait qui c'est ;
- sinon il croit « c'est X » comme un ouï-dire, pesé contre ce qu'il sait (X vu ailleurs il y a
  peu : il en doute). Le nom situe X (une croyance de lieu, source ``se_dit``) ; il ne donne
  jamais plus que la confiance accordée à un inconnu (``fiabilite``) ;
- plus tard, il entend la vraie voix de X : elle devient connue (``connaitre``) ; celle qui
  s'était dite X n'était pas la sienne, il sait qu'on lui a menti, sans savoir qui ; le jour où il
  voit parler le menteur, il reconnaît « la voix qui se disait X » et s'en méfie. Si c'était bien
  X, la croyance passe du ouï-dire au constat.

Une voix qu'il ne sait à qui prêter est un étranger : aucune confiance connue, une demande pèse
moins (``INCONNU``) ; s'il est prudent (``prudent`` : sa crainte contre son courage), il répond
« Qui va là ? » à une voix qui ne s'est pas nommée, au lieu d'accéder (``qui_va_la``).
"""
from .esprits import RECENT, croire, esprit, lire, memoriser

INCONNUE, PRETENDUE, RECONNUE, SUSPECTE = "inconnue", "pretendue", "reconnue", "suspecte"
VOIX_MAX = 24          # voix inconnues retenues ; au-delà, la plus anciennement entendue s'oublie
INCONNU = 2            # DD : une demande d'une voix qu'il ne sait à qui prêter pèse moins
VU_AILLEURS = RECENT   # minutes : « c'est X », de qui il a vu X ailleurs depuis moins, est douteux
CHAMPS_VOIX = {"minute", "se_dit", "mefiance", "n"}
OPTIONNELS = {"appelee"}   # le nom qu'une autre voix lui a donné en s'adressant à elle (``nommer``)


# --- Ce que chacun connaît -----------------------------------------------------------------

def _connues(monde, qui):
    return monde.data.get("voix_connues", []) if qui == "joueur" else lire(monde, qui)["voix"]


def entendues(monde, qui, ecrire=False):
    """Les voix inconnues qu'il a entendues : {signature: {minute, se_dit, mefiance, n}}."""
    if qui == "joueur":
        return monde.data.setdefault("voix_entendues", {}) if ecrire else monde.data.get("voix_entendues", {})
    return esprit(monde, qui)["voix_entendues"] if ecrire else lire(monde, qui)["voix_entendues"]


def connait(monde, qui, autre):
    """La voix d'``autre`` est-elle connue de ``qui`` ? Lecture brute : toute reconnaissance passe
    par ``reconnaitre``."""
    return autre in _connues(monde, qui)


def connait_nom(monde, qui, autre):
    """``qui`` (un PNJ) sait-il le nom d'``autre`` ? Un personnage dont il a une croyance, dont il
    connaît la voix ou dont une voix s'est dite : le scénario, ce qu'il a vu, entendu ou s'est laissé
    dire. Le joueur arrive en étranger : on ne sait son nom que s'il l'a donné (``se_nommer``) ou
    qu'on a entendu parler de lui (un ouï-dire : ``dit:…``)."""
    if autre == qui:
        return True
    e = lire(monde, qui)
    dites = {x["se_dit"] for x in e["voix_entendues"].values() if x["se_dit"] and not x["mefiance"]}
    if autre == "joueur":
        return "joueur" in dites or any(
            c["source"] == "se_dit" or c["source"].startswith("dit:") for c in e["croyances"].get("joueur", {}).values())
    return autre in e["croyances"] or autre in e["voix"] or autre in dites


def reconnaitre(monde, auditeur, locuteur):
    """(qui il croit entendre, certitude) quand il saisit les mots de la voix de ``locuteur``,
    sans le voir : (locuteur, RECONNUE) d'une voix connue ; (X, PRETENDUE) d'une voix inconnue qui
    s'est dite X ; (None, SUSPECTE) d'une voix dont il se méfie ; (None, INCONNUE) sinon.
    Seul point de reconnaissance d'une voix : l'imitation s'y branchera."""
    if connait(monde, auditeur, locuteur):
        return locuteur, RECONNUE
    entree = entendues(monde, auditeur).get(locuteur)
    if entree and entree["mefiance"]:
        return None, SUSPECTE
    if entree and entree["se_dit"]:
        return entree["se_dit"], PRETENDUE
    return None, INCONNUE


def voit(monde, x, y):
    if x == "joueur":
        return monde.visible(y)
    from .esprits import percoit
    return percoit(monde, x, y)


def _verrait_en_se_tournant(monde, x, y):
    """Ce que ``x`` verrait s'il se tournait vers une voix, d'où qu'elle vienne : son regard sans
    orientation (comme ``pnj.tour_d_horizon``) ; l'orientation est rendue aussitôt. La lumière le
    montre, le noir non."""
    porteur = monde.joueur if x == "joueur" else monde.objets[x]
    orientation = porteur.pop("orientation", None)
    try:
        return voit(monde, x, y)
    finally:
        if orientation is not None:
            porteur["orientation"] = orientation


def identifie(monde, x, y):
    """``x`` sait que c'est ``y`` qui lui parle : il le voit, le verrait en se tournant vers sa
    voix, ou reconnaît sa voix (``reconnaitre``). Jamais d'après la place réelle de ``y`` seule."""
    return (voit(monde, x, y) or _verrait_en_se_tournant(monde, x, y)
            or reconnaitre(monde, x, y)[1] == RECONNUE)


def fiabilite(monde, auditeur, locuteur):
    """La confiance qu'``auditeur`` accorde à qui lui parle, telle qu'il le perçoit : celle qu'il
    porte à ``locuteur`` s'il sait que c'est lui ; à une voix dont il se méfie, aucune ; à une
    autre voix inconnue, celle d'un étranger (None), même si elle s'est nommée."""
    if identifie(monde, auditeur, locuteur):
        return lire(monde, auditeur)["croyances"].get(locuteur, {}).get("fiable")
    if reconnaitre(monde, auditeur, locuteur)[1] == SUSPECTE:
        return {"valeur": False, "source": "entendu"}
    return None


def source_dite(monde, auditeur, locuteur):
    """La source d'un ouï-dire : « dit:X » de qui il sait que c'est X, « dit:voix:X » d'une voix
    qu'il ne sait à qui prêter (X, la signature, reste au moteur)."""
    return "dit:" + ("" if identifie(monde, auditeur, locuteur) else "voix:") + locuteur


def auteur_dit(source):
    """(signature du locuteur, vrai si ce n'était pour l'auditeur qu'une voix inconnue)."""
    reste = source[4:]
    return (reste[5:], True) if reste.startswith("voix:") else (reste, False)


# --- Ce qu'on apprend en entendant ------------------------------------------------------------

def retenir(monde, qui, signature):
    """Il retient une voix inconnue entendue maintenant ; renvoie ce qu'il en retient."""
    voix = entendues(monde, qui, ecrire=True)
    entree = voix.get(signature)
    if entree is None:
        entree = voix[signature] = {"minute": monde.data["minutes"], "se_dit": None, "mefiance": False,
                                    "n": 1 + max((e["n"] for e in voix.values()), default=0)}
        for vieille in sorted(voix, key=lambda s: (voix[s]["minute"], voix[s]["n"]))[:max(0, len(voix) - VOIX_MAX)]:
            del voix[vieille]
    entree["minute"] = monde.data["minutes"]
    return entree


def nommer(monde, qui, signature, nom):
    """``qui`` (le joueur) a entendu une autre voix s'adresser à la voix ``signature`` en l'appelant
    ``nom`` : « une voix qu'on appelle Gorm », un ouï-dire, jamais une identité. Rien s'il sait déjà
    à qui est cette voix, si elle s'est elle-même nommée, ou s'il connaît la vraie voix de ``nom`` :
    ce n'est pas elle, quoi qu'on dise. Renvoie vrai s'il l'a appris."""
    if identifie(monde, qui, signature) or nom == qui or connait(monde, qui, nom):
        return False
    entree = retenir(monde, qui, signature)
    if entree["se_dit"] or entree["mefiance"] or entree.get("appelee") == nom:
        return False
    entree["appelee"] = nom
    return True


def _clarte(monde, id):
    from .echanges import clarte
    return round(0.7 * clarte(monde, id), 2)


def _vu_ailleurs(monde, auditeur, nom, salle):
    """Il a vu ``nom`` ailleurs il y a peu : « c'est lui, ici » lui semble douteux."""
    c = lire(monde, auditeur)["croyances"].get(nom, {}).get("lieu")
    return bool(c and c["source"] in ("vu", "essai") and c["valeur"] not in (None, salle)
                and monde.data["minutes"] - c["minute"] <= VU_AILLEURS)


def _situer(monde, auditeur, nom, salle, case):
    croire(monde, auditeur, nom, "lieu", salle, "se_dit", _clarte(monde, auditeur), salle=salle,
           case=case if salle == monde.objets[auditeur]["lieu"] else None)


def entendre(monde, auditeur, locuteur, salle, case=None):
    """``auditeur`` (un PNJ ou le joueur) saisit les mots de la voix de ``locuteur``, venue de
    ``salle`` (``case`` s'il est dans la même). Il le voit parler : il saura reconnaître sa voix.
    Sinon : une voix connue, il croit son porteur là (``entendu``) ; une voix qui s'était dite X,
    il croit X là, comme un ouï-dire ; une voix inconnue, il la retient sans savoir à qui elle est.
    Renvoie (qui il croit entendre, certitude) ; (locuteur, "vu") s'il le voit."""
    if voit(monde, auditeur, locuteur):
        connaitre(monde, auditeur, locuteur)
        return locuteur, "vu"
    croit, certitude = reconnaitre(monde, auditeur, locuteur)
    if certitude == RECONNUE:
        if auditeur != "joueur":
            croire(monde, auditeur, locuteur, "lieu", salle, "entendu", salle=salle, case=case)
        return croit, certitude
    retenir(monde, auditeur, locuteur)
    if certitude == PRETENDUE and auditeur != "joueur" and not _vu_ailleurs(monde, auditeur, croit, salle):
        _situer(monde, auditeur, croit, salle, case)
    return croit, certitude


def connaitre(monde, qui, autre):
    """``qui`` connaît désormais la voix d'``autre`` : il l'a entendu parler en sachant que c'était
    lui. Il la compare à ce que les voix inconnues lui ont dit : la voix d'``autre`` s'était dite
    quelqu'un d'autre, ou il s'en méfiait, il se méfie désormais d'``autre`` ; elle s'était
    dite ``autre``, c'était bien lui, ce qu'il en croyait sur sa parole devient un constat ; une
    autre voix s'était dite ``autre``, il sait qu'on lui a menti, sans savoir qui."""
    connues = monde.data.setdefault("voix_connues", []) if qui == "joueur" else esprit(monde, qui)["voix"]
    if autre == qui or autre in connues:
        return
    connues.append(autre)
    voix = entendues(monde, qui, ecrire=True)
    entree = voix.pop(autre, None)
    if qui == "joueur":
        return  # Le joueur juge lui-même : ce qu'il entend s'affiche (``nom_pour_joueur``).
    croyances = esprit(monde, qui)["croyances"]
    if entree and (entree["mefiance"] or entree["se_dit"] not in (None, autre)):
        croire(monde, qui, autre, "fiable", False, "entendu")
        memoriser(monde, qui, {"type": "imposture", "locuteur": autre, "se_disait": entree["se_dit"]})
    elif entree and entree["se_dit"] == autre:
        c = croyances.get(autre, {}).get("lieu")
        if c and c["source"] == "se_dit":
            c.update(source="entendu", confiance=1.0)
    for signature, x in voix.items():
        if x["se_dit"] == autre and not x["mefiance"]:
            x["mefiance"] = True
            memoriser(monde, qui, {"type": "imposture", "se_disait": autre})
            c = croyances.get(autre, {}).get("lieu")
            if c and c["source"] == "se_dit":
                del croyances[autre]["lieu"]  # Ce n'était pas lui : il ne sait plus où il est.


def se_mefier(monde, auditeur, locuteur, source="entendu"):
    """Il se méfie de qui lui a menti : de ``locuteur`` s'il sait que c'est lui, sinon de sa voix."""
    if auditeur == "joueur":
        return
    if identifie(monde, auditeur, locuteur):
        croire(monde, auditeur, locuteur, "fiable", False, source)
    else:
        retenir(monde, auditeur, locuteur)["mefiance"] = True


def se_nommer(monde, auditeur, locuteur, nom):
    """``locuteur`` dit à ``auditeur`` être ``nom`` (« C'est Corvus », ou « Ici ! » à son nom).
    Renvoie l'issue : « connu » (il sait déjà que c'est lui), « demasque », « doute » ou « crue »."""
    from .ouie import _place
    if auditeur == "joueur":
        if identifie(monde, "joueur", locuteur):
            return "connu" if nom == locuteur else "demasque"
        retenir(monde, "joueur", locuteur)["se_dit"] = nom
        return "crue"
    if identifie(monde, auditeur, locuteur):
        if nom == locuteur:
            return "connu"
        se_mefier(monde, auditeur, locuteur)
        memoriser(monde, auditeur, {"type": "imposture", "locuteur": locuteur, "se_disait": nom})
        return "demasque"
    if reconnaitre(monde, auditeur, locuteur)[1] == SUSPECTE:
        return "demasque"
    if nom == auditeur or connait(monde, auditeur, nom):
        # Il connaît la vraie voix de celui qu'elle prétend être, ou c'est lui qu'elle prétend être.
        entree = retenir(monde, auditeur, locuteur)
        entree.update(se_dit=nom, mefiance=True)
        memoriser(monde, auditeur, {"type": "imposture", "se_disait": nom})
        return "demasque"
    salle, case = _place(monde, locuteur)
    entree = retenir(monde, auditeur, locuteur)
    if _vu_ailleurs(monde, auditeur, nom, salle):
        memoriser(monde, auditeur, {"type": "parole_doutee", "sujet": nom, "attribut": "nom"})
        return "doute"
    entree["se_dit"] = nom
    _situer(monde, auditeur, nom, salle, list(case) if case is not None else None)
    return "crue"


# --- Face à une voix inconnue -----------------------------------------------------------------

def prudent(monde, id):
    """Sa crainte (la sécurité qui le presse) l'emporte sur son courage : face à une voix qu'il ne
    connaît pas, il demande d'abord qui va là."""
    from .caractere import NEUTRE, valeur
    if not monde.objets[id].get("profil"):
        return False
    return lire(monde, id)["besoins"].get("securite", 0) + NEUTRE - valeur(monde, id, "courage") >= NEUTRE


def qui_va_la(monde, auditeur, locuteur):
    """``auditeur`` répond « Qui va là ? » au lieu d'accéder : il ne sait à qui est cette voix, elle
    ne s'est pas nommée, et il est prudent."""
    return (auditeur != "joueur" and not identifie(monde, auditeur, locuteur)
            and reconnaitre(monde, auditeur, locuteur)[1] == INCONNUE and prudent(monde, auditeur))


# --- Ce que le joueur et le MJ en savent ---------------------------------------------------------

PREFIXE = "voix_"


def designation(monde, id):
    """Comment le joueur, et le MJ qui lui parle, désignent ``id`` : son identifiant s'il sait qui
    c'est (il le voit, ou reconnaît sa voix) ; sinon « voix_<n> », la voix inconnue qu'il a
    entendue."""
    if id == "joueur" or id not in monde.objets or identifie(monde, "joueur", id):
        return id
    entree = monde.data.get("voix_entendues", {}).get(id)
    return f"{PREFIXE}{entree['n']}" if entree else id


def reel(monde, designation_):
    """Le personnage que désigne ``designation_`` (``designation``) ; None pour une voix que le
    joueur n'a pas entendue."""
    if not isinstance(designation_, str) or not designation_.startswith(PREFIXE):
        return designation_
    return next((s for s, e in monde.data.get("voix_entendues", {}).items()
                 if f"{PREFIXE}{e['n']}" == designation_ and s in monde.objets), None)


def nom_pour_joueur(monde, id, court=True):
    """Le nom que le joueur donne à ``id`` : son nom s'il sait qui c'est ; sinon « une voix
    inconnue », « une voix qui se dit Brune », et s'il connaît la vraie voix de Brune, « une voix qui
    se dit Brune (ce n'est pas la voix de Brune) » ; nommée par une autre voix, « une voix qu'on
    appelle Gorm »."""
    if designation(monde, id) == id:
        nom = monde.joueur["nom"] if id == "joueur" else monde.objets[id]["nom"]
        return nom.split(",")[0] if court else nom
    entree = monde.data.get("voix_entendues", {}).get(id) or {}
    nom, appelee = entree.get("se_dit"), not entree.get("se_dit") and entree.get("appelee")
    nom = nom or appelee
    if not nom or nom not in monde.objets and nom != "joueur":
        return "une voix inconnue"
    dit = monde.joueur["nom"] if nom == "joueur" else monde.objets[nom]["nom"].split(",")[0]
    nom_ = f"une voix qu'on appelle {dit}" if appelee else f"une voix qui se dit {dit}"
    return nom_ + f" (ce n'est pas la voix de {dit})" if connait(monde, "joueur", nom) else nom_


def personne_pour_joueur(monde, id, court=False):
    """(nom en tête de phrase, pronom, accord) pour dire au joueur ce que fait ``id``."""
    nom = nom_pour_joueur(monde, id, court=court)
    if designation(monde, id) != id:
        return nom[0].upper() + nom[1:], "elle", "e"
    f = monde.objets[id].get("genre") == "f"
    return nom, "elle" if f else "il", "e" if f else ""


def verifier_entrees(voix):
    assert isinstance(voix, dict) and all(
        isinstance(s, str) and isinstance(e, dict) and CHAMPS_VOIX <= set(e) <= CHAMPS_VOIX | OPTIONNELS
        and type(e["minute"]) is int and (e["se_dit"] is None or isinstance(e["se_dit"], str))
        and isinstance(e.get("appelee", ""), str) and type(e["mefiance"]) is bool
        and type(e["n"]) is int and e["n"] >= 1 for s, e in voix.items()), "Voix entendues invalides"
    assert len({e["n"] for e in voix.values()}) == len(voix), "Voix entendues invalides"
