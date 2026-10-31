"""A3 : grammaire liée sur le fil, refus avant préparation et reprise visible."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.fournisseurs.contrat import Demande
from donjon.fournisseurs.local import Local
from donjon.fournisseurs.openai import OpenAI
from donjon.fournisseurs.schema import verifier, restreint, union_seule
from donjon.mj import MJ, SCHEMA_PROPOSER
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import proposition
from donjon.operations import etape, sequence
from donjon.refus import RefusDeForme
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from tests import test_cache_kv_local as cache
from tests.test_comprehension import PontScript
from tests.test_expression_son import expression
from tests.test_schema_mutualise import developper
from tests.test_sous_obstacle import scene, passage
from tests.test_tensions import recharger


def exemple(s):
    """Témoin structurel, sans prétendre être exécutable dans un monde."""
    if 'anyOf' in s:
        return exemple(s['anyOf'][0])
    if 'enum' in s:
        return s['enum'][0]
    t = s['type']
    if t == 'object':
        return {k: exemple(s['properties'][k]) for k in s['required']}
    if t == 'array':
        return [exemple(s['items']) for _ in range(s.get('minItems', 0))]
    if t == 'string':
        return '1'  # convient aussi aux motifs de prix et de sujet non vide
    return {'integer': s.get('minimum', 0), 'number': s.get('minimum', 0),
            'boolean': False, 'null': None}[t]


def reponse(p):
    return {'mode': 'action', 'texte': '', 'faits': [], 'proposition': p}


def dimensions(s):
    """Limites publiées OpenAI, références développées pour la profondeur."""
    stats = dict(proprietes=0, enums=0, caracteres=0, profondeur=0)
    def visiter(v):
        if v.get('type') == 'object':
            assert v.get('additionalProperties') is False
            assert set(v['properties']) == set(v['required'])
        for k, p in v.get('properties', {}).items():
            stats['proprietes'] += 1
            stats['caracteres'] += len(k)
            visiter(p)
        for k, d in v.get('$defs', {}).items():
            stats['caracteres'] += len(k)
            visiter(d)
        for e in v.get('enum', []):
            stats['enums'] += 1
            stats['caracteres'] += len(e) if isinstance(e, str) else 0
        for p in v.get('anyOf', []):
            visiter(p)
        if 'items' in v:
            visiter(v['items'])
    def profondeur(v):
        if '$ref' in v:
            return profondeur(s['$defs'][v['$ref'].split('/')[-1]])
        enfants = [profondeur(p) for p in v.get('properties', {}).values()]
        enfants += [profondeur(p) for p in v.get('anyOf', [])]
        if 'items' in v:
            enfants += [profondeur(v['items'])]
        return (v.get('type') in ('object', 'array')) + max(enfants, default=0)
    visiter(s)
    stats['profondeur'] = profondeur(s)
    return stats


class LiaisonTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.entree, _, cls.schema = cache.PrefixeKVTests()._capter_appel(nouveau_monde(), 'Je regarde.')

    def demande(self, schema=None):
        return Demande('instructions', self.entree, 'Je regarde.', 'repondre_au_joueur',
                       schema or self.schema, 'gpt-6-luna')

    def test_prevol_forme_dimensions_et_equivalence_de_mutualisation(self):
        d = self.demande()
        avant = copy.deepcopy(d.schema)
        s = d.schema_transport()
        self.assertEqual(s['type'], 'object')
        self.assertNotIn('anyOf', s)
        self.assertEqual(developper(s)['properties']['reponse'], {'anyOf': d.schema['anyOf']})
        commun = {k: v for k, v in d.schema.items() if k != 'anyOf'}
        self.assertTrue(all(restreint(b, commun) for b in d.schema['anyOf']))
        stats = dimensions(s)
        for cle, maximum in (('proprietes', 5000), ('enums', 1000), ('caracteres', 120000), ('profondeur', 10)):
            self.assertLessEqual(stats[cle], maximum)
        self.assertEqual(d.schema, avant)

    def test_projection_ne_retire_jamais_une_contrainte_non_redondante(self):
        for champ, contrainte in (('texte', {'type': 'string', 'minLength': 2}),
                                   ('mode', {'type': 'string', 'enum': ['dialogue']})):
            s = copy.deepcopy(self.schema)
            s['properties'][champ] = contrainte
            with self.subTest(champ=champ), self.assertRaises(ValueError):
                self.demande(s).schema_transport()
        s = copy.deepcopy(self.schema)
        s['required'].append('autre_charge')
        with self.assertRaises(ValueError):
            self.demande(s).schema_transport()
        self.assertFalse(restreint({'type': 'integer'}, {'type': 'integer', 'maximum': 2}))
        self.assertFalse(restreint({'type': 'object'}, {'type': 'object', 'une_contrainte_inconnue': True}))
        self.assertFalse(restreint({'enum': [True]}, {'enum': [1]}))
        self.assertFalse(restreint({'type': 'object'},
                                  {'type': 'object', 'additionalProperties': {'type': 'integer'}}))

    def test_chaque_mode_refuse_toutes_les_charges_des_autres_modes(self):
        temoins = [exemple(s) for s in self.schema['anyOf']]
        projetee = union_seule(self.schema)
        for bon in temoins:
            verifier(bon, self.schema)
            verifier(bon, projetee)
            for autre in temoins:
                if bon['mode'] == autre['mode']:
                    continue
                with self.subTest(mode=bon['mode'], charge=autre['mode']):
                    with self.assertRaises(RefusDeForme) as refus:
                        verifier({**bon, 'proposition': autre['proposition']}, self.schema)
                    with self.assertRaises(RefusDeForme):
                        verifier({**bon, 'proposition': autre['proposition']}, projetee)
                    self.assertIn('proposition', refus.exception.attendu)
        for bon in temoins:
            if bon['mode'] != 'dialogue':
                with self.assertRaises(RefusDeForme):
                    verifier({**bon, 'texte': 'Un résultat déjà obtenu.'}, self.schema)

    def test_quatre_familles_et_suite_refusent_les_parametres_voisins(self):
        from tests.test_repli_et_appel import parole
        cas = [
            (proposition('attendre', '120'), 'outil', 'cle'),
            (sequence(etape('patienter')), 'destination', 'echoppe'),
            (sequence(etape('emettre_son', 'joueur', methode='cri')), 'outil', 'cle'),
            (sequence(etape('passer_obstacle', 'poutre', methode='dessous')), 'methode', 'simple'),
        ]
        for p, cle, faux in cas:
            invalide = copy.deepcopy(p)
            charge = invalide['etapes'][0] if 'etapes' in invalide else invalide
            charge[cle] = faux
            for candidat, valide in ((p, True), (invalide, False)):
                for avec_suite in (False, True):
                    r = reponse(candidat)
                    if avec_suite:
                        s = next(s for s in self.schema['anyOf'] if s['properties']['mode']['enum'] == ['etablir_faits'])
                        r = exemple(s)
                        r['proposition']['suite'] = candidat
                    with self.subTest(p=p, suite=avec_suite, valide=valide):
                        if valide:
                            verifier(r, self.schema)
                        else:
                            with self.assertRaises(RefusDeForme) as refus:
                                verifier(r, self.schema)
                            self.assertIn(cle, refus.exception.attendu)
        for acte in ('qui', 'localisation', 'ressource', 'reclamer'):
            bon = parole('Où ?', (acte, 'bois' if acte != 'qui' else '', '', ''), personnage='aubin')
            verifier(bon, self.schema)
            faux = copy.deepcopy(bon)
            faux['proposition']['contenu'][0].update(sujet='', attribut='bois')
            with self.assertRaises(RefusDeForme) as refus:
                verifier(faux, self.schema)
            self.assertIn('attribut', refus.exception.attendu)

    def test_cloud_et_local_emettent_le_meme_contrat_et_decodent_la_meme_charge(self):
        demandes = []
        bon = reponse(sequence(etape('patienter')))
        d = self.demande()
        def http(requete, **options):
            p = json.loads(requete.data)
            demandes.append(p)
            enveloppe = {'reponse': bon}
            if 'tools' in p:
                resultat = {'status': 'completed', 'output': [{'type': 'function_call',
                    'name': d.fonction, 'arguments': json.dumps(enveloppe)}]}
            else:
                resultat = {'choices': [{'message': {'content': json.dumps(enveloppe)}, 'finish_reason': 'stop'}]}
            return io.BytesIO(json.dumps(resultat).encode())
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'simulation'}), patch('urllib.request.urlopen', side_effect=http):
            for f in (OpenAI(), Local()):
                self.assertEqual(f.appeler(d).arguments, bon)
        cloud, local = demandes
        self.assertEqual(cloud['tools'][0]['parameters'], local['response_format']['json_schema']['schema'])
        self.assertEqual(cloud['instructions'], local['messages'][0]['content'])
        self.assertEqual(cloud['input'][0]['content'], local['messages'][1]['content'])

    def test_ancienne_api_utilise_aussi_les_contrats_attente_et_passage(self):
        dimensions(self.demande(SCHEMA_PROPOSER).schema_transport())
        for p in (proposition('attendre', '120'), proposition('franchir', 'echelle'), proposition('pousser', 'aubin')):
            verifier(p, SCHEMA_PROPOSER)
            with self.assertRaises(RefusDeForme):
                verifier({**p, 'methode': 'finesse'}, SCHEMA_PROPOSER)

    def test_union_sans_discriminant_reste_valide_et_mots_cles_inconnus_ne_sont_pas_ignores(self):
        schema = {'anyOf': [
            {'type': 'object', 'properties': {'type': {'enum': ['a']}, 'n': {'type': 'integer'}},
             'required': ['type', 'n']},
            {'type': 'object'}]}
        verifier({'type': 'a', 'n': 'texte'}, schema)
        with self.assertRaises(ValueError):
            verifier('texte', {'type': 'string', 'format_inconnu': True})

    def test_refus_de_grammaire_avant_preparation_dans_la_console_et_apres_recharge(self):
        from donjon.auberge import nouveau_auberge
        from donjon.defi import nouveau_defi
        from tests.test_repli_et_appel import jouer
        for creer in (nouveau_defi, nouveau_auberge):
            m = creer(depart='fixe')
            bon = reponse(proposition('observer'))
            faux = reponse(sequence(etape('patienter', outil='cle')))
            r, texte, appels = jouer(m, 'mj Je contemple les environs.', [faux, bon], [])
            corrections = [e['retour_forme'] for f, e in appels if 'retour_forme' in e]
            self.assertEqual(len(corrections), 1)
            self.assertIn('outil', corrections[0]['attendu'])
            self.assertIn('cle', corrections[0]['attendu'])
            temoin, rendu, _ = jouer(m, 'mj Je contemple les environs.', [bon], [])
            self.assertEqual(r.data, temoin.data)
            self.assertEqual(texte, rendu)
            self.assertEqual(regarder(r), regarder(recharger(r)))

    def test_passage_reel_autre_support_et_sons_sur_les_deux_transports(self):
        for connexion in ('api', 'local'):
            for scenario, cible in (('relais', 'poutre_conduite'), ('auberge', 'table_longue')):
                m = scene(scenario, cible)
                for sonore in (False, True):
                    p = expression('voix_melodique' if scenario == 'relais' else 'corps_rythmique') if sonore else passage(cible)
                    mots = ('je fredonne doucement' if scenario == 'relais' else 'je frappe un rythme avec mes mains') if sonore else f'je voudrais passer sous {cible}'
                    self.parcours(connexion, m, mots, p, sonore)

    def parcours(self, connexion, m, mots, p, sonore):
        # Les vrais adaptateurs, le MJ, la revue et la boucle console/PontWeb.
        requetes = []
        def http(requete, **options):
            q = json.loads(requete.data)
            cloud = 'tools' in q
            outil = q['tools'][0] if cloud else q['response_format']['json_schema']
            fonction = outil['name']
            requetes.append(fonction)
            if fonction == 'auditer_action':
                a = {'conforme': True, 'motif': ''}
            else:
                self.assertEqual(fonction, 'repondre_au_joueur')
                a = {'reponse': reponse(p)}
            resultat = ({'status': 'completed', 'output': [{'type': 'function_call', 'name': fonction, 'arguments': json.dumps(a)}]}
                        if cloud else {'choices': [{'message': {'content': json.dumps(a)}, 'finish_reason': 'stop'}]})
            return io.BytesIO(json.dumps(resultat).encode())
        with self.subTest(connexion=connexion, mots=mots), tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / 'partie.json'
            m.sauver(chemin)
            pont = PontScript(['mj ' + mots, 'tenter', 'quitter'], chemin)
            with patch.dict('os.environ', {'OPENAI_API_KEY': 'simulation'}), patch('urllib.request.urlopen', side_effect=http), patch('sys.stdout', io.StringIO()):
                self.assertEqual(jeu.main(['--console', '--connexion', connexion, '--save', str(chemin)], interface=pont), 0)
            r = Monde.charger(chemin)
            self.assertEqual(r.data, json.loads(json.dumps(pont.vu)))
            self.assertIn('repondre_au_joueur', requetes)
            self.assertIn('Compris :', r.data['conversation'][-1]['compris'])
            if sonore:
                self.assertTrue(r.data['sons'])
            else:
                self.assertEqual(r.joueur['position'][0], m.joueur['position'][0] + 2)
            reprise = PontScript(['quitter'], chemin)
            with patch('sys.stdout', io.StringIO()):
                jeu.main(['--console', '--offline', '--save', str(chemin)], interface=reprise)
            self.assertIn(r.data['conversation'][-1]['reponse'], '\n'.join(reprise.historique))
            self.assertEqual(Monde.charger(chemin).data, r.data)
            vivant = recharger(r)
            self.assertEqual((regarder(r), fiche(r), scene_percue(r)),
                             (regarder(vivant), fiche(vivant), scene_percue(vivant)))


if __name__ == '__main__':
    unittest.main()
