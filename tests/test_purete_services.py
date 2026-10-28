"""La clôture découverte par un candidat appartient au choix complet."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification
from donjon.biens import services_proteges
from donjon.esprits import croire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_service_non_defait import serrure
from tests.test_tensions import recharger, vivre


class PureteServicesTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def cesse(self):
        m, id, autre, c = serrure()
        croire(m, id, autre, 'lieu', 'dortoir', 'vu', salle='dortoir', case=None)
        return self.recharge(m), id, c

    def test_lecture_et_devis_isole_purs_puis_publication(self):
        m, id, c = self.cesse()
        avant = copy.deepcopy(m.data)
        self.assertNotIn(c, services_proteges(m, id))
        planification.planifier_pulsion(m, id, {'objet': 'vivres', 'lieu': 'dortoir'})
        self.assertEqual(avant, m.data)
        with patch.object(planification, 'VERIFIER', True):
            with planification.vues_du_choix(m, id):
                resultat = services_proteges(m, id)
                self.assertEqual(avant, m.data)
            self.assertEqual(resultat, services_proteges(m, id))
        self.assertFalse(m.data['services_rendus'])
        self.recharge(m)

    def test_choix_interrompu_meme_apres_choix_imbrique(self):
        m, id, c = self.cesse()
        avant = copy.deepcopy(m.data)
        with patch.object(planification, 'VERIFIER', True):
            with self.assertRaisesRegex(RuntimeError, 'interrompu'):
                with planification.vues_du_choix(m, id):
                    with planification.vues_du_choix(m, id):
                        self.assertNotIn(c, services_proteges(m, id))
                    self.assertEqual(avant, m.data)
                    raise RuntimeError('interrompu')
        self.assertEqual(avant, self.recharge(m).data)
        self.assertIsNone(m._clotures_services)

    def test_choix_imbrique_interrompu_ne_transmet_rien(self):
        m, id, c = self.cesse()
        traces = copy.deepcopy(m.data['services_rendus'])
        with planification.vues_du_choix(m, id):
            with self.assertRaises(RuntimeError):
                with planification.vues_du_choix(m, id):
                    services_proteges(m, id)
                    raise RuntimeError()
        self.assertEqual(traces, self.recharge(m).data['services_rendus'])

    def test_controle_de_purete_echoue_sans_publier(self):
        m, id, c = self.cesse()
        traces = copy.deepcopy(m.data['services_rendus'])
        with patch.object(planification, 'VERIFIER', True):
            with self.assertRaisesRegex(AssertionError, 'méthode candidate'):
                with planification.vues_du_choix(m, id):
                    self.assertNotIn(c, services_proteges(m, id))
                    m.data['_mutation_test'] = True
        del m.data['_mutation_test']
        self.assertEqual(traces, self.recharge(m).data['services_rendus'])

    def test_captures_reelles_lecture_choix_et_laps(self):
        for scenario in ('mine', 'rixe'):
            with self.subTest(scenario=scenario):
                chemin = Path(__file__).parent / f'fixtures/purete232/{scenario}.json.gz'
                with gzip.open(chemin, 'rt', encoding='utf8') as f:
                    m = self.recharge(Monde(json.load(f)))
                # L'acteur et les services viennent de la capture, sans règle de scénario.
                services = copy.deepcopy(m.data['services_rendus'])
                avant = copy.deepcopy(m.data)
                finis = []
                with patch.object(planification, 'VERIFIER', True):
                    for id in dict.fromkeys(s['de'] for s in services):
                        resultat = services_proteges(m, id)
                        self.assertEqual(avant, m.data)
                        with planification.vues_du_choix(m, id):
                            self.assertEqual(resultat, services_proteges(m, id))
                            planification._entrees_communes(planification.vue(m, id))
                            self.assertEqual(avant, m.data)
                        finis.extend(s for s in services if s['de'] == id
                                     and s not in m.data['services_rendus'])
                        avant = copy.deepcopy(m.data)
                self.assertTrue(finis)
                m = self.recharge(m)
                bloc, _ = vivre(m.copier(), 2)
                decoupe, _ = vivre(m.copier(), 1)
                decoupe, _ = vivre(self.recharge(decoupe), 1)
                self.assertEqual(bloc.data, decoupe.data)
                self.assertEqual(regarder(self.recharge(bloc)), regarder(self.recharge(decoupe)))
