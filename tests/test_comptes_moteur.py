"""Les comptes ont un texte moteur exact, y compris après trois récits refusés."""
import copy
import unittest

from donjon.biens import compte
from donjon.comptes_narratifs import completer, controler, phrases
from donjon.narration import segments_etablis
from donjon.rendu import decrire_comptes
from tests.consentement_support import jouer
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class ComptesMoteurTests(unittest.TestCase):
    def test_repli_reel_et_autre_creancier_sans_audit_comptable(self):
        for script, qui in (("comptes", "marchand"), ("soir-appel", "aubin")):
            with self.subTest(script=script):
                m = recharger(banc(script))
                avant = m.joueur["or"]
                mots = "Rends-moi les deux pièces dues."
                # Luna ne reçoit plus la rédaction de ce compte typé. Les
                # réponses supplémentaires ne doivent jamais être consommées.
                libre = "Tu me rends les deux pièces."
                r, sortie, appels = jouer(m, mots, [
                    parole(mots, ("reclamer", "", "", ""), personnage=qui),
                    *[dialogue(libre) for _ in range(3)]], [])
                self.assertEqual(r.joueur["or"], avant + 2)
                self.assertFalse(any(d["de"] == qui for d in r.data["dettes"]))
                self.assertNotIn(libre, sortie)
                self.assertFalse(any(f == "auditer_narration" for f, _ in appels))
                from donjon.emissions import pnj
                moteur = pnj(r)[-1]
                self.assertEqual(moteur['texte'], 'Je te rends 2 pièces.')
                self.assertIn(moteur['rendu_public'], sortie)
                self.assertIn(moteur['rendu_public'], str(r.data['narrations_mj']))
                self.assertIn(moteur['texte'], str(recharger(r).data['conversation']))
                self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 1)
                self.assertEqual(recharger(r).data, r.data)
                self.assertEqual(decrire_comptes(recharger(r)), decrire_comptes(r))

    def test_preuve_recalculee_et_aucune_inference_de_nom(self):
        faits = {"comptes": {"issue": [compte("personne_9", "joueur", montant=7, etat="rendu")]},
                 "interlocuteurs": {"personne_9": {"nom": "la voix grave"}}}
        avant = copy.deepcopy(faits)
        texte = completer("", faits)
        self.assertIn("la voix grave", texte.lower())
        self.assertNotIn("personne_9", texte)
        self.assertFalse(controler(texte, faits))
        self.assertTrue(segments_etablis(texte, faits))
        for modifie in (texte.replace("7", "8"), texte.replace("te rend", "lui rend"),
                        "« Je te rends sept pièces. »"):
            with self.subTest(texte=modifie):
                self.assertTrue(controler(modifie, faits))
                self.assertNotIn("0", segments_etablis(modifie, faits))
        self.assertEqual(faits, avant)

    def test_presence_exigee_pour_tous_les_etats_et_sens(self):
        for etat in ("du", "rendu", "absent"):
            for de, vers in (("joueur", "personne_3"), ("personne_3", "joueur")):
                with self.subTest(etat=etat, de=de):
                    faits = {"comptes": {"issue": [compte(de, vers, montant=2, etat=etat)]}}
                    texte = completer("", faits)
                    self.assertFalse(controler(texte, faits))
                    self.assertTrue(controler("D’accord.", faits))
                    self.assertEqual(completer(texte, faits), texte)


if __name__ == "__main__":
    unittest.main()
