"""Localiser les participants requis avant le geste, puis constater la rencontre."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, planification as p, pnj
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_empathie import scene
from tests.test_tensions import placer, recharger, vivre


def capture():
    chemin = Path(__file__).parent / 'captures/service-303-tilo.json.gz'
    return Monde(json.loads(gzip.decompress(chemin.read_bytes())))


def mine():
    m, a, b = scene()
    # Même charge durable, autre scénario et autre moyen matériel.
    condition = {'objet': 'vivres', 'servir': b}
    m.objets[a]['profil']['valeurs'].update(altruisme=0, empathie=0)
    m.objets[a]['profil']['pulsions'] = [{'besoin': 'devoir', 'condition': condition}]
    lire(m, a)['pulsions'] = []
    lire(m, a)['besoins']['devoir'] = 80.
    d.choisir(m, a, 0)
    placer(m, b, 'galerie', [2, 2])
    croire(m, a, b, 'lieu', None, 'vu', salle=None, case=None)
    return m


class ServiceRejoindreTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def verifier_chaine(self, fabrique, a, b, repas):
        depart = self.recharge(fabrique())
        self.assertIsNone(d.salle_crue(depart, a, b))
        g = p._etape('servir', repas, contenu={'pour': b})
        v = p.Vue(depart, a)
        e = p.depart(depart, a, v)
        self.assertIsNone(p._mesurer_direct(v, e, [g], e, 1))
        self.assertEqual(pnj.refus_etape(depart, a, [g]), 'participant à localiser')
        ancien = copy.deepcopy(lire(depart, a)['intention'])
        d.choisir(depart, a, depart.data['minutes'])
        i = lire(depart, a)['intention']
        self.assertEqual(i['but'], ancien['but'])
        self.assertTrue(i['plan'])
        self.assertFalse(any(g['operation'] == 'servir' for g in i['plan']))
        self.assertTrue(any(g['contenu'].get('localisation') == b
                            or g['contenu'].get('cherche') == b for g in i['plan']))
        executions = []
        executer = pnj._executer

        def observer(m, id, etape, *args, **kwargs):
            connu = d.salle_crue(m, id, b)
            resultat = executer(m, id, etape, *args, **kwargs)
            if id == a:
                executions.append((copy.deepcopy(etape), resultat, connu))
            return resultat

        with patch.object(pnj, '_executer', observer):
            bloc, lignes = vivre(self.recharge(depart), 6)
        services = [(g, r, s) for g, r, s in executions if g['operation'] == 'servir']
        self.assertTrue(services)
        self.assertTrue(all(r and s is not None for _, r, s in services))
        self.assertTrue(any(g['contenu'].get('localisation') == b
                            or g['contenu'].get('cherche') == b for g, _, _ in executions))
        self.assertLess(bloc.objets[repas]['portions'], depart.objets[repas]['portions'])
        self.assertTrue(any(c['pnj'] == a and 'donne une part' in c['texte']
                            for c in bloc.data['chronique']))
        morceaux = self.recharge(depart)
        lignes_decoupees = []
        for _ in range(6):
            morceaux, texte = vivre(morceaux, 1)
            lignes_decoupees.extend(texte)
        self.assertEqual(bloc.data, morceaux.data)
        self.assertEqual(lignes, lignes_decoupees)
        self.recharge(bloc)
        self.recharge(morceaux)

    def test_capture_reelle_289_tilo_mathurine(self):
        self.verifier_chaine(capture, 'tilo', 'mathurine', 'marmite_1_1')

    def test_mine_mathe_lucien(self):
        self.verifier_chaine(mine, 'mathe', 'lucien', 'vivres')

    def test_position_reelle_ignoree_et_devis_sans_effet(self):
        for fabrique, a, b, repas in ((capture, 'tilo', 'mathurine', 'marmite_1_1'),
                                     (mine, 'mathe', 'lucien', 'vivres')):
            with self.subTest(a=a):
                m = self.recharge(fabrique())
                condition = {'objet': repas, 'servir': b}
                avant = copy.deepcopy(m.data)
                attendu = p.planifier_pulsion(m, a, condition)
                self.assertEqual(m.data, avant)
                for salle in m.data['salles']:
                    n = Monde(copy.deepcopy(avant))
                    n.objets[b].update(lieu=salle, position=[1, 1], position_salle=salle)
                    self.assertEqual(p.planifier_pulsion(n, a, condition), attendu)

    def test_graphe_prepare_le_contact_sans_executer_le_suffixe(self):
        m = mine()
        trouve = p.chercher(m, 'mathe', lambda v, e: e.fait('servi', 'vivres'),
                            {'servir': {'vivres': ('lucien',)}}, emplois=())
        self.assertIsNotNone(trouve)
        self.assertTrue(any(g.get('suppose') for g in trouve[1]))
        self.assertFalse(any(g['operation'] == 'servir' for g in p._couper(trouve[1])))
        self.assertTrue(any(g['operation'] == 'servir' for g in trouve[1]))

    def test_venue_convenue_conserve_le_service(self):
        m, a, b = scene()
        c = {'objet': 'vivres', 'servir': b}
        agendas.prendre(m, a, {'condition': c, 'objet': 'vivres', 'pour': b,
                              'minute': m.data['minutes']})
        placer(m, b, 'galerie', [2, 2])
        croire(m, a, b, 'lieu', None, 'vu', salle=None, case=None)
        m = self.recharge(m)
        plan = p.planifier_tache(m, a, c, b)
        self.assertIsNotNone(plan)
        self.assertEqual(plan[1][-1]['operation'], 'servir')
        self.assertFalse(any(g['contenu'].get('cherche') or g['contenu'].get('localisation')
                             for g in plan[1]))


if __name__ == '__main__':
    unittest.main()
