"""Lot 66 : une recherche épuisée sans plan, dont seuls des prix ont changé depuis, ne se refait
pas ; le certificat d'absence (``planification._sans_plan``) se complète quand la recherche
s'épuise, et ne conclut jamais là où un autre prix trouverait un plan."""
from types import SimpleNamespace
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.caractere import prix_faute
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger


def capture(scenario):
    chemin = Path(__file__).parent / f"data/cout-12h/{scenario}-1985-480.json.gz"
    return recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))


def caches_vides():
    return (patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}),
            patch.object(p, "_IMPOSSIBLES", {}))


class CapturesTests(unittest.TestCase):
    # Rémy (le cas réel du lot 63) et Odon, autre affamé de la même mine, sans plan pour sa faim.
    CAS = (("mine", "remy"), ("mine", "odon"))

    def recherches(self, d, qui):
        return [x for x in d if x["pnj"] == qui and x["but"] == "faim"]

    def test_seul_le_prix_d_abimer_change_reprise_par_certificat_meme_resultat(self):
        for scenario, qui in self.CAS:
            with self.subTest(qui=qui):
                m = capture(scenario)
                a, b, c = caches_vides()
                with a, b, c, patch.object(p, "VERIFIER", True), p.diagnostics() as d:
                    self.assertIsNone(p.planifier(m, qui, "faim"))
                    premiere = self.recherches(d, qui)[-1]
                    # Épuisée dès la première recherche sur ces entrées : le certificat est complété.
                    self.assertEqual((premiere["issue"], premiere["preuve_issue"]), ("epuise", "epuise"))
                    prix = prix_faute(m, qui, "faim"), prix_faute(m, qui, "faim", "douceur")
                    # La faim monte d'un point, puis le monde est rechargé : des prix changent (celui
                    # d'abîmer pour Rémy), aucune permission.
                    lire(m, qui)["besoins"]["faim"] += 1
                    m = recharger(m)
                    nouveaux = prix_faute(m, qui, "faim"), prix_faute(m, qui, "faim", "douceur")
                    self.assertNotEqual(nouveaux, prix)
                    self.assertEqual([x is None for x in nouveaux], [x is None for x in prix])
                    if qui == "remy":
                        self.assertEqual((prix[0], nouveaux[0]), (None, None))
                    self.assertIsNone(p.planifier(m, qui, "faim"))   # VERIFIER : la recherche complète aussi
                    seconde = self.recherches(d, qui)[-1]
                    self.assertTrue(seconde["impossible"])
                    self.assertTrue(seconde["memoire"])
                    self.assertEqual(seconde["noeuds"], 0)

    def test_une_faute_devenue_permise_fait_refaire_la_recherche(self):
        m = capture("mine")
        qui = "remy"
        self.assertIsNone(prix_faute(m, qui, "faim"))
        a, b, c = caches_vides()
        with a, b, c, patch.object(p, "VERIFIER", True), p.diagnostics() as d:
            self.assertIsNone(p.planifier(m, qui, "faim"))
            self.assertEqual(self.recherches(d, qui)[-1]["preuve_issue"], "epuise")
            # Son honnêteté fléchit : voler devient envisageable, la preuve d'avant ne vaut plus.
            m.objets[qui]["profil"]["valeurs"]["honnetete"] = 40
            m = recharger(m)
            self.assertIsNotNone(prix_faute(m, qui, "faim"))
            p.planifier(m, qui, "faim")
            refaite = self.recherches(d, qui)[-1]
            self.assertFalse(refaite["impossible"])
            self.assertFalse(refaite["memoire"])
            self.assertGreater(refaite["noeuds"], 0)

    def test_cinq_minutes_meme_monde_et_rendu_avec_ou_sans_certificat(self):
        # La chaîne entière : moteur, délibération, sauvegarde et rendu, rechargés, identiques que
        # les recherches soient reprises par certificat ou refaites.
        for scenario in ("mine",):
            resultats, reprises = [], []
            for certificat in (True, False):
                m = capture(scenario)
                a, b, c = caches_vides()
                sans = patch.object(p, "_sans_plan", lambda *x, **k: (False, 0, "lacune"))
                with a, b, c, (patch.object(p, "VERIFIER", True) if certificat else sans), p.diagnostics() as d:
                    moteur = Moteur(m)
                    lignes = moteur.executer(moteur.preparer(proposition("attendre")))
                reprises.append(sum(bool(x["impossible"]) for x in d))
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                resultats.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
            self.assertEqual(resultats[0], resultats[1], scenario)
            self.assertGreater(reprises[0], 0, scenario)
            self.assertEqual(reprises[1], 0, scenario)


class CompletionTests(unittest.TestCase):
    """Graphes de synthèse : ce que la complétion développe et ce qu'elle refuse de prouver."""

    def vue(self, **k):
        return SimpleNamespace(**{"degat": 0, "menacees": set(), "peur": True, "eclairer": False,
                                  "_lumiere_lue": False, "_explore_furtif": False, "_discretion_lue": False,
                                  "_agissables": {}, "_devis_differes": 0, "_devis_developpes": 0, **k})

    def test_une_suite_differee_qui_mene_au_but_n_est_jamais_certifiee_vide(self):
        # Le chemin bon marché atteint x à la profondeur limite, sans le développer ; à un autre prix
        # de faute, le chemin court l'atteint plus tôt, et sa suite différée donne un résultat.
        etats = {s: p.Etat(s, (), {}) for s in "sabx"}
        fin = etats["x"].apres(faits=[(("estimation",), True)])
        arcs = {"s": [("a", 0), ("x", 1)], "a": [("b", 0)], "b": [("x", 0)]}
        def terminal(v):
            yield 0, 5, [p._etape("demander", "tiers")], fin, 0, False
        def suites(v, e, vises, but):
            if e.salle == "x":
                return [p.SuiteDifferee(5, terminal, ())]
            return [(faute, 1, [], etats[t], 0, False, 0) for t, faute in arcs.get(e.salle, [])]
        but = lambda v, e: False
        for differer in (True, False):
            with self.subTest(differer=differer), patch.object(p, "_suites", suites):
                v = self.vue()
                graphe = {"lumiere": {}}
                cher = p._explorer_etats(v, etats["s"], but, {}, 3, 100, 10, graphe=graphe["lumiere"],
                                         differer=differer)
                self.assertIsNone(cher[0])
                # Le graphe gardé a un trou en x : sans complétion, une lacune ; avec, le but.
                self.assertEqual(p._sans_plan(v, etats["s"], but, 3, 10, False, graphe, True)[2], "lacune")
                self.assertEqual(p._sans_plan(v, etats["s"], but, 3, 10, False, graphe, True, {},
                                              completer=True)[::2], (False, "but"))
                # Et en effet : à un autre prix, la recherche trouve ce plan.
                self.assertIsNotNone(p._explorer_etats(self.vue(), etats["s"], but, {}, 3, 100, 0,
                                                       differer=differer)[0])
                # Le graphe gardé n'a pas été modifié par la complétion : x reste non développé.
                self.assertIsNone(graphe["lumiere"][etats["x"]][3])

    def test_suite_differee_vide_et_trou_developpe_prouvent_l_absence(self):
        etats = {s: p.Etat(s, (), {}) for s in "sabx"}
        arcs = {"s": [("a", 0), ("x", 1)], "a": [("b", 0)], "b": [("x", 0)], "x": []}
        def suites(v, e, vises, but):
            vides = [p.SuiteDifferee(5, lambda v: iter(()), ())] if e.salle == "x" else []
            return vides + [(faute, 1, [], etats[t], 0, False, 0) for t, faute in arcs.get(e.salle, [])]
        but = lambda v, e: False
        with patch.object(p, "_suites", suites):
            v = self.vue()
            graphe = {"lumiere": {}}
            self.assertIsNone(p._explorer_etats(v, etats["s"], but, {}, 3, 100, 10, graphe=graphe["lumiere"])[0])
            self.assertEqual(p._sans_plan(v, etats["s"], but, 3, 10, False, graphe, True)[2], "lacune")
            self.assertEqual(p._sans_plan(v, etats["s"], but, 3, 10, False, graphe, True, {}, completer=True),
                             (True, 4, "epuise"))
            # La faute interdite, l'arête coûteuse disparaît : x n'est atteint qu'à la limite.
            self.assertTrue(p._sans_plan(v, etats["s"], but, 3, None, False, graphe, True, {}, completer=True)[0])

    def test_lumiere_lue_en_completant_renvoie_au_graphe_lumiere(self):
        # Sans peur du noir : le graphe sombre se complète ; un état dont les gestes lisent la lumière
        # n'y est pas suivi, et c'est le graphe lumière, développé avec les moyens d'éclairer, qui décide.
        etats = {s: p.Etat(s, (), {}) for s in "slf"}
        def suites(v, e, vises, but):
            if e.salle == "s":
                return [(0, 1, [], etats["l"], 0, False, 0)]
            if e.salle == "l":
                v._lumiere_lue = True   # une lecture commune de lumière
                return [(0, 1, [], etats["f"], 0, False, 0)] if v._lumiere_lue else []
            return []
        but = lambda v, e: e.salle == "f" and v.emploie
        for avec_but in (True, False):
            with self.subTest(avec_but=avec_but), patch.object(p, "_suites", suites):
                v = self.vue(peur=False)
                v.emploie = avec_but
                graphe = {"sombre": {}, "lumiere": {}}
                prouve, _, issue = p._sans_plan(v, etats["s"], but, 3, 10, False, graphe, False, {}, completer=True)
                self.assertEqual((prouve, issue), (not avec_but, "epuise" if not avec_but else "but"))
                self.assertFalse(v._lumiere_lue)   # la vue rendue dans son mode

    def test_discretion_decouverte_reprend_a_pas_feutres(self):
        # Hors allure feutrée, un geste discret possible n'est pas offert ; la complétion qui le
        # découvre reprend avec les deux allures, comme la recherche, et y trouve le but.
        depart = p.Etat("s", (), {})
        def suites(v, e, vises, but):
            if e.salle == "s" and not e.fait("furtif"):
                v._discretion_lue = True
                if e.allure == 30:
                    return [(0, 1, [], e.apres(salle="f", faits=[(("furtif",), True)]), 0, False, 0)]
            return []
        but = lambda v, e: e.salle == "f"
        with patch.object(p, "_suites", suites):
            v = self.vue(_cru_spatial={})
            prouve, _, issue = p._sans_plan(v, depart, but, 3, 10, False, {"lumiere": {}}, True, {},
                                            completer=True)
            self.assertEqual((prouve, issue), (False, "but"))
            self.assertFalse(v._explore_furtif)


if __name__ == "__main__":
    unittest.main()
