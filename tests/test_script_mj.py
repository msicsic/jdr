"""Essai du MJ qui répond par un appel Python à l'API du moteur, lu sans exécution."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon import script_mj
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.paroles import SCHEMA_PAROLE
from tests.test_narration import dialogue, segment

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "mode": {"type": "string", "enum": ["dialogue", "parole_joueur"]},
        "texte": {"type": "string"},
        "faits": {"type": "array", "items": {"type": "string", "enum": ["salle", "interlocuteurs"]}},
        "proposition": {"anyOf": [{"type": "null"}, SCHEMA_PAROLE]},
    },
    "required": ["mode", "texte", "faits", "proposition"],
}


def lire(source):
    return script_mj.lire(source, "repondre_au_joueur", SCHEMA)


class LectureTests(unittest.TestCase):
    def test_l_api_presente_la_fonction_et_ses_formes(self):
        texte = script_mj.api("repondre_au_joueur", SCHEMA)
        self.assertIn('mode: Literal["dialogue", "parole_joueur"],', texte)
        self.assertIn("proposition: None | PropositionPersonnage,", texte)
        self.assertIn("class PropositionPersonnage(TypedDict):", texte)
        self.assertIn("contenu: list[Contenu]  # au plus 3 éléments", texte)

    def test_constructeur_et_dictionnaire_donnent_la_meme_valeur(self):
        attendu = {"mode": "parole_joueur", "texte": "", "faits": ["interlocuteurs"],
                   "proposition": {"personnage": "marchand", "replique": "Bonjour.", "contenu": []}}
        self.assertEqual(lire('```python\nrepondre_au_joueur(mode="parole_joueur", texte="", faits=["interlocuteurs"],'
                              ' proposition=PropositionPersonnage(personnage="marchand", replique="Bonjour.",'
                              ' contenu=[]))\n```'), attendu)
        self.assertEqual(lire(script_mj.ecrire("repondre_au_joueur", attendu)), attendu)

    def test_rien_n_est_execute(self):
        for source in ("import os", "__import__('os').system('echo x')",
                       'repondre_au_joueur(mode=open("x"), texte="", faits=[], proposition=None)',
                       'repondre_au_joueur(mode=os.name, texte="", faits=[], proposition=None)',
                       'repondre_au_joueur(mode="dialogue", texte="a" * 3, faits=[], proposition=None)',
                       'x = 1\nrepondre_au_joueur(mode="dialogue", texte="a", faits=[], proposition=None)',
                       'repondre_au_joueur("dialogue", "a", [], None)',
                       'repondre_au_joueur(**{"mode": "dialogue"})'):
            with self.subTest(source=source), self.assertRaises(script_mj.ErreurScript):
                lire(source)

    def test_chaque_ecart_est_decrit_par_son_chemin(self):
        with self.assertRaises(script_mj.ErreurScript) as refus:
            lire('repondre_au_joueur(mode="parole_joueur", texte="", faits=["objet:marchand"], proposition='
                 '{"personnage": "marchand", "replique": "x", "contenu": [{"type": "affirmation", "sujet": "",'
                 ' "attribut": "", "value": ""}]})')
        message = str(refus.exception)
        self.assertIn('faits[0] : "objet:marchand" n\'est pas permis ; valeurs possibles : "salle", "interlocuteurs".',
                      message)
        self.assertIn("proposition.contenu[0] : champ manquant « valeur ».", message)
        self.assertIn("proposition.contenu[0] : champ inconnu « value »", message)


def scripte(*reponses):
    """Faux modèle : chaque réponse est (fonction attendue, valeur) écrite en script."""
    file = list(reponses)
    recues = []

    def appeler(_mj, instructions, entree, intention, fonction, schema):
        recues.append(entree)
        assert fonction == script_mj.FONCTION and schema == script_mj.SCHEMA
        attendue, valeur = file.pop(0)
        assert f"un appel à {attendue}(...)" in instructions, attendue
        return {"script": valeur if isinstance(valeur, str) else script_mj.ecrire(attendue, valeur)}
    return appeler, recues


class PartieEnScriptTests(unittest.TestCase):
    def jouer(self, appeler):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", appeler),
                  patch("builtins.input", side_effect=["mj Gorm, salut.", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api",
                                           "--langage", "script"]), 0)
            return sortie.getvalue(), Monde.charger(chemin)

    def test_une_parole_ecrite_en_script_est_entendue_apres_rechargement(self):
        citation = "La seconde cloche est sous le plancher."
        texte = "Gorm dit : « " + citation + " »."
        appeler, _ = scripte(("repondre_au_joueur", dialogue(texte)),
                             ("auditer_narration", segment("parole", locuteur="marchand", citation=citation)))
        sortie, reprise = self.jouer(appeler)
        self.assertIn(texte, sortie)
        self.assertEqual(reprise.data["paroles_pnj"][-1]["texte"], citation)
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_un_fait_invente_est_signale_puis_corrige(self):
        # Cas du banc Haiku : un fait cité hors de la liste fournie faisait perdre le tour.
        citation = "Je tiens comme je peux."
        texte = "Gorm dit : « " + citation + " »."
        invente = {**dialogue(texte), "faits": ["objet:gorm"]}
        appeler, recues = scripte(("repondre_au_joueur", invente), ("repondre_au_joueur", dialogue(texte)),
                                  ("auditer_narration", "auditer_narration(segments=[{'indice': 0}])"),
                                  ("auditer_narration", segment("parole", locuteur="marchand", citation=citation)))
        sortie, reprise = self.jouer(appeler)
        self.assertIn('"objet:gorm" n\'est pas permis', recues[1]["erreur_script"]["erreur"])
        self.assertIn("champ manquant « verdict »", recues[3]["erreur_script"]["erreur"])
        self.assertIn(texte, sortie)
        self.assertEqual(reprise.data["paroles_pnj"][-1]["texte"], citation)

    def test_deux_scripts_refuses_ne_changent_rien(self):
        appeler, _ = scripte(("repondre_au_joueur", "import os"), ("repondre_au_joueur", "repondre_au_joueur()"))
        sortie, reprise = self.jouer(appeler)
        self.assertIn("Réponse du MJ invalide. Aucune action appliquée.", sortie)
        self.assertEqual(reprise.data.get("paroles_pnj", []), [])


class JsonNonStrictTests(unittest.TestCase):
    def test_un_ecart_de_format_est_renvoye_une_fois_au_modele(self):
        mj = MJOpenAI("mimo-v2.6-flash", connexion="mimo")
        faux = {"mode": "dialogue", "texte": "Oui.", "faits": ["objet:x"], "proposition": None}
        bon = {**faux, "faits": ["salle"]}
        with patch.object(MJOpenAI, "_appeler_brut", side_effect=[faux, bon]) as appel:
            self.assertEqual(mj._demander("Règles.", {}, "x", "repondre_au_joueur", SCHEMA), bon)
        self.assertIn('"objet:x"', appel.call_args_list[1][0][1]["erreur_script"]["erreur"])

    def test_un_schema_strict_n_est_pas_revalide(self):
        mj = MJOpenAI("gpt-6-luna", connexion="api")
        with patch.object(MJOpenAI, "_appeler_brut", return_value={"x": 1}) as appel:
            self.assertEqual(mj._demander("Règles.", {}, "x", "repondre_au_joueur", SCHEMA), {"x": 1})
        self.assertEqual(appel.call_count, 1)

    def test_sans_strict_le_schema_n_est_plus_impose_mais_verifie(self):
        mj = MJOpenAI("gpt-6-luna", connexion="api", strict=False)
        faux = {"mode": "dialogue", "texte": "Oui.", "faits": ["objet:x"], "proposition": None}
        bon = {**faux, "faits": ["salle"]}
        with patch.object(MJOpenAI, "_appeler_brut", side_effect=[faux, bon]):
            self.assertEqual(mj._demander("Règles.", {}, "x", "repondre_au_joueur", SCHEMA), bon)
        sans_renvoi = MJOpenAI("gpt-6-luna", connexion="api", strict=False, renvoi=False)
        with patch.object(MJOpenAI, "_appeler_brut", return_value=faux) as appel:
            self.assertEqual(sans_renvoi._demander("Règles.", {}, "x", "repondre_au_joueur", SCHEMA), faux)
        self.assertEqual(appel.call_count, 1)

    def test_deux_ecarts_de_suite_arretent_le_tour(self):
        mj = MJOpenAI("mimo-v2.6-flash", connexion="mimo")
        with patch.object(MJOpenAI, "_appeler_brut", return_value={"mode": "autre"}), \
                self.assertRaises(ErreurMonde):
            mj._demander("Règles.", {}, "x", "repondre_au_joueur", SCHEMA)


if __name__ == "__main__":
    unittest.main()
