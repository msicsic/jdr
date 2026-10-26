"""Même tour moteur et même vue rechargée que le relevé direct par case."""
from contextlib import nullcontext
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, trajet_estime as t
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger


class ReleveObstaclesTests(unittest.TestCase):
    def test_captures_auberge_et_mine_memes_decisions_et_rendus_recharges(self):
        original = t._moyenne
        for scenario in ('auberge', 'mine'):
            with self.subTest(scenario=scenario):
                fichier = Path(__file__).parent / f'data/cout-12h/{scenario}-1985-480.json.gz'
                donnees = json.loads(gzip.decompress(fichier.read_bytes()))
                resultats = []
                for direct in (True, False):
                    m = recharger(Monde(copy.deepcopy(donnees)))
                    # L'oracle recalcule les tables et garde le prédicat spatial
                    # original case par case, indépendant du relevé groupé.
                    def oracle(*a, **k):
                        return original(*a, **{**k, 'pur': True})
                    with patch.object(p, '_MEMOIRE', {}), patch.object(p, '_GRAPHES', {}), \
                            patch.object(p, '_IMPOSSIBLES', {}), p.diagnostics() as recherches:
                        with patch.object(t, '_moyenne', oracle) if direct else nullcontext():
                            moteur = Moteur(m)
                            lignes = moteur.executer(moteur.preparer(proposition('attendre')))
                    recharge = recharger(m)
                    self.assertEqual(m.data, recharge.data)
                    self.assertEqual(regarder(m), regarder(recharge))
                    self.assertEqual(scene_percue(m), scene_percue(recharge))
                    resultats.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge),
                        [{k: x for k, x in r.items() if k != 'duree'} for r in recherches]))
                self.assertEqual(resultats[0], resultats[1])
