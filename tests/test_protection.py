"""Jalon I3 : protéger — l'appel à l'aide, le protecteur qui accourt, le protégé prévenu.

Chaque test vérifie l'état du monde et, quand le joueur est concerné, ce qu'il lit, après
rechargement.
"""
import copy
import unittest

from donjon.deliberation import verifier_profil
from donjon.esprits import croire, lire, memoriser, percevoir_tous
from donjon.moteur import Moteur, proposition
from tests.support import calme, regarder
from tests.test_tensions import chronique, placer, recharger, relais, vivre


def seule_et_a_bout(monde):
    """Placement d'auteur : Ilse seule dans l'échoppe obscure, à bout d'inquiétude, sans abri
    qu'elle connaisse : elle ne se fie plus qu'à Gorm, qu'elle croit aux vannes, dans le noir."""
    m = calme(monde, "marchand", "brune", "ilse", "aubin")
    m.objets["brasero"].update(allume=False, combustible=0)
    placer(m, "ilse", "echoppe", (3, 5))
    placer(m, "marchand", "crypte", (5, 3))
    for autre in ("brune", "aubin"):
        croire(m, "ilse", autre, "fiable", False, "vu")
    croire(m, "ilse", "marchand", "lieu", "crypte", "vu", salle="crypte", case=[5, 3])
    croire(m, "ilse", "crypte", "etat", {"eclairee": False}, "vu")
    croire(m, "ilse", "antichambre", "etat", {"eclairee": False}, "vu")
    lire(m, "ilse")["besoins"]["securite"] = 97.0
    return m


class AppelTests(unittest.TestCase):
    def test_a_bout_sans_abri_elle_appelle_et_gorm_accourt(self):
        m = seule_et_a_bout(relais())
        m, _ = vivre(m, 1)
        self.assertIn("Ilse appelle à l'aide.", chronique(m))
        self.assertEqual(lire(m, "marchand")["intention"]["motif"], "alerte")
        m, _ = vivre(m, 5)
        self.assertEqual(m.objets["marchand"]["lieu"], "echoppe")
        # Elle n'appelle pas à chaque minute.
        self.assertEqual(chronique(m).count("Ilse appelle à l'aide."), 1)

    def test_le_joueur_entend_l_appel_sans_tendre_l_oreille(self):
        m = seule_et_a_bout(relais())
        m.joueur.update(salle="antichambre", position=[3, 4])
        texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        m = recharger(m)
        # Gorm, qui accourt, se fait entendre aussi : l'appel et ses pas viennent de l'ouest.
        self.assertTrue(any(ligne.startswith("Tu entends un appel à l'aide") and ligne.endswith(" à l'ouest.")
                            for ligne in texte.splitlines()), texte)
        self.assertIn("appel", [b["nature"] for b in m.data["bruits"]])

    def test_qui_n_est_pas_protecteur_n_accourt_pas(self):
        m = seule_et_a_bout(relais())
        m.objets["marchand"]["profil"]["protege"] = []
        m, _ = vivre(m, 1)
        self.assertIn("Ilse appelle à l'aide.", chronique(m))
        intention = lire(m, "marchand")["intention"]
        self.assertTrue(intention is None or intention["motif"] != "alerte")


class PrevenirTests(unittest.TestCase):
    def test_gorm_voit_brune_prendre_les_planches_d_aubin_et_le_lui_dit(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Placement d'auteur : Brune, à bout de froid, sans scrupule, près des planches d'Aubin ;
        # Gorm la voit ; Aubin est aux vannes.
        m.objets["brasero"].update(allume=False, combustible=0)
        placer(m, "brune", "antichambre", (3, 5))
        placer(m, "marchand", "antichambre", (4, 5))
        placer(m, "aubin", "crypte", (5, 3))
        regarder(m, "marchand", "brune")
        lire(m, "brune")["besoins"]["chaleur"] = 99.0
        from donjon.pnj import tour_d_horizon
        tour_d_horizon(m, "brune")  # Elle a parcouru le refuge des yeux : torche, fanal, planches.
        percevoir_tous(m)
        # Elle sait le feu mort, et Aubin comme Gorm viennent de lui refuser leur bois.
        croire(m, "brune", "brasero", "etat", {"allume": False, "faible": False, "charge": False}, "vu")
        croire(m, "brune", "fanal", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        for de, objet in (("aubin", "planches"), ("marchand", "bois")):
            memoriser(m, "brune", {"type": "refus", "de": de, "operation": "demander", "raison": "refus", "objet": objet})
        avant = lire(m, "marchand")["besoins"]["devoir"]
        # Elle prend la torche et les planches, dans l'ordre que son plan retient : Gorm la voit.
        m, _ = vivre(m, 4)
        self.assertIn("vu_agir", [s["type"] for s in lire(m, "marchand")["memoire"]])
        self.assertGreater(lire(m, "marchand")["besoins"]["devoir"], avant + 20)
        m, _ = vivre(m, 12)
        self.assertTrue(any("Gorm" in t and "dit à Aubin" in t for t in chronique(m)), chronique(m)[-12:])
        self.assertFalse(lire(m, "aubin")["croyances"]["brune"]["fiable"]["valeur"])


class ProfilProtegeTests(unittest.TestCase):
    def test_on_ne_protege_que_des_personnages(self):
        m = relais()
        profil = copy.deepcopy(m.objets["marchand"]["profil"])
        for invalide in (["cloche"], ["marchand"], "ilse"):
            with self.assertRaises(AssertionError):
                verifier_profil(m, "marchand", {**profil, "protege": invalide})


if __name__ == "__main__":
    unittest.main()
