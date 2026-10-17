"""Réactions déclarées des PNJ et horloges d'environnement, vérifiées après rechargement."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, proposition


def jouer(monde, *saisies):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        with (patch("builtins.input", side_effect=[*saisies, "quitter"]),
              patch("sys.stdout", io.StringIO()) as sortie):
            assert jeu.main(["--console", "--offline", "--save", str(chemin)]) == 0
        return Monde.charger(chemin), sortie.getvalue()


def executer(monde, *propositions):
    for p in propositions:
        Moteur(monde).executer(Moteur(monde).preparer(p))


class ReactionsTests(unittest.TestCase):
    def test_gorm_alerte_par_un_cri_rejoint_le_joueur(self):
        m = nouveau_monde()
        m.objets["marchand"]["reaction_son"] = {"seuil": 2}
        reprise, sortie = jouer(m, "je crie à l'aide")
        self.assertEqual(reprise.objets["marchand"]["lieu"], "antichambre")
        self.assertNotIn("trajet", reprise.objets["marchand"])
        self.assertIn("Gorm le marchand arrive.", sortie)
        self.assertNotIn("aucune réponse", sortie)

    def test_porte_fermee_arrete_le_pnj_jusqu_a_son_ouverture(self):
        m = nouveau_monde()
        m.objets["porte"]["verrouillee"] = False
        # Placement d'auteur : Gorm attend dans la crypte, derrière la porte.
        m.objets["marchand"].update(lieu="crypte", position_salle="crypte", reaction_son={"seuil": 1})
        reprise, sortie = jouer(m, "crier", "attendre")
        self.assertEqual(reprise.objets["marchand"]["lieu"], "crypte")
        self.assertEqual(reprise.objets["marchand"]["trajet"]["vers"], "antichambre")
        self.assertIn("aucune réponse", sortie)
        reprise, sortie = jouer(reprise, "ouvrir porte", "attendre")
        self.assertEqual(reprise.objets["marchand"]["lieu"], "antichambre")
        self.assertIn("Gorm le marchand arrive.", sortie)

    def test_sans_reaction_declaree_le_pnj_reste_en_place(self):
        reprise, sortie = jouer(nouveau_monde(), "je crie à l'aide")
        self.assertEqual(reprise.objets["marchand"]["lieu"], "echoppe")
        self.assertEqual(reprise.objets["marchand"]["dernier_son_entendu"]["nature"], "appel")
        self.assertIn("aucune réponse", sortie)

    def test_son_trop_faible_sous_le_seuil(self):
        m = nouveau_monde()
        m.objets["marchand"]["reaction_son"] = {"seuil": 3}
        reprise, _ = jouer(m, "je crie à l'aide")
        self.assertEqual(reprise.objets["marchand"]["lieu"], "echoppe")
        self.assertNotIn("trajet", reprise.objets["marchand"])


HORLOGE = {"id": "courant_air", "minute": 5, "annonce": "Un souffle glacé traverse la salle et couche les flammes.",
           "lieux": ["antichambre"], "effets": [{"operation": "eteindre", "salles": ["antichambre"]}]}


class HorlogesTests(unittest.TestCase):
    def test_horloge_declenchee_une_fois_et_persistante(self):
        m = nouveau_monde()
        m.data["horloges"] = [copy.deepcopy(HORLOGE)]
        reprise, sortie = jouer(m, "attendre")
        self.assertFalse(reprise.objets["lanterne"]["allume"])
        self.assertTrue(reprise.objets["brasero"]["allume"])
        self.assertEqual(reprise.data["horloges_declenchees"], ["courant_air"])
        self.assertIn(HORLOGE["annonce"], sortie)
        reprise, sortie = jouer(reprise, "allumer lanterne", "attendre")
        self.assertTrue(reprise.objets["lanterne"]["allume"])
        self.assertNotIn(HORLOGE["annonce"], sortie)

    def test_annonce_hors_de_portee_et_effet_devenu_sans_objet(self):
        m = nouveau_monde()
        executer(m, proposition("prendre", "torche"))
        m.data["horloges"] = [{"id": "chute", "minute": 1, "annonce": "Une torche roule depuis l'échoppe.",
                               "lieux": ["echoppe"], "effets": [
                                   {"operation": "deplacer", "objet": "torche", "depuis": "antichambre",
                                    "lieu": "echoppe", "position": [1, 2]},
                                   {"operation": "eteindre", "salles": ["echoppe"]}]}]
        reprise, sortie = jouer(m, "attendre")
        self.assertEqual(reprise.objets["torche"]["lieu"], "joueur")
        self.assertFalse(reprise.objets["brasero"]["allume"])
        self.assertTrue(reprise.objets["lanterne"]["allume"])
        self.assertNotIn("Une torche roule", sortie)


if __name__ == "__main__":
    unittest.main()
