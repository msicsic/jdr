"""Protection déclarée : responsabilités communes et fins connues persistantes."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, defense, deliberation, planification
from donjon.esprits import croire, lire
from donjon.rendu import regarder
from tests import test_protection
from tests.test_tensions import recharger, relais, vivre


def declarer(m, qui="ilse", profil=False):
    p = m.objets["marchand"]["profil"]
    p["agendas"] = [{"sorte": "protéger", "parametres": {"qui": qui}}]
    p["protege"] = [qui] if profil else []
    return recharger(m)


class ProtegerTests(unittest.TestCase):
    def test_interposition_reelle_de_deux_protecteurs_sur_agenda_seul(self):
        from tests.test_interposition import epreuve
        from tests.test_tensions import placer
        from tests.support import regarder as orienter
        from donjon.esprits import percevoir_tous
        from tests.test_corps_blessable import passer
        from donjon.temps import MINUTE
        for acteur in ("marchand", "aubin"):
            m = epreuve(acteur)
            p = m.objets[acteur]["profil"]
            p.update(protege=[], pulsions=[], agendas=[{"sorte": "protéger", "parametres": {"qui": "brune"}}])
            lire(m, acteur)["pulsions"] = []
            placer(m, "brune", "antichambre", (4, 5))
            orienter(m, acteur, "brune")
            percevoir_tous(m)
            m.joueur["position"] = [1, 5]
            # Voir le mouvement, pas seulement retrouver le joueur au bord
            # du regard après avoir regardé le protégé dans l'autre sens.
            orienter(m, acteur, "joueur")
            percevoir_tous(m)
            m.joueur["position"] = [2, 5]
            percevoir_tous(m)
            deliberation.choisir(m, acteur, m.data["minutes"])
            self.assertEqual(lire(m, acteur)["intention"]["but"]["type"], "interposer")
            lignes = passer(m, MINUTE)
            self.assertIn("N'approche pas davantage", " ".join(lignes))
            m = recharger(m)
            self.assertEqual(m.objets[acteur]["position"], [3, 5])
            self.assertTrue(any(s["type"] == "mise_en_garde" and s["objet"] == "brune"
                                for s in lire(m, acteur)["memoire"]))
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_appel_reconnu_et_course_reels_sur_agenda_seul(self):
        original = test_protection.seule_et_a_bout
        with patch.object(test_protection, "seule_et_a_bout",
                          lambda m: declarer(original(m))):
            test_protection.AppelTests(
                "test_a_bout_sans_abri_elle_appelle_et_gorm_accourt"
            ).test_a_bout_sans_abri_elle_appelle_et_gorm_accourt()
            test_protection.AppelTests(
                "test_le_joueur_entend_l_appel_sans_tendre_l_oreille"
            ).test_le_joueur_entend_l_appel_sans_tendre_l_oreille()

    def test_responsabilites_sans_doublon_devis_sans_activation(self):
        for qui in ("ilse", "brune"):
            m = declarer(relais(), qui, profil=True)
            avant = copy.deepcopy(m.data)
            self.assertEqual(deliberation.proteges(m, "marchand"), [qui])
            self.assertIn(qui, defense.charges(m, "marchand"))
            self.assertIn("marchand", deliberation.protecteurs(m, qui))
            self.assertEqual(m.data, avant)
            self.assertNotIn("agendas", lire(m, "marchand"))

    def test_mort_crue_fin_differee_sans_renaissance_et_inconnu_non_terminal(self):
        for qui in ("ilse", "brune"):
            m = declarer(relais(), qui)
            agendas.actualiser(m, "marchand")
            croire(m, "marchand", qui, "lieu", None, "vu", salle=None, case=None)
            agendas.actualiser(m, "marchand")
            self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")
            croire(m, "marchand", qui, "etat", {"mort": True}, "vu")
            avant = copy.deepcopy(m.data)
            with planification.vues_du_choix(m, "marchand"):
                agendas.actualiser(m, "marchand")
                self.assertEqual(m.data, avant)
            m = recharger(m)
            a = agendas.projets(m, "marchand")[0]
            self.assertEqual((a["etat"], a["raison"]), ("abandonne", "protege cru mort"))
            self.assertNotIn(qui, defense.charges(m, "marchand"))
            croire(m, "marchand", qui, "etat", {"mort": False}, "vu")
            agendas.actualiser(m, "marchand")
            self.assertEqual(a, agendas.projets(m, "marchand")[0])
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_appel_meme_laps_decoupe_monde_et_rendu_recharges(self):
        m = declarer(test_protection.seule_et_a_bout(relais()))
        entier, _ = vivre(recharger(m), 3)
        morceaux = recharger(m)
        for _ in range(3):
            morceaux, _ = vivre(morceaux, 1)
        self.assertEqual(entier.data, morceaux.data)
        self.assertEqual(entier.data, recharger(entier).data)
        self.assertEqual(regarder(entier), regarder(recharger(morceaux)))

    def test_suivi_vocal_actif_sans_perdre_responsabilite(self):
        m = declarer(relais())
        agendas.actualiser(m, "marchand")
        avant = copy.deepcopy(m.data)
        plan = agendas.planifier(m, "marchand", "a1")
        self.assertEqual(plan[0]['agenda'], 'a1')
        self.assertEqual(plan[1][-1]['contenu'], {'portee': 'voix'})
        self.assertEqual(m.data, avant)
        with planification.vues_du_choix(m, "marchand"):
            agendas.planifier(m, "marchand", "a1")
        m = recharger(m)
        self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")
        self.assertIn("ilse", defense.charges(m, "marchand"))
