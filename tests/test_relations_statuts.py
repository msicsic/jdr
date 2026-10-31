"""254 : statut déclaré, croyance et parole restent distincts."""
import ast
import copy
import unittest
from pathlib import Path

from donjon import esprits, relations, social
from donjon.monde import Monde, ErreurMonde
from donjon.rendu import regarder
from donjon.voix import source_dite
from unittest.mock import patch
from tests.scenarios_contractuels import donnees
from tests.test_social import recharger, placer


class StatutsTests(unittest.TestCase):
    def scene(self, scenario='relais'):
        d = donnees(scenario)
        # Données d'auteur avant toute installation des esprits.
        personnages = [x for x, o in d['objets'].items() if o.get('profil')]
        a, b, c = (['marchand', 'brune', 'ilse'] if scenario == 'relais' else personnages[:3])
        lieu, ailleurs = list(d['salles'])[:2]
        titre = 'responsable' if scenario == 'relais' else 'employeur'
        valeur = {'titre': titre, 'lieux': [lieu], 'domaines': ['travail']}
        d['objets'][a]['profil']['statuts'] = [{**valeur, 'connus': [b]}]
        return Monde(d), a, b, c, lieu, ailleurs, valeur

    def persiste(self, m):
        from donjon.emissions import lire as paroles
        from donjon.scene import scene_percue
        m.verifier()
        avant = copy.deepcopy(m.data)
        public = regarder(m), scene_percue(m), copy.deepcopy(paroles(m))
        charge = recharger(m)
        self.assertEqual(charge.data, avant)
        self.assertEqual((regarder(charge), scene_percue(charge), paroles(charge)), public)
        return charge

    def test_savoir_declare_ignore_portee_et_recharge_deux_scenarios(self):
        for scenario in ('relais', 'mine'):
            with self.subTest(scenario=scenario):
                m, a, b, c, lieu, ailleurs, v = self.scene(scenario)
                avant = copy.deepcopy(m.data)
                lu = relations.statuts_reconnus(m, b, a, lieu, 'travail')
                self.assertEqual(lu['source'], 'savoir')
                self.assertEqual(lu['valeur'], [v])
                self.assertIsNone(relations.statuts_reconnus(m, c, a, lieu, 'travail'))
                self.assertIsNone(relations.statuts_reconnus(m, b, a, ailleurs, 'travail'))
                self.assertIsNone(relations.statuts_reconnus(m, b, a, lieu, 'combat'))
                lu['valeur'][0]['lieux'].clear()
                self.assertEqual(m.data, avant)
                self.persiste(m)

    def dire(self, m, locuteur, auditeur, sujet, valeurs):
        # Véritable émission : propagation, ouïe, mémoire puis croyance.
        social.faire_entendre(m, locuteur, auditeur,
                             '« Je vous parle de son statut. »', [sujet], [],
                             [{'type': 'affirmation', 'sujet': sujet,
                               'attribut': 'statuts', 'valeur': valeurs}], suites=False)
        # Comme se_parler : l'appelant traite le destinataire ; l'émission
        # commune traite les témoins et vérifie ce qui atteint leurs oreilles.
        from donjon.ouie import saisit
        if saisit(m, auditeur, locuteur, 'dire'):
            social.recevoir(m, auditeur, locuteur, {'type': 'affirmation', 'sujet': sujet,
                                                 'attribut': 'statuts', 'valeur': valeurs})

    def test_parole_propre_tiers_fausse_pretention_et_dementi(self):
        for scenario in ('relais', 'mine'):
            with self.subTest(scenario=scenario):
                m, a, b, c, lieu, ailleurs, v = self.scene(scenario)
                for x, case in ((a, [2, 2]), (b, [3, 2]), (c, [2, 3] if scenario == 'relais' else [4, 2])):
                    placer(m, x, lieu, case)
                from donjon.spatial import installer
                installer(m)
                # La même source inconnue peut ensuite retirer sa prétention.
                for e in m.data['esprits'].values():
                    e['voix'] = []
                faux = {**v, 'titre': 'capitaine'}
                self.dire(m, a, c, a, [faux])
                cru = esprits.croyance(m, c, a, 'statuts')
                self.assertIsNotNone(cru)
                self.assertEqual(cru['source'], source_dite(m, c, a))
                self.assertNotEqual(cru['source'], 'savoir')
                self.assertEqual(cru['confiance'], .7)
                self.assertEqual(esprits.poids_source(m, c, cru),
                                 esprits.poids_source(m, c, {'source': source_dite(m, c, a)}))
                self.assertEqual(m.objets[a]['profil']['statuts'][0]['titre'], v['titre'])
                m = self.persiste(m)
                self.dire(m, a, c, a, [])
                self.assertIsNone(relations.statuts_reconnus(m, c, a, lieu, 'travail'))
                self.dire(m, b, c, a, [v])
                self.assertEqual(esprits.croyance(m, c, a, 'statuts')['source'], source_dite(m, c, b))
                # Son savoir initial résiste à la prétention mensongère.
                self.assertEqual(esprits.croyance(m, b, a, 'statuts')['source'], 'savoir')
                self.assertEqual(esprits.croyance(m, b, a, 'statuts')['valeur'], [v])
                self.persiste(m)

    def test_validation_et_rumeur_datee(self):
        m, a, b, c, lieu, ailleurs, v = self.scene()
        for valeurs in ([{**v, 'lieux': []}], [{**v, 'lieux': ['absent']}], [{**v, 'domaines': []}], [dict(v, bonus=10)]):
            with self.assertRaises(AssertionError):
                esprits.verifier_statuts(m, valeurs)
        social.recevoir_statuts(m, c, a, a, [v], minute=10)
        social._adopter(m, c, b, {'type': 'constat', 'objet': a, 'attribut': 'statuts',
                                 'valeur': [], 'observe': 9}, 1)
        self.assertEqual(esprits.croyance(m, c, a, 'statuts')['valeur'], [v])
        m.objets[a]['profil']['statuts'][0]['connus'] = ['absent']
        with self.assertRaises(ErreurMonde):
            m.verifier()

    def test_voix_inconnue_sans_privilege_et_rectification_persistante(self):
        m, a, b, c, lieu, ailleurs, v = self.scene()
        # L'identification est la frontière du contrat voix ; aucun titre ne
        # peut rehausser le poids que cette frontière fournit.
        with patch('donjon.voix.identifie', return_value=False):
            social.recevoir(m, c, a, {'type': 'affirmation', 'sujet': a,
                                    'attribut': 'statuts', 'valeur': [dict(v, titre='roi')]})
            cru = esprits.croyance(m, c, a, 'statuts')
            self.assertEqual(cru['source'], 'dit:voix:' + a)
            self.assertAlmostEqual(esprits.poids_source(m, c, cru), .28)
            social.recevoir(m, c, a, {'type': 'affirmation', 'sujet': a,
                                    'attribut': 'statuts', 'valeur': []})
        m = self.persiste(m)
        self.assertEqual(esprits.croyance(m, c, a, 'statuts')['valeur'], [])
        self.assertIsNone(relations.statuts_reconnus(m, c, a, lieu, 'travail'))

    def test_nouvelle_commune_et_temoins_hors_ouie(self):
        m, a, b, c, lieu, ailleurs, v = self.scene()
        # Un tiers transmet par la nouvelle commune, avec atténuation du rang.
        with patch.object(Monde, 'd20', return_value=20):
            social.recevoir(m, c, b, {'type': 'rumeur', 'rang': 0, 'evenement': {
                'type': 'constat', 'objet': a, 'attribut': 'statuts', 'valeur': [v], 'observe': 0}})
        self.assertEqual(esprits.croyance(m, c, a, 'statuts')['source'], source_dite(m, c, b))
        self.persiste(m)
        # L'émission commune ne transmet rien à quelqu'un qui n'entend pas.
        esprits.lire(m, c)['croyances'].get(a, {}).pop('statuts', None)
        m.objets[c]['entend'] = False
        self.dire(m, a, b, a, [v])
        self.assertIsNone(esprits.croyance(m, c, a, 'statuts'))
        self.persiste(m)

    def test_ast_aucun_consommateur_de_decision(self):
        racine = Path(__file__).resolve().parents[1]
        fautes = []
        for p in (racine / 'donjon').rglob('*.py'):
            arbre = ast.parse(p.read_text(encoding='utf-8'))
            parents = {c: n for n in ast.walk(arbre) for c in ast.iter_child_nodes(n)}

            def porte(n):
                # S1 : seuls schéma, vue et admission historiques dans la porte,
                # sans exemption globale pour de nouveaux lecteurs de décision.
                if p.name != 'memoire.py':
                    return False
                while n in parents:
                    n = parents[n]
                    if isinstance(n, ast.FunctionDef):
                        return n.name in {'statuts_connus', 'recevoir_statuts', 'verifier_faits'}
                    if isinstance(n, ast.Assign):
                        if any(isinstance(t, ast.Name) and t.id == 'ATTRIBUTS_EAU_STATUTS'
                               for t in n.targets):
                            return True
                return False

            for n in ast.walk(arbre):
                if (isinstance(n, ast.Constant) and n.value == 'statuts'
                        and p.name not in ('relations.py', 'esprits.py', 'social.py', 'deliberation.py')
                        and not porte(n) or
                    isinstance(n, ast.Call) and getattr(n.func, 'attr', getattr(n.func, 'id', '')) == 'statuts_reconnus'
                        and p.name != 'relations.py'):
                    fautes.append(f'{p.name}:{n.lineno}')
        self.assertEqual(fautes, [])
