"""S1g : preuves matérielles pures et reprise de deux services historiques."""
import copy
import json
import unittest

from donjon import memoire
from donjon.biens import capacites_crues
from donjon.esprits import croire, croyance
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.emissions import lire as paroles
from tests.test_service_non_defait import cas_217, serrure
from tests.test_tensions import recharger, vivre


class MaterielTests(unittest.TestCase):
    def test_absence_fin_negative_et_proprietes_inconnues(self):
        m = cas_217()
        avant = copy.deepcopy(m.data)
        self.assertIsNone(memoire.fin_connue(m, 'absent', 'torche'))
        self.assertIsNone(memoire.etat_connu(m, 'absent', 'torche'))
        self.assertEqual(m.data, avant)
        croire(m, 'brune', 'torche', 'fin', None, 'essai')
        croire(m, 'brune', 'torche', 'etat', {'allume': False}, 'vu')
        m = recharger(m)
        self.assertIsNone(memoire.fin_connue(m, 'brune', 'torche')['valeur'])
        etat = memoire.etat_connu(m, 'brune', 'torche')['valeur']
        self.assertIs(etat['allume'], False)
        self.assertNotIn('charge', etat)

    def test_copies_profondes_de_toutes_les_voies_et_capacites_sans_reel(self):
        m = cas_217()
        croire(m, 'brune', 'torche', 'etat', {'allume': False, 'charge': True}, 'vu')
        croire(m, 'brune', 'torche', 'fin', None, 'essai')
        m.objets['torche'].update(allume=False, combustible=0)
        self.assertIn('lumiere', capacites_crues(m, 'brune', 'torche'))
        avant = copy.deepcopy(m.data)
        for preuve in (memoire.etat_connu(m, 'brune', 'torche'),
                       memoire.fait_brut(m, 'brune', 'torche', 'etat'),
                       memoire.faits_connus(m, 'brune', 'torche')['etat'],
                       croyance(m, 'brune', 'torche', 'etat')):
            preuve['valeur']['charge'] = False
            preuve['source'] = 'devine'
        self.assertEqual(m.data, avant)
        for attribut in memoire.ATTRIBUTS_MATERIELS - {'etat'}:
            valeur = None if attribut == 'fin' else False if attribut == 'verrouillee' else 2
            croire(m, 'brune', 'torche', attribut, valeur, 'savoir')
            avant = copy.deepcopy(m.data)
            croyance(m, 'brune', 'torche', attribut)['valeur'] = 'modifie'
            self.assertEqual(m.data, avant)
        self.assertEqual(m.data, recharger(m).data)
        croire(m, 'brune', 'torche', 'fin', 'detruit', 'vu')
        self.assertEqual(capacites_crues(recharger(m), 'brune', 'torche'), set())

    def test_services_feu_reel_et_serrure_laps_entier_decoupe_et_rendu(self):
        for initial in (cas_217(), serrure()[0]):
            with self.subTest(scenario=initial.data.get('scenario')):
                bloc, lignes = vivre(recharger(initial), 2)
                coupe, suite = recharger(initial), []
                for _ in range(2):
                    coupe, nouvelles = vivre(coupe, 1)
                    suite.extend(nouvelles)
                    coupe = recharger(coupe)
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(json.dumps(bloc.data), json.dumps(coupe.data))
                self.assertEqual(lignes, suite)
                public = (regarder(bloc), scene_percue(bloc), copy.deepcopy(paroles(bloc)))
                reprise = recharger(bloc)
                self.assertEqual(public, (regarder(reprise), scene_percue(reprise), paroles(reprise)))
