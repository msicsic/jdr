"""Le lanceur conserve les comptes et les verdicts de unittest, même avec subtests."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RACINE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("outil_tests", RACINE / "tools" / "tests.py")
outil = importlib.util.module_from_spec(spec)
spec.loader.exec_module(outil)


class OutilTestsTests(unittest.TestCase):
    def lancer(self, dossier, *arguments):
        rapport = Path(dossier) / "rapport.json"
        p = subprocess.run([sys.executable, str(RACINE / "tools" / "tests.py"),
                            "--dossier", str(dossier), "--processus", "2", "--durees",
                            str(Path(dossier) / "durees.json"), "--sortie", str(rapport), *arguments],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertTrue(rapport.exists(), p.stdout + p.stderr)
        return p, json.loads(rapport.read_text(encoding="utf-8"))

    def test_echec_subtests_saut_erreur_import_et_compte_unittest(self):
        with tempfile.TemporaryDirectory() as dossier:
            racine = Path(dossier)
            (racine / "test_a.py").write_text('''import unittest
class Exemple(unittest.TestCase):
    def test_ok(self):
        print("impression sans casser le JSON")
    @unittest.skip("absent")
    def test_saute(self): pass
    def test_echec(self):
        for i in range(2):
            with self.subTest(i=i): self.assertEqual(i, 10, "preuve_echec")
    @unittest.expectedFailure
    def test_attendu(self): self.fail("attendu")
''', encoding="utf-8")
            (racine / "test_b.py").write_text("raise RuntimeError('preuve_import')\n", encoding="utf-8")
            p, r = self.lancer(dossier)
            reference = unittest.TestResult()
            unittest.TestLoader().discover(dossier).run(reference)
            self.assertEqual(p.returncode, 1)
            self.assertEqual(r["tests"], reference.testsRun)
            for cle in ("failures", "errors", "skipped", "expectedFailures"):
                self.assertEqual(r[cle], len(getattr(reference, cle)))
            self.assertIn("preuve_echec", p.stderr)
            self.assertIn("preuve_import", p.stderr)
            self.assertIn("Traceback", p.stderr)

    def test_succes_inattendu_fait_echouer_et_cache_persiste(self):
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "test_surprise.py").write_text('''import unittest
class Exemple(unittest.TestCase):
    @unittest.expectedFailure
    def test_surprise(self): pass
''', encoding="utf-8")
            p, r = self.lancer(dossier)
            self.assertEqual(p.returncode, 1)
            self.assertEqual(r["unexpectedSuccesses"], 1)
            self.assertEqual(r["tests"], 1)
            self.assertEqual(len(outil.charger_durees(Path(dossier) / "durees.json")), 1)

    def test_selection_et_succes(self):
        with tempfile.TemporaryDirectory() as dossier:
            for nom in ("test_a.py", "test_b.py"):
                (Path(dossier) / nom).write_text('''import os
import unittest
from tests.support import calme
class Exemple(unittest.TestCase):
    def test_ok(self):
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            k = ctypes.windll.kernel32
            k.GetPriorityClass.argtypes = (wintypes.HANDLE,)
            self.assertEqual(k.GetPriorityClass(wintypes.HANDLE(-1)), 0x4000)
''', encoding="utf-8")
            p, r = self.lancer(dossier, "--motif", "test_a*.py")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(r["tests"], 1)
            self.assertIn("OK", p.stderr)

    def test_processus_interrompu_compte_comme_erreur(self):
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "test_crash.py").write_text('''import os
import unittest
class Exemple(unittest.TestCase):
    def test_crash(self): os._exit(7)
''', encoding="utf-8")
            p, r = self.lancer(dossier)
            self.assertEqual(p.returncode, 1)
            self.assertEqual(r["errors"], 1)
            self.assertIn("Code de retour : 7", p.stderr)

    def test_fichiers_doublons_et_plus_longs_d_abord(self):
        with tempfile.TemporaryDirectory() as dossier:
            a, b = [Path(dossier) / nom for nom in ("test_a.py", "test_b.py")]
            a.touch()
            b.touch()
            self.assertEqual(outil.selectionner(Path(dossier), [str(a), str(a)], "test_*.py"), [a.resolve()])
            self.assertEqual(outil.ordonner([a, b], {outil.cle_fichier(a): 1, outil.cle_fichier(b): 10}), [b, a])


if __name__ == "__main__":
    unittest.main()
