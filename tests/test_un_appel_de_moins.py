"""Interprétation et contrôle local des opérations, jusqu'à la sauvegarde rechargée."""
from donjon.emissions import joueur as emissions_joueur
import copy
import unittest

from donjon.paroles import OPERATIONS
from donjon.rendu import fiche
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class UnAppelDeMoinsTests(unittest.TestCase):
    def test_mots_exacts_sans_operation_sans_revue(self):
        for saisie, qui in (("bonsoir", "aubin"), ("Ilse, tu m'entends ?", "ilse"),
                           ("Aubin, tu tiens le coup ?", "aubin")):
            with self.subTest(saisie=saisie):
                m = banc("noms-dialogue")
                p = parole(saisie, personnage=qui)
                self.assertEqual(p["proposition"]["operations_demandees"], dict.fromkeys(OPERATIONS, False))
                r, sortie, appels = jouer(m, saisie, [p, dialogue("Ta parole est entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 0)
                self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 2)
                r = recharger(r)
                self.assertEqual(len(emissions_joueur(r)), 1)
                self.assertEqual(emissions_joueur(r)[-1]["texte"], saisie)
                self.assertIn(saisie, sortie)
                self.assertIn("Ta parole est entendue.", str(r.data["conversation"]))
                self.assertEqual(r.joueur["or"], m.joueur["or"])
                self.assertIn(str(r.joueur["or"]), fiche(r))

    def test_declaration_invalide_corrigee_sans_revue(self):
        for mauvaise in (None, {}, {**dict.fromkeys(OPERATIONS, False), "qui": "non"}):
            with self.subTest(mauvaise=mauvaise):
                m = banc("noms-dialogue")
                p = parole("Ilse, tu m'entends ?", personnage="ilse")
                faux = copy.deepcopy(p)
                faux["proposition"]["operations_demandees"] = mauvaise
                r, sortie, appels = jouer(m, "Ilse, tu m'entends ?", [faux, p, dialogue("Ta question est entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 0)
                retours = [e["faits"]["retour_moteur"] for _, e in appels if "retour_moteur" in e.get("faits", {})]
                self.assertIn("operations_demandees", retours[0]["attendu"])
                self.assertNotIn(retours[0]["attendu"], sortie)
                self.assertEqual(len(emissions_joueur(recharger(r))), 1)
                self.assertIn("Ilse, tu m'entends ?", sortie)

    def test_reformulation_typee_garde_la_revue(self):
        for saisie, replique, bien in (("je demande à Aubin s'il a du bois", "As-tu du bois ?", "bois"),
                                      ("je demande à Aubin de quoi manger", "As-tu à manger ?", "faim")):
            with self.subTest(saisie=saisie):
                m = banc("noms-dialogue")
                r, sortie, appels = jouer(m, saisie, [
                    parole(replique, ("ressource", bien, "", ""), personnage="aubin"),
                    dialogue("Ta question est entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))],
                    revues=[{"conforme": True, "motif": "Le bien demandé est conservé."}])
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
                self.assertIn(replique, sortie)
                self.assertEqual(len(emissions_joueur(recharger(r))), 1)
                self.assertEqual(r.joueur["or"], m.joueur["or"])
