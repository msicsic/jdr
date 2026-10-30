"""Oracles de reprise G5 (rapport 323) : seule la consultation est mémorisée."""
import copy

from donjon.monde import Monde
from donjon.rendu import regarder


def apres_regarder(etat):
    """État complet attendu après une commande regarder, sans effet de monde.

    Ne retire aucun champ de la comparaison : l'entrée exacte est ajoutée à
    la conversation attendue (bornée à douze tours comme le contrat public).
    """
    attendu = copy.deepcopy(etat)
    texte = regarder(Monde(copy.deepcopy(etat))).strip()
    attendu['conversation'] = [*attendu['conversation'], {
        'joueur': 'regarder', 'reponse': texte[:4000],
        'nature': 'resultat_moteur', 'revision': etat['revision']}][-12:]
    return attendu
