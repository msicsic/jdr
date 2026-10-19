"""Jalon I1 : le corps commun à tous — faim, froid, fatigue — et la part demandée par le joueur.

Chaque test vérifie l'état du monde et, quand le joueur est concerné, ce qu'il lit, après
rechargement.
"""
import copy
import unittest
from unittest.mock import patch

from donjon import corps
from donjon.deliberation import verifier_profil
from donjon.deplacement_objet import deplacer
from donjon.echanges import demander
from donjon.esprits import lire
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.rendu import fiche
from tests.support import calme
from tests.test_tensions import placer, recharger, relais, vivre


def executer(monde, p, jet=None):
    if jet is None:
        texte = Moteur(monde).executer(Moteur(monde).preparer(p))
    else:
        with patch.object(Monde, "d20", return_value=jet):
            texte = Moteur(monde).executer(Moteur(monde).preparer(p))
    return recharger(monde), texte


class ModeleCommunTests(unittest.TestCase):
    def test_le_scenario_declare_des_etats_dont_decoule_la_faim(self):
        m = relais()
        # Brune n'a pas mangé depuis la veille : 800 minutes à 6 par heure.
        self.assertEqual(m.objets["brune"]["corps"]["repas"], 800)
        self.assertAlmostEqual(lire(m, "brune")["besoins"]["faim"], 80.0)
        self.assertAlmostEqual(lire(m, "aubin")["besoins"]["chaleur"], 65.0)
        self.assertNotIn("faim", m.objets["brune"]["profil"]["besoins"])
        # Le profil règle le caractère, pas le corps.
        profil = copy.deepcopy(m.objets["brune"]["profil"])
        profil["besoins"]["faim"] = {"depart": 10, "derive_heure": 1, "urgence": 50}
        with self.assertRaises(AssertionError):
            verifier_profil(m, "brune", profil)

    def test_une_ancienne_partie_garde_ses_valeurs(self):
        m = relais()
        ancien = copy.deepcopy(m.data)
        for id in ("brune", "ilse"):
            ancien["objets"][id].pop("corps")
            ancien["objets"][id]["profil"]["besoins"]["faim"] = {"depart": 80, "derive_heure": 6, "urgence": 70}
            ancien["esprits"][id]["besoins"].pop("faim")
        reprise = Monde(ancien)
        self.assertNotIn("faim", reprise.objets["brune"]["profil"]["besoins"])
        self.assertEqual(lire(reprise, "brune")["besoins"]["faim"], 80.0)

    def test_l_effort_creuse_le_feu_rechauffe_et_seche(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, "brune")["besoins"].update(faim=0.0, repos=0.0)
        corps.vivre(m, "brune", 60)
        repos = dict(lire(m, "brune")["besoins"])
        lire(m, "brune")["besoins"].update(faim=0.0, repos=0.0)
        corps.vivre(m, "brune", 60, effort=True)
        self.assertAlmostEqual(lire(m, "brune")["besoins"]["faim"], repos["faim"] * corps.EFFORT, places=2)
        # Trempée loin du feu, le froid monte vite ; dans l'échoppe du brasero, il baisse, et
        # au bout d'une demi-heure au chaud, elle est sèche.
        placer(m, "brune", "chambre_cloche", (1, 3))
        lire(m, "brune")["besoins"]["chaleur"] = 50.0
        corps.vivre(m, "brune", 60)
        self.assertAlmostEqual(lire(m, "brune")["besoins"]["chaleur"], 60.0, places=2)
        placer(m, "brune", "echoppe", (3, 5))
        corps.vivre(m, "brune", 30)
        m = recharger(m)
        self.assertEqual(lire(m, "brune")["besoins"]["chaleur"], 0.0)
        self.assertEqual(m.objets["brune"]["corps"]["trempe"], 0)


class JoueurTests(unittest.TestCase):
    def test_le_temps_et_l_effort_se_lisent_sur_la_fiche(self):
        m = relais()
        self.assertIn("Faim : légère", fiche(m))
        corps.valeurs(m, "joueur")["faim"] = 69.5
        m, texte = executer(m, proposition("attendre"))
        self.assertIn("Tu as faim.", texte)
        self.assertIn("Faim : pressante", fiche(m))
        self.assertEqual(m.contexte()["joueur"]["corps"]["faim"], "pressante")
        self.assertNotIn("besoins", m.contexte()["joueur"])

    def test_attendre_repose(self):
        m = relais()
        corps.valeurs(m, "joueur")["repos"] = 50.0
        m, _ = executer(m, proposition("attendre"))
        self.assertAlmostEqual(corps.valeurs(m, "joueur")["repos"], 50.0 - 5 * corps.REPOS_MINUTE)

    def test_un_etat_pressant_coute_aux_jets_physiques(self):
        m = relais()
        m.joueur.update(salle="echoppe", position=[3, 5])
        corps.valeurs(m, "joueur").update(faim=80.0, repos=85.0)
        self.assertEqual(corps.malus(m, "DEX"), -2 * corps.MALUS)
        self.assertEqual(corps.malus(m, "INT"), 0)
        # Un sifflement n'a pas de jet ; un vol discret sous les yeux de Gorm en a un.
        deplacer(m, "bois", "echoppe")
        placer(m, "bois", "echoppe", (4, 5))
        placer(m, "marchand", "echoppe", (2, 5))
        plan = Moteur(m).preparer(sequence(etape("deplacer", "bois", "joueur", methode="discret")))
        self.assertIn("faim, froid ou fatigue -4", plan.resume(m))
        _, texte = executer(m, sequence(etape("deplacer", "bois", "joueur", methode="discret")), jet=10)
        self.assertIn("+ corps(-4)", texte)

    def test_l_extreme_affaiblit_sans_tuer(self):
        m = relais()
        corps.valeurs(m, "joueur")["faim"] = 99.0
        m.joueur["pv"] = 3
        for _ in range(12 * 4):
            m, texte = executer(m, proposition("attendre"))
        self.assertEqual(m.joueur["pv"], 1)

    def test_manger_ce_qui_est_a_soi_et_pas_le_bien_d_autrui(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[7, 3])
        m.objets["reserve"].update(verrouillee=False, ouverte=True)
        with self.assertRaisesRegex(ErreurMonde, "appartient à autrui"):
            Moteur(m).preparer(sequence(etape("manger", "vivres")))
        # Placement d'auteur : Gorm a donné les vivres au joueur.
        m.objets["vivres"]["proprietaire"] = "joueur"
        corps.valeurs(m, "joueur")["faim"] = 75.0
        m, texte = executer(m, sequence(etape("manger", "vivres")))
        self.assertIn("Tu manges une part des vivres du refuge.", texte)
        self.assertEqual(m.objets["vivres"]["portions"], 3)
        self.assertLess(corps.valeurs(m, "joueur")["faim"], 75.0 - corps.SATIETE + 1)


class PartDuJoueurTests(unittest.TestCase):
    def test_gorm_accepte_et_sert_le_joueur_la_ou_sont_les_vivres(self):
        m = calme(relais(), "brune", "ilse", "aubin")
        lire(m, "marchand")["besoins"].update(faim=0.0)
        m.joueur.update(salle="antichambre", position=[6, 4])
        corps.valeurs(m, "joueur")["faim"] = 80.0
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "joueur", "marchand", "vivres"), "promis")
        m, lignes = vivre(m, 15)
        self.assertEqual(m.objets["vivres"]["portions"], 3)
        self.assertLess(corps.valeurs(m, "joueur")["faim"], 80.0 - corps.SATIETE + 5)
        self.assertIn("Gorm te sert une part des vivres du refuge ; tu manges.", lignes)
        self.assertEqual(lire(m, "marchand")["engagements"], [])

    def test_on_demande_une_part_sans_l_avoir_vue(self):
        from donjon.paroles import preparer_parole
        m = relais()
        m.joueur.update(salle="echoppe", position=[1, 2])
        # Les vivres sont dans la réserve verrouillée : le joueur ne les a jamais vus.
        self.assertNotIn("vivres", m.data["connus"])
        p = {"personnage": "marchand", "replique": "Gorm, peux-tu me donner une part de vivres ?",
             "contenu": [{"type": "demande", "sujet": "vivres", "attribut": "", "valeur": ""}]}
        with patch.object(Monde, "d20", return_value=20):
            travail, rapport = preparer_parole(m, p)
        self.assertIn("il te la servira là où sont les vivres", rapport["faits"][0])
        self.assertEqual([x["condition"] for x in lire(recharger(travail), "marchand")["engagements"]],
                         [{"objet": "vivres", "servir": "joueur"}])
        # Ce qui n'est pas une ressource à lui reste soumis à la règle : on ne nomme que ce qu'on connaît.
        p["replique"], p["contenu"][0]["sujet"] = "Gorm, donne-moi les crochets.", "crochets"
        with self.assertRaises(ErreurMonde):
            preparer_parole(m, p)

    def test_une_part_de_bois_entretient_le_feu(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        corps.valeurs(m, "joueur")["chaleur"] = 60.0
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "joueur", "marchand", "bois"), "promis")
        self.assertIn({"objet": "brasero", "allume": True},
                      [x["condition"] for x in lire(recharger(m), "marchand")["engagements"]])


if __name__ == "__main__":
    unittest.main()
