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
        [(faute, duree, [], etats[t], 0, False, 0) for t, faute, duree in suites]]
        for s, suites in arcs.items()}
    return etats, noeuds


class AbsenceTests(unittest.TestCase):
    def test_cout_change_ne_suffit_pas_a_prouver_une_absence(self):
        # Un chemin peu cher mais long atteint x à la profondeur limite ; un autre prix
        # fait arriver par le chemin court et permet d'atteindre le but. Aucun cache de
        # résultat vide ne doit assimiler une exploration pondérée à un certificat.
        e, g = graphe({'s': [('a', 0, 1), ('x', 1, 1)], 'a': [('b', 0, 1)],
                      'b': [('x', 0, 1)], 'x': [('fin', 0, 1)], 'fin': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: x.salle == 'fin'
        self.assertIsNone(p._explorer(v, e['s'], but, {}, 3, 100, 10, graphe=g.copy())[0])
        self.assertIsNotNone(p._explorer(v, e['s'], but, {}, 3, 100, 0, graphe=g.copy())[0])
        self.assertFalse(p._sans_plan(v, e['s'], but, {}, 3, 10, False, g.copy())[0])

    def test_borne_ou_but_ne_sont_jamais_une_preuve_d_absence(self):
        e, g = graphe({'s': [('a', 0, 1)], 'a': [('fin', 0, 1)], 'fin': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: x.salle == 'fin'
        with patch.object(p, 'PREUVE_MAX', 1):
            self.assertEqual(p._sans_plan(v, e['s'], but, {}, 3, 1, False, g), (False, 1, 'borne'))
        self.assertFalse(p._sans_plan(v, e['s'], but, {}, 3, 1, False, g)[0])
        self.assertTrue(p._sans_plan(v, e['s'], but, {}, 1, 1, False, g)[0])

    def test_retirer_un_etat_domine_change_la_recherche_bornee(self):
        # Même salle et mêmes moyens, mais un chemin a coûté plus et dépensé une pièce.
        # Le retirer conserve l'optimum illimité, tout en changeant la réponse à cinq nœuds.
        s, fin = Etat('s', (), {}), Etat('fin', (), {})
        riches = [Etat(salle, (), {}) for salle in ('a', 'b', 'c')]
        pauvres = [Etat(salle, (), {('depense',): 1}) for salle in ('a', 'b', 'c')]
        g = {e: [e == fin, None, 0, []] for e in [s, fin, *riches, *pauvres]}
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
        complet = p._explorer(v, s, but, {}, 8, 50, 0, graphe=g)[0]
        self.assertEqual(complet[0], 10)
        self.assertIsNone(p._explorer(v, s, but, {}, 8, 5, 0, graphe=g)[0])
        reduit = {**g, s: [False, None, 0, g[s][3][:1]]}
        self.assertEqual(p._explorer(v, s, but, {}, 8, 5, 0, graphe=reduit)[0], complet)

    def test_permission_et_profondeur_entrent_dans_la_preuve(self):
        e, g = graphe({'s': [('a', 1, 1)], 'a': [('fin', 0, 1)], 'fin': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: x.salle == 'fin'
        self.assertTrue(p._sans_plan(v, e['s'], but, {}, 3, None, False, g)[0])
        self.assertFalse(p._sans_plan(v, e['s'], but, {}, 3, 1, False, g)[0])

    def test_un_graphe_incomplet_ne_prouve_rien_et_n_est_pas_developpe(self):
        e, g = graphe({'s': [('a', 0, 1)], 'a': []}, 'fin')
        v = SimpleNamespace(degat=0, menacees=set())
        but = lambda v, x: False
        g[e['a']][3] = None
        with patch.object(p, '_suites', side_effect=AssertionError('développement supplémentaire')):
            self.assertEqual(p._sans_plan(v, e['s'], but, {}, 3, 1, False, g), (False, 2, 'lacune'))
            del g[e['a']]
            self.assertEqual(p._sans_plan(v, e['s'], but, {}, 3, 1, False, g), (False, 2, 'lacune'))

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
