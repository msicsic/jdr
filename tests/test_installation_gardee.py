"""Briser une installation lèse son responsable cru, sans propriété inventée."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, biens, pnj, planification as plans, relations
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.rendu import regarder
from donjon.moteur import Moteur, proposition
from tests import test_petits_correctifs as anciens
from tests.test_tensions import placer, recharger, vivre


def scene(connue=True):
    m = anciens.ForcerTests().brune_aux_vannes(douceur=80)
    deplacer(m, 'vivres', 'beffroi', position=[4, 3])
    croire(m, 'brune', 'vivres', 'lieu', 'beffroi', 'savoir', salle='beffroi', case=[4, 3])
    croire(m, 'brune', 'porte', 'verrouillee', True, 'savoir')
    deplacer(m, 'cle', 'marchand')
    placer(m, 'marchand', 'crypte', (5, 3))
    percevoir_tous(m)
    if connue:
        croire(m, 'brune', 'cle', 'lieu', 'marchand', 'vu', salle=None, case=None)
    else:
        lire(m, 'brune')['croyances'].pop('cle', None)
    return m


class InstallationGardeeTests(unittest.TestCase):
    def preuve(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        return n

    def test_demande_plutot_que_bris_et_laps(self):
        m = self.preuve(scene())
        self.assertEqual(biens.a_autrui(m, 'porte', 'brune', 'frapper'), 'marchand')
        self.assertIsNone(biens.a_autrui(m, 'porte', 'brune'))
        self.assertNotIn('proprietaire', m.objets['porte'])
        plan = plans.planifier(m, 'brune', 'faim')
        self.assertTrue(any(e['operation'] == 'demander' and e['outil'] == 'cle' for e in plan[1]), plan)
        self.assertNotIn('frapper', [e['operation'] for e in plan[1]])
        entier, _ = vivre(recharger(m), 3)
        decoupe = recharger(m)
        for _ in range(3):
            decoupe, _ = vivre(decoupe, 1)
        self.assertEqual(entier.data, decoupe.data)
        self.assertEqual(regarder(entier), regarder(decoupe))
        self.assertGreater(entier.objets['porte']['integrite'], 0)
        self.preuve(entier)

    def test_aubin_froid_devant_la_porte_du_hameau(self):
        from donjon.banc_pnj import creer
        from tests.support import calme
        m = creer('crue_hameau', 1, 'fixe')
        calme(m, *m.data['esprits'])
        placer(m, 'aubin', 'crypte', (6, 3))
        placer(m, 'marchand', 'crypte', (5, 3))
        deplacer(m, 'cle', 'marchand')
        deplacer(m, 'pied_de_biche', 'aubin')
        m.joueur.update(salle='crypte', position=[5, 4])
        # Scène équivalente : les autres foyers sont épuisés ; le poêle du
        # guet est le recours chaud derrière la porte, comme dans la revue.
        for o, x in m.objets.items():
            if o != 'poele_guet' and 'allume' in x:
                x['allume'] = False
                if 'combustible' in x:
                    x['combustible'] = 0
        for o, c in lire(m, 'aubin')['croyances'].items():
            if o != 'poele_guet' and 'allume' in m.objets.get(o, {}):
                c.pop('etat', None)
        croire(m, 'aubin', 'cle', 'lieu', 'marchand', 'vu', salle=None, case=None)
        croire(m, 'aubin', 'porte', 'verrouillee', True, 'savoir')
        lire(m, 'aubin')['besoins']['chaleur'] = 85.0
        percevoir_tous(m)
        m = self.preuve(m)
        with patch.object(biens, 'responsable_cru', side_effect=lambda m, o, id: biens.proprietaire(m, o)):
            ancien = plans.planifier(m, 'aubin', 'chaleur')
        self.assertIn('frapper', [e['operation'] for e in ancien[1]], ancien)
        plan = plans.planifier(m, 'aubin', 'chaleur')
        self.assertIsNotNone(plan)
        self.assertTrue(any(e['operation'] == 'demander' and e['outil'] == 'cle' for e in plan[1]), plan)
        self.assertNotIn('frapper', [e['operation'] for e in plan[1]])
        n, _ = vivre(m, 3)
        self.assertGreater(n.objets['porte']['integrite'], 0)
        self.assertTrue(any('demande' in c['texte'] and 'clé' in c['texte']
                            for c in n.data.get('chronique', []) if c['pnj'] == 'aubin'))
        self.preuve(n)

    def test_joueur_frappe_et_temoin_reagit_par_le_moteur(self):
        m = scene()
        placer(m, 'marchand', 'crypte', (6, 2))
        m.objets['marchand'].pop('orientation', None)
        m.joueur.update(salle='crypte', position=[8, 3])
        deplacer(m, 'pied_de_biche', 'joueur')
        croire(m, 'joueur', 'cle', 'lieu', 'marchand', 'vu', salle=None, case=None)
        croire(m, 'marchand', 'cle', 'lieu', 'marchand', 'vu', salle=None, case=None)
        percevoir_tous(m)
        moteur = Moteur(self.preuve(m))
        avant = relations.axes(moteur.monde, 'marchand', 'joueur')['confiance']
        with patch('donjon.monde.Monde.d20', return_value=20):
            texte = moteur.executer(moteur.preparer(proposition('frapper', 'porte', 'pied_de_biche')))
        n = self.preuve(moteur.monde)
        self.assertLess(n.objets['porte']['integrite'], m.objets['porte']['integrite'])
        self.assertLess(relations.axes(n, 'marchand', 'joueur')['confiance'], avant)
        self.assertTrue(any(s['type'] == 'vu_agir' and s.get('victime') == 'marchand'
                            for s in lire(n, 'marchand')['memoire']))
        self.assertIn('abîmée', texte)
        self.assertIn('La porte étanche du beffroi est abîmée.', n.data['journal'][-1]['faits'])

    def test_ignorance_et_responsable_change_invalident_le_plan(self):
        m = self.preuve(scene(False))
        self.assertIsNone(biens.a_autrui(m, 'porte', 'brune', 'frapper'))
        avant = plans._entrees_communes(plans.Vue(m, 'brune'))
        croire(m, 'brune', 'cle', 'lieu', 'marchand', 'vu', salle=None, case=None)
        connu = plans._entrees_communes(plans.Vue(m, 'brune'))
        self.assertNotEqual(avant, connu)
        croire(m, 'brune', 'cle', 'lieu', 'aubin', 'vu', salle=None, case=None)
        self.assertNotEqual(connu, plans._entrees_communes(plans.Vue(m, 'brune')))
        # Le mouvement réel non appris ne remplace jamais la croyance.
        deplacer(m, 'cle', 'joueur')
        self.assertEqual(biens.responsable_cru(m, 'porte', 'brune'), 'aubin')
        self.preuve(m)

    def test_garde_lue_et_charge_propre_sans_lire_agenda_secret(self):
        m = scene(False)
        p = m.objets['marchand']['profil']
        p['agendas'] = [{'sorte': 'garder', 'parametres': {'lieu': 'beffroi'}}]
        agendas.actualiser(m, 'marchand')
        self.assertIsNone(biens.responsable_cru(m, 'porte', 'brune'))
        self.assertEqual(biens.responsable_cru(m, 'porte', 'marchand'), 'marchand')
        croire(m, 'brune', 'marchand', 'intention', 'garde', 'devine', envers='beffroi', signe='garde-test')
        self.assertEqual(biens.responsable_cru(m, 'porte', 'brune'), 'marchand')
        avant = copy.deepcopy(m.data)
        plans.Vue(m, 'brune')
        self.assertEqual(avant, m.data)
        m = self.preuve(m)
        avant = plans._entrees_communes(plans.Vue(m, 'brune'))
        m.data['minutes'] += 30
        self.assertIsNone(biens.responsable_cru(m, 'porte', 'brune'))
        self.assertNotEqual(avant, plans._entrees_communes(plans.Vue(m, 'brune')))
        self.preuve(m)

    def test_autre_contenant_et_temoins_joueur_et_pnj(self):
        for auteur in ('joueur', 'brune'):
            with self.subTest(auteur=auteur):
                m = scene()
                m.objets['reserve'].pop('proprietaire', None)
                deplacer(m, 'vivres', 'reserve')
                croire(m, 'brune', 'vivres', 'lieu', 'reserve', 'savoir', salle=None, case=None)
                deplacer(m, 'cle_reserve', 'marchand')
                placer(m, 'brune', 'antichambre', (6, 3))
                placer(m, 'marchand', 'antichambre', (5, 3))
                m.joueur.update(salle='antichambre', position=[6, 4])
                m.objets['marchand'].pop('orientation', None)
                percevoir_tous(m)
                for observateur in ('joueur', 'brune', 'marchand'):
                    croire(m, observateur, 'cle_reserve', 'lieu', 'marchand', 'vu', salle=None, case=None)
                    self.assertEqual(biens.responsable_cru(m, 'reserve', observateur), 'marchand')
                m = self.preuve(m)
                plan = plans.planifier(m, 'brune', 'faim')
                self.assertTrue(any(e['operation'] == 'demander' and e['outil'] == 'cle_reserve'
                                    for e in plan[1]), plan)
                self.assertNotIn('frapper', [e['operation'] for e in plan[1]])
                avant = relations.axes(m, 'marchand', auteur)['confiance']
                pnj.commencer_geste(m, auteur, 'frapper', 'reserve', 100)
                souvenirs = [s for s in lire(m, 'marchand')['memoire'] if s['type'] == 'vu_agir']
                self.assertTrue(souvenirs)
                self.assertEqual(souvenirs[-1]['victime'], 'marchand')
                self.assertLess(relations.axes(m, 'marchand', auteur)['confiance'], avant)
                self.preuve(m)

    def test_detresse_et_valeurs_communes(self):
        m = scene()
        # Sans tiers disponible, le seul recours reste de forcer. La faute
        # s'use avec la détresse, et une valeur entière reste inviolable.
        for i, x in enumerate(('marchand', 'ilse', 'aubin')):
            placer(m, x, 'beffroi', (2 + i, 3))
            croire(m, 'brune', x, 'lieu', 'beffroi', 'savoir', salle='beffroi', case=[2 + i, 3])
        for h, douceur, faim, possible in ((100, 80, 100, False), (65, 100, 100, False), (65, 80, 100, True)):
            with self.subTest(h=h, douceur=douceur):
                m.objets['brune']['profil']['valeurs'].update(honnetete=h, douceur=douceur)
                lire(m, 'brune')['besoins']['faim'] = faim
                m = self.preuve(m)
                v = plans.Vue(m, 'brune')
                from donjon.caractere import prix_faute
                v.degat = prix_faute(m, 'brune', 'faim', 'douceur')
                v.desespere = True
                etapes = list(plans.gestes(v, plans.depart(m, 'brune', v), {}))
                coups = [g for g in etapes if g[2][0]['operation'] == 'frapper']
                # L'honnêteté entière exclut la faute dans l'explorateur.
                admissible = bool(coups) and prix_faute(m, 'brune', 'faim') is not None
                self.assertEqual(admissible, possible)
        m, _ = vivre(m, 2, jet=20)
        self.assertLess(m.objets['porte']['integrite'], m.objets['porte']['maximum'])
        self.preuve(m)


if __name__ == '__main__':
    unittest.main()
