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
from donjon.transactions import ajouter
from donjon.emissions import joueur as emissions_joueur, pnj as emissions_pnj
from tests.test_comprehension import MJSimule, PontScript, cas, action
from tests.test_enfermer import scene


COMPTE_OFFRE = ("J'accepte cet échange. Tu m'as payé 3 pièces. "
                "Je te remets une part des planches de bac. "
                "Tu m'offres 3 pièces contre une part de planches de bac.")


def etat(m):
    return json.loads(json.dumps({k: v for k, v in m.data.items() if k != "conversation"}))


def scenario(nom):
    if nom in ("offre", "avis", "leger", "mixte"):
        m, saisie, r, _ = cas("offre" if nom == "mixte" else nom)
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
        if self.nom == "offre" and emissions_pnj(recharge):
            t.assertEqual(emissions_pnj(recharge)[-1]["texte"], COMPTE_OFFRE)
        return recharge

    def effet(self, monde):
        t = self.test
        if self.nom == "paiement":
            t.assertEqual(monde.objets["crochets"]["lieu"], "joueur")
            t.assertLess(monde.joueur["or"], self.avant["joueur"]["or"])
        elif self.nom in ("offre", "mixte"):
            t.assertEqual(monde.joueur["or"], self.avant["joueur"]["or"] - 3)
            t.assertEqual(monde.objets["planches"]["charges"], self.avant["objets"]["planches"]["charges"] - 1)
            t.assertIn("Je te paie trois pièces", emissions_joueur(monde)[-1]["texte"])
            if self.nom == "offre":
                t.assertEqual(emissions_pnj(monde)[-1]["texte"], COMPTE_OFFRE)
            else:
                t.assertEqual(monde.objets["couteau"]["lieu"], monde.joueur["salle"])
        elif self.nom == "avis":
            t.assertEqual(emissions_joueur(monde)[-1]["texte"], "l'eau va gagner la conduite basse")
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

    def test_demander_les_termes_ne_prend_pas_l_engagement(self):
        from donjon import agendas
        for transport in ("console", "web"):
            for acteur in ("marchand", "autre_donneur"):
                with self.subTest(transport=transport, acteur=acteur), tempfile.TemporaryDirectory() as tmp:
                    m = nouveau_monde()
                    if acteur != "marchand":
                        m.objets[acteur] = {**copy.deepcopy(m.objets["marchand"]),
                                            "id": acteur, "nom": "Maëlle", "aliases": []}
                        m = Monde(copy.deepcopy(m.data))
                    m.joueur["salle"] = "echoppe"
                    m.objets[acteur]["lieu"] = "echoppe"
                    m.data["missions"]["anneau_veilleur"]["donneur"] = acteur
                    m.data["finances_pnj"][acteur] = 50
                    p = {"personnage": acteur, "sujet": "Quelle récompense ?", "operation": "proposer",
                         "mission": "anneau_veilleur", "montant_demande": 0}
                    r = ajouter({"mode": "dialogue", "texte": "Une offre reste à accepter.", "proposition": None},
                                "conversation_pnj", m.data["revision"], p)
                    # Demander les termes n'engage pas Corvus. Leur acceptation
                    # reste un effet lourd, sur le même contrat de transaction.
                    d = preparer(m, r, "LLM")
                    self.assertFalse(d.confirmation)
                    r.update(d.compte_parle())
                    accepte = copy.deepcopy(r)
                    accepte["_transactions"][0]["revision"] = d.travail.data["revision"]
                    accepte["_transactions"][0]["proposition"]["operation"] = "accepter"
                    self.assertTrue(preparer(d.travail, accepte, "LLM").confirmation)
                    chemin = Path(tmp) / "partie.json"
                    m.sauver(chemin)
                    faux = MJSimule(r)
                    commandes = ["mj je demande quelle récompense on me propose", "quitter"]
                    pont = PontScript(commandes, chemin) if transport == "web" else None
                    with patch.object(jeu, "MJ", return_value=faux), \
                         patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                         patch("builtins.input", side_effect=commandes), patch("sys.stdout", io.StringIO()) as flux:
                        self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], pont), 0)
                    sorties = "\n".join(pont.historique) if pont else flux.getvalue()
                    self.assertNotIn("« tenter »", sorties)
                    self.assertEqual(faux.appels, 1)
                    recharge = Monde.charger(chemin)
                    self.assertEqual(recharge.data, json.loads(json.dumps(faux.monde.data)))
                    self.assertEqual(agendas.contrats(recharge)["anneau_veilleur"]["statut"], "propose")
                    self.assertEqual(recharge.joueur["or"], m.joueur["or"])
                    self.assertIn("offre à accepter", fiche(recharge))
                    self.assertEqual((regarder(recharge), fiche(recharge), scene_percue(recharge)),
                                     (regarder(faux.monde), fiche(faux.monde), scene_percue(faux.monde)))
                    avant = copy.deepcopy(recharge.data)
                    reprise = PontScript(["quitter"], chemin)
                    jeu.main(["--console", "--offline", "--save", str(chemin)], reprise)
                    self.assertEqual(Monde.charger(chemin).data, avant)

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

    def test_revalidation_actualise_le_sceau_et_garde_toute_la_composition(self):
        from donjon.emissions import enregistrer
        for nom in ("offre", "mixte"):
            with self.subTest(cas=nom), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r = scenario(nom)
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                faux = MJSimule(r)
                class Pont(PontWeb):
                    def __init__(pont):
                        super().__init__()
                        pont.tour = 0
                        pont.pending = None
                    def rafraichir(pont, monde, pending, mj):
                        pont.pending = pending
                        super().rafraichir(monde, pending, mj)
                    def lire(pont, *_):
                        pont.tour += 1
                        if pont.tour == 1:
                            return "mj " + saisie
                        if pont.tour == 2:
                            self.assertEqual(pont.pending.reponse["_comptes_parles"], [2])
                            enregistrer(faux.monde, "joueur", acte="parole_joueur", parametres={},
                                modalite="constat", evenement={"type": "dialogue_audite"},
                                auditeurs=["aubin"], a=["aubin"], texte="Je réfléchis.")
                            pont.avant = etat(faux.monde)
                            return "tenter"
                        if pont.tour == 3:
                            self.assertEqual(etat(faux.monde), pont.avant)
                            self.assertIn("nouvel aperçu", "\n".join(pont.historique))
                            self.assertEqual(pont.pending.reponse["_comptes_parles"], [3])
                            self.assertEqual(pont.pending.reponse["mode"], r["mode"])
                            return "tenter"
                        return "quitter"
                pont = Pont()
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
                    jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], pont)
                self.assertEqual(faux.appels, 1)
                self.assertEqual(faux.monde.joueur["or"], m.joueur["or"] - 3)
                comptes = [p for p in emissions_pnj(faux.monde) if p["acte"] == "reponse_comptable"]
                self.assertEqual([(p["id"], p["texte"]) for p in comptes], [(3, COMPTE_OFFRE)])
                self.assertEqual("\n".join(pont.historique).count(COMPTE_OFFRE), 1)
                if nom == "mixte":
                    self.assertEqual(faux.monde.objets["couteau"]["lieu"], faux.monde.joueur["salle"])
                Parcours(self, nom, chemin, faux, "web").recharge(faux.monde)


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
