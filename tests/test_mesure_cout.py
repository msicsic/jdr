"""Contrats de l'outil de mesure, sans Luna ni longue campagne."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import contextmanager

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import mesure_cout as outil
import references


class MesureCout(unittest.TestCase):
    def test_agregation_frontiere_horaire_et_buts(self):
        c = outil.Compteurs()
        c.ajouter(59.9, 'a', 'faim', gestes=2, noeuds=3)
        c.ajouter(60, 'a', 'faim', gestes=4)
        c.ajouter(60, 'b', 'froid', gestes=1)
        c.ajouter(60, 'a', '__choix__', choix=1)
        r = c.resultat(2)
        self.assertEqual(r['total'], dict(gestes=7, noeuds=3, choix=1))
        self.assertEqual(r['par_heure']['gestes'], 3.5)
        self.assertEqual(len(r['lignes']), 4)
        self.assertEqual(r, c.resultat(2))

    def test_cache_commit_et_configuration(self):
        config = dict(scenario='mine', graine=1985, heures=12, depart='fixe')
        resultat = dict(compteurs={'total': {'choix': 1}}, empreintes={'etat': 'a'}, secondes_cpu=1)
        @contextmanager
        def arbre(*a):
            yield Path('arbre')
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as temp, \
                patch.object(references, 'dossier', return_value=Path(temp)), \
                patch.object(references, 'resoudre', return_value='abc'), \
                patch('comparer_bancs.worktree_temporaire', arbre), \
                patch.object(outil, 'lancer', return_value=resultat) as lancer:
            a = outil.mesurer('.', 'ref', [config], True)
            self.assertEqual(lancer.call_count, 3)
            self.assertTrue(all(a[0]['verification'].values()))
            b = outil.mesurer('.', 'ref', [config], True)
            self.assertEqual(lancer.call_count, 3)
            self.assertTrue(b[0]['cache'])
            outil.mesurer('.', 'ref', [dict(config, graine=7)], True)
            self.assertEqual(lancer.call_count, 6)

    def test_refus_divergence_non_cachee(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as temp, \
                patch.object(references, 'dossier', return_value=Path(temp)), \
                patch.object(references, 'resoudre', return_value='abc'), \
                patch('comparer_bancs.worktree_temporaire') as arbre, \
                patch.object(outil, 'lancer', side_effect=[
                    dict(compteurs=1, empreintes=1), dict(compteurs=2, empreintes=1),
                    dict(compteurs=0, empreintes=1, secondes_cpu=1)]):
            arbre.return_value.__enter__.return_value = Path(temp)
            with self.assertRaisesRegex(RuntimeError, 'Contrôle échoué'):
                outil.mesurer('.', 'ref', [{}], True)
            self.assertEqual(list(Path(temp).rglob('*.json')), [])

    def test_nuit_reelle_invariance(self):
        # Processus propres : mêmes conditions que les références git.
        depot = Path(__file__).resolve().parents[1]
        config = dict(scenario='auberge', graine=1985, heures=.1, depart='fixe')
        a, b = outil.lancer(depot, config), outil.lancer(depot, config)
        temoin = outil.lancer(depot, config, False)
        self.assertEqual(a['compteurs'], b['compteurs'])
        self.assertEqual(a['empreintes'], b['empreintes'])
        self.assertEqual(a['empreintes'], temoin['empreintes'])
        self.assertGreater(a['compteurs']['total']['choix'], 0)
        self.assertEqual(sum(l.get('gestes', 0) for l in a['compteurs']['lignes']),
                         a['compteurs']['total']['gestes'])


if __name__ == '__main__':
    unittest.main()
