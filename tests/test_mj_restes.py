"""Ce que le MJ ne peut plus inventer : une parole que le moteur n'a pas fait entendre, le détail d'un
objet hors de portée, la faisabilité d'un geste que le moteur n'a pas jugée.

Cas réels (bancs Luna) : « Ilse, tu peux m'aider ? » racontée en dialogue (« Tu appelles Ilse et lui
demandes… ») sans que rien ne soit dit ; « à quoi ressemble le mur de l'atelier ? », mur à trois
cases, proposé en etablir_faits et refusé trois fois par la contre-revue sémantique avant que la
règle du moteur (le détail exige d'être à portée) ne soit lue ; « est-ce que je peux fabriquer une
échelle ? » expliqué par Luna (« en principe, les perches pourraient servir ») au lieu du moteur.
Chaque cas vérifie ce que lit le joueur et l'état après rechargement."""
import unittest

from donjon.atelier import nouveau_atelier
from donjon.narration import parole_racontee, paroles_sans_moteur
from donjon.rendu import decrire
from donjon.spatial import installer
from tests.test_parole_commune import paroles_retenues, scene
from tests.test_repli_et_appel import NEUTRE, dialogue, jouer, mj, parole, verdicts
from tests.test_tensions import placer, recharger


def faits(*ajouts):
    return {"mode": "etablir_faits", "texte": "", "faits": [], "proposition": {"ajouts": list(ajouts)}}


def assembler(montants=("", ""), barreaux="", lien="", outil=""):
    return {"mode": "action", "texte": "", "faits": [], "proposition": {
        "action": "assembler", "usage": "echelle", "pieces": {"montants": list(montants), "barreaux": barreaux},
        "lien": lien, "outil": outil, "longueur_cm": 240, "largeur_cm": 40, "difficulte": 0,
        "rythme": "soigne", "justification": ""}}


def fonctions(appels):
    return [f for f, _ in appels]


class ParoleRaconteeTests(unittest.TestCase):
    def test_formes(self):
        racontees = ["Tu appelles Ilse et lui demandes de t'aider.", "Tu demandes à Ilse si elle peut t'aider.",
                     "« Viens », dis-tu.", "Tu lui as dit la vérité.", "Tu t'adresses à Brune.",
                     "Tu lances à Gorm : « attrape »", "Tu salues Gorm."]
        libres = ["Tu peux lui demander de se décaler.", "Si tu lui demandes, elle répondra.",
                  "Tu dis que la porte est ouverte, mais elle est fermée.", "Tu appelles à l'aide.",
                  "Tu lances la corde.", "Tu ne dis rien.", "Brune te demande de partir.", "Gorm te salue."]
        for texte in racontees:
            self.assertTrue(parole_racontee(texte), texte)
        for texte in libres:
            self.assertFalse(parole_racontee(texte), texte)

    def test_une_parole_validee_ou_un_geste_resolu_peuvent_se_raconter(self):
        texte = "Tu demandes à Ilse de t'aider. « Oui », répond-elle."
        self.assertEqual(len(paroles_sans_moteur(texte, {}, adresse=True)), 2)
        self.assertEqual(paroles_sans_moteur(texte, {"conversation_validee": {"faits": []}}, adresse=True), [])
        self.assertEqual(paroles_sans_moteur(texte, {"resultat_resolu": {"faits": []}}, adresse=True), [])


class InterpellationTests(unittest.TestCase):
    """Sans guillemets ni verbe de parole, une interpellation reste à interpréter ; mais si elle n'est pas
    devenue une parole du moteur, le récit ne fait ni parler Corvus, ni répondre personne."""

    def test_cas_reel_l_aide_demandee_a_ilse(self):
        m = scene()
        saisie = "Ilse, tu peux m'aider à déplacer les planches ?"
        raconte = dialogue("Tu demandes à Ilse de t'aider. « Pas maintenant », te répond-elle.")
        reprise, sortie, appels = jouer(m, saisie, [
            raconte, raconte, parole(saisie, ("propos", "", "", ""), personnage="ilse"),
            dialogue("Ilse hésite.")], [verdicts(NEUTRE, NEUTRE), verdicts(NEUTRE)])
        # Ilse l'entendrait : le premier dialogue est renvoyé sans contrôle, avec ce qu'attend le moteur.
        retour = mj(appels)[1]["faits"]["retour_moteur"]
        self.assertEqual(retour["obstacle"], "Rien n'a encore été dit à Ilse.")
        self.assertIn("parole_joueur", retour["attendu"])
        # Le second est contrôlé : Corvus n'a rien dit, personne ne lui répond (contrôle déterministe).
        motifs = " ".join(o["motif"] for o in mj(appels)[2]["controle_narratif"])
        self.assertIn("Corvus n'a rien dit dans ce tour", motifs)
        self.assertIn("Aucun personnage ne parle ni ne réagit", motifs)
        self.assertIn(f"Tu dis à Ilse : « {saisie} »", sortie)
        self.assertIn("Ilse hésite.", sortie)
        self.assertNotIn("Pas maintenant", sortie)
        self.assertNotIn("Tu demandes à Ilse", sortie)
        # Après rechargement : la parole a été dite, à Ilse, et Ilse la retient.
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1], ("joueur", ["ilse"], saisie))
        self.assertEqual(reprise.data["conversation"][-1]["nature"], "parole_joueur")

    def test_sans_interpellation_le_recit_ne_fait_pas_parler_corvus(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "j'ai besoin d'aide pour les planches", [
            dialogue("Tu demandes à Ilse de t'aider."),
            dialogue("Tu peux demander de l'aide à Ilse, à deux pas au sud.")],
            [verdicts(NEUTRE), verdicts(NEUTRE)])
        self.assertIn("Corvus n'a rien dit", mj(appels)[1]["controle_narratif"][0]["motif"])
        self.assertIn("Tu peux demander de l'aide à Ilse", sortie)
        self.assertNotIn("Tu demandes à Ilse", sortie)
        self.assertEqual(reprise.data.get("paroles_joueur", []), [])
        self.assertEqual(paroles_retenues(reprise, "ilse"), [])

    def test_le_mj_peut_repondre_a_une_interpellation_sans_rien_faire_dire(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "Ilse, tu viens ?", [dialogue("Ilse acquiesce.")] + [
            dialogue("Ilse est à deux pas, au sud.")], [verdicts(NEUTRE)])
        # Renvoyé une fois (rien n'est dit) ; le second dialogue, contrôlé, s'affiche.
        self.assertEqual(len(mj(appels)), 2)
        self.assertNotIn("acquiesce", sortie)
        self.assertIn("Ilse est à deux pas, au sud.", sortie)
        self.assertEqual(reprise.data.get("paroles_joueur", []), [])


    def test_meme_nature_un_don_raconte_comme_accepte(self):
        # Luna, copie de la sauvegarde réelle : « Gorm, je te donne la cloche » → « Gorm acquiesce : la
        # cloche est bien revenue au refuge », la cloche restant dans la besace. Renvoyé, le MJ propose
        # le geste : la cloche passe à Gorm, et c'est le moteur qui l'établit.
        m = scene()
        placer(m, "marchand", "antichambre", (2, 3))
        m.objets["cloche"]["lieu"] = "joueur"
        m = recharger(m)
        remettre = {"mode": "action", "texte": "", "faits": [], "proposition": {
            "action": "remettre", "cible": "cloche", "outil": "marchand", "methode": "simple", "difficulte": 0,
            "justification": ""}}
        reprise, sortie, appels = jouer(m, "Gorm, je te donne la cloche", [
            dialogue("Gorm acquiesce : la cloche est bien revenue au refuge."), remettre,
            dialogue("Tu remets la cloche d'alarme à Gorm.")],
            [verdicts(("mecanique", ("resultat_resolu",), ""))])
        self.assertEqual(mj(appels)[1]["faits"]["retour_moteur"]["obstacle"], "Rien n'a encore été dit à Gorm.")
        self.assertNotIn("acquiesce", sortie)
        self.assertEqual(reprise.objets["cloche"]["lieu"], "marchand")


class DetailHorsDePorteeTests(unittest.TestCase):
    """Un objet hors de portée ne se décrit que par ce que Corvus en voit : le moteur refuse d'en établir
    un détail, et son refus passe avant la contre-revue sémantique."""

    def test_les_faits_disent_que_de_loin_on_ne_distingue_pas_les_details(self):
        m = scene()
        self.assertIn("Les planches de bac sont trop loin pour être manipulées d'ici ; de là, leurs détails "
                      "t'échappent", decrire(m, "planches", technique=False))
        self.assertIn("Ilse, meunière évacuée est trop loin pour que tu distingues ses traits",
                      decrire(m, "ilse", technique=False))

    def test_un_detail_d_un_objet_trop_loin(self):
        m = scene()
        avant = set(m.objets)
        reponse = "Tu vois des planches de bac en bois, au sud ; d'ici, tu n'en distingues pas les détails."
        reprise, sortie, appels = jouer(m, "à quoi ressemblent les planches ?", [
            faits({"type": "detail", "ancrage": "planches", "nom": "veinure", "genre": "f",
                   "texte": "Une veinure sombre court le long des planches."}),
            dialogue(reponse)], [verdicts(("mecanique", ("objet:planches",), ""))])
        # Aucune contre-revue de l'ajout : le moteur le refuse d'abord, et dit pourquoi.
        self.assertEqual(fonctions(appels), ["repondre_au_joueur", "repondre_au_joueur", "auditer_narration"])
        retour = mj(appels)[1]["faits"]["retour_moteur"]
        self.assertEqual(retour["obstacle"], "Tu es trop loin pour en distinguer les détails.")
        self.assertIn("non observable de près", retour["attendu"])
        self.assertIn(reponse, sortie)
        self.assertNotIn("veinure", sortie)
        self.assertEqual(set(reprise.objets), avant)

    def test_une_description_physique_d_un_objet_trop_loin(self):
        m = scene()
        physique = {"forme": "plaque", "matiere": "bois", "pieces": 2, "nom_piece": "planche de bac",
                    "dimensions": {"longueur_cm": 180, "largeur_cm": 25, "epaisseur_cm": 3, "diametre_cm": 0,
                                   "hauteur_cm": 0}}
        reprise, sortie, appels = jouer(m, "elles mesurent combien, les planches ?", [
            faits({"type": "qualification", "ancrage": "planches", "physique": physique}),
            dialogue("D'ici, tu ne peux pas juger de leurs mesures.")], [verdicts(("mecanique", ("objet:planches",), ""))])
        self.assertNotIn("auditer_capacites", fonctions(appels))
        retour = mj(appels)[1]["faits"]["retour_moteur"]
        self.assertEqual(retour["obstacle"], "Tu es trop loin pour en distinguer les détails.")
        self.assertIn("ne le remplace pas par un autre", retour["attendu"])
        self.assertNotIn("physique", reprise.objets["planches"])


class FaisabiliteTests(unittest.TestCase):
    """« Puis-je… ? » : le moteur répond, par la fiche du geste ou par la raison de son refus."""

    def test_cas_reel_rien_pour_les_montants(self):
        # Le refuge : les planches sont à Aubin, rien d'autre ne fait une barre libre.
        m = scene()
        reprise, sortie, appels = jouer(m, "est-ce que je peux fabriquer une échelle ?", [
            assembler(), dialogue("En principe, des planches pourraient servir.")], [])
        retour = mj(appels)[1]["faits"]["retour_moteur"]
        attendu = ("Pour une échelle, il te manque deux montants, deux barres libres d'une seule pièce : "
                   "rien de tel n'est à ta disposition ici.")
        self.assertEqual(retour["obstacle"], attendu)
        self.assertIn("question de faisabilité", retour["consigne"])
        self.assertIn(attendu, sortie)
        self.assertNotIn("En principe", sortie)
        self.assertEqual(reprise.data["conversation"][-1]["nature"], "refus_avant_action")
        self.assertFalse(reprise.data["journal"])

    def test_un_dialogue_qui_juge_lui_meme_est_renvoye_une_fois(self):
        # Cas réel (Luna, sauvegarde réelle) : « Oui, fabriquer une échelle est possible en principe… »
        m = scene()
        reprise, sortie, appels = jouer(m, "est-ce que je peux fabriquer une échelle ?", [
            dialogue("Oui, fabriquer une échelle est possible en principe."), assembler(),
            dialogue("En principe, des planches pourraient servir.")], [])
        # Ni le premier dialogue ni le dernier ne sont contrôlés : ni l'un ni l'autre ne s'affiche.
        self.assertEqual(fonctions(appels), ["repondre_au_joueur"] * 3)
        self.assertIn("proposition de ce geste", mj(appels)[1]["faits"]["retour_moteur"]["attendu"])
        self.assertIn("il te manque deux montants", sortie)
        self.assertNotIn("principe", sortie)
        self.assertFalse(reprise.data["journal"])

    def test_meme_nature_grimper_sans_appui(self):
        # Luna, copie de la sauvegarde réelle : le moteur disait « Il faut d'abord prendre l'objet qui
        # servira d'appui. » sans dire qu'il n'y en a aucun ici.
        m = scene()
        grimper = {"mode": "action", "texte": "", "faits": [], "proposition": {
            "action": "composer", "justification": "", "etapes": [{
                "operation": "franchir_obstacle", "cible": "appui_clocher", "destination": "chambre_cloche",
                "outil": "", "methode": "appui_mobile", "difficulte": 19}]}}
        reprise, sortie, appels = jouer(m, "est-ce que je pourrais grimper sur le palier ?", [grimper, grimper], [])
        self.assertEqual(len(mj(appels)), 2)
        self.assertIn("Il te faut un appui long à tenir, une perche par exemple : rien de tel n'est à ta "
                      "disposition ici.", sortie)
        self.assertEqual(reprise.joueur["salle"], "antichambre")
        self.assertFalse(reprise.data["journal"])

    def test_s_il_insiste_son_dialogue_est_controle_comme_un_autre(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "est-ce que je pourrais voler jusqu'au palier ?", [
            dialogue("Tu n'as pas d'ailes."), dialogue("Tu n'as aucun moyen de voler.")], [verdicts(NEUTRE)])
        self.assertEqual(fonctions(appels), ["repondre_au_joueur", "repondre_au_joueur", "auditer_narration"])
        self.assertIn("Tu n'as aucun moyen de voler.", sortie)
        self.assertNotIn("ailes", sortie)
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], "Tu n'as aucun moyen de voler.")

    def test_une_question_adressee_a_quelqu_un_n_en_est_pas_une(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "Ilse, est-ce que je peux t'aider ?",
                                        [dialogue("Oui.")] + [dialogue("Ilse est à deux pas, au sud.")],
                                        [verdicts(NEUTRE)])
        # Une interpellation, pas un « puis-je » : c'est ce qu'en dit le renvoi.
        self.assertEqual(mj(appels)[1]["faits"]["retour_moteur"]["obstacle"], "Rien n'a encore été dit à Ilse.")
        self.assertIn("Ilse est à deux pas, au sud.", sortie)

    def test_ce_qui_manque_compte_ce_que_corvus_verrait_en_se_tournant(self):
        # Banc Luna : la ficelle de l'atelier, dans le dos de Corvus, était dite absente (« rien de tel
        # n'est à ta disposition ici »). Ce qu'il peut désigner compte (``Monde.designable``).
        m = nouveau_atelier()
        installer(m)
        m = recharger(m)
        self.assertFalse(m.accessible("ficelle"))
        reprise, sortie, appels = jouer(m, "est-ce que je peux fabriquer une échelle avec ces perches ?", [
            assembler(("perche_1", "perche_2"), "perche_3", "", "hache"),
            assembler(("perche_1", "perche_2"), "perche_3", "ficelle", "hache")], [])
        retour = mj(appels)[1]["faits"]["retour_moteur"]
        self.assertEqual(retour["obstacle"], "Pour une échelle, il te manque un lien pour attacher les barreaux.")
        self.assertIn("parmi ficelle", retour["attendu"])
        self.assertIn("Approche-toi de la perche de bois 1", sortie)
        self.assertFalse(reprise.data["journal"])

    def test_des_perches_trop_loin(self):
        m = nouveau_atelier()
        installer(m)
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "est-ce que je peux fabriquer une échelle avec ces perches ?", [
            assembler(("perche_1", "perche_2"), "perche_3", "ficelle", "hache")], [])
        # Un seul appel : la distance, seul un pas du joueur la lève ; c'est la réponse du moteur.
        self.assertEqual(len(mj(appels)), 1)
        self.assertIn("Approche-toi de la perche de bois 1", sortie)
        self.assertFalse(reprise.data["journal"])
        self.assertFalse(any(o["nom"].startswith("échelle") for o in reprise.objets.values()))


if __name__ == "__main__":
    unittest.main()
