"""K2 : alternatives publiques, admises sans parole ni verdict social."""
import copy

from .monde import ErreurMonde
from .propositions import schema_compilation


OBSTACLES = {
    'condition_succes': 'La condition de succès demandée ne peut pas être exprimée par ce marché.',
    'reglement_conditionnel': 'Le règlement conditionnel demandé ne peut pas être exprimé par ce marché.',
    'echeance_non_typee': 'Cette échéance doit être précisée dans le formulaire d’accord.',
    'clause_non_typee': 'Une clause demandée ne peut pas être exprimée par les termes de ce marché.',
}


def termes_aide(contrepartie=False):
    s = schema_compilation()['properties']['contrepartie' if contrepartie else 'demande']
    for f in s['anyOf']:
        if 'condition' in f['properties']:
            f['properties']['condition']['anyOf'] = [c for c in f['properties']['condition']['anyOf']
                                                      if 'echeance' not in c['properties']]
    return s


SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'obstacle': {'type': 'string', 'enum': ['', *OBSTACLES]},
    'alternatives': {'type': 'array', 'maxItems': 2, 'items': {
        'type': 'object', 'additionalProperties': False, 'properties': {
            'destinataire': {'type': 'string'},
            'demande': termes_aide(), 'contrepartie': termes_aide(True)},
        'required': ['destinataire', 'demande', 'contrepartie']}},
}, 'required': ['obstacle', 'alternatives']}

REGLES = """
## Assistance à la négociation (mode accord, texte vide)
À la demande d’aide pour négocier, ou pour une intention sociale libre qui
cherche un marché sans en fixer les termes, propose {obstacle, alternatives}.
alternatives contient au plus deux marchés {destinataire, demande, contrepartie},
composés des seuls termes du catalogue accords_negociables, avec montants de
pièces modifiables. Une limite ponctuelle explicite peut compléter une part
ou une tâche, avec des pièces présentes en face : limite={dans_secondes:N}
pour une durée donnée, ou un instant de jeu explicitement donné. Ne traduis
pas un événement incertain ou un repère de calendrier en date de jeu.
Cherche des combinaisons pertinentes pour la demande du
joueur, notamment un troc ou une tâche ponctuelle en contrepartie ; ne devine
aucun besoin privé, prix accepté, vérité d’information ou verdict du PNJ.
Une tâche allume est une remise en état ponctuelle, jamais un entretien continu.
Si une clause demandée est inexprimable, obstacle vaut condition_succes,
reglement_conditionnel, echeance_non_typee ou clause_non_typee, et alternatives
est vide. Ne supprime aucune clause pour produire un marché simplifié.
Aucune parole prononcée, aucune réalisation : le joueur choisit et modifie
ensuite le brouillon dans l’éditeur avant de le soumettre au PNJ.
"""


def ouvrir(monde, p):
    from .accords_publics import accords_publics, parole_accord, nom_terme
    from .echanges import candidat_proposition
    from .esprits import preuve_possession
    from . import memoire
    from .voix import reel
    from .propositions import compiler_limites
    from .temps import instant

    if (not isinstance(p, dict) or set(p) != {'obstacle', 'alternatives'}
            or p.get('obstacle') not in ('', *OBSTACLES)
            or not isinstance(p.get('alternatives'), list) or len(p['alternatives']) > 2):
        raise ErreurMonde('L’aide à la négociation doit être précisée.',
                          f'accord reçu {p!r} ; attendu obstacle connu, alternatives (0 à 2 marchés).')
    if p['obstacle']:
        return {'mode': 'dialogue', 'texte': OBSTACLES[p['obstacle']] + ' Rien n’a été dit ni engagé.',
                'faits': [], 'proposition': None, '_texte_moteur': True}
    public = accords_publics(monde, avec_suggestions=False)
    suggestions = []
    for a in p['alternatives']:
        # Aucune prose du modèle n'est affichée. Un candidat refusé disparaît
        # entier, sans réparer une clause ni changer une référence.
        if not isinstance(a, dict) or set(a) != {'destinataire', 'demande', 'contrepartie'}:
            continue
        d = {'geste': 'accord', 'cible': a['destinataire'],
             'parametres': {k: copy.deepcopy(a[k]) for k in ('demande', 'contrepartie')}}
        try:
            types = compiler_limites([{'type': 'proposition', **d['parametres']}], instant(monde))[0]
            d['parametres'] = {k: types[k] for k in ('demande', 'contrepartie')}
            c = parole_accord(monde, d)['contenu'][0]
            if any('echeance' in c[k].get('condition', {})
                   for k in ('demande', 'contrepartie')):
                continue
            # La recevabilité matérielle ne doit pas servir d'oracle pour
            # découvrir à qui appartient un bien connu de Corvus.
            connu = True
            for t, de in ((c['demande'], reel(monde, a['destinataire'])),
                          (c['contrepartie'], 'joueur')):
                if 'objet' in t and de != 'joueur':
                    possession = ((preuve_possession(monde, t['objet']) if monde.visible(t['objet']) else None) or
                        (memoire.fait_brut(monde, 'joueur', t['objet'], 'lieu') or {}).get('possession', {}))
                    connu &= possession.get('proprietaire') == de
            if not connu or not candidat_proposition(monde, reel(monde, a['destinataire']),
                    c['demande'], contrepartie=c['contrepartie']):
                continue
            initial = {'destinataire': a['destinataire'], **copy.deepcopy(d['parametres'])}
            if any(s['initial'] == initial for s in suggestions):
                continue
            qui = next(x['nom'] for x in public['destinataires'] if x['id'] == a['destinataire'])
            limite = '' if any('limite' in initial[k] for k in ('demande', 'contrepartie')) else ' ; sans limite négociée'
            suggestions.append({'nom': f"{qui} — Corvus donne {nom_terme(public, initial['contrepartie'])} ; "
                f"Corvus demande {nom_terme(public, initial['demande'])}{limite}", 'initial': initial})
        except ErreurMonde:
            continue
    texte = ('Choisis une alternative pour préparer le marché. Rien n’a été dit ni engagé.' if suggestions else
             'Aucune alternative recevable pour cette demande. Rien n’a été dit ni engagé.')
    r = {'mode': 'dialogue', 'texte': texte, 'faits': [], 'proposition': None, '_texte_moteur': True}
    if suggestions:
        public['suggestions'] = suggestions
        r['_formulaire_accord'] = {'public': public, 'initial': {}}
    return r
