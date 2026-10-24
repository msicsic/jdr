"""Détresse perçue, sécurité vécue, rendu et sauvegarde sur les circuits communs."""
import unittest
from unittest.mock import patch

from donjon import deliberation, signes, vecu
from donjon.banc_pnj import creer
from donjon.esprits import lire, percevoir_tous
from donjon.ouie import retentir
from donjon.pnj import _etape
from donjon.rendu import regarder
from donjon.temps import MINUTE, instant
from donjon.voix import connaitre
from tests.support import calme, presentes, regarder as orienter
from tests.test_corps_blessable import passer
from tests.test_defense import epreuve
from tests.test_tensions import placer, recharger


def rester(m):
    # Placement d'auteur : isoler le temps vécu de la réaction autonome à mesurer ailleurs.
    for x in m.data['esprits']:
        e = lire(m, x)
        e.update(libre=instant(m) + 10 * MINUTE, eveil=None, intention=None)
        vecu.noter(m, x, instant(m), None)
    return m


def auberge():
    m = presentes(creer('auberge', 1985, 'fixe'))
    ids = [x for x, o in m.objets.items() if o['type'] == 'personnage']
    calme(m, *ids)
    for numero, x in enumerate(ids):
        if x not in ('lucien', 'hugues'):
            placer(m, x, 'etable', (numero, 3))
    placer(m, 'lucien', 'salle_commune', (3, 5))
    placer(m, 'hugues', 'salle_commune', (4, 5))
    m.joueur.update(salle='salle_commune', position=[2, 5], orientation='est')
    orienter(m, 'lucien', 'hugues')
    lire(m, 'lucien')['relations'].clear()
    from donjon import relations
    lire(m, 'lucien')['relations']['hugues'] = relations._nouvelle(
        {'confiance': 70, 'affection': 15}, m.data['minutes'])
    lire(m, 'lucien')['besoins']['securite'] = 30.
    connaitre(m, 'lucien', 'hugues')
    percevoir_tous(m)
    return m


class PeurTransmiseTests(unittest.TestCase):
    def comparer_laps(self, m, qui, duree=2 * MINUTE):
        a, b = recharger(m), recharger(m)
        passer(a, duree)
        for dt in (13, 587, duree - MINUTE):
            if dt:
                passer(b, dt)
                b = recharger(b)
        a = recharger(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        return a

    def test_epreuve_aubin_tremble_ilse_ne_s_apaise_plus_aupres_de_lui(self):
        m = rester(epreuve())
        a = deliberation.autour(m, 'ilse')
        self.assertNotIn('aubin', a['fiables'])
        self.assertAlmostEqual(a['detresse'], .85)
        self.assertLess(a['compagnie'], .85)
        avant = lire(m, 'ilse')['besoins']['securite']
        m = self.comparer_laps(m, 'ilse')
        self.assertGreater(lire(m, 'ilse')['besoins']['securite'], avant)
        self.assertIn('Aubin tremble et se recroqueville.', regarder(m))

    def test_appel_reconnu_visible_ou_entendu_a_l_auberge(self):
        for visible in (True, False):
            with self.subTest(visible=visible):
                m = auberge()
                if not visible:
                    # Hors du cône et trop loin pour le retournement réflexe.
                    placer(m, 'hugues', 'salle_commune', (7, 5))
                    m.objets['lucien']['orientation'] = 'ouest'
                    m.joueur['orientation'] = 'ouest'
                retentir(m, 'hugues', 'appel')
                self.assertIsNotNone(lire(m, 'lucien')['eveil'])
                m = rester(m)
                self.assertAlmostEqual(deliberation.autour(m, 'lucien')['detresse'], .85)
                self.assertNotIn('hugues', deliberation.autour(m, 'lucien')['fiables'])
                avant = lire(m, 'lucien')['besoins']['securite']
                m = self.comparer_laps(m, 'lucien', MINUTE)
                self.assertGreater(lire(m, 'lucien')['besoins']['securite'], avant)
                # Un appel ponctuel ne devient pas une émotion privée durable.
                self.assertEqual(deliberation.autour(m, 'lucien')['detresse'], 0)
                self.assertIn('SALLE COMMUNE', regarder(m).upper())
                if not visible:
                    self.assertTrue(any(b['nature'] == 'appel' for b in m.data['bruits']))
                    from donjon import ecoute
                    entendu = ecoute.rendre(m, ecoute.entendus(m, -1, ecoute.ENTENDU))
                    self.assertIn("appel à l'aide", ' '.join(entendu))

    def test_calme_et_signe_non_percu_gardent_la_compagnie(self):
        for condition in ('calme', 'dos', 'noir'):
            with self.subTest(condition=condition):
                m = auberge()
                if condition != 'calme':
                    lire(m, 'hugues')['besoins']['securite'] = 90.
                if condition == 'dos':
                    m.objets['lucien']['orientation'] = 'ouest'
                elif condition == 'noir':
                    for o in m.objets.values():
                        if o.get('allume'):
                            o['allume'] = False
                m = rester(m)
                a = deliberation.autour(m, 'lucien')
                self.assertEqual(a['detresse'], 0)
                self.assertAlmostEqual(a['compagnie'], .85)
                avant = lire(m, 'lucien')['besoins']['securite']
                ecart = deliberation.ecart_securite(m, 'lucien')
                m = self.comparer_laps(m, 'lucien', MINUTE)
                self.assertAlmostEqual(lire(m, 'lucien')['besoins']['securite'], avant + ecart, places=3)
                if condition == 'calme':
                    self.assertLess(lire(m, 'lucien')['besoins']['securite'], avant)
                self.assertFalse(any(s['signe'] == 'tremble' for s in signes.publics(m, 'lucien')))

    def test_fuite_visible_sans_lire_le_besoin_prive_et_sans_fuite_de_cible(self):
        m = auberge()
        rester(m)
        e = lire(m, 'hugues')
        e['intention'] = {'but': {'type': 'fuir', 'qui': 'odile'}, 'motif': 'securite',
                          'plan': [_etape('aller', lieu='cuisine'), _etape('fuite')],
                          'depuis': m.data['minutes'], 'attente': 0}
        # Le projet privé n'est pas un signe. Un vrai pas de fuite le devient.
        self.assertEqual(deliberation.autour(m, 'lucien')['detresse'], 0)
        from donjon.pnj import _avancer_de
        _avancer_de(m, 'hugues', [('salle_commune', (5, 5), None, (1, 0))], False, [])
        m = recharger(m)
        self.assertEqual(e['besoins']['securite'], 0)
        a = deliberation.autour(m, 'lucien')
        self.assertAlmostEqual(a['detresse'], .85)
        self.assertAlmostEqual(a['compagnie'], .4)  # Le joueur calme continue de rassurer.
        self.assertIn("Hugues s'éloigne en fuyant.", regarder(m))
        self.assertNotIn('odile', str(signes.publics(m, 'lucien')))
        avant = lire(m, 'lucien')['besoins']['securite']
        vecu.noter(m, 'lucien', instant(m), None)
        m = self.comparer_laps(m, 'lucien', MINUTE)
        self.assertGreater(lire(m, 'lucien')['besoins']['securite'], avant)
        m.objets['lucien']['orientation'] = 'ouest'
        self.assertEqual(deliberation.autour(m, 'lucien')['detresse'], 0)

    def test_le_lien_pondere_la_detresse_percue(self):
        m = auberge()
        lire(m, 'hugues')['besoins']['securite'] = 90.
        m = recharger(m)
        fort = deliberation.ecart_securite(m, 'lucien')
        self.assertGreater(fort, 0)
        from donjon import relations
        lire(m, 'lucien')['relations']['hugues'] = relations._nouvelle(
            {'confiance': 60, 'affection': 0}, m.data['minutes'])
        faible = deliberation.ecart_securite(m, 'lucien')
        self.assertLess(faible, fort)
        self.assertAlmostEqual(deliberation.autour(m, 'lucien')['detresse'], .6)

    def test_une_impression_faillible_exige_encore_le_signe_percu(self):
        m = auberge()
        lire(m, 'hugues')['emotions']['colere'] = {
            'contre': 'lucien', 'niveau': 30, 'depuis': m.data['minutes']}
        with patch('donjon.signes._jet', return_value=1):
            signes.lire(m, 'lucien')
        m = recharger(m)
        self.assertTrue(any(c['valeur'] == 'peur' for _, _, c in signes.actives(m, 'lucien')))
        self.assertAlmostEqual(deliberation.autour(m, 'lucien')['detresse'], .85)
        m.objets['lucien']['orientation'] = 'ouest'
        m = recharger(m)
        self.assertTrue(signes.actives(m, 'lucien'))
        self.assertEqual(deliberation.autour(m, 'lucien')['detresse'], 0)

    def test_un_appel_anonyme_ne_revele_pas_la_detresse_d_un_allie(self):
        m = auberge()
        placer(m, 'hugues', 'salle_commune', (7, 5))
        m.objets['lucien']['orientation'] = 'ouest'
        lire(m, 'lucien')['voix'].remove('hugues')
        retentir(m, 'hugues', 'appel')
        m = recharger(m)
        self.assertFalse(any(s['type'] == 'detresse' for s in lire(m, 'lucien')['memoire']))
        self.assertEqual(deliberation.autour(m, 'lucien')['detresse'], 0)
        # Voir qui appelle suffit à l'attribution, même sans connaître sa voix.
        m.objets['lucien']['orientation'] = 'est'
        retentir(m, 'hugues', 'appel')
        m = recharger(m)
        self.assertAlmostEqual(deliberation.autour(m, 'lucien')['detresse'], .85)


if __name__ == '__main__':
    unittest.main()
