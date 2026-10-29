"""Contre-épreuves de l'oracle fermé, sans importer le jeu ni appeler Luna."""
import copy
import json
from pathlib import Path
import unittest

from tools.oracle_g1 import (classer, compilations, empreinte, lire, observation,
                             rapport, satisfait, seuils)

DATA = Path(__file__).parent / "data"


class OracleG1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = lire(DATA / "oracle_g1.json")
        cls.cas = {c["id"]: c for c in cls.oracle["cas"]}
        cls.extraits = {(e["campagne"], e["id"]): e["tour"]
                        for e in lire(DATA / "oracle_g1_extraits.json")}

    def tour(self, campagne, cle):
        return copy.deepcopy(self.extraits[campagne, cle])

    def contrat(self, nom, cle=None):
        c = next(c for c in self.oracle["obligatoires"] if c["nom"] == nom)
        return c["contrats"][cle] if cle else c["contrat"]

    def test_corpus_fixe_sans_reduire_le_denominateur(self):
        self.assertEqual(len(self.cas), 91)
        self.assertEqual(sum(c["modele"] for c in self.cas.values()), 30)
        self.assertEqual(len(self.oracle["sources"]), 36)
        self.assertEqual(sum(self.oracle["familles_reference"].values()), 27)
        self.assertEqual({c["nom"] for c in self.oracle["obligatoires"]},
                         {"prix", "avis", "part_contre_pieces", "question_mj_sans_execution",
                          "attente_vol", "perche_puis_saut"})

    def test_tous_les_extraits_sont_des_preuves_connues(self):
        for (campagne, cle), t in self.extraits.items():
            if cle in self.cas:
                with self.subTest(campagne=campagne, cle=cle):
                    self.assertTrue(classer(t, self.cas[cle])["preuve_connue"])

    def test_proposition_fidele_et_faux_refus_de_revue_distincts(self):
        t = self.tour("230e7b3", "crypte/9")
        c = classer(t, self.cas["crypte/9"])
        self.assertTrue(c["proposition_fidele"])
        self.assertFalse(c["intention_servie"])
        self.assertEqual(c["execution"], "non_execute")
        self.assertEqual(c["admission"], "refuse")

    def test_admission_n_est_pas_execution(self):
        t = self.tour("230e7b3", "crypte/10")
        c = classer(t, self.cas["crypte/10"])
        self.assertTrue(c["admission_premier_coup"])
        self.assertTrue(c["proposition_fidele"])
        self.assertEqual(c["consentement"], "attente")
        self.assertEqual(c["execution"], "non_execute")
        t["refus"] = ["Autre refus"]
        self.assertFalse(classer(t, self.cas["crypte/10"])["admission_premier_coup"])

    def test_refus_fidele_et_attente_omise_ne_se_confondent_pas(self):
        for campagne, fidele in [("230e7b3", True), ("311", False)]:
            t = self.tour(campagne, "crypte/26")
            c = classer(t, self.cas["crypte/26"])
            self.assertIs(c["intention_servie"], fidele)
            self.assertEqual(c["execution"], "refus")
            self.assertIs(satisfait(observation(t), self.contrat("attente_vol", "crypte/26")), fidele)

    def test_prix_n_est_pas_propos_ni_negociation(self):
        rule = self.contrat("prix", "crypte/24")
        good = {"candidats": [{"mode": "conversation_pnj", "proposition": {
            "operation": "prix", "personnage": "marchand", "mission": "anneau_veilleur"}}]}
        self.assertTrue(satisfait(good, rule))
        for bad in ["negocier", "propos", "accepter"]:
            with self.subTest(operation=bad):
                fake = copy.deepcopy(good)
                fake["candidats"][0]["proposition"]["operation"] = bad
                self.assertFalse(satisfait(fake, rule))

    def test_avis_adresse_negation_et_sujet(self):
        t = self.tour("230e7b3", "avis-joueur/2")
        obs = observation(t)
        rule = self.contrat("avis", "avis-joueur/2")
        self.assertTrue(satisfait(obs, rule))
        for path, value in [(["personnage"], "marchand"),
                            (["contenu", 0, "valeur"], "oui"),
                            (["contenu", 0, "sujet"], "galerie")]:
            fake = copy.deepcopy(obs)
            target = fake["candidats"][-1]["proposition"]
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            self.assertFalse(satisfait(fake, rule))

    def test_part_et_montant_ne_sont_pas_un_objet_entier(self):
        obs = observation(self.tour("311", "soir-appel/5"))
        rule = self.contrat("part_contre_pieces", "soir-appel/5")
        self.assertTrue(satisfait(obs, rule))
        for field, value in [("type", "objet"), ("objet", "brasero")]:
            fake = copy.deepcopy(obs)
            fake["candidats"][-1]["proposition"]["contenu"][0]["demande"][field] = value
            self.assertFalse(satisfait(fake, rule))
        obs["candidats"][-1]["proposition"]["contenu"][0]["contrepartie"]["montant"] = 4
        self.assertFalse(satisfait(obs, rule))

    def test_question_mj_sans_parole_creee(self):
        for campagne, fidele in [("311", True), ("304", False)]:
            t = self.tour(campagne, "crypte/41")
            c = classer(t, self.cas["crypte/41"])
            self.assertIs(c["intention_servie"], fidele)
            self.assertIs(satisfait(observation(t), self.contrat(
                "question_mj_sans_execution", "crypte/41")), fidele)
        self.assertEqual(classer(self.tour("304", "crypte/41"),
                                 self.cas["crypte/41"])["execution"], "parole")

    def test_perche_puis_saut_ordre_outil_et_etat_recharge(self):
        t = self.tour("c9459ce", "atelier/13")
        charge = compilations(t)[-1]
        rule = self.contrat("perche_puis_saut")
        self.assertTrue(satisfait(charge, rule))
        self.assertNotIn("perche_3", t["etat"]["porte"])
        for action in ("inverser", "supprimer", "substituer"):
            fake = copy.deepcopy(charge)
            etapes = fake["proposition"]["etapes"]
            if action == "inverser":
                etapes.reverse()
            elif action == "supprimer":
                etapes.pop(0)
            else:
                etapes[1]["outil"] = "perche_1"
            self.assertFalse(satisfait(fake, rule))

    def test_cinq_issues_nouvelles_ne_sont_jamais_creditees(self):
        # Bonne charge, autre exécution/refus/confirmation/texte/état : la preuve
        # entière change ; aucun jugement de sens hérité par accident.
        original = self.tour("230e7b3", "crypte/10")
        for champ, valeur in [("texte", "Action exécutée"), ("refus", ["refus"]),
                              ("etat", {"porte": ["axe_haut"]}),
                              ("propositions", [{"action": "prendre"}]), ("saisie", "autre")]:
            fake = copy.deepcopy(original)
            fake[champ] = valeur
            if champ == "saisie":
                with self.assertRaises(ValueError):
                    classer(fake, self.cas["crypte/10"])
            else:
                c = classer(fake, self.cas["crypte/10"])
                self.assertFalse(c["preuve_connue"])
                self.assertEqual(c["intention_servie"], "non_evalue")
                self.assertEqual(c["consentement"], "non_evalue")

    def test_texte_propose_n_est_pas_texte_vu(self):
        t = self.tour("311", "crypte/41")
        c = classer(t, self.cas["crypte/41"])
        self.assertEqual(c["texte_vu"], t["texte"])
        self.assertNotEqual(c["texte_vu"], c["candidats"][0].get("texte"))

    def test_seuils_ne_compensent_pas_une_famille_perdue(self):
        m = {"admissions": 30, "fideles_premier": 30, "fideles_finales": 30,
             "abandons": 0, "appels_par_tour": 1, "tours_sans_compilation": 0}
        s = seuils(m, {"son": 0}, {"son": 1}, {"prix": False}, 0)
        self.assertFalse(s["I"]["aucune_famille_perdue"])
        self.assertFalse(s["I"]["zero_substitution_obligatoire"])
        self.assertIsNone(s["F"]["detail_autre_support_recharges"])
        self.assertIsNone(s["V"]["latence_confirmation_effet_mediane_p95"])
        self.assertFalse(s["validation_complete"])

    def test_corpus_incomplet_ne_reduit_pas_le_denominateur(self):
        with self.assertRaisesRegex(ValueError, "Corpus différent"):
            rapport([], self.oracle)

    def test_sceau_deterministe_sensible_au_rendu_et_a_la_recharge(self):
        obs = observation(self.tour("230e7b3", "crypte/10"))
        self.assertEqual(empreinte(obs), empreinte(json.loads(json.dumps(obs))))
        changed = copy.deepcopy(obs)
        changed["etat_recharge"]["porte"].append("axe_haut")
        self.assertNotEqual(empreinte(obs), empreinte(changed))


if __name__ == "__main__":
    unittest.main()
