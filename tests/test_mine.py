"""La mine de Cendrefer : un scénario de données, sur les mécanismes communs."""
import tempfile
import unittest
from pathlib import Path

from donjon.banc_pnj import creer, executer
from donjon.deliberation import verifier_profil
from donjon.esprits import lire, pnjs
from donjon.mine import nouveau_mine
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition


class MineTests(unittest.TestCase):
    def test_charge_et_verifie(self):
        m = nouveau_mine(1985, "fixe")
        m.verifier()
        self.assertEqual(sorted(pnjs(m)), ["bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy"])
        for id in pnjs(m):
            verifier_profil(m, id, m.objets[id]["profil"])
        # Les ressources rares sont sous clé, et la clé est portée par une personne.
        for porte, cle in (("porte_reserve", "passe"), ("porte_bureau", "cle_paie"),
                           ("garde_manger", "cle_garde_manger"), ("coffre_paie", "cle_paie")):
            self.assertTrue(m.objets[porte]["verrouillee"])
            self.assertIn(porte, m.objets[cle]["ouvre"])
            self.assertEqual(m.objets[m.objets[cle]["lieu"]]["type"], "personnage")

    def test_sauvegarde_et_rechargement(self):
        m = creer("mine", 7, "fixe")
        executer(m, 60)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "mine.json"
            m.sauver(chemin)
            r = Monde.charger(chemin)
        self.assertEqual(r.data["minutes"], m.data["minutes"])
        self.assertEqual(r.data["esprits"], m.data["esprits"])
        self.assertEqual({k: o["lieu"] for k, o in r.objets.items()}, {k: o["lieu"] for k, o in m.objets.items()})
        # Le monde rechargé continue sans violation.
        Moteur(r).executer(Moteur(r).preparer(proposition("attendre")))
        r.verifier()

    def test_une_nuit_courte_sans_violation(self):
        for graine in (1985, 42):
            m = creer("mine", graine, "fixe")
            chronique, mesures = executer(m, 150)
            m.verifier()
            self.assertEqual(mesures["usurpations"], 0)
            # Les évacués ont demandé des vivres, et la cuisinière a servi : l'économie du camp vit.
            self.assertTrue(any("demande une part" in c["texte"] for c in chronique))
            self.assertTrue(any("donne une part" in c["texte"] for c in chronique))
            # Le poêle chauffe encore, la cuisinière tient ses clés.
            self.assertTrue(m.objets["poele"]["allume"])
            self.assertEqual(m.objets["cle_garde_manger"]["lieu"], "mathe")
            self.assertTrue(m.objets["coffre_paie"]["verrouillee"])

    def test_la_nuit_diverge_selon_la_graine(self):
        a, b = creer("mine", 1985, "fixe"), creer("mine", 11, "fixe")
        ca, _ = executer(a, 240)
        cb, _ = executer(b, 240)
        self.assertNotEqual([c["texte"] for c in ca], [c["texte"] for c in cb])

    def test_le_noir_gagne_le_camp_et_les_protecteurs_accourent(self):
        # Quand le bois du camp est brûlé (les étais de Josse, puis les bûches que Gaspard lui
        # donne pour le poêle) et que la lampe s'éteint, le blessé appelle à l'aide. Ceux que le
        # noir inquiète vont vers la lumière dont ils se souviennent, celle du bureau : le payeur,
        # dans le noir, n'y est plus seul, ou il appelle à son tour.
        from donjon.deliberation import autour
        m = creer("mine", 3, "fixe")
        executer(m, 600)
        self.assertFalse(m.objets["poele"]["allume"])
        appels = {id for id in pnjs(m) if any(s["type"] == "appel" for s in lire(m, id)["memoire"])}
        self.assertIn("lucien", appels)
        bram = autour(m, "bram")
        self.assertFalse(bram["lumiere"])
        self.assertTrue("bram" in appels or bram["fiables"], (appels, bram))


if __name__ == "__main__":
    unittest.main()
