"""Une seule adresse, de la saisie à la sauvegarde ; cas du banc et autre scénario."""
from donjon.emissions import joueur as emissions_joueur, pnj as emissions_pnj
import copy
import unittest

from donjon.dialogues import interlocuteurs
from donjon import agendas
from donjon.biens import bourse, compte
from donjon.esprits import lire
from donjon.monde import ErreurMonde
from donjon.paroles import analyser, en_face, preparer_parole, prevue
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.spatial import porte_par
from donjon.voix import reel
from tests.test_audits_attendu import jouer, rapport, ligne
from tests.test_parole_commune import paroles_retenues
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger, vivre


class AudienceTests(unittest.TestCase):
    def verifier_recharge(self, m):
        r = recharger(m)
        self.assertEqual(r.data, m.data)
        self.assertEqual(regarder(r), regarder(m))
        self.assertEqual(scene_percue(r), scene_percue(m))
        return r

    def verifier_parole(self, m, saisie, besoin, personnage, destinataires):
        avant = copy.deepcopy(m.data)
        attendue = prevue(m, saisie)
        self.assertEqual(attendue["personnage"], personnage)
        self.assertEqual([reel(m, x) for x in attendue["destinataires"]], destinataires)
        self.assertEqual(m.data, avant)  # La prévision ne prononce rien.
        r, sortie, appels = jouer(m, saisie, [
            parole(saisie, ("ressource", besoin, "", ""), personnage=personnage),
            dialogue("Ta question a été entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))])
        validee = next(e["faits"]["conversation_validee"] for f, e in appels
                       if f == "repondre_au_joueur" and "conversation_validee" in e["faits"])
        self.assertEqual([reel(r, x) for x in validee["destinataires"]], destinataires)
        annonce = "Tu dis :" if personnage == "personne" else "Tu dis à "
        self.assertIn(annonce, sortie)
        self.assertNotIn("Précise à qui", sortie)
        p = emissions_joueur(r)[-1]
        mots = analyser(m, saisie)["mots"] or saisie
        self.assertEqual((p["auditeur"], p["texte"]), (reel(m, personnage), mots))
        self.assertTrue(p["auditeurs"])
        for qui in p["auditeurs"]:
            self.assertEqual(paroles_retenues(r, qui)[-1], ("joueur", destinataires, mots))
        self.assertIn("Ta question a été entendue.", str(r.data["conversation"]))
        for f, e in appels:
            if f == "auditer_action":
                revue = e["plan"]["parole"]
                self.assertEqual(set(revue), {"replique", "contenu", "sens_contenu", "comptes_avant"})
                self.assertTrue(all("joueur" in (c["debiteur"], c["creancier"])
                                    for c in revue["comptes_avant"]))
        return r, validee, sortie

    def test_cas_reel_trois_presents_et_une_voix_avec_aubin_en_face(self):
        m = banc("noms-dialogue")
        from donjon.paroles import entendre_repondant
        entendre_repondant(m, "marchand")
        m = recharger(m)
        self.assertEqual(en_face(m, [reel(m, x) for x in interlocuteurs(m)]), "aubin")
        r, validee, sortie = self.verifier_parole(m, "est-ce que quelqu'un a du bois ?", "chaleur", "aubin", ["aubin"])
        self.assertEqual(emissions_joueur(r)[-1]["auditeurs"], ["aubin"])
        self.assertEqual(validee["repondent"], ["aubin"])
        self.assertIn("Tu dis à Aubin : « est-ce que quelqu'un a du bois ? »", sortie)
        for qui in ("brune", "ilse", "marchand"):
            self.assertEqual(paroles_retenues(r, qui)[-1], ("joueur", ["aubin"], "est-ce que quelqu'un a du bois ?"))

    def test_autre_scenario_autres_mots_au_personnage_en_face(self):
        m = banc("sous-obstacle-auberge")
        m.joueur["orientation"] = "ouest"
        m = recharger(m)
        cible = prevue(m, "Avez-vous de quoi manger ?")["personnage"]
        self.assertEqual(reel(m, cible), "lucien")
        r, validee, _ = self.verifier_parole(m, "Avez-vous de quoi manger ?", "faim", cible, ["lucien"])
        self.assertEqual(emissions_joueur(r)[-1]["auditeurs"], ["lucien"])
        self.assertEqual(validee["repondent"], [cible])

    def test_sans_interlocuteur_percu_la_cantonade_garde_ses_repondants(self):
        m = banc("soir-noir")
        self.assertFalse(interlocuteurs(m))
        r, validee, sortie = self.verifier_parole(m, "Avez-vous de quoi manger ?", "faim", "personne", [])
        self.assertEqual(emissions_joueur(r)[-1]["auditeurs"], ["ilse"])
        self.assertEqual(validee["repondent"], ["voix_1"])
        self.assertIn("Tu dis : « Avez-vous de quoi manger ? »", sortie)

        # Une adresse individuelle ne devient pas publique : sans antécédent ni
        # personne perçue, « lui » garde son refus du lot 47, comme le chuchotement.
        for saisie in ("je lui dis : bonjour", "je chuchote : bonjour"):
            with self.subTest(saisie=saisie):
                seul = banc("soir-noir")
                r, sortie, appels = jouer(seul, saisie, [], [])
                self.assertFalse(appels)
                self.assertFalse(emissions_joueur(r))
                self.assertNotIn("Tu dis", sortie)

    def test_a_tous_adresse_le_groupe_malgre_aubin_en_face(self):
        m = banc("noms-dialogue")
        dest = [reel(m, x) for x in prevue(m, "à tous : avez-vous du bois ?")["destinataires"]]
        r, validee, sortie = self.verifier_parole(m, "à tous : avez-vous du bois ?", "chaleur", "tous", dest)
        self.assertTrue({"aubin", "brune", "ilse"} <= set(dest))
        self.assertEqual(set(emissions_joueur(r)[-1]["auditeurs"]), {"aubin", "brune", "ilse", "marchand"})
        self.assertIn("Tu dis à tous", sortie)

    def test_des_guillemets_poursuivent_ilse_malgre_aubin_en_face(self):
        m = banc("noms-dialogue")
        r, _, _ = jouer(m, "Ilse, bonsoir", [parole("Ilse, bonsoir", personnage="ilse"),
            dialogue("Ilse a entendu ta parole.")], [rapport(ligne("mecanique", sources=["conversation_validee"]))])
        self.assertEqual(en_face(r, [reel(r, x) for x in interlocuteurs(r)]), "aubin")
        r, validee, sortie = self.verifier_parole(r, "« As-tu de quoi manger ? »", "faim", "ilse", ["ilse"])
        self.assertEqual(validee["repondent"], ["ilse"])
        self.assertIn("Tu dis à Ilse", sortie)

    def test_une_adresse_contraire_est_refusee_avant_la_revue(self):
        for saisie, cible, faux in (("Aubin, as-tu du bois ?", "aubin", "tous"),
                                    ("je dis à Ilse : bonjour", "ilse", "aubin")):
            with self.subTest(saisie=saisie):
                m = banc("noms-dialogue")
                r, sortie, appels = jouer(m, saisie, [
                    parole("bonjour", personnage=faux), parole("bonjour", personnage=cible),
                    dialogue("Ta parole a été entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                retour = next(e["faits"]["retour_moteur"] for f, e in appels
                              if f == "repondre_au_joueur" and "retour_moteur" in e["faits"])
                self.assertIn(f"personnage = {cible}", retour["attendu"])
                self.assertEqual(emissions_joueur(r)[-1]["auditeurs"], [cible])
                self.assertIn("Tu dis à", sortie)
                self.assertNotIn("Précise à qui", sortie)

    def test_la_revue_refuse_encore_un_contenu_contraire(self):
        m = banc("noms-dialogue")
        saisie = "est-ce que quelqu'un a du bois ?"
        r, sortie, appels = jouer(m, saisie, [
            parole(saisie, ("ressource", "faim", "", ""), personnage="aubin"),
            parole(saisie, ("ressource", "chaleur", "", ""), personnage="aubin"),
            dialogue("Ta question a été entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))],
            revues=[{"conforme": False, "motif": "Du combustible est demandé, pas de la nourriture."},
                    {"conforme": True, "motif": ""}])
        self.assertNotIn("Précise à qui", sortie)
        self.assertEqual(len(emissions_joueur(r)), 1)
        self.assertEqual(emissions_joueur(r)[-1]["texte"], saisie)
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 2)

    def test_sans_adresse_ni_question_l_audience_ne_change_pas(self):
        m = banc("noms-dialogue")
        for saisie in ("je dis : bonsoir", "« Bonsoir. »", "Avez-vous faim ?"):
            with self.subTest(saisie=saisie):
                self.assertEqual(prevue(m, saisie)["personnage"], "aubin")
                with self.assertRaises(ErreurMonde):
                    preparer_parole(m, {"personnage": "personne", "replique": "Bonsoir.",
                                        "contenu": [], "_intention": saisie})

    def test_une_intention_nommee_reste_individuelle_sans_devenir_une_parole_forcee(self):
        m = banc("noms-dialogue")
        # Ce test d'audience attend un achat impossible. Depuis le lot 312,
        # ignorer le lieu du destinataire permet de le chercher : cela ne
        # suffit plus à refuser. Ici le lot est explicitement non transportable.
        m.objets["planches"]["mobile"] = False
        depart = m.joueur["or"]
        # Propositions initiales de Luna dans la passe du lot : elles ne doivent
        # plus être renvoyées au modèle pour réécrire leur audience.
        cas = [("je réclame à Aubin les deux pièces qu'il me doit", "Aubin, tu me dois deux pièces. Rends-les-moi.",
                ("reclamer", "", "", ""), depart + 2),
               ("je paie Aubin trois pièces pour une de ses planches", "Je te paie trois pièces pour une de tes planches.",
                ("demande", "planches", "", "3"), depart + 2)]
        for saisie, replique, contenu, pieces in cas:
            with self.subTest(saisie=saisie):
                self.assertEqual(prevue(m, saisie)["personnage"], "aubin")
                recit = ("Je te rends 2 pièces." if contenu[0] == 'reclamer' else
                         "Je ne vois pas comment exécuter cette demande.")
                controle = ligne("mecanique", sources=["conversation_validee", "comptes"])
                if contenu[0] == "reclamer":
                    controle["comptes"] = [compte("aubin", "joueur", montant=2, etat="rendu")]
                m, sortie, appels = jouer(m, saisie, [parole(replique, contenu, personnage="aubin"),
                    dialogue(recit)], [rapport(controle)])
                self.assertIn(recit, sortie)
                self.assertIn(recit, str(m.data["conversation"]))
                self.assertIn("Tu dis à Aubin", sortie)
                self.assertEqual(m.joueur["or"], pieces)
                self.assertEqual(emissions_joueur(m)[-1]["auditeurs"], ["aubin"])
                self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 1)
                if contenu[0] == "demande":
                    faits = emissions_pnj(m)[-1]['evenement']['faits']
                    self.assertIn("ne voit pas comment", " ".join(faits))
                    self.assertEqual(m.objets["planches"]["charges"], 2)
                    self.assertNotIn("planches_1", m.objets)
                    self.assertFalse(agendas.en_cours(m, "aubin"))
                m = self.verifier_recharge(m)
        for saisie in ("je regarde Aubin", "j'observe Ilse"):
            forme = analyser(m, saisie)
            self.assertFalse(forme["explicite"])
            self.assertIsNone(forme["nomme"])
            self.assertTrue(forme["cible_intention"])

        from donjon.moteur import proposition
        m = banc("noms-dialogue")
        r, sortie, _ = jouer(m, "je regarde Aubin", [{"mode": "action", "texte": "", "faits": [],
            "proposition": proposition("examiner", "aubin")}], [])
        self.assertFalse(emissions_joueur(r))
        self.assertIn("Aubin", sortie)

    def test_achats_differes_acceptes_et_livres_apres_la_saisie_libre(self):
        from donjon.banc_pnj import creer
        from donjon.esprits import percevoir_tous
        from tests.support import calme, presentes, regarder as orienter
        from tests.test_tensions import placer

        def relais():
            # Rejouer la séquence réelle entière : sinon Aubin rembourse
            # spontanément ces deux pièces pendant la livraison et change
            # légitimement les deux bourses indépendamment de l'achat.
            m = banc("noms-dialogue")
            or_avant = m.joueur["or"]
            saisie = "je réclame à Aubin les deux pièces qu'il me doit"
            controle = ligne("mecanique", sources=["conversation_validee", "comptes"])
            controle["comptes"] = [compte("aubin", "joueur", montant=2, etat="rendu")]
            m, sortie, appels = jouer(m, saisie, [
                parole("Aubin, tu me dois deux pièces. Rends-les-moi.",
                       ("reclamer", "", "", ""), personnage="aubin"),
                dialogue("Aubin a entendu ta demande.")], [rapport(controle)])
            self.assertEqual(m.joueur["or"], or_avant + 2)
            self.assertIn("Je te rends 2 pièces.", sortie)
            self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 1)
            return m

        def auberge():
            m = presentes(calme(creer("auberge", 1985, "fixe"), "joss"), "joss")
            m.objets["fagots_etable"]["charges"] = 3
            placer(m, "joss", "etable", (5, 3))
            m.joueur.update(salle="etable", position=[5, 2])
            orienter(m, "joss", "joueur")
            orienter(m, "joueur", "joss")
            percevoir_tous(m)
            return m

        for fabrique, vendeur, lot, prix, saisie in (
            (relais, "aubin", "planches", 3,
             "je paie Aubin trois pièces pour une de ses planches"),
            (auberge, "joss", "fagots_etable", 1,
             "je paie Joss une pièce pour une part de ses fagots"),
        ):
            with self.subTest(vendeur=vendeur):
                m = self.verifier_recharge(fabrique())
                or_avant, vendeur_avant = m.joueur["or"], bourse(m, vendeur)
                charges = m.objets[lot]["charges"]
                m, sortie, appels = jouer(m, saisie, [
                    parole(saisie, ("demande", lot, "", str(prix)), personnage=vendeur),
                    dialogue("Ta demande a été entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee", "comptes"]))])
                self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 1)
                self.assertEqual(emissions_joueur(m)[-1]["auditeurs"], [vendeur])
                self.assertIn(f"Tu m'as payé {prix} pièce", sortie)
                self.assertIn("Je dois encore te remettre une part", sortie)
                self.assertIn(emissions_pnj(m)[-1]['texte'], str(m.data['conversation']))
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
                piece = lot + "_1"
                condition = {"objet": piece, "remettre": "joueur"}
                self.assertEqual(m.joueur["or"], or_avant - prix)
                self.assertEqual(bourse(m, vendeur), vendeur_avant + prix)
                self.assertEqual(m.objets[lot]["charges"], charges - 1)
                self.assertFalse(porte_par(m, piece, "joueur"))
                self.assertEqual(agendas.en_cours(m, vendeur), [{
                    "condition": condition, "pour": "joueur", "minute": 0, "lot": lot,
                    "paye": {"objet": piece, "prix": prix, "quoi": "objet"}}])
                m = self.verifier_recharge(m)
                m, lignes = vivre(m, 3, jet=20)
                self.assertTrue(porte_par(m, piece, "joueur"), lignes)
                self.assertEqual(m.objets[piece]["proprietaire"], "joueur")
                self.assertEqual(m.objets[piece]["charges"], 1)
                self.assertEqual(m.objets[lot]["charges"], charges - 1)
                self.assertEqual(m.joueur["or"], or_avant - prix)
                self.assertEqual(bourse(m, vendeur), vendeur_avant + prix)
                self.assertFalse(agendas.en_cours(m, vendeur))
                self.assertTrue(any(x["type"] == "engagement_tenu" and x["condition"] == condition
                                    for x in lire(m, vendeur)["memoire"]))
                self.assertIn("tu l'avais payé", " ".join(lignes))
                self.verifier_recharge(m)
