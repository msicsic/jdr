"""S1f : porte des preuves composées et inventaire fermé des autres familles."""
import ast
from collections import Counter
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon import memoire
from donjon.esprits import croire, croyance, lire
from donjon.monde import Monde
from tests.test_tensions import recharger, vivre

RACINE = Path(__file__).resolve().parents[1]


def acces_croyances(source):
    """Suit stocks, cellules, alias, boucles et méthodes détachées locaux.

    L'inventaire gèle aussi les expressions dérivées : ajouter une lecture de
    lieu sous un ancien accès d'une autre famille fait donc échouer le contrôle.
    Les vues de memoire ne sont pas des stocks. Aucune analyse interprocédurale.
    """
    arbre = ast.parse(source)
    parents = {c: n for n in ast.walk(arbre) for c in ast.iter_child_nodes(n)}

    def fonction(n):
        while n in parents:
            n = parents[n]
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return n.name
        return '<module>'

    alias, cles = {}, {}

    def cle(n, f):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            return cles.get((f, n.id))

    def niveau(n, f):
        if isinstance(n, ast.Name):
            return alias.get((f, n.id), 0)
        if isinstance(n, ast.IfExp):
            return max(niveau(n.body, f), niveau(n.orelse, f))
        if isinstance(n, ast.Subscript):
            if cle(n.slice, f) == 'croyances':
                return 1
            v = niveau(n.value, f)
            return v + 1 if v else 0
        if isinstance(n, ast.Attribute):
            return niveau(n.value, f)
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Attribute):
                if n.args and n.func.attr in ('get', 'setdefault', '__getitem__') and cle(n.args[0], f) == 'croyances':
                    return 1
                v = niveau(n.func.value, f)
                if v:
                    return v + int(n.func.attr in ('get', 'setdefault', '__getitem__'))
            if isinstance(n.func, ast.Name) and n.func.id == 'next' and n.args:
                g = n.args[0]
                return niveau(g.elt, f) if isinstance(g, ast.GeneratorExp) else niveau(g, f)
            if isinstance(n.func, ast.Name) and n.func.id in ('list', 'tuple', 'iter', 'reversed') and n.args:
                return niveau(n.args[0], f)
        return 0

    def lier(cible, v, f):
        if isinstance(cible, ast.Name) and v:
            # Chaque variable est suivie de façon conservative, même réaffectée.
            alias[f, cible.id] = min(v, alias.get((f, cible.id), v))

    for _ in range(len(list(ast.walk(arbre)))):
        avant = dict(alias), dict(cles)
        for n in ast.walk(arbre):
            f = fonction(n)
            if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
                cibles = n.targets if isinstance(n, ast.Assign) else [n.target]
                for t in cibles:
                    lier(t, niveau(n.value, f), f)
                    if isinstance(t, ast.Name) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                        cles[f, t.id] = n.value.value
            if isinstance(n, (ast.For, ast.comprehension)):
                it = n.iter
                if isinstance(it, ast.Call) and isinstance(it.func, ast.Attribute):
                    v = niveau(it.func.value, f)
                    if v and it.func.attr == 'items' and isinstance(n.target, (ast.Tuple, ast.List)):
                        lier(n.target.elts[-1], v + 1, f)
                    elif v and it.func.attr == 'values':
                        lier(n.target, v + 1, f)
        if avant == (alias, cles):
            break

    resultats = Counter()
    for n in ast.walk(arbre):
        f = fonction(n)
        if isinstance(n, (ast.Subscript, ast.Call, ast.Attribute)) and niveau(n, f):
            resultats[f, ast.unparse(n)] += 1
        if isinstance(n, ast.Return) and n.value and niveau(n.value, f):
            resultats[f, ast.unparse(n)] += 1
    return resultats


class AccesLocalisationTests(unittest.TestCase):
    def test_inventaire_ferme_des_acces_non_portes(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf-8'))
        mesures = {}
        for p in [*RACINE.glob('*.py'), *(RACINE / 'donjon').rglob('*.py'), *(RACINE / 'tools').rglob('*.py')]:
            relatif = p.relative_to(RACINE).as_posix()
            if relatif == 'donjon/memoire.py':
                continue
            acces = acces_croyances(p.read_text(encoding='utf-8-sig'))
            if acces:
                mesures[relatif] = {f'{f}/{expression}': n for (f, expression), n in sorted(acces.items())}
        self.assertEqual(mesures, fixture['croyances_restantes_s1f'])

    def test_contre_epreuves_alias_cles_dynamiques_cellules_et_retours(self):
        for source in (
            'e["croyances"][s]["lieu"]',
            'cle = "croyances"; stock = e[cle]; alias = stock; alias[s][a] = c',
            'stock = e.get("croyances"); sujet = stock.get(s, {}); sujet.get(attribut)',
            'stock = e["croyances"]; prendre = stock.get; prendre(s)',
            'stock = e["croyances"]; del stock[s]["lieu"]',
            'for s, d in e["croyances"].items():\n c = d.get("lieu"); c["minute"] = 4',
            'for d in e["croyances"].values():\n d["lieu"]["possession"].update(permis=True)',
            'stock = e["croyances"]; c = next((d for d in stock.values())); c.clear()',
            'def fuite(e):\n stock = e["croyances"]; return stock',
        ):
            with self.subTest(source=source):
                self.assertTrue(acces_croyances(source))
        initial = 'stock = e["croyances"]; etat = stock.get(s, {}).get("etat")'
        extension = initial + '; lieu = stock[s]["lieu"]; lieu["case"][0] = 8'
        self.assertNotEqual(acces_croyances(initial), acces_croyances(extension))
        self.assertFalse(acces_croyances('c = memoire.localisation(m, a, s); c["case"][0] = 8'))
        for source, terminal in (
            ('stock = e["croyances"]; alias = stock; alias[s]["lieu"]["minute"] = 4',
             "alias[s]['lieu']['minute']"),
            ('for s, d in e["croyances"].items():\n c = d.get("lieu"); c["case"][0] = 4',
             "c['case'][0]"),
            ('stock = e["croyances"]; methode = stock.get; methode(s)', 'stock.get'),
            ('stock = e["croyances"]; c = next((d for d in stock.values())); c.clear()', 'c.clear()'),
        ):
            with self.subTest(terminal=terminal):
                self.assertIn(('<module>', terminal), acces_croyances(source))


class PreuvesComposeesTests(unittest.TestCase):
    def test_lectures_pures_copies_profondes_et_confiance_initiale(self):
        from tests.test_voix import hugues_cherche_anselme
        m = hugues_cherche_anselme()
        avant = copy.deepcopy(m.data)
        self.assertIsNone(memoire.localisation(m, 'absent', 'anselme'))
        self.assertEqual(memoire.faits_connus(m, 'absent'), {})
        self.assertEqual(memoire.faits_connus(m, 'hugues', None), {})
        self.assertEqual(m.data, avant)
        preuve = dict(porteur='anselme', proprietaire='hugues', permis=False,
                      remis_par=None, remise_autorisee=False)
        croire(m, 'hugues', 'anselme', 'lieu', 'couloir', 'vu', salle='couloir', case=[1, 2],
               origine=dict(source='vu', minute=0), possession=preuve)
        m.data['minutes'] += 30
        memoire.consommer_hypothese(m, 'hugues', 'anselme')
        avant = copy.deepcopy(m.data)
        initiale = memoire.localisation(m, 'hugues', 'anselme')
        self.assertEqual(initiale['confiance'], 1)
        self.assertLess(croyance(m, 'hugues', 'anselme', 'lieu')['confiance'], 1)
        for c in (initiale, memoire.fait_brut(m, 'hugues', 'anselme', 'lieu'),
                  memoire.faits_connus(m, 'hugues', 'anselme')['lieu'],
                  memoire.faits_connus(m, 'hugues')['anselme']['lieu'],
                  croyance(m, 'hugues', 'anselme', 'lieu')):
            c['case'][0] = -1
            c['origine']['minute'] = -1
            c['possession']['permis'] = True
            c['hypothese_consommee']['lieu'] = 'autre'
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)

    def test_confirmation_et_retrait_vocal_conservent_les_autres_preuves(self):
        from tests.test_voix import hugues_cherche_anselme
        m = hugues_cherche_anselme()
        croire(m, 'hugues', 'anselme', 'lieu', 'couloir', 'se_dit', .6,
               salle='couloir', case=[1, 2])
        avant = memoire.localisation(m, 'hugues', 'anselme')
        memoire.reconnaitre_localisation_vocale(m, 'hugues', 'anselme')
        self.assertEqual(memoire.localisation(m, 'hugues', 'anselme'),
                         dict(avant, source='entendu', confiance=1.0))
        memoire.reconnaitre_localisation_vocale(m, 'hugues', 'anselme', imposture=True)
        self.assertIsNotNone(memoire.localisation(m, 'hugues', 'anselme'))
        croire(m, 'hugues', 'anselme', 'lieu', 'couloir', 'se_dit', .6,
               salle='couloir', case=[1, 2])
        autres = memoire.faits_connus(m, 'hugues', 'anselme')
        del autres['lieu']
        memoire.reconnaitre_localisation_vocale(m, 'hugues', 'anselme', imposture=True)
        self.assertIsNone(memoire.localisation(m, 'hugues', 'anselme'))
        self.assertEqual(memoire.faits_connus(recharger(m), 'hugues', 'anselme'), autres)

    def test_captures_reelles_laps_entier_decoupe_et_publication_rechargee(self):
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from donjon.emissions import lire as paroles
        # Cas réel du 374 et autre scène : les pistes expirées d'Aubin puis
        # les contacts/possessions de Bram ne dépendent pas du découpage.
        for fichier in ('captures/position-374-crue-42-18.json.gz',
                        'data/appels-restes-mine-7-470.json.gz'):
            with self.subTest(fichier=fichier):
                m = Monde(json.loads(gzip.decompress((RACINE / 'tests' / fichier).read_bytes())))
                bloc, lignes = vivre(recharger(m), 2)
                coupe, suite = recharger(m), []
                for _ in range(2):
                    coupe, nouvelles = vivre(coupe, 1)
                    suite.extend(nouvelles)
                    coupe = recharger(coupe)
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(json.dumps(bloc.data), json.dumps(coupe.data))
                self.assertEqual(lignes, suite)
                public = (regarder(bloc), scene_percue(bloc), copy.deepcopy(paroles(bloc)))
                reprise = recharger(bloc)
                self.assertEqual(reprise.data, bloc.data)
                self.assertEqual((regarder(reprise), scene_percue(reprise), paroles(reprise)), public)
                self.assertEqual((regarder(coupe), scene_percue(coupe), paroles(coupe)), public)


if __name__ == '__main__':
    unittest.main()
