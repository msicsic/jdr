"""Le contrat des actes n'est répété dans le prompt que si le modèle ne lit pas le schéma.

OpenAI, Anthropic et MiMo reçoivent les descriptions du schéma ; Ollama et
llama.cpp ne reçoivent qu'une grammaire. Le prompt suit cette capacité, et
l'appel réel du compilateur porte bien la variante choisie.
"""
import unittest

from donjon.compilateur import (PROMPT_COMPILATEUR, PROMPT_COMPILATEUR_SCHEMA,
                                RENVOI_SCHEMA, compiler, prompt_compilateur)
from donjon.fournisseurs.anthropic import Anthropic
from donjon.fournisseurs.contrat import Fournisseur
from donjon.fournisseurs.local import Local
from donjon.fournisseurs.mimo import MiMo
from donjon.fournisseurs.openai import OpenAI
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.paroles import section_contenu


class Espion:
    def __init__(self, schema_lu):
        self.schema_lu = schema_lu
        self.instructions = None

    def appeler(self, demande):
        self.instructions = demande.instructions
        raise ErreurMonde("fin du test")


class PromptTransportTests(unittest.TestCase):
    def test_capacite_declaree_par_fournisseur(self):
        self.assertIs(Fournisseur.schema_lu, True)
        self.assertIs(OpenAI.schema_lu, True)
        self.assertIs(Anthropic.schema_lu, True)
        self.assertIs(MiMo.schema_lu, True)
        self.assertIs(Local.schema_lu, False)

    def test_le_prompt_suit_la_capacite(self):
        self.assertIs(prompt_compilateur(Espion(True)), PROMPT_COMPILATEUR_SCHEMA)
        self.assertIs(prompt_compilateur(Espion(False)), PROMPT_COMPILATEUR)

    def test_la_seule_difference_est_la_section(self):
        self.assertEqual(PROMPT_COMPILATEUR.replace(section_contenu(), RENVOI_SCHEMA),
                         PROMPT_COMPILATEUR_SCHEMA)

    def test_le_prompt_cloud_ne_redit_pas_les_exemples(self):
        self.assertNotIn('-> contenu = [{"', PROMPT_COMPILATEUR_SCHEMA)
        self.assertIn("schéma de contenu", PROMPT_COMPILATEUR_SCHEMA)
        self.assertEqual(PROMPT_COMPILATEUR.count('-> contenu = [{"'), 12)

    def test_l_appel_du_compilateur_porte_la_variante(self):
        for schema_lu, attendu in ((True, PROMPT_COMPILATEUR_SCHEMA),
                                   (False, PROMPT_COMPILATEUR)):
            espion = Espion(schema_lu)
            with self.assertRaises(ErreurMonde):
                compiler(espion, nouveau_monde(), "je regarde autour de moi")
            self.assertIs(espion.instructions, attendu)


if __name__ == "__main__":
    unittest.main()
