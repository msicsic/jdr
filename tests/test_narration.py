import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.improvisation import issue, proposition as improviser
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.narration import controler


def dialogue(texte):
    return {"mode": "dialogue", "texte": texte, "faits": [], "proposition": None}


def segment(verdict, sources=(), locuteur="", citation="", motif=""):
    return {"segments": [{"indice": 0, "verdict": verdict, "sources": list(sources),
                           "locuteur": locuteur, "citation": citation, "motif": motif}]}


class NarrationTests(unittest.TestCase):
    def test_couverture_et_references_du_controle(self):
        texte = "La porte est fermée. Une cloche apparaît."
        with self.assertRaises(ErreurMonde):
            controler(texte, segment("etabli", ["salle"]), {"salle": {}})
        with self.assertRaises(ErreurMonde):
            controler("La porte est fermée.", segment("etabli", ["source_inventee"]), {"salle": {}})

    def test_dialogue_invente_est_revise_puis_sauvegarde_avant_affichage(self):
        invention = "Une seconde cloche est cachée sous le plancher."
        corrige = "Tu te trouves dans le refuge du relais."
        sorties = [dialogue(invention), segment("nouveau", motif="Aucune seconde cloche établie."),
                   dialogue(corrige), segment("etabli", ["salle"])]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties) as appel,
                  patch("builtins.input", side_effect=["mj Que vois-je ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--defi", "--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertEqual(appel.call_count, 4)
        self.assertNotIn(invention, sortie.getvalue())
        self.assertIn(corrige, sortie.getvalue())
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], corrige)
        self.assertEqual(len([o for o in reprise.objets.values() if o["type"] == "tresor" and "cloche" in o["nom"]]), 1)
        self.assertEqual(reprise.data["objectif_partie"]["objet"], "cloche")

    def test_refus_repetes_ne_montrent_aucune_invention(self):
        invention = "Une seconde cloche est cachée sous le plancher."
        sorties = [item for _ in range(3) for item in
                   (dialogue(invention), segment("nouveau", motif="Fait absent du monde."))]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties),
                  patch("builtins.input", side_effect=["mj Que vois-je ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertNotIn(invention, sortie.getvalue())
        self.assertFalse(reprise.data.get("narrations_mj"))

    def test_parole_attribuee_devient_un_evenement_entendu_apres_rechargement(self):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        citation = "La seconde cloche est sous le plancher."
        texte = "Gorm dit : « " + citation + " »."
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      dialogue(texte), segment("parole", locuteur="marchand", citation=citation)]),
                  patch("builtins.input", side_effect=["mj Gorm, salut.", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(texte, sortie.getvalue())
        self.assertEqual(reprise.data["paroles_pnj"][-1]["texte"], citation)
        self.assertIn("joueur", reprise.data["paroles_pnj"][-1]["auditeurs"])
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_recit_d_improvisation_passe_par_le_meme_controle(self):
        p = improviser("je chante", issue("Une cloche surgit.", []))
        reponse = {"mode": "action", "texte": "", "faits": [], "proposition": p}
        mj = MJOpenAI()
        with patch.object(mj, "_appeler_brut", side_effect=[
            reponse, segment("nouveau", motif="Apparition sans effet."),
            reponse, segment("nouveau", motif="Apparition sans effet."),
            reponse, segment("nouveau", motif="Apparition sans effet.")]) as appel:
            with self.assertRaises(ErreurMonde):
                mj._appeler("instructions", {"faits": nouveau_monde().contexte()},
                           "je chante", "repondre_au_joueur", {})
        self.assertEqual(appel.call_count, 6)


if __name__ == "__main__":
    unittest.main()
