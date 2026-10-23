"""Temps prévu, exécution, perception et état sauvegardé du même trajet."""
import copy
import unittest
from unittest.mock import patch

from donjon import planification as p, spatial
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire
from donjon.monde import objet
from donjon.moteur import Moteur, proposition
from donjon.obstacles import cout_route
from donjon.pnj import agir, DUREES
from donjon.temps import MINUTE
from tests.support import calme
from tests.test_marche import intention
from tests.test_tensions import placer, recharger


def savoir(m, qui, o):
    x = m.objets[o]
    croire(m, qui, o, "lieu", x["lieu"], "savoir", salle=x["lieu"] if x["lieu"] in m.data["salles"] else None,
           case=x.get("position") if x["lieu"] in m.data["salles"] else None)
    if "allume" in x:
        croire(m, qui, o, "etat", {"allume": x["allume"], "charge": True}, "savoir")


def flammes(scenario):
    m = creer(scenario, 42, "fixe")
    calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
    qui, salle, source, feux = (("marchand", "echoppe", "torche", ("brasero", "fanal"))
                               if scenario == "relais" else
                               ("remy", "baraquement", "lampe_remy", ("lampe_baraque", "poele")))
    if source not in m.objets:
        source = next(k for k, o in m.objets.items() if o.get("mobile") and "allume" in o and o["lieu"] != "joueur")
    if scenario == "relais":
        m.data["salles"][salle]["plan"]["sol"] = ["........."] * 7
    placer(m, qui, salle, (6, 5))
    m.objets[qui]["orientation"] = "nord"
    m.objets[qui]["profil"]["pulsions"] = []
    lire(m, qui)["pulsions"] = []
    lire(m, qui)["croyances"].clear()
    for k, case in zip(feux, ((0, 0), (6, 3))):
        placer(m, k, salle, case)
        m.objets[k].update(allume=True, combustible=720, proprietaire=qui, mobile=False)
        savoir(m, qui, k)
    m.objets[source].update(lieu=qui, allume=False, combustible=120, proprietaire=qui)
    savoir(m, qui, source)
    # Les autres corps restent hors des cases de l'approche.
    autres = [k for k, o in m.objets.items() if o["type"] == "personnage" and k != qui and o["lieu"] == salle]
    for n, k in enumerate(autres):
        placer(m, k, salle, (8, n))
    m.joueur.update(salle=salle, position=[5, 5], orientation="nord")
    return recharger(m), qui, source, feux


def executer_plan(m, qui, etapes):
    intention(m, qui, etapes)
    temps, lignes = 0, []
    for _ in range(200):
        if not lire(m, qui)["intention"] or not lire(m, qui)["intention"]["plan"]:
            break
        duree, issue, _ = agir(m, qui, temps, lignes)
        if issue == "fin":
            break
        if issue in ("manque", "attente"):
            raise AssertionError((issue, lire(m, qui)["intention"]))
        temps += duree
    else:
        raise AssertionError("Plan inachevé")
    return recharger(m), temps, lignes


class TempsReelsTests(unittest.TestCase):
    def test_allure_feutree_du_plan_depuis_la_premiere_approche(self):
        m, qui, source, feux = flammes("relais")
        m.objets[source]["proprietaire"] = "aubin"
        m.objets[qui]["profil"]["valeurs"]["honnetete"] = 0
        for n, autre in enumerate(("aubin", "ilse", "brune")):
            placer(m, autre, "crypte", (2 + n, 5))
        m.joueur.update(salle="antichambre", position=[6, 5])
        m = recharger(m)
        but = lambda v, e: bool(e.fait("allume", source))
        r = p.chercher(m, qui, but, {"entretenir": [source]}, emplois=("feu",))
        self.assertIsNotNone(r)
        self.assertEqual(r[2].allure, 30)
        self.assertEqual(r[1][-1]["condition"], "sans_temoin")
        v = p.Vue(m, qui)
        e = p.depart(m, qui, v).apres(allure=30)
        t, _, _ = p._mesurer(v, e, r[1], r[2], 1)
        m, reel, _ = executer_plan(m, qui, r[1])
        self.assertAlmostEqual(t * MINUTE, reel)
        self.assertTrue(m.objets[source]["allume"])

    def test_une_cle_posee_ne_reste_pas_dans_le_parcours_projete(self):
        m, qui, _, _ = flammes("relais")
        m.objets["cle"]["lieu"] = qui
        m.objets["porte"].update(ouverte=False, verrouillee=True)
        savoir(m, qui, "cle")
        croire(m, qui, "porte", "verrouillee", True, "savoir")
        croire(m, qui, "porte", "etat", {"ouverte": False}, "savoir")
        m = recharger(m)
        v = p.Vue(m, qui)
        e = p.depart(m, qui, v)
        self.assertIsNotNone(v.route(e, "beffroi"))
        self.assertIsNone(v.route(e.apres(portes=e.portes - {"cle"}), "beffroi"))
        # L'autre sens : le plan ferme à clé une porte crue déverrouillée.
        croire(m, qui, "porte", "verrouillee", False, "savoir")
        v = p.Vue(m, qui)
        sans_cle = p.depart(m, qui, v).apres(portes=e.portes - {"cle"})
        self.assertIsNotNone(v.route(sans_cle, "beffroi"))
        ferme = sans_cle.apres(faits=[(("verrou", "porte"), True)])
        self.assertIsNone(v.route(ferme, "beffroi"))
        self.assertNotIn("beffroi", dict(v.allers(ferme, v.ouvertes(ferme))))
        m, _, _ = executer_plan(m, qui, [p._etape("poser", "cle", lieu=e.salle)])
        self.assertEqual(m.objets["cle"]["lieu"], e.salle)
        self.assertNotIn("cle", p.depart(m, qui).portes)

    def test_deux_portes_courtes_plutot_qu_un_long_detour_par_une_porte(self):
        m = creer("relais", 42, "fixe")
        calme(m, "marchand", "brune", "ilse", "aubin")
        for nom, largeur, origine in (("depart_test", 31, [50, 50]),
                                      ("milieu_test", 3, [40, 50]), ("fin_test", 3, [90, 50])):
            m.data["salles"][nom] = {"nom": nom, "fenetres": 0, "lumiere_naturelle": 0,
                                      "plan": {"origine": origine, "sol": ["." * largeur] * 3},
                                      "sorties": {}}
        for a, b, da, db, ca, cb, porte in (
                ("depart_test", "fin_test", "est", "ouest", [31, 1], [-1, 1], "direct_test"),
                ("depart_test", "milieu_test", "ouest", "est", [-1, 1], [3, 1], "court1_test"),
                ("milieu_test", "fin_test", "nord", "sud", [1, -1], [1, 3], "court2_test")):
            m.data["salles"][a]["sorties"][da] = {"vers": b, "porte": porte, "case": ca, "escalier": True}
            m.data["salles"][b]["sorties"][db] = {"vers": a, "porte": porte, "case": cb, "escalier": True}
            m.objets[porte] = objet(porte, porte, "porte", a, relie=[a, b], ouverte=False, verrouillee=False)
            croire(m, "marchand", porte, "etat", {"ouverte": False}, "savoir")
        placer(m, "marchand", "depart_test", (0, 1))
        m.objets["marchand"]["orientation"] = "ouest"
        spatial.installer(m)
        m = recharger(m)
        v = p.Vue(m, "marchand")
        e = p.depart(m, "marchand", v)
        route = v.route(e, "fin_test")
        self.assertEqual([s["porte"] for s in route], ["court1_test", "court2_test"])
        temps = cout_route(route, e.orientation)
        m, t, _ = executer_plan(m, "marchand", [p._etape("aller", lieu="fin_test")])
        self.assertEqual(m.objets["marchand"]["lieu"], "fin_test")
        self.assertTrue(m.objets["court1_test"]["ouverte"])
        self.assertTrue(m.objets["court2_test"]["ouverte"])
        self.assertFalse(m.objets["direct_test"]["ouverte"])
        self.assertAlmostEqual(t / MINUTE, temps)

    def test_deux_flammes_connues_la_plus_proche_et_duree_executee(self):
        for scenario in ("relais", "mine"):
            with self.subTest(scenario=scenario):
                m, qui, source, feux = flammes(scenario)
                but = lambda v, e: bool(e.fait("allume", source))
                with patch.object(p, "VERIFIER", True), patch.object(spatial, "VERIFICATION", 1):
                    r = p.chercher(m, qui, but, {"entretenir": [source]}, emplois=("feu",), nom="flamme-proche")
                self.assertIsNotNone(r)
                self.assertEqual(r[1][-1]["outil"], feux[1])
                v = p.Vue(m, qui)
                e = p.depart(m, qui, v)
                suites = [s for s in p._suites(v, e, {"entretenir": [source]}, but)
                          if s[2] and s[2][0]["operation"] == "allumer"]
                proche = next(s for s in suites if s[2][0]["outil"] == feux[1])
                loin = next(s for s in suites if s[2][0]["outil"] == feux[0])
                self.assertLess(proche[4], loin[4])
                m, temps, lignes = executer_plan(m, qui, r[1])
                self.assertAlmostEqual(proche[4] * MINUTE, temps)
                self.assertTrue(m.objets[source]["allume"])
                self.assertIn("allume", " ".join(lignes))
                self.assertEqual(tuple(m.objets[qui]["position"]), proche[3].case)
                self.assertTrue(m.visible(source))

    def test_objet_lointain_approche_et_position_du_geste_suivant(self):
        m, qui, _, _ = flammes("relais")
        for k, case in (("proche_test", (6, 4)), ("loin_test", (0, 0))):
            m.objets[k] = objet(k, k, "outil", "echoppe", mobile=True, position=list(case),
                                position_salle="echoppe", proprietaire=qui)
            savoir(m, qui, k)
        m = recharger(m)
        v = p.Vue(m, qui)
        e = p.depart(m, qui, v)
        vises = {"prendre": ["proche_test", "loin_test"]}
        but = lambda v, e: "loin_test" in e.portes
        prises = {s[2][0]["cible"]: s for s in p._suites(v, e, vises, but)
                  if s[2] and s[2][0]["operation"] == "prendre"}
        self.assertGreater(prises["loin_test"][4], prises["proche_test"][4])
        pres = prises["loin_test"][3]
        retour = p._mesurer(v, pres, [p._etape("prendre", "proche_test")],
                           pres.apres(portes=pres.portes | {"proche_test"}), 1)
        self.assertGreater(retour[0], DUREES["prendre"] / MINUTE)
        m, t, lignes = executer_plan(m, qui, prises["loin_test"][2])
        self.assertEqual(m.objets["loin_test"]["lieu"], qui)
        self.assertAlmostEqual(t / MINUTE, prises["loin_test"][4])
        self.assertIn("prend", " ".join(lignes))

    def test_pression_du_noir_proportionnelle_au_temps_et_avant_allumage(self):
        m, qui, source, feux = flammes("relais")
        m.objets[qui]["profil"].setdefault("securite", {})["noir"] = 1
        croire(m, qui, "echoppe", "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "savoir")
        m = recharger(m)
        v = p.Vue(m, qui)
        e = p.depart(m, qui, v)
        couts = []
        for f in feux:
            t, pression, final = p._mesurer(v, e, [p._etape("allumer", source, outil=f)],
                                          e.apres(faits=[(("allume", source), True)]), 1)
            couts.append(t)
            self.assertAlmostEqual(pression, t * p.NOIR)
            self.assertEqual(v.pression(final), 0)
        self.assertGreater(couts[0], couts[1])
        m, _, lignes = executer_plan(m, qui, [p._etape("allumer", source, outil=feux[1])])
        self.assertTrue(m.objets[source]["allume"])
        self.assertIn("allume", " ".join(lignes))

    def test_obstacle_cru_contre_obstacle_ignore_et_cache(self):
        from tests.test_sous_obstacle import corridor
        m = recharger(corridor())
        v, qui = p.Vue(m, "marchand"), "marchand"
        e = p.depart(m, qui, v)
        avec = cout_route(v.route(e, "antichambre"), e.orientation)
        avant = p._entrees(v, {}, 8, 4000)
        for k in list(lire(m, qui)["croyances"]):
            if m.objets.get(k, {}).get("bloque_passage"):
                del lire(m, qui)["croyances"][k]
        m = recharger(m)
        with patch.object(spatial, "VERIFICATION", 1):
            v = p.Vue(m, qui)
            e = p.depart(m, qui, v)
            sans = cout_route(v.route(e, "antichambre"), e.orientation)
        self.assertLess(sans, avec)
        self.assertNotEqual(avant, p._entrees(v, {}, 8, 4000))
        self.assertTrue(m.objets["poutre_conduite"]["bloque_passage"])

    def test_meme_laps_bloc_ou_decoupe_avec_rechargement(self):
        m, qui, source, feux = flammes("relais")
        intention(m, qui, [p._etape("allumer", source, outil=feux[1])])
        bloc, morceaux = recharger(m), recharger(m)
        texte = Moteur(bloc).executer(Moteur(bloc).preparer(proposition("attendre", "30")))
        for _ in range(6):
            Moteur(morceaux).executer(Moteur(morceaux).preparer(proposition("attendre", "5")))
            morceaux = recharger(morceaux)
        bloc = recharger(bloc)
        from tests.test_temps_etat import etat_pnj
        self.assertEqual(etat_pnj(bloc), etat_pnj(morceaux))
        self.assertTrue(bloc.objets[source]["allume"])
        self.assertIn("allume", texte)


if __name__ == "__main__":
    unittest.main()
