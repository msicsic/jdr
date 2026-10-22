"""Le temps vécu : corps, besoins et sécurité ressentie au temps réellement passé dans chaque état.

Avant, ils étaient échantillonnés à l'instant de la frontière de minute : un PNJ qui traversait un
couloir noir entre deux minutes n'avait pas peur, un autre qui s'y tenait une seconde à la frontière
en subissait une minute entière ; l'effort ou le repos se lisaient du geste en cours, pas des gestes
faits. Désormais chacun (joueur et PNJ qui ont un corps) porte dans ``corps["vecu"]`` l'état où il
se trouve depuis un instant donné : son activité (``effort`` d'un geste qui creuse, ``repos``, ou
rien), le chaud d'un feu, l'eau où il se tient et, pour un PNJ qui ressent sa sécurité, ce qu'elle
gagne ou perd par minute dans ces conditions (``deliberation.ecart_securite`` : le noir, la
compagnie, la méfiance, l'eau, la menace). Le temps passé dans cet état est soldé (``solder``) quand
il change (``noter`` : à chacun de ses gestes, à l'action du joueur) et à chaque frontière de minute
(``minute``, qui relit aussi les conditions). Ces instants ne dépendent pas du découpage des actions
du joueur, et un état inchangé ne solde rien : le même laps, découpé autrement, donne le même monde.

Les conditions se relisent à ses gestes, à chaque éveil (un événement le fait agir) et à chaque
minute : un feu qui s'éteint loin de ses yeux pendant qu'il attend ne compte qu'à la minute.
"""
from .temps import MINUTE

ACTIVITES = (None, "effort", "repos")
CLES = {"depuis", "activite", "chaud", "eau", "securite"}


def conditions(monde, id, activite):
    """Ce qui fait évoluer son corps et ses besoins tant que rien ne change, lu à l'instant."""
    from .corps import au_chaud, dans_l_eau, conscient
    if not conscient(monde, id):
        activite = None
    securite = None
    if id != "joueur":
        from .deliberation import ecart_securite
        securite = ecart_securite(monde, id)
    return {"activite": activite, "chaud": au_chaud(monde, id), "eau": dans_l_eau(monde, id),
            "securite": securite}


def _vecu(monde, id):
    from .corps import corps
    return corps(monde, id).get("vecu")


def solder(monde, id, t, lignes=None):
    """Le temps passé depuis ``depuis`` jusqu'à ``t`` dans l'état noté : le corps, les besoins du
    profil (leur dérive), la sécurité ressentie. Rien avant la première note."""
    from .corps import corps, vivre, vivre_joueur
    v = _vecu(monde, id)
    if v is None or t <= v["depuis"]:
        return
    dixiemes = t - v["depuis"]
    v["depuis"] = t
    effort, repos = v["activite"] == "effort", v["activite"] == "repos"
    if id == "joueur":
        vivre_joueur(monde, dixiemes, effort, repos, v["chaud"], v["eau"], lignes)
        return
    minutes = dixiemes / MINUTE
    from .deliberation import profil, relancer
    from .esprits import esprit
    e = esprit(monde, id)
    for nom, b in (profil(monde, id) or {}).get("besoins", {}).items():
        if nom in e["besoins"]:
            e["besoins"][nom] = round(min(100.0, max(0.0, e["besoins"][nom] + b["derive_heure"] / 60 * minutes)), 3)
    vivre(monde, id, minutes, effort, repos, v["chaud"], v["eau"])
    if v["securite"] is not None:
        relancer(monde, id, "securite", v["securite"] * minutes)
    corps(monde, id)["vecu"] = v


def noter(monde, id, t, activite):
    """À l'instant ``t``, il entre dans un état (son geste, l'action du joueur) : le temps passé
    dans le précédent est soldé s'il change ; un état inchangé continue sans rien solder."""
    from .corps import corps
    nouveau = conditions(monde, id, activite)
    v = _vecu(monde, id)
    if v is not None and all(v[k] == x for k, x in nouveau.items()):
        return
    solder(monde, id, t)
    corps(monde, id)["vecu"] = {"depuis": t if v is None else max(t, v["depuis"]), **nouveau}


def minute(monde, id, t, lignes=None):
    """La frontière de minute : le temps vécu est soldé, puis les conditions relues (un feu éteint,
    l'eau montée, quelqu'un venu) ; son activité reste celle de son geste en cours."""
    from .corps import corps
    v = _vecu(monde, id)
    solder(monde, id, t, lignes)
    corps(monde, id)["vecu"] = {"depuis": t, **conditions(monde, id, v["activite"] if v else None)}


def verifier(v):
    assert v is None or (isinstance(v, dict) and set(v) == CLES and type(v["depuis"]) is int and v["depuis"] >= 0
                         and v["activite"] in ACTIVITES and type(v["chaud"]) is bool and type(v["eau"]) is bool
                         and (v["securite"] is None or isinstance(v["securite"], (int, float)))), \
        "Temps vécu invalide"
