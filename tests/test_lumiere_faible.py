"""Une recharge sans capacité nouvelle n'élargit pas le graphe de recherche."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.esprits import croire, lire
from donjon.deplacement_objet import deplacer
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger
from donjon.perception import recharge
from tests.test_une_source import chercher, scene, jouer
from tests.test_temps_etat import decouper


def capture(nom="capture-3"):
    return Monde(json.loads(gzip.decompress((Path(__file__).parent /
        "data/lumiere-faible" / (nom + ".json.gz")).read_bytes())))


def ancienne_recharge(v, e, s, entretenus=()):
    return not v.feu(e, s)[1]


class LumiereFaibleTests(unittest.TestCase):
    def setUp(self):
        for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
            remplacement = patch.object(p, nom, {})
            remplacement.start()
            self.addCleanup(remplacement.stop)

    def visible(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_captures_reelles_sous_plafond_meme_plan_que_complete(self):
        for nom, salle in (("capture-3", "grenier"), ("capture-3", "chambre_chaude"),
                           ("capture-7", "chambre_chaude")):
            with self.subTest(capture=nom, salle=salle):
                m = self.visible(capture(nom))
                self.assertTrue(lire(m, "lucien")["croyances"]["lanterne_hugues"]["etat"]["valeur"]["faible"])
                but = lambda v, e: e.salle == salle
                explorer = p._explorer
                def uniforme(*a, **kw):
                    return explorer(*a, **{**kw, "differer": False, "borner": False,
                                          "decouvrir_discretion": False})
                with patch.object(p.Vue, "recharge_utile", ancienne_recharge), \
                        patch.object(p, "_explorer", uniforme):
                    complet, ancien = chercher(m, "lucien", but, None, emplois=None, motif="biens",
                                               tenir=True, noeuds=p.REFERENCE)
                self.assertGreater(ancien["noeuds"], p.NOEUDS)
                nouveau, diag = chercher(m, "lucien", but, None, emplois=(), motif="biens", tenir=True)
                self.assertIsNotNone(nouveau)
                self.assertEqual(nouveau, complet)
                self.assertLess(diag["noeuds"], p.NOEUDS)

    def test_lucien_garde_un_but_monde_et_rendu_recharges_laps_decoupes(self):
        def fabriquer():
            for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                getattr(p, nom).clear()
            return capture()
        bloc, morceaux = decouper(fabriquer, 437, recharger_tous=7)
        # Les rotations du joueur changent son orientation et sa mémoire visuelle.
        # Comparer les conséquences des PNJ indépendamment de ces gestes du joueur.
        for m in (bloc, morceaux):
            self.assertIsNotNone(lire(m, "lucien")["intention"])
            self.visible(m)
        self.assertEqual(bloc.data["esprits"]["lucien"], morceaux.data["esprits"]["lucien"])
        self.assertEqual(bloc.objets, morceaux.objets)

    def test_autre_source_faible_recharge_seulement_si_capacite_absente(self):
        m = scene("mine", "remy", "baraquement", "bureau", "lampe_remy",
                  {"lampe_remy": (True, "remy"), "lampe_filon": (True, "baraquement")}, "briquet")
        for allume in (True, False):
            with self.subTest(allume=allume):
                monde = Monde(copy.deepcopy(m.data))
                monde.objets["lampe_remy"].update(allume=allume, combustible=20)
                croire(monde, "remy", "lampe_remy", "etat",
                       {"allume": allume, "charge": True, "faible": True}, "vu")
                monde = self.visible(monde)
                v = p.Vue(monde, "remy")
                e = p.depart(monde, "remy", v)
                self.assertEqual(v.capacite(e, "lampe_remy")[0], 3 if allume else 1)
                self.assertEqual(v.recharge_utile(e, "lampe_remy"), not allume)
                self.assertTrue(v.recharge_utile(e, "lampe_remy", ("lampe_remy",)))
                r, _ = chercher(monde, "remy", p.eclaire, {"eclairer": True}, emplois=())
                with patch.object(p.Vue, "recharge_utile", ancienne_recharge):
                    complet, _ = chercher(monde, "remy", p.eclaire, {"eclairer": True},
                                          emplois=None, noeuds=p.REFERENCE)
                self.assertEqual(r, complet)
                if allume:
                    self.assertEqual(r[1], [])
                moteur = Moteur(monde)
                moteur.executer(moteur.preparer(proposition("attendre")))
                self.visible(monde)

    def test_recharge_inutile_omise_mais_entretien_explicite_execute(self):
        m = scene("mine", "remy", "baraquement", "bureau", "lampe_remy",
                  {"lampe_remy": (True, "remy"), "lampe_filon": (True, "baraquement")}, "briquet")
        source = "lampe_filon"
        fuel = next(k for k, o in m.objets.items() if recharge(m.objets[source], o))
        deplacer(m, fuel, "remy")
        m.objets[fuel].update(charges=1, proprietaire="remy")
        m.objets[source].update(allume=True, combustible=20)
        croire(m, "remy", fuel, "lieu", "remy", "vu", salle="baraquement", case=[2, 2])
        croire(m, "remy", fuel, "etat", {"disponible": True}, "vu")
        croire(m, "remy", source, "etat", {"allume": True, "faible": True, "charge": True}, "vu")
        m = self.visible(m)
        v = p.Vue(m, "remy")
        v.eclairer = True
        e = p.depart(m, "remy", v)
        ordinaires = [g[2] for g in p.gestes(v, e, {}) if not isinstance(g, p.SuiteDifferee)]
        self.assertFalse(any(x["operation"] == "alimenter" and x["cible"] == source
                             for gs in ordinaires for x in gs))
        entretien = [g[2] for g in p.gestes(v, e, {"entretenir": (source,)})
                     if not isinstance(g, p.SuiteDifferee)]
        gestes = next(gs for gs in entretien if any(x["operation"] == "alimenter" and x["cible"] == source
                                                   for x in gs))
        avant = m.objets[source]["combustible"]
        m = jouer(self, m, "remy", gestes)
        self.assertGreater(m.objets[source]["combustible"], avant)
        self.assertEqual(m.objets[fuel]["charges"], 0)
        self.visible(m)

    def test_lampe_faible_a_la_mine_meme_laps_decoupe(self):
        def fabriquer():
            for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                getattr(p, nom).clear()
            m = scene("mine", "remy", "baraquement", "bureau", "lampe_remy",
                      {"lampe_remy": (True, "remy")}, "briquet")
            m.objets["lampe_remy"].update(allume=True, combustible=20)
            croire(m, "remy", "lampe_remy", "etat",
                   {"allume": True, "charge": True, "faible": True}, "vu")
            return self.visible(m)
        bloc, morceaux = decouper(fabriquer, 1, recharger_tous=7)
        for m in (bloc, morceaux):
            self.assertTrue(m.objets["lampe_remy"]["allume"])
            self.visible(m)
        self.assertEqual(bloc.objets, morceaux.objets)
        self.assertEqual(lire(bloc, "remy"), lire(morceaux, "remy"))
