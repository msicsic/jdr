"""Besoins, délibération et plans des PNJ sur le Relais, vérifiés après rechargement."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.support import refusee, regarder, sans_evacues
from donjon import banc_pnj
from donjon.defi import nouveau_defi
from donjon.esprits import lire, percoit
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.spatial import installer


def recharger(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        return Monde.charger(chemin)


def relais():
    m = refusee(sans_evacues(nouveau_defi()))
    installer(m)
    return m


def attendre(monde, fois=1):
    texte = ""
    for _ in range(fois):
        texte += Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre"))) + "\n"
    return recharger(monde), texte


def chronique(monde):
    return [c["texte"] for c in monde.data.get("chronique", [])]


def absent(monde):
    # Placement d'auteur : le joueur est monté à la galerie de ronde, loin du refuge.
    monde.joueur.update(salle="chambre_cloche", position=[1, 3])
    return monde


class GardeMangerTests(unittest.TestCase):
    def test_brune_affamee_crochete_la_reserve_quand_personne_ne_la_voit(self):
        m, _ = attendre(absent(relais()), 3)
        self.assertEqual(m.objets["crochets"]["lieu"], "brune")
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        self.assertTrue(m.objets["reserve"]["ouverte"])
        self.assertEqual(m.objets["vivres"]["portions"], 3)
        self.assertLess(lire(m, "brune")["besoins"]["faim"], 70)
        textes = chronique(m)
        self.assertIn("Brune, batelière évacuée prend la trousse de crochets.", textes)
        self.assertIn("Brune, batelière évacuée crochète la serrure de la réserve de vivres.", textes)
        self.assertIn("Brune, batelière évacuée mange une part des vivres du refuge.", textes)
        self.assertLess(textes.index("Brune, batelière évacuée prend la trousse de crochets."),
                        textes.index("Brune, batelière évacuée crochète la serrure de la réserve de vivres."))

    def test_sous_les_yeux_du_joueur_elle_attend_puis_renonce(self):
        m = relais()
        # Placement d'auteur : le joueur s'est assis près de la réserve, sa lanterne allumée, et la regarde.
        m.joueur["position"] = [6, 4]
        regarder(m, "joueur", "reserve")
        m, texte = attendre(m, 8)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertEqual(m.objets["vivres"]["portions"], 4)
        self.assertEqual(m.objets["crochets"]["lieu"], "brune")
        self.assertIn("renoncement", [s["type"] for s in lire(m, "brune")["memoire"]])
        self.assertTrue(m.visible("brune"))
        self.assertNotIn("crochète", texte)

    def test_crochets_disparus_elle_replanifie_et_reste_sans_plan(self):
        m = relais()
        # Placement d'auteur : le joueur a pris la trousse avant que Brune ne s'en occupe.
        m.objets["crochets"]["lieu"] = "joueur"
        m.objets["crochets"].pop("position")
        m, _ = attendre(absent(m), 3)
        self.assertIsNone(lire(m, "brune")["croyances"]["crochets"]["lieu"]["valeur"])
        self.assertIn("absence", [s["type"] for s in lire(m, "brune")["memoire"]])
        self.assertIsNone(lire(m, "brune")["intention"])
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertEqual(m.objets["vivres"]["portions"], 4)

    def test_le_joueur_tapi_dans_l_ombre_la_surprend(self):
        m = relais()
        m.objets["lanterne"]["allume"] = False
        # Placement d'auteur : la torche brûle près de la réserve ; le joueur reste dans l'angle nord-ouest.
        m.objets["torche"].update(position=[8, 4], allume=True)
        m.joueur["position"] = [2, 1]
        m, texte = attendre(m, 4)
        self.assertIn("Brune, batelière évacuée crochète la serrure de la réserve de vivres.", texte)
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        self.assertFalse(percoit(m, "brune", "joueur"))

    def test_gorm_dans_l_ombre_la_voit_et_garde_sa_reserve(self):
        m = absent(relais())
        m.objets["lanterne"]["lieu"] = "joueur"
        # Placement d'auteur : la torche brûle près de la réserve.
        m.objets["torche"].update(position=[8, 4], allume=True)
        # Placement d'auteur : Gorm se repose dans l'angle sombre du refuge, ses rondes faites.
        m.objets["marchand"].update(lieu="antichambre", position_salle="antichambre", position=[2, 1])
        lire(m, "marchand")["visites"].update(antichambre=0, crypte=0)
        m, _ = attendre(m, 4)
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        souvenirs = [s for s in lire(m, "marchand")["memoire"] if s["type"] == "vu_agir"]
        self.assertEqual(souvenirs[0]["auteur"], "brune")
        self.assertFalse(lire(m, "marchand")["croyances"]["brune"]["fiable"]["valeur"])
        self.assertGreaterEqual(lire(m, "marchand")["besoins"]["biens"], 50)
        self.assertIn(lire(m, "marchand")["intention"]["but"]["type"], ("pulsion", "garder"))


class GormTests(unittest.TestCase):
    def surpris(self):
        m = relais()
        # Placement d'auteur : le marteau est à Gorm, qui regarde le joueur tendre la main.
        m.objets["marteau"]["proprietaire"] = "marchand"
        m.joueur.update(salle="echoppe", position=[7, 4])
        m.objets["marchand"]["position"] = [6, 2]
        with patch.object(Monde, "d20", return_value=1):
            Moteur(m).executer(Moteur(m).preparer(
                sequence(etape("deplacer", "marteau", "joueur", methode="discret"))))
        m.joueur.update(salle="crypte", position=[1, 1])
        # Placement d'auteur : Brune a déjà mangé et ne touche pas à la réserve pendant ce test.
        lire(m, "brune")["besoins"]["faim"] = 0
        return m

    def test_vol_surpris_il_garde_puis_rapporte_la_cloche_lui_meme(self):
        m = self.surpris()
        self.assertFalse(lire(m, "marchand")["croyances"]["joueur"]["fiable"]["valeur"])
        m, _ = attendre(m, 2)
        self.assertEqual(lire(m, "marchand")["intention"]["but"], {"type": "garder", "lieu": "antichambre"})
        self.assertEqual(m.objets["marchand"]["lieu"], "antichambre")
        m, _ = attendre(m, 28)
        self.assertEqual(m.objets["cloche"]["lieu"], "antichambre")
        self.assertEqual(m.objets["cle"]["lieu"], "marchand")
        self.assertFalse(m.objets["porte"]["verrouillee"])
        self.assertIn("Gorm, gardien du relais déverrouille la porte étanche du beffroi.", chronique(m))
        # La cloche posée au refuge reste l'objectif du joueur.
        m.joueur.update(salle="antichambre", position=[1, 3])
        m.objets["cloche"]["position"] = [1, 4]
        Moteur(m).executer(Moteur(m).preparer(proposition("prendre", "cloche")))
        self.assertTrue(m.data.get("objectif_atteint"))

    def test_sans_la_cle_la_porte_verrouillee_change_son_plan(self):
        m = self.surpris()
        # Le joueur emporte la clé du relais avant que Gorm ne la cherche.
        m.objets["cle"]["lieu"] = "joueur"
        m.objets["cle"].pop("position")
        m, _ = attendre(m, 30)
        self.assertEqual(m.objets["cloche"]["lieu"], "chambre_cloche")
        self.assertIsNone(lire(m, "marchand")["croyances"]["cle"]["lieu"]["valeur"])
        self.assertTrue(m.objets["porte"]["verrouillee"])
        self.assertNotEqual((lire(m, "marchand")["intention"] or {}).get("motif"), "devoir")

    def test_tant_qu_il_croit_le_joueur_fiable_il_lui_laisse_la_cloche(self):
        m, _ = attendre(absent(relais()), 24)
        self.assertGreaterEqual(lire(m, "marchand")["besoins"]["devoir"], 70)
        self.assertEqual(m.objets["cloche"]["lieu"], "chambre_cloche")
        # Ses rondes le mènent au refuge et aux vannes, jamais vers la cloche.
        self.assertNotIn("Gorm, gardien du relais passe dans : Palier des vannes.", chronique(m))
        self.assertNotEqual((lire(m, "marchand")["intention"] or {}).get("but", {}).get("objet"), "cloche")

    def test_honnete_il_ne_mange_pas_les_vivres_d_autrui(self):
        m = absent(relais())
        m.objets["vivres"]["proprietaire"] = "brune"
        lire(m, "marchand")["besoins"]["faim"] = 90
        m, _ = attendre(m, 2)
        self.assertNotEqual((lire(m, "marchand")["intention"] or {}).get("motif"), "faim")


class ProfilTests(unittest.TestCase):
    def test_profil_invalide_refuse_et_besoins_persistants(self):
        m = relais()
        mauvais = copy.deepcopy(m.data)
        mauvais["objets"]["brune"]["profil"]["capacites"] = ["voler_dans_les_airs"]
        with self.assertRaises(ErreurMonde):
            Monde(mauvais)
        m, _ = attendre(absent(m), 12)
        # La faim suit le corps commun : 6 par heure, moitié plus à l'effort.
        faim = lire(m, "marchand")["besoins"]["faim"]
        self.assertTrue(30 + 6 - 0.1 <= faim <= 30 + 6 * 1.5 + 0.1, faim)

    def test_banc_sans_joueur(self):
        with patch("sys.stdout", io.StringIO()) as sortie:
            self.assertEqual(banc_pnj.main(["--heures", "4", "--joueur", "chambre_cloche", "--chronique"]), 0)
        # Relais complet : affamée, Brune demande une part à Gorm, qui la sert et referme sa réserve ;
        # les évacués trempés se chauffent au brasero, que Gorm recharge avec son bois.
        self.assertIn("Brune demande une part des vivres du refuge à Gorm (promis).", sortie.getvalue())
        self.assertIn("Gorm appelle Brune et lui donne une part des vivres du refuge.", sortie.getvalue())
        self.assertIn("Gorm, gardien du relais verrouille la réserve de vivres.", sortie.getvalue())
        self.assertIn("se chauffe près du brasero.", sortie.getvalue())
        self.assertIn("Gorm, gardien du relais alimente le brasero.", sortie.getvalue())
        self.assertIn("== Entre eux ==", sortie.getvalue())
        self.assertIn("Mesures :", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
