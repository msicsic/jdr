"""Forcer : frapper une porte, un contenant (ou tout objet) jusqu'à le briser. Une seule règle
pour le joueur (action ``frapper``, alias « forcer » et « défoncer ») et pour les PNJ (geste
``frapper`` du planificateur).

Un coup demande un outil qui fait choc (percussion, levier) ou qui coupe ce qu'il frappe ; il
réussit sur d20 + FOR (modulée par le corps) + ``BONUS_PERCUSSION`` pour un outil de percussion
contre ``DD`` (un 1 échoue toujours, et abîme l'outil) ; réussi, il ôte à la cible la puissance de
l'outil plus le modificateur de FOR s'il est positif. À zéro, la cible est brisée : une porte reste
ouverte et déverrouillée, un contenant s'ouvre et ce qu'il contenait tombe au sol (``briser``). Un
coup est bruyant (``ouie.NATURES``).
"""
from math import ceil

DD = 10
BONUS_PERCUSSION = 2
CHOC = ("percussion", "levier")
COUPE = ("couper", "couper_bois")


def coupe(cible, outil):
    """L'outil coupe-t-il cette cible ? Sa puissance passe son seuil de coupe, ou la qualification
    de la cible le dit (``capacites_objet``)."""
    from .capacites_objet import statut
    if not outil or not set(outil.get("usages", [])) & set(COUPE):
        return False
    if "seuil_coupe" in cible:
        return outil.get("puissance", 0) >= cible["seuil_coupe"]
    return statut(cible, "tranchable", outil) == "etablie"


def choc(outil):
    return bool(outil) and bool(set(outil.get("usages", [])) & set(CHOC))


def adapte(cible, outil):
    """L'outil peut-il entamer la cible : il fait choc, ou il la coupe."""
    return choc(outil) or coupe(cible, outil)


def bonus(outil):
    return BONUS_PERCUSSION if outil and "percussion" in outil.get("usages", []) else 0


def degats(monde, auteur, outil):
    """Ce qu'un coup réussi ôte à la cible : la puissance de l'outil, plus la FOR si elle aide."""
    from .caractere import modificateur
    return (outil.get("puissance", 0) if outil else 0) + max(0, modificateur(monde, auteur, "FOR"))


def chance(monde, auteur, outil):
    """La part des faces du d20 qui font porter un coup (le 1 échoue toujours)."""
    from .caractere import modificateur
    seuil = DD - modificateur(monde, auteur, "FOR") - bonus(outil)
    return sum(1 for d in range(2, 21) if d >= seuil) / 20


def coups(monde, auteur, cible, outil):
    """Combien de coups réussis la briseraient ; None si aucun ne l'entame."""
    d = degats(monde, auteur, outil)
    return None if d <= 0 else ceil(cible["integrite"] / d)


def briser(monde, cible, salle=None):
    """La cible à zéro : une porte brisée reste ouverte et déverrouillée (sa cale tombe dans
    ``salle``) ; un contenant brisé s'ouvre, et ce qu'il contenait tombe au sol, là où il est.
    Renvoie ce qui est tombé."""
    from .deplacement_objet import deplacer
    from .geometrie import position_objet
    o = monde.objets[cible]
    tombes = []
    if o["integrite"] > 0:
        return tombes
    if o["type"] == "porte":
        o["ouverte"], o["verrouillee"] = True, False
        cale = o.get("bloque_par")
        if cale:
            deplacer(monde, cale, salle or monde.joueur["salle"])
            monde.objets[cale].pop("cale_de", None)
            o["bloque_par"] = None
    elif o["type"] == "contenant":
        o["ouverte"], o["verrouillee"] = True, False
        for enfant in monde.enfants(cible):
            deplacer(monde, enfant["id"], o["lieu"], position_objet(monde, o)
                     if o["lieu"] in monde.data["salles"] else None)
            tombes.append(enfant["id"])
    return tombes


def force_crue(monde, auteur, autre):
    """Estimation commune des armes et blessures perçues (coups, et future menace)."""
    from .combat import force_crue as estimer
    return estimer(monde, auteur, autre)
