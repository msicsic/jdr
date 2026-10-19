import copy
import io
import json
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import patch

import jeu
from donjon.commandes import analyser
from donjon.comparaison import Comparateur
from donjon.dialogues import commande_sociale, preparer_conversation
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire_accords
from donjon.transactions import du_type


def conversation(operation="proposer", montant=0, acteur="marchand", mission="anneau_veilleur", sujet="Quelle récompense pour l'anneau ?"):
    return {"personnage": acteur, "sujet": sujet, "operation": operation, "mission": mission, "montant_demande": montant}


def reponse(p):
    return {"mode": "conversation_pnj", "texte": "", "faits": ["interlocuteurs", "missions_discutables"], "proposition": p}


def dialogue(texte='Gorm : « Je te propose 20 pièces quand tu me remettras l’anneau. »'):
    return {"mode": "dialogue", "texte": texte, "faits": ["conversation_validee"],
            "proposition": None, "_texte_moteur": True}


class DialoguesTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        self.m.joueur["salle"] = "echoppe"

    def parler(self, operation="proposer", montant=0):
        self.m, rapport = preparer_conversation(self.m, conversation(operation, montant))
        return rapport

    def porter_anneau(self):
        self.m.objets["anneau"]["lieu"] = "joueur"

    def test_negociation_sans_personnage_explique_la_commande(self):
        with self.assertRaisesRegex(ErreurMonde, "Précise le personnage"):
            commande_sociale(self.m, "negocier 25")

    def test_offre_negociation_accord_rechargement_paiement_unique(self):
        self.parler()
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"], {"statut": "propose", "montant": 20})
        self.assertEqual(self.m.joueur["or"], 24)
        self.parler("negocier", 40)
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"]["montant"], 22)
        self.parler("accepter")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            self.m.sauver(path)
            self.m = Monde.charger(path)
        self.porter_anneau()
        moteur = Moteur(self.m)
        texte = moteur.executer(moteur.preparer(analyser(self.m, "remettre anneau à Gorm")))
        self.assertIn("22 pièces", texte)
        self.assertEqual(self.m.joueur["or"], 46)
        self.assertEqual(self.m.data["finances_pnj"]["marchand"], 28)
        self.assertEqual(self.m.objets["anneau"]["lieu"], "marchand")
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"]["statut"], "paye")
        self.assertIn("récompense payée", decrire_accords(self.m))
        avant = copy.deepcopy(self.m.data)
        with self.assertRaises(ErreurMonde):
            moteur.preparer(proposition("remettre", "anneau", "marchand"))
        with self.assertRaises(ErreurMonde):
            moteur.preparer(proposition("prendre", "anneau"))
        self.assertEqual(self.m.data, avant)
        self.parler()
        self.assertEqual(self.m.joueur["or"], 46)
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"]["statut"], "paye")

    def test_contre_offre_stable_et_pas_de_renegociation_apres_acceptation(self):
        self.parler("negocier", 100)
        for _ in range(5):
            self.parler("negocier", 100)
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"]["montant"], 22)
        self.assertEqual(self.m.data["jets"], 0)
        self.parler("accepter")
        self.parler("negocier", 5)
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"], {"statut": "accepte", "montant": 22})

    def test_charisme_et_fonds_bornent_negociation(self):
        self.m.joueur["stats"]["CHA"] = 20
        self.m.data["finances_pnj"]["marchand"] = 26
        self.parler("negocier", 999)
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"]["montant"], 26)
        autre = nouveau_monde()
        autre.joueur["salle"] = "echoppe"
        autre.data["finances_pnj"]["marchand"] = 19
        travail, rapport = preparer_conversation(autre, conversation())
        self.assertFalse(travail.data["engagements"])
        self.assertIn("argent nécessaire", rapport["faits"][0])

    def test_plusieurs_missions_ne_reservent_pas_les_memes_fonds(self):
        self.m.data["finances_pnj"]["marchand"] = 30
        self.parler()
        self.m.data["missions"]["cle"] = {**self.m.data["missions"]["anneau_veilleur"], "objet": "cle"}
        travail, rapport = preparer_conversation(self.m, conversation(mission="cle"))
        self.assertNotIn("cle", travail.data["engagements"])
        self.assertIn("argent nécessaire", rapport["faits"][0])

    def test_aucun_paiement_sans_accord_objet_et_presence(self):
        self.porter_anneau()
        with self.assertRaises(ErreurMonde):
            Moteur(self.m).preparer(proposition("remettre", "anneau"))
        self.parler()
        with self.assertRaises(ErreurMonde):
            Moteur(self.m).preparer(proposition("remettre", "anneau"))
        self.parler("accepter")
        self.m.joueur["salle"] = "antichambre"
        with self.assertRaises(ErreurMonde):
            Moteur(self.m).preparer(proposition("remettre", "anneau", "marchand"))
        self.m.joueur["salle"] = "echoppe"
        self.m.objets["anneau"]["lieu"] = "coffre"
        with self.assertRaises(ErreurMonde):
            Moteur(self.m).preparer(proposition("remettre", "anneau", "marchand"))
        self.assertEqual(self.m.joueur["or"], 24)

    def test_refus_ne_paie_pas_et_ne_cree_pas_un_accord_accepte(self):
        self.parler()
        self.parler("refuser")
        self.assertEqual(self.m.data["engagements"]["anneau_veilleur"]["statut"], "refuse")
        with self.assertRaises(ErreurMonde):
            self.parler("accepter")

    def test_pas_de_dialogue_a_distance_ni_de_budget_prive_dans_le_contexte(self):
        contexte = self.m.contexte()
        self.assertIn("marchand", contexte["interlocuteurs"])
        self.assertNotIn("prime_plafond", json.dumps(contexte))
        self.assertNotIn("finances_pnj", contexte)
        self.m.joueur["salle"] = "antichambre"
        self.assertFalse(self.m.contexte()["interlocuteurs"])
        with self.assertRaises(ErreurMonde):
            self.parler()

    def test_autre_pnj_et_mission_sans_replique_de_gorm(self):
        self.m.objets["mira"] = objet("mira", "Mira", "personnage", "echoppe")
        self.m.data["finances_pnj"]["mira"] = 12
        self.m.data["missions"]["cle_mira"] = {"donneur": "mira", "objet": "cle", "nom": "Apporter la clé",
            "condition": "Remettre la clé à Mira.", "prime_base": 5, "prime_plafond": 10}
        travail, rapport = preparer_conversation(self.m, conversation(acteur="mira", mission="cle_mira"))
        self.assertEqual(rapport["engagement"]["montant"], 5)
        self.assertEqual(rapport["personnage"], "mira")
        self.assertEqual(travail.data["finances_pnj"]["marchand"], 50)

    def test_migration_n_ecrase_pas_progression_et_ne_remplit_pas_la_bourse(self):
        ancien = copy.deepcopy(self.m.data)
        for cle in ("engagements", "dialogues_pnj", "finances_pnj", "missions", "dialogues_version"):
            ancien.pop(cle)
        ancien["joueur"]["or"] = 7
        migre = Monde(ancien)
        self.assertEqual(migre.joueur["or"], 7)
        migre.data["finances_pnj"]["marchand"] = 2
        recharge = Monde(copy.deepcopy(migre.data))
        self.assertEqual(recharge.data, migre.data)

    def test_achat_credite_bourse_du_marchand(self):
        moteur = Moteur(self.m)
        moteur.executer(moteur.preparer(analyser(self.m, "acheter marteau")))
        self.assertEqual(self.m.joueur["or"] + self.m.data["finances_pnj"]["marchand"], 74)

    def test_rejet_atomique_revision_montant_et_personnage_invalides(self):
        for p in ({**conversation(), "montant_demande": True}, conversation("negocier", -1), conversation(acteur="porte"),
                  conversation(mission="invente"), {**conversation(), "or": 999}):
            avant = copy.deepcopy(self.m.data)
            with self.assertRaises(ErreurMonde):
                preparer_conversation(self.m, p)
            self.assertEqual(self.m.data, avant)
        with self.assertRaises(ErreurMonde):
            preparer_conversation(self.m, conversation(), revision=999)

    def test_question_exacte_transmise_puis_reponse_sur_accord_valide(self):
        question = "je demande a gorn ce que j'y gagne a retrouver cet anneau"
        avant = copy.deepcopy(self.m.data)
        def appel(instructions, entree, intention, fonction, schema):
            self.assertEqual(entree["message"], question)
            if "conversation_validee" not in entree["faits"]:
                return reponse(conversation(sujet=question))
            rapport = entree["faits"]["conversation_validee"]
            self.assertEqual(rapport["sujet"], question)
            self.assertEqual(rapport["engagement"], {"statut": "propose", "montant": 20})
            return dialogue()
        with patch.object(MJOpenAI, "_appeler", side_effect=appel) as api:
            r = MJOpenAI().echanger(self.m, question)
        self.assertEqual(api.call_count, 2)
        self.assertIsNotNone(du_type(r, "conversation_pnj"))
        self.assertEqual(self.m.data, avant)

    def test_question_ne_peut_pas_accepter_et_panne_narration_ne_cree_pas_offre(self):
        # Le refus est d'abord recadré : le MJ reçoit son attendu et peut corriger une fois.
        for message, sorties in (("Puis-je accepter ?", [reponse(conversation("accepter"))] * 2),
                                 ("Je demande la récompense", [reponse(conversation()), ErreurMonde("Réseau")])):
            avant = copy.deepcopy(self.m.data)
            with patch.object(MJOpenAI, "_appeler", side_effect=sorties), self.assertRaises(ErreurMonde):
                MJOpenAI().echanger(self.m, message)
            self.assertEqual(self.m.data, avant)

    def test_discussion_sans_contrat_recoit_des_consignes_de_redaction_seulement(self):
        question = "Comment ouvrir la porte verrouillée au nord de l'antichambre ?"
        def appel(instructions, entree, intention, fonction, schema):
            if "conversation_validee" not in entree["faits"]:
                return reponse(conversation("discuter", mission="", sujet=question))
            self.assertEqual(entree["faits"]["conversation_validee"]["faits"], [])
            self.assertIn("objet:crochets", entree["faits"])
            self.assertNotIn("texte reste vide", instructions)
            self.assertNotIn("Mode action", instructions)
            self.assertNotIn("Mode enrichir", instructions)
            self.assertIn("doit quand même répondre", instructions)
            self.assertEqual(schema["properties"]["mode"]["enum"], ["dialogue"])
            self.assertEqual(schema["properties"]["proposition"], {"type": "null"})
            self.assertEqual(schema["properties"]["texte"]["minLength"], 1)
            return dialogue('Gorm : « Tu peux essayer des crochets. »')
        avant = copy.deepcopy(self.m.data)
        with patch.object(MJOpenAI, "_appeler", side_effect=appel):
            r = MJOpenAI().echanger(self.m, question)
        self.assertIn("crochets", r["texte"])
        self.assertEqual(self.m.data, avant)

    def test_dialogue_vide_et_action_erreurs_distinctes_sans_engagement(self):
        for resultat, erreur in (
            (dialogue(""), "dialogue vide"),
            (dialogue(" \n\t"), "dialogue vide"),
            ({"mode": "action", "texte": "", "faits": [], "proposition": proposition("prendre", "cle")}, "réponse finale"),
        ):
            with self.subTest(resultat=resultat):
                avant = copy.deepcopy(self.m.data)
                traces = []
                mj = MJOpenAI()
                mj.observateur = traces.append
                with patch.object(mj, "_appeler", side_effect=[reponse(conversation()), resultat]), self.assertRaisesRegex(ErreurMonde, erreur):
                    mj.echanger(self.m, "Gorm, quelle récompense ?")
                self.assertEqual(traces[-1]["reponse"], resultat)
                self.assertEqual(self.m.data, avant)

    def test_boucle_jeu_persiste_sujet_et_contrat(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            self.m.sauver(path)
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "_appeler", side_effect=[reponse(conversation()), dialogue()]), patch("builtins.input", side_effect=["je demande a gorn ce que j'y gagne a retrouver cet anneau", "accepter offre", "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                jeu.main(["--console", "--connexion", "api", "--save", str(path)])
            recharge = Monde.charger(path)
            self.assertIn("Je te propose 20 pièces", sortie.getvalue())
            self.assertNotIn("Un bon levier", sortie.getvalue())
            self.assertEqual(recharge.data["engagements"]["anneau_veilleur"]["statut"], "accepte")

    def test_comparateur_ne_melange_pas_les_deux_accords(self):
        fini = Event()
        c = Comparateur(MJOpenAI("principal"), MJOpenAI("secondaire"),
                        publier=lambda f: fini.set() if f["secondaire"]["statut"] == "Terminé" else None)
        avant = copy.deepcopy(self.m.data)
        try:
            with patch.object(c.principal, "_appeler", side_effect=[reponse(conversation()), dialogue()]), patch.object(c.secondaire, "_appeler", side_effect=[reponse(conversation("negocier", 30)), dialogue('Gorm : « 22 pièces. »')]):
                r = c.echanger(self.m, "Combien ?")
                self.assertTrue(fini.wait(2))
            self.assertEqual(du_type(r, "conversation_pnj")["rapport"]["engagement"]["montant"], 20)
            self.assertEqual(du_type(c.fiches[1]["secondaire"]["reponse"], "conversation_pnj")["rapport"]["engagement"]["montant"], 22)
            self.assertEqual(self.m.data, avant)
        finally:
            c.fermer()


if __name__ == "__main__":
    unittest.main()
