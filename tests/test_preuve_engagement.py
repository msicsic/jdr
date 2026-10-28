"""Une preuve après la parole, même dans la même minute, sans bruit nécessaire."""
import unittest

from donjon import agendas
from donjon.biens import services_proteges
from donjon.echanges import tenu
from donjon.esprits import constater, croire, lire, percoit
from donjon.pnj import _executer
from donjon.rendu import regarder as rendu
from donjon.scene import scene_percue
from tests.support import regarder
from tests import test_crochetage_surenchere as crochetage
from tests.test_tache_promise_recours import reserve
from tests.test_tensions import chronique, recharger


class PreuveEngagementTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(rendu(m), rendu(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def geste(self, m, id, op, objet, outil=""):
        self.assertTrue(_executer(m, id, {"operation": op, "cible": objet,
                                         "outil": outil, "lieu": "", "condition": ""}, [], []))

    def test_serrure_de_sa_main_meme_minute_apres_recharge(self):
        m, id, autre, c = reserve()
        agendas.prendre(m, id, {"condition": c, "pour": autre, "minute": 0})
        self.assertFalse(tenu(m, id, c, 0))
        m = self.recharge(m)
        self.geste(m, id, "fermer", "garde_manger")
        self.geste(m, id, "verrouiller", "garde_manger", "cle_garde_manger")
        self.assertEqual(m.data["minutes"], 0)
        agendas.echoir(m, id)
        m = self.recharge(m)
        self.assertTrue(m.objets["garde_manger"]["verrouillee"])
        self.assertNotIn(c, [x["condition"] for x in agendas.en_cours(m, id)])
        self.assertIn({"objet": "cle_garde_manger", "rendre": autre},
                      [x["condition"] for x in agendas.en_cours(m, id)])
        self.assertIn(c, services_proteges(m, id))
        self.assertTrue(any("verrouille" in t for t in chronique(m)))

    def test_geste_anterieur_meme_minute_ne_prouve_pas_la_parole(self):
        m, id, autre, c = reserve()
        self.geste(m, id, "fermer", "garde_manger")
        self.geste(m, id, "verrouiller", "garde_manger", "cle_garde_manger")
        agendas.prendre(m, id, {"condition": c, "pour": autre, "minute": 0})
        self.assertFalse(tenu(m, id, c, 0))
        m = self.recharge(m)
        self.assertFalse(tenu(m, id, c, 0))
        self.assertTrue(agendas.en_cours(m, id))
        # Une confirmation acoustique plus récente n'est pas une vue du verrou.
        m.data["minutes"] = 1
        croire(m, id, "garde_manger", "verrouillee", True, "entendu")
        self.assertFalse(tenu(self.recharge(m), id, c, 0))

    def test_observation_reelle_posterieure_sans_geste_propre(self):
        m = crochetage.TacheAccepteeTests().tilo_paye_pour_l_atre(briquet=True)
        c = {"objet": "atre", "allume": True}
        agendas.prendre(m, "tilo", {"condition": c, "pour": "odile", "minute": 0})
        self.assertFalse(tenu(m, "tilo", c, 0))
        m = self.recharge(m)
        # Un feu rallumé par un tiers entre ces deux observations.
        m.objets["atre"].update(allume=True, combustible=60)
        regarder(m, "tilo", "atre")
        self.assertTrue(percoit(m, "tilo", "atre"))
        constater(m, "tilo", "atre", "vu")
        self.assertEqual(lire(m, "tilo")["croyances"]["atre"]["etat"]["minute"], 0)
        agendas.echoir(m, "tilo")
        m = self.recharge(m)
        self.assertTrue(m.objets["atre"]["allume"])
        self.assertEqual(agendas.en_cours(m, "tilo"), [])
        self.assertIn(c, services_proteges(m, "tilo"))

    def test_paroles_identiques_meme_minute_ne_partagent_pas_la_preuve(self):
        m, id, autre, c = reserve()
        agendas.prendre(m, id, {"condition": c, "pour": autre, "minute": 0})
        self.assertFalse(tenu(m, id, c, 0))
        self.geste(m, id, "fermer", "garde_manger")
        self.geste(m, id, "verrouiller", "garde_manger", "cle_garde_manger")
        agendas.echoir(m, id)
        self.assertNotIn(c, [x["condition"] for x in agendas.en_cours(m, id)])
        agendas.prendre(m, id, {"condition": c, "pour": autre, "minute": 0})
        m = self.recharge(m)
        self.assertFalse(tenu(m, id, c, 0))
        self.assertIn(c, [x["condition"] for x in agendas.en_cours(m, id)])
        # Une nouvelle preuve réelle demeure recevable pour cette seconde parole.
        m.data["minutes"] = 1
        self.geste(m, id, "deverrouiller", "garde_manger", "cle_garde_manger")
        self.geste(m, id, "verrouiller", "garde_manger", "cle_garde_manger")
        agendas.echoir(m, id)
        self.assertNotIn(c, [x["condition"] for x in agendas.en_cours(self.recharge(m), id)])
