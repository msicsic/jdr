"""Même contrat sur le fil OpenAI, refus et recharge de la vraie console."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.fournisseurs.schema import mutualiser
from donjon.monde import Monde
from donjon.narration import schema_audit
from donjon.rendu import regarder
from tests.test_audits_attendu import ligne, rapport
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger
from tests.test_verdict_coherent import crypte, noir, jugement


def developper(schema):
    definitions = schema.get('$defs', {})
    def suivre(v):
        if isinstance(v, dict):
            if set(v) == {'$ref'}:
                return suivre(definitions[v['$ref'].removeprefix('#/$defs/')])
            return {k: suivre(x) for k, x in v.items() if k != '$defs'}
        return [suivre(x) for x in v] if isinstance(v, list) else v
    return suivre(schema)


class SchemaMutualiseTests(unittest.TestCase):
    def test_contrat_exact_pour_chaque_nombre_de_segments_et_dossier(self):
        for faits in ({'salle': {}}, {'salle': {}, 'comptes': {}, 'perception': {}}):
            for nombre in (1, 2, 4, 12):
                with self.subTest(nombre=nombre, faits=list(faits)):
                    schema = schema_audit(faits, nombre)
                    avant = copy.deepcopy(schema)
                    compact = mutualiser(schema)
                    self.assertEqual(developper(compact), schema)
                    self.assertEqual(schema, avant)
                    self.assertLessEqual(len(json.dumps(compact)), len(json.dumps(schema)))
                    if nombre > 1:
                        self.assertIn('$defs', compact)

    def test_valeurs_litterales_et_references_existantes_conservees(self):
        valeur = {'type': 'object', 'properties': {'nom': {'type': 'string', 'description': 'x' * 600}}}
        schema = {'type': 'object', 'properties': {'a': valeur, 'b': valeur},
                  'enum': [valeur], 'default': valeur}
        compact = mutualiser(schema)
        self.assertEqual(compact['enum'], [valeur])
        self.assertEqual(compact['default'], valeur)
        self.assertEqual(developper(compact), schema)
        for cle in ('$ref', '$id', '$defs', '$anchor', '$dynamicRef'):
            avec_reference = {**schema, cle: 'identite'}
            self.assertIs(mutualiser(avec_reference), avec_reference)

    def test_console_refus_revision_et_recharge_conservent_le_contrat(self):
        for m, faux, saisie, portee in (
                (noir(), "Elle n'est pas là pour que tu le lui demandes.",
                 'Ilse a-t-elle peur de Brune ?', 'sans_fondement'),
                (crypte(), 'Gorm est face à toi.', 'Gorm me fait-il face ?', 'contradictoire')):
            with self.subTest(portee=portee), tempfile.TemporaryDirectory() as tmp:
                m = recharger(m)
                avant = copy.deepcopy(m.objets)
                bon = 'Tu peux regarder autour de toi.'
                reponses = [dialogue(faux), dialogue(bon)]
                audits = [jugement('mecanique', portee),
                          jugement('contradictoire' if portee == 'contradictoire' else 'invention_protegee', portee),
                          rapport(ligne('neutre'))]
                appels, schemas = [], []

                def urlopen(requete, **options):
                    outil = json.loads(requete.data)['tools'][0]
                    fonction = outil['name']
                    appels.append(fonction)
                    schemas.append(outil['parameters'])
                    arguments = (audits if fonction == 'auditer_narration' else reponses).pop(0)
                    resultat = {'status': 'completed', 'output': [{'type': 'function_call',
                        'name': fonction, 'arguments': json.dumps(arguments)}]}
                    return io.BytesIO(json.dumps(resultat).encode())

                chemin = Path(tmp) / 'partie.json'
                m.sauver(chemin)
                with (patch.dict('os.environ', {'OPENAI_API_KEY': 'simulation'}),
                      patch('urllib.request.urlopen', side_effect=urlopen),
                      patch('builtins.input', side_effect=[saisie, 'quitter']),
                      patch('sys.stdout', io.StringIO()) as sortie):
                    self.assertEqual(jeu.main(['--console', '--connexion', 'api', '--save', str(chemin)]), 0)
                recharge = Monde.charger(chemin)
                self.assertEqual(appels, ['repondre_au_joueur', 'auditer_narration',
                                         'auditer_narration', 'repondre_au_joueur', 'auditer_narration'])
                self.assertTrue(any('$defs' in s for s in schemas))
                self.assertNotIn(faux, sortie.getvalue())
                self.assertNotIn(faux, str(recharge.data.get('narrations_mj')))
                self.assertIn(bon, sortie.getvalue())
                self.assertIn(bon, str(recharge.data['narrations_mj']))
                self.assertEqual(recharge.objets, avant)
                self.assertEqual(regarder(recharge), regarder(m))


if __name__ == '__main__':
    unittest.main()
