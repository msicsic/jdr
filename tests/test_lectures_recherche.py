"""Le diagnostic n'autorise aucune reprise et ne change ni partie ni rendu."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, pnj
from donjon.esprits import croire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger
from tools.mesurer_lectures_recherche import DictionnaireLu, Trace, observer, resumer


def capture(scenario):
    chemin = Path(__file__).parent / f"data/cout-12h/{scenario}-1985-480.json.gz"
    return recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))


class LecturesTests(unittest.TestCase):
    def test_absence_ordre_et_feuille_invalident_les_lectures(self):
        m = capture("mine")
        a, b = Trace(p.Vue(m, "remy")), Trace(p.Vue(m, "remy"))
        a.racines["essai"] = {"a": {"v": 1}, "b": 2}
        b.racines["essai"] = {"a": {"v": 1}, "b": 2}
        d = a.envelopper(a.racines["essai"], ("essai",))
        self.assertIsNone(d.get("absent"))
        self.assertEqual(list(d), ["a", "b"])
        self.assertEqual(d["a"]["v"], 1)
        self.assertEqual(b.changements(a), [])
        b.racines["essai"]["absent"] = False
        self.assertTrue(b.changements(a))
        b.racines["essai"] = {"b": 2, "a": {"v": 1}}
        self.assertTrue(b.changements(a))
        b.racines["essai"] = {"a": {"v": 3}, "b": 2}
        self.assertTrue(b.changements(a))

    def test_lecture_native_echappe_a_l_enveloppe_aucune_preuve_de_reprise(self):
        # Une sous-classe de dict ne suffit pas : le lecteur natif peut accéder
        # à sa table interne, sans appeler __getitem__. Ce trou est reproductible.
        t = Trace(p.Vue(capture("mine"), "remy"))
        d = DictionnaireLu({"valeur": 1}, t, ("essai",))
        self.assertEqual(dict.__getitem__(d, "valeur"), 1)
        self.assertEqual(t.lectures, {})
        detache = copy.deepcopy(d)
        self.assertIs(type(detache), dict)
        self.assertEqual(detache, {"valeur": 1})
        with self.assertRaisesRegex(RuntimeError, "Écriture"):
            d["valeur"] = 2

    def test_captures_reelles_instrumentation_et_temoins_identiques_apres_recharge(self):
        for scenario, qui in (("mine", "remy"), ("auberge", "joss")):
            with self.subTest(scenario=scenario):
                resultats, mondes = [], []
                for instrumente in (False, True):
                    m, releves = capture(scenario), []
                    with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                            patch.object(p, "_IMPOSSIBLES", {}), p.diagnostics():
                        if instrumente:
                            with observer(qui, "faim", 480, releves):
                                r = p.planifier(m, qui, "faim")
                        else:
                            r = p.planifier(m, qui, "faim")
                        # La recherche suivante et l'exécution ne conservent aucun
                        # proxy de diagnostic. Le joueur voit la même minute vécue.
                        pnj.avancer(m, 1, [])
                    resultats.append(r)
                    recharge = recharger(m)
                    self.assertEqual(m.data, recharge.data)
                    self.assertEqual(regarder(m), regarder(recharge))
                    self.assertEqual(scene_percue(m), scene_percue(recharge))
                    mondes.append(recharge)
                    if instrumente:
                        self.assertEqual(len(releves), 1)
                        self.assertGreater(releves[0]["lectures"], 0)
                        self.assertFalse(releves[0]["reutilisable_prouve"])
                self.assertEqual(resultats[0], resultats[1])
                self.assertEqual(mondes[0].data, mondes[1].data)
                self.assertEqual(regarder(mondes[0]), regarder(mondes[1]))
                self.assertEqual(scene_percue(mondes[0]), scene_percue(mondes[1]))

    def test_changement_de_vivre_lu_detecte_sur_la_capture_reelle(self):
        m, releves = capture("mine"), []
        with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                patch.object(p, "_IMPOSSIBLES", {}), p.diagnostics(), observer("remy", "faim", 480, releves):
            self.assertIsNone(p.planifier(m, "remy", "faim"))
            # Une croyance sans rapport fait rater la clé large ; le diagnostic
            # distingue ce raté d'un changement de donnée effectivement lue.
            croire(m, "remy", "souvenir_test", "etat", {"ouverte": True}, "savoir")
            self.assertIsNone(p.planifier(m, "remy", "faim"))
            self.assertTrue(releves[-1]["comparaison"]["inchange_observe"])
            croire(m, "remy", "pain_lucien", "etat", {"disponible": True}, "savoir")
            p.planifier(m, "remy", "faim")
        self.assertFalse(releves[-1]["comparaison"]["inchange_observe"])
        self.assertEqual(resumer(releves)["reprises_sures_hors_cle_actuelle"], 0)
        m = recharger(m)
        self.assertTrue(m.data["esprits"]["remy"]["croyances"]["pain_lucien"]["etat"]["valeur"]["disponible"])


if __name__ == "__main__":
    unittest.main()
