"""HTTP Xiaomi et SSE Chat Completions, sans modifier le réseau du processus."""
import base64
import http.client
import json
import socket
import time
import urllib.request

from .monde import ErreurMonde

LIMITE_REPONSE = 4_000_000


class FluxInvalide(ErreurMonde):
    pass


def _connexion_ipv4(adresse, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
    hote, port = adresse
    erreur = None
    debut = time.monotonic()
    for famille, type_, protocole, _, destination in socket.getaddrinfo(hote, port, socket.AF_INET, socket.SOCK_STREAM):
        connexion = socket.socket(famille, type_, protocole)
        try:
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                restant = None if timeout is None else timeout - (time.monotonic() - debut)
                if restant is not None and restant <= 0:
                    raise TimeoutError
                connexion.settimeout(restant)
            if source_address:
                connexion.bind(source_address)
            connexion.connect(destination)
            return connexion
        except OSError as exc:
            erreur = exc
            connexion.close()
    raise erreur or OSError('Aucune adresse IPv4')


class _HTTPSIPv4(http.client.HTTPSConnection):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._create_connection = _connexion_ipv4


class _GestionnaireIPv4(urllib.request.HTTPSHandler):
    def https_open(self, requete):
        return self.do_open(_HTTPSIPv4, requete, context=self._context)


class _SansRedirection(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **kw):
        return None


def ouvrir_flux(requete, timeout, ipv4=True):
    gestionnaires = [_SansRedirection()]
    if ipv4:
        gestionnaires.append(_GestionnaireIPv4())
    return urllib.request.build_opener(*gestionnaires).open(requete, timeout=timeout)


def recevoir(flux, brut, debut, echeance, notifier=lambda *a: None):
    """Lire jusqu'à EOF ; les erreurs de protocole n'interrompent pas l'audit du reste."""
    octets, bloc, textes, problemes = bytearray(), [], [], []
    mesures = brut['mesures']
    termine, fin, identifiant = False, None, None

    def evenement(donnees):
        nonlocal termine, fin, identifiant
        maintenant = time.monotonic() - debut
        if mesures['premier_evenement_s'] is None:
            mesures['premier_evenement_s'] = maintenant
        try:
            e = donnees if donnees == '[DONE]' else json.loads(donnees)
        except ValueError:
            e = {'sse_invalide': donnees}
            problemes.append('Événement SSE JSON invalide')
        brut['evenements'].append({'secondes': maintenant, 'evenement': e})
        notifier('evenement', brut['evenements'][-1])
        if termine:
            problemes.append('Données après le terminal DONE')
            return
        if e == '[DONE]':
            termine = True
            return
        try:
            if not isinstance(e, dict) or 'sse_invalide' in e:
                raise ValueError('Événement objet attendu')
            if e.get('error'):
                raise ValueError('Erreur signalée dans le flux')
            if e.get('id'):
                if identifiant is not None and identifiant != e['id']:
                    raise ValueError('Identifiant de réponse changé')
                identifiant = e['id']
            if e.get('model'):
                brut['modele_retourne'] = e['model']
            if e.get('usage') is not None:
                if not isinstance(e['usage'], dict):
                    raise ValueError('Usage mal formé')
                brut['usage'] = e['usage']
            choix = e.get('choices', [])
            if not isinstance(choix, list) or len(choix) > 1:
                raise ValueError('Une seule réponse attendue')
            for c in choix:
                if c.get('index', 0) != 0:
                    raise ValueError('Indice de réponse inattendu')
                delta = c.get('delta', {})
                if delta.get('tool_calls') or delta.get('function_call'):
                    problemes.append('Appel outil reçu en mode JSON natif')
                if delta.get('refusal'):
                    problemes.append('Réponse refusée par le modèle')
                if delta.get('role') not in (None, 'assistant'):
                    problemes.append('Rôle assistant attendu')
                if delta.get('reasoning_content') and mesures['premiere_reflexion_s'] is None:
                    mesures['premiere_reflexion_s'] = maintenant
                contenu = delta.get('content')
                if contenu is not None:
                    if not isinstance(contenu, str):
                        raise ValueError('Contenu texte attendu')
                    if contenu:
                        if fin is not None:
                            problemes.append('Contenu après finish_reason')
                        textes.append(contenu)
                        if mesures['ttft_s'] is None:
                            mesures['ttft_s'] = maintenant
                if c.get('finish_reason') is not None:
                    if fin is not None:
                        problemes.append('Plusieurs finish_reason')
                    fin = c['finish_reason']
        except (ValueError, TypeError, AttributeError) as exc:
            problemes.append(str(exc))

    try:
        while True:
            restant = echeance - time.monotonic()
            if restant <= 0:
                raise TimeoutError
            connexion = getattr(getattr(getattr(flux, 'fp', None), 'raw', None), '_sock', None)
            if connexion is not None:
                connexion.settimeout(restant)
            ligne = flux.readline(LIMITE_REPONSE - len(octets) + 1)
            if not ligne:
                mesures['flux_lu_jusqua_eof'] = True
                break
            maintenant = time.monotonic() - debut
            if mesures['premiere_ligne_sse_s'] is None:
                mesures['premiere_ligne_sse_s'] = maintenant
            octets.extend(ligne)
            notifier('octets', ligne)
            if len(octets) > LIMITE_REPONSE:
                mesures['capture_limitee'] = True
                raise FluxInvalide('MiMo : réponse trop volumineuse.')
            if time.monotonic() > echeance:
                raise TimeoutError
            try:
                texte = ligne.decode('utf-8').rstrip('\r\n')
            except UnicodeError:
                problemes.append('UTF-8 invalide')
                continue
            if texte.startswith('data:'):
                bloc.append(texte[5:].removeprefix(' '))
            elif not texte and bloc:
                evenement('\n'.join(bloc))
                bloc = []
        if bloc:
            evenement('\n'.join(bloc))
    finally:
        mesures['complet_s'] = time.monotonic() - debut
        brut['sse_base64'] = base64.b64encode(octets).decode('ascii')
        brut['contenu'] = [{'type': 'message', 'role': 'assistant',
            'content': [{'type': 'output_text', 'text': ''.join(textes)}]}]
        brut['stop_reason'] = fin
        brut['done_recu'] = termine
        if problemes:
            brut['diagnostic_flux'] = problemes
    if problemes:
        raise FluxInvalide('MiMo : flux de réponse invalide. Aucune proposition de cette réponse n’a été exécutée.')
    if fin != 'stop' or not termine:
        raise FluxInvalide('Réponse du MJ incomplète. Aucune proposition de cette réponse n’a été exécutée.')
    return ''.join(textes)
