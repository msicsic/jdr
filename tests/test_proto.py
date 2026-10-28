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
        from donjon.esprits import dernier_son
        self.assertEqual(dernier_son(self.m, "marchand")["nature"], "bruyant")
        bruit = self.m.data["bruit"]
        self.agir("attendre")
        self.assertLess(self.m.data["bruit"], bruit)
        self.assertNotIn("humeur", self.m.objets["marchand"])

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
        with tempfile.TemporaryDirectory() as tmp, \
             patch("urllib.request.urlopen", side_effect=AssertionError("Cette scène doit rester sans réseau")):
            fichier = Path(tmp) / "partie.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "cle-test"}), patch.object(MJOpenAI, "echanger", return_value={"mode": "action", "texte": "", "faits": [], "proposition": p}), patch("builtins.input", side_effect=["mj je retire l'axe", "quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--save", str(fichier)])
            self.assertTrue(Monde.charger(fichier).objets["axe_haut"]["attache"])
            # Suite sans réseau : après « tenter », le récit du résultat doit aussi être simulé.
            # Son indisponibilité laisse le texte du moteur, sans changer le geste testé.
            with patch.dict("os.environ", {"OPENAI_API_KEY": "cle-test"}), \
                 patch.object(MJOpenAI, "echanger", return_value={"mode": "action", "texte": "", "faits": [], "proposition": p}), \
                 patch.object(MJOpenAI, "raconter_resultat", side_effect=ErreurMonde("Récit indisponible dans cette scène sans réseau.")), \
                 patch.object(Monde, "d20", return_value=20), \
                 patch("builtins.input", side_effect=["mj je retire l'axe", "tenter", "quitter"]), \
                 patch("sys.stdout", io.StringIO()):
                jeu.main(["--save", str(fichier)])
            self.assertFalse(Monde.charger(fichier).objets["axe_haut"]["attache"])


    def test_compilateur_sons_improvises_et_absence_fuite_justification(self):
        from donjon.compilateur import extraire_contexte, normaliser_proposition
        from donjon.auberge import nouveau_auberge; m = nouveau_auberge(); m.data["mode_cases"] = True
        m.joueur["salle"] = m.joueur["position_salle"] = "couloir"
        m.joueur["position"] = [7, 2]
        m.joueur["orientation"] = "ouest"
        ctx = extraire_contexte(m)
        noms_ctx = [o["nom"] for o in ctx["objets"]] + [p["nom"] for p in ctx["interlocuteurs"]]
        self.assertNotIn("Hugues", noms_ctx)
        self.assertNotIn("Mathurine", noms_ctx)
        for phrase, action_brute, cible_brute, forme_attendue, rendu_attendu in (
            ("je chante", "improviser", "voix_melodique", "voix_melodique", "Tu fais entendre des notes de ta voix."),
            ("je tape dans mes mains", "improviser", "corps_rythmique", "corps_rythmique", "Tu frappes un rythme avec ton corps."),
        ):
            p = normaliser_proposition(
                {"action": action_brute, "cible": cible_brute, "texte": "", "justification": "Le joueur émet un son."},
                m,
                intention=phrase,
            )
            self.assertEqual(p["action"], "improviser")
            plan = Moteur(m).preparer(p)
            self.assertEqual(plan.stat, "")
            self.assertFalse(plan.confirmation)
            res = Moteur(m).executer(plan)
            self.assertIn(rendu_attendu, res)
            self.assertEqual(m.data["sons"][-1]["forme"], forme_attendue)
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "auberge.json"
            m.sauver(f)
            m2 = Monde.charger(f)
            self.assertEqual(m2.data["sons"][-1]["forme"], "corps_rythmique")
            self.assertTrue(m2.data["gestes_improvises"])
        p_dial = normaliser_proposition(
            {"action": "dialogue", "texte": "", "justification": "Le joueur bavarde; aucune action mécanique."},
            m,
            intention="bonjour",
        )
        self.assertEqual(p_dial["texte"], "")
        # Neutralisation / étranglement dans le dos d'Odile au contact : défense 10 par surprise et perte de connaissance
        m.objets["odile"]["lieu"] = m.objets["odile"]["position_salle"] = "couloir"
        m.objets["odile"]["position"] = [4, 1]
        m.objets["odile"]["orientation"] = "ouest"
        m.joueur["position"] = [5, 1]
        m.joueur["orientation"] = "ouest"
        p_etrangle = normaliser_proposition(
            {"action": "frapper", "cible": "", "outil": "", "methode": "assommer", "texte": "", "justification": ""},
            m,
            intention="je l'étrangle",
        )
        self.assertEqual(p_etrangle["action"], "frapper")
        self.assertEqual(p_etrangle["cible"], "odile")
        self.assertEqual(p_etrangle["methode"], "assommer")
        plan_etrangle = Moteur(m).preparer(p_etrangle)
        self.assertIn("défense 10 par surprise", plan_etrangle.resume(m))
        with patch.object(Monde, "d20", return_value=15):
            res_etrangle = Moteur(m).executer(plan_etrangle)
        self.assertIn("sans connaissance", res_etrangle)
        # Le compilateur ne réécrit plus la décision du modèle d'après des mots de la saisie :
        # c'est le modèle qui choisit l'action, le moteur qui valide.
        for phrase, action_brute in (("je l'étrangle", "dialogue"), ("je chante", "dialogue"), ("je lui saisis le bras", "dialogue")):
            p_brut = normaliser_proposition(
                {"action": action_brute, "cible": "", "texte": "", "justification": ""}, m, intention=phrase)
            self.assertEqual(p_brut["action"], "dialogue", phrase)
        p_muet = normaliser_proposition(
            {"action": "improviser", "cible": "", "texte": "", "justification": ""}, m, intention="je chante")
        self.assertEqual(p_muet["action"], "improviser")
        sons_avant = len(m.data.get("sons", []))
        Moteur(m).executer(Moteur(m).preparer(p_muet))
        self.assertEqual(len(m.data.get("sons", [])), sons_avant)  # forme non désignée : geste muet, pas de son deviné


class DialogueDecoupleTests(unittest.TestCase):
    """Le compilateur type la parole (``sujet_parole``) ; le moteur n'infère rien des mots de la saisie."""

    @staticmethod
    def _mj(sujet):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse

        class Faux(Fournisseur):
            def _appeler(self, demande):
                if demande.fonction == "compiler_intention":
                    return Reponse(arguments={
                        "action": "dialogue", "cible": "", "destination": "", "outil": "", "methode": "simple",
                        "difficulte": 0, "texte": "", "sujet_parole": sujet, "justification": "", "personnage": "",
                        "operation": "", "mission": "", "montant_demande": 0, "etapes": []}, brut={}, utilisation={})
                if demande.fonction == "repondre_dialogue":
                    return Reponse(arguments={"replique": f"{demande.entree['personnage_cible']} : « Hm. »"},
                                   brut={}, utilisation={})
                return Reponse(arguments={"texte": ""}, brut={}, utilisation={})

        return MJOpenAI(connexion="local", fournisseur=Faux(), decoupler=True)

    def _parler(self, phrase, sujet):
        from donjon.auberge import nouveau_auberge
        from donjon.transactions import appliquer
        from donjon.voix import connait_nom

        m = nouveau_auberge()
        m.joueur.update(salle="salle_commune", position=[4, 5], orientation="nord")
        reponse = self._mj(sujet).echanger(m, phrase)
        self.assertEqual(reponse["mode"], "dialogue")
        travail, _ = appliquer(m, reponse["_transactions"])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "auberge.json"
            travail.sauver(chemin)
            reprise = Monde.charger(chemin)
        return connait_nom(reprise, "joueur", "mathurine")

    def test_demande_d_identite_typee_par_le_modele_apprend_le_nom_apres_rechargement(self):
        # Deux formulations que nulle liste de mots ne prévoit : seul le type donné par le modèle compte.
        for phrase in ("à la vieille femme menue : c'est quoi ton blaze ?", "à la vieille femme menue : toi, t'es qui ?"):
            self.assertTrue(self._parler(phrase, "qui"), phrase)

    def test_meme_phrase_typee_propos_n_apprend_pas_le_nom(self):
        for phrase in ("à la vieille femme menue : comment tu t'appelles ?", "à la vieille femme menue : tu es qui ?"):
            self.assertFalse(self._parler(phrase, "propos"), phrase)

    def test_sujet_parole_normalise_et_defaut_propos(self):
        from donjon.compilateur import normaliser_proposition
        for brut, attendu in (("qui", "qui"), ("propos", "propos"), ("", "propos"), ("n'importe quoi", "propos")):
            p = normaliser_proposition({"action": "dialogue", "texte": "Le joueur demande quelque chose.",
                                        "sujet_parole": brut, "justification": ""}, nouveau_monde(), intention="bonjour")
            self.assertEqual(p["sujet_parole"], attendu)

    def test_texte_du_compilateur_n_est_jamais_affiche_si_le_narrateur_se_tait(self):
        from donjon.auberge import nouveau_auberge
        from donjon.fournisseurs.contrat import Fournisseur, Reponse

        for texte in ("Le joueur demande son nom au PNJ.", "Odile : « Le joueur d'échecs est parti. »"):
            class Faux(Fournisseur):
                def _appeler(self, demande):
                    if demande.fonction == "compiler_intention":
                        return Reponse(arguments={
                            "action": "dialogue", "cible": "", "destination": "", "outil": "", "methode": "simple",
                            "difficulte": 0, "texte": texte, "sujet_parole": "propos", "justification": "",
                            "personnage": "", "operation": "", "mission": "", "montant_demande": 0, "etapes": []},
                            brut={}, utilisation={})
                    return Reponse(arguments={"replique": "", "texte": ""}, brut={}, utilisation={})

            m = nouveau_auberge()
            m.joueur.update(salle="salle_commune", position=[4, 5], orientation="nord")
            mj = MJOpenAI(connexion="local", fournisseur=Faux(), decoupler=True)
            reponse = mj.echanger(m, "à la vieille femme menue : bonjour")
            self.assertNotIn(texte, reponse["texte"])
            self.assertNotIn("Le joueur", reponse["texte"])

    def test_parole_impossible_est_rendue_au_joueur_sans_reponse_inventee(self):
        """Un nom que Corvus ne connaît pas (deux cas) : aucune réplique, rien d'enregistré, le message du moteur."""
        from donjon.auberge import nouveau_auberge
        from donjon.paroles import ParoleImpossible

        for phrase in ("je dis à Mathurine : bonjour", "je dis à Lucien : bonjour"):
            m = nouveau_auberge()
            m.joueur.update(salle="salle_commune", position=[4, 5], orientation="nord")
            avant = copy.deepcopy(m.data)
            with self.assertRaises(ParoleImpossible) as ctx:
                self._mj("propos").echanger(m, phrase)
            self.assertIn("Tu ne connais personne du nom", str(ctx.exception))
            self.assertEqual(m.data, avant, phrase)

    def test_erreur_interne_n_est_pas_avalee(self):
        """Plus de `except Exception: pass` : un défaut du moteur ne se déguise pas en réplique."""
        from donjon.auberge import nouveau_auberge

        m = nouveau_auberge()
        m.joueur.update(salle="salle_commune", position=[4, 5], orientation="nord")
        with patch("donjon.paroles.preparer_parole", side_effect=KeyError("defaut")):
            with self.assertRaises(KeyError):
                self._mj("propos").echanger(m, "à la vieille femme menue : bonjour")

class CommerceEtRemiseCompilateurTests(unittest.TestCase):
    """Le modèle choisit l'action ; le moteur valide. Aucun mot de la saisie ne la change."""

    @staticmethod
    def _echoppe(anneau=False):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        if anneau:
            m.objets["anneau"]["lieu"] = "joueur"
        return m

    def test_catalogue_dit_par_le_vendeur_avec_les_faits_du_moteur(self):
        from donjon.compilateur import normaliser_proposition
        from donjon.rendu import prix
        m = self._echoppe()
        p = normaliser_proposition({"action": "lister_marchandises", "cible": "", "texte": "Des babioles !"}, m,
                                   intention="que vendez-vous ?")
        self.assertEqual(p["action"], "dialogue")
        self.assertTrue(p["_deterministe"])
        for o in m.objets.values():
            if o.get("en_vente") and o.get("lieu") == "echoppe":
                self.assertIn(o["nom"], p["texte"])
                self.assertIn(f"{prix(m, o)} pièce", p["texte"])
        self.assertNotIn("babioles", p["texte"])   # jamais le texte du modèle

    def test_catalogue_sans_rien_en_vente_est_refuse_avec_son_attendu(self):
        from donjon.compilateur import normaliser_proposition
        m = nouveau_monde()   # le joueur n'est pas dans l'échoppe
        m.joueur["salle"] = next(s for s in m.data["salles"] if s != "echoppe")
        with self.assertRaises(ErreurMonde) as ctx:
            normaliser_proposition({"action": "lister_marchandises", "cible": ""}, m, intention="que vendez-vous ?")
        self.assertTrue(getattr(ctx.exception, "attendu", ""))

    def test_les_mots_du_commerce_ne_changent_plus_l_action_du_modele(self):
        from donjon.compilateur import normaliser_proposition
        m = self._echoppe()
        for phrase in ("combien de pièces me reste-t-il ?", "ce que tu vends est-il de bonne qualité ?",
                       "je prends la trousse de crochets"):
            p = normaliser_proposition({"action": "dialogue", "cible": "", "texte": "", "personnage": "marchand"},
                                       m, intention=phrase)
            self.assertEqual(p["action"], "dialogue", phrase)
            self.assertFalse(p.get("_deterministe"), phrase)

    def test_les_mots_de_la_remise_ne_changent_plus_l_action_du_modele(self):
        from donjon.compilateur import normaliser_proposition
        m = self._echoppe(anneau=True)
        for phrase in ("Gorm, donne-moi 30 pièces pour l'anneau", "voici ce que je pense de l'anneau"):
            p = normaliser_proposition({"action": "conversation_pnj", "personnage": "marchand", "operation": "negocier",
                                        "mission": "", "montant_demande": 30}, m, intention=phrase)
            self.assertEqual(p["action"], "conversation_pnj", phrase)

    def test_remise_jamais_le_premier_objet_ni_le_premier_pnj(self):
        from donjon.compilateur import normaliser_proposition
        m = self._echoppe(anneau=True)
        m.objets["cle"]["lieu"] = "joueur"
        # Deux objets portés, aucun nommé : le moteur n'en choisit pas un à la place du joueur.
        p = normaliser_proposition({"action": "remettre", "cible": "", "outil": "marchand"}, m, intention="tiens, prends ça")
        self.assertEqual(p["cible"], "")
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(p)
        # Nommé dans la saisie, ou seul objet porté : déduit.
        p = normaliser_proposition({"action": "remettre", "cible": "", "outil": "marchand"}, m,
                                   intention="voici l'anneau du veilleur")
        self.assertEqual((p["cible"], p["outil"]), ("anneau", "marchand"))
        for i, o in m.objets.items():   # il ne porte plus que l'anneau
            if o.get("lieu") == "joueur" and i != "anneau":
                o["lieu"] = "echoppe"
        p = normaliser_proposition({"action": "remettre", "cible": "", "outil": ""}, m, intention="tiens")
        self.assertEqual((p["cible"], p["outil"]), ("anneau", "marchand"))

    def test_replique_accord_en_fiction_sans_phrase_de_regie_sur_deux_missions_et_recharge(self):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse
        from donjon.transactions import appliquer

        def mj_conv(personnage, operation, mission, montant=0):
            class Faux(Fournisseur):
                def _appeler(self, demande):
                    return Reponse(arguments={
                        "action": "conversation_pnj", "cible": "", "destination": "", "outil": "", "methode": "simple",
                        "difficulte": 0, "texte": "", "sujet_parole": "propos", "justification": "",
                        "personnage": personnage, "operation": operation, "mission": mission,
                        "montant_demande": montant, "etapes": []}, brut={}, utilisation={})
            return MJOpenAI(connexion="local", fournisseur=Faux(), decoupler=True)

        # 1) Mission de Gorm (l'anneau du veilleur) : offre, contre-offre, maintien, acceptation.
        m = self._echoppe()
        for op, dem, attendu_texte, attendu_montant, attendu_statut in (
            ("proposer", 0, "Je t'offre 20 pièces, payables contre la remise de l'anneau du veilleur.", 20, "propose"),
            ("negocier", 40, "Pas 40 pièces ; je monte à 22 pièces, payables à la remise de l'anneau du veilleur.", 22, "propose"),
            ("negocier", 40, "Pas 40 pièces : je maintiens mon offre de 22 pièces contre la remise de l'anneau du veilleur.", 22, "propose"),
            ("accepter", 0, "Marché conclu pour 22 pièces. Tu les auras à la remise de l'anneau du veilleur.", 22, "accepte"),
        ):
            r = mj_conv("marchand", op, "anneau_veilleur", dem).echanger(m, "parlons de l'anneau")
            self.assertIn(attendu_texte, r["texte"])
            for regie in ("Le joueur", "Aucun paiement immédiat", "Il maintient", "contre la remise de l'objet"):
                self.assertNotIn(regie, r["texte"])
            m, _ = appliquer(m, r["_transactions"])
            m.memoriser("parlons de l'anneau", r["texte"], "conversation_pnj")
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "echoppe.json"
            m.sauver(f)
            reprise = Monde.charger(f)
        self.assertEqual(reprise.data["engagements"]["anneau_veilleur"], {"statut": "accepte", "montant": 22})
        self.assertIn("Marché conclu pour 22 pièces", reprise.data["conversation"][-1]["reponse"])

        # 2) Autre PNJ et autre mission (Mira, la clé en fer) : même contrat sans mention de Gorm ni de l'anneau.
        m2 = self._echoppe()
        from donjon.voix import apprendre_nom
        m2.objets["mira"] = objet("mira", "Mira", "personnage", "echoppe", genre="f")
        apprendre_nom(m2, "joueur", "mira")
        m2.data["finances_pnj"]["mira"] = 12
        m2.data["missions"]["cle_mira"] = {
            "donneur": "mira", "objet": "cle", "nom": "Apporter la clé",
            "condition": "Remettre la clé à Mira.", "prime_base": 5, "prime_plafond": 10,
        }
        r2 = mj_conv("mira", "proposer", "cle_mira").echanger(m2, "Mira, combien pour la clé ?")
        self.assertEqual(
            r2["texte"],
            "Mira : « Je t'offre 5 pièces, payables contre la remise de la clé du veilleur. Dis-moi si tu acceptes. »",
        )
        m2, _ = appliquer(m2, r2["_transactions"])
        self.assertEqual(m2.data["engagements"]["cle_mira"], {"statut": "propose", "montant": 5})


class RelanceAttenduCompilateurTests(unittest.TestCase):
    """Le chemin découplé valide les propositions sur copie et transmet ``attendu`` au compilateur en cas de refus."""

    @staticmethod
    def _arg(**champs):
        base = {
            "action": "observer", "cible": "", "destination": "", "outil": "", "methode": "simple",
            "difficulte": 0, "texte": "", "sujet_parole": "", "justification": "",
            "personnage": "", "operation": "", "mission": "", "montant_demande": 0, "etapes": [],
        }
        base.update(champs)
        return base

    @staticmethod
    def _mj_sequence(reponses_compilateur, replique_dialogue="Gorm : « Entendu. »"):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse
        appels = []
        it = iter(reponses_compilateur)

        class Faux(Fournisseur):
            def _appeler(self, demande):
                if demande.fonction == "compiler_intention":
                    appels.append(copy.deepcopy(demande.entree))
                    return Reponse(arguments=next(it), brut={}, utilisation={"entree": 10, "sortie": 5})
                if demande.fonction == "repondre_dialogue":
                    return Reponse(arguments={"replique": replique_dialogue}, brut={}, utilisation={"entree": 5, "sortie": 5})
                return Reponse(arguments={"texte": ""}, brut={}, utilisation={})

        return MJOpenAI(connexion="local", fournisseur=Faux(), decoupler=True), appels

    def test_correction_sur_attendu_pour_contenant_ferme_et_objet_observe_avec_recharge(self):
        # Cas 1 : l'anneau est dans le coffre fermé (non verrouillé). Le 1er essai « prendre anneau »
        # reçoit attendu (« ouvre d'abord coffre... ») et se corrige en composer (ouvrir + deplacer).
        m = nouveau_monde()
        m.joueur["salle"] = "crypte"
        m.objets["coffre"]["verrouillee"] = False
        m.objets["coffre"]["ouverte"] = False
        mj, appels = self._mj_sequence([
            self._arg(action="prendre", cible="anneau"),
            self._arg(action="composer", etapes=[
                {"operation": "ouvrir", "cible": "coffre", "destination": "", "outil": "", "methode": "simple", "difficulte": 0},
                {"operation": "deplacer", "cible": "anneau", "destination": "joueur", "outil": "", "methode": "simple", "difficulte": 0},
            ]),
        ])
        r = mj.echanger(m, "je prends l'anneau dans le coffre")
        self.assertEqual(len(appels), 2)
        self.assertNotIn("retour_moteur", appels[0])
        retour = appels[1]["retour_moteur"]
        self.assertIn("ouvre d'abord coffre", retour["attendu"])
        self.assertNotIn("composer", retour["obstacle"])
        self.assertEqual(r["mode"], "action")
        self.assertEqual(r["proposition"]["action"], "composer")
        # Le monde d'origine n'a pas été muté pendant la validation
        self.assertFalse(m.objets["coffre"]["ouverte"])
        self.assertEqual(m.objets["anneau"]["lieu"], "coffre")
        # Exécution, sauvegarde et rechargement
        plan = Moteur(m).preparer(r["proposition"], "MJ")
        texte_res = Moteur(m).executer(plan)
        m.memoriser("je prends l'anneau dans le coffre", texte_res, "resultat_moteur")
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "crypte.json"
            m.sauver(f)
            reprise = Monde.charger(f)
        self.assertTrue(reprise.objets["coffre"]["ouverte"])
        self.assertEqual(reprise.objets["anneau"]["lieu"], "joueur")
        self.assertIn("anneau", reprise.data["conversation"][-1]["reponse"].lower())

        # Cas 2 : observer un objet précis (« antichambre_sol ») -> attendu oriente vers examiner.
        m2 = nouveau_monde()
        mj2, appels2 = self._mj_sequence([
            self._arg(action="observer", cible="antichambre_sol"),
            self._arg(action="examiner", cible="antichambre_sol"),
        ])
        r2 = mj2.echanger(m2, "j'observe les dalles du sol")
        self.assertEqual(len(appels2), 2)
        self.assertIn("examiner", appels2[1]["retour_moteur"]["attendu"])
        self.assertEqual(r2["mode"], "action")
        self.assertEqual((r2["proposition"]["action"], r2["proposition"]["cible"]), ("examiner", "antichambre_sol"))
        plan2 = Moteur(m2).preparer(r2["proposition"], "MJ")
        res2 = Moteur(m2).executer(plan2)
        m2.memoriser("j'observe les dalles du sol", res2, "resultat_moteur")
        with tempfile.TemporaryDirectory() as tmp:
            f2 = Path(tmp) / "antichambre.json"
            m2.sauver(f2)
            reprise2 = Monde.charger(f2)
        self.assertIn("sol en pierre", reprise2.data["conversation"][-1]["reponse"].lower())

    def test_correction_conversation_pnj_et_lister_marchandises_sur_attendu(self):
        from donjon.transactions import appliquer
        # 1) Accepter une offre non encore proposée -> attendu demande proposer ou negocier d'abord.
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        mj, appels = self._mj_sequence([
            self._arg(action="conversation_pnj", personnage="marchand", operation="accepter", mission="anneau_veilleur"),
            self._arg(action="conversation_pnj", personnage="marchand", operation="proposer", mission="anneau_veilleur"),
        ])
        r = mj.echanger(m, "parlons de la mission de l'anneau")
        self.assertEqual(len(appels), 2)
        self.assertIn("proposer ou negocier d'abord", appels[1]["retour_moteur"]["attendu"])
        self.assertEqual(r["mode"], "dialogue")
        self.assertIn("Je t'offre 20 pièces", r["texte"])
        m, _ = appliquer(m, r["_transactions"])
        self.assertEqual(m.data["engagements"]["anneau_veilleur"], {"statut": "propose", "montant": 20})

        # 2) lister_marchandises hors échoppe -> RefusDeForme corrigé en dialogue au 2e appel.
        m2 = nouveau_monde()
        mj2, appels2 = self._mj_sequence([
            self._arg(action="lister_marchandises"),
            self._arg(action="dialogue", sujet_parole="propos"),
        ], replique_dialogue="Il n'y a aucun marchand ici.")
        r2 = mj2.echanger(m2, "y a-t-il quelque chose à acheter ici ?")
        self.assertEqual(len(appels2), 2)
        self.assertIn("aucun objet en_vente", appels2[1]["retour_moteur"]["attendu"])
        self.assertEqual(r2["mode"], "dialogue")

    def test_reexamen_impossible_et_refus_monde_ou_hors_portee_sans_fuite_d_attendu(self):
        # 1) Si le compilateur répond « impossible » au 1er essai, RefusDeForme impose de proposer le geste ;
        # lorsque le moteur refuse ensuite (porte verrouillée) et que le compilateur conclut « impossible »,
        # le joueur reçoit exactement le refus du moteur, sans attendu.
        m = nouveau_monde()
        mj, appels = self._mj_sequence([
            self._arg(action="impossible", justification="Je pense que c'est fermé."),
            self._arg(action="ouvrir", cible="porte"),
            self._arg(action="impossible", justification="Inventé par le modèle."),
        ])
        r = mj.echanger(m, "j'ouvre la porte du nord")
        self.assertEqual(len(appels), 3)
        self.assertIn("action : le geste que demande la saisie", appels[1]["retour_moteur"]["attendu"])
        self.assertIn("C'est verrouillé.", r["texte"])
        self.assertNotIn("Inventé par le modèle", r["texte"])
        self.assertNotIn("attendu", r["texte"])
        self.assertTrue(r.get("_texte_moteur"))
        self.assertTrue(r.get("_validation_refusee"))

        # 2) HorsDePortee en mode_cases : réponse publique immédiate en 1 seul appel, sans relance.
        from tests.test_tensions import placer, recharger
        from tests.test_sous_obstacle import scene
        m_loin = scene()
        m_loin.data["salles"]["echoppe"]["lumiere_naturelle"] = 2
        m_loin.joueur.update(position=[3, 1], orientation="est")
        placer(m_loin, "crochets", "echoppe", (7, 1))
        m_loin = recharger(m_loin)
        mj_loin, appels_loin = self._mj_sequence([
            self._arg(action="prendre", cible="crochets"),
        ])
        r_loin = mj_loin.echanger(m_loin, "je prends la trousse de crochets")
        self.assertEqual(len(appels_loin), 1)
        self.assertEqual(r_loin["mode"], "dialogue")
        self.assertIn("Approche-toi", r_loin["texte"])
        self.assertNotIn("cible=", r_loin["texte"])
        self.assertTrue(r_loin.get("_texte_moteur"))


class ParoleJoueurDecoupleTests(unittest.TestCase):
    """Les actes de parole typés (``donjon/paroles.py``) passent par le compilateur et ``preparer_parole``."""

    @staticmethod
    def _arg(**champs):
        base = {
            "action": "dialogue", "cible": "", "destination": "", "outil": "", "methode": "simple",
            "difficulte": 0, "texte": "", "sujet_parole": "propos", "justification": "",
            "personnage": "", "operation": "", "mission": "", "montant_demande": 0,
            "etapes": [], "contenu": [],
        }
        base.update(champs)
        return base

    @staticmethod
    def _mj_sequence(reponses_compilateur, replique_dialogue="« Entendu. »"):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse
        appels_compil = []
        appels_dial = []
        it = iter(reponses_compilateur)

        class Faux(Fournisseur):
            def _appeler(self, demande):
                if demande.fonction == "compiler_intention":
                    appels_compil.append(copy.deepcopy(demande.entree))
                    return Reponse(arguments=next(it), brut={}, utilisation={"entree": 10, "sortie": 5})
                if demande.fonction == "repondre_dialogue":
                    appels_dial.append({"instructions": demande.instructions, "entree": copy.deepcopy(demande.entree)})
                    return Reponse(arguments={"replique": replique_dialogue}, brut={}, utilisation={"entree": 5, "sortie": 5})
                return Reponse(arguments={"texte": ""}, brut={}, utilisation={})

        return MJOpenAI(connexion="local", fournisseur=Faux(), decoupler=True), appels_compil, appels_dial

    def test_passage_et_reclamer_dette_enregistrent_effets_apres_rechargement(self):
        from donjon.transactions import appliquer
        from donjon.biens import rembourser
        from tests.test_parole_commune import scene
        from tests.test_parole_corrections import banc
        from tests.test_tensions import placer, recharger

        # Cas 1 : demander le passage à Brune au contact dans l'antichambre
        m = scene(brune=(2, 3), ilse=(5, 4), aubin=(1, 5))
        m.data["connus"].append("brune")
        m = recharger(m)
        mj, appels, _ = self._mj_sequence([
            self._arg(sujet_parole="passage"),
        ], replique_dialogue="Brune : « Passe donc. »")
        r = mj.echanger(m, "Brune, laisse-moi passer")
        self.assertEqual(len(appels), 1)
        self.assertEqual(r["mode"], "dialogue")
        self.assertIn("s'écarte d'un pas pour te laisser passer.", r["texte"])
        # Tant que la transaction n'est pas appliquée, le monde d'origine est intact
        self.assertEqual(m.objets["brune"]["position"], [2, 3])
        m, _ = appliquer(m, r["_transactions"])
        m.memoriser("Brune, laisse-moi passer", r["texte"], "dialogue")
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "passage.json"
            m.sauver(f)
            reprise = Monde.charger(f)
        self.assertNotEqual(reprise.objets["brune"]["position"], [2, 3])
        self.assertIn("s'écarte d'un pas", reprise.data["conversation"][-1]["reponse"])

        # Cas 2 : réclamer une dette d'or à Aubin
        m2 = banc("ressources")
        rembourser(m2, "aubin", "joueur", 2, "vivres", "part")
        m2 = recharger(m2)
        or_avant = m2.joueur.get("or", 0)
        mj2, appels2, _ = self._mj_sequence([
            self._arg(
                sujet_parole="reclamer",
                contenu=[{"type": "reclamer", "sujet": "", "attribut": "", "valeur": ""}],
            ),
        ], replique_dialogue="Aubin : « Voilà ton dû. »")
        r2 = mj2.echanger(m2, "Aubin, rends-moi les deux pièces que tu me dois")
        self.assertEqual(len(appels2), 1)
        self.assertIn("2 pièces", r2["texte"])
        m2, _ = appliquer(m2, r2["_transactions"])
        m2.memoriser("Aubin, rends-moi les deux pièces que tu me dois", r2["texte"], "dialogue")
        with tempfile.TemporaryDirectory() as tmp:
            f2 = Path(tmp) / "dette.json"
            m2.sauver(f2)
            reprise2 = Monde.charger(f2)
        self.assertEqual(reprise2.joueur.get("or", 0), or_avant + 2)
        self.assertEqual(reprise2.data.get("dettes", []), [])
        self.assertIn("2 pièces", reprise2.data["conversation"][-1]["reponse"])

    def test_localisation_avec_relance_attendu_et_affirmation_croyance_apres_rechargement(self):
        from donjon.transactions import appliquer
        from tests.test_parole_commune import scene
        from tests.test_paroles import relais, croyance

        # Cas 1 : demander à Ilse (en face) où est Brune (sans détourner le destinataire vers Brune !),
        # avec 1er essai fautif (« fantome_inconnu ») corrigé grâce à attendu.
        m = scene(ilse=(2, 4), aubin=(1, 5), brune=(7, 1))
        for pid in ("aubin", "brune", "ilse"):
            if pid not in m.data["connus"]:
                m.data["connus"].append(pid)
        mj, appels, _ = self._mj_sequence([
            self._arg(
                sujet_parole="localisation",
                contenu=[{"type": "localisation", "sujet": "fantome_inconnu", "attribut": "", "valeur": ""}],
            ),
            self._arg(
                sujet_parole="localisation",
                contenu=[{"type": "localisation", "sujet": "brune", "attribut": "", "valeur": ""}],
            ),
        ], replique_dialogue="Ilse : « Elle est par ici. »")
        r = mj.echanger(m, "je demande : où est Brune ?")
        self.assertEqual(len(appels), 2)
        self.assertIn("brune", appels[1]["retour_moteur"]["attendu"])
        self.assertIn("Ilse", r["texte"])
        m, _ = appliquer(m, r["_transactions"])
        self.assertEqual(r["_transactions"][0]["proposition"]["personnage"], "ilse")

        # Cas 2 : transmettre une affirmation à Gorm (avec relance RefusDeForme si valeur est vide au 1er essai)
        m2 = relais()
        mj2, appels2, _ = self._mj_sequence([
            self._arg(
                sujet_parole="affirmation",
                contenu=[{"type": "affirmation", "sujet": "cloche", "attribut": "lieu", "valeur": ""}],
            ),
            self._arg(
                sujet_parole="affirmation",
                contenu=[{"type": "affirmation", "sujet": "cloche", "attribut": "lieu", "valeur": "antichambre"}],
            ),
        ], replique_dialogue="Gorm : « Dans l'antichambre ? Je prends note. »")
        r2 = mj2.echanger(m2, "je lui dis que la cloche est déjà au refuge")
        self.assertEqual(len(appels2), 2)
        self.assertIn("contenu[0].valeur", appels2[1]["retour_moteur"]["attendu"])
        m2, _ = appliquer(m2, r2["_transactions"])
        with tempfile.TemporaryDirectory() as tmp:
            f2 = Path(tmp) / "croyance.json"
            m2.sauver(f2)
            reprise2 = Monde.charger(f2)
        croyance_cloche = croyance(reprise2, "cloche")
        self.assertEqual(croyance_cloche["valeur"], "antichambre")
        self.assertEqual(croyance_cloche["source"], "dit:joueur")

    def test_parole_attendue_bloque_action_physique_et_secret_nom_pnj_respecte(self):
        from donjon.transactions import appliquer
        from tests.test_parole_commune import scene
        from tests.test_tensions import recharger
        from donjon.voix import connait_nom

        # Cas 1 : « Pousse-toi de là ! » est une parole ; si le compilateur propose « pousser »,
        # le moteur refuse (« Corvus le dit ; il ne le fait pas. ») et relance vers dialogue/passage.
        m = scene(brune=(2, 3), ilse=(5, 4), aubin=(1, 5))
        if "brune" in m.data.get("connus", []):
            m.data["connus"].remove("brune")
        if "brune" in m.data.get("noms_connus", []):
            m.data["noms_connus"].remove("brune")
        m.data.get("voix_entendues", {}).pop("brune", None)
        m = recharger(m)
        mj, appels, appels_dial = self._mj_sequence([
            self._arg(action="pousser", cible="brune", sujet_parole="", contenu=[]),
            self._arg(action="dialogue", sujet_parole="passage"),
        ], replique_dialogue="« Du calme, je me pousse. »")
        r = mj.echanger(m, "« Pousse-toi de là ! »")
        self.assertEqual(len(appels), 2)
        self.assertEqual(appels[1]["retour_moteur"]["obstacle"], "Corvus le dit ; il ne le fait pas.")
        self.assertEqual(r["mode"], "dialogue")
        m, _ = appliquer(m, r["_transactions"])
        self.assertNotEqual(m.objets["brune"]["position"], [2, 3])
        # Brune n'a pas été questionnée sur son identité (« qui ») : son vrai nom n'est ni connu ni injecté au narrateur
        self.assertFalse(connait_nom(m, "joueur", "brune"))
        self.assertEqual(len(appels_dial), 1)
        self.assertNotIn("Brune", appels_dial[0]["instructions"])


class AtelierEtQualificationDecoupleTests(unittest.TestCase):
    """Vérifie le Lot C dans le chemin découplé : QualificationRequise / etablir_faits et atelier."""

    def _arg(self, **surcharges):
        base = {
            "action": "dialogue",
            "cible": "",
            "outil": "",
            "avec": "",
            "methode": "",
            "direction": "",
            "texte": "",
            "sujet_parole": "",
            "contenu": [],
        }
        base.update(surcharges)
        return base

    def _mj_sequence(self, reponses_compilateur, reponses_faits=()):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse
        appels_compil = []
        appels_faits = []
        it_compil = iter(reponses_compilateur)
        it_faits = iter(reponses_faits)

        class Faux(Fournisseur):
            def _appeler(self, demande):
                if demande.fonction == "compiler_intention":
                    appels_compil.append(copy.deepcopy(demande.entree))
                    return Reponse(arguments=next(it_compil), brut={}, utilisation={"entree": 10, "sortie": 5})
                if demande.fonction == "etablir_faits":
                    appels_faits.append(copy.deepcopy(demande.entree))
                    return Reponse(arguments=next(it_faits), brut={}, utilisation={"entree": 10, "sortie": 5})
                return Reponse(arguments={"texte": "", "replique": ""}, brut={}, utilisation={})

        return MJOpenAI(connexion="local", fournisseur=Faux(), decoupler=True), appels_compil, appels_faits

    def test_qualification_coupe_positive_et_negative_avec_rechargement(self):
        from unittest.mock import patch
        from donjon.atelier import nouveau_atelier
        from donjon.capacites_objet import statut as statut_capacite
        from donjon.monde import objet
        from donjon.moteur import Moteur
        from donjon.transactions import appliquer

        def _atelier_plaque_scie():
            m = nouveau_atelier()
            m.objets["plaque"] = objet(
                "plaque", "plaque d'acier", "materiau", "cour", genre="f",
                materiau="acier doux", masse=12.6, mobile=False,
                description_visuelle="Plaque d'acier doux de 2 mm, fixée au sol.")
            m.objets["plaque"]["position"] = list(m.joueur["position"])
            m.objets["scie"] = objet(
                "scie", "scie à métaux", "outil", "joueur", genre="f",
                materiau="acier", masse=0.6, usages=["couper"], puissance=2,
                description_visuelle="Lame fine adaptée au sciage de l'acier doux.")
            return m

        # Cas 1 : qualification positive (coupe_possible=True sur la plaque avec la scie)
        m = _atelier_plaque_scie()
        mj, appels_c, appels_f = self._mj_sequence(
            reponses_compilateur=[
                self._arg(action="couper", cible="plaque", outil="scie"),
            ],
            reponses_faits=[
                {
                    "ajouts": [{
                        "type": "qualification",
                        "ancrage": "plaque",
                        "moyen": "scie",
                        "coupe_possible": True,
                    }],
                },
            ],
        )
        r = mj.echanger(m, "Je scie la plaque avec la scie")
        self.assertEqual(len(appels_c), 1)
        self.assertEqual(len(appels_f), 1)
        self.assertEqual(r["mode"], "action")
        self.assertEqual(r["proposition"]["action"], "couper")
        self.assertEqual(len(r["_transactions"]), 1)
        self.assertEqual(r["_transactions"][0]["type"], "faits")

        m, _ = appliquer(m, r["_transactions"])
        with patch.object(Monde, "d20", return_value=20):
            res = Moteur(m).executer(Moteur(m).preparer(r["proposition"], "MJ"))
        self.assertIsInstance(res, str)
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "coupe_pos.json"
            m.sauver(f)
            reprise = Monde.charger(f)
        self.assertEqual(statut_capacite(reprise.objets["plaque"], "tranchable", reprise.objets["scie"]), "etablie")
        self.assertLess(reprise.objets["plaque"]["integrite"], 10)

        # Cas 2 : qualification négative (coupe_possible=False) après 1 relance sur outil invalide
        m2 = _atelier_plaque_scie()
        mj2, appels_c2, appels_f2 = self._mj_sequence(
            reponses_compilateur=[
                self._arg(action="couper", cible="plaque", outil="scie"),
            ],
            reponses_faits=[
                {
                    "ajouts": [{
                        "type": "qualification",
                        "ancrage": "plaque",
                        "moyen": "outil_inexistant",
                        "coupe_possible": False,
                    }],
                },
                {
                    "ajouts": [{
                        "type": "qualification",
                        "ancrage": "plaque",
                        "moyen": "scie",
                        "coupe_possible": False,
                    }],
                },
            ],
        )
        r2 = mj2.echanger(m2, "Je scie la plaque avec la scie")
        self.assertEqual(len(appels_c2), 1)
        self.assertEqual(len(appels_f2), 2)
        self.assertIn("moyen", appels_f2[1]["retour_moteur"]["attendu"])
        self.assertEqual(r2["mode"], "dialogue")
        self.assertIn("résiste à la scie", r2["texte"])
        self.assertEqual(len(r2["_transactions"]), 1)
        m2, _ = appliquer(m2, r2["_transactions"])
        with tempfile.TemporaryDirectory() as tmp:
            f2 = Path(tmp) / "coupe_neg.json"
            m2.sauver(f2)
            reprise2 = Monde.charger(f2)
        self.assertEqual(statut_capacite(reprise2.objets["plaque"], "tranchable", reprise2.objets["scie"]), "ecartee")
        self.assertEqual(reprise2.objets["plaque"]["integrite"], 10)

    def test_qualification_physique_puis_decouper_et_assembler_installer_franchir_apres_rechargement(self):
        from unittest.mock import patch
        from donjon.atelier import nouveau_atelier
        from donjon.moteur import Moteur
        from donjon.transactions import appliquer

        # Cas 1 : découper une planche brute non décrite physiquement déclenche etablir_faits (physique)
        m = nouveau_atelier()
        m.objets["planche_brute"] = {
            "id": "planche_brute",
            "nom": "planche brute",
            "aliases": ["planche"],
            "genre": "f",
            "type": "materiau",
            "lieu": "cour",
            "position": list(m.joueur["position"]),
            "position_salle": "cour",
            "mobile": True,
            "masse": 9.0,
            "materiau": "bois",
            "integrite": 10,
            "maximum": 10,
            "proprietaire": "joueur",
        }
        mj, appels_c, appels_f = self._mj_sequence(
            reponses_compilateur=[
                self._arg(action="decouper", cible="planche_brute", outil="hache", texte="100"),
            ],
            reponses_faits=[
                {
                    "ajouts": [{
                        "type": "qualification",
                        "ancrage": "planche_brute",
                        "physique": {
                            "forme": "barre",
                            "matiere": "bois",
                            "pieces": 1,
                            "nom_piece": "",
                            "dimensions": {
                                "longueur_cm": 300,
                                "largeur_cm": 20,
                                "epaisseur_cm": 2.5,
                                "diametre_cm": 0,
                                "hauteur_cm": 0,
                            },
                        },
                    }],
                },
            ],
        )
        r = mj.echanger(m, "Je coupe un morceau d'un mètre dans la planche brute avec la hache")
        self.assertEqual(len(appels_c), 1)
        self.assertEqual(len(appels_f), 1)
        self.assertEqual(r["mode"], "action")
        self.assertEqual(r["proposition"]["action"], "decouper")
        m, _ = appliquer(m, r["_transactions"])
        with patch.object(Monde, "d20", return_value=20):
            res = Moteur(m).executer(Moteur(m).preparer(r["proposition"], "MJ"))
        self.assertIsInstance(res, str)
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "decoupe.json"
            m.sauver(f)
            reprise = Monde.charger(f)
        self.assertEqual(reprise.objets["planche_brute"]["physique"]["dimensions"]["longueur_cm"], 200)
        self.assertIn("planche_brute_1", reprise.objets)
        self.assertEqual(reprise.objets["planche_brute_1"]["physique"]["dimensions"]["longueur_cm"], 100)

        # Cas 2 : assembler une échelle soignée, l'installer contre mur_atelier et franchir vers la terrasse
        m2 = nouveau_atelier(seed=1985)
        m2.data["mode_cases"] = False
        mj2, appels_c2, _ = self._mj_sequence(
            reponses_compilateur=[
                self._arg(action="assembler", cible="echelle", methode="soigne", texte="300"),
                self._arg(action="installer", cible="echelle_1", avec="mur_atelier"),
                self._arg(action="franchir", cible="mur_atelier"),
            ],
        )
        r_asm = mj2.echanger(m2, "Je fabrique soigneusement une échelle de 3 mètres avec les perches et la ficelle")
        self.assertEqual(r_asm["mode"], "action")
        self.assertEqual(r_asm["proposition"]["action"], "assembler")
        self.assertEqual(r_asm["proposition"]["rythme"], "soigne")
        with patch.object(Monde, "d20", return_value=20):
            res_asm = Moteur(m2).executer(Moteur(m2).preparer(r_asm["proposition"], "MJ"))
        self.assertIsInstance(res_asm, str)
        self.assertIn("assemblage_1", m2.objets)

        r_inst = mj2.echanger(m2, "Je dresse l'échelle contre le mur de l'atelier")
        self.assertEqual(r_inst["mode"], "action")
        self.assertEqual(r_inst["proposition"]["action"], "installer")
        with patch.object(Monde, "d20", return_value=20):
            res_inst = Moteur(m2).executer(Moteur(m2).preparer(r_inst["proposition"], "MJ"))
        self.assertIsInstance(res_inst, str)

        r_fr = mj2.echanger(m2, "Je grimpe à l'échelle jusqu'à la terrasse")
        self.assertEqual(r_fr["mode"], "action")
        self.assertEqual(r_fr["proposition"]["action"], "franchir")
        with patch.object(Monde, "d20", return_value=20):
            res_fr = Moteur(m2).executer(Moteur(m2).preparer(r_fr["proposition"], "MJ"))
        self.assertIsInstance(res_fr, str)

        with tempfile.TemporaryDirectory() as tmp:
            f2 = Path(tmp) / "atelier_echelle.json"
            m2.sauver(f2)
            reprise2 = Monde.charger(f2)
        self.assertEqual(reprise2.joueur["salle"], "terrasse")
        self.assertEqual(reprise2.objets["assemblage_1"]["installation"]["support"], "mur_atelier")

    def test_rythme_assembler_ignore_mots_temps_et_presser(self):
        from donjon.atelier import nouveau_atelier
        from donjon.compilateur import normaliser_proposition

        m = nouveau_atelier()
        for phrase in (
            "je presse le pas pour assembler l'échelle",
            "j'assemble l'échelle en même temps",
            "combien de temps faut-il pour assembler l'échelle",
        ):
            prop = normaliser_proposition(
                self._arg(action="assembler", cible="echelle", methode="simple", texte="300"),
                m,
                intention=phrase,
            )
            self.assertEqual(prop["action"], "assembler")
            self.assertEqual(prop["rythme"], "normal", f"« {phrase} » ne doit pas basculer en rythme soigné")

    def test_compiler_faits_route_vers_ollama_11434_par_defaut(self):
        from donjon.atelier import nouveau_atelier
        from donjon.compilateur import compiler_faits
        from donjon.fournisseurs.local import Local

        m = nouveau_atelier()
        urls_appelees = []
        payload_ollama = {
            "message": {
                "content": json.dumps({
                    "ajouts": [{
                        "type": "qualification",
                        "ancrage": "hache",
                        "coupe_possible": True,
                    }],
                }),
            },
            "prompt_eval_count": 12,
            "eval_count": 8,
        }

        def faux_urlopen(req, timeout=None):
            urls_appelees.append((req.full_url, json.loads(req.data.decode("utf-8"))))
            return io.BytesIO(json.dumps(payload_ollama).encode("utf-8"))

        with patch.dict("os.environ", {}, clear=True), \
             patch("urllib.request.urlopen", side_effect=faux_urlopen):
            arguments, _ = compiler_faits(
                Local(),
                m,
                "Je coupe la corde avec la hache",
                qualification_requise={"question": "coupe", "cible": "hache", "outil": "hache"},
            )
        ajouts = arguments["ajouts"]
        self.assertEqual(len(urls_appelees), 1)
        url, corps = urls_appelees[0]
        self.assertIn(":11434/api/chat", url)
        self.assertNotIn(":8080", url)
        self.assertFalse(corps.get("think", True))
        self.assertEqual(len(ajouts), 1)
        self.assertEqual(ajouts[0]["ancrage"], "hache")


class NarrationDeterministeDecoupleTests(unittest.TestCase):
    """Vérifie le Lot D dans donjon/narrateur.py : voix_auteur, paroles_sans_moteur, voix_inconnues, mentions."""

    def test_narrer_refuse_et_corrige_voix_auteur_coordonnees_parole_et_entite_non_percue(self):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse
        from donjon.narrateur import narrer
        from tests.test_parole_commune import scene
        from tests.test_tensions import recharger

        m = scene(brune=(2, 3), ilse=(5, 4), aubin=(1, 5))
        if "brune" in m.data.get("connus", []):
            m.data["connus"].remove("brune")
        if "brune" in m.data.get("noms_connus", []):
            m.data["noms_connus"].remove("brune")
        m = recharger(m)

        appels = []
        reponses = iter([
            "Je vois Corvus en [2, 3] devant Brune et l'anneau. Tu dis à Brune : « Salut ! »",
            "Une odeur d'huile froide flotte sous la voûte de pierre.",
        ])

        class FauxNarrateur(Fournisseur):
            def _appeler(self, demande):
                appels.append(copy.deepcopy(demande.entree))
                return Reponse(arguments={"texte": next(reponses)}, brut={}, utilisation={})

        texte = narrer(FauxNarrateur(), m, "observer la salle", "Tu observes la salle.")
        self.assertEqual(len(appels), 2)
        attendus = " ".join(o["attendu"] for o in appels[1]["controle_narratif"])
        # Vérifie que les 4 familles d'obstacles déterministes sont bien détectées au 1er essai :
        self.assertIn("« Je »", attendus)       # voix_auteur (1re personne)
        self.assertIn("« Corvus »", attendus)   # voix_auteur (nom du joueur)
        self.assertIn("« [2, 3] »", attendus)   # unites_moteur (coordonnées)
        self.assertIn("« Brune »", attendus)    # voix_inconnues (nom de PNJ non appris)
        self.assertIn("« anneau »", attendus)   # mentions (entité non perçue)
        self.assertEqual(texte, "Une odeur d'huile froide flotte sous la voûte de pierre.")

        # Cas 2 : si la 2e tentative comporte un segment valide et un segment fautif, seul le segment valide est gardé
        reponses2 = iter([
            "Corvus avance en [2, 3].",
            "L'air humide glace ta nuque. Brune te regarde en [2, 3].",
        ])

        class FauxNarrateur2(Fournisseur):
            def _appeler(self, demande):
                return Reponse(arguments={"texte": next(reponses2)}, brut={}, utilisation={})

        texte2 = narrer(FauxNarrateur2(), m, "avancer", "Tu fais un pas.")
        self.assertEqual(texte2, "L'air humide glace ta nuque.")

    def test_repondre_dialogue_refuse_nom_secret_nom_corvus_inconnu_et_entite_absente_ou_replie_sur_faits(self):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse
        from donjon.transactions import appliquer
        from tests.test_parole_commune import scene
        from tests.test_tensions import recharger

        m = scene(brune=(2, 3), ilse=(5, 4), aubin=(1, 5))
        if "brune" in m.data.get("connus", []):
            m.data["connus"].remove("brune")
        if "brune" in m.data.get("noms_connus", []):
            m.data["noms_connus"].remove("brune")
        m.data.get("voix_entendues", {}).pop("brune", None)
        m = recharger(m)

        appels_dial = []
        repliques = iter([
            "Brune : « Passe donc Corvus, je suis Brune et l'anneau est caché. »",
            "La femme trapue au tablier taché : « Passe donc, étranger. »",
        ])

        class Faux(Fournisseur):
            def _appeler(self, demande):
                if demande.fonction == "compiler_intention":
                    return Reponse(
                        arguments={
                            "action": "dialogue",
                            "cible": "",
                            "outil": "",
                            "avec": "",
                            "methode": "",
                            "direction": "",
                            "texte": "",
                            "sujet_parole": "passage",
                            "contenu": [],
                        },
                        brut={},
                        utilisation={"entree": 10, "sortie": 5},
                    )
                if demande.fonction == "repondre_dialogue":
                    appels_dial.append(copy.deepcopy(demande.entree))
                    return Reponse(arguments={"replique": next(repliques)}, brut={}, utilisation={"entree": 5, "sortie": 5})
                return Reponse(arguments={"texte": ""}, brut={}, utilisation={})

        mj = MJOpenAI(connexion="local", fournisseur=Faux(), decoupler=True)
        r = mj.echanger(m, "« Laisse-moi passer. »")
        self.assertEqual(len(appels_dial), 2)
        attendus = " ".join(o["attendu"] for o in appels_dial[1]["controle_narratif"])
        self.assertIn("« Brune »", attendus)
        self.assertIn("« Corvus »", attendus)
        self.assertIn("« anneau »", attendus)
        self.assertNotIn("Brune", r["texte"])
        self.assertNotIn("Corvus", r["texte"])
        self.assertNotIn("anneau", r["texte"])
        self.assertIn("Passe donc, étranger.", r["texte"])
        self.assertIn("s'écarte d'un pas pour te laisser passer.", r["texte"])

        m, _ = appliquer(m, r["_transactions"])
        m.memoriser("« Laisse-moi passer. »", r["texte"], "dialogue")
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "dial_controle.json"
            m.sauver(f)
            reprise = Monde.charger(f)
        self.assertNotEqual(reprise.objets["brune"]["position"], [2, 3])
        self.assertNotIn("Brune", reprise.data["conversation"][-1]["reponse"])

        # Cas 2 : si les deux essais de repondre_dialogue échouent au contrôle déterministe,
        # repondre_dialogue renvoie "" et MJ.echanger se replie proprement sur les faits du moteur.
        m2 = scene(brune=(2, 3), ilse=(5, 4), aubin=(1, 5))
        if "brune" in m2.data.get("connus", []):
            m2.data["connus"].remove("brune")
        if "brune" in m2.data.get("noms_connus", []):
            m2.data["noms_connus"].remove("brune")
        m2.data.get("voix_entendues", {}).pop("brune", None)
        m2 = recharger(m2)
        repliques = iter([
            "Brune : « Passe Corvus ! »",
            "Brune : « Encore Brune et Corvus ! »",
        ])
        r2 = mj.echanger(m2, "« Laisse-moi passer. »")
        self.assertNotIn("Brune", r2["texte"])
        self.assertNotIn("Corvus", r2["texte"])
        self.assertEqual(r2["texte"], "la femme sèche s'écarte d'un pas pour te laisser passer.")

    def test_narrer_refuse_chiffres_sans_fondement(self):
        from donjon.fournisseurs.contrat import Fournisseur, Reponse
        from donjon.narrateur import narrer
        from tests.test_parole_commune import scene

        m = scene(brune=(2, 3), ilse=(5, 4), aubin=(1, 5))
        appels = []
        reponses = iter([
            "Il reste 3 torches au mur et la porte a cédé au 2e coup.",
            "L'humidité suinte le long des pierres froides.",
        ])

        class FauxNarrateur(Fournisseur):
            def _appeler(self, demande):
                appels.append(copy.deepcopy(demande.entree))
                return Reponse(arguments={"texte": next(reponses)}, brut={}, utilisation={})

        texte = narrer(FauxNarrateur(), m, "observer la salle", "Tu observes la salle.")
        self.assertEqual(len(appels), 2)
        attendus = " ".join(o["attendu"] for o in appels[1]["controle_narratif"])
        self.assertIn("« 3 »", attendus)
        self.assertEqual(texte, "L'humidité suinte le long des pierres froides.")

    def test_liste_marchandises_sans_pnj_n_invente_pas_de_locuteur(self):
        from donjon.compilateur import _liste_marchandises

        # 1) 0 PNJ : constat sans locuteur ni guillemets, état du monde inchangé
        m0 = nouveau_monde()
        m0.joueur["salle"] = m0.joueur["position_salle"] = "echoppe"
        m0.objets["marchand"]["lieu"] = m0.objets["marchand"]["position_salle"] = "antichambre"
        avant0 = copy.deepcopy(m0.data)
        res0 = _liste_marchandises(m0)
        self.assertIsNotNone(res0)
        self.assertNotIn("marchand", res0["texte"].lower())
        self.assertNotIn("«", res0["texte"])
        self.assertTrue(res0["texte"].startswith("Articles en vente ici :"))
        self.assertEqual(m0.data, avant0)

        # 2) 1 PNJ non vendeur (mendiant présent, marchand absent) : aucun locuteur, le mendiant ne parle pas
        m1 = nouveau_monde()
        m1.joueur["salle"] = m1.joueur["position_salle"] = "echoppe"
        m1.objets["marchand"]["lieu"] = m1.objets["marchand"]["position_salle"] = "antichambre"
        m1.objets["mendiant"] = objet("mendiant", "un mendiant", "personnage", "echoppe", genre="m", mobile=False)
        avant1 = copy.deepcopy(m1.data)
        res1 = _liste_marchandises(m1)
        self.assertNotIn("«", res1["texte"])
        self.assertNotIn("mendiant", res1["texte"].lower())
        self.assertNotIn("homme", res1["texte"].lower())
        self.assertTrue(res1["texte"].startswith("Articles en vente ici :"))
        self.assertEqual(m1.data, avant1)

        # 3) 1 PNJ vendeur présent : le vendeur parle
        m2 = nouveau_monde()
        m2.joueur["salle"] = m2.joueur["position_salle"] = "echoppe"
        avant2 = copy.deepcopy(m2.data)
        res2 = _liste_marchandises(m2)
        self.assertTrue(res2["texte"].startswith("Gorm le marchand : « "))
        self.assertIn("pied-de-biche : 11 pièces", res2["texte"])
        self.assertEqual(m2.data, avant2)

        # 4) 2 PNJ présents dont un seul est vendeur : le vendeur parle, l'autre non
        m3 = nouveau_monde()
        m3.joueur["salle"] = m3.joueur["position_salle"] = "echoppe"
        m3.objets["mendiant"] = objet("mendiant", "un mendiant", "personnage", "echoppe", genre="m", mobile=False)
        avant3 = copy.deepcopy(m3.data)
        res3 = _liste_marchandises(m3)
        self.assertTrue(res3["texte"].startswith("Gorm le marchand : « "))
        self.assertNotIn("mendiant", res3["texte"].lower())
        self.assertEqual(m3.data, avant3)

    def test_drapeau_narration_seul_garde_action_monolithique_et_decouple_active_compilateur(self):
        import jeu
        from donjon.fournisseurs.contrat import Fournisseur, Reponse

        appels_action = []
        appels_narration = []

        class EspionAction(Fournisseur):
            def _appeler(self, demande):
                appels_action.append(demande.fonction)
                if demande.fonction == "repondre_au_joueur":
                    return Reponse(
                        arguments={
                            "mode": "action",
                            "texte": "",
                            "faits": ["joueur"],
                            "proposition": proposition("prendre", "cle"),
                        },
                        brut={},
                        utilisation={},
                    )
                if demande.fonction == "auditer_action":
                    return Reponse(
                        arguments={"conforme": True, "motif": ""},
                        brut={},
                        utilisation={},
                    )
                if demande.fonction == "compiler_intention":
                    return Reponse(
                        arguments={
                            "action": "prendre",
                            "cible": "cle",
                            "outil": "",
                            "avec": "",
                            "methode": "",
                            "direction": "",
                            "texte": "",
                            "sujet_parole": "",
                            "contenu": [],
                        },
                        brut={},
                        utilisation={"entree": 10, "sortie": 5},
                    )
                return Reponse(arguments={}, brut={}, utilisation={})

        class EspionNarration(Fournisseur):
            def _appeler(self, demande):
                appels_narration.append(demande.fonction)
                return Reponse(
                    arguments={"texte": "Le métal froid de la clé te glace la paume."},
                    brut={},
                    utilisation={},
                )

        def faux_creer(nom):
            return EspionNarration() if nom == "mimo" else EspionAction()

        # Cas 1 : --connexion api --narration mimo (sans --decouple, --action, ni local)
        # -> pipeline d'action monolithique (repondre_au_joueur + auditer_action, jamais compiler_intention),
        #    mais ambiance écrite par le fournisseur de narration (narrer_ambiance).
        with tempfile.TemporaryDirectory() as tmp:
            f1 = Path(tmp) / "narration_seule.json"
            sortie1 = io.StringIO()
            with patch.dict("os.environ", {"OPENAI_API_KEY": "cle-test", "MIMO_API_KEY": "cle-mimo"}), \
                 patch("donjon.mj.creer_fournisseur", side_effect=faux_creer), \
                 patch("builtins.input", side_effect=["mj je prends la clé", "quitter"]), \
                 patch("sys.stdout", sortie1):
                self.assertEqual(
                    jeu.main(["--console", "--connexion", "api", "--narration", "mimo", "--save", str(f1)]),
                    0,
                )
            reprise1 = Monde.charger(f1)

        self.assertNotIn("compiler_intention", appels_action)
        self.assertIn("repondre_au_joueur", appels_action)
        self.assertIn("auditer_action", appels_action)
        self.assertEqual(appels_narration, ["narrer_ambiance"])
        self.assertEqual(reprise1.objets["cle"]["lieu"], "joueur")
        self.assertEqual(
            [a["texte"] for a in reprise1.data["ambiances"]["antichambre"]],
            ["Le métal froid de la clé te glace la paume."],
        )

        # Cas 2 : avec --decouple, le compilateur d'intention est appelé
        appels_action.clear()
        appels_narration.clear()
        with tempfile.TemporaryDirectory() as tmp:
            f2 = Path(tmp) / "decouple.json"
            sortie2 = io.StringIO()
            with patch.dict("os.environ", {"OPENAI_API_KEY": "cle-test", "MIMO_API_KEY": "cle-mimo"}), \
                 patch("donjon.mj.creer_fournisseur", side_effect=faux_creer), \
                 patch("builtins.input", side_effect=["mj je prends la clé", "quitter"]), \
                 patch("sys.stdout", sortie2):
                self.assertEqual(
                    jeu.main(["--console", "--connexion", "api", "--narration", "mimo", "--decouple", "--save", str(f2)]),
                    0,
                )
            reprise2 = Monde.charger(f2)

        self.assertEqual(appels_action, ["compiler_intention"])
        self.assertEqual(appels_narration, ["narrer_ambiance"])
        self.assertEqual(reprise2.objets["cle"]["lieu"], "joueur")
        self.assertEqual(
            [a["texte"] for a in reprise2.data["ambiances"]["antichambre"]],
            ["Le métal froid de la clé te glace la paume."],
        )


if __name__ == "__main__":
    unittest.main()
