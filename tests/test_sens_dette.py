"""Qui doit quoi à qui : vraie boucle console, MJ simulé, état et rendu rechargés."""
import copy
import unittest

from donjon.biens import compte, etat_comptes_joueur, preter, rembourser
from donjon.echanges import ENGAGEMENT_MAX, _avec_joueur
from donjon.narration import AuditIllisible, consigner, controler, schema_audit
from donjon.rendu import fiche
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


def audit_compte(texte, c, locuteur="aubin"):
    l = ligne("parole" if locuteur else "mecanique", sources=["comptes"],
              locuteur=locuteur, citation=texte if locuteur else "")
    l["comptes"] = [c]
    return rapport(l)


class SensDetteTests(unittest.TestCase):
    def echanger(self, monde, mots, bon, attendu, mauvais=None, inverse=None, cible="aubin", sujet=""):
        reponses = [parole(mots, ("reclamer", sujet, "", ""), personnage=cible)]
        audits = []
        if mauvais:
            reponses.append(dialogue(f'{cible.capitalize()} répond : « {mauvais} »'))
            audits.append(audit_compte(mauvais, inverse, cible))
        reponses.append(dialogue(f'{cible.capitalize()} répond : « {bon} »'))
        audits.append(audit_compte(bon, attendu, cible))
        r, sortie, appels = jouer(recharger(monde), mots, reponses, audits)
        self.assertIn(bon, sortie)
        self.assertIn(bon, str(r.data["conversation"]))
        self.assertEqual(r.data["paroles_pnj"][-1]["texte"], bon)
        if mauvais:
            self.assertNotIn(mauvais, sortie)
            self.assertNotIn(mauvais, str(r.data["conversation"]))
            self.assertNotIn(mauvais, str(r.data["paroles_pnj"]))
            correction = next(e for f, e in appels if "controle_narratif" in e)
            refus = correction["controle_narratif"]
            self.assertIn("debiteur", refus[0]["attendu"])
            self.assertIn(str(attendu), refus[0]["attendu"])
            self.assertNotIn(refus[0]["attendu"], sortie)
        return r, sortie, appels

    def test_cas_reel_absence_dans_le_sens_demande_et_inverse_refuse(self):
        m = banc("ressources")
        r, _, appels = self.echanger(m, "Aubin, tu me dois quelque chose ?", "Non, je ne te dois rien.",
            compte("aubin", "joueur", etat="absent"), "Non, tu ne me dois rien.",
            compte("joueur", "aubin", etat="absent"))
        self.assertEqual(r.joueur["or"], m.joueur["or"])
        self.assertFalse(r.data.get("dettes"))
        issue = next(e["faits"]["conversation_validee"] for f, e in appels
                     if f == "repondre_au_joueur" and "conversation_validee" in e["faits"])
        self.assertEqual(issue["comptes"], [compte("aubin", "joueur", etat="absent")])

    def test_autre_personnage_meme_absence_et_meme_refus(self):
        m = banc("ressources")
        r, _, _ = self.echanger(m, "Brune, rends-moi ce que tu me dois.", "Je ne te dois rien.",
            compte("brune", "joueur", etat="absent"), "Tu ne me dois rien.",
            compte("joueur", "brune", etat="absent"), cible="brune")
        self.assertFalse(r.data.get("dettes"))

    def test_part_payee_deux_pieces_rendues_une_seule_fois(self):
        m = banc("ressources")
        rembourser(m, "aubin", "joueur", 2, "vivres", "part")
        avant = m.joueur["or"]
        r, _, _ = self.echanger(m, "Aubin, rends-moi les deux pièces que tu me dois.",
            "Je te rends les deux pièces.", compte("aubin", "joueur", montant=2, etat="rendu"),
            "Tu me rends les deux pièces.", compte("joueur", "aubin", montant=2, etat="rendu"))
        self.assertEqual(r.joueur["or"], avant + 2)
        self.assertEqual(r.data["dettes"], [])
        self.assertNotIn("te doit 2 pièces", fiche(r))

    def test_creance_refusee_reste_due_dans_le_meme_sens(self):
        m = banc("ressources")
        rembourser(m, "brune", "joueur", 2, "vivres", "part")
        r, _, _ = self.echanger(m, "Brune, rends-moi les deux pièces.",
            "Je te dois deux pièces, mais je les garde.", compte("brune", "joueur", montant=2), cible="brune")
        self.assertEqual(r.joueur["or"], m.joueur["or"])
        self.assertEqual(r.data["dettes"][0]["montant"], 2)
        self.assertIn("Brune te doit 2 pièces", fiche(r))

    def test_pret_echu_reclame_par_un_pnj_au_joueur(self):
        m = banc("ressources")
        m.objets["lanterne"]["proprietaire"] = "aubin"
        preter(m, "lanterne", "joueur")
        m.data["permissions"][-1]["minute"] = m.data["minutes"] - ENGAGEMENT_MAX - 1
        lignes = []
        _avec_joueur(m, "aubin", {"operation": "demander", "outil": "lanterne"}, lignes)
        self.assertIn("te demande de lui rendre", " ".join(lignes))
        bon, mauvais = "Tu me dois encore la lanterne.", "Je te dois encore la lanterne."
        r, sortie, appels = jouer(recharger(m), "Aubin, bonsoir", [
            parole("Aubin, bonsoir", personnage="aubin"),
            dialogue(f'Aubin répond : « {mauvais} »'), dialogue(f'Aubin répond : « {bon} »')], [
            audit_compte(mauvais, compte("aubin", "joueur", "lanterne", 1)),
            audit_compte(bon, compte("joueur", "aubin", "lanterne", 1))])
        self.assertNotIn(mauvais, sortie)
        self.assertIn(bon, sortie)
        self.assertEqual(r.data["paroles_pnj"][-1]["texte"], bon)
        self.assertEqual(r.objets["lanterne"]["lieu"], "joueur")
        self.assertEqual(r.data["permissions"][-1]["a"], "joueur")
        self.assertIn("Aubin t'a prêté la lanterne", fiche(r))
        self.assertTrue(any("controle_narratif" in e for _, e in appels))

    def test_objet_du_joueur_reclame_et_rendu_dans_le_meme_sens(self):
        from donjon.deplacement_objet import deplacer
        m = banc("ressources")
        m.objets["couteau"]["proprietaire"] = "joueur"
        m.data["connus"].append("couteau")
        deplacer(m, "couteau", "aubin")
        r, _, _ = self.echanger(m, "Aubin, rends-moi le couteau.", "Je te rends ton couteau.",
            compte("aubin", "joueur", "couteau", 1, "rendu"), sujet="couteau")
        self.assertEqual(r.objets["couteau"]["lieu"], "joueur")
        self.assertFalse(r.data.get("permissions"))
        self.assertNotIn("Tu as prêté le couteau", fiche(r))

    def test_narration_ordinaire_et_montant_faux_controles_aussi(self):
        m = banc("ressources")
        rembourser(m, "aubin", "joueur", 2, "vivres", "part")
        mauvais, bon = "Aubin te doit trois pièces.", "Aubin te doit deux pièces."
        r, sortie, _ = jouer(recharger(m), "mes comptes ?", [dialogue(mauvais), dialogue(bon)], [
            audit_compte(mauvais, compte("aubin", "joueur", montant=3), ""),
            audit_compte(bon, compte("aubin", "joueur", montant=2), "")])
        self.assertNotIn(mauvais, sortie)
        self.assertIn(bon, sortie)
        self.assertEqual(r.data["dettes"][0]["montant"], 2)
        self.assertIn("Aubin te doit 2 pièces", fiche(r))

    def test_rapport_obligatoire_et_garde_refait_a_l_enregistrement(self):
        m = banc("ressources")
        c = compte("aubin", "joueur", etat="absent")
        faits = {"comptes": {"etat": [], "issue": [c]}, "interlocuteurs": {"aubin": {}}}
        texte = 'Aubin répond : « Je ne te dois rien. »'
        sch = schema_audit(faits, 1)["properties"]["segments"]["items"]
        self.assertIn("comptes", sch["required"])
        incomplet = ligne("parole", locuteur="aubin", citation="Je ne te dois rien.")
        incomplet.pop("comptes")
        with self.assertRaises(AuditIllisible):
            controler(texte, rapport(incomplet), faits)
        a = controler(texte, audit_compte("Je ne te dois rien.", c), faits)
        a.update(faits=faits, texte_initial=texte, fondement="aubin", fondement_paroles="")
        a["segments"][0]["comptes"][0] = compte("joueur", "aubin", etat="absent")
        from donjon.monde import ErreurMonde
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            consigner(m, {**dialogue(texte), "_audit": a})
        self.assertEqual(m.data, avant)

    def test_aucun_compte_prive_entre_pnj_fourni(self):
        m = banc("ressources")
        rembourser(m, "aubin", "brune", 7, "vivres", "part")
        comptes = etat_comptes_joueur(recharger(m), ["aubin", "brune"])
        self.assertTrue(all("joueur" in (c["debiteur"], c["creancier"]) for c in comptes))
        self.assertNotIn(7, [c["montant"] for c in comptes])
