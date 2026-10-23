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
        from .voix import designation, nom_pour_joueur
        if o and o["type"] == "personnage" and designation(monde, id) != id:
            # Une voix qu'il ne sait à qui prêter : il ne l'approche que sous le nom qu'il lui connaît.
            voix = nom_pour_joueur(monde, id)
            nom = ("d'" if voix[:1].lower() in "aeiouyéèêh" else "de ") + voix
        position = position_cible(monde, id)
        if position:
            ox, oy = monde.data["salles"][monde.joueur["salle"]]["plan"]["origine"]
            position = position[0] + ox, position[1] + oy
        indication = f" ; position = {position}" if position and monde.visible(id) else ""
        raise HorsDePortee("Approche-toi " + nom + " : il faut être juste à côté pour agir.",
                          f"cible = {id} : hors de portée de main{indication} ; le joueur doit s'approcher.")
