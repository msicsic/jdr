"""Essai de Claude Haiku : la traduction vers l'API Messages garde le contrat du MJ."""
import json
import unittest
from unittest.mock import patch

from donjon.mj import MJOpenAI, decoder_imbrique, depuis_messages, schema_anthropic, vers_messages


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
    @staticmethod
    def payload(effort):
        return {"model": "claude-haiku-5-5", "instructions": "Règles.",
                "input": [{"role": "user", "content": "{}"}],
                "tools": [{"type": "function", "name": "repondre", "description": "d",
                           "parameters": SCHEMA, "strict": True}],
                "reasoning": {"effort": effort}, "max_output_tokens": 3000}

    def test_sans_reflexion_l_outil_est_impose_unique_et_strict(self):
        requete = vers_messages(self.payload("low"))
        self.assertEqual(requete["system"], "Règles.")
        self.assertEqual(requete["tools"][0]["input_schema"], SCHEMA)
        self.assertTrue(requete["tools"][0]["strict"])
        self.assertEqual(requete["tool_choice"], {"type": "tool", "name": "repondre", "disable_parallel_tool_use": True})
        self.assertNotIn("thinking", requete)

    def test_avec_reflexion_l_outil_reste_unique_mais_libre(self):
        requete = vers_messages(self.payload("medium"))
        self.assertEqual(requete["thinking"], {"type": "adaptive"})
        self.assertEqual(requete["output_config"], {"effort": "medium"})
        self.assertEqual(requete["tool_choice"], {"type": "auto", "disable_parallel_tool_use": True})
        self.assertEqual(requete["max_tokens"], 2048 + 3000)
        self.assertTrue(requete["tools"][0]["strict"])

    def test_un_appel_unique_est_rendu_au_controle(self):
        brut = {"stop_reason": "tool_use", "usage": {"input_tokens": 10, "output_tokens": 5},
                "content": [{"type": "tool_use", "name": "repondre", "input": {"texte": "Bonjour."}}]}
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "cle-de-test"}), \
                patch("urllib.request.urlopen", return_value=ReponseFactice(brut)) as appel:
            mj = MJOpenAI("claude-haiku-5-5", connexion="anthropic")
            self.assertEqual(mj._appeler_brut("Règles.", {}, "bonjour", "repondre", SCHEMA), {"texte": "Bonjour."})
        requete = appel.call_args[0][0]
        self.assertEqual(requete.full_url, "https://api.anthropic.com/v1/messages")
        self.assertEqual(requete.get_header("X-api-key"), "cle-de-test")
        self.assertIsNone(requete.get_header("Authorization"))
        self.assertEqual(mj.derniere_utilisation["total_tokens"], 15)

    def test_les_bornes_non_prises_en_charge_passent_dans_la_description(self):
        schema = {"type": "object", "properties": {
            "liste": {"type": "array", "maxItems": 3, "minItems": 1, "items": {"type": "integer", "minimum": 0}},
            "nom": {"type": "string", "description": "Nom.", "maxLength": 40}}}
        traduit = schema_anthropic(schema)
        liste = traduit["properties"]["liste"]
        self.assertNotIn("maxItems", liste)
        self.assertEqual(liste["minItems"], 1)
        self.assertEqual(liste["description"], "Contraintes : maxItems 3.")
        self.assertEqual(liste["items"], {"type": "integer", "description": "Contraintes : minimum 0."})
        self.assertEqual(traduit["properties"]["nom"]["description"], "Nom. Contraintes : maxLength 40.")
        self.assertEqual(schema["properties"]["liste"]["maxItems"], 3)

    def test_hors_mode_strict_un_objet_code_en_texte_est_decode_seulement_hors_texte(self):
        schema = {"type": "object", "properties": {
            "texte": {"type": "string"},
            "proposition": {"anyOf": [{"type": "object", "properties": {"x": {"type": "integer"}}}, {"type": "null"}]}}}
        brut = {"texte": '{"reste": "un texte"}', "proposition": '{"x": 1}'}
        self.assertEqual(decoder_imbrique(brut, schema), {"texte": '{"reste": "un texte"}', "proposition": {"x": 1}})

    def test_une_reponse_tronquee_ou_sans_outil_est_refusee(self):
        self.assertEqual(depuis_messages({"stop_reason": "max_tokens", "content": []})["status"], "incomplete")
        texte = depuis_messages({"stop_reason": "end_turn", "content": [{"type": "text", "text": "Bonjour."}]})
        self.assertEqual(texte["output"], [])


if __name__ == "__main__":
    unittest.main()
