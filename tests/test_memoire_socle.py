"""S1a : écritures structurelles fermées, sans porter les lecteurs historiques."""
import ast
from collections import Counter
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import memoire
from donjon.esprits import lire, memoriser
from tests.test_tensions import recharger, relais

RACINE = Path(__file__).resolve().parents[1]


def controle(source):
    """Relevé fermé des accès et détection des mutations de liste par alias.

    Les champs d'un épisode restent mutables jusqu'à S1b–e. Ce contrôle
    syntaxique n'est pas une preuve générale de flux interprocédural ; les
    accès bruts restants sont donc aussi gelés par fichier/fonction/clé.
    """
    arbre = ast.parse(source)
    acces, fautes = Counter(), []
    parents = {enfant: n for n in ast.walk(arbre) for enfant in ast.iter_child_nodes(n)}

    def fonction(n):
        while n in parents:
            n = parents[n]
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return n.name
        return '<module>'

    # Alias conservateurs, limités à leur fonction ; une réaffectation ne
    # doit pas permettre de cacher l'origine d'un stock à un contrôle lexical.
    alias, cles = {}, {}

    def cle(n, f):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            return cles.get((f, n.id))

    def stock(n, f):
        if isinstance(n, ast.IfExp):
            return stock(n.body, f) or stock(n.orelse, f)
        if isinstance(n, ast.Name):
            return n.id in alias.get(f, set())
        if isinstance(n, ast.Subscript):
            return cle(n.slice, f) == 'memoire'
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.args:
            return n.func.attr in ('get', 'setdefault', '__getitem__') and cle(n.args[0], f) == 'memoire'
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'souvenirs':
            return True  # Ancien retour brut explicite de defense, jusqu'à S1c.
        return False

    def faute(n):
        fautes.append((fonction(n), ast.unparse(n)))

    for _ in range(len(list(ast.walk(arbre)))):
        changement = False
        for n in ast.walk(arbre):
            if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
                f = fonction(n)
                cibles = n.targets if isinstance(n, ast.Assign) else [n.target]
                for cible in cibles:
                    if isinstance(cible, ast.Name):
                        if isinstance(n.value, ast.Constant) and n.value.value == 'memoire':
                            cles[f, cible.id] = 'memoire'
                        if stock(n.value, f) and cible.id not in alias.get(f, set()):
                            alias.setdefault(f, set()).add(cible.id)
                            changement = True
        if not changement:
            break

    for n in ast.walk(arbre):
        f = fonction(n)
        if isinstance(n, ast.Dict):
            for k, valeur in zip(n.keys, n.values):
                if cle(k, f) == 'memoire' and (isinstance(valeur, (ast.List, ast.ListComp))
                        or isinstance(valeur, ast.Name) and valeur.id == 'list'):
                    faute(n)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'dict':
            if any(k.arg == 'memoire' for k in n.keywords):
                faute(n)
        if stock(n, f) and not isinstance(n, ast.Name):
            acces[f, 'memoire'] += 1
        if isinstance(n, ast.Subscript) and isinstance(n.ctx, (ast.Store, ast.Del)):
            if cle(n.slice, f) == 'memoire' or stock(n.value, f):
                faute(n)
        if isinstance(n, ast.AugAssign) and stock(n.target, f):
            faute(n)
        if isinstance(n, ast.Return) and n.value is not None and stock(n.value, f):
            faute(n)
        if (isinstance(n, ast.Attribute) and stock(n.value, f)
                and n.attr not in ('count', 'index', 'copy', '__iter__', '__len__', '__getitem__')):
            faute(n)
        if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
            continue
        methode = n.func.attr
        if (methode in ('setdefault', 'pop', '__setitem__', '__delitem__') and n.args
                and cle(n.args[0], f) == 'memoire'):
            faute(n)
        if methode == 'update':
            cles_update = [k.arg for k in n.keywords]
            for argument in [*n.args, *(k.value for k in n.keywords if k.arg is None)]:
                if isinstance(argument, ast.Dict):
                    cles_update.extend(cle(k, f) for k in argument.keys)
            if 'memoire' in cles_update:
                faute(n)
    return acces, fautes


class AccesTests(unittest.TestCase):
    def test_inventaire_des_lectures_restantes_et_aucune_ecriture(self):
        inventaire = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf-8'))
        mesures, fautes = {}, []
        for p in [*RACINE.glob('*.py'), *(RACINE / 'donjon').rglob('*.py'), *(RACINE / 'tools').rglob('*.py')]:
            relatif = p.relative_to(RACINE).as_posix()
            if relatif == 'donjon/memoire.py':
                continue
            acces, erreurs = controle(p.read_text(encoding='utf-8-sig'))
            if acces:
                mesures[relatif] = {f'{f}/{k}': n for (f, k), n in sorted(acces.items())}
            fautes.extend((relatif, f, expression) for f, expression in erreurs)
        # Homonymes de diagnostic + ancien retour brut de S1c, fermés à
        # l'expression exacte : aucune exemption générale de fonction.
        self.assertEqual(Counter(fautes), Counter([
            ('donjon/banc_pnj.py', 'resume_diagnostic', "g['memoire'] += bool(r.get('memoire'))"),
            ('donjon/banc_pnj.py', 'resume_diagnostic', "g['memoire']"),
            ('tools/mesurer_attente_bornee.py', 'observer', "courant['memoire']"),
            ('donjon/defense.py', 'souvenirs', "return monde.data.get('violences_joueur', []) if id == 'joueur' else lire(monde, id)['memoire']"),
            # Créations historiques vides, schéma exact gelé ci-dessous.
            ('donjon/esprits.py', 'esprit', "{'croyances': {}, 'memoire': [], 'faits_dits': {}}"),
            ('donjon/esprits.py', '<module>', self.schema_champs()),
            # Fixture explicite d'un outil de test, sans monde vivant.
            ('tools/test_saillance_210.py', 'vue', "dict(croyances={'ancien': {'lieu': dict(source='vu', minute=0)}, 'recent': {'lieu': dict(source='entendu', minute=80)}, 'hors_monde': {'lieu': dict(source='vu', minute=100)}}, memoire=[dict(type='enquete', besoin='chaleur', objets=['lie'])])"),
        ]))
        self.assertEqual(mesures, inventaire)

    @staticmethod
    def schema_champs():
        # Le grand dictionnaire CHAMPS reste propriétaire du schéma de
        # l'esprit. Seule sa déclaration de mémoire est autorisée ici.
        from donjon.esprits import CHAMPS
        assert CHAMPS['memoire'] is list
        arbre = ast.parse((RACINE / 'donjon/esprits.py').read_text(encoding='utf-8'))
        return ast.unparse(next(n.value for n in arbre.body if isinstance(n, ast.Assign)
                                and any(isinstance(c, ast.Name) and c.id == 'CHAMPS' for c in n.targets)))

    def test_contre_epreuves_des_ecritures_et_alias(self):
        for source in (
            'e["memoire"] = []', 'del e["memoire"]', 'e.setdefault("memoire", [])',
            'e.pop("memoire")', 'e.update(memoire=[])', 'e.update({"memoire": []})',
            'e.update(**{"memoire": stock})',
            'e.__setitem__("memoire", [])', 'e.__delitem__("memoire")',
            'e = {"memoire": [s]}', 'e = dict(memoire=[s])',
            'e["memoire"].append(s)', 'e.get("memoire").clear()',
            'stock = e["memoire"]; alias = stock; alias.remove(s)',
            'stock = e["memoire"]; del stock[:-40]',
            'stock = e["memoire"]; stock[cle] = s',
            'stock = e["memoire"]; stock[:] = []',
            'stock = e["memoire"]; stock += [s]',
            'stock = e["memoire"]; stock.reverse()',
            'stock = e["memoire"]; ajouter = stock.append; ajouter(s)',
            'stock = souvenirs(monde, id); stock.clear()',
            'cle = "memoire"; stock = e[cle]; stock.extend([s])',
            'def fuite(e):\n return e["memoire"]',
            'def fuite(e):\n stock = e.get("memoire"); return stock',
        ):
            with self.subTest(source=source):
                self.assertTrue(controle(source)[1])

    def test_lecture_et_contenu_non_portes_ne_sont_pas_des_ecritures_structurelles(self):
        for source in ('stock = e["memoire"]; s = stock[0]; s["tenu"] = True',
                       'copie = list(e["memoire"]); copie.clear()',
                       'copie = e["memoire"][:]; copie.append(s)',
                       'compte = Counter(s["type"] for s in e["memoire"])'):
            with self.subTest(source=source):
                self.assertFalse(controle(source)[1])


class PorteTests(unittest.TestCase):
    def test_copie_plafond_dates_ordre_et_identite(self):
        m = relais()
        for qui in ('marchand', 'joueur'):
            from donjon.esprits import esprit
            stock = esprit(m, qui)['memoire']
            for n in range(43):
                evenement = {'type': 'examen', 'salle': 'echoppe', 'case': [n, 1], 'nature': 'pas', 'minute': n}
                memoriser(m, qui, evenement)
                evenement['case'][0] = -1
            self.assertIs(lire(m, qui)['memoire'], stock)
            self.assertEqual(len(stock), 40)
            self.assertEqual([s['minute'] for s in stock], list(range(3, 43)))
            self.assertEqual([s['case'][0] for s in stock], list(range(3, 43)))
            survivant = stock[-1]
            memoire.evincer_episodes(m, qui, lambda s: s['minute'] < 42)
            self.assertIs(stock[0], survivant)
            self.assertEqual(len(stock), 1)
        avant = copy.deepcopy(m.data)
        self.assertEqual(recharger(m).data, avant)

    def test_crochets_reentrants_apres_insertion_et_eviction(self):
        m = relais()
        for n in range(40):
            memoriser(m, 'marchand', {'type': 'examen', 'salle': 'echoppe', 'nature': 'pas', 'case': None, 'minute': n})
        visites = []

        def relation(monde, qui, s):
            self.assertIs(lire(monde, qui)['memoire'][-1], s)
            self.assertEqual(len(lire(monde, qui)['memoire']), 40)
            visites.append(('relation', s['type']))
            if s['type'] == 'appel':
                memoriser(monde, qui, {'type': 'examen', 'salle': 'echoppe', 'nature': 'pas', 'case': None})

        def defense(monde, qui, s):
            visites.append(('defense', s['type']))

        with patch('donjon.relations.souvenir', side_effect=relation), patch('donjon.defense.retenir', side_effect=defense):
            memoriser(m, 'marchand', {'type': 'appel'})
        self.assertEqual(visites, [('relation', 'appel'), ('relation', 'examen'),
                                  ('defense', 'examen'), ('defense', 'appel')])
        self.assertEqual([s['type'] for s in lire(m, 'marchand')['memoire'][-2:]], ['appel', 'examen'])

    def test_migration_des_presences_ne_change_pas_les_autres_occurrences(self):
        m = relais()
        memoriser(m, 'marchand', {'type': 'presence_percue', 'qui': 'ilse', 'salle': 'echoppe', 'instant': 0})
        memoriser(m, 'marchand', {'type': 'examen', 'salle': 'echoppe', 'nature': 'pas', 'case': None})
        survivants = [copy.deepcopy(s) for s in lire(m, 'marchand')['memoire'] if s['type'] != 'presence_percue']
        m = recharger(m)
        self.assertEqual(lire(m, 'marchand')['memoire'], survivants)
        self.assertIn({'qui': 'ilse', 'salle': 'echoppe', 'instant': 0}, lire(m, 'marchand')['indices_soupcon']['presences'])
        self.assertEqual(recharger(m).data, m.data)


class ChaineTests(unittest.TestCase):
    def test_appel_auberge_et_relais_etat_complet_et_publication_apres_recharge(self):
        from tests import test_ouie_commune as sons
        from tests.test_tensions import vivre
        from donjon.rendu import regarder
        from donjon.scene import scene_percue

        # Cas historique : Hugues entend l'appel du couloir puis va examiner.
        # Autre cas : Gorm entend derrière la porte étanche du beffroi.
        for scene, temoin in ((sons.GardienTests().scene, 'hugues'), (sons.PorteFermeeTests().scene, 'marchand')):
            with self.subTest(temoin=temoin):
                m = scene()
                m.objets[temoin]['profil']['alerte'] = 3
                texte = sons.faire(m, "je crie a l'aide")
                self.assertIn("Tu cries à l'aide.", texte)
                m = recharger(m)
                entier, morcele = m.copier(), m.copier()
                entier, lignes = vivre(entier, 6)
                suite = []
                for _ in range(3):
                    morcele, nouvelles = vivre(morcele, 2)
                    suite.extend(nouvelles)
                self.assertEqual(lignes, suite)
                # Comparaison sans retrait de champ : valeurs ET ordre JSON.
                self.assertEqual(entier.data, morcele.data)
                self.assertEqual(json.dumps(entier.data), json.dumps(morcele.data))
                self.assertTrue(entier.data['emissions_parole'])
                self.assertTrue(any('va voir' in c['texte'] for c in entier.data['chronique']))
                public = (regarder(entier), scene_percue(entier), copy.deepcopy(entier.data['emissions_parole']))
                reprise = recharger(entier)
                self.assertEqual(reprise.data, entier.data)
                self.assertEqual((regarder(reprise), scene_percue(reprise), reprise.data['emissions_parole']), public)
                self.assertEqual((regarder(morcele), scene_percue(morcele), morcele.data['emissions_parole']), public)


if __name__ == '__main__':
    unittest.main()
