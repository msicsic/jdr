"""G1 : contrat actuel invariant et aucune normalisation sémantique du prototype."""
import copy
import json
import unittest

from donjon.compilateur import (SCHEMA_COMPILATEUR, normaliser_proposition,
                               prompt_compilateur, schema_compilateur)
from donjon.paroles import SCHEMA_PAROLE, SENS_CONTENU, TYPES_JOUEUR, section_contenu
from donjon.sources import voie_cache, slot_cache


def parole_compilee():
    return next(v for v in SCHEMA_COMPILATEUR['properties']['proposition']['anyOf']
                if 'replique' in v.get('properties', {}))


class SchemaCompilateurTests(unittest.TestCase):
    def test_variantes_actuelles_conservees_sans_modifier_le_contrat(self):
        contenu = parole_compilee()['properties']['contenu']
        self.assertEqual(contenu, SCHEMA_PAROLE['properties']['contenu'])
        self.assertEqual({v['properties']['type']['enum'][0] for v in contenu['items']['anyOf']},
                         set(TYPES_JOUEUR))
        self.assertEqual(SCHEMA_COMPILATEUR, schema_compilateur())

    def test_contraintes_par_type_conservees(self):
        variantes = parole_compilee()['properties']['contenu']['items']['anyOf']
        par_type = {v['properties']['type']['enum'][0]: v['properties'] for v in variantes}
        self.assertEqual(par_type['avis']['attribut']['enum'], ['menace'])
        self.assertEqual(par_type['avis']['valeur']['enum'], ['oui', 'non'])
        for champ in ('sujet', 'attribut', 'valeur'):
            self.assertEqual(par_type['propos'][champ]['enum'], [''])

    def test_grammaire_refuse_un_avis_mal_type(self):
        contenu = parole_compilee()['properties']['contenu']
        branches = [v for v in contenu['items']['anyOf']
                    if 'avis' in v['properties']['type']['enum']]
        self.assertEqual(len(branches), 1)
        self.assertIn('menace', branches[0]['properties']['attribut']['enum'])
        self.assertNotIn('lieu', branches[0]['properties']['attribut']['enum'])

    def test_prompt_local_derive_des_douze_definitions_joueur(self):
        for t in TYPES_JOUEUR:
            self.assertIn(SENS_CONTENU[t], section_contenu())
        self.assertNotIn('compte_rendu', section_contenu())
        local = type('Local', (), {'schema_lu': False})()
        self.assertIn(section_contenu(), prompt_compilateur(local))

    def test_normaliser_ne_change_ni_cible_ni_termes_ni_methode(self):
        for p in ({'action': 'frapper', 'cible': 'inconnu', 'outil': 'lame', 'methode': 'assommer'},
                  {'action': 'conversation_pnj', 'operation': 'proposer', 'montant_demande': 9},
                  {'action': 'assembler', 'pieces': {}},
                  {'action': 'dialogue', 'contenu': [{'type': 'propos'}]}):
            avant = copy.deepcopy(p)
            r = normaliser_proposition(p)
            self.assertEqual(r, avant)
            self.assertIsNot(r, p)
            self.assertEqual(p, avant)

    def test_cache_compilateur_distinct_du_recit(self):
        self.assertEqual(voie_cache('repondre_au_joueur', {'compilation': True}), 'compiler_intention')
        self.assertEqual(slot_cache('compiler_intention'), 0)


if __name__ == '__main__':
    unittest.main()
