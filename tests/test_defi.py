"""Vérifie que les deux itinéraires du Relais des crues sont praticables."""
import copy
import unittest
from collections import deque
from unittest.mock import patch

from donjon.carte import carte
from donjon.defi import BEFFROI, OBJECTIF, PIED_BEFFROI, REFUGE, actualiser, nouveau_defi
from donjon.mj import MJOpenAI
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.spatial import installer as installer_spatial, preparer_pas


class DefiRelaisTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_defi()
        installer_spatial(self.m)
        self.moteur = Moteur(self.m)

    def agir(self, action, cible="", outil=""):
        return self.moteur.executer(self.moteur.preparer(proposition(action, cible, outil)))

    def victoire(self):
        self.assertTrue(self.m.data.get("objectif_atteint"))
        lignes = []
        self.assertTrue(actualiser(self.m, lignes))
        self.assertTrue(self.m.data["objectif_atteint"])

    def marcher_jusqua(self, destination):
        """Cherche un chemin local sur une copie puis exécute réellement chaque pas."""
        simulation = self.m.copier()
        debut = tuple(simulation.joueur["position"])
        file, vus = deque([(debut, [])]), {debut}
        chemin = None
        while file:
            position, trajet = file.popleft()
            if position == tuple(destination):
                chemin = trajet
                break
            simulation.joueur["position"] = list(position)
            for direction in ("nord", "sud", "est", "ouest"):
                try:
                    suivant = preparer_pas(simulation, direction)
                except ErreurMonde:
                    continue
                p = tuple(suivant["position"])
                if suivant["salle"] == self.m.joueur["salle"] and p not in vus:
                    vus.add(p)
                    file.append((p, trajet + [direction]))
        self.assertIsNotNone(chemin, "Aucun chemin réel vers " + str(destination))
        for direction in chemin:
            self.agir("marcher", direction)

    def aller_dans(self, destination):
        salle = self.m.data["salles"][self.m.joueur["salle"]]
        direction, sortie = next((d, s) for d, s in salle["sorties"].items()
                                  if s["vers"] == destination)
        dx, dy = {"nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0)}[direction]
        case = sortie["case"]
        self.marcher_jusqua((case[0] - dx, case[1] - dy))
        self.agir("marcher", direction)
        self.assertEqual(self.m.joueur["salle"], destination)

    def test_route_interieure_avec_cle_et_retour(self):
        self.assertEqual(self.m.data["scenario"]["objectif"], OBJECTIF)
        self.assertFalse(self.m.visible("cle"))
        self.assertNotIn("cle", [o["id"] for o in self.m.contexte()["objets_perceptibles"]])
        examen = self.agir("examiner", "gravure")
        self.assertIn("contournant", examen)
        self.assertIn("face ouest de la cloison", examen)
        self.marcher_jusqua((6, 5))
        self.assertTrue(self.m.visible("cle"))
        self.agir("prendre", "cle")
        self.aller_dans("echoppe")
        self.aller_dans("crypte")
        self.marcher_jusqua((7, 3))
        self.agir("deverrouiller", "porte", "cle")
        self.agir("ouvrir", "porte")
        self.aller_dans(PIED_BEFFROI)
        self.aller_dans(BEFFROI)
        self.assertEqual(self.m.joueur["salle"], BEFFROI)
        self.marcher_jusqua((1, 3))
        self.agir("prendre", "cloche")
        self.assertFalse(self.m.data.get("objectif_atteint", False))
        self.aller_dans(PIED_BEFFROI)
        self.aller_dans("crypte")
        self.aller_dans("echoppe")
        self.aller_dans(REFUGE)
        self.assertEqual(self.m.joueur["salle"], REFUGE)
        self.victoire()

    def test_consigne_touche_la_cloison_et_relation_transmise_au_mj(self):
        salle = self.m.data["salles"][REFUGE]
        self.assertEqual(salle["plan"]["sol"][3][3], " ")
        self.assertEqual(self.m.objets["gravure"]["position"], [2, 3])
        self.assertEqual(self.m.objets["antichambre_murs"]["position"], [2, 3])
        self.assertTrue(self.m.visible("gravure"))
        fait = next(o for o in self.m.contexte()["objets_perceptibles"]
                    if o["id"] == "gravure")
        self.assertEqual(fait["fixee_sur"], "la face ouest de la cloison de pierre")

        self.m.memoriser("comment la consigne est elle attachée ?",
                         "Elle tient au mur, mais sa fixation est inconnue.")
        mj = MJOpenAI("gpt-6-luna")
        reponse = {"mode": "dialogue", "texte": "La consigne est sur la cloison.",
                   "faits": ["objet:gravure"], "proposition": None}
        with patch.object(mj, "_appeler", return_value=reponse) as appel:
            mj._echanger(self.m, "comment la consigne est elle attachée ?", None, True)
        instructions, entree, *_ = appel.call_args.args
        self.assertEqual(entree["faits"]["objet:gravure"]["fixee_sur"],
                         "la face ouest de la cloison de pierre")
        self.assertIn("L'état actuel prime", instructions)

    def test_ancienne_partie_ajuste_la_cloison_sans_deplacer_la_consigne(self):
        donnees = copy.deepcopy(self.m.data)
        donnees["salles"][REFUGE]["plan"]["sol"][3] = ".... ...."
        donnees["objets"]["antichambre_murs"]["position"] = [3, 3]
        donnees["objets"]["gravure"].pop("fixee_sur")
        donnees["exploration"][REFUGE].append([3, 3])
        reprise = Monde(donnees)
        self.assertEqual(reprise.data["salles"][REFUGE]["plan"]["sol"][3], "...  ....")
        self.assertEqual(reprise.objets["gravure"]["position"], [2, 3])
        self.assertEqual(reprise.objets["antichambre_murs"]["position"], [2, 3])
        self.assertNotIn([3, 3], reprise.data["exploration"][REFUGE])
        self.assertIn("! ##", carte(reprise))

    def test_route_exterieure_par_echelle_et_retour(self):
        with self.assertRaises(ErreurMonde):
            self.agir("installer", "echelle_relais", "appui_clocher")
        self.marcher_jusqua((7, 4))
        self.agir("installer", "echelle_relais", "appui_clocher")
        self.assertEqual(self.m.objets["echelle_relais"]["position"], [8, 3])
        with patch.object(Monde, "d20", return_value=20):
            self.agir("franchir", "echelle_relais")
        self.assertEqual(self.m.joueur["salle"], BEFFROI)
        self.assertEqual(self.m.joueur["position"], [0, 3])
        self.marcher_jusqua((1, 3))
        self.agir("prendre", "cloche")
        self.assertFalse(self.m.data.get("objectif_atteint", False))
        with patch.object(Monde, "d20", return_value=20):
            self.agir("franchir", "echelle_relais")
        self.assertEqual(self.m.joueur["salle"], REFUGE)
        self.victoire()


if __name__ == "__main__":
    unittest.main()
