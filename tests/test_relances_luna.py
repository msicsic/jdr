"""Moins de relances de Luna, sans rien perdre de ce que le contrôle garantit (branche
``relances-luna``). Les bancs de référence montraient des appels qui ne pouvaient rien changer :

- un avis (« impossible », « clarifier ») que la boucle de décision refusera avant de le lire était
  d'abord audité, et relancé pour sa prose (« le moteur… ») ;
- la contre-revue refusait la perception que le moteur venait de prescrire pour chercher quelque chose
  (« je cherche des traces de pas sur le sol » : examiner le sol, 9 appels) ;
- les règles que le contrôle déterministe applique au texte (deuxième personne, pas de « je » hors des
  répliques) n'étaient dites nulle part au MJ.

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


class ConsignesTests(unittest.TestCase):
    def test_la_regle_du_texte_affiche_est_dite_au_mj(self):
        # Le contrôle déterministe refuse « je » hors des répliques et les mots d'auteur : la règle est dite.
        for mot in ("« je »", "Corvus", "moteur", "deuxième personne"):
            self.assertIn(mot, REGLE_NARRATION)

    def test_la_contre_revue_admet_la_perception_qui_cherche(self):
        self.assertIn("Chercher,\nfouiller ou inspecter", REVUE)


if __name__ == "__main__":
    unittest.main()
