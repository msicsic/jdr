from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.monde import ErreurMonde, Monde, nouveau_monde, nouveau_monde_libre, objet
from donjon.moteur import Moteur, proposition


class VenteGeneriqueTests(unittest.TestCase):
    def scene(self):
        m = nouveau_monde()
        m.objets["mira"] = objet("mira", "Mira", "personnage", "antichambre",
                                 vigilance=14, refuse_ventes_apres_vol=True)
        m.objets["broche"] = objet("broche", "broche d'étain", "tresor", "antichambre",
                                   mobile=True, masse=0.1, prix=5, en_vente=True,
                                   vendeur="mira")
        return m.copier()

    def test_achat_a_un_autre_vendeur_hors_echoppe_et_rechargement(self):
        m = self.scene()
        plan = Moteur(m).preparer(proposition("acheter", "broche"))
        resultat = Moteur(m).executer(plan)
        self.assertIn("Mira", resultat)
        self.assertEqual(m.objets["broche"]["lieu"], "joueur")
        self.assertEqual(m.data["finances_pnj"]["mira"], 4)
        self.assertEqual(m.joueur["or"], 20)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.objets["broche"]["proprietaire"], "joueur")
        self.assertFalse(reprise.objets["broche"]["en_vente"])

    def test_vol_remarque_declenche_refus_du_vendeur_concerne(self):
        m = self.scene()
        plan = Moteur(m).preparer(proposition("voler", "broche", methode="simple"))
        with patch.object(Monde, "d20", return_value=1):
            Moteur(m).executer(plan)
        self.assertEqual(m.data["relations_pnj"]["mira"]["vols_surpris"], 1)
        self.assertEqual(m.objets["broche"]["lieu"], "antichambre")
        with self.assertRaisesRegex(ErreurMonde, "refuse"):
            Moteur(m).preparer(proposition("acheter", "broche"))

    def test_vente_dans_un_scenario_sans_crypte_ni_gorm(self):
        m = nouveau_monde_libre(
            salles={"place": {"nom": "Place", "sorties": {}, "fenetres": 0,
                              "lumiere_naturelle": 2,
                              "plan": {"origine": [0, 0], "sol": ["..."] * 3, "repere": "P"}}},
            objets={
                "vendeuse": objet("vendeuse", "Mira", "personnage", "place"),
                "livre": objet("livre", "livre", "tresor", "place", mobile=True,
                               masse=0.2, prix=6, en_vente=True, vendeur="vendeuse"),
            },
            salle_depart="place", position=[1, 1],
            scenario={"debut": "Tu arrives sur une place.", "objectif": "Explorer."})
        m.joueur["or"] = 20
        m.verifier()
        Moteur(m).executer(Moteur(m).preparer(proposition("acheter", "livre")))
        self.assertEqual(m.objets["livre"]["lieu"], "joueur")
        self.assertEqual(m.data["finances_pnj"]["vendeuse"], 5)


if __name__ == "__main__":
    unittest.main()
