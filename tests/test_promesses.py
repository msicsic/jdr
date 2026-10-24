"""Un don clairement exprimé aboutit ; une explication de refus ne fait parler personne ; une
réplique de PNJ ne promet que ce que le moteur a prévu.

Cas d'une partie (sauvegarde du défi, révisions 188-189 et 240-422) : « je donne la cloche a
Gorm » partait au MJ ; l'explication du refus faisait parler Gorm ; Brune répondait « Je vais me
pousser » sans que rien ne la fasse bouger, et le MJ le rappelait ensuite comme acquis.
"""
from tests.support import presentes
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.esprits import esprit
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.narration import citations_nouvelles, controler
from donjon.paroles import esprits_interlocuteurs


def refuge():
    """Le refuge du Relais, hors cases : Brune, Ilse et Aubin présents, la besace de départ."""
    return presentes(nouveau_defi(1985, "fixe"))


def aupres_de_gorm():
    """Cas de la partie : la cloche rapportée, Gorm à côté du joueur, aucune mission au Relais."""
    m = presentes(nouveau_defi(1985, "fixe"))
    m.joueur["salle"] = m.objets["marchand"]["lieu"]
    m.objets["cloche"]["lieu"] = "joueur"
    return m


def jouer(monde, saisies, brut=None):
    """La boucle de la console, MJ actif ; sans ``brut``, tout appel au modèle fait échouer le test.
    Renvoie la partie rechargée et ce qui a été affiché."""
    with tempfile.TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "partie.json"
        monde.sauver(chemin)
        appel = brut or AssertionError("Appel au modèle inattendu")
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                patch.object(MJOpenAI, "_appeler_brut", side_effect=appel), \
                patch.object(MJOpenAI, "_auditer_action"), \
                patch("builtins.input", side_effect=[*saisies, "quitter"]), \
                patch("sys.stdout", io.StringIO()) as sortie:
            jeu.main(["--console", "--connexion", "api", "--save", str(chemin)])
        return Monde.charger(chemin), sortie.getvalue()


def ligne(verdict, sources=(), locuteur="", citation="", entites=()):
    return {"portee_mecanique": "aucune", "verdict": verdict, "sources": list(sources), "locuteur": locuteur, "citation": citation,
            "entites": list(entites), "motif": ""}


def audit(*lignes):
    return {"segments": {str(i): l for i, l in enumerate(lignes)}}


def simulateur(reponses, audits):
    """Réponses du MJ et rapports de l'auditeur, chacun dans l'ordre de ses appels."""
    reponses, audits = list(reponses), list(audits)

    def appeler(instructions, entree, intention, fonction, schema):
        if fonction == "auditer_narration":
            return audits.pop(0)
        if fonction == "repondre_au_joueur":
            return reponses.pop(0)
        raise AssertionError("Appel inattendu : " + fonction)
    return appeler


def dialogue(texte):
    return {"mode": "dialogue", "texte": texte, "faits": [], "proposition": None}


def parole(personnage, replique):
    return {"mode": "parole_joueur", "texte": "", "faits": [],
            "proposition": {"personnage": personnage, "replique": replique,
                            "contenu": [{"type": "propos", "sujet": "", "attribut": "", "valeur": ""}]}}


class DonLocalTests(unittest.TestCase):
    def test_formes_du_verbe_donner(self):
        m = aupres_de_gorm()
        for phrase in ("je donne la cloche a Gorm", "Je donne la cloche à Gorm", "je remets la cloche à Gorm",
                       "donne la cloche a gorm", "donner cloche à Gorm", "remettre la cloche d'alarme au gardien",
                       "je donne à Gorm la cloche", "je donne au gardien la cloche"):
            with self.subTest(phrase=phrase):
                p = analyser(m, phrase)
                self.assertEqual((p["action"], p["cible"], p["outil"]), ("remettre", "cloche", "marchand"))
        p = analyser(m, "je donne la cloche")
        self.assertEqual((p["action"], p["cible"], p["outil"]), ("remettre", "cloche", ""))

    def test_ce_qui_n_est_pas_un_don_nomme_va_au_mj(self):
        m = aupres_de_gorm()
        for phrase in ("je donne un coup de pied dans la poutre", "je donne la cloche a Gorm et je pars",
                       "je donne la cloche a Gorm discretement", "je donne une piece a Gorm"):
            with self.subTest(phrase=phrase), self.assertRaises(ErreurMonde):
                analyser(m, phrase)
        self.assertIsNone(analyser(m, "je donne la cloche à Gorm ?"))

    def test_le_don_de_la_cloche_aboutit_sans_appel_au_modele(self):
        recharge, sortie = jouer(aupres_de_gorm(), ["je donne la cloche a Gorm"])
        cloche = recharge.objets["cloche"]
        self.assertEqual((cloche["lieu"], cloche["proprietaire"]), ("marchand", "marchand"))
        self.assertIn("Tu donnes la cloche d'alarme à Gorm", sortie)
        self.assertEqual(recharge.data["conversation"][-1]["nature"], "resultat_moteur")

    def test_un_autre_objet_a_un_autre_personnage(self):
        recharge, sortie = jouer(refuge(), ["je remets le couteau à Brune"])
        self.assertEqual(recharge.objets["couteau"]["lieu"], "brune")
        self.assertIn("Tu donnes le couteau à lame fine à Brune", sortie)
        souvenirs = recharge.data["esprits"]["brune"]["memoire"]
        self.assertTrue(any(s["type"] == "don" and s["objet"] == "couteau" for s in souvenirs))

    def test_un_objet_qu_on_ne_porte_pas_est_refuse_par_le_moteur(self):
        m = aupres_de_gorm()
        m.objets["cloche"]["lieu"] = m.joueur["salle"]
        recharge, sortie = jouer(m, ["je donne la cloche a Gorm"])
        self.assertIn("Tu dois porter l'objet pour le donner.", sortie)
        self.assertEqual(recharge.objets["cloche"]["lieu"], m.joueur["salle"])


class ExplicationDeRefusTests(unittest.TestCase):
    def test_une_parole_nouvelle_est_refusee_meme_si_l_auditeur_la_manque(self):
        # L'auditeur classe la réplique de Gorm en mécanique : le contrôle ne dépend pas de lui.
        faits = {"interlocuteurs": {"marchand": {"nom": "Gorm"}},
                 "retour_moteur": {"proposition_refusee": {"action": "remettre"}, "obstacle": "refus"}}
        texte = "Gorm est à un pas de toi. « Pour me la remettre, dis-le-moi clairement. »"
        sobre = "Gorm ne prend pas encore la cloche : rien ne s'est échangé."
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler_brut", side_effect=[
                dialogue(texte), audit(ligne("mecanique", ["interlocuteurs"]), ligne("mecanique", ["interlocuteurs"])),
                dialogue(sobre), audit(ligne("mecanique", ["interlocuteurs"]))]) as appel:
            reponse = mj._appeler("instr", {"faits": faits, "conversation": [], "message": "je donne la cloche"},
                                  "je donne la cloche", "repondre_au_joueur", {})
        self.assertEqual(reponse["texte"], sobre)
        self.assertEqual(appel.call_count, 4)

    def test_le_rappel_d_une_parole_entendue_reste_permis(self):
        faits = {"paroles_entendues": [{"locuteur": "marchand", "texte": "Rapporte-moi la cloche."}],
                 "retour_moteur": {"proposition_refusee": {}, "obstacle": "refus"}}
        self.assertEqual(citations_nouvelles("Gorm t'a dit : « Rapporte-moi la cloche. »", faits), [])
        self.assertEqual(len(citations_nouvelles("Gorm répond : « Pas maintenant. »", faits)), 1)
        # La proposition refusée ne fait rien dire : sa réplique n'est pas une parole entendue.
        refus = {"retour_moteur": {"proposition_refusee": {"replique": "Pas maintenant."}}}
        self.assertEqual(len(citations_nouvelles("Gorm répond : « Pas maintenant. »", refus)), 1)


class EngagementTests(unittest.TestCase):
    def faits(self, monde, **autres):
        presents = ["brune", "marchand"]
        return {"interlocuteurs": {i: {} for i in presents},
                "esprits_interlocuteurs": esprits_interlocuteurs(monde, presents), **autres}

    def test_un_engagement_sans_issue_enregistree_est_refuse(self):
        texte = "Brune te regarde : « Je vais me pousser. »"
        rapport = controler(texte, audit(ligne("engagement", locuteur="brune", citation="Je vais me pousser.")),
                            self.faits(refuge()))
        self.assertEqual(len(rapport["obstacles"]), 1)
        self.assertEqual(rapport["paroles"], [])
        # Un engagement que le moteur n'a pas enregistré ne se justifie pas en le recopiant.
        rapport = controler(texte, audit(ligne("engagement", locuteur="brune", citation="Je vais me pousser.",
                                               entites=["se pousser"])), self.faits(refuge()))
        self.assertEqual(len(rapport["obstacles"]), 1)

    def test_le_recit_n_annonce_pas_non_plus_ce_qu_il_fera(self):
        rapport = controler("Brune va s'écarter.", audit(ligne("engagement", locuteur="brune")),
                            self.faits(refuge()))
        self.assertEqual(len(rapport["obstacles"]), 1)

    def test_un_engagement_pris_dans_le_moteur_peut_etre_dit(self):
        m = refuge()
        esprit(m, "marchand")["engagements"].append(
            {"condition": {"objet": "brasero", "allume": True}, "pour": "joueur", "minute": 0})
        faits = self.faits(m)
        prevu = "engagement pris envers toi : entretenir le brasero"
        self.assertIn(prevu, faits["esprits_interlocuteurs"]["marchand"]["engagements"])
        texte = "Gorm hoche la tête : « Je garderai le feu allumé. »"
        rapport = controler(texte, audit(ligne("engagement", locuteur="marchand",
                                               citation="Je garderai le feu allumé.", entites=[prevu])), faits)
        self.assertEqual(rapport["obstacles"], [])
        self.assertEqual(rapport["paroles"], [{"locuteur": "marchand", "texte": "Je garderai le feu allumé.", "passage": texte}])

    def test_l_issue_que_le_moteur_vient_de_valider_peut_etre_dite(self):
        accord = "Offre de 20 pièces contre la remise de l'objet. Le joueur ne l'a pas encore acceptée."
        faits = self.faits(refuge(), conversation_validee={"personnage": "marchand", "faits": [accord]})
        texte = "« Je te donnerai vingt pièces pour la cloche. »"
        ok = controler(texte, audit(ligne("engagement", locuteur="marchand", citation=texte[2:-2],
                                          entites=[accord])), faits)
        self.assertEqual(ok["obstacles"], [])
        # Une issue validée pour un autre personnage ne l'engage pas.
        autre = controler(texte, audit(ligne("engagement", locuteur="brune", citation=texte[2:-2],
                                             entites=[accord])), faits)
        self.assertEqual(len(autre["obstacles"]), 1)

    def test_intention_et_accord_de_mission_sont_des_engagements_enregistres(self):
        from donjon.monde import nouveau_monde
        m = nouveau_monde(1985)
        mission = next(iter(m.data["missions"]))
        donneur = m.data["missions"][mission]["donneur"]
        m.data["engagements"][mission] = {"statut": "accepte", "montant": 20}
        esprit(m, donneur)["intention"] = {"but": {"type": "repos"}, "motif": "repos", "plan": []}
        phrases = esprits_interlocuteurs(m, [donneur])[donneur]["engagements"]
        self.assertIn("intention en cours : se reposer", phrases)
        self.assertTrue(any(p.startswith("accord conclu : 20 pièces à la remise de ") for p in phrases))


class PromesseEnPartieTests(unittest.TestCase):
    """La chaîne entière : parole du joueur, réplique contrôlée, sauvegarde et rechargement."""

    def promesse_refusee(self, saisie, locuteur, promesse, reformulee):
        texte = f"{promesse[0]} : « {promesse[1]} »"
        recharge, sortie = jouer(refuge(), [saisie], brut=simulateur(
            [parole(locuteur, saisie), dialogue(texte), dialogue(reformulee[0] + " : « " + reformulee[1] + " »")],
            [audit(ligne("engagement", locuteur=locuteur, citation=promesse[1])),
             audit(ligne("parole", locuteur=locuteur, citation=reformulee[1]))]))
        dites = [p["texte"] for p in recharge.data["paroles_pnj"] if p["locuteur"] == locuteur]
        self.assertNotIn(promesse[1], dites)
        self.assertIn(reformulee[1], dites)
        self.assertNotIn(promesse[1], sortie)
        self.assertIn(reformulee[1], recharge.data["conversation"][-1]["reponse"])
        self.assertEqual(esprit(recharge, locuteur)["engagements"], [])
        return recharge

    def test_brune_ne_promet_pas_de_se_pousser(self):
        recharge = self.promesse_refusee(
            "Brune, pousse-toi s'il te plaît.", "brune",
            ("Brune te regarde", "Je t'entends. Je vais me pousser."),
            ("Brune te regarde sans bouger", "Je t'entends. Pas besoin de me brusquer."))
        self.assertEqual(recharge.objets["brune"]["lieu"], "antichambre")

    def test_ilse_ne_promet_pas_d_apporter_ce_qu_on_lui_demande(self):
        self.promesse_refusee(
            "Ilse, va me chercher de quoi manger.", "ilse",
            ("Ilse acquiesce", "D'accord, je vais te chercher à manger."),
            ("Ilse hésite", "Je ne sais pas où trouver à manger ici."))


if __name__ == "__main__":
    unittest.main()
