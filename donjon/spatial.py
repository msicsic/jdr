"""Moteur spatial déterministe en cases, indépendant du récit et de l'interface.

Les coordonnées d'objet sont locales à une salle. Les coordonnées de sortie
restent celles du plan (une case hors du sol) ; franchir une sortie prend un pas
et place le personnage sur la case intérieure de la salle voisine.
"""
from __future__ import annotations

from collections import deque
import heapq
from contextlib import contextmanager
import threading

from .geometrie import cases, distance, position_entree, position_objet, placer


VECTEURS = {
    "nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0),
    "nord-est": (1, -1), "nord-ouest": (-1, -1),
    "sud-est": (1, 1), "sud-ouest": (-1, 1),
    "ne": (1, -1), "no": (-1, -1), "se": (1, 1), "so": (-1, 1),
}


def active(m):
    return bool(m.data.get("mode_cases", False))


QUART = 5             # dixièmes de seconde pour tourner de 45° (un demi-tour : 2 s)


def orientation_vers(depart, arrivee):
    """La direction (parmi les huit) qui regarde le mieux d'une case vers une autre ; None si
    c'est la même case."""
    import math
    dx, dy = arrivee[0] - depart[0], arrivee[1] - depart[1]
    if dx == dy == 0:
        return None
    angle = round(math.atan2(dy, dx) / (math.pi / 4)) % 8
    vecteur = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)][angle]
    return next(nom for nom, v in VECTEURS.items() if v == vecteur)


def quarts(de, vers):
    """Nombre de huitièmes de tour (0 à 4) pour passer d'une orientation à une autre."""
    if de is None or vers is None:
        return 0
    ordre = ["est", "sud-est", "sud", "sud-ouest", "ouest", "nord-ouest", "nord", "nord-est"]
    ecart = abs(ordre.index(de) - ordre.index(vers)) % 8
    return min(ecart, 8 - ecart)


def dans_le_cone(origine, orientation, cible):
    """Une case est vue si elle est dans le cône de 120° devant soi, ou immédiatement sur les
    côtés ; derrière, rien. Sans orientation, on voit tout autour."""
    if orientation is None:
        return True
    dx, dy = cible[0] - origine[0], cible[1] - origine[1]
    if dx == dy == 0:
        return True
    fx, fy = VECTEURS[orientation]
    produit = dx * fx + dy * fy
    if max(abs(dx), abs(dy)) == 1 and produit >= 0:
        return True
    return produit * 2 >= ((dx * dx + dy * dy) * (fx * fx + fy * fy)) ** 0.5


def orientation_acteur(m, acteur="joueur"):
    """L'orientation du joueur ou d'un PNJ ; sans orientation, on voit tout autour de soi."""
    if acteur == "joueur":
        return m.joueur.get("orientation")
    return m.objets[acteur].get("orientation")


def regard_initial(m, salle, position):
    """Sans orientation connue, on fait face au centre de la salle."""
    sol = cases(m.data["salles"][salle])
    centre = (round(sum(x for x, _ in sol) / len(sol)), round(sum(y for _, y in sol) / len(sol)))
    return orientation_vers(tuple(position), centre) or "sud"


def _erreur(texte):
    from .monde import ErreurMonde
    raise ErreurMonde(texte)


def installer(m):
    """Active le mode et ajoute des positions manquantes sans écraser l'état."""
    migration_ancienne_partie = (not active(m) and "exploration" not in m.data
                                and bool(m.data.get("journal")))
    m.data["mode_cases"] = True
    memoire = m.data.setdefault("exploration", {})
    for id_salle in m.data["salles"]:
        memoire.setdefault(id_salle, [])
    if migration_ancienne_partie:
        for salle in m.data.get("visitees", []):
            if salle in m.data["salles"] and "plan" in m.data["salles"][salle]:
                memoire[salle] = [list(p) for p in sorted(cases(m.data["salles"][salle]))]
    for salle, piece in m.data["salles"].items():
        if "plan" not in piece:
            continue
        for sortie in piece.get("sorties", {}).values():
            sortie.setdefault("case", [])
    for o in m.objets.values():
        if o.get("type") == "porte":
            positions = o.setdefault("positions_salles", {})
            for salle in o.get("relie", []):
                piece = m.data["salles"].get(salle, {})
                sortie = next((s for s in piece.get("sorties", {}).values()
                               if s.get("porte") == o["id"]), None)
                if sortie:
                    pos = _case_interieure(m, salle, sortie)
                    if pos is not None:
                        positions.setdefault(salle, list(pos))
        if o.get("appui_vertical"):
            a = o["appui_vertical"]
            for cle, salle_cle in (("position_bas", "bas"), ("position_haut", "haut")):
                salle = a.get(salle_cle)
                if salle in m.data["salles"] and "plan" in m.data["salles"][salle]:
                    if tuple(a.get(cle, ())) not in cases(m.data["salles"][salle]):
                        a[cle] = list(position_entree(m, salle))
        salle = o.get("lieu")
        if (salle in m.data["salles"] and "plan" in m.data["salles"][salle]
                and o.get("type") not in ("surface", "porte")
                and (o.get("bloque_passage") or o.get("bloque_vue"))):
            placer(o, salle, position_objet(m, o))
    for o in m.objets.values():
        if (o.get("type") == "personnage" and "orientation" not in o and o.get("lieu") in m.data["salles"]
                and "plan" in m.data["salles"][o["lieu"]] and "position" in o):
            o["orientation"] = regard_initial(m, o["lieu"], o["position"])
    j = m.joueur
    if "orientation" not in j and "plan" in m.data["salles"].get(j["salle"], {}) and j.get("position"):
        j["orientation"] = regard_initial(m, j["salle"], j["position"])
    verifier(m)
    memoriser(m)


def _case_interieure(m, salle, sortie):
    direction = next((d for d, s in m.data["salles"][salle].get("sorties", {}).items()
                      if s is sortie), None)
    if direction not in VECTEURS or len(sortie.get("case", ())) != 2:
        return None
    dx, dy = VECTEURS[direction]
    x, y = sortie["case"]
    pos = (x - dx, y - dy)
    return pos if pos in cases(m.data["salles"][salle]) else None


def _salle_position(m, id, trace=None, salle_vue=None):
    """Résout une position réelle de façon bornée (contenants compris)."""
    salle_vue = salle_vue or m.joueur["salle"]
    trace = set() if trace is None else trace
    if id in trace or id not in m.objets:
        return None
    trace.add(id)
    o = m.objets[id]
    if o.get("incorpore"):
        return None
    if o.get("cote") and o.get("attache") and o["cote"] != salle_vue:
        return None
    if o.get("type") == "porte":
        p = o.get("positions_salles", {}).get(salle_vue)
        return (salle_vue, tuple(p)) if p is not None else None
    a = o.get("appui_vertical")
    if a:
        salle = salle_vue
        cle = "position_bas" if salle == a.get("bas") else "position_haut"
        p = a.get(cle)
        if salle in (a.get("bas"), a.get("haut")) and p is not None:
            return salle, tuple(p)
        return None
    inst = o.get("installation")
    if inst:
        support = m.objets.get(inst.get("support"), {})
        a = support.get("appui_vertical", {})
        salle = salle_vue
        if salle == a.get("bas"):
            return salle, tuple(o.get("position", a.get("position_bas", ())))
        if salle == a.get("haut"):
            return salle, tuple(a.get("position_haut", ()))
        return None
    lieu = o.get("lieu")
    if lieu == "joueur":
        return (salle_vue, tuple(m.joueur.get("position", ()))) if salle_vue == m.joueur["salle"] else None
    if lieu in m.data["salles"]:
        if lieu != salle_vue:
            return None
        if (o.get("type") == "surface" and o.get("nom", "").strip().lower() in ("sol", "plafond")
                and not (o.get("position_salle") == lieu
                         and tuple(o.get("position", ())) in cases(m.data["salles"][lieu]))):
            return lieu, tuple(m.joueur.get("position", ()))
        p = position_objet(m, o)
        return (lieu, tuple(p)) if p is not None else None
    if (o.get("position_autonome") and lieu == o.get("ancrage_initial")
            and lieu in m.objets
            and not m.objets[lieu]["mobile"]
            and o.get("position_salle") == salle_vue
            and tuple(o.get("position", ())) in cases(m.data["salles"][salle_vue])):
        return salle_vue, tuple(o["position"])
    parent = _salle_position(m, lieu, trace, salle_vue)
    if parent and parent[0] == salle_vue:
        conteneur = m.objets.get(lieu, {})
        if conteneur.get("type") == "contenant" and not conteneur.get("ouverte"):
            return None
        return parent
    return None


def position_cible(m, id, salle=None):
    """Position locale visible par la mécanique, sans fournir d'état distant."""
    if id not in m.objets:
        return None
    salle = salle or m.joueur["salle"]
    resultat = _salle_position(m, id, salle_vue=salle)
    return resultat[1] if resultat else None


def position_carte(m, id, salle=None):
    """Case dessinée ; la portée garde la case de contact de position_cible."""
    salle = salle or m.joueur["salle"]
    contact = position_cible(m, id, salle)
    if contact is None:
        return None
    o = m.objets[id]
    if o.get("ancrage_carte") and o.get("position_salle") == salle:
        return tuple(o["ancrage_carte"])
    return contact


def _bloquantes(m, salle, vue=False, sauf=None):
    """Les cases des objets de la salle qui bloquent le passage (ou la vue), hors ``sauf``."""
    return [position_cible(m, id, salle) for id, o in m.objets.items()
            if id != sauf and not o.get("incorpore") and o.get("lieu") == salle
            and (o.get("bloque_vue") if vue else o.get("bloque_passage"))]


def _bloque(m, salle, position, vue=False, sauf=None):
    return any(p == position for p in _bloquantes(m, salle, vue, sauf))


def _case_libre(m, salle, position):
    return position in cases(m.data["salles"][salle]) and not _bloque(m, salle, position)


def porte_par(m, id, acteur):
    """Vrai si l'objet est porté par l'acteur, directement ou dans un contenant porté."""
    vus = set()
    while id in m.objets and id not in vus:
        vus.add(id)
        id = m.objets[id]["lieu"]
        if id == acteur:
            return True
    return False


def position_acteur(m, acteur="joueur"):
    """Salle et case d'où un acteur, le joueur ou un PNJ, perçoit et agit."""
    if acteur == "joueur":
        return m.joueur["salle"], tuple(m.joueur["position"])
    salle = m.objets[acteur]["lieu"]
    return salle, position_cible(m, acteur, salle)


def proche(m, id, acteur="joueur"):
    if id not in m.objets:
        return False
    if porte_par(m, id, acteur) or (acteur == "joueur" and m.est_porte(id)):
        return True
    salle, origine = position_acteur(m, acteur)
    cible = position_cible(m, id, salle)
    if cible is None or origine is None:
        return False
    x, y = origine
    dx, dy = cible[0] - x, cible[1] - y
    if max(abs(dx), abs(dy)) > 1:
        return False
    if not (dx and dy):
        return True
    # Une diagonale ne passe pas en biais entre deux murs ou obstacles solides.
    return (_case_libre(m, salle, (x + dx, y))
            or _case_libre(m, salle, (x, y + dy)))


def _ligne(a, b):
    """Bresenham inclusif, sans dépendance et stable aux égalités."""
    x0, y0 = a
    x1, y1 = b
    dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
    dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
    err = dx + dy
    points = []
    while True:
        points.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return points
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _los(m, salle, origine, cible, cible_id=None):
    plan_cases = cases(m.data["salles"][salle])
    points = _ligne(origine, cible)
    for i, p in enumerate(points[1:], 1):
        if p not in plan_cases:
            return False
        # Les obstacles opaques cachent ce qui se trouve derrière eux.
        if i < len(points) - 1 and _bloque(m, salle, p, vue=True, sauf=cible_id):
            return False
        # Diagonale entre deux cases opaques : règle de coin coupé.
        avant = points[i - 1]
        if p[0] != avant[0] and p[1] != avant[1]:
            c1, c2 = (p[0], avant[1]), (avant[0], p[1])
            if ((c1 not in plan_cases or _bloque(m, salle, c1, vue=True))
                    and (c2 not in plan_cases or _bloque(m, salle, c2, vue=True))):
                return False
    return True


def _meme_niveau(m, a, b):
    """Même étage du plan : on s'y voit par une ouverture. Une différence d'altitude du sol
    (quelques marches, une pente) n'en fait pas un autre étage ; un escalier y mène (la vue ne
    le suit pas, ``_salles_relies``)."""
    return _etage(m, a) == _etage(m, b)


def _etage(m, salle):
    return m.data["salles"][salle].get("niveau") or 0


def altitude(m, salle):
    """Hauteur du sol en cm : déclarée, sinon celle de son étage."""
    piece = m.data["salles"][salle]
    if "altitude_cm" in piece:
        return piece["altitude_cm"]
    return _etage(m, salle) * 240


def _global(salle, position):
    ox, oy = salle["plan"]["origine"]
    return ox + position[0], oy + position[1]


def _opposite(direction):
    return {"nord": "sud", "sud": "nord", "est": "ouest", "ouest": "est"}.get(direction)


def _salles_relies(m, depart):
    """Salles accessibles par des sorties horizontales ouvertes."""
    vus, file = {depart}, deque([depart])
    while file:
        salle = file.popleft()
        for sortie in m.data["salles"][salle].get("sorties", {}).values():
            vers = sortie.get("vers")
            porte = m.objets.get(sortie.get("porte"))
            if (vers not in m.data["salles"] or porte and not porte.get("ouverte")
                    or sortie.get("escalier") or not _meme_niveau(m, salle, vers)):
                continue
            reciproque = next((s for s in m.data["salles"][vers].get("sorties", {}).values()
                               if s.get("vers") == salle and s.get("porte") == sortie.get("porte")), None)
            if reciproque and vers not in vus:
                vus.add(vers)
                file.append(vers)
    return vus


def _globales(m, salles):
    """Cases visibles dans le plan global, plus les seuils des sorties."""
    cases_globales, opaques = {}, set()
    for salle in salles:
        piece = m.data["salles"][salle]
        ox, oy = piece["plan"]["origine"]
        for x, y in cases(piece):
            cases_globales[ox + x, oy + y] = (salle, (x, y))
        for direction, sortie in piece.get("sorties", {}).items():
            if len(sortie.get("case", ())) == 2:
                seuil = ox + sortie["case"][0], oy + sortie["case"][1]
                cases_globales.setdefault(seuil, None)
                porte = m.objets.get(sortie.get("porte"))
                if porte and not porte.get("ouverte"):
                    opaques.add(seuil)
                else:
                    opaques.discard(seuil)
        for id, o in m.objets.items():
            if not o.get("bloque_vue") or o.get("incorpore") or o.get("lieu") == "joueur":
                continue
            p = position_cible(m, id, salle)
            if p is not None:
                opaques.add((ox + p[0], oy + p[1]))
    return cases_globales, opaques


def _los_global(m, a, b, terrain, opaques):
    """Le tracé de ``_ligne`` de a vers b, case après case sans le construire : chaque case doit être
    du terrain, aucune avant b ne doit être opaque, et une diagonale ne passe pas entre deux coins
    bouchés."""
    x, y = a
    x1, y1 = b
    dx, sx = abs(x1 - x), 1 if x < x1 else -1
    dy, sy = -abs(y1 - y), 1 if y < y1 else -1
    err = dx + dy
    while x != x1 or y != y1:
        avant_x, avant_y = x, y
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
        p = (x, y)
        if p not in terrain:
            return False
        if p in opaques and (x != x1 or y != y1):
            return False
        if x != avant_x and y != avant_y:
            c1, c2 = (x, avant_y), (avant_x, y)
            if ((c1 not in terrain or c1 in opaques)
                    and (c2 not in terrain or c2 in opaques)):
                return False
    return True


def visible(m, id, acteur="joueur", champ=None):
    if id not in m.objets or id == acteur:
        return False
    memo = _memo_vue(m)
    champ_propre = champ is None
    champ = _champ(m, acteur, memo) if champ is None else champ
    o = m.objets[id]
    if o["type"] == "surface" and o.get("lieu") == (m.joueur["salle"] if acteur == "joueur" else m.objets[acteur]["lieu"]):
        # Les murs, le sol, le plafond de sa pièce : on en voit toujours une part, où qu'on regarde.
        return any(c[0] == o["lieu"] for c in champ)
    vu = _vu_dans(m, id, acteur, champ, memo if champ_propre else None, memo)[1]
    if memo is not None and champ_propre and a_verifier():
        with sans_memoire(m):
            assert visible(m, id, acteur) == vu, f"Vue mémorisée périmée : {acteur} / {id}"
    return vu


def _vu_dans(m, id, acteur, champ, memo_champ, memo, salles_du_champ=None):
    """(première place de l'objet dans le champ, vu ou non). Une place hors du champ ne compte pas :
    on ne cherche l'objet que dans les salles que le champ touche. Un objet accroché au mur n'est vu
    que si ce mur l'est. ``memo_champ`` : le mémo de l'état quand ``champ`` est le champ propre de
    l'acteur (ses murs vus y sont gardés)."""
    if salles_du_champ is None:
        salles_du_champ = {c[0] for c in champ}
    premiere = None
    for salle in m.data["salles"]:
        if salle not in salles_du_champ:
            continue
        position = _position_vue(m, memo, id, salle)
        if position is not None and (salle, position[0], position[1]) in champ:
            if premiere is None:
                premiere = (salle, position)
            ancrage = m.objets[id].get("ancrage_carte")
            if ancrage and tuple(ancrage) not in _murs(m, champ, acteur, memo_champ).get(salle, set()):
                continue
            return premiere, True
    return premiere, False


def _murs(m, champ, acteur, memo_champ):
    if memo_champ is None:
        return murs_visibles(m, champ, acteur)
    if ("murs", acteur) not in memo_champ:
        memo_champ["murs", acteur] = murs_visibles(m, champ, acteur)
    return memo_champ["murs", acteur]


def _position_vue(m, memo, id, salle):
    """position_cible, gardée le temps d'un état inchangé (voir ``etat_vue``) ; pour un objet
    simplement posé dans cette salle, d'une étape à l'autre, par tout ce qui fixe sa case."""
    if memo is None:
        return position_cible(m, id, salle)
    positions = memo.setdefault("positions", {})
    if (id, salle) not in positions:
        o = m.objets[id]
        if poses(m, memo)[id] == salle and o["type"] != "surface":
            p = o.get("position")
            # ``_salle_position`` d'un objet posé dans la salle qu'on regarde ne lit que ces clés (une
            # surface, sol ou plafond, peut suivre le joueur : elle n'est gardée que pour l'état).
            cle = (id, salle, o["type"], o.get("incorpore"), o.get("cote"), o.get("attache"),
                   o.get("position_salle"), None if p is None else tuple(p))
            places = m._cache_vue["persistant"]["places"]
            if cle not in places:
                places[cle] = position_cible(m, id, salle)
            positions[id, salle] = places[cle]
        else:
            positions[id, salle] = position_cible(m, id, salle)
    return positions[id, salle]


# Ce qui peut placer un objet posé dans une salle ailleurs que dans cette salle (``_salle_position``).
AILLEURS = frozenset(("appui_vertical", "installation"))


def poses(m, memo=None):
    """Pour chaque objet, la salle où il est posé, sans rien qui le place ailleurs : il n'a de place
    que dans cette salle, et personne ne le porte ; None pour les autres. Gardé pour l'état."""
    if memo is not None and "poses" in memo:
        return memo["poses"]
    salles, objets = m.data["salles"], m.objets
    resultat = {}
    for id, o in objets.items():
        lieu = o["lieu"]
        resultat[id] = (lieu if lieu in salles and lieu not in objets and o["type"] != "porte"
                        and AILLEURS.isdisjoint(o) else None)
    if memo is not None:
        memo["poses"] = resultat
    return resultat


def eclairage_niveau(m):
    from .perception import eclairage
    return eclairage(m)["niveau"]


# Distance de vue d'une case, si rien ne s'interpose, en distance réelle (``geometrie.distance``) :
# 8 si elle reçoit une lumière directe ou la pleine lumière du jour, 3 si elle n'est que dans la
# pénombre diffuse de la pièce.
PORTEE_VUE = {1: 3, 2: 8}


def signature_vue(m, lumiere=True, allumees=None):
    """Tout ce dont dépendent la lumière et les lignes de vue, hors géométrie des salles : portes
    et contenants ouverts, sources allumées et la case d'où elles éclairent, objets qui bloquent
    la vue. Deux états de même signature se voient de la même façon. Sans ``lumiere``, ce qui
    borne seulement la vue (``VueGeometrique``) ; ``allumees`` recueille alors les sources."""
    from .perception import allumee, salle_source
    cle = []
    salles = m.data["salles"]
    for id, o in m.objets.items():
        if o["type"] in ("porte", "contenant") or "ouverte" in o:
            cle.append(("ouverte", id, bool(o.get("ouverte"))))
        if allumees is not None and o.get("allume") and allumee(o):
            allumees.append((id, o))
        if lumiere and allumee(o):
            source = salle_source(m, o)
            cle.append(("source", id, source, position_cible(m, id, source) if source else None,
                        o.get("luminosite")))
        if o.get("bloque_vue"):
            if o.get("lieu") in salles and o["type"] not in ("porte", "surface") and _COMPOSEES_PLACE.isdisjoint(o):
                # Posé dans une salle : sa case ne dépend que de ces clés (``_salle_position``).
                cle.append(("opaque", id, o.get("lieu"), o.get("position_salle"), tuple(o.get("position") or ()),
                            bool(o.get("incorpore"))))
            else:
                cle.append(("opaque_place", id, bool(o.get("incorpore")), o.get("lieu") == "joueur",
                            tuple(position_cible(m, id, salle) for salle in salles)))
    return tuple(cle)


# Ce qui place un objet autrement que sa salle et sa case.
_COMPOSEES_PLACE = frozenset(("appui_vertical", "installation", "cote", "position_autonome"))


class VueGeometrique:
    """Ce qui borne la vue autour d'une salle, lumière à part : les salles reliées, leurs cases et
    seuils, les obstacles opaques. Les lignes de vue s'y calculent une fois ; dans
    ``vue_memorisee``, elle est partagée par toutes les cartes de lumière de même géométrie."""

    def __init__(self, m, salle):
        self.salles = _salles_relies(m, salle)
        # Les salles d'où une lueur peut parvenir, par des passages ouverts (``_eclairage_pieces``).
        self.atteintes = _salles_atteintes(m, salle)
        self.terrain, self.opaques = _globales(m, self.salles)
        self._lignes = {}
        # Les cases du sol des salles reliées : ((salle, x, y), case globale).
        self.sol = [((salle, x, y), _global(m.data["salles"][salle], (x, y)))
                    for salle in self.salles for x, y in cases(m.data["salles"][salle])]

    def ligne(self, a, b):
        """``_los_global`` de a vers b. Seule l'extrémité b peut être ajoutée un instant au terrain
        (un seuil qu'on regarde) : sa présence fait partie de la clé."""
        cle = (a, b, b in self.terrain)
        resultat = self._lignes.get(cle)
        if resultat is None:
            resultat = self._lignes[cle] = _los_global(None, a, b, self.terrain, self.opaques)
        return resultat

    def mutuelle(self, a, b):
        """Vue symétrique : Bresenham diffère selon le sens, on exige les deux tracés libres."""
        return self.ligne(a, b) and self.ligne(b, a)


def _salles_atteintes(m, salle):
    """Les salles reliées à une salle par des passages sans porte fermée, à tout niveau."""
    vus, file = {salle}, deque([salle])
    while file:
        courante = file.popleft()
        for sortie in m.data["salles"][courante]["sorties"].values():
            porte = m.objets.get(sortie.get("porte"))
            if porte and not porte.get("ouverte"):
                continue
            if sortie.get("vers") not in vus:
                vus.add(sortie.get("vers"))
                file.append(sortie.get("vers"))
    return vus


def vue_geometrique(m, salle, geometrie=None):
    """La géométrie de la vue d'une salle, gardée dans ``vue_memorisee`` par signature sans lumière
    (``geometrie``, si elle est déjà calculée)."""
    cache = getattr(m, "_cache_vue", None)
    if cache is None:
        return VueGeometrique(m, salle)
    geometries = cache["persistant"]["geometries"]
    cle = (salle, signature_vue(m, lumiere=False) if geometrie is None else geometrie)
    if cle not in geometries:
        geometries[cle] = VueGeometrique(m, salle)
    return geometries[cle]


def signature_salle(m, salle):
    """La signature de la vue depuis une salle : la géométrie (signature sans lumière) et les
    seules sources dont la lumière peut y parvenir. D'une salle reliée, une source éclaire
    directement : sa case compte ; d'une salle atteinte par des passages ouverts, elle n'envoie
    qu'une lueur diffuse : sa salle et sa force comptent. Une lanterne qu'on promène ailleurs ne
    change pas ce qu'on voit ici."""
    from .perception import allumee, salle_source
    allumees = []
    geometrie = signature_vue(m, lumiere=False, allumees=allumees)
    vue = vue_geometrique(m, salle, geometrie)
    sources = []
    for id, o in allumees:
        origine = salle_source(m, o)
        if origine in vue.atteintes:
            sources.append((id, origine, o.get("luminosite"),
                            position_cible(m, id, origine) if origine in vue.salles else None))
    return geometrie, tuple(sources)


# Ce que lit la perception sur chaque objet (``percus``, ``visible``, ``position_cible``, la lumière
# et les lignes de vue) : ce qui le place, le montre ou le cache, l'éclaire ou bloque la vue.
CLES_VUE = ("id", "type", "lieu", "position_salle", "orientation", "detail_local", "incorpore", "allume",
            "luminosite", "ouverte", "bloque_vue", "masse", "longueur_cm", "mobile", "cote", "attache", "nom",
            "position_autonome", "ancrage_initial")
# Valeurs composées, rares, figées par leur texte : une modification en place change l'empreinte.
CLES_VUE_COMPOSEES = ("ancrage_carte", "positions_salles", "appui_vertical", "installation")
_COMPOSEES = frozenset(CLES_VUE_COMPOSEES)
ETATS_GARDES = 8      # états récents dont on garde la perception (un regard tourné puis rendu revient au même)


def etat_vue(m):
    """Empreinte de tout ce dont dépend la perception, hors géométrie des salles : pour chaque objet,
    les clés de ``CLES_VUE``, s'il éclaire, sa case et ses clés de ``CLES_VUE_COMPOSEES`` ; le joueur.
    Deux états de même empreinte se perçoivent de la même façon, par tout acteur."""
    from .perception import allumee
    j = m.joueur
    p = j.get("position")
    return (j.get("salle"), None if p is None else tuple(p), j.get("orientation"), tuple([
        (cle, tuple(map(o.get, CLES_VUE)), bool(o.get("allume")) and allumee(o),
         None if (p := o.get("position")) is None else tuple(p),
         None if _COMPOSEES.isdisjoint(o) else repr(tuple(map(o.get, CLES_VUE_COMPOSEES))))
        for cle, o in m.objets.items()]))


def _memo_vue(m):
    """Le mémo de l'état courant (positions, champs, perceptions des acteurs), à l'intérieur de
    ``vue_memorisee`` ; None ailleurs. La clé est l'empreinte complète de l'état (``etat_vue``) ;
    dans ``etat_fige``, celle calculée en entrant."""
    cache = getattr(m, "_cache_vue", None)
    if cache is None:
        return None
    if "fige" in cache:
        return cache["fige"]
    etat = etat_vue(m)
    etats = cache.setdefault("etats", {})
    memo = etats.get(etat)
    if memo is None:
        if len(etats) >= ETATS_GARDES:
            del etats[next(iter(etats))]
        # L'empreinte elle-même : ce qui a changé d'un état à l'autre (``esprits._percus_depuis``).
        memo = etats[etat] = {"etat": etat}
    return memo


@contextmanager
def etat_fige(m):
    """Un bloc qui ne touche ni aux objets ni au joueur (il ne révise que des esprits) : l'empreinte
    de l'état n'y est calculée qu'une fois. En vérification, on contrôle qu'il n'a rien changé."""
    cache = getattr(m, "_cache_vue", None)
    if cache is None or "fige" in cache:
        yield
        return
    cache["fige"] = _memo_vue(m)
    avant = etat_vue(m) if VERIFICATION else None
    try:
        yield
    finally:
        del cache["fige"]
    assert avant is None or etat_vue(m) == avant, "État modifié dans un bloc figé"


# Part des lectures mémorisées recomparées à un calcul de zéro (0 : aucune, 1 : toutes) ; un écart
# lève une AssertionError. Réservé aux tests et aux bancs de vérification.
VERIFICATION = 0.0


def a_verifier():
    if not VERIFICATION:
        return False
    import random
    global _TIRAGE
    if _TIRAGE is None:
        _TIRAGE = random.Random(1985)
    return _TIRAGE.random() < VERIFICATION


_TIRAGE = None


@contextmanager
def sans_memoire(m):
    """Le temps du bloc, tout est recalculé de zéro (vérification de la mémoire de la vue)."""
    cache = m.__dict__.pop("_cache_vue", None)
    try:
        yield
    finally:
        if cache is not None:
            m._cache_vue = cache


@contextmanager
def vue_memorisee(m):
    """Pendant la vie des PNJ, la géométrie ne change pas : cartes de lumière et champs de vision
    sont gardés tant que la signature de la vue ne change pas ; positions et perceptions, tant que
    l'état ne change pas (``etat_vue``). Hors de ce bloc, tout est recalculé.

    Lignes de vue, ce qu'on voit autour d'une case et champs de vision ne dépendent que des salles
    et de la signature : ils restent gardés d'un bloc à l'autre (``_memoire_geometrie``)."""
    ancien = getattr(m, "_cache_vue", None)
    m._cache_vue = {"persistant": _memoire_geometrie(m)} if ancien is None else ancien
    try:
        yield
    finally:
        if ancien is None:
            del m._cache_vue


_MEMOIRE = threading.local()   # par fil d'exécution : rien n'est partagé entre deux fils
GEOMETRIES_GARDEES = 4
ENTREES_MAX = 5000             # par sorte d'entrée et par géométrie ; au-delà, on repart de zéro


def _memoire_geometrie(m):
    """La mémoire de la vue pour la géométrie actuelle des salles (plans, sorties, niveaux, jour),
    clé : le texte complet des salles. Deux mondes de mêmes salles et de même signature se voient
    de la même façon : la mémoire ne garde rien d'autre qui leur soit propre."""
    memoires = getattr(_MEMOIRE, "geometries", None)
    if memoires is None:
        memoires = _MEMOIRE.geometries = {}
    cle = repr(m.data["salles"])
    if cle not in memoires:
        if len(memoires) >= GEOMETRIES_GARDEES:
            del memoires[next(iter(memoires))]
        memoires[cle] = {"geometries": {}, "alentours": {}, "portees": {}, "champs": {}, "places": {}}
    memoire = memoires[cle]
    for entrees in memoire.values():
        if len(entrees) > ENTREES_MAX:
            entrees.clear()
    return memoire


def _signature(m, memo, salle):
    """``signature_salle``, gardée pour l'état (``memo["signatures"]``, que des états de mêmes
    signatures se partagent : ``esprits._heriter_signatures``), recomparée en vérification."""
    if memo is None:
        return signature_salle(m, salle)
    signatures = memo.get("signatures")
    if signatures is None:
        signatures = memo["signatures"] = {}
    if salle not in signatures:
        signatures[salle] = signature_salle(m, salle)
    elif a_verifier():
        assert signatures[salle] == signature_salle(m, salle), f"Signature mémorisée périmée : {salle}"
    return signatures[salle]


def carte_lumiere(m, salle, memo=None):
    """La carte de lumière d'une salle, gardée par signature de la vue dans ``vue_memorisee``."""
    from .perception import CarteLumiere
    cache = getattr(m, "_cache_vue", None)
    if cache is None:
        return CarteLumiere(m, salle)
    # Hors d'un état figé, la signature seule coûte moins que l'empreinte complète.
    signature = _signature(m, cache.get("fige") if memo is None else memo, salle)
    cle = ("lumiere", salle, signature)
    if cle not in cache:
        carte = cache[cle] = CarteLumiere(m, salle, vue_geometrique(m, salle, signature[0]))
        # Ce qu'on voit autour de chaque case, jusqu'où porte la vue sur chaque case : ils ne
        # dépendent que des salles et de la signature.
        carte.alentours = cache["persistant"]["alentours"].setdefault((salle, signature), {})
        carte.portees = cache["persistant"]["portees"].setdefault((salle, signature), {})
    return cache[cle]


def _vue(m, acteur="joueur", memo=None):
    """Origine globale du regard d'un acteur, terrain et carte de lumière des salles reliées. Dans un
    état figé (``etat_fige``) ou avec le mémo de l'état, gardées pour l'état : elles ne dépendent que
    de ce que lit ``etat_vue`` (sa place, les sources et ce qui borne la vue), pas de son regard."""
    if memo is None:
        cache = getattr(m, "_cache_vue", None)
        fige = None if cache is None else cache.get("fige")
    else:
        fige = memo
    if fige is not None and ("vue", acteur) in fige:
        if a_verifier():
            salle, position = position_acteur(m, acteur)
            assert fige["vue", acteur] == (_global(m.data["salles"][salle], position), carte_lumiere(m, salle, memo)), \
                f"Regard mémorisé périmé : {acteur}"
        return fige["vue", acteur]
    salle, position = position_acteur(m, acteur)
    lumiere = carte_lumiere(m, salle, memo)
    origine = _global(m.data["salles"][salle], position)
    if fige is not None:
        fige["vue", acteur] = origine, lumiere
    return origine, lumiere


def _vu(m, origine, lumiere, cible, orientation=None):
    if not dans_le_cone(origine, orientation, cible):
        return False
    loin = distance(cible, origine)
    if loin > PORTEE_VUE[2]:
        return False  # Au-delà de la plus longue vue, inutile de chercher la lumière.
    if loin > _portee(lumiere, cible):
        return False
    return lumiere.geometrie.mutuelle(origine, cible)


def _portee(lumiere, cible):
    """Jusqu'où l'on voit une case : loin si elle est éclairée ou reçoit une lumière directe, de
    près dans la pénombre, pas du tout dans le noir. Gardé par la carte de lumière."""
    portee = lumiere.portees.get(cible)
    if portee is None:
        niveau = lumiere.niveau(cible)
        portee = lumiere.portees[cible] = PORTEE_VUE[2 if niveau == 2 or lumiere.directe(cible) else 1] if niveau else -1
    return portee


def acteurs_vus(m, acteur, autres):
    """Ceux d'``autres`` (personnages ou joueur) que l'acteur voit dans sa propre salle : un test
    case par case, sans calculer tout son champ de vision."""
    salle = position_acteur(m, acteur)[0]
    origine = lumiere = None
    vus = []
    for autre in autres:
        if autre == "joueur":
            if m.joueur["salle"] != salle:
                continue
            case = tuple(m.joueur["position"])
        else:
            case = position_cible(m, autre, salle) if m.objets[autre]["lieu"] == salle else None
        if case is None:
            continue
        if origine is None:
            origine, lumiere = _vue(m, acteur)
        if _vu(m, origine, lumiere, _global(m.data["salles"][salle], case), orientation_acteur(m, acteur)):
            vus.append(autre)
    return vus


def dans_le_regard(m, salle, case, acteur="joueur"):
    """Une case sous le regard de l'acteur, même dans le noir : une flamme y serait vue de loin."""
    origine, lumiere = _vue(m, acteur)
    if salle not in lumiere.salles:
        return False
    cible = _global(m.data["salles"][salle], case)
    if distance(cible, origine) > PORTEE_VUE[2]:
        return False
    if not dans_le_cone(origine, orientation_acteur(m, acteur), cible):
        return False
    return lumiere.geometrie.mutuelle(origine, cible)


def sortie_visible(m, salle, direction, acteur="joueur"):
    """Retourne si le seuil est visible, même si une porte le ferme."""
    sortie = m.data["salles"].get(salle, {}).get("sorties", {}).get(direction)
    if not sortie or len(sortie.get("case", ())) != 2:
        return False
    origine, lumiere = _vue(m, acteur)
    if salle not in lumiere.salles:
        return False
    cible = _global(m.data["salles"][salle], sortie["case"])
    ajoute = cible not in lumiere.terrain
    if ajoute:
        lumiere.terrain[cible] = None
    try:
        return _vu(m, origine, lumiere, cible, orientation_acteur(m, acteur))
    finally:
        if ajoute:
            del lumiere.terrain[cible]


def regard_vers(m, id):
    """La direction vers laquelle le joueur doit se tourner pour voir ``id``, qu'il ne voit pas de
    face mais verrait en se tournant ; None sinon."""
    j = m.joueur
    if (not m.data.get("mode_cases") or not j.get("orientation") or id not in m.objets or m.est_porte(id)
            or visible(m, id) or not m.present_physique(id)):
        return None
    case = position_cible(m, id, j["salle"])
    vers = orientation_vers(tuple(j["position"]), tuple(case)) if case is not None else None
    if vers is None:
        return None
    ancien = j["orientation"]
    j["orientation"] = vers
    try:
        return vers if visible(m, id) else None
    finally:
        j["orientation"] = ancien


def sortie_connue(m, salle, direction):
    """Une sortie qu'il voit, ou dont il a déjà vu ou foulé le seuil : il sait qu'elle est là,
    même dans son dos."""
    if sortie_visible(m, salle, direction):
        return True
    sortie = m.data["salles"].get(salle, {}).get("sorties", {}).get(direction)
    pos = _case_interieure(m, salle, sortie) if sortie else None
    return pos is not None and list(pos) in m.data.get("exploration", {}).get(salle, [])


def champ_visible(m, acteur="joueur"):
    """Cases vues maintenant par l'acteur, incluant les paliers d'une porte ouverte."""
    return set(_champ(m, acteur, _memo_vue(m)))


def _champ(m, acteur, memo):
    """Le champ de l'acteur, à ne pas modifier : gardé dans ``vue_memorisee`` par état (``memo``),
    et par position, regard et signature de la vue d'un état à l'autre."""
    if memo is not None and ("champ", acteur) in memo:
        return memo["champ", acteur]
    cache = getattr(m, "_cache_vue", None)
    cle = None
    orientation = orientation_acteur(m, acteur)
    if cache is not None:
        champs = cache["persistant"]["champs"]
        salle, position = position_acteur(m, acteur)
        cle = (salle, position, orientation, _signature(m, memo, salle))
        if cle in champs:
            memo["champ", acteur] = champs[cle]
            return champs[cle]
    origine, lumiere = _vue(m, acteur, memo)
    vus = {case for case, cible in _alentour(m, origine, lumiere) if dans_le_cone(origine, orientation, cible)}
    if cache is not None:
        champs[cle] = memo["champ", acteur] = frozenset(vus)
    return vus


def _alentour(m, origine, lumiere):
    """Ce qu'on verrait d'une case en regardant tout autour : [((salle, x, y), case globale)]. Le
    regard ne fait que retrancher ce qui sort du cône : gardé par la carte de lumière, pour toute
    orientation et tout acteur qui se tient là."""
    if origine not in lumiere.alentours:
        geometrie, vues = lumiere.geometrie, []
        for case, cible in geometrie.sol:
            loin = distance(cible, origine)
            if (loin <= PORTEE_VUE[2] and loin <= _portee(lumiere, cible)
                    and geometrie.mutuelle(origine, cible)):
                vues.append((case, cible))
        lumiere.alentours[origine] = vues
    return lumiere.alentours[origine]


def murs_visibles(m, champ=None, acteur="joueur"):
    """Murs vus depuis la position de l'acteur, sans déduire les contours du plan caché."""
    champ = champ_visible(m, acteur) if champ is None else champ
    if not champ:
        return {}
    salle_acteur, position = position_acteur(m, acteur)
    salles = _salles_relies(m, salle_acteur)
    terrain, opaques = _globales(m, salles)
    origine = _global(m.data["salles"][salle_acteur], position)
    rayon = PORTEE_VUE[2]
    vus = {}
    for salle, x, y in champ:
        if salle not in salles:
            continue
        ox, oy = m.data["salles"][salle]["plan"]["origine"]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cible = ox + x + dx, oy + y + dy
            if cible in terrain or distance(cible, origine) > rayon:
                continue
            terrain[cible] = None
            visible = _los_global(m, origine, cible, terrain, opaques)
            del terrain[cible]
            if visible:
                vus.setdefault(salle, set()).add((x + dx, y + dy))
    return vus


def memoriser(m):
    """Ce que le joueur voit maintenant devient connu : cases, murs, objets et portes vus. Ne touche
    ni aux objets ni au joueur : sa vue n'y est calculée qu'une fois."""
    with vue_memorisee(m), etat_fige(m):
        return _memoriser(m)


def _memoriser(m):
    from .carte import objets_visibles_cases, symbole_objet_cases, symbole_porte_cases
    from .francais import designer

    exploration = m.data.setdefault("exploration", {})
    for salle in m.data["salles"]:
        exploration.setdefault(salle, [])
    champ = champ_visible(m)
    for salle, x, y in sorted(champ):
        connues = {tuple(p) for p in exploration[salle]}
        if (x, y) not in connues:
            exploration[salle].append([x, y])
    # Même dans le noir, le joueur connaît la case sur laquelle il marche.
    salle_joueur = m.joueur["salle"]
    position_joueur = list(m.joueur["position"])
    if position_joueur not in exploration[salle_joueur]:
        exploration[salle_joueur].append(position_joueur)

    murs = m.data.setdefault("murs_memorises", {})
    for salle, positions in murs_visibles(m, champ).items():
        connues = {tuple(p) for p in murs.setdefault(salle, [])}
        for x, y in sorted(positions):
            if (x, y) not in connues:
                murs[salle].append([x, y])

    souvenirs = m.data.setdefault("souvenirs_visuels", {})
    observations = {objet["id"]: {
        "salle": salle, "position": list(pos),
        "contact": list(position_cible(m, objet["id"], salle)),
        "symbole": symbole_objet_cases(objet, salle, m), "nom": designer(objet),
    } for objet, salle, pos in objets_visibles_cases(m, champ)}
    for id, souvenir in list(souvenirs.items()):
        salle = souvenir["salle"]
        x, y = souvenir.get("contact", souvenir["position"])
        if (id in observations or m.est_porte(id)
                or (salle, x, y) in champ):
            del souvenirs[id]
    souvenirs.update(observations)

    portes_vues = m.data.setdefault("souvenirs_portes", {})
    for salle, piece in m.data["salles"].items():
        for direction, sortie in piece.get("sorties", {}).items():
            id_porte = sortie.get("porte")
            if id_porte in m.objets and sortie_visible(m, salle, direction):
                portes_vues[id_porte] = symbole_porte_cases(m.objets[id_porte])
    return exploration


def preparer_pas(m, direction):
    vecteur = VECTEURS.get(direction) if isinstance(direction, str) else direction
    if not isinstance(vecteur, (tuple, list)) or len(vecteur) != 2:
        _erreur("Direction de déplacement inconnue.")
    dx, dy = vecteur
    if type(dx) is not int or type(dy) is not int or max(abs(dx), abs(dy)) != 1:
        _erreur("Le déplacement doit avancer d'une case.")
    pas = pas_vers(m, m.joueur["salle"], tuple(m.joueur["position"]), (dx, dy))
    if pas["salle"] != m.joueur["salle"]:
        from .eau import refuser_entree
        refuser_entree(m, pas["salle"])
    destination = {"salle": pas["salle"], "position": pas["position"]}
    # Aucun pas ne s'achève sur la case d'un autre : on ne s'arrête pas sur quelqu'un. Celui qui
    # s'y tient s'écarte de lui-même, sauf raison de rester (``passage.laisser_passer``).
    from .pnj import occupants
    arrivee = (pas["salle"], tuple(pas["position"]))
    occupant = occupants(m, "joueur").get(arrivee)
    if occupant is not None:
        from .passage import laisser_passer
        case, raison = laisser_passer(m, occupant, "joueur", [arrivee])
        if case is None:
            raise _sur_le_passage(m, occupant, raison)
        destination["ecart"] = {"personnage": occupant, "salle": case[0], "position": list(case[1])}
    return destination


def _sur_le_passage(m, occupant, raison):
    """Le refus d'un pas sur la case d'un personnage qui ne s'écarte pas : le joueur voit ce qu'il
    ne fait pas, pas ce qu'il pense ; le MJ reçoit la raison et ce qui reste possible."""
    from .francais import designer
    from .monde import ErreurMonde
    o = m.objets[occupant]
    vu = m.visible(occupant)
    nom = designer(o, debut=True) if vu else "Quelqu'un"
    message = {"geste": " se tient là, sur ton passage, occupé" + ("e" if o.get("genre") == "f" else "")
                        + " à ce qu'" + ("elle" if o.get("genre") == "f" else "il") + " fait.",
               "place": " se tient là, sur ton passage, sans place pour s'écarter."}.get(
        raison, " se tient là, sur ton passage, et ne s'écarte pas.")
    pourquoi = {"geste": "un geste en cours le retient sur sa case", "mefiance": "il se méfie de Corvus",
                "orgueil": "sa fierté l'emporte de loin sur son altruisme",
                "place": "aucune case voisine libre hors du chemin"}.get(raison, raison)
    qui = occupant if vu else "un personnage"
    return ErreurMonde(nom + message,
                       f"la case visée est occupée par {qui}, qui ne s'écarte pas de lui-même ({pourquoi}) ; "
                       "un pas mène sur une case libre. Pour passer : le lui demander (parole_joueur, contenu "
                       f"{{type passage}} adressé à {qui}), ou le pousser (action pousser, cible {qui}), "
                       "ou passer ailleurs.")


def pas_vers(m, salle, position, vecteur, porte_fermee=False, case_libre=None):
    """Où mène un pas d'une case depuis (salle, position), pour le joueur comme pour un PNJ :
    {"salle", "position", "porte"}. ``porte`` est la porte fermée à franchir, si
    ``porte_fermee`` l'admet ; sinon une porte fermée bloque, comme un mur ou un obstacle.
    ``case_libre`` remplace ``_case_libre`` par une version mémorisée le temps d'une recherche."""
    pas = _pas(m, salle, position, vecteur, porte_fermee, case_libre)
    if isinstance(pas, str):
        _erreur(pas)
    return pas


def _pas(m, salle, position, vecteur, porte_fermee=False, case_libre=None):
    """``pas_vers``, qui rend la raison du refus (un texte) au lieu de la lever."""
    _case_libre_ = case_libre or (lambda s, c: _case_libre(m, s, c))
    dx, dy = vecteur
    x, y = position
    destination = (x + dx, y + dy)
    if destination in cases(m.data["salles"][salle]):
        if dx and dy and not (_case_libre_(salle, (x + dx, y))
                              and _case_libre_(salle, (x, y + dy))):
            return "Un mur ou un obstacle bloque le passage en diagonale."
        if not _case_libre_(salle, destination):
            return "Un obstacle solide occupe cette case."
        return {"salle": salle, "position": [destination[0], destination[1]], "porte": None}
    if dx and dy:
        return "Le mur bloque ce déplacement en diagonale."
    sortie = next((s for d, s in m.data["salles"][salle].get("sorties", {}).items()
                   if VECTEURS.get(d) == (dx, dy)
                   and _case_interieure(m, salle, s) == (x, y)), None)
    if not sortie:
        return "Un mur bloque le passage."
    porte = m.objets.get(sortie.get("porte"))
    fermee = bool(porte and not porte.get("ouverte"))
    if fermee and not porte_fermee:
        return "La porte fermée bloque le passage."
    vers = sortie.get("vers")
    piece_vers = m.data["salles"].get(vers, {})
    retour = next((s for s in piece_vers.get("sorties", {}).values()
                   if s.get("vers") == salle and s.get("porte") == sortie.get("porte")), None)
    pos = _case_interieure(m, vers, retour) if retour else None
    if pos is None:
        return "Aucun sol ne rejoint ce passage."
    if not _case_libre_(vers, pos):
        return "Un obstacle solide bloque l'autre côté du passage."
    return {"salle": vers, "position": [pos[0], pos[1]], "porte": porte["id"] if fermee else None}


def trajet(m, salle, position, arrivee, franchissable=lambda porte: True, libre=lambda salle, case: True,
           solides=True):
    """Le chemin le plus court en temps, d'un pas à la fois, vers une case où ``arrivee(salle, case)`` :
    [(salle, case, porte fermée à franchir ou None, sens du pas)], vide si l'on y est déjà, None
    sans passage. Chaque pas coûte sa durée (``temps.duree_pas`` : en diagonale, √2 fois un pas
    droit) ; à durée égale, l'ordre de découverte départage (les sens dans l'ordre de ``VECTEURS``
    triés), sans hasard.
    Une porte fermée se franchit si ``franchissable(porte)`` ; ``libre`` écarte les cases occupées.
    Sans ``solides``, les obstacles sont ignorés : le chemin qu'ils barrent."""
    from .temps import PAS_JOUEUR, duree_pas
    pas_de = _pas_possibles(m, solides)
    depart = (salle, tuple(position))
    if arrivee(*depart):
        return []
    sens = [(vecteur, duree_pas(PAS_JOUEUR, vecteur)) for vecteur in sorted(set(VECTEURS.values()))]
    couts, precedent, ordre = {depart: 0}, {depart: None}, 0
    file, faits = [(0, 0, depart)], set()
    while file:
        cout, _, courant = heapq.heappop(file)
        if courant in faits:
            continue
        faits.add(courant)
        if courant != depart and arrivee(*courant):
            chemin = []
            while precedent[courant]:
                avant, porte, vecteur = precedent[courant]
                chemin.append((courant[0], courant[1], porte, vecteur))
                courant = avant
            return chemin[::-1]
        for vecteur, duree in sens:
            pas = pas_de(courant[0], courant[1], vecteur)
            if pas is None:
                continue
            suivant, porte = pas
            if (suivant in faits or cout + duree >= couts.get(suivant, cout + duree + 1) or not libre(*suivant)
                    or porte and not franchissable(porte)):
                continue
            couts[suivant] = cout + duree
            precedent[suivant] = (courant, porte, vecteur)
            ordre += 1
            heapq.heappush(file, (cout + duree, ordre, suivant))
    return None


TABLES_DE_PAS = 16    # tables des pas gardées par géométrie (``_pas_possibles``)


def _pas_possibles(m, solides):
    """``_pas`` d'une case dans un sens, une porte fermée admise : ((salle, case), porte fermée ou
    None), ou None si le pas est impossible. Il ne dépend que de la géométrie des salles, des
    obstacles solides de chaque salle (``_bloquantes``) et des portes ouvertes ou fermées : dans
    ``vue_memorisee``, les pas sont gardés d'un trajet à l'autre tant que ceux-ci n'ont pas changé.
    En vérification (``VERIFICATION``), un pas gardé est recomparé à un calcul de zéro."""
    libres, bloquantes = {}, {}

    def case_libre(s, c):
        # ``_case_libre``, les obstacles de chaque salle relevés une fois.
        if (s, c) not in libres:
            if solides and s not in bloquantes:
                bloquantes[s] = _bloquantes(m, s)
            libres[s, c] = c in cases(m.data["salles"][s]) and not (solides and any(p == c for p in bloquantes[s]))
        return libres[s, c]

    def calculer(s, c, vecteur):
        pas = _pas(m, s, c, vecteur, porte_fermee=True, case_libre=case_libre)
        return None if isinstance(pas, str) else ((pas["salle"], tuple(pas["position"])), pas["porte"])
    cache = getattr(m, "_cache_vue", None)
    if cache is None:
        return calculer
    objets, salles = m.objets, m.data["salles"]
    # Les obstacles, tels que ``_bloquantes`` les relève pour chaque salle, en une passe ; les portes
    # des sorties, ouvertes ou non.
    obstacles = tuple((id, o["lieu"], position_cible(m, id, o["lieu"])) for id, o in objets.items()
                      if o.get("bloque_passage") and not o.get("incorpore") and o.get("lieu") in salles
                      ) if solides else None
    portes = tuple((id, id in objets, bool(objets[id].get("ouverte")) if id in objets else None)
                   for id in sorted({x["porte"] for d in salles.values() for x in d.get("sorties", {}).values()
                                     if x.get("porte")}))
    tables = cache["persistant"].setdefault("pas", {})
    cle = (solides, obstacles, portes)
    if cle not in tables:
        if len(tables) >= TABLES_DE_PAS:
            del tables[next(iter(tables))]
        tables[cle] = {}
    table = tables[cle]

    def pas_de(s, c, vecteur):
        k = (s, c, vecteur)
        if k not in table:
            table[k] = calculer(s, c, vecteur)
        elif a_verifier():
            assert table[k] == calculer(s, c, vecteur), f"Pas mémorisé périmé : {k}"
        return table[k]
    return pas_de


def destination_appui(m, support, salle):
    o = m.objets.get(support, {})
    a = o.get("appui_vertical", {})
    if salle == a.get("bas"):
        p = a.get("position_bas")
    elif salle == a.get("haut"):
        p = a.get("position_haut")
    else:
        return None
    if p is None or tuple(p) not in cases(m.data["salles"].get(salle, {})):
        return None
    if _bloque(m, salle, tuple(p), sauf=support):
        _erreur("Un obstacle solide bloque l'extrémité de l'appui.")
    return tuple(p)


def verifier(m):
    """Valide coordonnées spatiales présentes, tout en acceptant les vieilles parties."""
    for o in [*m.objets.values(), m.joueur]:
        if "orientation" in o and o["orientation"] not in VECTEURS:
            raise AssertionError(f"Orientation invalide : {o.get('id', 'joueur')}")
    for salle, piece in m.data["salles"].items():
        if "plan" not in piece:
            continue
        for direction, sortie in piece.get("sorties", {}).items():
            if sortie.get("case") and len(sortie["case"]) != 2:
                raise AssertionError(f"Case de sortie invalide : {salle}/{direction}")
            if sortie.get("case") and any(type(v) is not int for v in sortie["case"]):
                raise AssertionError(f"Case de sortie invalide : {salle}/{direction}")
    # Deux sols au même niveau ne peuvent occuper la même tuile globale.
    plans = [(id, p) for id, p in m.data["salles"].items() if "plan" in p]
    for i, (a, pa) in enumerate(plans):
        ax, ay = pa["plan"]["origine"]
        cases_a = {(ax + x, ay + y) for x, y in cases(pa)}
        for b, pb in plans[i + 1:]:
            if _etage(m, a) != _etage(m, b):
                continue
            bx, by = pb["plan"]["origine"]
            cases_b = {(bx + x, by + y) for x, y in cases(pb)}
            if cases_a & cases_b:
                raise AssertionError(f"Sols superposés au même niveau : {a}/{b}")
    # Une sortie ordinaire doit pointer sur le même seuil global que son opposée.
    for salle, piece in m.data["salles"].items():
        if "plan" not in piece:
            continue
        for direction, sortie in piece.get("sorties", {}).items():
            vers = sortie.get("vers")
            if direction not in ("nord", "sud", "est", "ouest") or vers not in m.data["salles"]:
                raise AssertionError(f"Sortie spatiale invalide : {salle}/{direction}")
            dest = m.data["salles"][vers]
            retour_direction = _opposite(direction)
            retour = dest.get("sorties", {}).get(retour_direction)
            if (not retour or retour.get("vers") != salle
                    or retour.get("porte") != sortie.get("porte")
                    or bool(retour.get("escalier")) != bool(sortie.get("escalier"))):
                raise AssertionError(f"Sortie sans réciproque opposée : {salle}/{direction}")
            if (not sortie.get("case") or len(sortie["case"]) != 2
                    or not retour.get("case") or len(retour["case"]) != 2):
                raise AssertionError(f"Seuil spatial incomplet : {salle}/{direction}")
            if not sortie.get("escalier"):  # Les deux bouts d'un escalier sont à des étages différents.
                if _global(piece, sortie["case"]) != _global(dest, retour["case"]):
                    raise AssertionError(f"Seuils globaux divergents : {salle}/{direction}")
    salle_joueur = m.joueur.get("salle")
    position_joueur = m.joueur.get("position")
    if (salle_joueur not in m.data["salles"] or not isinstance(position_joueur, (list, tuple))
            or len(position_joueur) != 2 or any(type(v) is not int for v in position_joueur)
            or tuple(position_joueur) not in cases(m.data["salles"][salle_joueur])):
        raise AssertionError("Position du joueur hors du sol")
    for id, o in m.objets.items():
        salle = o.get("position_salle")
        p = o.get("position")
        if salle in m.data["salles"] and p is not None and "plan" in m.data["salles"][salle]:
            if tuple(p) not in cases(m.data["salles"][salle]):
                raise AssertionError(f"Position d'objet hors du sol : {id}")
        if "ancrage_carte" in o:
            ancrage = o["ancrage_carte"]
            if (salle not in m.data["salles"] or not isinstance(p, list)
                    or len(p) != 2 or any(type(v) is not int for v in p)
                    or tuple(p) not in cases(m.data["salles"][salle])
                    or not isinstance(ancrage, list) or len(ancrage) != 2
                    or any(type(v) is not int for v in ancrage)
                    or tuple(ancrage) in cases(m.data["salles"][salle])
                    or abs(ancrage[0] - p[0]) + abs(ancrage[1] - p[1]) != 1
                    or any(tuple(sortie.get("case", ())) == tuple(ancrage)
                           for sortie in m.data["salles"][salle]["sorties"].values())
                    or (o["mobile"] and not o.get("attache"))):
                raise AssertionError(f"Ancrage mural invalide : {id}")
        if o.get("appui_vertical"):
            a = o["appui_vertical"]
            for cle, salle_cle in (("position_bas", "bas"), ("position_haut", "haut")):
                if cle in a:
                    endpoint = a[cle]
                    if (a.get(salle_cle) not in m.data["salles"]
                            or not isinstance(endpoint, (list, tuple)) or len(endpoint) != 2
                            or any(type(v) is not int for v in endpoint)
                            or tuple(endpoint) not in cases(m.data["salles"][a[salle_cle]])):
                        raise AssertionError(f"Extrémité d'appui hors du sol : {id}/{cle}")
        if o.get("type") == "porte":
            for salle, position in o.get("positions_salles", {}).items():
                if salle not in m.data["salles"] or tuple(position) not in cases(m.data["salles"][salle]):
                    raise AssertionError(f"Position de porte hors du sol : {id}/{salle}")
    for salle, positions in m.data.get("exploration", {}).items():
        if salle not in m.data["salles"] or not isinstance(positions, list):
            raise AssertionError(f"Mémoire d'exploration invalide : {salle}")
        connues = set()
        for position in positions:
            if (not isinstance(position, list) or len(position) != 2
                    or any(type(v) is not int for v in position)
                    or tuple(position) not in cases(m.data["salles"][salle])
                    or tuple(position) in connues):
                raise AssertionError(f"Case mémorisée invalide : {salle}/{position}")
            connues.add(tuple(position))
    murs = m.data.get("murs_memorises", {})
    if not isinstance(murs, dict):
        raise AssertionError("Mémoire des murs invalide")
    for salle, positions in murs.items():
        if salle not in m.data["salles"] or not isinstance(positions, list):
            raise AssertionError(f"Mémoire des murs invalide : {salle}")
        connues = set()
        for position in positions:
            if (not isinstance(position, list) or len(position) != 2
                    or any(type(v) is not int or abs(v) > 200 for v in position)
                    or tuple(position) in connues):
                raise AssertionError(f"Mur mémorisé invalide : {salle}/{position}")
            connues.add(tuple(position))
    souvenirs = m.data.get("souvenirs_visuels", {})
    if not isinstance(souvenirs, dict):
        raise AssertionError("Mémoire visuelle invalide")
    for id, souvenir in souvenirs.items():
        if not isinstance(id, str) or not isinstance(souvenir, dict):
            raise AssertionError("Souvenir visuel invalide")
        salle = souvenir.get("salle")
        pos = souvenir.get("position")
        contact = souvenir.get("contact", pos)
        if (salle not in m.data["salles"] or not isinstance(pos, list) or len(pos) != 2
                or any(type(v) is not int for v in pos)
                or not isinstance(contact, list) or len(contact) != 2
                or any(type(v) is not int for v in contact)
                or tuple(contact) not in cases(m.data["salles"][salle])
                or (tuple(pos) != tuple(contact) and
                    (tuple(pos) in cases(m.data["salles"][salle])
                     or abs(pos[0] - contact[0]) + abs(pos[1] - contact[1]) != 1
                     or pos not in m.data.get("murs_memorises", {}).get(salle, [])))
                or not isinstance(souvenir.get("nom"), str)
                or not isinstance(souvenir.get("symbole"), str)
                or len(souvenir["symbole"]) != 1):
            raise AssertionError(f"Souvenir visuel invalide : {id}")
    portes_vues = m.data.get("souvenirs_portes", {})
    if (not isinstance(portes_vues, dict)
            or any(id not in m.objets or m.objets[id].get("type") != "porte"
                   or symbole not in ("X", "+", "/", "x")
                   for id, symbole in portes_vues.items())):
        raise AssertionError("Souvenir de porte invalide")
