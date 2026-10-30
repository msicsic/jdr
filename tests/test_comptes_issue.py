"""Issue financière complète, vraie console, sauvegarde et rendu rechargés."""
from donjon.emissions import pnj as emissions_pnj
import copy
import unittest

from donjon.biens import compte, livraisons_dues
from donjon.matiere import id_piece
from donjon.narration import consigner, controler
from donjon.rendu import decrire_comptes
from donjon.monde import ErreurMonde
from donjon.voix import personne_pour_joueur
from tests.test_audits_attendu import ligne, rapport
from tests.consentement_support import jouer
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


def audit(texte, comptes, qui):
    # Les comptes restent un argument des anciens appelants, sans extraction
    # dans le rapport de la prose libre.
    l = ligne("parole", locuteur=qui, citation=texte)
    l.pop("comptes")
    return rapport(l)


class ComptesIssueTests(unittest.TestCase):
    def test_remboursement_reel_et_autre_creancier_omission_et_inverse_refuses(self):
        for script, qui in (("soir-appel", "aubin"), ("comptes", "marchand")):
            with self.subTest(script=script):
                m = banc(script)
                avant = m.joueur["or"]
                mots = "Je réclame les deux pièces dues."
                faux = "Je te rends dix pièces."
                inverse = "Tu me rends les deux pièces."
                bon = "D’accord."
                c = compte(qui, "joueur", montant=2, etat="rendu")
                r, sortie, appels = jouer(recharger(m), mots, [
                    parole(mots, ("reclamer", "", "", ""), personnage=qui),
                    dialogue(f"« {faux} »"), dialogue(f"« {inverse} »"), dialogue(f"« {bon} »")], [
                    audit(bon, [], qui)])
                self.assertIn('Je te rends 2 pièces.', sortie)
                for interdit in (faux, inverse):
                    self.assertNotIn(interdit, sortie)
                    self.assertNotIn(interdit, str(r.data["conversation"]))
                    self.assertNotIn(interdit, str(emissions_pnj(r)))
                self.assertEqual(r.joueur["or"], avant + 2)
                self.assertNotIn("_comptes_echange", r.data)
                self.assertFalse(any(d["de"] == qui for d in r.data.get("dettes", [])))
                nom = personne_pour_joueur(r, qui, court=True)[0]
                self.assertNotIn(nom + " te doit 2 pièces", decrire_comptes(r))
                corrections = [e["controle_narratif"] for _, e in appels if "controle_narratif" in e]
                self.assertTrue(all("comptes.issue" in str(correction) for correction in corrections))
                emission = emissions_pnj(r)[-1]
                self.assertEqual(emission['texte'], 'Je te rends 2 pièces.')
                self.assertIn(c, emission['evenement']['resolutions_comptables'][0]['comptes'])
                self.assertIn(emission['texte'], str(recharger(r).data['conversation']))
                self.assertFalse(corrections)
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))

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
                bon = "D’accord."
                cs = [compte("joueur", qui, montant=prix, etat="rendu"),
                      compte(qui, "joueur", piece, 1)]
                premier = parole(mots, ("demande", lot, "", str(prix)), personnage=qui)
                if qui == "aubin":
                    # Même marché atomique que dans la trace réelle du soir.
                    premier["proposition"]["contenu"] = [{"type": "proposition",
                        "demande": {"type": "part", "objet": lot},
                        "contrepartie": {"type": "pieces", "montant": prix}}]
                r, sortie, appels = jouer(m, mots, [premier, dialogue(f"« {bon} »")],
                                         [audit(bon, [], qui)])
                emission = emissions_pnj(r)[-1]
                self.assertIn(f"Tu m'as payé {prix} pièce", emission['texte'])
                self.assertIn(emission['rendu_public'], sortie)
                self.assertIn(emission['texte'], str(r.data['conversation']))
                self.assertEqual(r.joueur["or"], avant - prix)
                self.assertIn(cs[1], livraisons_dues(r))
                self.assertIn("remettre", decrire_comptes(r))
                self.assertNotIn("_comptes_echange", r.data)
                self.assertFalse(any("controle_narratif" in e for _, e in appels))
                self.assertEqual(emission['evenement']['resolutions_comptables'][0]['comptes'], cs)
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
                self.assertEqual(recharger(r).data, r.data)

    def test_couverture_refaite_avant_enregistrement(self):
        m = banc("soir-appel")
        c = compte("aubin", "joueur", montant=2, etat="rendu")
        faits = {"comptes": {"issue": [c]}, "interlocuteurs": {"aubin": {}}}
        from donjon.comptes_narratifs import phrases
        texte = " ".join(phrases(faits))
        a = controler(texte, {"segments": {}}, faits)
        self.assertFalse(a["obstacles"])
        a.update(faits=faits, texte_initial=texte, fondement=texte, fondement_paroles="")
        avant = copy.deepcopy(m.data)
        # Une preuve exacte ne peut pas être transportée vers un texte inversé.
        with self.assertRaises(ErreurMonde):
            consigner(m, {**dialogue(texte.replace("2 pièces", "3 pièces")), "_audit": a})
        self.assertEqual(m.data, avant)
