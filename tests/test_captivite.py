"""Captivité vécue : croyances, horloge commune, fiche et sauvegarde."""
from contextlib import ExitStack
import unittest
from unittest.mock import patch

from donjon import corps, vecu, tenir
from donjon.banc_pnj import creer, appliquer_etats
from donjon.caractere import modificateur
from donjon.deliberation import ecart_securite
from donjon.esprits import croire, lire
from donjon.rendu import fiche, regarder
from donjon.temps import MINUTE, instant, ecouler
from tests.test_enfermer import scene
from tests.test_corps_blessable import passer
from tests.test_tensions import placer, recharger
from tests.support import regarder as orienter


def sans_evasion():
    """Laisser vivre les corps sans que les acteurs mettent fin à l'épreuve."""
    s = ExitStack()
    for nom in ("deliberer", "choisir"):
        s.enter_context(patch("donjon.deliberation." + nom, return_value=None))
    s.enter_context(patch("donjon.social.bavarder", return_value=None))
    s.enter_context(patch("donjon.tenir.secours", return_value=None))
    return s


class CaptiviteTests(unittest.TestCase):
    def test_une_cle_portee_permet_de_sortir_sauf_si_ligote(self):
        from donjon.deplacement_objet import deplacer
        for qui in ("remy", "joueur"):
            with self.subTest(qui=qui):
                m, p = scene()
                if qui == "joueur":
                    m.joueur.update(salle="bureau", position=[1, 1])
                    m.data.setdefault("verrous_joueur", {})[p] = True
                self.assertTrue(tenir.captif(m, qui))
                deplacer(m, "passe", qui)
                self.assertFalse(tenir.captif(recharger(m), qui))
                appliquer_etats(m, ["remy:ligote"])
                if qui == "joueur":
                    lien = corps.corps(m, "remy").pop("lie")
                    m.objets[lien["lien"]]["lieu"] = "joueur"
                    corps.corps(m, "joueur")["lie"] = lien
                self.assertTrue(tenir.captif(recharger(m), qui))

    def test_joueur_verrou_visible_et_memoire_hors_de_vue(self):
        m, p = scene()
        m.joueur.update(salle="bureau", position=[1, 1])
        orienter(m, "joueur", p)
        self.assertTrue(m.visible(p))
        self.assertTrue(tenir.captif(m, "joueur"))
        m.data.setdefault("verrous_joueur", {})[p] = True
        m.objets[p].update(ouverte=True, verrouillee=False)
        self.assertFalse(tenir.captif(m, "joueur"))
        self.assertFalse(tenir.captif(recharger(m), "joueur"))

    def test_croyance_fausse_et_enfermement_ignore(self):
        for salle in ("bureau", "reserve"):
            with self.subTest(salle=salle):
                m, p = scene(salle=salle)
                croire(m, "remy", p, "verrouillee", False, "savoir")
                self.assertFalse(tenir.captif(m, "remy"))
                libre = ecart_securite(m, "remy")
                croire(m, "remy", p, "verrouillee", True, "savoir")
                m.objets[p].update(ouverte=True, verrouillee=False)
                self.assertTrue(tenir.captif(m, "remy"))
                self.assertAlmostEqual(ecart_securite(m, "remy"), libre + 1)
                vecu.noter(m, "remy", instant(m), None)
                ecouler(m, MINUTE)
                vecu.solder(m, "remy", instant(m))
                r = recharger(m)
                self.assertEqual(r.data, m.data)
                self.assertEqual(regarder(r), regarder(m))
                self.assertEqual(corps.corps(r, "remy")["captivite"]["duree"], MINUTE)

    def test_heures_securite_recuperation_et_decoupage(self):
        for salle in ("bureau", "reserve"):
            with self.subTest(salle=salle), sans_evasion():
                m, p = scene(salle=salle)
                for i in m.data["esprits"]:
                    lire(m, i).update(libre=10000000, eveil=None, veille=None, intention=None)
                vecu.noter(m, "remy", instant(m), None)
                securite = lire(m, "remy")["besoins"]["securite"]
                passer(m, MINUTE)
                self.assertGreater(lire(m, "remy")["besoins"]["securite"], securite)
                a, b = recharger(m), recharger(m)
                passer(a, 59 * MINUTE)
                for dt in (13, 47, 17 * MINUTE, 42 * MINUTE - 60):
                    passer(b, dt)
                    b = recharger(b)
                self.assertEqual(recharger(a).data, b.data)
                self.assertEqual(regarder(a), regarder(b))
                self.assertEqual(corps.corps(b, "remy")["volonte_brisee"], 1)
                # La liberté et le calme se lisent dans la nouvelle salle éclairée.
                a.objets["poele"]["combustible"] = 1000
                for i in a.data["esprits"]:
                    # Les autres dormeurs ne lancent pas d'appels de détresse pendant le répit.
                    if i != "remy":
                        corps.endormir(a, i)
                        corps.corps(a, i)["inconscient"] = 10000000
                        lire(a, i)["libre"] = 10000000
                placer(a, "remy", "baraquement", (3, 2))
                vecu.noter(a, "remy", instant(a), None)
                self.assertTrue(vecu.conditions(a, "remy", None)["calme"])
                b = recharger(a)
                passer(a, 120 * MINUTE)
                for dt in (31 * MINUTE + 9, 89 * MINUTE - 9):
                    passer(b, dt)
                    b = recharger(b)
                self.assertEqual(recharger(a).data, b.data)
                self.assertEqual(corps.corps(b, "remy")["volonte_brisee"], 0)

    def test_joueur_meme_corps_et_fiche_rechargee(self):
        with sans_evasion():
            m, p = scene()
            m.joueur.update(salle="bureau", position=[1, 1])
            m.data.setdefault("verrous_joueur", {})[p] = True
            vecu.noter(m, "joueur", instant(m), None)
            b = recharger(m)
            passer(m, 60 * MINUTE)
            for dt in (29 * MINUTE + 13, 31 * MINUTE - 13):
                passer(b, dt)
                b = recharger(b)
            m = recharger(m)
            self.assertEqual(m.data, b.data)
            self.assertEqual(corps.corps(m, "joueur")["volonte_brisee"], 1)
            # La caractéristique effective applique le même malus de volonté.
            avec = modificateur(m, "joueur", "VOL")
            corps.briser(m, "joueur", -1)
            self.assertEqual(avec, modificateur(m, "joueur", "VOL") - 1)
            corps.briser(m, "joueur", 1)
            self.assertIn("Captivité : inquiétante", fiche(m))
            self.assertIn("Volonté : éprouvée", fiche(m))
            self.assertEqual(fiche(m), fiche(recharger(m)))
            m.joueur.update(salle="baraquement", position=[3, 2])
            m.objets["poele"]["combustible"] = 1000
            vecu.noter(m, "joueur", instant(m), None)
            b = recharger(m)
            passer(m, 120 * MINUTE)
            for dt in (MINUTE + 17, 119 * MINUTE - 17):
                passer(b, dt)
                b = recharger(b)
            self.assertEqual(recharger(m).data, b.data)
            self.assertEqual(corps.corps(b, "joueur")["volonte_brisee"], 0)
            self.assertNotIn("Captivité", fiche(b))
            self.assertEqual(fiche(m), fiche(b))

    def test_ligote_sans_dependance_a_une_salle(self):
        with sans_evasion():
            m = creer("relais", 1985, "fixe")
            appliquer_etats(m, ["aubin:ligote"])
            vecu.noter(m, "aubin", instant(m), None)
            passer(m, 60 * MINUTE)
            m = recharger(m)
            self.assertTrue(tenir.captif(m, "aubin"))
            self.assertEqual(corps.corps(m, "aubin")["volonte_brisee"], 1)

    def test_repit_interrompu_et_bornes(self):
        m, _ = scene()
        for _ in range(8):
            corps.vivre_captivite(m, "remy", 60 * MINUTE, True, False)
        self.assertEqual(corps.corps(m, "remy")["volonte_brisee"], 5)
        corps.vivre_captivite(m, "remy", 119 * MINUTE, False, True)
        corps.vivre_captivite(m, "remy", MINUTE, False, False)
        corps.vivre_captivite(m, "remy", MINUTE, False, True)
        self.assertEqual(corps.corps(m, "remy")["volonte_brisee"], 5)
        corps.vivre_captivite(m, "remy", 20 * 120 * MINUTE, False, True)
        self.assertEqual(corps.corps(m, "remy")["volonte_brisee"], 0)
