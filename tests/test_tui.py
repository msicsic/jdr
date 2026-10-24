import asyncio
import importlib.util
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from donjon.mj import MJOpenAI
from donjon.defi import nouveau_defi
from donjon.faits_locaux import preparer_faits
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import proposition
from donjon.rendu import decrire
from donjon.operations import sequence, etape
from donjon.improvisation import proposition as improviser, issue
from donjon.spatial import installer
from donjon.spatial import position_carte, position_cible
from tests.support import sans_budget, simuler_couverture

# Délai d'une attente : large, pour qu'une machine chargée ne fasse pas échouer un test qui
# attend un état ; un blocage réel échoue quand même, avec l'état observé.
DELAI = 60

TEXTUAL = all(importlib.util.find_spec(m) is not None for m in ("textual", "pyperclip"))
if TEXTUAL:
    from donjon.tui import SeuilApp
    from textual.widgets import Input, TabbedContent


@unittest.skipUnless(TEXTUAL, "Installer requirements-tui.txt pour les tests d'interface")
class TUITests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        simuler_couverture(self)

    async def test_avis_libre_d_action_ne_traverse_pas_la_tui_ni_la_sauvegarde(self):
        invention = "Une seconde cloche est sous le plancher."
        reponse = {"mode": "action", "texte": "", "faits": [],
                   "proposition": proposition("observer", "scene", justification=invention)}
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(MJOpenAI, "_appeler_brut", return_value=reponse), \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj je regarde autour de moi", 0)
                self.assertNotIn(invention, " ".join(app.sorties))
                reprise = Monde.charger(chemin)
                self.assertNotIn(invention, str(reprise.data["journal"]))
                self.assertNotIn(invention, str(reprise.data["conversation"]))
                self.assertNotIn("seconde_cloche", reprise.objets)
                await self.fermer(app)

    async def test_capacites_improvisees_utilisables_et_sauvees_dans_la_tui(self):
        monde = sans_budget(nouveau_defi(depart="fixe"))
        installer(monde)
        monde, _, etablis = preparer_faits(monde, {"ajouts": [
            {"type": "objet", "ancrage": "antichambre_sol", "nom": "timbre de fer",
             "genre": "m", "texte": "Le métal résonne quand on le frappe.",
             "materiau": "fer", "masse": 0.2, "mobile": True, "relation": "pose",
             "capacites": [{"nature": "son", "intensite": 2}]},
            {"type": "objet", "ancrage": "antichambre_sol", "nom": "lampe à huile",
             "genre": "f", "texte": "Une mèche plonge dans l'huile de son réservoir.",
             "materiau": "cuivre et verre", "masse": 0.4, "mobile": True,
             "relation": "pose", "capacites": [{"nature": "lumiere", "niveau": 2,
                                                  "combustible": 6}]},
        ]})
        timbre, lampe = (e["objet"] for e in etablis)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            monde.sauver(chemin)
            app = SeuilApp(["--defi", "--offline", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                self.assertIn("timbre de fer", app.derniere_vue["carte"])
                await self.commande(app, pilot, "sonner timbre de fer")
                self.assertIn("produis un son", " ".join(app.sorties))
                self.assertEqual(Monde.charger(chemin).data["sons"][-1]["objet"], timbre)
                await self.commande(app, pilot, "prendre lampe à huile")
                await self.commande(app, pilot, "allumer lampe à huile")
                reprise = Monde.charger(chemin)
                self.assertTrue(reprise.objets[lampe]["allume"])
                self.assertEqual(reprise.objets[lampe]["lieu"], "joueur")
                self.assertIn("lampe à huile", app.derniere_vue["fiche"])
                await self.fermer(app)

    async def test_narration_fausse_corrigee_avant_affichage_et_sauvegardee(self):
        invention = "Une seconde cloche est cachée sous le plancher."
        corrige = "Tu te trouves dans : Antichambre."
        reponses = [
            {"mode": "dialogue", "texte": invention, "faits": [], "proposition": None},
            {"segments": [{"indice": 0, "verdict": "invention_protegee", "sources": [],
                           "locuteur": "", "citation": "", "entites": [], "motif": "Aucune seconde cloche établie."}]},
            {"mode": "dialogue", "texte": corrige, "faits": ["attestations"], "proposition": None},
            {"segments": [{"indice": 0, "verdict": "mecanique", "sources": ["attestations"],
                           "locuteur": "", "citation": "", "entites": [], "motif": ""}]},
        ]
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(MJOpenAI, "_appeler_brut", side_effect=reponses) as api, \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj Que vois-je ?", 0)
                self.assertNotIn(invention, " ".join(app.sorties))
                self.assertIn(corrige, " ".join(app.sorties))
                self.assertEqual(Monde.charger(chemin).data["narrations_mj"][-1]["texte"], corrige)
                await self.fermer(app)
            self.assertEqual(api.call_count, 4)

    async def test_inscription_du_mj_affichee_apres_sauvegarde_et_lisible(self):
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [{"type": "inscription",
                                               "ancrage": "antichambre_murs", "nom": "", "genre": "",
                                               "texte": "Veille au niveau des eaux."}]}}
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(MJOpenAI, "_appeler", return_value=reponse) as api, \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj y a-t-il une inscription sur les murs ?", 0)
                self.assertIn("Veille au niveau des eaux.", " ".join(app.sorties))
                self.assertIn("inscription sur les murs", app.derniere_vue["scene"])
                self.assertIn("fait_1_1", Monde.charger(chemin).objets)
                await self.fermer(app)
            api.assert_called_once()

    async def test_objet_du_mj_sur_la_carte_puis_dans_la_besace(self):
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [{
                       "type": "objet", "ancrage": "antichambre_sol",
                       "nom": "bouton de cuivre", "genre": "m",
                       "texte": "Un petit bouton rond repose sur la pierre.",
                       "materiau": "cuivre", "masse": 0.01, "mobile": True, "capacites": [],
                       "relation": "pose"}]}}
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(MJOpenAI, "_appeler", return_value=reponse), \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--defi", "--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj Que vois-je sur le sol ?", 0)
                cree = Monde.charger(chemin)
                id = cree.trouver("bouton de cuivre")
                self.assertIn("bouton de cuivre", app.derniere_vue["carte"])
                self.assertIn("bouton de cuivre", " ".join(app.sorties))
                await self.commande(app, pilot, "prendre bouton de cuivre")
                repris = Monde.charger(chemin)
                self.assertEqual(repris.objets[id]["lieu"], "joueur")
                self.assertNotIn("bouton de cuivre", app.derniere_vue["carte"])
                self.assertIn("bouton de cuivre", app.derniere_vue["fiche"])
                await self.fermer(app)

    async def test_objet_fixe_est_detache_sur_place_puis_pris(self):
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [{
                       "type": "objet", "ancrage": "antichambre_murs",
                       "nom": "crochet de cuivre", "genre": "m",
                       "texte": "Sa surface est couverte de patine.",
                       "materiau": "cuivre", "masse": 0.05, "mobile": True, "capacites": [],
                       "relation": "fixe"}]}}
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(MJOpenAI, "_appeler", return_value=reponse), \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--defi", "--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj Que vois-je sur les murs ?", 0)
                cree = Monde.charger(chemin)
                id = cree.trouver("crochet de cuivre")
                self.assertTrue(cree.objets[id]["attache"])
                self.assertEqual(position_cible(cree, id), (2, 3))
                self.assertEqual(position_carte(cree, id), (3, 3))
                self.assertIn("fixé aux murs", " ".join(app.sorties))
                self.assertIn("fixé aux murs", decrire(cree, id))
                self.assertIn("&#", app.derniere_vue["carte"])
                self.assertIn("crochet de cuivre", app.derniere_vue["carte"])
                await self.commande(app, pilot, "prendre crochet de cuivre")
                self.assertEqual(Monde.charger(chemin).objets[id]["lieu"], "antichambre_murs")
                self.assertIn("crochet de cuivre", app.derniere_vue["carte"])
                await self.commande(app, pilot, "détacher crochet de cuivre")
                libere = Monde.charger(chemin)
                # Détacher libère sur place, sans ranger : prendre est un geste distinct.
                self.assertFalse(libere.objets[id]["attache"])
                self.assertEqual(libere.objets[id]["lieu"], libere.joueur["salle"])
                await self.commande(app, pilot, "prendre crochet de cuivre")
                libere = Monde.charger(chemin)
                self.assertEqual(libere.objets[id]["lieu"], "joueur")
                self.assertNotIn("relation_support", libere.objets[id])
                self.assertEqual(position_carte(libere, id), tuple(libere.joueur["position"]))
                self.assertNotIn("ancrage_carte", libere.objets[id])
                self.assertNotIn("crochet de cuivre", app.derniere_vue["carte"])
                self.assertIn("crochet de cuivre", app.derniere_vue["fiche"])
                await self.fermer(app)

    async def test_objet_fixe_reste_sur_le_mur_en_souvenir_apres_rechargement(self):
        from donjon.spatial import memoriser

        monde = nouveau_defi(depart="fixe")
        installer(monde)
        monde, _, etablis = preparer_faits(monde, {"ajouts": [{
            "type": "objet", "ancrage": "antichambre_murs",
            "nom": "crochet de cuivre", "genre": "m",
            "texte": "Sa surface est patinée.", "materiau": "cuivre",
            "masse": 0.05, "mobile": True, "relation": "fixe", "capacites": []}]})
        id = etablis[0]["objet"]
        memoriser(monde)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            monde.sauver(chemin)
            app = SeuilApp(["--defi", "--offline", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)):
                await self.pret(app)
                self.assertIn("&#", app.derniere_vue["carte"])
                await self.fermer(app)

            monde = Monde.charger(chemin)
            monde.joueur["position"] = [7, 3]
            memoriser(monde)
            monde.sauver(chemin)
            app = SeuilApp(["--defi", "--offline", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)):
                await self.pret(app)
                self.assertEqual(Monde.charger(chemin).objets[id]["ancrage_carte"], [3, 3])
                self.assertIn("&~", app.derniere_vue["carte"])
                self.assertIn("crochet de cuivre", app.derniere_vue["carte"])
                self.assertIn("&#", app.query_one("#plan").render().plain)
                await self.fermer(app)

    async def test_detail_hors_portee_revise_avant_affichage_et_sauvegarde(self):
        invention = "Une seconde cloche est cachée sous le plancher."
        corrige = "Une tache sombre couvre quelques pierres."
        def proposition_mj(texte):
            return {"mode": "etablir_faits", "texte": "",
                    "faits": ["faits_narratifs_proposables"],
                    "proposition": {"ajouts": [{"type": "detail",
                                               "ancrage": "antichambre_murs",
                                               "nom": "tache d'humidité", "genre": "f",
                                               "texte": texte}]}}
        reponses = [
            proposition_mj(invention),
            {"usages": [{"perception_requise": False, "indice": False, "motif": ""}], "descriptions": [
                {"representation": "aspect", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [{"texte": "tache d'humidité", "portee": "sujet", "preuve": "", "motif": ""}]},
                {"representation": "etat_du_monde", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [{"texte": invention, "portee": "sans_preuve", "preuve": "", "motif": "Autre objet."}]},
            ]},
            proposition_mj(corrige),
            {"usages": [{"perception_requise": False, "indice": False, "motif": ""}], "descriptions": [
                {"representation": "aspect", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [{"texte": "tache d'humidité", "portee": "sujet", "preuve": "", "motif": ""}]},
                {"representation": "aspect", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [{"texte": corrige, "portee": "sujet", "preuve": "", "motif": ""}]},
            ]},
        ]
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(MJOpenAI, "_appeler_brut", side_effect=reponses) as api, \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj Décris un détail sur les murs.", 0)
                self.assertNotIn(invention, " ".join(app.sorties))
                self.assertIn(corrige, " ".join(app.sorties))
                detail = Monde.charger(chemin).trouver("tache d'humidité")
                self.assertEqual(Monde.charger(chemin).objets[detail]["description_visuelle"], corrige)
                self.assertIn("tache d'humidité", app.derniere_vue["scene"])
                await self.fermer(app)
            self.assertEqual(api.call_count, 4)

    async def test_sortie_galerie_vers_palier_noir_garde_joueur_sur_la_carte(self):
        with tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parents[1], suffix=".json", delete=False) as fichier:
            chemin = Path(fichier.name)
        self.addCleanup(chemin.unlink, missing_ok=True)
        monde = nouveau_defi(depart="fixe")
        installer(monde)
        monde.joueur.update(salle="chambre_cloche", position=[0, 11])
        for id in ("torche", "lanterne"):
            monde.objets[id].update(allume=False, combustible=0)
        from donjon.spatial import memoriser
        memoriser(monde)
        monde.sauver(chemin)
        app = SeuilApp(["--defi", "--offline", "--save", str(chemin)])
        async with app.run_test(size=(120, 40)) as pilot:
            await self.pret(app)
            await self.commande(app, pilot, "pas ouest", 0)
            self.assertEqual(app.derniere_vue["salle"], "Palier des vannes")
            self.assertRegex(app.derniere_vue["carte"], r"@.\^")
            self.assertIn("@", app.query_one("#plan").render().plain)
            await self.fermer(app)
        charge = Monde.charger(chemin)
        self.assertEqual((charge.joueur["salle"], charge.joueur["position"]),
                         ("beffroi", [8, 3]))

    async def test_palper_coffre_vide_depuis_tui_et_sauvegarder_le_constat(self):
        with tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parents[1], suffix=".json", delete=False) as fichier:
            chemin = Path(fichier.name)
        self.addCleanup(chemin.unlink, missing_ok=True)
        monde = nouveau_defi(depart="fixe")
        installer(monde)
        monde.joueur.update(salle="chambre_cloche", position=[4, 3])
        monde.sauver(chemin)
        p = improviser("Palper à la main les objets à l'intérieur du coffre",
                       issue("Tu sens des formes et des matières dans le coffre."),
                       cibles=["coffre"], approche="observation")
        reponses = [
            {"mode": "action", "texte": "", "faits": ["objet:coffre"], "proposition": p},
            {"mode": "action", "texte": "", "faits": ["objet:coffre"],
             "proposition": proposition("toucher", "coffre")},
        ]
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
             patch.object(MJOpenAI, "_appeler", side_effect=reponses) as api:
            app = SeuilApp(["--recit-moteur", "--defi", "--connexion", "api", "--model", "gpt-6-luna", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "je tate les objets dans le coffre avec mes mains", 0)
                self.assertIn("est vide", " ".join(app.sorties))
                await self.fermer(app)
            self.assertEqual(api.call_count, 2)
            self.assertTrue(api.call_args_list[1].args[1]["faits"]["objet:coffre"]["contenu_vide"])
            charge = Monde.charger(chemin)
            self.assertEqual(charge.data["journal"][-1]["action"]["action"], "toucher")
            self.assertFalse(charge.data.get("gestes_improvises"))

    async def test_ramassage_pied_de_biche_depuis_tui_malgre_ancien_refus(self):
        with tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parents[1], suffix=".json", delete=False) as fichier:
            chemin = Path(fichier.name)
        self.addCleanup(chemin.unlink, missing_ok=True)
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
             patch.object(MJOpenAI, "_appeler", side_effect=AssertionError("Appel LLM inattendu")) as api:
            monde = nouveau_defi(depart="fixe")
            installer(monde)
            monde.joueur.update(salle="echoppe", position=[6, 5])
            monde.memoriser("je ramasse le pied de biche",
                            "Le pied-de-biche est dans l'échoppe ; retourne-y pour le prendre.")
            monde.sauver(chemin)
            app = SeuilApp(["--defi", "--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                self.assertIn("le pied-de-biche", app.derniere_vue["carte"])
                await self.commande(app, pilot, "je ramasse le pied de biche", 1)
                self.assertNotIn("le pied-de-biche", app.derniere_vue["carte"])
                self.assertIn("pied-de-biche", app.derniere_vue["fiche"])
                self.assertIn("pied-de-biche", " ".join(app.sorties))
                await self.fermer(app)
            api.assert_not_called()
            self.assertEqual(Monde.charger(chemin).objets["pied_de_biche"]["lieu"], "joueur")

    async def test_ramassage_force_par_mj_depuis_tui(self):
        with tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parents[1], suffix=".json", delete=False) as fichier:
            chemin = Path(fichier.name)
        self.addCleanup(chemin.unlink, missing_ok=True)
        monde = nouveau_defi(depart="fixe")
        installer(monde)
        monde.joueur.update(salle="echoppe", position=[6, 5])
        monde.memoriser("je ramasse le pied de biche",
                        "Le pied-de-biche est dans l'échoppe ; retourne-y pour le prendre.")
        monde.sauver(chemin)
        reponses = [{"mode": "action", "texte": "", "faits": ["objet:pied_de_biche"],
                     "proposition": sequence(etape("deplacer", "pied_de_biche", "joueur"))}]
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
             patch.object(MJOpenAI, "_appeler", side_effect=reponses) as api:
            app = SeuilApp(["--recit-moteur", "--defi", "--connexion", "api", "--model", "gpt-6-luna", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj je ramasse le pied de biche", 1)
                self.assertNotIn("le pied-de-biche", app.derniere_vue["carte"])
                self.assertIn("pied-de-biche", app.derniere_vue["fiche"])
                self.assertIn("Tu prends le pied-de-biche", " ".join(app.sorties))
                await self.fermer(app)
            self.assertEqual(api.call_count, 1)
            entree = api.call_args_list[0].args[1]
            self.assertEqual(entree["conversation"], [])
            self.assertTrue(entree["faits"]["objet:pied_de_biche"]["a_portee_de_main"])
            self.assertNotIn("lieu", entree["faits"]["objet:pied_de_biche"])
            self.assertEqual(Monde.charger(chemin).objets["pied_de_biche"]["lieu"], "joueur")

    async def test_atelier_luna_seul_confirmation_et_debug(self):
        from donjon.artisanat import fabrication
        p = fabrication(["perche_1", "perche_2"], "perche_3", "ficelle", "hache")
        reponses = [{"mode": "action", "texte": "", "faits": ["atelier"], "proposition": p}]
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "_appeler", side_effect=reponses) as api, patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(Monde, "d20", return_value=20):
            path = Path(tmp) / "atelier.json"
            app = SeuilApp(["--recit-moteur", "--atelier", "--debug", "--connexion", "api", "--model", "gpt-6-luna", "--save", str(path)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "je fabrique une échelle", 0)
                self.assertTrue(app.query_one("#proposition-cadre").display)
                self.assertNotIn("échelle en bois et fibres", app.derniere_vue["scene"])
                await self.commande(app, pilot, "tenter", 26)
                self.assertIn("échelle en bois et fibres", app.derniere_vue["scene"])
                self.assertEqual(api.call_count, 1)
                self.assertTrue(all(f.get("mono_modele") for f in app.comparaisons.values()))
                await pilot.press("f5")
                self.assertFalse(app.query_one("#debug-secondaire-cadre").display)
                self.assertIn("fabriquer", str(app.query_one("#debug-principal").render()).lower())
                await pilot.press("f5")
                await self.fermer(app)

    async def attendre(self, condition, message, delai=DELAI):
        """Attend un état, borné par un délai qui tient sous charge ; le message dit l'état observé."""
        fin = time.monotonic() + delai
        while not condition():
            if time.monotonic() > fin:
                self.fail(message() if callable(message) else message)
            await asyncio.sleep(0.02)

    async def pret(self, app, minutes=None):
        def disponible():
            if getattr(app, "jeu_termine", False):  # Un arrêt du jeu est un vrai blocage : échec immédiat.
                self.fail("Le jeu s'est arrêté : " + " | ".join(app.sorties[-3:]))
            return app.derniere_vue and not app.occupe and (
                minutes is None or app.derniere_vue["minutes"] == minutes)
        await self.attendre(disponible, lambda: (
            "La TUI n'est pas redevenue disponible en %d s (occupée : %s, minutes : %s, attendues : %s)"
            % (DELAI, app.occupe, (app.derniere_vue or {}).get("minutes"), minutes)))

    async def commande(self, app, pilot, texte, minutes=None):
        app.query_one("#commande", Input).value = texte
        await pilot.press("enter")
        await self.pret(app, minutes)

    async def fermer(self, app):
        app.action_quitter()
        await self.attendre(lambda: not app.is_running, "La TUI ne se ferme pas")

    async def test_cle_disparait_et_inventaire_actualise_sans_changer_onglet(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--offline", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                self.assertIn("k la clé", app.derniere_vue["carte"])
                self.assertNotIn("clé du veilleur", app.derniere_vue["fiche"])
                await self.commande(app, pilot, "prendre clé", 1)
                self.assertNotIn("k la clé", app.derniere_vue["carte"])
                self.assertNotIn("clé du veilleur", app.derniere_vue["scene"])
                self.assertIn("clé du veilleur", app.derniere_vue["fiche"])
                self.assertEqual(app.query_one(TabbedContent).active, "onglet-carte")
                self.assertIn("Tu prends la clé du veilleur.", app.sorties)
                await self.commande(app, pilot, "poser clé", 2)
                self.assertIn("À tes pieds (@) : la clé", app.derniere_vue["carte"])
                self.assertNotIn("clé du veilleur", app.derniere_vue["fiche"])
                await self.fermer(app)
            self.assertEqual(Monde.charger(chemin).objets["cle"]["lieu"], "antichambre")

    async def test_conversation_accord_et_paiement_actualisent_la_fiche(self):
        reponses = [
            {"mode": "conversation_pnj", "texte": "", "faits": ["interlocuteurs"],
             "proposition": {"personnage": "marchand", "sujet": "Quelle récompense ?",
                             "operation": "proposer", "mission": "anneau_veilleur", "montant_demande": 0}},
            {"mode": "dialogue", "texte": "Gorm : « Je te propose 20 pièces pour cet anneau. »",
             "faits": ["conversation_validee"], "proposition": None, "_texte_moteur": True},
        ]
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "_appeler", side_effect=reponses), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            monde = nouveau_monde()
            monde.joueur["salle"] = "echoppe"
            monde.objets["anneau"]["lieu"] = "joueur"
            monde.sauver(chemin)
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "je demande a gorn ce que j'y gagne a retrouver cet anneau", 0)
                self.assertIn("offre à accepter", app.derniere_vue["fiche"])
                self.assertIn("20 pièces", app.derniere_vue["fiche"])
                await self.commande(app, pilot, "accepter offre", 0)
                self.assertIn("accord accepté", app.derniere_vue["fiche"])
                await self.commande(app, pilot, "remettre anneau", 1)
                self.assertIn("récompense payée", app.derniere_vue["fiche"])
                self.assertIn("44 pièces", app.derniere_vue["fiche"])
                sauvegarde = Monde.charger(chemin)
                self.assertEqual(sauvegarde.objets["anneau"]["lieu"], "marchand")
                self.assertEqual(sauvegarde.joueur["or"], 44)
                await self.fermer(app)

    async def test_mj_en_attente_ui_reactive_et_pas_de_double_action(self):
        arrive = threading.Event()
        continuer = threading.Event()
        def reponse(*args):
            arrive.set()
            continuer.wait(DELAI)
            return {"mode": "action", "texte": "", "faits": [], "proposition": proposition("prendre", "cle")}
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "echanger", side_effect=reponse) as mj, patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            app = SeuilApp(["--connexion", "api", "--save", str(Path(tmp) / "partie.json")])
            async with app.run_test(size=(100, 32)) as pilot:
                await self.pret(app)
                app.query_one("#commande", Input).value = "mj je prend la clé"
                await pilot.press("enter")
                await self.attendre(arrive.is_set, "Le MJ simulé n'a pas été appelé")
                self.assertTrue(app.occupe)
                self.assertTrue(app.query_one("#commande", Input).disabled)
                await pilot.press("f3")
                self.assertEqual(app.query_one(TabbedContent).active, "onglet-fiche")
                await pilot.resize_terminal(70, 30)
                self.assertTrue(app.screen.has_class("etroit"))
                app.soumettre("prendre clé")
                continuer.set()
                await self.pret(app, 1)
                self.assertEqual(mj.call_count, 1)
                self.assertNotIn("k la clé", app.derniere_vue["carte"])
                self.assertIn("clé du veilleur", app.derniere_vue["fiche"])
                self.assertFalse(app.query_one("#proposition-cadre").display)
                await self.fermer(app)

    async def test_savoir_pnj_persiste_depuis_interface(self):
        p = {"personnage": "marchand", "savoirs": [{"sujet": "lien_anneau",
             "texte": "Gorm associe l'anneau au souvenir de son ancien métier de veilleur."}]}
        reponses = [
            {"mode": "enrichir_savoirs", "texte": "", "faits": ["connaissances_a_completer"], "proposition": p},
            {"mode": "dialogue", "texte": "Gorm : « Il me rappelle mon ancien métier de veilleur. »",
             "faits": ["connaissances_pnj"], "proposition": None, "_texte_moteur": True},
        ]
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "_appeler", side_effect=reponses), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            m = nouveau_monde()
            m.joueur["salle"] = "echoppe"
            m.sauver(chemin)
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "Gorm, pourquoi cet anneau ?", 0)
                self.assertIn(reponses[1]["texte"], app.sorties)
                self.assertEqual(Monde.charger(chemin).data["savoirs_pnj"]["marchand"]["lien_anneau"]["texte"], p["savoirs"][0]["texte"])
                await self.fermer(app)

    async def test_boutons_proposition_et_annulation(self):
        p = {"mode": "action", "texte": "", "faits": [], "proposition": proposition("detacher", "axe_haut", "couteau", "levier", 18)}
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "echanger", return_value=p), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "mj je retire l'axe")
                self.assertTrue(app.query_one("#proposition-cadre").display)
                self.assertTrue(Monde.charger(chemin).objets["axe_haut"]["attache"])
                await pilot.click("#annuler")
                await self.pret(app)
                self.assertFalse(app.query_one("#proposition-cadre").display)
                await self.commande(app, pilot, "mj je retire l'axe")
                with patch.object(Monde, "d20", return_value=20):
                    await pilot.click("#tenter")
                    await self.pret(app, 3)
                self.assertFalse(app.query_one("#proposition-cadre").display)
                self.assertFalse(Monde.charger(chemin).objets["axe_haut"]["attache"])
                await self.fermer(app)

    async def test_vol_attend_tenter_puis_actualise_objet_ou_mefiance(self):
        reponse = {"mode": "action", "texte": "", "faits": [],
                   "proposition": proposition("voler", "crochets", methode="finesse")}
        for jet in (20, 1):
            with self.subTest(jet=jet), tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "echanger", return_value=reponse), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
                chemin = Path(tmp) / "partie.json"
                m = nouveau_monde()
                m.joueur["salle"] = "echoppe"
                m.sauver(chemin)
                app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
                async with app.run_test(size=(120, 40)) as pilot:
                    await self.pret(app)
                    await self.commande(app, pilot, "j'attens que Gorm ait le dos tourné pour discretement prendre la trousse de crochets", 0)
                    self.assertTrue(app.query_one("#proposition-cadre").display)
                    self.assertEqual(Monde.charger(chemin).objets["crochets"]["lieu"], "echoppe")
                    with patch.object(Monde, "d20", return_value=jet):
                        await pilot.click("#tenter")
                        await self.pret(app, 3)
                    self.assertFalse(app.query_one("#proposition-cadre").display)
                    if jet == 20:
                        self.assertNotIn("la trousse", app.derniere_vue["carte"])
                        self.assertIn("trousse", app.derniere_vue["fiche"])
                    else:
                        self.assertIn("la trousse", app.derniere_vue["carte"])
                        self.assertIn("fait des gestes brusques", app.derniere_vue["scene"])
                    self.assertEqual(Monde.charger(chemin).objets["crochets"]["lieu"], "joueur" if jet == 20 else "echoppe")
                    await self.fermer(app)

    async def test_manoeuvre_composee_et_recit_echec_partiel(self):
        p = sequence(*[etape("detacher", cible, outil="couteau", methode="levier", difficulte=18)
                       for cible in ("axe_haut", "axe_bas")])
        reponses = [{"mode": "action", "texte": "", "faits": [], "proposition": p}]
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "_appeler", side_effect=reponses) as appels, patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--recit-moteur", "--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(100, 36)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "Je retire les deux axes avec mon couteau", 0)
                self.assertTrue(app.query_one("#proposition-cadre").display)
                self.assertIn("Étape 2 — Libérer", app.derniere_vue["proposition"])
                with patch.object(Monde, "d20", side_effect=[20, 1]):
                    await pilot.click("#tenter")
                    await self.pret(app, 6)
                self.assertIn("L'axe du gond supérieur est libéré", " ".join(app.sorties))
                self.assertIn("La suite de la manœuvre est abandonnée", " ".join(app.sorties))
                self.assertNotIn("1d20(", " ".join(app.sorties))
                self.assertEqual(appels.call_count, 1)
                m = Monde.charger(chemin)
                self.assertTrue(any(ligne.startswith("1d20(") for ligne in m.data["journal"][-1]["faits"]))
                self.assertFalse(m.objets["axe_haut"]["attache"])
                self.assertTrue(m.objets["axe_bas"]["attache"])
                self.assertFalse(m.objets["porte"]["ouverte"])
                self.assertFalse(app.query_one("#proposition-cadre").display)
                await self.fermer(app)

    async def test_comparaison_lente_copie_et_seul_principal_enregistre(self):
        commence, liberer = threading.Event(), threading.Event()
        def appel(mj, instructions, entree, intention, fonction, schema):
            couleur = "gris" if mj.modele == "principal" else "bruns"
            if entree["faits"]["descriptions_a_completer"]:
                if mj.modele == "secondaire":
                    commence.set()
                    liberer.wait(DELAI)
                return {"mode": "enrichir", "texte": "", "faits": ["descriptions_a_completer"],
                        "proposition": {"ajouts": [{"personnage": "marchand", "facette": "yeux",
                                                    "description": "Ses yeux sont " + couleur + "."}]}}
            return {"mode": "dialogue", "texte": "Ses yeux sont " + couleur + ".", "faits": ["souvenirs_personnages"], "proposition": None, "_texte_moteur": True}
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "_appeler", autospec=True, side_effect=appel), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch("donjon.tui.pyperclip.copy") as copier:
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--model", "principal", "--compare-model", "secondaire", "--save", str(chemin)])
            try:
                async with app.run_test(size=(120, 40)) as pilot:
                    await self.pret(app)
                    await self.commande(app, pilot, "De quelle couleur sont ses yeux ?", 0)
                    self.assertTrue(commence.is_set())
                    self.assertFalse(app.occupe)
                    await pilot.press("f5")
                    self.assertTrue(app.debug_visible)
                    self.assertFalse(app.query_one("#corps").display)
                    self.assertEqual(app.comparaisons[1]["principal"]["statut"], "Terminé")
                    self.assertEqual(app.comparaisons[1]["secondaire"]["statut"], "En cours")
                    liberer.set()
                    await self.attendre(lambda: app.comparaisons[1]["secondaire"]["statut"] == "Terminé",
                                        "La comparaison secondaire ne se termine pas")
                    self.assertEqual(app.comparaisons[1]["secondaire"]["statut"], "Terminé")
                    await pilot.press("f4")
                    texte = copier.call_args.args[0]
                    self.assertIn("FAITS PROPOSÉS", texte)
                    self.assertIn("gris", texte)
                    self.assertIn("bruns", texte)
                    self.assertIn("jamais appliqué", texte)
                    await pilot.resize_terminal(60, 28)
                    self.assertGreater(app.query_one("#debug-secondaire-cadre").region.y, app.query_one("#debug-principal-cadre").region.y)
                    await pilot.press("f2")
                    self.assertFalse(app.debug_visible)
                    self.assertTrue(app.query_one("#corps").display)
                    self.assertEqual(Monde.charger(chemin).objets["detail_marchand_yeux"]["description_visuelle"], "Ses yeux sont gris.")
                    await self.fermer(app)
            finally:
                liberer.set()

    async def test_enrichissement_mj_sauvegarde_et_actualise_la_scene(self):
        reponses = [
            {"mode": "enrichir", "texte": "", "faits": ["descriptions_a_completer"],
             "proposition": {"ajouts": [{"personnage": "marchand", "facette": "yeux",
                                         "description": "Ses yeux sont gris clair."}]}},
            {"mode": "dialogue", "texte": "Gorm a les yeux gris clair.",
             "faits": ["objet:detail_marchand_yeux"], "proposition": None, "_texte_moteur": True},
        ]
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "_appeler", side_effect=reponses) as appels, patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "ouest", 1)
                await self.commande(app, pilot, "De quelle couleur sont ses yeux ?", 1)
                self.assertIn("Ses yeux sont gris clair.", app.derniere_vue["scene"])
                self.assertIn("detail_marchand_yeux", Monde.charger(chemin).objets)
                await self.commande(app, pilot, "examiner yeux", 1)
                self.assertIn("Ses yeux sont gris clair.", app.sorties)
                self.assertEqual(appels.call_count, 2)
                self.assertFalse(app.query_one("#proposition-cadre").display)
                await self.fermer(app)

    async def test_redimensionnement_et_historique_de_saisie(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = SeuilApp(["--offline", "--save", str(Path(tmp) / "partie.json")])
            async with app.run_test(size=(80, 25)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "prendre clé", 1)
                await pilot.press("up")
                self.assertEqual(app.query_one("#commande", Input).value, "prendre clé")
                await pilot.press("down")
                self.assertEqual(app.query_one("#commande", Input).value, "")
                await pilot.resize_terminal(60, 28)
                self.assertGreater(app.query_one("#recit").region.y, app.query_one("#etat").region.y)
                saisie = app.query_one("#commande", Input).region
                self.assertGreater(saisie.width, 0)
                self.assertLessEqual(saisie.bottom, 28)
                await self.fermer(app)

    async def test_espace_attend_un_instant_si_la_saisie_est_vide(self):
        from donjon.temps import instant
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--offline", "--save", str(chemin)])
            async with app.run_test(size=(80, 25)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "attendre 30 s")
                debut = instant(Monde.charger(chemin))
                # Saisie vide : Espace fait attendre le temps d'un pas, sans rien écrire.
                await pilot.press("space")
                await self.attendre(lambda: not app.occupe and instant(Monde.charger(chemin)) == debut + 15,
                                    lambda: "Espace n'a pas fait attendre 1,5 s : %s" % (instant(Monde.charger(chemin)) - debut))
                self.assertEqual(app.query_one("#commande", Input).value, "")
                # Une saisie commencée garde son espace, et le temps ne passe pas.
                await pilot.press("j", "e", "space")
                self.assertEqual(app.query_one("#commande", Input).value, "je ")
                self.assertEqual(instant(Monde.charger(chemin)), debut + 15)
                await self.fermer(app)

    async def test_quitter_pendant_mj_attend_et_sauvegarde_action(self):
        arrive = threading.Event()
        continuer = threading.Event()
        def reponse(*args):
            arrive.set()
            continuer.wait(DELAI)
            return {"mode": "action", "texte": "", "faits": [], "proposition": proposition("prendre", "cle")}
        with tempfile.TemporaryDirectory() as tmp, patch.object(MJOpenAI, "echanger", side_effect=reponse), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            chemin = Path(tmp) / "partie.json"
            app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
            async with app.run_test(size=(100, 32)) as pilot:
                await self.pret(app)
                app.query_one("#commande", Input).value = "mj je prends la clé"
                await pilot.press("enter")
                await self.attendre(arrive.is_set, "Le MJ simulé n'a pas été appelé")
                await pilot.press("ctrl+q")
                self.assertTrue(app.fermeture_demandee)
                self.assertTrue(app.is_running)
                continuer.set()
                await self.attendre(lambda: not app.is_running, "La TUI ne se ferme pas")
                self.assertFalse(app.is_running)
            self.assertEqual(Monde.charger(chemin).objets["cle"]["lieu"], "joueur")

    async def test_selection_souris_et_ctrl_c_copient_sans_quitter(self):
        with tempfile.TemporaryDirectory() as tmp, patch("donjon.tui.pyperclip.copy") as copier:
            app = SeuilApp(["--offline", "--save", str(Path(tmp) / "partie.json")])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                app.journal_entrees.clear()
                app.ajouter_journal("Corvus > pourquoi ?")
                app.ecrire("Une réponse étrange.\nAvec des accents : clé, émeraude.")
                await pilot.pause()
                await pilot.mouse_down("#journal-texte", offset=(0, 2))
                await pilot.hover("#journal-texte", offset=(20, 2))
                await pilot.mouse_up("#journal-texte", offset=(20, 2))
                selection = app.screen.get_selected_text()
                self.assertEqual(selection, "Une réponse étrange.")
                await pilot.press("ctrl+c")
                copier.assert_called_once_with(selection)
                self.assertTrue(app.is_running)
                self.assertFalse(app.fermeture_demandee)
                self.assertEqual(app.clipboard, selection)
                await self.fermer(app)

    async def test_f4_copie_la_commande_et_la_reponse_et_ctrl_c_vide_ne_quitte_pas(self):
        with tempfile.TemporaryDirectory() as tmp, patch("donjon.tui.pyperclip.copy") as copier:
            app = SeuilApp(["--offline", "--save", str(Path(tmp) / "partie.json")])
            async with app.run_test(size=(120, 40)) as pilot:
                await self.pret(app)
                await pilot.press("ctrl+c")
                copier.assert_not_called()
                self.assertTrue(app.is_running)
                await self.commande(app, pilot, "prendre clé", 1)
                await pilot.press("f4")
                copier.assert_called_once_with("Corvus > prendre clé\n\nTu prends la clé du veilleur.")
                self.assertEqual(app.derniere_vue["minutes"], 1)
                await self.fermer(app)

    async def test_presse_papiers_indisponible_ne_ferme_pas_le_jeu(self):
        from pyperclip import PyperclipException
        with tempfile.TemporaryDirectory() as tmp, patch("donjon.tui.pyperclip.copy", side_effect=PyperclipException("occupé")):
            app = SeuilApp(["--offline", "--save", str(Path(tmp) / "partie.json")])
            async with app.run_test(size=(100, 32)) as pilot:
                await self.pret(app)
                await self.commande(app, pilot, "prendre clé", 1)
                with patch.object(app, "notify") as notifier:
                    await pilot.press("f4")
                self.assertEqual(notifier.call_args.kwargs["severity"], "error")
                self.assertTrue(app.is_running)
                await self.fermer(app)


if __name__ == "__main__":
    unittest.main()
