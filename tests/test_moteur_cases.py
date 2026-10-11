import copy
import tempfile
from pathlib import Path
import unittest

from donjon.carte import carte
from donjon.commandes import analyser
from donjon.monde import Monde, ErreurMonde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.spatial import installer, proche


class IntegrationCasesTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        installer(self.m)
        self.moteur = Moteur(self.m)

    def agir(self, action, cible="", outil=""):
        return self.moteur.executer(self.moteur.preparer(proposition(action, cible, outil)))

    def test_prendre_exige_approche_et_met_a_jour_carte(self):
        avant = copy.deepcopy(self.m.data)
        with self.assertRaisesRegex(ErreurMonde, "Approche-toi"):
            self.agir("prendre", "cle")
        self.assertEqual(self.m.data, avant)
        self.assertIn("clé du veilleur", carte(self.m))
        self.agir("marcher", "est")
        self.agir("prendre", "cle")
        self.assertEqual(self.m.objets["cle"]["lieu"], "joueur")
        self.assertNotIn("cle", self.m.data["souvenirs_visuels"])
        self.assertNotIn("clé du veilleur", carte(self.m))

    def test_une_proposition_composee_ne_contourne_pas_la_portee(self):
        avant = copy.deepcopy(self.m.data)
        p = sequence(etape("deplacer", "cle", "joueur"))
        with self.assertRaisesRegex(ErreurMonde, "Approche-toi"):
            self.moteur.preparer(p, "LLM")
        self.assertEqual(self.m.data, avant)

    def test_objet_cache_par_obstacle_absent_du_contexte(self):
        self.m.objets["cloison"] = objet("cloison", "cloison", "surface", "antichambre",
            position_salle="antichambre", position=[2, 2], bloque_vue=True, bloque_passage=True)
        self.assertFalse(self.m.visible("cle"))
        self.assertNotIn("cle", {o["id"] for o in self.m.contexte()["objets_perceptibles"]})
        with self.assertRaises(ErreurMonde):
            self.agir("marcher", "est")
        self.agir("marcher", "sud")
        self.agir("marcher", "est")
        self.assertTrue(self.m.visible("cle"))

    def test_examiner_de_loin_ne_revele_pas_inscription(self):
        self.m.joueur["position"] = [0, 3]
        self.assertTrue(self.m.visible("gravure"))
        self.assertFalse(proche(self.m, "gravure"))
        description = self.agir("examiner", "gravure")
        self.assertNotIn(self.m.objets["gravure"]["inscription"], description)
        self.assertIn("Approche-toi", description)
        vue = next(o for o in self.m.contexte()["objets_perceptibles"] if o["id"] == "gravure")
        self.assertFalse(vue["a_portee"])
        self.assertNotIn("inscription", vue)

    def test_pas_locaux_sans_jet_et_temps_de_marche(self):
        for _ in range(5):
            for direction in ("est", "ouest"):
                p = analyser(self.m, "pas " + direction)
                self.moteur.executer(self.moteur.preparer(p))
        self.assertEqual(self.m.joueur["position"], [1, 2])
        self.assertEqual(self.m.data["minutes"], 1)
        self.assertEqual(self.m.data["jets"], 0)
        self.assertEqual(self.m.objets["lanterne"]["combustible"], 59)
        self.assertFalse(self.m.contexte()["evenements_recents"])

    def test_acheter_exige_aussi_proximite_du_marchand(self):
        self.m.joueur.update(salle="echoppe", position=[4, 1])
        with self.assertRaisesRegex(ErreurMonde, "Approche-toi"):
            self.agir("acheter", "pied_de_biche")
        self.agir("marcher", "ouest")
        self.agir("marcher", "ouest")
        self.agir("acheter", "pied_de_biche")
        self.assertEqual(self.m.objets["pied_de_biche"]["lieu"], "joueur")

    def test_sortie_visible_presente_dans_contexte(self):
        self.m.joueur["position"] = [3, 1]
        self.assertIn("nord", self.m.contexte()["salle"]["sorties"])
        self.assertNotIn("plan", self.m.contexte()["salle"])
        self.agir("marcher", "nord")
        with self.assertRaisesRegex(ErreurMonde, "fermée"):
            self.agir("marcher", "nord")

    def test_memoire_et_position_survivent_au_rechargement(self):
        self.agir("marcher", "est")
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as d:
            chemin = Path(d) / "test.json"
            self.m.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.joueur["position"], self.m.joueur["position"])
        self.assertEqual(reprise.data["exploration"], self.m.data["exploration"])
        self.assertEqual(carte(reprise), carte(self.m))


if __name__ == "__main__":
    unittest.main()
