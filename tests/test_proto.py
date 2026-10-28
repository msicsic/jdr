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

if __name__ == "__main__":
    unittest.main()
