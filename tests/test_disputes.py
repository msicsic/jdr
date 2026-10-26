"""Épisodes d'avis contradictoires : état et paroles persistent ensemble."""
import copy
import unittest
from unittest.mock import patch

from donjon import eau, ecoute, pnj, social
from donjon.esprits import croire, lire, prevision
from donjon.relations import envers
from donjon.rendu import regarder as rendu
from donjon.temps import ecouler
from tests.support import regarder
from tests.test_avis_menace import scene, relation
from tests.test_social import recharger, placer


def dispute(locuteur="aubin", contradicteur="ilse", salle="antichambre"):
    m = scene()
    if salle != "antichambre":
        for qui, case in ((locuteur, [2, 2]), (contradicteur, [3, 2]), ("marchand", [2, 3])):
            placer(m, qui, salle, case)
        m.joueur.update(salle=salle, position=[3, 3])
    regarder(m, "joueur", locuteur)
    for qui in (locuteur, contradicteur, "marchand"):
        for autre in (locuteur, contradicteur, "marchand"):
            if qui != autre:
                regarder(m, qui, autre)
                croire(m, qui, autre, "lieu", salle, "vu", salle=salle, case=m.objets[autre]["position"])
    # Scène d'auteur : deux preuves opposées, aucune lecture du pic caché.
    for qui in (locuteur, contradicteur, "marchand"):
        for a in lire(m, qui)["croyances"].values():
            a.pop("eau", None)
            a.pop("prevision", None)
    t = m.data["minutes"]
    croire(m, locuteur, salle, "prevision", [t, 10000, 1], "vu", .8, rang=0)
    croire(m, contradicteur, salle, "prevision", [t, -10000, 1], "vu", 1, rang=0)
    relation(m, locuteur, contradicteur, confiance=0, affection=0)
    relation(m, contradicteur, locuteur, confiance=0, affection=0)
    relation(m, "marchand", locuteur, confiance=0, affection=0)
    relation(m, "marchand", contradicteur, confiance=100, affection=80)
    m.objets[locuteur]["profil"]["valeurs"].update(fierte=80, altruisme=100, empathie=100)
    return recharger(m)


class DisputesTests(unittest.TestCase):
    def test_le_partisan_relaie_sa_propre_conviction(self):
        m = dispute()
        lire(m, "aubin")["croyances"]["antichambre"]["prevision"]["confiance"] = .69
        relation(m, "aubin", "marchand", confiance=100, affection=0)
        lignes = []
        social.bavarder(m, "aubin", lignes)
        m = recharger(m)
        self.assertEqual(prevision(m, "marchand", "antichambre")["source"], "dit:ilse")
        # Gorm ne transforme pas la conviction 1 d'Ilse en preuve directe :
        # son poids 0,98 donne 0,686 chez Aubin, sous sa preuve propre à 0,69.
        self.assertTrue(eau.menacee(m, "aubin", "antichambre"))
        self.assertEqual(prevision(m, "aubin", "antichambre")["source"], "vu")
        self.assertTrue(any(c.get("parti_pris") for c in m.data["chronique"]))
        self.assertIn("Non, l'eau ne menace pas", "\n".join(lignes))
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_eclat_voisin_et_aller_voir_par_la_regle_commune(self):
        from donjon.deliberation import bruit_a_voir
        m = dispute()
        m.objets["brune"]["profil"]["valeurs"]["courage"] = 100
        m.joueur.update(salle="echoppe", position=[1, 2])
        m.data["voix_connues"] = ["aubin"]
        social.bavarder(m, "aubin", [])
        m = recharger(m)
        self.assertTrue(any(s["type"] == "bruit" and s["nature"] == "eclat"
                            for s in lire(m, "brune")["memoire"]))
        self.assertEqual(bruit_a_voir(m, "brune"), ("antichambre", "securite"))
        sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
        texte = "\n".join(ecoute.rendre(m, sons))
        self.assertIn("menace", texte)
        self.assertEqual(texte, "\n".join(ecoute.rendre(recharger(m), sons)))

    def test_egalite_departagee_et_constat_propre_preserve(self):
        m = dispute()
        relation(m, "marchand", "aubin", confiance=100, affection=0)
        relation(m, "marchand", "ilse", confiance=80, affection=0)
        with patch("donjon.monde.Monde.d20", side_effect=[1, 20]), \
                patch("donjon.caractere.modificateur", return_value=0):
            social.bavarder(m, "aubin", [])
        self.assertEqual(prevision(recharger(m), "marchand", "antichambre")["source"], "dit:ilse")
        m = dispute()
        relation(m, "marchand", "aubin", confiance=100, affection=0)
        relation(m, "marchand", "ilse", confiance=80, affection=0)
        with patch("donjon.monde.Monde.d20", return_value=10), \
                patch("donjon.caractere.modificateur", return_value=0):
            social.bavarder(m, "aubin", [])
        self.assertIsNone(prevision(recharger(m), "marchand", "antichambre"))
        self.assertTrue(any(s["type"] == "parole_doutee" for s in lire(m, "marchand")["memoire"]))
        # Même contrat si ce témoin était le destinataire de la première phrase.
        m = dispute()
        relation(m, "aubin", "marchand", confiance=0, affection=100)
        relation(m, "marchand", "aubin", confiance=100, affection=0)
        relation(m, "marchand", "ilse", confiance=80, affection=0)
        with patch("donjon.monde.Monde.d20", return_value=10), \
                patch("donjon.caractere.modificateur", return_value=0):
            social.bavarder(m, "aubin", [])
        self.assertIsNone(prevision(recharger(m), "marchand", "antichambre"))
        m = dispute()
        t = m.data["minutes"]
        croire(m, "marchand", "antichambre", "prevision", [t, 10000, 1], "vu", 1, rang=0)
        avant = copy.deepcopy(prevision(m, "marchand", "antichambre"))
        social.bavarder(m, "aubin", [])
        self.assertEqual(prevision(recharger(m), "marchand", "antichambre"), avant)

    def test_deux_paires_lieux_paroles_et_suites_apres_recharge(self):
        for locuteur, contradicteur, salle in (("aubin", "ilse", "antichambre"),
                                               ("ilse", "aubin", "beffroi")):
            with self.subTest(salle=salle):
                m = dispute(locuteur, contradicteur, salle)
                lignes = []
                self.assertTrue(social.bavarder(m, locuteur, lignes))
                m = recharger(m)
                self.assertFalse(eau.menacee(m, "marchand", salle))
                self.assertEqual(prevision(m, "marchand", salle)["source"], "dit:" + contradicteur)
                self.assertTrue(any(s["type"] == "dispute_perdue" for s in lire(m, locuteur)["memoire"]))
                self.assertGreater(envers(m, locuteur, contradicteur)["rancune"], 0)
                self.assertGreater(envers(m, contradicteur, "marchand")["affection"], 0)
                texte = "\n".join(lignes)
                self.assertIn("Non, l'eau ne menace pas", texte)
                self.assertIn("Je maintiens", texte)
                self.assertIn("hausse la voix", texte)
                self.assertTrue(any(b["nature"] == "eclat" for b in m.data["bruits"]))
                self.assertFalse(any(s["type"] in ("mensonge_decouvert", "mensonge_dementi")
                                     for qui in (locuteur, contradicteur, "marchand") for s in lire(m, qui)["memoire"]))
                self.assertEqual(rendu(m), rendu(recharger(m)))
                n = sum(bool(c.get("dispute")) for c in m.data["chronique"])
                self.assertEqual(n, 1)
                for qui in (locuteur, contradicteur, "marchand"):
                    lire(m, qui)["memoire"].clear()
                ecouler(m, 600)
                social.bavarder(m, locuteur, [])
                social.bavarder(m, contradicteur, [])
                self.assertEqual(sum(bool(c.get("dispute")) for c in m.data["chronique"]), n)

    def test_meme_laps_decoupe_et_rendu_recharge(self):
        initial = dispute()
        for qui in ("marchand", "brune"):
            lire(initial, qui)["libre"] = 100000
        resultats = []
        for tranches in ((1200,), (150,) * 8):
            m, lignes = recharger(initial), []
            for dt in tranches:
                pnj.avancer(m, ecouler(m, dt), lignes, dt)
                m = recharger(m)
            self.assertTrue(any(c.get("dispute") for c in m.data["chronique"]))
            resultats.append((copy.deepcopy(m.data), rendu(m)))
        self.assertEqual(*resultats)

    def test_absence_de_reponse_sans_mots_et_pas_d_eclat_sans_fierte(self):
        m = dispute()
        m.objets["ilse"]["entend"] = False
        social.bavarder(m, "aubin", [])
        self.assertFalse(any(c.get("dispute") for c in recharger(m).data["chronique"]))
        m = dispute()
        m.objets["aubin"]["profil"]["valeurs"]["fierte"] = 0
        social.bavarder(m, "aubin", [])
        self.assertFalse(any(c.get("eclat") for c in recharger(m).data["chronique"]))
        m = dispute()
        m.objets["aubin"]["profil"]["valeurs"]["fierte"] = 0
        lire(m, "aubin")["emotions"]["colere"] = {"contre": "ilse", "niveau": 40, "depuis": m.data["minutes"]}
        social.bavarder(m, "aubin", [])
        self.assertEqual(sum(bool(c.get("eclat")) for c in recharger(m).data["chronique"]), 1)


if __name__ == "__main__":
    unittest.main()
