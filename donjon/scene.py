"""La scène perçue par le joueur : ce qu'il voit maintenant et ce dont il se souvient, structuré.

Une seule source pour ce que perçoit le joueur : la carte du terminal (``carte.py``) en est un
rendu en caractères, la page du navigateur un autre. Rien de ce qu'il ne perçoit pas n'y entre :
les cases sont celles qu'il voit (éclairées ou dans la pénombre) ou qu'il a déjà vues ; les objets
et personnages, ceux qu'il voit, chacun avec son identifiant ; les souvenirs, ce qu'il a aperçu et
qui n'est plus sous ses yeux, à l'endroit où il l'a vu.

Les coordonnées ``case`` sont locales à une salle ; ``globale`` est dans le repère commun des
salles d'un même niveau.
"""
from collections import defaultdict

from .francais import designer
from .geometrie import DIRECTIONS, cases

ETATS_PORTE = {"X": "verrouillee", "+": "fermee", "/": "ouverte", "x": "liberee"}


def _visible_par_salle(monde):
    from .spatial import champ_visible
    brut = champ_visible(monde)
    visible = defaultdict(set)
    if isinstance(brut, dict):
        visible.update({s: {tuple(p) for p in coords} for s, coords in brut.items()})
    else:
        for salle, x, y in brut:
            visible[salle].add((x, y))
    return visible


def _memorisees(monde, visible):
    """Cases connues par salle : mémorisées (accepte les anciens formats) et vues maintenant."""
    salles = monde.data["salles"]
    memorisees = {}
    for salle, valeurs in monde.data.get("exploration", {}).items():
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
    return memorisees


def _etages(monde, memorisees):
    """Salles à montrer par niveau : celles dont une case est connue, celle du joueur même dans le
    noir, et les deux bouts d'une échelle installée ; plus les échelles installées par support."""
    salles = monde.data["salles"]
    etages = defaultdict(list)
    for salle, coords in memorisees.items():
        if coords:
            etages[salles[salle].get("niveau", 0)].append(salle)
    etages[salles[monde.joueur["salle"]].get("niveau", 0)].append(monde.joueur["salle"])
    liens = {}
    for support in monde.objets.values():
        appui = support.get("appui_vertical", {})
        echelle = next((o for o in monde.objets.values()
                        if o.get("installation", {}).get("support") == support["id"] and o.get("integrite", 0) > 0), None)
        if appui and echelle:
            liens[support["id"]] = echelle
            for salle in (appui.get("bas"), appui.get("haut")):
                if salle in salles:
                    etages[salles[salle].get("niveau", 0)].append(salle)
    return etages, liens


def _portes(monde, porte):
    from .carte import symbole_porte_cases
    symbole = symbole_porte_cases(porte)
    return {"id": porte["id"], "nom": designer(porte), "etat": ETATS_PORTE[symbole], "symbole": symbole}


def scene_percue(monde):
    """La scène du joueur, niveau par niveau (voir le module)."""
    from .carte import objets_visibles_cases, symbole_objet_cases, symbole_personnage
    from .perception import CarteLumiere
    from .spatial import murs_visibles, position_cible, porte_par, sortie_visible

    salles = monde.data["salles"]
    visible = _visible_par_salle(monde)
    champ = {(s, x, y) for s, coords in visible.items() for x, y in coords}
    memorisees = _memorisees(monde, visible)
    etages, liens = _etages(monde, memorisees)
    joueur_salle = monde.joueur["salle"]
    joueur_pos = tuple(monde.joueur.get("position", ()))
    lumiere = CarteLumiere(monde, joueur_salle)
    murs_connus = {s: {tuple(p) for p in coords}
                   for s, coords in monde.data.get("murs_memorises", {}).items() if s in salles}
    for salle, positions in murs_visibles(monde, champ).items():
        murs_connus.setdefault(salle, set()).update(positions)
    objets_visibles = list(objets_visibles_cases(monde, champ))
    codes_echelles = {}
    niveaux = []
    for niveau in sorted(etages):
        ordre = sorted(set(etages[niveau]), key=lambda s: (salles[s].get("plan", {}).get("origine", [0, 0])[1], s))
        pieces, murs, sorties, souvenirs, objets, echelles = [], [], [], [], [], []
        for salle in ordre:
            piece = salles[salle]
            ox, oy = piece["plan"]["origine"]
            vu, connu = visible.get(salle, set()), memorisees[salle]
            cases_connues = []
            for x, y in connu:
                g = (ox + x, oy + y)
                if (x, y) in vu:
                    etat = "eclaire" if lumiere.niveau(g) == 2 or lumiere.directe(g) else "penombre"
                else:
                    etat = "memorise"
                cases_connues.append({"case": [x, y], "globale": list(g), "etat": etat})
            largeur = max((len(r) for r in piece.get("plan", {}).get("sol", [])), default=0)
            hauteur = len(piece.get("plan", {}).get("sol", []))
            pieces.append({"id": salle, "nom": piece["nom"], "repere": piece.get("plan", {}).get("repere", salle[:1].upper()),
                           "origine": [ox, oy], "connue": salle in monde.data.get("visitees", []) or salle == joueur_salle,
                           "entiere": cases(piece).issubset(connu), "dimensions": [largeur, hauteur],
                           "cases": cases_connues})
            for x, y in murs_connus.get(salle, set()):
                murs.append({"salle": salle, "case": [x, y], "globale": [ox + x, oy + y]})
            # Un seuil se connaît une fois sa case intérieure explorée ; son état ne se voit
            # que si le seuil est en vue, sinon on s'en souvient.
            for direction, sortie in piece["sorties"].items():
                x, y = sortie.get("case", (None, None))
                if x is None:
                    continue
                dx, dy = DIRECTIONS[direction]
                vue = sortie_visible(monde, salle, direction)
                if not vue and (x - dx, y - dy) not in connu:
                    continue
                vers = sortie.get("vers")
                s = {"salle": salle, "direction": direction, "globale": [ox + x, oy + y], "visible": vue,
                     "vers": vers, "vers_nom": salles[vers]["nom"] if memorisees.get(vers) else None}
                porte = monde.objets.get(sortie.get("porte"))
                if sortie.get("escalier"):
                    s["escalier"] = "monte" if salles.get(vers, {}).get("niveau", 0) > piece.get("niveau", 0) else "descend"
                elif vue and porte:
                    s["porte"] = _portes(monde, porte)
                elif not vue and porte:
                    souvenu = monde.data.get("souvenirs_portes", {}).get(porte["id"])
                    if souvenu:
                        s["porte"] = {"id": porte["id"], "nom": designer(porte), "etat": ETATS_PORTE[souvenu],
                                      "symbole": souvenu, "souvenir": True}
                sorties.append(s)
        # Un dernier aperçu reste là où il a été vu tant que cette case n'est pas revue.
        for id, souvenir in monde.data.get("souvenirs_visuels", {}).items():
            salle = souvenir["salle"]
            pos = tuple(souvenir["position"])
            contact = tuple(souvenir.get("contact", souvenir["position"]))
            ancre_mur = pos != contact
            if (salle not in ordre or contact not in memorisees.get(salle, set())
                    or (ancre_mur and pos not in murs_connus.get(salle, set()))
                    or contact in visible.get(salle, set()) or monde.est_porte(id)):
                continue
            ox, oy = salles[salle]["plan"]["origine"]
            personnage = monde.objets.get(id, {}).get("type") == "personnage"
            symbole = symbole_personnage(monde, monde.objets[id]) if personnage else souvenir["symbole"]
            souvenirs.append({"id": id, "nom": souvenir["nom"], "salle": salle, "case": list(pos),
                              "globale": [ox + pos[0], oy + pos[1]], "ancre_mur": ancre_mur,
                              "personnage": personnage, "symbole": symbole})
        # Ce qu'il voit maintenant, un par un, à sa position observée.
        for objet, salle, pos in objets_visibles:
            if salle not in ordre:
                continue
            ox, oy = salles[salle]["plan"]["origine"]
            o = {"id": objet["id"], "nom": designer(objet), "type": objet["type"], "salle": salle, "case": list(pos),
                 "globale": [ox + pos[0], oy + pos[1]], "ancre_mur": bool(objet.get("ancrage_carte")),
                 "aux_pieds": salle == joueur_salle and tuple(pos) == joueur_pos,
                 "symbole": symbole_objet_cases(objet, salle, monde)}
            if "allume" in objet:
                o["allume"] = bool(objet["allume"])
            if objet["type"] == "personnage":
                o["orientation"] = objet.get("orientation")
                o["porte"] = [{"id": k, "nom": designer(monde.objets[k])} for k in sorted(monde.objets)
                              if k != objet["id"] and porte_par(monde, k, objet["id"]) and monde.visible(k)]
            objets.append(o)
        # Les bouts d'une échelle installée, connus du joueur, portent le même code de liaison.
        for support in monde.objets.values():
            appui = support.get("appui_vertical", {})
            if not appui or support["id"] not in liens:
                continue
            for salle in (appui.get("bas"), appui.get("haut")):
                if salle not in ordre:
                    continue
                bout = position_cible(monde, support["id"], salle)
                if bout is None or memorisees.get(salle) and tuple(bout) not in memorisees[salle]:
                    continue
                code = codes_echelles.setdefault(support["id"], f"H{len(codes_echelles) + 1}")
                ox, oy = salles[salle]["plan"]["origine"]
                echelles.append({"code": code, "salle": salle, "support": support["id"],
                                 "nom": designer(liens[support["id"]]), "globale": [ox + bout[0], oy + bout[1]]})
        niveaux.append({"niveau": niveau, "salles": pieces, "murs": murs, "sorties": sorties,
                        "souvenirs": souvenirs, "objets": objets, "echelles": echelles})
    joueur = {"salle": joueur_salle, "case": list(joueur_pos), "orientation": monde.joueur.get("orientation"),
              "niveau": salles[joueur_salle].get("niveau", 0)}
    if joueur_pos:
        ox, oy = salles[joueur_salle]["plan"]["origine"]
        joueur["globale"] = [ox + joueur_pos[0], oy + joueur_pos[1]]
    return {"joueur": joueur, "niveaux": niveaux}
