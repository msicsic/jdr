"""Le savoir initial n'est pas une nouvelle ; un changement appris le devient."""
import copy
import unittest
from unittest.mock import patch

from donjon import social
from donjon.banc_pnj import creer
from donjon.deplacement_objet import deplacer
from donjon.esprits import constater, constater_possession, croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_garde_ouidire import garde, noyau
from tests.test_tensions import recharger


class NouvellesInitialesTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_inventaires_de_depart_revues_dates_et_recharges_restent_silencieux(self):
        for scenario, id, objet in (("mine", "bram", "cle_paie"),
                                    ("auberge", "anselme", "cle_coffre")):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, "fixe")
                for _ in range(2):
                    percevoir_tous(m)
                    self.assertFalse(any(n[1].get("objet") == objet and n[1].get("attribut") == "lieu"
                                         for n in social.nouvelles(m, id)))
                    m = self.recharge(m)
                    ecouler(m, 600)
                self.assertFalse(any(c.get("constat_confie") for c in m.data.get("chronique", [])))

    def test_un_transfert_appris_puis_son_retour_ne_redeviennent_pas_initiaux(self):
        for scenario, id, autre, objet in (("mine", "bram", "josse", "cle_paie"),
                                          ("auberge", "anselme", "hugues", "cle_coffre")):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, "fixe")
                constater_possession(m, id, objet, "vu")
                self.assertFalse(any(n[1].get("objet") == objet for n in social.nouvelles(m, id)))
                for porteur in (autre, id):
                    ecouler(m, 600)
                    deplacer(m, objet, porteur)
                    constater_possession(m, id, objet, "vu")
                    n = next(n[1] for n in social.nouvelles(m, id)
                             if n[1].get("objet") == objet and n[1].get("attribut") == "lieu")
                    self.assertEqual(n["details"]["possession"]["porteur"], porteur)
                    self.assertEqual(n["observe"], m.data["minutes"])
                    m = self.recharge(m)

    def test_savoir_de_garde_change_puis_retabli_reste_une_nouvelle(self):
        m = creer("mine", 1985, "fixe")
        id, objet = "bram", "porte_reserve"
        self.assertTrue(lire(m, id)["croyances"][objet]["verrouillee"]["valeur"])
        constater(m, id, objet, "vu")
        self.assertFalse(any(n[1].get("objet") == objet for n in social.nouvelles(m, id)))
        for ferme in (False, True):
            ecouler(m, 600)
            m.objets[objet]["verrouillee"] = ferme
            croire(m, id, objet, "verrouillee", ferme, "essai")
            m = self.recharge(m)
        self.assertTrue(any(n[1].get("objet") == objet and n[1].get("attribut") == "verrouillee"
                            for n in social.nouvelles(m, id)))

    def test_decouverte_tardive_silencieuse_puis_transfert_inedit(self):
        for scenario, temoin, porteur, objet in (("mine", "mathe", "josse", "cle_paie"),
                                                ("auberge", "odile", "hugues", "cle_coffre")):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, "fixe")
                lire(m, temoin)["croyances"].pop(objet, None)
                ecouler(m, 600)
                constater_possession(m, temoin, objet, "vu")
                self.assertFalse(any(n[1].get("objet") == objet for n in social.nouvelles(m, temoin)))
                m = self.recharge(m)
                deplacer(m, objet, porteur)
                constater_possession(m, temoin, objet, "vu")
                n = next(n[1] for n in social.nouvelles(m, temoin) if n[1].get("objet") == objet)
                self.assertEqual(n["details"]["possession"]["porteur"], porteur)
                self.assertEqual(n["observe"], 1)
                self.recharge(m)

    def test_fin_de_garde_entendue_apres_installation_sans_relecture_privee(self):
        for scenario, objet in (("relais", "cle_reserve"), ("auberge", "ballot")):
            with self.subTest(scenario=scenario):
                m, gardien, temoin, porteur = garde(scenario, objet)
                n = noyau(m, temoin, objet)
                initiaux = copy.deepcopy(lire(m, gardien)["faits_initiaux"])
                # Un changement non perçu avant recharge ne refait aucun ancrage.
                deplacer(m, objet, gardien)
                m = self.recharge(m)
                self.assertEqual(lire(m, gardien)["faits_initiaux"], initiaux)
                with patch.object(Monde, "d20", return_value=20):
                    self.assertEqual(social.recevoir(m, gardien, temoin,
                        {"type": "rumeur", "evenement": n, "rang": 0}), "crue")
                c = lire(m, gardien)["croyances"][objet]["lieu"]
                self.assertEqual(c["possession"]["porteur"], porteur)
                self.assertEqual(c["source"], "dit:" + temoin)
                self.recharge(m)
