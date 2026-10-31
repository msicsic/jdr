"""U-T information : vrais terminaux, choix web, paroles et état rechargé."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import jeu
from donjon.commandes import DescripteurPublic
from donjon.consentement import PropositionLibre
from donjon.dialogues import InformationTerminal, information_publique, parole_information, preparer_direct
from donjon.emissions import pnj
from donjon.esprits import croire, croyance
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde, objet
from donjon.paroles import preparer_parole
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer
from donjon.voix import reel
from tests import test_information_publique as web
from tests import test_tui as tui
from tests.test_gestes_terminal import sans_saisie
from tests.test_parole_corrections import banc
from tests.test_tensions import recharger


def parcours(m, d):
    formulaire = InformationTerminal(information_publique(m))
    numeros = ["information"]
    while not formulaire.terminee:
        if formulaire.destinataire is None:
            valeur = d.contenu["cible"]
        elif formulaire.formulaire is None:
            valeur = next(f for f in formulaire.formulaires if f["acte"] == d.contenu["parametres"]["acte"])
        else:
            valeur = d.contenu["parametres"][formulaire.champ["champ"]]
        numero = next(str(i) for i, (v, _) in enumerate(formulaire.choix(), 1) if v == valeur)
        numeros.append(numero)
        obtenu = formulaire.saisir(numero)
    assert obtenu == d
    return numeros


def partir(m):
    m.objets["aubin"]["lieu"] = "crypte"
    placer(m.objets["aubin"], "crypte", [3, 3])


class FormulaireTests(unittest.TestCase):
    def test_projection_figee_choix_explicites_et_limite_objet(self):
        m = banc("ressources")
        # Le choix vise un bien précis : le contexte lexical ne l'apprend pas.
        m.data["connus"].append("bois")
        avant = copy.deepcopy(m.data)
        public = information_publique(m)
        f = InformationTerminal(public)
        rendu = f.rendre()
        public["destinataires"].clear()
        self.assertEqual(f.rendre(), rendu)
        self.assertIn("où est un objet reste indisponible", rendu)
        m.objets["secret_369"] = objet("secret_369", "opale indicible", "tresor", "crypte")
        croire(m, "aubin", "secret_369", "lieu", "crypte", "vu")
        self.assertNotIn("secret_369", json.dumps(information_publique(m)))
        for acte in ("qui", "localisation", "affirmation", "ressource"):
            parametres = {"qui": {}, "localisation": {"sujet": "joueur"},
                "affirmation": {"sujet": "cloche", "valeur": "antichambre"},
                "ressource": {"sujet": "bois"}}[acte]
            d = web.descripteur("aubin", acte, **parametres)
            self.assertTrue(parcours(m, d))
        self.assertEqual({k: v for k, v in m.data.items() if k not in ("objets", "esprits")},
                         {k: v for k, v in avant.items() if k not in ("objets", "esprits")})
        f = InformationTerminal(information_publique(m))
        for texte in ("", "0", "1 2", "1,2", "aubin", "9" * 5000):
            with self.assertRaises(ValueError):
                f.saisir(texte)
        self.assertIsNone(f.saisir("annuler"))
        self.assertTrue(f.terminee)
        with self.assertRaises(ValueError):
            f.saisir("1")

    def test_biens_connus_ou_inconnus_memes_choix_web_terminal_apres_recharge(self):
        base = banc("ressources")
        for sujet in ("bois", "crochets"):
            self.assertNotIn(sujet, base.data["connus"])
            self.assertFalse(base.visible(sujet))
            for connu in (False, True):
                with self.subTest(sujet=sujet, connu=connu):
                    m = base.copier()
                    if connu:
                        m.data["connus"].append(sujet)
                    avant = copy.deepcopy(m.data)
                    vues = regarder(m), fiche(m), scene_percue(m)
                    public = information_publique(m)
                    m = recharger(m)
                    self.assertEqual(m.data, avant)
                    self.assertEqual((regarder(m), fiche(m), scene_percue(m)), vues)
                    self.assertEqual(information_publique(m), public)
                    self.assertEqual(m.objets, base.objets)
                    self.assertFalse(m.visible(sujet))

                    f = InformationTerminal(public)
                    f.saisir(next(str(i) for i, (v, _) in enumerate(f.choix(), 1) if v == "aubin"))
                    f.saisir(next(str(i) for i, (v, _) in enumerate(f.choix(), 1)
                                  if v["acte"] == "ressource"))
                    ids = [v for v, _ in f.choix()]
                    self.assertEqual(sujet in ids, connu)
                    self.assertEqual("[" + sujet + "]" in f.rendre(), connu)
                    self.assertEqual(ids, [x["id"] for x in public["ressources"]])

                    # Les vrais callbacks web rendent le même choix, y compris
                    # en négatif : la catégorie faim permet d'ouvrir le champ.
                    etat = web.etat(m)
                    self.assertEqual(etat["information"], {**public, "formulaires": f.formulaires})
                    etat["sonde_information"] = {"À qui parler": "aubin",
                        "Acte d'information": "ressource",
                        "Ressource recherchée": sujet if connu else "faim"}
                    clic = web.page(m, etat)["information"]
                    champ = next(c for c in clic["champs"] if c["nom"] == "Ressource recherchée")
                    self.assertEqual([c["valeur"] for c in champ["choix"] if c["valeur"]], ids)
                    d = web.descripteur("aubin", "ressource", sujet=sujet)
                    if connu:
                        self.assertTrue(parcours(m, d))
                        self.assertEqual(clic["envoye"], d.contenu)
                    else:
                        with self.assertRaises(ErreurMonde) as refus:
                            parole_information(m, d.contenu)
                        self.assertTrue(refus.exception.attendu)
                    self.assertEqual(m.data, avant)

    def test_homonymes_references_publiques_et_champs_du_catalogue(self):
        m, cible, autre = web.support_corps.monde_geste("saisir", 1)
        for qui in (cible, autre):
            parcours(m, web.descripteur(qui, "qui"))
        f = InformationTerminal(information_publique(m))
        noms = [l for _, l in f.choix()]
        self.assertEqual(len(noms), len(set(noms)))
        f.saisir("1")
        f.saisir("3")
        self.assertEqual(f.valeurs, [])  # Aucun lieu annoncé présélectionné.
        self.assertEqual(f.champ["champ"], "sujet")
        f.saisir("1")
        self.assertEqual(f.champ["champ"], "valeur")
        self.assertFalse(f.terminee)


class ParcoursInformation:
    async def jouer(self, m, entrees, *, depart=None, invalide=False):
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "copie.json"
            m.sauver(fichier)
            faux = MagicMock(connexion="api", erreur_auth=None)
            faux.echanger.side_effect = AssertionError("Appel au modèle")
            lignes, captures, monde_actuel = [], [], []
            original_revalider = PropositionLibre.revalider

            def preparation(monde, d):
                self.assertIsInstance(d, DescripteurPublic)
                captures.append(copy.deepcopy(d.contenu))
                monde_actuel[:] = [monde]
                if depart == "reception":
                    partir(monde)
                return preparer_direct(monde, d)

            def revalider(dossier, monde):
                if depart == "confirmation":
                    partir(monde)
                return original_revalider(dossier, monde)

            publications = []

            def verifier_sauvegarde(texte):
                if monde_actuel and monde_actuel[0].data.get("conversation"):
                    monde = monde_actuel[0]
                    if texte.strip() == monde.data["conversation"][-1]["reponse"].strip():
                        self.assertEqual(Monde.charger(fichier).data, json.loads(json.dumps(monde.data)))
                        publications.append(texte)

            with (patch("jeu.MJ", return_value=faux),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", side_effect=AssertionError("Analyse du choix")),
                  patch("donjon.paroles.analyser", side_effect=AssertionError("Analyse du choix")),
                  patch("donjon.dialogues.preparer_direct", side_effect=preparation),
                  patch.object(PropositionLibre, "revalider", revalider),
                  patch.object(Monde, "d20", return_value=20)):
                if self.interface == "console":
                    def ecrire(*args, **_):
                        texte = " ".join(map(str, args))
                        lignes.append(texte)
                        verifier_sauvegarde(texte)

                    with (patch("builtins.input", side_effect=[*entrees, "quitter"]),
                          patch("builtins.print", side_effect=ecrire)):
                        self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(fichier)]), 0)
                    self.assertIn("information. Demander", "\n".join(lignes))
                else:
                    from donjon.tui import SeuilApp
                    from textual.widgets import Input
                    app = SeuilApp(["--connexion", "api", "--save", str(fichier)])
                    ecrire_app = app.ecrire

                    def ecrire(texte):
                        verifier_sauvegarde(texte)
                        ecrire_app(texte)

                    app.ecrire = ecrire
                    async with app.run_test(size=(120, 40)) as pilot:
                        support = tui.TUITests()
                        await support.pret(app)
                        await pilot.press("f7")
                        self.assertEqual(app.derniere_vue["information"], information_publique(m))
                        for texte in entrees:
                            vue = app.derniere_vue
                            app.query_one("#commande", Input).value = texte
                            await pilot.press("enter")
                            if app.recette is not None:
                                self.assertIs(app.derniere_vue, vue)
                                self.assertTrue(app.pont.commandes.empty())
                                self.assertFalse(app.occupe)
                                self.assertEqual(Monde.charger(fichier).data, m.data)
                                if invalide:
                                    for incorrect in ("0", "1 2", "aubin"):
                                        app.query_one("#commande", Input).value = incorrect
                                        await pilot.press("enter")
                                        self.assertTrue(app.pont.commandes.empty())
                                    await pilot.press("ctrl+right", "shift+left")
                                    self.assertTrue(app.pont.commandes.empty())
                            elif app.occupe:
                                await support.attendre(lambda: app.derniere_vue is not vue and not app.occupe,
                                                       lambda: repr(app.sorties[-5:]))
                        lignes = list(app.sorties)
                        vue = app.derniere_vue
                        await support.fermer(app)
                        recharge = Monde.charger(fichier)
                        self.assertEqual(vue["fiche"], fiche(recharge))
                        self.assertEqual(vue["scene"], regarder(recharge))
            faux.echanger.assert_not_called()
            faux.raconter_resultat.assert_not_called()
            return Monde.charger(fichier), lignes, captures, publications

    async def comparer(self, m, d, *, annuler=False, depart=None, invalide=False):
        installer(m)
        numeros = parcours(m, d)
        clic, _ = web.InformationPubliqueTests().clic(m, d)
        self.assertEqual(clic, d)
        if not depart:
            p = parole_information(m, d.contenu)
            with patch.object(Monde, "d20", return_value=20):
                attendu_type, rapport = preparer_parole(m, {**p,
                    "_intention": f"je dis à {p['personnage']} : « {p['replique']} »"})
                dossier = preparer_direct(m, d)
            self.assertEqual(dossier.travail.data, attendu_type.data)
            self.assertEqual(dossier.rapports, [rapport])
        suite = ["annuler" if annuler else "tenter"] if d.contenu["parametres"]["acte"] == "affirmation" else []
        temoin = m.copier()
        if depart == "reception":
            # Même instant que le terminal : le destinataire a été perçu lors
            # de l'ouverture, puis part avant la préparation de la parole.
            # Le déplacer avant le chargement effacerait ce souvenir public.
            def preparation_web(monde, choix):
                partir(monde)
                return preparer_direct(monde, choix)
            with patch("donjon.dialogues.preparer_direct", side_effect=preparation_web):
                attendu, sorties_web, _ = web.InformationPubliqueTests().boucle(temoin, [d, *suite])
        else:
            attendu, sorties_web, _ = web.InformationPubliqueTests().boucle(
                temoin, [d, *suite], mutation=partir if depart == "confirmation" else None)
        obtenu, lignes, captures, publications = await self.jouer(m, [*numeros, *suite], depart=depart, invalide=invalide)
        self.assertEqual(captures, [d.contenu])
        self.assertEqual(sans_saisie(obtenu.data), sans_saisie(attendu.data))
        recharge = recharger(obtenu)
        self.assertEqual(recharge.data, obtenu.data)
        self.assertEqual(pnj(recharge), pnj(attendu))
        self.assertEqual(scene_percue(recharge), scene_percue(attendu))
        self.assertEqual(fiche(recharge), fiche(attendu))
        self.assertEqual(regarder(recharge), regarder(attendu))
        for emission in pnj(attendu):
            if emission not in pnj(m):
                self.assertIn(emission["texte"], "\n".join(lignes))
        if depart:
            self.assertIn("perçois plus", "\n".join(lignes))
            self.assertEqual(pnj(obtenu), pnj(m))
            self.assertEqual(obtenu.data["revision"], m.data["revision"])
        elif not annuler:
            self.assertTrue(publications)
        print("MESURE_UT_369=" + json.dumps({"interface": self.interface, "descripteur": d.contenu,
            "annule": annuler, "depart": depart, "saisies": [*numeros, *suite],
            "touches_jusqua_reponse": sum(len(n) + 1 for n in [*numeros, *suite]),
            "touches_avec_f7": sum(len(n) + 1 for n in [*numeros, *suite]) + (self.interface == "tui"),
            "appels_modele": 0}, ensure_ascii=False))
        return obtenu

    async def test_quatre_actes_reponses_croyances_et_recharge(self):
        m = banc("soir-noir")
        from donjon.paroles import entendre_repondant
        entendre_repondant(m, "ilse")
        voix = next(x["id"] for x in information_publique(m)["destinataires"] if reel(m, x["id"]) == "ilse")
        r = await self.comparer(m, web.descripteur(voix, "qui"))
        self.assertEqual(pnj(r)[-1]["texte"], "Je m'appelle Ilse.")
        self.assertEqual(r.data["voix_entendues"]["ilse"]["se_dit"], "ilse")
        for sujet, lieu_cru, lieu_reel in (("ilse", "crypte", "beffroi"), ("brune", "beffroi", "crypte")):
            with self.subTest(sujet=sujet):
                m = banc("noms-dialogue")
                m.objets[sujet]["lieu"] = lieu_reel
                placer(m.objets[sujet], lieu_reel, [3, 3])
                croire(m, "aubin", sujet, "lieu", lieu_cru, "vu", 1., salle=lieu_cru, case=None)
                m = recharger(m)
                r = await self.comparer(m, web.descripteur("aubin", "localisation", sujet=sujet))
                self.assertEqual(croyance(r, "joueur", sujet, "lieu")["valeur"], lieu_cru)
                self.assertNotEqual(croyance(r, "joueur", sujet, "lieu")["source"], "vu")
                self.assertEqual(r.objets[sujet]["lieu"], lieu_reel)
        for qui, sujet in (("aubin", "bois"), ("brune", "faim")):
            m = banc("ressources")
            if sujet == "bois":
                m.data["connus"].append(sujet)
            r = await self.comparer(m, web.descripteur(qui, "ressource", sujet=sujet))
            self.assertTrue(pnj(r)[-1]["texte"].startswith("J'ai ") if qui == "aubin"
                            else pnj(r)[-1]["texte"] == "Je n'en ai pas.")
        m = banc("ressources")
        m.data["connus"].append("crochets")
        r = await self.comparer(m, web.descripteur("aubin", "ressource", sujet="crochets"))
        self.assertEqual(pnj(r)[-1]["texte"], "Je n'en ai pas.")
        r = await self.comparer(banc("ressources"), web.descripteur("aubin", "affirmation", sujet="cloche", valeur="antichambre"))
        self.assertEqual(croyance(r, "aubin", "cloche", "lieu")["valeur"], "antichambre")

    async def test_autre_scenario_homonymes_et_mefiance(self):
        m, cible, autre = web.support_corps.monde_geste("saisir", 1)
        for qui in (cible, autre):
            r = await self.comparer(m.copier(), web.descripteur(qui, "qui"))
            self.assertEqual(pnj(r)[-1]["locuteur"], qui)
        for acte, params in (("ressource", {"sujet": "faim"}), ("localisation", {"sujet": autre}),
                             ("affirmation", {"sujet": "joueur", "valeur": "salle_commune"})):
            await self.comparer(m.copier(), web.descripteur(cible, acte, **params))
        from tests.test_avis_menace import relation
        for acte in ("qui", "ressource"):
            m = banc("ressources")
            if acte == "ressource":
                m.data["connus"].append("bois")
            relation(m, "aubin", "joueur", confiance=0)
            r = await self.comparer(m, web.descripteur("aubin", acte, **({"sujet": "bois"} if acte == "ressource" else {})))
            self.assertEqual(pnj(r)[-1]["modalite"], "refus")

    async def test_annulations_et_destinataire_parti(self):
        d = web.descripteur("aubin", "affirmation", sujet="cloche", valeur="antichambre")
        m = banc("ressources")
        r = await self.comparer(m, d, annuler=True)
        self.assertEqual(r.objets, m.objets)
        self.assertEqual(pnj(r), pnj(m))
        r, _, captures, _ = await self.jouer(m, [*parcours(m, d)[:-1], "annuler"], invalide=True)
        self.assertEqual(captures, [])
        self.assertEqual(r.data, m.data)
        await self.comparer(banc("ressources"), web.descripteur("aubin", "qui"), depart="reception")
        await self.comparer(banc("ressources"), d, depart="confirmation")


class ConsoleInformationTests(ParcoursInformation, unittest.IsolatedAsyncioTestCase):
    interface = "console"


@unittest.skipUnless(tui.TEXTUAL, "Installer requirements-tui.txt")
class TuiInformationTests(ParcoursInformation, unittest.IsolatedAsyncioTestCase):
    interface = "tui"
