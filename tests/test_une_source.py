"""Une source de lumière de plus, sans capacité que n'ait déjà une source portée, n'ouvre aucun geste.

Chaque cas compare la recherche à la même recherche sans la règle (``Vue.doublon`` à faux) et, quand
celle-ci atteint sa borne, à la recherche complète (``REFERENCE`` nœuds) : même résultat, moins d'états.
Les plans sont joués dans le monde et l'état relu après rechargement."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, pnj
from donjon.banc_pnj import creer
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.support import calme
from tests.test_tensions import placer, recharger

PLEINE = 240


def chercher(m, qui, but, vises, regle=True, noeuds=p.NOEUDS, **k):
    """La recherche neuve (caches vides), avec ou sans la règle ; (résultat, diagnostic)."""
    sans = {} if regle else {"doublon": lambda *a, **kw: False}
    with patch.multiple(p.Vue, **sans) if sans else patch.object(p, "BORNES", []), \
            patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), patch.object(p, "_IMPOSSIBLES", {}), \
            p.diagnostics() as diag:
        r = p.chercher(m, qui, but, vises, noeuds=noeuds, **k)
    return r, diag[-1]


def scene(scenario, qui, salle, ailleurs, porte, sources, briquet, donneur=None):
    """``qui`` dans ``salle`` obscure, avec ``briquet`` et la source ``porte`` ; ``sources`` :
    {source: (pleine, lieu)}, posées ou portées par ``donneur`` (seul avec lui, et à qui elles sont),
    sues de lui. Aucune réserve de combustible n'a de charge."""
    m = creer(scenario, 1985, "fixe")
    ids = [k for k, o in m.objets.items() if o.get("profil")]
    calme(m, *ids)
    for i, id in enumerate(x for x in ids if x not in (qui, donneur)):
        placer(m, id, ailleurs, (1 + i % 4, 1 + i // 4))
    placer(m, qui, salle, (2, 2))
    if donneur:
        placer(m, donneur, salle, (3, 2))
        # Le noir ne l'inquiète pas : il ne garde pas pour lui la lumière qu'il porte (``necessaire``).
        m.objets[donneur]["profil"].setdefault("securite", {})["noir"] = 0
    m.joueur.update(salle=ailleurs, position=[1, 3])
    for k, o in m.objets.items():
        if "allume" in o:
            o.update(allume=False, combustible=0)
        if "combustible" in o.get("usages", ()):
            o["charges"] = 0
    for i, (k, (pleine, lieu)) in enumerate(sources.items()):
        deplacer(m, k, lieu, position=[1 + i, 1] if lieu in m.data["salles"] else None)
        m.objets[k].update(combustible=PLEINE if pleine else 0, proprietaire=lieu if lieu == donneur else None)
    deplacer(m, briquet, qui)
    m.objets[briquet]["proprietaire"] = qui
    percevoir_tous(m)
    for s in m.data["salles"]:
        croire(m, qui, s, "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
    for k, o in m.objets.items():
        if "allume" in o:
            croire(m, qui, k, "etat", {"allume": False, "faible": False, "charge": bool(o["combustible"])}, "vu")
        if "combustible" in o.get("usages", ()):
            croire(m, qui, k, "etat", {"disponible": False}, "savoir")
    for k, (_, lieu) in sources.items():
        posee = lieu in m.data["salles"]
        croire(m, qui, k, "lieu", lieu, "savoir", salle=lieu if posee else salle,
               case=m.objets[k]["position"] if posee else [3, 2] if lieu == donneur else [2, 2])
    if donneur:
        croire(m, qui, donneur, "lieu", salle, "vu", salle=salle, case=[3, 2])
    lire(m, qui)["besoins"]["securite"] = 90.0
    m.objets[qui]["profil"]["valeurs"]["honnetete"] = 100
    assert m.objets[porte]["lieu"] == qui
    return recharger(m)


def jouer(test, m, qui, etapes):
    for etape in etapes:
        for _ in range(100):
            if pnj._executer(m, qui, etape, [], []):
                break
        else:
            test.fail(f"{etape} n'aboutit pas")
        m = recharger(m)
    recharge = recharger(m)
    test.assertEqual(m.data, recharge.data)
    test.assertEqual(regarder(recharge), regarder(m))
    test.assertEqual(scene_percue(recharge), scene_percue(m))
    return recharge


def acquiert(etapes, source):
    return any(x["operation"] in ("prendre", "demander", "acheter") and source in (x["cible"], x["outil"])
               for x in etapes)


class CapaciteTests(unittest.TestCase):
    def test_capacite_et_couverture(self):
        m = scene("mine", "remy", "baraquement", "bureau", "lampe_remy",
                  {"lampe_remy": (False, "remy"), "lampe_rechange_1": (True, "baraquement"),
                   "lampe_filon": (False, "baraquement")}, "briquet")
        v = p.Vue(m, "remy")
        e = p.depart(m, "remy", v)
        vide, pleine = v.capacite(e, "lampe_remy"), v.capacite(e, "lampe_rechange_1")
        self.assertEqual(vide, (1, "huile", True))
        self.assertEqual(pleine, (2, None, True))
        allumee = v.capacite(e.apres(faits=[(("allume", "lampe_remy"), True)]), "lampe_remy")
        self.assertEqual(allumee[0], 3)
        self.assertTrue(v.couvre(allumee, pleine) and v.couvre(pleine, vide) and v.couvre(vide, vide))
        self.assertFalse(v.couvre(vide, pleine))
        # Une autre substance n'est pas la même capacité ; une faute à toucher non plus.
        self.assertFalse(v.couvre((1, "cire", True), vide))
        self.assertFalse(v.couvre((2, None, False), pleine))
        # Une source vide ne couvre pas la pleine : elle s'acquiert ; une autre vide, non.
        self.assertFalse(v.doublon(e, "lampe_rechange_1", frozenset()))
        self.assertTrue(v.doublon(e, "lampe_filon", frozenset()))
        # Visée par le but, elle reste offerte.
        self.assertFalse(v.doublon(e, "lampe_filon", frozenset({"lampe_filon"})))
        # Un outil d'allumage n'est pas une source qui ne sert qu'à y voir.
        self.assertNotIn("briquet", v.sources_seules)


class UneSourceTests(unittest.TestCase):
    def test_source_pleine_demandee_quand_la_sienne_est_vide_deux_scenarios(self):
        # La seconde source apporte ce qui manque (une charge) : il la demande à qui la porte (il ne
        # peut l'allumer dans sa main), et l'allume ; une autre vide, que le même porte, n'est pas demandée.
        for scenario, qui, salle, ailleurs, porte, autre, inutile, briquet, donneur in (
            ("mine", "remy", "baraquement", "bureau", "lampe_remy", "lampe_rechange_1", "lampe_filon", "briquet",
             "gaspard"),
            ("auberge", "joss", "etable", "dortoir", "lanterne_etable", "lanterne_hugues", "bougeoir_mireille",
             "briquet_odile", "odile"),
        ):
            with self.subTest(scenario=scenario):
                m = scene(scenario, qui, salle, ailleurs, porte,
                          {porte: (False, qui), autre: (True, donneur), inutile: (False, donneur)}, briquet, donneur)
                with patch.object(p, "VERIFIER", True):
                    r, d = chercher(m, qui, p.eclaire, {"eclairer": True}, emplois=())
                sans, d_sans = chercher(m, qui, p.eclaire, {"eclairer": True}, regle=False, emplois=())
                self.assertEqual((r[0], r[1]), (sans[0], sans[1]))
                self.assertLessEqual(d["etats"], d_sans["etats"])
                self.assertTrue(acquiert(r[1], autre))
                self.assertFalse(acquiert(r[1], inutile))
                m = jouer(self, m, qui, p._couper(r[1]))
                self.assertEqual(m.objets[autre]["lieu"], qui)
                self.assertTrue(m.objets[autre]["allume"])
                self.assertEqual(m.objets[inutile]["lieu"], donneur)

    def test_seconde_source_sans_capacite_nouvelle_n_est_pas_prise_deux_scenarios(self):
        # Sa source est pleine : une autre pleine, ou une vide, n'apporte rien ; la recherche ne les
        # acquiert jamais, et rend le plan de la recherche sans la règle en moins d'états.
        for scenario, qui, salle, ailleurs, porte, pleine, vide, briquet in (
            ("mine", "remy", "baraquement", "bureau", "lampe_remy", "lampe_rechange_1", "lampe_filon", "briquet"),
            ("auberge", "joss", "etable", "dortoir", "lanterne_etable", "lanterne_hugues", "bougeoir_mireille",
             "briquet_odile"),
        ):
            with self.subTest(scenario=scenario):
                m = scene(scenario, qui, salle, ailleurs, porte,
                          {porte: (True, qui), pleine: (True, salle), vide: (False, salle)}, briquet)
                v = p.Vue(m, qui)
                e = p.depart(m, qui, v)
                offerts = [g[2] for g in p.gestes(v, e, {"eclairer": True}) if not isinstance(g, p.SuiteDifferee)]
                self.assertFalse(any(acquiert(x, pleine) or acquiert(x, vide) for x in offerts))
                with patch.object(p, "VERIFIER", True):
                    r, d = chercher(m, qui, p.eclaire, {"eclairer": True}, emplois=())
                sans, d_sans = chercher(m, qui, p.eclaire, {"eclairer": True}, regle=False, emplois=())
                self.assertEqual(r[0], sans[0])
                self.assertLess(d["etats"], d_sans["etats"])
                m = jouer(self, m, qui, p._couper(r[1]))
                self.assertTrue(m.objets[porte]["allume"])
                self.assertEqual(m.objets[pleine]["lieu"], salle)

    def test_source_visee_par_le_but_reste_prise(self):
        # Le but vise la seconde source (la rapporter ailleurs) : elle s'acquiert malgré la sienne, pleine.
        for scenario, qui, salle, ailleurs, porte, visee, briquet in (
            ("mine", "remy", "baraquement", "bureau", "lampe_remy", "lampe_rechange_1", "briquet"),
            ("auberge", "joss", "etable", "dortoir", "lanterne_etable", "lanterne_hugues", "briquet_odile"),
        ):
            with self.subTest(scenario=scenario):
                m = scene(scenario, qui, salle, ailleurs, porte, {porte: (True, qui), visee: (True, salle)}, briquet)
                cible = next(s for s in m.data["salles"] if s not in (salle, ailleurs)
                             and p.Vue(m, qui).route(p.depart(m, qui), s) is not None)
                def but(v, e):
                    return visee not in e.portes and v.lieu(e, visee) == cible
                vises = {"prendre": (visee,), "poser": (visee,)}
                with patch.object(p, "VERIFIER", True):
                    r, _ = chercher(m, qui, but, vises, emplois=())
                sans, _ = chercher(m, qui, but, vises, regle=False, emplois=())
                self.assertEqual((r[0], r[1]), (sans[0], sans[1]))
                self.assertTrue(acquiert(r[1], visee))
                m = jouer(self, m, qui, r[1])
                self.assertEqual(m.objets[visee]["lieu"], cible)


def borne(noeuds, chercher=p.chercher):
    def borne(*a, **k):
        return chercher(*a, **{**k, "noeuds": noeuds})
    return borne


class CaptureTests(unittest.TestCase):
    """La vraie nuit de la mine (graine 1985), rechargée à 8 h : les recherches qui atteignaient la borne."""

    def test_remy_et_josse_moins_d_etats_meme_resultat_que_la_recherche_complete(self):
        chemin = Path(__file__).parent / "data/cout-12h/mine-1985-480.json.gz"
        m = recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))
        for qui, faire in (
            ("remy", lambda m: p.planifier(m, "remy", "faim")),
            ("josse", lambda m: p.planifier_pulsion(m, "josse", {"objet": "poele", "allume": True})),
        ):
            with self.subTest(qui=qui):
                resultats = {}
                for cle, sans, noeuds in (("branche", {}, p.NOEUDS), ("base", {"doublon": lambda *a, **k: False}, p.NOEUDS),
                                          ("complete", {"doublon": lambda *a, **k: False}, p.REFERENCE)):
                    with patch.multiple(p.Vue, **sans) if sans else patch.object(p, "BORNES", []), \
                            patch.object(p, "chercher", borne(noeuds)), patch.object(p, "_MEMOIRE", {}), \
                            patch.object(p, "_GRAPHES", {}), patch.object(p, "_IMPOSSIBLES", {}), \
                            p.diagnostics() as diag:
                        r = faire(recharger(m))
                    resultats[cle] = (r, [x for x in diag if x["pnj"] == qui][-1])
                branche, base, complete = resultats["branche"], resultats["base"], resultats["complete"]
                self.assertEqual(base[1]["issue"], "borne")
                self.assertNotEqual(complete[1]["issue"], "borne")
                self.assertNotEqual(branche[1]["issue"], "borne")
                self.assertEqual(branche[0], complete[0])
                self.assertLess(branche[1]["etats"], complete[1]["etats"])
                self.assertLess(branche[1]["etats"], base[1]["etats"])


if __name__ == "__main__":
    unittest.main()
