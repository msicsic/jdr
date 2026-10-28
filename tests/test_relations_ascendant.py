"""A5/248 : axe orienté, pur, persistant et sans lecteur de décision."""
import copy
import unittest

from donjon import relations as R
from donjon.monde import ErreurMonde
from donjon.esprits import lire, memoriser
from donjon.rendu import regarder
from donjon.recit_pnj import Recit
from tests.test_social import relais, recharger, attendre


class AscendantTests(unittest.TestCase):
    def declarer(self, a, b, valeur):
        m = relais()
        m.objets[a]['profil'].setdefault('liens', {}).setdefault(b, {})['ascendant'] = valeur
        # Réinstalle le profil comme lors de la création d'un monde.
        lire(m, a).pop('relations')
        R.installer(m, a)
        return m

    def test_deux_liens_orientes_declares_et_rendus_apres_recharge(self):
        for a, b in (('brune', 'marchand'), ('ilse', 'aubin')):
            with self.subTest(a=a, b=b):
                m = self.declarer(a, b, 70)
                m.objets[b]['profil'].setdefault('liens', {}).setdefault(a, {})['ascendant'] = 20
                lire(m, b).pop('relations')
                R.installer(m, b)
                contraire = 20
                avant = copy.deepcopy(m.data)
                texte, recit = regarder(m), Recit(m).texte(m, [])
                self.assertEqual(R.autorite_reconnue(m, a, b), 70)
                self.assertEqual(R.autorite_reconnue(m, b, a), contraire)
                r = R.envers(m, a, b)
                self.assertTrue(r['bandes']['ascendant'])
                r['ascendant'] = 0
                self.assertEqual(m.data, avant)
                m = recharger(m)
                self.assertEqual(m.data, avant)
                self.assertEqual(R.autorite_reconnue(m, a, b), 70)
                self.assertEqual(regarder(m), texte)
                self.assertEqual(Recit(m).texte(m, []), recit)
                # Un acte existant conserve l'axe ; ce lot n'ajoute aucune épreuve.
                memoriser(m, a, {'type': 'service_rendu', 'de': b})
                m = recharger(m)
                self.assertEqual(R.autorite_reconnue(m, a, b), 70)
                self.assertIn('service_rendu', Recit(m).texte(m, m.data['chronique']))

    def test_ancienne_sauvegarde_sans_migration_et_meme_action_visible(self):
        for a, b in (('brune', 'marchand'), ('ilse', 'aubin')):
            m = self.declarer(a, b, 0)
            moderne = recharger(m)
            for e in m.data['esprits'].values():
                for r in e['relations'].values():
                    for bloc in (r, r['bandes'], r['ancrages']):
                        bloc.pop('ascendant', None)
            brut = copy.deepcopy(m.data)
            m = recharger(m)
            self.assertEqual(m.data, brut)
            self.assertEqual(R.autorite_reconnue(m, a, b), 0)
            R.signature(m, a)
            R.axes(m, a, b)
            self.assertEqual(m.data, brut)
            self.assertEqual(regarder(m), regarder(moderne))
            m, texte = attendre(m)
            moderne, autre_texte = attendre(moderne)
            self.assertEqual(texte, autre_texte)
            self.assertEqual(m.objets, moderne.objets)
            self.assertEqual(regarder(m), regarder(moderne))
            self.assertEqual(R.autorite_reconnue(m, a, b), 0)

    def test_estompement_hysteresis_et_laps_decoupes_sans_effet_cumule(self):
        m = self.declarer('ilse', 'aubin', 0)
        lire(m, 'ilse')['relations']['aubin'] = R._nouvelle({'ascendant': 60})
        direct = m.copier()
        for minute in range(1, 601):
            m.data['minutes'] = minute
            R.envers(m, 'ilse', 'aubin')
            if minute % 60 == 0:
                m = recharger(m)
        direct.data['minutes'] = 600
        self.assertEqual(R.envers(m, 'ilse', 'aubin'), R.envers(direct, 'ilse', 'aubin'))
        self.assertTrue(R.envers(m, 'ilse', 'aubin')['bandes']['ascendant'])
        m.data['minutes'] = 660
        self.assertFalse(R.envers(m, 'ilse', 'aubin')['bandes']['ascendant'])
        self.assertFalse(R._nouvelle({'ascendant': 59})['bandes']['ascendant'])

    def test_signatures_et_cache_invalide_par_axe_ancre_bande_et_profil(self):
        m = self.declarer('ilse', 'aubin', 60)
        r = lire(m, 'ilse')['relations']['aubin']
        for changer in (lambda: r.update(ascendant=61),
                        lambda: r['ancrages'].update(ascendant=[62, 0]),
                        lambda: r['bandes'].update(ascendant=False)):
            avant = R.signature(m, 'ilse')
            changer()
            self.assertNotEqual(R.signature(m, 'ilse'), avant)
        m.data['minutes'] = 120
        self.assertEqual(R.autorite_reconnue(m, 'ilse', 'aubin'), 60)
        m.objets['ilse']['profil']['liens']['aubin']['ascendant'] = 70
        self.assertEqual(R.autorite_reconnue(m, 'ilse', 'aubin'), 64)

    def test_validation_rejette_valeur_et_contrat_incomplet(self):
        for valeur in (-1, 101, True, 2.5):
            m = self.declarer('ilse', 'aubin', valeur)
            with self.assertRaises(ErreurMonde):
                m.verifier()
        for bloc in ('bandes', 'ancrages'):
            m = self.declarer('ilse', 'aubin', 60)
            lire(m, 'ilse')['relations']['aubin'][bloc].pop('ascendant')
            with self.assertRaises(ErreurMonde):
                m.verifier()

    def test_inconnu_ne_cree_pas_de_relation(self):
        m = relais()
        lire(m, 'ilse')['relations'].pop('aubin', None)
        avant = copy.deepcopy(m.data)
        self.assertEqual(R.autorite_reconnue(m, 'ilse', 'aubin'), 0)
        self.assertEqual(m.data, avant)
