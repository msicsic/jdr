"""Brouillons de prestations ponctuelles : mêmes termes publics dans les interfaces."""
import copy
import re

from .commandes import DescripteurPublic
from .monde import ErreurMonde
from .temps import instant, MINUTE


def accords_publics(monde, *, avec_suggestions=True):
    from .dialogues import information_publique
    from .paroles import _connu_du_joueur, contexte_fige
    from .deliberation import besoin_de_part
    from .propositions import en_mots
    from .noms import public, PERSONNES
    info = information_publique(monde)
    prestations, biens = [], []

    def ajouter(t):
        prestations.append({"terme": t, "nom": en_mots(monde, t)})

    with contexte_fige():
        for id, o in monde.objets.items():
            if not _connu_du_joueur(monde, id) or o['type'] in (*PERSONNES, 'partie_corps'):
                continue
            if o.get('mobile'):
                biens.append({'type': 'objet', 'objet': id})
            if o.get('mobile') and besoin_de_part(o) is not None:
                ajouter({'type': 'part', 'objet': id})
            for cle in ('allume', 'verrouillee'):
                if cle in o:
                    ajouter({'type': 'tache', 'condition': {'objet': id, cle: True}})
            if o.get('mobile'):
                for lieu in info['lieux']:
                    ajouter({'type': 'tache', 'condition': {'objet': id, 'lieu': lieu['id']}})
            if o['type'] == 'nourriture':
                for qui in info['personnes']:
                    from .voix import reel
                    ajouter({'type': 'tache', 'condition': {'objet': id, 'servir': reel(monde, qui['id'])}})
            if 'pieces' in o:
                biens.append({'type': 'pieces', 'montant': 1, 'objet': id})
    for t in biens:
        ajouter(t)
    ajouter({'type': 'pieces', 'montant': 1})
    projection = {"destinataires": info['destinataires'], "prestations": public(monde, prestations),
                  "or": monde.joueur['or'], "instant": instant(monde)}
    if avec_suggestions:
        from .dialogues import candidats_contrat
        projection['suggestions'] = candidats_contrat(monde, projection)
    return projection


def termes_parametres(p):
    """Adaptateur E5 sans perte ; la forme K1 transporte les deux termes entiers."""
    if set(p) in ({'prestation', 'prix'}, {'prestation', 'prix', 'limite'}):
        if not isinstance(p['prestation'], dict) or 'limite' in p['prestation']:
            raise ErreurMonde('Précise la prestation et sa limite dans les champs de l’accord.',
                              f'parametres.prestation : reçu {p["prestation"]!r} ; attendu terme sans limite imbriquée (limite dans parametres).')
        demande = copy.deepcopy(p['prestation'])
        if 'limite' in p:
            demande['limite'] = p['limite']
        return demande, {'type': 'pieces', 'montant': p['prix']}
    if set(p) == {'demande', 'contrepartie'}:
        return copy.deepcopy(p['demande']), copy.deepcopy(p['contrepartie'])
    raise ErreurMonde('Précise les deux termes de cet accord.',
                      f'parametres : reçu {p!r} ; attendu demande, contrepartie (ou prestation, prix, limite facultative).')


def parametres_termes(demande, contrepartie):
    """Conserver les descripteurs E5/K0 ; aucun champ typé n'est éliminé."""
    if (demande['type'] in ('part', 'tache') and
            set(contrepartie) == {'type', 'montant'} and contrepartie['type'] == 'pieces'):
        p = {'prestation': {k: copy.deepcopy(v) for k, v in demande.items() if k != 'limite'},
             'prix': contrepartie['montant']}
        if 'limite' in demande:
            p['limite'] = demande['limite']
        return p
    return {'demande': copy.deepcopy(demande), 'contrepartie': copy.deepcopy(contrepartie)}


def nom_terme(projection, t):
    from .propositions import en_mots_limite
    base = {k: v for k, v in t.items() if k != 'limite'}
    if t['type'] == 'pieces':
        base['montant'] = 1
    nom = next((x['nom'] for x in projection['prestations'] if x['terme'] == base), None)
    if nom is None:
        if base != {'type': 'rien'}:
            raise ValueError('Ce terme ne figure pas dans les choix publics.')
        nom = 'rien'
    if t['type'] == 'pieces':
        if t['montant'] == 1:
            nom += ' payée maintenant'
        else:
            nom = (str(t['montant']) + nom[1:].replace('pièce', 'pièces', 1)
                   .replace(' prise dans ', ' prises dans ') + ' payées maintenant')
    return nom + (en_mots_limite(t['limite'], projection['instant']) if 'limite' in t else '')


def parole_accord(monde, d):
    """Valider à chaque préparation/revalidation ; aucun choix par texte libre."""
    def refuser(champ, recu, attendu, message="Précise les termes de cet accord."):
        raise ErreurMonde(message, f"{champ} : reçu {recu!r} ; attendu {attendu}.")
    if not isinstance(d, dict) or set(d) != {'geste', 'cible', 'parametres'} or d['geste'] != 'accord':
        refuser('descripteur', d, 'geste=accord, cible, parametres')
    p = d['parametres']
    if not isinstance(p, dict):
        refuser('parametres', p, 'demande, contrepartie')
    demande, contrepartie = termes_parametres(p)
    choix = accords_publics(monde, avec_suggestions=False)
    if d['cible'] not in [x['id'] for x in choix['destinataires']]:
        refuser('cible', d['cible'], [x['id'] for x in choix['destinataires']],
                "Tu ne perçois plus cet interlocuteur pour lui proposer l'accord.")
    from .voix import reel
    from .propositions import en_mots, erreur_terme, verifier
    from .noms import public
    termes = []
    for nom, t in (('demande', demande), ('contrepartie', contrepartie)):
        erreur = erreur_terme(t, nom == 'contrepartie')
        if erreur:
            suffixe, recu, attendu = erreur
            refuser('parametres.' + nom + suffixe, recu, attendu)
        base = {k: v for k, v in t.items() if k != 'limite'}
        if t['type'] == 'pieces':
            base['montant'] = 1
        if base != {'type': 'rien'} and base not in [x['terme'] for x in choix['prestations']]:
            refuser('parametres.' + nom, t, [x['terme'] for x in choix['prestations']],
                    "Ce terme ne correspond plus aux choix publics.")
        if 'limite' in t and t['limite'] < instant(monde):
            refuser('parametres.' + nom + '.limite', t['limite'], f'entier >= {instant(monde)}',
                    "La limite est dépassée. L'offre périmée n'est pas émise.")
        if (nom == 'contrepartie' and t['type'] == 'pieces' and 'objet' not in t
                and t['montant'] > choix['or']):
            refuser('parametres.contrepartie.montant', t['montant'], f"entier de 1 à {choix['or']}",
                    "Le prix doit être couvert par ton or actuel.")
        t = copy.deepcopy(t)
        if 'objet' in t:
            t['objet'] = reel(monde, t['objet'])
        if 'condition' in t:
            t['condition'] = {k: reel(monde, v) if isinstance(v, str) else v for k, v in t['condition'].items()}
        termes.append(t)
    contenu = {'type': 'proposition', 'demande': termes[0], 'contrepartie': termes[1]}
    verifier(monde, contenu)
    # La parole choisie conserve le repère absolu ; seul l'aperçu recalcule
    # le temps restant. Revalider ne reformule pas les mots choisis.
    def dire(t):
        texte = en_mots(monde, t)
        if 'limite' in t:
            texte = texte.rsplit(' (', 1)[0]
        return texte + (' payées maintenant' if t['type'] == 'pieces' else '')
    mots = public(monde, f"Je propose {dire(termes[1])} contre {dire(termes[0])}.")
    return {'personnage': d['cible'], 'replique': mots, 'contenu': [contenu]}


class AccordTerminal:
    """Formulaire local figé, modifiable avant de soumettre à U-C."""
    champs = ('destinataire', 'prestation', 'prix', 'delai')

    def __init__(self, public, initial=None):
        self.public = copy.deepcopy(public)
        self.valeurs = {}
        self.etape = 'destinataire'
        self.terminee = False
        self.offre = None
        initial = initial or {}
        if 'demande' in initial:
            initial = copy.deepcopy(initial)
            demande = initial.pop('demande')
            initial['prestation'] = {k: v for k, v in demande.items() if k != 'limite'}
            initial['limite'] = demande.get('limite')
            initial['sans_limite'] = 'limite' not in demande
            self.offre = copy.deepcopy(initial['contrepartie'])
            self.valeurs['prix'] = (self.offre, nom_terme(self.public, self.offre))
        if initial.get('sans_limite') is True:
            self.valeurs['delai'] = (None, 'sans limite négociée')
        for cle, liste, champ in (('destinataire', 'destinataires', 'id'), ('prestation', 'prestations', 'terme')):
            for x in self.public[liste]:
                valeur = copy.deepcopy(initial.get(cle))
                base = copy.deepcopy(valeur)
                if cle == 'prestation' and isinstance(base, dict) and base.get('type') == 'pieces':
                    base['montant'] = 1
                if cle in initial and x[champ] == base:
                    self.valeurs[cle] = (valeur, nom_terme(self.public, valeur) if cle == 'prestation' else x['nom'])
                    break
        prix = initial.get('prix')
        if type(prix) is int and 1 <= prix <= self.public['or']:
            self.valeurs['prix'] = (prix, f'{prix} pièces payées maintenant')
        limite = initial.get('limite')
        if type(limite) is int and limite >= self.public['instant']:
            from .propositions import en_mots_limite
            self.valeurs['delai'] = (limite, en_mots_limite(limite, self.public['instant']).strip())
        self.etape = next((c for c in self.champs if c not in self.valeurs), None)

    def termes(self):
        demande = copy.deepcopy(self.valeurs['prestation'][0])
        if self.valeurs['delai'][0] is not None:
            demande['limite'] = self.valeurs['delai'][0]
        return demande, copy.deepcopy(self.offre or {'type': 'pieces', 'montant': self.valeurs['prix'][0]})

    def choix(self):
        if self.etape == 'destinataire':
            return [(x['id'], x['nom']) for x in self.public['destinataires']]
        if self.etape == 'prestation':
            return [(x['terme'], x['nom']) for x in self.public['prestations']]
        if self.etape == 'prix':
            return [(x['terme'], x['nom']) for x in self.public['prestations']] + [({'type': 'rien'}, 'rien')]
        return []

    def rendre(self):
        from .propositions import en_mots_limite
        lignes = ['Accord — annuler pour fermer ; corriger destinataire/prestation/prix/delai/delai_donne.',
                  'Deux termes : Corvus donne la contrepartie et demande la prestation. Ni prêt daté, ni maintien, ni paiement futur.',
                  'Une durée indéterminée ne peut être promise : un nouvel accord sans limite reste possible.']
        if not self.valeurs and self.public.get('suggestions'):
            lignes.extend(['Suggestions à discuter ; aucun accord ni paiement. Prix modifiable.',
                           *(f'suggestion {i}. {s["nom"]}'
                             for i, s in enumerate(self.public['suggestions'], 1)),
                           'Saisis « suggestion N » pour préremplir, ou compose les termes ci-dessous.'])
        for cle in self.champs:
            if cle in self.valeurs:
                valeur, nom = self.valeurs[cle]
                lignes.append({'prestation': 'Corvus demande', 'prix': 'Corvus donne',
                               'delai': 'Délai demandé'}.get(cle, cle) + ' : ' + nom)
                if cle == 'delai' and valeur is not None:
                    lignes.append(en_mots_limite(valeur, self.public['instant']).strip())
        if self.etape:
            lignes.append({'prix': f"Corvus donne : prix entier de 1 à {self.public['or']}, ou « terme N » parmi les choix ci-dessous.",
                           'delai': 'Délai : minutes entières, 0 pour sans limite. Demain exige un repère précis.'}.get(
                               self.etape, self.etape + ' : numéro puis Entrée'))
            lignes.extend(f'{i}. {nom}' for i, (_, nom) in enumerate(self.choix(), 1))
        else:
            demande, contrepartie = self.termes()
            lignes.append('Marché : Corvus donne ' + nom_terme(self.public, contrepartie) +
                          ' ; Corvus demande ' + nom_terme(self.public, demande) + '.')
            lignes.append('valider : préparer cet accord, puis tenter pour le proposer réellement.')
        return '\n'.join(lignes)

    def saisir(self, texte):
        t = texte.strip().casefold()
        if self.terminee:
            raise ValueError('Ce brouillon est fermé.')
        if t == 'annuler':
            self.terminee = True
            return None
        if not self.valeurs and t.startswith('suggestion '):
            numero = t[11:]
            suggestions = self.public.get('suggestions', [])
            if not re.fullmatch('[0-9]{1,9}', numero) or not 1 <= int(numero) <= len(suggestions):
                raise ValueError('Choisis une suggestion affichée.')
            self.__init__(self.public, suggestions[int(numero) - 1]['initial'])
            return None
        if t == 'corriger delai_donne':
            if not self.offre or self.offre['type'] not in ('part', 'tache'):
                raise ValueError('Seule une part ou une tâche peut porter une limite.')
            self.etape = 'delai_donne'
            return None
        if t.startswith('corriger ') and t[9:] in self.champs:
            self.etape = t[9:]
            return None
        if not self.etape:
            if t != 'valider':
                raise ValueError('Valider, corriger un champ ou annuler.')
            p = parametres_termes(*self.termes())
            self.terminee = True
            return DescripteurPublic({'geste': 'accord', 'cible': self.valeurs['destinataire'][0], 'parametres': p})
        if self.etape == 'prix' and re.fullmatch(r'terme [0-9]{1,9}', t):
            n = int(t[6:])
            if not 1 <= n <= len(self.choix()):
                raise ValueError('Choisis un terme affiché.')
            self.offre, nom = copy.deepcopy(self.choix()[n - 1])
            self.valeurs['prix'] = (self.offre, nom)
            self.etape = ('montant_donne' if self.offre['type'] == 'pieces' else
                          next((c for c in self.champs if c not in self.valeurs), None))
            return None
        if not re.fullmatch('[0-9]{1,9}', t):
            raise ValueError('Précise un nombre entier ; une date sans repère comme demain doit être précisée en minutes.')
        n = int(t)
        if self.etape in ('destinataire', 'prestation'):
            if not 1 <= n <= len(self.choix()):
                raise ValueError('Choisis un numéro affiché.')
            valeur = self.choix()[n - 1]
            if self.etape == 'prestation' and valeur[0]['type'] == 'pieces':
                self.valeurs['prestation'] = copy.deepcopy(valeur)
                self.etape = 'montant_demande'
                return None
        elif self.etape == 'prix':
            if not 1 <= n <= self.public['or']:
                raise ValueError('Le prix doit être couvert par ton or.')
            valeur = (n, f'{n} pièces payées maintenant')
            self.offre = None
        elif self.etape in ('montant_donne', 'montant_demande'):
            if n < 1:
                raise ValueError('Le montant doit être strictement positif.')
            cle = 'prix' if self.etape == 'montant_donne' else 'prestation'
            terme = copy.deepcopy(self.offre if cle == 'prix' else self.valeurs[cle][0])
            terme['montant'] = n
            if cle == 'prix':
                self.offre = terme
            self.valeurs[cle] = (terme, nom_terme(self.public, terme))
            self.etape = next((c for c in self.champs if c not in self.valeurs), None)
            return None
        elif self.etape == 'delai_donne':
            self.offre.pop('limite', None)
            if n:
                self.offre['limite'] = self.public['instant'] + n * MINUTE
            self.valeurs['prix'] = (self.offre, nom_terme(self.public, self.offre))
            self.etape = next((c for c in self.champs if c not in self.valeurs), None)
            return None
        else:
            valeur = (self.public['instant'] + n * MINUTE if n else None,
                      f'dans {n} minutes' if n else 'sans limite négociée')
        self.valeurs[self.etape] = valeur
        self.etape = next((c for c in self.champs if c not in self.valeurs), None)
        return None
