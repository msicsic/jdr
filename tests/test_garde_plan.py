"""Une garde ne défait pas les préconditions du service qu'elle mène elle-même."""
import copy
import unittest

from donjon.banc_pnj import creer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.rendu import decrire, regarder
from tests.support import calme
from tests.test_boucles_pnj import reserve_forcee
from tests.test_tensions import placer, recharger, vivre


def mine_avant_service():
    m = creer("mine", 3)
    m.joueur.update(salle="galerie", position=[1, 1])
    m, _ = vivre(m, 8)
    return m


def gardien_servant():
    m = creer("relais", 1985, "fixe")
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("ilse", "aubin")):
        placer(m, id, "crypte", [2 + n, 3])
    placer(m, "marchand", "antichambre", [5, 3])
    placer(m, "brune", "antichambre", [7, 3])
    p = m.objets["marchand"]["profil"]
    p["pulsions"] = [
        {"besoin": "biens", "condition": {"objet": "reserve", "verrouillee": True}},
        {"besoin": "devoir", "condition": {"objet": "vivres", "servir": "brune"}},
    ]
    lire(m, "marchand")["pulsions"] = []
    m.objets["vivres"]["lieu"] = "reserve"
    croire(m, "marchand", "vivres", "lieu", "reserve", "savoir", salle="antichambre", case=None)
    # Le service est nécessaire, sans que le besoin du gardien soit urgent.
    lire(m, "brune")["besoins"]["faim"] = 85.0
    m.joueur.update(salle="chambre_cloche", position=[1, 3])
    percevoir_tous(m)
    return recharger(m)


class GardeDuPlanTests(unittest.TestCase):
    def test_la_garde_ne_s_exclut_pas_elle_meme(self):
        m = gardien_servant()
        lire(m, "brune")["besoins"]["faim"] = 0.0
        m.objets["reserve"].update(ouverte=True, verrouillee=False)
        percevoir_tous(m)
        m, _ = vivre(recharger(m), 1)
        self.assertFalse(m.objets["reserve"]["ouverte"])
        self.assertTrue(m.objets["reserve"]["verrouillee"])

    def verifier_service(self, scene, gardien, convive, contenant, minutes):
        capture = scene()
        avant = copy.deepcopy(capture.data)
        bloc = recharger(capture)
        bloc, _ = vivre(bloc, minutes)
        morceaux = recharger(capture)
        for _ in range(minutes):
            morceaux, _ = vivre(morceaux, 1)
        # Même monde, mêmes croyances et chronique ; même rendu après vraie recharge.
        self.assertEqual(bloc.data, morceaux.data)
        m = recharger(morceaux)
        self.assertEqual(regarder(m), regarder(morceaux))
        c = [x for x in m.data["chronique"] if x not in avant.get("chronique", [])]
        gestes = [x["texte"] for x in c if x["pnj"] == gardien]
        nom = m.objets[convive]["nom"].split(",")[0]
        self.assertEqual(sum("donne une part" in t and nom in t for t in gestes), 1)
        nom_contenant = m.objets[contenant]["nom"]
        for operation in ("déverrouille", "ouvre", "ferme", "verrouille"):
            self.assertLessEqual(sum(f" {operation} " in t and nom_contenant in t for t in gestes), 2)
        self.assertTrue(m.objets[contenant]["verrouillee"])
        self.assertFalse(m.objets[contenant]["ouverte"])
        # Le joueur revient voir la réserve ; contrôler son texte public, puis le
        # même texte après sauvegarde, sans faire avancer les PNJ.
        m.joueur.update(salle=m.objets[contenant]["lieu"],
                        position=list(m.objets[contenant]["position"]))
        m = recharger(m)
        rendu = decrire(m, contenant)
        self.assertIn("fermé", rendu)
        self.assertIn("verrouillé", rendu)
        self.assertEqual(rendu, decrire(recharger(m), contenant))
        self.assertLess(lire(m, convive)["besoins"]["faim"], 70)
        return m

    def test_mine3_capture8_service_sans_urgence_et_recharge(self):
        self.verifier_service(mine_avant_service, "mathe", "lucien", "garde_manger", 7)

    def test_relais_service_depuis_la_reserve_gardee(self):
        self.verifier_service(gardien_servant, "marchand", "brune", "reserve", 5)

    def test_la_garde_referme_toujours_apres_un_tiers(self):
        from unittest.mock import patch
        from donjon.monde import Monde
        with patch.object(Monde, "d20", return_value=20):
            m, _ = vivre(reserve_forcee(), 20)
        m = recharger(m)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertFalse(m.objets["reserve"]["ouverte"])
        self.assertTrue(any(x["pnj"] == "marchand" and " ferme " in x["texte"]
                            for x in m.data["chronique"]))


if __name__ == "__main__":
    unittest.main()
