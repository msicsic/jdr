import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.transactions import ajouter, appliquer

DETAIL = {"ajouts": [{"type": "detail", "ancrage": "echoppe_murs", "nom": "éclat de peinture",
                      "genre": "m", "texte": "Un éclat bleu marque la pierre."}]}
SAVOIR = {"personnage": "marchand",
          "savoirs": [{"sujet": "lien_anneau",
                       "texte": "Gorm tient à l'anneau parce qu'il lui rappelle son ancien métier."}]}


def monde_echoppe():
    m = nouveau_monde()
    m.joueur["salle"] = "echoppe"
    return m


class TransactionsTests(unittest.TestCase):
    def test_deux_transactions_enchainees_puis_rechargement(self):
        m = monde_echoppe()
        revision = m.data["revision"]
        reponse = {"mode": "dialogue", "texte": "Gorm te regarde, puis parle de son ancien métier.",
                   "faits": [], "proposition": None, "_texte_moteur": True}
        # La seconde transaction a été préparée sur le monde déjà modifié par la première.
        ajouter(reponse, "faits", revision, DETAIL)
        ajouter(reponse, "savoirs", revision + 1, SAVOIR)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "echanger", return_value=reponse),
                  patch("builtins.input", side_effect=["mj parle-moi de toi, Gorm", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(reponse["texte"], sortie.getvalue())
        self.assertEqual(reprise.data["revision"], revision + 2)
        self.assertEqual(reprise.objets[reprise.trouver("éclat de peinture")]["genre"], "m")
        self.assertEqual(reprise.data["savoirs_pnj"]["marchand"]["lien_anneau"]["texte"],
                         SAVOIR["savoirs"][0]["texte"])
        self.assertEqual(reprise.data["conversation"][-1]["reponse"], reponse["texte"])

    def test_revision_perimee_refuse_toute_la_liste(self):
        m = monde_echoppe()
        revision = m.data["revision"]
        reponse = ajouter({}, "faits", revision, DETAIL)
        ajouter(reponse, "savoirs", revision, SAVOIR)  # préparée sur l'ancien monde
        avant = m.data.copy()
        with self.assertRaises(ErreurMonde):
            appliquer(m, reponse["_transactions"])
        self.assertEqual(m.data, avant)


if __name__ == "__main__":
    unittest.main()
