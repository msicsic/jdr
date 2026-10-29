"""La fidélité lit les termes dans les comptes avant règlement, puis console et recharge."""
import unittest

from donjon.biens import compte, rembourser
from donjon.rendu import fiche
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_comptes_issue import audit
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class ComptesFideliteTests(unittest.TestCase):
    def revue(self, debiteur, montant, conforme=True):
        def verifier(entree):
            dossier = entree["plan"]["parole"]
            comptes = dossier["comptes_avant"]
            c = next(c for c in comptes if c["debiteur"].endswith(f"({debiteur})")
                     and c["creancier"] == "joueur" and not c["objet"])
            self.assertEqual(c["montant"], montant)
            self.assertTrue(all("joueur" in (c["debiteur"], c["creancier"]) for c in comptes))
            return {"contenu_conforme": conforme, "perimetre": "sens",
                    "motif": "" if conforme else "La demande et le montant dû diffèrent.",
                    "operations_demandees": ["reclamer"]}
        return verifier

    def test_cas_reel_et_autre_dette_payes_une_fois_apres_recharge(self):
        for script, qui, nom, montant in (("comptes", "marchand", "Gorm", 2),
                                         ("ressources", "aubin", "Aubin", 5)):
            with self.subTest(qui=qui):
                m = banc(script)
                if montant == 5:
                    rembourser(m, qui, "joueur", montant, "vivres", "part")
                rembourser(m, "aubin", "brune", 7, "vivres", "part")
                m = recharger(m)
                avant = m.joueur["or"]
                mots = ("Gorm, rends-moi les deux pièces que tu me dois." if montant == 2
                        else "Aubin, rends-moi les cinq pièces que tu me dois.")
                texte = f"Je te rends {montant} pièces."
                r, sortie, appels = jouer(m, mots, [
                    parole(mots, ("reclamer", "", "", ""), personnage=qui), dialogue(f"« {texte} »")],
                    [audit(texte, [], qui)],
                    revues=[self.revue(qui, montant)])
                self.assertEqual(r.joueur["or"], avant + montant)
                self.assertFalse(any(d["a"] == "joueur" and d["de"] == qui for d in r.data["dettes"]))
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
                self.assertIn(texte, sortie)
                self.assertIn(mots, sortie)
                rr = recharger(r)
                self.assertEqual(rr.data, r.data)
                self.assertIn(texte, str(rr.data["conversation"]))
                self.assertNotIn(f"{nom} te doit {montant} pièces", fiche(rr))

    def test_refus_de_sens_sur_montant_different_reste_refuse(self):
        m = recharger(banc("comptes"))
        mots = "Gorm, rends-moi les trois pièces que tu me dois."
        p = parole(mots, ("reclamer", "", "", ""), personnage="marchand")
        r, sortie, appels = jouer(m, mots, [p, p, dialogue("Ta parole est entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))],
            revues=[self.revue("marchand", 2, False), self.revue("marchand", 2, False)])
        self.assertEqual(r.joueur["or"], m.joueur["or"])
        self.assertEqual(r.data["dettes"], m.data["dettes"])
        self.assertIn("Gorm te doit 2 pièces", fiche(recharger(r)))
        self.assertTrue(any("retour_moteur" in e.get("faits", {}) for _, e in appels))
        self.assertNotIn("Je te rends", sortie)
