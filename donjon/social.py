"""Couche sociale entre PNJ : nouvelles, rumeurs et réputations.

Un PNJ qui a une nouvelle (un geste illicite vu, un bien aperçu aux mains d'un autre, un
mensonge découvert, un objet disparu, une rumeur reçue) la confie à un personnage qu'il
perçoit dans sa salle et à qui il fait confiance ; le geste prend sa minute. Il ne la confie
ni à celui qu'elle accuse, ni à celui qui la lui a apprise. L'auditeur l'adopte avec la règle
des paroles du joueur : ce qu'il a vu récemment prime, sinon jet de CHA du locuteur contre
sa confiance. Une rumeur passe de proche en proche jusqu'au troisième relais, en perdant de
sa confiance. Le joueur entend ce qui se dit dans sa salle, en clair s'il connaît ce dont on
parle, sinon comme un échange à voix basse. Tout est déterministe ; Luna n'intervient pas.

Une parole, du joueur comme d'un PNJ, est entendue de tous ceux qui en saisissent les mots
(``ouie``) : qui n'en est pas le destinataire la retient aussi (``retenir_parole``), et ce
qu'elle transmet le touche par la même règle que le destinataire (``recevoir``) : une
affirmation se juge comme une confidence, une nouvelle comme une rumeur, un aveu se croit.
"""
from .esprits import croire, lire, memoriser, percoit, pnjs
from .francais import complement_de, designer
from .monde import normaliser

NOUVELLES = ("vu_agir", "vol_surpris", "vu_porter", "mensonge_decouvert", "mensonge_dementi", "absence")
RANG_MAX = 2           # une rumeur entendue de troisième main n'est plus répétée
GESTES = {"prendre": "a pris", "poser": "a posé", "ouvrir": "a ouvert", "fermer": "a fermé",
          "deverrouiller": "a déverrouillé", "verrouiller": "a verrouillé",
          "crocheter": "a crocheté la serrure de", "forcer": "a tenté de crocheter la serrure de",
          "manger": "a mangé une part de", "servir": "a servi une part de", "alimenter": "a rechargé",
          "allumer": "a allumé", "eteindre": "a éteint", "pousser": "a poussé"}


def _noyau(evenement):
    """Ce que dit la nouvelle, sans la trace de qui l'a dite à qui."""
    return {k: v for k, v in evenement.items() if k not in ("minute", "dit_a")}


def _fait(noyau):
    """Le fait dont parle la nouvelle, sans le lieu où chacun a vu l'objet aller : deux témoins
    du même geste racontent la même chose."""
    return {k: v for k, v in noyau.items() if k != "lieu"}


def accuse(evenement):
    if evenement["type"] in ("vu_agir", "vol_surpris", "vu_porter"):
        return evenement["auteur"]
    if evenement["type"] in ("mensonge_decouvert", "mensonge_dementi"):
        return evenement.get("locuteur", "joueur")
    return None


def _proprietaire(monde, evenement):
    """Propriétaire déclaré de l'objet ou de son contenant ; le porter ne suffit pas à le posséder."""
    o = monde.objets.get(evenement.get("objet") or "")
    while o and o["type"] != "personnage":
        if o.get("proprietaire"):
            return o["proprietaire"]
        o = monde.objets.get(o["lieu"])
    return None


def _croit_encore(monde, id, noyau):
    """On ne répète que ce qu'on croit encore."""
    croyances = lire(monde, id)["croyances"]
    if noyau["type"] == "absence":
        lieu = croyances.get(noyau["objet"], {}).get("lieu")
        return bool(lieu) and lieu["valeur"] is None
    return croyances.get(accuse(noyau), {}).get("fiable", {}).get("valeur") is not True


def nouvelles(monde, id):
    """(souvenir, noyau, rang) que le PNJ peut confier, du plus ancien au plus récent."""
    for souvenir in lire(monde, id)["memoire"]:
        if souvenir["type"] in NOUVELLES:
            noyau, rang, source = _noyau(souvenir), 0, None
        elif souvenir["type"] == "rumeur" and souvenir["rang"] < RANG_MAX:
            noyau, rang, source = souvenir["evenement"], souvenir["rang"], souvenir["de"]
        else:
            continue
        if (any(k not in monde.objets for k in (noyau.get("objet"),) if k and k != "joueur")
                or not _croit_encore(monde, id, noyau)):
            continue  # L'objet n'existe plus, ou il a changé d'avis : il n'y a plus rien à en dire.
        if "lieu" in noyau and _cru_ailleurs(monde, id, noyau):
            noyau = _fait(noyau)  # Il ne le croit plus là : il dit le geste, sans le lieu.
        yield souvenir, noyau, rang, source


def _cru_ailleurs(monde, id, noyau):
    """Depuis ce que dit la nouvelle, il a appris que l'objet n'est plus là où elle le met."""
    lieu = lire(monde, id)["croyances"].get(noyau["objet"], {}).get("lieu")
    return bool(lieu) and lieu["minute"] > noyau["lieu"]["minute"] and lieu["valeur"] != noyau["lieu"]["valeur"]


def _sait(monde, id, noyau):
    fait = _fait(noyau)
    return any((_fait(_noyau(s)) == fait if s["type"] in NOUVELLES
                else s["type"] == "rumeur" and _fait(s["evenement"]) == fait)
               for s in lire(monde, id)["memoire"])


def _auditeur(monde, id, souvenir, noyau, source):
    """Premier personnage présent à qui confier cette nouvelle, dans un ordre stable."""
    from .pnj import pourraient_se_parler
    croyances = lire(monde, id)["croyances"]
    for autre in sorted(pnjs(monde)):
        if (autre == id or autre in souvenir.get("dit_a", ()) or autre in (accuse(noyau), source)
                or not monde.objets[autre].get("profil")
                or monde.objets[autre]["lieu"] != monde.objets[id]["lieu"]
                or not pourraient_se_parler(monde, id, autre)
                or croyances.get(autre, {}).get("fiable", {}).get("valeur") is False):
            continue
        if noyau["type"] == "absence" and _proprietaire(monde, noyau) != autre:
            continue  # Un objet manquant ne regarde que son propriétaire.
        return autre
    return None


def _qui(monde, id):
    return monde.joueur["nom"] if id == "joueur" else monde.objets[id]["nom"].split(",")[0]


def phrase(monde, noyau):
    o = monde.objets.get(noyau.get("objet") or "")
    t = noyau["type"]
    if t == "absence":
        return designer(o) + " " + ("ont" if o.get("pluriel") else "a") + " disparu"
    qui = _qui(monde, accuse(noyau))
    if t in ("mensonge_decouvert", "mensonge_dementi"):
        return qui + " ment"
    if t == "vol_surpris":
        return qui + " a tenté de dérober " + designer(o)
    if t == "vu_porter":
        return qui + " porte " + designer(o) + ", qui n'est pas à " + ("lui" if monde.objets.get(accuse(noyau), {}).get("genre") != "f" else "elle")
    verbe = GESTES[noyau["operation"]]
    if noyau.get("objet") == "joueur":
        return qui + " " + verbe + " " + monde.joueur["nom"]  # Un geste contre lui (``pnj.CONTRAINTES``).
    return (qui + " " + (verbe[:-3] + " " + complement_de(o) if verbe.endswith(" de") else verbe + " " + designer(o))
            + _ou(monde, noyau))


def _ou(monde, noyau):
    """Où l'objet est allé, s'il l'a vu poser : « dans <salle> », « dans <contenant> » ; porté par
    l'auteur, la phrase le dit déjà (« a pris »)."""
    from .francais import lieu as designer_lieu
    lieu = (noyau.get("lieu") or {}).get("valeur")
    if lieu in monde.data["salles"]:
        return " dans " + designer_lieu(monde.data["salles"][lieu])
    if lieu in monde.objets and monde.objets[lieu]["type"] != "personnage":
        return " dans " + designer(monde.objets[lieu])
    return ""


def _lieu_dit(noyau):
    """Le lieu que la nouvelle donne à son objet (``_ou``), pour qui l'entend."""
    lieu = (noyau.get("lieu") or {}).get("valeur")
    return [lieu] if lieu and lieu != accuse(noyau) else []


def _adopter(monde, auditeur, locuteur, noyau, rang):
    """L'auditeur croit-il la nouvelle ? Effets sur ses croyances et ses besoins."""
    from .paroles import _stats_pnj, dementi, jet_persuasion
    objet = noyau.get("objet")
    if noyau["type"] == "absence" and dementi(monde, auditeur, objet, "lieu", None):
        croire(monde, auditeur, locuteur, "fiable", False, "vu")
        memoriser(monde, auditeur, {"type": "mensonge_dementi", "locuteur": locuteur, "sujet": objet, "attribut": "lieu"})
        return "dementi"
    if not jet_persuasion(monde, auditeur, locuteur, 10)[0]:
        memoriser(monde, auditeur, {"type": "parole_doutee", "locuteur": locuteur, "evenement": noyau})
        return "doute"
    confiance = round(0.7 * (0.5 if _stats_pnj(monde, auditeur)["INT"] <= 8 else 1.0) * 0.8 ** rang, 2)
    source = "dit:" + locuteur
    if noyau["type"] == "absence":
        croire(monde, auditeur, objet, "lieu", None, source, confiance, salle=None, case=None)
    elif accuse(noyau) != auditeur:
        _apprendre_lieu(monde, auditeur, noyau, source, confiance)
        actuelle = lire(monde, auditeur)["croyances"].get(accuse(noyau), {}).get("fiable")
        # Une méfiance qu'il tient de ses propres yeux ne devient pas un ouï-dire.
        if not (actuelle and actuelle["valeur"] is False and actuelle["source"] in ("vu", "essai")):
            croire(monde, auditeur, accuse(noyau), "fiable", False, source, confiance)
    return "crue"


def _apprendre_lieu(monde, auditeur, noyau, source, confiance):
    """Une nouvelle qui dit où l'objet est allé donne au destinataire une croyance de lieu, à la
    confiance du ouï-dire. Ce qu'il en a constaté lui-même après le geste rapporté (vu, essayé,
    entendu après la minute ``lieu["minute"]``) prime ; ne pas l'avoir trouvé là où il l'attendait
    ne dit pas qu'il n'est pas ailleurs, et un ouï-dire cède à la nouvelle qui le précise."""
    lieu, objet = noyau.get("lieu"), noyau.get("objet")
    if not lieu or objet not in monde.objets or lieu["valeur"] == auditeur:
        return
    if not (lieu["valeur"] in monde.data["salles"] or lieu["valeur"] in monde.objets or lieu["valeur"] == "joueur"):
        return  # Le lieu a disparu depuis : il n'y a plus rien à en croire.
    actuelle = lire(monde, auditeur)["croyances"].get(objet, {}).get("lieu")
    if (actuelle and actuelle["valeur"] is not None and actuelle["source"] in ("vu", "essai", "entendu")
            and actuelle["minute"] > lieu["minute"]):
        return
    croire(monde, auditeur, objet, "lieu", lieu["valeur"], source, confiance, salle=lieu["salle"],
           case=lieu["case"])


def faire_entendre(monde, id, auditeur, texte, cites, lignes, contenu=()):
    """Une parole retentit avec ses mots (``ouie``) : qui en saisit les mots sans en être le
    destinataire retient ce qu'elle transmet (``contenu``, typé : ``recevoir``). Ce que le joueur
    perçoit de l'échange, s'il le voit : en clair s'il connaît chacun de ceux dont on parle. Sans le
    voir (le noir, son dos), il n'en a que ce que son ouïe lui fait entendre (``ecoute`` : une voix
    qu'il reconnaît, ou « une voix »)."""
    from .ouie import retentir
    from .paroles import _connu_du_joueur
    retentir(monde, id, "dire", texte=texte, cites=[auditeur, *cites],
             parole={"a": [auditeur], "contenu": list(contenu)})
    a, b = monde.objets[id], monde.objets[auditeur]
    if a["lieu"] == monde.joueur["salle"] and monde.visible(id):
        if all(_connu_du_joueur(monde, x) for x in [id, auditeur, *cites] if x != "joueur"):
            lignes.append(texte)
        else:
            lignes.append(designer(a, debut=True) + " parle à voix basse avec " + designer(b) + ".")
    elif monde.visible(id):
        lignes.append(designer(a, debut=True) + " parle avec " + designer(b) + ".")


def _entendu(monde, id, auditeur, noyau, rang, lignes):
    cites = [x for x in (accuse(noyau), noyau.get("objet"), *_lieu_dit(noyau)) if x]
    faire_entendre(monde, id, auditeur, _qui(monde, id) + " glisse à " + _qui(monde, auditeur) + " que "
                   + phrase(monde, noyau) + ".", cites, lignes,
                   [{"type": "rumeur", "evenement": noyau, "rang": rang}])


def recevoir(monde, id, locuteur, c):
    """Ce qu'une parole transmet à ``id``, qui l'entend, destinataire ou non ; renvoie l'issue, ou
    None s'il n'y a rien à apprendre. Une affirmation se juge comme une confidence
    (``echanges.affirmer``) ; une nouvelle, comme une rumeur (``_adopter``) ; un aveu (le locuteur
    dit avoir fait un geste illicite) se croit : il ne le tient plus pour fiable et le sait de
    première main. Ce qu'on dit de lui-même ne lui apprend rien."""
    if c["type"] == "affirmation":
        if c["sujet"] == id:
            return None
        from .echanges import affirmer
        return affirmer(monde, locuteur, id, c["sujet"], c["attribut"], c["valeur"])
    noyau = c["evenement"]
    if accuse(noyau) == id or _sait(monde, id, noyau):
        return None
    if c["type"] == "aveu":
        actuelle = lire(monde, id)["croyances"].get(locuteur, {}).get("fiable")
        if not (actuelle and actuelle["valeur"] is False and actuelle["source"] in ("vu", "essai")):
            croire(monde, id, locuteur, "fiable", False, "entendu")
        issue, rang = "crue", 0
    else:
        issue, rang = _adopter(monde, id, locuteur, noyau, c["rang"]), c["rang"] + 1
    if issue == "crue":
        memoriser(monde, id, {"type": "rumeur", "de": locuteur, "rang": rang, "evenement": noyau})
        if _proprietaire(monde, noyau) == id:
            from .deliberation import VOL, relancer
            relancer(monde, id, "biens", 30 if noyau["type"] == "absence" else VOL // 2)
    return issue


def retenir_parole(monde, id, locuteur, destinataires, texte, cites, contenu):
    """``id`` saisit les mots d'une parole qui ne lui était pas adressée : il retient qu'elle a été
    dite, et à qui ; ce qu'elle transmet le touche comme le destinataire (``recevoir``), dans la
    limite de ce que l'INT de l'un et de l'autre fait passer. Une demande ou une prière adressée
    à un autre ne l'engage à rien."""
    from .paroles import _stats_pnj, capacite_transmission
    from .pnj import _chroniquer
    memoriser(monde, id, {"type": "parole", "locuteur": locuteur, "a": list(destinataires), "texte": texte[:240],
                          "cites": list(cites)})
    capacite = min(capacite_transmission(_stats_pnj(monde, x)["INT"]) for x in (locuteur, id))
    issues = [i for i in (recevoir(monde, id, locuteur, c) for c in contenu[:capacite]) if i]
    de = _qui(monde, locuteur)
    de = ("d'" if normaliser(de)[:1] in "aeiouyh" else "de ") + de
    _chroniquer(monde, id, f"{_qui(monde, id)} surprend les mots {de} à "
                + ", ".join(_qui(monde, x) for x in destinataires)
                + (f" ({', '.join(issues)})" if issues else "") + ".", "ouie")


def bavarder(monde, id, lignes):
    """Confie au plus une nouvelle ; renvoie True si la minute y est passée."""
    from .pnj import _chroniquer
    if not monde.objets[id].get("profil"):
        return False
    connues = list(nouvelles(monde, id))
    for souvenir, noyau, rang, source in reversed(connues):
        auditeur = _auditeur(monde, id, souvenir, noyau, source)
        if auditeur is None:
            continue
        # Une seule confidence par incident : ce qu'il sait du même accusé se dit d'un coup.
        lies = [x for x in connues if x[0] is souvenir or accuse(noyau) and accuse(x[1]) == accuse(noyau)]
        for autre, *_ in lies:
            if auditeur not in autre.get("dit_a", ()):
                autre.setdefault("dit_a", []).append(auditeur)
        inedits = [x for x in lies if not _sait(monde, auditeur, x[1])]
        if not inedits:
            continue  # Il le sait déjà : rien à apprendre, la minute n'est pas perdue.
        _, noyau, rang, _ = inedits[-1]
        issue = _adopter(monde, auditeur, id, noyau, rang)
        if issue == "crue":
            memoriser(monde, auditeur, {"type": "rumeur", "de": id, "rang": rang + 1, "evenement": noyau})
            siens = [x[1] for x in inedits if _proprietaire(monde, x[1]) == auditeur]
            if siens:
                from .deliberation import VOL, relancer
                relancer(monde, auditeur, "biens", 30 if all(x["type"] == "absence" for x in siens) else VOL // 2)
        _chroniquer(monde, id, f"{_qui(monde, id)} dit à {_qui(monde, auditeur)} que {phrase(monde, noyau)} ({issue}).",
                    "social")
        _entendu(monde, id, auditeur, noyau, rang, lignes)
        return True
    return False
