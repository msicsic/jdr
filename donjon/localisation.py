"""Repères publics calculés pour le MJ, sans lui faire interpréter les identifiants."""


REGLES = """
Les identifiants techniques des lieux sont des clés opaques, jamais des noms à interpréter.
salle.id est la clé de la pièce actuelle pour les propositions d'action ; salle.nom et
joueur.salle en sont le nom à utiliser dans le récit.
Pour chaque objet, localisation indique son lieu réel et sa position par rapport au joueur.
meme_salle=true signifie qu'il est dans la pièce actuelle. position_relative est déjà
calculée : ne la déduis pas d'anciennes réponses. Un objet visible qui bloque_passage
est un obstacle réel.
a_portee est calculé par le moteur : false interdit de manipuler d'ici ; true signifie
que la proximité est satisfaite. Ne réclame alors ni rapprochement ni retour dans une autre
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
                "position_relative": "dans tes affaires" if porte else position}
    return None


def relatif(monde, salle, case):
    """La direction et la position d'une case de ``salle`` par rapport au joueur, en mots."""
    salles = monde.data["salles"]
    ox, oy = salles[salle]["plan"]["origine"]
    jx, jy = salles[monde.joueur["salle"]]["plan"]["origine"]
    dx = ox + case[0] - jx - monde.joueur["position"][0]
    dy = oy + case[1] - jy - monde.joueur["position"][1]
    axes = [(dy, "nord" if dy < 0 else "sud"), (dx, "ouest" if dx < 0 else "est")]
    direction = "-".join(d for n, d in axes if n) or "ici"
    position = " et ".join(f"{abs(n)} case{'s' if abs(n) > 1 else ''} vers {d}"
                           for n, d in axes if n) or "sur ta case"
    return direction, position
