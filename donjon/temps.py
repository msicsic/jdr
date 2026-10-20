"""Le temps du monde, à la seconde près.

L'horloge compte des minutes (``data["minutes"]``), où vivent les besoins, les croyances, les
rondes, le feu et les horloges du scénario, et, à l'intérieur de la minute en cours, des
dixièmes de seconde (``data["dixiemes"]``, de 0 à 599) : des entiers, sans erreur d'arrondi.
Un geste a une durée en dixièmes ; le temps qui s'écoule fait passer les minutes entières qu'il
franchit.
"""

MINUTE = 600           # dixièmes de seconde dans une minute
PAS_JOUEUR = 15        # un pas en avant : 1,5 s
PAS_CHASSE = 30        # un pas de côté ou en arrière, sans se tourner : 3 s
PAS_FEUTRE = 30        # un pas feutré, qui ne s'entend que de tout près : 3 s
PAS_ANCIEN = 60        # le pas des parties d'avant le temps fin (6 s), pour les migrer


def duree(plan):
    """Durée d'un plan en dixièmes de seconde : la sienne, sinon ses minutes."""
    return plan.dixiemes if plan.dixiemes is not None else plan.minutes * MINUTE


def instant(monde):
    """L'instant courant, en dixièmes de seconde depuis le début de la partie."""
    return monde.data["minutes"] * MINUTE + monde.data.get("dixiemes", 0)


def ecouler(monde, dixiemes):
    """Fait passer ``dixiemes`` ; renvoie les minutes entières franchies."""
    minutes, monde.data["dixiemes"] = divmod(monde.data.get("dixiemes", 0) + dixiemes, MINUTE)
    monde.data["minutes"] += minutes
    return minutes


def installer(monde):
    """Anciennes parties : le compte des pas dans la minute devient des dixièmes."""
    pas = monde.data.pop("pas_depuis_minute", None)
    if pas is not None and "dixiemes" not in monde.data:
        monde.data["dixiemes"] = pas * PAS_ANCIEN
    monde.data.setdefault("dixiemes", 0)
    # Les bruits d'avant le temps fin étaient datés à la minute : ils le sont à l'instant.
    for b in monde.data.get("bruits", []):
        if "minute" in b:
            b["instant"] = b.pop("minute") * MINUTE
    # Aucun geste ne s'achève sur une case occupée : qui s'y trouvait déjà s'écarte.
    from .pnj import ecarter
    ecarter(monde)


def verifier(monde):
    d = monde.data.get("dixiemes", 0)
    assert type(d) is int and 0 <= d < MINUTE, "Horloge invalide"
