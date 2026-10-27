"""Contrat force : MJ simulé, console, corps et rendu relus depuis la sauvegarde."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon import corps
from donjon.dialogues import interlocuteurs
from donjon.esprits import percevoir_tous
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.narration import consigner, controler
from donjon.rendu import regarder
from tests.test_tenir import situation
from tests.test_trainer import scene as scene_trainer
from tests.test_enfermer import scene as scene_enfermer
from tests.test_tensions import recharger
from donjon.deplacement_objet import deplacer


def console(m, p, demande, scenario='--rixe'):
    reponse = {'mode': 'action', 'texte': '', 'faits': [], 'proposition': p}
    def appeler(*args):
        if args[3] == 'auditer_action':
            return {'conforme': True, 'motif': ''}
        return copy.deepcopy(reponse)
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / 'copie.json'
        m.sauver(chemin)
        with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
              patch.object(MJOpenAI, '_appeler_brut', side_effect=appeler),
              patch.object(type(m), 'd20', return_value=20),
              patch('builtins.input', side_effect=['mj ' + demande, 'tenter', 'quitter']),
              patch('sys.stdout', io.StringIO()) as sortie):
            assert jeu.main(['--console', scenario, '--save', str(chemin), '--connexion', 'api']) == 0
        return Monde.charger(chemin), sortie.getvalue()


class ForceLunaTests(unittest.TestCase):
    def test_destination_du_corps_dans_la_fiche_et_la_contre_revue(self):
        import json
        from tools.banc_parties import preparer
        from donjon.couverture_action import entree
        from tests.test_tensions import placer
        scenes = []
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / 'scene.json'
            preparer(json.loads(Path('tests/data/bancs/force-4f-trainer.json').read_text(encoding='utf-8')), chemin)
            scenes.append((Monde.charger(chemin), 'brune', 'sud'))
        m, c = scene_trainer()
        m.joueur.update(salle='echoppe', position=[8, 3], orientation='ouest')
        placer(m, c, 'antichambre', (0, 3))
        percevoir_tous(m)
        scenes.append((m, c, 'ouest'))
        for m, c, direction in scenes:
            salle = m.joueur['salle']
            plan = Moteur(m).preparer(proposition('trainer', c, direction))
            nom = m.data['salles'][salle]['nom']
            self.assertIn(nom, plan.information)
            self.assertIn(nom, entree('je traîne ce corps ici', plan, m)['plan']['information'])
            texte = Moteur(m).executer(plan)
            m = recharger(m)
            self.assertEqual(m.objets[c]['lieu'], salle)
            self.assertIn('traîné', texte)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_prendre_lier_delier_liberer_et_tuer_via_console(self):
        for cible in ('brune', 'aubin'):
            for action in ('saisir', 'ligoter', 'delier', 'liberer', 'tuer'):
                with self.subTest(cible=cible, action=action):
                    m = situation(cible)
                    m.joueur['stats']['FOR'] = 20
                    for i, o in m.objets.items():
                        if o['type'] == 'personnage' and (action != 'saisir' or i != cible):
                            corps.endormir(m, i)
                    if action in ('delier', 'liberer'):
                        from donjon.banc_pnj import appliquer_etats
                        appliquer_etats(m, [cible + ':ligote'])
                    if action == 'liberer':
                        lien = corps.corps(m, cible).pop('lie')
                        corps.corps(m, 'joueur')['lie'] = lien
                        m.objets[lien['lien']]['lieu'] = 'joueur'
                    percevoir_tous(m)
                    outil = 'corde_test' if action == 'ligoter' else ''
                    p = proposition(action, 'joueur' if action == 'liberer' else cible, outil)
                    plan = Moteur(m).preparer(p)
                    self.assertTrue(plan.confirmation)
                    m, texte = console(m, p, action + ' ' + m.objets[cible]['nom'])
                    if action == 'tuer':
                        self.assertEqual(m.objets[cible]['type'], 'depouille')
                        self.assertIn('tué', texte)
                        self.assertIn('corps', regarder(m))
                    elif action == 'ligoter':
                        self.assertIn('lie', corps.corps(m, cible))
                        self.assertIn('ligot', regarder(m))
                        self.assertIn('maintenant ligotée', texte)
                    elif action == 'saisir':
                        self.assertEqual(corps.corps(m, cible).get('tenu_par'), 'joueur')
                        self.assertIn('saisi', texte.lower())
                    else:
                        self.assertNotIn('lie', corps.corps(m, 'joueur' if action == 'liberer' else cible))
                        self.assertIn('liens', texte)
                    self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_trainer_et_verrouiller_deux_scenes_console(self):
        for scenario in ('relais', 'auberge'):
            m, c = scene_trainer(scenario)
            avant = list(m.joueur['position'])
            m, texte = console(m, proposition('trainer', c, 'est'), 'je traîne ce corps vers l’est',
                               '--defi' if scenario == 'relais' else '--auberge')
            self.assertEqual(m.objets[c]['position'], avant)
            self.assertIn('traîné', texte)
            self.assertEqual(regarder(m), regarder(recharger(m)))
        for salle in ('bureau', 'reserve'):
            m, porte = scene_enfermer(salle=salle)
            deplacer(m, 'passe', 'joueur')
            m.objets[porte]['verrouillee'] = False
            m, texte = console(m, proposition('verrouiller', porte, 'passe'), 'je verrouille la porte', '--mine')
            self.assertTrue(m.objets[porte]['verrouillee'])
            self.assertIn('verrouill', texte)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_corps_invente_refuse_avant_enregistrement_apres_recharge(self):
        for texte in ('Brune est morte.', 'Brune perd connaissance.', 'Brune est ligotée.', 'Brune est blessée.'):
            m = recharger(situation())
            avant = copy.deepcopy(m.data)
            ligne = {'indice': 0, 'verdict': 'invention_protegee', 'portee_mecanique': 'sans_fondement',
                     'sources': [], 'motif': 'Le corps ne l’établit pas.'}
            faits = {'objet:brune': {'etat_corps': corps.visible(m, 'brune')}}
            self.assertTrue(controler(texte, {'segments': [ligne]}, faits)['obstacles'])
            with self.assertRaises(ErreurMonde):
                consigner(m, {'texte': texte, '_audit': {'texte_initial': texte, 'segments': [ligne], 'faits': faits}})
            m = recharger(m)
            self.assertEqual(m.data, avant)
            self.assertNotIn(texte, str(m.data))
            self.assertTrue(corps.conscient(m, 'brune'))

    def test_invention_corporelle_ne_parvient_pas_a_la_console(self):
        from tests.test_narration import dialogue, segment
        for cible, invention in (('brune', 'Brune est morte.'), ('aubin', 'Aubin perd connaissance.')):
            m = situation(cible)
            with tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / 'copie.json'
                m.sauver(chemin)
                sorties = [x for _ in range(3) for x in
                           (dialogue(invention), segment('invention_protegee', motif='État du corps absent.'))]
                with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                      patch.object(MJOpenAI, '_appeler_brut', side_effect=sorties),
                      patch('builtins.input', side_effect=['mj Que vois-je ?', 'quitter']),
                      patch('sys.stdout', io.StringIO()) as sortie):
                    self.assertEqual(jeu.main(['--console', '--rixe', '--save', str(chemin), '--connexion', 'api']), 0)
                reprise = Monde.charger(chemin)
            self.assertNotIn(invention, sortie.getvalue())
            self.assertTrue(corps.conscient(reprise, cible))
            self.assertEqual(corps.visible(m, cible), corps.visible(reprise, cible))
            self.assertNotIn(invention, str(reprise.data.get('narrations_mj', [])))
            self.assertEqual(regarder(reprise), regarder(recharger(reprise)))

    def test_locuteur_devenu_inconscient_ou_mort_refuse_meme_audit_favorable(self):
        for cible in ('brune', 'aubin'):
            for mort in (False, True):
                m = situation(cible)
                faits = {'interlocuteurs': interlocuteurs(m)}
                self.assertIn(cible, faits['interlocuteurs'])
                texte = '« Bonjour à toi. »'
                ligne = {'indice': 0, 'verdict': 'parole', 'portee_mecanique': 'aucune',
                         'sources': [], 'locuteur': cible, 'citation': 'Bonjour à toi.', 'entites': [], 'motif': ''}
                corps.mourir(m, cible) if mort else corps.endormir(m, cible)
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                self.assertNotIn(cible, interlocuteurs(m))
                with self.assertRaises(ErreurMonde):
                    consigner(m, {'texte': texte, '_audit': {'texte_initial': texte, 'segments': [ligne],
                                                          'faits': faits, 'fondement': '', 'fondement_paroles': ''}})
                m = recharger(m)
                self.assertEqual(m.data, avant)
                self.assertNotIn(texte, str(m.data))
                self.assertEqual(regarder(m), regarder(recharger(m)))
