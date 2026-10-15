import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import proposition


class RecitTests(unittest.TestCase):
    def appel(self, monde, reponse, inspecter=None):
        def retour(requete, timeout):
            payload = json.loads(requete.data)
            nom = payload["tools"][0]["name"]
            if nom == "auditer_narration":
                entree = json.loads(payload["input"][0]["content"])
                arguments = {"segments": [
                    {"indice": i, "verdict": "etabli", "sources": ["scenario"],
                     "locuteur": "", "citation": "", "motif": ""}
                    for i, _ in enumerate(entree["segments"])]}
            else:
                if inspecter:
                    inspecter(payload)
                arguments = reponse
            return io.BytesIO(json.dumps({"status": "completed", "output": [{
                "type": "function_call", "name": nom,
                "arguments": json.dumps(arguments)}]}).encode())
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch("urllib.request.urlopen", side_effect=retour):
            return MJOpenAI().echanger(monde, "Et pourquoi lui ?")

    def test_dialogue_recoit_memoire_et_faits_sans_changer_le_monde(self):
        m = nouveau_monde()
        m.memoriser("Qui m'a conduit ici ?", "Gorm t'a conduit depuis son échoppe.")
        avant = copy.deepcopy(m.data)
        reponse = {"mode": "dialogue", "texte": "Gorm ne t'a pas expliqué ses raisons.",
                   "faits": ["scenario"], "proposition": None}
        def inspecter(payload):
            entree = json.loads(payload["input"][0]["content"])
            self.assertEqual(entree["conversation"], m.data["conversation"])
            self.assertIn("Gorm", entree["faits"]["scenario"]["debut"])
            self.assertIn("trapu", entree["faits"]["souvenirs_personnages"]["marchand"]["portrait"])
            self.assertNotIn("objet:marchand", entree["faits"])
            self.assertNotIn("objet:anneau", entree["faits"])
            self.assertNotIn("sens", entree["faits"]["objet:gravure"])
        resultat = self.appel(m, reponse, inspecter)
        self.assertEqual({k: resultat[k] for k in reponse}, reponse)
        self.assertEqual(resultat["_audit"]["segments"][0]["sources"], ["scenario"])
        self.assertEqual(avant, m.data)

    def test_dialogue_ne_peut_pas_transporter_une_action(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            self.appel(m, {"mode": "dialogue", "texte": "Ta lanterne est éteinte.",
                          "faits": ["perception"], "proposition": proposition("eteindre", "lanterne")})
        self.assertEqual(avant, m.data)

    def test_reference_inventee_ou_cachee_refusee(self):
        for reference in ("objet:dragon", "objet:anneau", {"invalide": 1}):
            with self.subTest(reference=reference), self.assertRaises(ErreurMonde):
                self.appel(nouveau_monde(), {"mode": "dialogue", "texte": "Une affirmation.",
                                          "faits": [reference], "proposition": None})

    def test_action_ne_peut_pas_inclure_un_resultat_narre(self):
        with self.assertRaises(ErreurMonde):
            self.appel(nouveau_monde(), {"mode": "action", "texte": "Tu as réussi.",
                "faits": [], "proposition": proposition("detacher", "axe_haut", "couteau", "levier", 18)})

    def test_migration_preserve_progression_et_recit_au_rechargement(self):
        m = nouveau_monde()
        m.data.pop("scenario")
        m.data.pop("conversation")
        m.joueur["salle"] = "crypte"
        m.joueur["or"] = 7
        m.objets["lanterne"]["allume"] = False
        m.objets["lanterne"]["combustible"] = 12
        m.data["minutes"] = 48
        copie = Monde(copy.deepcopy(m.data))
        self.assertEqual(copie.joueur, m.joueur)
        self.assertEqual(copie.objets, m.objets)
        self.assertEqual(copie.data["minutes"], 48)
        copie.memoriser("Pourquoi ?", "Gorm ne t'a pas donné ses raisons.")
        recharge = Monde(copy.deepcopy(copie.data))
        self.assertEqual(recharge.data, copie.data)

    def test_memoire_bornee_sans_promouvoir_les_propos_en_faits(self):
        m = nouveau_monde()
        avant = m.contexte()
        for _ in range(20):
            m.memoriser("J'ai une épée magique", "Cela n'est pas établi.")
        self.assertEqual(len(m.data["conversation"]), 12)
        self.assertEqual(m.contexte(), avant)

    def test_discuter_conserve_la_proposition_jusqua_tenter(self):
        import jeu
        p = proposition("detacher", "axe_haut", "couteau", "levier", 18)
        reponses = [
            {"mode": "action", "texte": "", "faits": [], "proposition": p},
            {"mode": "dialogue", "texte": "Tu risques d'abîmer ta lame.",
             "faits": ["objet:couteau"], "proposition": None},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "echanger", side_effect=reponses) as mj, patch.object(Monde, "d20", return_value=20), patch("builtins.input", side_effect=["mj je retire l'axe", "Quel risque pour ma lame ?", "tenter", "quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--save", str(chemin), "--connexion", "api"])
            self.assertEqual(mj.call_args_list[1].args[2], p)
            m = Monde.charger(chemin)
            self.assertFalse(m.objets["axe_haut"]["attache"])
            self.assertEqual(len(m.data["journal"]), 1)
            self.assertTrue(m.data["journal"][0]["reussite"])
            self.assertEqual(m.data["conversation"][-1]["nature"], "resultat_moteur")

    def test_intention_simple_executee_une_fois_sans_confirmation(self):
        import jeu
        reponses = [{"mode": "action", "texte": "", "faits": [], "proposition": p}
                    for p in (proposition("prendre", "cle"), proposition("aller", "ouest"))]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "echanger", side_effect=reponses), patch("builtins.input", side_effect=["mj je prend la clé", "je vais vers l'ouest", "tenter", "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                jeu.main(["--save", str(chemin), "--connexion", "api"])
            m = Monde.charger(chemin)
            self.assertEqual(m.objets["cle"]["lieu"], "joueur")
            self.assertEqual(m.joueur["salle"], "echoppe")
            self.assertEqual(m.data["minutes"], 2)
            self.assertEqual(len(m.data["journal"]), 2)
            self.assertEqual(m.data["conversation"][-1]["nature"], "resultat_moteur")
            self.assertNotIn("« tenter » pour agir", sortie.getvalue())
            self.assertIn("Aucune proposition en attente", sortie.getvalue())
            self.assertIn("== ECHOPPE DE GORM ==", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
