"""377 : les paroles actives réservent les mêmes moyens dans toutes les voies."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, echanges
from donjon.biens import bourse
from donjon.esprits import percevoir_tous
from donjon.monde import Monde
from donjon.pnj import avancer
from donjon.rendu import regarder as rendu
from donjon.temps import ecouler
from tests.test_propositions import scene
from tests.test_parts_achetees import parole
from tests.support import regarder
from tests.test_tensions import placer, recharger


def capture():
    p = Path(__file__).parent / 'captures/double-promesse-377.json.gz'
    return Monde(json.loads(gzip.decompress(p.read_bytes())))


class DoublePromesseTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(rendu(m), rendu(r))
        self.assertEqual(agendas.promesses_visibles(m), agendas.promesses_visibles(r))
        return r

    def avance(self, m, pas):
        lignes = []
        for dt in pas:
            ecouler(m, dt)
            avancer(m, 0, lignes, dixiemes=dt)
            m = self.recharge(m)
        return m, lignes

    def test_capture_mireille_ne_vend_pas_la_part_promise_a_tilo(self):
        m = self.recharge(capture())
        promesse = agendas.en_cours(m, 'mireille')
        avant = (bourse(m, 'mireille'), bourse(m, 'mathurine'))
        self.assertEqual(echanges.demander(m, 'mathurine', 'mireille', 'marmite_2', prix=1), 'impossible')
        self.assertEqual(agendas.en_cours(m, 'mireille'), promesse)
        self.assertEqual((bourse(m, 'mireille'), bourse(m, 'mathurine')), avant)
        m = self.recharge(m)
        a, _ = self.avance(self.recharge(m), [600])
        b, _ = self.avance(self.recharge(m), [20, 80, 200, 300])
        for r in (a, b):
            self.assertEqual(r.objets['marmite_2']['proprietaire'], 'tilo')
            self.assertFalse(agendas.en_cours(r, 'mireille'))
            self.assertFalse([d for d in r.data.get('dettes', []) if d['de'] == 'mireille'])
            self.assertEqual((bourse(r, 'mireille'), bourse(r, 'mathurine')), avant)
        self.assertEqual(rendu(a), rendu(b))

    def test_autre_bien_promis_refuse_dans_les_deux_voies_et_reste_livrable(self):
        m = scene('aubin')
        # Un objet indivisible, déjà promis à Brune, reste physiquement en main.
        m.objets['cloche'].update(lieu='aubin', proprietaire='aubin')
        placer(m, 'brune', 'antichambre', [2, 4])
        regarder(m, 'aubin', 'brune')
        regarder(m, 'brune', 'aubin')
        percevoir_tous(m)
        c = {'objet': 'cloche', 'remettre': 'brune'}
        agendas.prendre(m, 'aubin', {'condition': c, 'pour': 'brune', 'minute': 0})
        m = self.recharge(m)
        avant = m.joueur['or']
        self.assertEqual(echanges.demander(m, 'joueur', 'aubin', 'cloche', prix=20), 'impossible')
        bilan = echanges.proposer(m, 'joueur', 'aubin', {'type': 'objet', 'objet': 'cloche'},
                                 {'type': 'pieces', 'montant': 20})
        self.assertEqual(bilan['cause'], 'impossible')
        self.assertEqual(m.joueur['or'], avant)
        self.assertEqual(len(agendas.en_cours(m, 'aubin')), 1)
        from donjon.paroles import preparer_parole
        refus, rapport = preparer_parole(m, parole(
            'aubin', "Je t'achète cette cloche, vingt pièces.", 'demande', 'cloche', '20'))
        self.assertIn("Aubin, vieux passeur ne voit pas comment te donner la cloche d'alarme.", rapport['faits'])
        self.assertEqual(self.recharge(refus).joueur['or'], avant)
        for pas in ([600], [100, 200, 300]):
            r, _ = self.avance(self.recharge(m), pas)
            self.assertEqual(r.objets['cloche']['lieu'], 'brune')
            self.assertFalse(agendas.en_cours(r, 'aubin'))
            self.assertEqual(r.joueur['or'], avant)

    def test_service_reserve_une_part_et_non_tout_le_lot(self):
        for n, possible in ((1, False), (2, True), (4, True)):
            with self.subTest(n=n):
                m = scene('aubin')
                m.objets['vivres']['portions'] = n
                c = {'objet': 'vivres', 'servir': 'brune'}
                agendas.prendre(m, 'aubin', {'condition': c, 'pour': 'brune', 'minute': 0})
                m = self.recharge(m)
                avant = copy.deepcopy(m.data)
                self.assertEqual(agendas.disponibilite_promise(m, 'aubin', 'vivres', part=True), possible)
                self.assertFalse(agendas.disponibilite_promise(m, 'aubin', 'vivres'))
                self.assertEqual(m.data, avant)
                # Le devis de la parole existante ne se réserve pas contre lui-même.
                self.assertIsNotNone(echanges.devis_service(m, 'aubin', c, 'brune'))
                with patch.object(Monde, 'd20', return_value=20):
                    r = echanges.proposer(m, 'joueur', 'aubin', {'type': 'part', 'objet': 'vivres'},
                                         {'type': 'pieces', 'montant': 3})
                self.assertEqual(r['cause'], None if possible else 'impossible')
                m = self.recharge(m)
                self.assertEqual(m.objets['vivres']['portions'], n - int(possible))
                self.assertEqual(agendas.en_cours(m, 'aubin')[0]['condition'], c)

    def test_services_et_remises_partagent_la_reservation(self):
        m = capture()
        c = {'objet': 'marmite_2', 'servir': 'mathurine'}
        avant = copy.deepcopy(m.data)
        self.assertIsNone(echanges._devis_proposition(m, 'mireille', c, 'mathurine'))
        self.assertEqual(m.data, avant)
        self.assertEqual(echanges.engager(m, 'mathurine', 'mireille', c, 1), 'impossible')
        self.assertEqual(echanges.confier(m, 'mathurine', 'mireille', c), 'impossible')
        self.assertEqual(len(agendas.en_cours(self.recharge(m), 'mireille')), 1)

    def test_annulation_libere_le_bien_et_repetition_ne_le_facture_pas(self):
        m = capture()
        x, = agendas.en_cours(m, 'mireille')
        avant = copy.deepcopy(m.data)
        self.assertEqual(echanges._remettre_part(m, 'mireille', 'tilo', 'marmite', 1), 'promis')
        self.assertEqual(m.data, avant)
        agendas.annoncer_abandon(m, 'mireille', x)
        m = self.recharge(m)
        self.assertTrue(agendas.disponibilite_promise(m, 'mireille', 'marmite_2', part=True))

    def test_stock_distant_cache_ne_change_pas_le_devis(self):
        m = capture()
        # Le lieu et la quantité vrais, hors perception, ne donnent aucun moyen neuf.
        m.objets['marmite_2']['lieu'] = 'cellier'
        a = echanges._devis_proposition(m, 'mireille', {'objet': 'marmite_2', 'servir': 'mathurine'}, 'mathurine')
        m.objets['marmite_2']['portions'] = 50
        b = echanges._devis_proposition(m, 'mireille', {'objet': 'marmite_2', 'servir': 'mathurine'}, 'mathurine')
        self.assertIsNone(a)
        self.assertIsNone(b)

    def test_un_service_reserve_aussi_son_combustible_sans_metadonnee_de_part(self):
        from tests.test_tache_promise_recours import feu
        m, qui, pour, c = feu()
        m.objets['bois']['charges'] = 1
        agendas.prendre(m, qui, {'condition': c, 'pour': pour, 'minute': m.data['minutes']})
        m = self.recharge(m)
        charges, entiers = agendas.moyens_promis(m, qui)
        self.assertEqual(charges['bois'], 1)
        self.assertNotIn('bois', entiers)
        self.assertFalse(agendas.disponibilite_promise(m, qui, 'bois', part=True))
        self.assertIsNotNone(echanges.devis_service(m, qui, c, pour))
        m.objets['bois']['charges'] = 2
        self.assertTrue(agendas.disponibilite_promise(self.recharge(m), qui, 'bois', part=True))
