"""Lot 148 : évaluer les candidats d'un choix ne publie aucune transition."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, planification, spatial
from donjon.crue import nouvelle_crue
from donjon.esprits import croire
from donjon.rendu import regarder as rendu
from tests.test_agendas_activation import declarer
from tests.test_agendas_amener_fin import declarer as amener
from tests.test_avis_menace import scene
from tests.test_engagement_deplacement import scene as scene_marche
from tests.test_tensions import recharger


class EvaluationAgendaTests(unittest.TestCase):
    def test_crue_42_premier_choix_ne_modifie_pas_la_photographie(self):
        m = nouvelle_crue(42, depart="fixe")
        spatial.installer(m)
        with patch.object(planification, "VERIFIER", True):
            deliberation.choisir(m, "marchand", 0)
        a = agendas.projets(m, "marchand")[0]
        self.assertEqual((a["etat"], a["raison"]), ("sommeil", "contenu non cru"))
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(rendu(n), rendu(m))

    def test_devis_isole_sans_transition_et_choix_interrompu_sans_trace(self):
        m = declarer(scene())
        croire(m, "aubin", "ilse", "lieu", None, "vu", salle=None, case=None)
        avant = copy.deepcopy(m.data)
        self.assertIsNone(agendas.planifier(m, "aubin", "a1"))
        self.assertEqual(m.data, avant)
        with self.assertRaisesRegex(RuntimeError, "interrompu"):
            with planification.vues_du_choix(m, "aubin"):
                self.assertIsNone(agendas.planifier(m, "aubin", "a1"))
                self.assertEqual(m.data, avant)
                raise RuntimeError("interrompu")
        self.assertEqual(m.data, avant)
        with patch.object(planification, "VERIFIER", True):
            with planification.vues_du_choix(m, "aubin"):
                self.assertIsNone(agendas.planifier(m, "aubin", "a1"))
                self.assertEqual(m.data, avant)
        self.assertEqual(agendas.projets(m, "aubin")[0]["etat"], "sommeil")
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(rendu(n), rendu(m))

    def test_activation_et_fin_amener_differees_et_imbrication(self):
        for issue in ("atteint", "abandonne"):
            with self.subTest(issue=issue):
                m, condition = scene_marche()
                m = amener(m, "ilse", condition["lieu"])
                if issue == "atteint":
                    croire(m, "marchand", "ilse", "lieu", condition["lieu"],
                           "dit:ilse", salle=condition["lieu"], case=None)
                else:
                    croire(m, "marchand", condition["lieu"], "eau", 300, "vu")
                avant = copy.deepcopy(m.data)
                with patch.object(planification, "VERIFIER", True):
                    with planification.vues_du_choix(m, "marchand"):
                        with planification.vues_du_choix(m, "marchand"):
                            agendas.actualiser(m, "marchand")
                            self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], issue)
                            self.assertEqual(m.data, avant)
                        self.assertEqual(m.data, avant)
                self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], issue)
                self.assertEqual(len(m.data["chronique"]), len(avant["chronique"]) + 1)
                n = recharger(m)
                self.assertEqual(n.data, m.data)
                self.assertEqual(rendu(n), rendu(m))

    def test_lister_les_candidats_ne_declenche_plus_l_activation(self):
        m = nouvelle_crue(42, depart="fixe")
        spatial.installer(m)
        avant = copy.deepcopy(m.data)
        list(deliberation._candidats(m, "marchand"))
        self.assertEqual(m.data, avant)
        self.assertEqual(agendas.projets(m, "marchand"), [])
