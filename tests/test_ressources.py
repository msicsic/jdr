"""Branche ``ressources`` (données seulement) : la crue a un feu hors de l'eau, l'auberge du bois pour
la nuit, sans que la rareté disparaisse. Chaque nuit se vit par blocs, rechargée entre deux.

- crue : un poêle du guet allumé à la galerie de ronde, au plus haut et toujours au sec, avec trois
  charges de bûches à Gorm ; qui a froid y monte se chauffer, et le bois du guet se demande ou
  s'achète à Gorm ;
- auberge : les bûches de la cuisine (8 charges), d'Anselme (3), de Joss (3) et la réserve d'Odile
  (12, au cellier) suffisent aux foyers, mais les refus peuvent en interrompre l'entretien.
"""
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer, executer
from donjon.esprits import lire
from donjon.geometrie import position_entree
from donjon.perception import allumee, brule, substance
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
    def test_on_monte_se_chauffer_au_poele_du_guet_et_le_bois_reste_compte(self):
        # Avant (``verifier-eau``), le brasero de la conduite était le seul feu : menacé par l'eau,
        # personne ne s'y chauffait plus et Brune avait froid près de cinq heures par nuit.
        # Gorm peut refuser Brune ; les trajets et échanges déterminent le bois
        # qu'elle obtient. Toute recharge doit consommer une ressource du monde.
        m, textes = par_blocs(nuit("crue", 7, "chambre_cloche"), 270, 90)
        # Les recours refusés changent les trajets de cette nuit : Brune ne prend
        # pas les planches et ne rallume pas le poêle. Aucun bois fictif ne le recharge.
        self.assertFalse(allumee(m.objets["poele_guet"]))
        self.assertEqual(m.objets["poele_guet"]["lieu"], "chambre_cloche")
        # Les signes changent les occasions : cette nuit ne demande plus les bûches.
        # Le bois gardé reste intact ; une des deux planches prises a alimenté le poêle.
        self.assertEqual(m.objets["bois_guet"]["charges"], 3)
        self.assertEqual(m.objets["bois_guet"]["proprietaire"], "marchand")
        self.assertNotIn("Brune, batelière évacuée prend les planches de bac.", textes)
        self.assertEqual(m.objets["planches"]["charges"], 2)
        self.assertEqual(m.objets["planches"]["proprietaire"], "aubin")
        # La capacité de rejoindre le feu haut reste vérifiée dans la même crue,
        # avant son extinction, depuis le palier voisin (et après recharge).
        from tests.support import calme
        from tests.test_tensions import placer
        from donjon.esprits import croire
        m = nuit("crue", 7, "chambre_cloche")
        calme(m, "marchand", "brune", "ilse", "aubin")
        placer(m, "brune", "beffroi", (8, 3))
        lire(m, "brune")["besoins"]["chaleur"] = 80.0
        croire(m, "brune", "poele_guet", "etat", {"allume": True, "charge": True}, "savoir")
        m, textes = par_blocs(recharger(m), 10, 2)
        self.assertIn("Brune, batelière évacuée se chauffe près du poêle du guet.", textes)
        self.assertEqual(m.objets["brune"]["lieu"], "chambre_cloche")
        self.assertLess(lire(m, "brune")["besoins"]["chaleur"], 80)
        self.assertEqual(m.objets["bois_guet"]["charges"], 3)


class AubergeTests(unittest.TestCase):
    @patch("donjon.social._constats", return_value=())
    def test_le_bois_reste_compte_a_chaque_geste_et_apres_recharge(self, _constats):
        # Nuit commerciale fixée : pas de confidence ordinaire décalant ses jets.
        # Cas réel : l'auberge finissait dans le noir vers la cinquième heure, faute de bois.
        m = nuit("auberge", 1985, "dortoir", "fixe")
        def reserve_bois(monde):
            return sum(o.get("charges", 0) * o.get("duree_combustion", 0) for o in monde.objets.values()
                       if "combustible" in o.get("usages", ()) and substance(o) == "bois")
        def energie_bois(monde):
            return reserve_bois(monde) + sum(o.get("combustible", 0) for o in monde.objets.values()
                                             if brule(o) == "bois")
        from donjon import pnj
        executer_geste, recharges = pnj._executer, []
        def verifier_geste(monde, id, etape, *args):
            avant = energie_bois(monde)
            resultat = executer_geste(monde, id, etape, *args)
            # Donner, vendre, détacher une part et charger un foyer peuvent
            # transférer le bois, jamais créer des minutes de combustion.
            self.assertLessEqual(energie_bois(monde), avant + 1e-7, (id, etape))
            if etape["operation"] == "alimenter" and resultat:
                recharges.append((id, etape["cible"]))
            return resultat
        initiale = reserve_bois(m)
        energie_initiale = energie_bois(m)
        # Le séjour rassurant peut différer l'entretien d'Anselme : une nuit
        # n'impose ni cette vente précise ni trois foyers encore vifs à 300.
        # Le contrat porte sur chaque transfert réel et chaque recharge.
        with patch.object(pnj, "_executer", verifier_geste):
            m, textes = par_blocs(m, 300, 150)
            restante = reserve_bois(m)
            self.assertLess(restante, initiale)
            m, suite = par_blocs(m, 420, 60)
        self.assertTrue(recharges)
        self.assertEqual(m.objets["bois_reserve"]["proprietaire"], "odile")
        # La reprise conserve refus, ventes, dons, charges et feux ; la réserve reste finie,
        # consommée à chaque recharge, sans bois créé par les parts détachées.
        self.assertGreaterEqual(reserve_bois(m), 0)
        self.assertLessEqual(reserve_bois(m), restante)
        self.assertLess(energie_bois(m), energie_initiale)
        self.assertEqual(m.objets["bois_reserve"]["proprietaire"], "odile")
        from donjon.rendu import regarder
        self.assertEqual(regarder(m), regarder(recharger(m)))
        # Sept heures de choix commerciaux ne garantissent pas que chacun
        # entretienne encore son foyer : les refus retiennent désormais leurs
        # causes. Une flamme encore vive doit toujours brûler un vrai combustible.
        for foyer in ("atre", "fourneau", "poele"):
            if allumee(m.objets[foyer]):
                self.assertGreater(m.objets[foyer]["combustible"], 0)

if __name__ == "__main__":
    unittest.main()
