"""Un refus de marché survit aux abords sans rapport et aux plans rechargés."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon.echanges import executer
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import refus_tient
from donjon.rendu import regarder
from tests.test_proposer_recours import scene
from tests.test_tensions import recharger


class PropositionsReditesTests(unittest.TestCase):
    def capture(self, nom):
        with gzip.open(Path(__file__).parent / 'data' / nom, 'rt', encoding='utf8') as f:
            return recharger(Monde(json.load(f)))

    def test_captures_reelles_meme_laps_decoupe_et_recharge(self):
        for nom, auteur, autre, objet, attendu in (
            ('redites-mine7-240.json.gz', 'josse', 'lucien', 'pain_lucien', 1),
            ('redites-crue11-340.json.gz', 'brune', 'marchand', 'vivres', 0),
        ):
            with self.subTest(capture=nom):
                a = self.capture(nom)
                b = recharger(a.copier())
                debut = a.data['minutes']
                moteur = Moteur(a)
                moteur.executer(moteur.preparer(proposition('attendre', cible='600')))
                for _ in range(2):
                    moteur = Moteur(b)
                    moteur.executer(moteur.preparer(proposition('attendre', cible='300')))
                    b = recharger(b)
                a = recharger(a)
                self.assertEqual(a.data['minutes'], debut + 10)
                # Toutes les pensées et les possessions, pas la seule fonction du recours.
                for cle in ('esprits', 'objets', 'finances_pnj', 'gestes_en_cours', 'jets', 'chronique'):
                    self.assertEqual(a.data.get(cle), b.data.get(cle), cle)
                self.assertEqual(regarder(a), regarder(b))
                self.assertEqual(regarder(a), regarder(recharger(a)))
                offres = [s for s in lire(a, auteur)['memoire']
                          if s['type'] == 'proposition' and s['a'] == autre
                          and s['demande'].get('objet') == objet and s['minute'] >= debut]
                # Un moyen ordinaire peut aussi dispenser de la première offre.
                # La mine n'en répète aucune ; la crue avait déjà son refus à 0.
                identiques = [s for s in offres if s['contrepartie'] == (
                    {'type':'objet', 'objet':'lampe_josse'} if auteur == 'josse'
                    else {'type':'pieces', 'montant':2})]
                self.assertLessEqual(len(identiques), attendu)
                self.assertEqual(a.objets[objet]['proprietaire'], autre)

    def test_plan_refuse_recharge_sans_publication_puis_offre_plus_forte(self):
        from donjon.deliberation import choisir
        m = scene(10)
        m.data['finances_pnj']['brune'] = 1
        m.objets['crochets']['prix'] = 100
        choisir(m, 'brune', 0)
        geste = copy.deepcopy(lire(m, 'brune')['intention']['plan'][0])
        lignes = []
        executer(m, 'brune', geste, lignes)
        self.assertIn("refuse l'échange", ' '.join(lignes))
        m = recharger(m)
        avant = copy.deepcopy(m.data)
        lignes = []
        self.assertFalse(executer(m, 'brune', geste, lignes))
        self.assertEqual(m.data, avant)
        self.assertEqual(lignes, [])
        m.data['finances_pnj']['brune'] = 2
        geste['contenu']['contrepartie']['montant'] = 2
        executer(m, 'brune', geste, lignes)
        self.assertIn('2 pièces', ' '.join(lignes))
        m = recharger(m)
        self.assertEqual(lire(m, 'brune')['refus'][-1]['offre']['gain'], 2)
        self.assertEqual(m.data['finances_pnj']['brune'], 2)
        self.assertEqual(m.objets['vivres']['proprietaire'], 'marchand')

    def test_seul_le_bien_nouvellement_porte_et_offert_leve_le_refus(self):
        from donjon.deliberation import retenir_refus
        from donjon.pnj_propositions import entrees_refus
        m = scene()
        m.objets['crochets'].update(lieu='antichambre', position=[5, 4])
        offre = {'type':'pieces', 'montant':2}
        retenir_refus(m, 'brune', 'marchand', 'proposer', 'garde', objet='vivres',
                      offre=entrees_refus(m, 'brune', 'marchand', 'vivres', offre))
        m = recharger(m)
        s = lire(m, 'brune')['refus'][-1]
        m.objets['crochets'].update(lieu='brune', prix=1)
        self.assertTrue(refus_tient(m, 'brune', s, offre))
        self.assertFalse(refus_tient(m, 'brune', s, {'type':'objet', 'objet':'crochets'}))
        m.data['minutes'] += 300
        self.assertTrue(refus_tient(recharger(m), 'brune', s, offre))

    def test_achat_sauvegarde_refuse_sans_rejouer_le_meme_prix(self):
        from donjon.deliberation import retenir_refus
        m = scene()
        retenir_refus(m, 'brune', 'marchand', 'acheter', 'necessaire', objet='vivres', prix=1)
        m = recharger(m)
        geste = {'operation':'acheter', 'cible':'marchand', 'outil':'vivres',
                 'lieu':'', 'condition':'', 'contenu':{'prix':1}}
        avant = copy.deepcopy(m.data)
        lignes = []
        self.assertFalse(executer(m, 'brune', geste, lignes))
        self.assertEqual(m.data, avant)
        self.assertEqual(lignes, [])


if __name__ == '__main__':
    unittest.main()
