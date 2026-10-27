"""Contrat de la sonde et de ses alertes, hors appel au modèle."""
import gzip
from contextlib import nullcontext
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import detecter_changements_avis as d
from tools import audit_nuits as audit


def entrees(valeur=0, lieu="salle"):
    return {**{c: valeur for c in d.CATEGORIES_EXTERNES}, "lieu": lieu,
            "_details": {"croyances": {}}, "besoins_continus": {}}


def episode(but, debut, quitte, valeur=0, accompli=False):
    intention = {"but": {"type": but}, "plan": [], "motif": but}
    return {"decision": d._resume_decision(intention), "debut_t": debut * 600,
            "fin_t": debut * 600, "quitte_t": quitte * 600,
            "debut_minute": debut, "quitte_minute": quitte,
            "cause_entree": "minute", "quitte_cause": "minute",
            "debut_entrees": entrees(valeur), "quitte_entrees": entrees(valeur),
            "accompli_au_depart": accompli}


class DetecterAvisTests(unittest.TestCase):
    def analyser(self, eps, **kw):
        return d.analyser_episodes({"pnj": eps}, **kw)

    def test_retour_sans_entree_et_details(self):
        a = self.analyser([episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        self.assertEqual(a["total_non_justifies"], 1)
        self.assertEqual(a["par_pnj"]["pnj"]["non_justifie_strict_complet"], 1)
        self.assertEqual(a["allers_retours"][0]["retour_minute"], 2)

    def test_cycle_accompli_conserve_sa_preuve(self):
        a = self.analyser([episode("pulsion", 0, 1, accompli=True), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        self.assertEqual(a["total_cycles_accomplis"], 1)
        self.assertFalse(a["allers_retours"][0]["non_justifie"])

    def test_garde_interrompue_par_tache_accomplie(self):
        a = self.analyser([episode("garder", 0, 1), episode("pulsion", 1, 2, accompli=True), episode("garder", 2, 3)])
        self.assertEqual(a["comptes"], {"garde_interruption_accomplie": 1})

    def test_entree_changee_ne_certifie_pas_une_raison(self):
        eps = [episode("pulsion", 0, 1), episode("garder", 1, 2, 1), episode("pulsion", 2, 3, 2)]
        eps[0]["quitte_entrees"] = entrees(1)
        a = self.analyser(eps)
        self.assertEqual(a["total_a_expliquer"], 1)
        self.assertEqual(a["total_justifies"], 0)
        self.assertFalse(a["certification_complete"])
        n = {"scenario": "relais", "graine": 7, "heures": 1}
        audit.ajouter_avis(n, a)
        self.assertIn("avis_a_expliquer", {c["code"] for c in audit.analyser_nuit(n)})

    def test_horizon_et_deplacement(self):
        eps = [episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 62, 63)]
        self.assertEqual(self.analyser(eps)["total_non_justifies"], 0)
        eps[-1]["debut_t"] = 2 * 600
        eps[-1]["debut_entrees"]["lieu"] = "ailleurs"
        a = self.analyser(eps)
        self.assertEqual(a["comptes"], {"non_justifie_externe_fixe_seul_deplacement": 1})

    def test_restauration_apres_exception(self):
        choisir = d.deliberation.choisir
        with self.assertRaises(RuntimeError):
            with d.observer_avis():
                raise RuntimeError("essai")
        self.assertIs(d.deliberation.choisir, choisir)

    def test_alerte_et_archive_sans_mesure(self):
        n = {"scenario": "relais", "graine": 7, "heures": 1, "donnees": {"chronique": [], "mesures": {}}}
        self.assertIn("avis_non_mesures", {c["code"] for c in audit.analyser_nuit(n)})
        a = self.analyser([episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        audit.ajouter_avis(n, a)
        self.assertEqual(n["donnees"]["mesures"]["avis_non_justifies"], 1)
        self.assertIn("avis_non_justifie", {c["code"] for c in audit.analyser_nuit(n)})

    def test_captures_reelles(self):
        with gzip.open(Path(__file__).parent / "fixtures/changements_avis/episodes.json.gz", "rt", encoding="utf-8") as f:
            captures = json.load(f)
        for capture in captures:
            with self.subTest(capture=capture["nom"]):
                a = d.analyser_episodes(capture["episodes"])
                self.assertEqual(a["comptes"], capture["comptes"])
                self.assertTrue(capture["chronique"])

    def test_comparateur_mesure_et_alerte(self):
        from tools import comparer_bancs as c
        config = {"empreintes": False, "heures": 5/60, "depart": "fixe",
                  "verifier": False, "joueurs": c.JOUEURS}
        n = c.jouer_nuit(("relais", 7, config))
        self.assertIsNone(n["plantage"])
        self.assertIn("avis_non_justifies", n["donnees"]["mesures"])
        self.assertIn("par_pnj", n["avis"])
        self.assertNotIn("avis_non_mesures", {x["code"] for x in n["constats"]})

    def test_comparateur_identite_conserve_les_alertes(self):
        from tools import comparer_bancs as c
        a = self.analyser([episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        detecteur = c.audit.detecteur_avis()
        config = {"empreintes": True, "heures": 1/60, "depart": "fixe",
                  "verifier": False, "joueurs": c.JOUEURS}
        with patch.object(detecteur, "analyser_episodes", return_value=a):
            n = c.jouer_nuit(("relais", 7, config))
        self.assertIn("avis_non_justifie", {x["code"] for x in n["constats"]})

    def test_audit_ecrit_une_nuit_mesuree(self):
        with tempfile.TemporaryDirectory() as dossier:
            resultat = audit.jouer_nuit(("relais", 7, 5/60, dossier, False, True, "fixe", False))
            with gzip.open(resultat[2], "rt", encoding="utf-8") as f:
                nuit = json.load(f)
        self.assertIsNone(nuit["plantage"])
        self.assertIn("avis_non_justifies", nuit["donnees"]["mesures"])
        self.assertNotIn("avis_non_mesures", {c["code"] for c in audit.analyser_nuit(nuit)})

    def test_monde_et_vue_joueur_identiques_apres_rechargement(self):
        from donjon import banc_pnj
        from donjon.monde import Monde
        from donjon.rendu import regarder
        for scenario in ("relais", "mine"):
            vues = []
            for observer in (nullcontext, d.observer_avis):
                capture = {}
                creer = banc_pnj.creer
                def capturer(*a, **k):
                    capture["monde"] = creer(*a, **k)
                    return capture["monde"]
                with patch.object(banc_pnj, "creer", capturer), observer():
                    banc_pnj.nuit(scenario, 7, 5/60, d.SALLES_JOUEUR[scenario], depart="fixe")
                with tempfile.TemporaryDirectory() as dossier:
                    chemin = Path(dossier) / "monde.json"
                    capture["monde"].sauver(chemin)
                    recharge = Monde.charger(chemin)
                vues.append((recharge.data, regarder(recharge)))
            with self.subTest(scenario=scenario):
                self.assertEqual(vues[0], vues[1])

    def test_identite_reelle_deux_scenarios(self):
        for scenario in ("relais", "mine"):
            with self.subTest(scenario=scenario):
                d.jouer_nuit_sondee(scenario, 7, heures=5/60, verifier_empreinte=True)
