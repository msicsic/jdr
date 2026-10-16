import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.commandes import analyser, est_question
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.perception import eclairage
from donjon.rendu import decrire_perception, fiche, regarder


class EclairageTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        self.moteur = Moteur(self.m)

    def agir(self, commande):
        return self.moteur.executer(self.moteur.preparer(analyser(self.m, commande)))

    def obscurcir(self):
        self.m.objets["brasero"]["allume"] = False
        self.agir("éteindre lanterne")

    def test_piece_sans_fenetre_eclairee_par_source_reelle(self):
        texte = decrire_perception(self.m)
        self.assertIn("pas de fenêtre", texte)
        self.assertIn("Il ne fait pas noir", texte)
        self.assertIn("La lanterne, que vous portez", texte)
        self.assertIn("La torche est éteinte", texte)
        self.assertEqual(eclairage(self.m)["niveau"], 2)

    def test_eteindre_source_locale_laisse_lueur_de_piece_voisine(self):
        self.agir("éteindre lanterne")
        self.assertEqual(eclairage(self.m)["niveau"], 1)
        self.assertIn("ouest", decrire_perception(self.m))
        self.assertNotIn("brasero", decrire_perception(self.m).lower())
        self.assertIn("pas ses détails", self.agir("examiner gravure"))
        with self.assertRaises(ErreurMonde):
            self.agir("lire gravure")
        contexte = self.m.contexte()
        gravure = next(o for o in contexte["objets_perceptibles"] if o["id"] == "gravure")
        self.assertNotIn("motif", gravure)
        self.assertNotIn("inscription", gravure)

    def test_noir_masque_objets_et_nouveaux_secrets(self):
        self.obscurcir()
        self.assertEqual(eclairage(self.m)["niveau"], 0)
        texte = regarder(self.m)
        self.assertIn("entièrement noir", texte)
        self.assertNotIn("clé du veilleur", texte.lower())
        self.assertNotIn("gravure du chevalier", texte.lower())
        self.assertFalse(self.m.visible("porte"))
        self.assertNotIn('"id": "anneau"', json.dumps(self.m.contexte()))
        self.assertNotIn("chevalier", json.dumps(self.m.contexte()))
        with self.assertRaises(ErreurMonde):
            self.agir("examiner gravure")

    def test_affaires_accessibles_au_toucher_et_rallumage_dans_noir(self):
        self.obscurcir()
        self.assertIn("non visible", fiche(self.m))
        self.assertIn("matériau", self.agir("toucher couteau"))
        with self.assertRaises(ErreurMonde):
            self.agir("examiner couteau")
        self.agir("allumer lanterne")
        self.assertEqual(eclairage(self.m)["niveau"], 2)
        self.assertIn("chevalier", self.agir("examiner gravure"))

    def test_porte_fermee_bloque_lumiere(self):
        self.m.objets["lanterne"]["lieu"] = "crypte"
        self.m.objets["brasero"]["allume"] = False
        self.assertEqual(eclairage(self.m)["niveau"], 0)
        self.m.objets["porte"]["ouverte"] = True
        self.assertEqual(eclairage(self.m)["niveau"], 1)
        self.assertIn("nord", decrire_perception(self.m))

    def test_contenant_opaque_bloque_source(self):
        self.m.objets["lanterne"]["lieu"] = "coffre"
        self.m.objets["brasero"]["allume"] = False
        self.m.joueur["salle"] = "crypte"
        self.assertEqual(eclairage(self.m)["niveau"], 0)
        self.m.objets["coffre"]["ouverte"] = True
        self.assertEqual(eclairage(self.m)["niveau"], 2)

    def test_combustible_passe_avec_temps_pas_avec_question(self):
        avant = copy.deepcopy(self.m.data)
        plan = self.moteur.preparer(proposition("observer", "lumiere"))
        self.assertIn("Il ne fait pas noir", self.moteur.executer(plan))
        self.assertEqual(self.m.data, avant)
        self.m.objets["lanterne"]["combustible"] = 2
        self.m.objets["brasero"]["allume"] = False
        texte = self.agir("attendre")
        self.assertIn("La lanterne s'éteint", texte)
        self.assertEqual(eclairage(self.m)["niveau"], 0)
        with self.assertRaises(ErreurMonde):
            self.agir("allumer lanterne")

    def test_source_detruite_ne_produit_plus_lumiere(self):
        self.agir("ouest")
        self.agir("acheter marteau")
        self.m.objets["brasero"]["integrite"] = 1
        with patch.object(Monde, "d20", return_value=20):
            self.agir("frapper brasero avec marteau")
        self.assertFalse(self.m.objets["brasero"]["allume"])
        self.m.verifier()

    def test_sauvegarde_ne_rallume_pas_lanterne(self):
        self.agir("éteindre lanterne")
        copie = Monde(copy.deepcopy(self.m.data))
        self.assertFalse(copie.objets["lanterne"]["allume"])
        self.assertEqual(copie.data, self.m.data)

    def test_rechargement_ne_recree_pas_une_source_supprimee(self):
        data = copy.deepcopy(self.m.data)
        del data["objets"]["lanterne"]
        data["joueur"]["or"] = 3
        data["objets"]["porte"]["ouverte"] = True
        copie = Monde(data)
        self.assertEqual(copie.joueur["or"], 3)
        self.assertTrue(copie.objets["porte"]["ouverte"])
        self.assertNotIn("lanterne", copie.objets)


class QuestionsConsoleTests(unittest.TestCase):
    def test_formes_interrogatives_sans_point_ne_declenchent_pas_d_action(self):
        monde = nouveau_monde()
        for phrase in ("Où est la clé", "Qui tient la clé", "Combien de combustible reste",
                       "Puis-je éteindre la lanterne", "Peut-on éteindre la lanterne",
                       "je mesure combien"):
            with self.subTest(phrase=phrase):
                self.assertTrue(est_question(phrase))
                self.assertIsNone(analyser(monde, phrase))
        self.assertFalse(est_question("je prends la clé"))
        self.assertFalse(est_question("ouvrir la porte"))
        for phrase in ("Où est la clé", "Peut-on éteindre la lanterne"):
            with self.subTest(console=phrase):
                texte, reprise, _ = self.lancer([phrase], {
                    "mode": "action", "texte": "", "faits": [],
                    "proposition": proposition("eteindre", "lanterne")})
                self.assertIn("Aucune action n'a été appliquée", texte)
                self.assertTrue(reprise.objets["lanterne"]["allume"])
                self.assertEqual(reprise.data["revision"], 0)

    def lancer(self, commandes, p=None, panne=None):
        import jeu
        if isinstance(p, dict) and p.get("mode") == "dialogue":
            p = {**p, "_texte_moteur": True}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with patch("builtins.input", side_effect=commandes + ["quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "echanger", return_value=p, side_effect=panne) as mj:
                    options = ["--save", str(chemin), "--connexion", "api"]
                    if p is None and panne is None:
                        options.append("--offline")
                    jeu.main(options)
                    texte = sortie.getvalue()
            return texte, Monde.charger(chemin), mj.call_count

    def test_question_exacte_joueur_hors_ligne(self):
        texte, m, appels = self.lancer(["une sale sans fenetres, il fait tout noir ?"])
        self.assertIn("je ne peux pas interpréter cette question", texte)
        self.assertNotIn("Voici les faits observables", texte)
        self.assertEqual(appels, 0)
        self.assertEqual(m.data["revision"], 0)
        self.assertEqual(m.data["minutes"], 0)

    def test_question_mj_repond_immediatement_sans_tenter(self):
        texte, m, appels = self.lancer(["D'où vient la lumière ?"], {
            "mode": "dialogue", "texte": "Ta lanterne éclaire la pièce.", "faits": ["perception"], "proposition": None})
        self.assertEqual(appels, 1)
        self.assertNotIn("« tenter » pour agir", texte)
        self.assertEqual(m.data["revision"], 0)

    def test_question_nautorise_pas_action_du_modele(self):
        texte, m, _ = self.lancer(["Puis-je éteindre ma lanterne ?"], {
            "mode": "action", "texte": "", "faits": [], "proposition": proposition("eteindre", "lanterne")})
        self.assertIn("Aucune action n'a été appliquée", texte)
        self.assertTrue(m.objets["lanterne"]["allume"])

    def test_question_api_indisponible_sans_reponse_hors_sujet(self):
        texte, m, _ = self.lancer(["Il fait noir ?"], panne=ErreurMonde("MJ indisponible : 401"))
        self.assertNotIn("Faits observables", texte)
        self.assertIn("MJ indisponible : 401", texte)
        self.assertEqual(m.data["revision"], 0)

    def test_question_arrivee_est_un_dialogue_memorise(self):
        reponse = "Tu as suivi Gorm depuis son échoppe."
        texte, m, _ = self.lancer(["mais comment je suis arrivé ici ?"], {
            "mode": "dialogue", "texte": reponse, "faits": ["scenario"], "proposition": None})
        self.assertIn(reponse, texte)
        self.assertNotIn("ne sont pas encore définis", texte)
        self.assertEqual(m.data["conversation"][-1]["reponse"], reponse)
        self.assertEqual(m.data["revision"], 0)

    def test_contexte_utilise_dernier_deplacement_sans_inventer_passe(self):
        m = nouveau_monde()
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(analyser(m, "ouest")))
        avant = copy.deepcopy(m.data)
        texte = moteur.executer(moteur.preparer(analyser(m, "contexte")))
        self.assertIn("Echoppe", texte)
        self.assertIn("Dernier déplacement enregistré", texte)
        self.assertEqual(avant, m.data)


if __name__ == "__main__":
    unittest.main()
