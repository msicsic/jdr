"""Laisser passer, demander le passage, pousser : trois règles du moteur, communes à tous, joueur
compris.

- **Laisser passer.** Qui doit s'arrêter sur la case d'un PNJ pour passer (le pas du joueur, la
  case d'où un PNJ ouvre une porte, celle où il atteint ce qu'il veut toucher) le voit s'écarter
  de lui-même vers une case voisine libre, hors de son chemin, le temps d'un pas de côté
  (``ECART``). Il reste s'il a une raison de rester (``raison_de_rester`` : un geste en cours là
  où il se tient) ou s'il ne veut pas aider ce passant (``refus_d_aider`` : il s'en méfie, ou sa
  fierté l'emporte de loin sur son altruisme). Garder un lieu, pour le moteur, c'est se tenir
  dans une salle : un pas de côté ne l'en fait pas sortir.
- **Demander le passage** : une demande sociale typée, tranchée par le moteur comme les autres
  demandes, jamais par le MJ : méfiance, raison de rester, puis, chez qui ne s'écarterait pas de
  lui-même, un jet de persuasion que l'altruisme facilite et que la fierté durcit. Acceptée, le
  PNJ s'écarte réellement.
- **Pousser** : un geste court (``POUSSEE``), jet de FOR opposé sur les caractéristiques
  modulées ; réussi, la personne est déplacée d'une case libre dans le sens de la poussée, sinon
  rien ne bouge. C'est une contrainte légère : la victime et ceux qui voient faire (registre des
  gestes en cours) cessent de croire l'auteur fiable. La douceur à son comble l'interdit ; pour
  les autres PNJ, c'est une faute au prix de la douceur (``caractere.prix_faute``).

Un PNJ bloqué (``pnj._marcher``) attend d'abord qu'on s'écarte, puis demande, puis pousse si ses
valeurs le lui permettent, enfin patiente et renonce à la longue. Le joueur, que le moteur ne
déplace jamais de lui-même, est prié de laisser passer : s'il reste, c'est un refus. Tout ce dont
dépend la suite est dans ``data`` (positions, esprits, registre des gestes).
"""
from .caractere import interdit, penchant, prix_faute, valeur
from .esprits import croire, esprit, lire, memoriser
from .francais import designer, sujet
from .temps import MINUTE, PAS_CHASSE, duree_pas, instant

ECART = PAS_CHASSE     # s'écarter : un pas de côté, 3 s (en biais, √2 fois plus : ``duree_ecart``)
POUSSEE = 30           # pousser quelqu'un : 3 s
DEMANDE = 100          # demander le passage : comme les autres paroles d'un PNJ, 10 s
REPONSE = 300          # le joueur prié de laisser passer qui n'a pas bougé 30 s plus tard a refusé
PASSAGE = 8            # DD d'une demande de passage, que l'altruisme abaisse et que la fierté relève
ORGUEIL = 30           # fierté au-delà de l'altruisme d'autant : il ne s'écarte pas sans qu'on le lui demande
# Huit directions, dans l'ordre du tour : une poussée écarte de biais, de côté ou droit devant.
ROSE = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))


# --- Où l'on se tient ------------------------------------------------------------------------

def place(monde, x):
    """(salle, case) du joueur ou d'un personnage placé."""
    if x == "joueur":
        return monde.joueur["salle"], tuple(monde.joueur["position"])
    o = monde.objets[x]
    return o["lieu"], tuple(o["position"])


def place_connue(monde, x):
    if x == "joueur":
        return monde.joueur.get("position") is not None
    o = monde.objets.get(x)
    return bool(o and o["type"] == "personnage" and o.get("lieu") in monde.data["salles"]
                and o.get("position") is not None)


def _globale(monde, salle, case):
    origine = monde.data["salles"][salle].get("plan", {}).get("origine", (0, 0))
    return origine[0] + case[0], origine[1] + case[1]


def sens(monde, de, vers):
    """Le pas d'une case qui va le mieux de la place ``de`` vers la place ``vers`` (signes)."""
    a, b = _globale(monde, *de), _globale(monde, *vers)
    return (b[0] > a[0]) - (b[0] < a[0]), (b[1] > a[1]) - (b[1] < a[1])


def au_contact(monde, a, b):
    """Un pas d'une case mène de l'un à l'autre (un seuil ouvert compris) : la main l'atteint."""
    from .monde import ErreurMonde
    from .spatial import pas_vers
    if not (monde.data.get("mode_cases") and place_connue(monde, a) and place_connue(monde, b)):
        return False
    depart, cible = place(monde, a), place(monde, b)
    v = sens(monde, depart, cible)
    if v == (0, 0):
        return False
    try:
        pas = pas_vers(monde, depart[0], depart[1], v)
    except ErreurMonde:
        return False
    return (pas["salle"], tuple(pas["position"])) == cible


def _pas_libre(monde, id, vecteur, pris):
    """Où mène un pas d'une case depuis la place de ``id`` (règles du pas), si nul ne s'y tient."""
    from .monde import ErreurMonde
    from .spatial import pas_vers
    salle, case = place(monde, id)
    try:
        pas = pas_vers(monde, salle, case, vecteur)
    except ErreurMonde:
        return None
    arrivee = (pas["salle"], tuple(pas["position"]))
    if arrivee in pris:
        return None
    if arrivee[0] != salle:
        from .eau import noyee
        if noyee(monde, arrivee[0]):
            return None
    return arrivee


# --- Laisser passer ----------------------------------------------------------------------------

def raison_de_rester(monde, id):
    """Ce qui le retient sur sa case : « geste », un geste en cours là où il se tient (ce qu'il
    touche est à portée de sa main, ou la porte fermée qu'il va ouvrir pour passer), ou None.
    Marcher, parcourir une salle des yeux, se reposer, se chauffer ou s'abriter ne retiennent pas
    sur une case : un pas de côté n'y change rien."""
    from .pnj import DURABLES, _a_toucher, _accessible
    intention = lire(monde, id)["intention"]
    if not intention or not intention["plan"]:
        return None
    etape = intention["plan"][0]
    if etape["operation"] == "aller":
        return "geste" if _devant_sa_porte(monde, id, etape["lieu"]) else None
    if etape["operation"] in ("inspecter", *DURABLES):
        return None
    if all(_accessible(monde, id, x) for x in _a_toucher(monde, id, etape) if x in monde.objets):
        return "geste"
    return None


def _devant_sa_porte(monde, id, lieu):
    """Il se tient devant la porte fermée par où passe son chemin vers ``lieu`` : il va l'ouvrir."""
    from .pnj import chemin
    from .spatial import _case_interieure
    o = monde.objets[id]
    route = chemin(monde, id, o["lieu"], lieu) if lieu in monde.data["salles"] else None
    if not route:
        return False
    porte = monde.objets.get(route[0].get("porte") or "")
    return bool(porte and not porte.get("ouverte")
                and _case_interieure(monde, o["lieu"], route[0]) == tuple(o["position"]))


def refus_d_aider(monde, id, passant):
    """Il ne veut pas aider ce passant : « mefiance » s'il le croit peu fiable, « orgueil » si sa
    fierté l'emporte de loin sur son altruisme (``ORGUEIL``) ; None sinon. Qui le croit fiable
    l'aide toujours."""
    fiable = lire(monde, id)["croyances"].get(passant, {}).get("fiable")
    if fiable is not None:
        return None if fiable["valeur"] else "mefiance"
    if valeur(monde, id, "fierte") - valeur(monde, id, "altruisme") >= ORGUEIL:
        return "orgueil"
    return None


def case_d_ecart(monde, id, passant, chemin=()):
    """La case voisine libre où il s'écarte, hors du chemin du passant : ni la case du passant, ni
    celles de son chemin, ni celle qui suit la sienne dans le sens du passage. De côté d'abord,
    puis en arrière (vers le passant), puis en avant ; un pas droit avant un pas en biais. Il ne
    quitte pas sa salle. (salle, case), ou None s'il n'a pas la place."""
    from .pnj import occupants
    salle, ici = place(monde, id)
    s = sens(monde, place(monde, passant), (salle, ici))
    evites = {(x, tuple(c)) for x, c in chemin} | {place(monde, passant), (salle, (ici[0] + s[0], ici[1] + s[1]))}
    pris = occupants(monde, id)
    candidats = []
    for v in ROSE:
        arrivee = _pas_libre(monde, id, v, pris)
        if arrivee is None or arrivee[0] != salle or arrivee in evites:
            continue
        produit = v[0] * s[0] + v[1] * s[1]
        candidats.append((abs(produit), produit > 0, v[0] * v[0] + v[1] * v[1], v, arrivee))
    return min(candidats)[-1] if candidats else None


def laisser_passer(monde, id, passant, chemin=()):
    """Le PNJ ``id`` s'écarterait-il de lui-même devant ``passant`` ? (case, None) s'il s'écarte
    vers cette case ; (None, raison) s'il reste : « geste », « mefiance », « orgueil » ou
    « place ». Une décision, sans rien changer au monde."""
    raison = raison_de_rester(monde, id) or refus_d_aider(monde, id, passant)
    if raison:
        return None, raison
    case = case_d_ecart(monde, id, passant, chemin)
    return (case, None) if case else (None, "place")


def _qui(monde, x):
    from .social import _qui as qui
    return qui(monde, x)


def duree_ecart(monde, id, case):
    """La durée du pas de côté de ``id`` vers ``case`` (salle, case) de sa salle : ``ECART``, √2
    fois plus en biais (``temps.duree_pas``)."""
    ici = place(monde, id)[1]
    return duree_pas(ECART, (case[1][0] - ici[0], case[1][1] - ici[1]))


def s_ecarter(monde, id, case, passant, lignes):
    """Il fait un pas de côté vers ``case`` pour laisser passer ``passant`` ; son geste suivant
    attend la fin de ce pas, puis le temps d'un pas de l'autre : celui qu'il laisse passer passe
    d'abord, au lieu de lui voir reprendre la place. Renvoie la durée du pas de côté."""
    from .geometrie import placer
    from .pnj import _chroniquer
    o = monde.objets[id]
    vu = monde.visible(id)
    duree = duree_ecart(monde, id, case)
    placer(o, case[0], list(case[1]))
    from .ouie import retentir
    retentir(monde, id, "marcher")  # Un pas de côté s'entend comme un autre pas.
    e = esprit(monde, id)
    from .pnj import PAS
    e["libre"] = max(e["libre"], instant(monde) + duree + PAS)
    _chroniquer(monde, id, f"{_qui(monde, id)} s'écarte pour laisser passer {_qui(monde, passant)}.", "deplacement")
    if vu or monde.visible(id):
        lignes.append(sujet(o) + " s'écarte pour "
                      + ("te laisser passer." if passant == "joueur"
                         else "laisser passer " + _designer(monde, passant) + "."))
    elif passant == "joueur":
        lignes.append("Quelqu'un s'écarte devant toi.")
    return duree


def _designer(monde, x):
    return "toi" if x == "joueur" else designer(monde.objets[x])


# --- Demander le passage ------------------------------------------------------------------------

def demander_passage(monde, id, demandeur, lignes, chemin=()):
    """``demandeur`` prie le PNJ ``id`` de s'écarter. Renvoie l'issue, que le moteur décide seul :
    « ecarte » (il s'écarte vraiment), « geste », « mefiance », « place », « refus », ou
    « inutile » sans cases ni places."""
    from .paroles import jet_persuasion
    if not (monde.data.get("mode_cases") and place_connue(monde, id) and place_connue(monde, demandeur)):
        return "inutile"
    raison = raison_de_rester(monde, id)
    if raison:
        return raison
    if refus_d_aider(monde, id, demandeur) == "mefiance":
        return "mefiance"
    case = case_d_ecart(monde, id, demandeur, chemin)
    if case is None:
        return "place"
    # Qui s'écarterait de lui-même accepte ; l'orgueilleux se laisse convaincre, ou non.
    dd = PASSAGE - penchant(monde, id, "altruisme") + penchant(monde, id, "fierte")
    if refus_d_aider(monde, id, demandeur) == "orgueil" and not jet_persuasion(monde, id, demandeur, dd)[0]:
        return "refus"
    s_ecarter(monde, id, case, demandeur, lignes)
    return "ecarte"


def _demande(monde, id, autre):
    """La dernière fois qu'il a prié ``autre`` (le joueur) de le laisser passer, il y a moins de
    ``REDEMANDE`` minutes : depuis combien de dixièmes de seconde, ou None."""
    from .deliberation import REDEMANDE
    s = next((s for s in reversed(lire(monde, id)["memoire"]) if s["type"] == "passage_demande" and s["a"] == autre),
             None)
    if s is None or monde.data["minutes"] - s["minute"] >= REDEMANDE:
        return None
    return instant(monde) - s["instant"]


def refus_de_passage(monde, id, autre):
    """Un refus récent d'``autre`` de le laisser passer ; le joueur prié de laisser passer qui
    n'a pas bougé ``REPONSE`` plus tard a refusé."""
    from .deliberation import refuse_recemment
    if refuse_recemment(monde, id, autre, "passage"):
        return True
    depuis = _demande(monde, id, autre)
    return depuis is not None and depuis >= REPONSE


def _demande_en_cours(monde, id, autre):
    depuis = _demande(monde, id, autre)
    return depuis is not None and depuis < REPONSE


def _prier(monde, id, autre, chemin, lignes):
    """Le PNJ ``id`` demande à ``autre`` de le laisser passer : un geste social."""
    from .ouie import retentir
    from .pnj import _chroniquer
    a, b = _qui(monde, id), _qui(monde, autre)
    le = "la" if monde.objets[id].get("genre") == "f" else "le"
    if autre == "joueur":
        texte = f"{a} te demande de {le} laisser passer."
        memoriser(monde, id, {"type": "passage_demande", "a": "joueur", "instant": instant(monde)})
        _chroniquer(monde, id, f"{a} demande à {b} de {le} laisser passer.", "social")
        if monde.visible(id):
            lignes.append(texte)  # Il le voit le lui demander : c'est dit, sans écho à rendre.
        # Sa voix retentit : le joueur qui ne le voit pas l'entend (``ecoute.rendre``), les autres aussi.
        retentir(monde, id, "dire", texte=texte, cites=["joueur"], parole={"a": ["joueur"], "contenu": []})
        return
    issue = demander_passage(monde, autre, id, [], chemin)  # Ce qu'il en voit est dit ci-dessous.
    _chroniquer(monde, id, f"{a} demande à {b} de {le} laisser passer ({issue}).", "social")
    from .social import faire_entendre
    texte = f"{a} demande à {b} de {le} laisser passer." + (f" {b} s'écarte." if issue == "ecarte" else f" {b} refuse.")
    faire_entendre(monde, id, autre, texte, [], lignes)
    if issue != "ecarte":
        memoriser(monde, id, {"type": "refus", "de": autre, "operation": "passage", "raison": issue})


# --- Pousser -------------------------------------------------------------------------------------

def directions_de_poussee(monde, auteur, victime):
    """Les pas qu'une poussée peut faire faire à la victime, jamais vers l'auteur : dans l'ordre
    où l'on écarte quelqu'un de son chemin, de biais, puis de côté, et droit devant en dernier."""
    axe = sens(monde, place(monde, auteur), place(monde, victime))
    if axe == (0, 0):
        return []
    i = ROSE.index(axe)
    return [ROSE[(i + 1) % 8], ROSE[(i - 1) % 8], ROSE[(i + 2) % 8], ROSE[(i - 2) % 8], axe]


def destination_poussee(monde, auteur, victime, vecteur=None, evites=()):
    """La place où la poussée envoie la victime (salle, case), par les règles du pas, sur une case
    où nul ne se tient ; None s'il n'y en a pas. ``vecteur`` impose la direction, qui ne doit pas
    ramener la victime vers l'auteur ; sans lui, la première place hors de ``evites`` (le chemin
    de l'auteur), sinon la première tout court."""
    from .pnj import occupants
    permis = directions_de_poussee(monde, auteur, victime)
    pris = occupants(monde, victime)
    places = [_pas_libre(monde, victime, v, pris) for v in ([tuple(vecteur)] if vecteur else permis) if v in permis]
    places = [x for x in places if x is not None]
    return next((x for x in places if x not in set(evites)), places[0] if places else None)


def pousserait(monde, id, besoin=None):
    """Un PNJ envisage-t-il de pousser quelqu'un ? Jamais à la douceur entière ; sinon si la faute,
    au prix de sa douceur et de sa détresse, reste dans ce que vaut son but (``prix_faute``)."""
    if not monde.objets[id].get("profil") or interdit(monde, id, "douceur"):
        return False
    return prix_faute(monde, id, besoin, "douceur") is not None


def jet_oppose(monde, auteur, victime):
    """d20 + FOR modulée de l'auteur contre d20 + FOR modulée de la victime ; l'égalité ne déplace pas."""
    from .caractere import modificateur
    return (monde.d20() + modificateur(monde, auteur, "FOR")
            > monde.d20() + modificateur(monde, victime, "FOR"))


def deplacer_personne(monde, x, arrivee):
    """La personne poussée change de case (et de salle, par un seuil ouvert)."""
    from .geometrie import placer
    salle, case = arrivee
    if x == "joueur":
        monde.joueur["salle"], monde.joueur["position"] = salle, list(case)
        if salle not in monde.data["visitees"]:
            monde.data["visitees"].append(salle)
        return
    o = monde.objets[x]
    o["lieu"] = salle
    placer(o, salle, list(case))
    e = esprit(monde, x)
    e["libre"] = max(e["libre"], instant(monde) + POUSSEE)


def subir(monde, victime, auteur):
    """La victime d'une bousculade n'en garde pas confiance en son auteur, et s'en inquiète."""
    if victime == "joueur":
        return
    from .deliberation import inquieter
    croire(monde, victime, auteur, "fiable", False, "vu")
    memoriser(monde, victime, {"type": "pousse", "auteur": auteur})
    inquieter(monde, victime, "illicite")


def appliquer_poussee(monde, auteur, victime, arrivee, lignes):
    """Le résultat d'une poussée : la victime déplacée d'une case si ``arrivee``, sinon rien ne
    bouge ; elle la subit dans les deux cas. Les témoins viennent du registre des gestes."""
    from .pnj import _chroniquer
    reussie = arrivee is not None
    # Ce que le joueur voyait au moment du geste : on sait qui l'on vient de voir pousser.
    vus = {x for x in (auteur, victime) if x != "joueur" and monde.visible(x)}
    if reussie:
        deplacer_personne(monde, victime, arrivee)
    subir(monde, victime, auteur)
    a, b = _qui(monde, auteur), _qui(monde, victime)
    _chroniquer_auteur = auteur if auteur != "joueur" else victime
    _chroniquer(monde, _chroniquer_auteur, f"{a} pousse {b}" + (" ; " + b + " recule d'un pas." if reussie else
                                                              ", qui tient bon."), "geste")
    vb = None if victime == "joueur" else monde.objets[victime]
    if auteur == "joueur":
        lignes.append(f"Tu pousses {designer(vb)}" + (" : " + _pronom(vb) + " recule d'un pas." if reussie else
                                                      ", qui tient bon."))
    elif victime == "joueur":
        va = monde.objets[auteur]
        nom = sujet(va) if auteur in vus else "Quelqu'un"
        lignes.append(nom + (" te pousse : tu recules d'un pas." if reussie else " tente de te pousser ; tu tiens bon."))
    elif vus:
        lignes.append(sujet(monde.objets[auteur]) + " pousse " + designer(vb)
                      + (" : " + _pronom(vb) + " recule d'un pas." if reussie else ", qui tient bon."))
    return reussie


def _pronom(o):
    return "elle" if o.get("genre") == "f" else "il"


def pousser(monde, id, victime, lignes, gestes, chemin=()):
    """Le PNJ ``id`` écarte ``victime`` de son chemin en la poussant ; une poussée qui la laisserait
    sur ce chemin ne se tente pas. Le geste entre au registre des gestes en cours (``gestes``),
    d'où viennent les témoins."""
    evites = {(s, tuple(c)) for s, c in chemin}
    arrivee = destination_poussee(monde, id, victime, evites=evites)
    if arrivee is None or arrivee in evites:
        return False
    from .pnj import _faire_face
    _faire_face(monde, id, victime)
    reussie = jet_oppose(monde, id, victime)
    from .ouie import retentir
    retentir(monde, id, "pousser")
    appliquer_poussee(monde, id, victime, arrivee if reussie else None, lignes)
    memoriser(monde, id, {"type": "a_pousse", "victime": victime})
    gestes.append((id, "pousser", victime))
    return True


def _noms(vecteurs):
    from .spatial import VECTEURS
    return [next(n for n, v in VECTEURS.items() if v == x and len(n) > 2) for x in vecteurs]


def preparer_poussee(monde, p, plan):
    """L'action pousser du joueur : cible = un personnage au contact, outil = la direction de la
    poussée (vide : l'écarter de son chemin, de biais, de côté, droit devant en dernier). Jet de FOR
    opposé (``Plan.oppose``)."""
    from .esprits import pnjs
    from .monde import ErreurMonde
    from .refus import inaccessible, liste
    from .spatial import VECTEURS
    cible, direction = p["cible"], p["outil"]
    if not monde.data.get("mode_cases"):
        raise ErreurMonde("Lance cette partie avec --cases pour pousser quelqu'un.",
                          "partie sans cases : sans positions, pousser est impossible.")
    if p["methode"] != "simple" or p["difficulte"]:
        raise ErreurMonde("Pousser se fait à mains nues ; le moteur fixe le jet.",
                          "pousser : methode simple, difficulte 0 (jet de FOR opposé, fixé par le moteur).")
    contact = sorted(x for x in pnjs(monde) if monde.visible(x) and au_contact(monde, "joueur", x))
    o = monde.objets.get(cible)
    if o is not None and o["type"] != "personnage":
        raise ErreurMonde("On ne pousse ainsi qu'une personne.",
                          f"pousser : cible = un personnage au contact de Corvus, parmi {liste(contact)} ; "
                          f"{cible} est un objet (pour le déplacer : composer, deplacer).")
    if o is None or not (monde.visible(cible) or cible in monde.data.get("entendus", [])):
        raise inaccessible(monde, cible, filtre=lambda x: x["type"] == "personnage")
    if not au_contact(monde, "joueur", cible):
        raise ErreurMonde(designer(o, debut=True) + " est trop loin pour que tu "
                          + ("la" if o.get("genre") == "f" else "le") + " pousses.",
                          f"pousser exige le contact (une case voisine) : approche-toi d'abord de {cible} (marcher) ; "
                          f"personnages au contact : {liste(contact)}.")
    permis = directions_de_poussee(monde, "joueur", cible)
    vecteur = None
    if direction:
        if direction not in VECTEURS:
            raise ErreurMonde("Pousse vers une direction : nord, sud, est, ouest, nord-est…",
                              "outil = la direction de la poussée (exception au champ outil), parmi "
                              f"{', '.join(_noms(permis))}, ou vide pour l'écarter de son chemin ; reçu « {direction} ».")
        vecteur = VECTEURS[direction]
        if vecteur not in permis:
            raise ErreurMonde("On ne pousse pas quelqu'un vers soi.",
                              f"outil : une direction qui éloigne {cible} de Corvus, parmi {', '.join(_noms(permis))}, "
                              "ou vide.")
    arrivee = destination_poussee(monde, "joueur", cible, vecteur)
    if arrivee is None:
        raise ErreurMonde(designer(o, debut=True) + " n'a nulle part où reculer" + (" de ce côté." if vecteur else "."),
                          f"aucune case libre derrière {cible} vers {', '.join(_noms([vecteur] if vecteur else permis))} "
                          "(mur, obstacle, porte fermée ou quelqu'un) : d'ici, la poussée ne le déplacerait pas.")
    plan.titre = "Pousser " + designer(o) + (" vers " + _noms([vecteur])[0] if vecteur else "") + "."
    plan.stat, plan.oppose = "FOR", cible
    plan.minutes, plan.dixiemes, plan.bruit = 0, POUSSEE, 1
    plan.risque = ("Réussie ou non, la bousculade te coûte la confiance de " + designer(o)
                   + " et de quiconque te voit faire.")
    plan.effets = [("pousser", cible, {"salle": arrivee[0], "position": list(arrivee[1])})]
    plan.echec = [("pousser", cible, None)]
    return plan


def a_pousse(monde, id, victime):
    from .deliberation import REDEMANDE
    minute = monde.data["minutes"]
    return any(s["type"] == "a_pousse" and s["victime"] == victime and minute - s["minute"] < REDEMANDE
               for s in lire(monde, id)["memoire"])


# --- Un PNJ bloqué ---------------------------------------------------------------------------------

def faire_place(monde, id, autre, chemin, lignes, gestes):
    """Le PNJ ``id`` doit s'arrêter sur la case d'``autre`` pour passer ou atteindre ce qu'il vise.
    Renvoie la durée de ce qu'il fait : attendre qu'``autre`` s'écarte de lui-même, ou qu'il ait
    fini le geste qui le retient là ; sinon le lui demander, le pousser si ses valeurs le
    permettent, ou patienter jusqu'à la minute suivante (à la longue, il renonce)."""
    from .pnj import PAS
    t = instant(monde)
    if autre != "joueur":
        case, raison = laisser_passer(monde, autre, id, chemin)
        if case is not None:
            return s_ecarter(monde, autre, case, id, lignes)
        if raison == "geste":
            return PAS  # Il est occupé là (la porte qu'il ouvre, ce qu'il touche) : on attend qu'il ait fini.
    if not refus_de_passage(monde, id, autre):
        if _demande_en_cours(monde, id, autre):
            return PAS  # Le joueur prié de laisser passer a le temps de bouger (``REPONSE``).
        if not _peut_prier(monde, id, autre):
            return _patienter(monde, id, t)
        _prier(monde, id, autre, chemin, lignes)
        return DEMANDE
    intention = lire(monde, id)["intention"]
    besoin = intention["motif"] if intention else None
    if not a_pousse(monde, id, autre) and pousserait(monde, id, besoin) and pousser(monde, id, autre, lignes, gestes, chemin):
        return POUSSEE
    return _patienter(monde, id, t)


def _peut_prier(monde, id, autre):
    """Pour demander, ils se parlent (``pnj.se_parler`` : chacun saisit les mots de l'autre et sait
    qui lui parle). Le joueur : le PNJ ne prie que lui qu'il sait là (vu, ou reconnu à la voix
    depuis peu : ``pnj.croit_present``), et seulement s'il en saisirait les mots ; il se tourne
    vers lui."""
    from .ouie import saisit
    from .pnj import _faire_face, croit_present, se_parler
    if autre != "joueur":
        return se_parler(monde, id, autre)
    if not (croit_present(monde, id, "joueur") and saisit(monde, id, "joueur")):
        return False
    _faire_face(monde, id, "joueur")
    return True


def _patienter(monde, id, t):
    """Personne ne lui fait place : il patiente jusqu'à la minute suivante ; un but ordinaire finit
    par être abandonné (``PATIENCE``), un réflexe ou une stratégie attendent leur propre terme."""
    from .deliberation import PATIENCE, renoncer
    intention = esprit(monde, id)["intention"]
    if intention and intention["motif"] != "alerte" and intention["but"]["type"] != "strategie":
        intention["attente"] += 1
        if intention["attente"] > PATIENCE:
            renoncer(monde, id, monde.data["minutes"])
    return MINUTE - t % MINUTE
