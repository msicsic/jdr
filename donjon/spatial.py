"""Moteur spatial déterministe en cases, indépendant du récit et de l'interface.

Les coordonnées d'objet sont locales à une salle. Les coordonnées de sortie
restent celles du plan (une case hors du sol) ; franchir une sortie prend un pas
et place le personnage sur la case intérieure de la salle voisine.
"""
from __future__ import annotations

from collections import deque
from contextlib import contextmanager

from .geometrie import cases, position_entree, position_objet, placer


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
    """L'orientation d'un PNJ ; le joueur voit encore tout autour de lui (étape 4 du jalon)."""
    if acteur == "joueur":
        return None
    return m.objets[acteur].get("orientation")


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
            sol = cases(m.data["salles"][o["lieu"]])
            centre = (round(sum(x for x, _ in sol) / len(sol)), round(sum(y for _, y in sol) / len(sol)))
            o["orientation"] = orientation_vers(tuple(o["position"]), centre) or "sud"
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


def _bloque(m, salle, position, vue=False, sauf=None):
    for id, o in m.objets.items():
        if id == sauf or o.get("incorpore"):
            continue
        if o.get("lieu") != salle:
            continue
        if (o.get("bloque_vue") if vue else o.get("bloque_passage")):
            if position_cible(m, id, salle) == position:
                return True
    return False


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
    return _niveau(m, a) == _niveau(m, b)


def _niveau(m, salle):
    piece = m.data["salles"][salle]
    if "altitude_cm" in piece:
        return piece["altitude_cm"]
    return piece.get("niveau", 0) * 240


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
                    or not _meme_niveau(m, salle, vers)):
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
    points = _ligne(a, b)
    for i, p in enumerate(points[1:], 1):
        if p not in terrain:
            return False
        if i < len(points) - 1 and p in opaques:
            return False
        avant = points[i - 1]
        if p[0] != avant[0] and p[1] != avant[1]:
            c1, c2 = (p[0], avant[1]), (avant[0], p[1])
            if ((c1 not in terrain or c1 in opaques)
                    and (c2 not in terrain or c2 in opaques)):
                return False
    return True


def _los_mutuelle(m, a, b, terrain, opaques):
    """Vue symétrique : Bresenham diffère selon le sens, on exige les deux tracés libres."""
    return _los_global(m, a, b, terrain, opaques) and _los_global(m, b, a, terrain, opaques)


def visible(m, id, acteur="joueur", champ=None):
    if id not in m.objets or id == acteur:
        return False
    champ = champ_visible(m, acteur) if champ is None else champ
    for salle in m.data["salles"]:
        position = position_cible(m, id, salle)
        if position is not None and (salle, position[0], position[1]) in champ:
            ancrage = m.objets[id].get("ancrage_carte")
            if ancrage and tuple(ancrage) not in murs_visibles(m, champ, acteur).get(salle, set()):
                continue
            return True
    return False


def eclairage_niveau(m):
    from .perception import eclairage
    return eclairage(m)["niveau"]


# Distance de vue d'une case, si rien ne s'interpose : 8 si elle reçoit une lumière directe
# ou la pleine lumière du jour, 3 si elle n'est que dans la pénombre diffuse de la pièce.
PORTEE_VUE = {1: 3, 2: 8}


def signature_vue(m):
    """Tout ce dont dépendent la lumière et les lignes de vue, hors géométrie des salles : portes
    et contenants ouverts, sources allumées et la case d'où elles éclairent, objets qui bloquent
    la vue. Deux états de même signature se voient de la même façon."""
    from .perception import allumee, salle_source
    cle = []
    for id, o in m.objets.items():
        if o["type"] in ("porte", "contenant"):
            cle.append((id, bool(o.get("ouverte"))))
        if allumee(o):
            source = salle_source(m, o)
            cle.append((id, source, position_cible(m, id, source) if source else None, o.get("luminosite")))
        if o.get("bloque_vue"):
            cle.append((id, o.get("lieu"), tuple(o.get("position") or ()), bool(o.get("incorpore"))))
    return tuple(cle)


@contextmanager
def vue_memorisee(m):
    """Pendant la vie des PNJ, la géométrie ne change pas : cartes de lumière et champs de vision
    sont gardés tant que la signature de la vue ne change pas. Hors de ce bloc, tout est recalculé."""
    ancien = getattr(m, "_cache_vue", None)
    m._cache_vue = {} if ancien is None else ancien
    try:
        yield
    finally:
        if ancien is None:
            del m._cache_vue


def _vue(m, acteur="joueur", signature=None):
    """Origine globale du regard d'un acteur, terrain et carte de lumière des salles reliées."""
    from .perception import CarteLumiere
    salle, position = position_acteur(m, acteur)
    cache = getattr(m, "_cache_vue", None)
    if cache is None:
        lumiere = CarteLumiere(m, salle)
    else:
        cle = ("lumiere", salle, signature or signature_vue(m))
        if cle not in cache:
            cache[cle] = CarteLumiere(m, salle)
        lumiere = cache[cle]
    origine = _global(m.data["salles"][salle], position)
    return origine, lumiere


def _vu(m, origine, lumiere, cible, orientation=None):
    if not dans_le_cone(origine, orientation, cible):
        return False
    niveau = lumiere.niveau(cible)
    portee = PORTEE_VUE[2 if niveau == 2 or lumiere.directe(cible) else 1] if niveau else -1
    if max(abs(cible[0] - origine[0]), abs(cible[1] - origine[1])) > portee:
        return False
    return _los_mutuelle(m, origine, cible, lumiere.terrain, lumiere.opaques)


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
    if max(abs(cible[0] - origine[0]), abs(cible[1] - origine[1])) > PORTEE_VUE[2]:
        return False
    if not dans_le_cone(origine, orientation_acteur(m, acteur), cible):
        return False
    return _los_mutuelle(m, origine, cible, lumiere.terrain, lumiere.opaques)


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


def champ_visible(m, acteur="joueur"):
    """Cases vues maintenant par l'acteur, incluant les paliers d'une porte ouverte."""
    cache = getattr(m, "_cache_vue", None)
    signature = cle = None
    orientation = orientation_acteur(m, acteur)
    if cache is not None:
        signature = signature_vue(m)
        cle = ("champ", *position_acteur(m, acteur), orientation, signature)
        if cle in cache:
            return set(cache[cle])
    origine, lumiere = _vue(m, acteur, signature)
    vus = set()
    for salle in lumiere.salles:
        piece = m.data["salles"][salle]
        for x, y in cases(piece):
            if _vu(m, origine, lumiere, _global(piece, (x, y)), orientation):
                vus.add((salle, x, y))
    if cache is not None:
        cache[cle] = frozenset(vus)
    return vus


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
            if (cible in terrain or
                    max(abs(cible[0] - origine[0]), abs(cible[1] - origine[1])) > rayon):
                continue
            terrain[cible] = None
            visible = _los_global(m, origine, cible, terrain, opaques)
            del terrain[cible]
            if visible:
                vus.setdefault(salle, set()).add((x + dx, y + dy))
    return vus


def memoriser(m):
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
    return {"salle": pas["salle"], "position": pas["position"]}


def pas_vers(m, salle, position, vecteur, porte_fermee=False, case_libre=None):
    """Où mène un pas d'une case depuis (salle, position), pour le joueur comme pour un PNJ :
    {"salle", "position", "porte"}. ``porte`` est la porte fermée à franchir, si
    ``porte_fermee`` l'admet ; sinon une porte fermée bloque, comme un mur ou un obstacle.
    ``case_libre`` remplace ``_case_libre`` par une version mémorisée le temps d'une recherche."""
    _case_libre_ = case_libre or (lambda s, c: _case_libre(m, s, c))
    dx, dy = vecteur
    x, y = position
    destination = (x + dx, y + dy)
    if destination in cases(m.data["salles"][salle]):
        if dx and dy and not (_case_libre_(salle, (x + dx, y))
                              and _case_libre_(salle, (x, y + dy))):
            _erreur("Un mur ou un obstacle bloque le passage en diagonale.")
        if not _case_libre_(salle, destination):
            _erreur("Un obstacle solide occupe cette case.")
        return {"salle": salle, "position": [destination[0], destination[1]], "porte": None}
    if dx and dy:
        _erreur("Le mur bloque ce déplacement en diagonale.")
    sortie = next((s for d, s in m.data["salles"][salle].get("sorties", {}).items()
                   if VECTEURS.get(d) == (dx, dy)
                   and _case_interieure(m, salle, s) == (x, y)), None)
    if not sortie:
        _erreur("Un mur bloque le passage.")
    porte = m.objets.get(sortie.get("porte"))
    fermee = bool(porte and not porte.get("ouverte"))
    if fermee and not porte_fermee:
        _erreur("La porte fermée bloque le passage.")
    vers = sortie.get("vers")
    piece_vers = m.data["salles"].get(vers, {})
    retour = next((s for s in piece_vers.get("sorties", {}).values()
                   if s.get("vers") == salle and s.get("porte") == sortie.get("porte")), None)
    pos = _case_interieure(m, vers, retour) if retour else None
    if pos is None:
        _erreur("Aucun sol ne rejoint ce passage.")
    if not _case_libre_(vers, pos):
        _erreur("Un obstacle solide bloque l'autre côté du passage.")
    return {"salle": vers, "position": [pos[0], pos[1]], "porte": porte["id"] if fermee else None}


def trajet(m, salle, position, arrivee, franchissable=lambda porte: True, libre=lambda salle, case: True):
    """Le plus court chemin en cases, d'un pas à la fois, vers une case où ``arrivee(salle, case)`` :
    [(salle, case, porte fermée à franchir ou None, sens du pas)], vide si l'on y est déjà, None
    sans passage.
    Une porte fermée se franchit si ``franchissable(porte)`` ; ``libre`` écarte les cases occupées."""
    from .monde import ErreurMonde
    libres = {}

    def case_libre(s, c):
        if (s, c) not in libres:
            libres[s, c] = _case_libre(m, s, c)
        return libres[s, c]
    depart = (salle, tuple(position))
    if arrivee(*depart):
        return []
    precedent, file = {depart: None}, deque([depart])
    while file:
        courant = file.popleft()
        for vecteur in sorted(VECTEURS.values()):
            try:
                pas = pas_vers(m, courant[0], courant[1], vecteur, porte_fermee=True, case_libre=case_libre)
            except ErreurMonde:
                continue
            suivant = (pas["salle"], tuple(pas["position"]))
            if suivant in precedent or not libre(*suivant) or pas["porte"] and not franchissable(pas["porte"]):
                continue
            precedent[suivant] = (courant, pas["porte"], vecteur)
            if arrivee(*suivant):
                chemin = []
                while precedent[suivant]:
                    avant, porte, sens = precedent[suivant]
                    chemin.append((suivant[0], suivant[1], porte, sens))
                    suivant = avant
                return chemin[::-1]
            file.append(suivant)
    return None


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
    for o in m.objets.values():
        if "orientation" in o and o["orientation"] not in VECTEURS:
            raise AssertionError(f"Orientation invalide : {o['id']}")
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
            if _niveau(m, a) != _niveau(m, b):
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
            if not (sortie.get("escalier") and _niveau(m, salle) != _niveau(m, vers)):
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
