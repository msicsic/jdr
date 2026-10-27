"""Fin d'un projet de déplacement : croyances du porteur, jamais positions distantes."""
import copy
import unittest

from donjon import agendas, eau, echanges, pnj
from donjon.esprits import croire, lire
from donjon.rendu import regarder as rendu
from donjon.temps import ecouler
from tests.test_engagement_deplacement import scene
from tests.test_social import placer
from tests.test_tensions import recharger


def declarer(m, cibles, destination):
    m.objets["marchand"]["profil"]["agendas"] = [
        {"id": "evacuer", "sorte": "amener",
         "parametres": {"qui": cibles, "lieu": destination}}]
    agendas.actualiser(m, "marchand")
    return recharger(m)


class FinAmenerTests(unittest.TestCase):
    def verifier_recharge(self, m):
        avant = copy.deepcopy(m.data)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual(rendu(n), rendu(m))
        agendas.verifier(n, "marchand")
        return n

    def test_arrivee_distante_ne_suffit_pas_puis_vue_ou_parole(self):
        for cible, destination, source in (("ilse", "chambre_cloche", "vu"),
                                           ("brune", "echoppe", "dit:brune")):
            with self.subTest(cible=cible, source=source):
                m, condition = scene(cible, destination)
                m = declarer(m, cible, destination)
                placer(m, cible, destination, [1, 3])
                self.assertTrue(echanges.tenu(m, cible, condition))
                agendas.actualiser(m, "marchand")
                m = self.verifier_recharge(m)
                self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "sommeil")
                croire(m, "marchand", cible, "lieu", destination, source,
                       salle=destination, case=[1, 3])
                agendas.actualiser(m, "marchand")
                m = self.verifier_recharge(m)
                a = agendas.projets(m, "marchand")[0]
                self.assertEqual((a["etat"], a["raison"]), ("atteint", "arrivee crue"))
                self.assertEqual(list(agendas.essayables(m, "marchand")), [])
                # Un état terminal ne renaît pas si la personne repart.
                croire(m, "marchand", cible, "lieu", "antichambre", "vu",
                       salle="antichambre", case=[3, 4])
                agendas.actualiser(m, "marchand")
                self.assertEqual(agendas.projets(self.verifier_recharge(m), "marchand")[0], a)

    def test_toutes_les_personnes_doivent_etre_crues_arrivees(self):
        m, _ = scene()
        m = declarer(m, ["ilse", "brune"], "chambre_cloche")
        for cible in ("ilse", "brune"):
            croire(m, "marchand", cible, "lieu", "chambre_cloche", "dit:" + cible,
                   salle="chambre_cloche", case=None)
            agendas.actualiser(m, "marchand")
            m = self.verifier_recharge(m)
            self.assertEqual(agendas.projets(m, "marchand")[0]["etat"],
                             "sommeil" if cible == "ilse" else "atteint")

    def test_noyade_crue_abandonne_sans_consulter_le_niveau_reel(self):
        for cible, destination in (("ilse", "chambre_cloche"), ("brune", "echoppe")):
            with self.subTest(cible=cible):
                m, _ = scene(cible, destination)
                self.assertFalse(eau.noyee(m, destination))
                m = declarer(m, cible, destination)
                croire(m, "marchand", destination, "eau", 300, "vu")
                agendas.actualiser(m, "marchand")
                m = self.verifier_recharge(m)
                a = agendas.projets(m, "marchand")[0]
                self.assertEqual((a["etat"], a["raison"]),
                                 ("abandonne", "destination crue noyee"))
                croire(m, "marchand", destination, "eau", 0, "vu")
                agendas.actualiser(m, "marchand")
                self.assertEqual(agendas.projets(self.verifier_recharge(m), "marchand")[0], a)

    def test_sans_sous_but_aucun_engagement_ni_transport_meme_laps_decoupe(self):
        m, _ = scene()
        m = declarer(m, ["ilse", "brune"], "chambre_cloche")
        for qui in ("marchand", "ilse", "brune", "aubin"):
            lire(m, qui)["libre"] = 1000000
        a, b = recharger(m), recharger(m)
        def avancer(n, dt):
            pnj.avancer(n, ecouler(n, dt), [], dt)
            agendas.actualiser(n, "marchand")
            return self.verifier_recharge(n)
        a = avancer(a, 3 * 600)
        for _ in range(6):
            b = avancer(b, 300)
        self.assertEqual(a.data, b.data)
        self.assertEqual(rendu(a), rendu(b))
        self.assertEqual(agendas.projets(a, "marchand")[0]["etat"], "sommeil")
        self.assertFalse(list(agendas.essayables(a, "marchand")))
        for qui in ("ilse", "brune"):
            self.assertFalse(agendas.en_cours(a, qui))
            self.assertEqual(a.objets[qui]["lieu"], m.objets[qui]["lieu"])
