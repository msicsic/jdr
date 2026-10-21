"""Lumière case par case du mode cases, vérifiée sur le Relais après rechargement."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.defi import nouveau_defi
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.perception import eclairage
from donjon.rendu import regarder
from donjon.spatial import installer


def recharger(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        return Monde.charger(chemin)


def relais():
    m = nouveau_defi(depart="fixe")
    installer(m)
    return m


class LumiereCasesTests(unittest.TestCase):
    def test_zone_eclairee_visible_depuis_le_noir(self):
        m = relais()
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "defi.json"
            m.sauver(chemin)
            with (patch("builtins.input", side_effect=[
                      "éteindre lanterne", "éteindre torche", "tourner ouest", "regarder", "lire consigne",
                      "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--defi", "--console", "--offline", "--save", str(chemin)]), 0)
            reprise = Monde.charger(chemin)
        texte = " ".join(sortie.getvalue().split())
        # La conduite reste dans la pénombre diffuse ; le brasero, en lumière directe, se voit de loin.
        self.assertIn("Dans la pénombre", texte)
        self.assertIn("Au-delà du passage, tu distingues un brasero.", texte)
        self.assertFalse(reprise.objets["lanterne"]["allume"])
        self.assertEqual(eclairage(reprise)["niveau"], 1)
        self.assertTrue(reprise.visible("brasero"))
        self.assertIn([3, 4], reprise.data["exploration"]["echoppe"])
        with self.assertRaises(ErreurMonde):
            Moteur(reprise).preparer(proposition("lire", "gravure"))

    def test_lire_exige_une_source_proche(self):
        m = relais()
        Moteur(m).executer(Moteur(m).preparer(proposition("eteindre", "lanterne")))
        # Placement d'auteur : la torche allumée brûle au fond du refuge.
        m.objets["torche"].update(position=[8, 1], allume=True)
        reprise = recharger(m)
        self.assertEqual(eclairage(reprise)["niveau"], 1)
        self.assertIn("Dans la pénombre", regarder(reprise))
        with self.assertRaises(ErreurMonde):
            Moteur(reprise).preparer(proposition("lire", "gravure"))
        reprise.objets["torche"]["position"] = [1, 2]
        reprise = recharger(reprise)
        self.assertEqual(eclairage(reprise)["niveau"], 2)
        Moteur(reprise).executer(Moteur(reprise).preparer(proposition("lire", "gravure")))
        self.assertIn("gravure", reprise.data["lus"])

    def test_obstacle_opaque_projette_une_ombre(self):
        m = relais()
        for id in ("lanterne", "torche"):
            m.objets[id]["allume"] = False
        m.joueur.update(salle="echoppe", position=[6, 3])
        reprise = recharger(m)
        # La poutre de la conduite, en (5, 3), cache le brasero (3, 4) : pénombre diffuse seulement.
        self.assertEqual(eclairage(reprise)["niveau"], 1)
        reprise.joueur["position"] = [4, 3]
        self.assertEqual(eclairage(reprise)["niveau"], 2)
        self.assertIn("Le brasero éclaire la pièce.", regarder(reprise))


if __name__ == "__main__":
    unittest.main()
