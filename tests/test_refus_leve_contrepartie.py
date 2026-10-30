"""366 : la revalidation distingue le refus de la condition qui le lève."""
import copy
import unittest
from unittest.mock import patch

from donjon import pnj
from donjon.ecoute import ECOUTE, entendus, rendre
from donjon.echanges import executer, servir
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import plan_recours
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_contre_offre import demande, faim, refus
from tests.test_proposer_recours import scene
from tests.test_temps_etat import etat_pnj
from tests.test_tensions import recharger


class RefusLeveTests(unittest.TestCase):
    def public(self, m):
        return regarder(m), scene_percue(m), rendre(m, entendus(m, 0, ECOUTE))

    def persiste(self, m):
        public = self.public(m)
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(self.public(n), public)
        return n

    def test_prix_annonce_libere_achat_pas_demande_gratuite(self):
        for objet in ('vivres', 'cle_reserve'):
            with self.subTest(objet=objet):
                m = scene(70)
                m.data['finances_pnj']['brune'] = 100
                m, _ = refus(m, objet)
                etape = plan_recours(m, 'brune', 'faim', None)[-1]
                prix = etape['contenu']['prix']
                avant = copy.deepcopy(m.data)
                self.assertIsNone(pnj.refus_etape(m, 'brune', [etape]))
                self.assertEqual(m.data, avant, 'le contrôle ne paie ni ne perçoit')
                self.assertIsNotNone(pnj.refus_etape(m, 'brune', [demande(objet)]))
                self.assertEqual(m.data, avant)
                finances = copy.deepcopy(m.data['finances_pnj'])
                lignes = []
                with patch('donjon.echanges.jet_persuasion', side_effect=AssertionError('second jet')):
                    self.assertTrue(executer(m, 'brune', etape, lignes))
                m = self.persiste(m)
                self.assertEqual(m.data['finances_pnj']['brune'], finances['brune'] - prix)
                self.assertEqual(m.data['finances_pnj']['marchand'], finances['marchand'] + prix)
                self.assertIn("prend l'argent", ' '.join(lignes))
                self.assertFalse(any(s.get('objet') == objet for s in lire(m, 'brune')['refus']))

    def test_service_accompli_seul_le_beneficiaire_et_le_bien_convenus(self):
        m, _ = refus(faim(), 'cle_reserve')
        etape = demande('cle_reserve')
        avant = copy.deepcopy(m.data)
        self.assertIsNotNone(pnj.refus_etape(m, 'brune', [etape]))
        self.assertEqual(m.data, avant)
        # Le monde physique seul ne vaut pas prestation entendue/accomplie.
        lire(m, 'marchand')['besoins']['faim'] = 0
        m = self.persiste(m)
        self.assertIsNotNone(pnj.refus_etape(m, 'brune', [etape]))
        self.assertTrue(servir(m, 'brune', 'repas', 'marchand', []))
        m = self.persiste(m)
        avant = copy.deepcopy(m.data)
        self.assertIsNone(pnj.refus_etape(m, 'brune', [etape]))
        self.assertEqual(m.data, avant)
        # Une enquête au même interlocuteur conserve son refus propre.
        from donjon.deliberation import retenir_refus, refus_geste
        retenir_refus(m, 'brune', 'marchand', 'enqueter', 'rien', besoin='faim')
        enquete = {**etape, 'contenu': {'ressource': 'faim'}}
        self.assertTrue(refus_geste(self.persiste(m), 'brune', enquete))

    @patch('donjon.agendas._naissances', return_value=None)
    def test_autre_bien_service_pret_et_rendu_apres_laps_decoupe(self, _naissances):
        m = faim()
        cle = copy.deepcopy(m.objets['cle_reserve'])
        cle.update(id='cle_rechange', nom='clé de rechange')
        m.objets['cle_rechange'] = cle
        lire(m, 'marchand')['intention']['plan'][0]['outil'] = 'cle_rechange'
        m.objets['brune']['profil']['besoins']['devoir'] = {
            'depart': 80, 'derive_heure': 0, 'urgence': 60}
        lire(m, 'brune')['besoins'].update(faim=0, devoir=80)
        lire(m, 'brune')['intention']['motif'] = 'devoir'
        m.objets['reserve'].update(proprietaire='brune', ouverte=True, verrouillee=False)
        m.objets['brune']['profil']['pulsions'] = [
            {'besoin': 'devoir', 'condition': {'objet': 'reserve', 'verrouillee': True}}]
        lire(m, 'brune')['pulsions'] = [False]
        m, _ = refus(m, 'cle_rechange')
        a, b = self.persiste(m), self.persiste(m.copier())
        with patch.object(Monde, 'd20', return_value=20):
            moteur = Moteur(a)
            moteur.executer(moteur.preparer(proposition('attendre', cible='300')))
            for _ in range(5):
                moteur = Moteur(b)
                moteur.executer(moteur.preparer(proposition('attendre', cible='60')))
                b = self.persiste(b)
        a = self.persiste(a)
        self.assertEqual(etat_pnj(a), etat_pnj(b))
        self.assertEqual(self.public(a), self.public(b))
        self.assertEqual(a.data['finances_pnj'], b.data['finances_pnj'])
        self.assertEqual(a.data['permissions'], b.data['permissions'])
        self.assertTrue(any(s['type'] == 'pret' and s.get('objet') == 'cle_rechange'
                            for s in lire(a, 'marchand')['memoire']))
        self.assertTrue(a.objets['reserve']['verrouillee'])
        texte = ' '.join(f for j in a.data['journal'] for f in j['faits'])
        self.assertIn('donne une part', texte)
        self.assertIn('clé de rechange', texte)
        self.assertIn('lui remet', texte)


if __name__ == '__main__':
    unittest.main()
