"""L'estimation ignore le départ ; la marche persistée conserve sa durée réelle."""
import unittest
from unittest.mock import patch

from donjon import planification as p, spatial
from donjon.pnj import DUREES
from donjon.trajet_estime import moyenne
from tests.test_trajets_reels import flammes, executer_plan
from tests.test_tensions import placer, recharger


class TrajetEstimeTests(unittest.TestCase):
    def test_moyennes_reprises_dans_la_vue_figee_et_verifiees(self):
        from donjon import trajet_estime as t
        from copy import deepcopy
        for scenario in ("relais", "mine"):
            with self.subTest(scenario=scenario):
                m, qui, _, _ = flammes(scenario)
                m = recharger(m)
                avant = deepcopy(m.data)
                v = p.Vue(m, qui)
                e = p.depart(m, qui, v)
                cibles = {tuple(m.objets[qui]["position"])}
                with patch.object(t, "_moyenne", wraps=t._moyenne) as calcul:
                    resultat = moyenne(v, e, e.salle, cibles)
                    self.assertEqual(resultat, moyenne(v, e.apres(faits=[(("allume", "x"), True)]),
                                                       e.salle, cibles))
                    self.assertEqual(calcul.call_count, 1)
                    with patch.object(spatial, "VERIFICATION", 1):
                        self.assertEqual(resultat, moyenne(v, e, e.salle, cibles))
                    self.assertEqual(calcul.call_count, 2)
                    self.assertTrue(calcul.call_args.kwargs["pur"])
                self.assertEqual(m.data, avant)
                recharge = recharger(m)
                nouvelle = p.Vue(recharge, qui)
                self.assertFalse(nouvelle._moyennes)
                self.assertEqual(resultat, moyenne(nouvelle, p.depart(recharge, qui, nouvelle), e.salle, cibles))

    def test_moyennes_distinguent_cibles_sortie_allure_et_equipement_metrique(self):
        from donjon.trajet_estime import _moyenne
        m, qui, _, _ = flammes("relais")
        v = p.Vue(recharger(m), qui)
        e = p.depart(v.monde, qui, v)
        # Forcer le calcul métrique exerce la lecture des possessions même sans
        # obstacle franchissable ; les clés de table ne doivent pas les confondre.
        with patch.object(v, "metrique", return_value=True):
            for etat in (e, e.apres(allure=30), e.apres(portes=frozenset())):
                for cibles in ({(6, 5)}, {(6, 6)}):
                    for sortie in (False, True):
                        self.assertEqual(moyenne(v, etat, e.salle, cibles, sortie),
                                         _moyenne(v, etat, e.salle, cibles, sortie, pur=True))
        self.assertEqual(len(v._moyennes), 12)

    def test_moyenne_corrompue_detectee(self):
        m, qui, _, _ = flammes("relais")
        v = p.Vue(m, qui)
        e = p.depart(m, qui, v)
        moyenne(v, e, e.salle, {(6, 5)})
        v._moyennes[next(iter(v._moyennes))] = -1
        with patch.object(spatial, "VERIFICATION", 1):
            with self.assertRaisesRegex(AssertionError, "Trajet estimé périmé"):
                moyenne(v, e, e.salle, {(6, 5)})

    def test_meme_plan_deux_departs_execution_et_rendu_apres_recharge(self):
        for scenario in ("relais", "mine"):
            with self.subTest(scenario=scenario):
                origine, qui, source, feux = flammes(scenario)
                resultats, temps = [], []
                for case in ((6, 5), (6, 6)):
                    m = recharger(origine)
                    placer(m, qui, m.objets[qui]["lieu"], case)
                    m = recharger(m)
                    with patch.object(p, "VERIFIER", True), patch.object(spatial, "VERIFICATION", 1):
                        r = p.chercher(m, qui, lambda v, e: bool(e.fait("allume", source)),
                                       {"entretenir": [source]}, emplois=("feu",), memo=["estime-test"])
                    resultats.append(r)
                    m, duree, lignes = executer_plan(m, qui, r[1])
                    temps.append(duree)
                    self.assertTrue(m.objets[source]["allume"])
                    self.assertEqual(m.objets[source]["lieu"], qui)
                    from tests.support import regarder
                    regarder(m, "joueur", qui)
                    m = recharger(m)
                    self.assertTrue(m.visible(source))
                    self.assertIn("allume", " ".join(c["texte"] for c in m.data["chronique"]))
                    self.assertGreater(duree, DUREES["allumer"])
                self.assertEqual(resultats[0], resultats[1])
                self.assertLess(temps[0], temps[1])

    def test_grande_salle_plus_chere_apres_recharge(self):
        prix = []
        for largeur in (3, 15):
            m, qui, _, _ = flammes("relais")
            salle = "salle_estimee"
            m.data["salles"][salle] = {
                "nom": "Salle", "fenetres": 0, "lumiere_naturelle": 0, "plan": {"origine": [50, 50], "sol": ["." * largeur] * 3},
                "sorties": {"est": {"case": [largeur, 1], "vers": "echoppe"}}}
            m.data["salles"]["echoppe"]["sorties"]["ouest"] = {
                "case": [-1, 1], "vers": salle, "escalier": True}
            m.data["salles"][salle]["sorties"]["est"]["escalier"] = True
            m = recharger(m)
            v = p.Vue(m, qui)
            e = p.depart(m, qui, v).apres(salle=salle)
            prix.append(moyenne(v, e, salle, {(0, 1)}))
        self.assertGreater(prix[1], prix[0])
