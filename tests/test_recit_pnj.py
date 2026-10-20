"""Récit du banc sans joueur : il raconte sans rien changer au monde."""
import unittest

from donjon.banc_pnj import creer, executer
from donjon.francais import de
from donjon.recit_pnj import Recit, but_en_mots


class RecitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temoin = creer("relais", 7)
        cls.chronique_temoin, cls.mesures_temoin = executer(cls.temoin, 240)
        cls.monde = creer("relais", 7)
        cls.recit = Recit(cls.monde)
        cls.chronique, cls.mesures = executer(cls.monde, 240, cls.recit)
        cls.texte = cls.recit.texte(cls.monde, cls.chronique)

    def test_observer_ne_change_rien(self):
        self.assertEqual(self.chronique, self.chronique_temoin)
        self.assertEqual(self.mesures, self.mesures_temoin)
        self.assertEqual(self.monde.data["esprits"], self.temoin.data["esprits"])

    def test_buts_et_gestes_de_chacun(self):
        # Brune affamée : son but, et les gestes faits pour lui, dans l'ordre de la nuit.
        buts = [ep["but"]["type"] for ep in self.recit.episodes["brune"]]
        self.assertIn("manger", buts)
        self.assertIn("== Brune, batelière évacuée ==", self.texte)
        self.assertIn("crochète la serrure de la réserve de vivres", self.texte)
        self.assertGreater(self.recit.urgence["brune"]["faim"], 0)

    def test_entre_eux_et_temoins(self):
        self.assertIn("== Entre eux ==", self.texte)
        self.assertIn("Ilse voit Brune crocheter la réserve de vivres", self.texte)
        self.assertIn("se méfie de Brune", self.texte)

    def test_rondes_resumees(self):
        self.assertIn("Rondes :", self.texte)
        self.assertNotIn("ronde : ", self.texte)

    def test_mots(self):
        self.assertEqual(de("Aubin"), "d'Aubin")
        self.assertEqual(de("Gorm"), "de Gorm")
        self.assertEqual(but_en_mots(self.monde, {"type": "chaleur", "objet": "brasero"}), "se chauffer au brasero")
        self.assertEqual(but_en_mots(self.monde, {"type": "part", "objet": "planches", "de": "aubin"}),
                         "obtenir une part (les planches de bac) d'Aubin")


if __name__ == "__main__":
    unittest.main()
