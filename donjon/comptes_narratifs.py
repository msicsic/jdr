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
    return {**{cle[6:]: o for cle, o in faits.items()
               if cle.startswith('objet:') and isinstance(o, dict)},
            **faits.get('comptes', {}).get('biens_offres', {})}


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
    return [s.strip() for m in re.finditer(r'([^.;!?:]+)([.;!?:]|$)', texte)
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


def comptable(texte, faits):
    """Domaine grammatical commun ; un complément de lieu n'est pas une monnaie."""
    for brute in clauses(texte):
        clause = normaliser(brute)
        if DETTE.search(clause): return True
        verbe = VERBES.search(clause)
        if (verbe and verbe.lastgroup == 'devoir'
                and re.search(r"\b(?:me|m|te|t|lui|leur)\b", clause[:verbe.start()])
                and re.search(r'\brien\b', clause[verbe.end():])): return True
        for unite in re.finditer(r'\bpieces?\b', clause):
            prefixe = clause[:unite.start()]
            predicats = list(VERBES.finditer(prefixe))
            avant_unite = prefixe[predicats[-1].end():] if predicats else prefixe
            # Prépositions de lieu : elles relient le geste à la salle, jamais
            # le verbe de transfert à un complément monétaire.
            locatif = re.search(r'\b(?:dans|parmi|devant|derriere|hors|sur|sous|vers|depuis|autour)\b', avant_unite)
            if locatif: continue
            n = montant(clause[:unite.end()])
            if n is not None and (n != 1 or re.search(r'\b1\s*$', prefixe)):
                return True
            if predicats: return True
        # Les biens dus sont identifiés par le même registre public que les
        # pièces ; aucune liste d'objets ou de scénarios.
        ids = {c.get('objet') for c in faits.get('comptes', {}).get('issue', [])
               + faits.get('comptes', {}).get('etat', []) if c.get('objet')}
        ids.update(faits.get('comptes', {}).get('parts', {}).values())
        if verbe and any(ref in ids and any(nom and re.search(r'(?<!\w)' + re.escape(normaliser(nom))
                + r'(?!\w)', clause) for nom in (o.get('nom', ''), *o.get('aliases', [])))
                for ref, o in objets_publics(faits).items()): return True
    return False


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
        if not comptable(brute, faits): continue
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
        if verbe is None and not DETTE.search(clause) and not condition and not nominal:
            etat = None  # Quantité présentée sans verbe de transfert : ne pas en inventer un.
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
        if a['etat'] is not None and c.get('etat') != a['etat']: continue
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
            if (c['objet'] != a.get('objet')
                    and dossier.get('parts', {}).get(c['objet']) != a.get('objet')): continue
        elif a.get('objet') and not a['monetaire']: continue
        if a['montant'] is None or a['montant'] == c['montant']:
            resultat.append(c)
    return resultat


def phrases(faits):
    """Rendu naturel de l'état final, sans répéter soldes nuls et offres conclues."""
    def personne(ref):
        return 'toi' if ref == 'joueur' else personnes(faits).get(ref, 'une personne').split(',')[0]

    biens = objets_publics(faits)
    parts = faits.get('comptes', {}).get('parts', {})
    services = faits.get('comptes', {}).get('services', [])
    def quantite_compte(c):
        o = biens.get(c['objet'])
        if c['objet'] in parts:
            parent = biens.get(parts[c['objet']])
            nom = (parent['nom'] if c['objet'] in services else designer(parent)) if parent else 'le bien convenu'
            return ('une part' if c['montant'] == 1 else quantite(c['montant'], 'part')) + ' ' + groupe_nominal(nom, 'de')
        if not o: return 'le bien convenu'
        return designer(o, article='indefini') if c['montant'] == 1 else quantite(c['montant'], o['nom'])

    issue = faits.get('comptes', {}).get('issue', [])
    comptes = [c for i, c in enumerate(issue) if c not in issue[:i]
               and 'joueur' in (c['debiteur'], c['creancier'])]
    # Le remboursement dit déjà le transfert ; le solde nul n'ajoute pas une
    # seconde annonce du même règlement.
    comptes = [c for c in comptes if not (c['etat'] == 'absent' and any(
        a['etat'] == 'rendu' and a['montant'] > 0 and all(a[k] == c[k] for k in
        ('debiteur', 'creancier', 'objet')) for a in comptes))]
    textes, utilises, paiements = [], set(), []
    for i, c in enumerate(comptes):
        if i in utilises: continue
        de, vers = c['debiteur'], c['creancier']
        nom = personne(de if vers == 'joueur' else vers)
        q = quantite_compte(c) if c['objet'] else quantite(c['montant'], 'pièce')
        if c['etat'] == 'rendu':
            if de == 'joueur':
                texte = ('Tu remets ' + q if c['objet'] else 'Tu paies ' + q) + ' ' + groupe_nominal(nom, 'à')
                suite = next(((j, a) for j, a in enumerate(comptes) if j != i and j not in utilises
                    and a['debiteur'] == vers and a['creancier'] == 'joueur' and a['objet']
                    and a['etat'] in ('du', 'rendu')), None)
                if suite:
                    j, a = suite
                    verbe = 'servir' if a['objet'] in services else 'remettre'
                    texte += ', qui ' + ('doit encore te ' + verbe if a['etat'] == 'du' else 'te remet') + ' ' + quantite_compte(a)
                    utilises.add(j)
                elif not c['objet']:
                    paiements.append((len(textes), c))
            else:
                texte = groupe_nominal(nom, debut=True) + (' te remet ' if c['objet'] else ' te rend ') + q
                suite = next(((j, a) for j, a in enumerate(comptes) if j != i and j not in utilises
                    and not a['objet'] and a['etat'] == 'du' and a['debiteur'] == de
                    and a['creancier'] == vers), None) if not c['objet'] else None
                if suite:
                    j, a = suite
                    texte += ' et te doit encore ' + quantite(a['montant'], 'pièce')
                    utilises.add(j)
        elif c['etat'] == 'du':
            if c['objet']:
                verbe = 'servir' if c['objet'] in services else 'remettre'
                texte = ('Tu dois encore ' + verbe + ' ' + q + ' ' + groupe_nominal(nom, 'à') if de == 'joueur'
                         else groupe_nominal(nom, debut=True) + ' doit encore te ' + verbe + ' ' + q)
            else:
                texte = ('Tu dois encore ' + q + ' ' + groupe_nominal(nom, 'à') if de == 'joueur'
                         else groupe_nominal(nom, debut=True) + ' te doit encore ' + q)
        elif c['etat'] == 'absent':
            if c['objet']:
                texte = ('Tu ne remets pas ' + q + ' ' + groupe_nominal(nom, 'à') if de == 'joueur'
                         else groupe_nominal(nom, debut=True) + ' ne te remet pas ' + q)
            else:
                texte = ('Tu ne dois aucune pièce ' + groupe_nominal(nom, 'à') if de == 'joueur'
                         else groupe_nominal(nom, debut=True) + ' ne te doit aucune pièce')
        else:
            from .monde import ErreurMonde
            raise ErreurMonde('Ce compte ne peut pas encore être raconté.',
                              f"comptes.issue.etat : reçu {c['etat']!r} ; du, rendu ou absent")
        textes.append(texte + '.')
        utilises.add(i)
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
    conclues = (faits.get('conversation_validee') or {}).get('offres_conclues', [])
    couvertes = []
    for indice, c in paiements:
        candidats = [o for o in offres(faits) if o in conclues
                     and (o['debiteur'], o['creancier']) == (c['debiteur'], c['creancier'])
                     and o['contrepartie']['type'] == 'pieces'
                     and o['contrepartie']['montant'] == c['montant']]
        if len(candidats) == 1:
            o = candidats[0]
            if o['condition']['type'] != 'rien':
                textes[indice] = textes[indice][:-1] + ' pour ' + terme(o['condition']) + '.'
            couvertes.append(o)
    def en_compte(t):
        return t['type'] != 'tache' or any(k in t['condition'] for k in ('servir', 'remettre'))
    for o in offres(faits):
        if o not in actives or o in couvertes: continue
        if o in conclues and en_compte(o['condition']) and en_compte(o['contrepartie']): continue
        contre, condition = terme(o['contrepartie']), terme(o['condition'])
        rendu = (f"Tu offres {contre} {groupe_nominal(personne(o['creancier']), 'à')} contre {condition}."
                 if o['debiteur'] == 'joueur' else
                 f"{groupe_nominal(personne(o['debiteur']), debut=True)} t'offre {contre} contre {condition}.")
        if 'joueur' in (o['debiteur'], o['creancier']): textes.append(rendu)
    return list(dict.fromkeys(textes))


def completer(texte, faits):
    from .narration import segments
    moteurs = {s for cle in ('conversation_validee', 'resultat_resolu')
               for t in (faits.get(cle) or {}).get('faits', []) for s in segments(t)}
    remplaces = {s for cle in ('conversation_validee', 'resultat_resolu')
                 for t in (faits.get(cle) or {}).get('faits_comptables', []) for s in segments(t)}
    requis = phrases(faits)
    canoniques = list(dict.fromkeys(s for p in requis for s in segments(p)))
    passages = segments(texte)
    gardes = []
    for passage in passages:
        # Une ancienne phrase moteur du même compte est remplacée, sans toucher
        # aux paroles libres ni créditer une paraphrase du MJ comme preuve.
        if (passage not in canoniques and not CITATIONS.search(passage)
                and (passage in remplaces or passage in moteurs and requis and comptable(passage, faits))):
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
        narrateur = CITATIONS.sub('', passage)
        if comptable(narrateur, faits):
            obstacles.append(audit('Les comptes du narrateur sont écrits par le moteur.',
                'prose du narrateur sans compte ; conserver les phrases du moteur ; '
                f"comptes.issue : {faits.get('comptes', {}).get('issue', [])}",
                partie=partie, segment=i, texte=passage, recu=narrateur))
        for extrait in citations:
            if not comptable(extrait, faits): continue
            assertions = lire(extrait, faits, qui)
            if assertions is None and avant_audit: continue
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
