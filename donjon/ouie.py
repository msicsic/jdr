"""L'ouïe, commune au joueur et aux PNJ : tout geste fait un bruit, la distance l'atténue, chacun
l'interprète selon ce qu'il croit.

Bruit. Chaque geste a une nature, déclarée une fois (``NATURES``, un geste absent de la table est
ordinaire), et chaque nature une intensité en crans (``INTENSITES``) : pas feutré < pas, geste
ordinaire < voix < geste bruyant < appel. Un geste fait pour n'être pas remarqué (à pas feutrés,
en douce) est feutré, sauf s'il est bruyant par nature ; un geste du joueur que l'arbitrage dit
fracassant (bruit 3) est bruyant. Le moteur le fait retentir là où il accomplit le geste, du
joueur (``moteur``) comme d'un PNJ (``pnj``) ; une parole retentit avec ses mots
(``social.faire_entendre``, ``paroles.preparer_parole``), un chuchotement est feutré.

Paroles. Qui saisit les mots d'une parole (``mots_saisis`` : elle lui parvient au seuil commun, et
il l'entend) la retient, même sans en être le destinataire (``social.retenir_parole``) ; plus loin,
ou derrière une porte, il n'entend qu'une voix. Les mots d'un chuchotement ne vont qu'à son
destinataire.

Atténuation. Un cran par palier de distance (``PALIERS`` : un cran ≈ une distance doublée) ; d'une
salle à l'autre, le bruit gagne le seuil (la distance compte), passe (``OUVERTURE``, ``PORTE``
fermée), puis repart du seuil de l'autre côté. Un auditeur l'entend si ce qui lui parvient atteint
son seuil (``SEUIL``) : un cran de mieux aux aguets (une ronde, une garde, aller voir), un de moins
au repos ; la PER modulée y ajoute un cran par quatre points au-dessus de la moyenne.

Interprétation (PNJ), selon ce qu'il croit ; ce qu'il voit n'a pas besoin de l'ouïe :
- connu : un bruit ordinaire venu de là où il croit quelqu'un (vu ou entendu récemment) ; il
  l'attribue à cette personne et met sa croyance à jour, sans se retourner ;
- une voix dont il saisit les mots : il reconnaît qui il connaît (``esprits.connait`` : vu, ou
  entendu parler) et le croit là d'où elle vient ; une voix jamais entendue est un bruit inconnu ;
- inconnu (personne de cru là) ou inhabituel (bruyant, appel) : tout près et hors de son regard,
  il se tourne pour voir (le temps de la rotation), et s'il voit l'auteur en plein geste illicite,
  il en est témoin (``pnj.temoigner_en_cours``) ; plus loin, ou sans rien voir, il retient « un
  bruit vers tel lieu » (un souvenir par lieu, le plus fort tant qu'il ne l'a pas vu), qui
  l'inquiète une fois, à la mesure de ce qu'il en entend (un appel proche, pleinement ; des pas
  lointains, à peine) ; chaque appel à l'aide l'inquiète de nouveau ;
- aller voir un autre lieu est un but du planificateur (``deliberation.bruit_a_voir``), après ce
  qui presse et avant la routine : son devoir de garde l'y envoie, et pour un fracas ou un appel,
  son courage aussi ; qui vient de parcourir ce lieu n'y retourne pas pour un bruit ordinaire.
  Le bruit est expliqué quand il y a vu quelqu'un ou l'a parcouru des yeux (``parcouru``) ;
- méfiance : le bruit ordinaire d'une personne dont il se méfie se surveille : de près, il se
  retourne comme pour un inconnu.

Le joueur entend par le même calcul : ce qui lui parvient est rangé dans ``data["bruits"]``, avec
le niveau et la direction d'où il arrive ; ``ecoute`` en fait « Tu entends… », sans nommer ce qu'il
ne connaît pas. Il choisit lui-même de se retourner.
"""
import heapq
from itertools import count

INTENSITES = {"feutre": 1, "pas": 3, "geste": 3, "voix": 4, "bruyant": 7, "appel": 9}
HABITUELS = ("feutre", "pas", "geste", "voix")
NATURES = {
    **dict.fromkeys(("attendre", "patienter", "tourner", "orienter", "observer", "examiner", "lire", "ecouter",
                     "inspecter", "reposer", "chauffer", "abriter"), None),
    **dict.fromkeys(("aller", "marcher", "chasser"), "pas"),
    **dict.fromkeys(("faufiler", "toucher", "chuchoter"), "feutre"),
    **dict.fromkeys(("parler", "dire", "demander", "confier", "acheter", "sifflement"), "voix"),
    **dict.fromkeys(("crocheter", "forcer", "frapper", "couper", "decouper", "sauter", "franchir_obstacle"), "bruyant"),
    **dict.fromkeys(("appel", "cri"), "appel"),
}
FRACAS = 3             # l'arbitrage du bruit d'un geste du joueur (0 à 3) : 3 est un fracas
PALIERS = (1, 3, 6, 12, 24)    # cases : chaque palier dépassé coûte un cran
OUVERTURE = 1          # crans perdus en passant une ouverture
PORTE = 3              # en passant une porte fermée
PLANCHER = -2          # au-dessous, plus personne n'entend rien : le bruit ne va pas plus loin
SEUIL = 1              # ce qui parvient à ce niveau s'entend sans y prêter l'oreille
PROCHE = 6             # cases : assez près pour se tourner vers un bruit et en voir la cause
PRES_DE = 1            # case : un bruit venu d'aussi près de là où il croit quelqu'un est le sien (un pas)
HABITUDE = 15          # minutes : qui vient de parcourir un lieu n'y retourne pas pour un bruit ordinaire


def nature(geste, discret=False, bruit=0):
    """La nature du bruit d'un geste ; None s'il n'en fait pas."""
    n = NATURES.get(geste, "geste")
    if n is None:
        return None
    if bruit >= FRACAS and INTENSITES[n] < INTENSITES["bruyant"]:
        n = "bruyant"
    return "feutre" if discret and n in ("pas", "geste") else n


def distance(a, b):
    """En distance réelle, comme toute portée en cases (``geometrie.distance``) : un bruit à quatre
    cases en diagonale vient de plus loin qu'à quatre cases droites."""
    from .geometrie import distance as reelle
    return reelle(a, b)


def perte(a, b):
    """Crans perdus d'une case à l'autre dans une salle ; sans cases, rien."""
    if a is None or b is None:
        return 0
    d = distance(a, b)
    return sum(d > p for p in PALIERS)


def _place(monde, qui):
    cases = monde.data.get("mode_cases")
    if qui == "joueur":
        j = monde.joueur
        return j["salle"], (tuple(j["position"]) if cases and j.get("position") is not None else None)
    o = monde.objets[qui]
    return o["lieu"], (tuple(o["position"]) if cases and o.get("position") is not None else None)


def _passages(monde):
    """{salle: [(case du seuil, salle voisine, case du seuil d'en face, crans perdus, direction par où il
    arrive dans la voisine)]} : les sorties, et l'appui vertical qui donne sur son palier."""
    from .spatial import _case_interieure
    salles, cases = monde.data["salles"], monde.data.get("mode_cases")
    resultat = {s: [] for s in salles}
    for s, salle in salles.items():
        for sortie in salle["sorties"].values():
            vers = sortie["vers"]
            if vers not in salles:
                continue
            porte = monde.objets.get(sortie.get("porte") or "")
            cout = PORTE if porte and not porte.get("ouverte") else OUVERTURE
            direction, retour = next(((d, r) for d, r in salles[vers]["sorties"].items()
                                      if r.get("vers") == s and r.get("porte") == sortie.get("porte")), (None, None))
            ici = _case_interieure(monde, s, sortie) if cases else None
            la = _case_interieure(monde, vers, retour) if cases and retour is not None else None
            resultat[s].append((ici, vers, la, cout, direction))
            if retour is None:  # Une sortie déclarée d'un seul côté porte le son dans les deux sens.
                resultat[vers].append((la, s, ici, cout, None))
    for o in monde.objets.values():
        a = o.get("appui_vertical") or {}
        bas, haut = a.get("bas"), a.get("haut")
        if bas in resultat and haut in resultat:
            resultat[bas].append((None, haut, None, OUVERTURE, "bas"))
            resultat[haut].append((None, bas, None, OUVERTURE, "haut"))
    return resultat


def propager(monde, salle, case, intensite):
    """Ce qu'un bruit fait en ``case`` de ``salle`` laisse à l'entrée de chaque salle qu'il gagne :
    {salle: [(case d'où il repart, niveau, direction par où il arrive)]} ; dans sa salle, sa case,
    son intensité, sans direction."""
    meilleurs = {(salle, case, None): intensite}
    file, ordre = [(-intensite, 0, salle, case)], count(1)
    passages = None
    while file:
        moins, _, s, c = heapq.heappop(file)
        niveau = -moins
        if passages is None:
            passages = _passages(monde)
        for seuil, vers, arrivee, cout, direction in passages[s]:
            reste = niveau - perte(c, seuil) - cout
            cle = (vers, arrivee, direction)
            if reste >= PLANCHER and reste > meilleurs.get(cle, PLANCHER - 1):
                meilleurs[cle] = reste
                heapq.heappush(file, (-reste, next(ordre), vers, arrivee))
    entrees = {}
    for (s, c, direction), niveau in meilleurs.items():
        entrees.setdefault(s, []).append((c, niveau, direction))
    return entrees


def parvenu(entrees, salle, case):
    """(niveau, direction) de ce qui parvient en ``case`` de ``salle`` ; None si rien n'y arrive."""
    meilleur = None
    for c, niveau, direction in entrees.get(salle, ()):
        reste = niveau - perte(c, case)
        if meilleur is None or reste > meilleur[0]:
            meilleur = (reste, direction)
    return meilleur if meilleur is not None and meilleur[0] >= PLANCHER else None


def finesse(monde, qui):
    """Ce que la PER modulée ajoute à l'oreille : un cran par quatre points au-dessus de la moyenne."""
    from .caractere import BASE, caracteristique
    return (caracteristique(monde, qui, "PER") - BASE) // 4


def aux_aguets(intention):
    """Une ronde, une garde, aller voir ou accourir : il prête l'oreille."""
    if not intention:
        return False
    but = intention["but"]
    return but["type"] in ("garder", "voir", "rejoindre") or but["type"] == "pulsion" and "periode" in but


def seuil(monde, id):
    """Le niveau à partir duquel ce PNJ entend : mieux aux aguets, moins bien au repos."""
    from .esprits import lire
    s = SEUIL - finesse(monde, id)
    intention = lire(monde, id)["intention"]
    if aux_aguets(intention):
        s -= 1
    elif intention and intention["plan"] and intention["plan"][0]["operation"] == "reposer":
        s += 1
    return s


def mots_saisis(monde, id, niveau):
    """Un PNJ saisit les mots d'une parole qui lui parvient au seuil commun, s'il l'entend lui-même
    (au repos, il lui faut un cran de plus) ; en deçà, il n'entend qu'une voix."""
    return niveau >= max(SEUIL, seuil(monde, id))


def saisissent(monde, auteur, geste="parler"):
    """Les personnages qui saisiraient, ici et maintenant, les mots d'une parole de ``auteur`` :
    {id: niveau parvenu}."""
    from .esprits import pnjs
    n = nature(geste)
    salle, case = _place(monde, auteur)
    if n is None or salle not in monde.data["salles"]:
        return {}
    entrees = propager(monde, salle, case, INTENSITES[n])
    resultat = {}
    for id in pnjs(monde):
        o = monde.objets[id]
        if id == auteur or not o.get("entend", True) or o["lieu"] not in entrees:
            continue
        parvient = parvenu(entrees, *_place(monde, id))
        if parvient is not None and mots_saisis(monde, id, parvient[0]):
            resultat[id] = parvient[0]
    return resultat


def saisit(monde, auteur, auditeur, geste="parler"):
    """``auditeur`` (un PNJ ou le joueur) saisirait-il, ici et maintenant, les mots d'une parole
    d'``auteur`` ? Par l'atténuation commune (distance réelle, passages, porte fermée) : un PNJ par
    ``mots_saisis``, le joueur quand elle lui parvient au seuil commun (une parole nette, ``ecoute``)."""
    n = nature(geste)
    salle, case = _place(monde, auteur)
    if n is None or salle not in monde.data["salles"]:
        return False
    if auditeur != "joueur" and not monde.objets[auditeur].get("entend", True):
        return False
    parvient = parvenu(propager(monde, salle, case, INTENSITES[n]), *_place(monde, auditeur))
    if parvient is None:
        return False
    return parvient[0] >= SEUIL if auditeur == "joueur" else mots_saisis(monde, auditeur, parvient[0])


def s_entendent(monde, a, b):
    """Se parler, c'est saisir chacun les mots de l'autre (``saisit``) : par une ouverture, contre une
    porte fermée, pas à l'autre bout d'une grande salle."""
    return saisit(monde, a, b) and saisit(monde, b, a)


def entend(monde, auteur, auditeur, geste="dire"):
    """Le niveau auquel le PNJ ``auditeur`` entend, ici et maintenant, le geste d'``auteur`` (un PNJ
    ou le joueur) ; None s'il ne l'entend pas (sous son seuil, ou trop loin)."""
    n = nature(geste)
    salle, case = _place(monde, auteur)
    if n is None or salle not in monde.data["salles"] or not monde.objets[auditeur].get("entend", True):
        return None
    parvient = parvenu(propager(monde, salle, case, INTENSITES[n]), *_place(monde, auditeur))
    return parvient[0] if parvient is not None and parvient[0] >= seuil(monde, auditeur) else None


def retentir(monde, auteur, geste, discret=False, bruit=0, texte="", cites=(), parole=None):
    """Le geste de ``auteur`` (un PNJ ou le joueur) retentit maintenant, là où il se tient : qui
    l'entend l'interprète ; ce qui parvient au joueur est rangé pour lui. Une ``parole`` ({a :
    ses destinataires, contenu : ce qu'elle transmet, typé}) est retenue par ceux qui en saisissent
    les mots sans en être les destinataires (``social.retenir_parole``). Renvoie ceux qui se sont
    retournés."""
    n = nature(geste, discret, bruit)
    salle, case = _place(monde, auteur)
    if n is None or salle not in monde.data["salles"]:
        return []
    from .esprits import pnjs
    from .temps import instant
    entrees = propager(monde, salle, case, INTENSITES[n])
    t = instant(monde)
    if auteur != "joueur":
        _au_joueur(monde, auteur, salle, case, n, entrees, t, texte, [c for c in cites if c])
    retournes, temoins = [], []
    for id in pnjs(monde):
        o = monde.objets[id]
        if id == auteur or not o.get("profil") or not o.get("entend", True) or o["lieu"] not in entrees:
            continue
        parvient = parvenu(entrees, *_place(monde, id))
        if parvient is None:
            continue
        if parole is not None and id not in parole["a"] and mots_saisis(monde, id, parvient[0]):
            temoins.append(id)
        if parvient[0] >= seuil(monde, id) and entendre(monde, id, auteur, salle, case, n, t, parvient[0]):
            retournes.append(id)
    if temoins:
        from .social import retenir_parole
        for id in temoins:
            retenir_parole(monde, id, auteur, parole["a"], texte, [c for c in cites if c], parole["contenu"])
    return retournes


# --- Le joueur ----------------------------------------------------------------------------

BRUITS_MAX = 80


def _au_joueur(monde, auteur, salle, case, n, entrees, t, texte, cites):
    """Ce qui parvient au joueur, s'il ne voit pas l'auteur faire : son niveau, d'où il arrive
    (``par`` : une sortie de sa salle, ``None`` tout près, « piece » plus loin dans la pièce). Le
    même bruit sans paroles, au même niveau et d'où il venait déjà, ne se range qu'une fois."""
    ici, position = _place(monde, "joueur")
    parvient = parvenu(entrees, ici, position)
    if parvient is None or monde.visible(auteur):
        return
    niveau, par = parvient
    if ici == salle:
        par = None if case is None or position is None or distance(case, position) <= PROCHE else "piece"
    entree = {"instant": t, "auteur": auteur, "salle": salle, "nature": n, "niveau": niveau, "par": par,
              "texte": texte, "cites": cites}
    bruits = monde.data.setdefault("bruits", [])
    if not texte:
        semblable = next((i for i, b in enumerate(bruits) if not b["texte"] and all(
            b[k] == entree[k] for k in ("auteur", "salle", "nature", "niveau", "par"))), None)
        if semblable is not None:
            del bruits[semblable]
    bruits.append(entree)
    del bruits[:-BRUITS_MAX]


# --- Les PNJ ------------------------------------------------------------------------------

def _crus_la(monde, id, salle, case):
    """Ceux qu'il croit, depuis peu, là d'où vient le bruit : dans la salle, et près de la case
    s'il sait où ils se tiennent et d'où vient le bruit."""
    from .esprits import RECENT, lire
    minute = monde.data["minutes"]
    crus = []
    for x, attributs in lire(monde, id)["croyances"].items():
        if x == id or not (x == "joueur" or monde.objets.get(x, {}).get("type") == "personnage"):
            continue
        c = attributs.get("lieu")
        if not c or c["valeur"] != salle or minute - c["minute"] > RECENT:
            continue
        if case is not None and c.get("case") and distance(c["case"], case) > PRES_DE:
            continue
        crus.append(x)
    return crus


def _attribuer(monde, id, crus, salle, case):
    """Il prête le bruit à celui qu'il croit là, le plus près d'où il vient : il le croit là."""
    from .esprits import croire, lire
    croyances = lire(monde, id)["croyances"]

    def ecart(x):
        c = croyances[x]["lieu"]
        return (distance(c["case"], case) if case is not None and c.get("case") else 0, x)
    x = min(crus, key=ecart)
    c = croyances[x]["lieu"]
    croire(monde, id, x, "lieu", salle, "entendu", salle=salle,
           case=list(case) if case is not None else c.get("case"))


def _se_tourner(monde, id, case, t):
    """Il se tourne vers le bruit : la rotation retarde la fin de son geste en cours ; ce qu'il
    voit alors devient croyance, et l'auteur d'un geste illicite en cours, un témoignage."""
    from .esprits import esprit, percevoir
    from .francais import designer
    from .pnj import _chroniquer, temoigner_en_cours
    from .spatial import QUART, orientation_vers, quarts
    o = monde.objets[id]
    vers = orientation_vers(tuple(o["position"]), tuple(case))
    if vers is None:
        return False
    e = esprit(monde, id)
    e["libre"] = max(e["libre"], t) + QUART * quarts(o.get("orientation"), vers)
    o["orientation"] = vers
    percevoir(monde, id)
    _chroniquer(monde, id, designer(o, debut=True) + " se retourne au bruit.", "ouie")
    temoigner_en_cours(monde)
    return True


def resolu(monde, id, souvenir):
    """Un bruit inconnu n'est plus à aller voir : oublié, ou expliqué depuis, parce qu'il y a vu
    quelqu'un. Parcourir le lieu des yeux efface les bruits qu'il en avait retenus (``parcouru``)."""
    from .esprits import RECENT, lire
    e, salle, minute = lire(monde, id), souvenir["salle"], souvenir["minute"]
    if monde.data["minutes"] - minute > RECENT:
        return True
    return any(x != id and (a.get("lieu") or {}).get("valeur") == salle and a["lieu"]["source"] == "vu"
               and a["lieu"]["minute"] > minute for x, a in e["croyances"].items()
               if x == "joueur" or monde.objets.get(x, {}).get("type") == "personnage")


def parcouru(monde, id, salle):
    """Il a parcouru ``salle`` des yeux : les bruits qu'il en avait retenus sont vus ; renvoie vrai
    s'il en attendait un."""
    from .esprits import esprit
    memoire = esprit(monde, id)["memoire"]
    vus = [s for s in memoire if s["type"] == "bruit" and s["salle"] == salle]
    attendu = any(not resolu(monde, id, s) for s in vus)
    memoire[:] = [s for s in memoire if not any(s is v for v in vus)]
    return attendu


def _bruit_inconnu(monde, id, salle, n, niveau):
    """Un bruit vers ce lieu, dont il ne sait rien : un souvenir par lieu, qui l'inquiète."""
    from .deliberation import inquieter
    from .esprits import esprit, memoriser
    from .pnj import _chroniquer
    from .social import _qui
    memoire = esprit(monde, id)["memoire"]
    anciens = [s for s in memoire if s["type"] == "bruit" and s["salle"] == salle]
    attente = [s for s in anciens if not resolu(monde, id, s)]
    memoire[:] = [s for s in memoire if not any(s is a for a in anciens)]
    # Un bruit qu'il attend déjà de ce lieu ne l'inquiète pas de nouveau ; un appel, si : chaque
    # appel à l'aide en est un nouveau. Il s'inquiète à la mesure de ce qu'il en entend : un appel
    # tout proche, pleinement ; des pas lointains, à peine.
    if not attente or n == "appel":
        inquieter(monde, id, "bruit", max(0, niveau) / INTENSITES["appel"])
    if not attente:
        _chroniquer(monde, id, f"{_qui(monde, id)} entend un bruit : {monde.data['salles'][salle]['nom']}.", "ouie")
    # Tant qu'il ne l'a pas vu, il en retient le plus fort.
    memoriser(monde, id, {"type": "bruit", "salle": salle,
                          "nature": max([n, *(s["nature"] for s in attente)], key=INTENSITES.get)})


def entendre(monde, id, auteur, salle, case, n, t, niveau=SEUIL):
    """Un PNJ entend le bruit d'``auteur`` et l'interprète selon ce qu'il croit ; vrai s'il s'est
    retourné."""
    from .esprits import lire, percoit
    if percoit(monde, id, auteur):
        return False  # Il le voit faire : l'ouïe n'y ajoute rien.
    o = monde.objets[id]
    ici = salle == o["lieu"] and case is not None and o.get("position") is not None
    if n == "voix" and mots_saisis(monde, id, niveau):
        # Il en saisit les mots : il reconnaît la voix de qui il connaît, et le croit là d'où elle
        # vient ; une voix qu'il n'a jamais entendue n'est à personne qu'il croie là.
        from .esprits import connait, croire
        if connait(monde, id, auteur):
            croire(monde, id, auteur, "lieu", salle, "entendu", salle=salle, case=list(case) if ici else None)
            crus = [auteur]
        else:
            crus = []
    else:
        crus = _crus_la(monde, id, salle, case if ici else None)
    inhabituel = n not in HABITUELS
    croyances = lire(monde, id)["croyances"]
    mefiance = any((croyances[x].get("fiable") or {}).get("valeur") is False for x in crus)
    if crus and not inhabituel and not mefiance:
        _attribuer(monde, id, crus, salle, case if ici else None)
        return False
    retourne = False
    if ici and distance(case, o["position"]) <= PROCHE:
        from .spatial import dans_le_regard
        if not dans_le_regard(monde, salle, case, id):
            retourne = _se_tourner(monde, id, case, t)
            if percoit(monde, id, auteur):
                return retourne
    if crus and not inhabituel:
        _attribuer(monde, id, crus, salle, case if ici else None)  # Il le surveille, de loin.
    else:
        _bruit_inconnu(monde, id, salle, n, niveau)
    return retourne
