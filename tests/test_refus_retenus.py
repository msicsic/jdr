"""Un refus se retient selon sa cause (``deliberation.retenir_refus``, ``tient``) : ce que l'autre ne
peut pas (« impossible », « rien »…) ou garde (« necessaire »), tant que le demandeur ne croit rien de
nouveau des moyens de sa demande, sans délai ; un prix trop bas (« cher »), pour ce prix seulement ;
la méfiance et l'humeur, ``REDEMANDE`` minutes. C'est ce que croit le demandeur qui compte, jamais
l'état réel.

Chaque test vérifie l'état du monde après rechargement.
"""
import unittest

from donjon.banc_pnj import creer
from donjon.biens import bourse
from donjon.deliberation import REDEMANDE, refus_retenu, retenir_refus, tient
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.planification import Vue, s_enquerir
from tests.support import calme, regarder, sans_le_sou
from tests.test_tensions import chronique, placer, recharger, relais, vivre


def offres(textes, de, a, quoi="le fourneau soit allumé"):
    return [t for t in textes if t.startswith(f"{de} offre ") and f" à {a} pour " in t and quoi in t]


def vivre_long(m, minutes, pas=10):
    """``vivre`` par tranches, en gardant toute la chronique (elle n'en retient que les derniers pas)."""
    textes = []
    while minutes > 0:
        debut = m.data["minutes"]
        m, _ = vivre(m, min(pas, minutes))
        textes += [c["texte"] for c in m.data.get("chronique", []) if c["minute"] > debut]
        minutes -= pas
    return m, textes


def face_a_face(m, a, b, salle, cases=((1, 3), (2, 3))):
    """Placement d'auteur : ``a`` et ``b`` côte à côte, face à face, et chacun le sait."""
    placer(m, a, salle, cases[0])
    placer(m, b, salle, cases[1])
    regarder(m, a, b)
    regarder(m, b, a)
    percevoir_tous(m)


def fourneau_mort(qui="mathurine", fagots=0, bois_anselme=0):
    """Auberge (cas réel du banc : à court de bois, les offres « impossible » se répétaient toutes les
    deux heures) : plus une bûche dans l'auberge, le fourneau éteint ; Mireille le sait et paierait
    qu'on le rallume ; ``qui`` est en cuisine avec elle."""
    m = calme(creer("auberge", 1985, "fixe"), "mireille", qui)
    for k, charges in (("bois_cuisine", 0), ("fagots_etable", fagots), ("bois_anselme", bois_anselme)):
        m.objets[k]["charges"] = charges
    m.objets["fourneau"].update(allume=False, combustible=0)
    face_a_face(m, "mireille", qui, "cuisine")
    croire(m, "mireille", "fourneau", "etat", {"allume": False, "faible": False, "charge": False}, "vu")
    return recharger(m)


class TacheImpossibleTests(unittest.TestCase):
    """Une tâche que l'autre ne voit pas comment faire n'est pas reproposée tant que le payeur ne croit
    rien de nouveau de ce qu'elle emploierait ; elle l'est dès qu'il apprend du bois."""

    def test_mireille_ne_repropose_pas_l_impossible_puis_le_repropose_quand_elle_apprend_du_bois(self):
        m, textes = vivre_long(fourneau_mort(), 30)
        self.assertEqual(offres(textes, "Mireille", "Mathurine"),
                         ["Mireille offre 2 pièces à Mathurine pour qu'elle fasse en sorte que le fourneau soit allumé (impossible)."])
        refus = refus_retenu(m, "mireille", "mathurine", ("engager",), "fourneau")
        self.assertEqual((refus["raison"], refus["prix"], refus["tache"]), ("impossible", 2, "allume"))
        # Elle a vu depuis les bûches de la cuisine épuisées : un moyen de moins ne lève rien.
        self.assertIs(lire(m, "mireille")["croyances"]["bois_cuisine"]["etat"]["valeur"]["disponible"], False)
        # Bien au-delà du délai d'un refus d'humeur, elle ne lui repropose pas.
        m, textes = vivre_long(m, REDEMANDE + 10)
        self.assertEqual(offres(textes, "Mireille", "Mathurine"), [])
        self.assertIsNotNone(refus_retenu(m, "mireille", "mathurine", ("engager",), "fourneau"))
        # Hugues lui dit qu'Anselme a du bois dans sa chambre (une rumeur, rien de vu) : il y en a quelque
        # part, le refus ne tient plus.
        m.objets["bois_anselme"]["charges"] = 2
        croire(m, "mireille", "bois_anselme", "lieu", "chambre_chaude", "dit:hugues", 0.7,
               salle="chambre_chaude", case=None)
        m = recharger(m)
        self.assertIsNone(refus_retenu(m, "mireille", "mathurine", ("engager",), "fourneau"))
        m, textes = vivre_long(m, 40)
        # Une offre ; deux si, choisissant désormais à l'instant (``deliberation-evenements``), elle la
        # fait avant d'aller voir Anselme : ce qu'elle voit alors de sa chambre (ses abords) est un moyen
        # qu'elle ne croyait pas à la première, et le refus ne tient plus (``deliberation.tient``).
        self.assertIn(len(offres(textes, "Mireille", "Mathurine")), (1, 2), textes)
        # Mathurine n'en sait pas plus : refusée de nouveau, l'offre retient ce que Mireille croit désormais.
        refus = refus_retenu(m, "mireille", "mathurine", ("engager",), "fourneau")
        # (où elle le croit : dans la chambre, ou aux mains d'Anselme si elle l'y a vu depuis)
        self.assertTrue([f for f in refus["cause"] if f[:2] == ["moyen", "bois_anselme"]], refus["cause"])

    def test_au_banc_une_nuit_sans_bois_chaque_offre_impossible_n_est_faite_qu_une_fois(self):
        # Autre cas de même nature : toute l'auberge, trois foyers, plus de bois du tout (300 minutes).
        m = creer("auberge", 1985, "fixe")
        for k in ("bois_cuisine", "fagots_etable", "bois_anselme"):
            m.objets[k]["charges"] = 0
        m.objets["fourneau"]["combustible"] = 8
        m, textes = vivre_long(recharger(m), 300)
        impossibles = [t for t in textes if " fasse en sorte que " in t and t.endswith("(impossible).")]
        self.assertTrue(impossibles)
        self.assertEqual(len(impossibles), len(set(impossibles)), impossibles)


class PartImpossibleTests(unittest.TestCase):
    """Au Relais : Gorm a perdu la clé de la réserve ; une part qu'il ne peut pas servir n'est pas
    redemandée tant qu'Ilse ne croit rien de nouveau des vivres, de la réserve ou de sa clé."""

    def ilse_affamee(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        deplacer(m, "cle_reserve", "crypte")
        lire(m, "marchand")["croyances"].pop("cle_reserve", None)
        sans_le_sou(m, "ilse")
        face_a_face(m, "marchand", "ilse", "antichambre")
        lire(m, "ilse")["besoins"]["faim"] = 80.0
        return recharger(m)

    def test_ilse_ne_redemande_pas_puis_redemande_quand_elle_sait_la_cle(self):
        m, textes = vivre_long(self.ilse_affamee(), REDEMANDE + 30)
        demandes = [t for t in textes if t.startswith("Ilse demande une part des vivres")]
        self.assertEqual(demandes, ["Ilse demande une part des vivres du refuge à Gorm (impossible)."])
        self.assertEqual(refus_retenu(m, "ilse", "marchand", ("demander",), "vivres")["cause"],
                         [["moyen", "vivres", "reserve", None]])
        # Gorm a retrouvé sa clé, et Aubin le dit à Ilse.
        m.objets["cle_reserve"]["lieu"] = "marchand"
        croire(m, "marchand", "cle_reserve", "lieu", "marchand", "vu", salle=None, case=None)
        croire(m, "ilse", "cle_reserve", "lieu", "marchand", "dit:aubin", 0.7, salle=None, case=None)
        m = recharger(m)
        self.assertIsNone(refus_retenu(m, "ilse", "marchand", ("demander",), "vivres"))
        m, textes = vivre_long(m, 20)
        self.assertIn("Ilse demande une part des vivres du refuge à Gorm (promis).", textes)
        self.assertIsNone(refus_retenu(m, "ilse", "marchand", ("demander",), "vivres"))

    def test_qui_n_a_rien_n_est_pas_reinterroge(self):
        # « As-tu de quoi manger ? » : Aubin et Brune n'ont rien ; elle ne le leur redemande pas.
        m, textes = vivre_long(self.ilse_affamee(), REDEMANDE + 30)
        questions = [t for t in textes if t.startswith("Ilse demande à ") and " de quoi manger" in t]
        self.assertEqual(sorted(questions), ["Ilse demande à Aubin s'il a de quoi manger (rien).",
                                             "Ilse demande à Brune si elle a de quoi manger (rien)."])
        self.assertIsNone(s_enquerir(m, "ilse", "faim"))


class TacheCherTests(unittest.TestCase):
    """Trop peu payé, un refus ne tient que pour ce prix : il offre plus, s'il le peut."""

    def test_refuse_a_deux_pieces_anselme_accepte_a_quatre(self):
        m = fourneau_mort("anselme", bois_anselme=5)
        m.data["finances_pnj"]["mireille"] = 30
        m, textes = vivre_long(recharger(m), 15)
        self.assertEqual(offres(textes, "Mireille", "Anselme"), [
            "Mireille offre 2 pièces à Anselme pour qu'il fasse en sorte que le fourneau soit allumé (cher).",
            "Mireille offre 4 pièces à Anselme pour qu'il fasse en sorte que le fourneau soit allumé (accepte)."])
        self.assertEqual((bourse(m, "mireille"), bourse(m, "anselme")), (26, 34))
        self.assertIsNone(refus_retenu(m, "mireille", "anselme", ("engager",), "fourneau"))
        self.assertTrue(m.objets["fourneau"]["allume"])

    def test_jamais_au_prix_refuse_ni_au_dela_de_ses_moyens(self):
        # Le même marché, Mireille n'ayant que 3 pièces : refusée à deux, elle ne repropose jamais deux,
        # ni ce qu'elle n'a pas ; plus tard, ailleurs, la peine estimée vaut trois pièces : c'est plus.
        m = fourneau_mort("anselme", bois_anselme=5)
        m.data["finances_pnj"]["mireille"] = 3
        m, textes = vivre_long(recharger(m), REDEMANDE + 10)
        prix = [int(t.split(" offre ")[1].split(" ")[0]) for t in offres(textes, "Mireille", "Anselme")]
        self.assertEqual(prix[0], 2)
        self.assertTrue(offres(textes, "Mireille", "Anselme")[0].endswith("(cher)."))
        self.assertTrue(all(2 < p <= 3 for p in prix[1:]), prix)
        self.assertNotIn("4 pièces", " ".join(offres(textes, "Mireille", "Anselme")))


class MefianceTests(unittest.TestCase):
    """Un refus de méfiance ne dit rien des moyens : il tient ``REDEMANDE`` minutes, quoi qu'on
    apprenne entre-temps."""

    def test_joss_se_mefie_de_mireille(self):
        m = fourneau_mort("joss", fagots=3)
        croire(m, "joss", "mireille", "fiable", False, "vu")
        m, textes = vivre_long(recharger(m), 5)
        self.assertEqual(offres(textes, "Mireille", "Joss"), [
            "Mireille offre 2 pièces à Joss pour qu'il fasse en sorte que le fourneau soit allumé (mefiance)."])
        refus = refus_retenu(m, "mireille", "joss", ("engager",), "fourneau")
        self.assertNotIn("cause", refus)
        # Apprendre du bois ne lève pas une méfiance.
        m.objets["bois_anselme"]["charges"] = 2
        croire(m, "mireille", "bois_anselme", "lieu", "chambre_chaude", "dit:hugues", 0.7,
               salle="chambre_chaude", case=None)
        m = recharger(m)
        self.assertTrue(Vue(m, "mireille").refuse_tache("joss", "fourneau"))
        m.data["minutes"] = refus["minute"] + REDEMANDE - 1
        self.assertTrue(tient(m, "mireille", refus))
        m.data["minutes"] = refus["minute"] + REDEMANDE
        m = recharger(m)
        self.assertIsNone(refus_retenu(m, "mireille", "joss", ("engager",), "fourneau"))
        self.assertIsNone(Vue(m, "mireille").refuse_tache("joss", "fourneau"))

    def test_une_demande_accordee_efface_le_refus(self):
        # Refusée par humeur puis accordée : il ne reste aucun refus de cette demande.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        retenir_refus(m, "ilse", "marchand", "demander", "refus", objet="vivres")
        face_a_face(m, "marchand", "ilse", "antichambre")
        sans_le_sou(m, "ilse")
        lire(m, "ilse")["besoins"]["faim"] = 80.0
        m.data["minutes"] += REDEMANDE
        m, _ = vivre(recharger(m), 3, jet=20)
        self.assertIn("Ilse demande une part des vivres du refuge à Gorm (promis).", chronique(m))
        self.assertEqual([s for s in lire(m, "ilse")["refus"] if s["de"] == "marchand"], [])


class TachePayeeTenableTests(unittest.TestCase):
    """Audit des nuits (A3) : une tâche payée s'accepte sur ce qu'on peut faire soi-même, pas sur ce
    qu'un tiers donnerait ; et qui sait ne plus pouvoir la faire la rend aussitôt, sans attendre
    l'échéance."""

    def brasero_mort(self, qui="brune"):
        """Relais (cas réel, graine 11, minute 451) : le brasero est mort ; ``qui`` n'a pas de bois, ne
        connaît que les planches d'Aubin (qui les garde) ; Gorm la paie pour le rallumer."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["brasero"].update(allume=False, combustible=0)
        face_a_face(m, "marchand", qui, "antichambre")
        for x in ("marchand", qui):
            croire(m, x, "brasero", "etat", {"allume": False, "faible": False, "charge": False}, "vu")
        lire(m, qui)["croyances"].pop("bois", None)
        croire(m, qui, "planches", "lieu", "antichambre", "vu", salle="antichambre", case=[2, 5])
        return m

    def test_brune_ne_promet_pas_le_bois_d_aubin(self):
        from donjon.echanges import engager
        m = self.brasero_mort()
        avant = (bourse(m, "marchand"), bourse(m, "brune"))
        self.assertEqual(engager(m, "marchand", "brune", {"objet": "brasero", "allume": True}, 2), "impossible")
        m = recharger(m)
        self.assertEqual((bourse(m, "marchand"), bourse(m, "brune")), avant)
        self.assertEqual(lire(m, "brune")["engagements"], [])

    def test_ilse_n_accepte_que_ce_qu_elle_peut_faire_elle_meme(self):
        # Autre cas de même nature : Ilse (honnête), un briquet en main ; les planches d'Aubin, elle
        # devrait les lui demander : elle refuse ; à elle, elle accepte.
        from donjon.echanges import engager
        for proprietaire, issue in (("aubin", "impossible"), ("ilse", "accepte")):
            m = self.brasero_mort("ilse")
            deplacer(m, "briquet", "ilse")
            m.objets["planches"]["proprietaire"] = proprietaire
            self.assertEqual(engager(m, "marchand", "ilse", {"objet": "brasero", "allume": True}, 8), issue)
            m = recharger(m)
            self.assertEqual(len(lire(m, "ilse")["engagements"]), int(issue == "accepte"))

    def test_qui_ne_peut_plus_la_faire_la_rend_sans_attendre(self):
        # Auberge : Anselme accepte d'entretenir le fourneau avec son bois, puis le voit épuisé ; sans
        # autre moyen, il ne peut plus la faire : le prix est dû dès la minute suivante, et rendu.
        from donjon.echanges import engager
        from donjon.esprits import constater
        m = calme(creer("auberge", 1985, "fixe"), "anselme", "mireille")
        m.objets["fourneau"]["combustible"] = 8
        m.objets["bois_anselme"]["charges"] = 5
        face_a_face(m, "mireille", "anselme", "cuisine")
        self.assertEqual(engager(m, "mireille", "anselme", {"objet": "fourneau", "allume": True}, 2), "accepte")
        for k in ("bois_cuisine", "fagots_etable", "bois_anselme"):
            m.objets[k]["charges"] = 0
            constater(m, "anselme", k, "vu")
        m, _ = vivre(recharger(m), 1)
        self.assertEqual(lire(m, "anselme")["engagements"], [])
        self.assertTrue(any(s["type"] == "engagement_abandonne" for s in lire(m, "anselme")["memoire"]))
        self.assertEqual(m.data.get("dettes", []), [])
        self.assertEqual((bourse(m, "mireille"), bourse(m, "anselme")), (4, 30))


if __name__ == "__main__":
    unittest.main()
