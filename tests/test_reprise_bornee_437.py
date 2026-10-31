"""Reprise exacte et référence complète sur la capture fautive du lot 402."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, spatial
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger


def capture(minute):
    path = Path(__file__).parent / f'data/reprise-bornee-437/auberge-42-{minute}.json.gz'
    return Monde(json.loads(gzip.decompress(path.read_bytes())))


class RepriseBorneeTests(unittest.TestCase):
    def setUp(self):
        for nom in ('_MEMOIRE', '_GRAPHES', '_IMPOSSIBLES'):
            contexte = patch.object(p, nom, {})
            contexte.start()
            self.addCleanup(contexte.stop)

    def visible(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_capture_reelle_memoire_et_graphe_egaux_au_recalcul(self):
        m = self.visible(capture(364))
        avant = copy.deepcopy(m.data)
        resultats = []
        with patch.object(p, 'VERIFIER', True), patch.object(p, 'BORNES', []), p.diagnostics() as ds:
            for _ in range(3):
                p._MEMOIRE.clear()
                resultats.append(p.chercher(m, 'lucien', lambda v, e: e.salle == 'chambre_chaude',
                    memo=['garder', 'chambre_chaude'], nom='garder:chambre_chaude',
                    emplois=(), motif='biens', tenir=True, endurer=0))
            resultats.append(p.chercher(m, 'lucien', lambda v, e: e.salle == 'chambre_chaude',
                memo=['garder', 'chambre_chaude'], nom='garder:chambre_chaude',
                emplois=(), motif='biens', tenir=True, endurer=0))
            self.assertTrue(ds[2]['graphe'])
            self.assertTrue(ds[3]['memoire'])
            self.assertTrue(all(r == resultats[0] for r in resultats))
            self.assertAlmostEqual(resultats[0][0], 82.72039452358611)
            self.assertEqual(len(p.BORNES), 4)
            self.assertTrue(all(b['ancienne_borne'] and b['trouve'] == b['optimum'] for b in p.BORNES))
        self.assertEqual(avant, m.data)
        self.visible(m)

    def test_capture_360_avance_reelle_spatial_et_rechargement(self):
        fins = []
        for verifier in (False, True):
            m = self.visible(capture(360))
            for cache in (p._MEMOIRE, p._GRAPHES, p._IMPOSSIBLES):
                cache.clear()
            with patch.object(p, 'VERIFIER', verifier), patch.object(spatial, 'VERIFICATION', 1):
                moteur = Moteur(m)
                lignes = moteur.executer(moteur.preparer(proposition('attendre')))
            self.assertEqual(m.data['minutes'], 365)
            m = self.visible(m)
            fins.append((m.data, lignes, regarder(m), scene_percue(m)))
        self.assertEqual(*fins)

    def test_reprise_corrompue_refusee_meme_si_le_temoignage_uniforme_plafonne(self):
        m = capture(364)
        v = p.Vue(m, 'lucien')
        v.degat, v.motif, v.desespere = 1, 'biens', False
        e = p.depart(m, 'lucien', v)
        ancien = (1, (), e)
        neuf = (1, (p._figer_etape({'operation': 'aller'}),), e)
        with patch.object(p, '_explorer', return_value=(neuf, p.NOEUDS, 0, 0)), \
                self.assertRaisesRegex(AssertionError, 'mémoire, neuve'):
            p._verifier(m, 'lucien', v, lambda *a: False, None, None, 8, p.NOEUDS,
                        1, False, None, None, 'test', ancien, True, 'mémoire')

    def test_borne_jouee_sans_plan_reste_distincte_d_une_impossibilite(self):
        m = capture(364)
        v = p.Vue(m, 'lucien')
        v.degat, v.motif, v.desespere, v.emplois = 1, 'biens', False, frozenset()
        e = p.depart(m, 'lucien', v)
        def explorer(*a, **kw):
            return ((5, (), e), 1, 1, 0) if a[5] == p.REFERENCE else (None, p.NOEUDS, 1, 0)
        with patch.object(p, '_explorer', explorer), patch.object(p, 'BORNES', []):
            p._verifier(m, 'lucien', v, lambda *a: False, None, None, 8, p.NOEUDS,
                        1, False, None, None, 'test', None, True, 'borne')
            self.assertEqual(p.BORNES[0]['optimum'], 5)
            with self.assertRaisesRegex(AssertionError, 'certificat, complète'):
                p._verifier(m, 'lucien', v, lambda *a: False, None, None, 8, p.NOEUDS,
                            1, False, None, None, 'test', None, True, 'impossibilité')


if __name__ == '__main__':
    unittest.main()
