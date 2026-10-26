"""Compatibilité passive des données du stratège retiré (aucun appel au modèle)."""
import copy
import unittest

from donjon.banc_pnj import creer, executer
from donjon.recit_pnj import Recit
from tests.test_tensions import recharger


class AncienChampTests(unittest.TestCase):
    def test_le_champ_ancien_est_ignore_apres_recharge_et_jeu(self):
        for scenario in ("relais", "mine"):
            with self.subTest(scenario=scenario):
                temoin = recharger(creer(scenario, 1985, "fixe"))
                ancien = copy.deepcopy(temoin)
                champ = {"appels": [0], "dernier": {}, "oisif": {},
                         "suivis": {}, "bilan": {"appels": 1, "plan": 1}}
                ancien.data["stratege"] = copy.deepcopy(champ)
                ancien = recharger(ancien)
                rendus = []
                for monde in (temoin, ancien):
                    recit = Recit(monde)
                    chronique, mesures = executer(monde, 5, recit)
                    rendus.append((chronique, mesures, recit.texte(monde, chronique)))
                self.assertEqual(rendus[0], rendus[1])
                self.assertFalse(any(k.startswith("stratege_") for k in rendus[1][1]))
                temoin, ancien = recharger(temoin), recharger(ancien)
                self.assertEqual(ancien.data.pop("stratege"), champ)
                self.assertEqual(ancien.data, temoin.data)


if __name__ == "__main__":
    unittest.main()
