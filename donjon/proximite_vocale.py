"""Terminal de séjour vocal, sur la seule localisation et les portes crues.

La marche et son devis emploient le même ensemble d'arrivées. La portée est
celle des mots d'une voix ordinaire ; ni position ni oreille privées du tiers.
"""
from . import ouie
from .esprits import lire
from .obstacles import monde_cru


def vocale(etape):
    return etape['operation'] == 'rester' and etape.get('contenu', {}).get('portee') == 'voix'


def arrivees(monde, acteur, sujet, *, portes=()):
    croyances = lire(monde, acteur)['croyances']
    lieu = croyances.get(sujet, {}).get('lieu', {})
    salle = lieu.get('salle')
    if salle not in monde.data['salles'] or lieu.get('valeur') is None:
        return lambda s, c: False
    case = lieu.get('case')
    if monde.data.get('mode_cases') and case is None:
        return lambda s, c: False
    cru = monde_cru(monde, acteur)
    for porte, ouverte in portes:
        cru.objets[porte]['ouverte'] = ouverte
    # Une responsabilité n'est pas un repos ni une ronde. L'oreille propre
    # et le seuil commun des mots suffisent ; aucun état privé du protégé.
    seuil = max(ouie.SEUIL, ouie.SEUIL - ouie.finesse(monde, acteur))
    entend = monde.objets[acteur].get('entend', True)
    entrees = ouie.propager(cru, salle, tuple(case) if case is not None else None,
                           ouie.INTENSITES['voix'])

    def admissible(s, c):
        niveau = ouie.parvenu(entrees, s, c)
        return bool(entend and niveau is not None and niveau[0] >= seuil)
    return admissible


def entrees(monde, acteur):
    """Lectures propres du terminal à ajouter aux entrées de recherche."""
    return [ouie.finesse(monde, acteur), monde.objets[acteur].get('entend', True),
            ouie.INTENSITES['voix'], ouie.SEUIL, ouie.PALIERS, ouie.PORTE, ouie.OUVERTURE]
