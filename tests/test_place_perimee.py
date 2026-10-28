"""Une ancienne place sociale ne réserve pas le prochain geste."""
import unittest
import copy
from unittest.mock import patch

from donjon import relations, signes
from donjon.esprits import croire, lire
from donjon.geometrie import distance
from donjon.pnj import agir
from donjon.perception import eclairage
from donjon.rendu import regarder
from tests.scenarios_contractuels import creer
from tests.support import calme
from tests.test_signes import intention
from tests.test_tensions import placer, recharger, vivre


def scene(scenario, etat):
    m = creer(scenario, 7, "fixe")
    id, proche, perdu, salle = (("ilse", "aubin", "marchand", "antichambre") if scenario == "relais"
                              else ("hugues", "lucien", "anselme", "salle_commune"))
    ids = [x for x, o in m.objets.items() if o.get("profil")]
    calme(m, *ids)
    for x in ids:
        lire(m, x)["libre"] = 36000
    placer(m, id, salle, [1, 1])
    placer(m, proche, salle, [6, 5])
    m.joueur.update(salle=salle, position=[1, 3], orientation="est")
    m.data["salles"][salle]["lumiere_naturelle"] = 2
    e = lire(m, id)
    e["relations"].clear()
    # Un lien encore présent suffit à empêcher l'ancien nettoyage « pas de liens ».
    e["relations"][proche] = relations._nouvelle({"confiance": 70, "affection": 20}, m.data["minutes"])
    croire(m, id, proche, "lieu", salle, "vu", salle=salle, case=[6, 5])
    ailleurs = "echoppe" if scenario == "relais" else "cellier"
    croire(m, id, perdu, "lieu", None if etat == "inconnu" else ailleurs, "vu", salle=None, case=None)
    e["besoins"]["securite"] = 75
    intention(m, id, "abriter")
    e["intention"]["attitude"] = {"place": {"signe": "proche", "envers": perdu, "sens": "dependance"}}
    return recharger(m), id, proche


class PlacePerimeeTests(unittest.TestCase):
    def test_la_cible_connue_hors_d_atteinte_cede_a_la_compagnie_accessible(self):
        for scenario in ("relais", "auberge"):
            with self.subTest(scenario=scenario):
                m, id, proche = scene(scenario, "inconnu")
                perdu = "marchand" if scenario == "relais" else "anselme"
                salle = "salle_divisee"
                m.data["salles"][salle] = copy.deepcopy(m.data["salles"][m.objets[id]["lieu"]])
                m.data["salles"][salle].update(nom="Salle divisée", sorties={},
                    plan={"origine": [100, 100], "repere": "X", "sol": [".... ....."] * 7})
                for x, p in ((id, [3, 1]), (proche, [1, 4]), (perdu, [5, 1])):
                    placer(m, x, salle, p)
                m.joueur.update(salle=salle, position=[1, 2])
                for x in (proche, perdu):
                    croire(m, id, x, "lieu", salle, "vu", salle=salle, case=m.objets[x]["position"])
                lire(m, id)["relations"][perdu] = relations._nouvelle(
                    {"affection": 90, "confiance": 90}, m.data["minutes"])
                intention(m, id, "abriter")
                lire(m, id)["intention"]["attitude"] = {
                    "place": {"signe": "proche", "envers": perdu, "sens": "attachement"}}
                lire(m, id)["libre"] = 0
                bloc, _ = vivre(recharger(m), 2)
                morceaux, _ = vivre(recharger(m), 1)
                morceaux, _ = vivre(morceaux, 1)
                self.assertEqual(bloc.data, morceaux.data)
                self.assertEqual(regarder(bloc), regarder(morceaux))
                self.assertLessEqual(distance(bloc.objets[id]["position"], bloc.objets[proche]["position"]), 1)
                self.assertEqual(bloc.objets[id]["lieu"], salle)

    def test_la_place_sans_pas_cede_au_proche_dans_le_meme_geste(self):
        for scenario in ("relais", "auberge"):
            for etat in ("inconnu", "dementi"):
                with self.subTest(scenario=scenario, etat=etat):
                    m, id, proche = scene(scenario, etat)
                    avant = list(m.objets[id]["position"])
                    agir(m, id, m.data["minutes"] * 600, [])
                    m = recharger(m)
                    self.assertNotEqual(m.objets[id]["position"], avant)
                    self.assertNotIn("place", lire(m, id)["intention"].get("attitude", {}))
                    self.assertEqual(m.data, recharger(m).data)
                    self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_le_recours_rejoint_la_compagnie_apres_recharge_et_decoupe(self):
        for scenario in ("relais", "auberge"):
            with self.subTest(scenario=scenario):
                m, id, proche = scene(scenario, "inconnu")
                lire(m, id)["libre"] = 0
                bloc, _ = vivre(recharger(m), 2)
                morceaux, _ = vivre(recharger(m), 1)
                morceaux, _ = vivre(morceaux, 1)
                self.assertEqual(bloc.data, morceaux.data)
                self.assertEqual(regarder(bloc), regarder(morceaux))
                self.assertEqual(bloc.objets[id]["lieu"], bloc.objets[proche]["lieu"])
                self.assertLessEqual(distance(bloc.objets[id]["position"], bloc.objets[proche]["position"]), 1)
                self.assertGreater(eclairage(bloc, bloc.objets[id]["lieu"], bloc.objets[id]["position"])["niveau"], 0)

    def test_le_pas_social_impossible_ne_conserve_aucune_place(self):
        for signe, duree in ((s, d) for s in ("proche", "ecart") for d in (None, 15)):
            with self.subTest(signe=signe, duree=duree):
                m, id, proche = scene("relais", "inconnu")
                placer(m, id, "antichambre", [4, 5])
                i = lire(m, id)["intention"]
                i["attitude"]["place"] = {"signe": signe, "envers": proche, "sens": "dependance"}
                # Ouvrir un passage ou échouer peut consommer du temps sans
                # atteindre la place visée : le signe décrit la case effective.
                with patch("donjon.pnj._marcher", return_value=duree) as marcher:
                    self.assertEqual(signes.place(m, id, i["plan"][0], []), duree)
                marcher.assert_called_once()
                self.assertEqual(m.objets[id]["position"], [4, 5])
                self.assertNotIn("place", i["attitude"])
                self.assertNotIn("place", lire(recharger(m), id)["intention"].get("attitude", {}))
                self.assertEqual(regarder(m), regarder(recharger(m)))


if __name__ == "__main__":
    unittest.main()


