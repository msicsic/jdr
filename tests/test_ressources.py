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
from donjon.esprits import lire
from donjon.geometrie import position_entree
from donjon.perception import allumee, substance
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
    def test_les_trois_foyers_tiennent_la_cinquieme_heure_avec_des_parts_finies(self):
        # Cas réel : l'auberge finissait dans le noir vers la cinquième heure, faute de bois.
        m = nuit("auberge", 1985, "dortoir", "fixe")
        def reserve_bois(monde):
            return sum(o.get("charges", 0) * o.get("duree_combustion", 0) for o in monde.objets.values()
                       if "combustible" in o.get("usages", ()) and substance(o) == "bois")
        initiale = reserve_bois(m)
        m, textes = par_blocs(m, 300, 150)
        self.assertTrue(all(allumee(m.objets[f]) for f in ("atre", "fourneau", "poele")))
        # Portée, la réserve ne passe plus entière à Anselme : il reçoit une charge, qu'il
        # consomme, et Odile garde le lot. Les trois foyers restent entretenus.
        self.assertEqual(m.objets["bois_reserve"]["proprietaire"], "odile")
        recus = [s["objet"] for s in lire(m, "anselme")["memoire"]
                 if s["type"] == "recu" and s.get("lot") == "bois_reserve"]
        self.assertTrue(recus)
        self.assertTrue(all(m.objets[k]["proprietaire"] == "anselme" and m.objets[k]["charges"] == 0 for k in recus))
        restante = reserve_bois(m)
        self.assertLess(restante, initiale)
        m, suite = par_blocs(m, 420, 60)
        # Le partage par charges évite de céder le lot entier puis de le refuser : le poêle peut
        # tenir plus longtemps. L'invariant des données reste la réserve finie, consommée à chaque
        # recharge ; les parts détachées sont comprises dans ce compte et ne créent pas de bois.
        self.assertGreaterEqual(reserve_bois(m), 0)
        self.assertLess(reserve_bois(m), restante)
        self.assertEqual(m.objets["bois_reserve"]["proprietaire"], "odile")
        self.assertTrue(allumee(m.objets["atre"]) and allumee(m.objets["fourneau"]))


if __name__ == "__main__":
    unittest.main()
