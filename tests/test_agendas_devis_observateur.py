"""258 : le devis estimé n'interroge jamais le tiers réel."""
import copy
import unittest

from donjon import agendas, planification, relations
from donjon.esprits import croire, lire, percoit
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_agendas_jugement_mandat as jugement
from tests.test_avis_menace import relation
from tests.test_social import placer
from tests.test_tensions import recharger


class DevisObservateurTests(unittest.TestCase):
    def test_perception_du_devis_sans_position_joueur_ni_fuite_du_reel(self):
        from donjon.esprits import percus
        from donjon import pnj
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            with self.subTest(sorte=sorte):
                m, p, transmis = self.scene(sorte, cible)
                avant = copy.deepcopy(m.data)
                contexte = planification.ContexteDevis('marchand', 'aubin', transmis)
                projection = contexte.projeter(m)
                self.assertNotIn('position', projection.joueur)
                vus, champ = percus(projection, 'aubin')
                self.assertNotIn('joueur', vus)
                etape = planification._etape('confier', cible)
                contact = pnj._contact_vocal_cru(projection, 'aubin', etape, cible)
                # Le joueur réel peut changer de côté ; le même devis garde
                # strictement les données et perceptions de l'observateur.
                n = m.copier()
                n.joueur.update(salle='crypte', position=[1, 1])
                autre = contexte.projeter(n)
                self.assertEqual(percus(autre, 'aubin'), (vus, champ))
                self.assertEqual(pnj._contact_vocal_cru(autre, 'aubin', etape, cible), contact)
                self.assertEqual(projection.data, autre.data)
                self.assertIsNotNone(self.devis(m, p, transmis))
                self.assertEqual(m.data, avant)
                self.recharge(m)

    def scene(self, sorte='amener', cible='brune'):
        m, p = jugement.JugementMandatTests().scene(sorte, cible)
        if sorte == 'informer':
            # Dans la preuve 257, seul Aubin sait ce contenu. Pour pouvoir
            # l'estimer sans le lire, Gorm doit l'apprendre explicitement.
            croire(m, 'marchand', 'brasero', 'lieu', 'antichambre', 'savoir',
                   salle='antichambre', case=None)
        # Communication hypothétique explicite, pas assimilation de l'esprit.
        transmis = [(s, a) for s, c in lire(m, 'marchand')['croyances'].items() for a in c]
        return m, p, transmis

    def devis(self, m, p, transmis):
        avant = copy.deepcopy(m.data)
        d = agendas.devis_observateur(m, 'marchand', p['parent'], 'aubin',
                                     p['sorte'], p['parametres'], transmis=transmis)
        self.assertEqual(m.data, avant)
        return d

    def recharge(self, m):
        avant, texte, scene = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual(regarder(n), texte)
        self.assertEqual(scene_percue(n), scene)
        return n

    def test_deux_charges_sans_lecture_privee_et_recharge(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            with self.subTest(sorte=sorte):
                m, p, transmis = self.scene(sorte, cible)
                estime = self.devis(m, p, transmis)
                self.assertIsNotNone(estime)
                reel = agendas.devis_mandat(m, 'marchand', p['parent'], 'aubin', sorte, p['parametres'])
                self.assertIsNotNone(reel)
                contexte = planification.ContexteDevis('marchand', 'aubin', transmis)
                projection = contexte.projeter(m).data
                for mutation in ('lieu', 'savoir', 'possession', 'liens', 'capacites'):
                    n = m.copier()
                    if mutation == 'lieu':
                        placer(n, 'aubin', 'chambre_cloche', [1, 1])
                        self.assertFalse(percoit(n, 'marchand', 'aubin'))
                    elif mutation == 'savoir':
                        lire(n, 'aubin')['croyances'].pop(cible, None)
                    elif mutation == 'possession':
                        n.objets['cle']['lieu'] = 'aubin'
                    elif mutation == 'liens':
                        relation(n, 'aubin', cible, peur=100, rancune=100, affection=100)
                    else:
                        n.objets['aubin']['profil']['caracteristiques']['DEX'] = 20
                        n.objets['aubin']['profil']['valeurs']['honnetete'] = 100
                        n.objets['aubin']['profil']['capacites'] = ['crochetage']
                        lire(n, 'aubin')['besoins']['faim'] = 100
                    self.assertEqual(lire(n, 'marchand'), lire(m, 'marchand'))
                    self.assertEqual(contexte.projeter(n).data, projection, mutation)
                    self.assertEqual(self.devis(self.recharge(n), p, transmis), estime, mutation)
                    if mutation == 'savoir':
                        self.assertIsNone(agendas.devis_mandat(n, 'marchand', p['parent'], 'aubin', sorte, p['parametres']))
                self.assertEqual(agendas.devis_mandat(self.recharge(m), 'marchand', p['parent'], 'aubin', sorte, p['parametres']), reel)

    def test_depart_cru_change_le_devis_des_deux_charges(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, p, transmis = self.scene(sorte, cible)
            avant = self.devis(m, p, transmis)
            croire(m, 'marchand', 'aubin', 'lieu', 'chambre_cloche', 'savoir',
                   salle='chambre_cloche', case=None)
            self.assertNotEqual(self.devis(self.recharge(m), p, transmis), avant)

    def test_moyens_crus_et_entrees_completes(self):
        m, p, transmis = self.scene()
        c = planification.ContexteDevis('marchand', 'aubin', transmis)
        n = c.projeter(m)
        v = planification.vue(n, 'aubin')
        avant = planification._entrees(v, {}, 8, 4000)
        self.assertNotIn('cle', planification.depart(n, 'aubin', v).portes)
        croire(m, 'marchand', 'cle', 'lieu', 'aubin', 'savoir', salle='antichambre', case=None)
        n = c.projeter(self.recharge(m))
        v = planification.vue(n, 'aubin')
        self.assertIn('cle', planification.depart(n, 'aubin', v).portes)
        self.assertNotEqual(planification._entrees(v, {}, 8, 4000), avant)

    def test_possession_crue_change_le_devis_des_deux_charges(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, p, transmis = self.scene(sorte, cible)
            for qui, salle in [('aubin', 'crypte'), (cible, 'beffroi')]:
                croire(m, 'marchand', qui, 'lieu', salle, 'savoir', salle=salle, case=None)
            avant = self.devis(m, p, transmis)
            croire(m, 'marchand', 'cle', 'lieu', 'aubin', 'savoir', salle='crypte', case=None)
            apres = self.devis(self.recharge(m), p, transmis)
            self.assertIsNotNone(apres)
            self.assertNotEqual(apres, avant)

    def test_savoir_non_transmis_et_depart_inconnu(self):
        m, p, transmis = self.scene()
        c = planification.ContexteDevis('marchand', 'aubin')
        n = c.projeter(m)
        self.assertNotIn('brune', lire(n, 'aubin')['croyances'])
        self.assertIsNone(self.devis(m, p, []))
        lire(m, 'marchand')['croyances'].pop('aubin')
        self.assertIsNone(self.devis(self.recharge(m), p, []))
        with self.assertRaises(ValueError):
            planification.ContexteDevis('marchand', 'aubin', [('absent', 'lieu')]).projeter(self.scene()[0])

    def test_information_originale_257_privee_avant_apprentissage(self):
        m, p = jugement.JugementMandatTests().scene('informer', 'ilse')
        transmis = [(s, a) for s, c in lire(m, 'marchand')['croyances'].items() for a in c]
        self.assertIsNone(self.devis(self.recharge(m), p, transmis))
        lire(m, 'aubin')['croyances'].pop('ilse', None)
        self.assertIsNone(self.devis(self.recharge(m), p, transmis))
        croire(m, 'marchand', 'brasero', 'lieu', 'antichambre', 'savoir',
               salle='antichambre', case=None)
        self.assertIsNotNone(self.devis(self.recharge(m), p, transmis))

    def test_relations_refus_et_autorite_viennent_de_observateur(self):
        m, p, transmis = self.scene()
        relation(m, 'marchand', 'brune', peur=90, ascendant=100)
        n = planification.ContexteDevis('marchand', 'aubin', transmis).projeter(m)
        self.assertEqual(relations.axes(n, 'aubin', 'brune'), relations.axes(n, 'marchand', 'brune'))
        self.assertEqual(relations.autorite_estimee(m, 'marchand', 'brune', 'antichambre', 'amener')['bonus'], 0)
        croire(m, 'marchand', 'marchand', 'statuts', [
            {'titre': 'responsable', 'lieux': ['antichambre'], 'domaines': ['amener']}], 'savoir')
        self.assertEqual(relations.autorite_estimee(m, 'marchand', 'brune', 'antichambre', 'amener')['bonus'], 3)
        relation(m, 'brune', 'marchand', ascendant=100, dette=100)
        self.assertEqual(relations.autorite_estimee(self.recharge(m), 'marchand', 'brune', 'antichambre', 'amener')['ascendant'], 0)
        avant = self.devis(m, p, transmis)
        lire(m, 'marchand')['refus'].append({'de': 'brune', 'operation': 'confier',
            'objet': 'brune', 'raison': 'refus', 'minute': m.data['minutes']})
        self.assertNotEqual(self.devis(self.recharge(m), p, transmis), avant)

    def test_caches_reel_et_estime_separes(self):
        m, p, transmis = self.scene()
        reel = agendas.devis_mandat(m, 'marchand', p['parent'], 'aubin', p['sorte'], p['parametres'])
        estime = self.devis(m, p, transmis)
        self.assertEqual(self.devis(m, p, transmis), estime)
        self.assertEqual(agendas.devis_mandat(m, 'marchand', p['parent'], 'aubin', p['sorte'], p['parametres']), reel)
        self.assertTrue(any(isinstance(k[0], tuple) and k[0][0] == 'observateur' for k in planification._MEMOIRE))


if __name__ == '__main__':
    unittest.main()
