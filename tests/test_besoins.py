"""Besoins, délibération et plans des PNJ sur le Relais, vérifiés après rechargement."""

from tests.support import relation
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.support import refusee, regarder, sans_evacues
from donjon import banc_pnj
from donjon.defi import nouveau_defi
from donjon.esprits import lire, percoit, percevoir_tous
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
    from tests.support import presentes
    m = presentes(refusee(sans_evacues(nouveau_defi(depart="fixe"))))
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


def aux_vannes(monde):
    """Placement d'auteur : Gorm, ses rondes faites et son feu vu vif, se tient aux vannes, trop loin
    du refuge pour entendre crocheter (``ouie``)."""
    from donjon.esprits import croire
    from tests.support import calme
    monde.objets["marchand"].update(lieu="crypte", position_salle="crypte", position=[4, 3])
    croire(monde, "marchand", "brasero", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
    return calme(monde, "marchand")


class GardeMangerTests(unittest.TestCase):
    def test_brune_affamee_crochete_la_reserve_quand_personne_ne_la_voit(self):
        m, _ = attendre(absent(aux_vannes(relais())), 3)
        self.assertEqual(m.objets["crochets"]["lieu"], "brune")
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        self.assertTrue(m.objets["reserve"]["ouverte"])
        self.assertEqual(m.objets["vivres"]["portions"], 3)
        self.assertLess(lire(m, "brune")["besoins"]["faim"], 70)
        textes = chronique(m)
        self.assertIn("Brune, batelière évacuée prend la trousse de crochets.", textes)
        self.assertIn("Brune, batelière évacuée crochète la serrure de la réserve de vivres sans forcer.", textes)
        self.assertIn("Brune, batelière évacuée mange une part des vivres du refuge.", textes)
        self.assertLess(textes.index("Brune, batelière évacuée prend la trousse de crochets."),
                        textes.index("Brune, batelière évacuée crochète la serrure de la réserve de vivres sans forcer."))

    def test_sous_les_yeux_du_joueur_elle_attend_puis_renonce(self):
        m = relais()
        from donjon import relations
        lire(m, "marchand")["relations"]["brune"] = relations._nouvelle({"confiance": 10})
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
        # Cette scène exclut le forçage : à douceur 75, Brune peut désormais prévoir des coups.
        m.objets["brune"]["profil"]["valeurs"]["douceur"] = 100
        # Cette scène isole l'outil absent : aucun service d'allumage à offrir.
        m.objets['torche'].update(allume=True, combustible=120)
        # Pas de bois propre à échanger contre le repas non plus.
        from tests.test_entretenir import sans
        sans(m, 'bois_bateliere')
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
        m = aux_vannes(relais())
        m.objets["lanterne"]["allume"] = False
        # Placement d'auteur : la torche brûle près de la réserve ; le joueur reste dans l'angle nord-ouest.
        m.objets["torche"].update(position=[8, 4], allume=True)
        m.joueur["position"] = [2, 1]
        # Elle compte ceux qu'elle sait à portée d'oreille (branche ``ouie-temoins``) : elle l'a aperçu
        # en entrant ; à bout de faim, elle force quand même (``pnj.desespere``).
        lire(m, "brune")["besoins"]["faim"] = 96.0
        m, texte = attendre(m, 4)
        self.assertIn("Brune, batelière évacuée crochète la serrure de la réserve de vivres sans forcer.", texte)
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        self.assertFalse(percoit(m, "brune", "joueur"))

    @patch("donjon.agendas._naissances", return_value=None)
    def test_gorm_dans_l_ombre_la_voit_et_garde_sa_reserve(self, _naissance):
        # Isoler la garde vue du nouveau marché de reverrouillage après le repas.
        m = absent(relais())
        m.objets["lanterne"]["lieu"] = "joueur"
        # Placement d'auteur : la torche brûle près de la réserve.
        m.objets["torche"].update(position=[8, 4], allume=True)
        # Placement d'auteur : Gorm se repose dans l'angle sombre du refuge, ses rondes faites ; au
        # repos, il entend moins bien (``ouie``) et ne se lève pas pour des pas.
        m.objets["marchand"].update(lieu="antichambre", position_salle="antichambre", position=[2, 1])
        lire(m, "marchand")["visites"].update(antichambre=0, crypte=0)
        lire(m, "marchand")["besoins"]["repos"] = 40.0
        lire(m, "marchand")["intention"] = {"but": {"type": "repos"}, "motif": "repos", "depuis": 0, "attente": 0,
                                            "plan": [{"operation": "reposer", "cible": "", "outil": "", "lieu": "",
                                                      "condition": ""}]}
        # Elle l'a vu s'asseoir dans l'angle et le sait à portée d'oreille (branche ``ouie-temoins``) :
        # à bout de faim, elle force quand même (``pnj.desespere``).
        lire(m, "brune")["besoins"]["faim"] = 96.0
        # Elle a déjà épuisé le recours avec ses outils : la scène porte sur le guet caché.
        from donjon.pnj_propositions import _entrees
        m.objets["crochets"]["lieu"] = "brune"
        m.objets["crochets"].pop("position", None)
        percevoir_tous(m)
        lire(m, "brune")["recours_propositions"] = [_entrees(
            m, "brune", "marchand", "faim", {"type": "part", "objet": "vivres"})]
        m, _ = attendre(m, 4)
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        souvenirs = [s for s in lire(m, "marchand")["memoire"] if s["type"] == "vu_agir"]
        self.assertEqual(souvenirs[0]["auteur"], "brune")
        self.assertFalse(relation(m, "marchand", "brune")["valeur"])
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
        self.assertFalse(relation(m, "marchand", "joueur")["valeur"])
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
        # Le joueur emporte la clé du relais, et de quoi forcer la porte, avant que Gorm ne les cherche.
        for k in ("cle", "pied_de_biche", "marteau"):
            m.objets[k]["lieu"] = "joueur"
            m.objets[k].pop("position")
        m, _ = attendre(m, 30)
        self.assertEqual(m.objets["cloche"]["lieu"], "chambre_cloche")
        self.assertIsNone(lire(m, "marchand")["croyances"]["cle"]["lieu"]["valeur"])
        self.assertTrue(m.objets["porte"]["verrouillee"])
        # Il ne poursuit plus la cloche (un autre devoir, le brasero, a pu le reprendre).
        self.assertNotEqual((lire(m, "marchand")["intention"] or {}).get("but", {}).get("objet"), "cloche")

    def test_sans_la_cle_il_force_la_porte_qui_n_est_a_personne(self):
        # Le pied-de-biche reste à la conduite : la porte étanche n'est à personne, la forcer ne
        # lèse personne (``force``) ; il la force et rapporte la cloche.
        m = self.surpris()
        m.objets["cle"]["lieu"] = "joueur"
        m.objets["cle"].pop("position")
        m, _ = attendre(m, 30)
        self.assertIn("Gorm, gardien du relais force la porte étanche du beffroi.", chronique(m))
        self.assertEqual((m.objets["porte"]["integrite"], m.objets["porte"]["ouverte"]), (0, True))
        self.assertEqual(m.objets["cloche"]["lieu"], "antichambre")

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
        # Ce test vérifie le banc et son récit, pas le tirage d'un marché dont
        # l'évaluation peut évoluer. La demande de Brune est persuasive ici.
        with patch("sys.stdout", io.StringIO()) as sortie, patch.object(Monde, "d20", return_value=20):
            self.assertEqual(banc_pnj.main(["--heures", "4", "--joueur", "chambre_cloche", "--chronique"]), 0)
        # Relais complet : affamée, Brune demande une part à Gorm, qui la sert et referme sa réserve ;
        # les évacués trempés se chauffent au brasero, que Gorm recharge avec son bois.
        # Affamée, Brune demande sa part, ou Gorm la sert de lui-même s'il voit sa faim
        # (secours du lot 197) ; dans les deux cas, la part est réellement donnée.
        self.assertRegex(sortie.getvalue(), r"Brune demande une part des vivres du refuge à Gorm \("
                                            r"|servir les vivres du refuge à Brune \(empathie\)")
        self.assertRegex(sortie.getvalue(), "Gorm appelle Brune et lui donne une part des vivres du refuge"
                                           "|Gorm remet les vivres du refuge à Brune")
        self.assertIn("Gorm, gardien du relais verrouille la réserve de vivres.", sortie.getvalue())
        self.assertIn("se chauffe près du brasero.", sortie.getvalue())
        self.assertIn("Gorm, gardien du relais alimente le brasero.", sortie.getvalue())
        self.assertIn("== Entre eux ==", sortie.getvalue())
        self.assertIn("Mesures :", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
