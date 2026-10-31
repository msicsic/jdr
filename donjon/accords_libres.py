"""Orientation sans effet vers le choix direct ; jamais une parole ou un accord."""
import copy
import re

from .monde import ErreurMonde, normaliser
from .propositions import schema_terme, compiler_limites
from .temps import instant

REFUS = {
    'paiement_differe': 'Cet accord ne peut pas différer le paiement : les pièces sont payées maintenant.',
    'pret_date': 'Cet accord ne peut pas porter un prêt daté : la restitution demande un autre contrat.',
    'maintien_continu': 'Cet accord porte une prestation ponctuelle, pas le maintien continu d’un état.',
    'alternative': 'Cet accord ne peut pas porter une clause alternative : aucune branche ne sera exécutée séparément.',
}
_prestations = []
for _forme in schema_terme(service=True)['anyOf']:
    if ('limite' in _forme['properties'] or
            _forme['properties']['type']['enum'][0] not in ('part', 'tache')):
        continue
    _forme = copy.deepcopy(_forme)
    if 'condition' in _forme['properties']:
        _forme['properties']['condition']['anyOf'] = [c for c in _forme['properties']['condition']['anyOf']
                                                      if 'echeance' not in c['properties']]
    _prestations.append(_forme)
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'destinataire': {'type': 'string'},
    'prestation': {'anyOf': [*_prestations, {'type': 'null'}]},
    'prix': {'anyOf': [{'type': 'integer', 'minimum': 1}, {'type': 'null'}]},
    'duree_ecrite': {'type': 'string', 'description': 'Fragment exact des mots donnant le délai, ou vide. Aucun calcul de date.'},
    'obstacle': {'type': 'string', 'enum': ['', *REFUS]},
}, 'required': ['destinataire', 'prestation', 'prix', 'duree_ecrite', 'obstacle']}
REGLES = """
## Accord à préparer (mode accord, texte vide)
Une offre comportant une clause temporelle ouvre le choix direct, sans parler.
proposition = {destinataire, prestation, prix, duree_ecrite, obstacle}.
destinataire est une référence publique perçue ; prestation est le terme demandé
à ce destinataire, prix les pièces que Corvus offre maintenant. Inconnu : chaîne
vide ou null selon le champ. Le joueur corrige et valide au formulaire.
duree_ecrite cite exactement le fragment temporel du message ; ne convertis
aucun mot en date ni en nombre. Un repère sans durée explicite reste à remplir.
Toute clause de paiement différé, prêt daté, maintien continu ou alternative
est un obstacle portant sur l’accord entier : obstacle vaut respectivement
paiement_differe, pret_date, maintien_continu, alternative. Sinon obstacle vide.
Ce mode remplace parole_joueur pour ces offres, y compris les interpellations.
Aucune réplique de Corvus ou de PNJ : ni accord, ni refus de personnage inventé.
"""


def secondes_ecrites(expression, saisie):
    """Grammaire bornée de durées explicites ; l'inconnu reste un champ vide.

    Les mots de nombre ne servent qu'à lire une quantité avec une unité de
    durée ; aucun mot de calendrier n'est traduit en durée.
    """
    e, s = normaliser(expression), normaliser(saisie)
    if not e or e not in s:
        return None
    e = re.sub(r"^(?:dans|avant|d'ici|au plus tard dans)\s+", '', e)
    petits = dict(zip(('zero un deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze seize').split(), range(17)))
    petits['une'] = 1
    dizaines = {'vingt': 20, 'trente': 30, 'quarante': 40, 'cinquante': 50, 'soixante': 60}
    def nombre(mots):
        if re.fullmatch(r'[0-9]{1,9}', mots):
            return int(mots)
        tokens = mots.replace('-', ' ').split()
        if tokens == ['une']:
            return 1
        if len(tokens) == 1:
            return petits.get(tokens[0], dizaines.get(tokens[0]))
        # Cardinal composé : dizaine + unité, avec « et » facultatif.
        tokens = [t for t in tokens if t != 'et']
        if len(tokens) == 2 and tokens[0] in dizaines and tokens[1] in petits:
            return dizaines[tokens[0]] + petits[tokens[1]]
        return None
    morceaux = re.findall(r'(.+?)\s+(secondes?|minutes?|heures?)(?:\s+|$)', e)
    if not morceaux or ' '.join(n + ' ' + u for n, u in morceaux) != e:
        return None
    total = 0
    for n, u in morceaux:
        valeur = nombre(n)
        if valeur is None:
            return None
        total += valeur * (3600 if u.startswith('heure') else 60 if u.startswith('minute') else 1)
    return total


def ouvrir(monde, p, saisie):
    from .accords_publics import accords_publics
    if isinstance(p, dict) and ('alternatives' in p or 'obstacle' in p and 'prestation' not in p):
        from .negociation import ouvrir as ouvrir_aide
        return ouvrir_aide(monde, p)
    if not isinstance(p, dict) or set(p) != set(SCHEMA['required']) or p.get('obstacle') not in ('', *REFUS):
        raise ErreurMonde('Précise les clauses de cet accord dans le choix direct.',
                          f'accord reçu {p!r} ; attendu {SCHEMA["required"]}.')
    if p['obstacle']:
        return {'mode': 'dialogue', 'texte': REFUS[p['obstacle']] + ' Rien n’a été dit ni engagé.',
                'faits': [], 'proposition': None, '_texte_moteur': True}
    if p['prestation'] is not None:
        from .propositions import erreur_terme
        erreur = erreur_terme(p['prestation'], False)
        if erreur:
            suffixe, recu, attendu = erreur
            raise ErreurMonde('Précise toutes les clauses de cette prestation.',
                              f'proposition.prestation{suffixe} : reçu {recu!r} ; attendu {attendu}.')
    public = accords_publics(monde)
    initial = {}
    if p['destinataire'] in [x['id'] for x in public['destinataires']]:
        initial['destinataire'] = p['destinataire']
    for x in public['prestations']:
        if p['prestation'] == x['terme']:
            initial['prestation'] = copy.deepcopy(x['terme'])
            break
    if type(p['prix']) is int and 1 <= p['prix'] <= public['or']:
        initial['prix'] = p['prix']
    duree = secondes_ecrites(p['duree_ecrite'], saisie) if isinstance(p['duree_ecrite'], str) else None
    # E5 exprime ses délais en minutes entières. Les autres durées restent à
    # préciser au formulaire ; aucune approximation ni valeur sans unité.
    if duree is not None and duree > 0 and duree % 60 == 0:
        initial['limite'] = compiler_limites([{'type': 'proposition',
            'demande': {'limite': {'dans_secondes': duree}}}], instant(monde))[0]['demande']['limite']
    return {'mode': 'dialogue', 'texte': 'Prépare cet accord dans le formulaire. Les champs manquants restent à préciser ; rien n’a été dit ni engagé.',
            'faits': [], 'proposition': None, '_texte_moteur': True,
            '_formulaire_accord': {'public': public, 'initial': initial}}


def depuis_parole(monde, p, saisie, *, marches=False):
    """Raccord E6, puis marchés relus : aucune proposition n'est exécutée ici."""
    for c in p.get('contenu', []):
        if c.get('type') == 'proposition':
            from .propositions import erreur_terme
            if set(c) != {'type', 'demande', 'contrepartie'}:
                raise ErreurMonde('Précise les clauses de ce marché.',
                                  f'contenu : reçu {c!r} ; attendu type, demande, contrepartie.')
            for nom in ('demande', 'contrepartie'):
                erreur = erreur_terme(c[nom], nom == 'contrepartie')
                if erreur:
                    suffixe, recu, attendu = erreur
                    raise ErreurMonde('Précise toutes les clauses de ce marché.',
                                      f'contenu.{nom}{suffixe} : reçu {recu!r} ; attendu {attendu}.')
        if c.get('type') == 'proposition' and marches:
            from .accords_publics import accords_publics, parole_accord
            if len(p['contenu']) != 1:
                raise ErreurMonde('Compose ce marché séparément des autres actes de parole.',
                                  f'contenu : reçu {p["contenu"]!r} ; attendu une seule proposition indivisible.')
            d = {'geste': 'accord', 'cible': p.get('personnage', ''),
                 'parametres': {k: copy.deepcopy(c[k]) for k in ('demande', 'contrepartie')}}
            parole_accord(monde, d)  # Admission publique et typée, sans verdict ni effet.
            return {'mode': 'dialogue', 'texte': 'Prépare ce marché dans le formulaire ; rien n’a été dit ni engagé.',
                    'faits': [], 'proposition': None, '_texte_moteur': True,
                    '_formulaire_accord': {'public': accords_publics(monde),
                        'initial': {'destinataire': d['cible'], **copy.deepcopy(d['parametres'])}}}
        if c.get('type') == 'proposition' and any('limite' in c.get(k, {}) for k in ('demande', 'contrepartie')):
            if len(p['contenu']) != 1 or set(c['contrepartie']) != {'type', 'montant'} or c['contrepartie']['type'] != 'pieces':
                raise ErreurMonde('Précise tous les termes de cet accord daté dans le choix direct.',
                                  f'contenu : reçu {p["contenu"]!r} ; attendu une prestation ponctuelle contre des pièces présentes.')
            return ouvrir(monde, {'destinataire': p.get('personnage', ''),
                'prestation': {k: v for k, v in c['demande'].items() if k != 'limite'},
                'prix': c['contrepartie'].get('montant') if c['contrepartie'].get('type') == 'pieces' else None,
                'duree_ecrite': '', 'obstacle': ''}, saisie)
    return None
