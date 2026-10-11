import copy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon.atelier import nouveau_atelier
from donjon.franchissement import dossier
from donjon.mj import MJOpenAI
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence


def saut(dd=18, outil="perche_1", destination="terrasse"):
    return sequence(etape("deplacer", outil, "joueur"),
                    etape("franchir_obstacle", "mur_atelier", destination, outil, "appui_mobile", dd),
                    justification="Prendre la perche puis tenter un saut avec élan ; risque de retomber au pied du mur.")


class FranchissementTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_atelier()
        self.moteur = Moteur(self.m)

    def executer(self, p, jet=20):
        with patch.object(Monde, "d20", return_value=jet):
            return self.moteur.executer(self.moteur.preparer(p, "MJ"))

    def test_preparation_pure_puis_reussite_et_sauvegarde(self):
        avant = copy.deepcopy(self.m.data)
        p = self.moteur.preparer(saut(), "MJ")
        self.assertEqual(self.m.data, avant)
        self.assertEqual(len(p.plans), 2)
        self.assertEqual((p.stat, p.dd, p.minutes), ("DEX", 18, 2))
        self.assertNotIn("besace", p.resume(self.m))
        resultat = self.executer(saut())
        self.assertNotIn("besace", resultat)
        self.assertEqual(self.m.joueur["salle"], "terrasse")
        self.assertEqual(self.m.objets["perche_1"]["lieu"], "cour")
        self.assertFalse(self.m.objets["perche_1"].get("installation"))
        self.assertEqual(self.m.data["salles"]["terrasse"]["sorties"], {})
        self.assertEqual(len(self.m.data["journal"][-1]["etapes"]), 2)
        self.assertFalse(any(o.get("assemblage") for o in self.m.objets.values()))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "saut.json"
            self.m.sauver(chemin)
            self.assertEqual(Monde.charger(chemin).data, self.m.data)

    def test_echec_et_critique_couts_et_arbitrage_memorise(self):
        self.executer(saut(19), 2)
        self.assertEqual(self.m.joueur["salle"], "cour")
        self.assertEqual(self.m.joueur["pv"], 15)
        self.assertEqual(self.m.objets["perche_1"]["integrite"], 10)
        self.assertEqual(self.m.objets["perche_1"]["lieu"], "cour")
        self.assertEqual(self.m.data["minutes"], 2)
        p = self.moteur.preparer(saut(16, outil="perche_2"))
        self.assertEqual(p.dd, 19)  # perche équivalente et DD suggéré différent
        self.executer(saut(16, outil="perche_2"), 1)
        self.assertEqual(self.m.objets["perche_2"]["integrite"], 9)
        self.assertEqual(self.m.joueur["pv"], 12)

    def test_refus_physiques_avant_prise_sans_mutation(self):
        for champ, valeur in (("hauteur_cm", 400), ("elan_cm", 100), ("sol_stable", False), ("reception_stable", False)):
            with self.subTest(champ=champ):
                m = nouveau_atelier()
                m.objets["mur_atelier"]["appui_vertical"][champ] = valeur
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde):
                    Moteur(m).preparer(saut())
                self.assertEqual(m.data, avant)
        for champ, valeur in (("longueur_cm", 100), ("charge_jeu_kg", 50), ("proprietaire", "marchand")):
            m = nouveau_atelier()
            m.objets["perche_1"][champ] = valeur
            with self.assertRaises(ErreurMonde):
                Moteur(m).preparer(saut())

    def test_pas_de_teleportation_ni_outil_imaginaire(self):
        for p in (saut(destination="crypte"), saut(outil="couteau"), saut(dd=1)):
            with self.assertRaises(ErreurMonde):
                self.moteur.preparer(p)
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(sequence(saut()["etapes"][1]))

    def test_inconnue_non_inventee_et_migration_respecte_faits(self):
        del self.m.objets["mur_atelier"]["appui_vertical"]["elan_cm"]
        with self.assertRaisesRegex(ErreurMonde, "elan_cm"):
            self.moteur.preparer(saut())
        self.assertIn("elan_cm", dossier(self.m)["possibilites"][0]["obstacle_physique_ou_inconnue"])
        self.m.data.pop("franchissements_version")
        self.m.objets["mur_atelier"]["appui_vertical"]["elan_cm"] = 100
        m = Monde(copy.deepcopy(self.m.data))
        self.assertEqual(m.objets["mur_atelier"]["appui_vertical"]["elan_cm"], 100)
        self.assertNotIn("Fabriquer", m.data["scenario"]["objectif"])

    def test_refus_du_llm_reexamine_une_seule_fois(self):
        refus = {"mode": "action", "texte": "", "faits": [],
                 "proposition": proposition("impossible", justification="La solution prévue est l'échelle.")}
        reponse = {"mode": "action", "texte": "", "faits": ["franchissements"], "proposition": saut()}
        with patch.object(MJOpenAI, "_appeler", side_effect=[refus, reponse]) as api:
            r = MJOpenAI().echanger(self.m, "Je prends une perche pour franchir le mur")
        self.assertEqual(api.call_count, 2)
        self.assertIn("retour_moteur", api.call_args.args[1]["faits"])
        self.assertEqual(r["proposition"], saut())
        self.assertEqual(self.m.data["revision"], 0)
        with patch.object(MJOpenAI, "_appeler", return_value=refus) as api:
            r = MJOpenAI().echanger(self.m, "Je vole par-dessus le mur")
        self.assertEqual(api.call_count, 2)
        self.assertEqual(r["proposition"]["action"], "impossible")

    def test_question_ne_declenche_ni_prise_ni_saut(self):
        r = {"mode": "action", "texte": "", "faits": ["franchissements"], "proposition": saut()}
        with patch.object(MJOpenAI, "_appeler", return_value=r) as api:
            reponse = MJOpenAI().echanger(self.m, "Puis-je sauter avec la perche ?")
        self.assertEqual(api.call_count, 2)
        self.assertEqual(reponse["mode"], "dialogue")
        self.assertEqual(self.m.data["revision"], 0)
        self.assertEqual(self.m.objets["perche_1"]["lieu"], "cour")


if __name__ == "__main__":
    unittest.main()
