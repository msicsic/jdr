"""Le coût de calcul du planificateur, sans rien changer à ce que décident les PNJ.

Quand seuls le prix d'une faute ou celui d'abîmer ont changé (la détresse qui monte d'une minute à
l'autre), la recherche se refait sur le graphe gardé de la précédente (``planification._GRAPHES``)
au lieu de recalculer chaque geste. Chaque cas compare, après rechargement, le monde obtenu avec ce
graphe et celui obtenu en recalculant tout ; ``VERIFIER`` refait en plus chaque recherche reprise."""
import unittest
from unittest.mock import patch

from donjon import planification
from donjon.banc_pnj import creer
from donjon.caractere import prix_faute
from donjon.esprits import lire, percevoir_tous
from donjon.planification import diagnostics, garder
from tests.support import calme
from tests.test_tensions import placer, vivre


class Oublieux(dict):
    """Un graphe gardé qu'on ne retrouve jamais : chaque recherche recalcule tout."""

    def get(self, *args):
        return None


def lucien_au_grenier_noir():
    """Le cas réel (``test_dynamique_besoins``) : Lucien, qui craint le noir, garde son coffret au
    grenier sans lumière ; ses biens et sa sécurité pressent, la lanterne à rapporter est à autrui."""
    m = creer("auberge", 1985, "fixe")
    calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
    m.objets["poele"].update(allume=False, combustible=0)
    m.objets["bois_anselme"]["charges"] = 0
    placer(m, "lucien", "grenier", (2, 2))
    percevoir_tous(m)
    lire(m, "lucien")["besoins"].update(biens=65.0, securite=70.0)
    return m


def vivre_par_pas(m, minutes, pas, graphes):
    """Fait vivre le monde (rechargé à chaque pas), graphes gardés ou non ; VERIFIER actif."""
    with patch.object(planification, "_GRAPHES", graphes), patch.object(planification, "_MEMOIRE", {}), \
            patch.object(planification, "VERIFIER", True), diagnostics() as recherches:
        for _ in range(0, minutes, pas):
            m, _ = vivre(m, pas)
    return m, recherches


class GrapheReprisTests(unittest.TestCase):
    def test_lucien_garder_le_graphe_repris_rend_la_recherche_complete(self):
        m = lucien_au_grenier_noir()
        with patch.object(planification, "_GRAPHES", {}), patch.object(planification, "_MEMOIRE", {}), \
                patch.object(planification, "VERIFIER", True), diagnostics() as recherches:
            # Le graphe est gardé à la deuxième recherche sur les mêmes entrées, repris à la troisième.
            fautes, plans = [], []
            for biens in (65.0, 72.0, 80.0):
                lire(m, "lucien")["besoins"]["biens"] = biens
                fautes.append(prix_faute(m, "lucien", "biens"))
                plans.append(garder(m, "lucien", "grenier"))
        self.assertEqual(len(set(fautes)), 3)
        self.assertEqual([(r["graphe"], r["memoire"]) for r in recherches],
                         [(False, False), (False, False), (True, False)])
        # Les nouveaux prix peuvent changer l'arrêt devant les résultats
        # terminaux minorés ; comparer au recalcul avec ces mêmes prix.
        with patch.object(planification, "_GRAPHES", Oublieux()), patch.object(planification, "_MEMOIRE", {}), \
                diagnostics() as refaites:
            self.assertEqual(garder(m, "lucien", "grenier"), plans[2])
        self.assertEqual(recherches[2]["noeuds"], refaites[0]["noeuds"])
        self.assertEqual([x["operation"] for x in plans[0]], [x["operation"] for x in plans[2]])

    def assertMemeMonde(self, cree, minutes, pas, qui):
        avec, recherches = vivre_par_pas(cree(), minutes, pas, {})
        sans, _ = vivre_par_pas(cree(), minutes, pas, Oublieux())
        self.assertTrue(any(r["graphe"] and r["pnj"] == qui for r in recherches))
        self.assertEqual(avec.data, sans.data)

    def test_lucien_au_grenier_noir_meme_monde_avec_ou_sans_graphe(self):
        self.assertMemeMonde(lucien_au_grenier_noir, 30, 5, "lucien")

    def test_odon_affame_a_la_mine_meme_monde_avec_ou_sans_graphe(self):
        # Même nature, ailleurs : à la mine (départ tiré), Odon a faim et son scrupule s'use à
        # chaque minute.
        self.assertMemeMonde(lambda: creer("mine", 1985), 30, 5, "odon")


if __name__ == "__main__":
    unittest.main()
