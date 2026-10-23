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


if __name__ == "__main__":
    unittest.main()
