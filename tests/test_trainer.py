"""Traîner : deux positions atomiques, échéance persistée, passage commun."""
import unittest
from unittest.mock import patch
from donjon import corps, tenir, combat
from donjon.banc_pnj import creer, appliquer_etats
from donjon.commandes import analyser
from donjon.deplacement_objet import deplacer
from donjon.esprits import lire, percevoir_tous
from donjon.moteur import Moteur, proposition
from donjon.monde import ErreurMonde, objet
from donjon.passage import place
from donjon.rendu import regarder
from donjon.relations import se_mefie
from donjon.temps import instant
from tests.support import presentes, calme
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


def scene(scenario="relais"):
    m = presentes(creer(scenario, 1985, "fixe"))
    ids = [i for i, o in m.objets.items() if o["type"] == "personnage"]
    calme(m, *ids)
    salle = "antichambre" if scenario == "relais" else "salle_commune"
    if salle not in m.data["salles"]:
        salle = m.joueur["salle"]
    m.joueur.update(salle=salle, position=[3, 5], orientation="est")
    cible = "brune" if scenario == "relais" else "joss"
    for n, autre in enumerate(i for i in ids if i != cible):
        placer(m, autre, salle, (n, 1))
    placer(m, cible, salle, (2, 5))
    for i, o in m.objets.items():
        if o.get("lieu") == "joueur" and o.get("mobile"):
            deplacer(m, i, salle, (1, 1))
    corps.endormir(m, cible)
    percevoir_tous(m)
    return m, cible


class TrainerTests(unittest.TestCase):
    def test_diagonale_utilise_la_duree_du_pas_commun(self):
        m, c = scene("auberge")
        m.joueur["orientation"] = "nord-est"
        p = Moteur(m).preparer(proposition("trainer", c, "nord-est"))
        self.assertEqual(p.dixiemes, 64)
        debut = instant(m)
        Moteur(m).executer(p)
        m = recharger(m)
        self.assertEqual(instant(m) - debut, 64)
        self.assertEqual(place(m, c)[1], (3, 5))
        self.assertEqual(place(m, "joueur")[1], (4, 4))

    def test_joueur_commande_duree_positions_rendu_recharge(self):
        m, c = scene()
        for _ in range(2):
            debut, ancienne = instant(m), place(m, "joueur")
            p = Moteur(m).preparer(analyser(m, "traîner Brune vers est"))
            self.assertEqual(p.dixiemes, 45)
            texte = Moteur(m).executer(p)
            m = recharger(m)
            self.assertEqual(instant(m) - debut, 45)
            self.assertEqual(place(m, c), ancienne)
            self.assertEqual(m.joueur["orientation"], "est")
            self.assertIn("traîné", texte)
            self.assertTrue(m.data["journal"][-1]["reussite"])
            m.joueur["orientation"] = "ouest"
            self.assertIn("Brune", regarder(recharger(m)))
            self.assertFalse(corps.conscient(m, c))
            m.joueur["orientation"] = "est"

    def test_issue_atomique_meme_laps_decoupe(self):
        a, c = scene()
        tenir.commencer(a, "joueur", "trainer", c, "est")
        b = recharger(a)
        avant = place(b, c)
        passer(a, 45)
        for dt in (13, 17, 14):
            passer(b, dt)
            b = recharger(b)
            self.assertEqual(place(b, c), avant)
        passer(b, 1)
        a, b = recharger(a), recharger(b)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))

    def test_deces_aucune_contrainte_et_ligote_auberge(self):
        for scenario, mort in (("relais", True), ("auberge", False)):
            with self.subTest(scenario=scenario):
                m, c = scene(scenario)
                if mort:
                    corps.mourir(m, c)
                else:
                    corps.corps(m, c)["inconscient"] = 0
                    appliquer_etats(m, [c + ":ligote"])
                avant = place(m, "joueur")
                tenir.commencer(m, "joueur", "trainer", c, "est")
                g = m.data["gestes_en_cours"][-1]
                if mort:
                    self.assertEqual(g["temoins"], [])
                else:
                    self.assertTrue(any(s.get("operation") == "trainer" and s["type"] == "subi" for s in lire(m, c)["memoire"]))
                passer(m, 45)
                m = recharger(m)
                self.assertEqual(place(m, c), avant)
                self.assertEqual(m.objets[c]["type"], "depouille" if mort else "personnage")
                if not mort:
                    self.assertTrue(se_mefie(m, c, "joueur"))
                self.assertTrue(regarder(m))

    def test_refus_et_interruptions(self):
        for cause in ("libre", "occupe", "mains", "reveil", "inconscience", "coup", "deplace"):
            with self.subTest(cause=cause):
                m, c = scene()
                ancien = place(m, c)
                if cause == "libre":
                    corps.corps(m, c)["inconscient"] = 0
                elif cause == "occupe":
                    placer(m, "aubin", m.joueur["salle"], (4, 5))
                elif cause == "mains":
                    m.objets["outil_test"] = objet("outil_test", "outil", "outil", "joueur", mobile=True)
                if cause in ("libre", "occupe", "mains"):
                    with self.assertRaises(ErreurMonde) as r:
                        tenir.valider_trajet(m, "joueur", c, "est")
                    self.assertTrue(r.exception.attendu)
                    continue
                tenir.commencer(m, "joueur", "trainer", c, "est")
                passer(m, 20)
                if cause == "reveil":
                    corps.corps(m, c)["inconscient"] = instant(m)
                    corps.reveiller(m, c)
                elif cause == "inconscience":
                    corps.endormir(m, "joueur")
                elif cause == "coup":
                    placer(m, "aubin", m.joueur["salle"], (3, 6))
                    with patch.object(type(m), "d20", side_effect=[20, 1]):
                        combat.frapper(m, "aubin", "joueur")
                else:
                    m.joueur["position"] = [3, 1]
                m = recharger(m)
                passer(m, 25)
                m = recharger(m)
                self.assertEqual(place(m, c), ancien)
                self.assertFalse(any(e["type"] == "trainer" for e in m.data.get("historique_corps", [])))

    def test_pnj_meme_issue(self):
        m, c = scene()
        m.joueur["position"] = [7, 1]
        placer(m, "aubin", m.joueur["salle"], (3, 5))
        placer(m, c, m.joueur["salle"], (2, 5))
        for i, o in m.objets.items():
            if o.get("lieu") == "aubin" and o.get("mobile"):
                deplacer(m, i, m.joueur["salle"], (1, 1))
        m.objets["aubin"]["orientation"] = "est"
        tenir.commencer(m, "aubin", "trainer", c, "est")
        lire(m, "aubin")["libre"] = instant(m) + 45
        passer(m, 45)
        m = recharger(m)
        self.assertEqual(place(m, c)[1], (3, 5))
        self.assertEqual(place(m, "aubin")[1], (4, 5))

    def test_plusieurs_cases_et_seuil_reel_avec_temoin(self):
        m, c = scene()
        m.joueur.update(position=[1, 3], orientation="ouest")
        placer(m, c, "antichambre", (2, 3))
        placer(m, "aubin", "antichambre", (1, 4))
        m.objets["aubin"]["orientation"] = "nord"
        percevoir_tous(m)
        for _ in range(4):
            avant = place(m, "joueur")
            texte = Moteur(m).executer(Moteur(m).preparer(proposition("trainer", c, "ouest")))
            m = recharger(m)
            self.assertEqual(place(m, c), avant)
            self.assertIn("traîné", texte)
        self.assertEqual(m.joueur["salle"], "echoppe")
        self.assertEqual(m.objets[c]["lieu"], "echoppe")
        self.assertTrue(any(s.get("operation") == "trainer" and s["type"] == "vu_agir" for s in lire(m, "aubin")["memoire"]))
        self.assertTrue(se_mefie(m, "aubin", "joueur"))
        m.joueur["orientation"] = "est"
        self.assertIn("Brune", regarder(recharger(m)))

    def test_porte_fermee_et_rendu_ligote(self):
        m, c = scene("auberge")
        corps.corps(m, c)["inconscient"] = 0
        appliquer_etats(m, [c + ":ligote"])
        m.joueur.update(salle="cuisine", position=[2, 0], orientation="nord")
        placer(m, c, "cuisine", (2, 1))
        m.objets["porte_cellier"]["ouverte"] = False
        with self.assertRaises(ErreurMonde) as r:
            tenir.valider_trajet(m, "joueur", c, "nord")
        self.assertTrue(r.exception.attendu)
        m.objets["porte_cellier"]["ouverte"] = True
        texte = Moteur(m).executer(Moteur(m).preparer(proposition("trainer", c, "nord")))
        m = recharger(m)
        self.assertEqual(m.joueur["salle"], "cellier")
        self.assertIn("traîné", texte)
        m.joueur["orientation"] = "sud"
        self.assertIn("ligot", regarder(recharger(m)))

    def test_reddition_conservee_et_rotation_incluse(self):
        m, c = scene()
        corps.corps(m, c)["inconscient"] = 0
        corps.corps(m, c)["reddition"] = {"a": "joueur", "depuis": instant(m)}
        m.joueur["orientation"] = "nord"
        p = Moteur(m).preparer(proposition("trainer", c, "est"))
        self.assertEqual(p.dixiemes, 55)
        v = p.effets[0][2]
        tenir.commencer(m, "joueur", "trainer", c, "est", rotation_dixiemes=v["rotation_dixiemes"])
        avant = place(m, c)
        passer(m, 54)
        self.assertEqual(place(m, c), avant)
        passer(m, 1)
        m = recharger(m)
        self.assertEqual(place(m, c)[1], (3, 5))
        self.assertIn("reddition", corps.corps(m, c))

    def test_eau_obstacle_et_auteur_retenu(self):
        m, c = scene()
        m.joueur.update(position=[0, 3], orientation="ouest")
        placer(m, c, "antichambre", (1, 3))
        m.data["crue"] = {"depart_cm": 200, "tirage": {"minute_pic": 600, "hauteur_pic_cm": 200,
            "montee_cm_heure": 0, "baisse_cm_heure": 0}}
        with self.assertRaises(ErreurMonde) as r:
            tenir.valider_trajet(m, "joueur", c, "ouest")
        self.assertIn("noyé", str(r.exception))
        self.assertTrue(r.exception.attendu)
        m.data.pop("crue")
        m.joueur["position"] = [3, 5]
        placer(m, c, "antichambre", (2, 5))
        m.objets["bloc_test"] = objet("bloc_test", "bloc", "obstacle", "antichambre", bloque_passage=True,
                                    position=[4, 5], position_salle="antichambre")
        with self.assertRaises(ErreurMonde) as r:
            tenir.valider_trajet(m, "joueur", c, "est")
        self.assertTrue(r.exception.attendu)
        m.objets.pop("bloc_test")
        corps.corps(m, "joueur")["tenu_par"] = "aubin"
        with self.assertRaises(ErreurMonde) as r:
            tenir.valider_trajet(m, "joueur", c, "est")
        self.assertTrue(r.exception.attendu)

