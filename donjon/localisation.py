"""Repères publics calculés pour le MJ, sans lui faire interpréter les identifiants."""


REGLES = """
Les identifiants techniques des lieux sont des clés opaques, jamais des noms à interpréter.
salle.id est la clé de la pièce actuelle pour les propositions d'action ; salle.nom et
joueur.salle en sont le nom à utiliser dans le récit.
Pour chaque objet, localisation indique son lieu réel et sa position par rapport au joueur.
meme_salle=true signifie qu'il est dans la pièce actuelle. position_relative est déjà
calculée : ne la déduis pas d'anciennes réponses. Un objet visible qui bloque_passage
est un obstacle réel.
orientation_relative donne ses directions dans le regard actuel : devant, derriere,
gauche, droite (deux composantes possibles). Un souvenir porte ces mêmes directions
pour sa dernière position connue, recalculées selon ton regard maintenant ; ce repère
ne garantit pas que l'objet y soit encore. Une direction relative sans cible univoque
se remplace par le repère absolu en mètres fourni.
a_portee_de_main est calculé par le moteur : false interdit de manipuler d'ici et d'en distinguer
les détails (aspect fin, inscription, portrait, dimensions) : Corvus en voit le nom, la matière
et la place, rien de plus, et aucun détail ne s'établit d'ici. true signifie que la proximité
est satisfaite. Ne réclame alors ni rapprochement ni retour dans une autre
pièce. Vérifie encore les autres conditions (propriété, poids, outils, attaches).
Une demande de prise d'un objet à portée appelle une proposition prendre, pas un refus de
distance. Une question sur un obstacle visible appelle sa description, sans action.
L'état actuel prime sur toutes les réponses précédentes, qui peuvent être périmées ou fausses.
souvenirs_visuels liste des objets vus auparavant mais hors de vue : leur dernière salle
connue ne garantit ni leur présence ni leur position actuelle. Dans la pièce actuelle, vu_a
dit où Corvus l'a vu, par rapport à lui ; une action peut viser son id : le moteur le tourne
vers l'objet, vérifie qu'il y est encore et à portée, et dit sinon ce qui manque. Le récit ne
l'affirme pas présent tant que le moteur ne l'a pas établi.
Les pas au clavier ne figurent pas dans la conversation : le joueur peut s'être rapproché
depuis ta dernière réponse. Ni l'historique ni un nom technique ne priment sur ces repères.
"""


def decrire(monde, id, champ):
    """Résout aussi les contenants, portes, pièces voisines et extrémités d'échelle."""
    from .spatial import position_cible

    actuelle = monde.joueur["salle"]
    salles = monde.data["salles"]
    porte = monde.est_porte(id)
    # Les affaires portées ou connues au toucher peuvent être accessibles sans lumière.
    candidats = [actuelle] + [s for s in salles if s != actuelle]
    for salle in candidats:
        p = position_cible(monde, id, salle)
        if p is None:
            continue
        if salle != actuelle and (salle, *p) not in champ:
            continue
        if salle == actuelle and not monde.present_physique(id):
            continue
        direction, position = relatif(monde, salle, p)
        return {"salle_id": salle,
                "salle_nom": salles[salle]["nom"] if salle == actuelle or salle in monde.data["visitees"]
                             else "lieu inexploré au-delà du passage",
                "meme_salle": salle == actuelle, "porte_par_joueur": porte,
                "direction": "sur toi" if porte else direction,
                "position_relative": "dans tes affaires" if porte else position,
                "distance_metres": 0 if porte else distance(monde, salle, p),
                "orientation_relative": [] if porte else orientation_relative(monde, salle, p)}
    return None


def _ecart(monde, salle, case):
    """Écart global, y compris à travers un passage entre deux salles."""
    salles = monde.data["salles"]
    ox, oy = salles[salle]["plan"]["origine"]
    jx, jy = salles[monde.joueur["salle"]]["plan"]["origine"]
    dx = ox + case[0] - jx - monde.joueur["position"][0]
    dy = oy + case[1] - jy - monde.joueur["position"][1]
    return dx, dy


def orientation_relative(monde, salle, case):
    """Demi-plans du regard actuel, sans lire la position d'une entité cachée.

    L'appelant fournit soit la position perçue, soit la dernière position mémorisée.
    Un point sur le côté n'est ni devant ni derrière ; une diagonale a deux composantes.
    """
    from .spatial import VECTEURS
    regard = VECTEURS.get(monde.joueur.get("orientation"))
    if regard is None:
        return []
    dx, dy = _ecart(monde, salle, case)
    fx, fy = regard
    devant, droite = dx * fx + dy * fy, fx * dy - fy * dx
    return (["devant" if devant > 0 else "derriere"] if devant else []) + (
            ["droite" if droite > 0 else "gauche"] if droite else [])


def distance(monde, salle, case):
    from math import hypot
    return hypot(*_ecart(monde, salle, case))


def phrases_positions(faits):
    """Rendu exact des seuls repères publics, sans extraction de prose du MJ.

    Le souvenir est reprojeté par le capteur avant cet appel. Aucun état privé
    ni ancien texte de conversation ne permet de compléter un repère absent.
    """
    def repere(localisation):
        axes = localisation.get("position_relative") or localisation.get("vu_a")
        if not axes:
            return ""
        morceaux = [axes]
        metres = localisation.get("distance_metres")
        if metres:
            nombre = f"{metres:.1f}".rstrip("0").rstrip(".").replace(".", ",")
            morceaux.append(f"à environ {nombre} mètre{'s' if metres != 1 else ''} de toi")
        directions = {"devant": "devant toi", "derriere": "derrière toi",
                      "gauche": "à ta gauche", "droite": "à ta droite"}
        relatif = " et ".join(directions[d] for d in localisation.get("orientation_relative", []))
        if relatif:
            morceaux.append(relatif)
        return ", ".join(morceaux)

    positions = {}
    objets = faits.get("objets_perceptibles", [v for k, v in faits.items() if k.startswith("objet:")])
    from .francais import designer
    for o in objets:
        loc = o.get("localisation") or {}
        porte = loc.get("porte_par_joueur") or o.get("lieu") == "joueur"
        if not (o.get("visible") or porte):
            continue
        nom = designer(o, debut=True)
        lieu = "dans tes affaires" if porte else repere(loc)
        if not lieu and not faits.get("mode_cases") and o.get("lieu") == faits.get("salle", {}).get("id"):
            lieu = faits["salle"]["nom"]
        if lieu:
            positions[o["id"]] = f"{nom} : {lieu}."
    for souvenir in faits.get("souvenirs_visuels", []):
        if souvenir["id"] in positions:
            continue
        lieu = souvenir["derniere_salle"]
        relatif = repere(souvenir)
        if relatif:
            lieu += ", " + relatif
        positions[souvenir["id"]] = (f"Dernière observation de {souvenir['nom']} : {lieu}. "
                                      "Ce souvenir ne garantit pas sa position actuelle.")
    return positions


def relatif(monde, salle, case):
    """La direction et la position d'une case de ``salle`` par rapport au joueur, en mots."""
    dx, dy = _ecart(monde, salle, case)
    axes = [(dy, "nord" if dy < 0 else "sud"), (dx, "ouest" if dx < 0 else "est")]
    direction = "-".join(d for n, d in axes if n) or "ici"
    # Le plan est métrique (un mètre par unité) ; son quadrillage est privé.
    position = " et ".join(f"{abs(n)} mètre{'s' if abs(n) > 1 else ''} vers {d}"
                           for n, d in axes if n) or "à tes pieds"
    return direction, position
