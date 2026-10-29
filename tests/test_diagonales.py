"""Une géométrie juste : un pas en diagonale dure √2 fois un pas droit, pour le joueur et les PNJ,
à toute allure ; les chemins sont les plus courts en temps ; les portées (lumière, vue, ouïe, voix)
se mesurent en distance réelle, et une case voisine en diagonale reste au contact.

Vérifié sur l'état du monde après rechargement."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from donjon.esprits import lire
from donjon.geometrie import distance, racine
from donjon.moteur import Moteur, proposition
from donjon.ouie import perte
from donjon.perception import CarteLumiere
from donjon.pnj import PAS, _marcher, de_pres
from donjon.spatial import _global, trajet
from donjon.temps import PAS_CHASSE, PAS_FEUTRE, PAS_JOUEUR, duree_pas, instant
from tests.support import calme
from tests.test_tensions import placer, recharger, relais


def galerie():
    """La galerie de la cloche (7 × 15 cases, dégagée), le joueur seul, les PNJ à la crypte."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("marchand", "brune", "ilse", "aubin")):
        placer(m, id, "crypte", (2 + n, 3))
    m.joueur.update(salle="chambre_cloche", position=[0, 0], orientation="sud-est")
    return recharger(m)


def faire(m, action, cible=""):
    moteur = Moteur(m)
    return moteur.executer(moteur.preparer(proposition(action, cible)))


class RegleTests(unittest.TestCase):
    def test_une_duree_et_une_distance_declarees_une_fois(self):
        # √2 arrondi au dixième de seconde le plus proche, en entiers.
        self.assertEqual([duree_pas(a, (1, 1)) for a in (PAS_JOUEUR, PAS_CHASSE, PAS_FEUTRE)], [21, 42, 42])
        self.assertEqual([duree_pas(a, (0, -1)) for a in (PAS_JOUEUR, PAS_CHASSE, PAS_FEUTRE)], [15, 30, 30])
        self.assertEqual(duree_pas(PAS, (-1, 1)), 21)
        import math
        self.assertTrue(all(racine(n) == round(math.sqrt(n)) for n in range(1, 5000)))
        # Distance réelle, arrondie à la case : au contact en diagonale, des disques au-delà.
        self.assertEqual([distance((0, 0), (k, k)) for k in range(1, 7)], [1, 3, 4, 6, 7, 8])
        self.assertEqual([distance((0, 0), (k, 0)) for k in range(1, 7)], [1, 2, 3, 4, 5, 6])
        self.assertEqual(distance((2, 5), (3, 4)), 1)


class MarcheJoueurTests(unittest.TestCase):
    """Le même nombre de pas, droit ou en diagonale, ne prend pas le même temps."""

    def marche(self, regard, action, sens, fois=4):
        m = galerie()
        m.joueur["orientation"] = regard
        depart = instant(m)
        for _ in range(fois):
            faire(m, action, sens)
        m = recharger(m)
        return m, instant(m) - depart

    def test_pas_droits_et_pas_en_diagonale(self):
        droit, t_droit = self.marche("est", "marcher", "est")
        biais, t_biais = self.marche("sud-est", "marcher", "sud-est")
        self.assertEqual((droit.joueur["position"], biais.joueur["position"]), ([4, 0], [4, 4]))
        self.assertEqual((t_droit, t_biais), (4 * 15, 4 * 21))

    def test_a_toute_allure(self):
        # Pas feutrés : face à la direction, sans rotation.
        _, t_droit = self.marche("est", "faufiler", "est")
        m, t_biais = self.marche("sud-est", "faufiler", "sud-est")
        self.assertEqual((t_droit, t_biais), (4 * 30, 4 * 42))
        self.assertEqual(m.joueur["position"], [4, 4])
        # Pas chassés, de côté sans tourner : le regard reste au nord.
        _, t_droit = self.marche("nord", "chasser", "est")
        m, t_biais = self.marche("nord", "chasser", "sud-est")
        self.assertEqual((t_droit, t_biais), (4 * 30, 4 * 42))
        self.assertEqual((m.joueur["position"], m.joueur["orientation"]), ([4, 4], "nord"))
        # Un pas chassé droit devant garde l'allure d'un pas.
        _, t = self.marche("sud-est", "chasser", "sud-est")
        self.assertEqual(t, 4 * 21)


class MarchePNJTests(unittest.TestCase):
    """La marche d'un PNJ prend la durée de chaque pas selon son sens, même quand plusieurs pas
    font un seul geste."""

    def marcher(self, m, id, arrivee):
        durees = []
        while True:
            d = _marcher(m, id, lambda salle, case: (salle, case) == ("chambre_cloche", arrivee), [])
            if not d:
                return recharger(m), durees
            durees.append(d)

    def test_droit_ou_en_diagonale(self):
        m = galerie()
        placer(m, "marchand", "chambre_cloche", (1, 5))
        m.objets["marchand"]["orientation"] = "est"
        m, droit = self.marcher(m, "marchand", (5, 5))
        self.assertEqual(m.objets["marchand"]["position"], [5, 5])
        m = galerie()
        placer(m, "marchand", "chambre_cloche", (1, 5))
        m.objets["marchand"]["orientation"] = "sud-est"
        m, biais = self.marcher(m, "marchand", (5, 9))
        self.assertEqual(m.objets["marchand"]["position"], [5, 9])
        self.assertEqual((droit, biais), ([15] * 4, [21] * 4))

    def test_a_pas_feutres(self):
        m = galerie()
        placer(m, "brune", "chambre_cloche", (1, 5))
        m.objets["brune"]["orientation"] = "sud-est"
        # Elle prépare un geste qu'elle veut sans témoin : elle marche à pas feutrés.
        lire(m, "brune")["intention"] = {"but": {"type": "manger"}, "motif": "faim", "depuis": 0, "attente": 0,
                                         "plan": [{"operation": "prendre", "cible": "cloche", "outil": "", "lieu": "",
                                                   "condition": "sans_temoin"}]}
        m, biais = self.marcher(m, "brune", (3, 7))
        self.assertEqual(biais, [42, 42])
        self.assertEqual(m.objets["brune"]["position"], [3, 7])

    def test_les_pas_enchaines_d_un_meme_geste(self):
        # Ilse se tient sur la case du milieu : Gorm la traverse sans s'y arrêter, en un geste de
        # deux pas en diagonale.
        m = galerie()
        placer(m, "marchand", "chambre_cloche", (1, 5))
        placer(m, "ilse", "chambre_cloche", (2, 6))
        m.objets["marchand"]["orientation"] = "sud-est"
        m, biais = self.marcher(m, "marchand", (3, 7))
        self.assertEqual(biais, [42])
        m = galerie()
        placer(m, "marchand", "chambre_cloche", (1, 5))
        placer(m, "ilse", "chambre_cloche", (2, 5))
        m.objets["marchand"]["orientation"] = "est"
        m, droit = self.marcher(m, "marchand", (3, 5))
        self.assertEqual(droit, [30])
        self.assertEqual(m.objets["ilse"]["position"], [2, 5])


class TrajetTests(unittest.TestCase):
    def test_le_moins_de_pas_n_est_pas_le_plus_rapide(self):
        m = galerie()
        # Deux cases conviennent : trois pas en diagonale (6,3 s) ou quatre pas droits (6 s).
        buts = {(3, 3), (4, 0)}
        chemin = trajet(m, "chambre_cloche", (0, 0), lambda salle, case: case in buts)
        self.assertEqual([c[1] for c in chemin], [(1, 0), (2, 0), (3, 0), (4, 0)])
        self.assertEqual(sum(duree_pas(PAS_JOUEUR, c[3]) for c in chemin), 60)

    def test_contourner_par_le_plus_rapide(self):
        # Placement d'auteur : un plan où le chemin du moins de pas (7 pas, 12,3 s) passe au sud en
        # diagonales, et le plus rapide (8 pas, 12 s) au nord, droit.
        m = galerie()
        m.data["salles"]["chambre_cloche"]["plan"]["sol"] = [
            "       ",
            ".....  ",
            ".   ...",
            ".. ... ",
            ".....  ",
            "       ",
        ]
        chemin = trajet(m, "chambre_cloche", (6, 2), lambda salle, case: case == (0, 2))
        self.assertEqual(sum(duree_pas(PAS_JOUEUR, c[3]) for c in chemin), 120)
        self.assertEqual(len(chemin), 8)
        self.assertIn((2, 1), [c[1] for c in chemin])

    @unittest.skipUnless(shutil.which("node"), "node absent : le script de la page ne peut pas tourner")
    def test_le_clic_de_la_page_suit_la_meme_regle(self):
        from donjon.scene import scene_percue
        from donjon.gestes_publics import catalogue_public
        from donjon.spatial import memoriser
        m = galerie()
        m.joueur["orientation"] = "sud-est"
        memoriser(m)
        piece = m.data["salles"]["chambre_cloche"]
        etat = {"type": "etat", "salle": "", "pv": 1, "or": 0, "minutes": 0, "connexion": "", "fiche": "",
                "proposition": "", "scene": scene_percue(m), "catalogue_gestes": catalogue_public(),
                "sonde_buts": [list(_global(piece, (3, 3))), list(_global(piece, (4, 0)))]}
        page = Path(__file__).parents[1] / "donjon" / "web" / "page.html"
        sortie = subprocess.run(["node", str(Path(__file__).with_name("clic_page.js")), str(page)],
                                input=json.dumps(etat), capture_output=True, text=True, encoding="utf-8",
                                check=True).stdout
        self.assertEqual(json.loads(sortie)["vers_buts"], ["est"] * 4)


class PorteeTests(unittest.TestCase):
    def test_un_halo_rond(self):
        m = galerie()
        # La lanterne du joueur (pleine lumière à 4 cases, pénombre à 8), au bord ouest de la galerie.
        m.joueur.update(position=[0, 3])
        piece = m.data["salles"]["chambre_cloche"]
        carte = CarteLumiere(m, "chambre_cloche")

        def niveau(dx, dy):
            return max((d["niveau"] for d in carte.directes(_global(piece, (dx, 3 + dy)))
                        if d["source"] == "lanterne"), default=0)
        self.assertEqual([niveau(4, 0), niveau(3, 3), niveau(4, 4)], [2, 2, 1])
        self.assertEqual([niveau(0, 8), niveau(6, 6), niveau(6, 7), niveau(0, 9)], [1, 1, 0, 0])

    def test_un_bruit_en_diagonale_vient_de_plus_loin(self):
        # Un cran par distance doublée (1, 3, 6 cases…) : à trois et à cinq cases en diagonale, un
        # cran de plus qu'en ligne droite ; à quatre, le même palier.
        self.assertEqual([perte((0, 0), (k, 0)) for k in (1, 3, 4, 5)], [0, 1, 2, 2])
        self.assertEqual([perte((0, 0), (k, k)) for k in (1, 3, 4, 5)], [0, 2, 2, 3])

    def bruit_de_pas(self, arrivee):
        """Aubin (PER 12), au nord-ouest de la galerie, regarde au nord ; le joueur fait un pas qui
        s'achève sur ``arrivee``, dans son dos."""
        m = galerie()
        placer(m, "aubin", "chambre_cloche", (1, 2))
        m.objets["aubin"]["orientation"] = "nord"
        m.joueur.update(position=[arrivee[0], arrivee[1] + 1], orientation="nord")
        m = recharger(m)
        faire(m, "marcher", "nord")
        return recharger(m)

    def test_des_pas_a_cinq_cases(self):
        droit = self.bruit_de_pas((6, 2))       # cinq cases à l'est
        biais = self.bruit_de_pas((6, 7))       # cinq cases en diagonale : 7 en distance réelle
        self.assertEqual(droit.objets["aubin"]["orientation"], "est")
        self.assertEqual(lire(droit, "aubin")["croyances"]["joueur"]["lieu"]["valeur"], "chambre_cloche")
        self.assertEqual(biais.objets["aubin"]["orientation"], "nord")
        self.assertNotIn("joueur", lire(biais, "aubin")["croyances"])

    def test_la_voix_porte_en_rond(self):
        m = galerie()
        placer(m, "aubin", "chambre_cloche", (0, 4))
        for case, pres in (((6, 4), True), ((4, 8), True), ((5, 9), False), ((0, 10), True), ((0, 11), False)):
            m.joueur["position"] = list(case)
            self.assertEqual(de_pres(m, "aubin", "joueur"), pres, case)


if __name__ == "__main__":
    unittest.main()
