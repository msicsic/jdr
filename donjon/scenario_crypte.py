"""Scénario de la crypte : état initial déclaré hors du moteur commun."""
import json
from pathlib import Path

from .monde import Monde


ETAT_INITIAL = Path(__file__).with_name("scenario_crypte.json")


def nouveau_monde(seed=1985):
    data = json.loads(ETAT_INITIAL.read_text(encoding="utf-8"))
    data["seed"] = seed
    return Monde(data)


def demo():
    """Parcours reproductible propre à la crypte, sans sauvegarde."""
    from .commandes import analyser
    from .moteur import Moteur
    from .rendu import carte, fiche

    monde = nouveau_monde(1985)
    moteur = Moteur(monde)
    print("LE SEUIL — démonstration locale reproductible, aucune sauvegarde modifiée")
    print(carte(monde))

    def jouer(commande):
        print("\n> " + commande)
        print(moteur.executer(moteur.preparer(analyser(monde, commande))))

    for commande in ("examiner porte", "examiner gravure", "copier gravure avec cire",
                     "prendre clé", "ouest", "acheter pied-de-biche", "est"):
        jouer(commande)
    for axe, identifiant in (("supérieur", "axe_haut"), ("inférieur", "axe_bas")):
        while monde.objets[identifiant]["attache"]:
            jouer(f"retirer axe {axe} avec pied-de-biche")
    for commande in ("nord", "ouvrir coffre avec clé", "prendre anneau", "sud", "examiner porte"):
        jouer(commande)
    print("\n" + carte(monde))
    print(fiche(monde))
    return 0
