"""Caractéristiques et valeurs, communes à tous les personnages, joueur compris.

Caractéristiques (1 à 20) : FOR, DEX, INT, PER, CHA, et trois de l'esprit : VOL (la volonté :
tenir face à la persuasion, ne pas céder à un besoin pressant), ELO (l'éloquence : convaincre
par le discours) et PSY (la perspicacité : lire les autres). Le profil d'un PNJ, ou
``joueur["stats"]``, en donne la base ; les états la modulent, réglés par le moteur et les
mêmes pour tous (``corps.malus`` : faim, froid, fatigue qui pressent, volonté brisée). Toute
règle qui emploie une caractéristique lit sa valeur modulée (``caracteristique``).

Valeurs (0 à 100, dans le profil d'un PNJ) : le caractère, stable. Ce sont des poids, pas des
interdits : elles entrent dans les coûts du planificateur et dans les choix sociaux, et la
détresse les use. Seule une valeur à son comble interdit : honnêteté 100, il ne vole ni ne
ment ; douceur 100, il ne blesse ni ne pousse personne. Les anciennes limites tout ou rien (``ne_vole_pas``,
``ne_ment_pas``, ``ne_blesse_pas``) deviennent ces valeurs extrêmes.

Le joueur a des caractéristiques mais pas de valeurs : il décide lui-même de ce qu'il fait.
"""
STATS = ("FOR", "DEX", "INT", "PER", "CHA", "VOL", "ELO", "PSY")
BASE = 10              # une caractéristique que rien ne déclare : la moyenne
VALEURS = ("altruisme", "empathie", "honnetete", "douceur", "ambition", "courage", "loyaute", "fierte")
NEUTRE = 50            # une valeur que rien ne déclare
COMBLE = 100           # une valeur à son comble interdit ce qu'elle réprouve
LIMITES = {"ne_vole_pas": "honnetete", "ne_ment_pas": "honnetete", "ne_blesse_pas": "douceur"}
# Une faute (léser quelqu'un : prendre, ouvrir, manger son bien ; le contraindre : le pousser)
# coûte au plan, en minutes, FAUTE × h / (100 − h) pour la valeur h qu'elle heurte (honnêteté,
# douceur) : 5 à 20, 20 à 50, 80 à 80, 180 à 90. La détresse
# du besoin qu'il sert l'use, jusqu'à USURE à son comble, moins vite pour qui a de la volonté.
# Une faute qui coûte plus que l'ENJEU d'un besoin n'est pas envisagée.
FAUTE = 20
USURE = 0.9
ENJEU = 60


# --- Caractéristiques -------------------------------------------------------------------

def _profil(monde, id):
    return None if id == "joueur" else monde.objets[id].get("profil")


def base(monde, id, stat):
    """La valeur déclarée : profil du PNJ ou fiche du joueur ; la moyenne sans profil."""
    if id == "joueur":
        return monde.joueur["stats"].get(stat, BASE)
    p = _profil(monde, id)
    return p["caracteristiques"].get(stat, BASE) if p else BASE


def caracteristique(monde, id, stat):
    """La valeur modulée par les états : chaque point de malus aux jets en ôte deux."""
    from .corps import malus
    if id != "joueur" and not _profil(monde, id):
        return BASE
    return max(1, base(monde, id, stat) + 2 * malus(monde, stat, id))


def caracteristiques(monde, id):
    return {stat: caracteristique(monde, id, stat) for stat in STATS}


def modificateur(monde, id, stat):
    """Ce que la caractéristique modulée ajoute à un jet de d20."""
    return (caracteristique(monde, id, stat) - 10) // 2


# --- Valeurs ------------------------------------------------------------------------------

def valeur(monde, id, nom):
    p = _profil(monde, id)
    return (p or {}).get("valeurs", {}).get(nom, NEUTRE)


def interdit(monde, id, nom):
    """Une valeur à son comble : honnêteté 100 ne vole ni ne ment, douceur 100 ne blesse ni ne
    pousse."""
    return valeur(monde, id, nom) >= COMBLE


def detresse(monde, id, besoin=None):
    """De 0 au seuil d'urgence à 1 au comble : celle du besoin servi, sinon du plus pressant."""
    from .deliberation import seuils
    from .esprits import lire
    s, v = seuils(monde, id), lire(monde, id)["besoins"]
    noms = [besoin] if besoin in s else list(s)
    return max([min(1.0, max(0.0, (v.get(b, 0) - s[b]) / (100 - s[b]))) for b in noms if s[b] < 100] or [0.0])


def prix_faute(monde, id, besoin=None, nom="honnetete"):
    """Ce que coûte au plan, en minutes, de léser une personne ; None s'il ne l'envisage pas.
    La valeur que la faute heurte : l'honnêteté (prendre, ouvrir, manger le bien d'autrui), la
    douceur (contraindre : pousser)."""
    h = valeur(monde, id, nom)
    if h >= COMBLE:
        return None
    usure = min(1.0, detresse(monde, id, besoin) * BASE / caracteristique(monde, id, "VOL"))
    prix = FAUTE * h / (COMBLE - h) * (1 - USURE * usure)
    return prix if prix <= ENJEU else None


def penchant(monde, id, nom):
    """Ce qu'une valeur ajoute à un jet qui la sollicite : ±1 par dizaine autour de la moyenne."""
    return (valeur(monde, id, nom) - NEUTRE) // 10


# --- Migration et vérification -----------------------------------------------------------

def migrer(profil):
    """Profil d'une ancienne partie ou d'un ancien scénario : les limites deviennent des valeurs
    à leur comble, les caractéristiques nouvelles prennent la moyenne."""
    valeurs = profil.setdefault("valeurs", {})
    for limite in profil.pop("limites", []):
        if limite in LIMITES:
            valeurs[LIMITES[limite]] = COMBLE
    for nom in VALEURS:
        valeurs.setdefault(nom, NEUTRE)
    for stat in STATS:
        profil["caracteristiques"].setdefault(stat, BASE)


def installer(monde):
    from .esprits import pnjs
    stats = monde.joueur.setdefault("stats", {})
    for stat in STATS:
        stats.setdefault(stat, BASE)
    for id in pnjs(monde):
        p = monde.objets[id].get("profil")
        if p:
            migrer(p)


def verifier_valeurs(valeurs):
    assert (isinstance(valeurs, dict) and set(valeurs) == set(VALEURS)
            and all(type(v) is int and 0 <= v <= COMBLE for v in valeurs.values())), "Valeurs de PNJ invalides"


def verifier(monde):
    stats = monde.joueur["stats"]
    assert set(stats) == set(STATS) and all(type(v) is int and 1 <= v <= 20 for v in stats.values()), \
        "Caractéristiques du joueur invalides"
