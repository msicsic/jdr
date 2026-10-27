"""Jalon H : se sentir en sécurité — ce qui inquiète, ce qui rassure, se mettre à l'abri.

Chaque test vérifie l'état du monde et, quand le joueur est présent, ce qu'il lit, après
rechargement.
"""

from tests.support import lier
import unittest
from unittest.mock import patch

from donjon.deliberation import SECURITE, SECURITE_FIN, verifier_profil
from donjon.esprits import croire, lire, percevoir_tous
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.ouie import INTENSITES, parvenu, propager
from tests.support import calme, refusee
from tests.test_tensions import attendre, chronique, placer, recharger, relais, vivre


def dans_le_noir(monde, id, securite):
    """Placement d'auteur : le brasero est mort, ce PNJ se tient seul dans l'échoppe obscure ;
    il a vu le refuge, son fanal et ceux qui s'y trouvent."""
    percevoir_tous(monde)
    monde.objets["brasero"].update(allume=False, combustible=0)
    placer(monde, "marchand", "crypte", (5, 3))
    placer(monde, id, "echoppe", (3, 5))
    lire(monde, id)["besoins"]["securite"] = securite
    percevoir_tous(monde)
    return monde


class RessentirTests(unittest.TestCase):
    def test_le_noir_inquiete_la_lumiere_et_la_compagnie_rassurent(self):
        m = dans_le_noir(calme(relais(), "marchand", "brune", "ilse", "aubin"), "ilse", 40.0)
        m, _ = vivre(m, 10)
        # Dix minutes seule dans le noir : l'inquiétude monte, en plus de la dérive de fond.
        self.assertGreaterEqual(lire(m, "ilse")["besoins"]["securite"], 40.0 + 10 * SECURITE["noir"])
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, "ilse")["besoins"]["securite"] = 40.0
        m, _ = vivre(m, 10)
        # Au refuge éclairé par le fanal, près d'Aubin et de Brune qu'elle croit fiables.
        self.assertLessEqual(lire(m, "ilse")["besoins"]["securite"],
                             40.0 - 10 * (SECURITE["lumiere"] + SECURITE["compagnie"] * 0.85) + 1)

    def test_la_mefiance_inquiete(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, "ilse")["besoins"]["securite"] = 40.0
        # Placement d'auteur : Ilse a vu Brune voler ; elle ne la croit plus fiable. Brune se
        # tient à côté d'elle au refuge.
        placer(m, "brune", "antichambre", (4, 5))
        lier(m, "ilse", "brune", False, "vu")
        avec, _ = vivre(m, 10)
        sans = calme(relais(), "marchand", "brune", "ilse", "aubin")
        placer(sans, "brune", "antichambre", (4, 5))
        lire(sans, "ilse")["besoins"]["securite"] = 40.0
        sans, _ = vivre(sans, 10)
        self.assertAlmostEqual(lire(avec, "ilse")["besoins"]["securite"] - lire(sans, "ilse")["besoins"]["securite"],
                               10 * SECURITE["mefiance"], places=1)

    def test_une_ronde_accomplie_rassure(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, "aubin")["besoins"]["securite"] = 50.0
        # Sa ronde du refuge est due : il la fait sur place, le temps de gagner le centre.
        lire(m, "aubin")["visites"].pop("antichambre")
        m, _ = vivre(m, 2)
        self.assertGreaterEqual(lire(m, "aubin")["visites"]["antichambre"], m.data["minutes"] - 1)
        self.assertLess(lire(m, "aubin")["besoins"]["securite"], 50.0 - SECURITE["ronde"] + 1)

    def test_un_bruit_venu_d_ailleurs_inquiete_qui_n_en_voit_pas_la_cause(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Placement d'auteur : le joueur crie depuis le refuge ; Gorm est à l'échoppe.
        m.joueur.update(salle="antichambre", position=[3, 4])
        avant = lire(m, "marchand")["besoins"]["securite"]
        # Il s'inquiète à la mesure de ce qui lui parvient du cri, à travers le passage (``ouie``).
        o = m.objets["marchand"]
        niveau, _ = parvenu(propager(m, "antichambre", (3, 4), INTENSITES["appel"]), o["lieu"], tuple(o["position"]))
        from donjon import deliberation
        with patch.object(deliberation, "inquieter", wraps=deliberation.inquieter) as inquietudes:
            Moteur(m).executer(Moteur(m).preparer(sequence(etape("emettre_son", "joueur", methode="cri"))))
        m = recharger(m)
        # Un seul souvenir de ce qu'il entend : le bruit de l'ouïe commune, plus de « son » à part.
        self.assertNotIn("son", [s["type"] for s in lire(m, "marchand")["memoire"]])
        # Il l'a entendu ; il est allé voir aussitôt et a parcouru le refuge (le bruit est vu).
        self.assertIn("Gorm entend un bruit : Refuge du relais.", [c["texte"] for c in m.data["chronique"]])
        # Il s'en est inquiété à la mesure du cri (puis, allé voir, sa ronde l'a rassuré).
        self.assertIn(niveau / INTENSITES["appel"],
                      [c.args[3] for c in inquietudes.call_args_list if c.args[1:3] == ("marchand", "bruit")])
        self.assertGreater(SECURITE["bruit"] * niveau / INTENSITES["appel"], 1)

    def test_un_geste_illicite_vu_inquiete_le_temoin(self):
        # Gorm a déjà refusé une part à Brune : elle se sert.
        m = calme(refusee(relais()), "marchand", "ilse", "aubin")
        m.objets["reserve"].update(verrouillee=False, ouverte=True)
        lire(m, "brune")["besoins"]["faim"] = 99.0
        # Placement d'auteur : Brune, à bout de faim, devant la réserve ouverte ; Ilse la voit.
        placer(m, "brune", "antichambre", (7, 3))
        placer(m, "ilse", "antichambre", (5, 4))
        croire(m, "brune", "reserve", "verrouillee", False, "vu")
        croire(m, "brune", "reserve", "etat", {"ouverte": True}, "vu")
        lire(m, "ilse")["besoins"]["securite"] = 30.0
        m, _ = vivre(m, 3)
        self.assertIn("vu_agir", [s["type"] for s in lire(m, "ilse")["memoire"]])
        self.assertGreater(lire(m, "ilse")["besoins"]["securite"], 30.0 + SECURITE["illicite"] - 5)


class AbriTests(unittest.TestCase):
    def test_inquiete_dans_le_noir_elle_rejoint_la_lumiere_et_la_compagnie(self):
        m = dans_le_noir(calme(relais(), "marchand", "brune", "ilse", "aubin"), "ilse", 75.0)
        # Le joueur, au refuge éclairé par le fanal, la voit arriver ; sa lanterne éteinte ne
        # jette pas de lueur dans l'échoppe.
        m.joueur.update(salle="antichambre", position=[3, 4], orientation="ouest")
        m.objets["lanterne"]["allume"] = False
        # Ils restent au refuge pendant qu'elle les rejoint ; leur ronde ne doit
        # pas déplacer le compagnon que cette scène lui demande de retrouver.
        for id in ("aubin", "brune"):
            lire(m, id)["libre"] = 36000
        # Placement d'auteur : Gorm a déjà demandé à chacun s'il avait du bois et n'a pas de quoi payer
        # (``echanges.enqueter``, ``engager``) : il n'emmène pas Aubin rallumer le brasero.
        m.data["finances_pnj"]["marchand"] = 0
        from donjon.deliberation import retenir_refus
        for autre in ("brune", "ilse", "aubin"):
            retenir_refus(m, "marchand", autre, "enqueter", "rien", besoin="chaleur", souvenir=False)
        m, texte = attendre(recharger(m), 3)
        self.assertEqual(m.objets["ilse"]["lieu"], "antichambre")
        self.assertEqual(m.objets["aubin"]["lieu"], "antichambre")
        # 3c la rapproche ensuite réellement. Le texte de son arrivée à l’abri
        # reste celui de cet instant : elle n’était pas encore au contact.
        from donjon.geometrie import distance
        self.assertLessEqual(distance(m.objets["ilse"]["position"], m.objets["aubin"]["position"]), 1)
        self.assertIn("Ilse reste en compagnie.", chronique(m))
        self.assertIn("Ilse reste en compagnie.", texte.splitlines())
        # À l'abri, elle se calme : la lumière et la compagnie l'emportent sur la dérive.
        self.assertLess(lire(m, "ilse")["besoins"]["securite"], 75.0 - 5)

    def test_rassuree_elle_quitte_l_abri(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Ses compagnons restent ici, sans incident nouveau pendant l'apaisement.
        for id in ("marchand", "brune", "aubin"):
            lire(m, id)["libre"] = 36000
        m.objets["fanal"].update(allume=True, combustible=1000)
        placer(m, "marchand", "antichambre", (6, 5))
        # Son savoir de départ place encore Gorm ailleurs. La prémisse du
        # refuge déjà vu doit constater les compagnons réellement présents.
        from donjon.pnj import tour_d_horizon
        tour_d_horizon(m, "ilse")
        lire(m, "ilse")["besoins"]["securite"] = 65.0
        # Elle a vu le refuge éclairé (sa première minute) : elle s'y abrite près d'Aubin et de
        # Brune, sans aller chercher Gorm ailleurs (ce que l'abri lui apporterait de plus, rien).
        m, _ = vivre(m, 2)
        self.assertEqual(lire(m, "ilse")["intention"]["but"]["type"], "abri")
        self.assertEqual(lire(m, "ilse")["intention"]["but"]["lieu"], "antichambre")
        m, _ = vivre(m, 60)
        self.assertLessEqual(lire(m, "ilse")["besoins"]["securite"], SECURITE_FIN + 5)
        intention = lire(m, "ilse")["intention"]
        self.assertTrue(intention is None or intention["but"]["type"] != "abri")

    def test_le_joueur_rassure_qui_le_croit_fiable(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Placement d'auteur : Ilse seule à l'échoppe éclairée, Gorm aux vannes ; le joueur à
        # côté d'elle. Dans le noir, elle ne le verrait pas : seul ce qu'on voit rassure.
        placer(m, "marchand", "crypte", (5, 3))
        placer(m, "ilse", "echoppe", (3, 5))
        m.joueur.update(salle="echoppe", position=[4, 5])
        lire(m, "ilse")["besoins"]["securite"] = 40.0
        for confiance, signe in ((True, -1), (False, 1)):
            with self.subTest(fiable=confiance):
                essai = recharger(m)
                lier(essai, "ilse", "joueur", confiance, "vu")
                avant = lire(essai, "ilse")["besoins"]["securite"]
                essai, _ = vivre(essai, 1)
                ecart = lire(essai, "ilse")["besoins"]["securite"] - avant
                compagnie = 0.85 if confiance else 0.15
                attendu = (-SECURITE["lumiere"] - SECURITE["compagnie"] * compagnie
                           + (SECURITE["mefiance"] if not confiance else 0))
                self.assertAlmostEqual(ecart, attendu + 2 / 60, places=2)


class ProfilSecuriteTests(unittest.TestCase):
    def test_le_profil_nuance_les_valeurs_par_defaut(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Placement d'auteur : Ilse est surtout rassurée par la compagnie.
        m.objets["ilse"]["profil"]["securite"] = {"compagnie": 2}
        lire(m, "ilse")["besoins"]["securite"] = 40.0
        m = recharger(m)
        m, _ = vivre(m, 5)
        self.assertAlmostEqual(lire(m, "ilse")["besoins"]["securite"],
                               40.0 + 5 * (-SECURITE["lumiere"] - 2 * 0.85 + 2 / 60), places=2)
        profil = dict(m.objets["ilse"]["profil"])
        for invalide in ({"courage": 1}, {"noir": -1}, {"noir": "beaucoup"}):
            with self.assertRaises(AssertionError):
                verifier_profil(m, "ilse", {**profil, "securite": invalide})


if __name__ == "__main__":
    unittest.main()
