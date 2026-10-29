"""Un refus de marché survit aux abords sans rapport et aux plans rechargés."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon.echanges import executer
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import refus_tient
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import instant, MINUTE
from tests.test_proposer_recours import scene
from tests.test_tensions import recharger


class PropositionsReditesTests(unittest.TestCase):
    def setUp(self):
        # Rejouer les refus historiques sans ajouter un projet d'acquisition.
        naissance = patch("donjon.agendas._naissances", return_value=None)
        naissance.start()
        self.addCleanup(naissance.stop)

    def capture(self, nom):
        with gzip.open(Path(__file__).parent / 'data' / nom, 'rt', encoding='utf8') as f:
            return recharger(Monde(json.load(f)))

    def attendre_laps(self, monde, dixiemes):
        # Prémisse du test de refus : le joueur reprend son attente après les
        # appels entendus, sans répondre ni intervenir, jusqu'au même terme.
        # Une commande d'attente seule est interruptible et ne promet pas ce laps.
        fin = instant(monde) + dixiemes
        while instant(monde) < fin:
            avant = instant(monde)
            moteur = Moteur(monde)
            moteur.executer(moteur.preparer(proposition(
                'attendre', cible=f'{(fin - avant) / 10:g}')))
            self.assertGreater(instant(monde), avant)
            self.assertLessEqual(instant(monde), fin)
        self.assertEqual(instant(monde), fin)

    def test_captures_reelles_meme_laps_decoupe_et_recharge(self):
        for nom, auteur, autre, objet, attendu in (
            ('redites-mine7-240.json.gz', 'josse', 'lucien', 'pain_lucien', 1),
            ('redites-crue11-340.json.gz', 'brune', 'marchand', 'vivres', 0),
        ):
            with self.subTest(capture=nom):
                a = self.capture(nom)
                b = recharger(a.copier())
                debut = a.data['minutes']
                self.attendre_laps(a, 10 * MINUTE)
                for _ in range(2):
                    self.attendre_laps(b, 5 * MINUTE)
                    b = recharger(b)
                a = recharger(a)
                self.assertEqual(a.data['minutes'], debut + 10)
                self.assertEqual(instant(a), instant(b))
                # Toutes les pensées et les possessions, pas la seule fonction du recours.
                for cle in ('esprits', 'objets', 'finances_pnj', 'gestes_en_cours', 'jets', 'chronique'):
                    self.assertEqual(a.data.get(cle), b.data.get(cle), cle)
                self.assertEqual(regarder(a), regarder(b))
                self.assertEqual(regarder(a), regarder(recharger(a)))
                self.assertEqual(scene_percue(a), scene_percue(b))
                self.assertEqual(scene_percue(a), scene_percue(recharger(a)))
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

    def test_capture_mine_interlocuteur_inaccessible_hele_et_interrompt_l_attente(self):
        from donjon import planification as plans
        from donjon.ouie import saisit
        m = self.capture('redites-mine7-240.json.gz')
        debut = instant(m)
        v = plans.Vue(m, 'remy')
        e = plans.depart(m, 'remy', v)
        self.assertEqual(e.salle, 'baraquement')
        self.assertEqual(v.salle(e, 'bram'), 'bureau')
        self.assertEqual(m.objets['bram']['lieu'], 'bureau')
        self.assertIsNone(v.route(e, 'bureau'))
        self.assertTrue(v.verrouille(e, 'porte_bureau'))
        self.assertIsNotNone(plans._appeler(v, e, 'bram'))
        self.assertTrue(saisit(m, 'remy', 'bram', 'heler'))
        moteur = Moteur(m)
        texte = moteur.executer(moteur.preparer(proposition('attendre', cible='600')))
        self.assertEqual(instant(m), debut + 4 * MINUTE + 150)
        cris = [c for c in m.data['chronique'] if c['pnj'] == 'remy'
                and c['instant'] >= debut and ' appelle : ' in c['texte']]
        self.assertEqual(len(cris), 1)
        self.assertEqual(cris[0]['instant'], debut + 4 * MINUTE + 60)
        self.assertEqual(cris[0]['texte'], 'Rémy appelle : « Bram ? »')
        self.assertIn('Bram ?', texte)
        self.assertIn("tu cesses d'attendre", texte)
        recharge = recharger(m)
        self.assertEqual(m.data, recharge.data)
        self.assertEqual(regarder(m), regarder(recharge))
        self.assertEqual(scene_percue(m), scene_percue(recharge))

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
