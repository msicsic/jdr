"""A6 partiel : dette personnelle, cycle commun et moyens existants."""
import copy
import unittest

from donjon import agendas, deliberation, planification
from donjon.esprits import croire, lire, percevoir_tous
from donjon.rendu import regarder
from tests import test_echanges_argent as argent
from tests.test_tensions import placer, recharger, vivre


def scene(acteur="odon"):
    m = argent.ArgentTests().paie_a_portee(40)
    if acteur != "odon":
        placer(m, "odon", "baraquement", (3, 2))
        placer(m, acteur, "bureau", (3, 2))
        m.objets[acteur]["profil"]["situation"] = {"dette": 40}
        m.objets[acteur]["profil"]["valeurs"]["honnetete"] = 0
    m.objets["coffre_paie"]["verrouillee"] = False
    percevoir_tous(m)
    croire(m, acteur, "coffre_paie", "verrouillee", False, "essai")
    return recharger(m)


class NaissanceTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        return n

    def test_deux_debiteurs_agissent_et_terminent(self):
        for acteur in ("odon", "remy"):
            with self.subTest(acteur=acteur):
                m = scene(acteur)
                deliberation.choisir(m, acteur, m.data["minutes"])
                a = agendas.projets(m, acteur)[0]
                self.assertEqual((a["sorte"], a["origine"]["type"]), ("obtenir", "situation"))
                self.assertEqual(lire(m, acteur)["intention"]["motif"], "agenda")
                m, _ = vivre(self.recharge(m), 5, jet=20)
                self.assertEqual(m.objets["paie"]["lieu"], acteur)
                agendas.actualiser(m, acteur)
                self.assertEqual(agendas.projets(self.recharge(m), acteur)[0]["etat"], "atteint")

    def test_sans_dette_ou_pieces_suffisantes(self):
        for dette, pieces in ((0, 5), (40, 40)):
            m = scene()
            m.objets["odon"]["profil"]["situation"] = {"dette": dette}
            m.data["finances_pnj"]["odon"] = pieces
            agendas.actualiser(m, "odon")
            self.assertEqual(agendas.projets(self.recharge(m), "odon"), [])

    def test_honnetete_et_desespoir_ne_sont_pas_contournes(self):
        m = scene()
        m.objets["odon"]["profil"]["valeurs"]["honnetete"] = 100
        agendas.actualiser(m, "odon")
        with planification.vues_du_choix(m, "odon"):
            self.assertIsNone(agendas.planifier(m, "odon", "a1"))
        lire(m, "odon")["besoins"]["faim"] = 100
        candidats = list(deliberation._candidats(m, "odon"))
        faim = next(c for c in candidats if c.besoin == "faim")
        self.assertEqual(faim.urgence.palier, deliberation.Palier.DESESPOIR)
        self.assertEqual(agendas.projets(self.recharge(m), "odon")[0]["etat"], "sommeil")

    def test_publication_differee_et_interruption(self):
        m = scene()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(RuntimeError):
            with planification.vues_du_choix(m, "odon"):
                agendas.actualiser(m, "odon")
                self.assertEqual(m.data, avant)
                raise RuntimeError()
        self.assertEqual(m.data, avant)
        with planification.vues_du_choix(m, "odon"):
            agendas.actualiser(m, "odon")
            self.assertEqual(m.data, avant)
        self.assertEqual(len(agendas.projets(self.recharge(m), "odon")), 1)

    def test_solde_et_pas_de_renaissance(self):
        m = scene()
        agendas.actualiser(m, "odon")
        m.objets["odon"]["profil"]["situation"]["dette"] = 0
        agendas.actualiser(m, "odon")
        self.assertEqual(agendas.projets(self.recharge(m), "odon")[0]["raison"], "dette personnelle soldee")
        m.objets["odon"]["profil"]["situation"]["dette"] = 40
        agendas.actualiser(m, "odon")
        self.assertEqual(len(agendas.projets(m, "odon")), 1)
        self.assertEqual(agendas.projets(m, "odon")[0]["etat"], "atteint")

    def test_plafond_commun(self):
        m = scene()
        m.objets["odon"]["profil"]["agendas"] = [
            {"sorte": "garder", "parametres": {"lieu": "bureau"}} for _ in range(3)]
        agendas.actualiser(m, "odon")
        stock = agendas.projets(self.recharge(m), "odon")
        self.assertEqual(len(stock), 4)
        self.assertEqual(sum(a["etat"] == "actif" for a in stock), 3)
        self.assertEqual(sum(a["raison"] == "supplante" for a in stock), 1)

    def test_naissance_independante_du_registre_de_souvenirs(self):
        from donjon.esprits import memoriser
        m = scene()
        for n in range(200):
            memoriser(m, "odon", {"type": "bruit", "salle": "bureau",
                                 "nature": "choc", "niveau": 1, "direction": str(n)})
        agendas.actualiser(m, "odon")
        self.assertEqual(len(agendas.projets(self.recharge(m), "odon")), 1)
        lire(m, "odon")["memoire"].clear()
        agendas.actualiser(m, "odon")
        self.assertEqual(len(agendas.projets(self.recharge(m), "odon")), 1)

    def test_laps_entier_decoupe(self):
        m = scene()
        a, _ = vivre(self.recharge(m), 5, jet=20)
        b = self.recharge(m)
        for _ in range(5):
            b, _ = vivre(b, 1, jet=20)
            b = self.recharge(b)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))

    def test_sommeil_reveil_sur_croyance_nouvelle(self):
        m = scene()
        croire(m, "odon", "paie", "pieces", 0, "essai")
        agendas.actualiser(m, "odon")
        with planification.vues_du_choix(m, "odon"):
            self.assertIsNone(agendas.planifier(m, "odon", "a1"))
        m = self.recharge(m)
        self.assertEqual(agendas.projets(m, "odon")[0]["etat"], "sommeil")
        self.assertEqual(list(agendas.essayables(m, "odon")), [])
        croire(m, "odon", "paie", "pieces", 200, "essai")
        self.assertEqual(len(list(agendas.essayables(m, "odon"))), 1)
        with planification.vues_du_choix(m, "odon"):
            self.assertIsNotNone(agendas.planifier(m, "odon", "a1"))
        self.assertEqual(agendas.projets(self.recharge(m), "odon")[0]["etat"], "actif")
