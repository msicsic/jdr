"""Issue financière complète, vraie console, sauvegarde et rendu rechargés."""
import copy
import unittest

from donjon.biens import compte, livraisons_dues
from donjon.matiere import id_piece
from donjon.narration import consigner, controler
from donjon.rendu import decrire_comptes
from donjon.monde import ErreurMonde
from donjon.voix import personne_pour_joueur
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


def audit(texte, comptes, qui):
    l = ligne("parole", sources=["comptes"], locuteur=qui, citation=texte)
    l.update(comptes=comptes, portee_mecanique="etablie" if comptes else "aucune")
    return rapport(l)


class ComptesIssueTests(unittest.TestCase):
    def test_examen_explicite_remboursements_console_recharge(self):
        from donjon.narration import schema_comptes, AuditIllisible
        for script, qui, nom in (("comptes", "marchand", "Gorm"),
                                 ("soir-appel", "aubin", "Aubin")):
            with self.subTest(script=script):
                m = banc(script)
                avant = m.joueur["or"]
                c = compte(qui, "joueur", montant=2, etat="rendu")
                bon = f"{nom} te rend les deux pièces."
                faux = f"{nom} te rend trois pièces."
                def rapport_compte(extrait):
                    l = ligne("mecanique", sources=["conversation_validee"])
                    l["comptes"] = {"issue_0": extrait, "autres": []}
                    return rapport(l)
                mots = "Je réclame les deux pièces dues."
                r, sortie, appels = jouer(recharger(m), mots,
                    [parole(mots, ("reclamer", "", "", ""), personnage=qui),
                     dialogue(faux), dialogue(bon)],
                    [rapport_compte({**c, "montant": 3}), rapport_compte(c)])
                recharge = recharger(r)
                self.assertIn(bon, sortie)
                self.assertNotIn(faux, sortie)
                self.assertIn(bon, str(recharge.data["conversation"]))
                self.assertNotIn(faux, str(recharge.data["conversation"]))
                self.assertEqual(recharge.data, r.data)
                from donjon.rendu import regarder
                self.assertEqual(regarder(recharge), regarder(r))
                self.assertEqual(decrire_comptes(recharge), decrire_comptes(r))
                self.assertEqual(recharge.joueur["or"], avant + 2)
                self.assertNotIn(nom + " te doit 2 pièces", decrire_comptes(recharge))
                faits = next(e["faits"] for _, e in appels
                             if "conversation_validee" in e.get("faits", {}))
                self.assertEqual(set(schema_comptes(faits)["properties"]), {"issue_0", "autres"})
                self.assertTrue(controler(bon, rapport_compte(None), faits)["obstacles"])
                self.assertTrue(controler(bon, rapport_compte({**c, "debiteur": "joueur",
                    "creancier": qui}), faits)["obstacles"])
                with self.assertRaises(AuditIllisible):
                    incomplet = rapport_compte(c)
                    incomplet["segments"]["0"]["comptes"] = {"autres": []}
                    controler(bon, incomplet, faits)

    def test_remboursement_reel_et_autre_creancier_omission_et_inverse_refuses(self):
        for script, qui in (("soir-appel", "aubin"), ("comptes", "marchand")):
            with self.subTest(script=script):
                m = banc(script)
                avant = m.joueur["or"]
                mots = "Je réclame les deux pièces dues."
                faux = "Elles sont à moi et elles ne t'ont pas été remises."
                inverse = "Tu me rends les deux pièces."
                bon = "Je te rends les deux pièces."
                c = compte(qui, "joueur", montant=2, etat="rendu")
                r, sortie, appels = jouer(recharger(m), mots, [
                    parole(mots, ("reclamer", "", "", ""), personnage=qui),
                    dialogue(f"« {faux} »"), dialogue(f"« {inverse} »"), dialogue(f"« {bon} »")], [
                    audit(faux, [], qui), audit(inverse, [compte("joueur", qui, montant=2, etat="rendu")], qui),
                    audit(bon, [c], qui)])
                self.assertIn(bon, sortie)
                for interdit in (faux, inverse):
                    self.assertNotIn(interdit, sortie)
                    self.assertNotIn(interdit, str(r.data["conversation"]))
                    self.assertNotIn(interdit, str(r.data["paroles_pnj"]))
                self.assertEqual(r.joueur["or"], avant + 2)
                self.assertNotIn("_comptes_echange", r.data)
                self.assertFalse(any(d["de"] == qui for d in r.data.get("dettes", [])))
                nom = personne_pour_joueur(r, qui, court=True)[0]
                self.assertNotIn(nom + " te doit 2 pièces", decrire_comptes(r))
                corrections = [e["controle_narratif"] for _, e in appels if "controle_narratif" in e]
                self.assertTrue(any("omet" in str(correction) for correction in corrections))
                issue = next(e["faits"]["conversation_validee"] for _, e in appels
                             if "conversation_validee" in e.get("faits", {}))
                self.assertIn(c, issue["comptes"])
                self.assertIn(bon, str(recharger(r).data["conversation"]))

    def test_achats_de_parts_payees_et_differees_deux_biens(self):
        from donjon.banc_pnj import creer
        from donjon.esprits import percevoir_tous
        from tests.support import calme, presentes, regarder
        from tests.test_parts_achetees import antichambre_du_banc
        from tests.test_tensions import placer
        scenes = [(presentes(antichambre_du_banc(), "aubin"), "aubin", "planches", 3)]
        m = presentes(calme(creer("auberge", 1985, "fixe"), "joss"), "joss")
        m.objets["fagots_etable"]["charges"] = 3
        placer(m, "joss", "etable", (5, 3))
        m.joueur.update(salle="etable", position=[5, 2])
        regarder(m, "joss", "joueur")
        regarder(m, "joueur", "joss")
        percevoir_tous(m)
        scenes.append((recharger(m), "joss", "fagots_etable", 1))
        for m, qui, lot, prix in scenes:
            with self.subTest(lot=lot):
                if qui == "aubin":
                    # Le tour 2 réel demande le bois : Aubin constate sa réserve.
                    from donjon.echanges import enqueter
                    enqueter(m, "joueur", qui, "chaleur")
                    m = recharger(m)
                piece = id_piece(m, lot)
                avant = m.joueur["or"]
                mots = f"Je te paie {prix} pièces pour une part."
                bon = "Les pièces sont remises et je te dois encore cette part."
                cs = [compte("joueur", qui, montant=prix, etat="rendu"),
                      compte(qui, "joueur", piece, 1)]
                premier = parole(mots, ("demande", lot, "", str(prix)), personnage=qui)
                if qui == "aubin":
                    # Même marché atomique que dans la trace réelle du soir.
                    premier["proposition"]["contenu"] = [{"type": "proposition",
                        "demande": {"type": "part", "objet": lot},
                        "contrepartie": {"type": "pieces", "montant": prix}}]
                r, sortie, appels = jouer(m, mots, [premier, dialogue(f"« {bon} »")],
                                         [audit(bon, cs, qui)])
                self.assertIn(bon, sortie)
                self.assertIn(bon, str(r.data["conversation"]))
                self.assertEqual(r.joueur["or"], avant - prix)
                self.assertIn(cs[1], livraisons_dues(r))
                self.assertIn("remettre", decrire_comptes(r))
                self.assertNotIn("_comptes_echange", r.data)
                self.assertFalse(any("controle_narratif" in e for _, e in appels))
                issue = next(e["faits"]["conversation_validee"] for _, e in appels
                             if "conversation_validee" in e.get("faits", {}))
                self.assertEqual(issue["comptes"], cs)
                self.assertEqual(r.data["paroles_pnj"][-1]["texte"], bon)

    def test_couverture_refaite_avant_enregistrement(self):
        m = banc("soir-appel")
        c = compte("aubin", "joueur", montant=2, etat="rendu")
        faits = {"comptes": {"issue": [c]}, "interlocuteurs": {"aubin": {}}}
        texte = "« Je te rends les deux pièces. »"
        a = controler(texte, audit("Je te rends les deux pièces.", [c], "aubin"), faits)
        self.assertFalse(a["obstacles"])
        a.update(faits=faits, texte_initial=texte, fondement=texte, fondement_paroles="")
        a["segments"][0]["comptes"] = []
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            consigner(m, {**dialogue(texte), "_audit": a})
        self.assertEqual(m.data, avant)
