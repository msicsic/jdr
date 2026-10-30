"""G17 : mots comptables dérivés des seules résolutions typées, avant publication."""
import copy


def dossier(monde, rapport):
    faits = {}
    from .biens import etat_comptes_joueur, offres_joueur
    faits["comptes"] = {"etat": etat_comptes_joueur(monde, monde.contexte()["interlocuteurs"]),
                        "issue": rapport.get("comptes", []),
                        "offres_a_dire": rapport.get("offres", []),
                        "offres": offres_joueur(monde) + rapport.get("offres", [])}
    from .temps import instant
    faits['comptes']['instant'] = instant(monde)
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
    if r.get('mandat_joueur'):
        return r['mots']
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
        if r.get('refus_par') == 'joueur':
            debut.append("Tu refuses cet échange.")
        else:
            debut.extend(["Je refuse cet échange.", r['delai']['message'] if r.get('delai') else causes[r['cause']]])
        debut.append("Aucun règlement n'est effectué pour cet échange.")
    elif r.get('etat') == 'accepte':
        debut.append("J'accepte cet échange.")
        contenu = operation.get('contenu', {})
        if any('limite' in contenu.get(k, {}) for k in ('demande', 'contrepartie')):
            debut.append("Les pièces convenues sont payées maintenant, une seule fois.")
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


# Compatibilité des appelants G17 ; le contrat de publication est commun.
from .repliques_moteur import admettre, reponse, sceller, verifier_publication
