import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.defi import nouveau_defi
from donjon import scenario_crypte
from donjon.monde import Monde, nouveau_monde, nouveau_monde_libre, objet
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
    def test_empreinte_crypte_visible_apres_rechargement(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "crypte.json"
            nouveau_monde().sauver(chemin)
            with (patch("builtins.input", side_effect=["copier gravure avec cire", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            self.assertIn("empreinte de la gravure du chevalier", sortie.getvalue())
            reprise = Monde.charger(chemin)
            copies = [o for o in reprise.objets.values() if o.get("source") == "gravure"]
            self.assertEqual(len(copies), 1)
            self.assertEqual(copies[0]["lieu"], "joueur")
            self.assertEqual(copies[0]["materiau"], "cire")
            self.assertEqual(reprise.objets["cire"]["charges"], 1)
            with (patch("builtins.input", side_effect=["examiner " + copies[0]["id"], "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            self.assertIn("Un chevalier agenouillé", sortie.getvalue())

    def test_empreinte_dans_un_scenario_sans_crypte_est_visible_apres_rechargement(self):
        monde = creer()
        monde.objets["sceau"] = objet("sceau", "sceau du moulin", "motif", "cour",
                                     motif="Un épi entoure une roue.",
                                     inscription="La roue garde le grain.",
                                     mobile=False, position=[1, 2], position_salle="cour")
        monde.objets["argile"] = objet("argile", "galette d'argile", "consommable", "joueur",
                                      genre="f", mobile=True, materiau="argile", masse=0.2,
                                      charges=2, usages=["empreinte"])
        monde.verifier()
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "moulin.json"
            monde.sauver(chemin)
            with (patch("builtins.input", side_effect=["copier sceau avec argile", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            texte = sortie.getvalue()
            reprise = Monde.charger(chemin)
            copies = [o for o in reprise.objets.values() if o.get("source") == "sceau"]
            self.assertEqual(len(copies), 1)
            copie = copies[0]
            self.assertEqual(copie["lieu"], "joueur")
            self.assertEqual(copie["materiau"], "argile")
            self.assertEqual(copie["motif"], monde.objets["sceau"]["motif"])
            self.assertEqual(reprise.objets["argile"]["charges"], 1)
            self.assertIn("empreinte du sceau du moulin", texte)
            self.assertIn("galette d'argile", texte)
            self.assertNotIn("gravure", texte)
            self.assertNotIn("cire", texte)
            with (patch("builtins.input", side_effect=["examiner " + copie["id"], "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            self.assertIn("Un épi entoure une roue.", sortie.getvalue())

    def test_resultat_local_attend_une_sauvegarde_reussie_avant_affichage(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "moulin.json"
            creer().sauver(chemin)
            sauver = Monde.sauver
            appels = 0

            def ecriture(monde, destination):
                nonlocal appels
                appels += 1
                if appels == 1:
                    raise OSError("écriture simulée impossible")
                return sauver(monde, destination)

            with (patch.object(Monde, "sauver", ecriture),
                  patch("builtins.input", side_effect=["prendre jeton", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            self.assertIn("Ecriture de sauvegarde impossible", sortie.getvalue())
            self.assertNotIn("rejoint votre besace", sortie.getvalue())
            self.assertEqual(Monde.charger(chemin).objets["jeton"]["lieu"], "joueur")

    def test_relais_et_atelier_demarrent_sans_le_fichier_de_la_crypte(self):
        with patch.object(scenario_crypte, "ETAT_INITIAL", Path("absent.json")):
            relais = nouveau_defi()
            atelier = nouveau_atelier()
        self.assertIn("cloche", relais.objets)
        self.assertIn("perche_1", atelier.objets)
        self.assertEqual(relais.data["objectif_partie"]["objet"], "cloche")
        self.assertEqual(set(atelier.data["salles"]), {"cour", "terrasse"})
        self.assertNotIn("marchand", atelier.objets)
        self.assertIsNone(atelier.data["objectif_partie"])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "relais.json"
            relais.sauver(chemin)
            self.assertEqual(Monde.charger(chemin).objets["cloche"], relais.objets["cloche"])

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
