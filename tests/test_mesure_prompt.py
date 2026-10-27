import unittest
from unittest.mock import patch
import json

from tools.mesure_prompt import dossiers_portee, payload, prefixe, difference, voie


class MesurePromptTest(unittest.TestCase):
    def test_identique_au_fournisseur_sans_reseau(self):
        from donjon.fournisseurs.openai import OpenAI
        from donjon.fournisseurs.contrat import Demande
        e = dict(modele='gpt-6-luna', instructions='été', entree={'faits': {'salle': 'crypte'}},
                 fonction='repondre_au_joueur', schema={'type': 'object'}, effort='medium')
        demande = Demande(e['instructions'], e['entree'], '', e['fonction'], e['schema'],
                          e['modele'], cle_cache='00000000-0000-0000-0000-000000000000')
        with patch('donjon.fournisseurs.openai.jeton', return_value='simulation'), \
             patch('donjon.fournisseurs.openai.WebSocketResponses') as transport:
            transport.return_value.appeler.return_value = {'status': 'completed', 'output': [
                {'type': 'function_call', 'name': e['fonction'], 'arguments': '{}'}]}
            f = OpenAI(chatgpt=True)
            f.catalogue_verifie = True
            f._appeler(demande)
            p = transport.return_value.appeler.call_args.args[0]
            attendu = {'type': 'response.create', **{k: v for k, v in p.items() if k != 'stream'}}
            self.assertEqual(json.dumps(attendu, ensure_ascii=False), json.dumps(payload(e), ensure_ascii=False))

    def test_ordre_envoi_et_prefixe(self):
        e = dict(modele='gpt-6-luna', instructions='abc', entree={'faits': {}},
                 fonction='repondre_au_joueur', schema={'properties': {'mode': {'enum': ['dialogue', 'action']}}})
        p = payload(e)
        self.assertEqual(list(p)[:5], ['type', 'model', 'instructions', 'input', 'tools'])
        self.assertEqual(voie(e), 'interpretation')
        self.assertEqual(prefixe('abc', 'abd'), 2)
        self.assertEqual(prefixe('ab', 'abc'), 2)
        self.assertEqual(difference(p, {**p, 'instructions': 'abd'}), '/instructions')

    def test_portee_connue_et_inconnue(self):
        faits = {'atelier': {'ressources': ['bois']}, 'objet:bois': {'a_portee_de_main': False}}
        self.assertEqual(dossiers_portee(faits)['atelier']['statut'], 'aucun_proche')
        faits['objet:bois']['a_portee_de_main'] = True
        self.assertEqual(dossiers_portee(faits)['atelier']['statut'], 'proche')
        del faits['objet:bois']['a_portee_de_main']
        self.assertEqual(dossiers_portee(faits)['atelier']['statut'], 'inconnu')
