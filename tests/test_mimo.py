"""Essai d'un autre fournisseur : la traduction vers Chat Completions garde le contrat du MJ."""
import json
import unittest
from unittest.mock import patch

from donjon.mj import MJOpenAI, decoder_imbrique, depuis_chat, vers_chat


class ReponseFactice:
    def __init__(self, corps):
        self.corps = json.dumps(corps).encode("utf-8")

    def read(self, *_):
        return self.corps

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"texte": {"type": "string"}}, "required": ["texte"]}


class TraductionTests(unittest.TestCase):
    def test_l_outil_reste_force_et_le_schema_strict(self):
        payload = {"model": "mimo-v2.6-flash", "instructions": "Règles.",
                   "input": [{"role": "user", "content": "{}"}],
                   "tools": [{"type": "function", "name": "repondre", "description": "d",
                              "parameters": SCHEMA, "strict": True}],
                   "reasoning": {"effort": "medium"}, "max_output_tokens": 3000}
        chat = vers_chat(payload)
        self.assertEqual(chat["messages"][0], {"role": "system", "content": "Règles."})
        self.assertEqual(chat["tool_choice"], {"type": "function", "function": {"name": "repondre"}})
        self.assertTrue(chat["tools"][0]["function"]["strict"])
        self.assertEqual(chat["reasoning_effort"], "medium")

    def test_un_appel_unique_est_rendu_au_controle(self):
        brut = {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
            {"type": "function", "function": {"name": "repondre", "arguments": '{"texte": "Bonjour."}'}}]}}],
                "usage": {"total_tokens": 12}}
        with patch.dict("os.environ", {"MIMO_API_KEY": "cle-de-test"}), \
                patch("urllib.request.urlopen", return_value=ReponseFactice(brut)) as appel:
            mj = MJOpenAI("mimo-v2.6-flash", connexion="mimo")
            self.assertEqual(mj._appeler_brut("Règles.", {}, "bonjour", "repondre", SCHEMA), {"texte": "Bonjour."})
        self.assertIn("xiaomimimo.com/v1/chat/completions", appel.call_args[0][0].full_url)
        self.assertEqual(mj.derniere_utilisation, {"total_tokens": 12})

    def test_un_objet_code_en_texte_est_decode_seulement_hors_texte(self):
        schema = {"type": "object", "properties": {
            "texte": {"type": "string"},
            "proposition": {"anyOf": [{"type": "object", "properties": {"x": {"type": "integer"}}}, {"type": "null"}]}}}
        brut = {"texte": '{"reste": "un texte"}', "proposition": '{"x": 1}'}
        self.assertEqual(decoder_imbrique(brut, schema), {"texte": '{"reste": "un texte"}', "proposition": {"x": 1}})

    def test_une_reponse_tronquee_est_incomplete(self):
        self.assertEqual(depuis_chat({"choices": [{"finish_reason": "length", "message": {}}]})["status"],
                         "incomplete")


if __name__ == "__main__":
    unittest.main()
