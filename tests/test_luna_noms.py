"""Chaîne saisie/MJ/moteur/rendu/sauvegarde des défauts du banc Luna.

Le fournisseur est simulé ; les campagnes réelles sont décrites dans le rapport.
Chaque scène est sauvée avant la saisie et rechargée après par ``jouer``.
"""
from donjon.emissions import pnj as emissions_pnj, joueur as emissions_joueur
import copy
import unittest

from donjon.esprits import lire
from donjon.improvisation import proposition, issue
from donjon.moteur import proposition as operation
from donjon.monde import ErreurMonde
from donjon.narration import parole_racontee, segments
from donjon.paroles import preparer_parole, prevue
from donjon.refus import RefusDeForme
from tests.test_audits_attendu import jouer, rapport, ligne
from tests.test_parole_commune import scene, paroles_retenues
from tests.test_repli_et_appel import dialogue, parole, verdicts, NEUTRE
from tests.test_tensions import recharger


def action(p):
    return {"mode": "action", "texte": "", "faits": [], "proposition": p}


class AdresseTests(unittest.TestCase):
    def test_sans_adresse_celui_d_en_face_repond_les_autres_retiennent(self):
        for saisie in ("est-ce que quelqu'un a du bois ?", "qui peut nous aider ?"):
            with self.subTest(saisie=saisie):
                m = scene()
                r, sortie, appels = jouer(m, saisie, [
                    parole("Une réécriture.", personnage="ilse"),
                    dialogue("Plusieurs voix répondent.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                self.assertIn(f"Tu dis à Ilse : « {saisie} »", sortie)
                self.assertNotIn("Tu dis à Aubin", sortie)
                p = emissions_joueur(r)[-1]
                self.assertEqual(p["auditeur"], "ilse")
                self.assertEqual(p["auditeurs"], ["ilse"])
                self.assertEqual(p["texte"], saisie)

    def test_le_moteur_corrige_la_cible_avant_la_contre_revue(self):
        for saisie in ("est-ce que quelqu'un a du bois ?", "qui peut nous donner de quoi manger ?"):
            with self.subTest(saisie=saisie):
                m = scene()
                defaut = prevue(m, saisie)["personnage"]
                r, sortie, appels = jouer(m, saisie, [
                    parole(saisie, personnage="aubin"), parole(saisie, personnage=defaut),
                    dialogue("Tu as posé ta question.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))],
                    revues=[{"conforme": True, "motif": ""}])
                self.assertIn("Tu dis à Ilse :", sortie)
                self.assertNotIn("Tu dis à Aubin", sortie)
                self.assertEqual(len(emissions_joueur(r)), 1)
                self.assertEqual(emissions_joueur(r)[0]["auditeur"], "ilse")
                plans = [e["plan"]["parole"] for f, e in appels if f == "auditer_action"]
                self.assertEqual(len(plans), 0)  # Adresse fixée et mots exacts sans opération.

    def test_les_mots_exacts_sans_contenu_passent_sans_revue(self):
        m = scene()
        saisie = "je dis : qui peut nous aider ?"
        defaut = prevue(m, saisie)["personnage"]
        r, sortie, appels = jouer(m, saisie, [parole("qui peut nous aider ?", personnage=defaut),
            dialogue("Ta question a été entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))],
            revues=[{"conforme": True, "motif": "Parole sans opération demandée."}])
        self.assertNotIn("Précise ce que tu veux dire", sortie)
        self.assertNotIn("Précise à qui", sortie)
        self.assertIn("Tu dis à", sortie)
        self.assertEqual(emissions_joueur(r)[-1]["texte"], "qui peut nous aider ?")
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 0)

    def test_repondre_apres_s_etre_ecarte_ne_depend_pas_de_rester_en_vue(self):
        from tests.test_parole_corrections import banc
        from tests.test_tensions import placer
        for qui, nom in [("brune", "Brune"), ("aubin", "Aubin")]:
            with self.subTest(qui=qui):
                m = banc("soir-appel")
                if qui == "aubin":
                    brune, aubin = list(m.objets["brune"]["position"]), list(m.objets["aubin"]["position"])
                    placer(m, "brune", "antichambre", aubin)
                    placer(m, "aubin", "antichambre", brune)
                citation = "Oui, passe."
                texte = f"{nom} répond : « {citation} »"
                r, sortie, appels = jouer(m, f"{nom}, laisse-moi passer", [
                    parole("laisse-moi passer", ("passage", "", "", ""), personnage=qui), dialogue(texte)],
                    [rapport(ligne("parole", locuteur=qui, citation=citation))], suite=("tenter",))
                dites = [p for p in emissions_pnj(r)
                         if p['locuteur'] == qui and p['texte'] == citation]
                self.assertEqual(len(dites), 1)
                dite = dites[0]
                self.assertIn(texte, sortie)
                faits = next(e['faits'] for f, e in appels if f == 'auditer_narration')
                self.assertIn(qui, faits["interlocuteurs"])
                self.assertIn(qui, r.data["entendus"])
                self.assertNotEqual(r.objets[qui]["position"], m.objets[qui]["position"])
                self.assertFalse(r.visible(qui))
                self.assertEqual(dite["locuteur"], qui)
                self.assertEqual(dite["texte"], citation)

    def test_question_sans_nom_a_celui_d_en_face_sans_changer_les_mots(self):
        for saisie, besoin in [("est-ce que quelqu'un a du bois ?", "chaleur"),
                               ("qui peut nous donner de quoi manger ?", "faim")]:
            with self.subTest(saisie=saisie):
                m = scene(brune=(6, 4))
                r, sortie, appels = jouer(m, saisie, [
                    parole("Une réécriture ajoutée par le MJ", ("ressource", besoin, "", ""), personnage="ilse"),
                    dialogue("Tu as posé ta question.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                self.assertIn(f"Tu dis à Ilse : « {saisie} »", sortie)
                self.assertEqual(emissions_joueur(r)[-1]["auditeur"], "ilse")
                self.assertEqual(emissions_joueur(r)[-1]["texte"], saisie)
                for qui in ("aubin", "ilse"):
                    self.assertEqual(paroles_retenues(r, qui)[-1][2], saisie)
                    self.assertEqual(emissions_joueur(r)[-1]["auditeurs"], ["ilse"])
                self.assertEqual(appels[0][1]["faits"]["parole_prevue"]["personnage"], "ilse")
                # Le choix de parler est encore celui de l'interprétation ;
                # fournir une question au MJ ne la déclare pas déjà prononcée.
                self.assertNotIn("mots", appels[0][1]["faits"]["parole_prevue"])
                self.assertNotIn("Une réécriture ajoutée", sortie)

    def test_une_adresse_expresse_ne_peut_pas_etre_elargie(self):
        for saisie in ("Aubin, as-tu du bois ?", "je dis à Ilse : bonjour"):
            with self.subTest(saisie=saisie):
                m = scene()
                avant = copy.deepcopy(m.data)
                self.assertIn(prevue(m, saisie)["personnage"], ("aubin", "ilse"))
                with self.assertRaises(ErreurMonde) as e:
                    preparer_parole(m, {"personnage": "tous", "replique": "bonjour", "contenu": [],
                                        "_intention": saisie})
                self.assertIn("Tu t'adresses", str(e.exception))
                self.assertEqual(recharger(m).data, avant)

    def test_verbe_sans_propos_ne_cree_ni_appel_ni_parole(self):
        for saisie in ("je réponds", "je lui réponds", "je murmure"):
            with self.subTest(saisie=saisie):
                m = scene()
                r, sortie, appels = jouer(m, saisie, [], [])
                self.assertEqual(appels, [])
                self.assertIn("Précise ce que tu veux dire", sortie)
                self.assertEqual(emissions_joueur(r), [])
                self.assertEqual(r.data.get("sons", []), m.data.get("sons", []))
                self.assertIsNone(lire(r, "aubin")["rejoint"])

    def test_nom_non_resolu_ne_fait_pas_interpreter_un_dementi_au_mj(self):
        from tests.test_noms import relais
        for saisie, complement in (("Gorm, tu peux décrire le beffroi ?", "de Gorm"),
                                   ("Ilse, tu m'entends ?", "d'Ilse")):
            with self.subTest(saisie=saisie):
                m = relais()
                r, sortie, appels = jouer(m, saisie, [], [])
                self.assertEqual(appels, [])
                self.assertIn("Tu ne connais personne du nom " + complement, sortie)
                self.assertEqual(r.data["noms_connus"], [])
                self.assertEqual(emissions_joueur(r), [])

    def test_une_question_nominale_sans_lien_demande_une_designation_publique(self):
        from tests.test_noms import relais
        for nom in ("Gorm", "Ilse"):
            with self.subTest(nom=nom):
                m = relais()
                r, sortie, appels = jouer(m, f"de quelle couleur sont les yeux de {nom} ?", [], [])
                self.assertIn(f"Tu ne sais pas lequel d'entre eux est {nom}.", sortie)
                self.assertEqual(appels, [])
                self.assertEqual(r.data["noms_connus"], [])
                self.assertEqual(r.data.get("narrations_mj", []), m.data.get("narrations_mj", []))
                self.assertEqual(emissions_pnj(r), [])


class NarrationTests(unittest.TestCase):
    def test_la_reponse_audible_d_une_autre_salle_a_la_meme_autorite(self):
        from tests.test_parole_corrections import banc
        from tests.test_tensions import placer
        from donjon.voix import designation
        for qui in ("marchand", "ilse"):
            with self.subTest(qui=qui):
                m = banc("soir-appel")
                placer(m, qui, "echoppe", (4, 1))
                if qui != "marchand":
                    placer(m, "marchand", "crypte", (2, 3))
                m = recharger(m)
                p = {"personnage": "tous", "replique": "Qui a du bois ?", "contenu": [],
                     "_intention": "je dis à tous : Qui a du bois ?"}
                apercu, _ = preparer_parole(m, p)
                reference = designation(apercu, qui)
                texte = "Une voix répond : « Pas sur moi. »"
                r, sortie, appels = jouer(m, p["_intention"], [
                    parole(p["replique"], personnage="tous"), dialogue(texte)],
                    [rapport(ligne("parole", locuteur=reference, citation="Pas sur moi."))])
                self.assertIn(texte, sortie)
                self.assertEqual(emissions_pnj(r)[-1]["locuteur"], qui)
                self.assertEqual(emissions_pnj(r)[-1]["salle"], "echoppe")
                self.assertIn("joueur", emissions_pnj(r)[-1]["auditeurs"])
                faits = next(e["faits"] for f, e in appels if f == "auditer_narration")
                self.assertIn(reference, faits["interlocuteurs"])
                # Même source et mêmes auditeurs par la voie des faits typés.
                ajout = {"mode": "etablir_faits", "texte": "", "faits": [],
                         "proposition": {"ajouts": [{"type": "parole", "ancrage": reference,
                             "nom": "", "genre": "", "texte": "Je t'entends.", "presentation": ""}]}}
                usage = {"descriptions": [], "usages": [
                    {"perception_requise": False, "indice": False, "motif": "Parole entendue."}]}
                f, rendu, _ = jouer(apercu, "que dit cette voix ?", [ajout, usage], [])
                self.assertIn("Je t'entends.", rendu)
                self.assertEqual(emissions_pnj(f)[-1]["salle"], "echoppe")
                self.assertEqual(emissions_pnj(f)[-1]["auditeurs"], emissions_pnj(r)[-1]["auditeurs"])

    def test_une_presentation_absente_des_mots_n_etablit_aucun_nom_sans_relance(self):
        for nom in ("Aubin", "Ilse"):
            with self.subTest(nom=nom):
                m = scene()
                qui = nom.lower()
                texte = nom + " répond : « Bonsoir. »"
                faux = ligne("parole", locuteur=qui, citation="Bonsoir.")
                faux["presentation"] = nom
                bon = ligne("parole", locuteur=qui, citation="Bonsoir.")
                r, sortie, appels = jouer(m, "à tous : bonsoir", [
                    parole("bonsoir", personnage="tous"), dialogue(texte)], [rapport(faux), rapport(bon)])
                self.assertIn(texte, sortie)
                self.assertEqual([f for f, _ in appels].count("auditer_narration"), 1)
                self.assertEqual([f for f, _ in appels].count("repondre_au_joueur"), 2)
                self.assertNotIn("presentation", emissions_pnj(r)[-1])

    def test_chaque_locuteur_est_audite_et_retenu_dans_son_segment(self):
        for premier, second in [("Oui.", "Moi aussi."), ("Du bois ?", "Pas sur moi !")]:
            with self.subTest(premier=premier):
                m = scene()
                texte = f"Aubin répond : « {premier} » Ilse répond : « {second} »"
                self.assertEqual(len(segments(texte)), 2)
                r, sortie, _ = jouer(m, "à tous : bonsoir", [
                    parole("bonsoir", ("propos", "", "", ""), personnage="tous"), dialogue(texte)],
                    [rapport(ligne("parole", locuteur="aubin", citation=premier),
                             ligne("parole", locuteur="ilse", citation=second))])
                self.assertIn(texte, sortie)
                self.assertEqual([(p["locuteur"], p["texte"]) for p in emissions_pnj(r)[-2:]],
                                 [("aubin", premier), ("ilse", second)])
                self.assertTrue(all("joueur" in p["auditeurs"] for p in emissions_pnj(r)[-2:]))

    def test_sensoriel_d_un_objet_percu_est_enregistre_avant_affichage(self):
        from tests.test_paroles import relais
        for texte in ("Le brasero crépite doucement.", "Une odeur de fumée flotte près du brasero."):
            with self.subTest(texte=texte):
                m = relais()
                m.joueur.update(position=[3, 3], orientation="sud")
                r, sortie, appels = jouer(m, "décris l'ambiance", [dialogue(texte)],
                    [rapport(ligne("ambiance", entites=["brasero"]))])
                self.assertIn(texte, sortie)
                self.assertIn(texte, [a["texte"] for a in r.data["ambiances"]["echoppe"]])
                self.assertTrue(r.objets["brasero"]["allume"])
                self.assertEqual(set(m.objets), set(r.objets))
                faits = next(e["faits"] for f, e in appels if f == "auditer_narration")
                self.assertTrue(faits["objet:brasero"]["allume"])

    def test_demander_de_pouvoir_faire_n_est_pas_une_parole_accomplie(self):
        for texte in ("Tu demandes à passer sous la poutre.", "Tu demandes à sortir dans la cour."):
            with self.subTest(texte=texte):
                self.assertEqual(parole_racontee(texte), [])
                m = scene()
                r, sortie, _ = jouer(m, "est-ce faisable ?", [dialogue(texte)], [verdicts(NEUTRE)])
                self.assertIn(texte, sortie)
                self.assertEqual(emissions_joueur(r), [])

    def test_le_refus_de_proximite_ne_montre_pas_les_coordonnees(self):
        from tests.test_relances_luna import loin_de_la_poutre, CONTRADICTOIRE
        for cible in ("poutre_conduite", "crochets"):
            with self.subTest(cible=cible):
                m = loin_de_la_poutre()
                r, sortie, _ = jouer(m, "je touche cet objet", [
                    action(operation("toucher", cible)), dialogue("Il te faut t'en rapprocher.")], [CONTRADICTOIRE])
                self.assertIn("Approche-toi", sortie)
                self.assertNotIn("du plan)", sortie)
                self.assertNotIn("position =", sortie)
                self.assertEqual(r.data["journal"], [])

    def test_l_approche_structuree_ne_devient_pas_la_description_du_geste(self):
        from donjon.atelier import nouveau_atelier
        from donjon.moteur import Moteur
        from donjon.narration import rendre_resultat
        from donjon.rendu import regarder, fiche, carte
        from tests.test_tensions import recharger
        for saisie, approche, texte in [("je m'étire", "effort", "Tu étires tes bras."),
                                        ("je fais un salut", "expression", "Tu inclines la tête.")]:
            with self.subTest(saisie=saisie):
                m = nouveau_atelier()
                p = proposition(saisie, issue("Un brouillon qui ne doit pas être affiché."), approche=approche)
                temoin = m.copier()
                moteur = Moteur(temoin)
                attendu = rendre_resultat(moteur.executer(moteur.preparer(p)))
                # U-P décrit les paramètres admis, sans transformer l'approche
                # structurée ou le brouillon en une description du geste.
                compris = (f"Compris : Geste. (cibles : aucun; approche : {approche}; minutes : 1; bruit : 0; "
                           "en cas de réussite : effets : aucun; en cas d'échec : effets : aucun)")
                r, sortie, appels = jouer(m, saisie, [action(p)], [])
                self.assertIn(attendu, sortie)
                self.assertEqual(r.data['conversation'][-1]['compris'], compris)
                self.assertEqual(r.data['conversation'][-1]['reponse'], attendu + "\n" + compris)
                self.assertEqual(r.data['conversation'][-1]['nature'], 'resultat_moteur')
                self.assertNotIn(texte, sortie)
                self.assertEqual([f for f, _ in appels], ['repondre_au_joueur', 'auditer_action'])
                self.assertNotIn("geste d'", sortie)
                self.assertNotIn("brouillon", sortie)
                self.assertEqual(r.data["gestes_improvises"][-1]["approche"], approche)
                self.assertEqual(r.joueur["pv"], m.joueur["pv"])
                recharge = recharger(r)
                self.assertEqual(recharge.data, r.data)
                self.assertEqual((regarder(recharge), fiche(recharge), carte(recharge)),
                                 (regarder(r), fiche(r), carte(r)))


class TypesActionsTests(unittest.TestCase):
    def test_une_question_explicitement_dite_reste_une_parole(self):
        from tests.test_paroles import relais
        for saisie in ("Gorm, est-ce que je peux passer sous la poutre ?",
                       "je dis à Gorm : est-ce que je peux soulever le brasero ?"):
            with self.subTest(saisie=saisie):
                m = relais()
                texte = "Gorm répond : « Je ne sais pas. »"
                r, sortie, _ = jouer(m, saisie, [parole("Une réécriture.", personnage="marchand"), dialogue(texte)],
                    [rapport(ligne("parole", locuteur="marchand", citation="Je ne sais pas."))])
                self.assertIn("Tu dis à Gorm", sortie)
                self.assertIn(texte, sortie)
                self.assertEqual(len(emissions_joueur(r)), 1)
                self.assertEqual(r.data["journal"], [])

    def test_une_question_au_mj_ne_devient_pas_une_question_au_pnj(self):
        from tests.test_paroles import relais
        for saisie, cible, attendu in [
                ("est-ce que je pourrais passer sous la poutre effondrée ?", "poutre_conduite", "Approche-toi"),
                ("est-ce que je peux soulever le brasero ?", "brasero", "Rien n'est encore tenté")]:
            with self.subTest(saisie=saisie):
                m = relais()
                m.joueur.update(position=[3, 3], orientation="sud-est")
                p = proposition(saisie, issue("Le geste réussit."), cibles=[cible], approche="adresse")
                r, sortie, appels = jouer(m, saisie, [
                    parole(saisie, personnage="marchand"), action(p)], [])
                # L'adresse ne rend pas la poutre, à deux mètres, manipulable.
                self.assertIn(attendu, sortie)
                self.assertNotIn("Tu dis à", sortie)
                self.assertEqual(emissions_joueur(r), [])
                self.assertEqual(r.data["journal"], [])
                self.assertTrue(any("retour_moteur" in e.get("faits", {}) for _, e in appels))
                # Même frontière lorsque la parole arrive comme correction d'une
                # action mal typée, au lieu d'être la première interprétation.
                r, sortie, _ = jouer(m, saisie, [
                    action(operation("franchir", cible)), parole(saisie, personnage="marchand")], [])
                self.assertNotIn("Tu dis à", sortie)
                self.assertEqual(emissions_joueur(r), [])
                self.assertEqual(r.data["journal"], [])

    def test_franchir_un_autre_type_n_impose_pas_une_echelle(self):
        from donjon.moteur import Moteur
        from tests.test_paroles import relais
        for cible, saisie in [("poutre_conduite", "est-ce que je pourrais passer sous la poutre effondrée ?"),
                              ("brasero", "est-ce que je peux enjamber le brasero ?")]:
            with self.subTest(cible=cible):
                m = relais()
                m.joueur.update(position=[6, 2] if cible == "poutre_conduite" else [3, 3], orientation="sud")
                mauvaise = operation("franchir", cible)
                with self.assertRaises(RefusDeForme):
                    Moteur(m).preparer(mauvaise, "MJ")
                bonne = proposition(saisie, issue("Le geste réussit."), cibles=[cible], approche="adresse")
                r, sortie, appels = jouer(m, saisie, [action(mauvaise), action(bonne)], [])
                self.assertNotIn("Il faut une échelle", sortie)
                self.assertNotIn("ne s'applique pas", sortie)
                self.assertIn("Rien n'est encore tenté", sortie)
                self.assertEqual(r.data["journal"], [])
                self.assertEqual(r.joueur["position"], m.joueur["position"])
                self.assertTrue(any("retour_moteur" in e.get("faits", {}) for _, e in appels))
