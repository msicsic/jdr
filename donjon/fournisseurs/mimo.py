"""Xiaomi MiMo : JSON natif, validation locale et correction de format bornée."""
import copy
import json
import os
import time
import urllib.error
import urllib.request

from ..monde import ErreurMonde
from ..transport_mimo import ouvrir_flux, recevoir
from .contrat import Fournisseur, Reponse

MODELE = 'mimo-v2.6-flash'
CONTRAT_TRANSPORT = (
    '\nContrat de transport : rends les arguments de la fonction demandée comme un objet JSON unique, '
    'conforme au schéma fourni dans contrat_reponse. Le transport ne propose pas de canal outil ; '
    'seuls les arguments JSON sont attendus. Les règles métier précédentes restent applicables.')


def _uniques(paires):
    objet = {}
    for cle, valeur in paires:
        if cle in objet:
            raise ValueError('Clé JSON dupliquée')
        objet[cle] = valeur
    return objet


def _constante_invalide(_):
    raise ValueError('Constante JSON invalide')


def _additionner(total, ajout):
    total = dict(total or {})
    for cle, valeur in (ajout or {}).items():
        if isinstance(valeur, dict):
            total[cle] = _additionner(total.get(cle), valeur)
        elif type(valeur) in (int, float):
            total[cle] = total.get(cle, 0) + valeur
    return total or None


class MiMo(Fournisseur):
    def __init__(self, cle=None, *, ipv4=True, relances_format=1, observateur_transport=None):
        super().__init__()
        if relances_format not in (0, 1):
            raise ValueError('MiMo : zéro ou une relance de format autorisée')
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            raise ErreurMonde('Installez MiMo : python -m pip install -r requirements-mimo.txt') from None
        self.validateur = Draft202012Validator
        self._cle = cle if cle is not None else os.environ.get('MIMO_API_KEY') or os.environ.get('XIAOMI_API_KEY')
        self.ipv4, self.relances_format = ipv4, relances_format
        self.observateur_transport = observateur_transport
        self.numero_appel = 0

    def _notifier(self, type_, numero, donnees):
        if self.observateur_transport:
            self.observateur_transport(type_, numero, donnees)

    def _appeler(self, demande):
        if not self._cle or not self._cle.strip():
            raise ErreurMonde('MIMO_API_KEY absente. Les commandes hors ligne restent disponibles (aide).')
        if demande.effort not in ('none', 'low', 'medium', 'high'):
            raise ErreurMonde('MiMo : effort inconnu.')
        self.validateur.check_schema(demande.schema)
        validateur = self.validateur(demande.schema)
        payload = {'model': demande.modele,
            'messages': [{'role': 'system', 'content': demande.instructions + CONTRAT_TRANSPORT},
                {'role': 'user', 'content': json.dumps({'requete': demande.entree,
                    'contrat_reponse': {'fonction': demande.fonction, 'schema': demande.schema}}, ensure_ascii=False)}],
            'max_completion_tokens': 3000,
            'thinking': {'type': 'disabled' if demande.effort == 'none' else 'enabled'},
            'stream': True, 'stream_options': {'include_usage': True},
            'response_format': {'type': 'json_object'}}
        debut = time.monotonic()
        echeance = debut + demande.timeout
        tentatives = []
        self.dernier_brut = {'tentatives': tentatives, 'contenu': []}
        for essai in range(self.relances_format + 1):
            if time.monotonic() >= echeance:
                raise ErreurMonde('MiMo : délai dépassé. Aucune proposition de cette réponse n’a été exécutée.')
            self.numero_appel += 1
            numero = self.numero_appel
            brut = {'numero': numero, 'fonction': demande.fonction, 'essai': essai,
                'requete': copy.deepcopy(payload), 'contenu': [], 'evenements': [],
                'mesures': {'ttft_s': None, 'premiere_reflexion_s': None, 'premiere_ligne_sse_s': None,
                    'premier_evenement_s': None, 'flux_lu_jusqua_eof': False}}
            tentatives.append(brut)
            self._notifier('debut', numero, brut)
            debut_tentative = time.monotonic()
            try:
                restant = echeance - debut_tentative
                if restant <= 0:
                    raise TimeoutError
                requete = urllib.request.Request('https://api.xiaomimimo.com/v1/chat/completions',
                    data=json.dumps(payload).encode('utf-8'), headers={'api-key': self._cle,
                        'Content-Type': 'application/json'}, method='POST')
                with ouvrir_flux(requete, restant, self.ipv4) as flux:
                    texte = recevoir(flux, brut, debut_tentative, echeance,
                        lambda type_, d: self._notifier(type_, numero, d))
                try:
                    objet = json.loads(texte, object_pairs_hook=_uniques, parse_constant=_constante_invalide)
                    erreurs = list(validateur.iter_errors(objet))
                    if erreurs:
                        raise ValueError(erreurs[0].message)
                    if not isinstance(objet, dict):
                        raise ValueError('Objet JSON attendu')
                except (ValueError, TypeError) as exc:
                    brut['diagnostic_validation'] = str(exc)
                    if essai == self.relances_format:
                        raise ErreurMonde('Réponse du MJ invalide. Aucune proposition de cette réponse n’a été exécutée.') from None
                    payload['messages'].extend([{'role': 'assistant', 'content': texte},
                        {'role': 'user', 'content': json.dumps({'correction_transport': {
                            'diagnostic': str(exc), 'consigne': 'Rends uniquement les arguments JSON conformes au schéma initial. '
                            'Corrige la représentation de ta réponse sans inventer de fait ni exécuter de nouvelle action.'}}, ensure_ascii=False)}])
                    continue
                brut['schema_valide'] = True
                brut['arguments'] = copy.deepcopy(objet)
                return Reponse(objet, self.dernier_brut, _additionner(self.derniere_utilisation, brut.get('usage')))
            except urllib.error.HTTPError as exc:
                statut = exc.code
                exc.close()
                brut['statut_http'] = statut
                if statut == 401:
                    self.erreur_auth = 'MJ déconnecté : la clé Xiaomi est refusée. Aucun nouvel appel ne sera tenté dans cette session.'
                    raise ErreurMonde(self.erreur_auth) from None
                raise ErreurMonde(f'MiMo indisponible : HTTP {statut}.') from None
            except (urllib.error.URLError, OSError):
                brut['erreur_transport'] = 'reseau_ou_delai'
                raise ErreurMonde('MiMo : réseau ou délai dépassé. Aucune proposition de cette réponse n’a été exécutée.') from None
            finally:
                self.derniere_utilisation = _additionner(self.derniere_utilisation, brut.get('usage'))
                self.dernier_brut.clear()
                self.dernier_brut.update(brut)
                self.dernier_brut['tentatives'] = tentatives
                self._notifier('fin', numero, brut)
