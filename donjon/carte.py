"""Carte ASCII à échelle commune, limitée aux salles visitées et aux objets visibles."""
from collections import defaultdict

from .francais import designer, enumerer
from .geometrie import DIRECTIONS, cases, position_entree, position_objet


SYMBOLES = {"cle": "k", "personnage": "G", "contenant": "c", "tresor": "o",
            "outil": "!", "consommable": "!", "motif": "!", "assemblage": "H", "materiau": "b"}
FLECHES = {"nord": "^", "sud": "v", "est": ">", "ouest": "<"}


def symbole_porte(porte):
    return "x" if porte["integrite"] == 0 or porte.get("detachee") else (
        "/" if porte["ouverte"] else "#" if porte["verrouillee"] else "+")


def symbole_porte_cases(porte):
    return "x" if porte["integrite"] == 0 or porte.get("detachee") else (
        "/" if porte["ouverte"] else "X" if porte["verrouillee"] else "+")


def symbole_objet_cases(objet, salle):
    """Symbole d'un objet tel qu'il était au moment où il a été vu."""
    if objet.get("bloque_vue") or objet.get("bloque_passage"):
        return "O"
    if objet["type"] == "surface" and objet.get("appui_vertical"):
        return "^" if salle == objet["appui_vertical"].get("bas") else "v"
    if "allume" in objet:
        return "*" if objet["allume"] else "t"
    return SYMBOLES.get(objet["type"], "!")


def objets_visibles_cases(monde, champ):
    """Objets effectivement dessinables, avec leur position observée."""
    from .spatial import position_cible

    salles = monde.data["salles"]
    for objet in monde.objets.values():
        salle = objet.get("lieu")
        obstacle = bool(objet.get("bloque_vue") or objet.get("bloque_passage"))
        support_vertical = objet["type"] == "surface" and bool(objet.get("appui_vertical"))
        if (salle not in salles or (objet["type"] == "surface" and not obstacle and not support_vertical)
                or objet["type"] == "porte" or objet.get("installation")):
            continue
        pos = position_cible(monde, objet["id"], salle)
        if pos is not None and (salle, pos[0], pos[1]) in champ:
            yield objet, salle, tuple(pos)


def _carte_ancienne(monde):
    salles = monde.data["salles"]
    niveau = salles[monde.joueur["salle"]].get("niveau", 0)
    connues = [id for id in salles if (id in monde.data["visitees"] or id == monde.joueur["salle"])
               and salles[id].get("niveau", 0) == niveau]
    sols = {}
    for id in connues:
        ox, oy = salles[id]["plan"]["origine"]
        sols[id] = {(ox + x, oy + y) for x, y in cases(salles[id])}
    sol = set().union(*sols.values())
    murs = {(x + dx, y + dy) for x, y in sol for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - sol
    dessin = {p: ". " for p in sol}
    for x, y in murs:
        horizontal = (x - 1, y) in murs or (x + 1, y) in murs
        vertical = (x, y - 1) in murs or (x, y + 1) in murs
        if horizontal and not vertical:
            dessin[x, y] = "--"
        elif vertical and not horizontal:
            dessin[x, y] = "| "
        else:
            dessin[x, y] = "+" + ("-" if (x + 1, y) in murs else " ")

    passages = set()
    inexplore = False
    for id in connues:
        ox, oy = salles[id]["plan"]["origine"]
        for direction, sortie in salles[id]["sorties"].items():
            x, y = sortie["case"]
            position = ox + x, oy + y
            porte = monde.objets.get(sortie["porte"])
            symbole = symbole_porte(porte) if porte else "."
            dessin[position] = symbole + ("-" if porte and direction in ("nord", "sud") else " ")
            if porte:
                passages.add(symbole)
            if sortie["vers"] not in connues:
                dx, dy = DIRECTIONS[direction]
                dessin[position[0] + dx, position[1] + dy] = FLECHES[direction] + " "
                inexplore = True

    salle = monde.joueur["salle"]
    ox, oy = salles[salle]["plan"]["origine"]
    # Les bords ne sont pas des portes : la flèche indique un dénivelé connu,
    # sans dessiner la surface voisine tant qu'elle n'a pas été visitée.
    largeur, hauteur = len(salles[salle]["plan"]["sol"][0]), len(salles[salle]["plan"]["sol"])
    for support in monde.objets.values():
        a = support.get("appui_vertical", {})
        if a.get("haut") != salle or a.get("direction") not in FLECHES:
            continue
        direction = a["direction"]
        x, y = {"nord": (largeur//2, -1), "sud": (largeur//2, hauteur),
                "est": (largeur, hauteur//2), "ouest": (-1, hauteur//2)}[direction]
        installe = any(o.get("installation", {}).get("support") == support["id"] for o in monde.objets.values())
        dessin[ox+x, oy+y] = "H " if installe else FLECHES[direction] + " "
    position = tuple(monde.joueur["position"])
    if position not in cases(salles[salle]):
        position = position_entree(monde, salle)
    joueur = ox + position[0], oy + position[1]
    objets = defaultdict(list)
    for o in monde.presents():
        if o["lieu"] != salle or o["type"] in ("surface", "porte"):
            continue
        x, y = position_objet(monde, o)
        objets[ox + x, oy + y].append(o)
    legendes = defaultdict(list)
    for position, groupe in objets.items():
        if position == joueur:
            continue
        o = groupe[0]
        if len(groupe) > 1:
            symbole = "&"
        elif "allume" in o:
            symbole = "*" if o["allume"] else "t"
        else:
            symbole = SYMBOLES.get(o["type"], "!")
        dessin[position] = symbole + " "
        legendes[symbole].extend(designer(o) for o in groupe)
    dessin[joueur] = "@ "
    pieces = []
    for id in connues:
        piece = salles[id]
        repere = piece["plan"]["repere"]
        libre = next((p for p in sorted(sols[id], key=lambda p: (p[1], p[0])) if dessin[p] == ". "), None)
        if libre:
            dessin[libre] = repere + " "
        largeur = max(x for x, y in cases(piece)) + 1
        hauteur = len(piece["plan"]["sol"])
        pieces.append(f'{repere} : {piece["nom"]} ({largeur} x {hauteur} m)')

    xmin = min(x for x, y in dessin)
    xmax = max(x for x, y in dessin)
    ymin = min(y for x, y in dessin)
    ymax = max(y for x, y in dessin)
    lignes = ["PLAN — 1 case = 1 m ; deux colonnes par case"]
    for y in range(ymin, ymax + 1):
        lignes.append("".join(dessin.get((x, y), "  ") for x in range(xmin, xmax + 1)).rstrip())
    lignes.extend(["", " | ".join(pieces), "@ toi   . sol ou passage"])
    if any(o.get("appui_vertical", {}).get("haut") == salle for o in monde.objets.values()):
        lignes.append("^ v < > bord vers un sol en contrebas ; H échelle appuyée au bord")
    if inexplore:
        lignes[-1] += "   ^ v < > suite inexplorée"
    etats = {"#": "porte verrouillée", "+": "porte fermée", "/": "porte ouverte", "x": "passage libéré"}
    if passages:
        lignes.append("   ".join(s + " " + etats[s] for s in sorted(passages)))
    if legendes:
        lignes.append("   ".join(s + " " + enumerer(noms) for s, noms in legendes.items()))
    if joueur in objets:
        lignes.append("À tes pieds (@) : " + enumerer(designer(o) for o in objets[joueur]) + ".")
    for o in monde.presents():
        if o.get("installation"):
            lignes.append("H : accès vertical par " + designer(o) + " (monter / descendre échelle).")
    return "\n".join(lignes)


def _carte_cases(monde):
    """Carte métrique fondée sur la vision courante et les cases mémorisées."""
    from .spatial import champ_visible, position_cible, sortie_visible

    salles = monde.data["salles"]
    exploration = monde.data.get("exploration", {})
    visible_brut = champ_visible(monde)
    visible = defaultdict(set)
    if isinstance(visible_brut, dict):
        visible.update({s: {tuple(p) for p in coords} for s, coords in visible_brut.items()})
    else:
        for salle, x, y in visible_brut:
            visible[salle].add((x, y))
    champ = {(s, x, y) for s, coords in visible.items() for x, y in coords}
    # Accepte le format canonique (salle -> listes de coordonnées) et l'ancien
    # dictionnaire vide pendant les premiers instants d'une nouvelle partie.
    memorisees = {}
    for salle, valeurs in exploration.items():
        if salle not in salles:
            continue
        try:
            memorisees[salle] = {tuple(p) for p in valeurs}
        except (TypeError, ValueError):
            memorisees[salle] = set()
    for salle, coords in visible.items():
        memorisees.setdefault(salle, set()).update(coords)
    memorisees.setdefault(monde.joueur["salle"], set())
    memorisees[monde.joueur["salle"]].update(visible.get(monde.joueur["salle"], set()))

    # Each level uses the same world coordinate scale. Rooms with no remembered
    # floor stay entirely absent, so their shape and contents remain unknown.
    connus = {s: coords for s, coords in memorisees.items() if coords}
    etages = defaultdict(list)
    for salle in connus:
        etages[salles[salle].get("niveau", 0)].append(salle)
    liens_installes = {}
    for support in monde.objets.values():
        appui = support.get("appui_vertical", {})
        echelle = next((o for o in monde.objets.values()
                        if o.get("installation", {}).get("support") == support["id"]
                        and o.get("integrite", 0) > 0), None)
        if appui and echelle:
            liens_installes[support["id"]] = echelle
            for salle in (appui.get("bas"), appui.get("haut")):
                if salle in salles:
                    etages[salles[salle].get("niveau", 0)].append(salle)
    if not etages:
        etages[salles[monde.joueur["salle"]].get("niveau", 0)].append(monde.joueur["salle"])

    joueur_salle = monde.joueur["salle"]
    joueur_pos = tuple(monde.joueur.get("position", ()))
    dessin_panneaux = []
    legendes = defaultdict(list)
    details_salles = []
    passages = set()
    echelles = []
    marqueurs_lien = {}
    escaliers = []
    objets_aux_pieds = []
    souvenirs_dessines = []

    for niveau in sorted(etages):
        dessin = {}
        coords_absolues = set()
        sorties_connues = []
        salles_etage = sorted(set(etages[niveau]), key=lambda s: (salles[s].get("plan", {}).get("origine", [0, 0])[1], s))
        for salle in salles_etage:
            piece = salles[salle]
            ox, oy = piece["plan"]["origine"]
            vu = visible.get(salle, set())
            connu = memorisees[salle]
            for x, y in connu:
                p = (ox + x, oy + y)
                coords_absolues.add(p)
                dessin[p] = (". " if (x, y) in vu else ": ")

            # A threshold is remembered after its inner floor is explored,
            # while its current state is shown only when the threshold is seen.
            for direction, sortie in piece["sorties"].items():
                x, y = sortie.get("case", (None, None))
                if x is None:
                    continue
                p = (ox + x, oy + y)
                dx, dy = DIRECTIONS[direction]
                interieur = (x - dx, y - dy)
                if sortie_visible(monde, salle, direction):
                    sorties_connues.append((p, salle, direction, sortie, True))
                elif interieur in connu:
                    sorties_connues.append((p, salle, direction, sortie, False))

            repere = piece.get("plan", {}).get("repere", salle[:1].upper())
            # A room tag marks only a cell already known to the player.
            libre = next((p for p in sorted(coords_absolues, key=lambda p: (p[1], p[0]))
                          if dessin.get(p) == ". " and (p[0] - ox, p[1] - oy) in connu), None)
            if libre:
                dessin[libre] = repere + " "
            largeur = max((len(row) for row in piece.get("plan", {}).get("sol", [])), default=0)
            hauteur = len(piece.get("plan", {}).get("sol", []))
            if salle in monde.data.get("visitees", []) or salle == joueur_salle:
                details_salles.append(f'{repere} : {piece["nom"]} ({largeur} x {hauteur} m)')

        # Draw only known boundary walls. Unexplored cells that are actually
        # floor remain blank; consulting their floor mask here never renders them.
        sols_connus = set(dessin)
        sols_reels_niveau = set()
        for id_salle, piece_reelle in salles.items():
            if piece_reelle.get("niveau", 0) != niveau:
                continue
            rx, ry = piece_reelle["plan"]["origine"]
            sols_reels_niveau.update((rx + x, ry + y) for x, y in cases(piece_reelle))
        murs = {(x + dx, y + dy) for x, y in sols_connus
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - sols_connus - sols_reels_niveau
        for x, y in murs:
            dessin[x, y] = "##"
        souvenirs_niveau = []
        seuils_visibles = set()
        portes_souvenues_positions = set()
        for p, source, direction, sortie, visible_sortie in sorties_connues:
            if visible_sortie:
                seuils_visibles.add(p)
            elif p in seuils_visibles:
                continue
            souvenir_porte = False
            if sortie.get("escalier") and visible_sortie:
                vers = sortie.get("vers")
                monte = salles.get(vers, {}).get("niveau", 0) > salles[source].get("niveau", 0)
                symbole = "^" if monte else "v"
                escaliers.append((symbole, vers, monte))
            elif visible_sortie:
                porte = monde.objets.get(sortie.get("porte"))
                symbole = symbole_porte_cases(porte) if porte else "."
                if porte:
                    passages.add(symbole)
            else:
                symbole = monde.data.get("souvenirs_portes", {}).get(sortie.get("porte"))
                if symbole:
                    souvenir_porte = True
                    etat = {"X": "porte verrouillée", "+": "porte fermée",
                            "/": "porte ouverte", "x": "passage libéré"}[symbole]
                    if p not in portes_souvenues_positions:
                        souvenirs_niveau.append((p, symbole, [etat]))
                        portes_souvenues_positions.add(p)
                else:
                    symbole = ":"
            dessin[p] = "~" + symbole if souvenir_porte else symbole + " "

        # A last sighting remains at its observed position until that tile is
        # seen empty again. Never infer the current location of an unseen item.
        souvenirs_positions = defaultdict(list)
        for id, souvenir in monde.data.get("souvenirs_visuels", {}).items():
            salle = souvenir["salle"]
            pos = tuple(souvenir["position"])
            if (salle not in salles_etage or pos not in memorisees.get(salle, set())
                    or pos in visible.get(salle, set()) or monde.est_porte(id)):
                continue
            ox, oy = salles[salle]["plan"]["origine"]
            souvenirs_positions[(ox + pos[0], oy + pos[1])].append(souvenir)
        for p, groupe in souvenirs_positions.items():
            symbole = "&" if len(groupe) > 1 else groupe[0]["symbole"]
            dessin[p] = "~" + symbole
            souvenirs_niveau.append((p, symbole, [souvenir["nom"] for souvenir in groupe]))

        # Current visible objects are positioned through the shared spatial API.
        # This keeps dropped or picked up items in sync with the world state.
        objets_positions = defaultdict(list)
        for objet, salle, pos in objets_visibles_cases(monde, champ):
            if salle not in salles_etage:
                continue
            if salle == joueur_salle and pos == joueur_pos:
                objets_aux_pieds.append(objet)
                continue
            ox, oy = salles[salle]["plan"]["origine"]
            p = ox + pos[0], oy + pos[1]
            objets_positions[(p, salle)].append(objet)
        for (p, salle_groupe), groupe in objets_positions.items():
            symbole = "&" if len(groupe) > 1 else symbole_objet_cases(groupe[0], salle_groupe)
            dessin[p] = symbole + " "
            legendes[symbole].extend(designer(objet) for objet in groupe)

        # Ladder endpoints only appear when the support and that endpoint are
        # known. The same link code on both panels makes a vertical route clear.
        for support in monde.objets.values():
            appui = support.get("appui_vertical", {})
            if not appui:
                continue
            if support["id"] not in liens_installes:
                continue
            for salle in (appui.get("bas"), appui.get("haut")):
                if salle not in salles_etage:
                    continue
                endpoint = position_cible(monde, support["id"], salle)
                if endpoint is None:
                    continue
                endpoint = tuple(endpoint)
                if memorisees.get(salle) and endpoint not in memorisees[salle]:
                    continue
                code = marqueurs_lien.setdefault(support["id"], f"H{len(marqueurs_lien) + 1}")
                ox, oy = salles[salle]["plan"]["origine"]
                dessin[ox + endpoint[0], oy + endpoint[1]] = code
                echelles.append((code, salle, support["id"]))

        if joueur_salle in salles_etage:
            ox, oy = salles[joueur_salle]["plan"]["origine"]
            dessin[ox + joueur_pos[0], oy + joueur_pos[1]] = "@ "

        souvenirs_dessines.extend((symbole, noms) for p, symbole, noms in souvenirs_niveau
                                  if dessin.get(p) == "~" + symbole)

        if dessin:
            xmin = min(x for x, _ in dessin)
            xmax = max(x for x, _ in dessin)
            ymin = min(y for _, y in dessin)
            ymax = max(y for _, y in dessin)
            lignes = [f"NIVEAU {niveau:+g} — coordonnées (x, y), 1 case = 1 m",
                      "     " + "".join(f"{x:2d}" if x % 5 == 0 else "  " for x in range(xmin, xmax + 1))]
            lignes.extend(f"{y:>4} " + "".join(dessin.get((x, y), "  ") for x in range(xmin, xmax + 1)).rstrip()
                          for y in range(ymin, ymax + 1))
            dessin_panneaux.append("\n".join(lignes))

    lignes = ["PLAN — 1 case = 1 m", *dessin_panneaux]
    legende = [" | ".join(dict.fromkeys(details_salles)),
               "@ toi   ## mur   . terrain visible   : terrain mémorisé ou passage connu   cases vides : inconnues",
               "F6 puis flèches : marcher · Échap/Entrée : commande · Ctrl+flèches actifs",
               "O obstacle solide   ^/v appui vertical   H1 échelle · axes x,y ; une case par pas"]
    if passages:
        etats = {"X": "porte verrouillée", "+": "porte fermée", "/": "porte ouverte", "x": "passage libéré"}
        legende.append("   ".join(s + " " + etats[s] for s in sorted(passages)))
    if legendes:
        legende.append("   ".join(s + " " + enumerer(noms) for s, noms in legendes.items()))
    if souvenirs_dessines:
        legende.append("~ : dernier aperçu, présence ou état actuels non confirmés")
        legende.append("   ".join("~" + s + " " + enumerer(noms)
                                   for s, noms in souvenirs_dessines))
    for symbole, destination, monte in dict.fromkeys(escaliers):
        phrase = "escalier montant" if monte else "escalier descendant"
        if memorisees.get(destination):
            phrase += " vers " + salles[destination]["nom"]
        legende.append(f"{symbole} {phrase}")
    if objets_aux_pieds:
        legende.append("À tes pieds (@) : " + enumerer(designer(o) for o in objets_aux_pieds) + ".")
    for code, salle, support_id in dict.fromkeys(echelles):
        if salle in monde.data.get("visitees", []) or salle == joueur_salle:
            legende.append(f"{code} : liaison verticale par {designer(liens_installes[support_id])} à {salles[salle]['nom']}.")
    return "\n".join(lignes) + "\n\n=== LEGENDE ===\n" + "\n".join(legende)


def carte(monde):
    try:
        from .spatial import active
        if active(monde):
            return _carte_cases(monde)
    except ImportError:
        pass
    return _carte_ancienne(monde)
