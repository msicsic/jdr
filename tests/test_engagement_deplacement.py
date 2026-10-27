"""Une parole de déplacement s'exécute par la marche de son auteur."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, echanges, ecoute, pnj, planification
from tests.scenarios_contractuels import nouvelle_crue
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder as rendu
from donjon.spatial import installer
from donjon.temps import ecouler
from tests.support import calme, presentes, regarder
from tests.test_avis_menace import relation
from tests.test_social import placer
from tests.test_tensions import recharger


def scene(cible="ilse", destination="chambre_cloche", graine=1985):
    m = presentes(nouvelle_crue(graine, depart="fixe"))
    installer(m)
    calme(m, "marchand", "aubin", "ilse", "brune")
    for qui, case in (("marchand", [2, 4]), (cible, [3, 4])):
        placer(m, qui, "antichambre", case)
    regarder(m, "marchand", cible)
    regarder(m, cible, "marchand")
    relation(m, cible, "marchand", confiance=100, affection=100)
    m.joueur.update(salle="antichambre", position=[2, 3], orientation="nord")
    m.data["connus"] = sorted(m.objets)
    m.data["visitees"] = sorted(m.data["salles"])
    m.data["voix_connues"] = ["marchand", cible]
    return recharger(m), {"objet": cible, "lieu": destination}


class EngagementDeplacementTests(unittest.TestCase):
    def demander(self, m, cible, condition):
        etape = planification._etape("confier", cible, contenu=condition)
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(echanges.executer(m, "marchand", etape, []))
        self.assertEqual(m.objets[cible]["lieu"], "antichambre")
        self.assertEqual(agendas.en_cours(m, cible)[0]["condition"], condition)
        self.assertTrue(any("accepte" in x["texte"] for x in m.data["chronique"]))
        sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
        entendu = ecoute.rendre(m, sons)
        self.assertIn("accepte", "\n".join(entendu))
        m = recharger(m)
        self.assertEqual(entendu, ecoute.rendre(m, ecoute.entendus(m, -1, ecoute.ENTENDU)))
        return m

    def avancer(self, m, dt):
        pnj.avancer(m, ecouler(m, dt), [], dt)
        return recharger(m)

    def test_gorm_confie_deux_marches_et_pas_un_transport(self):
        for cible, destination in (("ilse", "chambre_cloche"), ("brune", "echoppe")):
            with self.subTest(cible=cible):
                m, condition = scene(cible, destination)
                devis = echanges.devis_service(m, cible, condition, "marchand")
                self.assertIsNotNone(devis)
                self.assertTrue(devis[1])
                self.assertFalse(any(x["operation"] in ("prendre", "poser")
                                     and x["cible"] == cible for x in devis[1]))
                m = self.demander(m, cible, condition)
                # Les autres restent témoins ; seul le destinataire choisit sa marche.
                for qui in ("marchand", "aubin", "ilse", "brune"):
                    if qui != cible:
                        lire(m, qui)["libre"] = 1000000
                a, b = recharger(m), recharger(m)
                a = self.avancer(a, 3 * 600)
                for _ in range(6):
                    b = self.avancer(b, 300)
                self.assertEqual(a.data, b.data)
                self.assertEqual(rendu(a), rendu(b))
                self.assertEqual(a.objets[cible]["lieu"], destination)
                self.assertTrue(echanges.tenu(a, cible, condition))
                self.assertFalse(agendas.en_cours(a, cible))
                self.assertTrue(any(x["type"] == "engagement_tenu" and x["condition"] == condition
                                    for x in lire(a, cible)["memoire"]))
                avant = copy.deepcopy(a.data)
                self.assertEqual(recharger(a).data, avant)
                self.assertEqual(rendu(a), rendu(recharger(a)))

    def test_mefiance_ne_cree_ni_engagement_ni_deplacement(self):
        m, condition = scene()
        relation(m, "ilse", "marchand", confiance=0, affection=0)
        self.assertEqual(echanges.confier(m, "marchand", "ilse", condition), "mefiance")
        m = recharger(m)
        self.assertFalse(agendas.en_cours(m, "ilse"))
        self.assertEqual(m.objets["ilse"]["lieu"], "antichambre")
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_position_propre_sans_croyance_sur_soi_et_arrivee_dans_la_minute(self):
        m, condition = scene()
        lire(m, "ilse")["croyances"].pop("ilse", None)
        self.assertFalse(deliberation.satisfaite(m, "ilse", condition))
        placer(m, "ilse", condition["lieu"], [1, 3])
        self.assertTrue(echanges.tenu(m, "ilse", condition, m.data["minutes"]))
        m = recharger(m)
        self.assertTrue(echanges.tenu(m, "ilse", condition, m.data["minutes"]))
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_destination_crue_noyee_refusee_avant_la_promesse(self):
        for cible in ("ilse", "brune"):
            with self.subTest(cible=cible):
                m, condition = scene(cible)
                croire(m, cible, condition["lieu"], "eau", 300, "vu")
                self.assertIsNone(echanges.devis_service(m, cible, condition, "marchand"))
                with patch.object(Monde, "d20", return_value=20):
                    self.assertEqual(echanges.confier(m, "marchand", cible, condition), "impossible")
                m = recharger(m)
                self.assertFalse(agendas.en_cours(m, cible))
                self.assertEqual(m.objets[cible]["lieu"], "antichambre")
                self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_la_position_reelle_d_autrui_ne_tient_pas_sa_parole_aux_yeux_du_demandeur(self):
        m, condition = scene()
        croire(m, "marchand", "ilse", "lieu", "antichambre", "vu",
               salle="antichambre", case=[3, 4])
        placer(m, "ilse", condition["lieu"], [1, 3])
        self.assertTrue(echanges.tenu(m, "ilse", condition))
        self.assertFalse(echanges.tenu(m, "marchand", condition))
        m = recharger(m)
        self.assertFalse(echanges.tenu(m, "marchand", condition))
        self.assertEqual(rendu(m), rendu(recharger(m)))


if __name__ == "__main__":
    unittest.main()
