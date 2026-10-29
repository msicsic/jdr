"""U-T : choix réellement saisis, même moteur que le clic, sauvegarde et reprise."""
import copy
import http.client
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch

import jeu
from donjon.commandes import DescripteurPublic
from donjon.gestes_publics import catalogue_public, choisir_numero, gestes_du_monde, liste_gestes, offres, rendre_liste
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.noms import reference
from donjon.scene import scene_percue
from donjon.web.pont import PontWeb
from donjon.web.serveur import PAGE, Serveur
from tests import test_descripteur_public as ud
from tests import test_tui as tui


CAS = [(False, g) for g in ud.GESTES[:9]] + [
    (True, g) for g in ("examiner", "ouvrir", "fermer", "deverrouiller", "crocheter")]


def menu(m, cible, geste):
    liste = gestes_du_monde(m)
    d = {"geste": geste, "cible": reference(m, cible)}
    numero = next(i for i, c in enumerate(liste, 1) if c.descripteur.contenu == d)
    return liste, str(numero), DescripteurPublic(d)


def sans_saisie(data):
    data = copy.deepcopy(data)
    for tour in data.get("conversation", []):
        tour.pop("joueur", None)
    return data


class CatalogueTests(unittest.TestCase):
    def test_projection_publique_seule_et_numeros_exacts(self):
        m, premiere, seconde = ud.scene("prendre")
        liste, numero, descripteur = menu(m, seconde, "prendre")
        self.assertEqual(choisir_numero(numero, liste), descripteur)
        self.assertEqual(choisir_numero("0" + numero, liste), descripteur)
        self.assertEqual(len({c.libelle for c in liste}), len(liste))
        self.assertNotEqual(menu(m, premiere, "prendre")[1], numero)
        self.assertIn(reference(m, seconde), rendre_liste(liste))
        self.assertNotIn("parler", {c.descripteur.contenu["geste"] for c in liste})
        for texte in ("0", "99999", "1 2", "1,2", "1/2", "1-2"):
            with self.subTest(texte=texte), self.assertRaises(ValueError):
                choisir_numero(texte, liste)
        self.assertIsNone(choisir_numero("je prends un objet", liste))
        # Une mémoire peut nommer une cible sans l'offrir à la manipulation.
        s = {"niveaux": [{"objets": [], "sorties": [], "souvenirs": [{"id": "secret"}]}]}
        self.assertEqual(liste_gestes(s), ())
        self.assertEqual(offres({"etat": "fermee", "souvenir": True}, porte=True), [])
        m.joueur.update(salle="beffroi", position=[3, 3])
        self.assertNotIn(reference(m, seconde), {c.descripteur.contenu["cible"]
                                               for c in liste_gestes(scene_percue(m))})

    def test_personnage_inconnu_garde_sa_reference_publique(self):
        m, cible, _ = ud.scene("observer")
        ref = reference(m, cible)
        self.assertNotEqual(ref, cible)
        liste = liste_gestes(scene_percue(m))
        self.assertIn(ref, {c.descripteur.contenu["cible"] for c in liste})
        self.assertNotIn(cible, rendre_liste(liste))

    @unittest.skipUnless(shutil.which("node"), "Node requis pour le menu web réel")
    def test_page_servie_catalogue_commun_et_callbacks_web(self):
        from tests.test_web import Flux
        pont, serveur = PontWeb(), None
        pont.rafraichir(ud.scene("prendre")[0], None, None)
        pont.occupe = False
        serveur = Serveur(pont, 0)
        threading.Thread(target=serveur.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", serveur.server_address[1], timeout=20)
            for url in ("/", "/index.html"):
                c.request("GET", url)
                r = c.getresponse()
                self.assertEqual(r.status, 200)
                self.assertEqual(r.read(), PAGE.read_bytes())
            c.close()
            flux = Flux(serveur.server_address[1])
            try:
                evenement = next(e for e in flux.jusqu_a_pret() if e["type"] == "etat")
                self.assertEqual(evenement["catalogue_gestes"], catalogue_public())
            finally:
                flux.reponse.close()
                flux.connexion.close()
        finally:
            serveur.arreter()
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "page.html"
            chemin.write_bytes(PAGE.read_bytes())
            for porte, geste in CAS:
                with self.subTest(porte=porte, geste=geste):
                    m, _, cible = ud.scene(geste, porte)
                    pont.rafraichir(m, None, None)
                    etat = pont.dernier_etat
                    s = etat["scene"]
                    self.assertEqual(etat["catalogue_gestes"], catalogue_public())
                    sortie = subprocess.run(["node", str(Path(__file__).with_name("clic_page.js")), str(chemin)],
                                            input=json.dumps(etat), capture_output=True, text=True,
                                            encoding="utf-8", check=True)
                    web = json.loads(sortie.stdout)
                    gestes_web = [d for choix in web["choix"].values() for d in choix
                                  if isinstance(d, dict) and d["geste"] != "tourner"]
                    terminal = [c.descripteur.contenu for c in liste_gestes(s)]
                    # U-M outils complète les offres paramétrées par un second
                    # choix. Le terminal premier geste conserve ses offres
                    # simples ; sa sélection des ressources attend U-T outils.
                    parametrees = {(o["id"], g) for n in s["niveaux"]
                                   for o, porte in ([(o, False) for o in n["objets"]] +
                                                    [(x["porte"], True) for x in n["sorties"] if x.get("porte")])
                                   for g, _, _ in offres(o, porte, parametrees=True)}
                    terminal = [d for d in terminal if (d["cible"], d["geste"]) not in parametrees]
                    # Le web montre un niveau à la fois ; les scènes du test en ont un.
                    self.assertEqual({json.dumps(d, sort_keys=True) for d in gestes_web},
                                     {json.dumps(d, sort_keys=True) for d in terminal})
                    for clic in web["envoisClic"]:
                        self.assertEqual(clic["envoye"], clic["choix"])


class ConsoleTests(unittest.TestCase):
    def jouer_console(self, m, entrees, avant_preparer=None):
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "copie.json"
            m.sauver(fichier)
            sorties, menus = [], []
            faux_mj = MagicMock(connexion="api", erreur_auth=None)
            faux_mj.echanger.side_effect = AssertionError("Appel au modèle")
            preparer = Moteur.preparer
            def preparation(moteur, p, *args, **kwargs):
                if avant_preparer and isinstance(p, DescripteurPublic):
                    avant_preparer(moteur.monde)
                return preparer(moteur, p, *args, **kwargs)
            def ecrire(*args, **_):
                texte = " ".join(map(str, args))
                sorties.append(texte)
                if texte.startswith("Gestes de la scène"):
                    menus.append(texte)
            with (patch("builtins.input", side_effect=[*entrees, "quitter"]),
                  patch("builtins.print", side_effect=ecrire),
                  patch("jeu.MJ", return_value=faux_mj),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", side_effect=AssertionError("Analyse de texte")),
                  patch.object(Moteur, "preparer", preparation),
                  patch.object(Monde, "d20", return_value=20)):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(fichier)]), 0)
            faux_mj.echanger.assert_not_called()
            faux_mj.raconter_resultat.assert_not_called()
            return Monde.charger(fichier), sorties, menus

    def test_chaque_geste_choisit_le_second_homonyme_meme_plan_texte_et_reprise(self):
        mesures = []
        for porte, geste in CAS:
            with self.subTest(porte=porte, geste=geste):
                m, _, cible = ud.scene(geste, porte)
                liste, numero, d = menu(m, cible, geste)
                temoin, sorties_web = ud.DescripteurPublicTests().boucle(m.copier(), d)
                obtenu, sorties, menus = self.jouer_console(m, [numero])
                self.assertEqual(menus[0], rendre_liste(liste))
                self.assertEqual(sans_saisie(obtenu.data), sans_saisie(temoin.data))
                self.assertEqual(ud.vues(obtenu), ud.vues(temoin))
                for tour in temoin.data.get("conversation", []):
                    self.assertIn(tour["reponse"], sorties)
                self.assertEqual(obtenu.data.get("journal"), temoin.data.get("journal"))
                mesures.append({"porte": porte, "geste": geste, "numero": numero,
                                "touches_console": len(numero) + 1,
                                "touches_tui_depuis_liste": len(numero) + 1,
                                "touches_tui_avec_f7": len(numero) + 2,
                                "touches_commande": len(geste + " " + d.contenu["cible"]) + 1,
                                "appels_modele": 0,
                                "effet_ou_refus": obtenu.data.get("conversation", [])[-1:]
                                or [s for s in sorties if s.startswith("Approche-toi")]})
        print("MESURES_UT_299=" + json.dumps(mesures, ensure_ascii=False))

    def test_portes_a_portee_ouvrent_et_ferment_la_cible_choisie(self):
        for geste in ("ouvrir", "fermer"):
            with self.subTest(geste=geste):
                m, autre, cible = ud.scene(geste, porte=True)
                m.joueur.update(position=[3, 4], orientation="sud")
                _, numero, d = menu(m, cible, geste)
                temoin, _ = ud.DescripteurPublicTests().boucle(m.copier(), d)
                obtenu, _, _ = self.jouer_console(m, [numero])
                self.assertEqual(sans_saisie(obtenu.data), sans_saisie(temoin.data))
                self.assertEqual(ud.vues(obtenu), ud.vues(temoin))
                self.assertEqual(obtenu.objets[cible]["ouverte"], geste == "ouvrir")
                self.assertEqual(obtenu.objets[autre]["ouverte"], geste == "fermer")

    def test_inconnu_et_ambigu_restent_locaux_sans_effet(self):
        m, _, _ = ud.scene("prendre")
        obtenu, sorties, _ = self.jouer_console(m, ["99999", "1 2", "1,2"])
        self.assertEqual(obtenu.data, m.data)
        self.assertIn("Numéro inconnu dans la liste affichée.", sorties)
        self.assertIn("Choix ambigu : saisis un seul numéro de la liste affichée.", sorties)

    def test_choix_perime_ne_vise_jamais_un_autre_homonyme(self):
        for geste in ("prendre", "lire"):
            with self.subTest(geste=geste):
                m, autre, cible = ud.scene(geste)
                _, numero, _ = menu(m, cible, geste)
                def supprimer(monde):
                    del monde.objets[cible]
                obtenu, sorties, _ = self.jouer_console(m, [numero], supprimer)
                self.assertIn("Tu ne vois plus cette cible ici.", sorties)
                self.assertEqual(obtenu.objets[autre]["lieu"], "antichambre")
                self.assertEqual(obtenu.data["journal"], m.data["journal"])
                self.assertEqual(ud.vues(obtenu), ud.vues(Monde(copy.deepcopy(obtenu.data))))


@unittest.skipUnless(tui.TEXTUAL, "Installer les dépendances TUI")
class TerminalTests(unittest.IsolatedAsyncioTestCase):
    attendre = tui.TUITests.attendre
    pret = tui.TUITests.pret
    fermer = tui.TUITests.fermer

    async def jouer_tui(self, m, geste, cible, perime=False, invalides=False):
        from textual.widgets import Input, TabbedContent
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "copie.json"
            m.sauver(fichier)
            faux_mj = MagicMock(connexion="api", erreur_auth=None)
            faux_mj.echanger.side_effect = AssertionError("Appel au modèle")
            with (patch("jeu.MJ", return_value=faux_mj),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", side_effect=AssertionError("Analyse de texte")),
                  patch.object(Monde, "d20", return_value=20)):
                app = tui.SeuilApp(["--connexion", "api", "--save", str(fichier)])
                async with app.run_test(size=(120, 40)) as pilot:
                    await self.pret(app)
                    liste, numero, d = menu(m, cible, geste)
                    self.assertEqual(app.derniere_vue["gestes"], liste)
                    if invalides:
                        app.action_debug()
                        app.focus_carte = True
                    await pilot.press("f7")
                    self.assertFalse(app.focus_carte)
                    self.assertFalse(app.debug_visible)
                    self.assertEqual(app.query_one("#etat", TabbedContent).active, "onglet-gestes")
                    self.assertEqual(str(app.query_one("#gestes").render()), rendre_liste(liste))
                    if invalides:
                        for texte in ("99999", "1 2", "1,2"):
                            app.query_one("#commande", Input).value = texte
                            await pilot.press("enter")
                            self.assertFalse(app.occupe)
                            self.assertTrue(app.pont.commandes.empty())
                        self.assertEqual(Monde.charger(fichier).data, m.data)
                    preparer = Moteur.preparer
                    def preparation(moteur, p, *args, **kwargs):
                        if isinstance(p, DescripteurPublic):
                            self.assertEqual(p, d)
                            if perime:
                                del moteur.monde.objets[cible]
                        return preparer(moteur, p, *args, **kwargs)
                    def termine():
                        self.assertFalse(getattr(app, "jeu_termine", False), app.sorties[-4:])
                        return app.derniere_vue is not ancien and not app.occupe
                    ancien = app.derniere_vue
                    with patch.object(Moteur, "preparer", preparation):
                        app.query_one("#commande", Input).value = ""
                        await pilot.press(*numero, "enter")
                        await self.attendre(termine,
                                            lambda: "Le geste numéroté n'a pas terminé : " + repr({
                                                "numero": numero, "occupe": app.occupe,
                                                "saisie": app.query_one("#commande", Input).value,
                                                "focus": str(app.focused), "sorties": app.sorties[-4:]}))
                    if perime:
                        self.assertIn("Tu ne vois plus cette cible ici.", app.sorties)
                    sorties = list(app.sorties)
                    vue = app.derniere_vue
                    await self.fermer(app)
            faux_mj.echanger.assert_not_called()
            faux_mj.raconter_resultat.assert_not_called()
            obtenu = Monde.charger(fichier)
            self.assertEqual(vue["carte"], ud.carte(obtenu))
            self.assertEqual(vue["scene"], ud.regarder(obtenu))
            self.assertEqual(ud.vues(obtenu), ud.vues(Monde(copy.deepcopy(obtenu.data))))
            return obtenu, sorties

    async def test_chaque_geste_reel_parite_web_homonyme_plan_texte_et_reprise(self):
        for porte, geste in CAS:
            with self.subTest(porte=porte, geste=geste):
                m, _, cible = ud.scene(geste, porte)
                d = menu(m, cible, geste)[2]
                # Exécution U-D dans la boucle publique, avant de lancer l'UI.
                temoin, _ = ud.DescripteurPublicTests().boucle(m.copier(), d)
                obtenu, sorties = await self.jouer_tui(m, geste, cible, invalides=geste == "prendre")
                self.assertEqual(sans_saisie(obtenu.data), sans_saisie(temoin.data))
                self.assertEqual(ud.vues(obtenu), ud.vues(temoin))
                for tour in temoin.data.get("conversation", []):
                    self.assertIn(tour["reponse"], sorties)

    async def test_choix_perime_deux_familles_sans_substitution(self):
        for geste in ("prendre", "lire"):
            with self.subTest(geste=geste):
                m, autre, cible = ud.scene(geste)
                obtenu, _ = await self.jouer_tui(m, geste, cible, perime=True)
                self.assertEqual(obtenu.objets[autre]["lieu"], "antichambre")
                self.assertEqual(obtenu.data["journal"], m.data["journal"])

    async def test_portes_a_portee_effet_et_reprise(self):
        for geste in ("ouvrir", "fermer"):
            with self.subTest(geste=geste):
                m, autre, cible = ud.scene(geste, porte=True)
                m.joueur.update(position=[3, 4], orientation="sud")
                d = menu(m, cible, geste)[2]
                temoin, _ = ud.DescripteurPublicTests().boucle(m.copier(), d)
                obtenu, _ = await self.jouer_tui(m, geste, cible)
                self.assertEqual(sans_saisie(obtenu.data), sans_saisie(temoin.data))
                self.assertEqual(ud.vues(obtenu), ud.vues(temoin))
                self.assertEqual(obtenu.objets[cible]["ouverte"], geste == "ouvrir")
                self.assertEqual(obtenu.objets[autre]["ouverte"], geste == "fermer")
