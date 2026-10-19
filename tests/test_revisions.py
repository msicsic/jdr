"""Moins de révisions : un obstacle qu'aucune proposition ne lève s'explique sans redemander,
et la contre-revue juge l'état, pas la forme d'un geste."""
import unittest
from unittest.mock import patch

from donjon.couverture_action import entree as entree_couverture
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from tests.test_tensions import placer, relais


class HorsDePorteeTests(unittest.TestCase):
    def test_une_cible_trop_loin_s_explique_sans_seconde_proposition(self):
        m = relais()
        m.joueur.update(salle="echoppe", position=[3, 5])
        # Placement d'auteur : les fagots sont au fond de la conduite, hors de portée.
        placer(m, "bois", "echoppe", (5, 2))
        m.objets["bois"]["proprietaire"] = "joueur"
        alimenter = {"mode": "action", "texte": "", "faits": [],
                     "proposition": sequence(etape("alimenter", "brasero", outil="bois"))}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler", side_effect=[alimenter, ErreurMonde("explication indisponible")]) as appel:
            reponse = mj._echanger_prepare(m, "je mets du bois dans le brasero")
        # Une proposition, puis directement l'explication : pas de correction demandée.
        self.assertEqual(appel.call_count, 2)
        retour = appel.call_args_list[1].args[1]["faits"]["retour_moteur"]
        self.assertIn("propositions_refusees", retour)
        self.assertIn("Approche-toi", retour["propositions_refusees"][0][1])
        self.assertTrue(reponse["_validation_refusee"])


class ContreRevueTests(unittest.TestCase):
    def test_un_sifflement_ne_prete_pas_d_intention(self):
        m = relais()
        plan = Moteur(m).preparer(sequence(etape("emettre_son", "joueur", methode="sifflement")))
        self.assertEqual(plan.plans[0].titre, "Siffler.")

    def test_la_contre_revue_sait_qu_un_geste_improvise_porte_sur_ses_cibles(self):
        m = relais()
        m.joueur.update(salle="echoppe", position=[3, 5])
        coup = {"action": "improviser", "intention": "Donner un coup de pied dans le brasero.",
                "cibles": ["brasero"], "outil": "", "approche": "effort", "stat": "", "difficulte": 0,
                "minutes": 0, "bruit": 1,
                "reussite": {"recit": "Tu frappes le brasero du pied.", "effets": [
                    {"operation": "son", "cible": "joueur", "destination": "", "texte": "corps_bref", "valeur": 1}]},
                "echec": {"recit": "", "effets": []}}
        plan = Moteur(m).preparer(coup)
        geste = entree_couverture("je donne un coup de pied dans le brasero", plan)["plan"]["geste_improvise"]
        self.assertEqual((geste["approche"], geste["cibles"]), ("effort", ["brasero"]))

    def test_un_geste_d_effort_exige_la_portee(self):
        from donjon.proximite import HorsDePortee
        m = relais()
        m.joueur.update(salle="echoppe", position=[5, 2])
        coup = {"action": "improviser", "intention": "Donner un coup de pied dans le brasero.",
                "cibles": ["brasero"], "outil": "", "approche": "effort", "stat": "", "difficulte": 0,
                "minutes": 0, "bruit": 1,
                "reussite": {"recit": "Tu frappes le brasero du pied.", "effets": []},
                "echec": {"recit": "", "effets": []}}
        with self.assertRaises(HorsDePortee):
            Moteur(m).preparer(coup)


if __name__ == "__main__":
    unittest.main()
