"""Moins de relances de Luna, sans rien perdre de ce que le contrôle garantit (branche
``relances-luna``). Les bancs de référence montraient des appels qui ne pouvaient rien changer :

- un avis (« impossible », « clarifier ») que la boucle de décision refusera avant de le lire était
  d'abord audité, et relancé pour sa prose (« le moteur… ») ;
- la contre-revue refusait la perception que le moteur venait de prescrire pour chercher quelque chose
  (« je cherche des traces de pas sur le sol » : examiner le sol, 9 appels) ;
- les règles que le contrôle déterministe applique au texte (deuxième personne, pas de « je » hors des
  répliques) n'étaient dites nulle part au MJ ;
- un nom typé autrement que ne le disent les mots de Corvus était refusé au MJ, alors que le moteur le
  lit lui-même dans les mots (« C'est moi, Brune. ») ;
- une citation recopiée par l'auditeur avec ses mots d'attribution refusait une réplique juste ;
- l'explication d'un geste refusé par le monde (trop loin) était relancée jusqu'à trois fois, alors que
  le refus du monde dit déjà au joueur, exactement, ce qui manque.

Chaque cas vérifie ce que lit le joueur, l'état après rechargement et les appels faits."""
import unittest

from donjon.couverture_action import INSTRUCTIONS as REVUE
from donjon.improvisation import issue, proposition
from donjon.narration import REGLE_NARRATION
from tests.test_audits_attendu import jouer
from tests.test_parole_commune import paroles_retenues, scene
from tests.test_repli_et_appel import NEUTRE, dialogue, mj, parole, verdicts


def action(p):
    return {"mode": "action", "texte": "", "faits": [], "proposition": p}


def avis(nom, justification):
    return action({"action": nom, "cible": "", "outil": "", "methode": "simple", "difficulte": 0,
                   "justification": justification})


def fonctions(appels):
    return [f for f, _ in appels]


class AvisNonLuTests(unittest.TestCase):
    def test_cas_reel_impossible_au_premier_examen_n_est_pas_audite(self):
        # Banc relais : « est-ce que je pourrais passer sous la poutre effondrée ? ». Luna concluait
        # « impossible » avec « le moteur » dans sa justification : audit, refus de la voix d'auteur, relance,
        # puis le même « impossible » refusé par la boucle (réexamen). L'audit ne servait à rien.
        from tests.test_paroles import relais
        m = relais()
        m.joueur["position"] = [6, 2]
        passer = proposition("passer sous la poutre", issue("Tu passes."), cibles=["poutre_conduite"],
                             approche="adresse", stat="DEX", difficulte=12)
        passer["echec"] = issue("Tu restes coincé.")
        reprise, sortie, appels = jouer(m, "est-ce que je pourrais passer sous la poutre effondrée ?", [
            avis("impossible", "Le moteur ne prévoit pas de passer sous une poutre."), action(passer)], [])
        self.assertNotIn("auditer_narration", fonctions(appels))
        self.assertEqual(fonctions(appels).count("repondre_au_joueur"), 2)
        retour = mj(appels)[1]["faits"]["retour_moteur"]
        self.assertTrue(retour["obstacle"].startswith("Réexamine l'intention entière"))
        self.assertIn("Rien n'est encore tenté", sortie)
        self.assertNotIn("moteur", sortie.split("est-ce que je pourrais")[-1].lower())
        self.assertEqual(reprise.data["journal"], [])

    def test_meme_nature_apres_le_reexamen_l_avis_est_audite_et_lu(self):
        # Le réexamen fait, un second « impossible » est lu par le joueur : sa justification passe l'audit.
        from tests.test_paroles import relais
        m = relais()
        m.joueur["position"] = [6, 2]
        reprise, sortie, appels = jouer(m, "je soulève la poutre effondrée à mains nues", [
            avis("impossible", "Rien."), avis("impossible", "Elle est bien trop lourde pour tes seuls bras.")],
            [verdicts(("mecanique", ("attestations",), ""))])
        self.assertEqual(fonctions(appels).count("auditer_narration"), 1)
        self.assertIn("Elle est bien trop lourde pour tes seuls bras.", sortie)
        self.assertEqual(reprise.data["journal"], [])

    def test_meme_nature_un_avis_sur_une_parole_sans_conteste(self):
        # « je dis à Aubin : … » est une parole : un « clarifier » serait refusé (« Corvus le dit »), il n'est
        # pas audité ; la parole proposée ensuite est dite et Aubin y répond.
        m = scene()
        saisie = "je dis à Aubin : il fait froid ce soir"
        reprise, sortie, appels = jouer(m, saisie, [
            avis("clarifier", "Le joueur veut-il parler à Aubin ?"),
            parole("il fait froid ce soir", ("propos", "", "", ""), personnage="aubin"),
            dialogue("Aubin hausse les épaules : « Comme chaque soir de crue. »")],
            [{"segments": {"0": {"verdict": "parole", "sources": [], "locuteur": "aubin",
                                 "citation": "Comme chaque soir de crue.", "entites": [], "motif": ""}}}])
        self.assertEqual(fonctions(appels).count("auditer_narration"), 1)
        self.assertIn("Tu dis à Aubin", sortie)
        self.assertNotIn("Le joueur veut-il", sortie)
        self.assertIn(("joueur", ["aubin"], "il fait froid ce soir"), paroles_retenues(reprise, "aubin"))


class NomTests(unittest.TestCase):
    def test_meme_nature_je_suis_gorm_type_corvus(self):
        # Même nature que « C'est moi, Brune. » (test_parole_corrections) : les mots disent Gorm, Luna type
        # Corvus ; le moteur lit Gorm, sans relance : Corvus ne s'est pas dit Corvus.
        from tests.test_parole_corrections import ImpostureTests as Appel, audit, ligne, narration
        m = Appel().appelee()
        reprise, sortie, appels = jouer(m, "« Je suis Gorm. »", [
            parole("Je suis Gorm.", ("nom", "joueur", "", ""), personnage="voix_1"),
            dialogue("La voix : « Gorm ? Ce n'est pas sa voix. »")],
            [audit(ligne("parole", "voix_1", "Gorm ? Ce n'est pas sa voix."))])
        self.assertEqual(len(mj(appels)), 2)
        faits = narration(appels)["faits"]["conversation_validee"]["faits"]
        self.assertFalse(any("c'est Corvus" in f for f in faits))
        self.assertIn("Tu dis à une voix qui se dit Ilse : « Je suis Gorm. »", sortie)
        from donjon.esprits import lire
        self.assertEqual(lire(reprise, "ilse")["voix_entendues"]["joueur"]["se_dit"], "marchand")


class CitationTests(unittest.TestCase):
    def rapport(self, citation):
        return {"segments": {"0": {"verdict": "parole", "sources": [], "locuteur": "aubin", "citation": citation,
                                   "entites": [], "motif": ""}}}

    def test_cas_reel_la_citation_recopiee_avec_l_attribution(self):
        # Banc soir-noir : l'auditeur citait « C'est Ilse », répond la voix, tout près dans le noir. ; la
        # réplique était refusée (« Une parole doit être citée entre « et », en entier ») et Luna relancée.
        m = scene()
        texte = "« Il gèle, ce soir », répond Aubin, sans lever les yeux."
        reprise, sortie, appels = jouer(m, "je dis à Aubin : il fait froid", [
            parole("il fait froid", ("propos", "", "", ""), personnage="aubin"), dialogue(texte)],
            [self.rapport("Il gèle, ce soir », répond Aubin, sans lever les yeux.")])
        self.assertEqual(fonctions(appels).count("auditer_narration"), 1)
        self.assertIn(texte, sortie)
        self.assertIn(("aubin", "Il gèle, ce soir"),
                      [(p["locuteur"], p["texte"]) for p in reprise.data["paroles_pnj"]])

    def test_meme_nature_une_citation_qui_ne_recouvre_aucune_replique_reste_refusee(self):
        from donjon.narration import controler
        faits = {"interlocuteurs": {"aubin": {}}}
        bon = controler("Aubin grogne : « Pas maintenant. »", self.rapport("« Pas maintenant »"), faits)
        self.assertEqual((bon["obstacles"], bon["paroles"]), ([], [{"locuteur": "aubin", "texte": "Pas maintenant."}]))
        recopie = controler("Aubin grogne : « Pas maintenant. »", self.rapport("grogne : « Pas maintenant. »"), faits)
        self.assertEqual(recopie["paroles"], [{"locuteur": "aubin", "texte": "Pas maintenant."}])
        faux = controler("Aubin grogne : « Pas maintenant. »", self.rapport("Plus tard."), faits)
        self.assertEqual(len(faux["obstacles"]), 1)
        self.assertIn("citée entre « et », en entier", faux["obstacles"][0]["motif"])


def loin_de_la_poutre():
    from tests.test_paroles import relais
    m = relais()
    m.joueur.update(position=[3, 3], orientation="est")
    return m


CONTRADICTOIRE = verdicts(("contradictoire", (), "« Il te faut t'en rapprocher » raconte un geste commencé."))


class ExplicationTests(unittest.TestCase):
    def test_cas_reel_coup_de_pied_trop_loin(self):
        # Banc relais : « je donne un coup de pied dans la poutre », trop loin. L'explication du MJ, refusée par
        # l'auditeur, était relancée (crypte : sept appels pour les crochets) ; le refus du monde répond.
        coup = proposition("coup de pied dans la poutre", issue("Tu frappes la poutre."),
                           cibles=["poutre_conduite"], approche="effort")
        reprise, sortie, appels = jouer(loin_de_la_poutre(), "je donne un coup de pied dans la poutre", [
            action(coup), dialogue("La poutre est trop loin, il te faut t'en rapprocher.")], [CONTRADICTOIRE])
        self.assertEqual(fonctions(appels).count("repondre_au_joueur"), 2)
        self.assertEqual(fonctions(appels).count("auditer_narration"), 1)
        self.assertIn("Approche-toi de la poutre effondrée", sortie)
        self.assertNotIn("Il te faut t'en rapprocher", sortie)
        self.assertNotIn("Je n'ai pas pu", sortie)
        self.assertEqual(reprise.data["journal"], [])
        self.assertEqual(reprise.objets["poutre_conduite"]["integrite"], loin_de_la_poutre().objets["poutre_conduite"]["integrite"])

    def test_meme_nature_attendre_puis_prendre_les_crochets(self):
        prendre = action({"action": "composer", "justification": "", "etapes": [
            {"operation": "patienter", "cible": "", "destination": "", "outil": "", "methode": "simple",
             "difficulte": 0},
            {"operation": "deplacer", "cible": "crochets", "destination": "joueur", "outil": "",
             "methode": "discret", "difficulte": 0}]})
        reprise, sortie, appels = jouer(loin_de_la_poutre(),
                                        "J'attends que Gorm ait le dos tourné pour prendre discrètement les crochets",
                                        [prendre, dialogue("Tu ne peux donc pas la prendre d'ici.")], [CONTRADICTOIRE])
        self.assertEqual(fonctions(appels).count("repondre_au_joueur"), 2)
        self.assertIn("Approche-toi de la trousse de crochets", sortie)
        self.assertNotEqual(reprise.objets["crochets"]["lieu"], "joueur")
        self.assertEqual(reprise.data["journal"], [])

    def test_une_explication_admise_reste_celle_du_mj(self):
        coup = proposition("coup de pied dans la poutre", issue("Tu frappes la poutre."),
                           cibles=["poutre_conduite"], approche="effort")
        _, sortie, appels = jouer(loin_de_la_poutre(), "je donne un coup de pied dans la poutre", [
            action(coup), dialogue("La poutre effondrée est à plusieurs pas de toi.")],
            [verdicts(("mecanique", ("retour_moteur",), ""))])
        self.assertIn("La poutre effondrée est à plusieurs pas de toi.", sortie)
        self.assertNotIn("Approche-toi", sortie)


class ConsignesTests(unittest.TestCase):
    def test_la_regle_du_texte_affiche_est_dite_au_mj(self):
        # Le contrôle déterministe refuse « je » hors des répliques et les mots d'auteur : la règle est dite.
        for mot in ("« je »", "Corvus", "moteur", "deuxième personne"):
            self.assertIn(mot, REGLE_NARRATION)

    def test_l_auditeur_sait_qu_un_temoin_silencieux_est_atteste(self):
        # Banc echanges : « Aubin, qui a entendu ta question sans y être interpellé, garde le silence » était
        # jugé contradictoire, alors que les témoins se taisent par la règle même du moteur.
        from donjon.narration import INSTRUCTIONS_AUDIT
        self.assertIn("dire qu'ils se taisent est mecanique, source conversation_validee",
                      " ".join(INSTRUCTIONS_AUDIT.split()))

    def test_la_contre_revue_admet_la_perception_qui_cherche(self):
        self.assertIn("Chercher,\nfouiller ou inspecter", REVUE)


if __name__ == "__main__":
    unittest.main()
