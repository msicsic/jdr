"""Abandon seulement sur une coupure prouvée par les croyances du porteur."""
import copy
import unittest

from donjon import agendas, planification, eau
from donjon.esprits import croire
from donjon.rendu import regarder as rendu
from tests.test_engagement_deplacement import scene
from tests.test_agendas_amener_fin import declarer
from tests.test_tensions import recharger


class AmenerRouteTests(unittest.TestCase):
    def test_route_crue_coupee_abandonnee_deux_destinations(self):
        for qui, destination in (("ilse", "chambre_cloche"), ("brune", "beffroi"), ("ilse", "echoppe")):
            m, _ = scene(qui, destination)
            m = declarer(m, qui, destination)
            for salle in m.data["salles"]:
                if salle not in ("antichambre", destination):
                    self.assertFalse(eau.noyee(m, salle))
                    croire(m, "marchand", salle, "eau", 300, "vu")
            # Une porte fermée n'est pas une preuve de coupure. L'échoppe
            # adjacente reste accessible malgré les salles lointaines noyées.
            avant = copy.deepcopy(m.data)
            with agendas.evaluation(m, "marchand", publier=False):
                agendas.actualiser(m, "marchand")
            self.assertEqual(m.data, avant)
            agendas.actualiser(m, "marchand")
            avant = copy.deepcopy(m.data)
            visible = rendu(m)
            m = recharger(m)
            self.assertEqual(m.data, avant)
            self.assertEqual(rendu(m), visible)
            a = agendas.projets(m, "marchand")[0]
            self.assertEqual(a["etat"], "abandonne" if destination != "echoppe" else "sommeil")
            if destination != "echoppe":
                self.assertEqual(a["raison"], "route crue coupee")
                for salle in m.data["salles"]:
                    croire(m, "marchand", salle, "eau", 0, "vu")
                agendas.actualiser(m, "marchand")
                self.assertEqual(agendas.projets(recharger(m), "marchand")[0], a)
            self.assertEqual(rendu(m), rendu(recharger(m)))

