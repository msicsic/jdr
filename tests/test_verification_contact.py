"""Le contact incertain prépare le geste ; seul le constat autorise sa reprise."""
import copy
import unittest
from unittest.mock import patch

from donjon import deliberation as d, memoire, planification as p, pnj
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import instant, MINUTE
from tests.test_proposer_recours import scene
from tests import test_propositions_redites as captures
from tests import test_gardien_detresse as gardien
from tests.test_tensions import placer, recharger


class VerificationContactTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        return n

    def executer_plan(self, m, acteur, plan):
        e = lire(m, acteur)
        e['intention'] = {'but': {'type': 'manger', 'objet': 'vivres'}, 'motif': 'faim',
                          'plan': copy.deepcopy(plan), 'depuis': m.data['minutes'], 'attente': 0}
        for _ in range(150):
            with patch.object(Monde, 'd20', return_value=20):
                duree, issue, manque = pnj.agir(m, acteur, instant(m), [])
            self.assertIsNone(manque)
            if not e['intention']['plan']:
                return self.recharge(m)
            t = instant(m) + max(1, duree)
            m.data['minutes'], m.data['dixiemes'] = divmod(t, MINUTE)
        self.fail('Le préfixe ne termine pas')

    def test_demande_preparee_constat_et_reprise_ou_recours_deux_contacts(self):
        from tests.support import lier
        for autre in ('marchand', 'aubin'):
            for present in (True, False):
                with self.subTest(autre=autre, present=present):
                    m = scene(70, autre)
                    m.data['minutes'] += 121
                    if not present:
                        placer(m, autre, 'crypte', (2, 2))
                        lier(m, autre, 'brune', False, 'vu')
                    m = self.recharge(m)
                    demande = p._etape('demander', autre, outil='cle_reserve')
                    plan = p.preparer_contact(m, 'brune', autre, [demande])
                    self.assertTrue(plan)
                    self.assertEqual(plan[-1]['operation'], 'inspecter')
                    self.assertIn(demande, list(p.gestes_conditionnes(plan)))
                    self.assertEqual(m.objets['cle_reserve']['lieu'], autre)
                    m = self.executer_plan(m, 'brune', plan)
                    suivant = p.preparer_contact(m, 'brune', autre, [demande])
                    if present:
                        self.assertFalse(memoire.position_a_verifier(m, 'brune', autre))
                        self.assertEqual(suivant[-1], demande)
                        m = self.executer_plan(m, 'brune', suivant)
                        self.assertEqual(m.objets['cle_reserve']['lieu'], 'brune')
                        self.assertTrue(any('demande' in c['texte'] and c['pnj'] == 'brune'
                                            for c in m.data['chronique']))
                    else:
                        self.assertTrue(memoire.hypothese_consommee(m, 'brune', autre))
                        self.assertIsNone(suivant)
                        m.data['minutes'] += 180
                        self.assertIsNone(p.preparer_contact(self.recharge(m), 'brune', autre, [demande]))
                        self.assertEqual(m.objets['cle_reserve']['lieu'], autre)

    def test_capture_mine_appel_eprouve_le_repere_sans_perdre_le_geste(self):
        m = captures.PropositionsReditesTests().capture('redites-mine7-240.json.gz')
        self.assertTrue(memoire.position_a_verifier(m, 'remy', 'bram'))
        self.assertIsNone(d.salle_crue(m, 'remy', 'bram'))
        demande = p._etape('demander', 'bram', outil='cle_paie')
        plan = p.preparer_contact(self.recharge(m), 'remy', 'bram', [demande])
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]['operation'], 'inspecter')
        self.assertEqual(plan[0]['lieu'], 'baraquement')
        self.assertEqual(plan[0]['contenu']['cherche'], 'bram')
        self.assertIn(demande, list(p.gestes_conditionnes(plan)))
        m = self.executer_plan(m, 'remy', plan)
        self.assertTrue(any(c['pnj'] == 'remy' and 'Bram ?' in c['texte'] for c in m.data['chronique']))
        self.assertEqual(m.objets['cle_paie']['lieu'], 'bram')

    def test_le_recours_lit_aussi_le_moyen_conditionnel(self):
        from donjon.pnj_propositions import plan_recours
        m = scene(10)
        faute = p._etape('manger', 'vivres', condition='sans_temoin')
        prefixe = p._preparer_suite((0, 0, [p._etape('inspecter', lieu='antichambre')]), [faute])[2]
        direct = plan_recours(self.recharge(m), 'brune', 'faim', [faute])
        prepare = plan_recours(self.recharge(m), 'brune', 'faim', prefixe)
        self.assertEqual(prepare, direct)
        self.assertEqual(prepare[-1]['operation'], 'proposer')
        self.assertEqual(m.objets['vivres']['proprietaire'], 'marchand')

    def test_la_provenance_n_entre_pas_dans_les_termes_de_l_aide(self):
        from donjon import echanges
        m = gardien.GardienDetresseTests().lumiere()
        condition = {'objet': 'chandelle', 'allume': True}
        geste = p._etape('confier', 'josse', contenu={**condition,
                         'suite_conditionnelle': [p._etape('abriter', lieu='bureau')]})
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(echanges.executer(m, 'bram', geste, []))
        m = self.recharge(m)
        self.assertEqual(lire(m, 'bram')['aides_attendues']['chandelle']['condition'], condition)
        self.assertFalse(m.objets['chandelle']['allume'])


if __name__ == '__main__':
    unittest.main()
