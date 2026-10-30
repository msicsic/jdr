"""Porte des épisodes, sons, approches et secours, au format historique.

S1a conserve la liste sauvegardée, son plafond et les crochets réentrants.
Les autres familles seront portées séparément ; aucune requête de ce
module ne renvoie le stock mutable aux consommateurs.
"""
import copy

MEMOIRE_MAX = 40


def derniere_approche(monde, id, auteur, objet, lieu, cible, case=None):
    """Dernière approche de la charge ; les anciens lieux/cibles restent implicites."""
    from .esprits import lire
    return copy.deepcopy(next((s for s in reversed(lire(monde, id)['memoire'])
        if s['type'] == 'approche_charge' and s['auteur'] == auteur and s['objet'] == objet
        and s.get('lieu', lieu) == lieu and s.get('cible', cible) == cible
        and (case is None or s['case'] == case)), None))


def mise_en_garde_retenue(monde, id, destinataire, objet, preuve):
    """Même preuve d'approche, sans péremption ni effet de lecture."""
    from .esprits import lire
    return any(s['type'] == 'mise_en_garde' and s['a'] == destinataire
               and s['objet'] == objet and s['preuve'] == preuve
               for s in lire(monde, id)['memoire'])


def avertissements_a_donner(monde, id):
    """Copies dans l'ordre historique, y compris les avertissements déjà tenus."""
    from .esprits import lire
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire'] if s['type'] == 'a_prevenir']


def _avertissement(monde, id, victime, auteur):
    from .esprits import lire
    # Le premier, même déjà tenu : ne pas passer à une autre occurrence.
    return next((s for s in lire(monde, id)['memoire'] if s['type'] == 'a_prevenir'
                 and s['victime'] == victime and s['auteur'] == auteur), None)


def avertissement_du(monde, id, victime, auteur):
    return copy.deepcopy(_avertissement(monde, id, victime, auteur))


def acquitter_avertissement(monde, id, victime, auteur):
    """Marque tenu le premier avertissement correspondant, sans crochet."""
    alerte = _avertissement(monde, id, victime, auteur)
    if alerte is None or alerte.get('tenu'):
        return False
    alerte['tenu'] = True
    return True


def secours_retenus(monde, id, qui=None, *, en_attente=False):
    """Copies ordonnées des cris ; le lecteur conserve sa borne de récence."""
    from .esprits import lire
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire'] if s['type'] == 'secours'
            and (qui is None or s['qui'] == qui) and (not en_attente or not s.get('examine'))]


def _examiner_secours(monde, id, constate):
    from .esprits import lire
    secourus = []
    for s in lire(monde, id)['memoire']:
        if s['type'] == 'secours' and not s.get('examine') and constate(s):
            s['examine'] = True
            secourus.append(s['qui'])
    return secourus


def examiner_secours_du_lieu(monde, id, salle):
    """Acquitte chaque cri du lieu effectivement inspecté, dans l'ordre."""
    return _examiner_secours(monde, id, lambda s: s['salle'] == salle)


def examiner_secours_constates(monde, id):
    """Vue actuelle ou état vu strictement après le cri, comme historiquement."""
    from .esprits import lire, percoit
    e = lire(monde, id)

    def constate(s):
        qui = s['qui']
        etat = e['croyances'].get(qui, {}).get('etat', {})
        vu = monde.visible(qui) if id == 'joueur' else percoit(monde, id, qui)
        return vu or etat.get('source') == 'vu' and etat['minute'] > s['minute']

    return _examiner_secours(monde, id, constate)


def retenir_episode(monde, id, evenement):
    """Copie, date et retient l'occurrence avant ses conséquences métier."""
    from .esprits import esprit, _date_indices_soupcon, GESTES_SOUPCON_MAX
    if evenement["type"] == "dit" and "valeur" in evenement:
        from .social import retenir_dit
        retenir_dit(monde, id, evenement["a"], {"type": "affirmation", **{
            k: evenement[k] for k in ("sujet", "attribut", "valeur")}})
    memoire = esprit(monde, id)["memoire"]
    souvenir = copy.deepcopy({"minute": monde.data["minutes"], **evenement})
    from .relations import identifier
    from .temps import instant
    if id != "joueur" and souvenir["type"] in ("vu_agir", "entendu_agir", "vu_porter", "vol_surpris"):
        # Même indice et même identité de preuve qu'avant la porte S1a.
        gestes = esprit(monde, id)["indices_soupcon"]["gestes"]
        gestes.append({"objet": souvenir["objet"], "instant": _date_indices_soupcon(monde)})
        del gestes[:-GESTES_SOUPCON_MAX]
    identifier(souvenir, instant(monde))
    memoire.append(souvenir)
    del memoire[:-MEMOIRE_MAX]
    from .relations import souvenir as eprouver_souvenir
    eprouver_souvenir(monde, id, souvenir)
    from .defense import retenir as retenir_violence
    retenir_violence(monde, id, souvenir)


def evincer_episodes(monde, id, retirer):
    """Filtre en place, dans l'ordre, sans crochet ni copie des survivants.

    Le prédicat porte la décision du consommateur ; il ne doit pas modifier
    le stock. L'identité de la liste et des épisodes conservés reste intacte.
    """
    from .esprits import esprit
    memoire = esprit(monde, id)["memoire"]
    memoire[:] = [s for s in memoire if not retirer(s)]


def bruits_retenus(monde, id, salle=None, *, examens=False):
    """Copies ordonnées des bruits, et éventuellement de leurs examens vains.

    Pas de filtre de péremption : chaque lecteur garde sa politique historique.
    Une consultation, même d'un esprit absent, ne crée rien.
    """
    from .esprits import lire
    types = ('bruit', 'examen') if examens else ('bruit',)
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire']
            if s['type'] in types and (salle is None or s['salle'] == salle)]


def retirer_bruits(monde, id, salle):
    """Retire les bruits du lieu, sans toucher aux examens ni aux crochets."""
    evincer_episodes(monde, id, lambda s: s['type'] == 'bruit' and s['salle'] == salle)


def retenir_examen_sonore(monde, id, salle, case=None):
    """Consomme les bruits parcourus et retient l'examen vain historique."""
    from .esprits import esprit
    from .ouie import resolu, INTENSITES
    stock = esprit(monde, id)['memoire']
    vus = [s for s in stock if s['type'] == 'bruit' and s['salle'] == salle]
    attendus = [s for s in vus if not resolu(monde, id, s)]
    evincer_episodes(monde, id, lambda s: any(s is v for v in vus)
                     or (s['type'] == 'examen' and s['salle'] == salle and attendus))
    if attendus:
        qui = {s.get('qui') for s in attendus}
        retenir_episode(monde, id, {'type': 'examen', 'salle': salle,
                                   'case': list(case) if case is not None else None,
                                   'nature': max((s['nature'] for s in attendus), key=INTENSITES.get),
                                   **({'qui': qui.pop()} if len(qui) == 1 and None not in qui else {})})
    return bool(attendus)


def _examen_couvrant(monde, id, salle, n, qui, case):
    """Référence interne uniquement ; même ordre et mêmes bornes historiques."""
    from .esprits import RECENT, lire
    from .ouie import INTENSITES
    minute = monde.data['minutes']
    for s in reversed(lire(monde, id)['memoire']):
        if s['type'] != 'examen' or s['salle'] != salle or minute - s['minute'] > RECENT:
            continue
        if INTENSITES[n] > INTENSITES[s['nature']] or qui is not None and qui != s.get('qui'):
            return None
        if case is not None and s['case'] is None:
            return None
        return s
    return None


def examen_couvrant(monde, id, salle, n, qui=None, case=None):
    """Copie de l'examen qui couvre le bruit, ou None ; aucune écriture."""
    return copy.deepcopy(_examen_couvrant(monde, id, salle, n, qui, case))


def rafraichir_examen_sonore(monde, id, salle, n, qui=None, case=None):
    """Prolonge le même examen si le bruit est couvert, sans nouvel épisode."""
    examen = _examen_couvrant(monde, id, salle, n, qui, case)
    if examen is None:
        return False
    examen['minute'] = monde.data['minutes']
    return True


def retenir_bruit_sans_profil(monde, id, salle, n, niveau):
    """Remplace les bruits du lieu par leur maximum, sans délibération."""
    from .esprits import esprit
    from .ouie import INTENSITES
    anciens = [s for s in esprit(monde, id)['memoire'] if s['type'] == 'bruit' and s['salle'] == salle]
    retirer_bruits(monde, id, salle)
    retenir_episode(monde, id, {'type': 'bruit', 'salle': salle,
                               'nature': max([n, *(s['nature'] for s in anciens)], key=INTENSITES.get),
                               'niveau': max([niveau, *(s.get('niveau', niveau) for s in anciens)])})
