"""Adaptateurs réels, réponses réseau simulées : moteur, affichage, sauvegarde et reprise."""
import base64
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import jeu
from donjon.fournisseurs.anthropic import Anthropic
from donjon.fournisseurs.openai import OpenAI
from donjon.mj import MJ
from donjon.monde import Monde
from donjon.moteur import proposition
from tests.test_claude import anthropic, bloc, reponse
from tools.verifier_websocket_jeu import CAS, Interface, parcours

try:
    from donjon.fournisseurs.mimo import MiMo
    import jsonschema
except ImportError:
    jsonschema = None


def arguments(cible, fonction, entree):
    if fonction == 'auditer_action':
        return {'conforme': True, 'motif': ''}
    if fonction == 'auditer_narration':
        return {'segments': {str(i): {'verdict': 'mecanique', 'sources': ['resultat_resolu'],
            'locuteur': '', 'citation': '', 'entites': [], 'motif': ''} for i, _ in enumerate(entree['segments'])}}
    if fonction == 'repondre_au_joueur':
        if 'resultat_resolu' in entree.get('faits', {}):
            texte = 'Tu prends la clé du veilleur.' if cible == 'cle' else 'Tu prends la bobine de ficelle solide.'
            return {'mode': 'dialogue', 'texte': texte, 'faits': ['resultat_resolu'], 'proposition': None}
        return {'mode': 'action', 'texte': '', 'faits': ['joueur'], 'proposition': proposition('prendre', cible)}
    raise AssertionError(fonction)


class ParcoursFournisseursTests(unittest.TestCase):
    def _parcours(self, type_fournisseur):
        for cas in CAS:
            with self.subTest(cas=cas, fournisseur=type_fournisseur):
                cible = CAS[cas][1]
                traces = []
                if type_fournisseur == 'anthropic':
                    fournisseur = Anthropic()
                    fournisseur.client = MagicMock()
                    def generer(**p):
                        fonction = p['tools'][0]['name']
                        a = arguments(cible, fonction, json.loads(p['messages'][0]['content']))
                        return reponse('tool_use', bloc('tool_use', name=fonction, input=a, id='appel-test'))
                    fournisseur.client.messages.create.side_effect = generer
                elif type_fournisseur == 'mimo':
                    fournisseur = MiMo('simulation')
                else:
                    fournisseur = OpenAI()

                def http(requete, timeout):
                    p = json.loads(requete.data)
                    if type_fournisseur == 'mimo':
                        self.assertIn('xiaomimimo.com', requete.full_url)
                        q = json.loads(p['messages'][1]['content'])
                        fonction = q['contrat_reponse']['fonction']
                        texte = json.dumps(arguments(cible, fonction, q['requete']))
                        evenements = [{'choices': [{'delta': {'content': texte}, 'finish_reason': None}]},
                            {'choices': [{'delta': {}, 'finish_reason': 'stop'}], 'usage': {'total_tokens': 12}}]
                        return io.BytesIO((''.join('data: ' + json.dumps(e) + '\n\n' for e in evenements) + 'data: [DONE]\n\n').encode())
                    self.assertIn('api.openai.com', requete.full_url)
                    fonction = p['tools'][0]['name']
                    a = arguments(cible, fonction, json.loads(p['input'][0]['content']))
                    return io.BytesIO(json.dumps({'status': 'completed', 'output': [
                        {'type': 'function_call', 'name': fonction, 'arguments': json.dumps(a)}]}).encode())

                def construire(*a, **kw):
                    a = list(a)
                    if type_fournisseur == 'mimo':
                        a[0], a[1] = 'mimo-v2.6-flash', 'none'
                    elif type_fournisseur == 'anthropic':
                        a[0] = 'claude-haiku-5-5'
                    kw.update(fournisseur=fournisseur, connexion=type_fournisseur)
                    mj = MJ(*a, **kw)
                    mj.journal_complet, mj.observateur = True, traces.append
                    return mj
                with patch('jeu.MJ', side_effect=construire), \
                     patch.dict(os.environ, {'OPENAI_API_KEY': 'simulation'}), \
                     patch('urllib.request.urlopen', side_effect=http):
                    r = parcours(cas)
                self.assertTrue(r['recit_sauve_avant_affichage'])
                self.assertTrue(r['etat_identique_apres_reprise'])
                self.assertEqual(r['executions_action'], 1)
                self.assertEqual([t['fonction'] for t in traces if t['etape'] == 'appel'],
                    ['repondre_au_joueur', 'auditer_action', 'repondre_au_joueur', 'auditer_narration'])

    def test_openai_http_deux_scenes(self):
        self._parcours('api')

    @unittest.skipIf(anthropic is None, 'SDK Anthropic facultatif absent')
    def test_anthropic_deux_scenes(self):
        self._parcours('anthropic')

    @unittest.skipIf(jsonschema is None, 'Dépendance MiMo facultative absente')
    def test_mimo_deux_scenes(self):
        self._parcours('mimo')

    @unittest.skipIf(jsonschema is None, 'Dépendance MiMo facultative absente')
    def test_mimo_deux_rejets_reels_sans_fuite_du_diagnostic(self):
        racine = Path(__file__).parent / 'data/mimo-rejets'
        for f in sorted(racine.iterdir()):
            with self.subTest(cas=f.name), tempfile.TemporaryDirectory() as temp:
                sauvegarde = Path(temp) / 'partie.json'
                shutil.copy2(f / 'avant.json', sauvegarde)
                avant = Monde.charger(sauvegarde).data
                p = json.loads((f / 'requete.json').read_text(encoding='utf-8'))
                intention = json.loads(p['messages'][1]['content'])['requete']['message']
                fournisseur = MiMo('simulation')
                interface = Interface([intention, 'quitter'], sauvegarde)
                def construire(*a, **kw):
                    return MJ(*a, **kw, fournisseur=fournisseur)
                flux = (f / 'reponse.sse').read_bytes()
                with patch('jeu.MJ', side_effect=construire), \
                     patch.dict(os.environ, {'OPENAI_API_KEY': 'simulation'}), \
                     patch('urllib.request.urlopen', return_value=io.BytesIO(flux)):
                    self.assertEqual(jeu.main(['--defi', '--save', str(sauvegarde), '--console',
                        '--connexion', 'api', '--model', 'mimo-v2.6-flash'], interface=interface), 0)
                self.assertIn('Réponse du MJ invalide.', '\n'.join(interface.sorties))
                self.assertNotIn('is not valid under any', '\n'.join(interface.sorties))
                self.assertIn('diagnostic_validation', fournisseur.dernier_brut)
                self.assertEqual(base64.b64decode(fournisseur.dernier_brut['sse_base64']), flux)
                self.assertEqual(Monde.charger(sauvegarde).data, avant)
                reprise = Interface(['inventaire', 'regarder', 'quitter'], sauvegarde)
                self.assertEqual(jeu.main(['--defi', '--save', str(sauvegarde), '--console', '--offline'], interface=reprise), 0)
                self.assertEqual(Monde.charger(sauvegarde).data, avant)
