"""Réactions des PNJ sans profil et horloges d'environnement, vérifiées après rechargement."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.esprits import dernier_son, lire


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
    """Le réflexe déclaré (``reaction_son``) n'existe plus : un PNJ va voir par la délibération, son
    devoir, son courage ou son seuil d'alerte (``tests/test_ouie_commune.py``). Un personnage sans
    profil (la crypte) ne délibère pas : il retient le cri qu'il entend, sans bouger."""

    def test_sans_profil_le_pnj_retient_le_cri_et_reste_en_place(self):
        reprise, sortie = jouer(nouveau_monde(), "je crie à l'aide")
        self.assertEqual(reprise.objets["marchand"]["lieu"], "echoppe")
        self.assertEqual(dernier_son(reprise, "marchand")["nature"], "appel")
        self.assertIsNone(lire(reprise, "marchand")["intention"])
        self.assertIn("aucune réponse", sortie)

    def test_un_ancien_reflexe_declare_est_refuse(self):
        m = nouveau_monde()
        m.objets["marchand"]["reaction_son"] = {"seuil": 2}
        with self.assertRaisesRegex(Exception, "seuil d'alerte"):
            m.verifier()


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
