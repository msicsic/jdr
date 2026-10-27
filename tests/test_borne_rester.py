"""Séjour final minoré : mêmes plans, égalités, monde et rendu après recharge."""
from contextlib import ExitStack
import gzip
import itertools
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger


class BorneResterTests(unittest.TestCase):
    def test_plancher_relaxe_les_passages_et_ne_lit_ni_noir_ni_compagnie(self):
        v = p.Vue.__new__(p.Vue)
        v.salles = {
            "a": {"sorties": {"nord": {"vers": "b", "porte": "verrou"}}},
            "b": {"sorties": {}}, "isolee": {"sorties": {}}}
        v.prix_gardes, v.eau, v._bornes_rester = {"a": 2, "b": 3, "isolee": 10}, {"a": 2}, {}
        # Une serrure peut être défaite par le plan ; l'exclure surestimerait H.
        self.assertEqual(v.borne_rester("a"), p.RESTER * 12)
        self.assertEqual(v.borne_rester("b"), p.RESTER * 12)
        self.assertEqual(v.borne_rester("inconnue"), 0)
        v.prix_gardes, v.eau = {}, {}
        v._bornes_rester.clear()
        self.assertEqual(v.borne_rester("a"), 0)

    def comparer_capture(self, scenario, qui, action):
        chemin = Path(__file__).parent / f"data/cout-12h/{scenario}-1985-480.json.gz"
        original = Monde(json.loads(gzip.decompress(chemin.read_bytes())))
        resultats, comptes = [], []
        for borner in (False, True):
            monde = recharger(original)
            with ExitStack() as pile:
                if not borner:
                    pile.enter_context(patch.object(p.Vue, "borne_rester", return_value=0))
                for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                    pile.enter_context(patch.object(p, nom, {}))
                # Le contrôle exhaustif à 60 000 nœuds n'est pas le témoin de
                # cette comparaison : ici, le témoin est la recherche sans H.
                pile.enter_context(patch.object(p, "VERIFIER", False))
                with p.diagnostics() as recherches:
                    plan = action(monde, qui)
                comptes.append(recherches[0]["noeuds"])
                moteur = Moteur(monde)
                lignes = moteur.executer(moteur.preparer(proposition("attendre")))
            recharge = recharger(monde)
            self.assertEqual(monde.data, recharge.data)
            self.assertEqual(regarder(monde), regarder(recharge))
            self.assertEqual(scene_percue(monde), scene_percue(recharge))
            resultats.append((plan, recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
        self.assertEqual(resultats[0], resultats[1])
        return comptes

    def test_lucien_reel_moins_d_etats_meme_monde_et_rendu(self):
        sans, avec = self.comparer_capture("auberge", "lucien", lambda m, q: p.garder(m, q, "etable"))
        self.assertLess(avec, sans)

    def test_lumiere_mine_meme_monde_et_rendu_quand_le_plancher_est_nul(self):
        sans, avec = self.comparer_capture("mine", "bram", p.eclairer)
        self.assertEqual(avec, sans)

    def test_reference_bornee_le_nouveau_plan_egale_la_complete_et_est_signale(self):
        chemin = Path(__file__).parent / "data/borne-rester/auberge-42-559.json.gz"
        m = recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))
        but = lambda v, e: e.salle == "grenier"
        with patch.object(p.Vue, "borne_rester", return_value=0), p.diagnostics() as recherches:
            ancien = p.chercher(m, "lucien", but, emplois=(), motif="biens", tenir=True)
            complet = p.chercher(m, "lucien", but, emplois=None, motif="biens", tenir=True, noeuds=p.REFERENCE)
        # Avant le lot 46, la recherche sans borne atteignait ici son plafond
        # (la seconde lanterne doublait les états) ; depuis, elle trouve le
        # plan de la recherche complète sous le plafond. La borne doit rendre
        # ce même plan, en moins d'états.
        self.assertIsNotNone(complet)
        self.assertEqual(ancien, complet)
        sans_borne = recherches[0]["noeuds"]
        with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                patch.object(p, "_IMPOSSIBLES", {}), patch.object(p, "BORNES", []), \
                patch.object(p, "VERIFIER", True), p.diagnostics() as recherches:
            nouveau = p.chercher(m, "lucien", but, emplois=(), motif="biens", tenir=True, nom="garder:grenier")
            self.assertEqual(nouveau, complet)
            # La localisation inconnue d'un personnage ne crée plus de prix
            # de compagnie/garde : sur cette capture, la borne peut être nulle.
            # Le gain strict est éprouvé par test_lucien_reel_moins_d_etats ;
            # ici restent l'absence de surcoût et l'identité du plan complet.
            self.assertLessEqual(recherches[0]["noeuds"], sans_borne)
        # Le plan a des conséquences réelles, persistées ; le joueur au
        # dortoir ne voit pas ces gestes cachés. Chacun des deux mondes reste
        # intégralement identique à lui-même après sauvegarde/rechargement.
        mondes = []
        for borner in (False, True):
            monde = recharger(m)
            with ExitStack() as pile:
                if not borner:
                    pile.enter_context(patch.object(p.Vue, "borne_rester", return_value=0))
                for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                    pile.enter_context(patch.object(p, nom, {}))
                pile.enter_context(patch.object(p, "VERIFIER", False))
                moteur = Moteur(monde)
                lignes = moteur.executer(moteur.preparer(proposition("attendre")))
            recharge = recharger(monde)
            self.assertEqual(monde.data, recharge.data)
            self.assertEqual(regarder(monde), regarder(recharge))
            self.assertEqual(scene_percue(monde), scene_percue(recharge))
            mondes.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
        # Depuis le lot 46, avec ou sans borne, Lucien prend la décision de la
        # recherche complète : les deux mondes sont identiques.
        self.assertEqual(mondes[0], mondes[1])

    def test_graphes_repris_aux_prix_variables_meme_resultat_que_sans_borne(self):
        chemin = Path(__file__).parent / "data/cout-12h/auberge-1985-480.json.gz"
        m = recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))
        graphe = {}
        for faute in (0, 20, 50, None):
            resultats = []
            for borner in (True, False):
                with ExitStack() as pile:
                    if not borner:
                        pile.enter_context(patch.object(p.Vue, "borne_rester", return_value=0))
                    v = p.Vue(m, "lucien")
                    v.emplois, v.degat = frozenset(), 20
                    e = p.depart(m, "lucien", v)
                    r = p._explorer(v, e, lambda v, e: e.salle == "etable", {}, 8, p.NOEUDS,
                                    faute, tenir=True, graphe=graphe if borner else None)
                    resultats.append(r[0])
            self.assertEqual(*resultats)

    def test_egalites_avec_suites_differees_et_resultats_ordinaires(self):
        e = p.Etat("s", (), {})
        a, b = (e.apres(faits=[(("but",), q)]) for q in ("a", "b"))
        fin = e.apres(faits=[(("estimation",), True)])
        for ordre in itertools.permutations(("a", "b", "devis")):
            resultats = []
            for borne, differer in itertools.product((0, 3), (False, True)):
                v = SimpleNamespace(degat=0, menacees=set(), _devis_developpes=0, _devis_differes=0,
                                    borne_rester=lambda s: borne, pression=lambda e: 3 / p.RESTER)
                def terminal(v):
                    yield 0, 1, [p._etape("devis")], fin, 0, False
                def suites(v, courant, vises, but):
                    if courant != e:
                        return []
                    options = {"a": (0, 1, [p._etape("a")], a, 0, False, 0),
                               "b": (0, 1, [p._etape("b")], b, 0, False, 0),
                               "devis": p.SuiteDifferee(1, terminal, ())}
                    return [options[q] for q in ordre]
                with patch.object(p, "_suites", suites):
                    r = p._explorer_etats(v, e, lambda v, e: bool(e.fait("but")), {}, 8, 20, 0,
                                          tenir=True, differer=differer)
                resultats.append(r[0])
            self.assertTrue(all(r == resultats[0] for r in resultats))
            self.assertEqual(resultats[0][0], 4)

    def test_decouverte_sans_borne_et_certificat_independant_des_couts(self):
        e = p.Etat("s", (), {})
        autre = e.apres(faits=[(("prepare",), True)])
        v = SimpleNamespace(degat=0, menacees=set(), _lumiere_lue=False,
                            borne_rester=lambda s: self.fail("La découverte doit rester sans borne"))
        def suites(v, courant, vises, but):
            return [(0, 1, [], autre, 0, False, 0)] if courant == e else []
        graphe = {}
        with patch.object(p, "_suites", suites):
            r = p._explorer_etats(v, e, lambda v, e: False, {}, 8, 20, 0,
                                  tenir=True, graphe=graphe, decouvrir=True)
        self.assertIsNone(r[0])
        self.assertEqual(p._sans_plan(v, e, None, 8, 0, True, {"sombre": graphe}, False),
                         (True, 2, "epuise"))
        v.borne_rester = lambda s: 3
        graphe_borne = {}
        with patch.object(p, "_suites", suites):
            borne = p._explorer_etats(v, e, lambda v, e: False, {}, 8, 20, 0,
                                      tenir=True, graphe=graphe_borne)
        self.assertEqual(borne, r)
        self.assertEqual(p._sans_plan(v, e, None, 8, 0, True, {"sombre": graphe_borne}, False),
                         (True, 2, "epuise"))
        # Une suite encore inconnue ne devient jamais une preuve vide.
        graphe[autre][3] = [p.SuiteDifferee(1, lambda v: iter(()), ())]
        self.assertEqual(p._parcours(v, graphe, e, 8, 0, True)[2], "lacune")

    def test_ajouter_le_plancher_ne_confond_pas_deux_couts_flottants(self):
        e = p.Etat("s", (), {})
        a, b = (e.apres(faits=[(("but",), q)]) for q in ("a", "b"))
        resultats = []
        for borne in (0, 1e16):
            v = SimpleNamespace(degat=0, menacees=set(), borne_rester=lambda s: borne,
                                pression=lambda e: 1e16 / p.RESTER)
            def suites(v, courant, vises, but):
                return ([(0, 1, [p._etape("a")], a, 0, False, 0),
                         (0, .5, [p._etape("b")], b, 0, False, 0)] if courant == e else [])
            with patch.object(p, "_suites", suites):
                r = p._explorer_etats(v, e, lambda v, e: bool(e.fait("but")), {}, 8, 20, 0, tenir=True)
            resultats.append(r[0])
        self.assertEqual(*resultats)
        self.assertEqual(resultats[0][1][0]["operation"], "b")


if __name__ == "__main__":
    unittest.main()
