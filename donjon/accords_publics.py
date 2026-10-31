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
    prestations = []

    def ajouter(t):
        prestations.append({"terme": t, "nom": en_mots(monde, t)})

    with contexte_fige():
        for id, o in monde.objets.items():
            if not _connu_du_joueur(monde, id) or o['type'] in (*PERSONNES, 'partie_corps'):
                continue
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
    projection = {"destinataires": info['destinataires'], "prestations": public(monde, prestations),
                  "or": monde.joueur['or'], "instant": instant(monde)}
    if avec_suggestions:
        from .dialogues import candidats_contrat
        projection['suggestions'] = candidats_contrat(monde, projection)
    return projection


def parole_accord(monde, d):
    """Valider à chaque préparation/revalidation ; aucun choix par texte libre."""
    def refuser(champ, recu, attendu, message="Précise les termes de cet accord."):
        raise ErreurMonde(message, f"{champ} : reçu {recu!r} ; attendu {attendu}.")
    if not isinstance(d, dict) or set(d) != {'geste', 'cible', 'parametres'} or d['geste'] != 'accord':
        refuser('descripteur', d, 'geste=accord, cible, parametres')
    p = d['parametres']
    if not isinstance(p, dict) or set(p) not in ({'prestation', 'prix'}, {'prestation', 'prix', 'limite'}):
        refuser('parametres', p, 'prestation, prix, limite facultative en dixièmes absolus')
    choix = accords_publics(monde, avec_suggestions=False)
    if d['cible'] not in [x['id'] for x in choix['destinataires']]:
        refuser('cible', d['cible'], [x['id'] for x in choix['destinataires']],
                "Tu ne perçois plus cet interlocuteur pour lui proposer l'accord.")
    if p['prestation'] not in [x['terme'] for x in choix['prestations']]:
        refuser('parametres.prestation', p['prestation'], [x['terme'] for x in choix['prestations']],
                "Cette prestation ne correspond plus aux choix publics.")
    if type(p['prix']) is not int or not 1 <= p['prix'] <= choix['or']:
        refuser('parametres.prix', p['prix'], f"entier de 1 à {choix['or']}",
                "Le prix doit être couvert par ton or actuel.")
    if 'limite' in p and (type(p['limite']) is not int or p['limite'] < instant(monde)):
        refuser('parametres.limite', p['limite'], f"entier >= {instant(monde)} en dixièmes absolus",
                "La limite doit être précisée et non dépassée. L'offre périmée n'est pas émise.")
    from .voix import reel
    from .propositions import en_mots
    from .noms import public
    terme = {k: (reel(monde, v) if isinstance(v, str) else v) for k, v in p['prestation'].items()}
    if 'condition' in terme:
        terme['condition'] = {k: reel(monde, v) if isinstance(v, str) else v
                              for k, v in terme['condition'].items()}
    if 'limite' in p:
        terme['limite'] = p['limite']
    contenu = {'type': 'proposition', 'demande': terme,
               'contrepartie': {'type': 'pieces', 'montant': p['prix']}}
    # La parole choisie conserve le repère absolu ; seul l'aperçu recalcule
    # le temps restant. Revalider ne reformule pas les mots choisis.
    prestation = en_mots(monde, terme).rsplit(' (', 1)[0] if 'limite' in terme else en_mots(monde, terme)
    mots = public(monde, f"Je propose {p['prix']} pièces payées maintenant contre {prestation}.")
    return {'personnage': d['cible'], 'replique': mots, 'contenu': [contenu]}


class AccordTerminal:
    """Formulaire local figé, modifiable avant de soumettre à U-C."""
    champs = ('destinataire', 'prestation', 'prix', 'delai')

    def __init__(self, public, initial=None):
        self.public = copy.deepcopy(public)
        self.valeurs = {}
        self.etape = 'destinataire'
        self.terminee = False
        initial = initial or {}
        if initial.get('sans_limite') is True:
            self.valeurs['delai'] = (None, 'sans limite négociée')
        for cle, liste, champ in (('destinataire', 'destinataires', 'id'), ('prestation', 'prestations', 'terme')):
            for x in self.public[liste]:
                if cle in initial and x[champ] == initial[cle]:
                    self.valeurs[cle] = (copy.deepcopy(x[champ]), x['nom'])
                    break
        prix = initial.get('prix')
        if type(prix) is int and 1 <= prix <= self.public['or']:
            self.valeurs['prix'] = (prix, f'{prix} pièces payées maintenant')
        limite = initial.get('limite')
        if type(limite) is int and limite >= self.public['instant']:
            from .propositions import en_mots_limite
            self.valeurs['delai'] = (limite, en_mots_limite(limite, self.public['instant']).strip())
        self.etape = next((c for c in self.champs if c not in self.valeurs), None)

    def choix(self):
        if self.etape == 'destinataire':
            return [(x['id'], x['nom']) for x in self.public['destinataires']]
        if self.etape == 'prestation':
            return [(x['terme'], x['nom']) for x in self.public['prestations']]
        return []

    def rendre(self):
        from .propositions import en_mots_limite
        lignes = ['Accord — annuler pour fermer ; corriger destinataire/prestation/prix/delai.',
                  'Prestation ponctuelle, pièces payées maintenant ; ni prêt daté, ni maintien, ni paiement futur.',
                  'Une durée indéterminée ne peut être promise : un nouvel accord sans limite reste possible.']
        if not self.valeurs and self.public.get('suggestions'):
            lignes.extend(['Suggestions à discuter ; aucun accord ni paiement. Prix modifiable.',
                           *(f'suggestion {i}. {s["nom"]}'
                             for i, s in enumerate(self.public['suggestions'], 1)),
                           'Saisis « suggestion N » pour préremplir, ou compose les termes ci-dessous.'])
        for cle in self.champs:
            if cle in self.valeurs:
                valeur, nom = self.valeurs[cle]
                lignes.append(cle + ' : ' + nom)
                if cle == 'delai' and valeur is not None:
                    lignes.append(en_mots_limite(valeur, self.public['instant']).strip())
        if self.etape:
            lignes.append({'prix': f"Prix : entier de 1 à {self.public['or']}",
                           'delai': 'Délai : minutes entières, 0 pour sans limite. Demain exige un repère précis.'}.get(
                               self.etape, self.etape + ' : numéro puis Entrée'))
            lignes.extend(f'{i}. {nom}' for i, (_, nom) in enumerate(self.choix(), 1))
        else:
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
        if t.startswith('corriger ') and t[9:] in self.champs:
            self.etape = t[9:]
            return None
        if not self.etape:
            if t != 'valider':
                raise ValueError('Valider, corriger un champ ou annuler.')
            p = {'prestation': self.valeurs['prestation'][0], 'prix': self.valeurs['prix'][0]}
            limite = self.valeurs['delai'][0]
            if limite is not None:
                p['limite'] = limite
            self.terminee = True
            return DescripteurPublic({'geste': 'accord', 'cible': self.valeurs['destinataire'][0], 'parametres': p})
        if not re.fullmatch('[0-9]{1,9}', t):
            raise ValueError('Précise un nombre entier ; une date sans repère comme demain doit être précisée en minutes.')
        n = int(t)
        if self.etape in ('destinataire', 'prestation'):
            if not 1 <= n <= len(self.choix()):
                raise ValueError('Choisis un numéro affiché.')
            valeur = self.choix()[n - 1]
        elif self.etape == 'prix':
            if not 1 <= n <= self.public['or']:
                raise ValueError('Le prix doit être couvert par ton or.')
            valeur = (n, f'{n} pièces payées maintenant')
        else:
            valeur = (self.public['instant'] + n * MINUTE if n else None,
                      f'dans {n} minutes' if n else 'sans limite négociée')
        self.valeurs[self.etape] = valeur
        self.etape = next((c for c in self.champs if c not in self.valeurs), None)
        return None
