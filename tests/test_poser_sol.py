"""Le sol public est relatif à Corvus ; l'état conserve un lieu physique."""
import io
import copy
import json
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

    def test_dossier_de_contre_revue_decrit_le_depot_sans_salle_destination(self):
        from donjon.couverture_action import entree

        cas = []
        for destination in ("sol", "antichambre"):
            m = nouveau_monde()
            Moteur(m).executer(Moteur(m).preparer(sequence(etape("deplacer", "torche", "joueur"))))
            cas.append((m, sequence(etape("deplacer", "torche", destination))))
        m = test_matiere.LotTests().lot_decrit()
        cas.extend((m.copier(), p) for p in (
            sequence(etape("prelever", "planches", "sol")),
            sequence(etape("prelever", "planches", "joueur"), etape("deplacer", "planches_1", "sol"))))
        m = nouveau_monde()
        Moteur(m).executer(Moteur(m).preparer(sequence(etape("deplacer", "cle", "joueur"))))
        cas.append((m, proposition("Jongler", issue("La clé tombe.", [effet("deplacer", "cle", "sol")]),
            issue("La clé tombe.", [effet("deplacer", "cle", "sol")]), cibles=["cle"],
            approche="adresse", stat="DEX", difficulte=12)))

        def verifier_plan(plan):
            for effets in (plan["effets_reussite"], plan["effets_echec"]):
                for op, cible, destination in effets:
                    if op == "transferer" and isinstance(destination, dict):
                        self.assertEqual(destination, {"destination": "sol", "position": "à tes pieds"})
                        self.assertIn("au sol, à tes pieds", plan["titre"] + plan["information"])
            for enfant in plan["etapes"]:
                verifier_plan(enfant)

        for m, p in cas:
            with self.subTest(proposition=p):
                plan = Moteur(m).preparer(p)
                avant = copy.deepcopy((m.data, plan))
                dossier = entree("je pose au sol", plan, m)
                verifier_plan(dossier["plan"])
                self.assertIn('"destination": "sol"', json.dumps(dossier["plan"], ensure_ascii=False))
                self.assertNotIn('"' + m.joueur["salle"] + '"', json.dumps(dossier["plan"], ensure_ascii=False))
                self.assertEqual(m.data, avant[0])
                self.assertEqual(plan, avant[1])

    def test_repere_du_depot_compile_ne_depend_pas_de_la_salle_initiale_du_dossier(self):
        from donjon.deplacement_objet import presenter_effet
        m = nouveau_monde()
        # Le dépôt a été validé dans une autre étape de la séquence : le dossier
        # peut être construit avant son franchissement, ou relu après son retour.
        self.assertNotEqual(m.joueur["salle"], "echoppe")
        self.assertEqual(presenter_effet(m, ("transferer", "torche", "echoppe")),
                         ["transferer", "torche", {"destination": "sol", "position": "à tes pieds"}])

