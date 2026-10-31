"""Découpe : quantité consommable conservée, vraie boucle MJ et sauvegardes."""
import copy
import unittest

from donjon.artisanat import decouper
from donjon.auberge import nouveau_auberge
from donjon.atelier import nouveau_atelier
from donjon.matiere import appliquer, valider
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.perception import alimenter
from donjon.pnj import _executer
from donjon.rendu import decrire
from tests.test_audits_attendu import jouer
from tests.test_assemblage import executer
from tests.test_matiere import planches, qualifier, relais_avec_planches
from tests.test_qualification import decoupe
from tests.test_relances_luna import action
from tests.test_tensions import recharger


def reserve(scenario):
    if scenario == "relais":
        m, _, _ = qualifier(relais_avec_planches(), "planches", planches())
        lot, feu, longueur = "planches", "brasero", 150
    else:
        m = nouveau_auberge(1985, "fixe")
        lot, feu, longueur = "fagots_etable", "atre", 40
        o = m.objets[lot]
        appliquer(o, valider(o, {"forme": "barre", "matiere": "bois", "pieces": 3,
            "nom_piece": "bûche de chauffage", "dimensions": {"longueur_cm": longueur, "diametre_cm": 10}}))
    m.data["mode_cases"] = False
    m.joueur["salle"] = m.objets[lot]["lieu"]
    m.data["salles"][m.joueur["salle"]]["lumiere_naturelle"] = 2
    # Prémisses d'auteur : le bois est acquis, une hache est portée.
    m.objets[lot]["proprietaire"] = "joueur"
    m.objets["hache"] = copy.deepcopy(nouveau_atelier().objets["hache"])
    m.objets["hache"]["lieu"] = "joueur"
    return recharger(m), lot, feu, longueur


class DecoupeRessourcesTests(unittest.TestCase):
    def test_planche_et_buche_decoupees_puis_brulées_dans_la_boucle(self):
        for scenario, taille, durees in (("relais", 50, (30, 60)), ("auberge", 10, (11, 34))):
            with self.subTest(scenario=scenario):
                m, lot, feu, longueur = reserve(scenario)
                quantite = m.objets[lot]["charges"] * m.objets[lot]["duree_combustion"]
                p = sequence(etape("prelever", lot, "joueur"))
                m, _, _ = jouer(m, "mj je prends une pièce de mon bois", [action(p)], [], suite=("tenter",))
                piece, morceau = lot + "_1", lot + "_1_1"
                masse = m.objets[piece]["masse"]
                p = decoupe(piece, longueur=taille)
                m, texte, _ = jouer(m, f"mj je coupe {taille} cm de mon bois", [action(p)], [], suite=("tenter",))
                self.assertIn(f"un morceau de {taille} cm s'en détache", texte)
                m = recharger(m)
                a, b = m.objets[morceau], m.objets[piece]
                self.assertEqual((a["duree_combustion"], b["duree_combustion"]), durees)
                self.assertEqual((a["charges"], b["charges"]), (1, 1))
                self.assertEqual(a["longueur_cm"] + b["longueur_cm"], longueur)
                self.assertAlmostEqual(a["masse"] + b["masse"], masse)
                self.assertEqual(sum(m.objets[i]["charges"] * m.objets[i]["duree_combustion"]
                                     for i in (lot, piece, morceau)), quantite)
                self.assertIn(f"{taille} cm", decrire(m, morceau, detail=True))
                self.assertIn("1 utilisation", decrire(m, morceau, detail=True, technique=True))
                # Aller au foyer du scénario avec le morceau porté, puis l'alimenter.
                m.joueur["salle"] = m.objets[feu]["lieu"]
                m.objets[feu]["allume"] = True
                m = recharger(m)
                avant, minute = m.objets[feu]["combustible"], m.data["minutes"]
                p = sequence(etape("alimenter", feu, outil=morceau))
                m, texte, _ = jouer(m, "mj je mets le morceau dans le feu", [action(p)], [], suite=("tenter",))
                m = recharger(m)
                self.assertEqual(m.objets[morceau]["charges"], 0)
                self.assertEqual(m.objets[feu]["combustible"], avant + durees[0] - (m.data["minutes"] - minute))
                self.assertIn("est rechargé avec le morceau", texte)
                self.assertIn("Il n'en reste plus", decrire(m, morceau, detail=True))
                self.assertIn(f"{m.objets[feu]['combustible']} min", decrire(m, feu, detail=True, technique=True))
                # Le reste est remis à un PNJ, qui exécute le même geste.
                qui = "aubin" if scenario == "relais" else "joss"
                m.objets[qui]["lieu"] = m.objets[feu]["lieu"]
                m.objets[piece]["lieu"] = qui
                m.objets[piece]["proprietaire"] = qui
                m = recharger(m)
                avant = m.objets[feu]["combustible"]
                lignes = []
                geste = {**etape("alimenter", feu, outil=piece), "condition": "toujours"}
                self.assertTrue(_executer(m, qui, geste, lignes, []))
                self.assertFalse(alimenter(m, feu, piece))
                m = recharger(m)
                self.assertEqual(m.objets[feu]["combustible"], avant + durees[1])
                self.assertTrue(any("alimente" in ligne for ligne in lignes))
                self.assertIn("Il n'en reste plus", decrire(m, piece, detail=True))

    def test_trop_petit_refuse_avant_execution_et_sans_mutation(self):
        for scenario in ("relais", "auberge"):
            for taille in (5, 35):
                with self.subTest(scenario=scenario, taille=taille):
                    m, lot, _, _ = reserve(scenario)
                    executer(m, sequence(etape("prelever", lot, "joueur")))
                    piece = lot + "_1"
                    # Deux minutes : 5 cm ne portent pas une minute ; 35 cm en laissent trop peu.
                    m.objets[piece]["duree_combustion"] = 2
                    if scenario == "relais" and taille == 35:
                        taille = 145
                    m = recharger(m)
                    avant = copy.deepcopy(m.data)
                    with self.assertRaises(ErreurMonde) as refus:
                        Moteur(m).preparer(decoupe(piece, longueur=taille))
                    self.assertIn(piece + ".duree_combustion=2", refus.exception.attendu)
                    self.assertIn("accepté", refus.exception.attendu)
                    self.assertEqual(m.data, avant)
                    p = decoupe(piece, longueur=taille)
                    # La boucle affiche le refus déterministe, puis abandon de la proposition.
                    m, texte, _ = jouer(m, "mj je coupe ce morceau", [action(p)] * 4, [])
                    self.assertIn("trop peu de ressource", texte)
                    self.assertNotIn(refus.exception.attendu, texte)
                    self.assertNotIn(piece + "_1", m.objets)
                    self.assertEqual(m.objets[piece], avant["objets"][piece])

    def test_torche_minutes_et_substance_sur_les_deux_fragments(self):
        m, _, _, _ = reserve("relais")
        o = m.objets["torche"]
        o.update(lieu="joueur", proprietaire="joueur", allume=False, contenu={"matiere": "cire"})
        appliquer(o, valider(o, {"forme": "barre", "matiere": "bois", "pieces": 1,
            "nom_piece": "", "dimensions": {"longueur_cm": 60, "diametre_cm": 3}}))
        total = o["combustible"]
        m, texte, _ = jouer(m, "mj je coupe 20 cm de ma torche", [action(decoupe("torche", longueur=20))], [], suite=("tenter",))
        m = recharger(m)
        self.assertEqual(sum(m.objets[i]["combustible"] for i in ("torche", "torche_1")), total)
        for i, minutes in (("torche", 40), ("torche_1", 20)):
            self.assertEqual(m.objets[i]["contenu"], {"matiere": "cire"})
            self.assertEqual(m.objets[i]["combustible"], minutes)
            self.assertFalse(m.objets[i]["allume"])
            self.assertIn(f"{minutes} min", decrire(m, i, detail=True, technique=True))
        self.assertIn("un morceau de 20 cm", texte)

    def test_compte_sans_duree_et_refus_sur_la_fonction_commune(self):
        m = nouveau_atelier()
        m.data["mode_cases"] = False
        m.objets["perche_1"]["charges"] = 9
        # Cette voie commune ne dépend ni de l'acteur, ni d'une proposition MJ.
        decouper(m, "perche_1", 100, "fragment")
        m = recharger(m)
        self.assertEqual((m.objets["fragment"]["charges"], m.objets["perche_1"]["charges"]), (3, 6))
        self.assertIn("3 utilisations", decrire(m, "fragment", detail=True, technique=True))
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as refus:
            decouper(m, "fragment", 5, "minuscule")
        self.assertIn("fragment.charges=3", refus.exception.attendu)
        self.assertEqual(m.data, avant)


if __name__ == "__main__":
    unittest.main()
