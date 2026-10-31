"""S1h : preuves détachées, révisions historiques et reprise publique complète."""
import copy
import json
import unittest

from donjon import eau, esprits, memoire
from donjon.emissions import lire as paroles
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_avis_reels import capture
from tests.test_memoire_localisation import acces_croyances
from tests import test_prevision_bornee, test_relations_statuts
from tests.test_tensions import recharger, vivre


class EauStatutsTests(unittest.TestCase):
    def test_vues_pures_profondes_absence_et_preuves_negatives(self):
        m, sujet, qui, *_ = test_relations_statuts.StatutsTests().scene()
        esprits.croire(m, qui, 'crypte', 'eau', 0, 'vu', niveau=None,
                       repere=[0, 2], montee=-5)
        esprits.croire(m, qui, 'crypte', 'prevision', [0, 2, -5], 'dit:aubin', .7, rang=2)
        esprits.croire(m, qui, sujet, 'statuts', [], 'savoir')
        avant = copy.deepcopy(m.data)
        for vue, cible in ((memoire.mesure_eau, 'crypte'), (memoire.avis_eau, 'crypte'),
                           (memoire.statuts_connus, sujet)):
            self.assertIsNone(vue(m, 'absent', cible))
        self.assertEqual(memoire.mesures_eau(m, 'absent'), {})
        self.assertEqual(memoire.statuts_connus(m, qui, sujet)['valeur'], [])
        self.assertEqual(memoire.mesure_eau(m, qui, 'crypte')['valeur'], 0)
        for preuve in (memoire.mesure_eau(m, qui, 'crypte'),
                       memoire.mesures_eau(m, qui)['crypte'],
                       esprits.croyance(m, qui, 'crypte', 'eau')):
            preuve['repere'][0] = -1
        for preuve in (memoire.avis_eau(m, qui, 'crypte'),
                       memoire.prevision(m, qui, 'crypte'),
                       esprits.prevision(m, qui, 'crypte'),
                       esprits.croyance(m, qui, 'crypte', 'prevision')):
            preuve['valeur'][0] = -1
            preuve['rang'] = 0
        for preuve in (memoire.statuts_connus(m, qui, sujet),
                       esprits.croyance(m, qui, sujet, 'statuts')):
            preuve['valeur'].append({'titre': 'faux'})
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)
        # Le chemin qualitatif rend aussi une copie, même quand il n'est pas borné.
        esprits.croire(m, qui, 'crypte', 'prevision', False, 'savoir')
        avant = copy.deepcopy(m.data)
        esprits.prevision(m, qui, 'crypte')['valeur'] = True
        self.assertIs(memoire.avis_eau(recharger(m), qui, 'crypte')['valeur'], False)
        self.assertEqual(m.data, avant)

    def test_propriete_de_statut_imbriquee_et_inventaire(self):
        m, sujet, qui, *_ = test_relations_statuts.StatutsTests().scene()
        avant = copy.deepcopy(m.data)
        for c in (memoire.statuts_connus(m, qui, sujet),
                  esprits.croyance(m, qui, sujet, 'statuts')):
            c['valeur'][0]['lieux'].clear()
            c['valeur'][0]['domaines'].append('combat')
        self.assertEqual(m.data, avant)
        for attribut in memoire.ATTRIBUTS_EAU_STATUTS:
            with self.subTest(attribut=attribut):
                source = f'cle = {attribut!r}; stock = e["croyances"]; c = stock[s][cle]; c["valeur"] = None'
                self.assertIn(('<module>', "c['valeur']"), acces_croyances(source))
                self.assertTrue(acces_croyances(
                    f'for a in e["croyances"].values():\n c = a.get({attribut!r}); c.clear()'))

    def test_constat_posterieur_retire_durablement_l_avis_sans_effacer_la_mesure(self):
        m = test_prevision_bornee.PrevisionBorneeTests().scene()
        esprits.croire(m, 'ilse', 'beffroi', 'prevision', False, 'dit:aubin', minute=99)
        mesure = memoire.mesure_eau(m, 'ilse', 'echoppe')
        eau.observer(m, 'ilse', 'beffroi')
        self.assertIsNone(memoire.avis_eau(m, 'ilse', 'beffroi'))
        self.assertEqual(memoire.mesure_eau(m, 'ilse', 'echoppe'), mesure)
        m = recharger(m)
        self.assertIsNone(memoire.avis_eau(m, 'ilse', 'beffroi'))
        avant = copy.deepcopy(m.data)
        for _ in range(2):
            esprits.prevision(m, 'ilse', 'beffroi')
            memoire.statuts_connus(m, 'ilse', 'aubin')
        self.assertEqual(m.data, avant)

    def test_avis_reels_deux_auditeurs_laps_et_publication_rechargee(self):
        # Captures historiques du 124 : Aubin prévient Gorm puis Ilse.
        for graine in (500, 2024):
            with self.subTest(graine=graine):
                initial = capture(graine)
                bloc, lignes = vivre(recharger(initial), 10)
                coupe, suite = recharger(initial), []
                for _ in range(10):
                    coupe, nouvelles = vivre(coupe, 1)
                    suite.extend(nouvelles)
                    coupe = recharger(coupe)
                self.assertTrue(any(c.get('avis_exprime') for c in bloc.data['chronique']))
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(json.dumps(bloc.data), json.dumps(coupe.data))
                self.assertEqual(lignes, suite)
                public = regarder(bloc), scene_percue(bloc), copy.deepcopy(paroles(bloc))
                for reprise in (recharger(bloc), coupe):
                    self.assertEqual(reprise.data, bloc.data)
                    self.assertEqual((regarder(reprise), scene_percue(reprise), paroles(reprise)), public)


if __name__ == '__main__':
    unittest.main()
