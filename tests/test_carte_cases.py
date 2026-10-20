import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from donjon.carte import carte
from donjon.defi import nouveau_defi
from donjon.faits_locaux import preparer_faits
from donjon.monde import Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.spatial import installer, memoriser


class CarteCasesTests(unittest.TestCase):
    def setUp(self):
        self.monde = nouveau_monde()
        installer(self.monde)

    def test_noir_ne_revele_pas_les_murs_inconnus(self):
        self.monde.objets["lanterne"]["allume"] = False
        self.monde.objets["brasero"]["allume"] = False
        self.monde.data["exploration"] = {salle: [] for salle in self.monde.data["salles"]}
        self.monde.data["exploration"][self.monde.joueur["salle"]] = [list(self.monde.joueur["position"])]
        self.monde.data["murs_memorises"] = {}
        plan = carte(self.monde).split("=== LEGENDE ===")[0]
        self.assertIn("@", plan)
        self.assertNotIn("##", plan)
        self.assertNotIn(" x ", carte(self.monde).split("=== LEGENDE ===")[1])

    def test_murs_vus_restent_memorises_apres_extinction_et_rechargement(self):
        murs = self.monde.data["murs_memorises"]
        self.assertTrue(murs["antichambre"])
        self.monde.objets["lanterne"]["allume"] = False
        plan = carte(self.monde).split("=== LEGENDE ===")[0]
        self.assertIn("##", plan)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "murs.json"
            self.monde.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.data["murs_memorises"], murs)
        self.assertIn("##", carte(reprise).split("=== LEGENDE ===")[0])

    def test_memorise_terrain_visible_objets_et_salles_inconnues(self):
        salle = self.monde.joueur["salle"]
        self.monde.data["exploration"][salle] = [[1, 2], [2, 2], [3, 2]]
        with patch("donjon.spatial.champ_visible", return_value={(salle, 2, 1)}):
            plan = carte(self.monde)
        self.assertIn(". ", plan)
        self.assertIn(": ", plan)
        self.assertNotIn("Crypte", plan)
        self.assertNotIn("coffre", plan)
        self.assertIn("cases vides : inconnues", plan)
        self.assertIn("coordonnées (x, y)", plan)
        self.assertIn("F6 puis flèches", plan)

    def test_carte_cases_reste_active_apres_deplacement_de_position(self):
        salle = self.monde.joueur["salle"]
        self.monde.data["exploration"][salle] = [[1, 2], [2, 2], [3, 2]]
        with patch("donjon.spatial.champ_visible", return_value={(salle, 2, 1)}):
            avant = carte(self.monde)
            self.monde.joueur["position"] = [2, 2]
            apres = carte(self.monde)
        self.assertIn("@", avant)
        self.assertIn("@", apres)
        self.assertIn("NIVEAU", apres)

    def test_echelle_affiche_son_extremite_inconnue_sans_reveler_la_salle(self):
        support = objet("mur_vertical", "mur vertical", "surface", "antichambre",
                        appui_vertical={"bas": "antichambre", "haut": "crypte",
                                        "position_bas": [4, 1], "position_haut": [4, 5]})
        echelle = objet("echelle_test", "échelle de branches", "assemblage", "antichambre",
                        installation={"support": "mur_vertical"}, position=[4, 1],
                        position_salle="antichambre")
        self.monde.objets.update({"mur_vertical": support, "echelle_test": echelle})
        self.monde.data["salles"]["crypte"]["niveau"] = 1
        self.monde.data["exploration"]["antichambre"] = [[1, 2], [2, 1], [2, 2], [3, 2], [4, 1]]
        with patch("donjon.spatial.champ_visible", return_value={("antichambre", 2, 1)}):
            plan = carte(self.monde)
        self.assertIn("NIVEAU +1", plan)
        self.assertGreaterEqual(plan.count("H1"), 2)
        self.assertNotIn("Crypte du veilleur", plan)

    def test_etat_porte_visible_seulement_au_seuil_et_souvenir_sans_etat(self):
        self.monde.data["souvenirs_portes"] = {}
        self.monde.data["exploration"]["antichambre"] = [[1, 2], [3, 0]]
        with patch("donjon.spatial.champ_visible", return_value={("antichambre", 1, 2)}), \
             patch("donjon.spatial.sortie_visible", return_value=False):
            cachee = carte(self.monde)
        self.assertIn(": ", cachee)
        self.assertNotIn("porte verrouillée", cachee)
        with patch("donjon.spatial.champ_visible", return_value={("antichambre", 1, 2)}), \
             patch("donjon.spatial.sortie_visible", return_value=True):
            vue = carte(self.monde)
        self.assertIn("X ", vue)
        self.assertIn("porte verrouillée", vue)

    def test_porte_vue_reste_un_souvenir_apres_deplacement_et_rechargement(self):
        m = nouveau_defi()
        installer(m)
        self.assertNotIn("porte", m.data.get("souvenirs_portes", {}))
        m.joueur.update(salle="crypte", position=[4, 0])
        memoriser(m)
        self.assertEqual(m.data["souvenirs_portes"]["porte"], "X")
        moteur = Moteur(m)
        for direction in ["sud"] * 5 + ["ouest"] * 4:
            moteur.executer(moteur.preparer(proposition("marcher", direction)))
        self.assertEqual(m.joueur["position"], [0, 5])
        self.assertIn("~X", carte(m).split("=== LEGENDE ===")[0])

        # Un changement hors champ ne révèle pas le nouvel état de la porte.
        m.objets["porte"].update(ouverte=True, verrouillee=False)
        self.assertIn("~X", carte(m).split("=== LEGENDE ===")[0])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "porte.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.data["souvenirs_portes"]["porte"], "X")
        self.assertIn("~X", carte(reprise).split("=== LEGENDE ===")[0])

        moteur = Moteur(reprise)
        for direction in ["est"] * 4 + ["nord"] * 5:
            moteur.executer(moteur.preparer(proposition("marcher", direction)))
        self.assertEqual(reprise.data["souvenirs_portes"]["porte"], "/")
        self.assertNotIn("~X", carte(reprise).split("=== LEGENDE ===")[0])

    def test_consigne_du_relais_est_dessinee_sur_le_mur_et_memorisee_apres_rechargement(self):
        m = nouveau_defi()
        installer(m)
        dessin = carte(m).split("=== LEGENDE ===")[0]
        self.assertIn("!#", dessin)
        self.assertEqual(m.data["souvenirs_visuels"]["gravure"]["position"], [3, 3])
        self.assertEqual(m.data["souvenirs_visuels"]["gravure"]["contact"], [2, 3])

        m.joueur["position"] = [7, 3]
        memoriser(m)
        self.assertFalse(m.visible("gravure"))
        self.assertIn("!~", carte(m).split("=== LEGENDE ===")[0])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "consigne.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertIn("!~", carte(reprise).split("=== LEGENDE ===")[0])
        reprise.joueur["position"] = [1, 3]
        memoriser(reprise)
        self.assertIn("!#", carte(reprise).split("=== LEGENDE ===")[0])
        self.assertNotIn("!~", carte(reprise).split("=== LEGENDE ===")[0])

    def test_objet_invente_sur_un_autre_mur_garde_son_ancrage_dans_le_noir(self):
        m = nouveau_monde()
        installer(m)
        m.joueur["orientation"] = "ouest"  # Placement d'auteur : il regarde le mur ouest.
        m, _, etablis = preparer_faits(m, {"ajouts": [{
            "type": "objet", "ancrage": "antichambre_murs",
            "nom": "anneau de fer", "genre": "m", "texte": "Le fer est rouillé.",
            "materiau": "fer", "masse": 0.1, "mobile": True,
            "relation": "fixe", "capacites": []}]})
        id = etablis[0]["objet"]
        memoriser(m)
        self.assertEqual(m.objets[id]["ancrage_carte"], [-1, 2])
        self.assertIn("!#", carte(m).split("=== LEGENDE ===")[0])

        m.objets["lanterne"]["allume"] = False
        m.objets["brasero"]["allume"] = False
        memoriser(m)
        self.assertFalse(m.visible(id))
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "mur.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.data["souvenirs_visuels"][id]["position"], [-1, 2])
        self.assertIn("!~", carte(reprise).split("=== LEGENDE ===")[0])

    def test_obstacle_opaque_est_representable_sur_la_carte(self):
        pilier = objet("pilier_test", "pilier de pierre", "contenant", "antichambre",
                       materiau="pierre", ouverte=False, verrouillee=False,
                       bloque_vue=True, bloque_passage=True,
                       position=[2, 1], position_salle="antichambre")
        self.monde.objets["pilier_test"] = pilier
        with patch("donjon.spatial.champ_visible", return_value={
                ("antichambre", 1, 2), ("antichambre", 2, 1)}):
            plan = carte(self.monde)
        self.assertIn("O ", plan)
        self.assertIn("O le pilier de pierre", plan)

    def test_escalier_change_de_glyph_selon_altitude_sans_nommer_destination_inconnue(self):
        self.monde.data["salles"]["crypte"]["niveau"] = 1
        self.monde.data["salles"]["antichambre"]["sorties"]["nord"]["escalier"] = True
        self.monde.data["exploration"]["antichambre"] = [[1, 2], [3, 0]]
        with patch("donjon.spatial.champ_visible", return_value={("antichambre", 1, 2)}), \
             patch("donjon.spatial.sortie_visible", return_value=True):
            plan = carte(self.monde)
        self.assertIn("^", plan)
        self.assertIn("escalier montant", plan)
        self.assertNotIn("Crypte du veilleur", plan)

    def test_symbole_de_source_lumineuse_suit_son_etat(self):
        self.monde.objets["torche"]["allume"] = True
        avec_lumiere = {("antichambre", 1, 2), ("antichambre", 4, 1)}
        with patch("donjon.spatial.champ_visible", return_value=avec_lumiere):
            allumee = carte(self.monde)
        self.assertIn("* la torche", allumee)
        self.monde.objets["torche"]["allume"] = False
        with patch("donjon.spatial.champ_visible", return_value=avec_lumiere):
            eteinte = carte(self.monde)
        self.assertIn("t la torche", eteinte)

    def test_objet_hors_vue_garde_sa_derniere_position_sans_reveler_son_deplacement(self):
        salle = "antichambre"
        ancien = (salle, 3, 2)
        nouveau = (salle, 4, 2)
        self.monde.data["souvenirs_visuels"] = {}
        with patch("donjon.spatial.champ_visible", return_value={ancien}):
            memoriser(self.monde)
        self.assertEqual(self.monde.data["souvenirs_visuels"]["cle"]["position"], [3, 2])

        self.monde.objets["cle"]["position"] = [4, 2]
        with patch("donjon.spatial.champ_visible", return_value={(salle, 1, 2)}):
            memoriser(self.monde)
            plan = carte(self.monde)
        self.assertIn("~k", plan)
        self.assertIn("~k la clé du veilleur", plan)
        self.assertIn("présence ou état actuels non confirmés", plan)
        self.assertEqual(self.monde.data["souvenirs_visuels"]["cle"]["position"], [3, 2])
        self.assertFalse(any(v["salle"] == nouveau[0] and tuple(v["position"]) == nouveau[1:]
                             for v in self.monde.data["souvenirs_visuels"].values()))
        with patch("donjon.spatial.champ_visible", return_value={(salle, 1, 2)}):
            self.assertIn({"nom": "la clé du veilleur", "derniere_salle": "Antichambre"},
                          self.monde.contexte()["souvenirs_visuels"])

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "souvenir.json"
            self.monde.sauver(chemin)
            reprise = Monde.charger(chemin)
        with patch("donjon.spatial.champ_visible", return_value={(salle, 1, 2)}):
            self.assertIn("~k", carte(reprise))

        with patch("donjon.spatial.champ_visible", return_value={ancien}):
            memoriser(reprise)
            self.assertNotIn("~k", carte(reprise))
        self.assertNotIn("cle", reprise.data["souvenirs_visuels"])

    def test_pnj_hors_vue_reste_un_souvenir(self):
        self.monde.objets["marchand"].update(lieu="antichambre", position_salle="antichambre", position=[2, 1])
        self.monde.data["souvenirs_visuels"] = {}
        with patch("donjon.spatial.champ_visible", return_value={("antichambre", 2, 1)}):
            memoriser(self.monde)
        with patch("donjon.spatial.champ_visible", return_value={("antichambre", 1, 2)}):
            self.assertIn("~G Gorm le marchand", carte(self.monde))


if __name__ == "__main__":
    unittest.main()
