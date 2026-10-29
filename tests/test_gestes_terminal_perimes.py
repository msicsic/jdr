"""Chaque offre U-T : numéro invalide puis choix devenu hors de vue à réception."""
import copy
import unittest
from unittest.mock import patch

from donjon.commandes import DescripteurPublic
from donjon.monde import Monde
from donjon.moteur import Moteur
from tests import test_gestes_terminal as terminal
from tests import test_descripteur_public as ud


def quitter_la_scene(monde, porte):
    monde.joueur.update(salle="grenier" if porte else "beffroi", position=[3, 3])


class ConsolePerimeeTests(unittest.TestCase):
    def test_chaque_geste_inconnu_ambigu_et_perime_sans_effet_ni_modele(self):
        interface = terminal.ConsoleTests()
        for porte, geste in terminal.CAS:
            with self.subTest(porte=porte, geste=geste):
                m, autre, cible = ud.scene(geste, porte)
                self.assertTrue(m.visible(cible) and m.visible(autre))
                _, numero, _ = terminal.menu(m, cible, geste)
                obtenu, sorties, _ = interface.jouer_console(
                    m, ["99999", "1 2", numero], lambda monde: quitter_la_scene(monde, porte))
                self.assertIn("Numéro inconnu dans la liste affichée.", sorties)
                self.assertIn("Choix ambigu : saisis un seul numéro de la liste affichée.", sorties)
                self.assertIn("Tu ne vois plus cette cible ici.", sorties)
                self.assertEqual(obtenu.objets[cible], m.objets[cible])
                self.assertEqual(obtenu.objets[autre], m.objets[autre])
                self.assertEqual(obtenu.data["journal"], m.data["journal"])
                self.assertEqual(ud.vues(obtenu), ud.vues(Monde(copy.deepcopy(obtenu.data))))


@unittest.skipUnless(terminal.tui.TEXTUAL, "Installer les dépendances TUI")
class TUIPerimeeTests(unittest.IsolatedAsyncioTestCase):
    async def test_chaque_geste_inconnu_ambigu_et_perime_sans_effet_ni_modele(self):
        interface = terminal.TerminalTests()
        preparer = Moteur.preparer
        for porte, geste in terminal.CAS:
            with self.subTest(porte=porte, geste=geste):
                m, autre, cible = ud.scene(geste, porte)
                self.assertTrue(m.visible(cible) and m.visible(autre))
                def preparation(moteur, p, *args, **kwargs):
                    if isinstance(p, DescripteurPublic):
                        quitter_la_scene(moteur.monde, porte)
                    return preparer(moteur, p, *args, **kwargs)
                with patch.object(Moteur, "preparer", preparation):
                    obtenu, sorties = await interface.jouer_tui(m, geste, cible, invalides=True)
                self.assertIn("Tu ne vois plus cette cible ici.", sorties)
                self.assertEqual(obtenu.objets[cible], m.objets[cible])
                self.assertEqual(obtenu.objets[autre], m.objets[autre])
                self.assertEqual(obtenu.data["journal"], m.data["journal"])
