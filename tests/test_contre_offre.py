"""Conditions dites, retenues et honorées : moteur, parole perçue et recharge."""
import copy
import unittest
from unittest.mock import patch

from donjon.deliberation import tient
from donjon.echanges import executer, servir
from donjon.esprits import lire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import plan_recours
from tests.test_proposer_recours import scene
from tests.test_tensions import recharger


def demande(objet):
    return {"operation": "demander", "cible": "marchand", "outil": objet, "lieu": "", "condition": ""}


def refus(m, objet):
    m.data["connus"].append(objet)
    with patch.object(Monde, "d20", return_value=1):
        lignes = []
        assert not executer(m, "brune", demande(objet), lignes)
    return recharger(m), lignes


def faim():
    m = scene(70)
    # La clé sert au repas en cours, sans garde ni pulsion durable.
    lire(m, "marchand")["besoins"]["faim"] = 75
    lire(m, "marchand")["intention"] = {
        "but": {"type": "manger", "objet": "vivres"}, "motif": "faim",
        "plan": [{"operation": "deverrouiller", "cible": "reserve", "outil": "cle_reserve",
                  "lieu": "", "condition": ""}], "depuis": 0, "attente": 0}
    repas = copy.deepcopy(m.objets["vivres"])
    repas.update(id="repas", nom="ration de voyage", lieu="brune", proprietaire="brune", portions=2)
    m.objets["repas"] = repas
    m.data["connus"].append("repas")
    percevoir_tous(m)
    from donjon.esprits import croire
    for id in ("marchand", "brune"):
        croire(m, id, "repas", "lieu", "brune", "savoir", salle="antichambre", case=[7, 3])
        croire(m, id, "repas", "etat", {"disponible": True}, "savoir")
    return recharger(m)


class ContreOffreTests(unittest.TestCase):
    def test_prix_dit_paye_et_reception_sans_second_jet_deux_biens(self):
        for objet in ("vivres", "cle_reserve"):
            with self.subTest(objet=objet):
                m, lignes = refus(scene(70), objet)
                s = lire(m, "brune")["refus"][-1]
                self.assertIn("Offre de", " ".join(lignes))
                prix = s["contre_offre"]["condition"]["montant"]
                self.assertIn(f"{prix} pièce" + ("s" if prix > 1 else ""), " ".join(lignes))
                avant = copy.deepcopy(m.data["finances_pnj"])
                plan = plan_recours(m, "brune", "faim", None)
                self.assertEqual(plan[-1]["operation"], "acheter")
                lignes = []
                with patch("donjon.echanges.jet_persuasion", side_effect=AssertionError("second jet")):
                    self.assertTrue(executer(m, "brune", plan[-1], lignes))
                m = recharger(m)
                self.assertEqual(m.data["finances_pnj"]["brune"], avant["brune"] - prix)
                self.assertEqual(m.data["finances_pnj"]["marchand"], avant["marchand"] + prix)
                self.assertIn("prend l'argent", " ".join(lignes))
                self.assertFalse(any(s.get("objet") == objet for s in lire(m, "brune")["refus"]))
                if objet == "cle_reserve":
                    self.assertEqual(m.objets[objet]["lieu"], "brune")

    def test_service_necessaire_condition_et_pret_apres_recharge(self):
        m, lignes = refus(faim(), "cle_reserve")
        s = lire(m, "brune")["refus"][-1]
        self.assertEqual(s["contre_offre"]["condition"], {
            "type": "tache", "condition": {"objet": "repas", "servir": "marchand"}})
        self.assertIn("servie", " ".join(lignes))
        plan = plan_recours(m, "brune", "faim", None)
        self.assertEqual(plan[-1]["operation"], "servir")
        lignes = []
        self.assertTrue(servir(m, "brune", "repas", "marchand", lignes))
        m = recharger(m)
        self.assertLess(lire(m, "marchand")["besoins"]["faim"], 75)
        self.assertTrue(lire(m, "brune")["refus"][-1]["condition_tenue"])
        # La preuve n'est pas perdue lorsque la mémoire courte s'efface.
        lire(m, "marchand")["memoire"] = []
        plan = plan_recours(recharger(m), "brune", "faim", None)
        with patch("donjon.echanges.jet_persuasion", side_effect=AssertionError("second jet")):
            self.assertTrue(executer(m, "brune", plan[-1], lignes))
        m = recharger(m)
        self.assertEqual(m.objets["cle_reserve"]["lieu"], "brune")
        self.assertIn("lui remet", " ".join(lignes))
        self.assertTrue(any(p["objet"] == "cle_reserve" and p["a"] == "brune" for p in m.data["permissions"]))

    def test_condition_impossible_retenue_sans_offres_aleatoires_ni_delai(self):
        m, _ = refus(faim(), "cle_reserve")
        m.objets["repas"]["portions"] = 0
        percevoir_tous(m)
        for _ in range(3):
            m = recharger(m)
            self.assertIsNone(plan_recours(m, "brune", "faim", None))
            self.assertTrue(tient(m, "brune", lire(m, "brune")["refus"][-1]))
            m.data["minutes"] += 121
        self.assertEqual(m.objets["cle_reserve"]["lieu"], "marchand")

    def test_autre_cle_meme_condition_et_pas_de_service_anterieur_reutilise(self):
        m = faim()
        cle = copy.deepcopy(m.objets["cle_reserve"])
        cle.update(id="cle_rechange", nom="clé de rechange")
        m.objets["cle_rechange"] = cle
        lire(m, "marchand")["intention"]["plan"][0]["outil"] = "cle_rechange"
        # Un repas d'avant la condition ne peut la remplir, même à la même minute.
        self.assertTrue(servir(m, "brune", "repas", "marchand", []))
        lire(m, "marchand")["besoins"]["faim"] = 75
        m, _ = refus(m, "cle_rechange")
        s = lire(m, "brune")["refus"][-1]
        self.assertFalse(s.get("condition_tenue", False))
        lignes = []
        self.assertTrue(servir(m, "brune", "repas", "marchand", lignes))
        m = recharger(m)
        with patch("donjon.echanges.jet_persuasion", side_effect=AssertionError("second jet")):
            self.assertTrue(executer(m, "brune", demande("cle_rechange"), lignes))
        m = recharger(m)
        self.assertEqual(m.objets["cle_rechange"]["lieu"], "brune")
        self.assertIn("clé de rechange", " ".join(lignes))

    def test_mefiance_et_garde_durable_sans_condition(self):
        for m, objet in ((scene(10), "vivres"), (scene(70, garde=True), "cle_reserve")):
            m, lignes = refus(m, objet)
            self.assertNotIn("contre_offre", lire(m, "brune")["refus"][-1])
            self.assertNotIn("Offre de", " ".join(lignes))

    def test_meme_laps_decoupe_et_recharge_prix(self):
        a, _ = refus(scene(70), "vivres")
        b = recharger(a.copier())
        from tests.test_temps_etat import etat_pnj
        with patch.object(Monde, "d20", return_value=20):
            moteur = Moteur(a)
            moteur.executer(moteur.preparer(proposition("attendre", cible="180")))
            for _ in range(3):
                moteur = Moteur(b)
                moteur.executer(moteur.preparer(proposition("attendre", cible="60")))
                b = recharger(b)
        a, b = recharger(a), recharger(b)
        self.assertEqual(etat_pnj(a), etat_pnj(b))
        self.assertEqual(a.data["finances_pnj"], b.data["finances_pnj"])
        self.assertTrue(any("prend l'argent" in f for j in a.data["journal"] for f in j["faits"]))

    @patch("donjon.agendas._naissances", return_value=None)
    def test_service_poursuivi_par_pnj_meme_laps_decoupe(self, _naissance):
        m = faim()
        m.objets["brune"]["profil"]["besoins"]["devoir"] = {"depart": 80, "derive_heure": 0, "urgence": 60}
        lire(m, "brune")["besoins"].update(faim=0, devoir=80)
        lire(m, "brune")["intention"]["motif"] = "devoir"
        m.objets["reserve"].update(proprietaire="brune", ouverte=True, verrouillee=False)
        m.objets["brune"]["profil"]["pulsions"] = [
            {"besoin": "devoir", "condition": {"objet": "reserve", "verrouillee": True}}]
        lire(m, "brune")["pulsions"] = [False]
        m, _ = refus(m, "cle_reserve")
        a, b = m, recharger(m.copier())
        from tests.test_temps_etat import etat_pnj
        with patch.object(Monde, "d20", return_value=20):
            moteur = Moteur(a)
            moteur.executer(moteur.preparer(proposition("attendre", cible="300")))
            for _ in range(5):
                moteur = Moteur(b)
                moteur.executer(moteur.preparer(proposition("attendre", cible="60")))
                b = recharger(b)
        a, b = recharger(a), recharger(b)
        self.assertEqual(etat_pnj(a), etat_pnj(b))
        self.assertLess(a.objets["repas"]["portions"], 2)
        self.assertTrue(any(s["type"] == "pret" and s.get("objet") == "cle_reserve"
                            for s in lire(a, "marchand")["memoire"]))
        texte = " ".join(f for j in a.data["journal"] for f in j["faits"])
        self.assertIn("donne une part", texte)
        self.assertIn("lui remet", texte)


if __name__ == "__main__":
    unittest.main()
