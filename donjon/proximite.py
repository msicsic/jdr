"""Contrôle commun des interactions manuelles en mode case par case."""
from .monde import ErreurMonde
from .francais import designer


def exiger(monde, id):
    if not monde.data.get("mode_cases"):
        return
    from .spatial import proche, position_cible
    if not proche(monde, id):
        o = monde.objets.get(id)
        nom = designer(o) if o else "cette cible"
        position = position_cible(monde, id)
        if position:
            ox, oy = monde.data["salles"][monde.joueur["salle"]]["plan"]["origine"]
            position = position[0] + ox, position[1] + oy
        indication = f" (case {position[0]}, {position[1]} du plan)" if position and monde.visible(id) else ""
        raise ErreurMonde("Approche-toi de " + nom + indication + " : il faut être sur sa case ou juste à côté pour agir.")
