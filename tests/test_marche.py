"""La marche des PNJ, case par case : on ne s'arrête jamais sur la case d'un autre ; on rejoint
ce qu'on touche (cible ou outil) pas à pas ; sans chemin en cases, le geste est manqué et l'on
apprend ce qui barre le passage ; on marche vers ce qu'on croit, puis on constate sur place.
Vérifié sur l'état du monde après rechargement."""
import copy
import unittest

from tests.support import calme
from tests.test_tensions import placer, recharger, relais, vivre
from donjon.esprits import croire, lire, percevoir, percoit
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj import PAS, agir, chemin, occupants


def tranquilles():
    return calme(relais(), "marchand", "brune", "ilse", "aubin")


def ecarter_tous(m, *ids):
    """Placement d'auteur : ces PNJ sont à la crypte, hors de la scène."""
    for n, id in enumerate(ids):
        placer(m, id, "crypte", (2 + n, 3))


def intention(m, id, plan, but=None, motif="alerte"):
    """Placement d'auteur : un plan à suivre ; un réflexe (« alerte ») va à son terme sans que la
    délibération ne le remplace."""
    lire(m, id)["intention"] = {"but": but or {"type": "rejoindre", "lieu": plan[0].get("lieu", "")}, "motif": motif,
                                "plan": [{"operation": "", "cible": "", "outil": "", "lieu": "", "condition": "", **x}
                                         for x in plan], "depuis": m.data["minutes"], "attente": 0}


def distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def gestes(m, id, fois):
    """``fois`` gestes du PNJ, sa perception à jour après chacun, comme pendant sa vie ; renvoie
    ses positions successives."""
    t, positions = 0, []
    for _ in range(fois):
        t += agir(m, id, t, [])
        percevoir(m, id)
        positions.append((m.objets[id]["lieu"], tuple(m.objets[id]["position"])))
    return positions


def faire(m, action, cible=""):
    moteur = Moteur(m)
    return moteur.executer(moteur.preparer(proposition(action, cible)))


class CaseOccupeeTests(unittest.TestCase):
    def test_arrive_dans_la_salle_il_ne_s_arrete_pas_sur_le_joueur(self):
        m = tranquilles()
        ecarter_tous(m, "brune", "ilse", "aubin")
        # Placement d'auteur : le joueur se tient sur le seuil intérieur de l'antichambre.
        m.joueur.update(salle="antichambre", position=[0, 3], orientation="sud")
        placer(m, "marchand", "echoppe", (7, 3))
        intention(m, "marchand", [{"operation": "aller", "lieu": "antichambre"}])
        faire(m, "tourner", "sud")
        m = recharger(m)
        faire(m, "attendre")
        m = recharger(m)
        g = m.objets["marchand"]
        self.assertEqual(g["lieu"], "antichambre")
        self.assertNotEqual(tuple(g["position"]), (0, 3))
        self.assertIsNone(lire(m, "marchand")["intention"])

    def test_ni_sur_un_autre_pnj(self):
        m = tranquilles()
        ecarter_tous(m, "brune", "ilse")
        # Placement d'auteur : Aubin se tient sur le seuil intérieur de l'antichambre.
        placer(m, "aubin", "antichambre", (0, 3))
        placer(m, "marchand", "echoppe", (7, 3))
        intention(m, "marchand", [{"operation": "aller", "lieu": "antichambre"}])
        m, _ = vivre(m, 2)
        g = m.objets["marchand"]
        self.assertEqual(g["lieu"], "antichambre")
        self.assertNotEqual(tuple(g["position"]), tuple(m.objets["aubin"]["position"]))

    def test_deux_personnages_sur_une_case_sont_refuses(self):
        m = tranquilles()
        m.joueur.update(salle="antichambre", position=list(m.objets["ilse"]["position"]))
        with self.assertRaises(ErreurMonde):
            m.verifier()

    def test_le_joueur_ne_marche_pas_sur_un_pnj(self):
        m = tranquilles()
        x, y = m.objets["ilse"]["position"]
        m.joueur.update(salle="antichambre", position=[x + 1, y], orientation="ouest")
        # Méfiante, Ilse ne s'écarte pas (``passage`` : sinon, elle laisserait passer).
        croire(m, "ilse", "joueur", "fiable", False, "vu")
        with self.assertRaises(ErreurMonde) as refus:
            faire(m, "marcher", "ouest")
        self.assertIn("ilse", refus.exception.attendu)
        self.assertEqual(m.joueur["position"], [x + 1, y])

    def test_une_ancienne_partie_superposee_s_ecarte_au_chargement(self):
        m = tranquilles()
        # Une partie d'avant la règle : Gorm s'était arrêté sur la case d'Ilse.
        placer(m, "marchand", "antichambre", m.objets["ilse"]["position"])
        m = recharger(Monde(copy.deepcopy(m.data)))
        self.assertEqual(len(occupants(m)), 5)  # Le joueur et quatre PNJ, chacun sur sa case.
        self.assertEqual(m.objets["marchand"]["lieu"], "antichambre")
        self.assertEqual(distance(m.objets["marchand"]["position"], m.objets["ilse"]["position"]), 1)


class ContactTests(unittest.TestCase):
    def test_il_marche_jusqu_a_la_flamme_ou_allumer_sa_lanterne(self):
        m = tranquilles()
        ecarter_tous(m, "brune", "ilse", "aubin")
        placer(m, "marchand", "echoppe", (8, 0))
        m.objets["lanterne"].update(lieu="marchand", allume=False)
        m.objets["lanterne"]["combustible"] = max(30, m.objets["lanterne"].get("combustible", 0))
        brasero = (3, 4)
        intention(m, "marchand", [{"operation": "allumer", "cible": "lanterne", "outil": "brasero"}],
                  {"type": "lumiere"})
        positions = gestes(m, "marchand", 1)
        # Un geste : un pas, pas un bond jusqu'à la flamme ; rien n'est encore allumé.
        self.assertEqual(distance(positions[0][1], (8, 0)), 1)
        self.assertFalse(m.objets["lanterne"]["allume"])
        m, _ = vivre(m, 1)
        # Allumée sur place ; sans autre usage, il la ménage ensuite (``menager_flamme``).
        self.assertIn("Gorm, gardien du relais allume la lanterne.", [c["texte"] for c in m.data["chronique"]])
        self.assertLessEqual(distance(m.objets["marchand"]["position"], brasero), 1)

    def test_il_marche_jusqu_au_feu_qu_il_eteint(self):
        # Éteindre touche sa cible comme tout geste de la main : il s'en approche d'abord.
        m = tranquilles()
        ecarter_tous(m, "brune", "ilse", "aubin")
        placer(m, "marchand", "echoppe", (8, 0))
        intention(m, "marchand", [{"operation": "eteindre", "cible": "brasero"}], {"type": "menager"})
        gestes(m, "marchand", 1)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertEqual(distance(m.objets["marchand"]["position"], (8, 0)), 1)
        m, _ = vivre(m, 1)
        self.assertFalse(m.objets["brasero"]["allume"])
        self.assertLessEqual(distance(m.objets["marchand"]["position"], (3, 4)), 1)


class ImpasseTests(unittest.TestCase):
    def barrer(self, salle, case):
        m = tranquilles()
        ecarter_tous(m, "marchand", "ilse", "aubin")
        placer(m, "brune", "antichambre", (5, 1))
        placer(m, "reserve", salle, case)
        m.objets["reserve"]["bloque_passage"] = True
        lire(m, "brune")["croyances"].pop("reserve", None)
        intention(m, "brune", [{"operation": "aller", "lieu": "echoppe"}])
        self.assertTrue(chemin(m, "brune", "antichambre", "echoppe"))
        return m

    def verifier_impasse(self, m, salle, case):
        m, _ = vivre(m, 1)
        self.assertEqual(m.objets["brune"]["lieu"], "antichambre")
        self.assertIsNone(lire(m, "brune")["intention"])  # Le réflexe cesse au geste manqué.
        cru = lire(m, "brune")["croyances"]["reserve"]["lieu"]
        self.assertEqual((cru["salle"], cru["case"]), (salle, list(case)))
        self.assertIsNone(chemin(m, "brune", "antichambre", "echoppe"))

    def test_un_obstacle_sur_le_seuil_barre_le_passage(self):
        m = self.barrer("antichambre", (0, 3))
        self.verifier_impasse(m, "antichambre", (0, 3))

    def test_un_obstacle_de_l_autre_cote_du_seuil(self):
        m = self.barrer("echoppe", (8, 3))
        self.verifier_impasse(m, "echoppe", (8, 3))

    def test_sans_chemin_le_but_ordinaire_patiente_puis_renonce(self):
        m = self.barrer("antichambre", (0, 3))
        intention(m, "brune", [{"operation": "aller", "lieu": "echoppe"}], {"type": "rejoindre", "lieu": "echoppe"},
                  "faim")
        agir(m, "brune", 0, [])
        self.assertEqual(lire(m, "brune")["intention"]["attente"], 1)
        lire(m, "brune")["intention"]["attente"] = 30
        agir(m, "brune", 600, [])
        self.assertIsNone(lire(m, "brune")["intention"])
        self.assertIn("renoncement", [s["type"] for s in recharger(m) and lire(m, "brune")["memoire"]])


class CroyanceTests(unittest.TestCase):
    def test_elle_marche_vers_ou_elle_croit_le_marteau(self):
        m = tranquilles()
        ecarter_tous(m, "marchand", "ilse", "aubin")
        placer(m, "brune", "antichambre", (1, 1))
        m.objets["brune"]["orientation"] = "nord"
        placer(m, "marteau", "antichambre", (7, 5))
        croire(m, "brune", "marteau", "lieu", "antichambre", "vu", salle="antichambre", case=[1, 5])
        self.assertFalse(percoit(m, "brune", "marteau"))
        intention(m, "brune", [{"operation": "prendre", "cible": "marteau"}], {"type": "prendre", "objet": "marteau"},
                  "biens")
        depart = (1, 1)
        for _, case in gestes(m, "brune", 2):
            # Tant qu'elle ne l'a pas vu ailleurs, elle se rapproche de là où elle le croit.
            self.assertLess(distance(case, (1, 5)), distance(depart, (1, 5)))
            self.assertGreaterEqual(distance(case, (7, 5)), distance(depart, (7, 5)) - 1)
            depart = case
        m, _ = vivre(m, 2)
        cru = lire(m, "brune")["croyances"]["marteau"]["lieu"]
        # Sur place, elle a constaté : il n'est pas là où elle le croyait.
        self.assertNotEqual((cru["valeur"], cru["case"]), ("antichambre", [1, 5]))

    def test_elle_va_parler_a_ilse_la_ou_elle_l_a_vue(self):
        m = tranquilles()
        ecarter_tous(m, "marchand", "aubin")
        placer(m, "brune", "antichambre", (1, 1))
        m.objets["brune"]["orientation"] = "nord"
        placer(m, "ilse", "antichambre", (7, 5))
        croire(m, "brune", "ilse", "lieu", "antichambre", "vu", salle="antichambre", case=[1, 5])
        self.assertFalse(percoit(m, "brune", "ilse"))
        intention(m, "brune", [{"operation": "demander", "cible": "ilse", "outil": "planches"}],
                  {"type": "obtenir", "objet": "planches"}, "chaleur")
        case = gestes(m, "brune", 1)[0][1]
        self.assertLess(distance(case, (1, 5)), distance((1, 1), (1, 5)))
        self.assertGreaterEqual(distance(case, (7, 5)), distance((1, 1), (7, 5)) - 1)


if __name__ == "__main__":
    unittest.main()
