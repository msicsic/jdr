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


def duree_pas(allure, vecteur):
    """La durée d'un pas d'une case selon son vecteur, pour le joueur comme pour un PNJ : l'allure
    (``PAS_JOUEUR``, ``PAS_CHASSE``, ``PAS_FEUTRE``, ``pnj.PAS``) pour un pas droit ; √2 fois
    l'allure en diagonale, arrondi au dixième de seconde le plus proche (``geometrie.racine`` :
    15 → 21, 30 → 42). Les chemins au plus court en temps (``spatial.trajet``) en prennent leur
    coût."""
    from .geometrie import racine
    dx, dy = vecteur
    return racine(2 * allure * allure) if dx and dy else allure


def duree(plan):
    """Durée d'un plan en dixièmes de seconde : la sienne, sinon ses minutes."""
    return plan.dixiemes if plan.dixiemes is not None else plan.minutes * MINUTE


ATTENTE_MAX = 12 * 60 * MINUTE   # une attente dure au plus douze heures


def lire_duree(texte):
    """Une durée d'attente en secondes, écrite en chiffres (« 30 », « 1.5 », « 1,5 ») : des
    dixièmes, entre un dixième et ``ATTENTE_MAX`` ; None sinon."""
    try:
        dixiemes = round(float(texte.strip().replace(",", ".")) * 10)
    except ValueError:
        return None
    return dixiemes if 0 < dixiemes <= ATTENTE_MAX else None


def dire_duree(dixiemes):
    """« 1,5 seconde », « 30 secondes », « 5 minutes », « 2 minutes 30 secondes », « 1 heure 5 minutes »."""
    heures, reste = divmod(dixiemes, 60 * MINUTE)
    minutes, reste = divmod(reste, MINUTE)
    secondes = reste / 10
    parties = []
    for nombre, unite in ((heures, "heure"), (minutes, "minute")):
        if nombre:
            parties.append(f"{nombre} {unite}" + ("s" if nombre > 1 else ""))
    if secondes or not parties:
        texte = f"{secondes:g}".replace(".", ",")
        parties.append(texte + " seconde" + ("s" if secondes >= 2 else ""))
    return " ".join(parties)


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
    # Les bruits d'avant l'ouïe commune ne disent pas ce qui en parvenait au joueur ; tous passés,
    # ils ne lui parviennent plus.
    if "bruits" in monde.data:
        monde.data["bruits"] = [b for b in monde.data["bruits"] if "auteur" in b]
    # Aucun geste ne s'achève sur une case occupée : qui s'y trouvait déjà s'écarte.
    from .pnj import ecarter
    ecarter(monde)


def verifier(monde):
    d = monde.data.get("dixiemes", 0)
    assert type(d) is int and 0 <= d < MINUTE, "Horloge invalide"
