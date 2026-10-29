"""Une perception est un geste complet ; son résultat n'est pas une ambiance."""
import copy
import unittest
from unittest.mock import patch

from donjon.atelier import nouveau_atelier
from donjon.commandes import analyser
from donjon.couverture_action import entree
from donjon.monde import nouveau_monde
from donjon.moteur import Moteur, PERCEPTIONS, Plan, proposition
from donjon.rendu import regarder
from donjon.spatial import installer
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_ecoute import au_palier, parler_pendant
from tests.test_relances_luna import action
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger, relais


class PerceptionGesteTests(unittest.TestCase):
    def test_les_operations_de_perception_sont_declarees_meme_sans_effet_immediat(self):
        # Pas de liste parallèle dans les revues ; même contrat dans une étape.
        for geste in PERCEPTIONS:
            with self.subTest(geste=geste):
                p = Plan(proposition(geste), 0, "Percevoir.")
                self.assertTrue(p.realise_geste)
                self.assertEqual(entree("je cherche", p)["plan"]["perception"],
                                 {"action": geste, "cible": ""})
                compose = Plan({"action": "composer"}, 0, "Chercher.", plans=[p])
                self.assertTrue(compose.realise_geste)
                self.assertIn("perception", entree("je cherche", compose)["plan"]["etapes"][0])
        self.assertFalse(Plan(proposition("attendre"), 0, "Attendre.").realise_geste)

    def test_ecouter_et_chercher_sans_revue_et_sont_sauves(self):
        for saisie, p in (("j'écoute à la porte pour savoir s'il y a quelque chose derrière",
                           proposition("ecouter")),
                          ("je cherche des traces de pas sur le sol", proposition("observer", "scene"))):
            with self.subTest(saisie=saisie):
                m = au_palier(relais(), (0, 3))
                parler_pendant(m)
                avant = copy.deepcopy(m.data)
                # Le fournisseur simulé accepte une opération de perception explicite,
                # pas un plan vide réputé conforme sans lire son dossier.
                from donjon.mj import MJOpenAI
                original = MJOpenAI._auditer_action
                def revue(mj, intention, plan, revision, monde):
                    dossier = entree(intention, plan, monde)["plan"]
                    self.assertEqual(dossier["perception"]["action"], p["action"])
                    self.assertEqual(dossier["perception"]["cible"], p["cible"])
                    return original(mj, intention, plan, revision, monde)
                with patch.object(MJOpenAI, "_auditer_action", revue):
                    r, texte, appels = jouer(m, "mj " + saisie, [action(p)], [])
                self.assertEqual([f for f, _ in appels], ["repondre_au_joueur"])
                resultat = r.data["conversation"][-1]
                self.assertEqual(resultat["nature"], "resultat_moteur")
                self.assertIn(resultat["reponse"], texte)
                self.assertEqual(r.joueur["position"], avant["joueur"]["position"])
                if p["action"] == "ecouter":
                    self.assertEqual(r.data["minutes"], avant["minutes"] + 3)
                    self.assertEqual(r.data["journal"][-1]["action"]["action"], "ecouter")
                    self.assertIn("Tu tends l'oreille contre la porte étanche du beffroi.", texte)
                    self.assertIn("Tu entends une voix à l'ouest.", texte)
                else:
                    self.assertEqual(r.data["minutes"], avant["minutes"])
                    self.assertEqual(resultat["reponse"], regarder(r).strip())
                    self.assertNotIn("aucune trace", texte)

    def test_une_perception_corrigee_ne_devient_pas_un_geste_vide(self):
        m = au_palier(relais(), (0, 3))
        r, texte, appels = jouer(m, "mj j'écoute à la porte", [
            action(proposition("ecouter", "porte_etanche")),
            action(proposition("ecouter"))], [])
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 0)
        self.assertEqual(r.data["minutes"], m.data["minutes"] + 3)
        self.assertEqual(r.data["journal"][-1]["action"]["action"], "ecouter")
        self.assertIn("rien de particulier ne te parvient", texte)
        self.assertNotIn("aucun effet", texte)

    def test_un_resultat_sans_perception_est_refuse_et_une_ambiance_persiste(self):
        for resultat in ("Aucun son de l'autre côté ne t'est perceptible.",
                         "Tu ne trouves aucune trace de pas sur le sol."):
            with self.subTest(resultat=resultat):
                m = au_palier(relais(), (0, 3))
                ambiance = "Une odeur de pierre humide flotte autour de toi."
                r, texte, appels = jouer(m, "mj dis-moi ce que tu remarques", [
                    dialogue(resultat), dialogue(ambiance)], [
                    rapport(ligne("mecanique", motif="Résultat de perception sans source.")),
                    rapport(ligne("ambiance", entites=["odeur de pierre humide"]))])
                self.assertNotIn(resultat, texte)
                self.assertIn(ambiance, texte)
                self.assertEqual(r.data["minutes"], m.data["minutes"])
                self.assertEqual(r.data["journal"], m.data["journal"])
                self.assertEqual(r.data["ambiances"][m.joueur["salle"]][-1]["texte"], ambiance)
                self.assertNotIn(resultat, str(r.data["conversation"]))
                self.assertEqual(sum(f == "auditer_narration" for f, _ in appels), 2)


class VueCouranteTests(unittest.TestCase):
    def test_absence_dans_le_noir_personnes_et_objet_apres_recharge(self):
        from pathlib import Path
        from donjon.monde import Monde
        reel = Monde.charger(Path("tests/data/scenes/signes_ecart_relais_noir.json"))
        autre = nouveau_monde()
        installer(autre)
        for o in autre.objets.values():
            if "allume" in o:
                o["allume"] = False
        for m, faux, corrige in (
                (reel, "Tu ne sais pas si Ilse a peur de Brune : tu n’as aucun indice sur ses sentiments, et aucune des deux n’est ici pour que tu puisses le vérifier.",
                 "Tu ne les vois pas dans l’obscurité."),
                (autre, "Il n'y a aucun objet dans cette pièce.",
                 "Tu ne vois pas les objets dans l’obscurité.")):
            with self.subTest(faux=faux):
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                # Le fournisseur simulé exerce la portée indépendamment du verdict,
                # y compris le classement neutre du constat réel. Le jugement de sens
                # reste celui de l'auditeur ; ce test ne simule pas sa compréhension.
                refus = {**ligne("neutre", motif="Absence au-delà de la vue couverte."),
                         "portee_mecanique": "sans_fondement"}
                r, texte, appels = jouer(m, "mj qui est ici ?", [dialogue(faux), dialogue(corrige)],
                    [rapport(refus), rapport(ligne("mecanique", ["perception"]))])
                faits = self.assertVueFournie(m, appels)
                self.assertEqual(faits["perception"]["couverture_vue"]["portee"], "aucune")
                self.assertSansGeste(avant, r)
                self.assertNotIn(faux, texte)
                self.assertNotIn(faux, str(r.data["conversation"]))
                self.assertNotIn(faux, str(r.data["narrations_mj"]))
                self.assertIn(corrige, texte)
                self.assertEqual(r.data["conversation"][-1]["reponse"], corrige)
                revision = [e for f, e in appels if f == "repondre_au_joueur"][1]
                self.assertIn("couverture_vue", str(revision["controle_narratif"]))
                self.assertIn("objets_visibles", str(revision["controle_narratif"]))
                if "ilse" in m.objets:
                    self.assertEqual(r.objets["ilse"]["lieu"], r.joueur["salle"])
                    self.assertEqual(r.objets["brune"]["lieu"], r.joueur["salle"])

    def test_couverture_visuelle_ne_depend_pas_de_la_liste_des_entites(self):
        from donjon.perception import couverture_vue
        m = nouveau_monde()
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        self.assertEqual(couverture_vue(m)["portee"], "aucune")
        m.data["salles"][m.joueur["salle"]]["lumiere_naturelle"] = 2
        self.assertEqual(couverture_vue(m)["portee"], "salle")
        installer(m)
        # La vue orientée ne couvre pas automatiquement la pièce éclairée.
        self.assertEqual(couverture_vue(m)["portee"], "partielle")

    def assertVueFournie(self, monde, appels):
        faits = next(e["faits"] for f, e in appels if f == "auditer_narration")
        attendus = {o["id"] for o in monde.contexte()["objets_perceptibles"] if o["visible"]}
        self.assertEqual(set(faits["perception"]["objets_visibles"]), attendus)
        self.assertEqual(attendus, {v["id"] for k, v in faits.items()
                                    if k.startswith("objet:") and v["visible"]})
        return faits

    def test_absence_etablie_par_fouille_reste_admise_apres_recharge(self):
        m = relais()
        from donjon.defi import BEFFROI
        m.joueur.update(salle=BEFFROI, position=[4, 3])
        m = recharger(m)
        r, texte, _ = jouer(m, "mj je fouille le coffre", [action(proposition("toucher", "coffre"))], [])
        self.assertIn("est vide : tes mains n'y trouvent rien", texte)
        self.assertEqual(r.data["journal"][-1]["action"]["action"], "toucher")
        self.assertEqual(r.objets["coffre"]["lieu"], m.objets["coffre"]["lieu"])
        phrase = "Le coffre est vide."
        suite, visible, appels = jouer(r, "mj qu'y avait-il dans le coffre ?", [dialogue(phrase)],
                                     [rapport(ligne("mecanique", ["objet:coffre"]))])
        faits = self.assertVueFournie(r, appels)
        self.assertTrue(faits["objet:coffre"]["contenu_vide"])
        self.assertIn(phrase, visible)
        self.assertEqual(suite.data["conversation"][-1]["reponse"], phrase)
        self.assertEqual(suite.data["journal"], r.data["journal"])

    def assertSansGeste(self, avant, reprise):
        for champ in ("minutes", "journal", "objets", "joueur", "jets"):
            self.assertEqual(reprise.data[champ], avant[champ], champ)

    def test_absence_visible_atelier_et_autre_salle_sans_fouille_apres_recharge(self):
        atelier = nouveau_atelier()
        installer(atelier)
        # Même parcours que le banc réel jusqu'aux questions 9 et 12.
        moteur = Moteur(atelier)
        for saisie in ("nord", "est"):
            moteur.executer(moteur.preparer(analyser(atelier, saisie)))
        moteur.executer(moteur.preparer(proposition("prendre", "ficelle")))
        crypte = nouveau_monde()
        installer(crypte)
        for m, saisie, phrase in (
                (atelier, "y a-t-il des outils qui traînent dans la cour ?",
                 "Tu ne vois pas d'autres outils traîner dans la cour."),
                (atelier, "je cherche une pierre pour caler une échelle",
                 "Tu ne vois pas de pierre distincte à portée de main."),
                (crypte, "y a-t-il des outils posés ici ?",
                 "Tu ne vois pas d'outil posé ici.")):
            with self.subTest(saisie=saisie):
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                r, texte, appels = jouer(m, "mj " + saisie, [dialogue(phrase)],
                                         [rapport(ligne("mecanique", ["perception"]))])
                self.assertEqual([f for f, _ in appels], ["repondre_au_joueur", "auditer_narration"])
                self.assertVueFournie(m, appels)
                self.assertSansGeste(avant, r)
                self.assertIn(phrase, texte)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], phrase)
                self.assertEqual(r.data["conversation"][-1]["reponse"], phrase)
                self.assertFalse(r.data.get("ambiances", {}))
                self.assertEqual(regarder(r), regarder(m))

    def test_absence_hors_vue_fermee_ou_noire_refusee_sans_perception_executee(self):
        for portee in ("porte", "contenant", "noir"):
            with self.subTest(portee=portee):
                m = nouveau_monde()
                installer(m)
                if portee == "contenant":
                    m.joueur.update(salle="crypte", position=[1, 2], orientation="est")
                    self.assertFalse(m.objets["coffre"]["ouverte"])
                    resultat = "Le coffre ne contient aucun objet."
                    attendu_absent = "anneau"
                elif portee == "noir":
                    for o in m.objets.values():
                        if "allume" in o:
                            o["allume"] = False
                    resultat = "Il n'y a aucun objet dans cette pièce."
                    attendu_absent = "cle"
                else:
                    self.assertFalse(m.objets["porte"]["ouverte"])
                    resultat = "Derrière la porte, il n'y a aucun objet."
                    attendu_absent = "coffre"
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                limite = "Tu ne peux pas en voir le contenu d'ici."
                r, texte, appels = jouer(m, "mj que vois-tu ?", [dialogue(resultat), dialogue(limite)], [
                    rapport(ligne("invention_protegee", motif="Absence hors de la vue courante, sans perception exécutée.")),
                    rapport(ligne("mecanique", ["perception"]))])
                faits = self.assertVueFournie(m, appels)
                self.assertNotIn("objet:" + attendu_absent, faits)
                self.assertNotIn(attendu_absent, faits["perception"]["objets_visibles"])
                if portee == "noir":
                    self.assertEqual(faits["perception"]["niveau"], 0)
                    self.assertEqual(faits["perception"]["objets_visibles"], [])
                    # Accessible au toucher ne veut pas dire visible.
                    self.assertIn("objet:couteau", faits)
                    self.assertFalse(faits["objet:couteau"]["visible"])
                self.assertSansGeste(avant, r)
                self.assertNotIn(resultat, texte)
                self.assertNotIn(resultat, str(r.data["conversation"]))
                self.assertNotIn(resultat, str(r.data["narrations_mj"]))
                self.assertIn(limite, texte)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], limite)
                self.assertEqual(regarder(r), regarder(m))
                relance = [e for f, e in appels if f == "repondre_au_joueur"][1]
                self.assertIn("invention_protegee", str(relance["controle_narratif"]))


if __name__ == "__main__":
    unittest.main()
