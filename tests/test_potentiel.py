import copy
from pathlib import Path
import tempfile
import unittest

from donjon.faits_locaux import catalogue, potentiel, preparer_faits
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition


def objet(nom, masse=0.3, capacites=()):
    return {"type": "objet", "ancrage": "antichambre_sol", "nom": nom, "genre": "m",
            "texte": "Un petit objet ordinaire.", "materiau": "pierre", "masse": masse,
            "mobile": True, "relation": "pose", "capacites": list(capacites)}


def creer(monde, *ajouts):
    travail, _, etablis = preparer_faits(monde, {"ajouts": list(ajouts)}, monde.data["revision"])
    return travail, etablis


class PotentielTests(unittest.TestCase):
    def test_budget_epuise_persiste_apres_rechargement_et_deplacement(self):
        m = nouveau_monde()
        self.assertEqual(potentiel(m)["objets_restants"], 2)
        m, etablis = creer(m, objet("caillou"), objet("tesson"))
        self.assertEqual(catalogue(m)["potentiel_invention"]["objets_restants"], 0)
        # Ramasser un objet créé ne libère pas sa place dans le lieu.
        Moteur(m).executer(Moteur(m).preparer(proposition("prendre", etablis[0]["objet"])))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        avant = copy.deepcopy(reprise.data)
        with self.assertRaises(ErreurMonde) as erreur:
            creer(reprise, objet("galet"))
        self.assertIn("plus rien de nouveau", str(erreur.exception))
        self.assertEqual(reprise.data, avant)

    def test_capacite_ou_masse_hors_budget_refusees(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as erreur:
            creer(m, objet("lampe", capacites=[{"nature": "lumiere", "niveau": 2, "combustible": 30}]))
        self.assertIn("lumiere", str(erreur.exception))
        with self.assertRaises(ErreurMonde):
            creer(m, objet("bloc", masse=8))
        self.assertEqual(m.data, avant)
        travail, _ = creer(m, objet("grelot", capacites=[{"nature": "son", "intensite": 1}]))
        self.assertEqual(travail.data["inventions"]["antichambre"], 1)

    def test_qualification_bornee_par_les_capacites_du_lieu(self):
        m = nouveau_monde()
        m, etablis = creer(m, objet("caillou"))
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            creer(m, {"type": "qualification", "ancrage": etablis[0]["objet"],
                      "capacites": [{"nature": "outil", "usages": ["levier"], "puissance": 2}]})
        self.assertEqual(m.data, avant)

    def test_lieu_sans_budget_reste_libre(self):
        m = nouveau_monde()
        m.data["salles"]["antichambre"].pop("potentiel_invention")
        self.assertIsNone(potentiel(m))
        self.assertNotIn("potentiel_invention", catalogue(m))
        travail, _ = creer(m, objet("lampe", capacites=[{"nature": "lumiere", "niveau": 2, "combustible": 30}]))
        self.assertNotIn("inventions", travail.data)


if __name__ == "__main__":
    unittest.main()
