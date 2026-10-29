"""G17 : mots comptables dérivés des seules résolutions typées, avant publication."""
import copy


def dossier(monde, rapport):
    faits = {}
    from .biens import etat_comptes_joueur, offres_joueur
    faits["comptes"] = {"etat": etat_comptes_joueur(monde, monde.contexte()["interlocuteurs"]),
                        "issue": rapport.get("comptes", []),
                        "offres_a_dire": rapport.get("offres", []),
                        "offres": offres_joueur(monde) + rapport.get("offres", [])}
    # Noms grammaticaux des seuls biens cités par les termes publics :
    # aucune position, possession cachée ni propriété physique ajoutée.
    biens_offres = {c['objet'] for c in faits['comptes']['issue'] if c.get('objet') in monde.objets}
    parts = dict(rapport.get('parts_comptables', {}))
    services = []
    from .agendas import en_cours
    for c in faits['comptes']['issue']:
        if not c.get('objet') or c['debiteur'] not in monde.objets: continue
        for engagement in en_cours(monde, c['debiteur'], objet=c['objet']):
            condition = engagement['condition']
            if condition.get('servir') == 'joueur':
                parts[c['objet']] = c['objet']
                services.append(c['objet'])
            elif engagement.get('lot'):
                parts[c['objet']] = engagement['lot']
    faits['comptes'].update(parts=parts, services=services)
    biens_offres.update(parts.values())
    for offre in faits["comptes"]["offres"]:
        for terme in (offre["condition"], offre["contrepartie"]):
            bien = terme.get("objet") or terme.get("condition", {}).get("objet")
            if bien in monde.objets:
                biens_offres.add(bien)
    faits["comptes"]["biens_offres"] = {
        bien: {k: copy.deepcopy(monde.objets[bien][k]) for k in
               ("nom", "type", "genre", "pluriel", "nom_propre", "elision", "aliases")
               if k in monde.objets[bien]} for bien in biens_offres if bien in monde.objets}
    faits['comptes']['biens_offres'].update(rapport.get('biens_comptables', {}))
    return faits['comptes']


def difference(avant, apres):
    """Effets de cette opération, même si le journal cumule deux paiements."""
    resultat = []
    for indice, (anciens, nouveaux) in enumerate(zip(avant, apres)):
        for n, c in enumerate(nouveaux):
            if indice == 0:
                if n < len(anciens):
                    continue
                delta = c
            else:
                precedent = next((a for a in anciens if all(a[k] == c[k] for k in
                    ('debiteur', 'creancier', 'objet', 'etat'))), None)
                if precedent == c:
                    continue
                delta = {**c, 'montant': c['montant'] - (precedent['montant'] if precedent else 0)}
            if delta not in resultat:
                resultat.append(copy.deepcopy(delta))
    return resultat


def formuler(faits, auteur, operation):
    from .comptes_narratifs import phrases
    r = operation['resolution']
    cs, os = operation['comptes'], operation['offres']
    debut = []
    if r.get('mission'):
        from .francais import quantite
        accord = r['engagement'] or {}
        statut, op = accord.get('statut'), r['operation']
        if statut == 'paye':
            return 'La récompense de ' + quantite(accord['montant'], 'pièce') + ' a déjà été versée. Aucun nouveau paiement.'
        if statut == 'refuse':
            debut.append("Tu refuses cette offre. Aucun engagement ni paiement.")
        elif statut == 'accepte':
            debut.append("Nous avons un accord. Le paiement aura lieu à la remise du bien convenu.")
        elif statut == 'propose':
            debut.append("Cette offre attend ton accord. Aucun paiement n'a eu lieu.")
        else:
            return "Je n'ai pas les fonds nécessaires pour faire cette offre. Aucun paiement n'a lieu."
        if r['montant_demande'] > accord.get('montant', 0):
            debut.append('Je refuse le montant demandé de ' + quantite(r['montant_demande'], 'pièce') + '.')
        # Les termes restent visibles même après un refus, sans accord implicite.
        if not os and accord:
            os = operation.get('termes', [])
    causes = {
        'mefiance': "Je ne te fais pas confiance.", 'rancune': "Je t'en veux encore.",
        'deja': "Cette tâche fait déjà partie de notre engagement.",
        'qui_va_la': "Je ne sais pas qui me parle.", 'necessaire': "Ce bien m'est nécessaire.",
        'garde': "Je garde cette réserve pour mes besoins.",
        'impossible': "Je ne vois pas comment exécuter cette demande.",
        'propriete': "Un bien proposé n'appartient pas à celui qui le cède.",
        'absent': "Je n'ai pas le bien à remettre sur moi.", 'epuise': "La réserve est épuisée.",
        'pauvre': "Tu n'as pas les pièces offertes.", 'portee': "Nous sommes trop éloignés pour échanger.",
        'meme_bien': "Les deux termes désignent le même bien.",
        'marche': "Ce que j'y perds l'emporte sur ce que j'y gagne.",
        'persuasion': "Tu ne m'as pas convaincu.",
        'geste': "Je suis occupé à mon geste.", 'place': "Je n'ai pas la place de m'écarter.",
        'inutile': "Je ne te barre pas le passage."}
    if r.get('etat') == 'refuse':
        debut.extend(["Je refuse cet échange.", causes[r['cause']],
                      "Aucun règlement n'est effectué pour cet échange."])
    elif r.get('etat') == 'accepte':
        debut.append("J'accepte cet échange.")
    elif r.get('etat') == 'refus' and r.get('prix'):
        from .francais import quantite
        debut.append("Je refuse à ce prix. J'en demande " + quantite(r['prix'], 'pièce') + '.')
    elif r.get('etat') in ('paye', 'ecarte'):
        debut.append("Je m'écarte pour te laisser passer.")
    elif not cs and r.get('etat') == 'promis':
        debut.append("Je maintiens l'engagement déjà pris. Aucun nouveau règlement.")
    elif not cs and r.get('etat'):
        # L'absence d'effet n'est jamais formulée comme un paiement.
        debut.extend([causes.get(r['etat'], "Je ne conclus pas cet échange."),
                      "Aucun règlement n'est effectué."])
    if 'garde' in r.get('reglements', []):
        debut.append("Je refuse de te rembourser.")
    if 'sans_le_sou' in r.get('reglements', []):
        debut.append("Je n'ai pas de quoi te rembourser davantage.")
    # Une offre refusée garde ses deux termes, sans devenir un accord.
    if r.get('offre'):
        from .propositions import offre
        c = r['offre']
        os = [offre('joueur', auteur, c['demande'], c['contrepartie'])]
    f = {**faits, 'conversation_validee': {}, 'comptes': {
        **faits['comptes'], 'issue': cs, 'offres': os, 'offres_a_dire': os}}
    return ' '.join([*debut, *phrases(f, auteur)])


def admettre(monde, autorisations, rapport):
    """Remplace les autorisations comptables par des émissions déjà fixées.

    La copie préparée seule reçoit les mots ; sa transaction sera rejouée sur
    l'original avant sauvegarde et affichage. Aucune publication de brouillon.
    """
    from .emissions import enregistrer, lire
    from .ouie import auditeurs_parole
    from .voix import nom_pour_joueur
    faits = {'comptes': dossier(monde, rapport)}
    for a in list(autorisations):
        operations = a['evenement'].get('resolutions_comptables', [])
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
        mots = ' '.join(formuler(faits, auteur, op) for op in operations)
        couverts = [f for op in operations for f in op['faits']]
        autres = [f for f in a['evenement']['faits'] if f not in couverts]
        rendu = ' '.join([f'{nom_pour_joueur(monde, auteur)} : « {mots} »', *autres])
        evenement = {**a['evenement'], 'type': 'compte_parle',
            'emission_joueur': next((p['id'] for p in reversed(lire(monde)) if p['locuteur'] == 'joueur'), None)}
        emission = enregistrer(monde, auteur, acte='reponse_comptable', parametres=a['parametres'],
            modalite='refus' if any(op['resolution'].get('etat') == 'refuse' or
                'garde' in op['resolution'].get('reglements', []) for op in operations) else 'constat',
            evenement=evenement, a=['joueur'], auditeurs=auditeurs_parole(monde, auteur),
            texte=mots, rendu=rendu)
        if emission and 'joueur' in emission['auditeurs']:
            emission['rendu_public'] = rendu
        # Les faits des autres opérations sont rendus tels quels. Seul un
        # propos libre résiduel peut encore demander des mots au modèle.
        if a['parametres'].get('contenu_libre'):
            a['parametres']['contenu'] = []
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
    if not any(p['acte'] == 'reponse_comptable' for p in flux) or reponses(rapport):
        return None
    texte = ' '.join(p.get('rendu_public', p.get('rendu', '')) for p in flux)
    return {'mode': 'dialogue', 'texte': texte, 'faits': [], 'proposition': None,
            '_texte_moteur': True}


def sceller(reponse, rapport):
    """Références à recontrôler sur la transaction réellement appliquée."""
    fixes = [p['id'] for p in rapport.get('emissions', [])
             if p.get('acte') == 'reponse_comptable' and 'joueur' in p.get('auditeurs', [])]
    if fixes:
        reponse['_comptes_parles'] = fixes
    return reponse


def verifier_publication(monde, reponse):
    from .emissions import lire
    from .narration import segments
    passages = segments(reponse['texte'])
    attendus = []
    for ref in reponse.get('_comptes_parles', []):
        p = next((p for p in lire(monde) if p['id'] == ref and p['acte'] == 'reponse_comptable'
                  and 'joueur' in p['auditeurs']), None)
        fixes = segments(p.get('rendu_public', '')) if p else []
        if not fixes:
            from .monde import ErreurMonde
            raise ErreurMonde('Cette réponse ne conserve pas les mots du compte entendu.',
                f'comptes_parles.emission : reçu {ref!r} ; rendu exact de cette émission audible, une seule fois.')
        attendus.extend(fixes)
    # L'ordre et la multiplicité appartiennent aux occurrences du registre.
    # Deux émissions aux mêmes mots restent deux émissions distinctes.
    if [s for s in passages if s in attendus] != attendus:
        from .monde import ErreurMonde
        raise ErreurMonde('Cette réponse ne conserve pas les mots des comptes entendus.',
            f'comptes_parles.texte : reçu {reponse["texte"]!r} ; rendus enregistrés dans leur ordre et leur multiplicité : {attendus!r}.')
    if reponse.get('_texte_moteur') and reponse.get('_comptes_parles'):
        permis = {s for p in lire(monde) if 'joueur' in p['auditeurs']
                  for s in segments(p.get('rendu_public', p.get('rendu', '')))}
        if any(s not in permis for s in passages):
            from .monde import ErreurMonde
            raise ErreurMonde('Cette réponse contient des mots non fixés par le moteur.',
                f'comptes_parles.texte : reçu {reponse["texte"]!r} ; seuls les rendus des émissions audibles enregistrées.')
