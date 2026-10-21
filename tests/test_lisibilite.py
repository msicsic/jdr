"""Lisibilité : la carte montre la lumière et distingue les personnages ; le récit reste dans la fiction."""
import unittest

from donjon.carte import carte, symbole_personnage
from donjon.defi import nouveau_defi
from donjon.narration import voix_auteur
from donjon.spatial import installer


def relais():
    m = nouveau_defi(1985, "fixe")
    installer(m)
    return m


class CarteTests(unittest.TestCase):
    def test_chaque_personnage_a_sa_lettre_distincte_des_salles(self):
        m = relais()
        lettres = {id: symbole_personnage(m, o) for id, o in m.objets.items() if o["type"] == "personnage"}
        self.assertEqual(len(set(lettres.values())), len(lettres))
        reperes = {s["plan"].get("repere") for s in m.data["salles"].values()}
        self.assertFalse(set(lettres.values()) & reperes)
        self.assertEqual((lettres["ilse"], lettres["aubin"]), ("I", "A"))

    def test_la_penombre_se_distingue_de_la_lumiere(self):
        m = relais()
        m.objets["lanterne"]["allume"] = False
        plan = carte(m)
        self.assertIn(", ", plan.split("=== LEGENDE ===")[0])
        self.assertIn("pénombre (vue courte)", plan)


class RecitTests(unittest.TestCase):
    def test_le_meta_langage_est_refuse(self):
        # Réponse réelle d'une partie : la lanterne et son combustible.
        self.assertTrue(voix_auteur("Elle dispose déjà de 60 minutes de combustible ; les faits ne "
                                    "précisent pas de quel type il s'agit."))
        self.assertTrue(voix_auteur("Les données ne disent rien de son contenu."))
        self.assertFalse(voix_auteur("Tu ne sais pas ce qu'elle brûle : rien ne l'indique à l'œil."))


if __name__ == "__main__":
    unittest.main()
