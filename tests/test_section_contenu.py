"""La section des actes de parole du compilateur est rendue depuis la table de paroles.

Le sens vient de ``SENS_CONTENU``, la forme de ``EXEMPLE_CONTENU`` : le prompt
ne peut plus dire autre chose que le schéma, et chaque exemple rendu est un
contenu que la grammaire accepte.
"""
import unittest

import jsonschema

from donjon.compilateur import PROMPT_COMPILATEUR, SCHEMA_COMPILATEUR
from donjon.paroles import (BESOINS_DEMANDES, CHAMPS_CONTENU, EXEMPLE_CONTENU,
                            RESSOURCES_DEMANDEES, SENS_CONTENU, TYPES, section_contenu)


class SectionContenuTests(unittest.TestCase):
    def test_chaque_type_a_sens_exemple_et_champs(self):
        for table in (SENS_CONTENU, CHAMPS_CONTENU, EXEMPLE_CONTENU):
            self.assertEqual(set(table), set(TYPES))

    def test_chaque_exemple_est_un_contenu_valide(self):
        schema = SCHEMA_COMPILATEUR["properties"]["contenu"]
        for type_contenu in TYPES:
            exemple = EXEMPLE_CONTENU[type_contenu]
            self.assertEqual(exemple["type"], type_contenu)
            jsonschema.validate([exemple], schema)

    def test_la_section_cite_chaque_type_une_fois(self):
        section = section_contenu()
        for type_contenu in TYPES:
            self.assertEqual(section.count(f'- "{type_contenu}" :'), 1)

    def test_le_prompt_contient_la_section_generee(self):
        self.assertIn(section_contenu(), PROMPT_COMPILATEUR)

    def test_les_besoins_generaux_sont_nommes(self):
        for besoin in BESOINS_DEMANDES:
            self.assertIn(f"{besoin} = {RESSOURCES_DEMANDEES[besoin]}", section_contenu())

    def test_l_aveu_liste_les_gestes(self):
        for geste in ("prendre", "crocheter", "eteindre"):
            self.assertIn(geste, SENS_CONTENU["aveu"])


if __name__ == "__main__":
    unittest.main()
