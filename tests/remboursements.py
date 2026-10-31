"""Exercer un remboursement local choisi, sans simuler les autres priorités du PNJ.

Depuis le lot 388, solder traite les réclamations ; un versement volontaire
vient du planificateur et passe par le même geste réel que la vie des PNJ.
Les tests d'autonomie restent dans test_rembourser_dette.
"""
from donjon.planification import rembourser
from donjon.pnj import _executer


def rembourser_local(monde, qui, lignes):
    projet = rembourser(monde, qui)
    if projet is None:
        return False
    # Ne jamais sauter un trajet ou une approche pour faire passer un test.
    assert [e['operation'] for e in projet[1]] == ['rembourser'], projet
    return _executer(monde, qui, projet[1][0], lignes, [])
