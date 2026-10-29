"""U-P : vrais plans/transactions, trois transports, sauvegarde avant affichage.

Saisies figées du corpus g1-318 : avis-joueur/0,2, crypte/26,41,
soir-appel/5 et echanges/4. Le corpus ne contient pas de perche/saut :
cette composition est une contre-épreuve supplémentaire sur l'atelier.
"""
import asyncio
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.commandes import DescripteurPublic
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import sequence, etape
from donjon.paroles import prevue
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from donjon.transactions import ajouter
from donjon.web.pont import PontWeb
from donjon.emissions import joueur as emissions_joueur
from tests.test_avis_joueur import preparer as scene_avis
from tests.test_espace import terrasse, AJOUT
from donjon.espace import preparer as preparer_espace
from tests.test_parts_achetees import antichambre_du_banc
from tests.test_parole_commune import scene as scene_parole
from tests.support import presentes


def action(p):
    return {"mode": "action", "texte": "", "proposition": p}


def dire(m, saisie, replique, contenu):
    p = {"personnage": prevue(m, saisie)["personnage"], "_intention": saisie,
         "replique": replique, "contenu": contenu}
    return ajouter({"mode": "dialogue", "texte": "Parole enregistrée.", "proposition": None},
                   "parole", m.data["revision"], p)


def cas(nom):
    commandes = []
    if nom in ("offre", "autre_offre"):
        m = presentes(antichambre_du_banc(), "aubin")
        m.objets["planches"]["lieu"] = "aubin"
        m.data["connus"].append("planches")
        lot = "planches"
        if nom == "autre_offre":
            lot = "huile_test"
            m.objets[lot] = {**copy.deepcopy(m.objets["planches"]), "id": lot,
                            "nom": "réserve d'huile", "genre": "f", "pluriel": False, "aliases": ["huile"]}
            m.objets[lot].pop("physique", None)
            m.data["connus"].append(lot)
        saisie = "je paie Aubin trois pièces pour une de ses planches"
        prix = 3 if nom == "offre" else 2
        r = dire(m, saisie, "Je te paie trois pièces pour une de tes planches.",
                 [{"type": "proposition", "demande": {"type": "part", "objet": lot},
                   "contrepartie": {"type": "pieces", "montant": prix}}])
        commandes = ["tenter"]
    elif nom in ("avis", "tous"):
        m = scene_avis()
        saisie = ("je dis à Gorm : l'eau va gagner la conduite basse" if nom == "avis" else
                  "à tous : l'eau ne menace pas le refuge du relais")
        r = dire(m, saisie, saisie.split(": ", 1)[1], [{"type": "avis", "attribut": "menace",
                 "sujet": "echoppe" if nom == "avis" else "antichambre", "valeur": "oui" if nom == "avis" else "non"}])
        commandes = ["tenter"]
    elif nom in ("parole", "chuchotement"):
        m = scene_parole(brune=(2, 3))
        saisie = ("je dis à Brune : bonsoir" if nom == "parole" else
                  "je chuchote à Brune que je me méfie d'Aubin")
        r = dire(m, saisie, "bonsoir" if nom == "parole" else "Je me méfie d'Aubin.", [{"type": "propos"}])
    elif nom == "question":
        m = nouveau_monde()
        saisie = "qu'est-ce qu'il y a derrière la porte, selon toi ?"
        r = {"mode": "dialogue", "texte": "Tu ne sais pas ce qu'il y a derrière.", "proposition": None}
    elif nom in ("vol", "vol_direct"):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        saisie = "J'attends que Gorm ait le dos tourné pour prendre discrètement les crochets"
        r = action(proposition("voler", "crochets", methode="finesse" if nom == "vol" else "simple"))
        commandes = ["tenter"]
    elif nom == "sequence":
        from donjon.atelier import nouveau_atelier
        perche = copy.deepcopy(nouveau_atelier().objets["perche_1"])
        m, _ = terrasse()
        m = preparer_espace(m, AJOUT)
        perche.update(lieu="terrasse", position=list(m.joueur["position"]))
        m.objets["perche_1"] = perche
        saisie = "je prends la perche puis je saute au nord"
        r = action(sequence(etape("deplacer", "perche_1", "joueur"),
                            etape("sauter", "appui_terrasse_nord", "abord_terrasse_nord")))
        commandes = ["tenter"]
    else:
        m = nouveau_monde()
        saisie = ("est-ce que je pourrais prendre la clé ?" if nom == "faisabilite" else
                  "puis-je examiner la clé ?" if nom == "question_perception" else "je ramasse la clé")
        r = action(proposition("examiner" if nom == "question_perception" else "prendre", "cle"))
    return m, saisie, r, commandes


class MJSimule:
    modele, connexion, erreur_auth = "gpt-6-luna", "api", None

    def __init__(self, reponse):
        self.reponse = reponse
        self.appels = 0
        self.monde = None

    def echanger(self, monde, *_):
        self.appels += 1
        self.monde = monde
        r = copy.deepcopy(self.reponse)
        r["_texte_moteur"] = True
        return r

    def fermer(self):
        pass


class PontScript(PontWeb):
    def __init__(self, commandes, chemin):
        super().__init__()
        self.script = iter(commandes)
        self.chemin = chemin
        self.vu = None

    def lire(self, *_):
        return next(self.script, "quitter")

    def ecrire(self, *args, **kw):
        s = " ".join(map(str, args)).strip("\n")
        if "Compris :" in s:
            assert Monde.charger(self.chemin).data["conversation"][-1]["reponse"] in s
        super().ecrire(*args, **kw)

    def rafraichir(self, monde, pending, mj):
        self.vu = copy.deepcopy(monde.data)
        super().rafraichir(monde, pending, mj)


NOMS = ("offre", "autre_offre", "avis", "tous", "parole", "chuchotement", "question",
        "vol", "vol_direct", "sequence", "leger", "faisabilite", "question_perception")
ORACLES = json.loads((Path(__file__).parent / "data" / "comprehension.json").read_text(encoding="utf-8"))


class ComprehensionTests(unittest.TestCase):
    def verifier(self, nom, m, sauvegarde, sorties, vivant):
        recharge = Monde.charger(sauvegarde)
        reponse = recharge.data["conversation"][-1]["reponse"]
        recapitulatifs = [e["reponse"] for e in recharge.data["conversation"]]
        self.assertIn(ORACLES[nom], "\n".join(recapitulatifs))
        if nom != "question":
            self.assertEqual(recharge.data["conversation"][-1]["compris"], ORACLES[nom])
        self.assertIn(reponse, "\n".join(sorties))
        # JSON représente les tuples de coordonnées par des listes ; comparer
        # toute la valeur sérialisable, sans exclure aucun champ du monde.
        self.assertEqual(recharge.data, json.loads(json.dumps(vivant.data)))
        self.assertEqual((regarder(recharge), fiche(recharge), scene_percue(recharge)),
                         (regarder(vivant), fiche(vivant), scene_percue(vivant)))
        if nom in ("question", "faisabilite", "question_perception"):
            self.assertEqual(recharge.objets, m.objets)
            self.assertEqual(recharge.joueur, m.joueur)
            self.assertEqual(recharge.data["journal"], m.data["journal"])
            self.assertIn("aucune action exécutée", reponse)
        elif nom in ("offre", "autre_offre"):
            self.assertEqual(recharge.joueur["or"], m.joueur["or"] - (3 if nom == "offre" else 2))
            lot = "planches" if nom == "offre" else "huile_test"
            self.assertEqual(recharge.objets[lot]["charges"], m.objets[lot]["charges"] - 1)
        elif nom in ("avis", "tous", "parole", "chuchotement"):
            self.assertGreater(len(emissions_joueur(recharge)), len(emissions_joueur(m)))
        elif nom == "sequence":
            self.assertEqual(recharge.objets["perche_1"]["lieu"], "joueur")
            self.assertEqual(recharge.joueur["salle"], "abord_terrasse_nord")
        elif nom in ("vol", "vol_direct"):
            self.assertEqual(recharge.objets["crochets"]["lieu"], "joueur")
            self.assertEqual(len(recharge.data["journal"][-1]["etapes"]), 2 if nom == "vol" else 1)
        elif nom == "leger":
            self.assertEqual(recharge.objets["cle"]["lieu"], "joueur")
        return recharge

    def test_console_et_web_tous_les_cas_puis_reprise(self):
        for transport in ("console", "web"):
            for nom in NOMS:
                with self.subTest(transport=transport, cas=nom), tempfile.TemporaryDirectory() as tmp:
                    m, saisie, r, suite = cas(nom)
                    chemin = Path(tmp) / "partie.json"
                    m.sauver(chemin)
                    commandes = ["mj " + saisie, *suite, "quitter"]
                    pont = PontScript(commandes, chemin) if transport == "web" else None
                    faux = MJSimule(r)
                    with patch.object(jeu, "MJ", return_value=faux), \
                         patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                         patch.object(Monde, "d20", return_value=20), \
                         patch("builtins.input", side_effect=commandes), patch("sys.stdout", io.StringIO()) as sortie:
                        self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], interface=pont), 0)
                    sorties = pont.historique if pont else [sortie.getvalue()]
                    recharge = self.verifier(nom, m, chemin, sorties, faux.monde)
                    avant = copy.deepcopy(recharge.data)
                    reprise = PontScript(["quitter"], chemin)
                    self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise), 0)
                    self.assertEqual(Monde.charger(chemin).data, avant)
                    if "Compris :" in ORACLES[nom]:
                        self.assertIn(recharge.data["conversation"][-1]["reponse"], "\n".join(reprise.historique))

    def test_perime_refuse_sans_compris_et_direct_sans_modele(self):
        for direct in (False, True):
            with self.subTest(direct=direct), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r, _ = cas("leger")
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                entree = DescripteurPublic({"geste": "prendre", "cible": "cle"}) if direct else "mj " + saisie
                pont = PontScript([entree, "quitter"], chemin)
                faux = MJSimule(r)
                preparer = Moteur.preparer
                def perimer(moteur, *a, **kw):
                    plan = preparer(moteur, *a, **kw)
                    if not direct:
                        # La préparation du libre est désormais sur copie ;
                        # périmer le monde vivant, comme une cible réellement partie.
                        faux.monde.objets["cle"]["lieu"] = "crypte"
                    return plan
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                     patch.object(Moteur, "preparer", new=perimer):
                    self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], interface=pont), 0)
                self.assertNotIn("Compris :", "\n".join(pont.historique))
                recharge = Monde.charger(chemin)
                self.assertEqual(recharge.objets["cle"]["lieu"], "joueur" if direct else "crypte")
                self.assertEqual(faux.appels, 0 if direct else 1)
                if not direct:
                    self.assertIn("ici", "\n".join(pont.historique))

    def test_rendu_long_non_tronque(self):
        m = nouveau_monde()
        rendu = "Compris : " + "clause admise ; " * 500
        m.memoriser("texte", rendu, "resultat_moteur", complet=True)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            self.assertEqual(Monde.charger(chemin).data["conversation"][-1]["reponse"], rendu)

    def test_menu_console_sans_compris_ni_appel(self):
        from tests.test_gestes_terminal import menu
        from tools.verifier_websocket_jeu import fixture
        m, _ = fixture("crypte")
        _, numero, _ = menu(m, "cle", "prendre")
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            faux = MJSimule(None)
            with patch.object(jeu, "MJ", return_value=faux), \
                 patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                 patch("builtins.input", side_effect=[numero, "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)]), 0)
            self.assertEqual(faux.appels, 0)
            self.assertNotIn("Compris :", sortie.getvalue())
            self.assertEqual(Monde.charger(chemin).objets["cle"]["lieu"], "joueur")


class ComprehensionTUITests(unittest.IsolatedAsyncioTestCase):
    async def test_tui_tous_les_cas(self):
        from donjon.tui import SeuilApp
        for nom in NOMS:
            with self.subTest(cas=nom), tempfile.TemporaryDirectory() as tmp:
                m, saisie, r, suite = cas(nom)
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                faux = MJSimule(r)
                with patch.object(jeu, "MJ", return_value=faux), \
                     patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                     patch.object(Monde, "d20", return_value=20):
                    app = SeuilApp(["--connexion", "api", "--save", str(chemin)])
                    async with app.run_test(size=(120, 40)) as pilot:
                        async def pret():
                            for _ in range(600):
                                if app.derniere_vue and not app.occupe:
                                    return
                                await asyncio.sleep(.05)
                            self.fail("TUI bloquée : " + str(app.sorties))
                        await pret()
                        for texte in ["mj " + saisie, *suite]:
                            app.soumettre(texte)
                            await pret()
                        ComprehensionTests.verifier(self, nom, m, chemin, app.sorties, faux.monde)
                        app.action_quitter()
                        for _ in range(600):
                            if not app.is_running:
                                break
                            await asyncio.sleep(.05)


if __name__ == "__main__":
    unittest.main()
