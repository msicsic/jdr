"""MiMo expérimental : JSON natif strict, accessible par injection dans un banc."""
import base64
import json
import urllib.error
import urllib.request

from ..monde import ErreurMonde
from .contrat import Fournisseur, Reponse


def _uniques(paires):
    objet = {}
    for cle, valeur in paires:
        if cle in objet:
            raise ValueError('Clé JSON dupliquée')
        objet[cle] = valeur
    return objet


def _constante_invalide(_):
    raise ValueError('Constante JSON invalide')


class MiMo(Fournisseur):
    def __init__(self, cle):
        super().__init__()
        # Dépendance réservée aux essais MiMo, jamais chargée par Luna.
        from jsonschema import Draft202012Validator
        self.validateur = Draft202012Validator
        self._cle = cle

    def _appeler(self, demande):
        schema = demande.schema
        self.validateur.check_schema(schema)
        payload = {'model': demande.modele,
            'messages': [{'role': 'system', 'content': demande.instructions +
                '\nContrat de transport : rends les arguments de la fonction demandée comme un objet JSON unique, '
                'conforme au schéma fourni dans contrat_reponse. Le transport ne propose pas de canal outil ; '
                'seuls les arguments JSON sont attendus. Les règles métier précédentes restent applicables.'},
                {'role': 'user', 'content': json.dumps({'requete': demande.entree,
                    'contrat_reponse': {'fonction': demande.fonction, 'schema': schema}}, ensure_ascii=False)}],
            'max_completion_tokens': 3000,
            'thinking': {'type': 'disabled' if demande.effort == 'none' else 'enabled'},
            'stream': True, 'stream_options': {'include_usage': True},
            'response_format': {'type': 'json_object'}}
        requete = urllib.request.Request('https://api.xiaomimimo.com/v1/chat/completions',
            data=json.dumps(payload).encode('utf-8'), headers={'api-key': self._cle,
                'Content-Type': 'application/json'}, method='POST')
        brut = self.dernier_brut = {'requete': payload, 'contenu': [], 'evenements': []}
        octets, textes, fin = bytearray(), [], None
        try:
            with urllib.request.urlopen(requete, timeout=demande.timeout) as flux:
                for ligne in flux:
                    octets.extend(ligne)
                    if len(octets) > 4_000_000:
                        raise ErreurMonde('Réponse du MJ trop volumineuse. Aucune action appliquée.')
                    if not ligne.startswith(b'data:'):
                        continue
                    donnees = ligne[5:].strip()
                    if donnees == b'[DONE]':
                        # Conserver aussi la fin physique du flux pour l'audit.
                        continue
                    evenement = json.loads(donnees)
                    brut['evenements'].append(evenement)
                    self.derniere_utilisation = evenement.get('usage') or self.derniere_utilisation
                    for choix in evenement.get('choices', []):
                        fin = choix.get('finish_reason') or fin
                        delta = choix.get('delta', {})
                        if delta.get('tool_calls'):
                            raise ErreurMonde('Réponse du MJ invalide. Un objet JSON unique est attendu.')
                        if delta.get('content'):
                            if not isinstance(delta['content'], str):
                                raise ErreurMonde('MiMo : contenu du flux invalide.')
                            textes.append(delta['content'])
        except urllib.error.HTTPError as exc:
            statut = exc.code
            exc.close()
            if statut == 401:
                self.erreur_auth = 'MJ déconnecté : la clé Xiaomi est refusée. Aucun nouvel appel ne sera tenté dans cette session.'
                raise ErreurMonde(self.erreur_auth) from None
            raise ErreurMonde(f'MiMo indisponible : HTTP {statut}.') from None
        except (urllib.error.URLError, OSError, ValueError, TypeError, AttributeError):
            raise ErreurMonde('MiMo : réseau ou flux invalide.') from None
        finally:
            brut['sse_base64'] = base64.b64encode(octets).decode('ascii')
            brut['contenu'] = [{'type': 'message', 'role': 'assistant',
                'content': [{'type': 'output_text', 'text': ''.join(textes)}]}]
        if fin != 'stop':
            raise ErreurMonde('Réponse du MJ incomplète. Aucune proposition de cette réponse n’a été exécutée.')
        try:
            objet = json.loads(''.join(textes), object_pairs_hook=_uniques, parse_constant=_constante_invalide)
            erreurs = list(self.validateur(schema).iter_errors(objet))
            if erreurs:
                raise ValueError(erreurs[0].message)
            if not isinstance(objet, dict):
                raise ValueError('Objet JSON attendu')
        except (ValueError, TypeError) as exc:
            brut['diagnostic_validation'] = str(exc)
            raise ErreurMonde('Réponse du MJ invalide. Aucune proposition de cette réponse n’a été exécutée.') from None
        return Reponse(objet, brut, self.derniere_utilisation)
