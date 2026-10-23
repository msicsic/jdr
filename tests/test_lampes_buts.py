"""Les moyens d'éclairer suivent le but et ses gestes, jusqu'au monde rechargé."""
import unittest
from unittest.mock import patch

from donjon import caractere, planification as P, pnj
from donjon.deplacement_objet import deplacer
from donjon.echanges import executer as echanger
from donjon.esprits import croire, percevoir_tous
from donjon.monde import Monde
from donjon.rendu import decrire_perception
from tests.test_lampes_parts import nuit_noire
from tests.test_tensions import recharger


class LumiereDuButTests(unittest.TestCase):
    def scene(self, scenario, qui, donneur, source, lot, salle, capacites=()):
        m = nuit_noire(scenario, qui, donneur, source, lot, salle)
        m.objets[qui]["profil"].setdefault("securite", {})["noir"] = 0
        m.objets[qui]["profil"]["capacites"] = list(capacites)
        # Une remise de main à main, réelle ; le plan devra ensuite employer la part créée.
        deplacer(m, lot, donneur)
        croire(m, qui, lot, "lieu", donneur, "savoir", salle=salle, case=[3, 2])
        return recharger(m)

    def accomplir(self, m, qui, source, lot, but, vises):
        def chercher():
            return P.chercher(m, qui, but, vises, memo=["but éclairé", vises], emplois=())

        with patch.object(P, "VERIFIER", True), patch.object(P, "_MEMOIRE", {}), \
                patch.object(P, "_GRAPHES", {}), patch.object(Monde, "d20", return_value=20):
            plan = chercher()
            self.assertIsNotNone(plan)
            self.assertEqual(chercher(), plan)
            demande = P._couper(plan[1])
            self.assertEqual(len(demande), 1)
            self.assertEqual(demande[0]["operation"], "demander")
            self.assertEqual(demande[0]["outil"], lot)
            self.assertTrue(echanger(m, qui, demande[0], []))
            m = recharger(m)
            self.assertEqual(m.objets[lot]["charges"], 2)
            self.assertEqual(m.objets[source]["combustible"], 0)
            piece = next(k for k in m.objets if k.startswith(lot + "_"))
            self.assertEqual(m.objets[piece]["lieu"], qui)
            plan = chercher()
            self.assertIsNotNone(plan)
            self.assertEqual(chercher(), plan)
            etapes = P._couper(plan[1])
            self.assertTrue(any(x["operation"] == "alimenter" and x["outil"] == piece for x in etapes))
            lignes = []
            for etape in etapes:
                self.assertTrue(pnj._executer(m, qui, etape, lignes, []), etape)
                m = recharger(m)
            self.assertTrue(m.objets[source]["allume"])
            self.assertGreater(m.objets[source]["combustible"], 0)
            self.assertEqual(m.objets[piece]["charges"], 0)
            self.assertIn("éclaire la pièce", decrire_perception(m))
            self.assertTrue(any("allume" in x["texte"] for x in m.data["chronique"]))
        return m

    def test_inspecter_un_lieu_eclaire_sans_peur_ni_crochetage_deux_scenarios(self):
        # Un but composé : inspecter, et avoir de la lumière à l'issue. L'inspection
        # ordinaire reste possible dans le noir ; aucune règle du jeu n'est ajoutée.
        for scenario, qui, donneur, source, lot, salle in (
            ("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve"),
            ("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable"),
        ):
            with self.subTest(scenario=scenario):
                m = self.scene(scenario, qui, donneur, source, lot, salle)
                def but(v, e):
                    return bool(e.fait("inspecte", salle)) and v.lumiere(e) > 0
                m = self.accomplir(m, qui, source, lot, but, {"inspecter": (salle,)})
                self.assertIn(salle, m.data["esprits"][qui]["visites"])

    def test_la_chance_d_un_geste_decouvre_la_lumiere_sans_peur(self):
        m = self.scene("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve", ("crochetage",))
        deplacer(m, "crochets", "remy")
        deplacer(m, "coffre_paie", "reserve", position=[2, 1])
        m.objets["coffre_paie"]["proprietaire"] = "remy"
        percevoir_tous(m)
        croire(m, "remy", "coffre_paie", "lieu", "reserve", "savoir", salle="reserve", case=[2, 1])
        croire(m, "remy", "coffre_paie", "verrouillee", True, "savoir")
        croire(m, "remy", "coffre_paie", "lumiere", 0, "savoir")
        m = recharger(m)
        but = lambda v, e: e.fait("verrou", "coffre_paie") is False
        m = self.accomplir(m, "remy", "lampe_remy", "bidon_huile", but, {})
        self.assertFalse(m.objets["coffre_paie"]["verrouillee"])

    def test_un_autre_geste_qui_lit_la_lumiere_obtient_aussi_ses_moyens(self):
        m = self.scene("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        gestes_ordinaires = P.gestes

        def gestes(v, e, vises=None, but=None):
            # Contrat d'extension : une inspection visuelle, au lieu de l'inspection
            # ordinaire qui peut se faire au toucher. Seul ce geste de la fixture
            # exige de la lumière ; le but, lui, ne la lit jamais.
            for g in gestes_ordinaires(v, e, vises, but):
                if any(x["operation"] == "inspecter" and x["lieu"] == "reserve" for x in g[2]):
                    if not v.lumiere(e):
                        continue
                yield g

        with patch.object(P, "gestes", gestes):
            m = self.accomplir(m, "remy", "lampe_remy", "bidon_huile",
                               lambda v, e: bool(e.fait("inspecte", "reserve")),
                               {"inspecter": ("reserve",)})
        self.assertIn("reserve", m.data["esprits"]["remy"]["visites"])

    def test_une_capacite_ne_rend_pas_le_combustible_pertinent_pour_un_autre_but(self):
        m = self.scene("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve", ("crochetage",))
        v = P.Vue(m, "remy")
        v.emplois = frozenset()
        self.assertFalse(v.emploie_lumiere)
        self.assertFalse(v.pertinent("bidon_huile", {}))
        self.assertEqual(list(P._parts_remises(v, P.depart(m, "remy", v), "bidon_huile", "gaspard", {})), [])

    def test_le_graphe_repris_garde_la_dependance_decouverte_et_le_meme_plan(self):
        m = self.scene("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        but = lambda v, e: bool(e.fait("inspecte", "reserve")) and v.lumiere(e) > 0
        with patch.object(P, "VERIFIER", True), patch.object(P, "_MEMOIRE", {}), \
                patch.object(P, "_GRAPHES", {}), P.diagnostics() as recherches:
            plans = [P.chercher(m, "remy", but, {"inspecter": ("reserve",)},
                               memo=["inspection éclairée"], emplois=(), endurer=gain)
                     for gain in (1000, 1001, 1002)]
            self.assertIsNotNone(plans[0])
            self.assertEqual(plans, [plans[0]] * 3)
            self.assertEqual([r["graphe"] for r in recherches], [False, False, True])
            graphe = next(g for _, g in P._GRAPHES.values())
            self.assertTrue(graphe["lumiere"])
            self.assertTrue(any(n[4] for n in graphe["sombre"].values()))

    def test_le_graphe_repris_redecouvre_la_lumiere_selon_le_prix_d_une_faute(self):
        # La découverte suit l'ordre d'exploration, que le prix d'une faute change sans changer
        # les entrées du graphe. Un geste fautif (de la fixture) mène à un état où un geste lit la
        # lumière : bon marché, il est exploré et fait découvrir la lumière ; cher, le plan honnête
        # est trouvé avant. Le graphe repris doit rendre chaque fois la recherche neuve.
        m = self.scene("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        m.data["mode_cases"] = False  # borne d'un graphe synthétique aux coûts historiques explicites
        gestes_ordinaires = P.gestes

        def gestes(v, e, vises=None, but=None):
            if e.fait("essai", "reserve"):
                v.lumiere(e)
            yield from gestes_ordinaires(v, e, vises, but)
            if not e.fait("essai", "reserve"):
                yield 1, 0.5, [P._etape("patienter")], e.apres(faits=[(("essai", "reserve"), True)])

        prix = {"faute": 10.0}
        prix_faute = caractere.prix_faute

        def faute(monde, id, besoin=None, nom="honnetete"):
            return prix["faute"] if nom == "honnetete" else prix_faute(monde, id, besoin, nom)

        but = lambda v, e: bool(e.fait("inspecte", "reserve"))
        with patch.object(P, "gestes", gestes), patch.object(caractere, "prix_faute", faute),                 patch.object(P, "VERIFIER", True), patch.object(P, "_MEMOIRE", {}),                 patch.object(P, "_GRAPHES", {}), P.diagnostics() as recherches:
            # Une borne qui tient le plan sans les moyens d'éclairer, pas avec eux.
            plans = []
            for valeur in (10.0, 0.0, 10.0, 0.0):
                prix["faute"] = valeur
                plans.append(P.chercher(m, "remy", but, {"inspecter": ("reserve",)}, memo=["essai"],
                                        emplois=(), noeuds=3))
        self.assertEqual([r["graphe"] for r in recherches], [False, False, True, True])
        self.assertEqual([r["issue"] for r in recherches], ["plan", "borne", "plan", "borne"])
        self.assertEqual(plans[0], plans[2])
        self.assertEqual([x["operation"] for x in plans[0][1]], ["inspecter"])


if __name__ == "__main__":
    unittest.main()
