"""Objectifs déclarés par la partie, sans règle de quête dans le moteur général."""


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
