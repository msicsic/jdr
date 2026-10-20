import unittest

from donjon.monde import ErreurMonde, nouveau_monde
from donjon import spatial


def monde_eclaire():
    m = nouveau_monde()
    spatial.installer(m)
    m.joueur.pop("orientation")  # Géométrie des lignes de vue seule : le regard tout autour.
    m.objets["torche"]["allume"] = True
    m.objets["torche"]["combustible"] = 10
    return m


class SpatialTests(unittest.TestCase):
    def test_installer_active_le_mode_et_initialise_la_memoire(self):
        m = nouveau_monde()
        spatial.installer(m)
        self.assertTrue(spatial.active(m))
        self.assertEqual(set(m.data["exploration"]), set(m.data["salles"]))
        porte = m.objets["porte"]["positions_salles"]
        self.assertEqual(set(porte), {"antichambre", "crypte"})
        self.assertEqual(spatial.destination_appui(m, "inexistant", "antichambre"), None)
        self.assertIn([1, 2], m.data["exploration"]["antichambre"])

    def test_ligne_de_vue_est_bloquee_par_un_objet_opaque(self):
        m = monde_eclaire()
        m.joueur["position"] = [1, 2]
        self.assertTrue(spatial.visible(m, "cle"))
        obstacle = {"id": "paravent", "type": "decoration", "lieu": "antichambre",
                    "position_salle": "antichambre", "position": [2, 2],
                    "bloque_vue": True, "bloque_passage": False}
        m.objets["paravent"] = obstacle
        self.assertFalse(spatial.visible(m, "cle"))

    def test_los_diagonal_ne_fuit_pas_entre_un_vide_et_un_obstacle_opaque(self):
        m = monde_eclaire()
        m.joueur["position"] = [1, 1]
        plan = m.data["salles"]["antichambre"]["plan"]
        plan["sol"][2] = plan["sol"][2][:1] + " " + plan["sol"][2][2:]
        m.objets["cle"]["position"] = [2, 2]
        m.objets["mur_diagonal"] = {"id": "mur_diagonal", "type": "deco",
            "lieu": "antichambre", "position_salle": "antichambre", "position": [2, 1],
            "bloque_vue": True}
        self.assertFalse(spatial.visible(m, "cle"))

    def test_visible_respecte_le_rayon_de_champ_visible(self):
        m = monde_eclaire()
        m.objets["torche"].update(luminosite=1, position=[0, 1])
        m.objets["lanterne"]["allume"] = False
        m.joueur["position"] = [1, 1]
        m.objets["cle"]["position"] = [5, 1]
        # Hors de portée directe de la torche, la clé n'est que dans la pénombre diffuse.
        self.assertNotIn(("antichambre", 5, 1), spatial.champ_visible(m))
        self.assertFalse(spatial.visible(m, "cle"))
        # Torche posée près de la clé : sa lumière directe la rend visible de plus loin.
        m.objets["torche"]["position"] = [4, 1]
        self.assertIn(("antichambre", 5, 1), spatial.champ_visible(m))
        self.assertTrue(spatial.visible(m, "cle"))

    def test_proximite_et_coin_diagonal(self):
        m = monde_eclaire()
        m.joueur["position"] = [2, 1]
        self.assertTrue(spatial.proche(m, "cle"))
        m.joueur["position"] = [1, 1]
        self.assertFalse(spatial.proche(m, "cle"))
        # Deux côtés bloqués interdisent l'approche diagonale.
        for id, p in (("mur_a", [3, 1]), ("mur_b", [2, 2])):
            m.objets[id] = {"id": id, "type": "decoration", "lieu": "antichambre",
                            "position_salle": "antichambre", "position": p,
                            "bloque_passage": True}
        m.joueur["position"] = [2, 1]
        m.objets["cle"]["position"] = [3, 2]
        self.assertFalse(spatial.proche(m, "cle"))

    def test_pas_franchit_les_sorties_et_refuse_porte_fermee(self):
        m = monde_eclaire()
        m.joueur["salle"] = "antichambre"
        m.joueur["position"] = [3, 0]
        with self.assertRaises(ErreurMonde):
            spatial.preparer_pas(m, "nord")
        m.objets["porte"]["ouverte"] = True
        self.assertEqual(spatial.preparer_pas(m, "nord"),
                         {"salle": "crypte", "position": [3, 6]})
        m.joueur["position"] = [0, 1]
        self.assertEqual(spatial.preparer_pas(m, "ouest"),
                         {"salle": "echoppe", "position": [4, 3]})

    def test_porte_detruite_mais_ouverte_laisse_passer(self):
        m = monde_eclaire()
        m.joueur["position"] = [3, 0]
        m.objets["porte"].update(ouverte=True, integrite=0)
        self.assertEqual(spatial.preparer_pas(m, "nord"),
                         {"salle": "crypte", "position": [3, 6]})

    def test_mur_interne_et_collision_bloquent_le_pas(self):
        m = monde_eclaire()
        m.joueur["position"] = [5, 0]
        with self.assertRaises(ErreurMonde):
            spatial.preparer_pas(m, "est")
        m.objets["baril"] = {"id": "baril", "type": "objet", "lieu": "antichambre",
                             "position_salle": "antichambre", "position": [2, 1],
                             "bloque_passage": True}
        m.joueur["position"] = [1, 1]
        with self.assertRaises(ErreurMonde):
            spatial.preparer_pas(m, "est")

    def test_exploration_memorise_seulement_le_terrain_visible(self):
        m = monde_eclaire()
        champ = spatial.champ_visible(m)
        self.assertIn(("antichambre", 1, 2), champ)
        self.assertNotIn(("crypte", 3, 6), champ)  # La porte est fermée.
        spatial.memoriser(m)
        self.assertIn([1, 2], m.data["exploration"]["antichambre"])
        self.assertNotIn("cle", str(m.data["exploration"]))
        m.objets["porte"]["ouverte"] = True
        m.joueur["position"] = [3, 0]
        m.objets["coffre"]["position"] = [3, 6]
        self.assertIn(("crypte", 3, 6), spatial.champ_visible(m))
        self.assertTrue(spatial.visible(m, "coffre"))

    def test_sortie_visible_et_objet_de_lautre_salle_demande_le_pas_de_portail(self):
        m = monde_eclaire()
        m.joueur["position"] = [3, 0]
        self.assertTrue(spatial.sortie_visible(m, "antichambre", "nord"))
        m.objets["porte"]["ouverte"] = True
        m.objets["coffre"]["position"] = [3, 6]
        # Le coffre est à deux cases globales du personnage : il faut franchir le seuil avant l'interaction.
        self.assertFalse(spatial.proche(m, "coffre"))
        pas = spatial.preparer_pas(m, "nord")
        m.joueur.update(salle=pas["salle"], position=pas["position"])
        self.assertTrue(spatial.proche(m, "coffre"))

    def test_objet_opaque_porte_nocclut_pas_la_vue(self):
        m = monde_eclaire()
        m.joueur["position"] = [1, 2]
        m.objets["cle"]["position"] = [3, 2]
        m.objets["voile"] = {"id": "voile", "type": "objet", "lieu": "joueur",
                              "bloque_vue": True}
        self.assertTrue(spatial.visible(m, "cle"))

    def test_verifier_refuse_position_joueur_et_memoire_invalides(self):
        m = monde_eclaire()
        m.joueur["position"] = [20, 20]
        with self.assertRaises(AssertionError):
            spatial.verifier(m)
        m.joueur["position"] = [1, 2]
        m.data["exploration"]["antichambre"] = [[99, 99]]
        with self.assertRaises(AssertionError):
            spatial.verifier(m)

    def test_objet_dans_contenant_ferme_et_fixation_de_lautre_cote_restent_caches(self):
        m = monde_eclaire()
        m.joueur["salle"] = "crypte"
        m.joueur["position"] = [3, 5]
        m.objets["torche"]["lieu"] = "joueur"
        self.assertFalse(spatial.visible(m, "anneau"))
        m.joueur["salle"] = "antichambre"
        m.objets["axe_haut"]["position_salle"] = "antichambre"
        m.objets["axe_haut"]["position"] = [2, 2]
        self.assertFalse(spatial.visible(m, "axe_haut"))

    def test_positions_des_extremites_verticales_et_echelle_installee(self):
        m = monde_eclaire()
        m.data["salles"]["haut"] = {"nom": "Palier", "sorties": {},
                                     "plan": {"origine": [30, 0], "sol": ["..."], "repere": "H"}}
        m.objets["appui_test"] = {"id": "appui_test", "type": "surface", "lieu": "antichambre",
            "appui_vertical": {"bas": "antichambre", "haut": "haut",
                                "position_bas": [4, 2], "position_haut": [1, 0]}}
        m.objets["echelle_test"] = {"id": "echelle_test", "type": "assemblage", "lieu": "antichambre",
                                    "position_salle": "antichambre", "position": [4, 2],
                                    "installation": {"support": "appui_test"}}
        self.assertEqual(spatial.destination_appui(m, "appui_test", "haut"), (1, 0))
        self.assertEqual(spatial.position_cible(m, "echelle_test", "haut"), (1, 0))
        self.assertEqual(spatial.position_cible(m, "appui_test", "antichambre"), (4, 2))

    def test_destination_appui_refuse_case_occupee_par_un_solide(self):
        m = monde_eclaire()
        m.objets["appui_solide"] = {"id": "appui_solide", "type": "surface",
            "nom": "mur concret", "lieu": "antichambre",
            "appui_vertical": {"bas": "antichambre", "haut": "crypte",
                                "position_bas": [4, 2], "position_haut": [1, 1]}}
        m.objets["bloc"] = {"id": "bloc", "type": "objet", "lieu": "antichambre",
                            "position_salle": "antichambre", "position": [4, 2],
                            "bloque_passage": True}
        with self.assertRaises(ErreurMonde):
            spatial.destination_appui(m, "appui_solide", "antichambre")

    def test_sol_et_plafond_non_positionnes_suivent_le_joueur(self):
        m = monde_eclaire()
        m.joueur["position"] = [5, 3]
        self.assertEqual(spatial.position_cible(m, "antichambre_sol"), (5, 3))
        self.assertEqual(spatial.position_cible(m, "antichambre_plafond"), (5, 3))
        self.assertTrue(spatial.proche(m, "antichambre_sol"))
        self.assertTrue(spatial.visible(m, "antichambre_plafond"))
        m.objets["mur_appui"] = {"id": "mur_appui", "type": "surface",
            "nom": "mur concret", "lieu": "antichambre",
            "appui_vertical": {"bas": "antichambre", "haut": "crypte",
                                "position_bas": [4, 2], "position_haut": [1, 1]}}
        self.assertEqual(spatial.position_cible(m, "mur_appui"), (4, 2))

    def test_piece_voisine_sombre_ne_devient_pas_visible_par_le_rayon_courant(self):
        m = nouveau_monde()
        antichambre = m.data["salles"]["antichambre"]
        antichambre["sorties"]["sud"] = {"vers": "sombre", "porte": None, "case": [2, 4]}
        m.data["salles"]["sombre"] = {"nom": "Salle sombre", "sorties": {
            "nord": {"vers": "antichambre", "porte": None, "case": [1, -1]}},
            "fenetres": 0, "lumiere_naturelle": 0,
            "plan": {"origine": [9, 15], "sol": ["..."], "repere": "S"}}
        m.joueur["position"] = [2, 3]
        m.objets["lanterne"]["allume"] = False
        # Torche hors d'axe : sa lumière directe n'atteint pas la salle voisine.
        m.objets["torche"].update(allume=True, luminosite=1, combustible=10, position=[5, 0])
        m.objets["boite_sombre"] = {"id": "boite_sombre", "type": "objet", "lieu": "sombre",
            "position_salle": "sombre", "position": [1, 0]}
        spatial.installer(m)
        from donjon.perception import eclairage
        self.assertGreater(eclairage(m, "antichambre")["niveau"], 0)
        self.assertEqual(eclairage(m, "sombre")["niveau"], 0)
        self.assertNotIn(("sombre", 1, 0), spatial.champ_visible(m))
        self.assertFalse(spatial.visible(m, "boite_sombre"))

    def test_champ_voit_par_un_portail_sans_voir_toute_la_frontiere_voisine(self):
        m = nouveau_monde()
        m.data["salles"]["antichambre"]["sorties"]["sud"] = {
            "vers": "piece_voisine", "porte": None, "case": [2, 4]}
        m.data["salles"]["piece_voisine"] = {"nom": "Pièce voisine", "sorties": {
            "nord": {"vers": "antichambre", "porte": None, "case": [1, -1]}},
            "fenetres": 0, "lumiere_naturelle": 2,
            "plan": {"origine": [9, 15], "sol": ["..."], "repere": "V"}}
        m.joueur["position"] = [2, 3]
        spatial.installer(m)
        m.joueur["orientation"] = "sud"  # Il regarde par le portail.
        vus = {p for salle, x, y in spatial.champ_visible(m)
               if salle == "piece_voisine" for p in ((x, y),)}
        self.assertIn((1, 0), vus)
        self.assertLess(len(vus), 3)

    def test_verifier_refuse_sols_superposes_au_meme_niveau(self):
        m = nouveau_monde()
        m.data["salles"]["echoppe"]["plan"]["origine"] = [8, 10]
        with self.assertRaisesRegex(AssertionError, "Sols superposés"):
            spatial.verifier(m)

    def test_verifier_refuse_seuil_divergent_ou_sortie_sans_reciproque(self):
        m = nouveau_monde()
        m.data["salles"]["antichambre"]["sorties"]["ouest"]["case"] = [-1, 0]
        with self.assertRaisesRegex(AssertionError, "Seuils globaux divergents"):
            spatial.verifier(m)
        m = nouveau_monde()
        del m.data["salles"]["echoppe"]["sorties"]["est"]
        with self.assertRaisesRegex(AssertionError, "réciproque opposée"):
            spatial.verifier(m)

    def test_verifier_accepte_escalier_entre_niveaux_distincts(self):
        m = nouveau_monde()
        crypt = m.data["salles"]["crypte"]
        crypt["altitude_cm"] = 240
        crypt["plan"]["origine"] = [30, 20]
        m.data["salles"]["antichambre"]["sorties"]["nord"]["escalier"] = True
        crypt["sorties"]["sud"]["escalier"] = True
        spatial.verifier(m)

    def test_migration_ancienne_partie_revele_les_salles_visitees_entieres(self):
        m = nouveau_monde()
        m.data.pop("exploration", None)
        m.data["journal"].append({"action": {"action": "ouvrir"}})
        m.data["visitees"] = ["antichambre", "echoppe"]
        spatial.installer(m)
        for salle in m.data["visitees"]:
            attendues = {tuple(p) for p in spatial.cases(m.data["salles"][salle])}
            self.assertEqual({tuple(p) for p in m.data["exploration"][salle]}, attendues)
        self.assertFalse(m.data["exploration"]["crypte"])

    def test_nouvelle_partie_ne_revele_pas_une_salle_visitee_hors_vue(self):
        m = nouveau_monde()
        self.assertFalse(m.data["journal"])
        self.assertIn("echoppe", m.data["visitees"])
        spatial.installer(m)
        cases_echoppe = spatial.cases(m.data["salles"]["echoppe"])
        explorees = {tuple(p) for p in m.data["exploration"]["echoppe"]}
        self.assertLess(len(explorees), len(cases_echoppe))


if __name__ == "__main__":
    unittest.main()
