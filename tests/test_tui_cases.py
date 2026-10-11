import asyncio
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

TEXTUAL = all(importlib.util.find_spec(m) is not None for m in ("textual", "pyperclip"))
if TEXTUAL:
    from donjon.tui import SeuilApp, SOL_VISIBLE, SOL_MEMORISE, SOUVENIR_OBJET, coloriser_plan, coloriser_legende
    from textual.widgets import Input


@unittest.skipUnless(TEXTUAL, "Installer requirements-tui.txt pour les tests d'interface")
class TUIExplorationTests(unittest.IsolatedAsyncioTestCase):
    def test_terrain_colore_sans_ponctuation_et_legende_lisible(self):
        ligne = f"{0:>4} " + ". : ##@ H2"
        rendu = coloriser_plan("NIVEAU +0\n" + ligne)
        self.assertEqual(rendu.plain, "NIVEAU +0\n" + f"{0:>4} " + "    ##@ H2")
        styles = [str(span.style) for span in rendu.spans]
        self.assertTrue(any(SOL_VISIBLE[0] in style for style in styles))
        self.assertTrue(any(SOL_MEMORISE[1] in style for style in styles))
        legende = coloriser_legende(
            "@ toi   ## mur   . terrain visible   : terrain mémorisé ou passage connu   cases vides : inconnues")
        self.assertIn("visible", legende.plain)
        self.assertIn("exploré hors de vue", legende.plain)
        self.assertNotIn(". terrain", legende.plain)

    def test_repere_souvenu_a_une_couleur_distincte(self):
        rendu = coloriser_plan("NIVEAU +0\n   0 ~k! ~XX ")
        self.assertIn("k ! X X ", rendu.plain)
        self.assertNotIn("~", rendu.plain)
        self.assertTrue(any(SOUVENIR_OBJET in str(span.style) for span in rendu.spans))
        self.assertTrue(any("#80d5d0" in str(span.style) for span in rendu.spans))
        legende = coloriser_legende(
            "~ : dernier aperçu, présence ou état actuels non confirmés\n~k la clé   ~X porte verrouillée")
        self.assertNotIn("~", legende.plain)
        self.assertIn("k la clé", legende.plain)
        self.assertIn("X porte verrouillée", legende.plain)

    async def test_focus_carte_marche_sans_detruire_la_saisie(self):
        app = SeuilApp([])
        vues = {"carte": "PLAN — 1 case = 1 m\nNIVEAU +0\n   0 @ . :\n\n=== LEGENDE ===\n@ toi",
                "fiche": "Corvus", "scene": "== SALLE ==\n\nUne pièce.", "salle": "Salle",
                "pv": "18/18", "or": 0, "minutes": 0, "proposition": "",
                "connexion": "hors ligne", "mode_cases": True}
        commandes = []

        def faux_jeu(argv, interface):
            interface.envoyer(app.actualiser, dict(vues))
            while True:
                commande = interface.lire("")
                if commande == "quitter":
                    return 0
                commandes.append(commande)
                vues["minutes"] += 1
                interface.envoyer(app.actualiser, dict(vues))

        with patch("jeu.main", side_effect=faux_jeu):
            async with app.run_test(size=(120, 40)) as pilot:
                for _ in range(250):
                    if app.derniere_vue and not app.occupe:
                        break
                    await asyncio.sleep(0.02)
                self.assertTrue(app.mode_cases)
                saisie = app.query_one("#commande", Input)
                saisie.value = "regarder"
                saisie.cursor_position = 3
                await pilot.press("ctrl+right")
                for _ in range(250):
                    if not app.occupe and app.derniere_vue.get("minutes") == 1:
                        break
                    await asyncio.sleep(0.02)
                await pilot.pause(0.1)
                self.assertEqual(saisie.value, "regarder")
                self.assertEqual(saisie.cursor_position, 3)
                self.assertEqual(commandes, ["pas est"])
                self.assertEqual(app.historique, [])
                await pilot.press("f6")
                self.assertTrue(app.focus_carte)
                await pilot.press("right")
                for _ in range(250):
                    if not app.occupe and app.derniere_vue.get("minutes") == 2:
                        break
                    await asyncio.sleep(0.02)
                await pilot.pause(0.1)
                self.assertEqual(saisie.value, "regarder")
                self.assertEqual(commandes, ["pas est", "pas est"])
                self.assertEqual(app.historique, [])
                self.assertIn("@", app.derniere_vue["carte"])
                self.assertIn("NIVEAU", app.query_one("#plan").render().plain)
                self.assertNotIn(". :", app.query_one("#plan").render().plain)
                await pilot.press("escape")
                self.assertFalse(app.focus_carte)
                self.assertIs(app.focused, saisie)
                app.action_quitter()

    async def test_ctrl_fleche_deplace_un_pas_dans_une_partie_cases(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            sauvegarde = Path(tmp) / "partie.json"
            app = SeuilApp(["--offline", "--cases", "--save", str(sauvegarde)])
            async with app.run_test(size=(120, 40)) as pilot:
                for _ in range(250):
                    if app.derniere_vue and not app.occupe:
                        break
                    await asyncio.sleep(0.02)
                self.assertTrue(app.mode_cases)
                avant = app.derniere_vue["carte"]
                await pilot.press("ctrl+right")
                for _ in range(250):
                    if not app.occupe and app.derniere_vue.get("carte") != avant:
                        break
                    await asyncio.sleep(0.02)
                from donjon.monde import Monde
                monde = Monde.charger(sauvegarde)
                self.assertEqual(monde.joueur["position"], [2, 2])
                self.assertEqual(monde.data["minutes"], 0)
                self.assertIn("NIVEAU", app.query_one("#plan").render().plain)
                app.action_quitter()
