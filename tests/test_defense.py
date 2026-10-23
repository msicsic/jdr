"""4c : conséquences, perception et sauvegarde sur la chaîne de jeu entière."""
import copy
from itertools import cycle
import unittest
from unittest.mock import patch

from donjon import combat, corps, defense, planification, spatial
from donjon.esprits import lire, percevoir_tous, croire
from donjon.esprits import memoriser
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.temps import MINUTE
from tests.support import regarder as orienter
from tests.test_combat import scene
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


def epreuve(cible="aubin"):
    m = scene(cible, False)
    placer(m, "ilse", "antichambre", (3, 4))
    orienter(m, "ilse", "brune")
    percevoir_tous(m)
    with patch.object(type(m), "d20", side_effect=[20, 1]):
        combat.frapper(m, "brune", cible)
    return m


def joueur_attaque(auteur="brune"):
    m = scene("marchand", False)
    if auteur == "marchand":
        placer(m, "brune", "echoppe", (3, 3))
        m.joueur["position"] = [2, 5]
    m.joueur["orientation"] = "est"
    m.data.setdefault("exploration", {}).setdefault("antichambre", []).append([0, 3])
    percevoir_tous(m)
    with patch.object(type(m), "d20", side_effect=[20, 1]):
        combat.frapper(m, auteur, "joueur")
    return m


class DefenseTests(unittest.TestCase):
    def test_epreuve_et_autre_victime_fuient_protecteur_entend_et_intervient(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            self.assertIn("brune", defense.dangers(m, cible))
            self.assertEqual(defense.protection(m, "marchand")[:2], (cible, "antichambre"))
            passer(m, 5 * MINUTE)
            m = recharger(m)
            h = m.data["historique_corps"]
            self.assertTrue(any(e["type"] == "fuite" and e["id"] == cible for e in h))
            self.assertTrue(any(e["type"] == "intervention" and e["id"] == "marchand" for e in h))
            self.assertFalse(defense.dangers(m, cible))
            self.assertFalse(m.data.get("defunts"))
            self.assertNotIn("sans connaissance", regarder(m))

    def test_meme_laps_bloc_ou_decoupe_recharge_epreuve_et_autre_victime(self):
        for cible in ("aubin", "ilse"):
            a = epreuve(cible)
            b = recharger(a)
            passer(a, 5 * MINUTE)
            for dt in (13, 587, 111, 73, 1216, 1000):
                passer(b, dt)
                b = recharger(b)
            a = recharger(a)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))

    def test_aucun_nom_d_agresseur_apres_surprise_ou_cri_inconnu(self):
        for cible in ("aubin", "marchand"):
            m = scene(cible, True)
            with patch.object(type(m), "d20", return_value=20):
                combat.frapper(m, "brune", cible, methode="assommer")
            m = recharger(m)
            self.assertNotIn("brune", defense.dangers(m, cible))
            self.assertIsNone(next(s for s in lire(m, cible)["memoire"] if s["type"] == "subi")["auteur"])
            self.assertIn("sans connaissance", regarder(m))

    def test_prix_unique_defense_douceur_100_et_reddition_double(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            m.objets[cible]["profil"]["valeurs"]["douceur"] = 100
            self.assertEqual(combat.prix_violence(m, cible, "securite", defense=True), 0)
            self.assertIsNone(combat.prix_violence(m, cible, "securite"))
            defense.se_rendre(m, cible, "brune", [])
            self.assertEqual(combat.prix_violence(m, "brune", rendu=True), 2 * combat.prix_violence(m, "brune"))
            m = recharger(m)
            self.assertIn("a cessé de résister", regarder(m))

    def test_riposte_reelle_a_douceur_100_et_protection_par_la_vue(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            m.objets[cible]["profil"]["valeurs"]["douceur"] = 100
            # Fixture de lieu sans passage : aucune fuite n'est inventée par le graphe.
            m.data["salles"]["antichambre"]["sorties"] = {}
            m.data["salles"]["echoppe"]["sorties"].pop("est")
            avant = corps.pv(m, "brune")
            with patch.object(type(m), "d20", side_effect=cycle([20, 1])):
                passer(m, MINUTE)
            m = recharger(m)
            self.assertTrue(any(e["type"] == "riposte" and e["id"] == cible for e in m.data["historique_corps"]))
            self.assertLess(corps.pv(m, "brune"), avant)
            self.assertFalse(m.data.get("defunts"))
            self.assertTrue(regarder(m))

    def test_joueur_fiches_et_issues_reelles_apres_rechargement(self):
        for auteur in ("brune", "marchand"):
            for action in ("fuir", "riposter", "se_rendre"):
                with self.subTest(auteur=auteur, action=action):
                    m = joueur_attaque(auteur)
                    # La fiche ne décide rien pour le joueur ni pour les autres.
                    avant = copy.deepcopy(m.data)
                    p = Moteur(m).preparer(proposition(action))
                    self.assertTrue(p.confirmation)
                    self.assertTrue(p.resume(m))
                    self.assertEqual(m.data, avant)
                    texte = Moteur(m).executer(p)
                    m = recharger(m)
                    if action == "fuir":
                        self.assertNotEqual(m.joueur["salle"], "antichambre")
                        self.assertIn("autre salle", texte)
                    elif action == "se_rendre":
                        self.assertEqual(corps.corps(m, "joueur")["reddition"]["a"], auteur)
                        self.assertIn("cesses de résister", texte)
                    else:
                        self.assertIn("frappes", texte)
                    self.assertFalse(m.data.get("defunts"))
                    self.assertTrue(regarder(m))

    def test_refus_avec_attendu_sans_danger_et_sans_prise(self):
        m = scene()
        for action in ("riposter", "se_rendre", "degager"):
            with self.assertRaises(ErreurMonde) as cm:
                Moteur(m).preparer(proposition(action))
            self.assertTrue(cm.exception.attendu)

    def test_reddition_autonome_acculer_deux_victimes_grievement_blessees(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            m.data["salles"]["antichambre"]["sorties"] = {}
            m.data["salles"]["echoppe"]["sorties"].pop("est")
            m.objets[cible]["profil"]["valeurs"]["douceur"] = 99
            m.objets[cible]["pv"] = 2
            if cible != "ilse":
                placer(m, "ilse", "echoppe", (4, 4))
                percevoir_tous(m)
            self.assertEqual(defense.choisir(m, cible)[0]["type"], "reddition")
            passer(m, 100)
            m = recharger(m)
            self.assertEqual(corps.corps(m, cible)["reddition"]["a"], "brune")
            self.assertIn("a cessé de résister", regarder(m))

    def test_se_degager_de_deux_auteurs_par_la_regle_commune(self):
        for auteur in ("brune", "marchand"):
            m = joueur_attaque(auteur)
            corps.corps(m, "joueur")["tenu_par"] = auteur
            p = Moteur(m).preparer(proposition("degager"))
            with patch.object(type(m), "d20", side_effect=cycle([20, 1])):
                texte = Moteur(m).executer(p)
            m = recharger(m)
            self.assertFalse(corps.corps(m, "joueur").get("tenu_par"))
            self.assertIn("te dégages", texte)
            self.assertTrue(regarder(m))

    def test_protecteur_voyant_intervient_sans_interdit_a_douceur_100(self):
        for cible in ("aubin", "ilse"):
            m = scene(cible, False)
            placer(m, "marchand", "antichambre", (3, 4))
            orienter(m, "marchand", "brune")
            m.objets["marchand"]["profil"]["valeurs"]["douceur"] = 100
            percevoir_tous(m)
            with patch.object(type(m), "d20", side_effect=[20, 1]):
                combat.frapper(m, "brune", cible)
            with patch.object(type(m), "d20", side_effect=cycle([20, 1])):
                passer(m, 100)
            m = recharger(m)
            self.assertTrue(any(e["type"] == "intervention" and e.get("contre") == "brune"
                                for e in m.data["historique_corps"]))
            self.assertFalse(m.data.get("defunts"))
            self.assertTrue(regarder(m))

    def test_danger_expire_et_reddition_cesse_si_la_personne_refrappe(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            defense.se_rendre(m, cible, "brune", [])
            self.assertTrue(corps.corps(m, cible).get("reddition"))
            m.data["dixiemes"] = combat.COUP
            with patch.object(type(m), "d20", return_value=1):
                combat.frapper(m, "brune", cible)
            m = recharger(m)
            self.assertFalse(corps.corps(m, cible).get("reddition"))
            m.data["minutes"] = defense.RECENT + 1
            self.assertFalse(defense.dangers(m, cible))

    def test_memoire_graphes_et_certificat_reactions_sont_controles(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            with patch.object(planification, "VERIFIER", True), patch.object(spatial, "VERIFICATION", 1):
                for _ in range(3):
                    self.assertIsNotNone(defense.choisir(m, cible))
                croire(m, cible, "brune", "etat", {"conscient": False}, "vu")
                self.assertFalse(defense.dangers(m, cible))
            m = recharger(m)
            self.assertTrue(regarder(m))

    def test_causes_percues_hors_recit_borne_et_pas_de_guerre_entre_defenseurs(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            temoin = "ilse" if cible == "aubin" else "marchand"
            if temoin == "marchand":
                placer(m, temoin, "antichambre", (2, 4))
                orienter(m, temoin, "brune")
                percevoir_tous(m)
                memoriser(m, temoin, {"type": "vu_agir", "auteur": "brune", "operation": "frapper",
                                     "objet": cible, "victime": cible})
            for _ in range(60):
                memoriser(m, temoin, {"type": "parcouru", "salle": "antichambre"})
            memoriser(m, temoin, {"type": "vu_agir", "auteur": cible, "operation": "frapper",
                                 "objet": "brune", "victime": "brune"})
            m = recharger(m)
            self.assertIn("brune", defense.auteurs(m, temoin))
            self.assertNotIn(cible, defense.auteurs(m, temoin))
            corps.endormir(m, "brune")
            percevoir_tous(m)
            corps.reveiller(m, "brune")
            m = recharger(m)
            self.assertNotIn("brune", defense.dangers(m, temoin))
            self.assertTrue(regarder(m))

    def test_un_coup_garde_sa_duree_meme_interrompu_et_recharge(self):
        for cible in ("aubin", "ilse"):
            m = epreuve(cible)
            combat.interrompre(m, "brune")
            m = recharger(m)
            with self.assertRaises(ErreurMonde) as cm:
                combat.frapper(m, "brune", cible)
            self.assertTrue(cm.exception.attendu)
            self.assertEqual(lire(m, "brune")["libre"], combat.COUP)
            self.assertTrue(regarder(m))
