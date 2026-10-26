"""Décision de calibration : dénominateurs, bornes et abstention."""
import copy
import unittest

from tools.calibrer_signes import bilan, classer


def candidat(parametres, bas=.7, haut=.8, meprises=.19, rien=.3):
    total = {"essais": 100, "rien": rien * 100, "part_meprises": meprises,
             "lectures": 100 * (1 - rien), "meprises": 100 * (1 - rien) * meprises}
    return {"parametres": parametres, "groupes": {
        "defaut": {"total": copy.deepcopy(total)},
        "regles": {"total": copy.deepcopy(total), "basse": {"justesse": bas},
                   "haute": {"justesse": haut}}}}


class CalibrationTests(unittest.TestCase):
    def test_abstention_hors_denominateur_des_lectures(self):
        preuves = [{"signe": {"signe": "attend"}, "psy": psy,
                    "marge": marge, "lecture": lecture}
                   for psy, marge, lecture in ((8, 1, "guet"), (14, -1, None), (14, -12, "fatigue"))]
        b = bilan(preuves)
        self.assertEqual(b["total"]["essais"], 3)
        self.assertEqual(b["total"]["lectures"], 2)
        self.assertEqual(b["total"]["part_meprises"], .5)
        self.assertEqual(b["total"]["abstention"], 1 / 3)
        self.assertEqual(b["haute"]["justesse"], 0)

    def test_bornes_inclusives_psy_et_stricte_meprises(self):
        bon = candidat([4, 3, 8])
        mauvais = [candidat([4, 3, 9], bas=.701), candidat([4, 4, 8], haut=.799),
                   candidat([3, 3, 8], meprises=.2)]
        resultat = classer([*mauvais, bon])
        self.assertEqual(resultat[0]["parametres"], bon["parametres"])
        self.assertEqual([r["admissible"] for r in resultat], [True, False, False, False])
        # Une population à 20 % ne fait pas échouer une moyenne globale <20 %.
        r = candidat([4, 3, 8], meprises=.1)
        r["groupes"]["regles"]["total"] = candidat([4, 3, 8], meprises=.2)["groupes"]["regles"]["total"]
        self.assertTrue(classer([r])[0]["admissible"])

    def test_plus_faible_abstention_et_compromis_explicite(self):
        a, b = candidat([4, 3, 8], rien=.4), candidat([3, 3, 8], rien=.3)
        self.assertEqual(classer([a, b])[0]["parametres"], b["parametres"])
        a, b = candidat([4, 3, 8], haut=.79), candidat([3, 3, 8], haut=.7, rien=0)
        self.assertEqual(classer([b, a])[0]["parametres"], a["parametres"])
        self.assertFalse(classer([b, a])[0]["admissible"])

    def test_pas_de_succes_sans_echantillon(self):
        r = candidat([4, 3, 8], haut=None)
        with self.assertRaisesRegex(ValueError, "échantillonnées"):
            classer([r])
