"""Parcours comptables : conserver les oracles après le consentement explicite."""
from tests.test_audits_attendu import jouer as jouer_une_saisie


def jouer(monde, saisie, reponses, audits, revues=()):
    """Le joueur soumet sa phrase, puis confirme la proposition éventuelle.

    Le MJ simulé et les oracles restent ceux du test. Le suffixe n'a aucun
    effet sur une réponse sans proposition ni sur les commandes directes.
    Les tests U-C contrôlent séparément l'aperçu et l'annulation sans effet.
    """
    return jouer_une_saisie(monde, saisie, reponses, audits, revues, suite=("tenter",))
