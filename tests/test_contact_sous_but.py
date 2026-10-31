"""Le contact perdu sert le but parent, sans fabriquer sa réussite."""
import gzip
import json
from pathlib import Path
import unittest

from donjon import deliberation as d, planification as p
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger, vivre
from tests.test_voix import hugues_cherche_anselme


def capture(nom):
    with gzip.open(Path(__file__).with_name('data') / ('contact-226-' + nom + '.json.gz'),
                   'rt', encoding='utf8') as f:
        return Monde(json.load(f))


class ContactSousButTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_ilse_recherche_sous_le_parent_securite(self):
        m = self.recharge(capture('crue-7-attente-ilse-10'))
        self.assertIsNone(d.salle_crue(m, 'ilse', 'aubin'))
        d.choisir(m, 'ilse', m.data['minutes'])
        m = self.recharge(m)
        i = lire(m, 'ilse')['intention']
        self.assertEqual(i['motif'], 'securite')
        self.assertEqual(i['but'], {'type': 'abri', 'lieu': None, 'qui': 'aubin'})
        self.assertEqual(i['plan'][-1]['contenu'], {'cherche': 'aubin'})
        self.assertFalse(any(x['operation'] == 'abriter' for x in i['plan']))
        m, _ = vivre(m, 2)
        self.recharge(m)
        self.assertTrue(any(c['pnj'] == 'ilse' and ('appelle' in c['texte'] or 'cherche' in c['texte'])
                            for c in m.data['chronique']))

    def test_brune_question_localisation_garde_enquete_chaleur(self):
        m = self.recharge(capture('crue_hameau-42-attente-brune-160'))
        d.choisir(m, 'brune', m.data['minutes'])
        m = self.recharge(m)
        i = lire(m, 'brune')['intention']
        self.assertEqual(i['but'], {'type': 'enquete', 'besoin': 'chaleur', 'qui': 'ilse'})
        self.assertEqual(i['motif'], 'chaleur')
        self.assertEqual(i['plan'][-1]['contenu']['localisation'], 'ilse')
        self.assertEqual(i['plan'][-1]['contenu']['suite_conditionnelle'], [
            p._etape('demander', 'ilse', contenu={'ressource': 'chaleur'})])
        self.assertFalse(any(x.get('contenu') == {'ressource': 'chaleur'} for x in i['plan']))

    def test_aubin_attend_encore_avec_moyens_connus_inaccessibles(self):
        m = self.recharge(capture('crue_hameau-7-attente-aubin-200'))
        self.assertIsNotNone(p.rejoindre(m, 'aubin', 'marchand'))
        # Connaître déjà les ressources du témoin ne justifie pas une enquête
        # répétée. Le contact ne lève ni la route ni le refus de ressource.
        self.assertIsNone(p.s_enquerir(m, 'aubin', 'chaleur'))
        d.choisir(m, 'aubin', m.data['minutes'])
        self.assertIsNone(lire(self.recharge(m), 'aubin')['intention'])

    def test_autre_scenario_enquete_recherche_puis_question(self):
        from tests.support import lier
        m = hugues_cherche_anselme()
        # Scène d'auteur : seul interlocuteur admissible, perdu de vue.
        v = p.vue(m, 'hugues')
        for autre in v.personnes():
            lier(m, 'hugues', autre, autre == 'anselme', 'vu')
        r = p.s_enquerir(self.recharge(m), 'hugues', 'faim')
        self.assertIsNotNone(r)
        self.assertEqual(r[0], {'type': 'enquete', 'besoin': 'faim', 'qui': 'anselme'})
        self.assertEqual(r[1][-1]['operation'], 'inspecter')
        croire(m, 'hugues', 'anselme', 'lieu', 'couloir', 'vu', salle='couloir', case=None)
        r = p.s_enquerir(self.recharge(m), 'hugues', 'faim')
        self.assertEqual(r[1][-1]['contenu'], {'ressource': 'faim'})

    def test_enquete_autonome_auberge_et_reponse_enregistree(self):
        from tests.support import lier
        m = hugues_cherche_anselme()
        # Scène d'auteur : aucun repas disponible connu et aucun devoir
        # concurrent. Anselme reste un témoin possible, sans savoir deviné.
        e = lire(m, 'hugues')
        e['memoire'] = []
        e['besoins']['faim'] = 90.
        e['besoins']['devoir'] = 0.
        m.objets['hugues']['profil']['pulsions'] = []
        e['pulsions'] = []
        for k, o in m.objets.items():
            if 'portions' in o:
                o['portions'] = 0
                if k in e['croyances'] or d.porte_par(m, k, 'hugues'):
                    etat = e['croyances'].get(k, {}).get('etat', {}).get('valeur', {})
                    croire(m, 'hugues', k, 'etat', {**etat, 'disponible': False}, 'vu')
        for autre in p.vue(m, 'hugues').personnes():
            lier(m, 'hugues', autre, autre == 'anselme', 'vu')
        m = self.recharge(m)
        d.choisir(m, 'hugues', m.data['minutes'])
        self.assertEqual(lire(m, 'hugues')['intention']['but'],
                         {'type': 'enquete', 'besoin': 'faim', 'qui': 'anselme'})
        m, _ = vivre(self.recharge(m), 5)
        m = self.recharge(m)
        self.assertTrue(any(s['operation'] == 'enqueter' and s['de'] == 'anselme'
                            and s.get('besoin') == 'faim' for s in lire(m, 'hugues')['refus']))
        self.assertTrue(any(c['pnj'] == 'hugues' and 'Hugues demande à Anselme' in c['texte']
                            for c in m.data['chronique']))

    def test_recherche_epuisee_et_mefiance_ne_sont_pas_oubliees(self):
        from tests.support import lier
        m = capture('crue-7-attente-ilse-10')
        for salle in m.data['salles']:
            d.recherche_vaine(m, 'ilse', 'aubin', salle)
        for autre in p.vue(m, 'ilse').personnes():
            if autre != 'aubin':
                lier(m, 'ilse', autre, False, 'vu')
        self.assertIsNone(d._plan_abri(self.recharge(m), 'ilse'))
        m.data['minutes'] += 200
        self.assertIsNone(d._plan_abri(self.recharge(m), 'ilse'))

    def test_laps_entier_et_decoupe_monde_rendu(self):
        for nom in ('crue-7-attente-ilse-10', 'crue_hameau-42-attente-brune-160'):
            with self.subTest(capture=nom):
                m = capture(nom)
                entier, _ = vivre(self.recharge(m), 2)
                morceaux, _ = vivre(self.recharge(m), 1)
                morceaux, _ = vivre(self.recharge(morceaux), 1)
                self.assertEqual(entier.data, morceaux.data)
                self.assertEqual(regarder(entier), regarder(morceaux))
                self.assertEqual(scene_percue(entier), scene_percue(morceaux))
                self.recharge(entier)

    def test_parent_apaise_ou_proche_dementi_arrete_la_recherche(self):
        from tests.support import lier
        for apaise in (True, False):
            with self.subTest(apaise=apaise):
                m = capture('crue-7-attente-ilse-10')
                d.choisir(m, 'ilse', m.data['minutes'])
                self.assertEqual(lire(m, 'ilse')['intention']['but']['qui'], 'aubin')
                if apaise:
                    lire(m, 'ilse')['besoins']['securite'] = 0.
                else:
                    lier(m, 'ilse', 'aubin', False, 'vu')
                m = self.recharge(m)
                d.choisir(m, 'ilse', m.data['minutes'])
                i = lire(self.recharge(m), 'ilse')['intention']
                self.assertTrue(i is None or i['but'] != {'type': 'abri', 'lieu': None, 'qui': 'aubin'})
