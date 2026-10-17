import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence


def partie_outillee():
    """Corvus a acheté les crochets et le marteau chez Gorm, puis est revenu devant la porte."""
    m = nouveau_monde()
    m.joueur["salle"] = "echoppe"
    m.joueur["or"] = 60
    for id in ("crochets", "marteau"):
        Moteur(m).executer(Moteur(m).preparer(proposition("acheter", id)))
    Moteur(m).executer(Moteur(m).preparer(proposition("aller", "est")))
    assert m.joueur["salle"] == "antichambre"
    return m


CROCHETER_OUVRIR_CALER = sequence(
    etape("crocheter", "porte", outil="crochets", methode="finesse"),
    etape("ouvrir", "porte"),
    etape("bloquer", "porte", outil="marteau"),
    justification="Crocheter, ouvrir puis caler la porte.")


class CompositionEtendueTests(unittest.TestCase):
    def test_sequence_crocheter_ouvrir_caler_puis_rechargement(self):
        m = partie_outillee()
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=lambda *a: (
                      {"conforme": True, "motif": ""} if a[3] == "auditer_action" else
                      {"mode": "action", "texte": "", "faits": [], "proposition": CROCHETER_OUVRIR_CALER})),
                  patch.object(Monde, "d20", return_value=20),
                  patch("builtins.input", side_effect=[
                      "je crochète la porte, je l'ouvre et je la cale avec le marteau", "tenter", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--recit-moteur", "--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        porte = reprise.objets["porte"]
        self.assertFalse(porte["verrouillee"])
        self.assertTrue(porte["ouverte"])
        self.assertEqual(porte["bloque_par"], "marteau")
        self.assertIn("en 3 étapes successives", sortie.getvalue())
        self.assertEqual(len(reprise.data["journal"][-1]["etapes"]), 3)

    def test_ordre_impossible_refuse_avant_tout_effet(self):
        m = partie_outillee()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(sequence(etape("ouvrir", "porte"),
                                        etape("crocheter", "porte", outil="crochets", methode="finesse")))
        self.assertEqual(m.data, avant)

    def test_echec_du_crochetage_arrete_la_suite(self):
        m = partie_outillee()
        plan = Moteur(m).preparer(CROCHETER_OUVRIR_CALER)
        with patch.object(Monde, "d20", return_value=2):
            Moteur(m).executer(plan)
        self.assertTrue(m.objets["porte"]["verrouillee"])
        self.assertFalse(m.objets["porte"]["ouverte"])
        self.assertEqual(len(m.data["journal"][-1]["etapes"]), 1)

    def test_destination_refusee_pour_une_action_composee(self):
        m = partie_outillee()
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(sequence(etape("ouvrir", "porte", destination="joueur")))


if __name__ == "__main__":
    unittest.main()
