"""U-C : consentement sur les trois transports, monde entier et recharge."""
import asyncio
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import jeu
from donjon.commandes import DescripteurPublic
from donjon.consentement import plan_lourd, effets_lourds, preparer
from donjon.deplacement_objet import deplacer
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, Plan, proposition
from donjon.operations import sequence, etape
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from donjon.web.pont import PontWeb
from tests.test_comprehension import MJSimule, PontScript, cas, action
from tests.test_enfermer import scene


def etat(m):
    return json.loads(json.dumps({k: v for k, v in m.data.items() if k != "conversation"}))


def scenario(nom):
    if nom in ("offre", "avis", "leger", "mixte"):
        m, saisie, r, _ = cas("offre" if nom == "mixte" else nom)
        if nom == "offre":
            from donjon import lexique
            from tests.test_narration import segment
            citation = "Bonsoir."
            r["texte"] = "Aubin dit : « " + citation + " »"
            r["_audit"] = {"texte_initial": r["texte"],
                           "segments": segment("parole", locuteur="aubin", citation=citation)["segments"],
                           "faits": {"interlocuteurs": {"aubin": {"nom": "Aubin"}}},
                           "fondement": lexique.corpus("Aubin"),
                           "fondement_paroles": lexique.corpus(citation)}
        if nom == "mixte":
            r.update(mode="action", texte="", proposition=proposition("poser", "couteau"))
            saisie += " puis je pose mon couteau"
        return m, saisie, r
    if nom == "direct":
        m, _, _, _ = cas("offre")
        m.objets["vivres"].update(lieu="joueur", proprietaire="joueur")
        return m, "manger", action(proposition("manger", "vivres"))
    if nom == "paiement":
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        return m, "j'achète les crochets", action(proposition("acheter", "crochets"))
    m, porte = scene()
    deplacer(m, "passe", "joueur")
    m.objets[porte].update(ouverte=nom == "composition", verrouillee=False)
    p = (sequence(etape("fermer", porte), etape("verrouiller", porte, outil="passe"))
         if nom == "composition" else proposition("verrouiller", porte, "passe"))
    return m, ("je ferme la porte du bureau puis je la verrouille avec le passe" if nom == "composition" else
               "je verrouille la porte du bureau avec le passe"), action(p)


LOURDS = ("paiement", "offre", "avis", "enfermement", "composition", "mixte")


def mesurer(transport, nom, phase, secondes, appels):
    chemin = Path(os.environ.get("SEUIL_UC_MESURES", "artifacts/uc-325/mesures.jsonl"))
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(transport=transport, cas=nom, phase=phase,
                               secondes=secondes, appels=appels, temps_humain=0)) + "\n")


class Parcours:
    def __init__(self, test, nom, chemin, faux, transport, mutation=None):
        self.test, self.nom, self.chemin, self.faux = test, nom, chemin, faux
        self.transport, self.mutation = transport, mutation
        self.avant = None
        self.fiche = None
        self.debut = time.perf_counter()

    def apercu(self, monde, pending):
        t = self.test
        t.assertIsNotNone(pending)
        t.assertIn("Compris :", pending.resume(monde))
        t.assertEqual(etat(monde), self.avant)
        t.assertEqual(etat(Monde.charger(self.chemin)), self.avant)
        t.assertEqual(self.faux.appels, 1)
        self.fiche = pending.resume(monde)
        t.assertIn(self.fiche, monde.data["conversation"][-1]["reponse"])
        mesurer(self.transport, self.nom, "saisie_apercu", time.perf_counter() - self.debut, 1)

    def recharge(self, monde):
        t = self.test
        recharge = Monde.charger(self.chemin)
        t.assertEqual(recharge.data, json.loads(json.dumps(monde.data)))
        t.assertEqual((regarder(recharge), fiche(recharge), scene_percue(recharge)),
                      (regarder(monde), fiche(monde), scene_percue(monde)))
        if self.nom == "offre" and recharge.data.get("paroles_pnj"):
            t.assertEqual(recharge.data["paroles_pnj"][-1]["texte"], "Bonsoir.")
        return recharge

    def effet(self, monde):
        t = self.test
        if self.nom == "paiement":
            t.assertEqual(monde.objets["crochets"]["lieu"], "joueur")
            t.assertLess(monde.joueur["or"], self.avant["joueur"]["or"])
        elif self.nom in ("offre", "mixte"):
            t.assertEqual(monde.joueur["or"], self.avant["joueur"]["or"] - 3)
            t.assertEqual(monde.objets["planches"]["charges"], self.avant["objets"]["planches"]["charges"] - 1)
            t.assertIn("Je te paie trois pièces", monde.data["paroles_joueur"][-1]["texte"])
            if self.nom == "offre":
                t.assertEqual(monde.data["paroles_pnj"][-1]["texte"], "Bonsoir.")
            else:
                t.assertEqual(monde.objets["couteau"]["lieu"], monde.joueur["salle"])
        elif self.nom == "avis":
            t.assertEqual(monde.data["paroles_joueur"][-1]["texte"], "l'eau va gagner la conduite basse")
        else:
            portes = [i for i, o in self.avant["objets"].items()
                      if o.get("type") == "porte" and not o.get("verrouillee")
                      and monde.objets[i].get("verrouillee")]
            t.assertEqual(len(portes), 1)


class ConsentementTests(unittest.TestCase):
    def test_classification_effets_branches_et_composition(self):
        leger = Plan({}, 0, "", effets=[("transferer", "a", "joueur")])
        lourd = Plan({}, 0, "", echec=[("endommager", "b", 1)])
        self.assertFalse(plan_lourd(leger))
        self.assertTrue(plan_lourd(lourd))
        self.assertTrue(plan_lourd(Plan({}, 0, "", plans=[leger, lourd])))
        self.assertTrue(effets_lourds([("effet_futur_non_classe", "", None)]))

    def jouer(self, transport, nom, *, mutation=None):
        with tempfile.TemporaryDirectory() as tmp:
            m, saisie, r = scenario(nom)
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            faux = MJSimule(r)
            parcours = Parcours(self, nom, chemin, faux, transport, mutation)
            commandes = iter(["mj " + saisie, "annuler", "mj " + saisie, "tenter", "quitter"])
            step = 0
            dernier_pending = None
            vivant = None
            sorties = []

            def lire(*_):
                nonlocal step
                if step == 0:
                    parcours.debut = time.perf_counter()
                elif step == 1:
                    parcours.apercu(vivant or faux.monde, dernier_pending or dossier[0])
                elif step == 2:
                    self.assertEqual(etat(faux.monde), parcours.avant)
                    self.assertEqual(etat(Monde.charger(chemin)), parcours.avant)
                    parcours.recharge(faux.monde)
                    self.assertEqual(faux.appels, 1)
                elif step == 3:
                    self.assertEqual(etat(faux.monde), parcours.avant)
                    parcours.debut = time.perf_counter()
                elif step == 4:
                    mesurer(transport, nom, "confirmation_effet", time.perf_counter() - parcours.debut,
                            faux.appels - 2)
                    self.assertEqual(faux.appels, 2)
                    self.assertNotEqual(etat(faux.monde), parcours.avant)
                    parcours.effet(faux.monde)
                    parcours.recharge(faux.monde)
                step += 1
                return next(commandes)

            dossier = [None]
            vrai_preparer = jeu.preparer_libre
            def preparer_capture(monde, *a, **kw):
                parcours.avant = etat(monde)
                dossier[0] = vrai_preparer(monde, *a, **kw)
                return dossier[0]

            class Pont(PontWeb):
                def lire(self, *_):
                    return lire()
                def rafraichir(self, monde, pending, mj):
                    nonlocal dernier_pending, vivant
                    dernier_pending, vivant = pending, monde
                    super().rafraichir(monde, pending, mj)

            pont = Pont() if transport == "web" else None
            with patch.object(jeu, "MJ", return_value=faux), \
                 patch.object(jeu, "preparer_libre", side_effect=preparer_capture), \
                 patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                 patch.object(Monde, "d20", return_value=20), \
                 patch("builtins.input", side_effect=lire), patch("sys.stdout", io.StringIO()) as flux:
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], pont), 0)
            sorties = pont.historique if pont else [flux.getvalue()]
            recharge = parcours.recharge(faux.monde)
            self.assertIn(recharge.data["conversation"][-1]["reponse"], "\n".join(sorties))
            avant = copy.deepcopy(recharge.data)
            with patch("builtins.input", return_value="quitter"), patch("sys.stdout", io.StringIO()) as flux:
                jeu.main(["--console", "--offline", "--save", str(chemin)])
                self.assertIn(recharge.data["conversation"][-1]["reponse"], flux.getvalue())
            self.assertEqual(Monde.charger(chemin).data, avant)

    def test_console_web_apercu_annuler_confirmer_recharger(self):
        for transport in ("console", "web"):
            for nom in LOURDS:
                with self.subTest(transport=transport, cas=nom):
                    self.jouer(transport, nom)

    def test_plan_perime_prix_et_cible_sans_revision(self):
        for transport, nom in ((t, n) for t in ("console", "web") for n in ("paiement", "offre")):
            with self.subTest(transport=transport, cas=nom), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r = scenario(nom)
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                faux = MJSimule(r)
                class Pont(PontWeb):
                    def __init__(self):
                        super().__init__()
                        self.tour = 0
                        self.apercus = []
                    def lire(pont, *_):
                        pont.tour += 1
                        if pont.tour == 1:
                            return "mj " + saisie
                        if pont.tour == 2:
                            pont.compris_initial = Monde.charger(chemin).data["conversation"][-1]["compris"]
                            if nom == "paiement":
                                faux.monde.objets["crochets"]["prix"] += 1
                            else:
                                faux.monde.objets["aubin"]["lieu"] = "echoppe"
                            pont.avant = etat(faux.monde)
                            return "tenter"
                        if pont.tour == 3:
                            self.assertEqual(etat(faux.monde), pont.avant)
                            self.assertEqual(faux.appels, 1)
                            derniere = Monde.charger(chemin).data["conversation"][-1]
                            self.assertIn("nouvel aperçu", derniere["reponse"])
                            if nom == "paiement":
                                self.assertNotEqual(pont.compris_initial, derniere["compris"])
                                return "tenter"
                            self.assertIn("Plan indisponible", derniere["reponse"])
                            return "annuler"
                        return "quitter"
                    def rafraichir(pont, monde, pending, mj):
                        if pending:
                            pont.apercus.append(pending.resume(monde))
                        super().rafraichir(monde, pending, mj)
                pont = Pont()
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                     patch("builtins.input", side_effect=pont.lire), patch("sys.stdout", io.StringIO()):
                    jeu.main(["--console", "--connexion", "api", "--save", str(chemin)],
                             pont if transport == "web" else None)
                self.assertEqual(faux.appels, 1)
                if nom == "paiement":
                    self.assertEqual(faux.monde.objets["crochets"]["lieu"], "joueur")
                Parcours(self, nom, chemin, faux, "web").recharge(faux.monde)

    def test_leger_et_clic_lourd_sans_fiche_de_fidelite(self):
        for transport, direct in ((t, d) for t in ("console", "web") for d in (False, True)):
            with self.subTest(transport=transport, direct=direct), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r = scenario("direct" if direct else "leger")
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                entree = DescripteurPublic({"geste": "manger", "cible": "vivres"}) if direct else "mj " + saisie
                faux = MJSimule(r)
                pont = PontScript([entree, "quitter"], chemin) if transport == "web" else None
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                     patch("builtins.input", side_effect=[entree, "quitter"]), \
                     patch("sys.stdout", io.StringIO()) as flux:
                    jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], pont)
                texte = "\n".join(pont.historique) if pont else flux.getvalue()
                self.assertNotIn("« tenter »", texte)
                self.assertEqual(faux.appels, 0 if direct else 1)
                self.assertEqual("Compris :" in texte, not direct)
                recharge = Monde.charger(chemin)
                if direct:
                    self.assertEqual(recharge.objets["vivres"]["portions"], m.objets["vivres"]["portions"] - 1)
                else:
                    self.assertEqual(recharge.objets["cle"]["lieu"], "joueur")

    def test_parole_revalidee_jette_la_narration_de_l_ancien_etat(self):
        with tempfile.TemporaryDirectory() as tmp:
            m, saisie, r = scenario("offre")
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            faux = MJSimule(r)
            class Pont(PontWeb):
                def __init__(pont):
                    super().__init__()
                    pont.tour = 0
                def lire(pont, *_):
                    pont.tour += 1
                    if pont.tour == 1:
                        return "mj " + saisie
                    if pont.tour == 2:
                        faux.monde.data["bruit"] += 1
                        pont.avant = etat(faux.monde)
                        return "tenter"
                    if pont.tour == 3:
                        self.assertEqual(etat(faux.monde), pont.avant)
                        self.assertIn("nouvel aperçu", "\n".join(pont.historique))
                        return "tenter"
                    return "quitter"
            pont = Pont()
            with patch.object(jeu, "MJ", return_value=faux), \
                 patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
                jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], pont)
            self.assertEqual(faux.appels, 1)
            self.assertEqual(faux.monde.joueur["or"], m.joueur["or"] - 3)
            self.assertNotIn("Bonsoir.", "\n".join(pont.historique))
            self.assertFalse(faux.monde.data.get("paroles_pnj"))
            self.assertIn("accepte l'échange", "\n".join(pont.historique))
            Parcours(self, "offre", chemin, faux, "web").recharge(faux.monde)


class ConsentementTUITests(unittest.IsolatedAsyncioTestCase):
    async def pret(self, app):
        for _ in range(1200):
            if not app.is_running:
                return
            if app.derniere_vue and not app.occupe:
                return
            await asyncio.sleep(.05)
        self.fail("TUI bloquée : " + str(app.sorties))

    async def test_tui_perime_prix_et_cible(self):
        from donjon.tui import SeuilApp
        for nom in ("paiement", "offre"):
            with self.subTest(cas=nom), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r = scenario(nom)
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                faux = MJSimule(r)
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
                    app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
                    async with app.run_test(size=(120, 40)) as pilot:
                        await self.pret(app)
                        app.soumettre("mj " + saisie)
                        await self.pret(app)
                        if nom == "paiement":
                            faux.monde.objets["crochets"]["prix"] += 1
                        else:
                            faux.monde.objets["aubin"]["lieu"] = "echoppe"
                        avant = etat(faux.monde)
                        app.soumettre("tenter")
                        await self.pret(app)
                        self.assertEqual(etat(faux.monde), avant)
                        self.assertEqual(faux.appels, 1)
                        self.assertTrue(app.query_one("#proposition-cadre").display)
                        self.assertIn("nouvel aperçu", "\n".join(app.sorties))
                        if nom == "paiement":
                            app.soumettre("tenter")
                            await self.pret(app)
                            self.assertEqual(faux.monde.objets["crochets"]["lieu"], "joueur")
                        else:
                            self.assertIn("Plan indisponible", "\n".join(app.sorties))
                            app.soumettre("annuler")
                            await self.pret(app)
                            self.assertEqual(etat(faux.monde), avant)
                        self.assertEqual(faux.appels, 1)
                        Parcours(self, nom, chemin, faux, "tui").recharge(faux.monde)
                        app.action_quitter()
                        await self.pret(app)

    async def test_tui_leger_et_menu_lourd_sans_fiche_de_fidelite(self):
        from donjon.tui import SeuilApp
        for direct in (False, True):
            with self.subTest(direct=direct), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r = scenario("direct" if direct else "leger")
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                faux = MJSimule(r)
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
                    app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
                    async with app.run_test(size=(120, 40)) as pilot:
                        await self.pret(app)
                        if direct:
                            numero = next(i for i, g in enumerate(app.derniere_vue["gestes"], 1)
                                          if g.descripteur.contenu.get("geste") == "manger" and g.descripteur.contenu.get("cible") == "vivres")
                            app.soumettre(str(numero))
                        else:
                            app.soumettre("mj " + saisie)
                        await self.pret(app)
                        self.assertFalse(app.query_one("#proposition-cadre").display)
                        self.assertEqual(faux.appels, 0 if direct else 1)
                        self.assertEqual("Compris :" in "\n".join(app.sorties), not direct)
                        recharge = Monde.charger(chemin)
                        if direct:
                            self.assertEqual(recharge.objets["vivres"]["portions"], m.objets["vivres"]["portions"] - 1)
                        else:
                            self.assertEqual(recharge.objets["cle"]["lieu"], "joueur")
                        app.action_quitter()
                        await self.pret(app)

    async def test_tui_apercu_annuler_confirmer_recharger(self):
        from donjon.tui import SeuilApp
        for nom in LOURDS:
            with self.subTest(cas=nom), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r = scenario(nom)
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                faux = MJSimule(r)
                parcours = Parcours(self, nom, chemin, faux, "tui")
                vrai = jeu.preparer_libre
                capture = [None]
                def preparer_capture(monde, *a, **kw):
                    parcours.avant = etat(monde)
                    capture[0] = vrai(monde, *a, **kw)
                    return capture[0]
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.object(jeu, "preparer_libre", side_effect=preparer_capture), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                     patch.object(Monde, "d20", return_value=20):
                    app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
                    async with app.run_test(size=(120, 40)) as pilot:
                        async def pret():
                            for _ in range(1200):
                                if not app.is_running:
                                    return
                                if app.derniere_vue and not app.occupe:
                                    return
                                await asyncio.sleep(.05)
                            self.fail("TUI bloquée : " + str(app.sorties))
                        await pret()
                        parcours.debut = time.perf_counter()
                        app.soumettre("mj " + saisie)
                        await pret()
                        parcours.apercu(faux.monde, capture[0])
                        self.assertTrue(app.query_one("#proposition-cadre").display)
                        await pilot.click("#annuler")
                        await pret()
                        self.assertEqual(etat(faux.monde), parcours.avant)
                        self.assertEqual(etat(Monde.charger(chemin)), parcours.avant)
                        parcours.recharge(faux.monde)
                        app.soumettre("mj " + saisie)
                        await pret()
                        avant = faux.appels
                        parcours.debut = time.perf_counter()
                        await pilot.click("#tenter")
                        await pret()
                        mesurer("tui", nom, "confirmation_effet", time.perf_counter() - parcours.debut,
                                faux.appels - avant)
                        self.assertEqual(faux.appels, avant)
                        self.assertNotEqual(etat(faux.monde), parcours.avant)
                        parcours.effet(faux.monde)
                        self.assertFalse(app.query_one("#proposition-cadre").display)
                        parcours.recharge(faux.monde)
                        app.action_quitter()
                        await pret()
