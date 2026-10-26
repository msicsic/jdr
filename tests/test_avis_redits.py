"""Distinguer une redite d'une nouvelle extinction et de deux objets homonymes."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import ecoute, pnj, social
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import ecouler
from tests.test_social import recharger


class AvisReditsReelsTests(unittest.TestCase):
    def parcours(self, scenario, minute, duree):
        chemin = Path(__file__).parent / 'fixtures/avis_redits' / f'{scenario}-2024-{minute}.json.gz'
        resultats = []
        for tranches in ((duree,), (150,) * (duree // 150)):
            with gzip.open(chemin, 'rt', encoding='utf-8') as f:
                m = recharger(Monde(json.load(f)))
            lignes = []
            rallumages = []
            reviser = social.reviser_dits
            def revision(monde, id, sujet, attribut, valeur, **details):
                if id == 'marchand' and sujet == 'torche' and attribut == 'etat' and valeur.get('allume'):
                    rallumages.append(monde.data['minutes'])
                return reviser(monde, id, sujet, attribut, valeur, **details)
            with patch.object(social, 'reviser_dits', revision):
                for dt in tranches:
                    pnj.avancer(m, ecouler(m, dt), lignes, dt)
                    m = recharger(m)
            if scenario == 'crue':
                self.assertTrue(any(146 < t < 242 for t in rallumages))
            sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
            visible = regarder(m), ecoute.rendre(m, sons)
            recharge = recharger(m)
            self.assertEqual(visible, (regarder(recharge), ecoute.rendre(recharge, sons)))
            resultats.append((m.data, visible))
        self.assertEqual(*resultats)
        return m

    def test_mine_2024_deux_lampes_homonymes_restent_deux_faits(self):
        m = self.parcours('mine', 70, 12 * 600)
        dits = [c for c in m.data['chronique'] if c['pnj'] == 'josse' and c.get('constat_confie')
                and 'Lucien' in c['texte'] and 'rechange' in c['texte']]
        self.assertEqual([c['minute'] for c in dits], [76, 79])
        for objet in ('lampe_rechange_1', 'lampe_rechange_2'):
            self.assertFalse(m.objets[objet]['allume'])
            self.assertFalse(lire(m, 'lucien')['croyances'][objet]['etat']['valeur']['allume'])

    def test_crue_2024_rallumage_connu_de_gorm_autorise_la_nouvelle_extinction(self):
        m = self.parcours('crue', 140, 110 * 600)
        dits = [c for c in m.data['chronique'] if c['pnj'] == 'brune' and c.get('constat_confie')
                and 'Gorm' in c['texte'] and 'torche' in c['texte']]
        self.assertEqual([c['minute'] for c in dits], [146, 242])
        # La croyance finale peut aussi venir de la parole d'un tiers.
        self.assertFalse(lire(m, 'marchand')['croyances']['torche']['etat']['valeur']['allume'])
        self.assertFalse(m.objets['torche']['allume'])
