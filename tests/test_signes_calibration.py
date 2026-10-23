"""Contrats des signes, du monde enregistré jusqu'à la vue après reprise."""
import copy
import unittest
from unittest.mock import patch

from donjon import relations, signes, spatial
from donjon.esprits import lire
from tests.test_signes import scene, ecarter
from tests.test_social import recharger


class CachesTests(unittest.TestCase):
    def test_emission_ne_recalcule_que_ses_causes_et_se_reconstruit(self):
        for id, autre in (("ilse", "brune"), ("brune", "ilse")):
            with self.subTest(id=id), patch.object(spatial, "VERIFICATION", 1):
                m = ecarter(scene(), id, autre)
                avant = copy.deepcopy(signes.publics(m))
                emission = signes.de(m, id)
                m.data["minutes"] += 1  # aucun seuil ne change
                self.assertIs(signes.de(m, id), emission)
                # Un axe changé en place doit invalider l'émission, même sans temps écoulé.
                r = lire(m, id)["relations"][autre]
                r["ancrages"]["peur"][0] = 0
                apres = signes.publics(m)
                self.assertNotEqual(avant, apres)
                self.assertEqual(signes.publics(recharger(m)), apres)

    def test_perception_ne_depend_pas_des_signes_hors_de_vue(self):
        for id in ("ilse", "brune"):
            with self.subTest(id=id):
                m = ecarter(scene())
                signes.percus(m, id)
                with patch("donjon.signes._percus", wraps=signes._percus) as calcul:
                    lire(m, "marchand")["emotions"]["colere"] = {
                        "contre": "aubin", "niveau": 50, "depuis": m.data["minutes"]}
                    avant = copy.deepcopy(signes.percus(m, id))
                    self.assertEqual(calcul.call_count, 0)
                self.assertEqual(signes.percus(recharger(m), id), avant)

    def test_relation_mutation_ancre_et_profil_comme_calcul_pur(self):
        for id, autre in (("ilse", "brune"), ("brune", "ilse")):
            m = ecarter(scene(), id, autre)
            for minute in (0, 10, 120):
                m.data["minutes"] = minute
                with patch.object(spatial, "VERIFICATION", 1):
                    self.assertEqual(relations.envers(m, id, autre), relations._lecture_pure(m, id, autre))
                self.assertEqual(relations.envers(recharger(m), id, autre), relations.envers(m, id, autre))


class RelecturesTests(unittest.TestCase):
    def _guet(self, scenario):
        from donjon.banc_pnj import creer
        from tests.test_signes import intention
        from tests.test_social import placer
        from tests.support import regarder
        if scenario == "relais":
            m, lecteur, auteur, salle, objet, outil = scene(), "marchand", "brune", "antichambre", "reserve", "crochets"
        else:
            m, lecteur, auteur, salle, objet, outil = creer("auberge", 7, "fixe"), "hugues", "lucien", "chambre_chaude", "coffre_marchand", "outils_lucien"
            outil = next(k for k, o in m.objets.items() if "crochetage" in o.get("usages", []))
        m.data["salles"][salle]["lumiere_naturelle"] = 2
        placer(m, lecteur, salle, [6, 4] if scenario == "relais" else [2, 3])
        placer(m, auteur, salle, [7, 3] if scenario == "relais" else [1, 3])
        regarder(m, lecteur, objet)
        intention(m, auteur, "crocheter", objet, outil, "sans_temoin", attente=600)
        lire(m, auteur)["patience"] = 0
        s = next(s for s in signes.percus(m, lecteur) if s["signe"] == "attend" and s["personnage"] == auteur)
        return m, lecteur, auteur, s

    def test_relecture_rafraichit_sans_souvenir_ni_ligne_et_echec_preserve(self):
        for scenario in ("relais", "auberge"):
            with self.subTest(scenario=scenario):
                m, lecteur, auteur, s = self._guet(scenario)
                with patch("donjon.signes._jet", return_value=20):
                    signes.lire(m, lecteur, [s], complet=True)
                m = recharger(m)
                avant = copy.deepcopy(lire(m, lecteur)["memoire"])
                nb = len(m.data["chronique"])
                m.data["minutes"] += 10
                with patch("donjon.signes._jet", return_value=20):
                    signes.lire(m, lecteur, [s], complet=True)
                m = recharger(m)
                self.assertEqual(lire(m, lecteur)["memoire"], avant)
                self.assertEqual(len(m.data["chronique"]), nb)
                c = copy.deepcopy(lire(m, lecteur)["croyances"][auteur]["intention"])
                self.assertEqual(c["minute"], m.data["minutes"])
                m.data["minutes"] += 10
                # DD élevé : ce jet manque dans la bande rien.
                with patch("donjon.signes.interpreter", return_value=(None, -1)):
                    signes.lire(m, lecteur, [s], complet=True)
                m = recharger(m)
                self.assertEqual(lire(m, lecteur)["croyances"][auteur]["intention"], c)
                self.assertEqual(lire(m, lecteur)["memoire"], avant)
                self.assertEqual(len(m.data["chronique"]), nb)

    def test_disparition_retour_et_peremption_sont_de_nouvelles_lectures(self):
        for scenario in ("relais", "auberge"):
            m, lecteur, auteur, s = self._guet(scenario)
            with patch("donjon.signes._jet", return_value=20):
                signes.lire(m, lecteur, [s], complet=True)
                signes.lire(m, lecteur, [], complet=True)
                m = recharger(m)
                signes.lire(m, lecteur, [s], complet=True)
                m = recharger(m)
                m.data["minutes"] += 31
                signes.lire(m, lecteur, [s], complet=True)
            m = recharger(m)
            self.assertEqual(sum(s["type"] == "intention_lue" for s in lire(m, lecteur)["memoire"]), 3)
            self.assertEqual(sum(c["nature"] == "lecture" and c["pnj"] == lecteur for c in m.data["chronique"]), 3)

    def test_observer_ne_repete_pas_une_impression_apres_reprise(self):
        for id, autre in (("ilse", "brune"), ("brune", "ilse")):
            m = ecarter(scene(), id, autre)
            with patch("donjon.signes._jet", return_value=20):
                premiere = signes.bilan_signes(m, observer=id)
            self.assertTrue(any("semble" in l for l in premiere))
            m = recharger(m)
            self.assertFalse(any("semble" in l for l in signes.bilan_signes(m, observer=id)))
            m.data["minutes"] += 10
            with patch("donjon.signes._jet", return_value=20):
                lignes = signes.bilan_signes(m, observer=id)
            m = recharger(m)
            self.assertFalse(any("semble" in l for l in lignes))
            self.assertTrue(signes.impressions(m))

    def test_meme_laps_d_un_bloc_ou_decoupe_et_recharge(self):
        from donjon.banc_pnj import creer
        from donjon.pnj import avancer
        from donjon.rendu import regarder
        from donjon.temps import ecouler
        for scenario in ("relais", "auberge"):
            a = creer(scenario, 7, "fixe")
            b = recharger(a)
            ecouler(a, 20 * 600)
            avancer(a, 20, [])
            for _ in range(20):
                ecouler(b, 600)
                avancer(b, 1, [])
                b = recharger(b)
            a, b = recharger(a), recharger(b)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))


if __name__ == "__main__":
    unittest.main()
