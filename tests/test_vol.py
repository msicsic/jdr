import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.commandes import analyser
from donjon.dialogues import preparer_conversation
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import carte, fiche
from donjon.vol import mefiance


class VolTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        self.m.joueur["salle"] = "echoppe"
        self.moteur = Moteur(self.m)

    def voler(self, jet, cible="crochets", methode="finesse"):
        p = self.moteur.preparer(proposition("voler", cible, methode=methode))
        with patch.object(Monde, "d20", return_value=jet):
            return self.moteur.executer(p)

    def test_succes_sans_paiement_ni_soupcon_carte_et_besace(self):
        plan = self.moteur.preparer(proposition("voler", "crochets", methode="finesse"))
        self.assertEqual((plan.stat, plan.dd, plan.minutes), ("DEX", 12, 3))
        self.assertIn("méfiants", plan.resume(self.m))
        self.assertIn("la trousse", carte(self.m))
        self.assertIn("Tu dérobes la trousse", self.voler(20))
        self.assertEqual(self.m.joueur["or"], 24)
        self.assertEqual(self.m.data["finances_pnj"]["marchand"], 50)
        self.assertEqual(self.m.objets["crochets"]["lieu"], "joueur")
        self.assertFalse(self.m.objets["crochets"]["en_vente"])
        self.assertEqual(self.m.objets["crochets"]["vole_a"], "marchand")
        self.assertEqual(mefiance(self.m, "marchand"), 0)
        self.assertNotIn("la trousse", carte(self.m))
        self.assertIn("trousse", fiche(self.m))
        self.assertEqual(self.m.data["minutes"], 3)
        self.moteur.executer(self.moteur.preparer(analyser(self.m, "poser crochets")))
        self.moteur.executer(self.moteur.preparer(analyser(self.m, "prendre crochets")))
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("voler", "crochets"))

    def test_echec_remarque_memoire_persistante_et_refus_vente(self):
        for jet in (1, 2):
            with self.subTest(jet=jet):
                self.setUp()
                texte = self.voler(jet)
                self.assertIn("te surprend", texte)
                self.assertEqual(self.m.objets["crochets"]["lieu"], "echoppe")
                self.assertTrue(self.m.objets["crochets"]["en_vente"])
                from donjon.signes import emotion
                self.assertEqual(emotion(self.m, "marchand")["contre"], "joueur")
                from donjon.relations import envers
                self.assertEqual(envers(self.m, "marchand", "joueur")["motifs"][-1]["objet"], "crochets")
                self.assertEqual(self.moteur.preparer(proposition("voler", "crochets", methode="finesse")).dd, 14)
                self.moteur.executer(self.moteur.preparer(proposition("attendre")))
                with tempfile.TemporaryDirectory() as tmp:
                    p = Path(tmp) / "partie.json"
                    self.m.sauver(p)
                    m = Monde.charger(p)
                self.assertNotIn("humeur", m.objets["marchand"])
                self.assertEqual(m.data["relations_pnj"]["marchand"]["vols_surpris"], 1)
                self.assertNotIn("relation_joueur", m.contexte()["interlocuteurs"]["marchand"])
                with self.assertRaisesRegex(ErreurMonde, "refuse"):
                    Moteur(m).preparer(proposition("acheter", "marteau"))
                self.assertEqual(m.joueur["or"], 24)

    def test_recompense_convenue_reste_due_apres_vol_surpris(self):
        p = {"personnage": "marchand", "sujet": "Récompense", "operation": "proposer", "mission": "anneau_veilleur", "montant_demande": 0}
        for op in ("proposer", "accepter"):
            m, _ = preparer_conversation(self.m, {**p, "operation": op})
            self.m.data = m.data
        self.voler(1)
        self.m.objets["anneau"].update(lieu="joueur", proprietaire="marchand", vole_a="marchand", vole_par="joueur")
        self.moteur.executer(self.moteur.preparer(proposition("remettre", "anneau")))
        self.assertEqual(self.m.joueur["or"], 44)
        self.assertNotIn("vole_par", self.m.objets["anneau"])
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("prendre", "anneau"))

    def test_pas_de_vol_par_prendre_ni_de_vol_impossible(self):
        self.m.objets["coffre"]["proprietaire"] = "marchand"
        for p in (proposition("prendre", "crochets"), proposition("voler", "couteau"),
                  proposition("voler", "cle"), proposition("voler", "coffre"),
                  proposition("voler", "crochets", "couteau"), proposition("voler", "crochets", methode="levier")):
            avant = copy.deepcopy(self.m.data)
            with self.assertRaises(ErreurMonde):
                self.moteur.preparer(p)
            self.assertEqual(self.m.data, avant)
        self.m.joueur["capacite"] = self.m.charge()
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("voler", "crochets"))

    def test_temoins_locaux_et_absence_sans_jet(self):
        self.m.objets["marchand"]["lieu"] = "antichambre"
        with patch.object(Monde, "d20", side_effect=AssertionError("Aucun témoin")):
            self.moteur.executer(self.moteur.preparer(proposition("voler", "crochets")))
        self.assertEqual(self.m.data["relations_pnj"]["marchand"]["vols_surpris"], 0)
        self.assertEqual(self.m.objets["crochets"]["lieu"], "joueur")

    def test_autre_temoin_et_propriete_heritee(self):
        self.m.objets["mira"] = objet("mira", "Mira", "personnage", "echoppe", vigilance=18)
        self.m.objets["sac"] = objet("sac", "sac", "contenant", "echoppe", ouverte=True, verrouillee=False, proprietaire="mira")
        self.m.objets["broche"] = objet("broche", "broche", "tresor", "sac", mobile=True, masse=.1)
        self.m.data = self.m.copier().data
        self.assertEqual(self.moteur.preparer(proposition("voler", "broche")).dd, 18)
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("prendre", "broche"))
        self.voler(1, "broche")
        self.assertEqual(self.m.data["relations_pnj"]["mira"]["vols_surpris"], 1)
        self.assertEqual(self.m.data["relations_pnj"]["marchand"]["vols_surpris"], 1)

    def test_difficulte_fixee_et_plan_perime(self):
        p = proposition("voler", "crochets", methode="finesse", difficulte=1)
        plan = self.moteur.preparer(p)
        self.assertEqual(plan.dd, 12)
        self.moteur.executer(self.moteur.preparer(proposition("attendre")))
        with self.assertRaises(ErreurMonde):
            self.moteur.executer(plan)
        self.m.data["bruit"] = 6
        self.assertEqual(self.moteur.preparer(p).dd, 14)

    def test_migration_ne_reinitialise_pas_relations(self):
        self.voler(1)
        avant = copy.deepcopy(self.m.data)
        self.assertEqual(self.m.copier().data, avant)
        avant.pop("relations_pnj")
        avant["objets"]["marchand"].pop("vigilance")
        m = Monde(avant)
        self.assertEqual(m.data["minutes"], self.m.data["minutes"])
        self.assertEqual(m.joueur, self.m.joueur)
        self.assertEqual(m.objets["marchand"]["vigilance"], 14)
