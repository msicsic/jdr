"""Prises et issues différées sur l'horloge, état et rendu rechargés."""
import unittest
import copy
from unittest.mock import patch

from donjon import corps, tenir, combat
from donjon.banc_pnj import appliquer_etats
from donjon.deplacement_objet import deplacer
from donjon.esprits import percevoir_tous, lire
from donjon.monde import objet, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.temps import instant
from tests.test_combat import scene
from tests.test_corps_blessable import passer
from tests.test_tensions import recharger, placer


def situation(cible="brune"):
    m = scene("marchand")
    if cible != "brune":
        placer(m, "brune", "echoppe", (3, 3))
        placer(m, cible, "antichambre", (2, 5))
    m.objets["corde_test"] = objet("corde_test", "corde", "outil", "joueur", usages=["lien"])
    percevoir_tous(m)
    return m


class TenirTests(unittest.TestCase):
    def test_assommer_ligoter_delier_deux_personnes_apres_recharge(self):
        for cible in ("brune", "aubin"):
            with self.subTest(cible=cible):
                m = situation(cible)
                lien = "corde_test"
                if cible == "brune":
                    from donjon.atelier import nouveau_atelier
                    m.objets["ficelle"] = copy.deepcopy(nouveau_atelier().objets["ficelle"])
                    deplacer(m, "ficelle", "joueur")
                    lien = "ficelle"
                m.objets[cible]["orientation"] = "est"
                with patch.object(type(m), "d20", return_value=20):
                    Moteur(m).executer(Moteur(m).preparer(proposition("frapper", cible, "", "assommer")))
                for autre in ("marchand", "ilse", "aubin", "brune"):
                    if autre != cible:
                        corps.endormir(m, autre)
                p = Moteur(m).preparer(proposition("ligoter", cible, lien))
                self.assertTrue(p.confirmation)
                texte = Moteur(m).executer(p)
                m = recharger(m)
                self.assertIn("commences", texte)
                self.assertIn("maintenant ligotée", texte)
                self.assertEqual(corps.corps(m, cible)["lie"]["lien"], lien)
                self.assertTrue(m.objets[lien]["entrave"])
                self.assertIn("ligot", regarder(m))
                with self.assertRaises(ErreurMonde) as refus:
                    deplacer(m, lien, "joueur")
                self.assertTrue(refus.exception.attendu)
                Moteur(m).executer(Moteur(m).preparer(proposition("delier", cible)))
                m = recharger(m)
                self.assertNotIn("lie", corps.corps(m, cible))
                self.assertEqual(m.objets[lien]["lieu"], "joueur")
                self.assertNotIn("ligot", regarder(m))

    def test_issue_a_la_fin_meme_laps_decoupe_recharge(self):
        for cible in ("brune", "aubin"):
            a = situation(cible)
            corps.endormir(a, cible)
            tenir.commencer(a, "joueur", "ligoter", cible, "corde_test")
            b = recharger(a)
            passer(a, 300)
            for dt in (13, 86, 200):
                passer(b, dt)
                b = recharger(b)
                self.assertNotIn("lie", corps.corps(b, cible))
            passer(b, 1)
            a, b = recharger(a), recharger(b)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))

    def test_reveil_ou_coup_interrompt_le_ligotage(self):
        for cause in ("reveil", "coup", "inconscience", "contact", "lien"):
            m = situation()
            corps.endormir(m, "brune")
            tenir.commencer(m, "joueur", "ligoter", "brune", "corde_test")
            passer(m, 100)
            if cause == "reveil":
                corps.corps(m, "brune")["inconscient"] = instant(m)
                corps.reveiller(m, "brune")
            elif cause == "coup":
                placer(m, "marchand", "antichambre", (1, 4))
                with patch.object(type(m), "d20", side_effect=[20, 1]):
                    self.assertTrue(combat.frapper(m, "marchand", "joueur")["touche"])
            elif cause == "inconscience":
                corps.endormir(m, "joueur")
            elif cause == "contact":
                m.joueur["position"] = [1, 2]
            else:
                deplacer(m, "corde_test", "antichambre")
            m = recharger(m)
            passer(m, 200)
            m = recharger(m)
            self.assertNotIn("lie", corps.corps(m, "brune"))
            self.assertNotIn("ligot", regarder(m))

    def test_saisir_surprise_face_et_pas_refuse_apres_recharge(self):
        for surprise in (True, False):
            m = situation()
            m.objets["brune"]["orientation"] = "est" if surprise else "ouest"
            with patch.object(type(m), "d20", side_effect=[20] if surprise else [20, 1]):
                self.assertTrue(tenir.commencer(m, "joueur", "saisir", "brune"))
            m = recharger(m)
            self.assertEqual(corps.corps(m, "brune")["tenu_par"], "joueur")
            self.assertIn("retenu", regarder(m))
            with self.assertRaises(ErreurMonde) as refus:
                tenir.autoriser(m, "brune", "aller")
            self.assertTrue(refus.exception.attendu)
            with self.assertRaises(ErreurMonde):
                tenir.valider(m, "joueur", "ligoter", "brune", "corde_test")
            tenir.lacher(m, "joueur", "dire")
            self.assertIn("tenu_par", corps.corps(m, "brune"))
            tenir.lacher(m, "joueur", "marcher")
            self.assertNotIn("tenu_par", corps.corps(m, "brune"))

    def test_joueur_tenu_ne_peut_pas_marcher_et_se_degage(self):
        m = situation()
        corps.corps(m, "joueur")["tenu_par"] = "brune"
        for action in ("marcher", "aller", "fuir", "faufiler", "chasser"):
            with self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(proposition(action, "ouest"))
            self.assertTrue(refus.exception.attendu)
        with patch.object(type(m), "d20", side_effect=[20, 1]):
            Moteur(m).executer(Moteur(m).preparer(proposition("degager")))
        m = recharger(m)
        self.assertNotIn("tenu_par", corps.corps(m, "joueur"))

    def test_protecteur_delie_et_prisonnier_se_libere_apres_dix_minutes(self):
        for cible in ("aubin", "ilse"):
            m = situation(cible)
            appliquer_etats(m, [cible + ":ligote"])
            placer(m, "marchand", "antichambre", (3, 5))
            m.objets["marchand"]["profil"]["protege"] = [cible]
            m.objets["marchand"]["orientation"] = "ouest"
            percevoir_tous(m)
            m = recharger(m)
            passer(m, 150)
            m = recharger(m)
            self.assertNotIn("lie", corps.corps(m, cible))
            self.assertEqual(m.objets["entrave_" + cible]["lieu"], "marchand")
            self.assertFalse(any(g["auteur"] == cible and g["operation"] == "liberer"
                                 for g in m.data.get("gestes_en_cours", ())))
            self.assertLess(lire(m, cible)["libre"], 6000)
            self.assertNotIn("ligot", regarder(m))
        m = situation()
        appliquer_etats(m, ["brune:ligote"])
        # Pas de protecteur : une issue propre à l'essai de la captive.
        with patch.object(type(m), "d20", return_value=20):
            passer(m, 5999)
            m = recharger(m)
            self.assertIn("lie", corps.corps(m, "brune"))
            passer(m, 2)
        m = recharger(m)
        self.assertNotIn("lie", corps.corps(m, "brune"))

    def test_joueur_ligote_se_libere_par_la_commande_et_liens_physiques(self):
        from donjon.commandes import analyser
        from donjon.spatial import porte_par
        m = situation()
        m.objets["corde_test"]["entrave"] = True
        corps.corps(m, "joueur")["lie"] = {"lien": "corde_test", "par": "brune", "depuis": instant(m)}
        self.assertFalse(porte_par(m, "corde_test", "joueur"))
        for action in ("marcher", "frapper", "prendre"):
            with self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(proposition(action, "brune"))
            self.assertTrue(refus.exception.attendu)
        # Pas de tiers pour décider d'un autre geste pendant les dix minutes.
        for autre in ("marchand", "ilse", "aubin", "brune"):
            corps.endormir(m, autre)
            corps.corps(m, autre)["inconscient"] += 6000
            lire(m, autre)["libre"] = corps.corps(m, autre)["inconscient"]
        with patch.object(type(m), "d20", return_value=20):
            p = Moteur(m).preparer(analyser(m, "se libérer"))
            self.assertEqual(p.dixiemes, 6000)
            texte = Moteur(m).executer(p)
        m = recharger(m)
        self.assertNotIn("lie", corps.corps(m, "joueur"))
        self.assertIn("Tu as défait tes liens", texte)
        self.assertTrue(porte_par(m, "corde_test", "joueur"))
        self.assertTrue(m.data["journal"][-1]["reussite"])

    def test_liberation_manquee_du_joueur_est_un_echec_d_action_apres_recharge(self):
        m = situation()
        m.objets["corde_test"]["entrave"] = True
        corps.corps(m, "joueur")["lie"] = {"lien": "corde_test", "par": "brune", "depuis": instant(m)}
        for autre in ("marchand", "ilse", "aubin", "brune"):
            corps.endormir(m, autre)
            corps.corps(m, autre)["inconscient"] += 6000
            lire(m, autre)["libre"] = corps.corps(m, autre)["inconscient"]
        with patch.object(type(m), "d20", return_value=1):
            texte = Moteur(m).executer(Moteur(m).preparer(proposition("liberer")))
        m = recharger(m)
        self.assertIn("lie", corps.corps(m, "joueur"))
        self.assertIn("ne parviens pas", texte)
        self.assertFalse(m.data["journal"][-1]["reussite"])

    def test_lien_forme_longueur_et_echec_de_liberation(self):
        m = situation()
        o = m.objets["corde_test"]
        o["usages"] = []
        o["physique"] = {"forme": "lien", "dimensions": {"longueur_cm": 99}}
        self.assertFalse(tenir.lien_valide(o))
        o["physique"]["dimensions"]["longueur_cm"] = 100
        self.assertTrue(tenir.lien_valide(o))
        # La donnée physique est seulement sondée ici ; la capture reste un monde
        # valide, avec un lien d'usage déclaré.
        o.pop("physique")
        o["usages"] = ["lien"]
        appliquer_etats(m, ["brune:ligote"])
        with patch.object(type(m), "d20", return_value=1):
            passer(m, 6001)
        m = recharger(m)
        self.assertIn("lie", corps.corps(m, "brune"))
        self.assertIn("ligot", regarder(m))
        self.assertEqual(sum(e["type"] == "liberation_manquee" for e in m.data["historique_corps"]), 1)

    def test_rotation_fait_partie_de_l_echeance_et_couper_prend_trois_secondes(self):
        m = situation()
        corps.endormir(m, "brune")
        m.joueur["orientation"] = "nord"
        p = Moteur(m).preparer(proposition("ligoter", "brune", "corde_test"))
        self.assertGreater(p.dixiemes, 300)
        valeur = p.effets[0][2]
        tenir.commencer(m, "joueur", valeur["operation"], "brune", valeur["outil"],
                        rotation_dixiemes=valeur["rotation_dixiemes"])
        passer(m, 300)
        m = recharger(m)
        self.assertNotIn("lie", corps.corps(m, "brune"))
        passer(m, p.dixiemes - 300)
        m = recharger(m)
        self.assertIn("lie", corps.corps(m, "brune"))
        deplacer(m, "couteau", "joueur")
        m.joueur["orientation"] = "est"
        p = Moteur(m).preparer(proposition("delier", "brune", "couteau"))
        self.assertEqual(p.dixiemes, 30)
        Moteur(m).executer(p)
        m = recharger(m)
        self.assertNotIn("lie", corps.corps(m, "brune"))
        self.assertEqual(m.objets["corde_test"]["lieu"], "joueur")


if __name__ == "__main__":
    unittest.main()
