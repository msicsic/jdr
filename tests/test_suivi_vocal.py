"""Agenda de protection : portée crue, marche réelle, secours et persistance."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, ouie, planification as p, pnj
from donjon.esprits import croire, lire, percevoir_tous
from donjon.proximite_vocale import arrivees
from donjon.scene import scene_percue
from donjon.temps import MINUTE
from donjon.voix import connaitre
from tests.support import calme, regarder
from tests.test_corps_blessable import passer
from tests.test_empathie import rendu
from tests.test_empathie_peur import scene as scene_compagnie
from tests.test_tensions import placer, recharger


def scene(nom='relais'):
    m, acteur, autre = scene_compagnie(nom)
    calme(m, acteur, autre)
    m.objets[acteur]['profil']['valeurs'].update(empathie=0, altruisme=0)
    m.objets[acteur]['profil']['agendas'] = [{'sorte': 'protéger', 'parametres': {'qui': autre}}]
    connaitre(m, acteur, autre)
    # Ces scènes isolent le suivi de l'interposition et du secours spontané.
    percevoir_tous(m)
    return recharger(m), acteur, autre


def public(m):
    return rendu(m), scene_percue(m)


class SuiviVocalTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(public(m), public(n))
        return n

    def laps(self, m, minutes):
        entier = recharger(m)
        texte = passer(entier, minutes * MINUTE)
        morceaux = recharger(m)
        for _ in range(minutes):
            passer(morceaux, MINUTE)
            morceaux = recharger(morceaux)
        self.assertEqual(entier.data, morceaux.data)
        self.assertEqual(public(entier), public(morceaux))
        return self.recharge(entier), texte

    def test_changement_de_salle_repositionnement_et_appel_de_deux_scenarios(self):
        for nom, destination, position in [('relais', 'crypte', [5, 3]), ('mine', 'filon', [8, 3])]:
            with self.subTest(scenario=nom):
                m, a, b = scene(nom)
                m, texte = self.laps(m, 1)
                self.assertIn("reste à l'écoute", '\n'.join(texte))
                avant = copy.deepcopy(m.objets[a]['position'])
                self.assertEqual(lire(m, a)['intention']['but']['agenda'], 'a1')
                # Nouvelle localisation acquise (donnée d'épreuve), sans consulter
                # la cible réelle lors du devis. La marche, elle, est autonome.
                placer(m, b, destination, position)
                croire(m, a, b, 'lieu', destination, 'vu', salle=destination, case=position)
                self.assertFalse(arrivees(m, a, b)(m.objets[a]['lieu'], tuple(avant)))
                d.choisir(m, a, m.data['minutes'])
                m, _ = self.laps(m, 3)
                self.assertTrue(arrivees(m, a, b)(m.objets[a]['lieu'], tuple(m.objets[a]['position'])))
                self.assertTrue(ouie.s_entendent(m, a, b))
                self.assertTrue(m.objets[a]['position'] != avant or m.objets[a]['lieu'] != ('antichambre' if nom == 'relais' else 'baraquement'))
                self.assertEqual(agendas.projets(m, a)[0]['etat'], 'actif')
                # L'appel réel doit encore traverser l'ouïe, établir le secours
                # et faire choisir le palier d'alarme, avant tout autre projet.
                ouie.retentir(m, b, 'crier', force='cri')
                self.assertTrue(any(s['type'] == 'secours' and s['qui'] == b for s in lire(m, a)['memoire']))
                d.choisir(m, a, m.data['minutes'])
                reaction = lire(m, a)['intention']['but']['type']
                if reaction == 'agenda':
                    # Déjà vu à portée : le secours est constaté et clôturé
                    # immédiatement par la règle existante, sans course vide.
                    self.assertTrue(any(s['type'] == 'secours' and s['qui'] == b and s.get('examine')
                                        for s in lire(m, a)['memoire']))
                    self.assertTrue(any(e['type'] == 'intervention' and e['id'] == a
                                        and b in e['proteges'] for e in m.data['historique_corps']))
                else:
                    self.assertIn(reaction, ('voir', 'proteger'))
                m, _ = self.laps(m, 1)
                self.assertEqual(m.objets[a]['lieu'], destination)
                self.assertTrue(any(c['pnj'] == a and 'passe dans' in c['texte'] for c in m.data['chronique']))

    def test_perdu_recherche_commune_sans_lecture_de_la_position_reelle(self):
        for nom in ('relais', 'mine'):
            m, a, b = scene(nom)
            croire(m, a, b, 'lieu', None, 'vu', salle=None, case=None)
            with p.vues_du_choix(m, a):
                agendas.actualiser(m, a)
            avant = copy.deepcopy(m.data)
            attendu = p.rejoindre(m, a, b)
            plan = agendas.planifier(m, a, 'a1')
            self.assertEqual(plan[1], attendu[0])
            self.assertEqual(m.data, avant)
            n = recharger(m)
            # Faux monde réel, mêmes croyances et aucune perception entre les devis.
            placer(n, b, 'crypte' if nom == 'relais' else 'filon', [5, 3])
            self.assertEqual(plan, agendas.planifier(n, a, 'a1'))
            self.assertTrue(any(g['operation'] == 'inspecter' or g.get('contenu', {}).get('localisation') == b
                                for g in plan[1]))
            d.choisir(m, a, m.data['minutes'])
            m, _ = self.laps(m, 1)
            self.assertEqual(agendas.projets(m, a)[0]['etat'], 'actif')

    def test_priorite_du_palier_superieur(self):
        m, a, b = scene()
        d.choisir(m, a, 0)
        self.assertEqual(lire(m, a)['intention']['but']['agenda'], 'a1')
        # Le désespoir propre passe avant la responsabilité d'agenda.
        lire(m, a)['besoins']['repos'] = 100.
        d.choisir(m, a, 0)
        self.assertEqual(lire(m, a)['intention']['motif'], 'repos')
        self.assertEqual(agendas.projets(m, a)[0]['etat'], 'actif')
        self.recharge(m)

    def test_portee_limite_et_pas_non_percu_ne_font_pas_marcher(self):
        m, a, b = scene('mine')
        # Dernière portée de voix ordinaire dans une même salle (règle des paliers).
        salle = copy.deepcopy(m.data['salles']['baraquement'])
        salle['sorties'] = {}
        salle['plan'].update(origine=[100, 100], sol=['.' * 15] * 3)
        m.data['salles']['epreuve'] = salle
        placer(m, a, 'epreuve', [0, 1])
        placer(m, b, 'epreuve', [12, 1])
        croire(m, a, b, 'lieu', 'epreuve', 'vu', salle='epreuve', case=[12, 1])
        self.assertTrue(arrivees(m, a, b)('epreuve', (0, 1)))
        d.choisir(m, a, 0)
        m, _ = self.laps(m, 3)
        self.assertEqual(m.objets[a]['position'], [0, 1])
        # Une position privée différente ne change ni devis ni arrivées.
        avant = p.proximite(m, a, b, portee='voix')
        placer(m, b, 'filon', [8, 3])
        self.assertEqual(avant, p.proximite(m, a, b, portee='voix'))
        self.recharge(m)

    def test_geometrie_vocale_et_portes_crues_cachees(self):
        m, a, b = scene('mine')
        placer(m, b, 'bureau', [2, 3])
        croire(m, a, b, 'lieu', 'bureau', 'vu', salle='bureau', case=[2, 3])
        # Géométrie réelle et crue identiques pour l'oracle acoustique.
        for ouvert in (False, True):
            m.objets['porte_bureau']['ouverte'] = ouvert
            croire(m, a, 'porte_bureau', 'etat', {'ouverte': ouvert}, 'vu')
            possible = arrivees(m, a, b)
            v = p.Vue(m, a)
            e = p.depart(m, a, v)
            lectures = p._entrees(v, {'pres': (b,), 'portee': 'voix'}, 4, 100)
            for case in ((4, 0), (4, 2), (0, 5)):
                placer(m, a, 'baraquement', case)
                self.assertEqual(possible('baraquement', case), ouie.saisit(m, b, a))
            if not ouvert:
                ferme = lectures
            else:
                self.assertNotEqual(ferme, lectures)
            # Une ouverture privée réelle ne change pas l'estimation.
            m.objets['porte_bureau']['ouverte'] = not ouvert
            self.assertEqual(v.cases_vocales(e, b), p.Vue(m, a).cases_vocales(e, b))
            self.recharge(m)

    def test_cout_et_entrees_de_l_oreille_propre(self):
        m, a, b = scene('mine')
        placer(m, b, 'filon', [8, 3])
        croire(m, a, b, 'lieu', 'filon', 'vu', salle='filon', case=[8, 3])
        with patch.object(p, 'VERIFIER', True):
            devis = p.proximite(m, a, b, portee='voix')
            self.assertGreater(devis[0], 0)
            self.assertTrue(any(g['operation'] == 'aller' for g in devis[1]))
            avant = p._entrees(p.Vue(m, a), {'pres': (b,), 'portee': 'voix'}, 4, 100)
            m.objets[a]['profil']['caracteristiques']['PER'] = 6
            apres = p._entrees(p.Vue(m, a), {'pres': (b,), 'portee': 'voix'}, 4, 100)
            self.assertNotEqual(avant, apres)
            p.proximite(m, a, b, portee='voix')
        self.recharge(m)

    def test_salle_crue_sans_case_est_inspectee(self):
        m, a, b = scene('mine')
        croire(m, a, b, 'lieu', 'baraquement', 'entendu', salle='baraquement', case=None)
        plan = p.proximite(m, a, b, portee='voix')
        self.assertEqual(plan[1][-1]['operation'], 'inspecter')
        self.assertEqual(plan[1][-1]['contenu']['cherche'], b)
        d.choisir(m, a, 0)
        m, _ = self.laps(m, 2)
        self.assertTrue(lire(m, a)['croyances'][b]['lieu'].get('case'))


if __name__ == '__main__':
    unittest.main()
