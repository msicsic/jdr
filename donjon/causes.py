"""Demander la cause d'une détresse : propositions tirées des seuls savoirs du locuteur.

La décision ne consulte que l'observateur. La réponse est un contenu de parole
daté, reçu par la même voie par le demandeur et les témoins qui l'entendent.
"""
from copy import deepcopy
import json

from .esprits import lire, croire, poids_source, reconsiderer


def connues(monde, id, proche=None):
    """Causes crues encore actives, sans aller vérifier leur réalité."""
    from .defense import RECENT, actifs
    from .deliberation import salle_crue
    from .esprits import prevision
    from .memoire import mesure_eau
    from .eau import menacee
    from .ouie import resolu
    cible = proche or id
    croyances = lire(monde, id)['croyances']
    for auteur in sorted(actifs(monde, id, cible)):
        c = croyances[auteur]['violence']
        v = c['valeur'][cible]
        if monde.data['minutes'] - v['minute'] < RECENT:
            yield dict(type='cause_detresse', sorte='violence', sujet=auteur,
                       victime=cible, valeur=deepcopy(v), minute=v['minute'],
                       source=c['source'], confiance=c['confiance'])
    salle = salle_crue(monde, id, cible) if proche else monde.objets[id]['lieu']
    if salle and menacee(monde, id, salle):
        predit = prevision(monde, id, salle)
        c = predit or mesure_eau(monde, id, salle)
        if c:
            yield dict(type='cause_detresse', sorte='eau', sujet=salle,
                       valeur=deepcopy(predit['valeur']) if predit else True, minute=c['minute'],
                       source=c['source'], confiance=c['confiance'])
    from .memoire import bruits_retenus
    for s in reversed(bruits_retenus(monde, id)):
        if not s.get('qui') and not resolu(monde, id, s):
            if proche and s['salle'] != salle:
                continue
            yield dict(type='cause_detresse', sorte='bruit', sujet=s['salle'],
                       valeur={k: s[k] for k in ('nature', 'niveau')},
                       minute=s['minute'], source=s.get('source', 'entendu'),
                       confiance=s.get('confiance', 1.))


def contexte(monde, id, proche):
    """Entrées publiques du demandeur ; ni délai ni esprit privé du proche."""
    from .signes import detresse_retenue
    c = detresse_retenue(monde, id, proche)
    preuve = c['preuve'] if c else None
    # La date de rafraîchissement ne constitue pas une nouvelle détresse.
    signal = {k: preuve[k] for k in ('canal', 'signe', 'attribut', 'valeur')} if preuve else None
    return [['detresse', proche, json.dumps(signal, sort_keys=True), None]] if c else []


def demander_possible(monde, id, proche):
    from .deliberation import secours, refus_retenu
    from .relations import se_mefie
    if proche == 'joueur' or not monde.objets.get(proche, {}).get('profil'):
        return False
    return (any(q == proche and b == 'peur' for q, b, *_ in secours(monde, id))
            and not se_mefie(monde, id, proche)
            and not next(connues(monde, id, proche), None)
            and not refus_retenu(monde, id, proche, ('enqueter_cause',)))


def recevoir(monde, id, locuteur, c):
    """Un ouï-dire pondéré ; les constats plus récents ou plus solides priment."""
    from .voix import source_dite
    source = source_dite(monde, id, locuteur)
    confiance = .7 * c['confiance']
    candidate = dict(source=source, confiance=confiance)
    poids = poids_source(monde, id, candidate) * confiance
    if poids <= 0:
        return 'doute'
    sujet, sorte = c['sujet'], c['sorte']
    if sorte == 'eau':
        from .esprits import recevoir_prevision
        return recevoir_prevision(monde, id, locuteur,
                                  dict(objet=sujet, prevision=c['valeur'], observe=c['minute'],
                                       conviction=confiance), 0)
    if sorte == 'violence':
        ancienne = lire(monde, id)['croyances'].get(sujet, {}).get('violence')
        v = (ancienne or {}).get('valeur', {}).get(c['victime'])
        if v and (v['minute'] > c['minute'] or
                  poids_source(monde, id, ancienne) * ancienne['confiance'] >= poids):
            return 'doute'
        valeurs = deepcopy((ancienne or {}).get('valeur', {}))
        valeurs[c['victime']] = deepcopy(c['valeur'])
        croire(monde, id, sujet, 'violence', valeurs, source, confiance,
               minute=c['minute'], origine=dict(source=c['source'], minute=c['minute']))
    elif sorte == 'bruit':
        from .memoire import bruits_retenus, retenir_episode
        from .ouie import resolu
        son = dict(type='bruit', salle=sujet, minute=c['minute'], **c['valeur'])
        if resolu(monde, id, son) or any(
                s['minute'] >= c['minute'] for s in bruits_retenus(monde, id, sujet)):
            return 'doute'
        retenir_episode(monde, id, dict(son, source=source, confiance=confiance))
        from .deliberation import inquieter
        inquieter(monde, id, 'bruit', poids)
    reconsiderer(monde, id)
    return 'crue'


def phrase(monde, locuteur, c):
    from .social import _qui, GESTES
    from .francais import lieu
    if c['sorte'] == 'violence':
        fait = (f"{_qui(monde, c['sujet'], locuteur)} {GESTES[c['valeur']['operation']]} "
                f"{_qui(monde, c['victime'], locuteur)}")
    elif c['sorte'] == 'eau':
        fait = "l'eau menace " + lieu(monde.data['salles'][c['sujet']])
    else:
        fait = "un bruit sans cause identifiée venait de " + lieu(monde.data['salles'][c['sujet']])
    return f"{_qui(monde, locuteur)} explique son inquiétude : {fait} (croyance de la minute {c['minute']})."


def demander(monde, id, proche, lignes):
    from .corps import conscient
    from .echanges import accueil
    from .social import _qui, faire_entendre, recevoir as recevoir_parole
    from .pnj import _chroniquer
    from .deliberation import retenir_refus
    from .ouie import saisit
    # Un ancien plan ne force ni une question devenue inutile ni une répétition.
    if not demander_possible(monde, id, proche):
        return True
    entree = contexte(monde, id, proche)
    texte = f"{_qui(monde, id)} demande à {_qui(monde, proche)} ce qui l'inquiète."
    faire_entendre(monde, id, proche, texte, [], lignes, suites=False)
    issue = accueil(monde, id, proche) if conscient(monde, proche) else 'inconscient'
    dit = next(connues(monde, proche), None) if not issue else None
    issue = issue or ('dit' if dit else 'rien')
    # Le registre des réponses est indépendant des quarante souvenirs et du délai.
    retenir_refus(monde, id, proche, 'enqueter_cause',
                  'inconnu' if issue == 'qui_va_la' else issue, souvenir=False)
    reponse = lire(monde, id)['refus'][-1]
    reponse['cause'] = entree
    _chroniquer(monde, id, texte + f' ({issue})', 'social')
    monde.data['chronique'][-1]['demande_cause'] = dict(a=proche, issue=issue)
    if dit:
        reponse_texte = phrase(monde, proche, dit)
        apprentissage = recevoir_parole(monde, id, proche, dit) if saisit(monde, proche, id, 'dire') else None
        _chroniquer(monde, proche, reponse_texte, 'social')
        monde.data['chronique'][-1]['reponse_cause'] = dict(a=id, sorte=dit['sorte'], reception=apprentissage)
        faire_entendre(monde, proche, id, reponse_texte,
                       [dit['sujet'], *([dit['victime']] if 'victime' in dit else [])],
                       lignes, [dit], suites=False)
    elif conscient(monde, proche):
        reponse_texte = (f"{_qui(monde, proche)} ne donne pas de cause à son inquiétude."
                         if issue == 'rien' else f"{_qui(monde, proche)} refuse de répondre.")
        faire_entendre(monde, proche, id, reponse_texte, [], lignes, suites=False)
    return True
