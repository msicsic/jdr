"""S1a–d : porte des épisodes et requêtes/opérations historiques."""
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

    # S1b–d ferment aussi les champs des familles portées issues du stock brut.
    # Les autres familles gardent leurs mutations historiques jusqu'à leur lot.
    sons = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Compare):
            valeurs = [v.value for c in n.comparators for v in ast.walk(c) if isinstance(v, ast.Constant)]
            if not any(v in ('bruit', 'examen', 'approche_charge', 'mise_en_garde',
                             'a_prevenir', 'secours', 'promis', 'nourri', 'recu', 'promesse_annulee',
                             'creance', 'tache_payee', 'suivi_engagement', 'engagement_pris',
                             'engagement_tenu', 'engagement_abandonne', 'pret', 'pret_reclame',
                             'abandon_annonce') for v in valeurs):
                continue
            for c in ast.walk(n.left):
                if isinstance(c, ast.Subscript) and cle(c.slice, fonction(n)) == 'type' and isinstance(c.value, ast.Name):
                    sons.add((fonction(n), c.value.id))

    def derive_stock(n, f):
        return stock(n, f) or (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                              and n.func.id in ('reversed', 'iter', 'list')
                              and any(derive_stock(a, f) for a in n.args))

    elements = set()
    for n in ast.walk(arbre):
        if isinstance(n, (ast.For, ast.comprehension)) and isinstance(n.target, ast.Name):
            f = fonction(n)
            if (f, n.target.id) in sons and derive_stock(n.iter, f):
                elements.add((f, n.target.id))
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Subscript):
            f = fonction(n)
            if derive_stock(n.value.value, f):
                elements.update((f, t.id) for t in n.targets if isinstance(t, ast.Name)
                                and (f, t.id) in sons)

    def element(n, f):
        if isinstance(n, ast.Name):
            return (f, n.id) in elements
        if isinstance(n, (ast.Subscript, ast.Attribute)):
            return element(n.value, f)
        return False

    for _ in range(len(list(ast.walk(arbre)))):
        avant = len(elements)
        for n in ast.walk(arbre):
            if isinstance(n, ast.Assign):
                valeur = n.value
                selection = (isinstance(valeur, ast.Call) and isinstance(valeur.func, ast.Name)
                             and valeur.func.id == 'next' and valeur.args
                             and isinstance(valeur.args[0], ast.GeneratorExp)
                             and element(valeur.args[0].elt, fonction(n)))
                if element(valeur, fonction(n)) or selection:
                    elements.update((fonction(n), t.id) for t in n.targets if isinstance(t, ast.Name))
        if len(elements) == avant:
            break

    for n in ast.walk(arbre):
        f = fonction(n)
        if isinstance(n, ast.Subscript) and isinstance(n.ctx, (ast.Store, ast.Del)) and element(n.value, f):
            faute(n)
        if isinstance(n, ast.Attribute) and element(n.value, f) and n.attr in (
                'update', 'pop', 'clear', 'setdefault', '__setitem__', '__delitem__', 'append', 'extend'):
            faute(n)
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

    def test_contre_epreuves_des_mutations_de_souvenirs_sonores(self):
        for mutation in ('s["minute"] = 3', 'alias = s; alias["case"][0] = 1',
                         's.update(minute=3)', 'del s["qui"]', 's.pop("case")',
                         'modifier = s.update; modifier(minute=3)'):
            source = ('stock = e["memoire"]\nfor s in reversed(stock):\n'
                      ' if s["type"] == "examen":\n  ' + mutation)
            with self.subTest(source=source):
                self.assertTrue(controle(source)[1])

    def test_contre_epreuves_des_mutations_approches_avertissements_et_secours(self):
        for famille in ('approche_charge', 'mise_en_garde', 'a_prevenir', 'secours'):
            for mutation in ('s["examine"] = True', 'alias = s; alias["case"][0] = 1',
                             's.update(tenu=True)', 'del s["preuve"]', 's.pop("case")',
                             'modifier = s.update; modifier(tenu=True)'):
                source = ('stock = e["memoire"]\nfor s in reversed(stock):\n'
                          f' if s["type"] == "{famille}":\n  ' + mutation)
                with self.subTest(famille=famille, mutation=mutation):
                    self.assertTrue(controle(source)[1])
            source = (f'alerte = next((s for s in e["memoire"] if s["type"] == "{famille}"), None)\n'
                      'alias = alerte\nalias["tenu"] = True')
            with self.subTest(selection=famille):
                self.assertTrue(controle(source)[1])


class MemoireEngagementsTests(unittest.TestCase):
    def test_requetes_pures_copies_et_ordre_de_liste_plutot_que_dates(self):
        m = relais()
        avant = copy.deepcopy(m.data)
        self.assertEqual(memoire.episodes_parts_promises(m, 'inconnu'), [])
        self.assertEqual(memoire.travaux_payes_retenus(m, 'inconnu'), [])
        self.assertEqual(memoire.dernier_travail_paye(m, 'inconnu', {}), (None, False))
        self.assertIsNone(memoire.suivi_engagement(m, 'inconnu', {}, 0))
        self.assertFalse(memoire.pret_retenu(m, 'inconnu', 'objet', 'joueur'))
        self.assertEqual(m.data, avant)
        c = {'objet': 'brasero', 'allume': True}
        with patch('donjon.relations.souvenir'), patch('donjon.defense.retenir'):
            for s in ({'type': 'creance', 'de': 'aubin', 'quoi': 'tache', 'minute': 99},
                      {'type': 'tache_payee', 'a': 'aubin', 'condition': c, 'minute': 2},
                      {'type': 'tache_payee', 'a': 'aubin', 'condition': c, 'minute': 1},
                      {'type': 'promis', 'de': 'aubin', 'objet': 'planches', 'part': ['detail']},
                      {'type': 'suivi_engagement', 'condition': c, 'depuis': 0, 'initiale': {'valeur': [True]}}):
                memoriser(m, 'marchand', s)
        avant = copy.deepcopy(m.data)
        travaux = memoire.travaux_payes_retenus(m, 'marchand')
        self.assertEqual([s['minute'] for s in travaux], [2, 1])
        dernier, reclame = memoire.dernier_travail_paye(m, 'marchand', c)
        self.assertEqual(dernier['minute'], 1)
        self.assertFalse(reclame)  # La créance plus ancienne dans la liste ne clôt rien.
        travaux[0]['condition']['allume'] = False
        dernier['condition']['allume'] = False
        memoire.episodes_parts_promises(m, 'marchand')[-1]['part'].clear()
        memoire.suivi_engagement(m, 'marchand', c, 0)['initiale']['valeur'].clear()
        self.assertEqual(m.data, avant)
        with patch('donjon.relations.souvenir'), patch('donjon.defense.retenir'):
            memoriser(m, 'marchand', {'type': 'creance', 'de': 'aubin', 'quoi': 'tache', 'minute': 0})
        self.assertTrue(memoire.dernier_travail_paye(m, 'marchand', c)[1])

    def test_suivi_arrete_par_autre_parole_et_fenetre_quarante(self):
        m = relais()
        c = {'objet': 'brasero', 'allume': True}
        with patch('donjon.relations.souvenir'), patch('donjon.defense.retenir'):
            memoriser(m, 'marchand', {'type': 'suivi_engagement', 'condition': c, 'depuis': 0, 'initiale': None})
            memoriser(m, 'marchand', {'type': 'engagement_pris', 'condition': c})
            self.assertIsNone(memoire.suivi_engagement(m, 'marchand', c, 0))
            memoriser(m, 'marchand', {'type': 'pret', 'objet': 'torche', 'a': 'joueur'})
            self.assertTrue(memoire.pret_retenu(m, 'marchand', 'torche', 'joueur'))
            for _ in range(40):
                memoriser(m, 'marchand', {'type': 'examen', 'salle': 'echoppe', 'nature': 'pas', 'case': None})
        self.assertFalse(memoire.pret_retenu(m, 'marchand', 'torche', 'joueur'))
        self.assertEqual(len(lire(m, 'marchand')['memoire']), 40)
        self.assertEqual(memoire.episodes_parts_promises(m, 'marchand'), [])
        self.assertEqual(recharger(m).data, m.data)

    def test_remise_meme_auteur_objet_et_minute_seulement(self):
        m = relais()
        with patch('donjon.relations.souvenir'), patch('donjon.defense.retenir'):
            memoriser(m, 'marchand', {'type': 'recu', 'de': 'aubin', 'objet': 'torche', 'minute': 3})
        self.assertTrue(memoire.remise_retenue(m, 'marchand', 'aubin', 'torche', 3))
        for de, objet, minute in (('ilse', 'torche', 3), ('aubin', 'planches', 3), ('aubin', 'torche', 2)):
            self.assertFalse(memoire.remise_retenue(m, 'marchand', de, objet, minute))

    def test_jugement_pret_identite_bornes_et_reentrance_sur_stock_vivant(self):
        from donjon.biens import RENDRE
        m = relais()
        with patch('donjon.relations.souvenir'), patch('donjon.defense.retenir'):
            for _ in range(40):
                memoriser(m, 'marchand', {'type': 'pret_reclame', 'objet': 'torche', 'pret': 0,
                                         'echu': True, 'minute': 0})
        stock = lire(m, 'marchand')['memoire']
        originaux = list(stock)
        m.data['minutes'] = RENDRE - 1
        consequence = []
        memoire.juger_reclamations_pret(m, 'marchand', 'torche', 0, lambda: consequence.append(True))
        self.assertEqual(consequence, [])
        m.data['minutes'] = RENDRE
        def suite():
            # Le crochet est appelé après la marque et ajoute un épisode qui
            # décale le prochain indice de l'itérateur, comme historiquement.
            consequence.append(True)
            self.assertTrue(any(s.get('juge') for s in stock))
            memoriser(m, 'marchand', {'type': 'appel'})
        with patch('donjon.relations.souvenir') as relation, patch('donjon.defense.retenir') as defense:
            memoire.juger_reclamations_pret(m, 'marchand', 'torche', 0, suite)
        self.assertIs(lire(m, 'marchand')['memoire'], stock)
        self.assertEqual([i for i, s in enumerate(originaux) if s.get('juge')], list(range(0, 40, 2)))
        self.assertEqual(len(consequence), 20)
        self.assertEqual(relation.call_count, 20)
        self.assertEqual(defense.call_count, 20)
        self.assertIs(stock[0], originaux[20])

    def test_controle_des_marques_de_promesses_et_prets(self):
        for famille in ('promis', 'nourri', 'recu', 'promesse_annulee', 'creance', 'tache_payee',
                        'suivi_engagement', 'engagement_pris', 'engagement_tenu',
                        'engagement_abandonne', 'pret', 'pret_reclame', 'abandon_annonce'):
            for selection in (f'for s in e["memoire"]:\n if s["type"] == "{famille}":\n  s["juge"] = True',
                              f'stock = e["memoire"]\ns = stock[0]\nif s["type"] == "{famille}":\n s.update(juge=True)'):
                with self.subTest(famille=famille, source=selection):
                    self.assertTrue(controle(selection)[1])


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


class MemoireSonoreTests(unittest.TestCase):
    def test_requetes_pures_et_copies_profondes_y_compris_la_facade(self):
        from donjon.ouie import couvert
        m = relais()
        avant = copy.deepcopy(m.data)
        self.assertEqual(memoire.bruits_retenus(m, 'inexistant'), [])
        self.assertIsNone(memoire.examen_couvrant(m, 'inexistant', 'echoppe', 'pas'))
        self.assertFalse(memoire.rafraichir_examen_sonore(m, 'inexistant', 'echoppe', 'pas'))
        self.assertEqual(m.data, avant)
        for qui in ('marchand', 'joueur'):
            memoriser(m, qui, dict(type='bruit', salle='echoppe', nature='pas', niveau=2, case=[1, 2]))
            memoriser(m, qui, dict(type='examen', salle='echoppe', nature='appel', case=[3, 2]))
            avant = copy.deepcopy(m.data)
            sons = memoire.bruits_retenus(m, qui, 'echoppe', examens=True)
            sons[0]['case'][0] = -1
            sons[1]['minute'] = -1
            sons.clear()
            for lecture in (memoire.examen_couvrant, couvert):
                examen = lecture(m, qui, 'echoppe', 'pas')
                examen['case'][0] = -1
                examen['minute'] = -1
            self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, m.data)

    def test_rafraichissement_meme_occurrence_sans_crochet_et_bornes_historiques(self):
        from donjon.esprits import RECENT
        m = relais()
        memoriser(m, 'marchand', dict(type='examen', salle='echoppe', nature='bruyant',
                                     qui='ilse', case=None))
        stock = lire(m, 'marchand')['memoire']
        occurrence = stock[-1]
        date = occurrence['minute']
        m.data['minutes'] = date + RECENT
        # Dernier instant inclus ; ni nouvelle preuve, ni déplacement dans la liste.
        with patch('donjon.relations.souvenir') as relation, patch('donjon.defense.retenir') as defense:
            self.assertTrue(memoire.rafraichir_examen_sonore(m, 'marchand', 'echoppe', 'pas', 'ilse'))
            relation.assert_not_called()
            defense.assert_not_called()
        self.assertIs(stock[-1], occurrence)
        self.assertEqual(occurrence['minute'], date + RECENT)
        avant = copy.deepcopy(m.data)
        for nature, qui, case in (('appel', None, None), ('pas', 'aubin', None), ('pas', None, [1, 2])):
            self.assertFalse(memoire.rafraichir_examen_sonore(m, 'marchand', 'echoppe', nature, qui, case))
        self.assertEqual(m.data, avant)
        m.data['minutes'] += RECENT + 1
        self.assertIsNone(memoire.examen_couvrant(m, 'marchand', 'echoppe', 'pas'))
        self.assertEqual(recharger(m).data, m.data)

    def test_examen_plus_recent_incompatible_ne_reprend_pas_un_ancien(self):
        m = relais()
        for nature in ('appel', 'pas'):
            memoriser(m, 'marchand', dict(type='examen', salle='echoppe', nature=nature, case=[1, 2]))
        self.assertIsNone(memoire.examen_couvrant(m, 'marchand', 'echoppe', 'bruyant'))
        self.assertEqual(memoire.examen_couvrant(m, 'marchand', 'echoppe', 'pas')['nature'], 'pas')

    def test_remplacements_conservent_ordre_maximum_et_crochets_reentrants(self):
        from donjon.ouie import _retenir_seulement, parcouru
        m = relais()
        for nature, niveau in (('bruyant', 5), ('pas', 2)):
            memoriser(m, 'marchand', dict(type='bruit', salle='echoppe', nature=nature, niveau=niveau))
        memoriser(m, 'marchand', dict(type='examen', salle='antichambre', nature='pas', case=None))
        survivant = lire(m, 'marchand')['memoire'][-1]
        visites = []

        def relation(monde, qui, s):
            visites.append(('relation', s['type']))
            self.assertIs(lire(monde, qui)['memoire'][-1], s)
            if s['type'] == 'examen':
                memoriser(monde, qui, dict(type='attente'))

        def defense(monde, qui, s):
            visites.append(('defense', s['type']))

        with patch('donjon.relations.souvenir', side_effect=relation), patch('donjon.defense.retenir', side_effect=defense):
            _retenir_seulement(m, 'marchand', 'echoppe', 'voix', 3)
            self.assertEqual(memoire.bruits_retenus(m, 'marchand', 'echoppe')[-1]['nature'], 'bruyant')
            self.assertEqual(memoire.bruits_retenus(m, 'marchand', 'echoppe')[-1]['niveau'], 5)
            self.assertTrue(parcouru(m, 'marchand', 'echoppe', (1, 2)))
        self.assertIs(lire(m, 'marchand')['memoire'][0], survivant)
        self.assertEqual(visites, [('relation', 'bruit'), ('defense', 'bruit'),
                                  ('relation', 'examen'), ('relation', 'attente'),
                                  ('defense', 'attente'), ('defense', 'examen')])
        self.assertFalse(parcouru(m, 'marchand', 'echoppe'))
        self.assertIsNotNone(memoire.examen_couvrant(m, 'marchand', 'echoppe', 'pas'))
        self.assertEqual(recharger(m).data, m.data)


class ApprochesSecoursTests(unittest.TestCase):
    def test_lectures_pures_copies_et_selection_historique(self):
        m = relais()
        avant = copy.deepcopy(m.data)
        self.assertEqual(memoire.secours_retenus(m, 'absent'), [])
        self.assertEqual(memoire.avertissements_a_donner(m, 'absent'), [])
        self.assertIsNone(memoire.derniere_approche(m, 'absent', 'ilse', 'bois', 'echoppe', [1, 2]))
        self.assertIsNone(memoire.avertissement_du(m, 'absent', 'ilse', 'brune'))
        self.assertFalse(memoire.mise_en_garde_retenue(m, 'absent', 'ilse', 'bois', 'p'))
        self.assertFalse(memoire.acquitter_avertissement(m, 'absent', 'ilse', 'brune'))
        self.assertEqual(memoire.examiner_secours_constates(m, 'absent'), [])
        self.assertEqual(memoire.examiner_secours_du_lieu(m, 'absent', 'echoppe'), [])
        self.assertEqual(m.data, avant)
        for qui in ('marchand', 'joueur'):
            for preuve in ('ancien', 'recent'):
                memoriser(m, qui, dict(type='approche_charge', auteur='ilse', objet='bois',
                                      case=[1, 2], preuve=preuve))
            memoriser(m, qui, dict(type='mise_en_garde', a='ilse', objet='bois', preuve='ancien'))
            memoriser(m, qui, dict(type='a_prevenir', victime='ilse', auteur='brune', preuve='alerte'))
            memoriser(m, qui, dict(type='secours', qui='ilse', salle='echoppe', case=[1, 2]))
            avant = copy.deepcopy(m.data)
            approche = memoire.derniere_approche(m, qui, 'ilse', 'bois', 'echoppe', [3, 4])
            self.assertEqual(approche['preuve'], 'recent')
            approche['case'][0] = -1
            self.assertIsNone(memoire.derniere_approche(m, qui, 'ilse', 'bois', 'echoppe', [3, 4], [0, 0]))
            self.assertTrue(memoire.mise_en_garde_retenue(m, qui, 'ilse', 'bois', 'ancien'))
            self.assertFalse(memoire.mise_en_garde_retenue(m, qui, 'ilse', 'bois', 'recent'))
            memoire.secours_retenus(m, qui)[0]['case'][0] = -1
            memoire.avertissements_a_donner(m, qui)[0]['tenu'] = True
            memoire.avertissement_du(m, qui, 'ilse', 'brune')['tenu'] = True
            self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, m.data)

    def test_acquittements_meme_occurrence_ordre_et_sans_crochet(self):
        m = relais()
        for qui in ('marchand', 'joueur'):
            for _ in range(2):
                memoriser(m, qui, dict(type='a_prevenir', victime='ilse', auteur='brune'))
            for personne, salle in (('ilse', 'echoppe'), ('brune', 'antichambre'), ('ilse', 'echoppe')):
                memoriser(m, qui, dict(type='secours', qui=personne, salle=salle, case=[1, 2]))
            stock = lire(m, qui)['memoire']
            occurrences = list(stock)
            alertes = [s for s in stock if s['type'] == 'a_prevenir']
            with patch('donjon.relations.souvenir') as relation, patch('donjon.defense.retenir') as defense:
                self.assertTrue(memoire.acquitter_avertissement(m, qui, 'ilse', 'brune'))
                self.assertFalse(memoire.acquitter_avertissement(m, qui, 'ilse', 'brune'))
                self.assertTrue(alertes[0]['tenu'])
                self.assertNotIn('tenu', alertes[1])
                self.assertEqual(memoire.examiner_secours_du_lieu(m, qui, 'echoppe'), ['ilse', 'ilse'])
                self.assertEqual(memoire.examiner_secours_du_lieu(m, qui, 'echoppe'), [])
                self.assertEqual([s['qui'] for s in memoire.secours_retenus(m, qui, en_attente=True)], ['brune'])
                relation.assert_not_called()
                defense.assert_not_called()
            self.assertIs(stock, lire(m, qui)['memoire'])
            self.assertTrue(all(a is b for a, b in zip(stock, occurrences)))
        self.assertEqual(recharger(m).data, m.data)

    def test_constat_strictement_posterieur_ou_vue_actuelle(self):
        m = relais()
        for minute in (0, 1):
            memoriser(m, 'marchand', dict(type='secours', qui='ilse', salle='echoppe', minute=minute))
        e = lire(m, 'marchand')
        e['croyances']['ilse']['etat'] = dict(valeur={}, source='vu', minute=1, confiance=1)
        with patch('donjon.esprits.percoit', return_value=False):
            self.assertEqual(memoire.examiner_secours_constates(m, 'marchand'), ['ilse'])
        self.assertEqual([s.get('examine', False) for s in memoire.secours_retenus(m, 'marchand')], [True, False])
        with patch('donjon.esprits.percoit', return_value=True):
            self.assertEqual(memoire.examiner_secours_constates(m, 'marchand'), ['ilse'])
        self.assertEqual(recharger(m).data, m.data)

    def test_avertissement_acquitte_avant_crochet_reentrant_du_service(self):
        from donjon.relations import FIABLE
        from donjon.voix import connaitre
        m = relais()
        connaitre(m, 'ilse', 'marchand')
        memoriser(m, 'marchand', dict(type='a_prevenir', victime='ilse', auteur='brune', preuve='alerte'))
        visites = []

        def defense(monde, qui, souvenir):
            visites.append((qui, souvenir['type']))
            if souvenir['type'] == 'prevenu':
                self.assertTrue(memoire.avertissement_du(monde, 'marchand', 'ilse', 'brune')['tenu'])

        with patch('donjon.defense.retenir', side_effect=defense):
            for _ in range(2):
                memoriser(m, 'marchand', dict(type='dit', a='ilse', sujet='brune', attribut=FIABLE, valeur=False))
        self.assertEqual(visites, [('ilse', 'prevenu'), ('marchand', 'dit'), ('marchand', 'dit')])
        prevenus = [s for s in lire(m, 'ilse')['memoire'] if s['type'] == 'prevenu']
        self.assertEqual([s['preuve'] for s in prevenus], ['service:alerte'])
        self.assertEqual(recharger(m).data, m.data)


class ChaineTests(unittest.TestCase):
    def test_examen_vain_et_appel_repete_mine_et_autre_auditeur_apres_recharges(self):
        from tests.test_ouie_temoins import creer, calme, MINEURS, placer, percevoir_tous
        from tests.test_tensions import vivre
        from donjon.ouie import entendre, parcouru, couvert
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from donjon.emissions import lire as paroles

        # Mine 18, minutes 455–560 : Mathe ne repart plus pour le même appel
        # du bureau noir. Bram éprouve le même contrat avec un autre observateur.
        for qui in ('mathe', 'bram'):
            with self.subTest(qui=qui):
                m = creer('mine', 18, depart='fixe')
                calme(m, *MINEURS)
                m.objets['chandelle'].update(allume=False, combustible=0)
                m.objets['porte_bureau'].update(verrouillee=False, ouverte=True)
                placer(m, qui, 'baraquement', (2, 2))
                placer(m, 'lucien', 'bureau', (0, 3))
                percevoir_tous(m)
                # L'émetteur reste sur place pendant cette éprouvette sonore ;
                # sa voix anonyme n'ouvre pas un secours distinct de l'examen.
                lire(m, 'lucien')['libre'] = 6000
                lire(m, qui)['voix'].remove('lucien')
                entendre(m, qui, 'lucien', 'bureau', (0, 3), 'appel', 0, 6)
                self.assertTrue(memoire.bruits_retenus(m, qui, 'bureau'))
                self.assertTrue(parcouru(m, qui, 'bureau'))
                m = recharger(m)
                entier, morcele = m.copier(), m.copier()
                for _ in range(2):
                    entier, lignes = vivre(entier, 2)
                    suite = []
                    for _ in range(2):
                        morcele, nouvelles = vivre(morcele, 1)
                        suite.extend(nouvelles)
                        morcele = recharger(morcele)
                    self.assertEqual(lignes, suite)
                    for monde in (entier, morcele):
                        avant = couvert(monde, qui, 'bureau', 'appel')
                        self.assertIsNotNone(avant)
                        entendre(monde, qui, 'lucien', 'bureau', (0, 3), 'appel', 0, 6)
                        self.assertEqual(memoire.bruits_retenus(monde, qui, 'bureau'), [])
                        apres = couvert(monde, qui, 'bureau', 'appel')
                        self.assertEqual(apres, dict(avant, minute=monde.data['minutes']))
                    self.assertEqual(entier.data, morcele.data)
                    self.assertEqual(json.dumps(entier.data), json.dumps(morcele.data))
                    public = (regarder(entier), scene_percue(entier), copy.deepcopy(paroles(entier)))
                    reprise = recharger(entier)
                    self.assertEqual(reprise.data, entier.data)
                    self.assertEqual((regarder(reprise), scene_percue(reprise), paroles(reprise)), public)
                    self.assertEqual((regarder(morcele), scene_percue(morcele), paroles(morcele)), public)
                # Mieux situé depuis le bureau : ce son nouveau reste à examiner.
                for monde in (entier, morcele):
                    placer(monde, qui, 'bureau', (4, 0))
                    entendre(monde, qui, 'lucien', 'bureau', (0, 3), 'appel', 0, 6)
                    self.assertEqual(memoire.bruits_retenus(recharger(monde), qui, 'bureau')[-1]['case'], [0, 3])
                self.assertEqual(recharger(entier).data, recharger(morcele).data)

    def test_appel_auberge_et_relais_etat_complet_et_publication_apres_recharge(self):
        from tests import test_ouie_commune as sons
        from tests.test_tensions import vivre
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from donjon.emissions import lire as paroles

        # Cas historique : Hugues entend l'appel du couloir puis va examiner.
        # Autre cas : Gorm entend derrière la porte étanche du beffroi.
        for scene, temoin, resultat, mots in (
                (sons.GardienTests().scene, 'hugues', "Hugues va voir d'où venait le bruit : Couloir de l'étage.", None),
                (sons.PorteFermeeTests().scene, 'marchand', 'Gorm, gardien du relais force la porte étanche du beffroi.',
                 'Gorm glisse à Aubin que la torche est éteinte.')):
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
                self.assertIn(resultat, [c['texte'] for c in entier.data['chronique']])
                # Un cri d'aide est un son ; il n'impose pas une parole.
                # Le second parcours produit aussi une confidence entendue.
                if mots is not None:
                    self.assertIn(mots, [p['texte'] for p in paroles(entier)])
                public = (regarder(entier), scene_percue(entier), copy.deepcopy(paroles(entier)))
                reprise = recharger(entier)
                self.assertEqual(reprise.data, entier.data)
                self.assertEqual((regarder(reprise), scene_percue(reprise), paroles(reprise)), public)
                self.assertEqual((regarder(morcele), scene_percue(morcele), paroles(morcele)), public)


if __name__ == '__main__':
    unittest.main()
