"""Captures réelles crue 500/2024, profils inchangés, juste avant les avis à 72/102 min."""
import gzip
import json
from pathlib import Path
import unittest

from donjon import ecoute, pnj, social
from donjon.esprits import lire, prevision
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import ecouler
from tests.test_social import recharger


def capture(graine):
    chemin = Path(__file__).parent / 'fixtures' / 'avis_reels' / f'crue-{graine}.json.gz'
    with gzip.open(chemin, 'rt', encoding='utf8') as f:
        return recharger(Monde(json.load(f)))


class AvisReelsTests(unittest.TestCase):
    def parcours(self, graine, locuteur, auditeur, minute, id_auditeur):
        resultats = []
        for tranches in ((6000,), (150,) * 40):
            m = capture(graine)
            for dt in tranches:
                pnj.avancer(m, ecouler(m, dt), [], dt)
                m = recharger(m)
            avis = [c for c in m.data['chronique'] if c.get('avis_exprime')]
            self.assertTrue(any(c['pnj'] == locuteur and c['minute'] == minute
                                and auditeur in c['texte'] and '(doute)' in c['texte'] for c in avis))
            # Les preuves propres gardent leur autorité ; dire ne signifie pas imposer.
            self.assertFalse(prevision(m, id_auditeur, 'crypte')['source'].startswith('dit:'))
            self.assertFalse(any(c.get('changement_avis') == 'dit' for c in m.data['chronique']))
            self.assertEqual(len(avis), len({(c['pnj'], c['texte']) for c in avis}))
            sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
            visible = (regarder(m), ecoute.rendre(m, sons))
            self.assertIn('voix', ' '.join(visible[1]))
            self.assertNotIn('menace', ' '.join(visible[1]))  # Trop loin pour saisir les mots.
            recharge = recharger(m)
            self.assertEqual(visible, (regarder(recharge), ecoute.rendre(recharge, sons)))
            resultats.append((m.data, visible))
        self.assertEqual(*resultats)

    def test_crue_500_avis_doute_et_reprise_decoupee(self):
        self.parcours(500, 'aubin', 'Gorm', 72, 'marchand')

    def test_crue_2024_autre_auditeur_et_reprise_decoupee(self):
        self.parcours(2024, 'aubin', 'Ilse', 102, 'ilse')

    def test_auditeur_choisi_sans_lire_sa_prevision_privee(self):
        for graine, cible in ((500, 'marchand'), (2024, 'ilse')):
            with self.subTest(graine=graine):
                m = capture(graine)
                qui = 'aubin'
                nouvelle = next(n for n in social.nouvelles(m, qui)
                                if n[1]['type'] == 'avis' and n[1]['objet'] == 'crypte')
                avant = social._auditeur(m, qui, nouvelle[0], nouvelle[1], nouvelle[3])
                self.assertEqual(avant, cible)
                autre = recharger(m)
                for attributs in lire(autre, cible)['croyances'].values():
                    attributs.pop('eau', None)
                    attributs.pop('prevision', None)
                self.assertEqual(avant, social._auditeur(autre, qui, nouvelle[0], nouvelle[1], nouvelle[3]))
                self.assertEqual(m.data, recharger(m).data)

