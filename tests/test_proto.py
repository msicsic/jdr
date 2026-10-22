import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from donjon.commandes import analyser
from donjon.config import charger_env
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import carte, decrire, regarder


class MondeEtReglesTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        self.moteur = Moteur(self.m)

    def agir(self, commande, jet=20):
        plan = self.moteur.preparer(analyser(self.m, commande))
        with patch.object(Monde, "d20", return_value=jet):
            return self.moteur.executer(plan)

    def acheter(self, nom):
        self.agir("ouest")
        self.agir("acheter " + nom)
        self.agir("est")

    def ouvrir_porte(self):
        self.acheter("crochets")
        self.agir("crocheter serrure avec crochets")
        self.agir("ouvrir porte")

    def test_description_ne_revele_pas_tresor_ou_secret(self):
        contexte = json.dumps(self.m.contexte(), ensure_ascii=False)
        self.assertNotIn('"id": "anneau"', contexte)
        self.assertNotIn("La clé du veilleur ouvre", contexte)
        self.assertNotIn("anneau", regarder(self.m))
        self.assertFalse(self.m.visible("anneau"))
        self.assertNotIn("sens", next(o for o in self.m.contexte()["objets_perceptibles"] if o["id"] == "gravure"))

    def test_tous_les_objets_visibles_sont_examinables(self):
        for o in self.m.presents():
            self.assertEqual(self.m.trouver(o["id"]), o["id"])
            self.moteur.preparer(proposition("examiner", o["id"]))

    def test_examen_sans_jet_ni_temps(self):
        avant = (self.m.data["jets"], self.m.data["minutes"])
        texte = self.agir("examiner gravure")
        self.assertIn("chevalier", texte)
        self.assertEqual(avant, (self.m.data["jets"], self.m.data["minutes"]))

    def test_absence_de_teleportation_et_objets_distants(self):
        avant = copy.deepcopy(self.m.data)
        for p in (proposition("prendre", "anneau"), proposition("aller", "nord"),
                  proposition("examiner", "coffre"), proposition("acheter", "marteau")):
            with self.assertRaises(ErreurMonde):
                self.moteur.preparer(p)
        self.assertEqual(avant, self.m.data)

    def test_outil_non_possede_ou_casse_refuse(self):
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("detacher", "axe_haut", "pied_de_biche", "levier"))
        self.m.objets["couteau"]["integrite"] = 0
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("detacher", "axe_haut", "couteau", "levier"))

    def test_pas_de_porte_soulevee_au_couteau(self):
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("detacher", "porte", "couteau", "levier"))

    def test_difficulte_bornee_et_arbitrage_memorise(self):
        p = proposition("detacher", "axe_haut", "couteau", "levier", 1, "Trop facile")
        plan = self.moteur.preparer(p, "LLM")
        self.assertEqual(plan.dd, 17)
        with patch.object(Monde, "d20", return_value=2):
            self.moteur.executer(plan)
        p["difficulte"] = 22
        p["justification"] = "Nouvelle formulation"
        nouveau = self.moteur.preparer(p, "LLM")
        self.assertEqual(nouveau.dd, 17)
        self.assertEqual(nouveau.origine, "arbitrage mémorisé")
        self.assertTrue(self.m.objets["axe_haut"]["attache"])

    def test_echec_critique_abime_outil_sans_detacher_axe(self):
        self.agir("retirer axe supérieur avec couteau", jet=1)
        self.assertEqual(self.m.objets["couteau"]["integrite"], 2)
        self.assertTrue(self.m.objets["axe_haut"]["attache"])
        self.assertEqual(self.m.data["minutes"], 3)

    def test_deux_axes_et_porte_unique_depuis_deux_cotes(self):
        self.acheter("pied-de-biche")
        self.agir("retirer axe supérieur avec pied-de-biche")
        self.assertFalse(self.m.objets["porte"]["ouverte"])
        self.agir("retirer axe inférieur avec pied-de-biche")
        self.assertTrue(self.m.objets["porte"]["detachee"])
        self.agir("nord")
        self.assertIn("dégondé", self.agir("examiner porte"))
        self.assertIn("x", carte(self.m))
        with self.assertRaises(ErreurMonde):
            self.agir("fermer porte")

    def test_stabilisation_utilise_les_fixations_de_chaque_porte(self):
        self.m.objets["herse"] = objet("herse", "herse", "porte", "antichambre",
                                       ouverte=False, verrouillee=True, detachee=False,
                                       bloque_par=None, relie=[], fixations=["cheville"])
        self.m.objets["cheville"] = objet("cheville", "cheville", "fixation", "joueur",
                                          attache=False, mobile=True)
        self.moteur.executer(self.moteur.preparer(proposition("attendre")))
        self.assertTrue(self.m.objets["herse"]["detachee"])
        self.assertTrue(self.m.objets["herse"]["ouverte"])
        self.assertFalse(self.m.objets["herse"]["verrouillee"])

    def test_acces_aux_axes_depuis_un_seul_cote(self):
        self.ouvrir_porte()
        self.agir("nord")
        self.assertFalse(self.m.visible("axe_haut"))
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("detacher", "axe_haut", "couteau", "levier"))

    def test_cale_bloque_fermeture_et_est_recuperable(self):
        self.ouvrir_porte()
        self.acheter("marteau")
        self.agir("caler porte avec marteau")
        self.assertEqual(self.m.objets["marteau"]["lieu"], "porte")
        with self.assertRaises(ErreurMonde):
            self.agir("fermer porte")
        with self.assertRaises(ErreurMonde):
            self.agir("prendre marteau")
        self.agir("nord")
        self.agir("débloquer porte")
        self.assertEqual(self.m.objets["marteau"]["lieu"], "crypte")
        self.agir("prendre marteau")
        self.agir("fermer porte")
        self.assertFalse(self.m.objets["porte"]["ouverte"])

    def test_empreinte_persiste_apres_destruction_original(self):
        masse = self.m.charge()
        self.agir("copier gravure avec cire")
        self.assertAlmostEqual(masse, self.m.charge())
        self.m.objets["porte"]["integrite"] = 1
        self.agir("frapper porte avec couteau")
        self.assertIn("illisible", self.agir("examiner gravure"))
        self.assertIn("chevalier", self.agir("examiner empreinte"))
        with self.assertRaises(ErreurMonde):
            self.agir("lire gravure")
        self.assertIn("ouvre le coffre", self.agir("lire empreinte"))

    def test_pas_de_cire_infinie(self):
        self.agir("copier gravure avec cire")
        self.agir("copier gravure avec cire")
        with self.assertRaises(ErreurMonde):
            self.agir("copier gravure avec cire")
        self.assertEqual(self.m.objets["cire"]["charges"], 0)

    def test_lecture_revele_sens_uniquement_apres_succes(self):
        self.agir("lire gravure", jet=2)
        self.assertNotIn("sens", next(o for o in self.m.contexte()["objets_perceptibles"] if o["id"] == "gravure"))
        self.agir("lire gravure")
        self.assertIn("ouvre le coffre", self.agir("examiner gravure"))

    def test_achat_paye_une_fois_et_ne_duplique_pas(self):
        self.acheter("marteau")
        self.assertEqual(self.m.joueur["or"], 18)
        self.assertFalse(self.m.objets["marteau"]["en_vente"])
        avant = copy.deepcopy(self.m.data)
        with self.assertRaises(ErreurMonde):
            self.agir("acheter marteau")
        self.assertEqual(avant, self.m.data)

    def test_achat_sans_fonds_et_vol_refuses(self):
        self.agir("ouest")
        with self.assertRaises(ErreurMonde):
            self.agir("prendre marteau")
        self.m.joueur["or"] = 0
        with self.assertRaises(ErreurMonde):
            self.agir("acheter marteau")
        self.assertTrue(self.m.objets["marteau"]["en_vente"])

    def test_coffre_cache_anneau_et_mauvaise_cle_refusee(self):
        self.agir("prendre clé")
        with self.assertRaises(ErreurMonde):
            self.agir("ouvrir porte avec clé")
        self.ouvrir_porte()
        self.agir("nord")
        self.assertFalse(self.m.visible("anneau"))
        self.agir("ouvrir coffre avec clé")
        self.assertTrue(self.m.visible("anneau"))
        self.assertIn("OBJECTIF ATTEINT", self.agir("prendre anneau"))

    def test_destruction_contenant_libere_contenu(self):
        self.ouvrir_porte()
        self.acheter("marteau")
        self.agir("nord")
        self.m.objets["coffre"]["integrite"] = 1
        self.agir("frapper coffre avec marteau")
        self.assertEqual(self.m.objets["anneau"]["lieu"], "crypte")
        self.assertTrue(self.m.visible("anneau"))

    def test_critique_crochetage_bloque_serrure(self):
        self.acheter("crochets")
        self.agir("crocheter serrure avec crochets", jet=1)
        self.assertTrue(self.m.objets["serrure"]["bloquee"])
        with self.assertRaises(ErreurMonde):
            self.agir("crocheter porte avec crochets")

    def test_bruit_reaction_et_attente(self):
        self.agir("frapper porte avec couteau", jet=2)
        self.agir("frapper porte avec couteau", jet=2)
        self.assertEqual(self.m.objets["marchand"]["humeur"], "inquiet")
        self.agir("attendre")
        self.assertEqual(self.m.objets["marchand"]["humeur"], "calme")

    def test_plan_perime_refuse_et_effets_forges_ignores(self):
        plan = self.moteur.preparer(proposition("examiner", "porte"))
        plan.effets = [("deplacer", "anneau", "joueur")]
        self.moteur.executer(plan)
        self.assertEqual(self.m.objets["anneau"]["lieu"], "coffre")
        with self.assertRaises(ErreurMonde):
            self.moteur.executer(plan)

    def test_transaction_annulee_si_effet_echoue(self):
        plan = self.moteur.preparer(proposition("prendre", "cle"))
        avant = copy.deepcopy(self.m.data)
        with patch.object(Moteur, "_stabiliser", side_effect=ErreurMonde("échec simulé")):
            with self.assertRaises(ErreurMonde):
                self.moteur.executer(plan)
        self.assertEqual(avant, self.m.data)

    def test_sauvegarde_reprise_conserve_etat_arbitrages_et_des(self):
        self.agir("retirer axe supérieur avec couteau", jet=2)
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "partie.json"
            self.m.sauver(fichier)
            suite = Monde.charger(fichier)
            self.assertEqual(self.m.data, suite.data)
            self.assertEqual(self.m.d20(), suite.d20())
            self.assertTrue(suite.data["arbitrages"])

    def test_cycles_et_or_negatif_refuses(self):
        for modification in ("cycle", "or"):
            data = copy.deepcopy(self.m.data)
            if modification == "cycle":
                data["objets"]["porte"]["lieu"] = "gravure"
            else:
                data["joueur"]["or"] = -1
            with self.assertRaises(ErreurMonde):
                Monde(data)

    def test_objets_ambigus_et_phrase_libre(self):
        with self.assertRaises(ErreurMonde):
            self.m.trouver("axe")
        self.assertIsNone(analyser(self.m, "Je glisse mon couteau sous l'axe supérieur"))

    def test_proposition_malveillante_refusee(self):
        propositions = [proposition("eval", "porte"), proposition("prendre", "objet_invente"),
                        {**proposition("examiner", "porte"), "effets": [{"or": 999}]},
                        {**proposition("examiner", "porte"), "difficulte": True}]
        avant = copy.deepcopy(self.m.data)
        for p in propositions:
            with self.assertRaises(ErreurMonde):
                self.moteur.preparer(p, "LLM")
        self.assertEqual(avant, self.m.data)


class MJTests(unittest.TestCase):
    def test_configuration_locale_limitee_et_prioritaire(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_text('# commentaire\nOPENAI_API_KEY="locale"\nOPENAI_MODEL=test\nPATH=injection\n', encoding="utf-8")
            with patch.dict("os.environ", {"OPENAI_API_KEY": "heritee", "PATH": "original"}):
                charger_env(env)
                import os
                self.assertEqual(os.environ["OPENAI_API_KEY"], "locale")
                self.assertEqual(os.environ["OPENAI_MODEL"], "test")
                self.assertEqual(os.environ["PATH"], "original")

    def test_appel_structure_sans_secret_du_monde(self):
        p = proposition("detacher", "axe_haut", "couteau", "levier", 18, "Le couteau est fragile.")
        retour = {"status": "completed", "output": [
            {"type": "reasoning", "summary": []},
            {"type": "function_call", "name": "proposer_action", "arguments": json.dumps(p)}],
            "usage": {"total_tokens": 123}}
        def repondre(requete, timeout):
            corps = json.loads(requete.data)
            self.assertFalse(corps["store"])
            self.assertTrue(corps["tools"][0]["strict"])
            self.assertNotIn('"id": "anneau"', corps["input"][0]["content"])
            self.assertEqual(corps["tool_choice"]["name"], "proposer_action")
            return io.BytesIO(json.dumps(retour).encode())
        with patch.dict("os.environ", {"OPENAI_API_KEY": "cle-de-test"}), patch("urllib.request.urlopen", side_effect=repondre):
            resultat = MJOpenAI().proposer(nouveau_monde(), "Je soulève l'axe avec mon couteau")
        self.assertEqual(resultat, p)
        self.assertEqual(Moteur(nouveau_monde()).preparer(resultat).dd, 18)

    def test_api_en_erreur_ne_modifie_pas_monde_ni_expose_cle(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        erreur = urllib.error.HTTPError("https://api.openai.com", 401, "unauthorized", {},
                                        io.BytesIO(b'{"error":{"code":"invalid_api_key"}}'))
        with patch.dict("os.environ", {"OPENAI_API_KEY": "secret-a-ne-pas-afficher"}), patch("urllib.request.urlopen", side_effect=erreur):
            with self.assertRaises(ErreurMonde) as capture:
                MJOpenAI().proposer(m, "bonjour")
        self.assertNotIn("secret-a-ne-pas-afficher", str(capture.exception))
        self.assertEqual(avant, m.data)

    def test_reponse_tronquee_refusee(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch("urllib.request.urlopen", return_value=io.BytesIO(b'{"status":"incomplete","output":[]}')):
            with self.assertRaises(ErreurMonde):
                MJOpenAI().proposer(nouveau_monde(), "agir")

    def test_reponse_mal_formee_refusee(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch("urllib.request.urlopen", return_value=io.BytesIO(b'[]')):
            with self.assertRaises(ErreurMonde):
                MJOpenAI().proposer(nouveau_monde(), "agir")


class ConsoleTests(unittest.TestCase):
    def test_console_sauvegarde_reprise_et_nouvelle_partie(self):
        import jeu
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "partie.json"
            sorties = io.StringIO()
            with patch("builtins.input", side_effect=["prendre clé", "ouest", "acheter marteau", "quitter"]), patch("sys.stdout", sorties):
                self.assertEqual(jeu.main(["--offline", "--save", str(fichier)]), 0)
            sauvegarde = Monde.charger(fichier)
            self.assertEqual(sauvegarde.joueur["or"], 18)
            self.assertEqual(sauvegarde.objets["marteau"]["lieu"], "joueur")
            with patch("builtins.input", side_effect=["fiche", "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                jeu.main(["--offline", "--save", str(fichier)])
                self.assertIn("18 pièces", sortie.getvalue())
            with patch("builtins.input", side_effect=["quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--offline", "--new", "--save", str(fichier)])
            self.assertEqual(Monde.charger(fichier).joueur["or"], 24)
            self.assertEqual(Monde.charger(fichier.with_suffix(".json.bak")).joueur["or"], 18)

    def test_console_mj_propose_sans_agir_puis_execute_sur_tenter(self):
        import jeu
        p = proposition("detacher", "axe_haut", "couteau", "levier", 18, "Petit axe, lame fragile.")
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "partie.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "cle-test"}), patch.object(MJOpenAI, "echanger", return_value={"mode": "action", "texte": "", "faits": [], "proposition": p}), patch("builtins.input", side_effect=["mj je retire l'axe", "quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--save", str(fichier)])
            self.assertTrue(Monde.charger(fichier).objets["axe_haut"]["attache"])
            with patch.dict("os.environ", {"OPENAI_API_KEY": "cle-test"}), patch.object(MJOpenAI, "echanger", return_value={"mode": "action", "texte": "", "faits": [], "proposition": p}), patch.object(Monde, "d20", return_value=20), patch.object(MJOpenAI, "raconter_resultat", return_value={}), patch("builtins.input", side_effect=["mj je retire l'axe", "tenter", "quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--save", str(fichier)])
            self.assertFalse(Monde.charger(fichier).objets["axe_haut"]["attache"])


if __name__ == "__main__":
    unittest.main()
