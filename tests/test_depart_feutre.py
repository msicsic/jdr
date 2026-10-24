"""Découverte de discrétion, reprise et conséquences persistées."""
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_planification import relais
from tests.test_tensions import recharger, placer
from tests.test_trajets_reels import flammes, executer_plan


def departs_historiques(v, e):
    """Témoin d60b80a : autorisation globale, sans découverte par les gestes."""
    v._explore_furtif = True
    if v._cru_spatial is None:
        return [e]
    furtif = (any(v.illicite[o] and v.autorise[o] for o in v.connus)
              or v.degat is not None and any(v.violence(x) is not None for x in v.personnes()))
    return [e.apres(allure=15), e.apres(allure=30)] if furtif else [e]


class DepartFeutreTests(unittest.TestCase):
    def test_la_decouverte_ne_deplace_pas_les_lectures_de_lumiere(self):
        e = p.Etat("salle", (), {})
        for utile in (False, True):
            v = SimpleNamespace(_cru_spatial=object(), _explore_furtif=False,
                                _lumiere_lue=False, _discretion_lue=False, seul=None)
            def but(v, e):
                v._lumiere_lue = True
                return utile
            geste = (1, 1, [p._etape("manger", "repas", condition="sans_temoin")],
                     e.apres(faits=[(("mange", "repas"), True)]))
            self.assertEqual(p._normaliser_suites(v, e, {}, but, [geste]), [])
            self.assertEqual(v._discretion_lue, utile)
            self.assertFalse(v._lumiere_lue)

    def comparer(self, original, qui, chercher, executer=None):
        resultats, comptes = [], []
        for historique in (True, False):
            m = recharger(original)
            with ExitStack() as pile:
                for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                    pile.enter_context(patch.object(p, nom, {}))
                pile.enter_context(patch.object(p, "VERIFIER", False))
                if historique:
                    pile.enter_context(patch.object(p, "_departs", departs_historiques))
                with p.diagnostics() as recherches:
                    r = chercher(m, qui)
                comptes.append(recherches[0]["noeuds"])
                if executer:
                    m, _, lignes = executer(m, qui, r[1])
                else:
                    moteur = Moteur(m)
                    lignes = moteur.executer(moteur.preparer(proposition("attendre")))
            recharge = recharger(m)
            self.assertEqual(m.data, recharge.data)
            self.assertEqual(regarder(m), regarder(recharge))
            self.assertEqual(scene_percue(m), scene_percue(recharge))
            resultats.append((r, recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
        self.assertEqual(*resultats)
        return comptes, resultats[1]

    def test_remy_capture_moins_d_etats_meme_monde_et_rendu(self):
        chemin = Path(__file__).parent / "data/cout-12h/mine-1985-480.json.gz"
        m = Monde(json.loads(gzip.decompress(chemin.read_bytes())))
        comptes, resultat = self.comparer(m, "remy", lambda m, q: p.planifier(m, q, "faim"))
        self.assertIsNone(resultat[0])
        self.assertLess(comptes[1], comptes[0])

    def test_brune_reserve_plan_discret_identique_apres_recharge(self):
        m = relais()
        placer(m, "brune", "antichambre", (3, 4))
        autres = [q for q, o in m.objets.items() if o["type"] == "personnage" and q != "brune"]
        for n, autre in enumerate(autres):
            placer(m, autre, "crypte", (2 + n, 5))
        m.joueur.update(salle="chambre_cloche", position=[2, 2])
        m.data["salles"]["antichambre"]["lumiere_naturelle"] = 2
        with patch.object(Monde, "d20", return_value=20):
            _, resultat = self.comparer(m, "brune", lambda m, q: p.chercher(
                m, q, p.a_mange, emplois=("manger",), motif="faim"), executer_plan)
        r = resultat[0]
        self.assertIsNotNone(r)
        self.assertEqual(r[2].allure, 30)
        self.assertTrue(any(x.get("condition") == "sans_temoin" for x in r[1]))
        self.assertTrue(resultat[1]["objets"]["reserve"]["ouverte"])
        self.assertEqual(resultat[1]["objets"]["vivres"]["portions"], m.objets["vivres"]["portions"] - 1)

    def scene_flamme(self):
        m, qui, source, _ = flammes("relais")
        m.objets[source]["proprietaire"] = "aubin"
        m.objets[qui]["profil"]["valeurs"]["honnetete"] = 0
        for n, autre in enumerate(("aubin", "ilse", "brune")):
            placer(m, autre, "crypte", (2 + n, 5))
        m.joueur.update(salle="antichambre", position=[6, 5])
        return recharger(m), qui, source

    def test_allumage_illicite_executable_meme_monde_et_rendu(self):
        m, qui, source = self.scene_flamme()
        _, resultat = self.comparer(m, qui, lambda m, q: p.chercher(
            m, q, lambda v, e: bool(e.fait("allume", source)),
            {"entretenir": [source]}, emplois=("feu",)), executer_plan)
        self.assertTrue(resultat[1]["objets"][source]["allume"])
        self.assertEqual(resultat[0][2].allure, 30)

    def test_marque_retenue_des_la_premiere_recherche_et_invalidation(self):
        m, qui, source = self.scene_flamme()
        def chercher(gain):
            return p.chercher(m, qui, lambda v, e: bool(e.fait("allume", source)),
                              {"entretenir": [source]}, emplois=("feu",),
                              memo=["allumage-test"], endurer=gain)
        with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                patch.object(p, "_IMPOSSIBLES", {}), patch.object(p, "VERIFIER", True):
            r = chercher(1000)
            g = next(g for _, g in p._GRAPHES.values())
            self.assertTrue(g["discretion"])
            self.assertNotIn("sombre", g)  # la première recherche ne garde que la marque
            departs_lus = []
            explorer = p._explorer_etats
            def suivre(v, *a, **k):
                departs_lus.append((v._explore_furtif, k.get("differer", True)))
                return explorer(v, *a, **k)
            with patch.object(p, "_explorer_etats", suivre):
                self.assertEqual(chercher(1001), r)
                # Une seule passe jouée ; VERIFIER refait aussi ses témoins.
                self.assertEqual([furtif for furtif, jouee in departs_lus if jouee], [True])
            self.assertIs(next(g for _, g in p._GRAPHES.values()), g)
            # Même but, permission modifiée : les entrées relisent les gardes.
            m.objets[source]["proprietaire"] = qui
            m = recharger(m)
            ordinaire = chercher(1002)
            nouveau = next(g for _, g in p._GRAPHES.values())
            self.assertIsNot(nouveau, g)
            self.assertFalse(nouveau["discretion"])
            self.assertEqual(ordinaire[2].allure, 15)
            # Le geste discret redevient possible : nouvelle découverte, pas
            # de permission ni de marque figées par le graphe précédent.
            m.objets[source]["proprietaire"] = "aubin"
            m = recharger(m)
            self.assertEqual(chercher(1003), r)
            self.assertTrue(next(g for _, g in p._GRAPHES.values())["discretion"])

    def test_certificat_et_recherche_partagent_les_departs(self):
        m, qui, source = self.scene_flamme()
        v = p.Vue(m, qui)
        v.emplois = frozenset(("feu",))
        g = {}
        e = p.depart(m, qui, v)
        p._explorer(v, e, lambda v, e: bool(e.fait("allume", source)),
                    {"entretenir": [source]}, 8, p.NOEUDS, 0, graphe=g)
        self.assertTrue(g["discretion"])
        departs = p._departs(v, e)
        with patch.object(p, "_departs", wraps=p._departs) as d:
            self.assertFalse(p._sans_plan(v, e, None, 8, 0, False, g, False)[0])
        self.assertEqual(p._departs(*d.call_args.args), departs)
