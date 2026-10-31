"""Identité du monde complet, appariement, mesures et propriété du worktree."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import comparer_bancs as outil


class ComparerBancsTests(unittest.TestCase):
    def test_observateur_courant_charge_sans_vue_dans_la_reference(self):
        import importlib.util
        from types import ModuleType
        from unittest.mock import patch
        from donjon.banc_pnj import creer
        from donjon.esprits import memoriser

        monde = creer('relais', 7, 'fixe')
        memoriser(monde, 'marchand', {'type': 'examen', 'salle': 'antichambre',
                                    'nature': 'pas', 'case': None})
        avant = copy.deepcopy(monde.data)
        # Une référence ancienne ne livre pas episodes. L'observation courante
        # emploie sa propre porte, dont les imports lisent toujours ce moteur.
        racine = Path(__file__).resolve().parents[1]
        with patch.dict(sys.modules, {'donjon.memoire': ModuleType('donjon.memoire')}):
            for nom, fichier in (('donjon._recit_test', 'donjon/recit_pnj.py'),
                                 ('_detecteur_test', 'tools/detecter_changements_avis.py')):
                spec = importlib.util.spec_from_file_location(nom, racine / fichier)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            vue = module.episodes(monde, 'marchand')
            self.assertEqual(vue[-1]['type'], 'examen')
            vue[-1].clear()
            # S1f : la même porte d'observation lit les localisations d'une
            # référence antérieure à faits_connus, sans dépendre de son API.
            faits = module.faits_connus(monde, 'marchand')
            self.assertEqual(faits, avant['esprits']['marchand']['croyances'])
            for attributs in faits.values():
                attributs.clear()
        self.assertEqual(monde.data, avant)

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
