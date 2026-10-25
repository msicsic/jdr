"""Lot 75 : diagnostic transparent, monde et rendu vérifiés après recharge."""
from contextlib import ExitStack
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger
from tools.mesurer_pertinence_arriere import charger, observer_recherche


DONNEES = Path(__file__).parent / "data/cout-12h"


class PertinenceArriereTests(unittest.TestCase):
    def test_cas_reels_joss_tilo_sans_acquisition_ni_plafond(self):
        for qui, noeuds in (("joss", 149), ("tilo", 169)):
            with self.subTest(qui=qui):
                m = charger(DONNEES / "auberge-1985-480.json.gz")
                avant = recharger(m)
                resultats = []
                for limite in (p.NOEUDS, p.REFERENCE):
                    r = None
                    def rechercher():
                        nonlocal r
                        r = p.chercher(m, qui, p.a_mange, emplois=("manger",) if limite == p.NOEUDS else None,
                                       motif="faim", noeuds=limite)
                        return r
                    if limite == p.NOEUDS:
                        d = observer_recherche(m, qui, rechercher)
                        self.assertEqual(d["diagnostic"]["noeuds"], noeuds)
                        self.assertEqual(d["avec_acquisitions"], 0)
                        self.assertEqual(d["objets"], {})
                        self.assertEqual(d["candidats_pertinents"], {"marmite": ["repas"], "vivres": ["repas"]})
                    else:
                        rechercher()
                    resultats.append(r)
                self.assertTrue(p._egaux(*resultats))
                self.assertEqual(m.data, avant.data)
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))

    def test_observation_ne_change_pas_la_partie_deux_captures(self):
        for scenario in ("auberge", "mine"):
            with self.subTest(scenario=scenario):
                resultats = []
                for instrumenter in (False, True):
                    m = charger(DONNEES / f"{scenario}-1985-480.json.gz")
                    recherches = []
                    chercher = p.chercher
                    def observer(*a, **k):
                        r = None
                        def calcul():
                            nonlocal r
                            r = chercher(*a, **k)
                            return r
                        if instrumenter:
                            observer_recherche(a[0], a[1], calcul)
                        else:
                            calcul()
                        recherches.append((a[1], k.get("nom"), r))
                        return r
                    with ExitStack() as pile:
                        for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                            pile.enter_context(patch.object(p, nom, {}))
                        pile.enter_context(patch.object(p, "chercher", observer))
                        moteur = Moteur(m)
                        lignes = moteur.executer(moteur.preparer(proposition("attendre")))
                    recharge = recharger(m)
                    self.assertEqual(m.data, recharge.data)
                    self.assertEqual(regarder(m), regarder(recharge))
                    self.assertEqual(scene_percue(m), scene_percue(recharge))
                    # Le bloc de diagnostic de l'observateur est local ; comparer
                    # les plans et la chaîne complète, pas la collecte imbriquée.
                    resultats.append((recherches, recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
                self.assertEqual(*resultats)
