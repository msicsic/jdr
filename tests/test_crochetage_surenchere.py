"""Deux réglages décidés le 2026-10-22 (branche ``crochetage-surenchere``).

Le bruit du crochetage selon l'adresse (``ouie.nature_crochetage``), règle commune au joueur et aux
PNJ : réussi, la serrure cède sous la main (un geste ordinaire, feutré fait en douce) ; manqué, on
s'acharne sur la serrure : un fracas. Le voleur qui veut agir sans être entendu attend du geste le
bruit que lui promet son adresse (``planification.bruit_crochetage``).

La surenchère progressive (``planification._engager``) : refusé pour un prix trop bas, le payeur hausse
d'un palier (+50 %), une hausse par délibération à la minute, tant que ce que lui coûtent
ces pièces ne passe pas la peine que la tâche lui épargne ; puis il renonce. Accepter une tâche et la
dire ensuite impossible se jugent par le même devis (``echanges.empeche``).

Chaque cas vérifie l'état du monde après rechargement, et ce que le joueur lit quand il est là."""
import unittest
from unittest.mock import patch

from donjon.echanges import empeche, engager
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.pnj import lumiere_du_geste
from donjon.planification import bruit_crochetage, chance_crochetage
from tests.test_ouie import brune_crochete_dans_le_dos_de_gorm, faire, intention, plan, souvenirs, vu_agir
from donjon.banc_pnj import creer
from tests.support import calme
from tests.test_refus_retenus import face_a_face, fourneau_mort, vivre_long
from tests.test_tensions import chronique, placer, recharger, vivre

CROCHETE = "Brune, batelière évacuée crochète la serrure de la réserve de vivres"
RETOURNE = "Gorm, gardien du relais se retourne au bruit."


def brune_en_douce(gorm_la_sait=False):
    """Le cas réel, Brune à bout de faim, crochetant cette fois en douce (sans témoin, comme le plan
    d'un vol) ; Gorm ne la sait pas là : un bruit qu'il entendrait lui serait inconnu."""
    m = brune_crochete_dans_le_dos_de_gorm(gorm_la_sait)
    intention(m, "brune", plan("crocheter", "reserve", "crochets", condition="sans_temoin"))
    return recharger(m)


class BruitDuCrochetageTests(unittest.TestCase):
    def test_reussi_en_douce_gorm_n_entend_rien(self):
        # Cas réel (« le fracas du crochetage fait se retourner » le gardien de dos) : réussi en douce, le
        # geste est feutré ; à trois cases, Gorm n'en entend rien.
        m = brune_en_douce()
        with patch.object(Monde, "d20", return_value=20):
            faire(m, "tourner sud")
        m = recharger(m)
        self.assertIn(CROCHETE + " sans forcer.", chronique(m))
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        self.assertNotIn(RETOURNE, chronique(m))
        self.assertEqual(vu_agir(m, "marchand"), [])
        self.assertEqual(souvenirs(m, "marchand", "entendu_agir") + souvenirs(m, "marchand", "bruit"), [])

    def test_manque_en_douce_c_est_un_fracas(self):
        # Le même geste manqué : elle s'acharne sur la serrure, un fracas que Gorm entend et va voir.
        m = brune_en_douce()
        with patch.object(Monde, "d20", return_value=1):
            faire(m, "tourner sud")
        m = recharger(m)
        self.assertIn(CROCHETE.replace("crochète la serrure de", "s'acharne sur la serrure de") + ".", chronique(m))
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertIn(RETOURNE, chronique(m))
        self.assertIn(("brune", "reserve"), vu_agir(m, "marchand"))

    @patch("donjon.social._constats", return_value=())
    def test_reussi_sans_se_cacher_un_bruit_ordinaire_de_qui_il_sait_la(self, _constats):
        # Autre cas de même nature : sans se cacher, Gorm la sachant là. Manqué, il se retourne même
        # s'il la sait là (``test_ouie``) ; réussi, c'est un geste ordinaire qu'il lui prête sans se
        # retourner. Peu de bruit n'est pas aucun : à trois cases, il l'entend toucher à la réserve
        # qu'il croit là, et le sait par l'oreille (``pnj._temoins_a_l_oreille``), sans l'avoir vue.
        m = brune_crochete_dans_le_dos_de_gorm()
        with patch.object(Monde, "d20", return_value=20):
            faire(m, "tourner sud")
        m = recharger(m)
        self.assertIn(CROCHETE + " sans forcer.", chronique(m))
        self.assertNotIn(RETOURNE, chronique(m))
        self.assertEqual([s.get("par") for s in souvenirs(m, "marchand", "vu_agir")], ["ouie"])

    def test_le_joueur_n_entend_pas_un_crochetage_reussi_dans_la_salle_voisine(self):
        # ``test_ouie`` : manqué, « Tu entends un grand bruit… à l'est » ; réussi, rien de tel.
        for jet, grand_bruit in ((20, False), (1, True)):
            m = brune_crochete_dans_le_dos_de_gorm()
            placer(m, "marchand", "crypte", (5, 3))
            m.joueur.update(salle="echoppe", position=[5, 3], orientation="ouest")
            m = recharger(m)
            with patch.object(Monde, "d20", return_value=jet):
                texte = faire(m, "attendre")
            m = recharger(m)
            self.assertEqual(any(l.startswith("Tu entends un grand bruit") for l in texte.splitlines()), grand_bruit)
            self.assertEqual(m.objets["reserve"]["verrouillee"], jet == 1)


class CrochetageDuJoueurTests(unittest.TestCase):
    """La même règle pour Corvus : son jet fait le bruit de son crochetage."""

    def corvus_devant_la_reserve(self):
        m = brune_crochete_dans_le_dos_de_gorm()
        lire(m, "brune")["intention"] = None
        placer(m, "brune", "crypte", (2, 2))
        lire(m, "brune")["croyances"].pop("reserve", None)
        # Gorm est à l'échoppe, la salle voisine ; Corvus, les crochets en main, devant la réserve.
        placer(m, "marchand", "echoppe", (5, 3))
        lire(m, "marchand")["croyances"].pop("joueur", None)
        m.objets["crochets"]["lieu"] = "joueur"
        m.joueur.update(salle="antichambre", position=[7, 3], orientation="est")
        return recharger(m)

    def test_son_bruit_tient_a_son_jet(self):
        for jet, entendu in ((20, False), (1, True)):
            m = self.corvus_devant_la_reserve()
            # Ilse/Aubin n'enquêtent pas sur les vivres pour Brune : seul le geste fait du bruit.
            from tests.support import sans_souci
            sans_souci(m, "ilse", "aubin")
            with patch.object(Monde, "d20", return_value=jet):
                texte = faire(m, "crocheter reserve avec crochets")
            m = recharger(m)
            self.assertEqual(m.objets["reserve"]["verrouillee"], jet == 1, texte)
            # Le fracas l'a fait venir voir le refuge (il en garde l'examen) ; réussi, il n'a rien entendu.
            examens = [s for s in souvenirs(m, "marchand", "examen") if s["salle"] == "antichambre"]
            self.assertEqual(bool(examens), entendu, (jet, texte))
            self.assertEqual(m.objets["marchand"]["lieu"], "antichambre" if entendu else "echoppe")
            self.assertEqual(souvenirs(m, "marchand", "bruit"), [])


class VoleurQuiSeSaitHabileTests(unittest.TestCase):
    """Le voleur qui veut agir sans être entendu attend que s'éloignent ceux qu'il croit à portée
    d'oreille du bruit qu'il attend de son geste ; de son adresse (sa DEX, la lumière qu'il a), il
    attend un fracas ou un geste feutré."""

    def brune_et_une_oreille(self, dex):
        # Brune, une lanterne en main, crochète en douce ; elle croit Ilse à trois cases, dans l'ombre
        # (Ilse est en fait à la crypte : c'est ce qu'elle croit qui compte). Pas à bout de faim.
        m = brune_crochete_dans_le_dos_de_gorm(gorm_la_sait=False)
        placer(m, "marchand", "echoppe", (5, 3))
        m.objets["lanterne"]["lieu"] = "brune"
        m.objets["brune"]["profil"]["caracteristiques"]["DEX"] = dex
        lire(m, "brune")["besoins"]["faim"] = 80.0
        intention(m, "brune", plan("crocheter", "reserve", "crochets", condition="sans_temoin"))
        croire(m, "brune", "ilse", "lieu", "antichambre", "vu", salle="antichambre", case=[4, 3])
        return recharger(m)

    def test_maladroite_elle_attend(self):
        # Cas réel : Brune (DEX 15, la faim la diminue) a moins d'une chance sur deux : elle attend un
        # fracas et guette.
        m = self.brune_et_une_oreille(15)
        lumiere = lumiere_du_geste(m, "brune")
        self.assertLess(chance_crochetage(m, "brune", lumiere), 0.5)
        self.assertEqual(bruit_crochetage(m, "brune", lumiere), "bruyant")
        m, _ = vivre(m, 2, jet=20)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertEqual(lire(m, "brune")["intention"]["plan"][0]["operation"], "crocheter")
        self.assertGreater(lire(m, "brune")["intention"]["attente"], 0)

    def test_habile_elle_agit(self):
        # Autre cas de même nature : plus adroite, elle se sait capable d'un crochetage feutré, qu'Ilse
        # n'entendrait pas d'où elle la croit : elle agit, et la serrure cède sans bruit.
        m = self.brune_et_une_oreille(20)
        lumiere = lumiere_du_geste(m, "brune")
        self.assertGreaterEqual(chance_crochetage(m, "brune", lumiere), 0.5)
        self.assertEqual(bruit_crochetage(m, "brune", lumiere), "feutre")
        m, _ = vivre(m, 2, jet=20)
        self.assertFalse(m.objets["reserve"]["verrouillee"])
        self.assertIn(CROCHETE + " sans forcer.", chronique(m))



class TacheAccepteeTests(unittest.TestCase):
    """Accepter une tâche se juge exactement sur ce qui la rendrait ensuite impossible : le même devis
    (``planification.devis_pulsion``), et la tâche se fait par son plan."""

    def tilo_paye_pour_l_atre(self, briquet):
        """Le cas réel (auberge 42, minutes 342 et 343 : Odile paie Tilo pour l'âtre ; il accepte, le
        croyant allumé et chargé, d'après ce qu'il en sait, n'y compte qu'une recharge, puis le voit
        éteint et le doit aussitôt, sans flamme pour le rallumer). L'âtre est éteint et vide, Odile l'a
        vu ; Tilo sait les bûches de la cuisine ; ``briquet`` : il porte de quoi le rallumer."""
        m = calme(creer("auberge", 1985, "fixe"), "odile", "tilo")
        m.objets["atre"].update(allume=False, combustible=0)
        face_a_face(m, "odile", "tilo", "salle_commune", cases=((1, 3), (2, 3)))
        croire(m, "odile", "atre", "etat", {"allume": False, "faible": False, "charge": False}, "vu")
        croire(m, "tilo", "bois_cuisine", "lieu", "cuisine", "vu", salle="cuisine",
               case=list(m.objets["bois_cuisine"]["position"]))
        if briquet:
            m.objets["briquet"]["lieu"] = "tilo"
        m.data["finances_pnj"]["odile"] = 100
        return recharger(m)

    def test_sans_flamme_tilo_refuse_au_lieu_de_devoir_aussitot(self):
        # Celui qui le paie le sait éteint : il le compte à recharger et à rallumer, et voit qu'il ne
        # le peut pas. Avant : « accepte », puis « Tilo doit désormais 20 pièces… » à la minute suivante.
        m = self.tilo_paye_pour_l_atre(briquet=False)
        self.assertEqual(engager(m, "odile", "tilo", {"objet": "atre", "allume": True}, 20), "impossible")
        m, textes = vivre_long(recharger(m), 15)
        self.assertFalse([t for t in textes if " doit désormais " in t])
        self.assertEqual(m.data.get("dettes", []), [])

    def test_avec_un_briquet_tilo_fait_le_travail(self):
        m = self.tilo_paye_pour_l_atre(briquet=True)
        self.assertEqual(engager(m, "odile", "tilo", {"objet": "atre", "allume": True}, 20), "accepte")
        self.assertFalse(empeche(m, "tilo", lire(m, "tilo")["engagements"][0]))
        m, textes = vivre_long(recharger(m), 15)
        # Il peut le faire dès la minute initiale, exclue du relevé de vivre_long.
        self.assertIn("Tilo, neveu de l'aubergiste allume l'âtre.", chronique(m))
        self.assertTrue(m.objets["atre"]["allume"])
        # La preuve de son propre geste peut solder la parole dans la minute
        # initiale, que vivre_long exclut de ses relevés. Garder toute la trace.
        self.assertIn("Tilo a fait le travail que Odile lui avait payé pour que l'âtre soit allumé.", chronique(m))
        self.assertEqual(lire(m, "tilo")["engagements"], [])
        from donjon.biens import services_proteges
        self.assertIn({"objet": "atre", "allume": True}, services_proteges(recharger(m), "tilo"))
        self.assertEqual(m.data.get("dettes", []), [])

    def test_odile_hausse_par_paliers_puis_renonce(self):
        # Le cas réel : Odile offrait à Tilo 2, 4, 8, 16, 32 puis 64 pièces, plusieurs dans la même
        # minute. Refusée chaque fois pour trop peu, elle offre désormais 2, 3, 5, 8 (un palier de
        # +50 %, une hausse par minute), puis plus rien : 12 pièces lui coûteraient plus que la peine
        # de la tâche (5 minutes, l'âtre est dans la salle où ils se tiennent).
        from donjon.deliberation import retenir_refus
        from donjon.planification import Vue, _engager, depart, peine_tache
        m = self.tilo_paye_pour_l_atre(briquet=True)
        condition, suite = {"objet": "atre", "allume": True}, []
        for _ in range(10):
            v = Vue(m, "odile")
            e = depart(m, "odile", v)
            offres = [x[2][0]["contenu"]["prix"] for x in _engager(v, e, condition) if x[2][0]["cible"] == "tilo"]
            if not offres:
                break
            self.assertLessEqual(v.depense(offres[0]), peine_tache(v, e, condition))
            suite.append(offres[0])
            retenir_refus(m, "odile", "tilo", "engager", "cher", objet="atre", prix=offres[0], tache="allume")
            m = recharger(m)
            # À la minute même du refus, aucune hausse.
            v = Vue(m, "odile")
            self.assertEqual([x for x in _engager(v, depart(m, "odile", v), condition) if x[2][0]["cible"] == "tilo"], [])
            m.data["minutes"] += 1
        self.assertEqual(suite, [2, 3, 5, 8])
        self.assertGreater(Vue(m, "odile").depense(12), 5)

    def test_joss_fait_le_travail_paye_sans_le_devoir(self):
        # Cas de même nature que le cas réel (auberge 42, minute 195 : Joss acceptait d'allumer le
        # fourneau, le rechargeait, et le devait aussitôt) : payé, il recharge et rallume le fourneau de
        # ses fagots ; ce qu'il voit après avoir accepté (le feu qu'il a rechargé lui-même), il le croit.
        m = fourneau_mort("joss", fagots=2)
        m.data["finances_pnj"]["mireille"] = 30
        m = recharger(m)
        condition = {"objet": "fourneau", "allume": True}
        self.assertEqual(engager(m, "mireille", "joss", condition, 2), "accepte")
        self.assertFalse(empeche(m, "joss", lire(m, "joss")["engagements"][0]))
        m, textes = vivre_long(recharger(m), 15)
        self.assertIn("Joss a fait le travail que Mireille lui avait payé pour que le fourneau soit allumé.", textes)
        self.assertFalse([t for t in textes if " doit désormais " in t])
        self.assertTrue(m.objets["fourneau"]["allume"])
        self.assertEqual(m.data.get("dettes", []), [])


if __name__ == "__main__":
    unittest.main()
