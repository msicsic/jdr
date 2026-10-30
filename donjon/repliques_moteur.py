"""Publication commune des répliques typées, fixées dans G15 avant affichage."""

ACTES = ('reponse_comptable', 'reponse_information', 'reponse_avis')


def est_fixee(emission):
    """Réplique admise ou avis social déjà formulé et enregistré par le moteur."""
    contenus = emission.get('parametres', {}).get('contenu', [])
    return (emission.get('acte') in ACTES
        or emission.get('evenement', {}).get('replique_moteur', False)
        or bool(contenus) and all(
            c.get('type') == 'rumeur' and c.get('evenement', {}).get('type') == 'avis'
            for c in contenus))


def admettre(monde, autorisations, rapport):
    """Remplace les autorisations typées par des émissions déjà fixées.

    La copie préparée seule reçoit les mots ; sa transaction sera rejouée sur
    l'original avant sauvegarde et affichage. Aucune publication de brouillon.
    """
    from .comptes_parles import dossier, formuler
    from .emissions import enregistrer, lire
    from .ouie import auditeurs_parole
    from .voix import nom_pour_joueur
    faits = {'comptes': dossier(monde, rapport)}
    for a in list(autorisations):
        operations = a['evenement'].get('resolutions_parlees', a['evenement'].get('resolutions_comptables', []))
        if not operations:
            continue
        auteur = a['locuteur']
        # Les biens d'une offre refusée ne figurent pas parmi les offres actives.
        # Ils restent nécessaires à la désignation exacte de ses termes.
        from .propositions import offre
        refusees = [offre('joueur', auteur, op['resolution']['offre']['demande'],
                    op['resolution']['offre']['contrepartie']) for op in operations
                    if op['resolution'].get('offre')]
        if refusees:
            faits = {'comptes': dossier(monde, {**rapport, 'offres': rapport.get('offres', []) + refusees})}
        from .informations_parlees import formuler as informer
        from .avis_parles import formuler as donner_avis
        mots = ' '.join(donner_avis(monde, op['contenu'], op['avis']) if 'avis' in op
                        else informer(monde, auteur, op['contenu'], op['information']) if 'information' in op
                        else formuler(faits, auteur, op) for op in operations)
        couverts = [f for op in operations for f in op['faits']]
        autres = [f for f in a['evenement']['faits'] if f not in couverts]
        restants = [c for c in a['parametres']['contenu']
                    if not any(c == op.get('contenu') for op in operations)]
        libre = restants or a['parametres'].get('contenu_libre')
        rendu = ' '.join([f'{nom_pour_joueur(monde, auteur)} : « {mots} »', *([] if libre else autres)])
        comptable = any(not ({'information', 'avis'} & op.keys()) for op in operations)
        acte = 'reponse_comptable' if comptable else 'reponse_information' if any(
            'information' in op for op in operations) else 'reponse_avis'
        auditeurs = auditeurs_parole(monde, auteur)
        presentation = next((op['information']['nom'] for op in operations
            if op.get('contenu', {}).get('type') == 'qui'
            and op.get('information', {}).get('etat') == 'nomme'), '')
        # Même réception que pour une réplique admise par l'audit. Les mots
        # entendus et la présentation typée précèdent la sauvegarde.
        from .noms import entendre, presenter
        for auditeur in auditeurs:
            entendre(monde, auditeur, auteur, mots)
            if presentation:
                presenter(monde, auditeur, auteur, presentation, mots)
        evenement = {**a['evenement'], 'faits': couverts if libre else a['evenement']['faits'], 'type': {
            'reponse_comptable': 'compte_parle', 'reponse_information': 'information_parlee',
            'reponse_avis': 'avis_parle'}[acte],
            'emission_joueur': next((p['id'] for p in reversed(lire(monde)) if p['locuteur'] == 'joueur'), None)}
        emission = enregistrer(monde, auteur, acte=acte, parametres={**a['parametres'],
            'contenu': [op['contenu'] for op in operations if 'contenu' in op], 'contenu_libre': False},
            modalite='refus' if any(op['resolution'].get('etat') == 'refuse' or
                'garde' in op['resolution'].get('reglements', []) or
                op.get('information', {}).get('etat') in ('refus', 'mefiance', 'rancune', 'qui_va_la')
                for op in operations) else 'croyance' if any({'information', 'avis'} & op.keys() for op in operations) else 'constat',
            evenement=evenement, a=['joueur'], auditeurs=auditeurs,
            texte=mots, rendu=rendu, presentation=presentation)
        if emission and 'joueur' in emission['auditeurs']:
            emission['rendu_public'] = rendu
        # Les voies non portées conservent leur autorisation et leurs audits.
        if libre:
            a['parametres']['contenu'] = restants
            a['evenement'] = {'type': 'parole_joueur', 'faits': autres}
        else:
            autorisations.remove(a)

def reponse(rapport):
    """Résultat entièrement moteur quand il ne reste rien à faire formuler."""
    from .emissions import entendues, reponses
    # Les admissions sans conversation (description, fait local...) n'ont
    # pas de rapport vocal. Elles gardent leur voie de rédaction existante.
    rapport = rapport or {}
    flux = entendues(rapport)
    if not any(est_fixee(p) for p in flux) or reponses(rapport):
        return None
    texte = ' '.join(p.get('rendu_public', p.get('rendu', '')) for p in flux)
    return {'mode': 'dialogue', 'texte': texte, 'faits': [], 'proposition': None,
            '_texte_moteur': True}


def sceller(reponse, rapport):
    """Références à recontrôler sur la transaction réellement appliquée."""
    rapport = rapport or {}
    fixes = [p['id'] for p in rapport.get('emissions', [])
             if p.get('statut') == 'prononcee' and est_fixee(p) and 'joueur' in p.get('auditeurs', [])]
    if fixes:
        reponse['_repliques_moteur'] = fixes
    return reponse


def verifier_publication(monde, reponse):
    from .emissions import lire
    from .narration import segments
    passages = segments(reponse['texte'])
    attendus = []
    for ref in reponse.get('_repliques_moteur', []):
        p = next((p for p in lire(monde) if p['id'] == ref and est_fixee(p)
                  and 'joueur' in p['auditeurs']), None)
        fixes = segments(p.get('rendu_public', '')) if p else []
        if not fixes:
            from .monde import ErreurMonde
            raise ErreurMonde('Cette réponse ne conserve pas les mots de la réplique entendue.',
                f'repliques_moteur.emission : reçu {ref!r} ; rendu exact de cette émission audible, une seule fois.')
        attendus.extend(fixes)
    # L'ordre et la multiplicité appartiennent aux occurrences du registre.
    # Deux émissions aux mêmes mots restent deux émissions distinctes.
    if [s for s in passages if s in attendus] != attendus:
        from .monde import ErreurMonde
        raise ErreurMonde('Cette réponse ne conserve pas les mots des répliques entendues.',
            f'repliques_moteur.texte : reçu {reponse["texte"]!r} ; rendus enregistrés dans leur ordre et leur multiplicité : {attendus!r}.')
    if reponse.get('_texte_moteur') and reponse.get('_repliques_moteur'):
        permis = {s for p in lire(monde) if 'joueur' in p['auditeurs']
                  for s in segments(p.get('rendu_public', p.get('rendu', '')))}
        if any(s not in permis for s in passages):
            from .monde import ErreurMonde
            raise ErreurMonde('Cette réponse contient des mots non fixés par le moteur.',
                f'repliques_moteur.texte : reçu {reponse["texte"]!r} ; seuls les rendus des émissions audibles enregistrées.')
