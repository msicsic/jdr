"""Ce qu'un personnage éprouve envers un autre : le seul accès du moteur (``docs/plan-relations.md``).

Une relation est dans l'esprit de chacun, orientée : ce que Gorm éprouve envers Brune n'est pas ce
qu'elle éprouve envers lui. Elle a cinq axes, entiers de 0 à 100 (``AXES``) : la **confiance** (on le
croit, on lui confie, on attend qu'il tienne parole), l'**affection** (son bien compte pour soi, sa
compagnie rassure), la **rancune** (le tort qu'on lui garde), la **peur** (ce qu'il pourrait vous
faire) et la **dette** (ce qu'on lui doit, à ses propres yeux). Sans relation, c'est un **étranger**
(``ETRANGER`` : confiance 40, le reste à 0).

Sous-étape 3a (le socle) : la relation est encore portée par la croyance ``fiable`` de l'esprit
(``croyances[autre][FIABLE]``, vrai ou faux, avec source, minute et certitude), que ce module seul lit
et écrit ; il la traduit en axes (vrai : confiance 70 ; absente : 40 ; faux : 15), et ses prédicats
redonnent exactement les règles d'avant : on se fie à qui l'on croyait fiable (``se_fie``), on se
méfie de qui l'on ne croyait pas fiable (``se_mefie``) ; l'affection, la rancune, la peur et la dette
restent à 0 (``en_veut``, ``craint``, ``doit`` ne disent encore rien). Ce qu'on perçoit de qui parle
passe par l'identification (``percue``) : sa relation si l'on sait que c'est lui, aucune confiance
pour une voix qu'on sait menteuse, celle d'un étranger sinon, même si elle s'est nommée.

Toute variation est une cause nommée, déclarée une fois (``EPREUVES``) : le témoin d'un geste
illicite, le mensonge découvert, la rumeur crue, la part servie… (``eprouver``). En 3a, chaque cause
pose encore la croyance ; en 3b, la table portera ses effets sur chaque axe, modulés par les valeurs,
estompés avec le temps et lus avec hystérésis, sans que les sites d'appel changent.
"""
from .esprits import croire, lire

FIABLE = "fiable"   # l'attribut de croyance qui porte encore la relation (3a) ; aussi le mot de la parole
AXES = ("confiance", "affection", "rancune", "peur", "dette")
ETRANGER = {"confiance": 40, "affection": 0, "rancune": 0, "peur": 0, "dette": 0}
# La croyance ``fiable`` traduite en confiance (3a) : vraie, absente (étranger), fausse.
TRADUCTION = {True: 70, None: ETRANGER["confiance"], False: 15}
MENTEUSE = 0        # la confiance accordée à une voix qu'on sait menteuse (``percue``)
# Les seuils : on se méfie sous MEFIANCE, on fait confiance dès CONFIANCE ; en veut, craint dès
# RANCUNE, PEUR. L'hystérésis (en sortir 10 points plus loin) viendra avec les relations graduées.
MEFIANCE = 30
CONFIANCE = 60
RANCUNE = 40
PEUR = 40

# Chaque cause qui fait varier une relation : ce qu'elle pose en 3a (fiable ou non), et si une
# méfiance que l'on tient de ses propres yeux (vu, essai) tient contre elle, qui ne la remplace pas.
EPREUVES = {
    "vu_agir": (False, False),           # témoin d'un geste illicite ou d'une contrainte (``pnj._temoins``)
    "agir_entendu": (False, True),       # le même geste reconnu à l'oreille (``pnj._temoins_a_l_oreille``)
    "vu_porter": (False, False),         # son bien aux mains d'un autre, sans l'avoir prêté (``esprits._vu_porter``)
    "mensonge_decouvert": (False, False),  # ce qu'on lui a dit, démenti sous ses yeux (``esprits.reviser``)
    "mensonge_dementi": (False, False),  # une parole que ce qu'il a vu dément (``voix.se_mefier``)
    "imposture": (False, False),         # la voix qui s'était dite un autre, enfin reconnue (``voix.connaitre``)
    "rumeur": (False, True),             # une nouvelle crue qui l'accuse (``social._adopter``)
    "aveu": (False, True),               # il avoue un geste illicite (``social.recevoir``)
    "pousse": (False, False),            # bousculé par lui (``passage.subir``)
    "vol_surpris": (False, False),       # le joueur surpris à le voler (``vol.appliquer``)
    "dette_niee": (False, False),        # il refuse de rendre l'argent dû (``biens``)
    "pret_garde": (False, False),        # il garde un prêt échu qu'on lui réclame (``biens``)
    "nourri": (True, False),             # il l'a servi (``echanges.servir``) : il lui sait gré
}
CONSTATS = ("vu", "essai")


def croyance(monde, id, autre):
    """La croyance qui porte la relation d'``id`` envers ``autre`` (3a : ``fiable``), telle quelle
    (valeur, source, minute, certitude), ou None : ce qui en fixe la date et la source."""
    return lire(monde, id)["croyances"].get(autre, {}).get(FIABLE)


def connus(monde, id):
    """Ceux envers qui ``id`` éprouve quelque chose (une relation), dans l'ordre des identifiants."""
    return sorted(x for x, attributs in lire(monde, id)["croyances"].items() if FIABLE in attributs)


def _relation(c):
    r = dict(ETRANGER, confiance=TRADUCTION[None if c is None else c["valeur"]])
    r.update(minute=None if c is None else c["minute"], source=None if c is None else c["source"])
    return r


def envers(monde, id, autre):
    """Ce qu'``id`` éprouve envers ``autre`` : les cinq axes (``AXES``), la minute et la source de son
    dernier changement (None pour un étranger)."""
    return _relation(croyance(monde, id, autre))


def percue(monde, auditeur, locuteur):
    """Ce qu'``auditeur`` éprouve envers qui lui parle, tel qu'il le perçoit : sa relation à
    ``locuteur`` s'il sait que c'est lui (``voix.identifie``) ; envers une voix qu'il sait menteuse,
    aucune confiance ; envers une autre voix inconnue, celle d'un étranger, même si elle s'est nommée."""
    from .voix import SUSPECTE, identifie, reconnaitre
    if identifie(monde, auditeur, locuteur):
        return envers(monde, auditeur, locuteur)
    if reconnaitre(monde, auditeur, locuteur)[1] == SUSPECTE:
        return dict(_relation(None), confiance=MENTEUSE, source="entendu")
    return _relation(None)


def mefiance(relation):
    """Une relation où l'on se méfie (confiance sous ``MEFIANCE``)."""
    return relation["confiance"] < MEFIANCE


def confiance(relation):
    """Une relation où l'on fait confiance (confiance dès ``CONFIANCE``)."""
    return relation["confiance"] >= CONFIANCE


def _confiance(monde, id, autre):
    c = croyance(monde, id, autre)
    return TRADUCTION[None if c is None else c["valeur"]]


def se_mefie(monde, id, autre):
    """``id`` se méfie d'``autre`` (``mefiance``)."""
    return _confiance(monde, id, autre) < MEFIANCE


def se_fie(monde, id, autre):
    """``id`` fait confiance à ``autre`` (``confiance``)."""
    return _confiance(monde, id, autre) >= CONFIANCE


def en_veut(monde, id, autre, seuil=RANCUNE):
    return envers(monde, id, autre)["rancune"] >= seuil


def craint(monde, id, autre, seuil=PEUR):
    return envers(monde, id, autre)["peur"] >= seuil


def doit(monde, id, autre):
    """Ce qu'``id`` croit devoir à ``autre`` (0 à 100)."""
    return envers(monde, id, autre)["dette"]


def fiable(monde, id, autre):
    """Ce qu'``id`` dirait d'``autre`` s'il en parlait (le mot de la parole, ``paroles.ATTRIBUTS``) :
    digne de confiance (True), peu fiable (False), ou rien (None)."""
    r = envers(monde, id, autre)
    return True if confiance(r) else False if mefiance(r) else None


def eprouver(monde, id, autre, cause, source="vu", certitude=1.0):
    """``id`` éprouve ``cause`` (``EPREUVES``) envers ``autre``, qu'il tient de ``source``. Une méfiance
    qu'il tient de ses propres yeux ne devient pas un ouï-dire : une cause qui ne la remplace pas la
    laisse telle quelle."""
    valeur, constat_tient = EPREUVES[cause]
    if constat_tient:
        c = croyance(monde, id, autre)
        if c and c["valeur"] is False and c["source"] in CONSTATS:
            return
    croire(monde, id, autre, FIABLE, valeur, source, certitude)


def avis(monde, id, autre, valeur, source, certitude):
    """Un avis sur une personne qu'on lui a fait croire (« Brune n'est pas fiable », ``echanges.affirmer``) :
    en 3a, il pose la croyance telle quelle ; il deviendra une rumeur pesée par la confiance envers la source."""
    croire(monde, id, autre, FIABLE, valeur, source, certitude)


def valide(c):
    """La forme de la croyance qui porte la relation (``esprits.verifier``)."""
    return type(c.get("valeur")) is bool
