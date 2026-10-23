"""Une économie de calcul doit préserver chaque recherche et chaque empreinte de la nuit."""
import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import empreintes_nuits as outil


class ComparaisonTests(unittest.TestCase):
    def nuit(self):
        return dict(scenario='mine', graine=7, depart='tire', heures=8,
                    empreintes={n: 'identique' for n in
                        ('chronique', 'mesures', 'recit', 'souvenirs', 'etat', 'banc', 'recherches_neuves')},
                    neuves=20, noeuds=100, recherches_logiques=30, trace_recherches='tous-les-resultats',
                    secondes=1, planificateur=0.5, memoire_mo=40)

    def comparer(self, a, b, calcul=True):
        with tempfile.TemporaryDirectory() as dossier:
            chemins = [Path(dossier) / n for n in ('a.json', 'b.json')]
            for chemin, valeurs in zip(chemins, (a, b)):
                chemin.write_text(json.dumps(valeurs), encoding='utf-8')
            with redirect_stdout(io.StringIO()):
                return outil.comparer(SimpleNamespace(a=chemins[0], b=chemins[1], calcul=calcul))

    def test_seuls_les_comptes_de_calcul_peuvent_changer(self):
        a, b = self.nuit(), self.nuit()
        b.update(neuves=3, noeuds=8, secondes=0.1)
        b['empreintes']['recherches_neuves'] = 'moins-de-recherches'
        self.assertEqual(self.comparer([a], [b]), 0)
        self.assertEqual(self.comparer([a], [b], calcul=False), 1)
        for champ in ('recherches_logiques', 'trace_recherches', 'heures'):
            avec_ecart = {**b, champ: 'autre'}
            self.assertEqual(self.comparer([a], [avec_ecart]), 1, champ)
        for champ in ('chronique', 'mesures', 'recit', 'souvenirs', 'etat', 'banc'):
            avec_ecart = copy.deepcopy(b)
            avec_ecart['empreintes'][champ] = 'autre'
            self.assertEqual(self.comparer([a], [avec_ecart]), 1, champ)

    def test_un_controle_ou_une_nuit_absents_font_echouer(self):
        a = self.nuit()
        self.assertEqual(self.comparer([a], []), 1)
        for champ in ('trace_recherches', 'recherches_logiques'):
            b = copy.deepcopy(a)
            del b[champ]
            self.assertEqual(self.comparer([b], [b]), 1)
        del a['empreintes']['etat']
        self.assertEqual(self.comparer([a], [a]), 1)
