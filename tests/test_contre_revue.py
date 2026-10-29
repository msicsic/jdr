"""La contre-revue juge la fidélité du plan, et une revue illisible ne juge pas la proposition."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from donjon.couverture_action import RapportInvalide, entree, verifier
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition


def detacher_axe(m):
    return Moteur(m).preparer(proposition("detacher", "axe_haut", "couteau", "levier", 18))


class RaccourciTests(unittest.TestCase):
    def test_detacher_ne_prend_pas_la_fixation(self):
        m = nouveau_monde()
        plan = detacher_axe(m)
        # Le plan soumis à la revue ne contient que la libération demandée.
        operations = [e[0] for etape in entree("je fais levier sur l'axe", plan)["plan"]["etapes"]
                      for e in etape["effets_reussite"]]
        self.assertNotIn("transferer", operations)
        with tempfile.TemporaryDirectory() as tmp, patch.object(Monde, "d20", return_value=20):
            Moteur(m).executer(detacher_axe(m))
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            recharge = Monde.charger(chemin)
        self.assertFalse(recharge.objets["axe_haut"].get("attache"))
        self.assertEqual(recharge.objets["axe_haut"]["lieu"], recharge.joueur["salle"])

    def test_detacher_puis_prendre_reste_une_manoeuvre_explicite(self):
        from donjon.operations import etape, sequence
        m = nouveau_monde()
        plan = Moteur(m).preparer(sequence(etape("detacher", "axe_haut", outil="couteau", methode="levier", difficulte=18),
                                           etape("deplacer", "axe_haut", "joueur")))
        with patch.object(Monde, "d20", return_value=20):
            Moteur(m).executer(plan)
        self.assertEqual(m.objets["axe_haut"]["lieu"], "joueur")


class RapportTests(unittest.TestCase):
    def test_un_rapport_mal_forme_n_est_pas_un_refus_de_la_proposition(self):
        with self.assertRaises(RapportInvalide):
            verifier({"conforme": "non", "motif": ""})
        with self.assertRaises(ErreurMonde) as refus:
            verifier({"conforme": False, "motif": "x" * 500, "perimetre": "sens"})
        self.assertNotIsInstance(refus.exception, RapportInvalide)
        self.assertLessEqual(len(str(refus.exception)), 400)
        self.assertTrue(refus.exception.attendu)

    def test_une_revue_illisible_est_redemandee_puis_le_plan_passe(self):
        m = nouveau_monde()
        mj = MJOpenAI("gpt-6-luna")
        traces = []
        mj.observateur = traces.append
        with patch.object(mj, "_appeler_brut", side_effect=[{"conforme": True}, {"avis": "ok"}]) as appel:
            mj._auditer_action("je retire l'axe", detacher_axe(m), m.data["revision"])
        self.assertEqual(appel.call_count, 2)
        self.assertTrue(any("illisible" in t.get("erreur", "") for t in traces))

    def test_une_revue_relue_conforme_suffit(self):
        m = nouveau_monde()
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler_brut", side_effect=[{}, {"conforme": True, "motif": "", "perimetre": "sens"}]) as appel:
            mj._auditer_action("je retire l'axe", detacher_axe(m), m.data["revision"])
        self.assertEqual(appel.call_count, 2)

    def test_une_revue_non_conforme_reste_un_refus(self):
        m = nouveau_monde()
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler_brut", return_value={"conforme": False, "motif": "Prise non demandée.", "perimetre": "sens"}):
            with self.assertRaisesRegex(ErreurMonde, "Prise non demandée"):
                mj._auditer_action("je fais levier", detacher_axe(m), m.data["revision"])


if __name__ == "__main__":
    unittest.main()
