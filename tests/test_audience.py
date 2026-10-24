"""Une seule adresse, de la saisie à la sauvegarde ; cas du banc et autre scénario."""
import copy
import unittest

from donjon.dialogues import interlocuteurs
from donjon.monde import ErreurMonde
from donjon.paroles import analyser, en_face, preparer_parole, prevue
from donjon.voix import reel
from tests.test_audits_attendu import jouer, rapport, ligne
from tests.test_parole_commune import paroles_retenues
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class AudienceTests(unittest.TestCase):
    def verifier_cantonade(self, m, saisie, besoin):
        avant = copy.deepcopy(m.data)
        attendue = prevue(m, saisie)
        self.assertEqual(attendue["personnage"], "personne")
        self.assertEqual(attendue["destinataires"], [])
        self.assertEqual(m.data, avant)  # La prévision ne prononce rien.
        r, sortie, appels = jouer(m, saisie, [
            parole(saisie, ("ressource", besoin, "", ""), personnage="personne"),
            dialogue("Ta question a été entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))])
        validee = next(e["faits"]["conversation_validee"] for f, e in appels
                       if f == "repondre_au_joueur" and "conversation_validee" in e["faits"])
        self.assertEqual(validee["destinataires"], [])
        self.assertIn(f"Tu dis : « {saisie} »", sortie)
        self.assertNotIn("Précise à qui", sortie)
        p = r.data["paroles_joueur"][-1]
        self.assertEqual((p["auditeur"], p["texte"]), ("personne", saisie))
        self.assertTrue(p["auditeurs"])
        for qui in p["auditeurs"]:
            self.assertEqual(paroles_retenues(r, qui)[-1], ("joueur", [], saisie))
        self.assertIn("Ta question a été entendue.", str(r.data["conversation"]))
        revue = next(e["plan"]["parole"] for f, e in appels if f == "auditer_action")
        self.assertEqual(revue["adresse"], "cantonade")
        self.assertNotIn("audiences_autorisees", revue)
        return r, validee

    def test_cas_reel_trois_presents_et_une_voix_avec_aubin_en_face(self):
        m = banc("noms-dialogue")
        # La voix de l'ouest reste une voix audible ; son identité n'est pas devinée.
        from donjon.paroles import entendre_repondant
        entendre_repondant(m, "marchand")
        m = recharger(m)
        self.assertEqual(en_face(m, [reel(m, x) for x in interlocuteurs(m)]), "aubin")
        r, validee = self.verifier_cantonade(m, "est-ce que quelqu'un a du bois ?", "chaleur")
        self.assertEqual(set(r.data["paroles_joueur"][-1]["auditeurs"]), {"aubin", "brune", "ilse", "marchand"})
        self.assertEqual(len(validee["repondent"]), 4)

    def test_autre_scenario_autres_mots_malgre_un_interlocuteur_en_face(self):
        m = banc("sous-obstacle-auberge")
        m.joueur["orientation"] = "ouest"
        m = recharger(m)
        self.assertIn("lucien", [reel(m, x) for x in interlocuteurs(m)])
        self.verifier_cantonade(m, "Avez-vous de quoi manger ?", "faim")

    def test_une_adresse_contraire_est_refusee_avant_la_revue(self):
        for saisie, cible, faux in (("Aubin, as-tu du bois ?", "aubin", "tous"),
                                    ("je dis à Ilse : bonjour", "ilse", "aubin")):
            with self.subTest(saisie=saisie):
                m = banc("noms-dialogue")
                r, sortie, appels = jouer(m, saisie, [
                    parole("bonjour", personnage=faux), parole("bonjour", personnage=cible),
                    dialogue("Ta parole a été entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                retour = next(e["faits"]["retour_moteur"] for f, e in appels
                              if f == "repondre_au_joueur" and "retour_moteur" in e["faits"])
                self.assertIn(f"personnage = {cible}", retour["attendu"])
                self.assertEqual(r.data["paroles_joueur"][-1]["auditeurs"], [cible])
                self.assertIn("Tu dis à", sortie)
                self.assertNotIn("Précise à qui", sortie)

    def test_la_revue_refuse_encore_un_contenu_contraire(self):
        m = banc("noms-dialogue")
        saisie = "est-ce que quelqu'un a du bois ?"
        r, sortie, appels = jouer(m, saisie, [
            parole(saisie, ("ressource", "faim", "", ""), personnage="personne"),
            parole(saisie, ("ressource", "chaleur", "", ""), personnage="personne"),
            dialogue("Ta question a été entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))],
            revues=[{"conforme": False, "motif": "Du combustible est demandé, pas de la nourriture."},
                    {"conforme": True, "motif": ""}])
        self.assertNotIn("Précise à qui", sortie)
        self.assertEqual(len(r.data["paroles_joueur"]), 1)
        self.assertEqual(r.data["paroles_joueur"][-1]["texte"], saisie)
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 2)

    def test_sans_adresse_ni_question_l_audience_ne_change_pas(self):
        m = banc("noms-dialogue")
        for saisie in ("je dis : bonsoir", "« Bonsoir. »", "Avez-vous faim ?"):
            with self.subTest(saisie=saisie):
                self.assertEqual(prevue(m, saisie)["personnage"], "personne")
                with self.assertRaises(ErreurMonde):
                    preparer_parole(m, {"personnage": "aubin", "replique": "Bonsoir.",
                                        "contenu": [], "_intention": saisie})

    def test_une_intention_nommee_reste_individuelle_sans_devenir_une_parole_forcee(self):
        m = banc("noms-dialogue")
        depart = m.joueur["or"]
        # Propositions initiales de Luna dans la passe du lot : elles ne doivent
        # plus être renvoyées au modèle pour réécrire leur audience.
        cas = [("je réclame à Aubin les deux pièces qu'il me doit", "Aubin, tu me dois deux pièces. Rends-les-moi.",
                ("reclamer", "", "", ""), depart + 2),
               ("je paie Aubin trois pièces pour une de ses planches", "Je te paie trois pièces pour une de tes planches.",
                ("demande", "planches", "", "3"), depart + 2)]
        for saisie, replique, contenu, pieces in cas:
            with self.subTest(saisie=saisie):
                self.assertEqual(prevue(m, saisie)["personnage"], "aubin")
                m, sortie, appels = jouer(m, saisie, [parole(replique, contenu, personnage="aubin"),
                    dialogue("Aubin a entendu ta demande.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                self.assertIn("Tu dis à Aubin", sortie)
                self.assertEqual(m.joueur["or"], pieces)
                self.assertEqual(m.data["paroles_joueur"][-1]["auditeurs"], ["aubin"])
                self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 2)
                if contenu[0] == "demande":
                    faits = next(e["faits"]["conversation_validee"]["faits"] for f, e in appels
                                 if f == "repondre_au_joueur" and "conversation_validee" in e["faits"])
                    self.assertIn("ne voit pas comment", " ".join(faits))
                    self.assertEqual(m.objets["planches"]["charges"], 2)
        for saisie in ("je regarde Aubin", "j'observe Ilse"):
            forme = analyser(m, saisie)
            self.assertFalse(forme["explicite"])
            self.assertIsNone(forme["nomme"])
            self.assertTrue(forme["cible_intention"])

        from donjon.moteur import proposition
        m = banc("noms-dialogue")
        r, sortie, _ = jouer(m, "je regarde Aubin", [{"mode": "action", "texte": "", "faits": [],
            "proposition": proposition("examiner", "aubin")}], [])
        self.assertFalse(r.data.get("paroles_joueur"))
        self.assertIn("Aubin", sortie)
