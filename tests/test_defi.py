"""Vérifie que les deux itinéraires du Relais des crues sont praticables."""
import unittest
from collections import deque
from unittest.mock import patch

from donjon.defi import BEFFROI, OBJECTIF, PIED_BEFFROI, REFUGE, actualiser, nouveau_defi
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.spatial import installer as installer_spatial, preparer_pas


class DefiRelaisTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_defi()
        installer_spatial(self.m)
        self.moteur = Moteur(self.m)

    def agir(self, action, cible="", outil=""):
        return self.moteur.executer(self.moteur.preparer(proposition(action, cible, outil)))

    def victoire(self):
        self.assertTrue(self.m.data.get("objectif_atteint"))
        lignes = []
        self.assertTrue(actualiser(self.m, lignes))
        self.assertTrue(self.m.data["objectif_atteint"])

    def marcher_jusqua(self, destination):
        """Cherche un chemin local sur une copie puis exécute réellement chaque pas."""
        simulation = self.m.copier()
        debut = tuple(simulation.joueur["position"])
        file, vus = deque([(debut, [])]), {debut}
        chemin = None
        while file:
            position, trajet = file.popleft()
            if position == tuple(destination):
                chemin = trajet
                break
            simulation.joueur["position"] = list(position)
            for direction in ("nord", "sud", "est", "ouest"):
                try:
                    suivant = preparer_pas(simulation, direction)
                except ErreurMonde:
                    continue
                p = tuple(suivant["position"])
                if suivant["salle"] == self.m.joueur["salle"] and p not in vus:
                    vus.add(p)
                    file.append((p, trajet + [direction]))
        self.assertIsNotNone(chemin, "Aucun chemin réel vers " + str(destination))
        for direction in chemin:
            self.agir("marcher", direction)

    def aller_dans(self, destination):
        salle = self.m.data["salles"][self.m.joueur["salle"]]
        direction, sortie = next((d, s) for d, s in salle["sorties"].items()
                                  if s["vers"] == destination)
        dx, dy = {"nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0)}[direction]
        case = sortie["case"]
        self.marcher_jusqua((case[0] - dx, case[1] - dy))
        self.agir("marcher", direction)
        self.assertEqual(self.m.joueur["salle"], destination)

    def test_route_interieure_avec_cle_et_retour(self):
        self.assertEqual(self.m.data["scenario"]["objectif"], OBJECTIF)
        self.assertFalse(self.m.visible("cle"))
        self.assertNotIn("cle", [o["id"] for o in self.m.contexte()["objets_perceptibles"]])
        self.assertIn("contournant", self.agir("examiner", "gravure"))
        self.marcher_jusqua((6, 5))
        self.assertTrue(self.m.visible("cle"))
        self.agir("prendre", "cle")
        self.aller_dans("echoppe")
        self.aller_dans("crypte")
        self.marcher_jusqua((7, 3))
        self.agir("deverrouiller", "porte", "cle")
        self.agir("ouvrir", "porte")
        self.aller_dans(PIED_BEFFROI)
        self.aller_dans(BEFFROI)
        self.assertEqual(self.m.joueur["salle"], BEFFROI)
        self.marcher_jusqua((1, 3))
        self.agir("prendre", "cloche")
        self.assertFalse(self.m.data.get("objectif_atteint", False))
        self.aller_dans(PIED_BEFFROI)
        self.aller_dans("crypte")
        self.aller_dans("echoppe")
        self.aller_dans(REFUGE)
        self.assertEqual(self.m.joueur["salle"], REFUGE)
        self.victoire()

    def test_route_exterieure_par_echelle_et_retour(self):
        with self.assertRaises(ErreurMonde):
            self.agir("installer", "echelle_relais", "appui_clocher")
        self.marcher_jusqua((7, 4))
        self.agir("installer", "echelle_relais", "appui_clocher")
        self.assertEqual(self.m.objets["echelle_relais"]["position"], [8, 3])
        with patch.object(Monde, "d20", return_value=20):
            self.agir("franchir", "echelle_relais")
        self.assertEqual(self.m.joueur["salle"], BEFFROI)
        self.assertEqual(self.m.joueur["position"], [0, 3])
        self.marcher_jusqua((1, 3))
        self.agir("prendre", "cloche")
        self.assertFalse(self.m.data.get("objectif_atteint", False))
        with patch.object(Monde, "d20", return_value=20):
            self.agir("franchir", "echelle_relais")
        self.assertEqual(self.m.joueur["salle"], REFUGE)
        self.victoire()


if __name__ == "__main__":
    unittest.main()
