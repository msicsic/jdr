"""Garde déclarée : lecture commune, choix différé et monde rechargé."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, defense, deliberation, planification
from donjon.esprits import lire
from donjon.rendu import regarder
from tests import test_interposition as interposition
from tests.test_tensions import recharger


def declarer(m, acteur, objet="cle_reserve", pulsion=False):
    p = m.objets[acteur]["profil"]
    p["agendas"] = [{"sorte": "garder", "parametres": {"objet": objet}}]
    if not pulsion:
        p["pulsions"] = []
        lire(m, acteur)["pulsions"] = []
    agendas.actualiser(m, acteur)
    return recharger(m)


class GarderTests(unittest.TestCase):
    def test_interposition_reveille_aussi_la_garde_endormie(self):
        m = declarer(interposition.epreuve(), "marchand")
        lire(m, "marchand")["agendas"][0]["etat"] = "sommeil"
        avant = copy.deepcopy(m.data)
        with planification.vues_du_choix(m, "marchand"):
            self.assertEqual(agendas.planifier(m, "marchand", "a1")[0]["type"], "interposer")
            self.assertEqual(m.data, avant)
        m = recharger(m)
        self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")

    def test_anselme_ballot_agenda_sans_pulsion(self):
        from donjon import banc_pnj
        original = banc_pnj.creer
        def creer(*args, **kwargs):
            return declarer(original(*args, **kwargs), "anselme", "ballot")
        with patch.object(banc_pnj, "creer", creer):
            interposition.InterpositionTests(
                "test_epreuve_anselme_ballot_en_donnees"
            ).test_epreuve_anselme_ballot_en_donnees()

    def test_deux_gardes_interposition_monde_et_rendu_recharges(self):
        original = interposition.epreuve
        def epreuve(gardien="marchand", approchant="joueur"):
            return declarer(original(gardien, approchant), gardien)
        # Même chaîne réelle de perception, poste, parole, persistance et recharge
        # que le lot 167, ici sans aucune pulsion de garde.
        with patch.object(interposition, "epreuve", epreuve):
            interposition.InterpositionTests(
                "test_deux_gardiens_poste_parole_persistance_et_rendu_recharges"
            ).test_deux_gardiens_poste_parole_persistance_et_rendu_recharges()
            interposition.InterpositionTests(
                "test_meme_laps_decoupe_et_recharge"
            ).test_meme_laps_decoupe_et_recharge()

    def test_prix_unique_avec_pulsion_et_agenda(self):
        for acteur in ("marchand", "aubin"):
            m = interposition.epreuve(acteur)
            ancien = planification.prix_gardes(m, acteur, ["antichambre"])
            m = declarer(m, acteur, pulsion=True)
            self.assertEqual(planification.prix_gardes(m, acteur, ["antichambre"]), ancien)
            m = declarer(m, acteur)
            self.assertEqual(planification.prix_gardes(m, acteur, ["antichambre"]), ancien)
            self.assertIn("cle_reserve", defense.charges(m, acteur))
            self.assertIn("antichambre", deliberation.gardes(m, acteur))

    def test_garde_tenue_et_fin_differee_avec_cause(self):
        for acteur in ("marchand", "aubin"):
            m = declarer(interposition.epreuve(acteur), acteur)
            avant = copy.deepcopy(m.data)
            with planification.vues_du_choix(m, acteur):
                resultat = agendas.planifier(m, acteur, "a1")
                self.assertEqual(m.data, avant)
            self.assertIsNotNone(resultat)
            self.assertEqual(agendas.projets(m, acteur)[0]["etat"], "actif")
            # L'échéance est le seul motif terminal livré dans cette tranche.
            lire(m, acteur)["agendas"][0]["echeance"] = -1
            avant = copy.deepcopy(m.data)
            with planification.vues_du_choix(m, acteur):
                agendas.actualiser(m, acteur)
                self.assertEqual(m.data, avant)
            m = recharger(m)
            a = agendas.projets(m, acteur)[0]
            self.assertEqual((a["etat"], a["raison"]), ("abandonne", "echeance"))
            self.assertFalse(agendas.gardes(m, acteur))
            agendas.actualiser(m, acteur)
            self.assertEqual(agendas.projets(m, acteur)[0], a)
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_lieu_sans_objet_et_devis_sans_publication(self):
        m = declarer(interposition.epreuve(), "marchand")
        lire(m, "marchand")["agendas"][0]["parametres"] = {"lieu": "antichambre"}
        m = recharger(m)
        avant = copy.deepcopy(m.data)
        self.assertIsNotNone(agendas.planifier(m, "marchand", "a1"))
        self.assertEqual(m.data, avant)
        self.assertTrue(deliberation.de_garde(m, "marchand", "antichambre"))
        self.assertEqual(deliberation.gardes(m, "marchand"), ("antichambre",))
        self.assertGreater(planification.prix_gardes(m, "marchand", ["antichambre"])["antichambre"], 0)
