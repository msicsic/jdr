import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.capacites_objet import proprietes
from donjon.capacites_objet import absence as absence_capacite, statut as statut_capacite
from donjon.commandes import analyser
from donjon.mj import MJOpenAI
from donjon.faits_locaux import preparer_faits
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, QualificationRequise, proposition
from donjon.rendu import decrire
from tests.support import simuler_couverture
from donjon.transactions import du_type


PORTEE_QUALIFICATION = {"descriptions": [], "usages": [
    {"perception_requise": False, "indice": False, "motif": ""}]}


class CoupeTests(unittest.TestCase):
    def setUp(self):
        simuler_couverture(self)

    def test_scie_moins_puissante_que_hache_peut_entamer_apres_arbitrage(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "acier.json"
            depart = nouveau_atelier()
            depart.objets["plaque"] = objet(
                "plaque", "plaque d'acier", "materiau", "cour", genre="f",
                materiau="acier doux", masse=12.6, mobile=False,
                description_visuelle="Plaque d'acier doux de 2 mm, fixée au sol.")
            depart.objets["plaque"]["position"] = list(depart.joueur["position"])
            depart.objets["scie"] = objet(
                "scie", "scie à métaux", "outil", "joueur", genre="f",
                materiau="acier", masse=0.6, usages=["couper"], puissance=2,
                description_visuelle="Lame fine adaptée au sciage de l'acier doux.")
            depart, _, _ = preparer_faits(depart, {"ajouts": [{
                "type": "qualification", "ancrage": "plaque", "moyen": "hache",
                "coupe_possible": False}]})
            depart.sauver(chemin)
            action = {"mode": "action", "texte": "", "faits": [],
                      "proposition": proposition("couper", "plaque", outil="scie")}
            jugement = {"mode": "etablir_faits", "texte": "", "faits": [],
                        "proposition": {"ajouts": [{"type": "qualification",
                            "ancrage": "la plaque d'acier", "moyen": "scie à métaux",
                            "coupe_possible": True}]}}
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      action, jugement, PORTEE_QUALIFICATION, {"jugements": [{"compatible": True, "motif": ""}]},
                      action]) as appel,
                  patch.object(Monde, "d20", return_value=20),
                  patch("builtins.input", side_effect=[
                      "je coupe la plaque d'acier avec la scie à métaux", "tenter",
                      "examiner plaque d'acier", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--recit-moteur", "--console", "--atelier", "--save",
                                           str(chemin), "--connexion", "api"]), 0)
            self.assertEqual(appel.call_count, 5)
            self.assertEqual(appel.call_args_list[3].args[1]["qualifications"][0]
                             ["moyen"]["id"], "scie")
            fin = Monde.charger(chemin)
            self.assertLess(fin.objets["scie"]["puissance"], fin.objets["hache"]["puissance"])
            self.assertNotIn("seuil_coupe", fin.objets["plaque"])
            self.assertLess(fin.objets["plaque"]["integrite"], 10)
            self.assertEqual(statut_capacite(fin.objets["plaque"], "tranchable",
                                            fin.objets["scie"]), "etablie")
            self.assertIn("peut être entamée avec la scie", sortie.getvalue())
            self.assertIn("peut être entamée avec la scie", decrire(fin, "plaque", detail=True))
            self.assertEqual(Moteur(fin).preparer(
                proposition("couper", "plaque", outil="scie")).effets[0][0], "endommager")
            fin.objets["scie"]["integrite"] -= 1
            fin.sauver(chemin)
            usee = Monde.charger(chemin)
            self.assertEqual(statut_capacite(usee.objets["plaque"], "tranchable",
                                            usee.objets["scie"]), "etablie")
            usee.objets["scie"]["integrite"] = 0
            usee.sauver(chemin)
            brisee = Monde.charger(chemin)
            self.assertEqual(statut_capacite(brisee.objets["plaque"], "tranchable",
                                            brisee.objets["scie"]), "inconnue")
            self.assertIn("état antérieur", decrire(brisee, "plaque", detail=True))

    def test_moyen_plus_puissant_rouvre_la_qualification_apres_rechargement(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "atelier.json"
            depart = nouveau_atelier()
            depart.objets["plaque"] = objet("plaque", "plaque d'acier", "materiau", "cour",
                                            genre="f", materiau="acier doux", masse=12.6,
                                            mobile=False,
                                            description_visuelle="Plaque homogène de 2 mm d'épaisseur, fixée au sol.")
            depart.objets["plaque"]["position"] = list(depart.joueur["position"])
            depart.objets["scie"] = objet("scie", "scie à métaux", "outil", "joueur",
                                          genre="f", materiau="acier", masse=2,
                                          usages=["couper"], puissance=5,
                                          description_visuelle="Lame adaptée à l'acier doux.")
            depart.objets["lame"] = objet("lame", "petite lame", "outil", "joueur",
                                          genre="f", materiau="acier", masse=0.2,
                                          usages=["couper"], puissance=2)
            depart, _, _ = preparer_faits(depart, {"ajouts": [{
                "type": "qualification", "ancrage": "plaque",
                "moyen": "hache", "coupe_possible": False}]})
            depart.sauver(chemin)
            reprise = Monde.charger(chemin)
            self.assertEqual(statut_capacite(reprise.objets["plaque"], "tranchable",
                                            reprise.objets["hache"]), "ecartee")
            self.assertEqual(statut_capacite(reprise.objets["plaque"], "tranchable",
                                            reprise.objets["lame"]), "inconnue")
            self.assertEqual(statut_capacite(reprise.objets["plaque"], "tranchable",
                                            reprise.objets["scie"]), "inconnue")
            with self.assertRaises(QualificationRequise):
                Moteur(reprise).preparer(proposition("couper", "plaque", outil="scie"))
            action = {"mode": "action", "texte": "", "faits": [],
                      "proposition": proposition("couper", "plaque", outil="scie")}
            qualification = {"mode": "etablir_faits", "texte": "", "faits": [],
                             "proposition": {"ajouts": [{"type": "qualification",
                                 "ancrage": "plaque", "moyen": "scie",
                                 "coupe_possible": True}]}}
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      action, qualification, PORTEE_QUALIFICATION, {"jugements": [{"compatible": True,
                                                               "motif": ""}]}, action]),
                  patch.object(Monde, "d20", return_value=20),
                  patch("builtins.input", side_effect=[
                      "couper plaque d'acier avec scie à métaux", "tenter", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--recit-moteur", "--console", "--atelier", "--save",
                                           str(chemin), "--connexion", "api"]), 0)
            fin = Monde.charger(chemin)
            self.assertNotIn("seuil_coupe", fin.objets["plaque"])
            self.assertEqual(statut_capacite(fin.objets["plaque"], "tranchable",
                                            fin.objets["scie"]), "etablie")
            self.assertLess(fin.objets["plaque"]["integrite"], 10)
            self.assertIn("Entailler", sortie.getvalue())
            self.assertIn("résiste à la hache", decrire(fin, "plaque", detail=True))
            self.assertIn("état antérieur", decrire(fin, "plaque", detail=True))
            self.assertIn("peut être entamée avec la scie", decrire(fin, "plaque", detail=True))
            with self.assertRaises(QualificationRequise):
                Moteur(fin).preparer(proposition("couper", "plaque", outil="lame"))
            with self.assertRaises(QualificationRequise):
                Moteur(fin).preparer(proposition("couper", "plaque", outil="hache"))

    def test_capacite_ecartee_sur_pierre_reste_vraie_apres_rechargement(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "atelier.json"
            depart = nouveau_atelier()
            depart.objets["dalle"] = objet("dalle", "dalle de granit", "materiau", "cour",
                                            genre="f", materiau="granit", masse=52,
                                            mobile=False,
                                            description_visuelle="Granit massif de 8 cm d'épaisseur, fixé au sol.")
            depart.sauver(chemin)
            cible = "dalle"
            phrase = "La dalle de granit résiste à la hache."
            action = {"mode": "action", "texte": "", "faits": [],
                      "proposition": proposition("couper", cible, outil="hache")}
            exclusion = {"mode": "etablir_faits", "texte": "", "faits": [],
                         "proposition": {"ajouts": [{"type": "qualification",
                             "ancrage": "la dalle de granit", "moyen": "la hache",
                             "coupe_possible": False}]}}
            revue = {"jugements": [{"compatible": True,
                                     "motif": "La dalle résiste à cette hache."}]}
            explication = {"mode": "dialogue", "texte": phrase,
                           "faits": ["attestations"], "proposition": None}
            audit = {"segments": [{"portee_mecanique": "aucune", "indice": 0, "verdict": "mecanique",
                                   "sources": ["attestations"], "locuteur": "",
                                   "citation": "", "entites": [], "comptes": [], "motif": ""}]}
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut",
                               side_effect=[action, exclusion, PORTEE_QUALIFICATION, revue, action,
                                            explication, audit]) as appel,
                  patch("builtins.input", side_effect=[
                      "couper dalle de granit avec hache", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--atelier", "--save",
                                           str(chemin), "--connexion", "api"]), 0)
            self.assertEqual(appel.call_count, 6)  # la résistance est un constat exact du moteur
            self.assertEqual(appel.call_args_list[3].args[1]["qualifications"][0]
                             ["moyen"]["id"], "hache")
            self.assertIn(phrase, sortie.getvalue())
            reprise = Monde.charger(chemin)
            self.assertEqual(statut_capacite(reprise.objets[cible], "tranchable",
                                            reprise.objets["hache"]), "ecartee")
            self.assertEqual(reprise.objets[cible]["integrite"], 10)
            self.assertIn(phrase, decrire(reprise, cible, detail=True))
            with self.assertRaisesRegex(ErreurMonde, "résiste à la hache"):
                Moteur(reprise).preparer(proposition("couper", cible, outil="hache"))
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut",
                               side_effect=AssertionError("Luna rappelée inutilement")) as appel,
                  patch("builtins.input", side_effect=[
                      "couper dalle de granit avec hache", "examiner dalle de granit", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--atelier", "--save",
                                           str(chemin), "--connexion", "api"]), 0)
            self.assertEqual(appel.call_count, 0)
            self.assertIn(phrase, sortie.getvalue())
            self.assertEqual(Monde.charger(chemin).objets[cible]["constats_capacites"][0]
                             ["puissance_observee"], reprise.objets["hache"]["puissance"])
            reprise.objets["hache"]["integrite"] -= 1
            reprise.sauver(chemin)
            hache_changee = Monde.charger(chemin)
            self.assertEqual(statut_capacite(hache_changee.objets[cible], "tranchable",
                                            hache_changee.objets["hache"]), "inconnue")
            self.assertIn("état antérieur", decrire(hache_changee, cible, detail=True))
            with self.assertRaises(QualificationRequise):
                Moteur(hache_changee).preparer(proposition("couper", cible, outil="hache"))

    def test_qualification_survit_a_une_reponse_finale_mal_formee(self):
        m = nouveau_atelier()
        m.objets["dalle"] = objet("dalle", "dalle de granit", "materiau", "cour",
                                   genre="f", materiau="granit", masse=52,
                                   mobile=False,
                                   description_visuelle="Granit massif de 8 cm d'épaisseur, fixé au sol.")
        action = {"mode": "action", "texte": "", "faits": [],
                  "proposition": proposition("couper", "dalle", outil="hache")}
        exclusion = {"mode": "etablir_faits", "texte": "", "faits": [],
                     "proposition": {"ajouts": [{"type": "qualification",
                         "ancrage": "dalle", "moyen": "hache",
                         "coupe_possible": False}]}}
        invalide = {"mode": "action",
                    "texte": "La dalle de granit résiste à la hache.",
                    "faits": [], "proposition": {}}
        # La forme invalide reçoit sa correction propre avant le repli commun.
        with patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                action, exclusion, PORTEE_QUALIFICATION, {"jugements": [{"compatible": True,
                    "motif": "Le granit résiste aux outils connus."}]}, invalide, invalide]):
            reponse = MJOpenAI().echanger(m, "couper dalle de granit avec hache")
        self.assertEqual(reponse["mode"], "dialogue")
        self.assertTrue(reponse["_texte_moteur"])
        self.assertIn("résiste à la hache", reponse["texte"])
        travail, _, _ = preparer_faits(m, du_type(reponse, "faits")["proposition"],
                                        du_type(reponse, "faits")["revision"])
        self.assertEqual(statut_capacite(travail.objets["dalle"], "tranchable",
                                        travail.objets["hache"]), "ecartee")

    def test_qualification_objet_existant_reprend_la_meme_action_et_persiste(self):
        for cible, tenacite in (("perche_1", 10), ("perche_2", 3)):
            with self.subTest(cible=cible), tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / "atelier.json"
                depart = nouveau_atelier()
                depart.objets[cible].pop("seuil_coupe")
                depart.objets[cible]["position"] = list(depart.joueur["position"])
                if cible == "perche_2":
                    depart.objets[cible]["integrite"] = tenacite
                    depart.objets[cible]["maximum"] = tenacite
                with self.assertRaises(QualificationRequise):
                    Moteur(depart).preparer(proposition("couper", cible, outil="hache"))
                depart.sauver(chemin)
                action = {"mode": "action", "texte": "", "faits": [],
                          "proposition": proposition("couper", cible, outil="hache")}
                qualification = {"mode": "etablir_faits", "texte": "", "faits": [],
                                 "proposition": {"ajouts": [{"type": "qualification",
                                     "ancrage": cible, "moyen": "hache",
                                     "coupe_possible": True}]}}
                revue = {"jugements": [{"compatible": True, "motif": ""}]}
                interface = Mock() if cible == "perche_2" else None
                if interface:
                    interface.lire.side_effect = [
                        f"couper {depart.objets[cible]['nom']} avec hache", "tenter", "quitter"]
                with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                      patch.object(MJOpenAI, "_appeler_brut",
                                   side_effect=[action, qualification, PORTEE_QUALIFICATION, revue, action]),
                      patch.object(Monde, "d20", return_value=20),
                      patch("builtins.input", side_effect=[
                          f"couper {depart.objets[cible]['nom']} avec hache",
                          "tenter", "quitter"]),
                      patch("sys.stdout", io.StringIO()) as sortie):
                    self.assertEqual(jeu.main(["--recit-moteur", "--console", "--atelier", "--save",
                                               str(chemin), "--connexion", "api"],
                                               interface=interface), 0)
                affichage = ("\n".join(str(a.args[0]) for a in interface.ecrire.call_args_list)
                             if interface else sortie.getvalue())
                reprise = Monde.charger(chemin)
                self.assertNotIn("seuil_coupe", reprise.objets[cible])
                if reprise.objets[cible]["integrite"]:
                    self.assertEqual(statut_capacite(reprise.objets[cible], "tranchable",
                                                    reprise.objets["hache"]), "etablie")
                self.assertEqual(reprise.objets[cible]["maximum"], tenacite)
                self.assertLess(reprise.objets[cible]["integrite"], tenacite)
                self.assertIn("Entailler", affichage)
                self.assertIn("brisée" if cible == "perche_2" else "abîmée", affichage)

    def test_qualification_ne_reecrit_pas_une_propriete_etablie(self):
        m = nouveau_atelier()
        p = {"ajouts": [{"type": "qualification", "ancrage": "perche_1",
                         "capacites": [{"nature": "tranchable", "seuil": 1,
                                        "tenacite": 2}]}]}
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, p)
        self.assertEqual(m.data, avant)
        m.objets["perche_1"].pop("seuil_coupe")
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, p)
        m.objets["perche_1"]["integrite"] -= 1
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, p)

    def test_contre_revue_refuse_une_capacite_incoherente(self):
        propositions = ({"moyen": "hache", "coupe_possible": True},
                        {"moyen": "hache", "coupe_possible": False})
        for choix in propositions:
            with self.subTest(choix=choix):
                m = nouveau_atelier()
                m.objets["perche_1"].pop("seuil_coupe")
                avant = copy.deepcopy(m.data)
                demande = {"mode": "etablir_faits", "texte": "", "faits": [],
                           "proposition": {"ajouts": [{"type": "qualification",
                               "ancrage": "perche_1", **choix}]}}
                refus = {"jugements": [{"compatible": False,
                         "motif": "La matière et l'état décrit ne permettent pas cette conclusion."}]}
                with patch.object(MJOpenAI, "_appeler_brut",
                                  side_effect=[demande, PORTEE_QUALIFICATION, refus] * 3):
                    reponse = MJOpenAI().echanger(m, "Je coupe la perche avec la hache")
                self.assertEqual(reponse["mode"], "dialogue")
                self.assertIsNone(du_type(reponse, "faits"))
                self.assertEqual(m.data, avant)

    def test_objet_tranchable_cree_par_mj_coupe_en_console_et_persiste(self):
        ajout = {"type": "objet", "ancrage": "antichambre_sol",
                 "nom": "cordelette de chanvre", "genre": "f",
                 "texte": "Ses fibres souples peuvent être tranchées par une lame.",
                 "materiau": "chanvre", "masse": 0.1, "mobile": True,
                 "relation": "pose", "capacites": [{"nature": "tranchable", "seuil": 1,
                                                  "tenacite": 2}]}
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [ajout]}}
        rapport = {"usages": [{"perception_requise": False, "indice": False, "motif": ""}], "descriptions": [{
            "representation": representation, "mobilite": [], "placement": "aucun",
            "impact_scenario": "aucun", "capacites": ["tranchable"],
            "fragments": [{"texte": texte, "portee": "sujet", "preuve": "", "motif": ""}]}
            for representation, texte in (("objet", ajout["nom"]), ("aspect", ajout["texte"]))]}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[reponse, rapport]),
                  patch("builtins.input", side_effect=[
                      "mj Y a-t-il une cordelette ici ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            self.assertIn("cordelette de chanvre", sortie.getvalue())
            cree = Monde.charger(chemin)
            id = cree.trouver("cordelette de chanvre")
            self.assertEqual(cree.objets[id]["seuil_coupe"], 1)
            self.assertEqual(analyser(cree, "couper cordelette de chanvre avec couteau")["action"], "couper")
            with (patch.object(Monde, "d20", return_value=20),
                  patch("builtins.input", side_effect=[
                      "couper cordelette de chanvre avec couteau", "tenter", "examiner cordelette de chanvre", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            reprise = Monde.charger(chemin)
            self.assertEqual(reprise.objets[id]["integrite"], 0)
            self.assertIn("brisée", sortie.getvalue())
            self.assertIn("brisée", decrire(reprise, id, detail=True))
            self.assertEqual(reprise.objets[id]["lieu"], "antichambre_sol")

    def test_perche_non_chene_et_cible_resistante_suivent_le_meme_seuil(self):
        m = nouveau_atelier()
        self.assertEqual(m.objets["perche_1"]["materiau"], "bois")
        moteur = Moteur(m)
        plan = moteur.preparer(proposition("couper", "perche_1", outil="hache"))
        with patch.object(Monde, "d20", return_value=20):
            resultat = moteur.executer(plan)
        self.assertIn("est abîmée", resultat)
        self.assertLess(m.objets["perche_1"]["integrite"], 10)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "atelier.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
            self.assertIn("abîmée", decrire(reprise, "perche_1", detail=True))
            reprise.objets["perche_2"]["seuil_coupe"] = 4
            avant = copy.deepcopy(reprise.data)
            with self.assertRaises(ErreurMonde):
                Moteur(reprise).preparer(proposition("couper", "perche_2", outil="hache"))
            self.assertEqual(reprise.data, avant)

        crypte = nouveau_monde()
        crypte.joueur["salle"] = "crypte"
        with self.assertRaises(ErreurMonde):
            Moteur(crypte).preparer(proposition("couper", "coffre", outil="couteau"))
        with self.assertRaisesRegex(ErreurMonde, "outil de coupe"):
            Moteur(crypte).preparer(proposition("couper", "coffre"))

    def test_seuil_invalide_refuse(self):
        for seuil in (0, 8, True, "2"):
            with self.subTest(seuil=seuil), self.assertRaises(ErreurMonde):
                proprietes([{"nature": "tranchable", "seuil": seuil, "tenacite": 2}], 0.2)
        for tenacite in (0, 21, True, "2"):
            with self.subTest(tenacite=tenacite), self.assertRaises(ErreurMonde):
                proprietes([{"nature": "tranchable", "seuil": 2,
                             "tenacite": tenacite}], 0.2)


if __name__ == "__main__":
    unittest.main()
