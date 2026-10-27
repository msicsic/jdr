"""Le recours vit hors de la recherche, et survit à une recharge entre deux gestes."""
import copy
import unittest
from unittest.mock import patch

from donjon import relations
from tests.scenarios_contractuels import nouvelle_crue
from donjon.deliberation import choisir, retenir_refus
from donjon.echanges import executer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import recours
from donjon.spatial import installer
from tests.support import calme, presentes, regarder
from tests.test_tensions import placer, recharger


def scene(confiance=10, autre="marchand", garde=False):
    m = presentes(nouvelle_crue(depart="fixe"))
    # Scène de marché : isoler les recours du projet autonome d'évacuation.
    m.objets["marchand"]["profil"]["agendas"] = []
    installer(m)
    calme(m, "brune", "marchand", "ilse", "aubin")
    m.joueur.update(salle="antichambre", position=[6, 4], orientation="est")
    placer(m, "brune", "antichambre", [7, 3])
    placer(m, autre, "antichambre", [7, 4])
    regarder(m, "brune", autre)
    regarder(m, autre, "brune")
    if not garde:
        m.objets[autre]["profil"]["pulsions"] = []
        lire(m, autre)["pulsions"] = []
    m.objets["reserve"]["proprietaire"] = autre
    m.objets["vivres"]["proprietaire"] = autre
    m.objets["cle_reserve"].update(proprietaire=autre, lieu=autre)
    m.objets["crochets"].update(proprietaire="brune", lieu="brune")
    lire(m, "brune")["besoins"]["faim"] = 95
    lire(m, autre)["relations"]["brune"] = relations._nouvelle({"confiance": confiance})
    m.data["connus"].extend(["vivres", "crochets", "reserve"])
    percevoir_tous(m)
    croire(m, "brune", "vivres", "lieu", "reserve", "savoir", salle="antichambre", case=[8, 3])
    lire(m, "brune")["intention"] = {"but": {"type": "manger", "objet": "vivres"}, "motif": "faim",
                                     "plan": [], "depuis": 0, "attente": 0}
    # Une demande ordinaire vient d'être refusée ; le recours a le même besoin.
    retenir_refus(m, "brune", autre, "demander", "refus", objet="vivres")
    return recharger(m)


class RecoursTests(unittest.TestCase):
    def test_part_promise_attendue_sans_racheter_ni_voler_avec_garde_active(self):
        m = scene(70, garde=True)
        with patch.object(Monde, "d20", return_value=20):
            Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        m = recharger(m)
        offres = [s for s in lire(m, "brune")["memoire"] if s["type"] == "proposition"]
        self.assertEqual(len(offres), 1)
        self.assertEqual(offres[0]["issue"], "accepte")
        self.assertLess(lire(m, "brune")["besoins"]["faim"], 95)

    def test_mine_odon_paie_la_contre_offre_apres_refus_et_mathe_livre(self):
        from donjon.mine import nouveau_mine
        m = presentes(nouveau_mine(depart="fixe"))
        installer(m)
        ids = [i for i, o in m.objets.items() if o.get("profil")]
        calme(m, *ids)
        m.joueur.update(salle="baraquement", position=[4, 4], orientation="ouest")
        placer(m, "odon", "baraquement", [3, 5])
        placer(m, "mathe", "baraquement", [3, 4])
        regarder(m, "odon", "mathe")
        regarder(m, "mathe", "odon")
        m.objets["mathe"]["profil"]["pulsions"] = []
        lire(m, "mathe")["pulsions"] = []
        lire(m, "odon")["besoins"]["faim"] = 95
        m.data["finances_pnj"]["odon"] = 5  # Il peut remplir la condition monétaire annoncée.
        for o, x in m.objets.items():
            if x["type"] == "nourriture" and o != "vivres":
                x["portions"] = 0
        lire(m, "mathe")["relations"]["odon"] = relations._nouvelle({"confiance": 70})
        m.data["connus"].extend(["vivres", "crochets", "garde_manger"])
        percevoir_tous(m)
        lire(m, "odon")["intention"] = {"but": {"type": "manger", "objet": "vivres"},
                                        "motif": "faim", "plan": [], "depuis": 0, "attente": 0}
        etape = {"operation": "demander", "cible": "mathe", "outil": "vivres", "lieu": "", "condition": ""}
        with patch.object(Monde, "d20", return_value=1):
            self.assertFalse(executer(m, "odon", etape, []))
        m = recharger(m)
        with patch.object(Monde, "d20", return_value=20):
            Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        m = recharger(m)
        offres = [s for s in lire(m, "odon")["memoire"] if s["type"] == "proposition"]
        self.assertFalse(offres)  # La condition dite dispense d'un marché au hasard.
        self.assertLess(lire(m, "odon")["besoins"]["faim"], 95)
        self.assertIn("prend l'argent", " ".join(m.data["journal"][-1]["faits"]))

    def test_crue_offre_avant_faute_et_part_acceptee_deux_auditeurs(self):
        for autre in ("marchand", "aubin"):
            for confiance in (10, 70):
                with self.subTest(autre=autre, confiance=confiance):
                    m = scene(confiance, autre)
                    with patch.object(Monde, "d20", return_value=20):
                        # Sans durée : le bloc historique laisse finir la livraison.
                        Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
                    m = recharger(m)
                    offres = [s for s in lire(m, "brune")["memoire"] if s["type"] == "proposition"]
                    self.assertTrue(offres)
                    self.assertEqual(offres[0]["contrepartie"], {"type": "pieces", "montant": 2})
                    journal = " ".join(m.data["journal"][-1]["faits"])
                    self.assertIn("propose", journal)
                    if confiance == 70:
                        self.assertEqual(offres[0]["issue"], "accepte")
                        self.assertEqual(m.data["finances_pnj"]["brune"], 1)
                        self.assertLess(lire(m, "brune")["besoins"]["faim"], 95)
                        self.assertFalse(any(s["type"] == "vu_agir" and s.get("auteur") == "brune"
                                             for s in lire(m, autre)["memoire"]))
                        self.assertIn("accepte l'échange", journal)
                    else:
                        self.assertEqual(offres[0]["issue"], "mefiance")
                        chronique = m.data["chronique"]
                        offre = next(i for i, c in enumerate(chronique) if " propose à " in c["texte"])
                        faute = next(i for i, c in enumerate(chronique) if "crochète" in c["texte"])
                        self.assertLess(offre, faute)
                        self.assertEqual(m.data["finances_pnj"]["brune"], 3)
                        self.assertIn("refuse l'échange", journal)

    def test_meme_laps_decoupe_et_recharge(self):
        for confiance in (10, 70):
            a = scene(confiance)
            b = recharger(a.copier())
            with patch.object(Monde, "d20", return_value=20):
                Moteur(a).executer(Moteur(a).preparer(proposition("attendre")))
                from donjon.temps import instant
                from donjon.commandes import analyser
                n = 0
                while instant(b) < instant(a):
                    moteur = Moteur(b)
                    moteur.executer(moteur.preparer(analyser(b, "tourner est" if n % 2 else "tourner ouest")))
                    n += 1
                    if n % 25 == 0:
                        b = recharger(b)
            a = recharger(a)
            b = recharger(b)
            from tests.test_temps_etat import etat_pnj
            self.assertEqual(etat_pnj(a), etat_pnj(b))
            self.assertEqual(a.data["finances_pnj"], b.data["finances_pnj"])

    def test_recours_ne_relit_pas_attitude_privee_et_ne_passe_pas_devant_demande(self):
        a, b = scene(10), scene(70)
        choisir(a, "brune", 0)
        choisir(b, "brune", 0)
        self.assertEqual(lire(a, "brune")["intention"]["plan"], lire(b, "brune")["intention"]["plan"])
        m = scene()
        e = lire(m, "brune")
        e["demande_refusee"] = None
        demande = {"operation": "demander", "cible": "marchand", "outil": "vivres", "lieu": "", "condition": ""}
        self.assertIsNone(recours(m, "brune", "faim", [demande]))

    def test_refus_ne_se_reessaie_pas_avec_le_temps_ni_sur_un_autre_bien(self):
        m = scene()
        choisir(m, "brune", 0)
        etape = copy.deepcopy(lire(m, "brune")["intention"]["plan"][0])
        executer(m, "brune", etape, [])
        m = recharger(m)
        faute = {"operation": "manger", "cible": "vivres", "outil": "", "lieu": "", "condition": "sans_temoin"}
        self.assertIsNone(recours(m, "brune", "faim", [faute]))
        m.data["minutes"] += 60
        self.assertIsNone(recours(m, "brune", "faim", [faute]))
        m.data["finances_pnj"]["brune"] += 1
        self.assertIsNone(recours(m, "brune", "faim", [faute]))  # Le montant offert n'a pas changé.


if __name__ == "__main__":
    unittest.main()
