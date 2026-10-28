"""Récit du banc sans joueur : il raconte sans rien changer au monde."""
import unittest

from donjon.banc_pnj import creer, executer
from donjon.francais import de
from donjon.recit_pnj import Recit, but_en_mots


class RecitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temoin = creer("relais", 7, "fixe")
        cls.chronique_temoin, cls.mesures_temoin = executer(cls.temoin, 240)
        cls.monde = creer("relais", 7, "fixe")
        cls.recit = Recit(cls.monde)
        cls.chronique, cls.mesures = executer(cls.monde, 240, cls.recit)
        cls.texte = cls.recit.texte(cls.monde, cls.chronique)

    def test_observer_ne_change_rien(self):
        self.assertEqual(self.chronique, self.chronique_temoin)
        self.assertEqual(self.mesures, self.mesures_temoin)
        self.assertEqual(self.monde.data["esprits"], self.temoin.data["esprits"])

    def test_l_estompement_compte_aussi_sans_recit_apres_reprise(self):
        from donjon import relations
        from donjon.esprits import lire, pnjs
        from tests.support import calme
        from tests.test_tensions import recharger
        for axe in ("peur", "rancune"):
            m = calme(creer("crue", 42, "fixe"), "ilse", "brune", "aubin", "marchand")
            for id in pnjs(m):
                lire(m, id)["libre"] = 600000
            for id in pnjs(m):
                lire(m, id)["relations"].clear()
            m.objets["ilse"]["profil"]["valeurs"].update(fierte=1, douceur=100)
            lire(m, "ilse")["relations"]["aubin"] = relations._nouvelle({axe: 50})
            m = recharger(m)
            avec = recharger(m)
            recit = Recit(avec)
            chronique, mesures = executer(m, 120)
            raconte, mesure_racontee = executer(avec, 120, recit)
            m, avec = recharger(m), recharger(avec)
            self.assertEqual(m.data, avec.data)
            self.assertEqual(chronique, raconte)
            self.assertEqual(mesures, mesure_racontee)
            self.assertEqual(mesures["relations_changees"], 1)
            self.assertIn("estompement", recit.texte(avec, raconte))

    def test_buts_et_gestes_de_chacun(self):
        # Brune affamée : son but, et les gestes faits pour lui, dans l'ordre de la nuit.
        buts = [ep["but"]["type"] for ep in self.recit.episodes["brune"]]
        self.assertTrue(any(b in ("manger", "part") for b in buts), buts)
        self.assertIn("== Brune, batelière évacuée ==", self.texte)
        # Un essai, plusieurs résumés en un (« s'acharne »), ou un renoncement devant une serrure trop
        # sombre, selon la nuit (depuis la branche ``temps-reel``, cette nuit-ci renonce).
        self.assertRegex(self.texte, "(crochète|s'acharne sur) la serrure de la réserve de vivres"
                                     "|renonce à crocheter la réserve de vivres|propose à Gorm .+ contre une part"
                                     "|demande une part des vivres")
        # Une part obtenue avant la première minute peut apaiser la faim avant
        # le premier relevé d'urgence ; son motif reste raconté.
        self.assertTrue(any(ep["motif"] == "faim" for ep in self.recit.episodes["brune"]))

    def test_entre_eux_et_temoins(self):
        # Placement d'auteur : Brune, gelée et sans scrupule, près des planches d'Aubin, sous les
        # yeux de Gorm (la scène de test_protection).
        from tests.support import calme, regarder
        from donjon.deliberation import retenir_refus
        from donjon.esprits import croire, lire, percevoir_tous
        from tests.test_tensions import placer, relais
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["brasero"].update(allume=False, combustible=0)
        placer(m, "brune", "antichambre", (3, 5))
        placer(m, "marchand", "antichambre", (4, 5))
        placer(m, "aubin", "crypte", (5, 3))
        regarder(m, "marchand", "brune")
        lire(m, "brune")["besoins"]["chaleur"] = 99.0
        from donjon.pnj import tour_d_horizon
        tour_d_horizon(m, "brune")  # Elle a parcouru le refuge des yeux : torche, fanal, planches.
        percevoir_tous(m)
        croire(m, "brune", "brasero", "etat", {"allume": False, "faible": False, "charge": False}, "vu")
        croire(m, "brune", "fanal", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        for de, objet in (("aubin", "planches"), ("marchand", "bois")):
            retenir_refus(m, "brune", de, "demander", "refus", objet=objet)
        recit = Recit(m)
        chronique, _ = executer(m, m.data["minutes"] + 20, recit)
        texte = recit.texte(m, chronique)
        self.assertIn("== Entre eux ==", texte)
        self.assertIn("Gorm voit Brune prendre les planches de bac", texte)
        self.assertIn("Gorm envers Brune : se méfie ; tort_tiers.", texte)

    def test_rondes_resumees(self):
        self.assertIn("Rondes :", self.texte)
        # Contrat du résumé, indépendant des rencontres d'une nuit : une
        # inspection seule est regroupée ; parole et décision restent visibles.
        m = creer("relais", 7, "fixe")
        recit = Recit(m)
        recit.episodes["aubin"] = [
            {"but": {"type": "pulsion", "lieu": "antichambre", "periode": 30},
             "motif": "devoir", "debut": minute, "fin": minute, "abandon": False}
            for minute in range(3)]
        evenements = [
            ("geste", "Aubin inspecte le refuge"),
            ("social", "Aubin demande une part des vivres du refuge à Gorm"),
            ("decision", "Aubin : agenda a1 sommeil (sans plan admissible au cout)")]
        chronique = [{"pnj": "aubin", "minute": minute, "nature": nature, "texte": texte}
                     for minute, (nature, texte) in enumerate(evenements)]
        lignes = recit.personnage(m, "aubin", chronique)
        self.assertTrue(any("Rondes : Refuge du relais ×1" in ligne for ligne in lignes), lignes)
        detail = [ligne for ligne in lignes if "ronde : " in ligne]
        self.assertTrue(any("demande une part des vivres du refuge" in ligne for ligne in detail), detail)
        self.assertTrue(any("agenda a1 sommeil" in ligne for ligne in detail), detail)

    def test_mots(self):
        self.assertEqual(de("Aubin"), "d'Aubin")
        self.assertEqual(de("Gorm"), "de Gorm")
        self.assertEqual(but_en_mots(self.monde, {"type": "chaleur", "objet": "brasero"}), "se chauffer au brasero")
        self.assertEqual(but_en_mots(self.monde, {"type": "part", "objet": "planches", "de": "aubin"}),
                         "obtenir une part (les planches de bac) d'Aubin")


class NuitsTests(unittest.TestCase):
    def test_des_nuits_en_parallele_comme_une_a_une(self):
        from donjon.banc_pnj import nuit, nuits, tableau
        ensemble = nuits("relais", [7, 42], 1, "chambre_cloche")
        seule = nuit("relais", 42, 1, "chambre_cloche")
        self.assertEqual(ensemble[1][1], seule[1])
        self.assertEqual(ensemble[1][0], seule[0])
        self.assertIn("moyenne", tableau([7, 42], [m for _, m, _ in ensemble]))

    def test_diagnostic_du_planificateur(self):
        from donjon.banc_pnj import nuit
        texte, mesures, donnees = nuit("relais", 42, 1, "chambre_cloche", diagnostic=True)
        self.assertEqual(mesures, nuit("relais", 42, 1, "chambre_cloche")[1])
        recherches, resume = donnees["diagnostic"]["recherches"], donnees["diagnostic"]["resume"]
        self.assertTrue(recherches)
        self.assertTrue(all(r["issue"] in ("plan", "borne", "epuise", "endure") and r["but"] for r in recherches))
        self.assertEqual(sum(g["recherches"] for g in resume), len(recherches))
        self.assertIn("Planificateur :", texte)

    def test_diagnostic_compte_chaque_issue_d_une_recherche(self):
        # Une recherche qui trouve un plan mais où il endure plutôt que d'y aller (``endurer``) a
        # son issue propre : le résumé la compte comme les autres.
        from donjon.banc_pnj import resume_diagnostic, texte_diagnostic
        recherches = [{"pnj": "bram", "but": "lumiere", "issue": issue, "memoire": False, "noeuds": 3,
                       "profondeur": 1, "duree": 0.001} for issue in ("plan", "borne", "epuise", "endure", "attente")]
        resume = resume_diagnostic(recherches)
        self.assertEqual([(g["plan"], g["borne"], g["epuise"], g["endure"]) for g in resume], [(1, 1, 1, 1)])
        self.assertIn("endure", texte_diagnostic(resume))
        self.assertEqual(resume[0]["attente"], 1)
        self.assertIn("attente", texte_diagnostic(resume))


if __name__ == "__main__":
    unittest.main()
