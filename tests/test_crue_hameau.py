"""Le dérivé conserve ses données, son asymétrie et sa reprise temporelle."""
import json
from pathlib import Path
import unittest

from donjon.banc_pnj import creer
from donjon.esprits import pnjs, lire
from donjon import pnj
from donjon.temps import ecouler
from donjon.rendu import regarder
from tests.test_social import recharger


class CrueHameauTests(unittest.TestCase):
    def test_profils_et_references(self):
        raw = json.loads((Path(__file__).parents[1] / "donjon/scenario_crue_hameau.json").read_text(encoding="utf-8"))
        ids = set(raw["objets"]) | set(raw["salles"]) | {"joueur"}
        for o in raw["objets"].values():
            self.assertIn(o["lieu"], ids)
            for salle in o.get("relie", []):
                self.assertIn(salle, raw["salles"])
        for qui in ("mael", "seve"):
            self.assertFalse(any("eau" in a or "prevision" in a for a in raw["esprits"][qui]["croyances"].values()))
        for qui in ("marchand", "aubin"):
            self.assertIn("eau", raw["esprits"][qui]["croyances"]["crypte"])

    def test_chargement_et_rendu_recharges(self):
        for seed in (1985, 7, 42, 2024):
            with self.subTest(seed=seed):
                m = creer("crue_hameau", seed)
                m.verifier()
                self.assertEqual(len(list(pnjs(m))), 6)
                self.assertEqual(m.data, recharger(m).data)
                self.assertEqual(regarder(m), regarder(recharger(m)))
                for qui in ("mael", "seve"):
                    self.assertIn("hameau_noye", m.data["savoirs_pnj"][qui])

    def test_scene_bloc_et_decoupee(self):
        for seed in (1985, 42):
            resultats = []
            for tranches in ((1200,), (150,) * 8):
                m = creer("crue_hameau", seed)
                for dt in tranches:
                    pnj.avancer(m, ecouler(m, dt), [], dt)
                    m = recharger(m)
                m.verifier()
                resultats.append((m.data, regarder(m)))
            with self.subTest(seed=seed):
                self.assertEqual(*resultats)

    def test_adoptions_naturelles_persistantes(self):
        import gzip
        from donjon.monde import Monde
        from donjon.esprits import recevoir_prevision, prevision
        from donjon.ecoute import entendus, rendre, ENTENDU
        for qui in ("seve", "aubin"):
            with self.subTest(qui=qui):
                chemin = Path(__file__).parent / "fixtures/crue_hameau" / (qui + "-1985.json.gz")
                with gzip.open(chemin, "rt", encoding="utf-8") as f:
                    c = json.load(f)
                m = recharger(Monde(c["data"]))
                # Aucun constat direct des salles basses ; le palier a été vu.
                for salle in ("echoppe", "crypte"):
                    eau = lire(m, qui)["croyances"][salle]["eau"]
                    self.assertTrue(eau["source"].startswith("dit:"))
                self.assertTrue(c["propre"]["source"].startswith("dit:"))
                self.assertEqual(recevoir_prevision(m, qui, c["locuteur"], c["noyau"], c["rang"], **c["kw"]), "crue")
                self.assertEqual(prevision(m, qui, c["noyau"]["objet"]), c["apres"])
                sons = entendus(m, -1, ENTENDU)
                visible = (regarder(m), rendre(m, sons))
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(visible, (regarder(recharge), rendre(recharge, sons)))
                self.assertTrue(any(e.get("changement_avis") == "dit" and e["pnj"] == qui
                                    for e in recharge.data["chronique"]))
