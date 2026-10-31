"""Capacités compensées : captures du hameau, vente et remplacement après recharge."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import echanges
from donjon.biens import capacites_crues, valeur_capacites
from donjon.caractere import valeur_pieces
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_ceder_outil as ceder
from tests.test_tensions import recharger


class CompensationTests(unittest.TestCase):
    def stable(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def hameau(self, objet):
        p = Path(__file__).parent / f'data/compensation-228-hameau-{objet}.json.gz'
        return recharger(Monde(json.loads(gzip.decompress(p.read_bytes()))))

    def test_hameau_cle_et_torche_refus_sous_compense_puis_vente(self):
        for objet in ('cle', 'torche'):
            with self.subTest(objet=objet):
                m = self.hameau(objet)
                m.data['finances_pnj']['aubin'] = 100
                avant = copy.deepcopy(m.objets[objet])
                finances = copy.deepcopy(m.data['finances_pnj'])
                self.assertGreater(valeur_capacites(m, 'brune', objet), valeur_pieces(m, 'brune', 1))
                self.assertEqual(echanges.demander(m, 'aubin', 'brune', objet, prix=1), 'necessaire')
                self.assertEqual(m.objets[objet], avant)
                self.assertEqual(m.data['finances_pnj'], finances)
                offre = echanges.contre_offre(m, 'aubin', 'brune', objet, 'necessaire')
                self.assertIsNotNone(offre)
                prix = offre['condition']['montant']
                self.assertGreaterEqual(valeur_pieces(m, 'brune', prix), valeur_capacites(m, 'brune', objet))
                m = self.stable(m)
                with patch.object(Monde, 'd20', return_value=20):
                    self.assertEqual(echanges.demander(m, 'aubin', 'brune', objet, prix=prix), 'vendu')
                m = self.stable(m)
                self.assertEqual(m.objets[objet]['lieu'], 'aubin')
                self.assertEqual(m.objets[objet]['proprietaire'], 'aubin')
                self.assertEqual(m.data['finances_pnj']['aubin'], finances['aubin'] - prix)
                self.assertEqual(m.data['finances_pnj']['brune'], finances['brune'] + prix)

    def active(self):
        m = ceder.CederOutilTests().scene()
        croire(m, 'anselme', 'crochets_lucien', 'lieu', 'lucien', 'savoir',
               salle='salle_commune', case=list(m.objets['lucien']['position']))
        lire(m, 'lucien')['intention'] = dict(but={'type': 'argent', 'objet': 'coffret_lucien'},
            motif='argent', depuis=m.data['minutes'], attente=0, plan=[
                dict(operation='aller', cible='grenier', outil='', lieu='', condition=''),
                dict(operation='crocheter', cible='coffret_lucien', outil='crochets_lucien', lieu='', condition='')])
        return self.stable(m)

    def test_remplacement_acquis_compense_meme_un_outil_du_plan(self):
        m = self.active()
        m.objets['crochets_rechange'] = {**copy.deepcopy(m.objets['crochets_lucien']),
            'id': 'crochets_rechange', 'lieu': 'anselme', 'proprietaire': 'anselme'}
        for qui, objet, porteur in (('lucien', 'crochets_rechange', 'anselme'),
                                    ('anselme', 'crochets_lucien', 'lucien')):
            croire(m, qui, objet, 'lieu', porteur, 'savoir', salle='salle_commune',
                   case=list(m.objets[porteur]['position']))
        m = self.stable(m)
        with patch.object(Monde, 'd20', return_value=20):
            bilan = echanges.proposer(m, 'anselme', 'lucien',
                {'type': 'objet', 'objet': 'crochets_lucien'},
                {'type': 'objet', 'objet': 'crochets_rechange'})
        self.assertTrue(bilan.get('accepte'), bilan)
        m = self.stable(m)
        self.assertEqual(m.objets['crochets_rechange']['lieu'], 'lucien')
        self.assertEqual(m.objets['crochets_lucien']['lieu'], 'anselme')
        self.assertIn('crochetage', capacites_crues(m, 'lucien', 'crochets_rechange'))

    def test_valeur_suffisante_compense_outil_du_plan(self):
        m = self.active()
        m.data['finances_pnj']['anselme'] = 100
        offre = echanges.contre_offre(m, 'anselme', 'lucien', 'crochets_lucien', 'necessaire')
        self.assertIsNotNone(offre)
        prix = offre['condition']['montant']
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.demander(m, 'anselme', 'lucien', 'crochets_lucien', prix=prix), 'vendu')
        self.assertEqual(self.stable(m).objets['crochets_lucien']['proprietaire'], 'anselme')

    def test_prix_eleve_ne_masque_pas_un_don_de_capacite_sans_compensation(self):
        m = self.active()
        m.objets['crochets_lucien']['prix'] = 100
        bilan = echanges.proposer(m, 'anselme', 'lucien',
            {'type': 'objet', 'objet': 'crochets_lucien'}, {'type': 'rien'})
        self.assertEqual(bilan['cause'], 'necessaire')
        self.assertEqual(self.stable(m).objets['crochets_lucien']['proprietaire'], 'lucien')

    def test_prix_annonce_et_honore_sans_second_jet(self):
        from tests.test_garde_pret import DemandeTests
        m, acheteur, donneurs = DemandeTests().scene('relais')
        vendeur, objet = donneurs[0], 'source_0'
        m.data['finances_pnj'][acheteur] = 100
        def achat(prix):
            return dict(operation='acheter', cible=vendeur, outil=objet, lieu='', condition='', contenu={'prix': prix})
        lignes = []
        self.assertFalse(echanges.executer(m, acheteur, achat(1), lignes))
        refus = lire(m, acheteur)['refus'][-1]
        prix = refus['contre_offre']['condition']['montant']
        self.assertGreater(prix, 1)
        self.assertIn('Offre de', ' '.join(lignes))
        m = self.stable(m)
        lignes = []
        with patch('donjon.echanges.jet_persuasion', side_effect=AssertionError('second jet')):
            self.assertTrue(echanges.executer(m, acheteur, achat(prix), lignes))
        self.assertEqual(self.stable(m).objets[objet]['proprietaire'], acheteur)
        self.assertIn("prend l'argent", ' '.join(lignes))

    def test_negatif_du_contrat_precedent_est_rejuge_apres_recharge(self):
        from donjon import memoire, pnj_propositions as propositions
        data = Path(__file__).parent / 'data'
        m = self.stable(Monde(json.loads(gzip.decompress((data / 'recours-228-odon.json.gz').read_bytes()))))
        lire(m, 'odon')['attentes_bornees'].update(json.loads((data / 'compensation-228-cache-v1.json').read_text(encoding='utf8')))
        with patch.object(propositions, '_contreparties', wraps=propositions._contreparties) as calcul:
            for _ in range(2):
                m = self.stable(m)
                intention = lire(m, 'odon')['intention']
                with memoire.choix_complet(m, 'odon'):
                    self.assertIsNone(propositions.recours(m, 'odon', intention['motif'], intention['plan']))
            self.assertEqual(calcul.call_count, 1)


if __name__ == '__main__':
    unittest.main()
