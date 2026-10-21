"""Contrat du fournisseur, traces d'échec et isolation des connexions."""
import io
import json
import unittest
from unittest.mock import Mock, patch

from donjon.fournisseurs import Demande, Reponse, ErreurFournisseur, creer
from donjon.fournisseurs.anthropic import Anthropic
from donjon.fournisseurs.openai import OpenAI
from donjon.mj import MJ, MJOpenAI
from donjon.monde import ErreurMonde


SCHEMA = {'type': 'object', 'properties': {'ok': {'type': 'boolean'}},
          'required': ['ok'], 'additionalProperties': False}


class ContratTests(unittest.TestCase):
    def test_injection_sans_acces_au_mj_et_sans_mutation_du_contexte(self):
        entree = {'faits': {'revision': 7, 'liste': ['a']}}
        schema = {'type': 'object'}
        demandes = []
        def appeler(demande):
            demandes.append(demande)
            demande.entree['faits']['liste'].append('mutation du fournisseur')
            demande.schema['type'] = 'array'
            return Reponse({'ok': True}, ['brut'], {'total_tokens': 9})
        fournisseur = Mock(appeler=appeler)
        mj = MJ('modele-test', fournisseur=fournisseur)
        mj.observateur, mj.journal_complet = Mock(), True
        self.assertIs(MJOpenAI, MJ)
        self.assertEqual(mj._appeler_brut('règles', entree, 'intention', 'proposer', schema), {'ok': True})
        self.assertIsInstance(demandes[0], Demande)
        self.assertEqual(entree['faits']['liste'], ['a'])
        self.assertEqual(schema['type'], 'object')
        self.assertEqual(mj.observateur.call_args.args[0]['usage'], {'total_tokens': 9})
        mj.fermer()
        fournisseur.fermer.assert_called_once()

    def test_echec_ne_reprend_pas_le_cout_ou_la_reponse_precedente(self):
        fournisseur = Mock()
        fournisseur.appeler.side_effect = [Reponse({'ok': True}, ['ancien'], {'total_tokens': 99}),
            ErreurFournisseur('Refus', brut=['rejeté'], utilisation={'total_tokens': 3}),
            ErreurMonde('Réseau')]
        mj = MJ(fournisseur=fournisseur)
        traces = []
        mj.observateur, mj.journal_complet = traces.append, True
        mj._appeler_brut('', {}, '', 'f', SCHEMA)
        for _ in range(2):
            with self.assertRaises(ErreurMonde):
                mj._appeler_brut('', {}, '', 'f', SCHEMA)
        self.assertEqual(traces[1]['brut'], ['rejeté'])
        self.assertEqual(traces[1]['usage']['total_tokens'], 3)
        self.assertIsNone(traces[2]['brut'])
        self.assertIsNone(traces[2]['usage'])

    def test_mauvais_contrat_de_retour_rejete(self):
        for reponse in ({'ok': True}, Reponse([], ['brut'])):
            with self.subTest(type=type(reponse).__name__):
                mj = MJ(fournisseur=Mock(appeler=Mock(return_value=reponse)))
                with self.assertRaisesRegex(ErreurMonde, 'fournisseur mal formée'):
                    mj._appeler_brut('', {}, '', 'f', SCHEMA)
                if isinstance(reponse, Reponse):
                    self.assertEqual(mj.dernier_brut, ['brut'])

    def test_fabrique_et_etat_propres_a_chaque_instance(self):
        self.assertIsInstance(creer('api'), OpenAI)
        self.assertTrue(creer('chatgpt').chatgpt)
        a, b = creer('anthropic'), creer('anthropic')
        self.assertIsInstance(a, Anthropic)
        a.sans_strict.add('proposer')
        self.assertEqual(b.sans_strict, set())
        with self.assertRaises(ValueError):
            creer('mimo')  # L'essai n'est pas activé dans le jeu.

    def test_openai_incomplet_garde_le_brut_et_les_tokens(self):
        resultat = {'status': 'incomplete', 'output': [{'type': 'message', 'content': []}],
                    'usage': {'total_tokens': 12}}
        mj = MJ()
        traces = []
        mj.observateur, mj.journal_complet = traces.append, True
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'simulation'}), \
             patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(resultat).encode())):
            with self.assertRaisesRegex(ErreurMonde, 'incomplète'):
                mj._appeler_brut('', {}, '', 'f', SCHEMA)
        self.assertEqual(traces[0]['brut'], resultat['output'])
        self.assertEqual(traces[0]['usage'], resultat['usage'])
