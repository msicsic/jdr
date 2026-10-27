"""Sous-buts sociaux : demandes réelles et marches indépendantes après recharge."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, echanges, pnj, planification
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder as rendu
from donjon.temps import ecouler
from tests.test_agendas_amener_fin import declarer
from tests.test_engagement_deplacement import scene
from tests.test_avis_menace import relation
from tests.test_tensions import recharger


def prochain(m):
    avant = copy.deepcopy(m.data)
    with planification.vues_du_choix(m, "marchand"):
        resultat = agendas.planifier(m, "marchand", "evacuer")
        assert m.data == avant
    return resultat


class AmenerSocialTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(rendu(n), rendu(m))
        return n

    @patch("donjon.agendas._naissances", return_value=None)
    def test_deux_personnes_evacuations_successives_et_laps(self, _naissance):
        from tests.test_social import placer
        from tests.support import regarder
        for graine in (2024, 42):
            with self.subTest(graine=graine):
                m, _ = scene(graine=graine)
                # Isoler la coopération sociale de la recherche de clé : chacun
                # possède ici une route autonome vers la destination.
                m.objets["porte"].update(ouverte=True, verrouillee=False)
                from donjon.deplacement_objet import deplacer
                deplacer(m, "lanterne", "marchand")
                placer(m, "brune", "antichambre", [0, 1])
                regarder(m, "marchand", "brune")
                regarder(m, "brune", "marchand")
                for q in ("ilse", "brune"):
                    relation(m, q, "marchand", confiance=100, affection=100)
                    croire(m, "marchand", q, "lieu", "antichambre", "vu",
                           salle="antichambre", case=m.objets[q]["position"])
                m = declarer(m, ["ilse", "brune"], "chambre_cloche")
                lire(m, "aubin")["libre"] = 1000000
                a, b = self.recharge(m), self.recharge(m)
                def avancer(n, dt):
                    with patch.object(Monde, "d20", return_value=20):
                        pnj.avancer(n, ecouler(n, dt), [], dt)
                    return self.recharge(n)
                a = avancer(a, 10 * 600)
                for _ in range(20):
                    b = avancer(b, 300)
                self.assertEqual(a.data, b.data)
                for q in ("ilse", "brune"):
                    self.assertEqual(a.objets[q]["lieu"], "chambre_cloche",
                                     [(x["minute"], x["texte"]) for x in a.data["chronique"]
                                      if x["pnj"] == "marchand" and x["nature"] in ("social", "decision")])
                self.assertEqual(agendas.projets(a, "marchand")[0]["etat"], "atteint")
                demandes = [x["texte"] for x in a.data["chronique"]
                            if x["pnj"] == "marchand" and "demande à" in x["texte"] and "galerie" in x["texte"]]
                self.assertIn("Ilse", demandes[0])
                self.assertIn("Brune", demandes[1])

    def test_avis_de_menace_avant_demande(self):
        from tests.test_avis_menace import scene as menace
        from donjon.esprits import prevision
        m = menace()
        m.objets["aubin"]["profil"]["agendas"] = [
            {"id": "evacuer", "sorte": "amener", "parametres": {"qui": "ilse", "lieu": "chambre_cloche"}}]
        agendas.actualiser(m, "aubin")
        with planification.vues_du_choix(m, "aubin"):
            resultat = agendas.planifier(m, "aubin", "evacuer")
        etape = resultat[1][-1]
        self.assertEqual(etape["operation"], "dire")
        self.assertTrue(echanges.executer(m, "aubin", etape, []))
        m = self.recharge(m)
        self.assertEqual(prevision(m, "ilse", "antichambre")["source"], "dit:aubin")
        with planification.vues_du_choix(m, "aubin"):
            resultat = agendas.planifier(m, "aubin", "evacuer")
        self.assertEqual(resultat[1][-1]["operation"], "confier")

    @patch("donjon.agendas._naissances", return_value=None)
    def test_demande_accompagnement_et_marche_autonome_deux_destinations(self, _naissance):
        # Éprouver la marche convenue sans projet concurrent du destinataire.
        for cible, destination in (("ilse", "chambre_cloche"), ("brune", "echoppe")):
            with self.subTest(cible=cible):
                m, condition = scene(cible, destination)
                m = declarer(m, cible, destination)
                resultat = prochain(m)
                self.assertIsNotNone(resultat)
                etape = resultat[1][-1]
                self.assertEqual(etape["operation"], "confier")
                with patch.object(Monde, "d20", return_value=20):
                    self.assertTrue(echanges.executer(m, "marchand", etape, []))
                m = self.recharge(m)
                self.assertEqual(m.objets[cible]["lieu"], "antichambre")
                self.assertEqual(agendas.en_cours(m, cible)[0]["condition"], condition)
                accompagnement = prochain(m)
                self.assertIsNotNone(accompagnement)
                self.assertTrue(accompagnement[1])
                self.assertFalse(any(x["operation"] in ("prendre", "poser") and x["cible"] == cible
                                     for x in accompagnement[1]))
                # Le destinataire marche par son propre choix ; le porteur reste témoin.
                for q in ("marchand", "aubin", "ilse", "brune"):
                    if q != cible:
                        lire(m, q)["libre"] = 1000000
                a, b = self.recharge(m), self.recharge(m)
                def avancer(n, dt):
                    pnj.avancer(n, ecouler(n, dt), [], dt)
                    return self.recharge(n)
                a = avancer(a, 3 * 600)
                for _ in range(6):
                    b = avancer(b, 300)
                self.assertEqual(a.data, b.data)
                self.assertEqual(a.objets[cible]["lieu"], destination)
                croire(a, "marchand", cible, "lieu", destination, "dit:" + cible,
                       salle=destination, case=None)
                agendas.actualiser(a, "marchand")
                self.assertEqual(agendas.projets(self.recharge(a), "marchand")[0]["etat"], "atteint")

    def test_refus_mefiance_sommeil_sans_repetition_et_reveil(self):
        m, _ = scene()
        m = declarer(m, "ilse", "chambre_cloche")
        relation(m, "ilse", "marchand", confiance=0, affection=0)
        etape = prochain(m)[1][-1]
        self.assertFalse(echanges.executer(m, "marchand", etape, []))
        m = self.recharge(m)
        self.assertIsNone(prochain(m))
        a = agendas.projets(self.recharge(m), "marchand")[0]
        self.assertEqual((a["etat"], a["raison"]), ("sommeil", "refus mefiance"))
        self.assertEqual(list(agendas.essayables(m, "marchand")), [])
        self.assertFalse(agendas.en_cours(m, "ilse"))
        # Nouvelle croyance : réévaluation, mais un refus encore valable reste respecté.
        croire(m, "marchand", "brasero", "etat", {"allume": False}, "vu")
        self.assertTrue(list(agendas.essayables(m, "marchand")))
        self.assertIsNone(prochain(m))
        self.recharge(m)

    def test_faim_desesperee_prioritaire(self):
        m, _ = scene()
        m = declarer(m, "ilse", "chambre_cloche")
        lire(m, "marchand")["besoins"]["faim"] = 100
        candidats = list(deliberation._candidats(m, "marchand"))
        faim = next(c for c in candidats if c.besoin == "faim")
        agenda = next(c for c in candidats if c.besoin == "agenda")
        self.assertLess(faim.urgence.cle(), agenda.urgence.cle())
        self.recharge(m)

    def test_position_apprise_reveille_un_projet_sans_recours(self):
        m, _ = scene()
        m = declarer(m, "ilse", "chambre_cloche")
        croire(m, "marchand", "ilse", "lieu", None, "vu", salle=None, case=None)
        self.assertIsNone(prochain(m))
        m = self.recharge(m)
        self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "sommeil")
        croire(m, "marchand", "ilse", "lieu", "antichambre", "vu",
               salle="antichambre", case=m.objets["ilse"]["position"])
        self.assertTrue(list(agendas.essayables(m, "marchand")))
        self.assertIsNotNone(prochain(m))
        self.assertEqual(agendas.projets(self.recharge(m), "marchand")[0]["etat"], "actif")

    def test_abandon_annonce_invalide_seulement_aide_correspondante(self):
        for cible, destination in (("ilse", "chambre_cloche"), ("brune", "echoppe")):
            with self.subTest(cible=cible):
                m, condition = scene(cible, destination)
                with patch.object(Monde, "d20", return_value=20):
                    self.assertEqual(echanges.confier(m, "marchand", cible, condition), "accepte")
                e = lire(m, cible)["engagements"][0]
                e["annule"] = "impossible"
                # Pas de télépathie : seul le destinataire connaît encore l'abandon.
                self.assertIn(cible, lire(self.recharge(m), "marchand")["aides_attendues"])
                self.assertTrue(echanges.annoncer_abandon(m, cible, "marchand", condition, []))
                m = self.recharge(m)
                self.assertNotIn(cible, lire(m, "marchand")["aides_attendues"])
                self.assertTrue(deliberation.refus_retenu(m, "marchand", cible, ("confier",), cible))
