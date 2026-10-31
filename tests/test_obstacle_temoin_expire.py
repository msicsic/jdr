"""417 : une vérification conserve la cause et attend son constat."""
import copy
import unittest

from donjon import deliberation as d, memoire, planification as p
from donjon.esprits import croire, lire
from donjon.monde import ErreurMonde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_reessai_obstacle as captures, test_temps_reel as temps
from tests.test_tensions import placer, recharger, vivre


class ObstacleTemoinExpireTests(unittest.TestCase):
    def recharge(self, m):
        avant = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual((n.data, regarder(n), scene_percue(n)), avant)
        return n

    def test_expiration_et_piste_consommee_ne_sont_pas_un_dementi(self):
        m = captures.odon()
        r = copy.deepcopy(lire(m, 'odon')['renoncements']['agenda'][0])
        m.data.update(minutes=500, dixiemes=0)
        self.assertIsNone(d.salle_crue(m, 'odon', 'bram'))
        self.assertIn('bram', d.obstacle_patience(m, 'odon', r['cause']))
        memoire.consommer_hypothese(m, 'odon', 'bram')
        m = self.recharge(m)
        self.assertIn('bram', d.obstacle_patience(m, 'odon', r['cause']))
        # Départ caché : même obstacle et même choix, puis démenti explicite.
        a = self.recharge(m)
        b = self.recharge(m)
        placer(b, 'bram', 'filon', (4, 2))
        for n in (a, b):
            d.choisir(n, 'odon', 500)
            self.assertNotEqual((lire(n, 'odon')['intention'] or {}).get('but'), r['but'])
            self.recharge(n)
        self.assertEqual(lire(a, 'odon')['intention'], lire(b, 'odon')['intention'])
        croire(b, 'odon', 'bram', 'lieu', None, 'vu', salle='bureau', case=None)
        self.assertNotIn('bram', d.obstacle_patience(self.recharge(b), 'odon', r['cause']))

    def test_prefixe_reel_et_suffixe_coupe_gardent_leur_provenance(self):
        m = captures.odon()
        m.data.update(minutes=91, dixiemes=0)
        r = lire(m, 'odon')['renoncements']['agenda'][0]
        candidat = next(c for c in d._candidats(m, 'odon') if c.besoin == 'agenda')
        but, plan = candidat.methode(m, 'odon')
        self.assertTrue(any('suite_conditionnelle' in x.get('contenu', {}) for x in plan))
        self.assertTrue(d.renoncement_tient(m, 'odon', r, (but, plan)))
        # La provenance du contact seul doit survivre à une marche consommée.
        lire(m, 'odon')['intention'] = {'but': but, 'motif': 'agenda',
            'plan': plan[-1:], 'depuis': 91, 'attente': 0}
        m = self.recharge(m)
        self.assertTrue(d.renoncement_tient(m, 'odon', r,
            (but, lire(m, 'odon')['intention']['plan'])))
        # Un autre moyen du même but reste permis. Le suffixe après un
        # contact incertain porte aussi les obstacles ultérieurs du plan.
        contact = {**p._etape('demander', 'bram', contenu={'localisation': 'gaspard'}), 'suppose': True}
        autre = p._couper([contact, p._etape('demander', 'bram', outil='paie')])
        self.assertFalse(d.renoncement_tient(m, 'odon', r, (but, autre)))
        bloque = p._couper([contact, r['cause']['etape']])
        self.assertTrue(d.renoncement_tient(m, 'odon', r, (but, bloque)))
        lire(m, 'odon')['intention']['plan'] = bloque
        self.recharge(m)

    def test_guet_brune_laps_entier_et_decoupe_recharges(self):
        depart = self.recharge(temps.brune_guette())
        fins = []
        for laps in ([34], [17, 17]):
            m = self.recharge(depart.copier())
            for minutes in laps:
                m, _ = vivre(m, minutes)
                m = self.recharge(m)
            self.assertIn('faim', lire(m, 'brune')['renoncements'])
            self.assertTrue(m.objets['reserve']['verrouillee'])
            self.assertNotEqual((lire(m, 'brune')['intention'] or {}).get('motif'), 'faim')
            fins.append(m)
        self.assertEqual(fins[0].data, fins[1].data)
        self.assertEqual(regarder(fins[0]), regarder(fins[1]))
        self.assertEqual(scene_percue(fins[0]), scene_percue(fins[1]))

    def test_provenance_corrompue_refusee_a_la_sauvegarde(self):
        m = captures.odon()
        but = lire(m, 'odon')['renoncements']['agenda'][0]['but']
        for suite in ({}, [], [{'operation': 'inventer'}]):
            with self.subTest(suite=suite):
                n = m.copier()
                lire(n, 'odon')['intention'] = {'but': but, 'motif': 'agenda',
                    'plan': [p._etape('inspecter', lieu='bureau', contenu={'suite_conditionnelle': suite})],
                    'depuis': n.data['minutes'], 'attente': 0}
                with self.assertRaises(ErreurMonde):
                    recharger(n)


if __name__ == '__main__':
    unittest.main()
