"""Actions des PNJ : le moteur exécute leurs intentions avec les règles physiques du joueur.

Une intention a un but (pour l'instant : rejoindre un lieu) ; le chemin est cherché sur ce
que le PNJ croit des portes, puis chaque geste est revalidé sur l'état réel. Une porte
fermée se franchit en l'ouvrant ; une porte verrouillée sans clé portée arrête le PNJ et
devient une croyance apprise par l'essai. Chaque geste coûte une minute. Luna ne décide
ni de l'alerte ni du déplacement ; elle reçoit la position qui en résulte.
"""
from collections import deque

from .esprits import croire, esprit, lire, percevoir
from .francais import designer
from .geometrie import placer, position_entree


def verifier(monde):
    for o in monde.objets.values():
        if o["type"] != "personnage":
            continue
        reaction = o.get("reaction_son")
        assert reaction is None or (isinstance(reaction, dict) and set(reaction) == {"seuil"}
                                    and type(reaction["seuil"]) is int
                                    and 1 <= reaction["seuil"] <= 5), "Réaction de PNJ invalide"


def reagir(monde, id, origine, niveau):
    """Réflexe déclaré par l'auteur : un son assez fort donne l'intention d'aller voir."""
    pnj = monde.objets[id]
    reaction = pnj.get("reaction_son")
    if reaction and niveau >= reaction["seuil"] and origine != pnj["lieu"]:
        esprit(monde, id)["intention"] = {"but": {"type": "rejoindre", "lieu": origine},
                                          "minutes": 0, "depuis": monde.data["minutes"]}


def _cle_portee(monde, id, porte):
    from .spatial import porte_par
    return next((c for c, o in monde.objets.items()
                 if porte_par(monde, c, id) and porte in o.get("ouvre", [])), None)


def _franchissable_cru(monde, id, porte):
    """Le PNJ tente toute porte, sauf celle qu'il sait verrouillée sans en porter la clé."""
    if not porte:
        return True
    cru = lire(monde, id)["croyances"].get(porte, {}).get("verrouillee")
    return not (cru and cru["valeur"]) or _cle_portee(monde, id, porte) is not None


def chemin(monde, id, depart, arrivee):
    """Sorties à emprunter selon ce que le PNJ croit des portes ; None si aucun passage cru."""
    precedent, file = {depart: None}, deque([depart])
    while file:
        lieu = file.popleft()
        for sortie in monde.data["salles"][lieu]["sorties"].values():
            vers = sortie["vers"]
            if (vers in precedent or vers not in monde.data["salles"]
                    or not _franchissable_cru(monde, id, sortie.get("porte"))):
                continue
            precedent[vers] = (lieu, sortie)
            file.append(vers)
    if arrivee not in precedent:
        return None
    etapes = []
    while arrivee != depart:
        lieu, sortie = precedent[arrivee]
        etapes.append(sortie)
        arrivee = lieu
    return etapes[::-1]


def _au_seuil(monde, o, sortie):
    """Place le PNJ sur la case intérieure de la sortie, comme le joueur pour l'ouvrir."""
    if "position" not in o or not monde.data.get("mode_cases"):
        return
    from .spatial import _case_interieure, _case_libre
    case = _case_interieure(monde, o["lieu"], sortie)
    if case is not None and _case_libre(monde, o["lieu"], case):
        placer(o, o["lieu"], list(case))


def _annoncer(monde, id, porte, texte_vu, texte_porte, lignes):
    if monde.visible(id):
        lignes.append(designer(monde.objets[id], debut=True) + texte_vu + designer(porte) + ".")
    elif monde.visible(porte["id"]):
        lignes.append(designer(porte, debut=True) + texte_porte)


def _geste(monde, id, sortie, lignes):
    """Un geste d'une minute vers la sortie : ouvrir, déverrouiller, essayer ou passer."""
    o = monde.objets[id]
    porte = monde.objets.get(sortie.get("porte") or "")
    if porte and not porte.get("ouverte"):
        _au_seuil(monde, o, sortie)
        if porte.get("verrouillee"):
            cle = _cle_portee(monde, id, porte["id"])
            if cle is None:
                croire(monde, id, porte["id"], "verrouillee", True, "essai")
                _annoncer(monde, id, porte, " tente d'ouvrir ", " résiste à une poussée.", lignes)
                return
            porte["verrouillee"] = False
            croire(monde, id, porte["id"], "verrouillee", False, "essai")
            _annoncer(monde, id, porte, " déverrouille ", " se déverrouille.", lignes)
            return
        porte["ouverte"] = True
        croire(monde, id, porte["id"], "verrouillee", False, "essai")
        _annoncer(monde, id, porte, " ouvre ", " s'ouvre.", lignes)
        return
    depuis, o["lieu"] = o["lieu"], sortie["vers"]
    if "position" in o:
        placer(o, o["lieu"], position_entree(monde, o["lieu"], depuis))


def avancer(monde, minutes, lignes):
    """Renvoie les PNJ apparus dans la perception du joueur pendant ces minutes."""
    apparus = []
    for id, o in monde.objets.items():
        if o["type"] != "personnage":
            continue
        if not lire(monde, id)["intention"]:
            continue
        intention = esprit(monde, id)["intention"]
        if not intention:
            continue
        but = intention["but"]["lieu"]
        budget = intention["minutes"] + minutes
        vu = monde.visible(id)
        while budget >= 1 and o["lieu"] != but:
            etapes = chemin(monde, id, o["lieu"], but)
            if not etapes:
                # Aucun passage cru : il attend sur place, sans accumuler d'avance.
                budget = 0
                break
            _geste(monde, id, etapes[0], lignes)
            budget -= 1
            percevoir(monde, id)
        if o["lieu"] == but:
            esprit(monde, id)["intention"] = None
        else:
            intention["minutes"] = budget
        if monde.visible(id) and not vu:
            lignes.append(designer(o, debut=True) + " arrive.")
            apparus.append(id)
        elif vu and not monde.visible(id):
            lignes.append(designer(o, debut=True) + " s'éloigne.")
    return apparus
