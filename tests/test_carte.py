import copy
import unittest
from unittest.mock import patch

from donjon.carte import carte
from donjon.commandes import analyser
from donjon.geometrie import DIRECTIONS, cases, position_entree
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur
from donjon.rendu import regarder


class CarteTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        self.moteur = Moteur(self.m)

    def agir(self, texte):
        return self.moteur.executer(self.moteur.preparer(analyser(self.m, texte)))

    def test_piece_inexploree_ne_revele_ni_forme_ni_nom_ni_objets(self):
        avant = carte(self.m)
        self.assertNotIn("?", avant)
        self.assertNotIn("Crypte", avant)
        self.assertNotIn("coffre", avant)
        self.assertIn("^", avant)
        self.assertIn("# porte verrouillée", avant)
        self.m.data["salles"]["crypte"]["plan"]["sol"] = ["................."] * 12
        self.m.data["salles"]["crypte"]["plan"]["origine"] = [80, 80]
        self.assertEqual(carte(self.m), avant)

    def test_meme_echelle_pour_dimensions_differentes(self):
        plan = carte(self.m)
        self.assertIn("6 x 4 m", plan)
        self.assertIn("5 x 6 m", plan)
        # Les coordonnées des objets se projettent avec deux caractères par mètre.
        lignes = plan.splitlines()
        ligne_joueur = next(ligne for ligne in lignes[1:] if "@" in ligne)
        self.assertEqual(ligne_joueur.index("k") - ligne_joueur.index("@"), 4)
        self.assertEqual(len(cases(self.m.data["salles"]["antichambre"])), 24)

    def test_passages_partages_et_entrees_sur_le_sol(self):
        for id, piece in self.m.data["salles"].items():
            for direction, sortie in piece["sorties"].items():
                voisine = self.m.data["salles"][sortie["vers"]]
                retour = next(s for s in voisine["sorties"].values() if s["vers"] == id)
                p = tuple(a + b for a, b in zip(piece["plan"]["origine"], sortie["case"]))
                q = tuple(a + b for a, b in zip(voisine["plan"]["origine"], retour["case"]))
                self.assertEqual(p, q)
                dx, dy = DIRECTIONS[direction]
                x, y = sortie["case"]
                self.assertIn((x - dx, y - dy), cases(piece))
                self.assertNotIn((x, y), cases(piece))

    def test_objets_visibles_seulement_et_positions_suivent_les_actions(self):
        avant = carte(self.m)
        self.assertIn("k la clé", avant)
        self.assertNotIn("brasero", avant)
        self.agir("prendre clé")
        self.assertNotIn("k la clé", carte(self.m))
        self.agir("ouest")
        self.assertEqual(tuple(self.m.joueur["position"]), position_entree(self.m, "echoppe", "antichambre"))
        self.assertIn("G Gorm", carte(self.m))
        self.agir("poser clé")
        self.assertEqual(self.m.objets["cle"]["position"], self.m.joueur["position"])
        self.assertEqual(self.m.objets["cle"]["position_salle"], "echoppe")
        self.assertIn("À tes pieds (@) : la clé", carte(self.m))

    def test_forme_crypte_revelee_seulement_apres_entree(self):
        self.m.objets["porte"]["ouverte"] = True
        self.agir("nord")
        plan = carte(self.m)
        self.assertIn("Crypte du veilleur (8 x 7 m)", plan)
        self.assertIn("c le coffre", plan)
        self.assertNotIn("anneau", plan)
        self.assertNotIn("suite inexplorée", plan)
        self.assertLess(len(cases(self.m.data["salles"]["crypte"])), 8 * 7)

    def test_noir_masque_objets_et_carte_ne_modifie_pas_etat(self):
        self.m.objets["lanterne"]["allume"] = False
        self.m.objets["brasero"]["allume"] = False
        avant = copy.deepcopy(self.m.data)
        plan = carte(self.m)
        self.assertNotIn("clé", plan)
        self.assertNotIn("torche", plan)
        self.assertIn("@", plan)
        self.assertEqual(self.m.data, avant)

    def test_contenu_libere_au_meme_endroit_que_le_coffre(self):
        self.m.objets["porte"]["ouverte"] = True
        self.agir("ouest")
        self.agir("acheter marteau")
        self.agir("est")
        self.agir("nord")
        self.m.objets["coffre"]["integrite"] = 1
        with patch.object(Monde, "d20", return_value=20):
            self.agir("frapper coffre avec marteau")
        self.assertEqual(self.m.objets["anneau"]["position"], self.m.objets["coffre"]["position"])
        self.assertIn("& le coffre de pierre et l'anneau", carte(self.m))

    def test_rechargement_preserve_la_partie(self):
        self.agir("prendre clé")
        self.agir("ouest")
        data = copy.deepcopy(self.m.data)
        m = Monde(data)
        self.assertEqual(m.joueur["salle"], "echoppe")
        self.assertEqual(m.objets["cle"]["lieu"], "joueur")
        self.assertEqual(m.data["minutes"], self.m.data["minutes"])
        self.assertEqual(m.data["journal"], self.m.data["journal"])
        self.assertEqual(Monde(copy.deepcopy(m.data)).data, m.data)

    def test_scene_unifiee_et_compteurs_reserves_a_examen(self):
        texte = regarder(self.m)
        self.assertIn("clé du veilleur", texte)
        self.assertIn("Sorties :", texte)
        self.assertNotIn("Combustible", texte)
        self.assertFalse(any(ligne.startswith("  ") for ligne in texte.splitlines()))
        self.assertIn("Combustible restant", self.agir("examiner torche"))


if __name__ == "__main__":
    unittest.main()
