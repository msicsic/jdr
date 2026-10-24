import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.monde import Monde
from donjon.moteur import proposition
from tests.faux_websocket import FauxWebSocket, resultat
from tools.verifier_websocket_jeu import CAS, Interface, fixture, parcours


class ParcoursWebSocketTests(unittest.TestCase):
    def repondre(self, cible, payload):
        outil = payload['tools'][0]['tools'][0]
        fonction = outil['name']
        entree = json.loads(payload['input'][0]['content'])
        if fonction == 'auditer_action':
            args = {'conforme': True, 'motif': ''}
        elif fonction == 'auditer_narration':
            args = {'segments': {str(i): {"portee_mecanique": "aucune", 'verdict': 'mecanique', 'sources': ['resultat_resolu'],
                'locuteur': '', 'citation': '', 'entites': [], "comptes": [], 'motif': ''} for i, _ in enumerate(entree['segments'])}}
        elif fonction == 'repondre_au_joueur':
            if 'resultat_resolu' in entree.get('faits', {}):
                texte = 'Tu prends la clé du veilleur.' if cible == 'cle' else 'Tu prends la bobine de ficelle solide.'
                args = {'mode': 'dialogue', 'texte': texte, 'faits': ['resultat_resolu'], 'proposition': None}
            else:
                args = {'mode': 'action', 'texte': '', 'faits': ['joueur'], 'proposition': proposition('prendre', cible)}
        else:
            raise AssertionError(fonction)
        return resultat(payload, args)

    def test_deux_scenes_passent_par_mj_moteur_audits_affichage_et_reprise(self):
        for cas in CAS:
            with self.subTest(cas=cas):
                cible = CAS[cas][1]
                socket = FauxWebSocket(lambda p: self.repondre(cible, p))
                with patch('donjon.fournisseurs.openai.jeton', return_value='test'), \
                        patch('donjon.fournisseurs.openai.modeles', return_value=[{'slug': 'gpt-6-luna'}]), \
                        patch('donjon.transport_openai.ouvrir_websocket', return_value=socket) as ouvrir:
                    r = parcours(cas)
                self.assertTrue(r['etat_identique_apres_reprise'])
                self.assertEqual(ouvrir.call_count, 1)
                self.assertEqual(socket.fermetures, 1)
                noms = [p['tools'][0]['tools'][0]['name'] for p in socket.envois]
                self.assertEqual(noms, ['repondre_au_joueur', 'auditer_action', 'repondre_au_joueur', 'auditer_narration'])
                for p in socket.envois:
                    self.assertNotIn('previous_response_id', p)
                    self.assertNotIn('stream_id', p)
                    self.assertEqual(len(p['input']), 1)
                premier = json.loads(socket.envois[0]['input'][0]['content'])
                dernier = json.loads(socket.envois[2]['input'][0]['content'])
                self.assertNotEqual(premier, dernier)

    def test_coupure_avant_action_ou_apres_sauvegarde_ne_publie_jamais_de_fragment(self):
        for cas in CAS:
            for apres_action in (False, True):
                with self.subTest(cas=cas, apres_action=apres_action), tempfile.TemporaryDirectory() as dossier:
                    chemin = Path(dossier) / 'partie.json'
                    monde, cible = fixture(cas)
                    monde.sauver(chemin)
                    # Le démarrage mémorise la perception courante, même sans action.
                    demarrage = Interface(['quitter'], chemin)
                    self.assertEqual(jeu.main(['--save', str(chemin), '--offline', '--console', '--cases'], interface=demarrage), 0)
                    avant = copy.deepcopy(Monde.charger(chemin).data)
                    def repondre(p):
                        e = json.loads(p['input'][0]['content'])
                        if not apres_action or 'resultat_resolu' in e.get('faits', {}):
                            return [{'type': 'response.created', 'response': {'id': 'interrompue'}},
                                {'type': 'response.output_text.delta', 'response_id': 'interrompue',
                                 'delta': 'FRAGMENT QUI NE DOIT PAS ÊTRE AFFICHÉ'}]
                        return self.repondre(cible, p)
                    sockets = [FauxWebSocket(repondre) for _ in range(2)]
                    interface = Interface(['mj Je prends ' + monde.objets[cible]['nom'] + '.', 'quitter'], chemin)
                    with patch('donjon.fournisseurs.openai.jeton', return_value='test'), \
                            patch('donjon.fournisseurs.openai.modeles', return_value=[{'slug': 'gpt-6-luna'}]), \
                            patch('donjon.transport_openai.ouvrir_websocket', side_effect=sockets) as ouvrir:
                        self.assertEqual(jeu.main(['--save', str(chemin), '--console', '--connexion', 'chatgpt', '--cases'], interface=interface), 0)
                    recharge = Monde.charger(chemin)
                    if apres_action:
                        self.assertEqual(recharge.objets[cible]['lieu'], 'joueur')
                        self.assertIn(recharge.data['conversation'][-1]['reponse'], interface.deja_sauves)
                    else:
                        self.assertEqual(recharge.data, avant)
                    self.assertNotIn('FRAGMENT QUI NE DOIT PAS ÊTRE AFFICHÉ', '\n'.join(interface.sorties))
                    self.assertEqual(ouvrir.call_count, 2)
                    self.assertTrue(all(s.fermetures == 1 for s in sockets))
                    etat = copy.deepcopy(recharge.data)
                    reprise = Interface(['inventaire', 'regarder', 'quitter'], chemin)
                    self.assertEqual(jeu.main(['--save', str(chemin), '--offline', '--console'], interface=reprise), 0)
                    self.assertEqual(Monde.charger(chemin).data, etat)
                    self.assertIn(recharge.objets[cible]['nom'].casefold(), '\n'.join(reprise.sorties).casefold())

    def test_reconnexion_transparente_aux_quatre_etapes_execute_une_seule_action(self):
        for cas in CAS:
            for etape in ('interpretation', 'auditer_action', 'narration', 'auditer_narration'):
                with self.subTest(cas=cas, etape=etape):
                    cible = CAS[cas][1]
                    coupee = False
                    def repondre(p):
                        nonlocal coupee
                        fonction = p['tools'][0]['tools'][0]['name']
                        e = json.loads(p['input'][0]['content'])
                        phase = ('narration' if 'resultat_resolu' in e.get('faits', {}) else 'interpretation') if fonction == 'repondre_au_joueur' else fonction
                        r = self.repondre(cible, p)
                        if phase == etape and not coupee:
                            coupee = True
                            return [{'type': 'response.created', 'response': {'id': 'perdue'}},
                                {'type': 'response.output_item.done', 'response_id': 'perdue',
                                 'output_index': 0, 'item': r['output'][0]}]
                        return r
                    sockets = [FauxWebSocket(repondre) for _ in range(2)]
                    with patch('donjon.fournisseurs.openai.jeton', return_value='test'), \
                            patch('donjon.fournisseurs.openai.modeles', return_value=[{'slug': 'gpt-6-luna'}]), \
                            patch('donjon.transport_openai.ouvrir_websocket', side_effect=sockets) as ouvrir:
                        r = parcours(cas)
                    self.assertTrue(coupee)
                    self.assertEqual(ouvrir.call_count, 2)
                    self.assertTrue(all(s.fermetures == 1 for s in sockets))
                    self.assertEqual(sockets[0].envois[-1], sockets[1].envois[0])
                    self.assertEqual(r['executions_action'], 1)
                    self.assertTrue(r['recit_sauve_avant_affichage'])
                    self.assertTrue(r['etat_identique_apres_reprise'])
                    self.assertFalse(any('réseau' in t or 'Réessayez' in t for t in r['sorties']))
