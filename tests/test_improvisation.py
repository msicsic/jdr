import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition as action
from donjon.improvisation import proposition, issue, effet
from donjon.mj import MJOpenAI
from donjon.rendu import decrire


def chant():
    return proposition("Fredonner une chanson", issue("Tu fredonnes quelques mesures.", [effet("son", "joueur", valeur=1)]), bruit=1)


def marque():
    return proposition("Graver un repère", issue("Tu traces une flèche sur le bois.", [effet("marquer", "perche_1", texte="flèche vers le nord")]),
                       cibles=["perche_1"], outil="couteau", approche="manipulation", minutes=2)


def jongler():
    return proposition("Jongler avec une clé", issue("Tu rattrapes la clé."), issue("La clé tombe au sol.", [effet("deplacer", "cle", "antichambre")]),
                       cibles=["cle"], approche="adresse", stat="DEX", difficulte=12)


def reponse(p):
    return {"mode": "action", "texte": "", "faits": ["improvisation"], "proposition": p}


class ImprovisationTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_atelier()
        self.moteur = Moteur(self.m)

    def test_geste_sans_jet_purete_et_evenement_persistant(self):
        p = proposition("S'étirer", issue("Tu étires tes bras et délies tes épaules."))
        avant = copy.deepcopy(self.m.data)
        plan = self.moteur.preparer(p, "MJ")
        self.assertEqual(self.m.data, avant)
        self.assertFalse(plan.stat)
        self.assertIn("S'étirer", plan.resume(self.m))
        with patch.object(Monde, "d20", side_effect=AssertionError("Sans dé")):
            texte = self.moteur.executer(plan)
        self.assertIn("délies", texte)
        self.assertEqual(self.m.data["minutes"], 1)
        self.assertEqual(self.m.joueur["pv"], 18)
        self.assertEqual(self.m.data["gestes_improvises"][-1]["intention"], "S'étirer")

    def test_son_entendu_sans_reponse_inventee_et_isolation(self):
        self.moteur.executer(self.moteur.preparer(chant()))
        self.assertFalse(self.m.data["sons"][-1]["auditeurs"])
        from donjon.monde import nouveau_monde
        crypte = nouveau_monde()
        crypte.joueur["salle"] = "echoppe"
        Moteur(crypte).executer(Moteur(crypte).preparer(chant()))
        self.assertEqual(crypte.objets["marchand"]["dernier_son_entendu"]["intention"], "Fredonner une chanson")
        self.assertFalse(crypte.data["engagements"])

    def test_marque_cree_detail_examinable_et_sauvegarde(self):
        avant = copy.deepcopy(self.m.data)
        plan = self.moteur.preparer(marque())
        self.assertEqual(self.m.data, avant)
        self.moteur.executer(plan)
        self.assertEqual(self.m.objets["marque_1"]["lieu"], "perche_1")
        self.assertIn("flèche vers le nord", decrire(self.m, "marque_1", detail=True))
        self.assertIn("marque 1", decrire(self.m, "perche_1", detail=True))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"m.json"
            self.m.sauver(p)
            charge = Monde.charger(p)
            self.assertEqual(charge.data, self.m.data)
            self.assertIn("flèche vers le nord", decrire(charge, "marque_1", detail=True))

    def test_marquer_sans_outil_ou_sur_pnj_interdit(self):
        for cas in ("outil", "pnj", "inaccessible", "noir"):
            with self.subTest(cas=cas):
                p = marque()
                m = self.m.copier()
                if cas == "outil": p["outil"] = ""
                if cas == "pnj": p["reussite"]["effets"][0]["cible"] = "marchand"
                if cas == "inaccessible": m.objets["perche_1"]["lieu"] = "crypte"
                if cas == "noir": m.data["salles"]["cour"]["lumiere_naturelle"] = 0
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde): Moteur(m).preparer(p)
                self.assertEqual(m.data, avant)

    def test_echec_deplace_reellement_et_dd_memorisee(self):
        from donjon.monde import nouveau_monde
        m = nouveau_monde()
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(action("prendre", "cle")))
        with patch.object(Monde, "d20", return_value=1):
            t = moteur.executer(moteur.preparer(jongler()))
        self.assertEqual(m.objets["cle"]["lieu"], "antichambre")
        self.assertIn("tombe au sol", t)
        moteur.executer(moteur.preparer(action("prendre", "cle")))
        p = jongler()
        p["difficulte"] = 18
        self.assertEqual(moteur.preparer(p).dd, 12)

    def test_pas_de_contournement_vol_attaches_poids_teleportation(self):
        from donjon.monde import nouveau_monde
        for cible, salle, destination in (("crochets", "echoppe", "joueur"), ("porte", "antichambre", "joueur"),
                                         ("perche_1", "cour", "crypte"), ("perche_1", "cour", "joueur")):
            with self.subTest(cible=cible, destination=destination):
                m = self.m.copier() if salle == "cour" else nouveau_monde()
                m.joueur["salle"] = salle
                if cible == "perche_1" and destination == "joueur": m.objets[cible]["masse"] = 99
                p = proposition("Déplacer", issue("Tu déplaces l'objet.", [effet("deplacer", cible, destination)]), cibles=[cible])
                with self.assertRaises(ErreurMonde): Moteur(m).preparer(p)

    def test_consequences_bornees_et_jet_obligatoire_pour_blessure(self):
        for pv, effets, stat in ((18, [effet("blesser", "joueur", valeur=4)], "DEX"),
                                (2, [effet("blesser", "joueur", valeur=2)], "DEX"),
                                (18, [effet("blesser", "joueur", valeur=2)]*2, "DEX"),
                                (18, [effet("blesser", "joueur", valeur=1)], "")):
            m = self.m.copier()
            m.joueur["pv"] = pv
            p = proposition("Faire un effort", issue("Tu te cognes.", effets), issue("Tu renonces.") if stat else None,
                            approche="effort", stat=stat, difficulte=12 if stat else 0)
            with self.assertRaises(ErreurMonde): Moteur(m).preparer(p)

    def test_plan_mute_et_revision_revalides(self):
        plan = self.moteur.preparer(chant())
        plan.effets = [("payer", "crochets", -100)]
        self.moteur.executer(plan)
        self.assertEqual(self.m.joueur["or"], 24)
        with self.assertRaises(ErreurMonde): self.moteur.executer(plan)

    def test_refus_technique_repare_sans_second_modele(self):
        for r in ({"mode": "dialogue", "texte": "Chanter n'est pas pris en charge par le moteur.", "faits": [], "proposition": None},
                  reponse(action("impossible", justification="Le moteur ne permet pas de chanter."))):
            with patch.object(MJOpenAI, "_appeler", side_effect=[r, reponse(chant())]) as api:
                sortie = MJOpenAI().echanger(self.m, "je chante")
            self.assertEqual(api.call_count, 2)
            self.assertEqual(sortie["proposition"], chant())
            self.assertEqual(self.m.data["revision"], 0)

    def test_question_sans_action_et_une_seule_correction(self):
        with patch.object(MJOpenAI, "_appeler", return_value=reponse(chant())) as api:
            sortie = MJOpenAI().echanger(self.m, "Est-ce que je peux chanter ?")
        self.assertEqual(api.call_count, 2)
        self.assertEqual(sortie["mode"], "dialogue")
        self.assertEqual(self.m.data["revision"], 0)
        invalide = chant()
        invalide["minutes"] = 500
        refus = {"mode": "dialogue", "texte": "Le moteur ne permet pas cela.", "faits": [], "proposition": None}
        with patch.object(MJOpenAI, "_appeler", side_effect=[refus, reponse(invalide)]) as api:
            sortie = MJOpenAI().echanger(self.m, "je chante")
        self.assertEqual(api.call_count, 2)
        self.assertEqual(sortie["mode"], "dialogue")

    def test_console_applique_et_sauve_geste_sans_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"partie.json"
            with patch("builtins.input", side_effect=["je fredonne pour passer le temps", "quitter"]), \
                 patch("jeu.MJOpenAI.echanger", return_value=reponse(chant())), \
                 patch("jeu.MJOpenAI.raconter_resultat", side_effect=AssertionError("Pas de second appel de narration")), \
                 patch("sys.stdout", new_callable=io.StringIO) as output:
                jeu.main(["--console", "--atelier", "--connexion", "api", "--save", str(p)])
            m = Monde.charger(p)
            self.assertEqual(m.data["minutes"], 1)
            self.assertEqual(m.data["gestes_improvises"][-1]["intention"], "Fredonner une chanson")
            self.assertNotIn("« tenter »", output.getvalue())
