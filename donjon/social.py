"""Couche sociale entre PNJ : nouvelles, rumeurs et réputations.

Un PNJ qui a une nouvelle (un geste illicite vu, un bien aperçu aux mains d'un autre, un
mensonge découvert, un objet disparu, une rumeur reçue) la confie à un personnage qu'il
perçoit dans sa salle et à qui il fait confiance ; le geste prend sa minute. Il ne la confie
ni à celui qu'elle accuse, ni à celui qui la lui a apprise. L'auditeur l'adopte avec la règle
des paroles du joueur : ce qu'il a vu récemment prime, sinon jet de CHA du locuteur contre
sa confiance. Une rumeur passe de proche en proche jusqu'au troisième relais, en perdant de
sa confiance. Le joueur entend ce qui se dit dans sa salle, en clair s'il connaît ce dont on
parle, sinon comme un échange à voix basse. Tout est déterministe ; Luna n'intervient pas.
"""
from .esprits import croire, lire, memoriser, percoit, pnjs
from .francais import complement_de, designer

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
        yield souvenir, noyau, rang, source


def _sait(monde, id, noyau):
    return any((_noyau(s) == noyau if s["type"] in NOUVELLES else s["type"] == "rumeur" and s["evenement"] == noyau)
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
    return qui + " " + (verbe[:-3] + " " + complement_de(o) if verbe.endswith(" de") else verbe + " " + designer(o))


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
        croire(monde, auditeur, accuse(noyau), "fiable", False, source, confiance)
    return "crue"


def faire_entendre(monde, id, auditeur, texte, cites, lignes):
    """Ce que le joueur perçoit d'un échange : en clair s'il connaît chacun de ceux dont on parle."""
    from .ecoute import bruit
    from .paroles import _connu_du_joueur
    bruit(monde, id, "voix", texte, [auditeur, *cites])
    a, b = monde.objets[id], monde.objets[auditeur]
    if a["lieu"] == monde.joueur["salle"]:
        if all(_connu_du_joueur(monde, x) for x in [id, auditeur, *cites] if x != "joueur"):
            lignes.append(texte)
        else:
            lignes.append(designer(a, debut=True) + " parle à voix basse avec " + designer(b) + ".")
    elif monde.visible(id):
        lignes.append(designer(a, debut=True) + " parle avec " + designer(b) + ".")


def _entendu(monde, id, auditeur, noyau, lignes):
    cites = [x for x in (accuse(noyau), noyau.get("objet")) if x]
    faire_entendre(monde, id, auditeur, _qui(monde, id) + " glisse à " + _qui(monde, auditeur) + " que "
                   + phrase(monde, noyau) + ".", cites, lignes)


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
        _entendu(monde, id, auditeur, noyau, lignes)
        return True
    return False
