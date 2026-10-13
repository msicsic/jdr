"""Objectifs déclarés par la partie, sans règle de quête dans le moteur général."""


def installer(m):
    """Complète les anciennes sauvegardes sans changer leur progression."""
    if "objectif_partie" in m.data:
        return
    defi = m.data.get("defi_relais")
    if defi:
        m.data["objectif_partie"] = {
            "objet": defi.get("objet", "cloche"), "lieu": "joueur",
            "salle": defi.get("refuge", "antichambre"),
            "message": "OBJECTIF ATTEINT : la cloche est de retour au refuge. Le relais peut donner l'alarme.",
        }
    elif (m.data.get("scenario_id") != "libre" and "anneau" in m.objets
          and m.data.get("scenario", {}).get("objectif")
          == "Retrouver l'anneau du veilleur dans la crypte."):
        m.data["objectif_partie"] = {
            "objet": "anneau", "lieu": "joueur",
            "message": "OBJECTIF ATTEINT : vous avez retrouvé l'anneau du veilleur. L'exploration reste ouverte.",
        }


def verifier(m):
    objectif = m.data.get("objectif_partie")
    if objectif is None:
        return
    if (not isinstance(objectif, dict)
            or not isinstance(objectif.get("objet"), str)
            or not isinstance(objectif.get("lieu"), str)
            or not isinstance(objectif.get("message"), str)
            or not objectif["message"].strip()
            or len(objectif["message"]) > 500
            or ("salle" in objectif and objectif["salle"] not in m.data["salles"])):
        raise AssertionError("Objectif de partie invalide")


def actualiser(m, lignes):
    objectif = m.data.get("objectif_partie")
    if not objectif or m.data.get("objectif_atteint"):
        return bool(m.data.get("objectif_atteint"))
    cible = m.objets.get(objectif.get("objet"))
    if (cible and cible["lieu"] == objectif.get("lieu")
            and (not objectif.get("salle") or m.joueur["salle"] == objectif["salle"])):
        m.data["objectif_atteint"] = True
        lignes.append(objectif["message"])
    return bool(m.data.get("objectif_atteint"))
