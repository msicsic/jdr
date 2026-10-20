"""La scène perçue : chaque chose avec son identité, rien de ce que le joueur ne perçoit pas."""
import json
import unittest

from tests.support import calme, regarder
from donjon.defi import nouveau_defi
from donjon.geometrie import placer
from donjon.scene import scene_percue
from donjon.spatial import installer, memoriser


def relais():
    m = nouveau_defi()
    installer(m)
    return calme(m, "marchand", "brune", "ilse", "aubin")


def objets(scene):
    return {o["id"]: o for n in scene["niveaux"] for o in n["objets"]}


def souvenirs(scene):
    return {s["id"]: s for n in scene["niveaux"] for s in n["souvenirs"]}


class ScenePercueTests(unittest.TestCase):
    def test_rien_de_ce_qu_il_ne_percoit_pas(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[5, 5], orientation="est")
        m.objets["marteau"].update(lieu="antichambre", position=[3, 5], position_salle="antichambre")
        scene = scene_percue(m)
        vus = objets(scene)
        self.assertNotIn("marteau", vus)  # Dans son dos.
        for id in vus:
            self.assertTrue(m.visible(id), id)
        json.dumps(scene)  # Elle part telle quelle vers la page.

    def test_chaque_chose_a_son_identite_et_son_nom(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[2, 5], orientation="nord-est")
        vus = objets(scene_percue(m))
        self.assertTrue(vus)
        for id, o in vus.items():
            self.assertEqual(o["id"], id)
            self.assertTrue(o["nom"])
            self.assertEqual(len(o["case"]), 2)

    def test_un_personnage_vu_avec_son_regard_et_ce_qu_il_porte_visiblement(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[1, 5], orientation="est")
        m.objets["marchand"]["lieu"] = "antichambre"
        placer(m.objets["marchand"], "antichambre", [4, 5])
        regarder(m, "marchand", [8, 5])
        m.objets["pied_de_biche"].update(lieu="marchand")
        m.objets["pied_de_biche"].pop("position", None)
        gorm = objets(scene_percue(m))["marchand"]
        self.assertEqual(gorm["orientation"], "est")
        self.assertEqual([x["id"] for x in gorm["porte"]], ["pied_de_biche"])  # Ni sa barbe ni ses mains.

    def test_ce_qu_il_ne_voit_plus_reste_un_souvenir_a_sa_place(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[5, 5], orientation="ouest")
        m.objets["marteau"].update(lieu="antichambre", position=[3, 5], position_salle="antichambre")
        memoriser(m)
        self.assertIn("marteau", objets(scene_percue(m)))
        m.joueur["orientation"] = "est"
        scene = scene_percue(m)
        self.assertNotIn("marteau", objets(scene))
        self.assertEqual(souvenirs(scene)["marteau"]["case"], [3, 5])

    def test_son_regard_et_sa_place_dans_le_repere_commun(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[2, 3], orientation="nord-est")
        j = scene_percue(m)["joueur"]
        ox, oy = m.data["salles"]["antichambre"]["plan"]["origine"]
        self.assertEqual((j["orientation"], j["globale"]), ("nord-est", [ox + 2, oy + 3]))

    def test_la_lumiere_de_chaque_case_vue_suit_le_moteur(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[1, 3], orientation="est")

        def degres():
            salle = next(s for n in scene_percue(m)["niveaux"] for s in n["salles"] if s["id"] == "antichambre")
            return {tuple(c["case"]): c.get("lumiere") for c in salle["cases"]}

        memoriser(m)
        self.assertEqual(degres()[tuple(m.objets["fanal"]["position"])], "pleine")
        for o in m.objets.values():
            if o.get("allume"):
                o["allume"] = False
        self.assertFalse({"pleine", "directe"} & set(degres().values()))
        m.joueur["orientation"] = "ouest"
        self.assertIsNone(degres()[(4, 5)])  # Hors de vue : un souvenir, sans lumière.


if __name__ == "__main__":
    unittest.main()
