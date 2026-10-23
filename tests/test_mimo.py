"""Contrat JSON MiMo, flux complets, correction bornée et accès explicite du jeu."""
import base64
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import jeu
from donjon.fournisseurs import Demande, ErreurFournisseur
from donjon.fournisseurs.mimo import MiMo
from donjon.mj import MJ
from donjon.monde import Monde
from tools.verifier_websocket_jeu import Interface
from tools.traces_mimo import JournalMiMo

try:
    import jsonschema
except ImportError:
    jsonschema = None

SCHEMA = {'type': 'object', 'properties': {'ok': {'type': 'boolean'}},
          'required': ['ok'], 'additionalProperties': False}
DEMANDE = Demande('instructions', {'message': 'intention'}, 'intention', 'fonction', SCHEMA,
                  'mimo-v2.6-flash', effort='none')


def flux(texte='{"ok":true}', fin='stop', done=True, usage=10):
    evenements = [{'id': 'r', 'model': 'mimo-v2.6-flash', 'choices': [{'index': 0, 'delta': {'content': texte}, 'finish_reason': None}]},
                  {'id': 'r', 'choices': [{'index': 0, 'delta': {}, 'finish_reason': fin}], 'usage': {'total_tokens': usage}}]
    return (''.join('data: ' + json.dumps(e) + '\n\n' for e in evenements) + ('data: [DONE]\n\n' if done else '')).encode()


@unittest.skipIf(jsonschema is None, 'Dépendances MiMo facultatives absentes')
class MiMoTests(unittest.TestCase):
    def test_correction_format_par_le_modele_et_cout_des_deux_reponses(self):
        donnees = [flux('{"ok":true}<'), flux()]
        requetes = []
        def ouvrir(r, timeout, ipv4):
            requetes.append(json.loads(r.data))
            return io.BytesIO(donnees[len(requetes) - 1])
        p = MiMo('secret-simulation')
        with patch('donjon.fournisseurs.mimo.ouvrir_flux', side_effect=ouvrir):
            r = p.appeler(DEMANDE)
        self.assertEqual(r.arguments, {'ok': True})
        self.assertEqual(r.utilisation['total_tokens'], 20)
        self.assertEqual(len(r.brut['tentatives']), 2)
        self.assertEqual(requetes[1]['messages'][2]['content'], '{"ok":true}<')
        self.assertEqual(requetes[0]['messages'], requetes[1]['messages'][:2])
        self.assertNotIn('diagnostic_validation', r.brut)
        for a, octets in zip(r.brut['tentatives'], donnees):
            self.assertEqual(base64.b64decode(a['sse_base64']), octets)
        self.assertNotIn('secret-simulation', json.dumps(r.brut))

    def test_donnee_absente_non_completee_et_relance_limitee(self):
        p = MiMo('simulation')
        with patch('donjon.fournisseurs.mimo.ouvrir_flux', side_effect=lambda *a: io.BytesIO(flux('{}'))) as ouvrir:
            with self.assertRaisesRegex(ErreurFournisseur, 'Réponse du MJ invalide') as erreur:
                p.appeler(DEMANDE)
        self.assertEqual(ouvrir.call_count, 2)
        self.assertNotIn('required', str(erreur.exception))
        self.assertIn('required', p.dernier_brut['diagnostic_validation'])
        self.assertTrue(all('arguments' not in a for a in p.dernier_brut['tentatives']))

    def test_doublons_nan_tableau_et_caracteres_parasites_refuses(self):
        for texte in ('{"ok":true,"ok":false}', '{"ok":NaN}', '[true]', '{"ok":true}<'):
            with self.subTest(texte=texte):
                p = MiMo('simulation', relances_format=0)
                with patch('donjon.fournisseurs.mimo.ouvrir_flux', return_value=io.BytesIO(flux(texte))):
                    with self.assertRaises(ErreurFournisseur):
                        p.appeler(DEMANDE)
                self.assertEqual(len(p.dernier_brut['tentatives']), 1)

    def test_coupure_troncature_erreur_et_protocole_ne_declenchent_pas_de_relance(self):
        variantes = [flux(done=False), flux(fin='length'), b'data: {"error":{"message":"refus"}}\n\ndata: [DONE]\n\n',
            flux() + b'data: {"choices":[]}\n\n', b'data: ceci nest pas du json\n\n' + flux(),
            b'data: {"choices":[{"delta":{"tool_calls":[{}]}}]}\n\n' + flux()]
        for octets in variantes:
            with self.subTest(octets=octets[:30]):
                p = MiMo('simulation')
                with patch('donjon.fournisseurs.mimo.ouvrir_flux', return_value=io.BytesIO(octets)) as ouvrir:
                    with self.assertRaises(ErreurFournisseur):
                        p.appeler(DEMANDE)
                self.assertEqual(ouvrir.call_count, 1)
                self.assertEqual(base64.b64decode(p.dernier_brut['sse_base64']), octets)
                self.assertTrue(p.dernier_brut['mesures']['flux_lu_jusqua_eof'])

    def test_sse_multiligne_commentaires_crlf_et_mesures_distinctes(self):
        contenu = (b': keepalive\r\n\r\ndata: {"choices":[],\r\ndata: "model":"mimo-v2.6-flash"}\r\n\r\n'
                   b'data: {"choices":[{"delta":{"reasoning_content":"raison"}}]}\r\n\r\n' + flux())
        p = MiMo('simulation')
        horloge = iter(range(1000))
        with patch('donjon.transport_mimo.time.monotonic', side_effect=lambda: next(horloge)), \
             patch('donjon.fournisseurs.mimo.ouvrir_flux', return_value=io.BytesIO(contenu)):
            r = p.appeler(Demande(**{**DEMANDE.__dict__, 'timeout': 1000}))
        m = r.brut['mesures']
        self.assertLess(m['premiere_ligne_sse_s'], m['premier_evenement_s'])
        self.assertLess(m['premiere_reflexion_s'], m['ttft_s'])
        self.assertEqual(r.arguments, {'ok': True})

    def test_timeout_global_de_la_correction_et_aucun_deuxieme_envoi(self):
        horloge = [0.0]
        def observer(type_, *a):
            if type_ == 'fin':
                horloge[0] = 46.0
        p = MiMo('simulation', observateur_transport=observer)
        with patch('donjon.fournisseurs.mimo.time.monotonic', side_effect=lambda: horloge[0]), \
             patch('donjon.fournisseurs.mimo.ouvrir_flux', return_value=io.BytesIO(flux('{}'))) as ouvrir:
            with self.assertRaisesRegex(ErreurFournisseur, 'délai dépassé'):
                p.appeler(DEMANDE)
        self.assertEqual(ouvrir.call_count, 1)
        self.assertEqual(p.numero_appel, 1)

    def test_limite_de_taille_et_echec_reseau_ne_sont_pas_des_reponses(self):
        p = MiMo('simulation')
        with patch('donjon.transport_mimo.LIMITE_REPONSE', 32), \
             patch('donjon.fournisseurs.mimo.ouvrir_flux', return_value=io.BytesIO(flux())):
            with self.assertRaisesRegex(ErreurFournisseur, 'volumineuse'):
                p.appeler(DEMANDE)
        self.assertTrue(p.dernier_brut['mesures']['capture_limitee'])
        with patch('donjon.fournisseurs.mimo.ouvrir_flux', side_effect=TimeoutError) as ouvrir:
            with self.assertRaisesRegex(ErreurFournisseur, 'délai'):
                p.appeler(DEMANDE)
        self.assertEqual(ouvrir.call_count, 1)

    def test_authentification_coupe_la_session_sans_repli_openai(self):
        p = MiMo('cle-xiaomi-test')
        erreur = urllib.error.HTTPError('https://api.xiaomimimo.com', 401, '', {}, io.BytesIO())
        with patch('donjon.fournisseurs.mimo.ouvrir_flux', side_effect=erreur) as ouvrir:
            for _ in range(2):
                with self.assertRaisesRegex(ErreurFournisseur, 'déconnecté') as e:
                    p.appeler(DEMANDE)
                self.assertNotIn('cle-xiaomi-test', str(e.exception))
        self.assertEqual(ouvrir.call_count, 1)
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'autre-fournisseur'}, clear=True):
            sans_cle = MiMo()
            with patch('donjon.fournisseurs.mimo.ouvrir_flux') as ouvrir:
                with self.assertRaisesRegex(ErreurFournisseur, 'MIMO_API_KEY absente'):
                    sans_cle.appeler(DEMANDE)
                ouvrir.assert_not_called()

    def test_cli_mimo_rejoue_deux_rejets_reels_avec_correction_bornee(self):
        racine = Path(__file__).parent / 'data/mimo-rejets'
        for dossier in sorted(racine.iterdir()):
            with self.subTest(cas=dossier.name), tempfile.TemporaryDirectory() as temp:
                save = Path(temp) / 'partie.json'
                shutil.copy2(dossier / 'avant.json', save)
                # Actualiser une fois les symboles de perception de cette scène ancienne,
                # comme le fait l'ouverture du jeu, avant la comparaison du rejet.
                from donjon.spatial import installer
                monde = Monde.charger(save)
                installer(monde)
                monde.sauver(save)
                avant = monde.data
                p = json.loads((dossier / 'requete.json').read_text(encoding='utf-8'))
                intention = json.loads(p['messages'][1]['content'])['requete']['message']
                interface = Interface([intention, 'quitter'], save)
                brut = (dossier / 'reponse.sse').read_bytes()
                def ouvrir(requete, timeout, ipv4):
                    self.assertEqual(requete.get_header('Api-key'), 'xiaomi-test')
                    self.assertNotIn('autre-fournisseur', str(requete.headers))
                    corps = json.loads(requete.data)
                    self.assertEqual(corps['model'], 'mimo-v2.6-flash')
                    self.assertEqual(corps['thinking'], {'type': 'disabled'})
                    self.assertTrue(ipv4)
                    return io.BytesIO(brut)
                with patch.dict(os.environ, {'MIMO_API_KEY': 'xiaomi-test', 'OPENAI_API_KEY': 'autre-fournisseur', 'OPENAI_MODEL': 'modele-autre'}, clear=True), \
                     patch('jeu.charger_env'), patch('donjon.fournisseurs.mimo.ouvrir_flux', side_effect=ouvrir) as api:
                    self.assertEqual(jeu.main(['--defi', '--connexion', 'mimo', '--console', '--save', str(save)], interface=interface), 0)
                self.assertEqual(api.call_count, 2)
                self.assertIn('Réponse du MJ invalide.', '\n'.join(interface.sorties))
                self.assertNotIn('is not valid under any', '\n'.join(interface.sorties))
                self.assertEqual(Monde.charger(save).data, avant)
                reprise = Interface(['inventaire', 'regarder', 'quitter'], save)
                self.assertEqual(jeu.main(['--defi', '--offline', '--console', '--save', str(save)], interface=reprise), 0)
                self.assertEqual(Monde.charger(save).data, avant)

    def test_mode_par_defaut_reste_luna_meme_avec_une_cle_mimo(self):
        with patch.dict(os.environ, {'MIMO_API_KEY': 'xiaomi-test'}, clear=True):
            self.assertEqual(MJ().modele, 'gpt-6-luna')
            self.assertEqual(MJ().effort, 'medium')
            self.assertEqual(MJ(connexion='mimo').modele, 'mimo-v2.6-flash')
            self.assertEqual(MJ(connexion='mimo').effort, 'none')

    def test_budget_physique_compte_la_correction_et_garde_la_premiere_capture(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = JournalMiMo(temp, maximum=1)
            p = MiMo('simulation', observateur_transport=journal.observateur())
            octets = flux('{}')
            with patch('donjon.fournisseurs.mimo.ouvrir_flux', return_value=io.BytesIO(octets)) as ouvrir:
                with self.assertRaisesRegex(RuntimeError, 'Budget maximal'):
                    p.appeler(DEMANDE)
            self.assertEqual(ouvrir.call_count, 1)
            self.assertEqual(len(journal.appels), 1)
            capture = Path(temp) / journal.appels[0]['dossier_trace']
            self.assertEqual((capture / 'reponse.sse').read_bytes(), octets)
            self.assertTrue((capture / 'mesure.json').is_file())
