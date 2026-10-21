import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.spatial import installer


class PrisesLocalesTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_defi(depart="fixe")
        installer(self.m)
        self.m.joueur.update(salle='echoppe', position=[6, 5])
        self.m.memoriser('je prends le pied de biche',
                        "Tu es dans la Conduite basse ; retourne dans l'échoppe pour le prendre.")

    def test_formulations_simples_executees_malgre_ancien_refus(self):
        for phrase in ('je ramasse le pied de biche', 'je prend le pied de biche',
                       'je prends le pied-de-biche', 'ramasser le pied de biche',
                       'ramasse le pied-de-biche', 'prends le pied de biche'):
            with self.subTest(phrase=phrase):
                m = self.m.copier()
                p = analyser(m, phrase)
                self.assertEqual(p['action'], 'prendre')
                moteur = Moteur(m)
                moteur.executer(moteur.preparer(p))
                self.assertEqual(m.objets['pied_de_biche']['lieu'], 'joueur')

    def test_aucune_condition_question_ou_seconde_action_ignoree(self):
        avant = copy.deepcopy(self.m.data)
        for phrase in ('je ramasse le pied de biche ?',
                       'je ramasse le pied de biche si Gorm accepte',
                       'je ramasse discrètement le pied de biche',
                       'je ramasse le pied de biche discrètement',
                       'je prends le pied de biche et je force la porte',
                       'je prends le pied de biche avec mon couteau',
                       'je ne prends pas le pied de biche'):
            with self.subTest(phrase=phrase):
                self.assertIsNone(analyser(self.m, phrase))
        self.assertEqual(self.m.data, avant)

    def test_prise_locale_respecte_portee_et_propriete(self):
        self.m.joueur['position'] = [5, 4]
        moteur = Moteur(self.m)
        with self.assertRaisesRegex(ErreurMonde, 'Approche-toi'):
            moteur.preparer(analyser(self.m, 'je ramasse le pied de biche'))
        self.m.joueur['position'] = [6, 5]
        self.m.objets['pied_de_biche']['proprietaire'] = 'marchand'
        with self.assertRaises(ErreurMonde):
            moteur.preparer(analyser(self.m, 'je ramasse le pied de biche'))
        self.assertEqual(self.m.objets['pied_de_biche']['lieu'], 'echoppe')

    def test_boucle_complete_mj_actif_sans_appel_pour_ramasser(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / 'defi.json'
            self.m.sauver(chemin)
            with patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}), \
                 patch.object(MJOpenAI, '_appeler', side_effect=AssertionError('Appel LLM inattendu')) as appel, \
                 patch('builtins.input', side_effect=['je ramasse le pied de biche', 'quitter']), \
                 patch('sys.stdout', io.StringIO()):
                self.assertEqual(jeu.main(['--console', '--connexion', 'api', '--save', str(chemin)]), 0)
            appel.assert_not_called()
            self.assertEqual(Monde.charger(chemin).objets['pied_de_biche']['lieu'], 'joueur')
