"""Perception par acteur et croyances des PNJ, vérifiées sur l'état et après rechargement."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.defi import nouveau_defi
from donjon.esprits import lire, percoit
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.spatial import installer


def recharger(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        return Monde.charger(chemin)


def relais():
    m = nouveau_defi()
    installer(m)
    return m


def attendre(monde):
    Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre")))
    return recharger(monde)


def croyance(monde, sujet, attribut="lieu"):
    return lire(monde, "marchand")["croyances"].get(sujet, {}).get(attribut)


class PerceptionParActeurTests(unittest.TestCase):
    def test_gorm_voit_ce_que_la_lumiere_et_la_ligne_de_vue_lui_montrent(self):
        m = relais()
        # Placement d'auteur : Gorm se tient au milieu de la conduite.
        m.objets["marchand"]["position"] = [6, 2]
        reprise = attendre(m)
        self.assertEqual(croyance(reprise, "crochets")["valeur"], "echoppe")
        self.assertEqual(croyance(reprise, "crochets")["case"], [8, 5])
        self.assertEqual(croyance(reprise, "crochets")["source"], "vu")
        # La poutre de la conduite lui cache le brasero.
        self.assertIsNone(croyance(reprise, "brasero", "etat"))
        reprise.objets["marchand"]["position"] = [4, 2]
        reprise = attendre(reprise)
        self.assertEqual(croyance(reprise, "brasero", "etat")["valeur"], {"allume": True})
        self.assertNotIn("barbe_gorm", lire(reprise, "marchand")["croyances"])

    def test_gorm_ne_voit_rien_dans_le_noir(self):
        m = relais()
        m.objets["marchand"]["position"] = [6, 2]
        for id in ("brasero", "lanterne", "torche"):
            m.objets[id]["allume"] = False
        reprise = attendre(m)
        self.assertIsNone(croyance(reprise, "crochets"))
        self.assertIsNone(croyance(reprise, "joueur"))
        # Même règle sans cases : la crypte noire ne lui montre rien, une torche portée si.
        c = nouveau_monde()
        c.objets["marchand"].update(lieu="crypte", position_salle="crypte")
        c = attendre(c)
        self.assertEqual(lire(c, "marchand")["croyances"], {})
        c.objets["torche"].update(lieu="marchand", allume=True)
        c = attendre(c)
        self.assertEqual(croyance(c, "porte", "etat")["valeur"], {"ouverte": False})
        self.assertEqual(croyance(c, "torche")["valeur"], "marchand")

    def test_la_poutre_cache_le_joueur(self):
        m = relais()
        m.joueur.update(salle="echoppe", position=[7, 3])
        m.objets["marchand"]["position"] = [3, 3]
        reprise = attendre(m)
        self.assertFalse(percoit(reprise, "marchand", "joueur"))
        self.assertIsNone(croyance(reprise, "joueur"))
        reprise.objets["marchand"]["position"] = [3, 1]
        reprise = attendre(reprise)
        self.assertEqual(croyance(reprise, "joueur")["valeur"], "echoppe")
        self.assertEqual(croyance(reprise, "joueur")["case"], [7, 3])

    def test_tapi_dans_la_penombre_on_voit_sans_etre_vu(self):
        m = relais()
        for id in ("lanterne", "torche"):
            m.objets[id]["allume"] = False
        # Placement d'auteur : la trousse a glissé dans l'angle nord-est de la conduite.
        m.objets["crochets"]["position"] = [8, 3]
        m.joueur.update(salle="echoppe", position=[8, 2])
        m.objets["marchand"]["position"] = [3, 1]
        m = recharger(m)
        self.assertTrue(m.visible("marchand"))
        self.assertFalse(percoit(m, "marchand", "joueur"))
        geste = sequence(etape("deplacer", "crochets", "joueur", methode="discret"))
        self.assertFalse(Moteur(m).preparer(geste).stat)
        # Le même geste sous les yeux de Gorm, ou à la lueur de la lanterne, demande un jet.
        m.objets["marchand"]["position"] = [6, 2]
        self.assertEqual(Moteur(m).preparer(geste).stat, "DEX")
        m.objets["marchand"]["position"] = [3, 1]
        m.objets["lanterne"]["allume"] = True
        self.assertTrue(percoit(m, "marchand", "joueur"))
        self.assertEqual(Moteur(m).preparer(geste).stat, "DEX")


class CroyancesTests(unittest.TestCase):
    def test_croyance_perimee_jusqu_a_ce_qu_il_revoie_la_place(self):
        m = relais()
        m.objets["marchand"]["position"] = [6, 2]
        m = attendre(m)
        # Placement d'auteur : Gorm descend à la salle des vannes ; le joueur prend la trousse.
        m.objets["marchand"].update(lieu="crypte", position_salle="crypte", position=[4, 1])
        m.joueur.update(salle="echoppe", position=[8, 4])
        Moteur(m).executer(Moteur(m).preparer(proposition("prendre", "crochets")))
        m = recharger(m)
        self.assertEqual(m.objets["crochets"]["lieu"], "joueur")
        self.assertEqual(croyance(m, "crochets")["valeur"], "echoppe")
        # Le joueur s'éloigne ; Gorm revient et voit l'étagère vide.
        m.joueur.update(salle="antichambre", position=[1, 3])
        m.objets["marchand"].update(lieu="echoppe", position_salle="echoppe", position=[6, 2])
        m = attendre(m)
        self.assertIsNone(croyance(m, "crochets")["valeur"])
        self.assertEqual(lire(m, "marchand")["memoire"][-1]["type"], "absence")
        self.assertEqual(lire(m, "marchand")["memoire"][-1]["objet"], "crochets")

    def test_gorm_croit_la_cloche_dans_la_galerie_tant_qu_il_ne_l_a_pas_vue_ailleurs(self):
        m = relais()
        self.assertEqual(croyance(m, "cloche")["source"], "savoir")
        # Placement d'auteur : le joueur est monté à la galerie et prend la cloche, loin de Gorm.
        m.joueur.update(salle="chambre_cloche", position=[2, 2])
        Moteur(m).executer(Moteur(m).preparer(proposition("prendre", "cloche")))
        m = recharger(m)
        self.assertEqual(m.objets["cloche"]["lieu"], "joueur")
        self.assertEqual(croyance(m, "cloche")["valeur"], "chambre_cloche")
        self.assertEqual(croyance(m, "cloche")["source"], "savoir")
        # Il la voit dans les mains du joueur dès que celui-ci passe sous ses yeux.
        m.joueur.update(salle="echoppe", position=[7, 1])
        m.objets["marchand"]["position"] = [6, 2]
        m = attendre(m)
        self.assertEqual((croyance(m, "cloche")["valeur"], croyance(m, "cloche")["source"]), ("joueur", "vu"))

    def test_un_objet_porte_se_remarque_s_il_est_encombrant(self):
        m = relais()
        # Placement d'auteur : le joueur revient de la galerie avec la cloche et la clé.
        for id in ("cloche", "cle"):
            m.objets[id]["lieu"] = "joueur"
            m.objets[id].pop("position", None)
        m.joueur.update(salle="echoppe", position=[7, 1])
        m.objets["marchand"]["position"] = [6, 2]
        m = attendre(m)
        self.assertEqual(croyance(m, "cloche")["valeur"], "joueur")
        # La clé, trop petite pour se remarquer, reste crue au refuge.
        self.assertEqual((croyance(m, "cle")["valeur"], croyance(m, "cle")["source"]), ("antichambre", "savoir"))

    def test_vol_surpris_memorise_apres_rechargement(self):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        geste = sequence(etape("deplacer", "crochets", "joueur", methode="discret"))
        with patch.object(Monde, "d20", return_value=1):
            Moteur(m).executer(Moteur(m).preparer(geste))
        reprise = recharger(m)
        evenement = lire(reprise, "marchand")["memoire"][-1]
        self.assertEqual((evenement["type"], evenement["objet"]), ("vol_surpris", "crochets"))
        self.assertEqual(croyance(reprise, "joueur")["valeur"], "echoppe")

    def test_ancienne_partie_migree(self):
        m = nouveau_monde()
        data = m.data
        data["esprits"] = {}
        data["objets"]["marchand"]["dernier_son_entendu"] = {
            "tour": 3, "minute": 2, "origine": "antichambre", "nature": "appel", "intensite": 3}
        data["objets"]["marchand"]["reaction_son"] = {"seuil": 2}
        data["objets"]["marchand"]["trajet"] = {"vers": "antichambre", "minutes": 0}
        reprise = Monde(data)
        self.assertNotIn("trajet", reprise.objets["marchand"])
        self.assertEqual(lire(reprise, "marchand")["memoire"][0]["nature"], "appel")
        self.assertEqual(lire(reprise, "marchand")["intention"]["but"]["lieu"], "antichambre")
        reprise = attendre(reprise)
        self.assertEqual(reprise.objets["marchand"]["lieu"], "antichambre")


class CommandeEspritTests(unittest.TestCase):
    def test_esprit_reserve_au_debug(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            nouveau_monde().sauver(chemin)
            with (patch("builtins.input", side_effect=["attendre", "esprit gorm", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--debug", "--save", str(chemin)]), 0)
        self.assertIn('"croyances"', sortie.getvalue())
        self.assertIn('"intention"', sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
