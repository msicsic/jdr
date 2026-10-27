"""Le moteur valide les valeurs variables, sans varier le contrat réseau."""
import copy
import json
import unittest

from donjon.narration import AuditIllisible, controler, schema_audit


class AuditInvariantTests(unittest.TestCase):
    def test_schema_identique_et_independant_des_copies(self):
        reference = json.dumps(schema_audit({}, 0), ensure_ascii=False)
        for faits in ({'salle': {}}, {'comptes': {}, 'perception': {}, 'echanges_passes': {}}):
            for indices in (1, 24, ['1', '7'], []):
                self.assertEqual(json.dumps(schema_audit(faits, indices), ensure_ascii=False), reference)
        schema = schema_audit({}, 1)
        schema['properties'].clear()
        self.assertEqual(json.dumps(schema_audit({}, 2), ensure_ascii=False), reference)

    def test_indices_invalides_et_sources_inconnues_meme_resultat(self):
        ligne = {'nature': 'mecanique', 'portee_mecanique': 'etablie',
                 'sources': ['inconnue'], 'rappels': [], 'comptes': [], 'eclairages': []}
        texte = 'La porte est fermée.'
        avant = copy.deepcopy(ligne)
        ancien = controler(texte, {'segments': {'0': ligne}}, {'salle': {}})
        nouveau = controler(texte, {'segments': [dict(ligne, indice=0)]}, {'salle': {}})
        self.assertEqual(nouveau, ancien)
        self.assertTrue(nouveau['obstacles'])
        self.assertIn('attendu', nouveau['obstacles'][0])
        self.assertEqual(ligne, avant)
        for indices in ([1], [-1], [24], [True], ['0'], [0, 0], [], [1, 0]):
            with self.subTest(indices=indices), self.assertRaises(AuditIllisible):
                controler(texte, {'segments': [dict(ligne, indice=i) for i in indices]}, {})
        contradiction = dict(ligne, portee_mecanique='contradictoire')
        for rapport in ({'0': contradiction}, [dict(contradiction, indice=0)]):
            with self.assertRaises(AuditIllisible):
                controler(texte, {'segments': rapport}, {})

    def test_refus_indices_sources_console_et_recharge_sur_deux_scenes(self):
        from tests.test_audits_attendu import jouer
        from tests.test_repli_et_appel import dialogue
        from tests.test_verdict_coherent import crypte, noir
        from tests.test_tensions import recharger
        from donjon.rendu import regarder
        for creer in (crypte, noir):
            for defaut in ('indice', 'source'):
                resultats = []
                for forme in ('cles', 'liste'):
                    m = recharger(creer())
                    avant = copy.deepcopy(m.data)
                    faux = 'Une tour apparaît devant toi.'
                    bon = 'Tu peux regarder autour de toi.'
                    ligne = {'nature': 'mecanique', 'portee_mecanique': 'etablie',
                             'sources': ['inconnue'], 'comptes': [], 'rappels': [], 'eclairages': []}
                    i = 1 if defaut == 'indice' else 0
                    invalide = {'segments': {str(i): ligne} if forme == 'cles' else [dict(ligne, indice=i)]}
                    valide = {'segments': [{'indice': 0, 'nature': 'neutre',
                        'portee_mecanique': 'aucune', 'sources': [], 'comptes': [],
                        'rappels': [], 'eclairages': []}]}
                    audits = [invalide] * (2 if defaut == 'indice' else 1) + [valide]
                    r, sortie, appels = jouer(m, 'mj Que vois-je ?',
                        [dialogue(faux), dialogue(bon)], audits)
                    reprise = recharger(r)
                    self.assertNotIn(faux, sortie)
                    self.assertIn(bon, sortie)
                    self.assertEqual(reprise.objets, avant['objets'])
                    self.assertEqual(regarder(reprise), regarder(m))
                    self.assertNotIn(faux, str(reprise.data.get('narrations_mj')))
                    resultats.append((reprise.data, sortie, appels))
                self.assertEqual(resultats[0], resultats[1])
