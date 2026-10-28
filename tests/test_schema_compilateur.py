"""Le schéma du compilateur dit le sens générique de ``sujet`` une seule fois.

Le contrat par type reste porté par les variantes (``enum`` d'attribut et de
valeur, champs vides) ; seule la description commune cesse d'être recopiée
dans chaque branche. Le schéma de ``parole_joueur`` garde la sienne.
"""
import unittest

import jsonschema

from donjon.compilateur import PROMPT_COMPILATEUR, SCHEMA_COMPILATEUR
from donjon.paroles import SCHEMA_PAROLE


def variantes(schema):
    return schema["properties"]["contenu"]["items"]["anyOf"]


class SchemaCompilateurTests(unittest.TestCase):
    def test_sens_de_sujet_dit_une_fois_dans_le_prompt(self):
        self.assertIn("même inconnu de Corvus", PROMPT_COMPILATEUR)
        self.assertIn("faim = de quoi manger", PROMPT_COMPILATEUR)
        for variante in variantes(SCHEMA_COMPILATEUR):
            sujet = variante.get("properties", {}).get("sujet", {})
            self.assertNotIn("description", sujet)

    def test_contraintes_par_type_conservees(self):
        par_type = {v["properties"]["type"]["enum"][0]: v["properties"]
                    for v in variantes(SCHEMA_COMPILATEUR)}
        self.assertEqual(par_type["avis"]["attribut"]["enum"], ["menace"])
        self.assertEqual(par_type["avis"]["valeur"]["enum"], ["oui", "non"])
        for champ in ("sujet", "attribut", "valeur"):
            self.assertEqual(par_type["propos"][champ]["enum"], [""])

    def test_grammaire_refuse_un_avis_mal_type(self):
        schema_contenu = SCHEMA_COMPILATEUR["properties"]["contenu"]
        avis = {"type": "avis", "sujet": "salle", "attribut": "menace", "valeur": "oui"}
        jsonschema.validate([avis], schema_contenu)
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate([{**avis, "attribut": "lieu"}], schema_contenu)

    def test_le_schema_de_parole_garde_la_description_pour_le_dialogue(self):
        descriptions = [
            v.get("properties", {}).get("sujet", {}).get("description")
            for v in SCHEMA_PAROLE["properties"]["contenu"]["items"]["anyOf"]
        ]
        self.assertTrue(any(d and "même inconnu de Corvus" in d for d in descriptions))


if __name__ == "__main__":
    unittest.main()
