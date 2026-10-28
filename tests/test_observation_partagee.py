"""Chronologie et précision des faits partagés, de la parole à la sauvegarde."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import pnj, social
from donjon.esprits import croire, lire
from donjon.monde import Monde, ErreurMonde
from donjon.rendu import regarder as rendu
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_constats_partages import scene
from tests.test_deja_dit import confier
from tests.test_social import recharger
from tests.test_sait_observations import mots_enregistres


class ObservationPartageeTests(unittest.TestCase):
    def verifier_recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(rendu(m), rendu(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        for qui in ('brune', 'aubin', 'ilse'):
            self.assertEqual(mots_enregistres(m, qui), mots_enregistres(r, qui))
        return r

    def test_capture_hameau_219_estimation_ancienne_ne_reouvre_pas_la_redite(self):
        data = json.loads(gzip.decompress((Path(__file__).parent /
            'data/partagee-hameau-1985-219.json.gz').read_bytes()))
        resultats = []
        for tranches in ((1800,), (150,) * 12):
            m = Monde(copy.deepcopy(data))
            debut = len(m.data['chronique'])
            with patch.object(Monde, 'd20', return_value=20):
                for dt in tranches:
                    minutes = ecouler(m, dt)
                    pnj.avancer(m, minutes, [], dt)
                    m = self.verifier_recharge(m)
            paroles = [c for c in m.data['chronique'][debut:] if c.get('constat_confie')
                       and '79 cm' in c['texte']]
            # Une mise à jour (stable, 216) est licite ; l'estimation de 211
            # ne doit pas la contredire à nouveau à chaque minute.
            self.assertLessEqual(len(paroles), 1, paroles)
            for qui, autre in (('aubin', 'brune'), ('brune', 'aubin')):
                for _, n, _, _ in social.nouvelles(m, qui):
                    if n.get('attribut') == 'eau' and n['objet'] == 'crypte':
                        self.assertFalse(social._nouveau(m, qui, autre, n))
            resultats.append(m.data)
        self.assertEqual(*resultats)

    def test_autre_scenario_mesure_sans_vitesse_nefface_pas_la_direction(self):
        m = scene()
        n = {'type': 'constat', 'objet': 'echoppe', 'attribut': 'eau',
             'valeur': 35, 'observe': 0, 'details': {'montee': 12}}
        social.retenir_dit(m, 'ilse', 'marchand', n)
        partiel = {**n, 'observe': 2, 'details': {}}
        social._retenir_audience(m, [('ilse', 'marchand', partiel)])
        m = self.verifier_recharge(m)
        self.assertFalse(social._nouveau(m, 'ilse', 'marchand', n))
        self.assertFalse(social._nouveau(m, 'ilse', 'marchand', partiel))
        # La date du niveau seul ne rajeunit pas la direction ancienne.
        self.assertTrue(social._nouveau(m, 'ilse', 'marchand',
            {**n, 'observe': 1, 'details': {'montee': -12}}))
        # Une vraie observation postérieure de décrue reste une nouvelle.
        ecouler(m, 1800)
        croire(m, 'ilse', 'echoppe', 'eau', 34, 'vu', montee=-12)
        m, dit, _ = confier(m)
        self.assertTrue(dit)
        self.assertTrue(any('34 cm' in c['texte'] for c in m.data['chronique']))
        self.verifier_recharge(m)

    def test_auditeur_de_dos_recoit_encore_le_constat_non_partage(self):
        from donjon.esprits import constater, percoit
        from tests.support import regarder
        m = scene()
        m.objets['vivres'].update(lieu='antichambre', position=[3, 3])
        m.objets['ilse']['position'] = [2, 5]
        regarder(m, 'ilse', 'vivres')
        m.objets['marchand']['orientation'] = 'sud'
        self.assertTrue(percoit(m, 'ilse', 'marchand'))
        self.assertFalse(percoit(m, 'marchand', 'vivres'))
        constater(m, 'ilse', 'vivres', 'vu')
        n = {'type': 'constat', 'objet': 'vivres', 'attribut': 'etat',
             'valeur': {'disponible': False}}
        self.assertFalse(social.deja_dit(self.verifier_recharge(m), 'ilse', 'marchand', n))
        m, dit, _ = confier(m)
        self.assertTrue(dit)
        self.assertTrue(any('épuisés' in c['texte'] for c in m.data['chronique']))
        self.verifier_recharge(m)

    def test_date_du_suivi_invalide_refusee(self):
        m = scene()
        social.retenir_dit(m, 'ilse', 'marchand', {'type': 'constat',
            'objet': 'echoppe', 'attribut': 'eau', 'valeur': 35})
        fait = lire(m, 'ilse')['faits_dits']['["echoppe","eau"]']
        fait['portee_date_a']['marchand'] = 'hier'
        with self.assertRaisesRegex(ErreurMonde, 'Faits dits invalides'):
            recharger(m)
