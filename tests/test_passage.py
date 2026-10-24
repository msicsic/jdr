"""Laisser passer, demander le passage, pousser (``donjon/passage.py``), pour le joueur comme pour
les PNJ. Vérifié sur l'état du monde et sur ce que lit le joueur, après rechargement.

Cas réel : Brune, désœuvrée sur le seuil du refuge, barrait la sortie au joueur ; « je demande à
Brune de se pousser » lui faisait promettre de bouger sans que rien ne la déplace, et « je la
pousse » était refusé faute d'action."""

from tests.support import lier, relation
import unittest
from unittest.mock import patch

from tests.support import regarder
from tests.test_marche import ecarter_tous, faire, intention, tranquilles
from tests.test_paroles import jouer, parole, reponse_pnj
from tests.test_tensions import placer, recharger, vivre
from donjon.commandes import analyser
from donjon.esprits import croire, lire
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.paroles import preparer_parole
from donjon.passage import raison_de_rester

SEUIL = (0, 3)         # case intérieure de la seule sortie du refuge, vers la conduite basse


def distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def refuge():
    """Le cas réel reconstruit : Brune, désœuvrée, se tient sur le seuil du refuge ; Ilse et Aubin
    sont plus loin dans la salle, Gorm dans la conduite ; le joueur, à côté d'elle, regarde la
    sortie."""
    m = tranquilles()
    placer(m, "brune", "antichambre", SEUIL)
    placer(m, "ilse", "antichambre", (5, 2))
    placer(m, "aubin", "antichambre", (5, 5))
    placer(m, "marchand", "echoppe", (4, 1))
    regarder(m, "brune", (4, 3))
    m.joueur.update(salle="antichambre", position=[1, 3], orientation="ouest")
    return recharger(m)


def tenter(m, action, cible="", outil="", jets=None):
    """L'action du joueur ; ``jets`` : ses premiers dés (le sien, puis celui qui s'oppose), 10 ensuite."""
    moteur = Moteur(m)
    plan = moteur.preparer(proposition(action, cible, outil))
    if jets is None:
        return moteur.executer(plan)
    des = list(jets)
    with patch.object(Monde, "d20", side_effect=lambda: des.pop(0) if des else 10):
        return moteur.executer(plan)


def porte_ouverte_a_gorm(m):
    """Placement d'auteur : la porte de la salle des vannes est fermée sans être verrouillée, et
    Gorm le sait."""
    m.objets["porte"].update(ouverte=False, verrouillee=False)
    croire(m, "marchand", "porte", "verrouillee", False, "essai")


class LaisserPasserJoueurTests(unittest.TestCase):
    def test_cas_reel_brune_s_ecarte_du_seuil(self):
        m = refuge()
        texte = faire(m, "marcher", "ouest")
        self.assertIn("Brune, batelière évacuée, s'écarte pour te laisser passer.", texte)
        self.assertIn("Tu avances d'un pas.", texte)
        m = recharger(m)
        brune = m.objets["brune"]
        self.assertEqual((m.joueur["salle"], tuple(m.joueur["position"])), ("antichambre", SEUIL))
        # Un pas de côté, dans la salle, hors du chemin : ni le seuil, ni la case du joueur.
        self.assertEqual(brune["lieu"], "antichambre")
        self.assertEqual(distance(brune["position"], SEUIL), 1)
        self.assertEqual(brune["position"][0], 0)
        self.assertTrue(any("s'écarte pour laisser passer" in c["texte"] for c in m.data["chronique"]))
        # La sortie est libre : le pas suivant mène dans la conduite basse.
        self.assertIn("Tu entres dans : Conduite basse.", faire(m, "marcher", "ouest"))
        self.assertEqual(recharger(m).joueur["salle"], "echoppe")

    def test_ilse_au_milieu_du_refuge_s_ecarte_aussi(self):
        m = tranquilles()
        placer(m, "ilse", "antichambre", (3, 1))
        m.joueur.update(salle="antichambre", position=[2, 1], orientation="est")
        texte = faire(m, "marcher", "est")
        self.assertIn("Ilse, meunière évacuée, s'écarte pour te laisser passer.", texte)
        m = recharger(m)
        self.assertEqual(tuple(m.joueur["position"]), (3, 1))
        ilse = tuple(m.objets["ilse"]["position"])
        # De côté (nord ou sud), pas devant le joueur ni sur sa ligne.
        self.assertEqual(ilse[0], 3)
        self.assertNotEqual(ilse, (3, 1))

    def test_un_pnj_mefiant_ne_s_ecarte_pas(self):
        m = refuge()
        lier(m, "brune", "joueur", False, "vu")
        with self.assertRaises(ErreurMonde) as refus:
            faire(m, "marcher", "ouest")
        self.assertEqual(str(refus.exception), "Brune, batelière évacuée se tient là, sur ton passage, et ne s'écarte pas.")
        self.assertIn("se méfie", refus.exception.attendu)
        self.assertIn("type passage", refus.exception.attendu)
        self.assertIn("action pousser", refus.exception.attendu)
        m = recharger(m)
        self.assertEqual(tuple(m.objets["brune"]["position"]), SEUIL)
        self.assertEqual(tuple(m.joueur["position"]), (1, 3))

    def test_un_geste_en_cours_la_retient(self):
        m = tranquilles()
        # Placement d'auteur : Brune, à côté des planches, s'apprête à en prendre.
        placer(m, "brune", "antichambre", (2, 4))
        intention(m, "brune", [{"operation": "prendre", "cible": "planches"}], but={"type": "bois"}, motif="chaleur")
        m.joueur.update(salle="antichambre", position=[2, 3], orientation="sud")
        with self.assertRaises(ErreurMonde) as refus:
            faire(m, "marcher", "sud")
        self.assertIn("occupée à ce qu'elle fait", str(refus.exception))
        self.assertIn("geste en cours", refus.exception.attendu)
        self.assertEqual(tuple(recharger(m).objets["brune"]["position"]), (2, 4))


class DemanderLePassageTests(unittest.TestCase):
    def orgueilleuse(self):
        """Brune, plus fière qu'altruiste, ne s'écarte pas d'elle-même : il faut le lui demander."""
        m = refuge()
        m.objets["brune"]["profil"]["valeurs"].update(fierte=80, altruisme=30)
        with self.assertRaises(ErreurMonde):
            faire(m, "marcher", "ouest")
        return m

    def test_cas_reel_acceptee_elle_s_ecarte_vraiment(self):
        m = self.orgueilleuse()
        reprise, sortie, appels = jouer(m, "je demande a brune de se pousser", [
            parole("Brune, pousse-toi, s'il te plaît.", ("passage", "", "", ""), personnage="brune"),
            reponse_pnj("Brune s'écarte en maugréant.")], jet=20)
        faits = appels[1]["faits"]["conversation_validee"]["faits"]
        self.assertIn("Brune, batelière évacuée s'écarte d'un pas pour te laisser passer.", faits)
        self.assertIn("Tu dis à Brune : « Brune, pousse-toi, s'il te plaît. »", sortie)
        brune = reprise.objets["brune"]
        self.assertEqual(distance(brune["position"], SEUIL), 1)
        self.assertEqual(brune["position"][0], 0)
        # La sortie est libre.
        self.assertIn("Tu avances d'un pas.", faire(reprise, "marcher", "ouest"))

    def test_refusee_elle_reste_et_le_mj_le_sait(self):
        m = self.orgueilleuse()
        reprise, _, appels = jouer(m, "je demande a brune de se pousser", [
            parole("Brune, pousse-toi.", ("passage", "", "", ""), personnage="brune"),
            reponse_pnj("Brune ne bouge pas.")], jet=1)
        faits = appels[1]["faits"]["conversation_validee"]["faits"]
        self.assertIn("Brune, batelière évacuée n'est pas convaincue et reste où elle est.", faits)
        self.assertEqual(tuple(reprise.objets["brune"]["position"]), SEUIL)

    def test_mefiante_elle_refuse_quel_que_soit_le_jet(self):
        m = refuge()
        lier(m, "brune", "joueur", False, "vu")
        with patch.object(Monde, "d20", return_value=20):
            travail, rapport = preparer_parole(m, {"_intention": "je lui dis : Laisse-moi passer.", "personnage": "brune", "replique": "Laisse-moi passer.",
                                                   "contenu": [{"type": "passage", "sujet": "", "attribut": "",
                                                                "valeur": ""}]})
        self.assertEqual(rapport["faits"], ["Brune, batelière évacuée refuse de s'écarter : elle ne te fait pas confiance."])
        self.assertEqual(tuple(recharger(travail).objets["brune"]["position"]), SEUIL)

    def test_une_demande_pour_un_autre_n_est_pas_un_passage(self):
        m = refuge()
        travail, rapport = preparer_parole(m, {"_intention": "je lui dis : Dis à Ilse de bouger.", "personnage": "brune", "replique": "Dis à Ilse de bouger.",
                                               "contenu": [{"type": "passage", "sujet": "ilse", "attribut": "",
                                                            "valeur": ""}]})
        self.assertEqual(rapport["faits"], [])
        self.assertEqual(tuple(travail.objets["brune"]["position"]), SEUIL)


class PousserJoueurTests(unittest.TestCase):
    def scene(self):
        m = refuge()
        lier(m, "brune", "joueur", False, "vu")  # Elle ne s'écarte pas pour lui.
        placer(m, "ilse", "antichambre", (0, 2))
        regarder(m, "ilse", "joueur")    # Ilse regarde le joueur ; Aubin, le mur du fond.
        regarder(m, "aubin", (8, 6))
        return recharger(m)

    def test_la_commande_pousser(self):
        m = self.scene()
        self.assertEqual(analyser(m, "pousser brune"), proposition("pousser", "brune"))
        self.assertEqual(analyser(m, "pousser brune vers le nord"), proposition("pousser", "brune", "nord"))
        self.assertEqual(analyser(m, "pousser brune vers l'ouest"), proposition("pousser", "brune", "ouest"))

    def test_reussie_elle_recule_et_les_temoins_s_en_souviennent(self):
        m = self.scene()
        texte = tenter(m, "pousser", "brune", jets=[18, 3])
        self.assertIn("REUSSITE", texte)
        self.assertIn("Tu pousses Brune, batelière évacuée : elle recule d'un pas.", texte)
        self.assertIn("Ilse, meunière évacuée t'a vu faire.", texte)
        m = recharger(m)
        brune = m.objets["brune"]
        # Écartée de son chemin : de côté, dans le refuge, pas dans la conduite.
        self.assertEqual(brune["lieu"], "antichambre")
        # La réaction 4c peut déjà la faire marcher pendant les 3 s du geste : le recul
        # réellement appliqué reste dans le journal physique, indépendamment de la fuite.
        poussee = next(e for e in m.data["historique_corps"] if e["type"] == "poussee")
        self.assertEqual(distance(poussee["arrivee"][1], SEUIL), 1)
        self.assertNotEqual(tuple(brune["position"]), (1, 3))
        self.assertIs(relation(m, "brune", "joueur")["valeur"], False)
        self.assertIs(relation(m, "ilse", "joueur")["valeur"], False)
        # Aubin, qui regardait ailleurs, n'a rien vu : il ne le sait que par ce qu'Ilse lui en dit.
        from donjon.relations import croyance
        self.assertTrue((croyance(m, "aubin", "joueur") or {"source": "dit:"})["source"].startswith("dit:"))
        self.assertIn({"type": "vu_agir", "auteur": "joueur", "operation": "pousser", "objet": "brune"},
                      [{k: v for k, v in s.items() if k not in ("minute", "dit_a", "preuve", "victime", "deja_entendu")} for s in lire(m, "ilse")["memoire"]])
        # Elle peut regagner le seuil pendant sa fuite : pousser ne promet plus que la case
        # restera libre après les réactions sur la même horloge.
        if tuple(brune["position"]) == SEUIL:
            with self.assertRaises(ErreurMonde) as cm:
                faire(m, "marcher", "ouest")
            self.assertTrue(cm.exception.attendu)
        else:
            self.assertIn("Tu avances d'un pas.", faire(m, "marcher", "ouest"))

    def test_manquee_rien_ne_bouge_mais_la_confiance_est_perdue(self):
        m = self.scene()
        lire(m, "brune")["croyances"].pop("joueur", None)
        texte = tenter(m, "pousser", "brune", jets=[3, 18])
        self.assertIn("ECHEC", texte)
        self.assertIn("Tu pousses Brune, batelière évacuée, qui tient bon.", texte)
        m = recharger(m)
        self.assertEqual(tuple(m.objets["brune"]["position"]), SEUIL)
        self.assertIs(relation(m, "brune", "joueur")["valeur"], False)
        self.assertIs(relation(m, "ilse", "joueur")["valeur"], False)
        # Bousculée, elle ne s'écarte plus de bon gré.
        with self.assertRaises(ErreurMonde):
            faire(m, "marcher", "ouest")

    def test_refus_qui_guident(self):
        m = self.scene()
        regarder(m, "joueur", (2, 1))
        placer(m, "ilse", "antichambre", (3, 1))
        with self.assertRaises(ErreurMonde) as loin:
            faire(m, "pousser", "ilse")
        regarder(m, "joueur", SEUIL)
        self.assertIn("trop loin", str(loin.exception))
        self.assertIn("approche-toi", loin.exception.attendu)
        with self.assertRaises(ErreurMonde) as vers_soi:
            Moteur(m).preparer(proposition("pousser", "brune", "est"))
        self.assertIn("vers soi", str(vers_soi.exception))
        self.assertIn("nord", vers_soi.exception.attendu)
        with self.assertRaises(ErreurMonde) as objet:
            faire(m, "pousser", "planches")
        self.assertIn("qu'une personne", str(objet.exception))
        # Contre le mur du nord : nulle part où reculer de ce côté.
        m.joueur.update(position=[3, 1], orientation="nord")
        placer(m, "ilse", "antichambre", (3, 0))
        with self.assertRaises(ErreurMonde) as mur:
            Moteur(m).preparer(proposition("pousser", "ilse", "nord"))
        self.assertIn("nulle part où reculer", str(mur.exception))


class PorteEtroiteTests(unittest.TestCase):
    """Deux PNJ au passage étroit du palier des vannes : la porte de la salle des vannes s'ouvre
    depuis la case qui la précède, où l'un se tient quand l'autre veut passer."""
    PORTE = (0, 3)

    def palier(self, valeurs_gorm=None):
        m = tranquilles()
        ecarter_tous(m, "brune", "ilse")
        porte_ouverte_a_gorm(m)
        placer(m, "aubin", "beffroi", self.PORTE)
        regarder(m, "aubin", (5, 3))
        placer(m, "marchand", "beffroi", (3, 3))
        regarder(m, "marchand", (0, 3))
        if valeurs_gorm:
            m.objets["marchand"]["profil"]["valeurs"].update(valeurs_gorm)
        intention(m, "marchand", [{"operation": "aller", "lieu": "crypte"}])
        m.joueur.update(salle="beffroi", position=[6, 3], orientation="ouest")
        return recharger(m)

    def test_aubin_s_ecarte_et_gorm_passe(self):
        m, lignes = vivre(self.palier(), 1)
        self.assertEqual(m.objets["marchand"]["lieu"], "crypte")
        self.assertEqual(m.objets["aubin"]["lieu"], "beffroi")
        self.assertNotEqual(tuple(m.objets["aubin"]["position"]), self.PORTE)
        textes = [c["texte"] for c in m.data["chronique"]]
        self.assertIn("Aubin s'écarte pour laisser passer Gorm.", textes)
        self.assertIn("Aubin, vieux passeur, s'écarte pour laisser passer Gorm, gardien du relais.", lignes)

    def test_deux_qui_vont_a_la_meme_porte_passent_l_un_apres_l_autre(self):
        # Cas du banc de l'auberge : devant la porte qu'il allait ouvrir, Aubin ne s'écarte pas
        # (avant, chacun s'écartait pour l'autre et reprenait la place, sans fin).
        m = self.palier()
        croire(m, "aubin", "porte", "verrouillee", False, "essai")
        intention(m, "aubin", [{"operation": "aller", "lieu": "crypte"}])
        self.assertEqual(raison_de_rester(m, "aubin"), "geste")
        placer(m, "marchand", "beffroi", (1, 3))  # Gorm arrive sur ses talons.
        m, _ = vivre(m, 2)
        self.assertEqual(m.objets["aubin"]["lieu"], "crypte")
        self.assertEqual(m.objets["marchand"]["lieu"], "crypte")
        self.assertFalse(any("laisser passer" in c["texte"] for c in m.data["chronique"]))

    def test_mefiant_aubin_refuse_et_gorm_patiente(self):
        m = self.palier()
        lier(m, "aubin", "marchand", False, "vu")
        m, _ = vivre(m, 3)
        textes = [c["texte"] for c in m.data["chronique"]]
        self.assertIn("Gorm demande à Aubin de le laisser passer (mefiance).", textes)
        # Gorm, à la douceur entière, ne pousse personne : il attend.
        self.assertFalse(any(" pousse " in t for t in textes))
        self.assertEqual(m.objets["marchand"]["lieu"], "beffroi")
        self.assertEqual(tuple(m.objets["aubin"]["position"]), self.PORTE)

    def test_un_gorm_brutal_pousse_aubin_devant_ilse(self):
        m = self.palier({"douceur": 30})
        lier(m, "aubin", "marchand", False, "vu")
        placer(m, "ilse", "beffroi", (2, 2))
        regarder(m, "ilse", "marchand")
        # Mêmes dés : la FOR de Gorm (14) l'emporte sur celle d'Aubin (12).
        m, lignes = vivre(m, 3, jet=10)
        textes = [c["texte"] for c in m.data["chronique"]]
        self.assertIn("Gorm demande à Aubin de le laisser passer (mefiance).", textes)
        self.assertIn("Gorm pousse Aubin ; Aubin recule d'un pas.", textes)
        # Aubin réagit désormais à la violence : le but initial de Gorm peut céder à sa défense.
        self.assertTrue(any(e["type"] == "poussee" and e["auteur"] == "marchand" and e["reussie"]
                            for e in m.data["historique_corps"]))
        self.assertNotEqual(tuple(m.objets["aubin"]["position"]), self.PORTE)
        self.assertIs(relation(m, "aubin", "marchand")["valeur"], False)
        from donjon.relations import envers
        self.assertLessEqual(envers(m, "ilse", "marchand")["confiance"], 50)
        self.assertIn("poussee_vue", [x["type"] for x in envers(m, "ilse", "marchand")["motifs"]])
        self.assertIn("Gorm, gardien du relais, pousse Aubin, vieux passeur : il recule d'un pas.", lignes)


class JoueurSurLePassageTests(unittest.TestCase):
    """Le joueur sur la case d'où un PNJ doit ouvrir une porte : on le prie de laisser passer ;
    s'il reste, un PNJ que ses valeurs y autorisent le pousse."""

    def palier(self, valeurs_gorm=None):
        m = tranquilles()
        ecarter_tous(m, "brune", "ilse", "aubin")
        porte_ouverte_a_gorm(m)
        m.joueur.update(salle="beffroi", position=[0, 3], orientation="est")
        placer(m, "marchand", "beffroi", (3, 3))
        regarder(m, "marchand", (0, 3))
        if valeurs_gorm:
            m.objets["marchand"]["profil"]["valeurs"].update(valeurs_gorm)
        intention(m, "marchand", [{"operation": "aller", "lieu": "crypte"}])
        return recharger(m)

    def test_gorm_demande_au_joueur_de_le_laisser_passer(self):
        m = self.palier()
        texte = faire(m, "attendre")
        self.assertIn("Gorm te demande de le laisser passer.", texte)
        m = recharger(m)
        self.assertEqual(tuple(m.joueur["position"]), (0, 3))
        self.assertEqual(m.objets["marchand"]["lieu"], "beffroi")
        self.assertFalse(any(" pousse " in c["texte"] for c in m.data["chronique"]))

    def test_s_il_reste_un_gorm_brutal_le_pousse(self):
        m = self.palier({"douceur": 30})
        # Mêmes dés : la FOR de Gorm (14) l'emporte sur celle du joueur (10).
        with patch.object(Monde, "d20", return_value=10):
            texte = faire(m, "attendre")
        self.assertIn("Gorm te demande de le laisser passer.", texte)
        self.assertIn("Gorm, gardien du relais, te pousse : tu recules d'un pas.", texte)
        self.assertEqual(texte.count("de le laisser passer"), 1)
        m = recharger(m)
        self.assertIn("Gorm pousse Corvus ; Corvus recule d'un pas.", [c["texte"] for c in m.data["chronique"]])
        self.assertNotEqual(tuple(m.joueur["position"]), (0, 3))
        self.assertEqual(m.objets["marchand"]["lieu"], "crypte")


if __name__ == "__main__":
    unittest.main()
