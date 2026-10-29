"""Le protégé appartient au but ; l'agresseur aux gestes, jusque dans la sauvegarde."""
import copy
import gzip
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon import combat, corps, deliberation, paroles
from donjon.esprits import lire, percevoir_tous
from donjon.monde import Monde
from donjon.recit_pnj import Recit, but_en_mots
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import instant
from tests.test_corps_blessable import passer
from tests.test_combat import scene
from tests.test_tensions import placer, recharger
from tests.support import regarder as orienter
from tools import audit_nuits, detecter_changements_avis as avis


def capture():
    # Octets de la capture 279, 0bad227, crue 2024, avant le premier coup.
    source = Path(__file__).parent / 'data/protection-281-avant-coup.json.gz'
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / 'monde.json'
        chemin.write_bytes(gzip.decompress(source.read_bytes()))
        return Monde.charger(chemin)


class ButProtectionTests(unittest.TestCase):
    def identique(self, a, b):
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(scene_percue(a), scene_percue(b))

    def contrat(self, m, protege):
        recharge = recharger(m)
        self.identique(m, recharge)
        avant = copy.deepcopy(recharge.data)
        intention = lire(recharge, 'marchand')['intention']
        self.assertEqual(intention['but'], {'type': 'proteger', 'qui': protege})
        self.assertEqual(intention['plan'][0]['operation'], 'frapper')
        self.assertEqual(intention['plan'][0]['cible'], 'brune')
        attendu = 'protéger ' + recharge.objets[protege]['nom'].split(',')[0]
        self.assertEqual(but_en_mots(recharge, intention['but']), attendu)
        self.assertIn('intention en cours : ' + attendu,
                      paroles.engagements_enregistres(recharge, 'marchand'))
        self.assertNotIn('intention en cours : protéger Brune',
                         paroles.engagements_enregistres(recharge, 'marchand'))
        self.assertEqual(audit_nuits._releve(recharge)['pnj']['marchand']['b'], attendu)
        decision = avis._resume_decision(intention)
        self.assertEqual(decision['but']['qui'], protege)
        self.assertEqual(decision['tete_plan']['cible'], 'brune')
        self.assertFalse(avis._est_accompli(recharge, 'marchand', intention, recharge.data['minutes']))
        recit = Recit(recharge)
        recit._episode(recharge, 'marchand', recharge.data['minutes'])
        episode = recit.donnees(recharge, [])['episodes']['marchand'][-1]
        self.assertEqual(episode['mots'], attendu)
        self.assertEqual(episode['but']['qui'], protege)
        self.assertEqual(recharge.data, avant)

    def test_capture_279_memes_quinze_coups_et_textes_justes_apres_recharge(self):
        a = capture()
        b = recharger(a)
        self.identique(a, b)
        coups, intentions = [], []
        original = combat.frapper

        def frapper(m, auteur, cible, *args, **kwargs):
            t = instant(m)
            if auteur == 'marchand':
                self.contrat(m, 'aubin')
                intentions.append(copy.deepcopy(lire(m, auteur)['intention']))
            resultat = original(m, auteur, cible, *args, **kwargs)
            coups.append((t, auteur, cible, resultat['degats']))
            return resultat

        with patch.object(combat, 'frapper', side_effect=frapper):
            passer(a, 120)
        # Les quinze gestes et six coups portés de l'archive 279, sans jets forcés.
        self.assertEqual(coups, [
            (357620, 'brune', 'aubin', 0), (357620, 'marchand', 'brune', 0),
            (357635, 'marchand', 'brune', 3), (357635, 'brune', 'marchand', 0),
            (357635, 'aubin', 'brune', 0), (357650, 'marchand', 'brune', 3),
            (357650, 'aubin', 'brune', 0), (357665, 'marchand', 'brune', 5),
            (357665, 'aubin', 'brune', 0), (357680, 'marchand', 'brune', 0),
            (357680, 'aubin', 'brune', 0), (357695, 'marchand', 'brune', 3),
            (357695, 'aubin', 'brune', 1), (357710, 'marchand', 'brune', 0),
            (357710, 'aubin', 'brune', 1),
        ])
        self.assertEqual(len(intentions), 7)
        self.assertEqual({i['depuis'] for i in intentions}, {596})
        self.assertEqual(corps.pv(a, 'brune'), 0)
        self.assertFalse(corps.conscient(a, 'brune'))
        self.assertFalse(a.data.get('defunts'))
        for _ in range(2):
            passer(b, 60)
            b = recharger(b)
        self.identique(a, recharger(a))
        self.identique(a, b)

    def test_autre_victime_4c_but_plan_et_restitution_persistes(self):
        m = scene('ilse', False)
        placer(m, 'marchand', 'antichambre', (3, 4))
        orienter(m, 'marchand', 'brune')
        percevoir_tous(m)
        with patch.object(type(m), 'd20', side_effect=[20, 1]):
            combat.frapper(m, 'brune', 'ilse')
        deliberation.choisir(m, 'marchand', m.data['minutes'])
        self.contrat(m, 'ilse')
        a, b = recharger(m), recharger(m)
        passer(a, 100)
        for _ in range(2):
            passer(b, 50)
            b = recharger(b)
        self.identique(a, recharger(a))
        self.identique(a, b)
        self.assertTrue(any(e['type'] == 'intervention' and e['id'] == 'marchand'
                            and e.get('contre') == 'brune'
                            for e in a.data['historique_corps']))
        self.assertTrue(regarder(recharger(a)))


if __name__ == '__main__':
    unittest.main()
