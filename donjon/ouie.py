"""L'ouïe, commune au joueur et aux PNJ : tout geste fait un bruit, la distance l'atténue, chacun
l'interprète selon ce qu'il croit.

Bruit. Chaque geste a une nature, déclarée une fois (``NATURES``, un geste absent de la table est
ordinaire), et chaque nature une intensité en crans (``INTENSITES``) : pas feutré < pas, geste
ordinaire < voix < geste bruyant < appel. Un geste fait pour n'être pas remarqué (à pas feutrés,
en douce) est feutré, sauf s'il est bruyant par nature ; un geste du joueur que l'arbitrage dit
fracassant (bruit 3) est bruyant. Un crochetage sonne selon l'adresse (``nature_crochetage``) :
réussi, un geste ordinaire ; manqué, un fracas. Le moteur le fait retentir là où il accomplit le geste, du
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
- connu : un bruit ordinaire compatible avec une présence crue récente ; il l'attribue sans se
  retourner. Le recalage précis reste dans la zone crue, la marche possible ne se confirme pas ;
- une voix dont il saisit les mots : s'il voit qui parle, il connaîtra sa voix ; sinon il la
  reconnaît ou non (``voix.reconnaitre``) : une voix connue, il croit son porteur là d'où elle
  vient ; une voix qui s'était nommée, il croit celui qu'elle a dit être là, comme un ouï-dire ;
  une voix jamais entendue est un bruit inconnu, qu'il retient comme une voix inconnue ;
- héler (``hele``) : un cri, de la portée d'un appel. Qui en saisit les mots entend qu'on appelle
  tel nom, sans alarme ; sans les mots, c'est un cri qu'il ne comprend pas, inquiétant comme tout
  bruit fort inconnu ; un appel à l'aide reste un appel ;
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
from . import memoire
import heapq
from itertools import count

from .geometrie import distance as _reelle

INTENSITES = {"feutre": 1, "pas": 3, "geste": 3, "voix": 4, "eclat": 6, "bruyant": 7, "hele": 9, "appel": 9, "cri": 9}
HABITUELS = ("feutre", "pas", "geste", "voix")
VOCALES = ("voix", "eclat", "hele")   # ce qui porte des mots, et fait reconnaître une voix
NATURES = {
    **dict.fromkeys(("attendre", "patienter", "tourner", "orienter", "observer", "examiner", "lire", "ecouter",
                     "inspecter", "reposer", "chauffer", "abriter"), None),
    **dict.fromkeys(("aller", "marcher", "chasser"), "pas"),
    **dict.fromkeys(("faufiler", "toucher", "chuchoter"), "feutre"),
    **dict.fromkeys(("parler", "dire", "demander", "confier", "acheter", "demander_feu"), "voix"),
    # Un sifflement porte loin et ne dit rien : inhabituel comme un fracas. Un crochetage dont on
    # connaît le jet sonne selon l'adresse (``nature_crochetage``) ; sinon, comme un fracas.
    **dict.fromkeys(("crocheter", "forcer", "frapper", "assommer", "couper", "decouper", "sauter", "franchir_obstacle",
                     "sifflement"), "bruyant"),
    # Héler quelqu'un par son nom est un cri : même portée qu'un appel ; ce sont les mots qui
    # l'en distinguent, pour qui les saisit (``entendre``).
    "heler": "hele",
    "contredire": "voix", "disputer": "eclat",
    # Un appel à l'aide, un cri : la voix à pleine force, sans mots qu'on saisisse ; qui connaît
    # cette voix sait qui crie (``entendre``).
    "appel": "appel", "cri": "cri",
    "ramper": "feutre", "enjamber": "pas", "escalader": "geste",
}
# Le son d'un objet (une cloche, ``sonorite``) ou un son improvisé, selon son intensité déclarée (1 à
# 3) : un tintement comme un geste, un son franc comme un fracas, une cloche d'alarme comme un appel.
SONS = {1: "geste", 2: "bruyant", 3: "appel"}
FRACAS = 3             # l'arbitrage du bruit d'un geste du joueur (0 à 3) : 3 est un fracas
AISANCE = 0            # marge du jet sur son seuil à partir de laquelle la serrure cède sans fracas (``nature_crochetage``)
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


def nature_crochetage(marge, discret=False):
    """Le bruit d'un crochetage selon l'adresse, règle commune au joueur et aux PNJ. ``marge`` : de
    combien son jet a passé le seuil (None : manqué). Réussi (``AISANCE`` : toute réussite), la serrure
    cède sous la main : un geste ordinaire, feutré s'il le fait en douce ; l'adresse (la DEX, la
    lumière qui font le jet) en fait la part. Manqué, il s'acharne sur la serrure : un fracas, comme
    forcer (``NATURES``, qui garde ce fracas pour un crochetage dont on ignore le jet)."""
    if marge is None or marge < AISANCE:
        return "bruyant"
    return "feutre" if discret else "geste"


def distance(a, b):
    """En distance réelle, comme toute portée en cases (``geometrie.distance``) : un bruit à quatre
    cases en diagonale vient de plus loin qu'à quatre cases droites."""
    return _reelle(a, b)


def perte(a, b):
    """Crans perdus d'une case à l'autre dans une salle ; sans cases, rien."""
    if a is None or b is None:
        return 0
    d = distance(a, b)
    return sum(d > p for p in PALIERS)


def _place(monde, qui):
    from .presence import parti
    if parti(monde, qui):
        return None, None
    cases = monde.data.get("mode_cases")
    if qui == "joueur":
        j = monde.joueur
        return j["salle"], (tuple(j["position"]) if cases and j.get("position") is not None else None)
    o = monde.objets[qui]
    return o["lieu"], (tuple(o["position"]) if cases and o.get("position") is not None else None)


PASSAGES_GARDES = 16    # relevés des passages gardés par géométrie (``_passages``)


def _passages(monde):
    """{salle: [(case du seuil, salle voisine, case du seuil d'en face, crans perdus, direction par où il
    arrive dans la voisine)]} : les sorties, et l'appui vertical qui donne sur son palier. Ils ne
    dépendent que de la géométrie des salles, des portes ouvertes ou fermées et des appuis verticaux :
    dans ``spatial.vue_memorisee``, gardés sous cette clé (à ne pas modifier), recomparés en
    vérification (``spatial.VERIFICATION``)."""
    from .spatial import a_verifier
    cache = getattr(monde, "_cache_vue", None)
    if cache is None:
        return _relever_passages(monde)
    objets, salles = monde.objets, monde.data["salles"]
    portes = tuple((id, id in objets and bool(objets[id].get("ouverte")))
                   for salle in salles.values() for x in salle["sorties"].values() for id in (x.get("porte") or "",))
    appuis = tuple(((o.get("appui_vertical") or {}).get("bas"), (o.get("appui_vertical") or {}).get("haut"))
                   for o in objets.values() if o.get("appui_vertical"))
    cle = (bool(monde.data.get("mode_cases")), portes, appuis)
    gardes = cache["persistant"].setdefault("passages", {})
    if cle not in gardes:
        if len(gardes) >= PASSAGES_GARDES:
            del gardes[next(iter(gardes))]
        gardes[cle] = _relever_passages(monde)
    elif a_verifier():
        assert gardes[cle] == _relever_passages(monde), "Passages mémorisés périmés"
    return gardes[cle]


def _relever_passages(monde):
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


def saisissent(monde, auteur, geste="parler", force=None):
    """Les personnages qui saisiraient, ici et maintenant, les mots d'une parole de ``auteur`` :
    {id: niveau parvenu}."""
    from .corps import conscient
    from .esprits import pnjs
    n = force or nature(geste)
    salle, case = _place(monde, auteur)
    if n is None or salle not in monde.data["salles"]:
        return {}
    entrees = propager(monde, salle, case, INTENSITES[n])
    resultat = {}
    for id in pnjs(monde):
        o = monde.objets[id]
        if id == auteur or not conscient(monde, id) or not o.get("entend", True) or o["lieu"] not in entrees:
            continue
        parvient = parvenu(entrees, *_place(monde, id))
        if parvient is not None and mots_saisis(monde, id, parvient[0]):
            resultat[id] = parvient[0]
    return resultat


def saisit(monde, auteur, auditeur, geste="parler", force=None):
    """``auditeur`` (un PNJ ou le joueur) saisirait-il, ici et maintenant, les mots d'une parole
    d'``auteur`` ? Par l'atténuation commune (distance réelle, passages, porte fermée) : un PNJ par
    ``mots_saisis``, le joueur quand elle lui parvient au seuil commun (une parole nette, ``ecoute``)."""
    from .corps import conscient
    if not conscient(monde, auditeur):
        return False
    n = force or nature(geste)
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


def auditeurs_parole(monde, auteur, geste="parler", force=None):
    """Auditeurs réels d'une réplique affichée : les PNJ et le joueur soumis
    au même trajet acoustique, sans supposer qu'il est dans la salle du locuteur."""
    auditeurs = set(saisissent(monde, auteur, geste, force))
    if auteur != "joueur" and saisit(monde, auteur, "joueur", geste, force):
        auditeurs.add("joueur")
    return sorted(auditeurs)


def entend(monde, auteur, auditeur, geste="dire", force=None):
    """Le niveau auquel le PNJ ``auditeur`` entend, ici et maintenant, le geste d'``auteur`` (un PNJ
    ou le joueur) ; None s'il ne l'entend pas (sous son seuil, ou trop loin). ``force`` : la nature
    du bruit, comme pour ``retentir``."""
    from .corps import conscient
    if not conscient(monde, auditeur):
        return None
    n = force or nature(geste)
    salle, case = _place(monde, auteur)
    if n is None or salle not in monde.data["salles"] or not monde.objets[auditeur].get("entend", True):
        return None
    parvient = parvenu(propager(monde, salle, case, INTENSITES[n]), *_place(monde, auditeur))
    return parvient[0] if parvient is not None and parvient[0] >= seuil(monde, auditeur) else None


def retentir(monde, auteur, geste, discret=False, bruit=0, texte="", cites=(), parole=None, vers=(), force=None,
             dits=None, appris=False, emission=None):
    """Le geste de ``auteur`` (un PNJ ou le joueur) retentit maintenant, là où il se tient : qui
    l'entend l'interprète ; ce qui parvient au joueur est rangé pour lui. Une ``parole`` ({a :
    ses destinataires, contenu : ce qu'elle transmet, typé}) est retenue par ceux qui en saisissent
    les mots sans en être les destinataires (``social.retenir_parole``). ``vers`` : à qui s'adressent
    des mots qui ne transmettent rien (héler quelqu'un) : l'appelé qui les saisit se tourne vers la
    voix (``entendre``) ; le joueur s'en sert pour relier les voix d'un échange (``ecoute.lier``).
    ``force`` : la nature du bruit, quand elle ne tient pas au geste (le son d'un objet, ``SONS``).
    ``dits`` : les mots prononcés, quand ``texte`` est la parole même et non un récit qui les cite entre
    guillemets (la réplique du joueur). ``appris`` : le joueur, à qui s'adresse ce geste (il reçoit un
    objet, on lui réclame le sien), l'a appris de première main, à la deuxième personne : son ouïe ne le
    lui redit pas. Renvoie ceux qui se sont retournés."""
    from .corps import conscient
    n = force or nature(geste, discret, bruit)
    if n in VOCALES and not conscient(monde, auteur):
        return []
    salle, case = _place(monde, auteur)
    if n is None or salle not in monde.data["salles"]:
        return []
    from .esprits import percoit as percoit_, pnjs
    from .temps import instant
    entrees = propager(monde, salle, case, INTENSITES[n])
    t = instant(monde)
    emission_dite = None
    if texte and (n in VOCALES or dits is not None):
        from .emissions import diffuser
        a = list(parole["a"]) if parole else list(vers)
        auditeurs = auditeurs_parole(monde, auteur, geste, n)
        if geste == "chuchoter":
            auditeurs = [id for id in auditeurs if id in a]
        emission_dite = diffuser(monde, auteur, geste, texte, dits,
                 list(parole["contenu"]) if parole else [], a, auditeurs, emission, cites)
    if auteur != "joueur" and not appris:
        _au_joueur(monde, auteur, salle, case, n, entrees, t, texte, [c for c in cites if c],
                   list(parole["a"]) if parole else list(vers), list(parole["contenu"]) if parole else [],
                   emission_dite["id"] if emission_dite else None)
    retournes, temoins, saisis = [], [], []
    for id in pnjs(monde):
        o = monde.objets[id]
        if id == auteur or not conscient(monde, id) or not o.get("entend", True) or o["lieu"] not in entrees:
            continue
        parvient = parvenu(entrees, *_place(monde, id))
        if parvient is None:
            continue
        if not o.get("profil"):
            # Sans profil, il ne délibère pas : il retient seulement ce qu'il entend sans le voir.
            if n not in HABITUELS and parvient[0] >= seuil(monde, id) and not percoit_(monde, id, auteur):
                _retenir_seulement(monde, id, salle, n, parvient[0])
            continue
        if n in VOCALES and texte and mots_saisis(monde, id, parvient[0]):
            saisis.append(id)
            from .signes import entendre_ton
            entendre_ton(monde, id, auteur, list(parole["a"]) if parole else list(vers))
            if parole is not None and id in parole["a"]:
                from .esprits import reconsiderer
                reconsiderer(monde, id)  # Une parole qui lui est adressée change sa situation.
            elif parole is not None:
                temoins.append(id)
        if parvient[0] >= seuil(monde, id) and entendre(monde, id, auteur, salle, case, n, t, parvient[0],
                                                        vises=vers, par=parvient[1]):
            retournes.append(id)
    if temoins:
        from .social import retenir_parole
        for id in temoins:
            retenir_parole(monde, id, auteur, parole["a"], texte, [c for c in cites if c], parole["contenu"])
    if saisis:
        # Chacun relie les voix de l'échange par la règle du joueur (``voix.lier``) : une voix qu'une
        # autre appelle par son nom, entendue dans le même échange, est « une voix qu'on appelle … ».
        from .voix import lier, parole_saisie, retenir_echange
        a = list(parole["a"]) if parole else list(vers)
        for id in saisis:
            saisie = parole_saisie(monde, id, auteur, t, a, texte, [c for c in cites if c], percoit_(monde, id, auteur),
                                   dits)
            lier(monde, id, saisie, retenir_echange(monde, id, saisie))
    return retournes


# --- Le joueur ----------------------------------------------------------------------------

BRUITS_MAX = 80


def _au_joueur(monde, auteur, salle, case, n, entrees, t, texte, cites, a=(), contenu=(), emission_id=None):
    """Ce qui parvient au joueur : son niveau, d'où il arrive (``par`` : une sortie de sa salle,
    ``None`` tout près, « piece » plus loin dans la pièce). Le même bruit sans paroles, au même
    niveau et d'où il venait déjà, ne se range qu'une fois. Une parole dont il saisit les mots se
    range même s'il voit qui parle (``vu`` : il le voit parler, il connaîtra sa voix ; rien à en
    rendre de plus), avec ses destinataires (``a``) : c'est par elle qu'il relie les voix d'un
    échange et les noms qu'elles se donnent (``ecoute.lier``)."""
    from .corps import conscient
    if not conscient(monde):
        return
    ici, position = _place(monde, "joueur")
    parvient = parvenu(entrees, ici, position)
    if parvient is None:
        return
    vu = monde.visible(auteur)
    mots = n in VOCALES and parvient[0] >= SEUIL
    if mots and texte:
        from .signes import entendre_ton
        entendre_ton(monde, "joueur", auteur, a)
    if vu:
        if mots:
            from .voix import connaitre
            connaitre(monde, "joueur", auteur)  # Il le voit parler : il saura reconnaître sa voix.
        if not (mots and texte):
            return
    if n in HABITUELS and not mots and parvient[0] >= SEUIL - finesse(monde, "joueur"):
        # Même interprétation que les PNJ, avant le rendu et la sauvegarde. Le bruit
        # reste rendu comme tel : cette attribution n'est pas une identité vue.
        crus = _crus_la(monde, "joueur", salle, case if ici == salle else None)
        if crus:
            _attribuer(monde, "joueur", crus, salle, case if ici == salle else None)
    niveau, par = parvient
    if ici == salle:
        par = None if case is None or position is None or distance(case, position) <= PROCHE else "piece"
    entree = {"instant": t, "auteur": auteur, "salle": salle, "nature": n, "niveau": niveau, "par": par,
              "texte": texte, "cites": cites, **({"a": list(a)} if a and mots else {}), **({"vu": True} if vu else {})}
    if emission_id is not None:
        entree["emission"] = emission_id
    bruits = monde.data.setdefault("bruits", [])
    if not texte:
        semblable = next((i for i, b in enumerate(bruits) if not b["texte"] and all(
            b[k] == entree[k] for k in ("auteur", "salle", "nature", "niveau", "par"))), None)
        if semblable is not None:
            del bruits[semblable]
    bruits.append(entree)
    del bruits[:-BRUITS_MAX]
    # Le rendu aux événements peut précéder la fin de l'action du joueur.
    # Admettre la voix dès sa réception, comme les noms de l'échange, pour
    # qu'une voix encore inconnue ait déjà sa référence publique sauvegardable.
    from .ecoute import ENTENDU, retenir
    if niveau >= ENTENDU:
        retenir(monde, [(entree, niveau, par)])
    if mots and texte:
        from .ecoute import lier
        lier(monde, entree, contenu)


# --- Les PNJ ------------------------------------------------------------------------------

def _crus_la(monde, id, salle, case):
    """Présences crues compatibles avec une marche depuis leur dernière localisation.

    Les croyances sont datées à la minute : retenir toute la minute possible,
    sans inventer l'instant de la perception. Ni position ni trajet réels ne
    permettent de corriger cette hypothèse, qui peut être une méprise.
    """
    from .esprits import RECENT, lire
    from .pnj import PAS
    from .temps import MINUTE, PAS_JOUEUR, instant
    minute = monde.data["minutes"]
    crus = []
    for x, attributs in memoire.faits_connus(monde, id).items():
        if x == id or not (x == "joueur" or monde.objets.get(x, {}).get("type") == "personnage"):
            continue
        c = attributs.get("lieu")
        age = minute - c["minute"] if c else -1
        if (not c or c["valeur"] != salle or not 0 <= age <= RECENT
                or attributs.get("etat", {}).get("valeur", {}).get("parti")):
            continue
        # Début de la minute crue : borne supérieure du temps écoulé possible.
        ecoule = instant(monde) - c["minute"] * MINUTE
        allure = PAS_JOUEUR if x == "joueur" else PAS
        if case is not None and c.get("case") and distance(c["case"], case) > PRES_DE + ecoule / allure:
            continue
        crus.append(x)
    return crus


def objet_situe(monde, id, objet, salle, case):
    """Il croit ``objet``, ou ce qui le contient, tout près de la case d'où vient un bruit de
    ``salle`` (à ``PRES_DE`` de la case qu'il lui croit ; sans cases, dans la salle) : ce bruit, il
    sait sur quoi il porte (``pnj._temoins_a_l_oreille``). Un bien fixe qu'il connaît (il en a une
    croyance, ou c'est le sien) est à sa place : on sait où se tient un coffre, une réserve, même
    sans en retenir la case."""
    from .esprits import lire
    croyances = memoire.faits_connus(monde, id)
    vus, x = set(), objet
    while x in monde.objets and x not in vus:
        vus.add(x)
        o = monde.objets[x]
        c = croyances.get(x, {}).get("lieu")
        if not c and not o.get("mobile", True) and (x in croyances or o.get("proprietaire") == id):
            c = {"valeur": o["lieu"]}
        if not c or c["valeur"] is None:
            return False
        if c["valeur"] == salle:
            if case is None:
                return True
            ou = c.get("case")
            if ou is None and not monde.objets[x].get("mobile", True) and monde.objets[x].get("lieu") == salle:
                ou = monde.objets[x].get("position")
            return ou is not None and distance(ou, case) <= PRES_DE
        x = c["valeur"]
    return False


def _cru_le_plus_proche(monde, id, crus, case):
    """La même attribution pour interpréter le bruit, le surveiller et le retenir."""
    from .esprits import lire
    croyances = memoire.faits_connus(monde, id)

    def ecart(x):
        c = croyances[x]["lieu"]
        return (distance(c["case"], case) if case is not None and c.get("case") else 0, x)
    return min(crus, key=ecart)


def _attribuer(monde, id, crus, salle, case):
    """Recaler dans la zone crue ; expliquer un déplacement possible ne le confirme pas."""
    from .esprits import croire, lire
    x = _cru_le_plus_proche(monde, id, crus, case)
    c = memoire.faits_connus(monde, id)[x]["lieu"]
    # Pouvoir avoir marché jusque-là explique le bruit, sans identifier celui
    # qui l'a fait. Cette hypothèse ne doit pas déplacer ni rajeunir la preuve
    # de présence qui l'a rendue possible. La localisation acoustique précise
    # conserve sa tolérance commune ; une voix reconnue est déjà située par voix.
    if case is not None and c.get("case") is not None and distance(c["case"], case) > PRES_DE:
        return
    # Un bruit ne dit pas qui le fait : qui ne le croit là que sur la parole d'une voix inconnue
    # (``se_dit``) ne le croit pas davantage.
    source, confiance = ("se_dit", c["confiance"]) if c["source"] == "se_dit" else ("entendu", 1.0)
    croire(monde, id, x, "lieu", salle, source, confiance, salle=salle,
           case=list(case) if case is not None else c.get("case"), minute=c["minute"],
           origine=c.get("origine") or {"source": c["source"], "minute": c["minute"]},
           mobilite=c.get("mobilite", "mobile"))


def _se_tourner(monde, id, case, t, texte=" se retourne au bruit.", depuis=None):
    """Il se tourne vers le bruit : la rotation retarde la fin de son geste en cours ; ce qu'il
    voit alors devient croyance, et l'auteur d'un geste illicite en cours, un témoignage. ``depuis`` :
    sa case dans le plan commun, quand ``case`` y est donnée (une autre salle)."""
    from .esprits import esprit, percevoir, reconsiderer
    from .francais import designer
    from .pnj import _chroniquer, temoigner_en_cours
    from .spatial import QUART, orientation_vers, quarts
    o = monde.objets[id]
    vers = orientation_vers(tuple(depuis or o["position"]), tuple(case))
    if vers is None:
        return False
    e = esprit(monde, id)
    e["libre"] = max(e["libre"], t) + QUART * quarts(o.get("orientation"), vers)
    o["orientation"] = vers
    percevoir(monde, id)
    reconsiderer(monde, id)  # Le bruit qui l'a fait se retourner change sa situation.
    _chroniquer(monde, id, designer(o, debut=True) + texte, "ouie")
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
               and a["lieu"]["minute"] > minute for x, a in memoire.faits_connus(monde, id).items()
               if x == "joueur" or monde.objets.get(x, {}).get("type") == "personnage")


def source(monde, id, salle):
    """La case d'où venait le plus récent bruit qu'il attend de ``salle`` et qu'il a pu situer
    (il l'a entendu de cette salle même) ; None s'il ne le situe pas plus près que la salle."""
    from .memoire import bruits_retenus
    for s in reversed(bruits_retenus(monde, id, salle)):
        if s.get("case") is not None and not resolu(monde, id, s):
            return tuple(s["case"])
    return None


def parcouru(monde, id, salle, case=None):
    """Il a parcouru ``salle`` des yeux (vers ``case``, la source qu'il est allé voir) : les bruits
    qu'il en avait retenus sont vus ; renvoie vrai s'il en attendait un.

    Allé voir sans rien trouver, ou sans rien pouvoir voir (le noir), il a fait ce qu'il pouvait :
    il retient cet examen (``examen`` : le lieu, la case s'il l'a situé, le plus fort de ce qu'il
    attendait et qui appelait s'il avait reconnu la voix). Le même bruit, ou un moindre, venu du même
    endroit ne l'y renvoie plus tant qu'il continue (``couvert``) ; seul un bruit nouveau le relance :
    plus fort, d'une autre voix, ou qu'il situe mieux. Qui a vu quelqu'un là s'explique le bruit
    (``resolu``) : rien à retenir."""
    from .memoire import retenir_examen_sonore
    return retenir_examen_sonore(monde, id, salle, case)


def couvert(monde, id, salle, n, qui=None, case=None):
    """Le souvenir d'examen (``parcouru``) qui couvre ce bruit : venu du lieu qu'il est allé voir sans
    rien y trouver, pas plus fort que ce qu'il y attendait, d'aucune autre voix, sans qu'il le situe
    mieux (il avait examiné le lieu entier, et l'entend maintenant d'une case : c'est nouveau), dans
    les ``RECENT`` minutes qui suivent l'examen ou le dernier bruit pareil ; None sinon. Dans une
    salle où il n'a rien pu voir, des pas de plus ne lui apprennent rien.
    La consultation renvoie une copie ; elle ne rafraîchit pas l'examen."""
    from .memoire import examen_couvrant
    return examen_couvrant(monde, id, salle, n, qui, case)


def _retenir_seulement(monde, id, salle, n, niveau):
    """Un personnage sans profil ne délibère pas (ni inquiétude, ni aller voir) : il retient le bruit
    inhabituel qu'il a entendu sans le voir, le plus fort par lieu, ce que le MJ lit de lui
    (``esprits.dernier_son``)."""
    from .memoire import retenir_bruit_sans_profil
    retenir_bruit_sans_profil(monde, id, salle, n, niveau)


def _bruit_inconnu(monde, id, salle, n, niveau, qui=None, case=None):
    """Un bruit vers ce lieu, dont il ne sait rien de plus : un souvenir par lieu, qui l'inquiète, avec
    le plus fort niveau qui lui en est parvenu (``deliberation.alarme``), la case d'où il vient quand il
    l'entend de cette salle même (il le situe : aller voir mène à portée de vue de sa source) et, d'un
    appel dont il a reconnu la voix, qui appelait. Un bruit que couvre un examen resté vain (``couvert``)
    ne lui apprend rien : il ne le retient pas ; un appel l'inquiète encore."""
    from .deliberation import inquieter
    from .esprits import reconsiderer
    from .memoire import bruits_retenus, retirer_bruits, retenir_episode, rafraichir_examen_sonore
    from .pnj import _chroniquer
    from .social import _qui
    if rafraichir_examen_sonore(monde, id, salle, n, qui, case):
        if n in ("appel", "cri"):
            inquieter(monde, id, "bruit", max(0, niveau) / INTENSITES["appel"])
        return
    anciens = bruits_retenus(monde, id, salle)
    attente = [s for s in anciens if not resolu(monde, id, s)]
    reconsiderer(monde, id)  # Un bruit vers ce lieu, qu'il ira peut-être voir, et qui l'inquiète.
    retirer_bruits(monde, id, salle)
    # Un bruit qu'il attend déjà de ce lieu ne l'inquiète pas de nouveau ; un appel, si : chaque
    # appel à l'aide en est un nouveau. Il s'inquiète à la mesure de ce qu'il en entend : un appel
    # tout proche, pleinement ; des pas lointains, à peine.
    if not attente or n in ("appel", "cri"):
        inquieter(monde, id, "bruit", max(0, niveau) / INTENSITES["appel"])
    if not attente:
        # Ce bruit nouveau peut être la personne cherchée, sans lui en attribuer l'auteur.
        # Un bruit déjà attendu ou couvert par l'examen ne relance pas la recherche.
        from .deliberation import indice_bruit, indice_recherche
        indice_recherche(monde, id, salle, qui, indice=indice_bruit(
            {"nature": n, "qui": qui, "case": list(case) if case is not None else None}))
        _chroniquer(monde, id, f"{_qui(monde, id)} entend un bruit : {monde.data['salles'][salle]['nom']}.", "ouie")
    # Tant qu'il ne l'a pas vu, il en retient le plus fort, et qui appelait s'il l'a reconnu ; d'où il
    # vient, le dernier endroit d'où il l'a situé.
    qui = qui or next((s["qui"] for s in reversed(attente) if s.get("qui")), None)
    case = list(case) if case is not None else next((s["case"] for s in reversed(attente) if s.get("case")), None)
    retenir_episode(monde, id, {"type": "bruit", "salle": salle,
                               "nature": max([n, *(s["nature"] for s in attente)], key=INTENSITES.get),
                               "niveau": max([niveau, *(s.get("niveau", niveau) for s in attente)]),
                               **({"qui": qui} if qui else {}), **({"case": case} if case else {})})


def entendre(monde, id, auteur, salle, case, n, t, niveau=SEUIL, vises=(), par=None):
    """Un PNJ entend le bruit d'``auteur`` et l'interprète selon ce qu'il croit ; vrai s'il s'est
    retourné. ``vises`` : ceux que l'auteur hèle ; ``par`` : la sortie de sa salle par où le bruit
    lui arrive (None de la sienne).

    Hélé par son nom, il en saisit les mots : il se tourne vers la voix (vers l'appelant s'il le
    verrait ainsi, dans sa salle ou au-delà d'un seuil ; sinon vers le seuil par où elle arrive
    d'ailleurs), le temps de la rotation, et peut ainsi le voir. Qui attend d'être rejoint par
    l'appelant (``appel.attendre``) se tourne vers lui quand il l'entend approcher,
    dès qu'il peut le voir. Un appel ou un cri, sans mots, porte la voix : qui la connaît sait qui
    crie, et le croit là."""
    from .corps import conscient
    if not conscient(monde, id):
        return False
    from .esprits import croire, lire, percoit
    from .voix import PRETENDUE, RECONNUE, connaitre, entendre as entendre_voix, reconnaitre
    o = monde.objets[id]
    if (n in ("appel", "cri") and niveau >= SEUIL
            and (percoit(monde, id, auteur) or reconnaitre(monde, id, auteur)[1] == RECONNUE)):
        from .esprits import memoriser, reconsiderer
        memoriser(monde, id, {"type": "detresse", "qui": auteur})
        reconsiderer(monde, id)
    # Même vu, le cri est une information ; une voix jamais reconnue ne livre aucun nom.
    # Un seul souvenir du bruit par cri (et une seule inquiétude) : la suite ne le retient pas de nouveau.
    retenu = False
    if n == "cri" and niveau >= SEUIL and reconnaitre(monde, id, auteur)[1] == RECONNUE:
        from .deliberation import proteges
        if auteur in proteges(monde, id):
            _bruit_inconnu(monde, id, salle, n, niveau, auteur, case if salle == o["lieu"] else None)
            retenu = True
            from .esprits import memoriser, reconsiderer
            memoriser(monde, id, {"type": "secours", "qui": auteur, "salle": salle,
                                  "case": list(case) if case is not None else None})
            reconsiderer(monde, id)
    ici = salle == o["lieu"] and case is not None and o.get("position") is not None
    mots = n in VOCALES and mots_saisis(monde, id, niveau)
    if percoit(monde, id, auteur):
        if mots:
            connaitre(monde, id, auteur)  # Il le voit parler : il saura reconnaître sa voix.
        return False  # Il le voit faire : l'ouïe n'y ajoute rien d'autre.
    retourne = False
    if mots and n == "hele" and id in vises:
        # Il entend son nom : il se tourne vers la voix, et voit peut-être qui l'appelle.
        retourne = _vers_la_voix(monde, id, auteur, case if ici else None, par, t)
        if percoit(monde, id, auteur):
            connaitre(monde, id, auteur)
            return retourne
    elif (memoire.attente_convenue(monde, id) or {}).get("qui") == auteur and _vers_qui_l_a_hele(monde, id, auteur, t):
        # Il attend qui doit le rejoindre : à son approche, il se tourne vers lui dès qu'il peut le voir.
        if mots:
            connaitre(monde, id, auteur)
        return True
    reconnu = None
    if mots:
        # Il en saisit les mots : une voix connue, il croit son porteur là d'où elle vient ; une voix
        # qui s'était nommée, celui qu'elle a dit être ; une voix inconnue n'est à personne qu'il
        # croie là (``voix.entendre``).
        _, certitude = entendre_voix(monde, id, auteur, salle, list(case) if ici else None)
        if certitude == PRETENDUE:
            return retourne  # Une voix qu'il a déjà entendue se nommer : rien d'inquiétant.
        crus = [auteur] if certitude == RECONNUE else []
    else:
        crus = _crus_la(monde, id, salle, case if ici else None)
        if n in ("appel", "cri") and niveau >= SEUIL and reconnaitre(monde, id, auteur)[1] == RECONNUE:
            # Un cri porte la voix : il sait qui crie, et le croit là d'où vient le cri.
            reconnu = auteur
            croire(monde, id, auteur, "lieu", salle, "entendu", salle=salle,
                   case=list(case) if ici else None)
    # Héler : qui en saisit les mots entend qu'on appelle quelqu'un, sans alarme.
    inhabituel = n not in HABITUELS and not (n == "hele" and mots)
    from .relations import se_mefie, craint
    if crus:
        # Surveiller celui à qui il prête ce bruit ; un autre candidat lointain
        # ne doit pas rendre suspect le geste attribué à son compagnon.
        crus = [_cru_le_plus_proche(monde, id, crus, case if ici else None)]
    mefiance = any(se_mefie(monde, id, x) or craint(monde, id, x) for x in crus)
    if crus and not inhabituel and not mefiance:
        _attribuer(monde, id, crus, salle, case if ici else None)
        # Expliquer le bruit dispense de se retourner, pas de lui prêter
        # attention : cette présence peut offrir une occasion de lui parler.
        # Le choix et l'échange gardent leurs contrôles de présence et d'ouïe.
        from .esprits import reconsiderer
        reconsiderer(monde, id)
        return retourne
    if not retourne and ici and distance(case, o["position"]) <= PROCHE:
        from .spatial import dans_le_regard
        if not dans_le_regard(monde, salle, case, id):
            retourne = _se_tourner(monde, id, case, t) or retourne
            if percoit(monde, id, auteur):
                if mots:
                    connaitre(monde, id, auteur)  # Il s'est tourné et le voit parler.
                return retourne
    if crus and not inhabituel:
        _attribuer(monde, id, crus, salle, case if ici else None)  # Il le surveille, de loin.
        from .esprits import reconsiderer
        reconsiderer(monde, id)
    elif not (mots and n == "hele") and not retenu:
        _bruit_inconnu(monde, id, salle, n, niveau, reconnu, case if ici else None)
    return retourne


def _vers_la_voix(monde, id, auteur, case, par, t):
    """Il se tourne vers la voix qui l'appelle : vers l'appelant s'il le verrait ainsi (dans sa salle,
    ou au-delà d'un seuil ouvert, ``_vers_qui_l_a_hele``) ; sinon vers sa case dans sa salle, ou vers
    le seuil de la sortie par où la voix arrive d'une autre ; rien s'il la regarde déjà (ou sans
    cases). Vrai s'il s'est tourné."""
    from .spatial import _case_interieure, dans_le_regard
    o = monde.objets[id]
    if o.get("position") is None:
        return False
    if _vers_qui_l_a_hele(monde, id, auteur, t, " se tourne vers la voix qui l'appelle."):
        return True
    cible = case
    if cible is None:
        sortie = monde.data["salles"][o["lieu"]]["sorties"].get(par) if par else None
        cible = _case_interieure(monde, o["lieu"], sortie) if sortie else None
    if cible is None or tuple(cible) == tuple(o["position"]) or dans_le_regard(monde, o["lieu"], tuple(cible), id):
        return False
    return _se_tourner(monde, id, cible, t, " se tourne vers la voix qui l'appelle.")


def _vers_qui_l_a_hele(monde, id, auteur, t, texte=None):
    """Il ne voit pas ``auteur`` (qui l'a hélé, ou qu'il attend), mais le verrait en se tournant vers
    lui, dans sa salle ou au-delà d'un seuil (``voix._verrait_en_se_tournant`` : la lumière le montre,
    le noir non) : il se tourne vers lui, le temps de la rotation. Vrai s'il s'est tourné."""
    from .esprits import percoit
    from .spatial import _global
    from .voix import _verrait_en_se_tournant
    o = monde.objets[id]
    if o.get("position") is None or percoit(monde, id, auteur) or not _verrait_en_se_tournant(monde, id, auteur):
        return False
    salle, case = _place(monde, auteur)
    if case is None:
        return False
    salles = monde.data["salles"]
    ici = _global(salles[o["lieu"]], o["position"])
    la = _global(salles[salle], case)
    if texte is None:
        from .social import _qui
        texte = f" se tourne vers {_qui(monde, auteur)}, qui arrive comme convenu."
    return _se_tourner(monde, id, la, t, texte, depuis=ici)
