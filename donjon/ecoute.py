"""Ce que le joueur entend : pas, gestes, voix, appels, par la règle d'ouïe commune (``ouie``).

Ce qui parvient au joueur d'un geste qu'il ne voit pas faire est rangé, daté à l'instant (dixièmes
de seconde), dans ``data["bruits"]`` : l'auteur, la salle d'origine, la nature, le niveau parvenu et
d'où il arrive. Le joueur entend de lui-même ce qui lui parvient au seuil commun (``ENTENDU``) ; en
écoutant, un cran plus bas, et un de mieux collé à la porte par où le bruit arrive. Une parole n'est
rendue en clair que si elle est nette (au seuil commun), d'une voix qu'il reconnaît
(``voix.reconnaitre``) et ne nomme que ce qu'il connaît ; d'une voix inconnue, il en saisit les mots
cités sans savoir qui parle (« une voix inconnue : « Ici ! » ») ; sinon il entend « une voix ».
Ceux dont il a entendu nettement la voix pendant son dernier geste sont retenus
(``data["entendus"]``) : il peut leur répondre, sous le nom qu'il leur connaît (``voix``).
"""
import re

from .ouie import BRUITS_MAX, INTENSITES, SEUIL, VOCALES

ENTENDU = SEUIL        # niveau perçu sans y prêter l'oreille, et parole nette
ECOUTE = SEUIL - 1     # niveau perçu en écoutant


def appel(monde, id):
    """Un appel à l'aide : il retentit comme tout geste ; les PNJ à portée l'entendent aussi comme un
    son (``esprits.entendre``), et un protecteur accourt (``pnj.reagir``)."""
    from .esprits import entendre, pnjs
    from .ouie import retentir
    from .pnj import _chroniquer
    from .social import _qui
    from .sons import VOIX, portee
    salle = monde.objets[id]["lieu"]
    _chroniquer(monde, id, f"{_qui(monde, id)} appelle à l'aide.", "social")
    retentir(monde, id, "appel")
    intensite = VOIX["appel"][2]
    niveaux = portee(monde, salle, intensite)
    evenement = {"minute": monde.data["minutes"], "origine": salle, "nature": "appel",
                 "intensite": intensite, "auteur": id}
    for autre in pnjs(monde):
        o = monde.objets[autre]
        if autre != id and o["lieu"] in niveaux and o.get("entend", True):
            entendre(monde, autre, evenement, niveaux[o["lieu"]])


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


def entendus(monde, depuis, seuil):
    """Bruits survenus après l'instant ``depuis`` (en dixièmes de seconde : le début du geste du
    joueur) qui lui parviennent au moins à ``seuil`` : [(bruit, niveau, d'où il arrive)]. Le monde a
    traité jusqu'à cet instant compris pendant le geste précédent, et ce qu'il a fait entendre l'a
    été alors."""
    from .ouie import finesse
    ecoute, seuil = seuil <= ECOUTE, seuil - finesse(monde, "joueur")
    resultat = []
    for b in monde.data.get("bruits", []):
        if b["instant"] <= depuis or b["auteur"] not in monde.objets:
            continue
        niveau = b["niveau"] + (1 if ecoute and _a_la_porte(monde, b["par"]) else 0)
        if niveau >= seuil:
            resultat.append((b, niveau, b["par"]))
    return resultat


def _lieu(direction):
    return {None: "tout près", "piece": "dans la pièce", "nord": "au nord", "sud": "au sud", "est": "à l'est",
            "ouest": "à l'ouest", "haut": "au-dessus", "bas": "en dessous"}.get(direction, "plus loin")


def nette(bruit, niveau):
    """Une parole nette : une voix qui lui parvient au seuil commun."""
    return bruit["nature"] in VOCALES and niveau >= ENTENDU


def reconnue(monde, bruit, niveau):
    """Une parole nette, d'une voix que le joueur reconnaît (``voix.reconnaitre``)."""
    from .voix import RECONNUE, reconnaitre
    return nette(bruit, niveau) and reconnaitre(monde, "joueur", bruit["auteur"])[1] == RECONNUE


MOTS = re.compile(r"«\s*(.+?)\s*»")


def _heler(bruit):
    """Un cri qui porte des mots : un appel, ou la réponse à un appel (``pnj.repondre``)."""
    return " répondre" if " répond : « " in bruit["texte"] else " appeler"


def rendre(monde, entendus_):
    """Ce que le joueur entend, par direction : un appel, un grand bruit, des voix, des pas, ou une
    parole nette d'une voix qu'il reconnaît, qui ne nomme que ce qu'il connaît."""
    from .paroles import _connu_du_joueur
    from .voix import nom_pour_joueur
    lignes, groupes = [], {}
    for b, niveau, direction in entendus_:
        connus = b["texte"] and all(_connu_du_joueur(monde, x) for x in b["cites"] if x != "joueur")
        mots = MOTS.search(b["texte"]) if connus and nette(b, niveau) else None
        if connus and reconnue(monde, b, niveau):
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
        if "hele" in natures:
            parties.append("quelqu'un appeler" if len(natures["hele"]) == 1 else "des appels")
        if "bruyant" in natures:
            parties.append("un grand bruit")
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


def verifier(monde):
    bruits = monde.data.get("bruits", [])
    assert isinstance(bruits, list) and len(bruits) <= BRUITS_MAX and all(
        isinstance(b, dict) and set(b) == {"instant", "auteur", "salle", "nature", "niveau", "par", "texte", "cites"}
        and b["nature"] in INTENSITES and b["salle"] in monde.data["salles"] and isinstance(b["auteur"], str)
        and type(b["instant"]) is int and b["instant"] >= 0 and type(b["niveau"]) is int
        and (b["par"] is None or isinstance(b["par"], str)) and isinstance(b["texte"], str)
        and isinstance(b["cites"], list) for b in bruits), "Bruits invalides"
    entendus_ = monde.data.get("entendus", [])
    assert isinstance(entendus_, list) and all(
        id in monde.objets and monde.objets[id]["type"] == "personnage" for id in entendus_), "Bruits entendus invalides"
    voix = monde.data.get("voix_connues", [])
    assert isinstance(voix, list) and len(set(voix)) == len(voix) and all(
        isinstance(id, str) for id in voix), "Voix connues invalides"
    from .voix import verifier_entrees
    verifier_entrees(monde.data.get("voix_entendues", {}))


def retenir(monde, entendus_):
    """Ceux dont le joueur a entendu nettement la voix pendant son geste (``nette``) : il peut leur
    répondre, même sans les voir (``dialogues.interlocuteurs``). Une voix qu'il reconnaît lui dit
    qui est là ; une voix inconnue, il la retient sans savoir à qui elle est (``voix.retenir``).
    Des pas, un bruit, une voix trop faible ne lui disent rien de plus."""
    from .voix import RECONNUE, reconnaitre, retenir as retenir_voix
    retenus = monde.data.setdefault("entendus", [])
    for b, niveau, _ in entendus_:
        if not nette(b, niveau) or b["auteur"] not in monde.objets:
            continue
        if reconnaitre(monde, "joueur", b["auteur"])[1] != RECONNUE:
            retenir_voix(monde, "joueur", b["auteur"])
        if b["auteur"] not in retenus:
            retenus.append(b["auteur"])
