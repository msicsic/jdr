"""P3 : mesure sans effet et contre-exemple à la domination du trajet direct."""
from contextlib import ExitStack, nullcontext
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, pnj
from donjon.esprits import croire
from donjon.monde import Monde
from donjon.obstacles import cout_route
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import placer, recharger
from tests.test_trajets_reels import flammes, executer_plan
from tools.mesurer_salles_interet import instrumenter


def losange(largeur):
    m, qui, _, _ = flammes("relais")
    for s, w, xy in [("a", 3, [50, 50]), ("b", 3, [60, 50]),
                      ("c", largeur, [50, 60]), ("d", 3, [60, 60])]:
        m.data["salles"][s] = {"nom": s, "lumiere_naturelle": 0 if s == "b" else 2, "fenetres": 0,
                                 "plan": {"origine": xy, "sol": ["." * w] * 3}, "sorties": {}}
        croire(m, qui, s, "etat", {"eclairee": s != "b", "niveau": 0 if s == "b" else 2,
                                    "propre": 0 if s == "b" else 2}, "savoir")
    for s, direction, t, case in [
        ("a", "est", "b", [3, 1]), ("a", "sud", "c", [1, 3]),
        ("b", "ouest", "a", [-1, 1]), ("b", "sud", "d", [1, 3]),
        ("c", "nord", "a", [1, -1]), ("c", "est", "d", [largeur, 1]),
        ("d", "nord", "b", [1, -1]), ("d", "ouest", "c", [-1, 1]),
    ]:
        m.data["salles"][s]["sorties"][direction] = {"vers": t, "case": case, "escalier": True, "porte": None}
    m.objets[qui]["profil"].setdefault("securite", {})["noir"] = 1
    placer(m, qui, "a", (1, 1))
    m.joueur.update(salle="d", position=[2, 1], orientation="ouest")
    return recharger(m), qui


class DiagnosticSallesTests(unittest.TestCase):
    def test_instrumentation_identique_sur_deux_captures_apres_recharge(self):
        for scenario in ("mine", "auberge"):
            with self.subTest(scenario=scenario):
                original = Monde(json.loads(gzip.decompress((Path(__file__).parent /
                    f"data/cout-12h/{scenario}-1985-480.json.gz").read_bytes())))
                resultats, passes = [], []
                for mesurer in (False, True):
                    m = recharger(original)
                    with ExitStack() as pile:
                        for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                            pile.enter_context(patch.object(p, nom, {}))
                        pile.enter_context(instrumenter(lambda l: passes.append(l["examines"]))
                                           if mesurer else nullcontext())
                        with p.diagnostics() as recherches:
                            lignes = []
                            pnj.avancer(m, 1, lignes)
                    for r in recherches:
                        r.pop("duree")
                    recharge = recharger(m)
                    self.assertEqual(m.data, recharge.data)
                    self.assertEqual(regarder(m), regarder(recharge))
                    self.assertEqual(scene_percue(m), scene_percue(recharge))
                    resultats.append((recharge.data, lignes, regarder(recharge), recherches))
                self.assertEqual(*resultats)
                self.assertTrue(passes)

    def test_un_arret_sans_action_peut_reduire_le_cout_avec_la_pression(self):
        for largeur in (5, 9):
            with self.subTest(largeur=largeur):
                m, qui = losange(largeur)
                v = p.Vue(m, qui)
                e = p.depart(m, qui, v)
                direct, premier = v.route(e, "d"), v.route(e, "c")
                intermediaire = v.arrivee(e, "c", premier)
                second = v.route(intermediaire, "d")
                self.assertEqual([x["vers"] for x in direct], ["b", "d"])
                self.assertFalse(any(o.get("lieu") == "c" for o in m.objets.values()))
                duree_directe = cout_route(direct)
                duree_detour = cout_route(premier) + cout_route(second)
                prix_direct = duree_directe + v.prix_route(e, direct)
                prix_detour = duree_detour + v.prix_route(e, premier) + v.prix_route(intermediaire, second)
                self.assertLess(duree_directe, duree_detour)
                self.assertLess(prix_detour, prix_direct)
                but = lambda v, e: e.salle == "d"
                plan = p.chercher(m, qui, but, emplois=(), noeuds=p.REFERENCE)
                self.assertEqual([x["lieu"] for x in plan[1]], ["c", "d"])
                self.assertAlmostEqual(plan[0], prix_detour)
                allers = p.Vue.allers
                # Hypothèse P3 uniquement dans ce témoin de diagnostic :
                # « d » est le seul lieu du but, les autres salles sont vides.
                with patch.object(p.Vue, "allers", lambda v, e, ouvertes: [
                        (s, d) for s, d in allers(v, e, ouvertes) if s == "d"]):
                    filtre = p.chercher(m, qui, but, emplois=(), noeuds=p.REFERENCE)
                self.assertAlmostEqual(filtre[0], prix_direct)
                self.assertGreater(filtre[0], plan[0])
                apres, _, _ = executer_plan(m, qui, plan[1])
                self.assertEqual(apres.objets[qui]["lieu"], "d")
                recharge = recharger(apres)
                self.assertEqual(apres.data, recharge.data)
                self.assertEqual(regarder(apres), regarder(recharge))
                self.assertEqual(scene_percue(apres), scene_percue(recharge))
                self.assertTrue(recharge.visible(qui))
