"""Calcul des suites terminales, rang des égalités et état persistant."""
from types import SimpleNamespace
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, pnj, part_estimee
from donjon.esprits import croire
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from tests import test_lampes_buts as lampes
from tests.test_tensions import recharger


class BorneTests(unittest.TestCase):
    def test_attente_part_reemploie_exactement_les_etats_equivalents(self):
        m = lampes.LumiereDuButTests().scene("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        v = p.Vue(recharger(m), "remy")
        e = p.depart(v.monde, "remy", v)
        with patch.object(v, "_attente_part", wraps=v._attente_part) as calcul:
            a = v.attente_part(e, "gaspard", "bidon_huile", e.salle)
            # Les droits et les effets du but ne changent pas le trajet du donneur.
            autre = e.apres(faits=[(("inspecte", "reserve"), True), (("depense",), 1)])
            self.assertEqual(a, v.attente_part(autre, "gaspard", "bidon_huile", e.salle))
            self.assertEqual(calcul.call_count, 1)
            # Le lieu du donneur, en revanche, doit invalider la lecture.
            autre = e.apres(faits=[(("lieu", "gaspard"), "bureau")])
            v.attente_part(autre, "gaspard", "bidon_huile", e.salle)
            self.assertEqual(calcul.call_count, 2)
        v.eclairer = True
        besoins = v.sources_a_charger(e, {})
        self.assertIn("lampe_remy", besoins)
        self.assertIs(besoins, v.sources_a_charger(e.apres(faits=[(("inspecte", "reserve"), True)]), {}))
        plein = e.apres(faits=[(("charge", "lampe_remy"), True)])
        self.assertNotIn("lampe_remy", v.sources_a_charger(plein, {}))

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
                resultats, devis, etats_devis, mondes = [], [], [], []
                explorer = p._explorer
                trajets = part_estimee._trajets
                for differe in (True, False):
                    monde = recharger(m)
                    visites = 0
                    def chercher(*a, **k):
                        return explorer(*a, **k, differer=differe)
                    def suivre(*a, **k):
                        nonlocal visites
                        for etat in trajets(*a, **k):
                            visites += 1
                            yield etat
                    with patch.object(p, "_explorer", chercher), \
                            patch.object(part_estimee, "_trajets", suivre), p.diagnostics() as recherches:
                        r = p.chercher(monde, qui, p.eclaire, {"eclairer": True}, emplois=())
                    self.assertIsNotNone(r)
                    resultats.append(r)
                    devis.append(recherches[-1]["devis_developpes"])
                    etats_devis.append(visites)
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
                self.assertLess(etats_devis[0], etats_devis[1])
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

    def test_suite_differee_respecte_les_memes_filtres_que_les_gestes_immediats(self):
        e = p.Etat("s", (), {})
        fin = e.apres(faits=[(("estimation",), True)])
        def terminal(v):
            yield 0, 5, [p._etape("demander", "tiers")], fin, 0, False
        v = SimpleNamespace(seul="commanditaire", _devis_developpes=0)
        s = p.SuiteDifferee(3, terminal, (), depuis=e, vises={}, but=lambda v, e: True)
        self.assertEqual(s.developper(v), [])

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
        # Cas du présent lot : les deux vraies nuits qui ont fourni le profil,
        # rechargées à 8 h puis vécues par la chaîne moteur/rendu/sauvegarde.
        explorer = p._explorer
        for scenario in ("mine", "auberge"):
            chemin = Path(__file__).parent / f"data/cout-12h/{scenario}-1985-480.json.gz"
            resultats = []
            for differe in (True, False):
                m = recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))
                def chercher(*a, **k):
                    return explorer(*a, **k, differer=differe)
                with patch.object(p, "_explorer", chercher), patch.object(p, "_MEMOIRE", {}), \
                        patch.object(p, "_GRAPHES", {}), patch.object(p, "_IMPOSSIBLES", {}), \
                        patch.object(p, "VERIFIER", False):
                    moteur = Moteur(m)
                    lignes = moteur.executer(moteur.preparer(proposition("attendre")))
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))
                resultats.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
            self.assertEqual(resultats[0], resultats[1], scenario)
