"""Branche ``ressources`` (données seulement) : la crue a un feu hors de l'eau, l'auberge du bois pour
la nuit, sans que la rareté disparaisse. Chaque nuit se vit par blocs, rechargée entre deux.

- crue : un poêle du guet allumé à la galerie de ronde, au plus haut et toujours au sec, avec trois
  charges de bûches à Gorm ; qui a froid y monte se chauffer, et le bois du guet se demande ou
  s'achète à Gorm ;
- auberge : les bûches de la cuisine (8 charges), d'Anselme (3), de Joss (3) et la réserve d'Odile
  (12, au cellier) tiennent les trois foyers allumés à la cinquième heure ; ensuite le bois se dispute.
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
        # La nuit diverge avec les services autonomes : Aubin se chauffe au poêle ; Brune y monte
        # avant que Gorm le rallume, sans être annoncée comme réchauffée.
        m, textes = par_blocs(nuit("crue", 7, "chambre_cloche"), 240, 80)
        self.assertIn("Aubin, vieux passeur se chauffe près du poêle du guet.", textes)
        self.assertIn("Brune, batelière évacuée passe dans : Galerie de ronde.", textes)
        # Le bois du guet est à Gorm : on lui demande de l'acheter ; il refuse s'il ne peut servir.
        self.assertTrue(any(t.startswith("Aubin achète une part des bûches du guet à Gorm") for t in textes))
        self.assertIn("Gorm, gardien du relais alimente le poêle du guet.", textes)
        self.assertTrue(allumee(m.objets["poele_guet"]))
        self.assertEqual(m.objets["poele_guet"]["lieu"], "chambre_cloche")
        # La rareté reste : il ne reste que deux charges, et l'eau garde la conduite.
        self.assertEqual(m.objets["bois_guet"]["charges"], 2)


class AubergeTests(unittest.TestCase):
    def test_les_trois_foyers_tiennent_la_cinquieme_heure_puis_le_bois_se_dispute(self):
        # Cas réel : l'auberge finissait dans le noir vers la cinquième heure, faute de bois.
        m = nuit("auberge", 1985, "dortoir", "fixe")
        m, textes = par_blocs(m, 300, 150)
        self.assertTrue(all(allumee(m.objets[f]) for f in ("atre", "fourneau", "poele")))
        # Odile prête sa réserve à Anselme, puis la reprend ; la cuisinière et l'aubergiste se
        # passent les bûches de la cuisine.
        self.assertIn("Anselme demande les bûches de réserve à Odile (remis).", textes)
        self.assertIn("Mireille demande les bûches de hêtre à Odile (remis).", textes)
        m, suite = par_blocs(m, 420, 60)
        # Ensuite la réserve passe de l'un à l'autre (au temps vécu, branche ``temps-reel``, Odile la
        # reprend puis la prête de nouveau, et le poêle d'Anselme tient encore à 420) sans s'épuiser.
        self.assertIn("Odile demande les bûches de réserve à Anselme (remis).", suite)
        self.assertIn("Anselme demande les bûches de réserve à Odile (remis).", suite)
        self.assertGreater(m.objets["bois_reserve"]["charges"], 0)
        self.assertTrue(allumee(m.objets["atre"]) and allumee(m.objets["fourneau"]))


if __name__ == "__main__":
    unittest.main()
