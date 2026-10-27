"""Le sol public est relatif à Corvus ; l'état conserve un lieu physique."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jeu
from donjon.carte import carte, objets_visibles_cases
from donjon.improvisation import proposition, issue, effet
from donjon.mj import MJOpenAI
from donjon.monde import Monde, ErreurMonde, nouveau_monde
from donjon.moteur import Moteur
from donjon.operations import sequence, etape
from donjon.rendu import regarder
from donjon.spatial import champ_visible
from tests.support import simuler_couverture
from tests import test_matiere


class PoserSolTests(unittest.TestCase):
    def setUp(self):
        simuler_couverture(self)

    def console(self, m, p):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            m.sauver(path)
            reponse = dict(mode="action", texte="", faits=[], proposition=p)
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                 patch.object(MJOpenAI, "_appeler", return_value=reponse), \
                 patch("builtins.input", side_effect=["je pose au sol", "tenter", "quitter"]), \
                 patch("sys.stdout", io.StringIO()) as sortie:
                jeu.main(["--recit-moteur", "--console", "--connexion", "api", "--save", str(path)])
            return Monde.charger(path), sortie.getvalue()

    def verifier_sol(self, m, cible):
        o = m.objets[cible]
        self.assertEqual(o["lieu"], m.joueur["salle"])
        self.assertEqual(o["position"], m.joueur["position"])
        self.assertTrue(m.visible(cible))
        self.assertIn(o["nom"], regarder(m))
        self.assertIn(o["nom"], carte(m))
        dessines = {o["id"]: (s, pos) for o, s, pos in objets_visibles_cases(m, champ_visible(m))}
        self.assertEqual(dessines[cible], (m.joueur["salle"], tuple(m.joueur["position"])))

    def test_torche_console_sequence_et_ancienne_destination(self):
        for destination in ("sol", "antichambre"):
            with self.subTest(destination=destination):
                m, texte = self.console(nouveau_monde(), sequence(
                    etape("deplacer", "torche", "joueur"), etape("deplacer", "torche", destination)))
                self.verifier_sol(m, "torche")
                self.assertIn("au sol", texte)

    def test_planche_prelevee_puis_posee_console(self):
        m = test_matiere.LotTests().lot_decrit()
        m, _ = self.console(m, sequence(etape("prelever", "planches", "joueur"),
                                       etape("deplacer", "planches_1", "sol")))
        self.verifier_sol(m, "planches_1")
        self.assertEqual(m.objets["planches"]["physique"]["pieces"], 1)

    def test_prelevement_direct_au_sol(self):
        for destination in ("sol", "ancienne_forme"):
            m = test_matiere.LotTests().lot_decrit()
            destination = "sol" if destination == "sol" else m.joueur["salle"]
            m, _ = self.console(m, sequence(etape("prelever", "planches", destination)))
            self.verifier_sol(m, "planches_1")

    def test_improvisation_pose_avec_le_meme_contrat(self):
        m = nouveau_monde()
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(sequence(etape("deplacer", "cle", "joueur"))))
        p = proposition("Laisser tomber la clé", issue("La clé tombe.",
                        [effet("deplacer", "cle", "sol")]), cibles=["cle"], approche="manipulation")
        m, _ = self.console(m, p)
        self.verifier_sol(m, "cle")

    def test_autre_salle_refusee_sans_mutation(self):
        m = nouveau_monde()
        avant = m.copier().data
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(sequence(etape("deplacer", "torche", "echoppe")))
        self.assertIn("sol", refus.exception.attendu)
        self.assertIn("echoppe", refus.exception.attendu)
        self.assertEqual(m.data, avant)

