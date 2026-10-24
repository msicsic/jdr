import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.capacites_objet import statut as statut_capacite
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.faits_locaux import preparer_faits
from donjon.improvisation import effet, issue, proposition as improviser
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, QualificationRequise, proposition
from donjon.operations import etape, sequence
from donjon.rendu import decrire
from donjon.spatial import installer
from tests.support import sans_budget


class CapacitesObjetTests(unittest.TestCase):
    def test_etat_des_capacites_physiques_et_contradictions(self):
        m = nouveau_atelier()
        self.assertEqual(statut_capacite(m.objets["ficelle"], "son"), "inconnue")
        self.assertEqual(statut_capacite(m.objets["hache"], "couper"), "etablie")
        self.assertEqual(statut_capacite(m.objets["hache"], "allumage"), "ecartee")
        with self.assertRaises(QualificationRequise):
            Moteur(m).preparer(analyser(m, "sonner ficelle"))
        with self.assertRaises(QualificationRequise):
            Moteur(m).preparer(proposition("allumer", "ficelle"))
        exclusion = {"ajouts": [{"type": "qualification", "ancrage": "ficelle",
                                 "ecartees": ["son", "lumiere"]}]}
        travail, texte, _ = preparer_faits(m, exclusion)
        self.assertEqual(statut_capacite(travail.objets["ficelle"], "son"), "ecartee")
        self.assertEqual(statut_capacite(travail.objets["ficelle"], "lumiere"), "ecartee")
        self.assertIn("ne peut pas produire de son", texte)
        self.assertIn("ne peut pas éclairer", decrire(travail, "ficelle", detail=True))
        with self.assertRaisesRegex(ErreurMonde, "ne peut pas produire de son"):
            Moteur(travail).preparer(analyser(travail, "sonner ficelle"))
        with self.assertRaisesRegex(ErreurMonde, "ne peut pas éclairer"):
            Moteur(travail).preparer(proposition("allumer", "ficelle"))
        with self.assertRaises(ErreurMonde):
            preparer_faits(travail, {"ajouts": [{"type": "qualification",
                "ancrage": "ficelle", "capacites": [{"nature": "son", "intensite": 2}]}]})
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, {"ajouts": [{"type": "qualification",
                "ancrage": "hache", "ecartees": ["couper"]}]})
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "atelier.json"
            travail.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual([c["capacite"] for c in reprise.objets["ficelle"]["constats_capacites"]],
                         ["son", "lumiere"])
        self.assertIn("ne peut pas éclairer", decrire(reprise, "ficelle", detail=True))
        reprise.objets["ficelle"]["sonorite"] = 2
        with self.assertRaises(ErreurMonde):
            reprise.verifier()
        reprise.objets["ficelle"].pop("sonorite")
        reprise.objets["ficelle"]["materiau"] = "cuivre"
        self.assertEqual(statut_capacite(reprise.objets["ficelle"], "son"), "inconnue")
        self.assertIn("état antérieur", decrire(reprise, "ficelle", detail=True))
        reprise.verifier()
        reprise, _, _ = preparer_faits(reprise, {"ajouts": [{
            "type": "qualification", "ancrage": "ficelle",
            "capacites": [{"nature": "son", "intensite": 2}]}]})
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "nouvel_etat.json"
            reprise.sauver(chemin)
            changee = Monde.charger(chemin)
        self.assertEqual(statut_capacite(changee.objets["ficelle"], "son"), "etablie")
        self.assertIn("état antérieur", decrire(changee, "ficelle", detail=True))

    def test_outil_declare_par_luna_en_console_et_utilisable_apres_rechargement(self):
        ajout = {"type": "objet", "ancrage": "antichambre_sol",
                 "nom": "percuteur de fer", "genre": "m",
                 "texte": "Il produit des étincelles pour allumer une autre source.",
                 "materiau": "fer et silex", "masse": 0.2, "mobile": True,
                 "relation": "pose", "capacites": [{"nature": "outil",
                                                  "usages": ["allumage"], "puissance": 0}]}
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [ajout]}}
        rapport = {"usages": [{"perception_requise": False, "indice": False, "motif": ""}], "descriptions": [{
            "representation": representation, "mobilite": [], "placement": "aucun",
            "impact_scenario": "aucun", "capacites": ["allumage"],
            "fragments": [{"texte": texte, "portee": "sujet", "preuve": "", "motif": ""}]}
            for representation, texte in (("objet", ajout["nom"]), ("aspect", ajout["texte"]))]}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            sans_budget(nouveau_monde()).sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[reponse, rapport]),
                  patch("builtins.input", side_effect=["mj Y a-t-il un percuteur ici ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            self.assertIn("percuteur de fer", sortie.getvalue())
            reprise = Monde.charger(chemin)
            id = reprise.trouver("percuteur de fer")
            self.assertEqual(reprise.objets[id]["usages"], ["allumage"])
            moteur = Moteur(reprise)
            moteur.executer(moteur.preparer(proposition("prendre", id)))
            reprise.objets["lanterne"]["allume"] = False
            moteur.executer(moteur.preparer(proposition("allumer", "lanterne", outil=id)))
            reprise.sauver(chemin)
            verifie = Monde.charger(chemin)
            self.assertTrue(verifie.objets["lanterne"]["allume"])
            self.assertEqual(verifie.objets[id]["lieu"], "joueur")
            self.assertIn("allumer une source", decrire(verifie, id, detail=True))

    def test_objet_sonore_propose_par_luna_sonne_en_console_apres_rechargement(self):
        ajout = {"type": "objet", "ancrage": "antichambre_sol",
                 "nom": "clochette de cuivre", "genre": "f",
                 "texte": "Le cuivre est martelé et vibre quand on la secoue.",
                 "materiau": "cuivre", "masse": 0.2, "mobile": True,
                 "relation": "pose", "capacites": [{"nature": "son", "intensite": 2}]}
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [ajout]}}
        rapport = {"usages": [{"perception_requise": False, "indice": False, "motif": ""}], "descriptions": [
            {"representation": "objet", "mobilite": [], "placement": "aucun",
             "impact_scenario": "aucun", "capacites": ["son"], "fragments": [{
                 "texte": ajout["nom"], "portee": "sujet", "preuve": "", "motif": ""}]},
            {"representation": "aspect", "mobilite": [], "placement": "aucun",
             "impact_scenario": "aucun", "capacites": ["son"], "fragments": [{
                 "texte": ajout["texte"], "portee": "sujet", "preuve": "", "motif": ""}]},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[reponse, rapport]) as appel,
                  patch("builtins.input", side_effect=["mj Y a-t-il une clochette ici ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            self.assertEqual(appel.call_count, 2)
            self.assertIn("clochette de cuivre", sortie.getvalue())
            cree = Monde.charger(chemin)
            id = cree.trouver("clochette de cuivre")
            self.assertEqual(cree.objets[id]["sonorite"], 2)
            self.assertIn("son audible", decrire(cree, id))
            with (patch("builtins.input", side_effect=["sonner clochette de cuivre", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            reprise = Monde.charger(chemin)
            self.assertIn("produis un son", sortie.getvalue())
            self.assertEqual(reprise.data["sons"][-1]["objet"], id)
            self.assertEqual(reprise.data["sons"][-1]["intensite"], 2)
            self.assertEqual(reprise.objets[id]["lieu"], "antichambre_sol")

    def test_source_improvisee_consomme_son_combustible_et_eclaire(self):
        m = sans_budget(nouveau_monde())
        installer(m)
        m, _, etablis = preparer_faits(m, {"ajouts": [{
            "type": "objet", "ancrage": "antichambre_sol",
            "nom": "petite lampe à huile", "genre": "f",
            "texte": "Sa mèche plonge dans une réserve d'huile.",
            "materiau": "cuivre et verre", "masse": 0.4, "mobile": True,
            "relation": "pose", "capacites": [{"nature": "lumiere", "niveau": 2,
                                                 "combustible": 3}]}]})
        id = etablis[0]["objet"]
        self.assertFalse(m.objets[id]["allume"])
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition("prendre", id)))
        m.objets["lanterne"]["allume"] = False
        m.objets["brasero"]["allume"] = False
        self.assertEqual(m.contexte()["perception"]["niveau"], 0)
        moteur.executer(moteur.preparer(proposition("allumer", id)))
        self.assertEqual(m.objets[id]["combustible"], 2)
        self.assertEqual(m.contexte()["perception"]["niveau"], 2)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "lampe.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
            self.assertTrue(reprise.objets[id]["allume"])
            self.assertEqual(reprise.contexte()["perception"]["niveau"], 2)
            moteur = Moteur(reprise)
            moteur.executer(moteur.preparer(proposition("attendre")))
            reprise.sauver(chemin)
            epuisee = Monde.charger(chemin)
        self.assertFalse(epuisee.objets[id]["allume"])
        self.assertEqual(epuisee.objets[id]["combustible"], 0)
        self.assertEqual(epuisee.contexte()["perception"]["niveau"], 0)

    def test_capacite_invalide_refusee_sans_mutation(self):
        m = nouveau_monde()
        avant = set(m.objets)
        base = {"type": "objet", "ancrage": "antichambre_sol",
                "nom": "clochette de fer", "genre": "f", "texte": "Le fer est poli.",
                "materiau": "fer", "masse": 0.2, "mobile": True,
                "relation": "pose"}
        for capacites in ([{"nature": "son", "intensite": 5}],
                          [{"nature": "lumiere", "niveau": 2, "combustible": 0}],
                          [{"nature": "son", "intensite": 2}] * 2):
            with self.subTest(capacites=capacites), self.assertRaises(ErreurMonde):
                preparer_faits(m, {"ajouts": [{**base, "capacites": capacites}]})
            self.assertEqual(set(m.objets), avant)
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(analyser(m, "sonner marteau"))

    def test_outils_improvises_couper_levier_allumage_apres_rechargement(self):
        m = sans_budget(nouveau_monde())
        ajouts = [
            {"type": "objet", "ancrage": "antichambre_sol",
             "nom": "barre à tranchant", "genre": "f",
             "texte": "Une arête d'acier tranche le bois ; son corps rigide fait levier.",
             "materiau": "acier", "masse": 1.2, "mobile": True, "relation": "pose",
             "capacites": [{"nature": "outil", "usages": ["couper", "levier"],
                            "puissance": 2}]},
            {"type": "objet", "ancrage": "antichambre_sol",
             "nom": "percuteur à silex", "genre": "m",
             "texte": "Le silex produit des étincelles pour allumer une mèche.",
             "materiau": "silex", "masse": 0.2, "mobile": True, "relation": "pose",
             "capacites": [{"nature": "outil", "usages": ["allumage"],
                            "puissance": 0}]},
        ]
        m, rendus, etablis = preparer_faits(m, {"ajouts": ajouts})
        self.assertIn("barre à tranchant", rendus)
        lame, silex = [e["objet"] for e in etablis]
        moteur = Moteur(m)
        for id in (lame, silex):
            moteur.executer(moteur.preparer(proposition("prendre", id)))
        self.assertIn("couper", decrire(m, lame, detail=True))
        self.assertIn("allumer une source", decrire(m, silex, detail=True))
        plan = moteur.preparer(proposition("frapper", "porte", outil=lame))
        self.assertEqual(plan.effets[0][0], "endommager")
        extraction = moteur.preparer(proposition("detacher", "axe_haut", outil=lame,
                                                 methode="levier", difficulte=12))
        self.assertEqual(extraction.plans[0].effets[0][0], "liberer")
        usure = improviser("Éprouver le tranchant", issue("Le tranchant s'émousse.",
                         [effet("user", lame, valeur=1)]), issue("Le geste s'arrête."),
                         outil=lame, approche="manipulation", stat="DEX", difficulte=10)
        with patch.object(Monde, "d20", return_value=20):
            moteur.executer(moteur.preparer(usure))
        self.assertEqual(m.objets[lame]["integrite"], 9)
        m.objets["lanterne"]["allume"] = False
        moteur.executer(moteur.preparer(proposition("allumer", "lanterne", outil=silex)))
        self.assertTrue(m.objets["lanterne"]["allume"])
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "outils.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
            self.assertEqual(reprise.objets[lame]["usages"], ["couper", "levier"])
            self.assertEqual(reprise.objets[silex]["usages"], ["allumage"])
            self.assertTrue(reprise.objets["lanterne"]["allume"])
            self.assertEqual(reprise.objets[lame]["lieu"], "joueur")
            self.assertEqual(reprise.objets[silex]["lieu"], "joueur")
            self.assertIn("levier robuste", decrire(reprise, lame, detail=True))
            self.assertEqual(Moteur(reprise).preparer(proposition("frapper", "porte", outil=lame)).effets[0][0], "endommager")

    def test_outil_improvise_incoherent_refuse_sans_mutation(self):
        m = nouveau_monde()
        base = {"type": "objet", "ancrage": "antichambre_sol", "nom": "outil",
                "genre": "m", "texte": "Un outil ordinaire.", "materiau": "fer",
                "masse": 1, "mobile": True, "relation": "pose"}
        capacites = [
            [{"nature": "outil", "usages": ["couper", "couper"], "puissance": 2}],
            [{"nature": "outil", "usages": ["levier"], "puissance": 0}],
            [{"nature": "outil", "usages": ["ouvrir_tout"], "puissance": 3}],
        ]
        for capacite in capacites:
            with self.subTest(capacite=capacite), self.assertRaises(ErreurMonde):
                preparer_faits(m, {"ajouts": [{**base, "capacites": capacite}]})
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, {"ajouts": [{**base, "mobile": False,
                                           "capacites": [{"nature": "outil", "usages": ["levier"],
                                                          "puissance": 2}]}]})
        self.assertFalse(any(o.get("scene_detail") for o in m.objets.values()))

    def test_cloche_du_scenario_emploie_la_meme_capacite_sonore(self):
        m = nouveau_defi(depart="fixe")
        installer(m)
        m.joueur.update(salle="chambre_cloche", position=[1, 3])
        self.assertEqual(m.objets["cloche"]["sonorite"], 3)
        plan = Moteur(m).preparer(sequence(etape("emettre_son", "cloche")))
        texte = Moteur(m).executer(plan)
        self.assertIn("cloche d'alarme", texte)
        self.assertEqual(m.data["sons"][-1]["objet"], "cloche")
        self.assertEqual(m.data["sons"][-1]["intensite"], 3)


if __name__ == "__main__":
    unittest.main()
