"""Le lanceur détaché annonce aussi les échecs de son initialisation."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


CHEMIN = Path(__file__).resolve().parents[1] / 'tools/verifier_contact_313.py'
spec = importlib.util.spec_from_file_location('verifier_contact_313', CHEMIN)
lanceur = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lanceur)


class LanceurContactTests(unittest.TestCase):
    def verifier_echec(self, priorite, erreur):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                sys, 'argv', [str(CHEMIN), '--sortie', tmp]), patch.dict(
                sys.modules, {'priorite': priorite}), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lanceur.main(), 1)
            bilan = json.loads((Path(tmp) / 'fin.json').read_text(encoding='utf8'))
            self.assertFalse(bilan['ok'])
            self.assertIn(erreur, bilan['erreur'])
            self.assertGreaterEqual(bilan['fin'], bilan['debut'])
            self.assertNotIn('tests_code', bilan)

    def test_import_en_echec_ecrit_fin(self):
        self.verifier_echec(None, 'ModuleNotFoundError')

    def test_initialisation_priorite_en_echec_ecrit_fin(self):
        def ceder():
            raise RuntimeError('priorité indisponible')
        self.verifier_echec(SimpleNamespace(ceder=ceder), 'priorité indisponible')


if __name__ == '__main__':
    unittest.main()
