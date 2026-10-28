"""Un certificat d'absence de flamme ne retire aucune suite du devis."""
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import part_estimee as pe, planification as p
from donjon.monde import Monde
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_lampes_buts as lampes
from tests.test_tensions import recharger


class DevisVidesTests(unittest.TestCase):
    def test_captures_reelles_memes_recherches_monde_et_rendu_recharges(self):
        for scenario in ("auberge", "mine"):
            chemin = Path(__file__).parent / f"data/cout-12h/{scenario}-1985-480.json.gz"
            depart = json.loads(gzip.decompress(chemin.read_bytes()))
            resultats, comptes, exclusions = [], [], []
            for filtrer in (False, True):
                m = recharger(Monde(depart))
                recherches, preparatifs, exclus = [], 0, 0
                chercher, preparer, allumable = p.chercher, pe._preparer, pe._allumable

                def observer(*a, **k):
                    r = chercher(*a, **k)
                    recherches.append((a[1], k.get("nom"), r))
                    return r

                def condition(v, e, source):
                    nonlocal exclus
                    possible = allumable(v, e, source)
                    exclus += not possible
                    return possible if filtrer else True

                def preparation(v, e, source, *a, **k):
                    nonlocal preparatifs
                    preparatifs += 1
                    r = list(preparer(v, e, source, *a, **k))
                    # Preuve différentielle sur toutes les suites réelles :
                    # un certificat négatif ne cache jamais une suite non vide.
                    if r:
                        self.assertTrue(allumable(v, e, source))
                    yield from r

                with ExitStack() as pile:
                    for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                        pile.enter_context(patch.object(p, nom, {}))
                    pile.enter_context(patch.object(p, "VERIFIER", False))
                    pile.enter_context(patch.object(p, "chercher", observer))
                    pile.enter_context(patch.object(pe, "_allumable", condition))
                    pile.enter_context(patch.object(pe, "_preparer", preparation))
                    moteur = Moteur(m)
                    lignes = []
                    for _ in range(3):
                        lignes.extend(moteur.executer(moteur.preparer(proposition("attendre"))))
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))
                resultats.append((recherches, recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
                comptes.append(preparatifs)
                exclusions.append(exclus)
            self.assertEqual(resultats[0], resultats[1], scenario)
            # Une capture peut désormais attendre au lieu de rechercher une
            # flamme. Aucun gain strict n'est attendu sans devis à exclure ;
            # le cas sans flamme ci-dessous en exige toujours un, dans les
            # deux scénarios. L'identité complète reste exigée ici.
            self.assertLessEqual(comptes[1], comptes[0], scenario)
            if any(exclusions):
                self.assertLess(comptes[1], comptes[0], scenario)

    def test_sans_flamme_deux_scenes_aucun_preparatif_et_meme_absence_rechargee(self):
        for scenario, qui, donneur, source, lot, salle in (
            ("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve"),
            ("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable"),
        ):
            resultats, comptes = [], []
            for filtrer in (False, True):
                m = lampes.LumiereDuButTests().scene(scenario, qui, donneur, source, lot, salle)
                for k, x in m.objets.items():
                    if "allumage" in x.get("usages", ()):
                        deplacer(m, k, "joueur")
                        croire(m, qui, k, "lieu", "joueur", "savoir", salle=salle, case=[1, 2])
                m = recharger(m)
                with ExitStack() as pile:
                    for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                        pile.enter_context(patch.object(p, nom, {}))
                    if not filtrer:
                        pile.enter_context(patch.object(pe, "_allumable", return_value=True))
                    preparer = pile.enter_context(patch.object(pe, "_preparer", wraps=pe._preparer))
                    r = p.chercher(m, qui, p.eclaire, {"eclairer": True}, emplois=())
                    comptes.append(preparer.call_count)
                self.assertIsNone(r)
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                resultats.append((recharge.data, regarder(recharge), scene_percue(recharge)))
            self.assertGreater(comptes[0], 0)
            self.assertEqual(comptes[1], 0)
            self.assertEqual(resultats[0], resultats[1])

    def test_condition_remplie_meme_suite_et_livraison_reelle_deux_scenarios(self):
        for scenario, qui, donneur, source, lot, salle in (
            ("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve"),
            ("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable"),
        ):
            resultats = []
            for filtrer in (False, True):
                m = lampes.LumiereDuButTests().scene(scenario, qui, donneur, source, lot, salle)
                v = p.Vue(m, qui)
                v.eclairer = True
                e = p.depart(m, qui, v)
                but = lambda v, e: bool(e.fait("inspecte", salle)) and v.lumiere(e) > 0
                vises = {"inspecter": (salle,)}
                self.assertTrue(pe._allumable(v, e, source))
                with patch.object(pe, "_allumable", wraps=pe._allumable) if filtrer else \
                        patch.object(pe, "_allumable", return_value=True):
                    suites = pe.suites(v, e, lot, vises, but)
                    self.assertTrue(suites)
                    m = lampes.LumiereDuButTests().accomplir(m, qui, source, lot, but, vises)
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                resultats.append((suites, recharge.data, regarder(recharge), scene_percue(recharge)))
            self.assertEqual(resultats[0], resultats[1], scenario)


if __name__ == "__main__":
    unittest.main()
