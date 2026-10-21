"""Eclairage discret : 0 noir, 1 pénombre, 2 assez de lumière pour les détails.

Sans cases, chaque pièce a un niveau et une ouverture transmet la lumière avec une perte
d'un niveau. En mode cases, chaque source éclaire les cases qu'elle voit selon sa portée.
Un contenant fermé opaque bloque une source. Le calcul est pur : observer ne consomme
pas de temps.
"""
from collections import deque

from .francais import designer


def salle_source(monde, source):
    lieu = source["lieu"]
    vus = set()
    while lieu in monde.objets:
        if lieu in vus:
            return None
        vus.add(lieu)
        parent = monde.objets[lieu]
        if parent["type"] == "contenant" and not parent["ouverte"]:
            return None
        lieu = parent["lieu"]
    return monde.joueur["salle"] if lieu == "joueur" else lieu


def allumee(o):
    return bool(o.get("allume")) and o.get("combustible", 0) > 0 and o["integrite"] > 0


def flamme(o):
    """Ce qui allume une autre source : un outil d'allumage intact, ou une source allumée."""
    return ("allumage" in o.get("usages", []) and o.get("integrite", 0) > 0) or ("allume" in o and allumee(o))


def eclairage(monde, salle=None, position=None):
    """Niveau perçu à la position du joueur ; en mode cases, calculé case par case."""
    salle = salle or monde.joueur["salle"]
    if _par_case(monde, salle):
        from .spatial import carte_lumiere
        if position is None and salle == monde.joueur["salle"]:
            position = monde.joueur["position"]
        if position is not None:
            return carte_lumiere(monde, salle).eclairage(salle, position)
        from .geometrie import cases
        carte = carte_lumiere(monde, salle)
        return max((carte.eclairage(salle, p) for p in cases(monde.data["salles"][salle])),
                   key=lambda e: e["niveau"])
    return _eclairage_pieces(monde, salle, _sources(monde) + _jour(monde))


def _resultat(contributions):
    niveau = max((c["niveau"] for c in contributions), default=0)
    return {"niveau": niveau, "etat": ["obscurité", "pénombre", "éclairé"][niveau],
            "contributions": contributions}


def _sources(monde):
    sources = []
    for o in monde.objets.values():
        if allumee(o):
            origine = salle_source(monde, o)
            if origine in monde.data["salles"]:
                sources.append((origine, o["luminosite"], o["id"]))
    return sources


def _jour(monde):
    return [(id, piece["lumiere_naturelle"], "jour") for id, piece in monde.data["salles"].items()
            if piece.get("lumiere_naturelle", 0) > 0]


def _eclairage_pieces(monde, salle, sources):
    """Modèle par pièce : une ouverture transmet la lumière avec une perte d'un niveau."""
    contributions = []
    # Parcours depuis l'observateur : la direction initiale explique d'où entre la lueur.
    file = deque([(salle, 0, "")])
    distances = {salle: 0}
    while file:
        courante, distance, direction_initiale = file.popleft()
        for origine, intensite, id in sources:
            if origine == courante and intensite > distance:
                contributions.append({"source": id if distance == 0 else None,
                                      "niveau": min(2, intensite - distance),
                                      "direction": direction_initiale})
        for direction, sortie in monde.data["salles"][courante]["sorties"].items():
            porte = monde.objets.get(sortie["porte"])
            if porte and not porte["ouverte"]:
                continue
            destination = sortie["vers"]
            if destination not in distances:
                distances[destination] = distance + 1
                file.append((destination, distance + 1, direction_initiale or direction))
    return _resultat(contributions)


# Portée directe d'une source en cases, en distance réelle (``geometrie.distance``) : pleine
# lumière, puis pénombre. Les halos sont ronds.
PORTEES = {1: (2, 4), 2: (4, 8), 3: (6, 12)}
BOUSSOLE = {(0, -1): "nord", (0, 1): "sud", (1, 0): "est", (-1, 0): "ouest",
            (1, -1): "nord-est", (-1, -1): "nord-ouest", (1, 1): "sud-est", (-1, 1): "sud-ouest"}


def _par_case(monde, salle):
    return bool(monde.data.get("mode_cases")) and "plan" in monde.data["salles"][salle]


class CarteLumiere:
    """Lumière case par case des salles reliées à une salle, au même niveau.

    Une source éclaire directement les cases qu'elle voit : murs, portes fermées et
    obstacles opaques projettent de l'ombre. Sa lumière diffuse (reflets, lueur passant
    par une ouverture) suit le modèle par pièce mais ne dépasse pas la pénombre. La
    lumière du jour garde le modèle par pièce.
    """

    def __init__(self, monde, salle, geometrie=None):
        from .spatial import _global, position_cible, vue_geometrique
        from .geometrie import distance
        self._distance = distance
        self.monde = monde
        # Salles reliées, terrain et obstacles : la géométrie de la vue, partagée à lumière près.
        self.geometrie = vue_geometrique(monde, salle) if geometrie is None else geometrie
        self.salles, self.terrain, self.opaques = self.geometrie.salles, self.geometrie.terrain, self.geometrie.opaques
        self.sources = []
        for o in monde.objets.values():
            if not allumee(o):
                continue
            origine = salle_source(monde, o)
            if origine not in self.salles:
                continue
            p = position_cible(monde, o["id"], origine)
            if p is not None:
                self.sources.append((o["id"], origine, _global(monde.data["salles"][origine], p),
                                     PORTEES[max(1, min(3, o["luminosite"]))]))
        self._ambiance, self._cache = {}, {}
        self.alentours = {}   # par case d'origine : ce qu'on y voit tout autour (``spatial._alentour``)
        self.portees = {}     # par case : jusqu'où porte la vue (``spatial._portee``)

    def directes(self, cible):
        """Lumière directe reçue par une case globale, une entrée par source."""
        if cible in self._cache:
            return self._cache[cible]
        ajoute = cible not in self.terrain
        if ajoute:
            self.terrain[cible] = None
        resultat = []
        for id, _, origine, (plein, penombre) in self.sources:
            dx, dy = origine[0] - cible[0], origine[1] - cible[1]
            distance = self._distance(origine, cible)
            niveau = 2 if distance <= plein else 1 if distance <= penombre else 0
            if niveau and (distance == 0 or self.geometrie.ligne(origine, cible)):
                resultat.append({"source": id, "niveau": niveau,
                                 "direction": BOUSSOLE.get(((dx > 0) - (dx < 0), (dy > 0) - (dy < 0)), "")})
        if ajoute:
            del self.terrain[cible]
        self._cache[cible] = resultat
        return resultat

    def ambiance(self, salle):
        """Jour et lumière diffuse des sources, communs à toutes les cases d'une salle."""
        if salle not in self._ambiance:
            resultat = [dict(c, source="jour") for c in
                        _eclairage_pieces(self.monde, salle, _jour(self.monde))["contributions"]]
            for source in _sources(self.monde):
                for c in _eclairage_pieces(self.monde, salle, [source])["contributions"]:
                    resultat.append(dict(c, source=source[2], niveau=1))
            self._ambiance[salle] = resultat
        return self._ambiance[salle]

    def _salles_de(self, cible):
        place = self.terrain.get(cible)
        if place:
            return [place[0]]
        # Un seuil reçoit l'ambiance des cases qui le bordent.
        return list(dict.fromkeys(self.terrain[v][0] for v in (
            (cible[0] + 1, cible[1]), (cible[0] - 1, cible[1]),
            (cible[0], cible[1] + 1), (cible[0], cible[1] - 1)) if self.terrain.get(v)))

    def niveau(self, cible):
        """Niveau à une case globale, seuils compris."""
        contributions = self.directes(cible) + [c for s in self._salles_de(cible) for c in self.ambiance(s)]
        return max((c["niveau"] for c in contributions), default=0)

    def directe(self, cible):
        return bool(self.directes(cible))

    def eclairage(self, salle, position):
        """Une contribution par source ; une source d'une autre pièce est désignée par sa direction."""
        from .spatial import _global
        cible = _global(self.monde.data["salles"][salle], position)
        ambiance, directes = self.ambiance(salle), self.directes(cible)
        par_source = {}
        for c in ambiance + directes:
            par_source.setdefault(c["source"], []).append(c)
        contributions = []
        for id, liste in par_source.items():
            niveau = max(c["niveau"] for c in liste)
            if id == "jour":
                contributions.extend(c for c in liste if c["niveau"] == niveau)
                continue
            meme_piece = salle_source(self.monde, self.monde.objets[id]) == salle
            # La direction de l'ouverture explique mieux d'où entre une lueur voisine.
            diffuses = [c["direction"] for c in liste if c in ambiance]
            direction = "" if meme_piece else (diffuses or [c["direction"] for c in liste])[0]
            contributions.append({"source": id if meme_piece else None, "niveau": niveau,
                                  "direction": direction})
        return _resultat(contributions)


FEU_FAIBLE = 45   # minutes de combustible en deçà desquelles on voit le feu baisser


def faible(o):
    return bool(o.get("allume")) and o.get("combustible", 0) <= FEU_FAIBLE


def combustible(o):
    """Une réserve qui peut recharger une source : une charge par geste, tant qu'il en reste."""
    return "combustible" in o.get("usages", []) and o.get("charges", 0) > 0


# Ce que brûle un foyer dont le contenu n'est pas déclaré : du bois.
FOYER = "bois"


def brule(source):
    """La substance que consomme une source et dont elle se recharge : son contenu déclaré
    (``matiere.SUBSTANCES`` : une lampe brûle de l'huile, une chandelle de la cire) ; à défaut,
    du bois pour un foyer. None : une source sans contenu déclaré est son propre réservoir (une
    torche) et ne se recharge pas."""
    if "allume" not in source:
        return None
    return (source.get("contenu") or {}).get("matiere") or (FOYER if source.get("foyer") else None)


def substance(reserve):
    """Ce que fournit une réserve de combustible : son contenu déclaré (un bidon d'huile), sinon
    la matière dont elle est faite (des bûches de bois)."""
    from .matiere import SUBSTANCES
    matiere = (reserve.get("contenu") or {}).get("matiere") or reserve.get("materiau")
    return matiere if matiere in SUBSTANCES else None


def recharge(source, reserve):
    """Cette réserve de combustible recharge-t-elle cette source ? La même règle pour toutes :
    un consommable recharge ce qui consomme sa substance (un foyer et du bois, une lampe et de
    l'huile)."""
    return "combustible" in reserve.get("usages", []) and brule(source) is not None and substance(reserve) == brule(source)


def alimenter(monde, source, reserve):
    """Une charge de combustible prolonge une source qui le consomme, allumée ou non."""
    f, b = monde.objets[source], monde.objets[reserve]
    if not recharge(f, b) or not combustible(b):
        return False
    b["charges"] -= 1
    from .matiere import retirer_piece
    retirer_piece(b)
    f["combustible"] += b["duree_combustion"]
    return True


def avancer_combustion(monde, minutes, lignes):
    for o in monde.objets.values():
        if not o.get("allume"):
            continue
        perceptible = monde.present_physique(o["id"])
        o["combustible"] = max(0, o["combustible"] - minutes)
        if o["combustible"] == 0 or o["integrite"] == 0:
            o["allume"] = False
            if perceptible:
                lignes.append(designer(o, debut=True) + " s'éteint.")
