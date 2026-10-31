"""S1k : recours historiques, admissions copiées et chaînes sauvegardées."""
import copy
import gzip
import json
import unittest
from unittest.mock import patch

from donjon import memoire, pnj
from donjon.deliberation import retenir_refus
from donjon.emissions import lire as emissions
from donjon.esprits import lire, memoriser, percevoir_tous
from donjon.monde import Monde
from donjon.pnj_propositions import _entrees, _tient, plan_recours, rendre_service
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_memoire_refus import RACINE
from tests.test_proposer_recours import scene
from tests.test_rendre_service import scene as service
from tests.test_tache_promise_recours import feu, reserve
from tests.test_tensions import recharger


class RecoursMemoireTests(unittest.TestCase):
    def test_vues_sans_creation_et_admissions_copiees(self):
        m = scene()
        demande = memoire.demande_refusee(m, 'brune')
        condition = {'objet': 'brasero', 'allume': True}
        tentative = {**demande, 'operation': 'demander', 'minute': 0}
        intermediaire = {**tentative, 'via': 'ilse', 'issue': 'preparee',
                        'livraison': 'vivres', 'abouti': False}
        entrees = _entrees(m, 'brune', 'marchand', 'faim', {'type': 'part', 'objet': 'vivres'})
        memoire.retenir_service_tente(m, 'brune', tentative)
        memoire.entreprendre_service(m, 'brune', demande, condition)
        memoire.retenir_intermediaire(m, 'brune', intermediaire)
        memoire.retenir_proposition_tentee(m, 'brune', entrees)
        self.assertIsNone(memoire.demande_refusee(m, 'brune'))
        retenir_refus(m, 'brune', 'marchand', 'demander', 'mefiance', objet='vivres')
        avant = copy.deepcopy(m.data)
        entrees['lien']['bandes'].clear()
        condition.clear()
        memoire.propositions_tentees(m, 'brune')[0]['lien']['bandes'].clear()
        memoire.service_en_cours(m, 'brune')['condition'].clear()
        for entree in (demande, tentative, intermediaire, entrees, condition):
            entree.clear()
        for qui in ('brune', 'inexistant', 'joueur'):
            for vue in (memoire.demande_refusee, memoire.propositions_tentees,
                        memoire.services_tentes, memoire.intermediaires_retenus, memoire.service_en_cours):
                valeur = vue(m, qui)
                if isinstance(valeur, list) and valeur:
                    valeur[0].clear()
                elif valeur:
                    valeur.clear()
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)

    def test_ecritures_intermediaire_ciblees_et_sans_crochets(self):
        m = scene()
        demande = memoire.demande_refusee(m, 'brune')
        tentative = {**demande, 'operation': 'demander', 'minute': 0,
                     'via': 'ilse', 'issue': 'preparee', 'livraison': 'vivres', 'abouti': False}
        for via, issue in (('ilse', 'preparee'), ('aubin', 'preparee'), ('ilse', 'mefiance')):
            memoire.retenir_intermediaire(m, 'brune', {**tentative, 'via': via, 'issue': issue})
        with patch('donjon.esprits.memoriser') as souvenir:
            memoire.retenir_issue_intermediaire(m, 'brune', 'ilse', {'objet': 'vivres'}, 'accepte')
            memoire.affecter_livraison_intermediaire(m, 'brune', 'ilse', 'vivres', 'part_livree')
            memoire.accomplir_livraison_intermediaire(m, 'brune', 'ilse', 'vivres')
            self.assertFalse(memoire.intermediaires_retenus(m, 'brune')[0]['abouti'])
            memoire.accomplir_livraison_intermediaire(m, 'brune', 'ilse', 'part_livree')
            souvenir.assert_not_called()
        stock = memoire.intermediaires_retenus(recharger(m), 'brune')
        self.assertEqual([(s['via'], s['issue'], s['livraison'], s['abouti']) for s in stock],
                         [('ilse', 'accepte', 'part_livree', True), ('aubin', 'preparee', 'vivres', False),
                          ('ilse', 'mefiance', 'vivres', False)])

    def test_predicats_et_survie_hors_tampon(self):
        from donjon import relations
        m = scene()
        # Isoler le temps des évolutions relationnelles historiques : une
        # rancune qui s'estompe serait une amélioration réelle du lien.
        lire(m, 'brune')['relations']['marchand'] = relations._nouvelle(
            m.objets['brune']['profil']['liens']['marchand'])
        demande = {'type': 'part', 'objet': 'vivres'}
        avant = _entrees(m, 'brune', 'marchand', 'faim', demande)
        memoire.retenir_proposition_tentee(m, 'brune', avant)
        for _ in range(45):
            memoriser(m, 'brune', {'type': 'attendu'})
        m.data['minutes'] += 180
        m.data['finances_pnj']['brune'] = 0
        m.objets['crochets'].update(lieu='joueur', proprietaire='joueur')
        m = recharger(m)
        self.assertEqual(memoire.propositions_tentees(m, 'brune'), [avant])
        self.assertTrue(_tient(avant, _entrees(m, 'brune', 'marchand', 'faim', demande)))
        m.data['finances_pnj']['brune'] = avant['pieces'] + 1
        self.assertFalse(_tient(avant, _entrees(recharger(m), 'brune', 'marchand', 'faim', demande)))
        # Le service impossible ne se redévise pas après délai ou perte de moyens.
        m, qui, autre, _ = service(feu)
        m.objets['bois']['charges'] = 0
        percevoir_tous(m)
        self.assertIsNone(rendre_service(m, qui, 'faim', []))
        tentatives = memoire.services_tentes(m, qui)
        m.data['minutes'] += 60
        m = recharger(m)
        with patch('donjon.pnj_propositions._plan_service', side_effect=AssertionError('redévisé')):
            self.assertIsNone(rendre_service(m, qui, 'faim', []))
        self.assertEqual(memoire.services_tentes(m, qui), tentatives)

    def test_projection_de_service_et_validation(self):
        m, qui, autre, condition = service(feu)
        self.assertTrue(plan_recours(m, qui, 'faim', None))
        tentatives, en_cours = memoire.services_tentes(m, qui), memoire.service_en_cours(m, qui)
        memoire.clore_service(m, qui)
        memoire.restaurer_services_devises(m, qui, tentatives, en_cours)
        tentatives.clear()
        en_cours['condition'].clear()
        memoire.verifier_recours(m, qui)
        self.assertEqual(memoire.service_en_cours(recharger(m), qui)['condition'], condition)
        for registre, valeur in (('demande_refusee', {}), ('service_en_cours', {}),
                                 ('recours_services', [{'minute': 1.5}]),
                                 ('recours_intermediaires', [{}]), ('recours_propositions', [{}])):
            copie = m.copier()
            lire(copie, qui)[registre] = valeur
            with self.subTest(registre=registre), self.assertRaises(AssertionError):
                memoire.verifier_recours(copie, qui)

    def continuite(self, initial):
        resultats = []
        for tranches in ((1200,), (300,) * 4):
            m, lignes = recharger(initial), []
            with patch.object(Monde, 'd20', return_value=20):
                for dt in tranches:
                    pnj.avancer(m, ecouler(m, dt), lignes, dt)
                    m = recharger(m)
            public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
            recharge = recharger(m)
            self.assertEqual(recharge.data, m.data)
            self.assertEqual((regarder(recharge), scene_percue(recharge), emissions(recharge)), public)
            resultats.append((copy.deepcopy(m.data), json.dumps(m.data), lignes, public))
        self.assertEqual(*resultats)
        return m

    def test_capture_reelle_et_deux_services_etat_rendu_scene_paroles(self):
        # La capture historique conserve les essais de Brune et Ilse : leur
        # migration, les choix suivants et toute la présentation restent stables.
        with gzip.open(RACINE / 'tests/data/offre-sensee-crue7-353.json.gz', 'rt', encoding='utf-8') as f:
            m = recharger(Monde(json.load(f)))
        self.assertEqual(len(memoire.propositions_tentees(m, 'brune')), 3)
        self.assertEqual(len(memoire.propositions_tentees(m, 'ilse')), 1)
        self.continuite(m)
        for fabrique in (feu, reserve):
            with self.subTest(scene=fabrique.__name__):
                m, qui, autre, _ = service(fabrique)
                plan = plan_recours(m, qui, 'faim', None)
                self.assertTrue(plan)
                self.assertTrue(memoire.services_tentes(m, qui))
                lire(m, qui)['intention']['plan'] = plan
                m = self.continuite(m)
                self.assertTrue(any(s['type'] == 'service_rendu' for s in memoire.episodes(m, autre)))
                self.assertTrue(emissions(m))
                self.assertTrue(m.data['chronique'])

    def test_commissions_deux_scenes_etat_complet(self):
        from tests.test_intermediaires import scene as commission
        from tests.support import sans_souci
        for auberge in (False, True):
            with self.subTest(auberge=auberge):
                m, qui, autre, via = commission(auberge)
                sans_souci(m)
                plan = plan_recours(m, qui, 'faim', None)
                self.assertEqual(plan[-1]['operation'], 'confier')
                lire(m, qui)['intention']['plan'] = plan
                m = self.continuite(m)
                tentative, = memoire.intermediaires_retenus(m, qui)
                self.assertEqual(tentative['issue'], 'accepte')
                self.assertTrue(tentative['abouti'])
                self.assertEqual(m.objets['vivres']['portions'], 7)
                self.assertTrue(emissions(m))


if __name__ == '__main__':
    unittest.main()
