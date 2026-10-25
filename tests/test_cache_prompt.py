"""Lot 85 : préfixes constants et contrats de scène conservés après recharge."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.couverture_action import schema as schema_action, verifier
from donjon.mj import MJ, SCHEMA_REPONSE
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, Plan, proposition
from donjon.narration import controler, schema_audit
from donjon.rendu import regarder
from tests.faux_websocket import FauxWebSocket, resultat
from tests.test_gardes_justes import crypte
from tests.test_tensions import recharger
from tests.test_verdict_coherent import noir
from tools.mesurer_cache_prompt import mesurer


TEXTE = 'Tu peux regarder autour de toi.'
DIALOGUE = {"mode": "dialogue", "texte": TEXTE, "faits": [], "proposition": None}
AUDIT = {"segments": [{"indice": 0, "verdict": "neutre", "sources": [],
    "portee_mecanique": "aucune", "locuteur": "", "citation": "", "presentation": "",
    "entites": [], "motif": "", "comptes": [], "eclairages": []}]}


class CachePromptTests(unittest.TestCase):
    def test_console_deux_scenes_deux_tours_transport_et_recharge(self):
        prefixes = {}
        for fabriquer in (noir, crypte):
            m = fabriquer()
            avant = copy.deepcopy(m.objets)
            vue = regarder(m)
            def repondre(payload):
                fonction = payload['tools'][0]['tools'][0]['name']
                prefixe = (payload['tools'], payload['instructions'])
                if fonction in prefixes:
                    self.assertEqual(prefixe, prefixes[fonction])
                prefixes[fonction] = copy.deepcopy(prefixe)
                return resultat(payload, AUDIT if fonction == 'auditer_narration' else DIALOGUE)
            socket = FauxWebSocket(repondre)
            with tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / 'copie.json'
                m.sauver(chemin)
                with (patch('donjon.fournisseurs.openai.jeton', return_value='test'),
                      patch('donjon.fournisseurs.openai.modeles', return_value=[{'slug': 'gpt-6-luna'}]),
                      patch('donjon.transport_openai.ouvrir_websocket', return_value=socket) as ouvrir,
                      patch('builtins.input', side_effect=['Que puis-je faire ?', 'Et maintenant ?', 'quitter']),
                      patch('sys.stdout', io.StringIO()) as sortie):
                    self.assertEqual(jeu.main(['--console', '--connexion', 'chatgpt', '--save', str(chemin)]), 0)
                r = Monde.charger(chemin)
                self.assertEqual(r.objets, avant)
                self.assertEqual(regarder(r), vue)
                self.assertIn(TEXTE, sortie.getvalue())
                self.assertIn(TEXTE, str(r.data['narrations_mj']))
                self.assertEqual(len(socket.envois), 4)
                ouvrir.assert_called_once()
                cles = [p['prompt_cache_key'] for p in socket.envois]
                self.assertEqual(cles[0], cles[2])
                self.assertEqual(cles[1], cles[3])
                self.assertNotEqual(cles[0], cles[1])

    def test_interpretation_narration_et_correction_meme_prefixe(self):
        prefixes = []
        entrees = []
        def appel(instructions, entree, intention, fonction, schema):
            prefixes.append((instructions, copy.deepcopy(schema)))
            entrees.append(entree)
            return copy.deepcopy(DIALOGUE)
        mj = MJ()
        with patch.object(mj, '_appeler', side_effect=appel):
            for m in (noir(), crypte()):
                for enrichir in (True, False):
                    for retour in (None, {'obstacle': 'La cible est trop loin.'}):
                        mj._echanger(recharger(m), 'Que vois-je ?', None, enrichir, retour_moteur=retour)
        self.assertTrue(all(p == prefixes[0] for p in prefixes))
        self.assertEqual(prefixes[0][1], SCHEMA_REPONSE)
        self.assertEqual({e['cadre_du_tour']['phase'] for e in entrees}, {'interpretation', 'narration'})
        self.assertGreater(len({json.dumps(e['faits'], sort_keys=True) for e in entrees}), 2)

    def test_audits_action_et_parole_meme_schema_sans_confondre_les_verdicts(self):
        geste = Plan({}, 0, 'Un geste')
        parole = Plan({}, 0, 'Une parole', parole={'replique': 'Bonjour', 'contenu': []})
        self.assertEqual(schema_action(geste), schema_action(parole))
        verifier({'rapport': {'conforme': True, 'motif': ''}}, geste)
        verifier({'rapport': {'contenu_conforme': True, 'motif': '', 'operations_demandees': []}}, parole)
        with self.assertRaises(ErreurMonde):
            verifier({'rapport': {'conforme': True, 'motif': ''}}, parole)

    def test_portee_des_portraits_et_faits_meme_prefixe(self):
        prefixes = []
        for m in (noir(), crypte()):
            for tour in range(2):
                for mode, ajout in (
                    ('enrichir', {'personnage': 'ilse', 'facette': 'yeux', 'description': 'Ses yeux sont gris.'}),
                    ('etablir_faits', {'type': 'detail', 'ancrage': m.joueur['salle'], 'nom': 'surface',
                                       'genre': 'f', 'texte': 'La surface est rugueuse.'})):
                    reponse = {'mode': mode, 'texte': '', 'faits': [], 'proposition': {'ajouts': [ajout]}}
                    def appeler(instructions, entree, intention, fonction, schema):
                        if fonction == 'auditer_portee':
                            prefixes.append((instructions, copy.deepcopy(schema)))
                            return {}
                        return copy.deepcopy(reponse)
                    mj = MJ()
                    with (patch.object(mj, '_appeler_brut', side_effect=appeler),
                          patch('donjon.mj.controler_portee', return_value=[]),
                          patch('donjon.mj.controler_usages', return_value=[])):
                        mj._appeler('règles', {'faits': {'salle': m.joueur['salle'], 'revision': tour}},
                                    'Décris cette surface.', 'repondre_au_joueur', SCHEMA_REPONSE)
        self.assertEqual(len(prefixes), 8)
        self.assertTrue(all(p == prefixes[0] for p in prefixes))

    def test_sources_et_cibles_hors_scene_toujours_refusees_sans_mutation(self):
        for m in (noir(), crypte()):
            m = recharger(m)
            avant, vue = copy.deepcopy(m.data), regarder(m)
            p = proposition('ouvrir', 'cible_hors_scene')
            refus = []
            for _ in range(2):
                with self.assertRaises(ErreurMonde) as erreur:
                    Moteur(m).preparer(p)
                self.assertTrue(erreur.exception.attendu)
                refus.append((str(erreur.exception), erreur.exception.attendu))
                m = recharger(m)
            self.assertEqual(refus[0], refus[1])
            self.assertEqual(m.data, avant)
            self.assertEqual(regarder(m), vue)
            a = copy.deepcopy(AUDIT)
            a['segments'][0].update(verdict='mecanique', portee_mecanique='etablie', sources=['hors_scene'])
            self.assertTrue(controler('La porte est fermée.', a, {'salle': {}})['obstacles'])
            self.assertEqual(schema_audit({'salle': {}}, 1), schema_audit({'joueur': {}}, 3))

    def test_mesure_ponderee_et_appels_sans_usage(self):
        def appel(tokens, cache, instructions='A'):
            return {'etape': 'appel', 'fonction': 'f', 'instructions': instructions, 'schema': {},
                    'usage': {'input_tokens': tokens, 'input_tokens_details': {'cached_tokens': cache}}}
        resultat = mesurer([{'tours': [{'fil': [appel(100, 0), appel(900, 800),
            {**appel(0, 0, 'B'), 'usage': None}]}]}])
        self.assertEqual(resultat['total']['part_cache'], .8)
        self.assertEqual(resultat['fonctions']['f']['prefixes'], 2)
        self.assertEqual(resultat['total']['sans_usage'], 1)
