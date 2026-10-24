"""Une perception est un geste complet ; son résultat n'est pas une ambiance."""
import copy
import unittest
from unittest.mock import patch

from donjon.couverture_action import entree
from donjon.moteur import Moteur, PERCEPTIONS, Plan, proposition
from donjon.rendu import regarder
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_ecoute import au_palier, parler_pendant
from tests.test_relances_luna import action
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import relais


class PerceptionGesteTests(unittest.TestCase):
    def test_les_operations_de_perception_sont_declarees_meme_sans_effet_immediat(self):
        # Pas de liste parallèle dans les revues ; même contrat dans une étape.
        for geste in PERCEPTIONS:
            with self.subTest(geste=geste):
                p = Plan(proposition(geste), 0, "Percevoir.")
                self.assertTrue(p.realise_geste)
                self.assertEqual(entree("je cherche", p)["plan"]["perception"],
                                 {"action": geste, "cible": ""})
                compose = Plan({"action": "composer"}, 0, "Chercher.", plans=[p])
                self.assertTrue(compose.realise_geste)
                self.assertIn("perception", entree("je cherche", compose)["plan"]["etapes"][0])
        self.assertFalse(Plan(proposition("attendre"), 0, "Attendre.").realise_geste)

    def test_ecouter_et_chercher_passent_la_revue_du_premier_coup_et_sont_sauves(self):
        for saisie, p in (("j'écoute à la porte pour savoir s'il y a quelque chose derrière",
                           proposition("ecouter")),
                          ("je cherche des traces de pas sur le sol", proposition("observer", "scene"))):
            with self.subTest(saisie=saisie):
                m = au_palier(relais(), (0, 3))
                parler_pendant(m)
                avant = copy.deepcopy(m.data)
                # Le fournisseur simulé accepte une opération de perception explicite,
                # pas un plan vide réputé conforme sans lire son dossier.
                from donjon.mj import MJOpenAI
                original = MJOpenAI._auditer_action
                def revue(mj, intention, plan, revision, monde):
                    dossier = entree(intention, plan, monde)["plan"]
                    self.assertEqual(dossier["perception"]["action"], p["action"])
                    self.assertEqual(dossier["perception"]["cible"], p["cible"])
                    return original(mj, intention, plan, revision, monde)
                with patch.object(MJOpenAI, "_auditer_action", revue):
                    r, texte, appels = jouer(m, "mj " + saisie, [action(p)], [])
                self.assertEqual([f for f, _ in appels], ["repondre_au_joueur", "auditer_action"])
                resultat = r.data["conversation"][-1]
                self.assertEqual(resultat["nature"], "resultat_moteur")
                self.assertIn(resultat["reponse"], texte)
                self.assertEqual(r.joueur["position"], avant["joueur"]["position"])
                if p["action"] == "ecouter":
                    self.assertEqual(r.data["minutes"], avant["minutes"] + 3)
                    self.assertEqual(r.data["journal"][-1]["action"]["action"], "ecouter")
                    self.assertIn("Tu tends l'oreille contre la porte étanche du beffroi.", texte)
                    self.assertIn("Tu entends une voix à l'ouest.", texte)
                else:
                    self.assertEqual(r.data["minutes"], avant["minutes"])
                    self.assertEqual(resultat["reponse"], regarder(r).strip())
                    self.assertNotIn("aucune trace", texte)

    def test_une_perception_corrigee_ne_devient_pas_un_geste_vide(self):
        m = au_palier(relais(), (0, 3))
        r, texte, appels = jouer(m, "mj j'écoute à la porte", [
            action(proposition("ecouter", "porte_etanche")),
            action(proposition("ecouter"))], [])
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
        self.assertEqual(r.data["minutes"], m.data["minutes"] + 3)
        self.assertEqual(r.data["journal"][-1]["action"]["action"], "ecouter")
        self.assertIn("rien de particulier ne te parvient", texte)
        self.assertNotIn("aucun effet", texte)

    def test_un_resultat_sans_perception_est_refuse_et_une_ambiance_persiste(self):
        for resultat in ("Aucun son de l'autre côté ne t'est perceptible.",
                         "Tu ne trouves aucune trace de pas sur le sol."):
            with self.subTest(resultat=resultat):
                m = au_palier(relais(), (0, 3))
                ambiance = "Une odeur de pierre humide flotte autour de toi."
                r, texte, appels = jouer(m, "mj dis-moi ce que tu remarques", [
                    dialogue(resultat), dialogue(ambiance)], [
                    rapport(ligne("mecanique", motif="Résultat de perception sans source.")),
                    rapport(ligne("ambiance", entites=["odeur de pierre humide"]))])
                self.assertNotIn(resultat, texte)
                self.assertIn(ambiance, texte)
                self.assertEqual(r.data["minutes"], m.data["minutes"])
                self.assertEqual(r.data["journal"], m.data["journal"])
                self.assertEqual(r.data["ambiances"][m.joueur["salle"]][-1]["texte"], ambiance)
                self.assertNotIn(resultat, str(r.data["conversation"]))
                self.assertEqual(sum(f == "auditer_narration" for f, _ in appels), 2)


if __name__ == "__main__":
    unittest.main()
