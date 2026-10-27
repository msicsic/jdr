"""Issue déclarée : départ, ignorance et fin de protection persistante."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, presence, pnj, social
from donjon.esprits import croire, lire, percevoir_tous, pnjs, percoit
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.spatial import _case_interieure
from tests.test_tensions import relais, placer, recharger
from tests.support import regarder as orienter


def scene(qui="ilse", temoin=True):
    m = relais()
    salle = "antichambre"
    sortie = m.data["salles"][salle]["sorties"]["ouest"]
    sortie["exterieur"] = True
    case = _case_interieure(m, salle, sortie)
    placer(m, qui, salle, case)
    m.objets["marchand"]["profil"]["agendas"] = [{"sorte": "protéger", "parametres": {"qui": qui}}]
    if temoin:
        placer(m, "marchand", salle, (case[0] + 1, case[1]))
        orienter(m, "marchand", qui)
    else:
        placer(m, "marchand", "chambre_cloche", (5, 3))
    percevoir_tous(m)
    agendas.actualiser(m, "marchand")
    return recharger(m), sortie["vers"]


class DepartTests(unittest.TestCase):
    def preuve_recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        return n

    def test_marche_vue_biens_et_retour_deux_personnes(self):
        for qui in ("ilse", "brune"):
            with self.subTest(qui=qui):
                m, vers = scene(qui)
                self.assertTrue(percoit(m, "marchand", qui))
                lignes = []
                self.assertTrue(presence.franchir(m, qui, "antichambre", vers, lignes))
                self.assertTrue(presence.parti(m, qui))
                self.assertNotIn(qui, pnjs(m))
                self.assertFalse(m.present_physique(qui, salle="antichambre"))
                self.assertFalse(percoit(m, "marchand", qui))
                self.assertNotIn(qui, pnj.occupants(m, "marchand").values())
                from donjon.ouie import saisit
                self.assertFalse(saisit(m, qui, "marchand"))
                for objet in m.enfants(qui):
                    self.assertTrue(presence.parti(m, objet["id"]))
                    self.assertFalse(m.present_physique(objet["id"], salle="antichambre"))
                agendas.actualiser(m, "marchand")
                m = self.preuve_recharge(m)
                a = agendas.projets(m, "marchand")[0]
                self.assertEqual(a["raison"], "protege cru parti")
                presence.revenir(m, qui)
                self.assertFalse(presence.parti(m, qui))
                self.assertFalse(lire(m, "marchand")["croyances"][qui]["etat"]["valeur"].get("parti"))
                agendas.actualiser(m, "marchand")
                self.assertEqual(a, agendas.projets(m, "marchand")[0])
                self.preuve_recharge(m)

    def test_hors_vue_nouvelle_commune_et_date(self):
        m, vers = scene(temoin=False)
        placer(m, "aubin", "antichambre", (2, 3))
        orienter(m, "aubin", "ilse")
        percevoir_tous(m)
        presence.franchir(m, "ilse", "antichambre", vers, [])
        agendas.actualiser(m, "marchand")
        self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")
        nouvelles = [n for _, n, _, _ in social._constats(m, "aubin")
                     if n.get("objet") == "ilse" and n.get("valeur", {}).get("parti")]
        self.assertEqual(len(nouvelles), 1)
        m.data["minutes"] += 1
        placer(m, "marchand", "antichambre", (3, 5))
        placer(m, "aubin", "antichambre", (2, 5))
        m.joueur.update(salle="antichambre", position=[1, 5])
        orienter(m, "aubin", "marchand")
        orienter(m, "marchand", "aubin")
        from tests.support import lier
        lier(m, "aubin", "marchand", True)
        # Le projet de Gorm n'est pas lu dans son esprit : Aubin connaît
        # sa demande de retrouver Ilse dans l'antichambre.
        from donjon.esprits import memoriser
        memoriser(m, "aubin", {"type": "engagement_pris", "pour": "marchand",
                               "condition": {"objet": "ilse", "lieu": "antichambre"}})
        percevoir_tous(m)
        lignes = []
        with patch("donjon.paroles.jet_persuasion", return_value=(True, 20)):
            for _ in range(20):
                social.bavarder(m, "aubin", lignes)
                if lire(m, "marchand")["croyances"].get("ilse", {}).get("etat", {}).get("valeur", {}).get("parti"):
                    break
                m.data["minutes"] += 1
        self.assertEqual(lire(m, "marchand")["croyances"]["ilse"]["etat"]["minute"], 0)
        agendas.actualiser(m, "marchand")
        self.assertEqual(agendas.projets(m, "marchand")[0]["raison"], "protege cru parti")
        self.assertTrue(lignes)
        self.preuve_recharge(m)

    def test_inconnu_et_publication_differee(self):
        m, _ = scene()
        croire(m, "marchand", "ilse", "lieu", None, "vu", salle=None, case=None)
        agendas.actualiser(m, "marchand")
        self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")
        croire(m, "marchand", "ilse", "etat", {"parti": True}, "vu")
        avant = copy.deepcopy(m.data)
        with agendas.evaluation(m, "marchand"):
            agendas.actualiser(m, "marchand")
            self.assertEqual(m.data, avant)
        self.assertEqual(agendas.projets(m, "marchand")[0]["raison"], "protege cru parti")
        self.preuve_recharge(m)

    def test_joueur_marche_et_fin_sauvegardee(self):
        m, _ = scene(temoin=False)
        placer(m, "ilse", "antichambre", (2, 3))
        m.joueur.update(salle="antichambre", position=[0, 3], orientation="ouest")
        m = recharger(m)
        texte = Moteur(m).executer(Moteur(m).preparer(proposition("marcher", "ouest")))
        self.assertIn("Tu quittes les lieux", texte)
        self.assertEqual(m.data["fin"]["cause"], "depart")
        self.assertIn("Tu as quitté les lieux", regarder(m))
        self.preuve_recharge(m)

    def test_issue_du_hameau_et_joueur_sans_cases(self):
        from donjon.crue_hameau import nouvelle_crue_hameau
        from donjon.spatial import installer
        for cases in (True, False):
            m = nouvelle_crue_hameau(depart="fixe")
            installer(m)
            m.data["mode_cases"] = cases
            m.joueur.update(salle="antichambre", position=[8, 3], orientation="est")
            m = recharger(m)
            texte = Moteur(m).executer(Moteur(m).preparer(proposition("aller", "est")))
            self.assertIn("Tu quittes les lieux", texte)
            self.assertEqual(m.data["fin"]["cause"], "depart")
            self.preuve_recharge(m)

    def test_meme_laps_entier_decoupe_apres_depart(self):
        from tests.test_tensions import vivre
        m, vers = scene()
        presence.franchir(m, "ilse", "antichambre", vers, [])
        entier, _ = vivre(recharger(m), 3)
        morceaux = recharger(m)
        for _ in range(3):
            morceaux, _ = vivre(morceaux, 1)
        self.assertEqual(entier.data, morceaux.data)
        self.assertEqual(agendas.projets(entier, "marchand")[0]["raison"], "protege cru parti")
        self.assertEqual(regarder(entier), regarder(self.preuve_recharge(morceaux)))

    def test_cache_vue_depart_du_joueur_et_retour_sans_temps_retroactif(self):
        from donjon.spatial import vue_memorisee
        from donjon.corps import corps
        m, _ = scene()
        placer(m, "ilse", "antichambre", (2, 3))
        m.joueur.update(salle="antichambre", position=[0, 3], orientation="ouest")
        orienter(m, "marchand", "joueur")
        with vue_memorisee(m):
            self.assertTrue(percoit(m, "marchand", "joueur"))
            presence.franchir(m, "joueur", "antichambre", "echoppe", [])
            self.assertFalse(percoit(m, "marchand", "joueur"))
        m.data["minutes"] = 60
        presence.revenir(m, "joueur")
        self.assertNotIn("fin", m.data)
        self.assertEqual(corps(m, "joueur")["vecu"]["depuis"], 36000)
        self.preuve_recharge(m)

    def test_joueur_voit_depart_et_affaires_emportees_n_eclairent_plus(self):
        from donjon.perception import salle_source
        from donjon.spatial import position_cible
        m, vers = scene()
        m.joueur.update(salle="antichambre", position=[2, 5])
        orienter(m, "joueur", "ilse")
        m.objets["lanterne"].update(lieu="ilse", allume=True, combustible=100)
        percevoir_tous(m)
        self.assertTrue(m.visible("ilse"))
        lignes = []
        presence.franchir(m, "ilse", "antichambre", vers, lignes)
        self.assertIn("quitte les lieux", " ".join(lignes))
        self.assertIsNone(salle_source(m, m.objets["lanterne"]))
        self.assertIsNone(position_cible(m, "lanterne"))
        self.assertFalse(m.accessible("lanterne"))
        self.assertFalse(m.visible("ilse"))
        m = self.preuve_recharge(m)
        self.assertTrue(lire(m, "joueur")["croyances"]["ilse"]["etat"]["valeur"]["parti"])
        presence.revenir(m, "ilse")
        self.assertFalse(lire(m, "joueur")["croyances"]["ilse"]["etat"]["valeur"]["parti"])
        self.preuve_recharge(m)
