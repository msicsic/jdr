"""Comptes publics : rendu exact et lecture grammaticale locale des paroles.

La lecture couvre une grammaire bornée (rôles pronominaux, nombres et prédicats
comptables), pas toute la sémantique du français. Aucun verdict du MJ ne fait preuve.
"""
import re

from .monde import normaliser
from .refus import audit
from .francais import groupe_nominal, quantite, designer

# Lexique grammatical, partagé par toutes les personnes et tous les biens.
NOMBRES = dict(zip(('zero un deux trois quatre cinq six sept huit neuf dix onze douze '
                   'treize quatorze quinze seize').split(), range(17)))
NOMBRES.update(une=1, vingt=20, trente=30, quarante=40, cinquante=50,
               soixante=60, cent=100, mille=1000, million=1_000_000)
VERBES = re.compile(r"\b(?P<devoir>dois|doit|devons|devez|doivent|devrai\w*|devra\w*)\b"
    r"|\b(?P<remettre>remets?|remett\w*|remettr\w*|remis\w*)\b"
    r"|\b(?P<rendre>rends?|rendent|rendr\w*|rendu\w*)\b"
    r"|\b(?P<donner>donn\w*)\b"
    r"|\b(?P<payer>pai(?:e|es|ent|erai|eras|era|erons|erez|eront)|"
    r"pay(?:er|e|es|ee|ees|ons|ez|ent|ais|ait|ions|iez|aient|ai|as|a|ant))\b"
    r"|\b(?P<recevoir>recoi\w*|recu\w*|recev\w*)\b"
    r"|\b(?P<prendre>prends?|prennent|prendr\w*|pris\w*)\b")
DETTE = re.compile(r"\b(?:dette|dettes|creance|creances|debiteur|creancier|rembours\w*|paiement)\b")
CITATIONS = re.compile(r'«([^»]*)»')
VERBE_CONDITION = re.compile(VERBES.pattern + r'|\b(?P<rapporter>rapport\w*|apport\w*)\b')


def nombre(mots):
    mots = normaliser(mots)
    if re.fullmatch(r'-?\d+', mots): return int(mots)
    mots = mots.replace('-', ' ').split()
    signe = -1 if mots and mots[0] == 'moins' else 1
    if signe == -1: mots = mots[1:]
    if len(mots) == 1 and mots[0].isdigit(): return signe * int(mots[0])
    mots = [m[:-1] if m.endswith('s') and m[:-1] in NOMBRES else m for m in mots]
    if not mots or any(m not in NOMBRES and m != 'et' for m in mots):
        return None
    total, courant, precedent = 0, 0, ''
    for mot in mots:
        if mot == 'et': continue
        n = NOMBRES[mot]
        if n == 100:
            courant = max(1, courant) * n
        elif n >= 1000:
            total += max(1, courant) * n
            courant = 0
        elif mot == 'vingt' and precedent == 'quatre':
            courant += 76
        else:
            courant += n
        precedent = mot
    return signe * (total + courant)


def montant(texte):
    for m in re.finditer(r'\bpieces?\b', texte):
        avant = re.findall(r"[\w-]+", texte[:m.start()])
        for debut in range(len(avant)):
            n = nombre(' '.join(avant[debut:]))
            if n is not None: return n
    return None


def offres(faits):
    dossier = faits.get('comptes', {})
    resultat = []
    for champ in ('offres', 'offre'):
        valeur = dossier.get(champ, [])
        for offre in ([valeur] if isinstance(valeur, dict) else valeur):
            if offre not in resultat: resultat.append(offre)
    return resultat


def personnes(faits):
    resultat = {}
    for ref, o in faits.get('interlocuteurs', {}).items():
        resultat[ref] = o.get('nom', ref)
    for cle, o in faits.items():
        if cle.startswith('objet:') and isinstance(o, dict) and o.get('type') == 'personnage':
            resultat.setdefault(cle[6:], o.get('nom', cle[6:]))
    return resultat


def objets_publics(faits):
    return {**faits.get('comptes', {}).get('biens_offres', {}),
            **{cle[6:]: o for cle, o in faits.items()
               if cle.startswith('objet:') and isinstance(o, dict)}}


def presenter_offres(faits, texte):
    """Sélection moteur conservée sur les relances : jamais le montant de la prose."""
    dossier = faits.get('comptes', {})
    retenues = list(dossier.get('offres_a_dire', []))
    for passage in CITATIONS.finditer(texte):
        qui = locuteur(texte[:passage.start()] + passage[0], faits)
        assertions = lire(passage[1], faits, qui)
        if assertions and any(a['etat'] == 'offre' for a in assertions):
            for o in offres(faits):
                if qui is None or o['debiteur'] == qui:
                    if o not in retenues: retenues.append(o)
    return {**faits, 'comptes': {**dossier, 'offres_a_dire': retenues}}


def references(texte, faits):
    trouves = []
    for ref, nom in personnes(faits).items():
        for forme in (ref, nom, nom.split(',')[0]):
            for m in re.finditer(r'(?<!\w)' + re.escape(normaliser(forme)) + r'(?!\w)', texte):
                trouves.append((m.start(), ref))
    return sorted(set(trouves))


def locuteur(passage, faits):
    prefixe = normaliser(passage.split('«')[0])
    refs = {ref for _, ref in references(prefixe, faits)}
    if len(refs) == 1: return refs.pop()
    repondent = (faits.get('conversation_validee') or {}).get('repondent', [])
    if len(repondent) == 1: return repondent[0]
    interlocuteurs = faits.get('interlocuteurs', {})
    return next(iter(interlocuteurs)) if len(interlocuteurs) == 1 else None


def clauses(texte):
    return [s.strip() for m in re.finditer(r'([^.;!?]+)([.;!?]|$)', texte)
            if m[2] != '?' for s in re.split(r'\bmais\b', m[1]) if s.strip()]


def roles(avant, faits, qui, apres='', preposition='à'):
    pronoms = list(re.finditer(r"\b(je|j|tu|il|elle|nous|vous)\b", avant))
    sujet = 'joueur' if pronoms and pronoms[-1][1] in ('tu', 'vous') else qui
    noms = references(avant, faits)
    if noms and (not pronoms or noms[-1][0] > pronoms[-1].start()): sujet = noms[-1][1]
    receveur = 'joueur' if sujet != 'joueur' else qui
    objets = list(re.finditer(r"\b(me|m|te|t|lui|leur)\b", avant))
    if objets:
        pronom = objets[-1][1]
        receveur = qui if pronom in ('me', 'm') else 'joueur' if pronom in ('te', 't') else None
    complements = set()
    for ref, nom in personnes(faits).items():
        for forme in (nom, nom.split(',')[0]):
            complement = normaliser(groupe_nominal(forme, preposition))
            if re.search(r'(?<!\w)' + re.escape(complement) + r'(?!\w)', apres): complements.add(ref)
    for pronom, ref in (('moi', qui), ('toi', 'joueur')):
        if re.search(r'\b' + normaliser(preposition) + r'\s+' + pronom + r'\b', apres): complements.add(ref)
    if len(complements) > 1: receveur = None
    elif complements:
        cible = complements.pop()
        receveur = None if objets and cible != receveur else cible
    return sujet, receveur, bool(pronoms or noms)


def lire(texte, faits, qui):
    """Assertions monétaires explicites ; None pour un rôle grammatical ambigu."""
    assertions = []
    for brute in clauses(texte):
        clause = normaliser(brute)
        entete = re.split(r'\b(?:si|contre)\b', clause, maxsplit=1)[0].strip()
        verbe = VERBES.search(entete)
        objets = {ref for ref, o in objets_publics(faits).items()
                  if o.get('type') != 'personnage'
                  and any(nom and re.search(r'(?<!\w)' + re.escape(normaliser(nom)) + r'(?!\w)', clause)
                          for nom in (o.get('nom', ''), *o.get('aliases', [])))}
        objet = next(iter(objets)) if len(objets) == 1 else None
        comptes_objets = {c.get('objet') for c in faits.get('comptes', {}).get('issue', [])
                          + faits.get('comptes', {}).get('etat', []) if c.get('objet')}
        n = montant(clause)
        unite = bool(re.search(r'\bpieces?\b', clause))
        fragment = re.match(r"([\w -]+?)\s+pieces?\s*(?:,|$)", entete)
        nominal = bool(fragment and nombre(fragment[1]) is not None)
        # Un nom de salle ou un nombre de pièces sans prédicat monétaire ne
        # devient pas une dette. Le nominal monétaire est une quantité offerte.
        absence_personnelle = bool(verbe and verbe.lastgroup == 'devoir'
            and re.search(r'\b(?:me|m|te|t|lui|leur)\b', entete[:verbe.start()])
            and re.search(r'\brien\b', entete[verbe.end():]))
        domaine = bool(DETTE.search(clause) or verbe and (unite or objet in comptes_objets
                       or verbe.lastgroup == 'payer' or absence_personnelle)
                       or nominal and offres(faits))
        if not domaine: continue
        if qui is None: return None
        avant = entete[:verbe.start()] if verbe else entete
        genre = verbe.lastgroup if verbe else 'donner'
        apres = entete[verbe.end():] if verbe else ''
        sujet, receveur, explicite = roles(avant, faits, qui, apres,
                                         'de' if genre in ('prendre', 'recevoir') else 'à')
        if receveur is None: return None
        if genre in ('prendre', 'recevoir'):
            # Sans sujet, l'impératif s'adresse au joueur.
            if not explicite: sujet, receveur = 'joueur', qui
            sujet, receveur = receveur, sujet
        negatif = bool(re.search(r'\b(?:pas|rien|aucun|aucune)\b', clause))
        condition = bool(re.search(r'\b(?:si|contre)\b', clause))
        etat = ('absent' if negatif else 'du') if genre == 'devoir' or DETTE.search(clause) else (
            'du' if negatif else 'offre' if condition or nominal else 'rendu')
        if n == 0 and (genre == 'devoir' or DETTE.search(clause)): etat = 'absent'
        if etat == 'absent': n = 0
        assertions.append({'debiteur': sujet, 'creancier': receveur, 'etat': etat,
                           'montant': n, 'reciproque': bool(re.search(r'\bentre nous\b', clause)),
                           'objet': objet, 'monetaire': unite, 'texte': clause, 'locuteur': qui})
    return assertions


def compatibles(a, faits):
    dossier = faits.get('comptes', {})
    candidats = offres(faits) if a['etat'] == 'offre' else (
        dossier.get('issue', []) + dossier.get('etat', []))
    candidats = [c for c in candidats if (c['debiteur'], c['creancier']) ==
                  (a['debiteur'], a['creancier'])]
    if a['reciproque']:
        dettes = dossier.get('issue', []) + dossier.get('etat', [])
        if any(c.get('etat') == 'du' and not c.get('objet') and c.get('montant', 0) > 0
               and {c['debiteur'], c['creancier']} == {a['debiteur'], a['creancier']} for c in dettes):
            return []
    resultat = []
    for c in candidats:
        if c.get('etat') != a['etat']: continue
        if a['etat'] == 'offre':
            terme = c['contrepartie']
            if terme['type'] != 'pieces': continue
            n = terme['montant']
            condition = c['condition']
            subordonnees = re.split(r'\b(?:si|contre)\b', a['texte'], maxsplit=1)
            if len(subordonnees) > 1:
                subordonnee = subordonnees[1]
                verbe = VERBE_CONDITION.search(subordonnee)
                if verbe:
                    de, vers, _ = roles(subordonnee[:verbe.start()], faits, a['locuteur'], subordonnee[verbe.end():])
                    if (de, vers) != (c['creancier'], c['debiteur']): continue
                if condition['type'] == 'pieces':
                    recu = montant(subordonnee)
                    if recu is not None and recu != condition['montant']: continue
            cible = condition.get('objet') or condition.get('condition', {}).get('objet')
            # Si le texte cite un autre objet connu, le montant seul ne suffit pas.
            for ref, o in objets_publics(faits).items():
                if o.get('type') == 'personnage' or ref == cible: continue
                noms = [o.get('nom', ''), *o.get('aliases', [])]
                if any(nom and re.search(r'(?<!\w)' + re.escape(normaliser(nom)) + r'(?!\w)', a['texte']) for nom in noms):
                    break
            else:
                if a['montant'] is None or a['montant'] == n: resultat.append(c)
            continue
        if c.get('objet'):
            if c['objet'] != a.get('objet'): continue
        elif a.get('objet') and not a['monetaire']: continue
        if a['montant'] is None or a['montant'] == c['montant']:
            resultat.append(c)
    return resultat


def phrases(faits):
    """Une phrase moteur par compte public, offres typées comprises."""
    def personne(ref):
        if ref == 'joueur': return 'toi'
        nom = personnes(faits).get(ref, 'une personne')
        return nom + ',' if ',' in nom and not nom.endswith(',') else nom
    textes = []
    for c in faits.get('comptes', {}).get('issue', []):
        if 'joueur' not in (c['debiteur'], c['creancier']): continue
        de = groupe_nominal(personne(c['debiteur']), 'de')
        vers = groupe_nominal(personne(c['creancier']), 'à')
        if c.get('objet'):
            bien = faits.get('objet:' + c['objet'], {}).get('nom', 'le bien convenu')
            q = f"{c['montant']} × {bien}"
        else:
            q = quantite(c['montant'], 'pièce')
        if c['etat'] == 'rendu': texte = f'Remise effectuée : {de} {vers}, {q}.'
        elif c['etat'] == 'du': texte = f'Reste dû : {de} {vers}, {q}.'
        elif c['etat'] == 'absent':
            texte = f"Aucune dette {de} envers {personne(c['creancier'])} pour " + (bien if c.get('objet') else 'les pièces') + '.'
        else:
            from .monde import ErreurMonde
            raise ErreurMonde('Ce compte ne peut pas encore être raconté.',
                              f"comptes.issue.etat : reçu {c['etat']!r} ; du, rendu ou absent")
        textes.append(texte)
    dossier = faits.get('comptes', {})
    biens = objets_publics(faits)
    def bien(ref, determine=True):
        o = biens.get(ref)
        return (designer(o) if determine else o['nom']) if o else 'le bien convenu'
    def terme(t):
        if t['type'] == 'pieces': return quantite(t['montant'], 'pièce')
        if t['type'] == 'rien': return 'rien'
        if t['type'] == 'tache':
            c = t['condition']
            nom = bien(c['objet'])
            if 'servir' in c:
                return ("le service d'une part " + groupe_nominal(bien(c['objet'], False), 'de')
                        + ' ' + groupe_nominal(personne(c['servir']), 'pour')).rstrip(',')
            if 'remettre' in c:
                return ('la remise ' + groupe_nominal(nom, 'de') + ' '
                        + groupe_nominal(personne(c['remettre']), 'à')).rstrip(',')
            if 'lieu' in c:
                return 'le déplacement ' + groupe_nominal(nom, 'de') + ' vers le lieu convenu'
            action = (('allumage' if c['allume'] else 'extinction') if 'allume' in c else
                      ('verrouillage' if c['verrouillee'] else 'déverrouillage'))
            return designer({'nom': action}) + ' ' + groupe_nominal(nom, 'de')
        nom = bien(t['objet'], determine=t['type'] != 'part')
        return 'une part ' + groupe_nominal(nom, 'de') if t['type'] == 'part' else nom
    actives = dossier.get('offres_a_dire', offres(faits))
    for o in offres(faits):
        if o not in actives: continue
        rendu = (f"Offre {groupe_nominal(personne(o['debiteur']), 'de')} "
                 f"{groupe_nominal(personne(o['creancier']), 'à')} : "
                 f"{terme(o['contrepartie'])} contre {terme(o['condition'])}.")
        if 'joueur' in (o['debiteur'], o['creancier']): textes.append(rendu)
    return list(dict.fromkeys(textes))


def completer(texte, faits):
    from .narration import segments
    moteurs = {s for cle in ('conversation_validee', 'resultat_resolu')
               for t in (faits.get(cle) or {}).get('faits', []) for s in segments(t)}
    requis = phrases(faits)
    canoniques = list(dict.fromkeys(s for p in requis for s in segments(p)))
    passages = segments(texte)
    gardes = []
    for passage in passages:
        # Une ancienne phrase moteur du même compte est remplacée, sans toucher
        # aux paroles libres ni créditer une paraphrase du MJ comme preuve.
        assertions = lire(passage, faits, locuteur(passage, faits)) if passage in moteurs else []
        if (passage not in canoniques and assertions and all(compatibles(a, faits) for a in assertions)
                and not CITATIONS.search(passage)):
            continue
        gardes.append(passage)
    presents = set(gardes)
    base = texte.strip() if len(gardes) == len(passages) else ' '.join(gardes)
    return ' '.join([base, *(s for s in canoniques if s not in presents)]).strip()


def controler(texte, faits, partie='texte', locuteurs=None, avant_audit=False):
    from .narration import segments, textes_etablis
    etablis = textes_etablis(faits)
    passages = segments(texte)
    obstacles = []
    for i, passage in enumerate(passages):
        if passage in etablis: continue
        citations = CITATIONS.findall(passage)
        qui = locuteur(passage, faits)
        if locuteurs is not None: qui = locuteurs.get(i) or qui
        extraits = [(CITATIONS.sub('', passage), None)] + [(c, qui) for c in citations]
        for extrait, auteur in extraits:
            assertions = lire(extrait, faits, auteur)
            # Avant l'audit, une attribution absente est différée à son locuteur
            # typé. L'enregistrement refait la même comparaison avec ce locuteur.
            if assertions is None and citations and avant_audit: continue
            if assertions is None or any(not compatibles(a, faits) for a in assertions):
                obstacles.append(audit('Ce compte ne correspond pas aux comptes du moteur.',
                    f"comptes.issue : {faits.get('comptes', {}).get('issue', [])} ; "
                    f"comptes.offres : {offres(faits)} ; reçu {assertions!r} ; "
                    'une parole aux mêmes rôles, état et montant, ou un texte sans compte',
                    partie=partie, segment=i, texte=passage, recu=extrait))
    for phrase in dict.fromkeys(s for p in phrases(faits) for s in segments(p)):
        if phrase not in passages:
            obstacles.append(audit("Le texte moteur d'un compte manque.",
                f'comptes.issue/offres : conserver exactement {phrase!r}',
                partie=partie, segment=0, texte=texte, recu=texte))
    return obstacles
