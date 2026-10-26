"""Dépendances et durée de vie des reprises exactes du planificateur."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.monde import Monde


def capture():
    chemin = Path(__file__).parent / 'data/cout-12h/auberge-1985-600.json.gz'
    return Monde(json.loads(gzip.decompress(chemin.read_bytes())))


class EntreesTests(unittest.TestCase):
    def test_gestes_lisent_indirectement_l_allure_des_trajets(self):
        m = capture()
        v = p.Vue(m, 'joss')
        e = p.depart(m, 'joss', v)
        resultats = []
        for allure in (15, 30):
            etat = e.apres(allure=allure)
            resultats.append([(g[2][0]['lieu'], float(g[1]).hex())
                for g in p.gestes(v, etat, {}, p.a_mange)
                if not isinstance(g, p.SuiteDifferee)
                and g[2] and g[2][0]['operation'] == 'aller'])
        self.assertEqual([s for s, _ in resultats[0]], [s for s, _ in resultats[1]])
        self.assertNotEqual(resultats[0], resultats[1])

    def test_cases_de_toutes_les_salles_conservees_sauf_acteur(self):
        m = capture()
        v = p.Vue(m, 'joss')
        croyances = copy.deepcopy(p.lire(m, 'joss')['croyances'])
        for qui in ('joss', 'odile'):
            croyances.setdefault(qui, {})['lieu'] = {
                'valeur': 'salle_commune', 'salle': 'salle_commune', 'case': [2, 3]}
        a = p._cases_lues(v, croyances)
        self.assertNotIn('joss', [x[0] for x in a])
        self.assertIn(['odile', 'salle_commune', [2, 3]], a)
        croyances['odile']['lieu']['case'] = [3, 3]
        self.assertNotEqual(a, p._cases_lues(v, croyances))

    def test_signes_bruts_ne_sont_pas_relus_par_la_cle(self):
        m = capture()
        v = p.Vue(m, 'joss')
        # Les effets déjà dérivés de la garde et des relations restent relevés.
        with patch('donjon.signes.actives', side_effect=AssertionError('lecture morte')):
            p._entrees_communes(v)

    def test_premier_epuisement_certifie_et_libere_les_noeuds(self):
        chemin = Path(__file__).parent / 'data/cout-12h/mine-1985-480.json.gz'
        m = Monde(json.loads(gzip.decompress(chemin.read_bytes())))
        with patch.object(p, '_MEMOIRE', {}), patch.object(p, '_GRAPHES', {}), \
                patch.object(p, '_IMPOSSIBLES', {}), p.diagnostics() as ds:
            r = p.chercher(m, 'remy', p.a_mange, memo=['faim'], emplois=('manger',), motif='faim')
            self.assertIsNone(r)
            self.assertEqual(ds[-1]['preuve_issue'], 'epuise')
            self.assertTrue(next(iter(p._IMPOSSIBLES.values()))[1])
            self.assertEqual(set(next(iter(p._GRAPHES.values()))[1]), {'discretion'})
            p._MEMOIRE.clear()
            self.assertIsNone(p.chercher(m, 'remy', p.a_mange, memo=['faim'], emplois=('manger',), motif='faim'))
            self.assertEqual(ds[-1]['noeuds'], 0)
            self.assertTrue(ds[-1]['impossible'])

