"""Assembler avec n'importe quelle pièce décrite ; découper une pièce à longueur."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.atelier import nouveau_atelier
from donjon.monde import ErreurMonde, Monde, objet
from donjon.moteur import Moteur
from donjon.operations import etape, sequence


def atelier_avec_planches():
    """L'atelier, plus un tas de planches décrit par l'auteur : 3 planches de 3 m."""
    m = nouveau_atelier()
    m.data["mode_cases"] = False
    m.objets["planches"] = objet(
        "planches", "planches", "materiau", m.joueur["salle"], aliases=["planches"], genre="f",
        materiau="bois", masse=27, mobile=True, proprietaire="joueur",
        physique={"forme": "barre", "matiere": "bois", "pieces": 3, "nom_piece": "planche",
                  "dimensions": {"longueur_cm": 300, "largeur_cm": 20, "epaisseur_cm": 2.5}})
    return Monde(m.data)


def executer(m, p):
    with patch.object(Monde, "d20", return_value=20):
        return Moteur(m).executer(Moteur(m).preparer(p))


def assembler(montants, barreaux, lien="ficelle", outil="hache"):
    return {"action": "assembler", "usage": "echelle", "pieces": {"montants": montants, "barreaux": barreaux},
            "lien": lien, "outil": outil, "longueur_cm": 300, "largeur_cm": 35, "difficulte": 12,
            "rythme": "normal", "justification": "Deux montants, des barreaux liés."}


class AssemblageTests(unittest.TestCase):
    def test_une_echelle_de_planches_decrites(self):
        m = atelier_avec_planches()
        for _ in range(2):
            executer(m, sequence(etape("prelever", "planches", m.joueur["salle"])))
        # La dernière pièce reste le lot lui-même, au nom d'une planche.
        self.assertEqual((m.objets["planches"]["nom"], m.objets["planches"]["physique"]["pieces"]), ("planche", 1))
        executer(m, assembler(["planches_1", "planches_2"], "planches"))
        echelle = next(o for o in m.objets.values() if o.get("assemblage"))
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)
            recharge = Monde.charger(chemin)
        echelle = recharge.objets[echelle["id"]]
        self.assertEqual((echelle["nom"], echelle["materiau"], echelle["longueur_cm"]), ("échelle", "bois et fibres", 300))

    def test_un_lot_ne_s_assemble_pas_sans_prelevement(self):
        m = atelier_avec_planches()
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(assembler(["planches", "perche_1"], "perche_2"))
        self.assertIn("prélève d'abord une pièce", refus.exception.attendu)

    def test_l_ancienne_fabrication_reste_acceptee(self):
        from donjon.artisanat import fabrication
        m = atelier_avec_planches()
        plan = Moteur(m).preparer(fabrication(["perche_1", "perche_2"], "perche_3", "ficelle", "hache"))
        self.assertEqual(plan.effets[0][0], "assembler")


class DecoupeTests(unittest.TestCase):
    def test_couper_une_perche_donne_un_morceau_et_raccourcit_le_reste(self):
        m = atelier_avec_planches()
        masse = m.objets["perche_1"]["masse"]
        executer(m, sequence(etape("deplacer", "hache", "joueur")) if m.objets["hache"]["lieu"] != "joueur" else
                 sequence(etape("patienter")))
        executer(m, {"action": "decouper", "cible": "perche_1", "outil": "hache", "longueur_cm": 100,
                     "justification": "Une traverse."})
        morceau, reste = m.objets["perche_1_1"], m.objets["perche_1"]
        self.assertEqual((morceau["longueur_cm"], reste["longueur_cm"]), (100, 200))
        self.assertAlmostEqual(morceau["masse"] + reste["masse"], masse, places=2)
        self.assertEqual(morceau["physique"]["dimensions"]["diametre_cm"], 5)

    def test_une_lame_fine_ne_coupe_pas_une_perche(self):
        m = atelier_avec_planches()
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer({"action": "decouper", "cible": "perche_1", "outil": "couteau", "longueur_cm": 100,
                                "justification": ""})
        self.assertIn("couper_bois", refus.exception.attendu)


if __name__ == "__main__":
    unittest.main()
