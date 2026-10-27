"""Un déplacement interne ne change jamais la présence en départ."""
import unittest

from donjon import planification as plans, pnj, presence
from donjon.esprits import lire
from donjon.rendu import regarder
from donjon.spatial import vue_memorisee, _pas_possibles
from tests.test_depart_definitif import scene
from tests.test_tensions import recharger, vivre, placer


class SortieInterneTests(unittest.TestCase):
    def preuve(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        return n

    def test_routes_recherche_et_marche_avec_et_sans_cases(self):
        for cases in (True, False):
            with self.subTest(cases=cases):
                m, dehors = scene()
                m.data['mode_cases'] = cases
                # Couper aussi l'autre route intérieure vers la même salle :
                # l'interdiction porte sur les transitions, pas sur son nom.
                for s, piece in m.data['salles'].items():
                    for sortie in piece['sorties'].values():
                        if sortie['vers'] == dehors:
                            sortie['exterieur'] = True
                m = self.preuve(m)
                v = plans.Vue(m, 'ilse')
                e = plans.depart(m, 'ilse', v)
                self.assertNotIn(dehors, v.salles)
                self.assertIsNone(v.route(e, dehors))
                self.assertIsNone(pnj.chemin(m, 'ilse', e.salle, dehors))
                visites = lire(m, 'ilse')['visites']
                visites.update({s: 0 for s in v.salles})
                visites[dehors] = -10
                recherche = plans._chercher(v, e, 'marchand')
                if recherche is not None:
                    self.assertNotEqual(recherche[3].salle, dehors)
                if cases:
                    self.assertIsNone(pnj._marcher(m, 'ilse', lambda s, c: s == dehors, []))
                else:
                    pnj._pas(m, 'ilse', {'vers': dehors, 'exterieur': True}, [])
                self.assertFalse(presence.parti(m, 'ilse'))
                self.assertEqual(m.objets['ilse']['lieu'], e.salle)
                self.preuve(m)

    def test_cle_recherche_et_cache_geometrique_changent_avec_les_issues(self):
        m, _ = scene()
        sortie = m.data['salles']['antichambre']['sorties']['ouest']
        sortie['exterieur'] = False
        avant = plans._entrees(plans.Vue(m, 'ilse'), [], 3, 50)
        with vue_memorisee(m):
            # Chauffer le cache joueur avant le calcul interne.
            pas_joueur = _pas_possibles(m, True)('antichambre', (0, 3), (-1, 0))
            self.assertIsNotNone(pas_joueur)
            sortie['exterieur'] = True
            self.assertIsNone(_pas_possibles(presence.interieur(m), True)(
                'antichambre', (0, 3), (-1, 0)))
        apres = plans._entrees(plans.Vue(m, 'ilse'), [], 3, 50)
        self.assertNotEqual(avant, apres)
        self.preuve(m)

    def test_destination_accessible_par_un_passage_interne_reste_admissible(self):
        m, destination = scene()
        # La même destination est intérieure depuis la crypte : seul le
        # franchissement déclaré terminal est interdit, jamais son identifiant.
        placer(m, 'ilse', 'crypte', (3, 3))
        m = self.preuve(m)
        for cases in (True, False):
            m.data['mode_cases'] = cases
            v = plans.Vue(m, 'ilse')
            e = plans.depart(m, 'ilse', v)
            self.assertIn(destination, v.salles)
            route = v.route(e, destination)
            self.assertIsNotNone(route)
            self.assertFalse(any(s.get('exterieur') for s in route))
        self.preuve(m)

    def test_pas_prepare_avant_changement_de_presence_est_revalide(self):
        m, destination = scene()
        avant = m.objets['ilse']['lieu']
        pnj._avancer_de(m, 'ilse', [(destination, (8, 3), None, (-1, 0))], False, [])
        # La copie d'une ancienne sortie n'a pas encore le marqueur terminal.
        pnj._pas(m, 'ilse', {'vers': destination}, [])
        self.assertEqual(m.objets['ilse']['lieu'], avant)
        self.assertFalse(presence.parti(m, 'ilse'))
        self.preuve(m)

    def test_ronde_exterieure_sans_depart_et_laps_decoupe(self):
        from tests.support import calme
        m, dehors = scene('aubin')
        calme(m, 'marchand', 'brune', 'ilse', 'aubin')
        # Un autre but que chercher quelqu'un, donné par les données ordinaires.
        m.objets['aubin']['profil']['pulsions'] = [
            {'besoin': 'securite', 'condition': {'lieu': dehors, 'periode': 1}}]
        lire(m, 'aubin')['pulsions'] = [None]
        lire(m, 'aubin')['besoins']['securite'] = 90.0
        lire(m, 'aubin')['visites'][dehors] = -100
        m = self.preuve(m)
        entier, _ = vivre(recharger(m), 2)
        morceaux = recharger(m)
        for _ in range(2):
            morceaux, _ = vivre(morceaux, 1)
        self.assertEqual(entier.data, morceaux.data)
        self.assertEqual(regarder(entier), regarder(morceaux))
        self.assertFalse(presence.parti(entier, 'aubin'))
        self.preuve(entier)


if __name__ == '__main__':
    unittest.main()
