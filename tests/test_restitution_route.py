"""Restituer : employer le bien en route, conserver un moyen après remise."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as d, planification as p
from donjon.echanges import necessaire
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.scene import scene_percue
from tests import test_echanges_argent as emprunts
from tests.test_empathie import executer, rendu
from tests.test_tensions import placer, recharger


class RestitutionRouteTests(unittest.TestCase):
    def identique_recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        return n

    def avancer_identique(self, m, minutes):
        n = self.identique_recharge(m)
        executer(m, minutes)
        for _ in range(minutes):
            executer(n, 1)
            n = recharger(n)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        return self.identique_recharge(m)

    def test_capture_reelle_421_retour_revalide_et_effectue(self):
        fichier = Path(__file__).parent / 'fixtures/restitution-246-421-4306c14.json.gz'
        m = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
        m = self.identique_recharge(m)
        self.assertEqual(m.data['minutes'], 421)
        self.assertEqual(m.objets['mael']['lieu'], 'crypte')
        self.assertTrue(necessaire(m, 'mael', 'torche'))
        condition = {'objet': 'torche', 'rendre': 'aubin'}
        self.assertIsNotNone(p._rendre(m, 'mael', 'torche', condition))
        d.choisir(m, 'mael', m.data['minutes'])
        self.assertEqual(lire(m, 'mael')['intention']['but'], {'type': 'pulsion', **condition})
        # Deux revalidations de la même intention ne doivent pas l'invalider.
        m = self.identique_recharge(m)
        d.choisir(m, 'mael', m.data['minutes'])
        self.assertEqual(lire(m, 'mael')['intention']['but'], {'type': 'pulsion', **condition})
        m = self.avancer_identique(m, 5)
        self.assertEqual(m.objets['torche']['lieu'], 'aubin')
        self.assertFalse(any(x['objet'] == 'torche' for x in m.data['permissions']))
        self.assertTrue(any('Maël rend' in x['texte'] and '(rendu)' in x['texte']
                            for x in m.data['chronique']))

    def mine(self, eclairee=True, remplacement=False):
        m = emprunts.PretTests().lampe_empruntee()
        m.objets['lampe_gaspard'].update(allume=True, combustible=200)
        m.objets['lampe_baraque'].update(allume=eclairee, combustible=200 if eclairee else 0)
        placer(m, 'remy', 'galerie', (2, 2))
        placer(m, 'gaspard', 'baraquement', (2, 2))
        # Scène d'auteur : seul l'emprunteur agit, les autres attendent.
        for id, o in m.objets.items():
            if o.get('profil'):
                o['profil']['pulsions'] = []
                o['profil']['agendas'] = []
                lire(m, id)['pulsions'] = []
                lire(m, id).pop('agendas', None)
                lire(m, id)['intention'] = None
                lire(m, id)['libre'] = 0 if id == 'remy' else 60000
        lire(m, 'remy')['besoins']['securite'] = 0.
        if remplacement:
            from donjon.deplacement_objet import deplacer
            deplacer(m, 'lampe_remy', 'remy')
            m.objets['lampe_remy'].update(allume=True, combustible=200)
        percevoir_tous(m)
        croire(m, 'remy', 'gaspard', 'lieu', 'baraquement', 'savoir', salle='baraquement', case=[2, 2])
        croire(m, 'remy', 'baraquement', 'etat',
               {'eclairee': eclairee, 'niveau': 2 if eclairee else 0, 'propre': 2 if eclairee else 0}, 'savoir')
        return self.identique_recharge(m)

    def test_autre_lampe_depuis_galerie_sombre(self):
        with patch('donjon.agendas._naissances', return_value=None):
            m = self.mine()
            self.assertTrue(necessaire(m, 'remy', 'lampe_gaspard'))
            d.choisir(m, 'remy', m.data['minutes'])
            self.assertEqual(lire(m, 'remy')['intention']['but'].get('rendre'), 'gaspard')
            self.assertTrue(m.objets['lampe_gaspard']['allume'])
            m = self.avancer_identique(m, 5)
            self.assertEqual(m.objets['lampe_gaspard']['lieu'], 'gaspard')
            self.assertFalse(any(x['objet'] == 'lampe_gaspard' for x in m.data['permissions']))
            self.assertTrue(any('Rémy rend' in x['texte'] and '(rendu)' in x['texte']
                                for x in m.data['chronique']))

    def test_besoin_apres_remise_sans_et_avec_autre_moyen(self):
        with patch('donjon.agendas._naissances', return_value=None):
            for remplacement in (False, True):
                with self.subTest(remplacement=remplacement):
                    m = self.mine(False, remplacement)
                    retour = p._rendre(m, 'remy', 'lampe_gaspard',
                                       {'objet': 'lampe_gaspard', 'rendre': 'gaspard'})
                    self.assertEqual(retour is not None, remplacement)
                    m = self.avancer_identique(m, 5)
                    self.assertEqual(m.objets['lampe_gaspard']['lieu'], 'gaspard' if remplacement else 'remy')
                    if remplacement:
                        self.assertEqual(m.objets['lampe_remy']['lieu'], 'remy')
                        self.assertTrue(m.objets['lampe_remy']['allume'])
