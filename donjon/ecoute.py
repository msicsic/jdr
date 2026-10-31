"""Ce que le joueur entend : pas, gestes, voix, appels, par la règle d'ouïe commune (``ouie``).

Ce qui parvient au joueur d'un geste qu'il ne voit pas faire est rangé, daté à l'instant (dixièmes
de seconde), dans ``data["bruits"]`` : l'auteur, la salle d'origine, la nature, le niveau parvenu et
d'où il arrive. Le joueur entend de lui-même ce qui lui parvient au seuil commun (``ENTENDU``) ; en
écoutant, un cran plus bas, et un de mieux collé à la porte par où le bruit arrive. Une parole n'est
rendue en clair que si elle est nette (au seuil commun), d'une voix qu'il reconnaît
(``voix.reconnaitre``) et ne nomme que ce qu'il connaît ; sinon, nette, il en saisit les mots cités
tels qu'ils sont dits, sans savoir qui parle (« une voix inconnue : « Ici ! » ») ; sinon il entend
« une voix ». Ceux dont il a entendu nettement la voix pendant son dernier geste sont retenus
(``data["entendus"]``) : il peut leur répondre, sous le nom qu'il leur connaît (``voix``).

Les voix d'un échange (``lier``) : une voix qui dit son propre nom se dit ainsi (``voix.se_nommer``) ;
une voix à qui une autre s'adresse en la nommant, et qu'il entend dans le même échange (« Gorm ? »
puis « Ici ! »), est « une voix qu'on appelle Gorm » (``voix.nommer``) : un ouï-dire, jamais une
identité. Une parole qu'il voit dire (``vu``) compte dans l'échange sans être rendue de nouveau.
"""
import re

from .ouie import BRUITS_MAX, INTENSITES, SEUIL, VOCALES

from .voix import ECHANGE

ENTENDU = SEUIL        # niveau perçu sans y prêter l'oreille, et parole nette
ECOUTE = SEUIL - 1     # niveau perçu en écoutant


def appel(monde, id):
    """Un appel à l'aide : il retentit comme tout geste, par l'ouïe commune (``ouie``). Qui connaît
    la voix sait qui appelle ; un protecteur qui reconnaît son protégé accourt (``deliberation.alarme``)."""
    from .ouie import retentir
    from .pnj import _chroniquer
    from .social import _qui
    _chroniquer(monde, id, f"{_qui(monde, id)} appelle à l'aide.", "social")
    retentir(monde, id, "appel")


def _a_la_porte(monde, par):
    """Le joueur se tient collé à la porte de la sortie ``par``."""
    if not monde.data.get("mode_cases"):
        return False
    from .spatial import proche
    sortie = monde.data["salles"][monde.joueur["salle"]]["sorties"].get(par)
    return bool(sortie and sortie.get("porte") in monde.objets and proche(monde, sortie["porte"]))


def portes_contre(monde):
    """Les portes de sa salle auxquelles le joueur est collé : celles qui l'aident à entendre."""
    return [s["porte"] for par, s in monde.data["salles"][monde.joueur["salle"]]["sorties"].items()
            if _a_la_porte(monde, par)]


def entendus(monde, depuis, seuil, *, bruits=None):
    """Bruits survenus après l'instant ``depuis`` (en dixièmes de seconde : le début du geste du
    joueur) qui lui parviennent au moins à ``seuil`` : [(bruit, niveau, d'où il arrive)]. Le monde a
    traité jusqu'à cet instant compris pendant le geste précédent, et ce qu'il a fait entendre l'a
    été alors."""
    from .ouie import finesse
    ecoute, seuil = seuil <= ECOUTE, seuil - finesse(monde, "joueur")
    resultat = []
    for b in monde.data.get("bruits", []) if bruits is None else bruits:
        if b["instant"] <= depuis or b["auteur"] not in monde.objets or b.get("vu"):
            continue
        niveau = b["niveau"] + (1 if ecoute and _a_la_porte(monde, b["par"]) else 0)
        if niveau >= seuil:
            resultat.append((b, niveau, b["par"]))
    return resultat


def rendre_evenement(monde, parvenu, precedent=None):
    """Un son à son instant. Le fond inchangé ne se répète pas : son précédent
    vient de la file sauvegardée des bruits, jamais de la borne d'une action.
    Les paroles restent des événements distincts, même si leurs mots se répètent."""
    b, niveau, direction = parvenu
    if precedent is not None and not b["texte"] and not precedent[0]["texte"]:
        a, ancien_niveau, ancienne_direction = precedent
        if (b["nature"], niveau, direction) == (a["nature"], ancien_niveau, ancienne_direction):
            return []
    return rendre(monde, [parvenu])


def _lieu(direction):
    return {None: "tout près", "piece": "dans la pièce", "nord": "au nord", "sud": "au sud", "est": "à l'est",
            "ouest": "à l'ouest", "haut": "au-dessus", "bas": "en dessous"}.get(direction, "plus loin")


def nette(bruit, niveau):
    """Une parole nette : une voix qui lui parvient au seuil commun."""
    return bruit["nature"] in VOCALES and niveau >= ENTENDU


def eveille(bruit, niveau):
    """Ce qui tire le joueur d'une attente (``Moteur._attendre``) : un appel, un cri, un fracas, ou
    une parole dont il saisit les mots. Des pas, un geste ordinaire, des voix dont les mots lui
    échappent sont le bruit de fond d'un lieu habité."""
    return bruit["nature"] in ("hele", "appel", "cri", "bruyant", "eclat") or bool(nette(bruit, niveau) and MOTS.search(bruit["texte"]))


def reconnue(monde, bruit, niveau):
    """Une parole nette, d'une voix que le joueur reconnaît (``voix.reconnaitre``)."""
    from .voix import RECONNUE, reconnaitre
    return nette(bruit, niveau) and reconnaitre(monde, "joueur", bruit["auteur"])[1] == RECONNUE


BORNE = r"\b"   # une borne de mot
MOTS = re.compile(r"«\s*(.+?)\s*»")


def connus(monde, bruit):
    """Tout ce que la parole nomme, le joueur le connaît (``paroles._connu_du_joueur``)."""
    from .paroles import _connu_du_joueur
    return bool(bruit["texte"]) and all(_connu_du_joueur(monde, x) for x in bruit["cites"] if x != "joueur")


def mots_percus(monde, bruit):
    """Ce que le joueur saisit d'une parole nette, par la règle commune (``voix.mots``) : tout le texte
    d'une voix qu'il voit ou reconnaît et qui ne nomme que ce qu'il connaît ; sinon les mots cités,
    tels qu'ils sont dits."""
    from .voix import mots
    return mots(monde, "joueur", bruit["auteur"], bruit["texte"], bruit["cites"], bool(bruit.get("vu")))


def nomme(monde, bruit, id):
    """Les mots que le joueur saisit de cette parole nomment-ils ``id`` ?"""
    from .voix import nom_dit
    return id in bruit["cites"] and id in monde.objets and nom_dit(monde, id, mots_percus(monde, bruit))


def _saisie(monde, bruit):
    """La parole nette ``bruit`` telle que le joueur la retient pour relier les voix d'un échange
    (``voix.parole_saisie``) : ce qu'en disent les mots qu'il en saisit."""
    from .voix import parole_saisie
    return parole_saisie(monde, "joueur", bruit["auteur"], bruit["instant"],
                         [x for x in bruit.get("a", ()) if x in bruit["cites"]], bruit["texte"], bruit["cites"],
                         bool(bruit.get("vu")))


def lier(monde, bruit, contenu=()):
    """Ce que le joueur apprend des voix d'un échange, à la parole nette ``bruit`` qu'il vient de
    saisir. Une voix qui dit son propre nom se dit ainsi (``voix.se_nommer``). Une voix à qui une
    autre s'adresse en la nommant, qu'il entend dans le même échange, est « une voix qu'on appelle
    … » : la règle commune aux PNJ et au joueur (``voix.lier``). Rien ne le lui apprend d'une voix
    qu'il reconnaît ou voit."""
    from .paroles import contexte_fige
    from .voix import lier as lier_voix, se_nommer
    auteur = bruit["auteur"]
    recents = [b for b in monde.data.get("bruits", []) if b is not bruit and b["texte"] and b["nature"] in VOCALES
               and b["niveau"] >= ENTENDU and 0 <= bruit["instant"] - b["instant"] <= ECHANGE
               and b["auteur"] in monde.objets]
    if any(c.get("type") == "nom" and c.get("sujet") == auteur for c in contenu) and nomme(monde, bruit, auteur):
        se_nommer(monde, "joueur", auteur, auteur)
    with contexte_fige():  # Ce qu'il saisit de chaque parole : des lectures.
        saisie, saisies = _saisie(monde, bruit), [_saisie(monde, b) for b in recents]
    lier_voix(monde, "joueur", saisie, saisies)


def _heler(bruit):
    """Un cri qui porte des mots : un appel, ou la réponse à un appel (``appel.dire``)."""
    return " répondre" if " répond : « " in bruit["texte"] else " appeler"


REPONDRE = 600         # dixièmes de seconde : on répond « juste après » un appel


def appels(monde):
    """Ceux qui attendent une réponse de Corvus, et dont il a saisi le cri : leur dernière parole
    l'a hélé par son nom, lui a demandé ce qu'il veut, ou lui a dit ce qu'ils veulent (``appel``),
    entendue pendant son dernier geste (``data["entendus"]``) ou il y a moins d'une minute
    (``REPONDRE``, aussi de qui il voit). Le plus récent d'abord : il peut leur répondre
    (``appel.dire``)."""
    from .appel import en_attente
    return [id for id, _ in en_attente(monde)]


def rendre(monde, entendus_):
    """Ce que le joueur entend, par direction : un appel, un grand bruit, des voix, des pas, ou une
    parole nette d'une voix qu'il reconnaît, qui ne nomme que ce qu'il connaît."""
    from .paroles import contexte_fige
    with contexte_fige():  # Rendre ce qu'il entend ne fait que lire.
        return _rendre(monde, entendus_)


def _rendre(monde, entendus_):
    from .voix import nom_pour_joueur
    lignes, groupes = [], {}
    for b, niveau, direction in entendus_:
        if "emission" in b:
            from .emissions import lire
            p = next(p for p in lire(monde) if p["id"] == b["emission"])
            b = {**b, "auteur": p["locuteur"], "texte": p["rendu"]}
        mots = MOTS.search(b["texte"]) if nette(b, niveau) else None
        if connus(monde, b) and reconnue(monde, b, niveau):
            texte = f"Tu entends, {_lieu(direction)} : {b['texte']}"
        elif mots:
            # Une voix qu'il ne sait à qui prêter : ses mots, sans le nom de qui parle.
            texte = (f"Tu entends, {_lieu(direction)}, {nom_pour_joueur(monde, b['auteur'])}"
                     + (_heler(b) if b["nature"] == "hele" else "") + f" : « {mots.group(1)} »")
        else:
            texte = None
        if texte:
            if texte not in lignes:
                lignes.append(texte)
        else:
            groupes.setdefault(direction, {}).setdefault(b["nature"], set()).add(b["auteur"])
    for direction, natures in groupes.items():
        parties = []
        if "appel" in natures:
            parties.append("un appel à l'aide")
        if "cri" in natures:
            parties.append("un cri")
        if "hele" in natures:
            parties.append("quelqu'un appeler" if len(natures["hele"]) == 1 else "des appels")
        if "bruyant" in natures:
            parties.append("un grand bruit")
        if "eclat" in natures:
            parties.append("des éclats de voix")
        if "voix" in natures:
            parties.append("une voix" if len(natures["voix"]) == 1 else "des voix")
        if "pas" in natures:
            parties.append("des pas")
        if "geste" in natures and not parties:
            parties.append("des bruits")
        if "feutre" in natures and not parties:
            parties.append("un léger bruit")
        lignes.append("Tu entends " + ", ".join(parties[:-1]) + (" et " if len(parties) > 1 else "")
                      + parties[-1] + " " + _lieu(direction) + ".")
    return lignes


CHAMPS = {"instant", "auteur", "salle", "nature", "niveau", "par", "texte", "cites"}


def verifier(monde):
    bruits = monde.data.get("bruits", [])
    assert isinstance(bruits, list) and len(bruits) <= BRUITS_MAX and all(
        isinstance(b, dict) and CHAMPS <= set(b) <= CHAMPS | {"a", "vu", "emission"}
        and isinstance(b.get("a", []), list) and b.get("vu", True) is True
        and b["nature"] in INTENSITES and b["salle"] in monde.data["salles"] and isinstance(b["auteur"], str)
        and type(b["instant"]) is int and b["instant"] >= 0 and type(b["niveau"]) is int
        and (b["par"] is None or isinstance(b["par"], str)) and isinstance(b["texte"], str)
        and isinstance(b["cites"], list) for b in bruits), "Bruits invalides"
    entendus_ = monde.data.get("entendus", [])
    assert isinstance(entendus_, list) and all(
        id in monde.objets and monde.objets[id]["type"] == "personnage" for id in entendus_), "Bruits entendus invalides"
    from .memoire import verifier_identite_vocale
    verifier_identite_vocale(monde, "joueur")


def retirer_interlocuteur(monde, id):
    """Une voix reste mémorisée, mais son auteur ne peut plus être un interlocuteur."""
    if 'entendus' in monde.data:
        monde.data['entendus'] = [x for x in monde.data['entendus'] if x != id]


def retenir(monde, entendus_):
    """Ceux dont le joueur a entendu nettement la voix pendant son geste (``nette``) : il peut leur
    répondre, même sans les voir (``dialogues.interlocuteurs``). Une voix qu'il reconnaît lui dit
    qui est là ; une voix inconnue, il la retient sans savoir à qui elle est (``voix.retenir``).
    Des pas, un bruit, une voix trop faible ne lui disent rien de plus."""
    from .temps import MINUTE
    from .voix import RECONNUE, reconnaitre, retenir as retenir_voix
    retenus = monde.data.setdefault("entendus", [])
    for b, niveau, _ in entendus_:
        if not nette(b, niveau) or monde.objets.get(b['auteur'], {}).get('type') != 'personnage':
            continue
        if reconnaitre(monde, "joueur", b["auteur"])[1] != RECONNUE:
            # À la minute où il l'a entendue, pas à la fin de son geste : d'un bloc ou par tranches,
            # le même souvenir.
            retenir_voix(monde, "joueur", b["auteur"], b["instant"] // MINUTE)
        if b["auteur"] not in retenus:
            retenus.append(b["auteur"])
