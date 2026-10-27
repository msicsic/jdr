"""Contrat de la sonde et de ses alertes, hors appel au modèle."""
import gzip
from collections import Counter
import copy
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
        self.assertEqual(a["par_pnj"]["pnj"]["repetition_sans_entree_nouvelle"], 1)
        self.assertEqual(a["allers_retours"][0]["retour_minute"], 2)

    def test_cycle_accompli_conserve_sa_preuve(self):
        a = self.analyser([episode("pulsion", 0, 1, accompli=True), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        self.assertEqual(a["total_cycles_accomplis"], 1)
        self.assertFalse(a["allers_retours"][0]["non_justifie"])

    def test_fin_intermediaire_seule_ne_prouve_pas_un_progres(self):
        for but in ("garder", "autre"):
            a = self.analyser([episode(but, 0, 1), episode("pulsion", 1, 2, accompli=True), episode(but, 2, 3)])
            self.assertEqual(a["comptes"], {"entree_nouvelle_a_expliquer": 1})

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
        self.assertEqual(a["comptes"], {"repetition_sans_entree_nouvelle": 1})

    def test_restauration_apres_exception(self):
        choisir = d.deliberation.choisir
        with self.assertRaises(RuntimeError):
            with d.observer_avis():
                raise RuntimeError("essai")
        self.assertIs(d.deliberation.choisir, choisir)

    def test_paliers_observes_stricts_et_regle_unique(self):
        for palier, attendu in ((12, "preemption_palier_superieur"),
                                (13, "repetition_sans_entree_nouvelle"),
                                (14, "repetition_sans_entree_nouvelle")):
            eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
            eps[0]["palier"], eps[1]["palier"] = 13, palier
            eps[1]["faits"] = [{"cle": eps[0]["decision"]["cle"], "t": 900,
                                "autrui": True, "progression": True}]
            # La préemption prime ; sinon la satisfaction observée prime sur le progrès.
            if palier == 12:
                self.assertEqual(self.analyser(eps)["comptes"], {attendu: 1})
            else:
                self.assertEqual(self.analyser(eps)["comptes"], {"satisfaction_ou_dementi_autrui": 1})
                eps[1]["faits"] = []
                self.assertEqual(self.analyser(eps)["comptes"], {attendu: 1})

    def test_progression_avec_preuve_et_derive_separee(self):
        eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
        eps[1]["faits"] = [{"cle": eps[0]["decision"]["cle"], "t": 900,
                            "progression": True, "preuve": "etape_executee"}]
        self.assertEqual(self.analyser(eps)["comptes"], {"progression_reelle": 1})
        self.assertEqual(self.analyser(eps)["total_derives_ouvertes"], 0)
        a = self.analyser([episode("a", 0, 1), episode("b", 1, 2), episode("c", 2, 3)])
        self.assertEqual(a["total_derives_ouvertes"], 1)
        self.assertEqual(a["total_non_justifies"], 0)

    def test_sonde_attribue_une_fin_survenue_pendant_action_autrui(self):
        sonde = d.SondeAvis()
        eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
        sonde.episodes["aidant"] = eps[:2]
        cle = eps[0]["decision"]["cle"]
        from types import SimpleNamespace
        monde = SimpleNamespace(data={"minutes": 1})
        with patch.object(d, "instant", return_value=900), \
             patch.object(d, "_est_accompli", return_value=False):
            avant = sonde.accomplissements(monde)
        with patch.object(d, "instant", return_value=900), \
             patch.object(d, "_est_accompli", side_effect=lambda m, qui, dec, minute: dec["cle"] == cle):
            sonde.constater(monde, "tiers", avant)
        sonde.episodes["aidant"].append(eps[2])
        a = sonde.analyser()
        self.assertEqual(a["comptes"], {"satisfaction_ou_dementi_autrui": 1})
        self.assertEqual(a["allers_retours"][0]["preuves"][0]["acteur"], "tiers")

    def test_etat_paye_perdu_sans_duree_ne_viole_pas_un_contrat(self):
        from types import SimpleNamespace
        sonde = d.SondeAvis()
        sonde.episodes["payeur"] = []
        souvenir = {"type": "tache_payee", "a": "artisan", "minute": 0,
                    "condition": {"objet": "bien", "verrouillee": True}, "prix": 2}
        monde = SimpleNamespace(objets={"bien": {"verrouillee": False}}, data={"minutes": 0})
        with patch.object(d, "lire", return_value={"memoire": [souvenir]}), patch.object(d, "instant", return_value=600):
            sonde.relever_services(monde)
            monde.objets["bien"]["verrouillee"] = True
            sonde.relever_services(monde)
            souvenir.clear()  # Le souvenir borné disparaît, l'observation demeure.
            monde.objets["bien"]["verrouillee"] = False
            sonde.relever_services(monde)
        a = sonde.analyser()
        self.assertEqual(a["total_services_etat_perdu"], 1)
        self.assertFalse(a["services_etat_perdu"][0]["violation"])
        self.assertEqual(a["total_non_justifies"], 0)
        nuit = {"scenario": "synthese", "graine": 0, "heures": 1}
        audit.ajouter_avis(nuit, a)
        constats = audit.analyser_nuit(nuit)
        self.assertEqual([c["niveau"] for c in constats], ["observation"])

    def test_torche_hameau_1985_service_perdu(self):
        nuit = d.jouer_nuit_sondee("crue_hameau", 1985, heures=9/60, verifier_empreinte=True)
        pertes = [s for s in nuit["analyse"]["services_etat_perdu"] if s["prestataire"] == "brune"]
        self.assertTrue(pertes)
        self.assertTrue(all(s["reussite_t"] < s["perte_t"] < 9 * d.MINUTE for s in pertes))
        self.assertTrue(all(not s["violation"] for s in pertes))

    def test_torche_historique_217_rechargee(self):
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        with gzip.open(Path(__file__).parent / "fixtures/changements_avis/service-217.json.gz", "rt", encoding="utf8") as f:
            capture = json.load(f)
        sonde = d.SondeAvis()
        # Le paiement observé appartient au fil d'audit, même si le souvenir
        # a déjà disparu des deux captures de fin de service.
        contrat = copy.deepcopy(capture["services"][0])
        contrat.update(reussite_t=None, perte_t=None)
        sonde.services["contrat_capture"] = contrat
        for phase in ("reussite", "perte"):
            monde = Monde(copy.deepcopy(capture["etats"][phase]))
            with tempfile.TemporaryDirectory() as dossier:
                chemin = Path(dossier) / "monde.json"
                monde.sauver(chemin)
                recharge = Monde.charger(chemin)
            self.assertEqual(monde.data, recharge.data)
            self.assertEqual(regarder(monde), regarder(recharge))
            self.assertEqual(scene_percue(monde), scene_percue(recharge))
            sonde.relever_services(recharge)
        pertes = sonde.analyser()["services_etat_perdu"]
        self.assertEqual(len(pertes), 1)
        self.assertEqual(pertes[0]["reussite_t"], capture["services"][0]["reussite_t"])
        self.assertEqual(pertes[0]["perte_t"], capture["services"][0]["perte_t"])
        self.assertLess(pertes[0]["reussite_t"], pertes[0]["perte_t"])
        self.assertEqual(pertes[0]["reussite_t"] // d.MINUTE, 7)
        self.assertEqual(pertes[0]["perte_t"] // d.MINUTE, 8)
        self.assertFalse(pertes[0]["violation"])

    def test_alerte_et_archive_sans_mesure(self):
        n = {"scenario": "relais", "graine": 7, "heures": 1, "donnees": {"chronique": [], "mesures": {}}}
        self.assertIn("avis_non_mesures", {c["code"] for c in audit.analyser_nuit(n)})
        a = self.analyser([episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        audit.ajouter_avis(n, a)
        self.assertEqual(n["donnees"]["mesures"]["avis_non_justifies"], 1)
        self.assertNotIn("avis_services_etat_perdu", n["donnees"]["mesures"])
        self.assertIn("avis_non_justifie", {c["code"] for c in audit.analyser_nuit(n)})

    def test_captures_reelles(self):
        with gzip.open(Path(__file__).parent / "fixtures/changements_avis/episodes.json.gz", "rt", encoding="utf-8") as f:
            captures = json.load(f)
        for capture in captures:
            with self.subTest(capture=capture["nom"]):
                a = d.analyser_episodes(capture["episodes"])
                self.assertEqual(dict(Counter(r["classe_199"] for r in a["allers_retours"])), capture["comptes"])
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
