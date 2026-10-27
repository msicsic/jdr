"""Poste physique, avertissement entendu et persistance après recharge."""
import copy
import unittest

from donjon import defense, relations
from donjon.deliberation import choisir
from donjon.esprits import lire, percevoir_tous, memoriser, croire
from donjon.passage import demander_passage, laisser_passer
from donjon.rendu import regarder
from donjon.temps import MINUTE
from tests.support import regarder as orienter
from tests.test_combat import scene
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


def epreuve(gardien="marchand", approchant="joueur"):
    m = scene(gardien, False)
    placer(m, gardien, "antichambre", (3, 4))
    if approchant == "joueur":
        m.joueur.update(position=[2, 5], orientation="est")
        placer(m, "brune", "echoppe", (3, 3))
    else:
        placer(m, approchant, "antichambre", (2, 5))
        m.joueur.update(position=[1, 4], orientation="est")
    o = m.objets["cle_reserve"]
    o.update(lieu="antichambre", position=[4, 5], position_salle="antichambre", proprietaire=gardien)
    p = m.objets[gardien]["profil"]
    p["besoins"]["biens"] = {"depart": 0, "derive_heure": 0, "urgence": 70}
    p["pulsions"] = [{"besoin": "biens", "condition": {"objet": "cle_reserve", "lieu": "antichambre"}}]
    lire(m, gardien)["pulsions"] = [True]
    orienter(m, gardien, approchant)
    percevoir_tous(m)
    lire(m, gardien)["relations"].pop(approchant, None)
    memoriser(m, gardien, {"type": "service_rendu", "de": approchant, "preuve": "fixture-service"})
    memoriser(m, gardien, {"type": "vol_surpris", "auteur": approchant, "objet": "cle_reserve"})
    return recharger(m)


class InterpositionTests(unittest.TestCase):
    def test_deux_gardiens_poste_parole_persistance_et_rendu_recharges(self):
        for gardien, autre in (("marchand", "joueur"), ("aubin", "brune")):
            with self.subTest(gardien=gardien):
                m = epreuve(gardien, autre)
                avant = copy.deepcopy(m.data)
                r = defense.interposition(m, gardien)
                self.assertIsNotNone(r)
                self.assertEqual(m.data, avant)
                choisir(m, gardien, m.data["minutes"])
                self.assertEqual(lire(m, gardien)["intention"]["but"]["type"], "interposer")
                lignes = passer(m, MINUTE)
                m = recharger(m)
                self.assertEqual(m.objets[gardien]["position"], [3, 5])
                self.assertTrue(any(s["type"] == "mise_en_garde" for s in lire(m, gardien)["memoire"]))
                self.assertIn("interpose", str(m.data))
                self.assertTrue(regarder(m))
                axes = relations.axes(m, gardien, autre)
                self.assertEqual(laisser_passer(m, gardien, autre)[1], "garde")
                self.assertEqual(demander_passage(m, gardien, autre, []), "mefiance")
                m = recharger(m)
                apres = relations.axes(m, gardien, autre)
                self.assertLess(apres["confiance"], axes["confiance"])
                self.assertGreater(apres["rancune"], axes["rancune"])
                self.assertFalse(m.data.get("historique_corps"))

    def test_confiance_ne_provoque_pas_interposition(self):
        m = epreuve()
        # Une relation initiale de confiance, fixée par la scène.
        lire(m, "marchand")["relations"].pop("joueur", None)
        self.assertIsNone(defense.interposition(m, "marchand"))

    def test_guet_lu_protege_et_tiers_sur(self):
        m = epreuve()
        lire(m, "marchand")["relations"].pop("joueur", None)
        croire(m, "marchand", "joueur", "intention", "guet", "devine",
               signe="fixture-guet", envers="cle_reserve")
        self.assertIsNotNone(defense.interposition(m, "marchand"))
        # Une personne protégée emploie la même règle de poste.
        m.objets["marchand"]["profil"]["pulsions"] = []
        lire(m, "marchand")["pulsions"] = []
        m.objets["marchand"]["profil"]["protege"] = ["ilse"]
        placer(m, "ilse", "antichambre", (4, 5))
        croire(m, "marchand", "joueur", "intention", "guet", "devine",
               signe="fixture-guet-personne", envers="ilse")
        orienter(m, "marchand", "ilse")
        percevoir_tous(m)
        orienter(m, "marchand", "joueur")
        percevoir_tous(m)
        r = defense.interposition(m, "marchand")
        self.assertIsNotNone(r)
        self.assertEqual(r[0]["objet"], "ilse")

    def test_epreuve_anselme_ballot_en_donnees(self):
        from donjon.banc_pnj import creer
        from donjon.deplacement_objet import deplacer
        from tests.support import presentes, calme
        m = presentes(creer("auberge", 1985, "fixe"))
        calme(m, "anselme", "hugues", "lucien", "odile")
        deplacer(m, "ballot", "chambre_chaude")
        placer(m, "ballot", "chambre_chaude", (4, 2))
        placer(m, "anselme", "chambre_chaude", (3, 1))
        m.joueur.update(salle="chambre_chaude", position=[2, 2], orientation="est")
        orienter(m, "anselme", "ballot")
        percevoir_tous(m)
        orienter(m, "anselme", "joueur")
        percevoir_tous(m)
        memoriser(m, "anselme", {"type": "vol_surpris", "auteur": "joueur", "objet": "ballot"})
        m = recharger(m)
        choisir(m, "anselme", 0)
        passer(m, MINUTE)
        m = recharger(m)
        self.assertEqual(m.objets["anselme"]["position"], [3, 2])
        self.assertTrue(any(s["type"] == "mise_en_garde" and s["objet"] == "ballot"
                            for s in lire(m, "anselme")["memoire"]))
        self.assertIn("Anselme", regarder(m))

    def test_meme_laps_decoupe_et_recharge(self):
        for gardien, autre in (("marchand", "joueur"), ("aubin", "brune")):
            a = epreuve(gardien, autre)
            b = recharger(a)
            passer(a, MINUTE)
            for dt in (13, 87, 210, 290):
                passer(b, dt)
                b = recharger(b)
            a = recharger(a)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))

    def test_absence_de_vue_et_cible_emportee_annulent(self):
        m = epreuve()
        orienter(m, "marchand", (5, 4))
        percevoir_tous(m)
        self.assertIsNone(defense.interposition(m, "marchand"))
        m = epreuve()
        m.objets["cle_reserve"]["lieu"] = "marchand"
        percevoir_tous(m)
        self.assertIsNone(defense.interposition(m, "marchand"))
