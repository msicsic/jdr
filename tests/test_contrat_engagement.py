"""L'intention survit à sa naissance ; priorités et démentis restent effectifs."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d
from donjon.esprits import croire, lire, percevoir_tous, percus
from donjon.planification import _etape
from donjon.monde import Monde
from tests.test_empathie import scene, executer, rendu
from tests.test_tensions import placer, recharger


class ContratEngagementTests(unittest.TestCase):
    def test_captures_209_reelles_recharge_et_laps_decoupes(self):
        for nom, auteur, minutes in (('mine-42', 'remy', 4), ('auberge-1985', 'mireille', 10)):
            with self.subTest(capture=nom):
                fichier = Path(__file__).parent / 'data' / f'engagement-213-{nom}.json.gz'
                m = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
                m = recharger(m)
                n = recharger(m.copier())
                demandes = []
                choisir = d.choisir

                def observer(monde, id, minute):
                    resultat = choisir(monde, id, minute)
                    if id == auteur:
                        contrat = agendas.contrat_intention(monde, id)
                        if contrat and contrat['demande'] and 'raison' in contrat['demande']:
                            demandes.append(contrat['demande'])
                    return resultat

                with patch.object(d, 'choisir', observer):
                    executer(m, minutes)
                self.assertTrue(demandes, 'le secours historique doit être réellement adopté')
                for _ in range(minutes):
                    executer(n, 1)
                    n = recharger(n)
                m = recharger(m)
                self.assertEqual(m.data, n.data)
                self.assertEqual(rendu(m), rendu(n))
                self.assertTrue(any(c['pnj'] == auteur for c in m.data['chronique']))

    def test_secours_adopte_hors_vue_et_dementi_apres_recharge(self):
        m, auteur, autre = scene()
        d.choisir(m, auteur, m.data['minutes'])
        but = copy.deepcopy(lire(m, auteur)['intention']['but'])
        contrat = agendas.contrat_intention(m, auteur)
        self.assertEqual(contrat['demande']['raison'], {'qui': autre, 'besoin': 'faim'})
        placer(m, autre, 'galerie', [3, 1])
        percevoir_tous(m)
        self.assertNotIn(autre, percus(m, auteur)[0])
        self.assertTrue(lire(m, auteur)['croyances'][autre]['etat']['valeur']['faim'])
        m = recharger(m)
        # Une coupure de plan ne termine pas la condition à servir.
        lire(m, auteur)['intention']['plan'] = []
        d.choisir(m, auteur, m.data['minutes'])
        self.assertEqual(lire(m, auteur)['intention']['but'], but)
        self.assertEqual(agendas.contrat_intention(m, auteur), contrat)
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        etat = dict(lire(m, auteur)['croyances'][autre]['etat']['valeur'], faim=False)
        croire(m, auteur, autre, 'etat', etat, 'vu')
        d.choisir(m, auteur, m.data['minutes'])
        self.assertIsNone(lire(m, auteur)['intention'])
        self.assertIsNone(agendas.contrat_intention(m, auteur))
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))

    def test_preemption_ronde_par_secours_et_accomplissement_decoupe(self):
        m, auteur, autre = scene()
        condition = {'lieu': 'galerie', 'periode': 30}
        m.objets[auteur]['profil']['pulsions'] = [{'besoin': 'devoir', 'condition': condition}]
        lire(m, auteur)['pulsions'] = []
        # La ronde était déjà adoptée avant la découverte du besoin d'autrui.
        lire(m, auteur)['intention'] = {'but': {'type': 'pulsion', **condition},
                                        'motif': 'devoir', 'plan': [], 'depuis': 0, 'attente': 0}
        d.choisir(m, auteur, 0)
        self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
        m = recharger(m)
        n = recharger(m.copier())
        executer(m, 6)
        for _ in range(3):
            executer(n, 2)
            n = recharger(n)
        m = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertLess(lire(m, autre)['besoins']['faim'], 70)
        self.assertEqual(sum(c['pnj'] == auteur and 'donne une part' in c['texte']
                             for c in m.data['chronique']), 1)

    def test_autre_secours_froid_hors_vue_et_accomplissement(self):
        m, auteur, autre = scene(True)
        d.choisir(m, auteur, 0)
        self.assertEqual(agendas.contrat_intention(m, auteur)['demande']['raison']['besoin'], 'chaleur')
        but = copy.deepcopy(lire(m, auteur)['intention']['but'])
        placer(m, autre, 'antichambre', [1, 3])
        percevoir_tous(m)
        self.assertNotIn(autre, percus(m, auteur)[0])
        m = recharger(m)
        d.choisir(m, auteur, 0)
        self.assertEqual(lire(m, auteur)['intention']['but'], but)
        n = recharger(m.copier())
        executer(m, 3)
        for _ in range(3):
            executer(n, 1)
            n = recharger(n)
        m = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertGreater(m.objets['brasero']['combustible'], 8)
        self.assertFalse(any(s['type'] == 'service_rendu' and s['de'] == auteur
                             for s in lire(m, autre)['memoire']))

    def test_garde_vide_marge_et_palier_superieur_apres_recharge(self):
        for marge in (d.INERTIE - 1, d.INERTIE, 100):
            m, auteur, _ = scene()
            garde = {'type': 'garder', 'lieu': m.objets[auteur]['lieu']}
            secours = {'type': 'voir', 'lieu': 'galerie'}
            lire(m, auteur)['intention'] = {'but': garde, 'motif': 'biens', 'plan': [],
                                            'depuis': 0, 'attente': 0}
            m = recharger(m)
            palier = d.Palier.SECOURS if marge == 100 else d.Palier.ROUTINE
            cs = [d.Candidat('devoir', lambda m, i: (secours, [_etape('inspecter', lieu='galerie')]),
                              True, True, d.Urgence(palier, marge, ())),
                  d.Candidat('biens', lambda m, i: (garde, []), True, True,
                              d.Urgence(d.Palier.ROUTINE, 0, ()))]
            with patch.object(d, '_candidats', return_value=cs):
                d.choisir(m, auteur, 0)
            self.assertEqual(lire(m, auteur)['intention']['but'], secours if marge >= d.INERTIE else garde)
            n = recharger(m)
            self.assertEqual(m.data, n.data)
            self.assertEqual(rendu(m), rendu(n))

    def test_echec_libere_l_engagement_et_ses_preferences_de_cible(self):
        m, auteur, autre = scene()
        d.choisir(m, auteur, 0)
        i = lire(m, auteur)['intention']
        self.assertTrue(i['plan'])
        lire(m, auteur)['manque'] = {'minute': 0,
                                    'etape': {k: i['plan'][0][k] for k in ('operation', 'cible', 'outil', 'lieu')}}
        m = recharger(m)
        observes = []

        def candidats(monde, id):
            observes.append(lire(monde, id)['intention'])
            return []

        with patch.object(d, '_candidats', candidats):
            d.choisir(m, auteur, 0)
        self.assertEqual(observes, [None])
        self.assertIsNone(lire(m, auteur)['intention'])
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))


if __name__ == '__main__':
    unittest.main()
