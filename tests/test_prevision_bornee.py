"""Le sec borne un niveau extrapolé, sans fabriquer une vitesse mesurée."""
import copy
import unittest

from donjon import eau, esprits, planification
from donjon.crue import nouvelle_crue
from donjon.rendu import regarder
from tests.test_social import recharger


class PrevisionBorneeTests(unittest.TestCase):
    def scene(self, qui='ilse'):
        m = nouvelle_crue(42, depart='fixe')
        for a in esprits.lire(m, qui)['croyances'].values():
            a.pop('eau', None)
        m.data['minutes'] = 100
        esprits.croire(m, qui, 'echoppe', 'eau', 20, 'vu',
                       niveau=-100, repere=[100, -100], montee=30)
        m.data['minutes'] = 400
        return recharger(m)

    def test_sec_borne_le_niveau_commun_et_la_cle_sans_changer_la_pente(self):
        for qui in ('ilse', 'aubin'):
            with self.subTest(qui=qui):
                m = self.scene(qui)
                ancien = copy.deepcopy(esprits.lire(m, qui)['croyances']['echoppe']['eau'])
                v = planification.Vue(m, qui)
                cle = planification._entrees(v, {}, 8, 4000)
                self.assertEqual(eau.attendue(m, qui, 'echoppe'), 200)
                # La crue historique est désormais redescendue : ce sol est sec.
                self.assertEqual(eau.profondeur(m, 'beffroi'), 0)
                eau.observer(m, qui, 'beffroi')
                m = recharger(m)
                self.assertEqual(eau.estimation(m, qui)[2], 30)
                self.assertEqual(eau.attendue(m, qui, 'beffroi', horizon=0), 0)
                self.assertEqual(eau.attendue(m, qui, 'echoppe', horizon=0), 60)
                self.assertEqual(eau.attendue(m, qui, 'echoppe'), 90)
                self.assertEqual(eau.attendue(m, qui, 'echoppe', projection=True), (20, 60, .5))
                self.assertEqual(esprits.lire(m, qui)['croyances']['echoppe']['eau'], ancien)
                self.assertNotEqual(cle, planification._entrees(planification.Vue(m, qui), {}, 8, 4000))
                self.assertEqual(m.data, recharger(m).data)
                self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_sans_observation_contraire_la_prevision_reste(self):
        m = self.scene()
        e = eau.estimation(m, 'ilse')
        # Revoir un sol plus haut que la droite n'est pas une réfutation.
        eau.observer(m, 'ilse', 'chambre_cloche')
        self.assertEqual(e, eau.estimation(recharger(m), 'ilse'))
        m.data['minutes'] += 60
        self.assertEqual(eau.attendue(m, 'ilse', 'echoppe'), 230)
        # Une modification cachée de la crue n'est pas une observation.
        m.data['crue']['tirage']['hauteur_pic_cm'] += 500
        self.assertEqual(eau.attendue(recharger(m), 'ilse', 'echoppe'), 230)

    def test_avis_quantitatif_borne_sans_mesure_ni_mutation_de_l_avis(self):
        m = self.scene()
        for a in esprits.lire(m, 'ilse')['croyances'].values():
            a.pop('eau', None)
        esprits.croire(m, 'ilse', 'echoppe', 'prevision', [100, -100, 30], 'dit:aubin')
        avis = copy.deepcopy(esprits.lire(m, 'ilse')['croyances']['echoppe']['prevision'])
        eau.observer(m, 'ilse', 'beffroi')
        m = recharger(m)
        self.assertIsNone(eau.estimation(m, 'ilse'))
        self.assertEqual(eau.attendue(m, 'ilse', 'echoppe'), 90)
        self.assertEqual(esprits.lire(m, 'ilse')['croyances']['echoppe']['prevision'], avis)
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_mesure_plus_recente_et_ordre_des_croyances(self):
        m = self.scene()
        eau.observer(m, 'ilse', 'beffroi')
        esprits.croire(m, 'ilse', 'crypte', 'eau', 5, 'essai', niveau=-95,
                       repere=[400, -95], montee=None)
        m = recharger(m)
        self.assertEqual(eau.attendue(m, 'ilse', 'crypte', horizon=0), 5)
        self.assertEqual(eau.estimation(m, 'ilse')[2], 30)
        e = eau.estimation(m, 'ilse')
        c = esprits.lire(m, 'ilse')['croyances']
        esprits.lire(m, 'ilse')['croyances'] = dict(reversed(list(c.items())))
        self.assertEqual(e, eau.estimation(m, 'ilse'))

    def test_le_sec_ne_devient_pas_une_trace_d_eau_par_arrondi(self):
        m = self.scene()
        c = esprits.lire(m, 'ilse')['croyances']['echoppe']['eau']
        c.update(montee=5)
        m.data['minutes'] = 582
        eau.observer(m, 'ilse', 'beffroi')
        m = recharger(m)
        self.assertEqual(eau.estimation(m, 'ilse'), (582, -60, 5))
        self.assertEqual(eau.attendue(m, 'ilse', 'beffroi', horizon=0), 0)
        self.assertEqual(eau.attendue(m, 'ilse', 'beffroi', projection=True), (0, 0, 5 / 60))
