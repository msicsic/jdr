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
        # Les gestes, et ce que l'ouïe a fait (se retourner, retenir un bruit, aller le voir).
        self.assertEqual(mesures["gestes"] + sum(c["nature"] in ("ouie", "lecture") for c in chronique), len(chronique))

    def test_la_borne_ne_fait_ni_perdre_ni_doubler(self):
        a, b, c, d = ({"minute": i, "texte": str(i)} for i in range(4))
        self.assertEqual(_nouvelles([a, b], [a, b, c]), [c])
        self.assertEqual(_nouvelles([a, b], [b, c, d]), [c, d])  # La borne a fait tomber a.
        self.assertEqual(_nouvelles([a, b], [c, d]), [c, d])
        self.assertEqual(_nouvelles([], [a]), [a])
        self.assertEqual(_nouvelles([a], [a]), [])


if __name__ == "__main__":
    unittest.main()


class ChargeDuBancTests(unittest.TestCase):
    """Le banc tourne sur le poste de l'utilisateur : il plafonne ses nuits simultanées."""

    def test_les_nuits_a_la_fois_sont_plafonnees(self):
        from unittest.mock import patch
        from donjon import banc_pnj
        vus = []

        class Pool:
            def __init__(self, max_workers):
                vus.append(max_workers)

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def map(self, f, arguments):
                return [None for _ in arguments]

        with patch("concurrent.futures.ProcessPoolExecutor", Pool):
            banc_pnj.nuits("relais", list(range(12)), 1, None, processus=3)
            banc_pnj.nuits("relais", [1, 2], 1, None, processus=3)
            banc_pnj.nuits("relais", list(range(64)), 1, None)
        self.assertEqual(vus, [3, 2, min(64, banc_pnj.PROCESSUS)])
        self.assertLessEqual(banc_pnj.PROCESSUS, max(1, (__import__("os").cpu_count() or 2) // 2))
