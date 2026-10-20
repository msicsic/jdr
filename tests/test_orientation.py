"""Orientation et cône de vision : on ne voit pas dans son dos, on se retourne au bruit, on
regarde autour de soi avant un geste qu'on veut sans témoin ; tourner prend du temps."""
from pathlib import Path
import tempfile
import unittest

from tests.support import calme, regarder
from donjon.defi import nouveau_defi
from donjon.esprits import lire, percevoir_tous, percoit
from donjon.geometrie import placer
from donjon.monde import Monde
from donjon.ouie import retentir
from donjon.pnj import PAS, _marcher, tour_d_horizon
from donjon.spatial import QUART, dans_le_cone, installer, quarts


def relais():
    m = nouveau_defi()
    installer(m)
    return calme(m, "marchand", "brune", "ilse", "aubin")


def poser(m, id, salle, case):
    m.objets[id]["lieu"] = salle
    placer(m.objets[id], salle, case)


class ConeTests(unittest.TestCase):
    def test_le_cone_couvre_l_avant_et_les_cotes_immediats(self):
        self.assertTrue(dans_le_cone((0, 0), "est", (5, 2)))
        self.assertTrue(dans_le_cone((0, 0), "est", (0, 1)))   # juste à côté
        self.assertFalse(dans_le_cone((0, 0), "est", (0, 3)))  # sur le côté, plus loin
        self.assertFalse(dans_le_cone((0, 0), "est", (-1, 0)))  # dans le dos
        self.assertEqual((quarts("nord", "sud"), quarts("est", "nord-est")), (4, 1))

    def test_dans_son_dos_il_ne_voit_personne_et_l_orientation_se_recharge(self):
        m = relais()
        poser(m, "marchand", "antichambre", [5, 5])
        poser(m, "ilse", "antichambre", [2, 5])
        regarder(m, "marchand", [8, 5])
        percevoir_tous(m)
        self.assertFalse(percoit(m, "marchand", "ilse"))
        regarder(m, "marchand", "ilse")
        self.assertTrue(percoit(m, "marchand", "ilse"))
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)
            self.assertEqual(Monde.charger(chemin).objets["marchand"]["orientation"], "ouest")


class RetournerTests(unittest.TestCase):
    def test_des_pas_tout_proches_le_font_se_retourner(self):
        m = relais()
        poser(m, "marchand", "antichambre", [5, 5])
        poser(m, "ilse", "antichambre", [3, 5])
        regarder(m, "marchand", [8, 5])
        lire(m, "marchand")["croyances"].pop("ilse")  # Il ne la sait pas là.
        m.data["dixiemes"] = 100
        retentir(m, "ilse", "aller")
        self.assertEqual(m.objets["marchand"]["orientation"], "ouest")
        self.assertTrue(percoit(m, "marchand", "ilse"))
        self.assertEqual(lire(m, "marchand")["libre"], 100 + 4 * QUART)  # Un demi-tour : 2 s.

    def test_tourner_s_ajoute_au_pas(self):
        m = relais()
        poser(m, "ilse", "antichambre", [5, 5])
        regarder(m, "ilse", [8, 5])
        duree = _marcher(m, "ilse", lambda salle, case: salle == "antichambre" and case == (4, 5), [])
        self.assertEqual(duree, 4 * QUART + PAS)
        self.assertEqual(m.objets["ilse"]["orientation"], "ouest")


class TourDHorizonTests(unittest.TestCase):
    def test_un_tour_d_horizon_voit_tout_autour_puis_reprend_son_orientation(self):
        m = relais()
        poser(m, "brune", "antichambre", [5, 5])
        poser(m, "marchand", "antichambre", [2, 5])
        regarder(m, "brune", [8, 5])
        self.assertFalse(percoit(m, "brune", "marchand"))
        self.assertIn("marchand", tour_d_horizon(m, "brune"))
        self.assertEqual(m.objets["brune"]["orientation"], "est")
        self.assertEqual(lire(m, "brune")["croyances"]["marchand"]["lieu"]["valeur"], "antichambre")


if __name__ == "__main__":
    unittest.main()
