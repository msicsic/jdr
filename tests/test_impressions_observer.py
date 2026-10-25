"""Observer restitue une lecture actuelle, même déjà annoncée, après reprise."""
import copy
from pathlib import Path
import unittest

from donjon import signes
from donjon.commandes import analyser
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.rendu import regarder
from tests.test_signes import ecarter, scene
from tests.test_social import recharger


class ImpressionsObserverTests(unittest.TestCase):
    def observer(self, m, id):
        moteur = Moteur(m)
        texte = moteur.executer(moteur.preparer(analyser(m, "observer " + id)))
        self.assertEqual(m.data["journal"][-1]["faits"], texte.splitlines())
        avant = copy.deepcopy(m.data)
        vue = regarder(m)
        reprise = recharger(m)
        self.assertEqual(reprise.data, avant)
        self.assertEqual(regarder(reprise), vue)
        self.assertEqual(reprise.data["journal"][-1]["faits"], texte.splitlines())
        return reprise, texte

    def cas(self):
        # Le script réel lit Ilse au bilan de « observer Brune », avant de la cibler.
        m = Monde.charger(Path(__file__).parent / "data/scenes/signes_ecart_relais.json")
        m, _ = self.observer(m, "brune")
        self.assertEqual({s["texte"] for s in signes.impressions(m)},
                         {"Ilse semble craindre Brune.", "Ilse semble avoir peur."})
        yield m, "ilse", "brune"
        m = ecarter(scene(), "brune", "ilse")
        m, _ = self.observer(m, "brune")
        yield m, "brune", "ilse"

    def test_observations_successives_rendent_les_impressions_sans_relancer(self):
        for m, id, autre in self.cas():
            with self.subTest(id=id):
                lectures = copy.deepcopy(m.data["lectures"])
                tirages = m.data["tirages_lecture_acteurs"]["joueur"]
                attendus = {s["texte"] for s in signes.impressions(m) if s["personnage"] == id}
                physiques = {s["texte"] for s in signes.publics(m) if s["personnage"] == id}
                self.assertTrue(attendus)
                for _ in range(2):
                    m, texte = self.observer(m, id)
                    self.assertTrue(attendus <= set(texte.splitlines()))
                    self.assertTrue(physiques <= set(texte.splitlines()))
                    self.assertEqual(m.data["lectures"], lectures)
                    self.assertEqual(m.data["tirages_lecture_acteurs"]["joueur"], tirages)
                    for impression in attendus:
                        self.assertIn(impression, regarder(m))
                # Le bilan spontané ne répète toujours pas les lectures acquises.
                self.assertFalse(any("semble" in l for l in signes.bilan_signes(m)))

    def test_signe_disparu_retire_son_impression_mais_garde_la_memoire(self):
        for m, id, autre in self.cas():
            with self.subTest(id=id):
                lectures = copy.deepcopy(m.data["lectures"])
                e = lire(m, id)
                e["relations"].clear()
                if e["intention"]:
                    e["intention"].get("attitude", {}).pop("place", None)
                # La peur sans cible demeure : seule la crainte appuyée par l'écart/les yeux cesse.
                m = recharger(m)
                self.assertFalse(any(s["envers"] == autre and s["personnage"] == id
                                     for s in signes.publics(m)))
                restantes = {s["texte"] for s in signes.impressions(m) if s["personnage"] == id}
                m, texte = self.observer(m, id)
                self.assertNotIn("semble craindre", texte)
                self.assertTrue(restantes <= set(texte.splitlines()))
                self.assertEqual(m.data["lectures"], lectures)
                self.assertNotIn("semble craindre", regarder(m))
                self.assertFalse(any(s["envers"] == autre for s in signes.impressions(m)
                                     if s["personnage"] == id))

    def test_perte_de_vue_masque_la_lecture_et_retour_sans_nouveau_de(self):
        for m, id, _ in self.cas():
            with self.subTest(id=id):
                lectures = copy.deepcopy(m.data["lectures"])
                tirages = m.data["tirages_lecture_acteurs"]["joueur"]
                orientation = m.joueur["orientation"]
                m.joueur["orientation"] = "ouest"
                m = recharger(m)
                self.assertFalse(signes.impressions(m))
                self.assertNotIn("semble", regarder(m))
                m.joueur["orientation"] = orientation
                m = recharger(m)
                m, texte = self.observer(m, id)
                self.assertIn("semble", texte)
                self.assertEqual(m.data["lectures"], lectures)
                self.assertEqual(m.data["tirages_lecture_acteurs"]["joueur"], tirages)
