"""Calcul des suites terminales, rang des égalités et état persistant."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from donjon import planification as p, pnj
from donjon.esprits import croire
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_lampes_buts as lampes
from tests.test_tensions import recharger


class BorneTests(unittest.TestCase):
    def test_la_borne_evite_des_etats_de_devis_meme_plan_et_monde_recharge(self):
        for scenario, qui, donneur, source, lot, salle, arrivee in (
            ("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve", "bureau"),
            ("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable", "salle_commune"),
        ):
            with self.subTest(scenario=scenario):
                m = lampes.LumiereDuButTests().scene(scenario, qui, donneur, source, lot, salle)
                m.data["salles"][arrivee]["lumiere_naturelle"] = 2
                croire(m, qui, arrivee, "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "savoir")
                for k, x in m.objets.items():
                    if x["type"] == "porte":
                        x["verrouillee"] = False
                        croire(m, qui, k, "verrouillee", False, "savoir")
                m = recharger(m)
                resultats, devis, mondes = [], [], []
                explorer = p._explorer
                for differe in (True, False):
                    monde = recharger(m)
                    def chercher(*a, **k):
                        return explorer(*a, **k, differer=differe)
                    with patch.object(p, "_explorer", chercher), p.diagnostics() as recherches:
                        r = p.chercher(monde, qui, p.eclaire, {"eclairer": True}, emplois=())
                    self.assertIsNotNone(r)
                    resultats.append(r)
                    devis.append(recherches[-1]["devis_developpes"])
                    self.assertTrue(all(x["operation"] == "aller" for x in r[1]))
                    for etape in r[1]:
                        for _ in range(100):
                            if pnj._executer(monde, qui, etape, [], []):
                                break
                        else:
                            self.fail("Le trajet n'aboutit pas")
                        monde = recharger(monde)
                    recharge = recharger(monde)
                    self.assertEqual(monde.data, recharge.data)
                    self.assertEqual(regarder(monde), regarder(recharge))
                    self.assertEqual(scene_percue(monde), scene_percue(recharge))
                    self.assertFalse(monde.objets[source]["allume"])
                    self.assertEqual(monde.objets[lot]["charges"], 3)
                    mondes.append((recharge.data, regarder(recharge), scene_percue(recharge)))
                self.assertEqual(resultats[0], resultats[1])
                self.assertLess(devis[0], devis[1])
                self.assertEqual(mondes[0], mondes[1])

    def test_egalite_et_plafond_conservent_l_ordre_de_la_file_historique(self):
        e = p.Etat("s", (), {})
        fin = e.apres(faits=[(("estimation",), True)])
        def terminal(v):
            yield 0, 5, [p._etape("premier")], fin, 0, False
        def suites(v, etat, vises, but):
            return [p.SuiteDifferee(3, terminal, ()),
                    (0, 5, [p._etape("second")], fin, 0, False, 0)]
        for noeuds in (1, 2, 10):
            resultats = []
            for differe in (True, False):
                v = SimpleNamespace(degat=0, menacees=set(), _devis_developpes=0, _devis_differes=0)
                with patch.object(p, "_suites", suites):
                    r = p._explorer_etats(v, e, lambda v, e: False, {}, 8, noeuds, 0, differer=differe)
                resultats.append(r)
            self.assertEqual(resultats[0], resultats[1])
            if noeuds > 1:
                self.assertEqual(resultats[0][0][1][0]["operation"], "premier")

    def test_certificat_non_developpe_reste_inconnu_et_absence_prouvee_apres_recharge(self):
        # Le parcours de preuve n'évalue jamais un devis manquant.
        e = p.Etat("s", (), {})
        v = SimpleNamespace(degat=0, menacees=set())
        differe = p.SuiteDifferee(3, lambda v: iter(()), ())
        graphe = {e: [False, None, 0, [differe], False]}
        self.assertEqual(p._parcours(v, graphe, e, 8, 0, False)[2], "lacune")
        differe.suites = []
        self.assertTrue(p._parcours(v, graphe, e, 8, 0, False)[0])
        # Les deux sauvegardes réelles d'absence passent déjà les prix variables,
        # la reprise du certificat et le rendu après cinq minutes rechargées.
        from tests.test_cout_suite import AbsenceTests
        AbsenceTests().test_deux_sauvegardes_reelles_meme_monde_et_rendu_apres_reprise()
