"""Ce que le joueur entend des PNJ : pas, gestes, voix, appels, propagés de salle en salle.

Chaque geste ou parole d'un PNJ laisse un bruit daté à l'instant (dixièmes de seconde) dans
``data["bruits"]``, avec sa salle d'origine et une intensité (pas et gestes 1, voix 2, appel 3).
Il se propage comme les autres sons (``sons.liens`` : une ouverture coûte 1, une porte fermée
2). Le joueur entend de lui-même ce qui lui parvient au niveau 2 ou plus ; en écoutant,
jusqu'au niveau 1, et un cran de mieux collé à une porte. Une parole n'est rendue en clair que
si elle est nette (niveau 2) et ne nomme que ce qu'il connaît ; sinon il entend « des voix ».
Ceux qu'il a entendus pendant son dernier geste sont retenus (``data["entendus"]``).
"""
import heapq

INTENSITES = {"pas": 1, "geste": 1, "voix": 2, "appel": 3}
NATURES = {"deplacement": "pas", "geste": "geste"}     # nature de chronique -> bruit
ENTENDU = 2            # niveau perçu sans y prêter l'oreille
ECOUTE = 1             # niveau perçu en écoutant
BRUITS_MAX = 80


def bruit(monde, id, nature, texte="", cites=()):
    """Un PNJ fait du bruit là où il se tient."""
    salle = monde.objets[id]["lieu"]
    if salle not in monde.data["salles"]:
        return
    from .temps import instant
    bruits = monde.data.setdefault("bruits", [])
    bruits.append({"instant": instant(monde), "pnj": id, "salle": salle, "nature": nature,
                   "intensite": INTENSITES[nature], "texte": texte, "cites": [c for c in cites if c]})
    del bruits[:-BRUITS_MAX]


def appel(monde, id):
    """Un appel à l'aide : le joueur l'entend comme les autres bruits ; les PNJ à portée
    l'entendent aussi, et un protecteur accourt (``pnj.reagir``)."""
    from .esprits import entendre, pnjs
    from .pnj import _chroniquer
    from .social import _qui
    from .sons import portee
    salle = monde.objets[id]["lieu"]
    _chroniquer(monde, id, f"{_qui(monde, id)} appelle à l'aide.", "social")
    bruit(monde, id, "appel")
    niveaux = portee(monde, salle, INTENSITES["appel"])
    evenement = {"minute": monde.data["minutes"], "origine": salle, "nature": "appel",
                 "intensite": INTENSITES["appel"], "auteur": id}
    for autre in pnjs(monde):
        o = monde.objets[autre]
        if autre != id and o["lieu"] in niveaux and o.get("entend", True):
            entendre(monde, autre, evenement, niveaux[o["lieu"]])


def _chemins(monde):
    """Coût du son depuis la salle du joueur vers chaque salle, et la sortie par où il arrive."""
    from .sons import liens
    graphe, depart = liens(monde), monde.joueur["salle"]
    sorties = {s["vers"]: d for d, s in monde.data["salles"][depart]["sorties"].items()}
    couts, par, file = {depart: 0}, {depart: None}, [(0, depart)]
    while file:
        cout, lieu = heapq.heappop(file)
        if cout != couts[lieu]:
            continue
        for destination, perte in graphe[lieu]:
            if cout + perte < couts.get(destination, 99):
                couts[destination] = cout + perte
                par[destination] = sorties.get(destination) if lieu == depart else par[lieu]
                heapq.heappush(file, (cout + perte, destination))
    return couts, par


def au_contact_d_une_porte(monde):
    if not monde.data.get("mode_cases"):
        return False
    from .spatial import proche
    salle = monde.data["salles"][monde.joueur["salle"]]
    return any(s.get("porte") in monde.objets and proche(monde, s["porte"]) for s in salle["sorties"].values())


def entendus(monde, depuis, seuil):
    """Bruits survenus après l'instant ``depuis`` (en dixièmes de seconde : le début du geste du
    joueur) qui lui parviennent au moins à ``seuil``, hors de ce qu'il voit déjà :
    [(bruit, niveau, direction)]. Le monde a traité jusqu'à cet instant compris pendant le geste
    précédent, et ce qu'il a fait entendre l'a été alors."""
    couts, par = _chemins(monde)
    bonus = 1 if seuil == ECOUTE and au_contact_d_une_porte(monde) else 0
    resultat = []
    for b in monde.data.get("bruits", []):
        if b["instant"] <= depuis or b["salle"] not in couts or b["pnj"] not in monde.objets:
            continue
        if b["salle"] == monde.joueur["salle"] and monde.visible(b["pnj"]):
            continue  # Il le voit faire : les lignes du geste le disent déjà.
        niveau = b["intensite"] - couts[b["salle"]] + (bonus if b["salle"] != monde.joueur["salle"] else 0)
        if niveau >= seuil:
            resultat.append((b, niveau, par[b["salle"]]))
    return resultat


def _lieu(direction):
    return {None: "tout près", "nord": "au nord", "sud": "au sud", "est": "à l'est",
            "ouest": "à l'ouest"}.get(direction, "plus loin")


def rendre(monde, entendus_):
    """Ce que le joueur entend, par direction : des pas, des bruits, des voix, ou une parole nette."""
    from .paroles import _connu_du_joueur
    lignes, groupes = [], {}
    for b, niveau, direction in entendus_:
        nette = (b["nature"] == "voix" and niveau >= ENTENDU and b["texte"]
                 and all(_connu_du_joueur(monde, x) for x in [b["pnj"], *b["cites"]] if x != "joueur"))
        if nette:
            texte = f"Tu entends, {_lieu(direction)} : {b['texte']}"
            if texte not in lignes:
                lignes.append(texte)
        else:
            groupes.setdefault(direction, {}).setdefault(b["nature"], set()).add(b["pnj"])
    for direction, natures in groupes.items():
        parties = []
        if "appel" in natures:
            parties.append("un appel à l'aide")
        if "voix" in natures:
            parties.append("une voix" if len(natures["voix"]) == 1 else "des voix")
        if "pas" in natures:
            parties.append("des pas")
        if "geste" in natures and not parties:
            parties.append("des bruits")
        if parties:
            lignes.append("Tu entends " + ", ".join(parties[:-1]) + (" et " if len(parties) > 1 else "")
                          + parties[-1] + " " + _lieu(direction) + ".")
    return lignes


def verifier(monde):
    bruits = monde.data.get("bruits", [])
    assert isinstance(bruits, list) and len(bruits) <= BRUITS_MAX and all(
        isinstance(b, dict) and b.get("nature") in INTENSITES and b.get("salle") in monde.data["salles"]
        and type(b.get("instant")) is int and b["instant"] >= 0 and isinstance(b.get("cites"), list)
        for b in bruits), "Bruits invalides"
    entendus_ = monde.data.get("entendus", [])
    assert isinstance(entendus_, list) and all(
        id in monde.objets and monde.objets[id]["type"] == "personnage" for id in entendus_), "Bruits entendus invalides"


def retenir(monde, entendus_):
    """Ceux dont un bruit est parvenu au joueur pendant son geste : il les sait là, même sans les
    voir (``dialogues.interlocuteurs``)."""
    retenus = monde.data.setdefault("entendus", [])
    retenus.extend(sorted({b["pnj"] for b, _, _ in entendus_} - set(retenus)))
