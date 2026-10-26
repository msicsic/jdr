"""Liens comptables du moteur : console, sauvegarde et recharge."""
import unittest
from unittest.mock import patch
from donjon import narration
from donjon.biens import compte
from donjon.rendu import fiche
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger
from tests import test_comptes_issue as anciens


def audit_liens(texte, qui, liens):
    def construire(entree):
        l = ligne("parole", sources=["comptes"], locuteur=qui, citation=texte)
        l["nature"] = l.pop("verdict")
        del l["comptes"]
        l["liens_comptes"] = {ref: "non_evoque" for ref in narration.references_comptes(entree["faits"])}
        l["liens_comptes"].update(dict(liens))
        return rapport(l)
    return construire


class ComptesLiensTests(unittest.TestCase):
    def test_remboursements_sans_relance_et_inverse_refuse(self):
        for script, qui in (("comptes", "marchand"), ("soir-appel", "aubin")):
            with self.subTest(script=script):
                m = recharger(banc(script))
                avant = m.joueur["or"]
                mots = "Rends-moi les deux pièces dues."
                bon = "Je te rends les deux pièces."
                for inverse in (False, True):
                    mauvais = "Tu me rends les deux pièces."
                    reponses = [parole(mots, ("reclamer", "", "", ""), personnage=qui)]
                    audits = []
                    if inverse:
                        reponses.append(dialogue(f"« {mauvais} »"))
                        audits.append(audit_liens(mauvais, qui, [("issue.1", "contredit")]))
                    reponses.append(dialogue(f"« {bon} »"))
                    audits.append(audit_liens(bon, qui, [("issue.1", "restitue")]))
                    r, sortie, appels = jouer(recharger(m), mots, reponses, audits)
                    self.assertEqual(r.joueur["or"], avant + 2)
                    self.assertIn(bon, sortie)
                    self.assertNotIn(mauvais, sortie)
                    self.assertEqual(sum("controle_narratif" in e for _, e in appels), int(inverse))
                    rr = recharger(r)
                    self.assertEqual(rr.data, r.data)
                    self.assertIn(bon, str(rr.data["conversation"]))
                    self.assertFalse(any(d["de"] == qui and d["a"] == "joueur" for d in rr.data["dettes"]))
                    dossier = next(e["faits"] for f,e in appels if f == "auditer_narration")
                    self.assertEqual(dossier["references_comptes"], narration.references_comptes(dossier))

    def test_achats_complets_utilisent_les_liens_apres_recharge(self):
        # Réutilise les deux chaînes réelles (soir + autre bien), avec le nouveau format réseau.
        def nouveau(texte, comptes, qui):
            return audit_liens(texte, qui, [(f"issue.{i}", "restitue") for i in range(len(comptes))])
        with patch("tests.test_comptes_issue.audit", nouveau):
            anciens.ComptesIssueTests("test_achats_de_parts_payees_et_differees_deux_biens").test_achats_de_parts_payees_et_differees_deux_biens()

    def test_refus_brune_reste_du_sans_relance(self):
        m = recharger(banc("comptes"))
        avant = m.joueur["or"]
        mots = "Brune, rends-moi les deux pièces."
        bon = "Je te dois deux pièces, mais je les garde."
        r, sortie, appels = jouer(m, mots, [
            parole(mots, ("reclamer", "", "", ""), personnage="brune"), dialogue(f"« {bon} »")],
            [audit_liens(bon, "brune", [("issue.0", "restitue")])])
        self.assertEqual(r.joueur["or"], avant)
        self.assertIn(bon, sortie)
        self.assertFalse(any("controle_narratif" in e for _, e in appels))
        rr = recharger(r)
        self.assertIn("Brune te doit 2 pièces", fiche(rr))
        self.assertIn(bon, str(rr.data["paroles_pnj"]))

    def test_liens_conserves_et_recontroles_dans_audit_canonique(self):
        c = compte("a", "joueur", montant=2, etat="rendu")
        faits = {"comptes": {"issue": [c], "etat": [c]}, "interlocuteurs": {"a": {}}}
        texte = "« Je te rends deux pièces. »"
        initial = audit_liens("Je te rends deux pièces.", "a", [("issue.0", "restitue")])({"faits": faits})
        controle = narration.controler(texte, initial, faits)
        self.assertFalse(controle["obstacles"])
        self.assertNotIn("comptes", controle["segments"][0])
        self.assertEqual(controle["segments"][0]["liens_comptes"], {"issue.0": "restitue"})
        self.assertFalse(narration.controler(texte, {"segments": controle["segments"]}, faits)["obstacles"])
        controle["segments"][0]["liens_comptes"]["issue.0"] = "contredit"
        self.assertTrue(narration.controler(texte, {"segments": controle["segments"]}, faits)["obstacles"])
        controle["segments"][0]["liens_comptes"] = {}
        with self.assertRaises(narration.AuditIllisible):
            narration.controler(texte, {"segments": controle["segments"]}, faits)

    def test_schema_ne_demande_plus_roles_ni_quantites(self):
        faits = {"comptes": {"issue": [compte("a", "joueur", montant=2, etat="rendu")]}}
        s = narration.schema_audit(faits, {"0": "texte"})
        self.assertIn("liens_comptes", str(s))
        self.assertNotIn("debiteur", str(s))
        for ref in ("invente", "issue.12"):
            with self.assertRaises(narration.AuditIllisible):
                narration.controler("« Je te rends deux pièces. »", audit_liens("Je te rends deux pièces.", "a", [(ref,"restitue")])({"faits": faits}), faits)

if __name__ == "__main__":
    unittest.main()

