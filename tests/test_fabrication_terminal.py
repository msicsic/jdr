"""U-T fabrication : saisies réelles, même recette web et vues rechargées."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.fabrication_terminal import RecetteTerminal, fabrication_publique
from donjon.geometrie import placer
from donjon.gestes_publics import catalogue_public
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.noms import reference
from donjon.spatial import memoriser
from tests import test_fabrication_publique as web
from tests import test_gestes_terminal as terminal
from tests import test_tui as tui


def parcours(m, geste, valeurs=None):
    valeurs = valeurs or web.valeurs(m, geste)
    recette = RecetteTerminal(fabrication_publique(m))
    numeros = ["0", next(str(i) for i, (f, _) in enumerate(recette.choix(), 1) if f["geste"] == geste)]
    recette.saisir(numeros[-1])
    while not recette.terminee:
        c = recette.champ
        valeur = valeurs[c["libelle"]]
        numero = (str(valeur) if c["type"] == "nombre" else
                  next(str(i) for i, (v, _) in enumerate(recette.choix(), 1) if v == valeur))
        numeros.append(numero)
        d = recette.saisir(numero)
    return numeros, d


class ProjectionTests(unittest.TestCase):
    def test_catalogue_et_ressources_communs_figes_homonymes_et_physique(self):
        m = web.atelier()
        public = fabrication_publique(m)
        self.assertEqual(public["formulaires"], catalogue_public()["fabrication"])
        self.assertEqual(public["ressources"], web.etat(m)["fabrication"])
        recette = RecetteTerminal(public)
        premier = recette.rendre()
        public["formulaires"].clear()
        public["ressources"].clear()
        self.assertEqual(recette.rendre(), premier)
        recette.saisir("1")
        texte = recette.rendre()
        for id in ("perche_1", "perche_2"):
            self.assertIn("[" + reference(m, id) + "]", texte)
        self.assertIn("3 m de long", texte)

    def test_catalogue_modifie_sans_recette_parallele(self):
        public = fabrication_publique(web.atelier())
        # L'interface suit aussi un rôle, un usage et une borne ajoutés au catalogue.
        public["formulaires"] = [{"geste": "assembler", "cible": "usage catalogue",
                                  "libelle": "Nouvelle recette du catalogue", "champs": [
                                      {"type": "ressource", "chemin": ["pieces", "nouveau_role", 0], "libelle": "Rôle"},
                                      {"type": "nombre", "chemin": ["mesure"], "libelle": "Mesure", "minimum": 2, "maximum": 3}]}]
        recette = RecetteTerminal(public)
        self.assertIn("Nouvelle recette", recette.rendre())
        recette.saisir("1")
        recette.saisir("2")
        with self.assertRaises(ValueError):
            recette.saisir("4")
        d = recette.saisir("3")
        self.assertEqual(d.contenu, {"geste": "assembler", "cible": "usage catalogue", "parametres": {
            "pieces": {"nouveau_role": [public["ressources"][1]["id"]]}, "mesure": 3}})

    def test_incomplet_ambigu_bornes_annulation_aucun_effet(self):
        m = web.atelier()
        avant = copy.deepcopy(m.data)
        recette = RecetteTerminal(fabrication_publique(m))
        for texte in ("", "99999", "1 2", "1,2", "perche"):
            with self.assertRaises(ValueError):
                recette.saisir(texte)
        recette.saisir("2")
        recette.saisir("1")
        recette.saisir("2")
        for texte in ("", "0", "1.5", "-1", "9" * 5000):
            with self.assertRaises(ValueError):
                recette.saisir(texte)
        self.assertIsNone(recette.saisir("annuler"))
        self.assertTrue(recette.terminee)
        self.assertEqual(m.data, avant)

    def test_projection_privee_ou_lointaine_exclue_et_physique_inconnue_dite(self):
        m = web.atelier()
        for cle in ("physique", "ressource", "longueur_cm", "charge_jeu_kg"):
            m.objets["perche_2"].pop(cle, None)
        placer(m.objets["perche_1"], "cour", [5, 3])
        m.objets["perche_3"]["lieu"] = web.proprietaire_test(m)
        recette = RecetteTerminal(fabrication_publique(m))
        recette.saisir("1")
        self.assertIn("Description physique manquante", recette.rendre())
        ids = {r["id"] for r in recette.public["ressources"]}
        self.assertNotIn(reference(m, "perche_1"), ids)
        self.assertNotIn(reference(m, "perche_3"), ids)


class Parcours:
    async def jouer_tui(self, m, entrees, invalides=False):
        from donjon.tui import SeuilApp
        from textual.widgets import Input
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "copie.json"
            m.sauver(fichier)
            faux_mj = MagicMock(connexion="api", erreur_auth=None)
            faux_mj.echanger.side_effect = AssertionError("Appel au modèle")
            with (patch("jeu.MJ", return_value=faux_mj),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", side_effect=AssertionError("Analyse de texte")),
                  patch.object(Monde, "d20", return_value=20)):
                app = SeuilApp(["--connexion", "api", "--save", str(fichier)])
                async with app.run_test(size=(120, 40)) as pilot:
                    support = terminal.TerminalTests()
                    await support.pret(app)
                    await pilot.press("f7")
                    initial = app.derniere_vue
                    for numero in entrees[:-1]:
                        app.query_one("#commande", Input).value = ""
                        await pilot.press(*numero, "enter")
                        self.assertIs(app.derniere_vue, initial)
                        self.assertFalse(app.occupe)
                        self.assertTrue(app.pont.commandes.empty())
                        self.assertEqual(Monde.charger(fichier).data, m.data)
                    if invalides:
                        for texte in ("0", "1.5", "999999999999999999"):
                            app.query_one("#commande", Input).value = texte
                            await pilot.press("enter")
                            self.assertIs(app.derniere_vue, initial)
                            self.assertTrue(app.pont.commandes.empty())
                        await pilot.press("ctrl+right", "shift+left")
                        self.assertTrue(app.pont.commandes.empty())
                    app.query_one("#commande", Input).value = ""
                    await pilot.press(*entrees[-1], "enter")
                    await support.attendre(lambda: app.derniere_vue is not initial and not app.occupe,
                                           lambda: repr(app.sorties[-5:]))
                    lignes = list(app.sorties)
                    vue = app.derniere_vue
                    # La disparition injectée au devis simule une mise à jour du
                    # monde ; fermer passe par la vraie sauvegarde, même au refus.
                    await support.fermer(app)
                    recharge = Monde.charger(fichier)
                    self.assertEqual(vue["carte"], web.support.vues(recharge)[1])
                    self.assertEqual(vue["fiche"], web.support.vues(recharge)[2])
                    self.assertEqual(vue["scene"], web.support.vues(recharge)[3])
            faux_mj.echanger.assert_not_called()
            faux_mj.raconter_resultat.assert_not_called()
            return Monde.charger(fichier), lignes

    async def comparer(self, m, geste, valeurs=None, mutation=None):
        numeros, d = parcours(m, geste, valeurs)
        clic = web.page(m, geste, valeurs)
        self.assertEqual(d.contenu, clic["envoye"])
        temoin = m.copier()
        if mutation:
            mutation(temoin)
        if mutation is None:
            self.assertEqual(proposition_descripteur(temoin, d), analyser(temoin, web.commande(d.contenu)))
        try:
            plan = copy.deepcopy(Moteur(temoin.copier()).preparer(d).__dict__)
        except ErreurMonde as exc:
            refus, plan = str(exc), None
        else:
            refus = None
        attendu, lignes = web.FabricationPubliqueTests().boucle(temoin.copier(), d)
        if mutation is None:
            par_commande, _ = web.FabricationPubliqueTests().boucle(temoin.copier(), web.commande(d.contenu))
            self.assertEqual(terminal.sans_saisie(attendu.data), terminal.sans_saisie(par_commande.data))
        plans = []
        preparer = Moteur.preparer

        def preparation(moteur, p, *args, **kwargs):
            if isinstance(p, DescripteurPublic):
                self.assertEqual(p, d)
                if mutation:
                    mutation(moteur.monde)
            resultat = preparer(moteur, p, *args, **kwargs)
            if isinstance(p, DescripteurPublic):
                plans.append(copy.deepcopy(resultat.__dict__))
            return resultat

        with patch.object(Moteur, "preparer", preparation):
            if self.interface == "console":
                obtenu, sorties, _ = terminal.ConsoleTests().jouer_console(m, numeros)
            else:
                obtenu, sorties = await self.jouer_tui(m, numeros, invalides=geste == "decouper")
        self.assertEqual(terminal.sans_saisie(obtenu.data), terminal.sans_saisie(attendu.data))
        self.assertEqual(web.support.vues(obtenu), web.support.vues(attendu))
        self.assertEqual(web.etat(obtenu), web.etat(attendu))
        self.assertEqual(web.support.vues(obtenu), web.support.vues(Monde(copy.deepcopy(obtenu.data))))
        if refus:
            self.assertIn(refus, lignes)
            self.assertIn(refus, sorties)
            self.assertEqual(obtenu.data, temoin.data)
            self.assertEqual(plans, [])
        else:
            self.assertEqual(plans, [plan])
            for tour in attendu.data.get("conversation", []):
                self.assertIn(tour["reponse"], sorties)
        return obtenu, numeros

    async def test_quatre_parcours_web_commande_plan_effet_et_recharge(self):
        mesures = []
        for geste, variante in (("assembler", False), ("assembler", True), ("decouper", "ficelle"), ("decouper", "perche_2")):
            with self.subTest(geste=geste, variante=variante):
                m = web.atelier(cases=not (geste == "assembler" and variante),
                                planches=geste == "assembler" and variante)
                valeurs = web.valeurs(m, geste, variante if geste == "decouper" else "ficelle",
                                      soigne=geste == "assembler" and variante)
                obtenu, numeros = await self.comparer(m, geste, valeurs)
                if geste == "assembler":
                    echelle = next(o for o in obtenu.objets.values() if o.get("assemblage"))
                    self.assertEqual((echelle["longueur_cm"], echelle["barreaux"]), (300, 8))
                    self.assertEqual(obtenu.objets["ficelle"]["longueur_cm"], 1040)
                else:
                    self.assertEqual(obtenu.objets[variante + "_1"]["longueur_cm"], 100)
                    self.assertEqual(obtenu.objets["perche_1"], m.objets["perche_1"])
                mesures.append({"interface": self.interface, "geste": geste, "variante": variante,
                                "saisies": numeros, "touches_depuis_liste": sum(len(n) + 1 for n in numeros),
                                "touches_avec_f7": sum(len(n) + 1 for n in numeros) + (self.interface == "tui"),
                                "appels_modele": 0})
        print("MESURES_UT_321=" + json.dumps(mesures, ensure_ascii=False))

    async def test_perime_hors_portee_forme_inconnue_et_droits_deux_gestes(self):
        for geste in ("assembler", "decouper"):
            for cause in ("supprimee", "lointaine", "physique", "proprietaire"):
                with self.subTest(geste=geste, cause=cause):
                    m = web.atelier()
                    cible = "perche_2" if geste == "assembler" else "ficelle"
                    mutation = None
                    if cause == "physique":
                        for cle in ("physique", "ressource", "longueur_cm", "charge_jeu_kg"):
                            m.objets[cible].pop(cle, None)
                    elif cause == "proprietaire":
                        m.objets[cible]["proprietaire"] = web.proprietaire_test(m)
                        m = m.copier()
                        from donjon.spatial import installer
                        installer(m)
                        memoriser(m)
                        web.support.vues(m)
                    else:
                        def mutation(monde):
                            if cause == "supprimee":
                                del monde.objets[cible]
                            else:
                                placer(monde.objets[cible], "cour", [5, 3])
                            memoriser(monde)
                            web.support.vues(monde)
                    obtenu, _ = await self.comparer(m, geste, mutation=mutation)
                    self.assertFalse(any(o.get("assemblage") for o in obtenu.objets.values()))


@unittest.skipUnless(shutil.which("node"), "Node requis pour le vrai formulaire web")
class ConsoleTests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = "console"

    async def test_annulation_et_dimensions_invalides_restent_locales(self):
        m = web.atelier()
        numeros, _ = parcours(m, "decouper")
        obtenu, sorties, _ = terminal.ConsoleTests().jouer_console(m, [*numeros[:-1], "0", "1.5", "annuler"])
        self.assertEqual(obtenu.data, m.data)
        self.assertTrue(any("dimension entière" in l for l in sorties))


@unittest.skipUnless(tui.TEXTUAL and shutil.which("node"), "Textual et Node requis")
class TerminalTests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = "tui"

    async def test_annulation_et_nouvelle_vue_ferment_la_recette_sans_effet(self):
        from donjon.tui import SeuilApp
        from textual.widgets import Input
        m = web.atelier()
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "copie.json"
            m.sauver(fichier)
            with (patch("jeu.analyser", side_effect=AssertionError("Analyse de texte")),
                  patch("jeu.MJ", side_effect=AssertionError("Modèle"))):
                app = SeuilApp(["--offline", "--save", str(fichier)])
                async with app.run_test(size=(120, 40)) as pilot:
                    support = terminal.TerminalTests()
                    await support.pret(app)
                    for nouvelle_vue in (False, True):
                        for texte in ("0", "1", "2"):
                            app.query_one("#commande", Input).value = texte
                            await pilot.press("enter")
                        self.assertIsNotNone(app.recette)
                        if nouvelle_vue:
                            app.actualiser(copy.deepcopy(app.derniere_vue))
                        else:
                            app.query_one("#commande", Input).value = "annuler"
                            await pilot.press("enter")
                        self.assertIsNone(app.recette)
                        self.assertFalse(app.occupe)
                        self.assertTrue(app.pont.commandes.empty())
                        self.assertEqual(Monde.charger(fichier).data, m.data)
                    await support.fermer(app)
            recharge = Monde.charger(fichier)
            self.assertEqual(recharge.data, m.data)
            self.assertEqual(web.support.vues(recharge), web.support.vues(m))
