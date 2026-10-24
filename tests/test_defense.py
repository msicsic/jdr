"""4c : conséquences, perception et sauvegarde sur la chaîne de jeu entière."""
import copy
from itertools import cycle, product
import unittest
from unittest.mock import patch

from donjon import combat, corps, defense, planification, spatial
from donjon.esprits import lire, percevoir_tous, croire
from donjon.esprits import memoriser
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder, fiche
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
    # Ces scènes fixent les jets de combat ; les confidences matérielles ordinaires
    # (test_constats_partages) ne doivent pas consommer ces jets préparés.
    @patch("donjon.social._constats", return_value=())
    def test_epreuve_et_autre_victime_fuient_protecteur_entend_et_intervient(self, _constats):
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
            vue = " ".join(regarder(m).split())
            self.assertNotIn("sans connaissance", vue)
            self.assertNotIn(m.objets[cible]["nom"], vue)
            self.assertIn(m.objets["brune"]["nom"], vue)

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
            self.assertIn("a cessé de résister", " ".join(regarder(m).split()))

    @patch("donjon.social._constats", return_value=())
    def test_riposte_reelle_a_douceur_100_et_protection_par_la_vue(self, _constats):
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
            vue = " ".join(regarder(m).split())
            self.assertIn("sans connaissance" if not corps.conscient(m, "brune") else "blessé", vue)

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
                        self.assertIn(m.data["salles"][m.joueur["salle"]]["nom"].upper(), regarder(m).upper())
                    elif action == "se_rendre":
                        self.assertEqual(corps.corps(m, "joueur")["reddition"]["a"], auteur)
                        self.assertIn("cesses de résister", texte)
                        self.assertIn("a cessé de résister", fiche(m))
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

    def test_le_danger_percu_est_fourni_au_mj_et_au_joueur_sans_identite_devinee(self):
        from donjon.noms import apprendre
        for auteur in ("brune", "marchand"):
            m = joueur_attaque(auteur)
            apprendre(m, "joueur", auteur)
            m = recharger(m)
            # Le fait vu avec son auteur : sans lui, le MJ concluait que personne n'attaquait.
            self.assertEqual(m.contexte()["joueur"]["dangers_percus"],
                             [{"auteur": auteur, "geste": "frapper", "contre": "joueur", "il_y_a_minutes": 0}])
            self.assertIn("Danger perçu :", fiche(m))
            self.assertIn(m.objets[auteur]["nom"].split(",")[0], fiche(m))
            # Même auteur, mais un coup qu'il ne voit pas : la préparation ne livre aucun nom.
            m = scene()
            if auteur == "marchand":
                placer(m, "brune", "echoppe", (3, 3))
                m.joueur["position"] = [2, 5]
            m.joueur["orientation"] = "ouest"
            percevoir_tous(m)
            with patch.object(type(m), "d20", return_value=20):
                combat.frapper(m, auteur, "joueur")
            m = recharger(m)
            self.assertNotIn("dangers_percus", m.contexte()["joueur"])
            self.assertNotIn("Danger perçu :", fiche(m))

    def test_fuite_interrompue_par_inconscience_ne_repart_pas_au_reveil(self):
        for auteur, par_porte in product(("brune", "marchand"), (False, True)):
            m = scene()
            if auteur == "marchand":
                placer(m, "brune", "echoppe", (3, 3))
                placer(m, auteur, "antichambre", (2, 5))
            if par_porte:
                m.joueur.update(salle="beffroi", position=[0, 3], orientation="ouest")
                placer(m, auteur, "beffroi", (1, 3))
                m.objets["porte"].update(ouverte=False, verrouillee=False)
            salle_depart = m.joueur["salle"]
            # Fixture d'un geste commandé : aucun choix autonome de ce PNJ pendant l'épreuve.
            for x in ("brune", "marchand", "aubin", "ilse"):
                m.objets[x].pop("profil")
                lire(m, x)["intention"] = None
                lire(m, x)["pulsions"] = []
                lire(m, x)["besoins"] = {b: v for b, v in lire(m, x)["besoins"].items()
                                          if b in ("faim", "repos", "chaleur")}
            e = lire(m, auteur)
            e.update(libre=0, veille=None, eveil=1, intention={"but": {"type": "frapper", "qui": "joueur"},
                     "motif": "securite", "depuis": 0, "attente": 0,
                     "plan": [{"operation": "assommer", "cible": "joueur", "outil": "", "lieu": "", "condition": ""}]})
            m.data.setdefault("exploration", {}).setdefault(salle_depart, []).append([0, 3])
            percevoir_tous(m)
            p = Moteur(m).preparer(proposition("fuir", "ouest" if par_porte else ""))
            with patch.object(type(m), "d20", return_value=20):
                texte = Moteur(m).executer(p)
            m = recharger(m)
            self.assertIn("Tu reviens à toi.", texte)
            self.assertTrue(corps.conscient(m))
            self.assertEqual(m.joueur["salle"], salle_depart)
            self.assertFalse(m.data["journal"][-1]["reussite"])
            self.assertIn(m.data["salles"][salle_depart]["nom"].upper(), regarder(m).upper())

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
            self.assertIn("a cessé de résister", " ".join(regarder(m).split()))

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
            self.assertNotIn("sans connaissance", " ".join(regarder(m).split()))

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


class CriUniqueTests(unittest.TestCase):
    """Fusion 4c : un cri reconnu d'un protégé est un seul bruit et une seule inquiétude."""

    def test_un_cri_de_protege_inquiete_une_fois_et_se_retient_une_fois(self):
        from donjon import ouie
        from donjon.deliberation import taux
        from donjon.esprits import percoit
        from donjon.temps import instant
        from donjon.voix import RECONNUE, reconnaitre
        for cible in ("aubin", "ilse"):
            m = scene(cible, False)
            self.assertFalse(percoit(m, "marchand", cible))
            self.assertEqual(reconnaitre(m, "marchand", cible)[1], RECONNUE)
            lire(m, "marchand")["besoins"]["securite"] = 10.0
            niveau = ouie.SEUIL + 2
            ouie.entendre(m, "marchand", cible, "antichambre", (3, 5), "cri", instant(m), niveau)
            m = recharger(m)
            e = lire(m, "marchand")
            attendu = 10.0 + taux(m, "marchand", "bruit") * niveau / ouie.INTENSITES["appel"]
            self.assertAlmostEqual(e["besoins"]["securite"], attendu)
            bruits = [s for s in e["memoire"] if s["type"] == "bruit" and s["salle"] == "antichambre"]
            self.assertEqual(len(bruits), 1)
            self.assertEqual(bruits[0].get("qui"), cible)
            self.assertEqual(sum(s["type"] == "secours" and s["qui"] == cible for s in e["memoire"]), 1)
            self.assertEqual(defense.protection(m, "marchand")[:2], (cible, "antichambre"))


class DangerDitAuMjTests(unittest.TestCase):
    """Fusion 4c : ce que le MJ et la contre-revue lisent d'un danger et d'une réaction du joueur."""

    def test_fait_du_danger_et_sens_des_reactions_apres_rechargement(self):
        for auteur in ("brune", "marchand"):
            for connu in (True, False):
                m = joueur_attaque(auteur)
                # La scène présente tout le monde ; sinon, Corvus n'a jamais entendu son nom.
                if not connu:
                    m.data["noms_connus"].remove(auteur)
                m = recharger(m)
                danger = m.contexte()["joueur"]["dangers_percus"]
                self.assertEqual(len(danger), 1)
                self.assertEqual((danger[0]["geste"], danger[0]["contre"]), ("frapper", "joueur"))
                nom = m.objets[auteur]["nom"].split(",")[0]
                if connu:
                    self.assertEqual(danger[0]["auteur"], auteur)
                else:
                    # Un agresseur dont Corvus ignore le nom : sa désignation, jamais son nom ni son identifiant.
                    self.assertTrue(danger[0]["auteur"].startswith("personne_"))
                    self.assertNotIn(nom, str(m.contexte()["joueur"]))
                titres = {}
                for action in ("riposter", "se_rendre", "fuir"):
                    plan = Moteur(m).preparer(proposition(action))
                    titres[action] = " ".join(plan.titre.split())
                    self.assertEqual(nom in titres[action], connu)
                    self.assertIn("qui t'a agressé", titres[action])
                self.assertTrue(titres["riposter"].startswith("Te défendre : riposter contre "))
                self.assertIn("c'est toi qui cesses de résister", titres["se_rendre"])
                self.assertTrue(titres["fuir"].startswith("Fuir "))


class ForcerNEstPasAgresserTests(unittest.TestCase):
    """Forcer un contenant emploie le geste ``frapper``, mais sur une chose : c'est un geste illicite
    contre son propriétaire, pas une violence contre une personne (``pnj.est_contrainte``). Cas réel :
    Relais 1985, 12 h, minute 690, Aubin force la réserve de Gorm au refuge ; Brune, Ilse et Gorm,
    le croyant dangereux, fuyaient dans la conduite noire puis revenaient à la lumière, des centaines
    de fois par heure."""

    def scene(self, temoin):
        from tests.test_petits_correctifs import ForcerTests
        m = ForcerTests.brune_aux_vannes(None, douceur=60)
        placer(m, "brune", "antichambre", (6, 3))
        for i, id in enumerate(sorted({"marchand", "ilse", "aubin"} - {temoin})):
            placer(m, id, "beffroi", (2 + i, 3))
        placer(m, temoin, "antichambre", (6, 5))
        orienter(m, temoin, "brune")
        percevoir_tous(m)
        lire(m, "brune")["besoins"]["faim"] = 96.0  # Au-delà du désespoir : un témoin ne la retient plus.
        # Cette scène porte sur l'effraction observée : un marché ne la remplace pas.
        from donjon import relations
        lire(m, "marchand")["relations"]["brune"] = relations._nouvelle({"confiance": 10})
        return recharger(m)

    def test_un_temoin_de_l_effraction_ne_la_fuit_pas(self):
        # Ilse, témoin d'un tort fait à un tiers ; Gorm, témoin du tort fait à son propre bien.
        for temoin in ("ilse", "marchand"):
            with self.subTest(temoin=temoin):
                m = self.scene(temoin)
                vu = False
                for _ in range(6):
                    passer(m, MINUTE)
                    m = recharger(m)
                    vu = vu or any(s["type"] == "vu_agir" and s["auteur"] == "brune" and s["operation"] == "frapper"
                                   and s["objet"] == "reserve" for s in lire(m, temoin)["memoire"])
                    self.assertNotIn("violence", lire(m, temoin)["croyances"].get("brune", {}))
                    self.assertEqual(defense.dangers(m, temoin), [])
                    self.assertNotIn((lire(m, temoin)["intention"] or {}).get("but", {}).get("type"),
                                     ("fuir", "riposter", "reddition"))
                self.assertTrue(vu)   # Il l'a bien vue forcer : un geste illicite, retenu comme tel.
                self.assertFalse([e for e in m.data.get("historique_corps", [])
                                  if e["id"] == temoin and e["type"] in ("fuite", "riposte", "reddition")])
