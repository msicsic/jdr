"""Contrôle commun des interactions manuelles en mode case par case."""
from .monde import ErreurMonde
from .francais import complement_de


class HorsDePortee(ErreurMonde):
    """La cible est trop loin : seul un déplacement du joueur lève l'obstacle, aucune autre
    proposition du MJ ne le peut."""


def exiger(monde, id):
    if not monde.data.get("mode_cases"):
        return
    from .spatial import proche, position_cible
    if not proche(monde, id):
        o = monde.objets.get(id)
        nom = complement_de(o) if o else "de cette cible"
        position = position_cible(monde, id)
        if position:
            ox, oy = monde.data["salles"][monde.joueur["salle"]]["plan"]["origine"]
            position = position[0] + ox, position[1] + oy
        indication = f" (case {position[0]}, {position[1]} du plan)" if position and monde.visible(id) else ""
        raise HorsDePortee("Approche-toi " + nom + indication + " : il faut être sur sa case ou juste à côté pour agir.")
