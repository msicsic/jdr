"""Banc multiple : les indicateurs d'une passe et le résumé par variante."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import banc_multi  # noqa: E402


def partie(*tours):
    return {"tours": [{"saisie": "x", "appels": a, "secondes": s, "replis": ["r"] if r else [], "refus": [],
                       "fil": []} for a, s, r in tours]}


class BancMultiTests(unittest.TestCase):
    def test_mesure_d_une_passe(self):
        with tempfile.TemporaryDirectory() as dossier:
            f = Path(dossier) / "a.json"
            f.write_text(json.dumps(partie((2, 10.0, False), (4, 20.0, True), (0, 0.0, False))), encoding="utf-8")
            m = banc_multi.mesurer([f])
        self.assertEqual((m["tours_mj"], m["appels_par_tour"], m["secondes_par_tour"], m["replis"]), (2, 3.0, 15.0, 1))

    def test_resume_moyenne_et_etendue_par_variante(self):
        base = {"appels_par_tour": 3.0, "secondes_par_tour": 10.0, "replis": 0, "tours_refus": 1,
                "obstacles": 4, "cout": 0.1, "reflexion": 1.0, "tours_mj": 31}
        passes = [("avant", {**base, "replis": 0}), ("avant", {**base, "replis": 2}), ("apres", base)]
        tableau = banc_multi.resumer(passes)
        self.assertIn("avant (2 passes)", tableau)
        self.assertIn("| Tours en repli | 1.0 (0.0 – 2.0) | 0.0 |", tableau)


if __name__ == "__main__":
    unittest.main()
