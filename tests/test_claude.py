"""Adaptateur Anthropic : une réponse rendue en texte est transcrite en appel, réflexion comprise."""
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde

try:
    import anthropic  # noqa: F401  (dépendance facultative : requirements-claude.txt)
except ImportError:
    anthropic = None


def bloc(type_, **champs):
    return SimpleNamespace(type=type_, **champs,
                           model_dump=lambda **_: {"type": type_, **champs})


def reponse(stop, *blocs):
    usage = SimpleNamespace(input_tokens=10, output_tokens=5, cache_read_input_tokens=0,
                            cache_creation_input_tokens=0)
    return SimpleNamespace(stop_reason=stop, content=list(blocs), usage=usage)


def mj_libre(*reponses):
    mj = MJOpenAI("claude-haiku-5-5", connexion="anthropic")
    mj.reflexion = "libre"
    mj.fournisseur.client = MagicMock()
    mj.fournisseur.client.messages.create.side_effect = list(reponses)
    return mj


SCHEMA = {"type": "object", "properties": {"mode": {"type": "string"}}, "required": ["mode"]}


@unittest.skipIf(anthropic is None, "SDK anthropic absent")
class TranscriptionTests(unittest.TestCase):
    def test_reponse_en_texte_transcrite_en_appel_impose(self):
        mj = mj_libre(
            reponse("end_turn", bloc("thinking", thinking="Une question : dialogue.", signature="s"),
                    bloc("text", text="Le mur est en pierre.")),
            reponse("tool_use", bloc("tool_use", name="repondre_au_joueur", input={"mode": "dialogue"}, id="t")))
        arguments = mj._appeler_brut("instr", {"message": "le mur ?"}, "le mur ?", "repondre_au_joueur", SCHEMA)
        brut = mj.dernier_brut
        self.assertEqual(arguments, {"mode": "dialogue"})
        suite = mj.fournisseur.client.messages.create.call_args_list[1].kwargs
        # La relance impose l'outil et renvoie la réponse du modèle, réflexion comprise.
        self.assertEqual(suite["tool_choice"]["name"], "repondre_au_joueur")
        self.assertEqual([b["type"] for b in suite["messages"][1]["content"]], ["thinking", "text"])
        self.assertEqual(mj.derniere_utilisation["output_tokens"], 10)
        self.assertIn({"type": "transcription"}, brut["contenu"])

    def test_appel_direct_sans_relance(self):
        mj = mj_libre(reponse("tool_use", bloc("tool_use", name="repondre_au_joueur",
                                               input={"mode": "action"}, id="t")))
        arguments = mj._appeler_brut("instr", {}, "intention", "repondre_au_joueur", SCHEMA)
        self.assertEqual(arguments, {"mode": "action"})
        self.assertEqual(mj.fournisseur.client.messages.create.call_count, 1)

    def test_transcription_qui_echoue_reste_un_refus(self):
        mj = mj_libre(reponse("end_turn", bloc("text", text="Rien.")), reponse("end_turn", bloc("text", text="Rien.")))
        with self.assertRaisesRegex(ErreurMonde, "proposition unique"):
            mj._appeler_brut("instr", {}, "intention", "repondre_au_joueur", SCHEMA)


if __name__ == "__main__":
    unittest.main()
