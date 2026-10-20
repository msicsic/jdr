"""Carte ASCII à échelle commune, limitée aux salles visitées et aux objets visibles."""
from collections import defaultdict

from .francais import designer, enumerer
from .geometrie import DIRECTIONS, cases, position_entree, position_objet


SYMBOLES = {"cle": "k", "personnage": "G", "contenant": "c", "tresor": "o",
            "outil": "!", "consommable": "!", "motif": "!", "assemblage": "H", "materiau": "b"}
FLECHES = {"nord": "^", "sud": "v", "est": ">", "ouest": "<"}
# La direction du regard du joueur, accolée à son @.
REGARD = {"nord": "↑", "sud": "↓", "est": "→", "ouest": "←",
          "nord-est": "↗", "sud-est": "↘", "sud-ouest": "↙", "nord-ouest": "↖"}


def symbole_porte(porte):
    return "x" if porte["integrite"] == 0 or porte.get("detachee") else (
        "/" if porte["ouverte"] else "#" if porte["verrouillee"] else "+")


def symbole_porte_cases(porte):
    return "x" if porte["integrite"] == 0 or porte.get("detachee") else (
        "/" if porte["ouverte"] else "X" if porte["verrouillee"] else "+")


RESERVES = set("OHX")  # obstacle, échelle, porte verrouillée


def symbole_personnage(monde, objet):
    """Initiale du personnage, distincte des repères de salles et des autres personnages.

    L'attribution parcourt les personnages dans un ordre fixe : un même personnage garde la
    même lettre d'un affichage à l'autre, souvenirs compris."""
    import unicodedata
    pris = RESERVES | {s.get("plan", {}).get("repere", id[:1].upper()) for id, s in monde.data["salles"].items()}
    attribues = {}
    for id in sorted(i for i, o in monde.objets.items() if o["type"] == "personnage"):
        nom = unicodedata.normalize("NFD", monde.objets[id]["nom"])
        lettres = [c.upper() for c in nom if c.isascii() and c.isalpha()]
        attribues[id] = next((c for c in lettres if c not in pris and c not in attribues.values()), "G")
    return attribues.get(objet["id"], "G")


def symbole_objet_cases(objet, salle, monde=None):
    """Symbole d'un objet tel qu'il était au moment où il a été vu."""
    if objet["type"] == "personnage" and monde is not None:
        return symbole_personnage(monde, objet)
    if objet.get("bloque_vue") or objet.get("bloque_passage"):
        return "O"
    if objet["type"] == "surface" and objet.get("appui_vertical"):
        return "^" if salle == objet["appui_vertical"].get("bas") else "v"
    if "allume" in objet:
        return "*" if objet["allume"] else "t"
    return SYMBOLES.get(objet["type"], "!")


def objets_visibles_cases(monde, champ):
    """Objets effectivement dessinables, avec leur position observée."""
    from .spatial import position_cible, position_carte

    salles = monde.data["salles"]
    for objet in monde.objets.values():
        salle = objet.get("lieu")
        if salle not in salles and objet.get("cartographier") and not monde.est_porte(objet["id"]):
            for salle_vue in salles:
                contact = position_cible(monde, objet["id"], salle_vue)
                if (contact is not None and monde.visible(objet["id"])
                        and (salle_vue, contact[0], contact[1]) in champ):
                    yield objet, salle_vue, tuple(position_carte(monde, objet["id"], salle_vue))
                    break
            continue
        obstacle = bool(objet.get("bloque_vue") or objet.get("bloque_passage"))
        support_vertical = objet["type"] == "surface" and bool(objet.get("appui_vertical"))
        if (salle not in salles or (objet["type"] == "surface" and not obstacle and not support_vertical)
                or objet["type"] == "porte" or objet.get("installation")):
            continue
        contact = position_cible(monde, objet["id"], salle)
        if (contact is not None and (salle, contact[0], contact[1]) in champ
                and monde.visible(objet["id"])):
            yield objet, salle, tuple(position_carte(monde, objet["id"], salle))


def _carte_ancienne(monde):
    from .spatial import position_carte
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
        x, y = position_carte(monde, o["id"], salle)
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
        dessin[position] = symbole + ("#" if any(o.get("ancrage_carte") for o in groupe) else " ")
        legendes[symbole].extend(designer(o) for o in groupe)
    dessin[joueur] = "@" + REGARD.get(monde.joueur.get("orientation"), " ")
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


ETATS_SOUVENIR_PORTE = {"X": "porte verrouillée", "+": "porte fermée", "/": "porte ouverte", "x": "passage libéré"}


def _carte_cases(monde):
    """Carte métrique : la scène perçue (``scene.scene_percue``) rendue en deux caractères par case."""
    from .scene import scene_percue
    scene = scene_percue(monde)
    joueur = scene["joueur"]
    dessin_panneaux, legendes, details_salles = [], defaultdict(list), []
    passages, echelles, escaliers, objets_aux_pieds, souvenirs_dessines = set(), [], [], [], []
    penombre_vue = False
    for niveau in scene["niveaux"]:
        dessin, coords_absolues = {}, set()
        for piece in niveau["salles"]:
            ox, oy = piece["origine"]
            connu = set()
            for c in piece["cases"]:
                p = tuple(c["globale"])
                connu.add(tuple(c["case"]))
                coords_absolues.add(p)
                penombre_vue = penombre_vue or c["etat"] == "penombre"
                dessin[p] = {"eclaire": ". ", "penombre": ", ", "memorise": ": "}[c["etat"]]
            # Le repère d'une salle ne marque qu'une case déjà vue.
            libre = next((p for p in sorted(coords_absolues, key=lambda p: (p[1], p[0]))
                          if dessin.get(p) in (". ", ", ") and (p[0] - ox, p[1] - oy) in connu), None)
            if libre:
                dessin[libre] = piece["repere"] + " "
            if piece["connue"]:
                largeur, hauteur = piece["dimensions"]
                details_salles.append(f'{piece["repere"]} : {piece["nom"]}'
                                      + (f" ({largeur} x {hauteur} m)" if piece["entiere"] else ""))
        for mur in niveau["murs"]:
            dessin.setdefault(tuple(mur["globale"]), "##")
        souvenirs_niveau, seuils_visibles, portes_souvenues = [], set(), set()
        for s in niveau["sorties"]:
            p = tuple(s["globale"])
            if s["visible"]:
                seuils_visibles.add(p)
            elif p in seuils_visibles:
                continue
            porte = s.get("porte")
            if "escalier" in s:
                symbole = "^" if s["escalier"] == "monte" else "v"
                escaliers.append((symbole, s["vers"], s["escalier"] == "monte", s["vers_nom"]))
                dessin[p] = symbole + " "
            elif porte and porte.get("souvenir"):
                if p not in portes_souvenues:
                    souvenirs_niveau.append((p, porte["symbole"], False, [ETATS_SOUVENIR_PORTE[porte["symbole"]]]))
                    portes_souvenues.add(p)
                dessin[p] = "~" + porte["symbole"]
            elif s["visible"]:
                if porte:
                    passages.add(porte["symbole"])
                dessin[p] = (porte["symbole"] if porte else ".") + " "
            else:
                dessin[p] = ": "
        groupes = defaultdict(list)
        for souvenir in niveau["souvenirs"]:
            groupes[tuple(souvenir["globale"])].append(souvenir)
        for p, groupe in groupes.items():
            symbole = "&" if len(groupe) > 1 else groupe[0]["symbole"]
            ancre_mur = any(s["ancre_mur"] for s in groupe)
            dessin[p] = symbole + "~" if ancre_mur else "~" + symbole
            souvenirs_niveau.append((p, symbole, ancre_mur, [s["nom"] for s in groupe]))
        groupes = defaultdict(list)
        for o in niveau["objets"]:
            if o["aux_pieds"]:
                objets_aux_pieds.append(o["nom"])
                continue
            groupes[(tuple(o["globale"]), o["salle"])].append(o)
        for (p, _), groupe in groupes.items():
            symbole = "&" if len(groupe) > 1 else groupe[0]["symbole"]
            dessin[p] = symbole + ("#" if any(o["ancre_mur"] for o in groupe) else " ")
            legendes[symbole].extend(o["nom"] for o in groupe)
        for e in niveau["echelles"]:
            dessin[tuple(e["globale"])] = e["code"]
            echelles.append((e["code"], e["salle"], e["nom"]))
        if joueur["salle"] in {piece["id"] for piece in niveau["salles"]} and "globale" in joueur:
            dessin[tuple(joueur["globale"])] = "@" + REGARD.get(joueur["orientation"], " ")
        souvenirs_dessines.extend((symbole, noms) for p, symbole, mur, noms in souvenirs_niveau
                                  if dessin.get(p) == (symbole + "~" if mur else "~" + symbole))
        if dessin:
            xmin = min(x for x, _ in dessin)
            xmax = max(x for x, _ in dessin)
            ymin = min(y for _, y in dessin)
            ymax = max(y for _, y in dessin)
            lignes = [f"NIVEAU {niveau['niveau']:+g} — coordonnées (x, y), 1 case = 1 m",
                      "     " + "".join(f"{x:2d}" if x % 5 == 0 else "  " for x in range(xmin, xmax + 1))]
            lignes.extend(f"{y:>4} " + "".join(dessin.get((x, y), "  ") for x in range(xmin, xmax + 1)).rstrip()
                          for y in range(ymin, ymax + 1))
            dessin_panneaux.append("\n".join(lignes))
    lignes = ["PLAN — 1 case = 1 m", *dessin_panneaux]
    legende = [" | ".join(dict.fromkeys(details_salles)),
               "@ toi   ## mur   . terrain visible et éclairé" + ("   , terrain visible dans la pénombre (vue courte)"
                                                                  if penombre_vue else "")
               + "   : terrain mémorisé ou passage connu   cases vides : inconnues",
               "La flèche à côté de @ : ton regard. Tu vois devant toi (120°) et à tes côtés, pas derrière.",
               "F6 puis flèches : marcher · Maj+flèches : pas chassé · Alt+flèches : pas feutré · Échap/Entrée : commande",
               "O obstacle solide   ^/v appui vertical   H1 échelle · axes x,y ; une case par pas"]
    if passages:
        legende.append("   ".join(s + " " + ETATS_SOUVENIR_PORTE[s] for s in sorted(passages)))
    if legendes:
        legende.append("   ".join(s + " " + enumerer(noms) for s, noms in legendes.items()))
    if souvenirs_dessines:
        legende.append("~ : dernier aperçu, présence ou état actuels non confirmés")
        legende.append("   ".join("~" + s + " " + enumerer(noms) for s, noms in souvenirs_dessines))
    for symbole, _, monte, vers_nom in dict.fromkeys(escaliers):
        legende.append(f"{symbole} " + ("escalier montant" if monte else "escalier descendant")
                       + (" vers " + vers_nom if vers_nom else ""))
    if objets_aux_pieds:
        legende.append("À tes pieds (@) : " + enumerer(objets_aux_pieds) + ".")
    salles = monde.data["salles"]
    for code, salle, nom in dict.fromkeys(echelles):
        if salle in monde.data.get("visitees", []) or salle == joueur["salle"]:
            legende.append(f"{code} : liaison verticale par {nom} à {salles[salle]['nom']}.")
    return "\n".join(lignes) + "\n\n=== LEGENDE ===\n" + "\n".join(legende)


def carte(monde):
    try:
        from .spatial import active
        if active(monde):
            return _carte_cases(monde)
    except ImportError:
        pass
    return _carte_ancienne(monde)
