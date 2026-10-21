"""Jalon I2 : écouter — les PNJ font du bruit, le joueur l'entend selon la distance et les portes.

Chaque test vérifie ce que le joueur lit, et l'état après rechargement.
"""
import unittest

from donjon.commandes import analyser
from donjon.ecoute import ENTENDU, rendre
from donjon.moteur import Moteur, proposition
from donjon.ouie import retentir
from donjon.social import faire_entendre
from tests.support import calme
from tests.test_tensions import placer, recharger, relais, vivre


def executer(monde, p):
    texte = Moteur(monde).executer(Moteur(monde).preparer(p))
    return recharger(monde), texte


def au_palier(monde, case):
    """Placement d'auteur : le joueur sur le palier des vannes ; Aubin et Gorm parlent derrière la
    porte fermée, dans la salle des vannes."""
    m = calme(monde, "marchand", "brune", "ilse", "aubin")
    m.joueur.update(salle="beffroi", position=list(case))
    placer(m, "aubin", "crypte", (4, 1))
    placer(m, "marchand", "crypte", (5, 1))
    return m


def parler_pendant(monde, minutes_plus_tard=1):
    """Une parole d'Aubin à Gorm, datée pendant le geste que le joueur va faire."""
    monde.data["minutes"] += minutes_plus_tard
    retentir(monde, "aubin", "dire", texte="Aubin dit à Gorm que l'eau monte aux vannes.", cites=["marchand"])
    monde.data["minutes"] -= minutes_plus_tard


class BruitsTests(unittest.TestCase):
    def test_les_pas_et_les_paroles_des_pnj_font_du_bruit(self):
        m = calme(relais(), "brune", "ilse", "aubin")
        # Le joueur au refuge, dos à l'échoppe ; de garde, Gorm part en ronde : ses pas résonnent.
        m.joueur.update(salle="antichambre", position=[1, 3], orientation="est")
        m, _ = vivre(m, 3)
        self.assertIn("pas", [b["nature"] for b in m.data["bruits"] if b["auteur"] == "marchand"])
        m.joueur["orientation"] = "nord"
        faire_entendre(m, "aubin", "marchand", "Aubin dit à Gorm que l'eau monte.", [], [])
        m = recharger(m)
        voix = [b for b in m.data["bruits"] if b["nature"] == "voix"][-1]
        self.assertEqual((voix["auteur"], voix["cites"]), ("aubin", ["marchand"]))


class EcouterTests(unittest.TestCase):
    def test_colle_a_la_porte_on_entend_des_voix_derriere(self):
        m = au_palier(relais(), (0, 3))
        parler_pendant(m)
        m, texte = executer(m, analyser(m, "j'écoute à la porte"))
        # Le résultat dit la condition qui l'aide : son oreille contre la porte (banc Luna : le MJ
        # racontait « contre la porte » sans fait pour l'attester).
        self.assertIn("Tu tends l'oreille contre la porte étanche du beffroi.", texte)
        self.assertIn("Tu entends une voix à l'ouest.", texte)
        # La parole n'est pas nette à travers la porte : son contenu ne passe pas.
        self.assertNotIn("l'eau monte", texte)

    def test_loin_de_la_porte_ou_sans_ecouter_rien_ne_passe(self):
        for case, action in (((7, 3), "ecouter"), ((0, 3), "attendre")):
            with self.subTest(case=case, action=action):
                m = au_palier(relais(), case)
                parler_pendant(m)
                m, texte = executer(m, proposition(action))
                self.assertNotIn("Tu entends une voix", texte)
        m = au_palier(relais(), (7, 3))
        _, texte = executer(m, proposition("ecouter"))
        self.assertIn("Tu tends l'oreille : rien de particulier ne te parvient.", texte)
        m = au_palier(relais(), (0, 3))
        _, texte = executer(m, proposition("ecouter"))
        self.assertIn("Tu tends l'oreille contre la porte étanche du beffroi : rien de particulier ne te parvient.",
                      texte)

    def test_un_appel_s_entend_sans_tendre_l_oreille(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[3, 4])
        placer(m, "ilse", "echoppe", (3, 5))
        m.data["minutes"] += 1
        retentir(m, "ilse", "appel")
        m.data["minutes"] -= 1
        m, texte = executer(m, proposition("attendre"))
        self.assertTrue(any(l.startswith("Tu entends un appel à l'aide") and l.endswith(" à l'ouest.")
                            for l in texte.splitlines()))

    def test_une_parole_nette_ne_dit_que_ce_que_le_joueur_connait(self):
        m = relais()
        nette = {"auteur": "aubin", "nature": "voix", "texte": "Aubin dit à Gorm que l'eau monte.",
                 "cites": ["marchand"], "salle": "antichambre", "instant": 600, "niveau": ENTENDU, "par": None}
        m.data["connus"] = sorted({*m.data["connus"], "aubin", "marchand"})
        self.assertEqual(rendre(m, [(nette, ENTENDU, None)]),
                         ["Tu entends, tout près : Aubin dit à Gorm que l'eau monte."])
        # Une parole qui nomme ce qu'il ignore reste des voix.
        inconnue = {**nette, "texte": "Aubin dit à Gorm que les crochets sont aux vannes.", "cites": ["crochets"]}
        self.assertEqual(rendre(m, [(inconnue, ENTENDU, "est")]), ["Tu entends une voix à l'est."])


if __name__ == "__main__":
    unittest.main()
