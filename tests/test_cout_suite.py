"""Optimisations exactes : preuves de graphe et empreintes des mutations ordinaires."""
from types import SimpleNamespace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, spatial
from donjon.banc_pnj import creer
from donjon.esprits import percus
from donjon.planification import Etat


def graphe(arcs, but):
    etats = {s: Etat(s, (), {}) for s in arcs}
    noeuds = {etats[s]: [s == but, None, 0,
        [(faute, duree, [], etats[t], 0, False, 0) for t, faute, duree in suites], False]
        for s, suites in arcs.items()}
    return etats, noeuds


def preuve(v, depart, but, profondeur, faute, tenir, sombre, lumiere=None, voir=False):
    """Le certificat sur les deux graphes gardés (``_explorer``)."""
    return p._sans_plan(v, depart, but, profondeur, faute, tenir,
                        {"sombre": sombre, "lumiere": lumiere or {}}, voir)


class AbsenceTests(unittest.TestCase):
    def test_cout_change_ne_suffit_pas_a_prouver_une_absence(self):
        # Un chemin peu cher mais long atteint x à la profondeur limite ; un autre prix
        # fait arriver par le chemin court et permet d'atteindre le but. Aucun cache de
        # résultat vide ne doit assimiler une exploration pondérée à un certificat.
        e, g = graphe({'s': [('a', 0, 1), ('x', 1, 1)], 'a': [('b', 0, 1)],
                      'b': [('x', 0, 1)], 'x': [('fin', 0, 1)], 'fin': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: x.salle == 'fin'
        self.assertIsNone(p._explorer_etats(v, e['s'], but, {}, 3, 100, 10, graphe=g.copy())[0])
        self.assertIsNotNone(p._explorer_etats(v, e['s'], but, {}, 3, 100, 0, graphe=g.copy())[0])
        self.assertFalse(preuve(v, e['s'], but, 3, 10, False, g.copy())[0])

    def test_borne_ou_but_ne_sont_jamais_une_preuve_d_absence(self):
        e, g = graphe({'s': [('a', 0, 1)], 'a': [('fin', 0, 1)], 'fin': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: x.salle == 'fin'
        with patch.object(p, 'PREUVE_MAX', 1):
            self.assertEqual(preuve(v, e['s'], but, 3, 1, False, g), (False, 1, 'borne'))
        self.assertFalse(preuve(v, e['s'], but, 3, 1, False, g)[0])
        self.assertTrue(preuve(v, e['s'], but, 1, 1, False, g)[0])

    def test_retirer_un_etat_domine_change_la_recherche_bornee(self):
        # Même salle et mêmes moyens, mais un chemin a coûté plus et dépensé une pièce.
        # Le retirer conserve l'optimum illimité, tout en changeant la réponse à cinq nœuds.
        s, fin = Etat('s', (), {}), Etat('fin', (), {})
        riches = [Etat(salle, (), {}) for salle in ('a', 'b', 'c')]
        pauvres = [Etat(salle, (), {('depense',): 1}) for salle in ('a', 'b', 'c')]
        g = {e: [e == fin, None, 0, [], False] for e in [s, fin, *riches, *pauvres]}
        def arc(de, vers, cout):
            g[de][3].append((0, cout, [], vers, 0, False, 0))
        arc(s, riches[0], 1)
        arc(s, pauvres[0], 2)
        for chemin in (riches, pauvres):
            arc(chemin[0], chemin[1], 1)
            arc(chemin[0], fin, 9)
            arc(chemin[1], chemin[2], 1)
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, e: e == fin
        complet = p._explorer_etats(v, s, but, {}, 8, 50, 0, graphe=g)[0]
        self.assertEqual(complet[0], 10)
        self.assertIsNone(p._explorer_etats(v, s, but, {}, 8, 5, 0, graphe=g)[0])
        reduit = {**g, s: [False, None, 0, g[s][3][:1], False]}
        self.assertEqual(p._explorer_etats(v, s, but, {}, 8, 5, 0, graphe=reduit)[0], complet)

    def test_permission_et_profondeur_entrent_dans_la_preuve(self):
        e, g = graphe({'s': [('a', 1, 1)], 'a': [('fin', 0, 1)], 'fin': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: x.salle == 'fin'
        self.assertTrue(preuve(v, e['s'], but, 3, None, False, g)[0])
        self.assertFalse(preuve(v, e['s'], but, 3, 1, False, g)[0])

    def test_un_graphe_incomplet_ne_prouve_rien_et_n_est_pas_developpe(self):
        e, g = graphe({'s': [('a', 0, 1)], 'a': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: False
        g[e['a']][3] = None
        with patch.object(p, '_suites', side_effect=AssertionError('développement supplémentaire')):
            self.assertEqual(preuve(v, e['s'], but, 3, 1, False, g), (False, 2, 'lacune'))
            del g[e['a']]
            self.assertEqual(preuve(v, e['s'], but, 3, 1, False, g), (False, 2, 'lacune'))

    def test_une_lecture_de_lumiere_dans_le_graphe_sombre_demande_la_preuve_avec_lumiere(self):
        # Graphe sombre : x lit la lumière quand ses gestes se développent (« gestes ») ; aucun
        # but dans le noir. Le graphe lumière, que la reprise avec les moyens d'éclairer emploie,
        # atteint le but : l'absence n'est pas prouvée. Sans ce graphe, c'est une lacune.
        e, sombre = graphe({'s': [('a', 0, 1), ('x', 1, 1)], 'a': [], 'x': []}, 'fin')
        sombre[e['x']][4] = 'gestes'
        _, lumiere = graphe({'s': [('fin', 0, 1)], 'fin': []}, 'fin')
        lumiere = {e['s'] if k.salle == 's' else k: n for k, n in lumiere.items()}
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: x.salle == 'fin'
        self.assertEqual(p._parcours(v, sombre, e['s'], 3, 1, False)[::3], (True, True))
        self.assertEqual(preuve(v, e['s'], but, 3, 1, False, sombre, lumiere), (False, 5, 'but'))
        self.assertEqual(preuve(v, e['s'], but, 3, 1, False, sombre), (False, 4, 'lacune'))
        # Lu par le but de x (« but ») : de même, même à la profondeur limite.
        sombre[e['x']][4] = 'but'
        self.assertFalse(preuve(v, e['s'], but, 1, 1, False, sombre, lumiere)[0])
        # Lu par ses gestes à la profondeur limite : ils ne s'y développent pas, rien n'est lu.
        sombre[e['x']][4] = 'gestes'
        self.assertEqual(preuve(v, e['s'], but, 1, 1, False, sombre, lumiere), (True, 3, 'epuise'))
        # Le graphe lumière sans but prouve aussi l'absence ; qui voit dès le départ n'y lit que lui.
        sans_but = {k: [False, *n[1:]] for k, n in lumiere.items()}
        self.assertTrue(preuve(v, e['s'], but, 3, 1, False, sombre, sans_but)[0])
        self.assertEqual(preuve(v, e['s'], but, 3, 1, False, {}, lumiere, voir=True), (False, 2, 'but'))

    def test_recherche_epuisee_dans_le_noir_que_la_lumiere_reprendrait_n_est_pas_prouvee(self):
        # Chaîne réelle de ``chercher`` (mine dans le noir, Rémy sans peur ni but de lumière) avec
        # des gestes de fixture. Un geste fautif mène tout droit à x, dont les gestes lisent la
        # lumière ; un détour honnête y mène à la profondeur limite, sans les développer. Le but
        # n'a de geste qu'avec les moyens d'éclairer. Faute bon marché : x se développe, la
        # lumière se découvre, la reprise avec lumière trouve le plan. Chère : la recherche
        # sombre s'épuise sans rien lire, et le parcours du seul graphe sombre conclurait à
        # l'absence. Le certificat doit refuser, et la recherche suivante, à faute bon marché,
        # retrouver le plan.
        from donjon import caractere
        from tests.test_lampes_parts import nuit_noire
        from tests.test_tensions import recharger
        m = nuit_noire("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        m.objets["remy"]["profil"].setdefault("securite", {})["noir"] = 0
        m.objets["remy"]["profil"]["capacites"] = []
        m = recharger(m)
        cle = ("etape", "reserve")

        def gestes(v, e, vises=None, but=None):
            etape = e.fait(*cle)
            if etape is None:
                yield 1, 0.5, [p._etape("patienter")], e.apres(faits=[(cle, "x")])
                yield 0, 0.5, [p._etape("patienter")], e.apres(faits=[(cle, "a")])
                if v.emploie_lumiere:
                    yield 0, 2, [p._etape("patienter")], e.apres(faits=[(cle, "fin")])
            elif etape == "a":
                yield 0, 0.5, [p._etape("patienter")], e.apres(faits=[(cle, "b")])
            elif etape == "b":
                yield 0, 0.5, [p._etape("patienter")], e.apres(faits=[(cle, "x")])
            elif etape == "x":
                v.lumiere(e)

        prix = {"faute": 0.0}
        prix_faute = caractere.prix_faute

        def faute(monde, id, besoin=None, nom="honnetete"):
            return prix["faute"] if nom == "honnetete" else prix_faute(monde, id, besoin, nom)

        but = lambda v, e: e.fait(*cle) == "fin"
        with patch.object(p, "gestes", gestes), patch.object(caractere, "prix_faute", faute),                 patch.object(p, "VERIFIER", True), patch.object(p, "_MEMOIRE", {}),                 patch.object(p, "_GRAPHES", {}), patch.object(p, "_IMPOSSIBLES", {}),                 p.diagnostics() as recherches:
            plans = []
            # La deuxième recherche (entrées de prix différentes, même graphe) garde le graphe.
            for valeur in (0.0, 0.1, 10.0, 0.0, 10.0):
                prix["faute"] = valeur
                plans.append(p.chercher(m, "remy", but, {}, memo=["preuve"], emplois=(), profondeur=3))
            graphe_ = next(g for _, g in p._GRAPHES.values())
            depart = p.depart(m, "remy", p.Vue(m, "remy"))
            seul_sombre = p._parcours(SimpleNamespace(menacees=set()), graphe_["sombre"], depart, 3, 10, False)
        self.assertIsNotNone(plans[0])
        self.assertEqual(plans, [plans[0], plans[0], None, plans[0], None])
        self.assertEqual([r["issue"] for r in recherches], ["plan", "plan", "epuise", "plan", "epuise"])
        self.assertEqual([r["graphe"] for r in recherches], [False, False, True, True, True])
        self.assertEqual(recherches[2]["preuve_issue"], "but")
        self.assertFalse(any(r["impossible"] for r in recherches))
        # Le seul graphe sombre ne voit aucun but : sans la règle, l'absence passait pour prouvée.
        self.assertEqual(seul_sombre[::3], (True, True))
        self.assertEqual(recharger(m).data, m.data)

    def test_ordre_des_visites_conserve_les_egalites(self):
        salles = {'a': {}, 'b': {}, 'c': {}, 'd': {}}
        a = p._ordre_visites(salles, {'a': 40, 'b': 80, 'c': 80})
        self.assertEqual(a, p._ordre_visites(salles, {'a': 41, 'b': 90, 'c': 90}))
        self.assertNotEqual(a, p._ordre_visites(salles, {'a': 80, 'b': 80, 'c': 80}))

    def test_deux_sauvegardes_reelles_meme_monde_et_rendu_apres_reprise(self):
        from donjon.caractere import prix_faute
        from donjon.esprits import lire
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_planif_cout import Oublieux
        from tests.test_tensions import recharger, vivre
        dossier = Path(__file__).parent / 'data/cout-suite'
        for scenario in ('mine', 'crue'):
            meta = json.loads((dossier / f'{scenario}-7-meta.json').read_text(encoding='utf-8'))
            qui, besoin = meta['pnj'], meta['besoin']
            resultats = []
            for reprendre in (True, False):
                m = Monde.charger(dossier / f'{scenario}-7.json')
                with patch.object(p, '_GRAPHES', {}), patch.object(p, '_MEMOIRE', {}), \
                        patch.object(p, '_IMPOSSIBLES', {} if reprendre else Oublieux()), \
                        patch.object(p, 'VERIFIER', True), p.diagnostics() as recherches:
                    poids = []
                    for niveau in (70, 72, 75, 78):
                        lire(m, qui)['besoins'][besoin] = niveau
                        poids.append((prix_faute(m, qui, besoin), prix_faute(m, qui, besoin, 'douceur')))
                        self.assertIsNone(p.planifier(m, qui, besoin), scenario)
                    self.assertGreater(len(set(poids)), 1)
                    self.assertEqual(any(r['impossible'] for r in recherches), reprendre)
                    m = recharger(m)
                    m, lignes = vivre(m, 5)
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))
                resultats.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
            self.assertEqual(resultats[0], resultats[1], scenario)

    def test_les_deux_recherches_reelles_bornees_restent_identiques_apres_recharge(self):
        import gzip
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tensions import recharger, vivre
        dossier = Path(__file__).parent / 'data/cout-suite'
        for graine in (7, 42):
            meta = json.loads((dossier / f'auberge-{graine}-borne-meta.json').read_text(encoding='utf-8'))
            m = Monde(json.loads(gzip.decompress((dossier / f'auberge-{graine}-borne.json.gz').read_bytes())))
            with patch.object(p, '_MEMOIRE', {}), patch.object(p, '_GRAPHES', {}), \
                    patch.object(p, '_IMPOSSIBLES', {}), patch.object(p, 'VERIFIER', True), p.diagnostics() as recherches:
                if meta['memo'][0] == 'abri':
                    resultat = p.abri(m, meta['pnj'], meta['memo'][1])
                else:
                    resultat = p.planifier_pulsion(m, meta['pnj'], meta['memo'][1], tache=meta['memo'][2])
                self.assertIsNone(resultat, graine)
                self.assertEqual((recherches[-1]['issue'], recherches[-1]['noeuds']), ('borne', 4000))
                recharge = recharger(m)
                self.assertEqual(recharge.data, m.data)
                self.assertEqual(regarder(recharge), regarder(m))
                self.assertEqual(scene_percue(recharge), scene_percue(m))
                vecu, lignes = vivre(m, 1)
                autre, autres_lignes = vivre(recharge, 1)
            self.assertEqual(vecu.data, autre.data)
            self.assertEqual(lignes, autres_lignes)
            self.assertEqual(regarder(vecu), regarder(autre))
            self.assertEqual(scene_percue(vecu), scene_percue(autre))


class EmpreinteTests(unittest.TestCase):
    def test_positions_en_place_lumiere_portes_et_objets_ajoutes(self):
        m = creer('relais', 1985, 'fixe')
        with spatial.vue_memorisee(m), patch.object(spatial, 'VERIFICATION', 1):
            initial = spatial.etat_vue(m)
            self.assertIs(spatial.etat_vue(m), initial)
            # Corps et croyances ne changent aucune propriété que lit la vue.
            m.objets['ilse']['corps']['trempe'] += 1
            self.assertIs(spatial.etat_vue(m), initial)
            m.objets['ilse']['position'][0] += 1
            suivant = spatial.etat_vue(m)
            self.assertNotEqual(suivant, initial)
            m.objets['fanal'].update(allume=True, combustible=1)
            allume = spatial.etat_vue(m)
            m.objets['fanal']['combustible'] = 0
            self.assertNotEqual(spatial.etat_vue(m), allume)
            copie = dict(m.objets['fanal'], id='copie_fanal')
            m.objets['copie_fanal'] = copie
            avec = spatial.etat_vue(m)
            del m.objets['copie_fanal']
            self.assertNotEqual(spatial.etat_vue(m), avec)
            m.joueur['position'][0] += 1
            self.assertEqual(spatial.etat_vue(m), spatial._etat_vue_brut(m))
            avant = spatial.etat_vue(m)
            m.objets['ilse'] = m.objets.pop('ilse')
            self.assertNotEqual(spatial.etat_vue(m), avant)

    def test_donnees_composees_et_ordre_de_leurs_cles(self):
        m = creer('relais')
        m.objets['fanal']['installation'] = {'x': [1, 2], 'y': {'z': True}}
        with spatial.vue_memorisee(m), patch.object(spatial, 'VERIFICATION', 1):
            avant = spatial.etat_vue(m)
            m.objets['fanal']['installation']['x'][0] = 2
            apres = spatial.etat_vue(m)
            self.assertNotEqual(avant, apres)
            inst = m.objets['fanal']['installation']
            inst['x'] = inst.pop('x')
            self.assertNotEqual(apres, spatial.etat_vue(m))

    def test_perception_mutations_et_recharge(self):
        from tests.test_tensions import recharger
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        for scenario, acteur in (('relais', 'brune'), ('mine', 'remy')):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985)
                with spatial.vue_memorisee(m), patch.object(spatial, 'VERIFICATION', 1):
                    percus(m, acteur)
                    m.objets[acteur]['orientation'] = 'sud'
                    attendu = percus(m, acteur)
                    with spatial.sans_memoire(m):
                        self.assertEqual(percus(m, acteur), attendu)
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))
