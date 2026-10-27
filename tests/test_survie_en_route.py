"""Sortir d'un séjour dans l'eau, sans transformer une traversée en séjour."""
import unittest

from donjon import deliberation, eau, planification
from donjon.esprits import croire, lire
from donjon.rendu import regarder
from donjon.temps import MINUTE
from tests.test_corps_blessable import passer
from tests.test_route_admissible import scene
from tests.test_tensions import placer, recharger


def sejour(qui):
    m = scene('auteur-100' if qui == 'ilse' else 'crue500-160')
    placer(m, qui, 'beffroi', (5, 2))
    eau.percevoir(m, qui)
    # Le scénario de l'autre lot éprouvait un trajet vers le feu. Ici le
    # séjour humide doit cesser même sans inquiétude et pendant un répit.
    e = lire(m, qui)
    e['intention'] = None
    e['besoins']['securite'] = 0
    e['renoncements']['securite'] = m.data['minutes'] * MINUTE
    return recharger(m)


class SurvieEnRouteTests(unittest.TestCase):
    def test_sejour_humide_repit_et_recharge_sur_deux_personnes(self):
        for qui in ('brune', 'ilse'):
            with self.subTest(qui=qui):
                m = sejour(qui)
                ici = m.objets[qui]['lieu']
                self.assertGreater(eau.eau_crue(m, qui, ici), 0)
                self.assertLess(eau.attendue(m, qui, ici), eau.NOYEE_CM)
                self.assertTrue(eau.en_peril(m, qui))
                deliberation.choisir(m, qui, m.data['minutes'])
                self.assertEqual(lire(m, qui)['intention']['but'],
                                 {'type': 'abri', 'lieu': 'chambre_cloche'})
                a, b = recharger(m), recharger(m)
                passer(a, 5 * MINUTE)
                for _ in range(20):
                    passer(b, MINUTE // 4)
                    b = recharger(b)
                a = recharger(a)
                self.assertEqual(a.data, b.data)
                self.assertEqual(regarder(a), regarder(b))
                self.assertEqual(eau.profondeur(a, a.objets[qui]['lieu']), 0)

    def test_une_traversee_admissible_continue(self):
        m = sejour('brune')
        e = lire(m, 'brune')
        e['intention'] = {'but': {'type': 'abri', 'lieu': 'chambre_cloche'},
                          'motif': 'securite', 'depuis': m.data['minutes'], 'attente': 0,
                          'plan': [planification._etape('aller', lieu='chambre_cloche')]}
        m = recharger(m)
        self.assertFalse(eau.en_peril(m, 'brune'))
        a, b = recharger(m), recharger(m)
        passer(a, 5 * MINUTE)
        for _ in range(5):
            passer(b, MINUTE)
            b = recharger(b)
        a = recharger(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(a.objets['brune']['lieu'], 'chambre_cloche')

    def test_un_reflexe_en_attente_ne_retient_pas_dans_l_eau(self):
        m = sejour('ilse')
        lire(m, 'ilse')['intention'] = {
            'but': {'type': 'alerte', 'lieu': 'antichambre'}, 'motif': 'alerte',
            'plan': [planification._etape('inspecter', lieu='beffroi')],
            'depuis': m.data['minutes'], 'attente': 1}
        lire(m, 'ilse')['patience'] = m.data['minutes'] * MINUTE
        m = recharger(m)
        deliberation.choisir(m, 'ilse', m.data['minutes'])
        self.assertEqual(lire(m, 'ilse')['intention']['but'],
                         {'type': 'abri', 'lieu': 'chambre_cloche'})
        a, b = recharger(m), recharger(m)
        passer(a, 5 * MINUTE)
        for _ in range(5):
            passer(b, MINUTE)
            b = recharger(b)
        a = recharger(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(eau.profondeur(a, a.objets['ilse']['lieu']), 0)

    def test_la_verite_distante_ne_declenche_pas_l_evacuation(self):
        m = sejour('brune')
        qui, ici = 'brune', m.objets['brune']['lieu']
        for c in lire(m, qui)['croyances'].values():
            c.pop('eau', None)
        m = recharger(m)
        self.assertGreater(eau.profondeur(m, ici), 0)
        self.assertFalse(eau.en_peril(m, qui))
        v = planification.Vue(m, qui)
        avant = planification._entrees(v, {}, 4, 100)
        croire(m, qui, ici, 'eau', 1, 'vu', niveau=None, repere=None, montee=None)
        m = recharger(m)
        self.assertTrue(eau.en_peril(m, qui))
        self.assertNotEqual(avant, planification._entrees(planification.Vue(m, qui), {}, 4, 100))
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_un_geste_fini_au_sec_a_temps_ne_devient_pas_une_attente(self):
        m = sejour('ilse')
        from donjon.deplacement_objet import deplacer
        deplacer(m, 'vivres', 'ilse')
        croire(m, 'ilse', 'vivres', 'lieu', 'ilse', 'vu', salle='beffroi', case=None)
        croire(m, 'ilse', 'vivres', 'etat', {'disponible': True}, 'vu')
        e = lire(m, 'ilse')
        e['besoins']['faim'] = 100
        e['patience'] = None
        e['intention'] = {'but': {'type': 'manger', 'objet': 'vivres'}, 'motif': 'faim',
                          'plan': [planification._etape('aller', lieu='beffroi'),
                                   planification._etape('manger', 'vivres')],
                          'depuis': m.data['minutes'], 'attente': 0}
        m = recharger(m)
        self.assertFalse(eau.en_peril(m, 'ilse'))
        a, b = recharger(m), recharger(m)
        passer(a, 5 * MINUTE)
        for _ in range(5):
            passer(b, MINUTE)
            b = recharger(b)
        a = recharger(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertLess(lire(a, 'ilse')['besoins']['faim'], deliberation.DESESPOIR)
        self.assertEqual(eau.profondeur(a, a.objets['ilse']['lieu']), 0)


if __name__ == '__main__':
    unittest.main()
