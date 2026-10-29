"""Occasion et service de protection, sur les seules croyances de l'acteur.

Le marché reste une proposition ordinaire, son exécution une tâche payée.
Ce module ne donne ni position ni moyens privés au futur protecteur.
"""
from .esprits import lire


def peur_crue(monde, id, autre):
    from .signes import detresse_retenue
    from .causes import connues
    etat = lire(monde, id)['croyances'].get(autre, {}).get('etat', {}).get('valeur', {})
    if etat.get('mort') or etat.get('parti') or etat.get('conscient') is False:
        return False
    return bool(detresse_retenue(monde, id, autre) or next(connues(monde, id, autre), None))


def fonds_crus(monde, id, autre):
    """Sommes connues, jamais la bourse réelle ni une fortune supposée."""
    connus = lire(monde, id)['croyances']
    return sum(c.get('pieces', {}).get('valeur', 0) for x, c in connus.items()
               if x == autre or c.get('lieu', {}).get('possession', {}).get('porteur') == autre)


def capable(monde, id, autre):
    from .caractere import valeur
    from .combat import force_crue
    from .defense import actifs
    adversaires = actifs(monde, id, autre)
    # L'inconnu n'est pas un ennemi faible inventé : force_crue a son a priori neutre.
    force = min((force_crue(monde, id, a) for a in adversaires), default=force_crue(monde, id, autre))
    return valeur(monde, id, 'courage') / 100 + force >= 1


def devis(monde, id, condition):
    from .planification import _pulsion, RESTER
    from .caractere import valeur
    from .combat import force_crue
    from .defense import actifs
    autre = condition['objet']
    if condition['echeance'] <= monde.data['minutes'] or not capable(monde, id, autre):
        return None
    trouve = _pulsion(monde, id, {'pres': autre}, False)
    if trouve is None:
        return None
    force = min((force_crue(monde, id, a) for a in actifs(monde, id, autre)), default=.5)
    risque = (1 - force) * (1 - valeur(monde, id, 'courage') / 100)
    return trouve[0] + min(RESTER, condition['echeance'] - monde.data['minutes']) * (1 + risque), trouve[2]


def occasions(monde, id):
    from .caractere import valeur, valeur_pieces
    from .planification import RESTER, prix_tache
    from .echanges import offre_sensee
    from .deliberation import salle_crue, urgents
    from . import agendas
    if not valeur(monde, id, 'ambition') or urgents(monde, id) or agendas.en_cours(monde, id, actifs=True) or agendas.proteges(monde, id):
        return
    for autre in sorted(lire(monde, id)['croyances']):
        if autre == id or (autre != 'joueur' and monde.objets.get(autre, {}).get('type') not in ('personnage', 'depouille')):
            continue
        if not peur_crue(monde, id, autre) or fonds_crus(monde, id, autre) <= 0:
            continue
        if autre in agendas.proteges(monde, id) or salle_crue(monde, id, autre) is None:
            continue
        c = {'objet': autre, 'proteger': True, 'echeance': monde.data['minutes'] + RESTER}
        d = devis(monde, id, c)
        if d is None:
            continue
        prix = prix_tache(d[0])
        if prix > fonds_crus(monde, id, autre) or valeur_pieces(monde, id, prix) * valeur(monde, id, 'ambition') / 50 < d[0]:
            continue
        demande, terme = {'type': 'pieces', 'montant': prix}, {'type': 'tache', 'condition': c}
        if offre_sensee(monde, id, autre, demande, terme):
            yield {'qui': autre, 'demande': demande, 'contrepartie': terme}


def utilite(monde, observateur, beneficiaire, protecteur):
    """Même valeur du secours, jugement propre ou estimation depuis une peur perçue."""
    from .caractere import ENJEU
    from .deliberation import seuils
    from .combat import force_crue
    peur = peur_crue(monde, observateur, beneficiaire)
    if observateur == beneficiaire:
        seuil = seuils(monde, observateur).get('securite', 100)
        peur = peur or lire(monde, observateur)['besoins'].get('securite', 0) >= seuil
    force = (force_crue(monde, observateur, beneficiaire) if protecteur == observateur else
             1 - force_crue(monde, observateur, protecteur))
    return ENJEU * force if peur else 0.


def fin(monde, id, condition, depuis):
    """Une fin positive connue ; aucune absence de signe ne prouve la sécurité."""
    autre = condition['objet']
    c = lire(monde, id)['croyances'].get(autre, {})
    etat = c.get('etat', {}).get('valeur', {})
    if etat.get('mort'):
        return 'protege cru mort'
    if etat.get('parti'):
        return 'protege cru parti'
    calme = c.get('detresse', {})
    if calme.get('valeur') is False and calme.get('minute', -1) >= depuis and not peur_crue(monde, id, autre):
        return 'danger cru passe'
    if monde.data['minutes'] >= condition['echeance']:
        return 'echeance'
    return None
