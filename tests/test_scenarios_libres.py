import tempfile
import unittest
from pathlib import Path

from donjon.monde import Monde, nouveau_monde_libre, objet
from donjon.moteur import Moteur, proposition
from donjon.spatial import installer


def creer(objectif=None):
    salles = {"cour": {"nom": "Cour du moulin", "sorties": {}, "fenetres": 1,
                       "lumiere_naturelle": 2, "altitude_cm": 0,
                       "plan": {"origine": [0, 0], "sol": ["...", "...", "..."], "repere": "C"}}}
    objets = {"jeton": objet("jeton", "jeton de bois", "objet", "cour",
                              mobile=True, masse=0.1, position=[1, 2], position_salle="cour")}
    scenario = {"version": 1, "debut": "Tu arrives dans la cour du moulin.",
                "objectif": "Explore la cour.", "liberte_personnage": "Corvus choisit sa voie."}
    monde = nouveau_monde_libre(salles, objets, "cour", [1, 1], scenario, objectif)
    installer(monde)
    return monde


class ScenariosLibresTests(unittest.TestCase):
    def test_partie_sans_crypte_agit_et_se_recharge(self):
        monde = creer()
        self.assertEqual(set(monde.objets), {"jeton"})
        self.assertEqual(monde.data["missions"], {})
        self.assertEqual(monde.contexte()["salle"]["nom"], "Cour du moulin")
        moteur = Moteur(monde)
        moteur.executer(moteur.preparer(proposition("attendre")))
        self.assertEqual(monde.data["revision"], 1)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "moulin.json"
            monde.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(set(reprise.objets), {"jeton"})
        self.assertEqual(reprise.data["revision"], 1)
        self.assertIsNone(reprise.data["objectif_partie"])

    def test_objectif_libre_suit_son_objet_declare(self):
        objectif = {"objet": "jeton", "lieu": "joueur", "message": "Le jeton est retrouvé."}
        monde = creer(objectif)
        moteur = Moteur(monde)
        texte = moteur.executer(moteur.preparer(proposition("prendre", "jeton")))
        self.assertIn("Le jeton est retrouvé.", texte)
        self.assertTrue(monde.data["objectif_atteint"])


if __name__ == "__main__":
    unittest.main()
