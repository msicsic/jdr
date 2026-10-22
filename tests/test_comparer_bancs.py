"""Identité du monde complet, appariement, mesures et propriété du worktree."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import comparer_bancs as outil


class ComparerBancsTests(unittest.TestCase):
    def config(self, **options):
        return {"empreintes": True, "heures": 5 / 60, "depart": "fixe", "verifier": False,
                "joueurs": outil.JOUEURS, "scenarios": ["relais"], "graines": [7], "processus": 1, **options}

    def test_deux_nuits_reelles_identiques_sans_comparer_les_temps(self):
        a = outil.executer_lot(self.config())[0]
        b = outil.executer_lot(self.config())[0]
        self.assertIsNone(a["plantage"])
        b["secondes_cpu"] += 100
        self.assertIsNone(outil.comparer_identite([a], [b]))
        self.assertGreater(a["secondes_cpu"], 0)

    def test_difference_de_donnee_dans_deux_scenes_sauvees(self):
        from donjon.monde import Monde, nouveau_monde
        for sujet in ("joueur", "interne"):
            with self.subTest(sujet=sujet), tempfile.TemporaryDirectory() as dossier:
                m = nouveau_monde(7)
                if sujet == "joueur":
                    m.joueur["nom"] = "Autre nom"
                else:
                    m.data["preuve_outil"] = {"valeur": 2}
                chemin = Path(dossier) / "monde.json"
                m.sauver(chemin)
                recharge = Monde.charger(chemin)
                # Aucune physique ni chronique n'a besoin de changer pour détecter data.
                a = {"scenario": "relais", "graine": 7, "plantage": None,
                     "donnees": {"chronique": [], "mesures": {}},
                     "etat_final": outil.empreinte(nouveau_monde(7).data),
                     "minutes": {"0": outil.empreinte(nouveau_monde(7).data)}}
                b = {**a, "etat_final": outil.empreinte(recharge.data),
                     "minutes": {"0": outil.empreinte(recharge.data)}}
                d = outil.comparer_identite([a], [b])
                self.assertEqual(d["parties"], ["etat_final"])
                self.assertEqual(d["minute"], 0)

    def test_premiere_nuit_et_minute_et_chronique_plus_courte(self):
        a = {"scenario": "mine", "graine": 42, "plantage": None, "etat_final": "a",
             "donnees": {"chronique": [{"minute": 2}, {"minute": 9}], "mesures": {}},
             "minutes": {"0": "a", "3": "b", "8": "c"}}
        b = copy.deepcopy(a)
        b["donnees"]["chronique"].pop()
        b["minutes"]["3"] = "autre"
        self.assertEqual(outil.comparer_identite([a], [b])["minute"], 3)
        b.pop("minutes")
        a.pop("minutes")
        self.assertEqual(outil.comparer_identite([a], [b])["minute"], 9)

    def test_mesure_absente_non_inventee_et_violations_visibles(self):
        a = {"scenario": "mine", "graine": 7, "plantage": None, "donnees": {"mesures": {"x": 4}},
             "secondes": 4, "secondes_cpu": 2}
        b = {**a, "plantage": {"message": "refus"}, "donnees": None}
        lignes = {l["mesure"]: l for l in outil.resumer([a], [b])["mine"]}
        self.assertIsNone(lignes["x"]["branche"])
        self.assertEqual(lignes["violations"]["branche"]["moyenne"], 1)

    def test_worktree_nettoye_en_cas_d_erreur_sans_changer_la_branche(self):
        with tempfile.TemporaryDirectory() as dossier:
            racine = Path(dossier)
            def git(*args):
                return outil.git(racine, *args)
            git("init", "-b", "origine")
            (racine / "donnee").write_text("test", encoding="utf-8")
            git("add", "donnee")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "initial")
            with self.assertRaisesRegex(RuntimeError, "délibérée"):
                with outil.worktree_temporaire(racine, "HEAD") as arbre:
                    self.assertTrue((arbre / "donnee").exists())
                    raise RuntimeError("délibérée")
            self.assertFalse(arbre.exists())
            self.assertEqual(git("branch", "--show-current"), "origine")
            self.assertEqual(len(git("worktree", "list").splitlines()), 1)

    def test_plantage_n_est_jamais_une_identite(self):
        a = {"scenario": "mine", "graine": 7, "plantage": {"minute": 3}}
        self.assertEqual(outil.comparer_identite([a], [a])["parties"], ["plantage"])


if __name__ == "__main__":
    unittest.main()
