import copy
import io
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.commandes import analyser
from donjon.dialogues import interlocuteurs
from donjon.mj import MJOpenAI
from donjon.monde import Monde, ErreurMonde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.sons import auditeurs, portee


def appel(mode="appel"):
    return sequence(etape("emettre_son", "joueur", methode=mode))


class SonsTests(unittest.TestCase):
    def test_crier_local_sans_jet_et_sans_creer_de_secours(self):
        m = nouveau_atelier()
        avant = copy.deepcopy(m.data)
        moteur = Moteur(m)
        plan = moteur.preparer(analyser(m, "je crie à l'aide"))
        self.assertEqual(m.data, avant)
        self.assertFalse(plan.stat)
        with patch.object(Monde, "d20", side_effect=AssertionError("Pas de jet pour crier")):
            texte = moteur.executer(plan)
        self.assertIn("Tu cries à l'aide", texte)
        self.assertIn("aucune réponse", texte)
        self.assertEqual(set(m.objets), set(avant["objets"]))
        self.assertEqual(m.data["sons"][-1]["auditeurs"], [])
        self.assertEqual(m.objets["marchand"]["humeur"], avant["objets"]["marchand"]["humeur"])
        self.assertEqual((m.data["minutes"], m.data["bruit"], m.data["revision"]), (1, 3, 1))
        # Une action ultérieure ne doit pas réintroduire une alerte mondiale.
        moteur.executer(moteur.preparer(appel()))
        moteur.executer(moteur.preparer(proposition("examiner", "hache")))
        self.assertEqual(m.objets["marchand"]["humeur"], "calme")

    def test_audition_persistante_sans_reveler_un_pnj_distant(self):
        m = nouveau_monde()
        moteur = Moteur(m)
        texte = moteur.executer(moteur.preparer(appel()))
        self.assertNotIn("Gorm", texte)
        self.assertEqual(m.data["sons"][-1]["auditeurs"], ["marchand"])
        self.assertEqual(m.objets["marchand"]["humeur"], "inquiet")
        self.assertEqual(m.objets["marchand"]["lieu"], "echoppe")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            m.sauver(path)
            m = Monde.charger(path)
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition("aller", "ouest")))
        self.assertEqual(interlocuteurs(m)["marchand"]["dernier_son_entendu"]["nature"], "appel")

    def test_portes_attenuation_et_lieux_non_relies(self):
        m = nouveau_monde()
        self.assertEqual(portee(m, "crypte", 3)["antichambre"], 1)
        self.assertNotIn("echoppe", portee(m, "crypte", 3))
        m.objets["porte"]["ouverte"] = True
        self.assertEqual(portee(m, "crypte", 3)["echoppe"], 1)
        self.assertEqual(auditeurs(m, "crypte", 3), ["marchand"])
        m.objets["marchand"]["entend"] = False
        self.assertEqual(auditeurs(m, "crypte", 3), [])
        m = nouveau_atelier()
        self.assertIn("terrasse", portee(m, "cour", 3))
        self.assertNotIn("echoppe", portee(m, "cour", 3))

    def test_pas_de_destination_forcee_et_source_vocale_verifiee(self):
        m = nouveau_atelier()
        for e in (etape("emettre_son", "marchand", methode="appel"),
                  etape("emettre_son", "joueur", "echoppe", methode="appel"),
                  etape("emettre_son", "joueur", outil="hache", methode="appel")):
            with self.assertRaises(ErreurMonde):
                Moteur(m).preparer(sequence(e))
        m.joueur["peut_parler"] = False
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(appel())

    def test_son_composable_et_pnj_visible_entend(self):
        m = nouveau_monde()
        m.joueur.update(salle="echoppe", position=[1, 2])
        p = sequence(etape("emettre_son", "joueur", methode="sifflement"),
                     etape("allumer", "lanterne"))
        m.objets["lanterne"]["allume"] = False
        # L'échoppe a déjà un brasero ; la composition reste validable.
        moteur = Moteur(m)
        texte = moteur.executer(moteur.preparer(p))
        self.assertIn("Gorm le marchand entend ton sifflement", texte)
        self.assertTrue(m.objets["lanterne"]["allume"])
        self.assertEqual(len(m.data["journal"][-1]["etapes"]), 2)

    def test_console_cri_hors_ligne_et_luna_avec_phrase_libre(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "atelier.json"
            with patch.object(MJOpenAI, "_appeler", side_effect=AssertionError("Pas d'appel local")), patch("builtins.input", side_effect=["je crie a l'aide", "quitter"]), patch("sys.stdout", io.StringIO()) as out:
                jeu.main(["--console", "--offline", "--atelier", "--save", str(path)])
            self.assertIn("Tu cries à l'aide", out.getvalue())
            self.assertEqual(Monde.charger(path).data["sons"][-1]["nature"], "appel")
        m = nouveau_atelier()
        def repondre(instructions, entree, *args):
            self.assertIn("emettre_son", instructions)
            return {"mode": "action", "texte": "", "faits": ["joueur"], "proposition": appel()}
        with patch.object(MJOpenAI, "_appeler", side_effect=repondre):
            r = MJOpenAI().echanger(m, "Je lance un appel à l'aide aussi fort que possible")
        self.assertEqual(r["proposition"], appel())
        self.assertEqual(m.data["revision"], 0)


if __name__ == "__main__":
    unittest.main()
