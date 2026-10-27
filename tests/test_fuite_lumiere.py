"""Les recours de sécurité partagent le danger cru de la fuite, après recharge."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import defense, planification
from donjon.banc_pnj import executer
from donjon.esprits import croire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import MINUTE
from tests.test_defense import epreuve
from tests.test_tensions import recharger
from tests.test_corps_blessable import passer


class FuiteLumiereTests(unittest.TestCase):
    @patch('donjon.social._constats', return_value=())
    def test_autre_scene_violence_bloc_decoupe_et_rendu(self, _):
        a = recharger(epreuve('ilse'))
        b = recharger(a)
        passer(a, 5 * MINUTE)
        for _ in range(20):
            passer(b, MINUTE // 4)
            b = recharger(b)
        a = recharger(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertNotIn(a.objets['ilse']['lieu'], defense.lieux_dangereux(a, 'ilse'))
        self.assertNotIn(a.objets['ilse']['nom'], regarder(a))

    def test_capture_reelle_bloc_et_decoupes_recharges(self):
        with gzip.open(Path(__file__).parent / 'data/crue-2024-680.json.gz', 'rt', encoding='utf-8') as f:
            a = recharger(Monde(json.load(f)))
        b = recharger(a)
        chronique, _ = executer(recharger(a), 720)
        passer(a, 40 * MINUTE)
        for _ in range(40):
            passer(b, MINUTE)
            b = recharger(b)
        a = recharger(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        passages = [c for c in chronique if c['pnj'] == 'brune' and 'passe dans' in c['texte']]
        self.assertEqual(len(passages), 8)
        self.assertFalse(any(c['minute'] >= 689 for c in passages))
        self.assertEqual(a.objets['brune']['lieu'], 'antichambre')
        self.assertNotIn(a.objets['brune']['nom'], regarder(a))

    @patch('donjon.social._constats', return_value=())
    def test_autres_victimes_lieu_cru_fin_et_cle_memoire(self, _):
        for cible in ('aubin', 'ilse'):
            m = recharger(epreuve(cible))
            # La menace reste connue après le départ de la victime, sans lire
            # la position réelle de l'auteur distant.
            croire(m, cible, 'brune', 'lieu', 'echoppe', 'vu', salle='echoppe', case=None)
            croire(m, cible, 'echoppe', 'etat', {'eclairee': True, 'niveau': 2, 'propre': 2}, 'vu')
            croire(m, cible, 'antichambre', 'etat', {'eclairee': False, 'niveau': 0, 'propre': 0}, 'vu')
            m = recharger(m)
            self.assertEqual(defense.lieux_dangereux(m, cible), {'echoppe'})
            self.assertFalse(defense.dangers(m, cible))
            v = planification.vue(m, cible)
            e = planification.depart(m, cible, v).apres(salle='echoppe')
            cle = planification._entrees(v, {}, 4, 100)
            self.assertTrue(v.dangereuse(e))
            self.assertFalse(planification.eclaire(v, e))
            self.assertIsNone(planification.abri(m, cible, ['echoppe']))
            pression = v.pression(e)
            for fin in ('parti', 'neutralise', 'expire'):
                n = recharger(m)
                if fin == 'parti':
                    croire(n, cible, 'brune', 'lieu', 'antichambre', 'vu', salle='antichambre', case=None)
                elif fin == 'neutralise':
                    croire(n, cible, 'brune', 'etat', {'conscient': False}, 'vu')
                else:
                    n.data['minutes'] += defense.RECENT
                n = recharger(n)
                w = planification.vue(n, cible)
                self.assertFalse(w.dangereuse(e))
                self.assertNotEqual(cle, planification._entrees(w, {}, 4, 100))
                if fin != 'parti':
                    self.assertLess(w.pression(e), pression)
                self.assertTrue(planification.eclaire(w, e))
                self.assertIsNotNone(planification.abri(n, cible, ['echoppe']))
                self.assertEqual(regarder(n), regarder(recharger(n)))


if __name__ == '__main__':
    unittest.main()

