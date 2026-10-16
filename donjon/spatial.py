"""Moteur spatial déterministe en cases, indépendant du récit et de l'interface.

Les coordonnées d'objet sont locales à une salle. Les coordonnées de sortie
restent celles du plan (une case hors du sol) ; franchir une sortie prend un pas
et place le personnage sur la case intérieure de la salle voisine.
"""
from __future__ import annotations

from collections import deque

from .geometrie import cases, position_entree, position_objet, placer


VECTEURS = {
    "nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0),
    "nord-est": (1, -1), "nord-ouest": (-1, -1),
    "sud-est": (1, 1), "sud-ouest": (-1, 1),
    "ne": (1, -1), "no": (-1, -1), "se": (1, 1), "so": (-1, 1),
}


def active(m):
    return bool(m.data.get("mode_cases", False))


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


def proche(m, id):
    if id not in m.objets:
        return False
    o = m.objets[id]
    if o.get("lieu") == "joueur" or m.est_porte(id):
        return True
    cible = position_cible(m, id)
    if cible is None:
        return False
    x, y = m.joueur["position"]
    dx, dy = cible[0] - x, cible[1] - y
    if max(abs(dx), abs(dy)) > 1:
        return False
    if not (dx and dy):
        return True
    salle = m.joueur["salle"]
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


def visible(m, id):
    if id not in m.objets:
        return False
    if eclairage_niveau(m) <= 0:
        return False
    champ = champ_visible(m)
    for salle in m.data["salles"]:
        position = position_cible(m, id, salle)
        if position is not None and (salle, position[0], position[1]) in champ:
            ancrage = m.objets[id].get("ancrage_carte")
            if ancrage and tuple(ancrage) not in murs_visibles(m, champ).get(salle, set()):
                continue
            return True
    return False


def eclairage_niveau(m):
    from .perception import eclairage
    return eclairage(m)["niveau"]


def rayon_vision(m):
    niveau = eclairage_niveau(m)
    return 3 if niveau == 1 else 8 if niveau >= 2 else 0


def sortie_visible(m, salle, direction):
    """Retourne si le seuil est visible, même si une porte le ferme."""
    sortie = m.data["salles"].get(salle, {}).get("sorties", {}).get(direction)
    if not sortie or len(sortie.get("case", ())) != 2 or eclairage_niveau(m) <= 0:
        return False
    salles = _salles_relies(m, m.joueur["salle"])
    if salle not in salles:
        return False
    terrain, opaques = _globales(m, salles)
    ox, oy = m.data["salles"][salle]["plan"]["origine"]
    cible = ox + sortie["case"][0], oy + sortie["case"][1]
    terrain.setdefault(cible, None)
    origine_piece = m.data["salles"][m.joueur["salle"]]
    sx, sy = origine_piece["plan"]["origine"]
    x, y = m.joueur["position"]
    origine = sx + x, sy + y
    return (max(abs(cible[0] - origine[0]), abs(cible[1] - origine[1])) <= rayon_vision(m)
            and _los_global(m, origine, cible, terrain, opaques))


def champ_visible(m):
    """Ensemble des cases vues maintenant, incluant les paliers d'une porte ouverte."""
    niveau = eclairage_niveau(m)
    if niveau <= 0:
        return set()
    rayon = rayon_vision(m)
    origine = tuple(m.joueur["position"])
    salle_origine = m.joueur["salle"]
    salles = _salles_relies(m, salle_origine)
    terrain, opaques = _globales(m, salles)
    piece = m.data["salles"][salle_origine]
    ox, oy = piece["plan"]["origine"]
    centre_global = (ox + origine[0], oy + origine[1])
    vus = set()
    for salle in salles:
        p = m.data["salles"][salle]["plan"]
        sx, sy = p["origine"]
        from .perception import eclairage
        niveau_piece = eclairage(m, salle)["niveau"]
        rayon_piece = 3 if niveau_piece == 1 else 8 if niveau_piece >= 2 else 0
        if rayon_piece == 0:
            continue
        for x, y in cases(m.data["salles"][salle]):
            cible = sx + x, sy + y
            if (max(abs(cible[0] - centre_global[0]), abs(cible[1] - centre_global[1])) <= min(rayon, rayon_piece)
                    and _los_global(m, centre_global, cible, terrain, opaques)):
                vus.add((salle, x, y))
    return vus


def murs_visibles(m, champ=None):
    """Murs vus depuis la position actuelle, sans déduire les contours du plan caché."""
    champ = champ_visible(m) if champ is None else champ
    if not champ:
        return {}
    salles = _salles_relies(m, m.joueur["salle"])
    terrain, opaques = _globales(m, salles)
    origine = _global(m.data["salles"][m.joueur["salle"]], m.joueur["position"])
    rayon = rayon_vision(m)
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
        "symbole": symbole_objet_cases(objet, salle), "nom": designer(objet),
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
    salle = m.joueur["salle"]
    x, y = m.joueur["position"]
    destination = (x + dx, y + dy)
    if destination in cases(m.data["salles"][salle]):
        if dx and dy and not (_case_libre(m, salle, (x + dx, y))
                              and _case_libre(m, salle, (x, y + dy))):
            _erreur("Un mur ou un obstacle bloque le passage en diagonale.")
        if not _case_libre(m, salle, destination):
            _erreur("Un obstacle solide occupe cette case.")
        return {"salle": salle, "position": [destination[0], destination[1]]}
    if dx and dy:
        _erreur("Le mur bloque ce déplacement en diagonale.")
    sortie = next((s for d, s in m.data["salles"][salle].get("sorties", {}).items()
                   if VECTEURS.get(d) == (dx, dy)
                   and _case_interieure(m, salle, s) == (x, y)), None)
    if not sortie:
        _erreur("Un mur bloque le passage.")
    porte = m.objets.get(sortie.get("porte"))
    if porte and not porte.get("ouverte"):
        _erreur("La porte fermée bloque le passage.")
    vers = sortie.get("vers")
    piece_vers = m.data["salles"].get(vers, {})
    retour = next((s for s in piece_vers.get("sorties", {}).values()
                   if s.get("vers") == salle and s.get("porte") == sortie.get("porte")), None)
    pos = _case_interieure(m, vers, retour) if retour else None
    if pos is None:
        _erreur("Aucun sol ne rejoint ce passage.")
    if not _case_libre(m, vers, pos):
        _erreur("Un obstacle solide bloque l'autre côté du passage.")
    return {"salle": vers, "position": [pos[0], pos[1]]}


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
