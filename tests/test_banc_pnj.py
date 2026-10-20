"""Le banc sans joueur recueille toute la chronique, même bornée, même la première minute d'un pas."""
import unittest

from donjon.banc_pnj import _nouvelles, creer, executer
from donjon.geometrie import position_entree


class ChroniqueDuBancTests(unittest.TestCase):
    def test_tout_ce_qui_s_ajoute_est_recueilli(self):
        m = creer("relais", 7)
        m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
        chronique, mesures = executer(m, 90)
        self.assertLess(len(m.data["chronique"]), 300)  # Sans troncature : le banc a tout.
        self.assertEqual(chronique, m.data["chronique"])
        self.assertTrue(any(c["minute"] % 5 == 0 for c in chronique))
        self.assertEqual(mesures["gestes"], len(chronique))

    def test_la_borne_ne_fait_ni_perdre_ni_doubler(self):
        a, b, c, d = ({"minute": i, "texte": str(i)} for i in range(4))
        self.assertEqual(_nouvelles([a, b], [a, b, c]), [c])
        self.assertEqual(_nouvelles([a, b], [b, c, d]), [c, d])  # La borne a fait tomber a.
        self.assertEqual(_nouvelles([a, b], [c, d]), [c, d])
        self.assertEqual(_nouvelles([], [a]), [a])
        self.assertEqual(_nouvelles([a], [a]), [])


if __name__ == "__main__":
    unittest.main()
