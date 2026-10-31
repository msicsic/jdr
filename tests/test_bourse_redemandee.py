"""Une restitution clôt l'essai d'emprunt, jusqu'à une entrée utile nouvelle."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import biens, echanges, planification
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from tests import test_garde_pret as scenes
from tests.test_tensions import recharger
from tests.support import canal_constats_anterieur_337


class RestitutionTests(unittest.TestCase):
    def stable(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        return n

    @canal_constats_anterieur_337
    def test_capture_reelle_mine_mathe_remy_et_laps_decoupe(self):
        # 360 : conserver le canal de constats récents de cette ancienne
        # nuit ; restitution, droits et blocage du réemprunt restent réels.
        with gzip.open(Path(__file__).parent / 'data/bourse-220-mine-290.json.gz', 'rt', encoding='utf-8') as f:
            m = Monde(json.load(f))
        a, b = self.stable(m), self.stable(m)
        from donjon.pnj import avancer
        from donjon.temps import ecouler
        avancer(a, ecouler(a, 9000), [], 9000)
        for _ in range(3):
            avancer(b, ecouler(b, 3000), [], 3000)
            b = self.stable(b)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(a.objets['paie']['lieu'], 'remy')
        self.assertEqual(a.objets['paie']['proprietaire'], 'remy')
        self.assertFalse([c for c in a.data['chronique'] if c['minute'] >= 290
                          and c['pnj'] in ('mathe', 'remy')
                          and ' demande la bourse' in c['texte']])
        retours = a.data.get('restitutions', {})
        self.assertTrue(any('paie' in retours.get(x, {}) for x in ('mathe', 'remy')))
        # La mémoire n'est pas le récit tronqué : chaque emprunt effectivement
        # rendu reste bloqué, même si les conversations ont rempli la mémoire.
        for acteur in ('mathe', 'remy'):
            retour = retours.get(acteur, {}).get('paie')
            if retour:
                self.assertTrue(biens.restitution_retenue(a, acteur, retour['a'], 'paie'))
        self.stable(a)

    def test_autre_bien_deux_scenarios_restitution_volontaire_ou_imposee(self):
        for scenario in ('relais', 'auberge'):
            for imposee in (False, True):
                with self.subTest(scenario=scenario, imposee=imposee):
                    m, acteur, donneurs = scenes.DemandeTests().scene(scenario)
                    autre, objet = donneurs[0], 'source_0'
                    with patch.object(Monde, 'd20', return_value=20):
                        self.assertEqual(echanges.demander(m, acteur, autre, objet), 'remis')
                    m = self.stable(m)
                    lire(m, acteur)['intention'] = None
                    if imposee:
                        self.assertEqual(echanges.demander(m, autre, acteur, objet), 'rendu')
                    else:
                        echanges.remettre(m, acteur, autre, objet)
                    m = self.stable(m)
                    avant = copy.deepcopy(m.data)
                    self.assertTrue(planification.Vue(m, acteur).refuse(autre, objet))
                    self.assertEqual(echanges.demander(m, acteur, autre, objet), 'refus')
                    self.assertEqual(m.objets[objet]['lieu'], autre)
                    self.assertEqual(m.data, avant)
                    # Le temps seul et la répétition du même savoir ne relancent rien.
                    m.data['minutes'] += 300
                    croire(m, acteur, objet, 'lieu', autre, 'vu', salle=m.objets[autre]['lieu'],
                           case=m.objets[autre]['position'])
                    self.assertTrue(biens.restitution_retenue(self.stable(m), acteur, autre, objet))
                    # Un nouveau moyen propre permet un nouvel essai.
                    m.data['finances_pnj'][acteur] = biens.bourse(m, acteur) + 1
                    m = self.stable(m)
                    self.assertFalse(biens.restitution_retenue(m, acteur, autre, objet))
                    with patch.object(Monde, 'd20', return_value=20):
                        self.assertEqual(echanges.demander(m, acteur, autre, objet), 'remis')
                    self.stable(m)

    def test_joueur_et_transfert_impose_hors_remise(self):
        from donjon.deplacement_objet import deplacer
        m, _, donneurs = scenes.DemandeTests().scene('relais')
        autre, objet = donneurs[0], 'source_0'
        echanges.remettre(m, autre, 'joueur', objet)
        m = self.stable(m)
        deplacer(m, objet, autre)
        m = self.stable(m)
        self.assertTrue(biens.restitution_retenue(m, 'joueur', autre, objet))
        self.assertEqual(lire(m, 'joueur')['croyances'][objet]['lieu']['valeur'], autre)
        self.assertEqual(echanges.demander(m, 'joueur', autre, objet), 'refus')
        m.joueur['or'] += 1
        self.assertFalse(biens.restitution_retenue(self.stable(m), 'joueur', autre, objet))

    def test_nouveau_besoin_rouvre_sans_delai(self):
        m, acteur, donneurs = scenes.DemandeTests().scene('auberge')
        autre, objet = donneurs[0], 'source_0'
        m.objets[objet]['prix'] = 0
        echanges.remettre(m, autre, acteur, objet)
        echanges.remettre(m, acteur, autre, objet)
        self.assertTrue(biens.restitution_retenue(self.stable(m), acteur, autre, objet))
        lire(m, acteur)['besoins']['faim'] = 100.0
        self.assertFalse(biens.restitution_retenue(self.stable(m), acteur, autre, objet))

    def test_achat_reste_une_autre_reponse_et_don_non_restitue(self):
        m, acteur, donneurs = scenes.DemandeTests().scene('relais')
        autre, objet = donneurs[0], 'source_0'
        m.data['finances_pnj'][acteur] = 100
        m.objets[objet]['prix'] = 1
        echanges.remettre(m, autre, acteur, objet)
        echanges.remettre(m, acteur, autre, objet)
        m = self.stable(m)
        self.assertTrue(biens.restitution_retenue(m, acteur, autre, objet))
        # Une vente est distincte d'un nouvel emprunt, mais elle doit payer
        # la capacité perdue : une pièce ne compense pas cette lampe unique.
        self.assertEqual(echanges.demander(m, acteur, autre, objet, prix=1), 'necessaire')
        offre = echanges.contre_offre(m, acteur, autre, objet, 'necessaire')
        self.assertIsNotNone(offre)
        prix = offre['condition']['montant']
        self.assertGreater(prix, 1)
        m = self.stable(m)
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.demander(m, acteur, autre, objet, prix=prix), 'vendu')
        self.assertEqual(self.stable(m).objets[objet]['proprietaire'], acteur)
        # Un transfert gratuit de propriété est un don, pas un prêt rendu.
        objet = 'source_1'
        m.objets[objet].update(type='nourriture', portions=1)
        echanges.remettre(m, donneurs[1], acteur, objet)
        self.assertNotIn(objet, m.data.get('restitutions', {}).get(donneurs[1], {}))
        self.stable(m)
