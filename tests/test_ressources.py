"""Branche ``ressources`` (données seulement) : la crue a un feu hors de l'eau, l'auberge du bois pour
la nuit, sans que la rareté disparaisse. Chaque nuit se vit par blocs, rechargée entre deux.

- crue : un poêle du guet allumé à la galerie de ronde, au plus haut et toujours au sec, avec trois
  charges de bûches à Gorm ; qui a froid y monte se chauffer, et le bois du guet se demande ou
  s'achète à Gorm ;
- auberge : les bûches de la cuisine (8 charges), d'Anselme (3), de Joss (3) et la réserve d'Odile
  (12, au cellier) suffisent aux foyers, mais les refus peuvent en interrompre l'entretien.
"""
import unittest

from donjon.banc_pnj import creer, executer
from donjon.geometrie import position_entree
from donjon.perception import allumee
from tests.test_tensions import recharger


def nuit(scenario, graine, salle, depart="tire"):
    m = creer(scenario, graine, depart)
    m.joueur.update(salle=salle, position=list(position_entree(m, salle)))
    return m


def par_blocs(m, jusqu_a, bloc):
    """Fait vivre le monde jusqu'à ``jusqu_a``, rechargé tous les ``bloc`` minutes ; renvoie le
    monde et les textes de la chronique."""
    textes = []
    while m.data["minutes"] < jusqu_a:
        chronique, _ = executer(m, min(jusqu_a, m.data["minutes"] + bloc))
        textes += [c["texte"] for c in chronique]
        m = recharger(m)
    return m, textes


class CrueTests(unittest.TestCase):
    def test_on_monte_se_chauffer_au_poele_du_guet_et_son_bois_se_demande(self):
        # Avant (``verifier-eau``), le brasero de la conduite était le seul feu : menacé par l'eau,
        # personne ne s'y chauffait plus et Brune avait froid près de cinq heures par nuit.
        # Les relations graduées changent cette nuit : Gorm refuse Brune, qui prend ensuite
        # les planches d'Aubin et rallume le poêle à 253. Les ressources restent comptées.
        m, textes = par_blocs(nuit("crue", 7, "chambre_cloche"), 270, 90)
        self.assertIn("Brune, batelière évacuée se chauffe près du poêle du guet.", textes)
        self.assertIn("Brune demande une part des bûches du guet à Gorm (mefiance).", textes)
        self.assertIn("Brune, batelière évacuée alimente le poêle du guet.", textes)
        self.assertIn("Brune, batelière évacuée allume le poêle du guet.", textes)
        self.assertTrue(allumee(m.objets["poele_guet"]))
        self.assertEqual(m.objets["poele_guet"]["lieu"], "chambre_cloche")
        # Le bois refusé reste intact ; une des deux planches prises a alimenté le poêle.
        self.assertEqual(m.objets["bois_guet"]["charges"], 3)
        self.assertEqual(m.objets["bois_guet"]["proprietaire"], "marchand")
        self.assertIn("Brune, batelière évacuée prend les planches de bac.", textes)
        self.assertEqual(m.objets["planches"]["charges"], 1)
        self.assertEqual(m.objets["planches"]["proprietaire"], "aubin")


class AubergeTests(unittest.TestCase):
    def test_une_reserve_non_epuisee_est_refusee_puis_les_trois_foyers_reprennent(self):
        # Cas réel : l'auberge finissait dans le noir vers la cinquième heure, faute de bois.
        m = nuit("auberge", 1985, "dortoir", "fixe")
        m, textes = par_blocs(m, 300, 150)
        # Avec les relations graduées, ce n'est plus le manque de combustible :
        # Odile refuse Anselme. Son poêle s'éteint malgré les huit charges restantes.
        self.assertTrue(all(allumee(m.objets[f]) for f in ("atre", "fourneau")))
        self.assertFalse(allumee(m.objets["poele"]))
        self.assertEqual(m.objets["bois_anselme"]["charges"], 0)
        self.assertEqual(m.objets["bois_reserve"]["charges"], 8)
        self.assertEqual(m.objets["bois_reserve"]["lieu"], "odile")
        self.assertIn("Anselme demande les bûches de réserve à Odile (refus).", textes)
        m, suite = par_blocs(m, 420, 60)
        # Elle accepte ensuite ; il alimente et rallume le poêle, puis obtient du
        # bois de Mireille. La reprise conserve les dons, les charges et les feux.
        self.assertIn("Anselme demande les bûches de réserve à Odile (remis).", suite)
        self.assertIn("Anselme demande les bûches de hêtre à Mireille (remis).", suite)
        self.assertIn("Anselme, marchand drapier alimente le poêle de fonte.", suite)
        self.assertEqual(m.objets["bois_reserve"]["charges"], 5)
        self.assertTrue(all(allumee(m.objets[f]) for f in ("atre", "fourneau", "poele")))


if __name__ == "__main__":
    unittest.main()
