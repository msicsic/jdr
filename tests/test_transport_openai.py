import json
import unittest
from unittest.mock import patch

from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde
from donjon.transport_openai import WebSocketResponses, ErreurTransport, DUREE_CONNEXION
from tests.faux_websocket import FauxWebSocket, resultat


SCHEMA = {'type': 'object', 'properties': {'ok': {'type': 'boolean'}},
          'required': ['ok'], 'additionalProperties': False}


class TransportTests(unittest.TestCase):
    def test_mj_audits_et_nouvelles_regles_utilisent_la_meme_connexion_sans_historique(self):
        socket = FauxWebSocket(lambda p: resultat(p, {'ok': True}))
        mj = MJOpenAI(connexion='chatgpt')
        with patch('donjon.mj.jeton', return_value='test-prive'), \
                patch('donjon.mj.modeles', return_value=[{'slug': mj.modele}]), \
                patch('donjon.transport_openai.ouvrir_websocket', return_value=socket) as ouvrir:
            for i, (fonction, regles) in enumerate([('proposer', 'A'), ('auditer', 'B'), ('proposer', 'C')]):
                schema = {**SCHEMA, 'description': 'contrat ' + regles}
                entree = {'faits': {'revision': 0, 'inventaire': [str(i)]}}
                self.assertEqual(mj._appeler_brut(regles, entree, 'intention', fonction, schema), {'ok': True})
                p = socket.envois[-1]
                self.assertEqual(p['instructions'], regles)
                self.assertEqual(json.loads(p['input'][0]['content']), entree)
                self.assertEqual(p['tools'][0]['tools'][0]['parameters'], schema)
                for interdit in ('previous_response_id', 'conversation', 'stream_id', 'stream', 'max_output_tokens'):
                    self.assertNotIn(interdit, p)
            self.assertEqual(ouvrir.call_count, 1)
            self.assertEqual(socket.fermetures, 0)
            mj.fermer()
            mj.fermer()
            self.assertEqual(socket.fermetures, 1)

    def test_fragment_abandonne_et_reconnexion_transparente_du_meme_appel(self):
        casse = FauxWebSocket(lambda _: [{'type': 'response.created', 'response': {'id': 'r1'}},
            {'type': 'response.function_call_arguments.delta', 'response_id': 'r1', 'delta': '{"ok":true}'}])
        bon = FauxWebSocket(lambda p: resultat(p, {'ok': True}))
        mj = MJOpenAI(connexion='chatgpt')
        mj.catalogue_verifie = True
        with patch('donjon.mj.jeton', return_value='test'), \
                patch('donjon.transport_openai.ouvrir_websocket', side_effect=[casse, bon]) as ouvrir:
            self.assertEqual(mj._appeler_brut('règles', {'nouveau': True}, 'intention', 'proposer', SCHEMA), {'ok': True})
            self.assertEqual(ouvrir.call_count, 2)
            self.assertEqual(len(casse.envois), 1)
            self.assertEqual(casse.fermetures, 1)
            self.assertEqual(casse.envois[0], bon.envois[0])
            self.assertEqual(json.loads(bon.envois[0]['input'][0]['content']), {'nouveau': True})
            mj.fermer()

    def test_401_handshake_ou_evenement_coupe_la_session_sans_fuite(self):
        for ouverture in (ErreurTransport(401), FauxWebSocket(lambda _: [{'type': 'error', 'status': 401}])):
            with self.subTest(ouverture=type(ouverture).__name__):
                mj = MJOpenAI(connexion='chatgpt')
                mj.catalogue_verifie = True
                kwargs = {'side_effect': ouverture} if isinstance(ouverture, Exception) else {'return_value': ouverture}
                with patch('donjon.mj.jeton', return_value='secret-a-ne-pas-afficher'), \
                        patch('donjon.transport_openai.ouvrir_websocket', **kwargs) as ouvrir:
                    for _ in range(2):
                        with self.assertRaisesRegex(ErreurMonde, 'MJ déconnecté') as erreur:
                            mj._appeler_brut('règles', {}, 'intention', 'proposer', SCHEMA)
                        self.assertNotIn('secret-a-ne-pas-afficher', str(erreur.exception))
                    self.assertEqual(ouvrir.call_count, 1)

    def test_autre_reponse_incomplete_erreur_et_volume_sont_refuses(self):
        evenements = [
            [{'type': 'response.output_item.done', 'output_index': 0,
              'item': {'type': 'function_call', 'name': 'ancien', 'arguments': '{}'}},
             {'type': 'response.created', 'response': {'id': 'r'}},
             {'type': 'response.completed', 'response': {'id': 'r', 'status': 'completed', 'output': []}}],
            [{'type': 'response.completed', 'response': {'id': 'ancien', 'status': 'completed', 'output': []}}],
            [{'type': 'response.created', 'response': {'id': 'r'}},
             {'type': 'response.in_progress', 'response': {'id': 'autre'}}],
            [{'type': 'response.created', 'response': {'id': 'r'}},
             {'type': 'response.completed', 'response': {'id': 'autre', 'status': 'completed', 'output': []}}],
            [{'type': 'response.failed', 'response': {'error': {'code': 'subscription_sharing_usage_limit_exceeded'}}}],
            [{'type': 'response.created', 'response': {'id': 'r'}},
             {'type': 'response.completed', 'response': {'id': 'r', 'status': 'incomplete', 'output': []}}],
            [{'type': 'response.created', 'response': {'id': 'r'}},
             {'type': 'response.output_text.delta', 'response_id': 'r', 'delta': 'x' * 4_000_001}],
            ['texte-invalide'],
        ]
        for events in evenements:
            with self.subTest(type=type(events[-1]).__name__):
                socket = FauxWebSocket(lambda _: events)
                t = WebSocketResponses()
                with patch('donjon.transport_openai.ouvrir_websocket', return_value=socket):
                    with self.assertRaises((ErreurMonde, ErreurTransport)):
                        t.appeler({}, 'test', 'session', 1)
                self.assertEqual(socket.fermetures, 1)

    def test_rotation_jeton_expiration_et_socket_fermee_renouvellent_avant_envoi(self):
        for raison in ('jeton', 'duree', 'fermee', 'session'):
            with self.subTest(raison=raison):
                sockets = [FauxWebSocket(lambda _: {'status': 'completed', 'output': []}) for _ in range(2)]
                t = WebSocketResponses()
                with patch('donjon.transport_openai.ouvrir_websocket', side_effect=sockets) as ouvrir:
                    t.appeler({}, 'test', 'session', 1)
                    if raison == 'duree':
                        t._ouverture -= DUREE_CONNEXION
                    if raison == 'fermee':
                        sockets[0].close_code = 1000
                    t.appeler({}, 'autre' if raison == 'jeton' else 'test',
                              'autre' if raison == 'session' else 'session', 1)
                    self.assertEqual(ouvrir.call_count, 2)
                    self.assertEqual(len(sockets[0].envois), 1)
                    self.assertEqual(len(sockets[1].envois), 1)
                    t.fermer()

    def test_delai_global_et_exception_du_client_sans_secret(self):
        socket = FauxWebSocket(lambda _: [])
        t = WebSocketResponses()
        with patch('donjon.transport_openai.ouvrir_websocket', return_value=socket), \
                patch('donjon.transport_openai.time.monotonic', side_effect=[0, 0, 0, 2, 2]):
            with self.assertRaises(ErreurTransport):
                t.appeler({}, 'test', 'session', 1)
        self.assertEqual(socket.fermetures, 1)
        socket = FauxWebSocket(lambda _: [])
        with patch.object(socket, 'recv', side_effect=RuntimeError('Bearer secret-test')), \
                patch('donjon.transport_openai.ouvrir_websocket', return_value=socket):
            with self.assertRaises(ErreurTransport) as erreur:
                WebSocketResponses().appeler({}, 'secret-test', 'session', 1)
        self.assertNotIn('secret-test', str(erreur.exception))

    def test_limite_60_minutes_et_echec_initial_de_connexion_sont_transparents(self):
        limite = FauxWebSocket(lambda _: [{'type': 'error', 'status': 400,
            'error': {'code': 'websocket_connection_limit_reached', 'message': '60 minutes'}}])
        for premiere in (limite, ErreurTransport(503, reessayable=True)):
            with self.subTest(premiere=type(premiere).__name__):
                bon = FauxWebSocket(lambda _: {'status': 'completed', 'output': []})
                t = WebSocketResponses()
                with patch('donjon.transport_openai.ouvrir_websocket', side_effect=[premiere, bon]) as ouvrir:
                    self.assertEqual(t.appeler({'instructions': 'actuelles', 'input': []}, 'test', 'session', 5)['status'], 'completed')
                    self.assertEqual(ouvrir.call_count, 2)
                    self.assertEqual(len(bon.envois), 1)
                    t.fermer()

    def test_panne_persistante_bornee_a_deux_tentatives(self):
        sockets = [FauxWebSocket(lambda _: []) for _ in range(2)]
        t = WebSocketResponses()
        with patch('donjon.transport_openai.ouvrir_websocket', side_effect=sockets) as ouvrir:
            with self.assertRaises(ErreurTransport):
                t.appeler({}, 'test', 'session', 5)
            self.assertEqual(ouvrir.call_count, 2)
        self.assertTrue(all(len(s.envois) == s.fermetures == 1 for s in sockets))

    def test_reconnexion_partage_le_budget_de_delai_initial(self):
        temps = [0]
        casse = FauxWebSocket(lambda _: [])
        bon = FauxWebSocket(lambda _: {'status': 'completed', 'output': []})
        def couper(*a, **kw):
            temps[0] = 2
            raise OSError('coupure')
        with patch.object(casse, 'recv', side_effect=couper), \
                patch('donjon.transport_openai.time.monotonic', side_effect=lambda: temps[0]), \
                patch('donjon.transport_openai.ouvrir_websocket', side_effect=[casse, bon]) as ouvrir:
            t = WebSocketResponses()
            self.assertEqual(t.appeler({}, 'test', 'session', 5)['status'], 'completed')
            self.assertEqual([a.args[2] for a in ouvrir.call_args_list], [5, 3])
            t.fermer()
