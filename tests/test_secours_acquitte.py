"""Le constat remplace l'appel ; un cri ne rend pas une destination sûre."""
import copy
import gzip
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon import defense, planification, ouie
from donjon.esprits import lire, memoriser, percevoir_tous, percoit
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import MINUTE, instant
from tests.support import regarder as orienter
from tests.test_combat import scene
from tests.test_corps_blessable import passer
from tests.test_tensions import placer, recharger


def capture(n):
    p = Path(__file__).parent / "data" / f"secours-223-{n}.json.gz"
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "monde.json"
        f.write_bytes(gzip.decompress(p.read_bytes()))
        return Monde.charger(f)


class SecoursAcquitteTests(unittest.TestCase):
    def identique(self, a, b):
        a, b = recharger(a), recharger(b)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(scene_percue(a), scene_percue(b))

    def test_captures_reelles_ne_renvoient_plus_au_danger(self):
        for n in (22, 26):
            m = capture(n)
            avant = copy.deepcopy(m.data)
            aide = defense.protection(m, "marchand")
            self.assertEqual(m.data, avant)
            self.assertEqual(aide, ("brune", "antichambre", []))
            self.assertIsNone(planification.reagir(m, "marchand", [], aide))
            # Sans preuve visuelle postérieure, le cri reste en attente.
            self.assertFalse(next(s for s in lire(m, "marchand")["memoire"]
                                  if s["type"] == "secours").get("examine"))
            a, b = recharger(m), recharger(m)
            retours = []
            reagir = planification.reagir

            def observer(monde, id, dangers, aide=None):
                choix = reagir(monde, id, dangers, aide)
                if (id == "marchand" and choix and aide == ("brune", "antichambre", [])
                        and "antichambre" in defense.lieux_dangereux(monde, id)
                        and any(e["operation"] == "aller" for e in choix[1])):
                    retours.append(choix)
                return choix

            with patch.object(planification, "reagir", side_effect=observer):
                passer(a, MINUTE)
            self.assertEqual(retours, [])
            for _ in range(4):
                passer(b, MINUTE // 4)
                b = recharger(b)
            self.identique(a, b)
            # Une recherche d'abri peut le détourner avant le constat. Le cri
            # reste alors en attente, sans retour au danger ni acquittement
            # inventé. L'autre scène ci-dessous contrôle le constat effectif.
            cri = next(s for s in lire(a, "marchand")["memoire"] if s["type"] == "secours")
            if not cri.get("examine"):
                self.assertFalse(percoit(a, "marchand", cri["qui"]))
                etat = lire(a, "marchand")["croyances"].get(cri["qui"], {}).get("etat", {})
                self.assertFalse(etat.get("source") == "vu" and etat["minute"] > cri["minute"])

    def test_appel_reel_suivi_puis_constate_autre_scenario(self):
        for protecteur, cible in (("marchand", "aubin"), ("ilse", "aubin")):
            m = scene(cible, False)  # rixe, autre scénario que la capture crue
            m.objets[protecteur]["profil"]["protege"] = [cible]
            from donjon.voix import connaitre
            connaitre(m, protecteur, cible)
            ouie.entendre(m, protecteur, cible, "antichambre", (3, 5), "cri",
                         instant(m), ouie.SEUIL + 2)
            m = recharger(m)
            aide = defense.protection(m, protecteur)
            self.assertEqual(aide, (cible, "antichambre", []))
            self.assertIsNotNone(planification.reagir(m, protecteur, [], aide))
            a, b = recharger(m), recharger(m)
            passer(a, 2 * MINUTE)
            for _ in range(4):
                passer(b, MINUTE // 2)
                b = recharger(b)
            self.identique(a, b)
            self.assertTrue(any(s["type"] == "secours" and s.get("examine")
                                for s in lire(a, protecteur)["memoire"]))
            # Un constat réel, sans exécuter l'étape inspecter.
            placer(m, protecteur, "antichambre", (4, 5))
            orienter(m, protecteur, cible)
            percevoir_tous(m)
            self.assertIsNone(defense.choisir(m, protecteur))
            m = recharger(m)
            self.assertTrue(next(s for s in lire(m, protecteur)["memoire"]
                                 if s["type"] == "secours").get("examine"))
            self.assertTrue(any(e["type"] == "intervention" and e["id"] == protecteur
                                for e in m.data["historique_corps"]))
            # Le départ ne réactive pas l'appel acquitté.
            placer(m, protecteur, "echoppe", (5, 4))
            self.assertIsNone(defense.protection(recharger(m), protecteur))

    def test_joueur_constate_et_nouveau_cri_reouvre(self):
        m = scene("aubin", False)
        memoriser(m, "joueur", dict(type="secours", qui="aubin", salle="antichambre"))
        self.assertTrue(m.visible("aubin"))
        planification.reagir(m, "joueur", [], defense.protection(m, "joueur"))
        m = recharger(m)
        self.assertTrue(lire(m, "joueur")["memoire"][-1]["examine"])
        placer(m, "aubin", "echoppe", (8, 4))
        memoriser(m, "joueur", dict(type="secours", qui="aubin", salle="echoppe"))
        planification.reagir(m, "joueur", [], defense.protection(m, "joueur"))
        self.assertFalse(lire(m, "joueur")["memoire"][-1].get("examine"))


if __name__ == "__main__":
    unittest.main()
