"""Description physique commune : le MJ décrit un objet existant, le moteur vérifie et déduit."""
from pathlib import Path
import tempfile
import unittest

from donjon.atelier import nouveau_atelier
from donjon.defi import nouveau_defi
from donjon.faits_locaux import preparer_faits
from donjon.matiere import charge_deduite, masse_deduite, valider
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import decrire


def planches(pieces=2, longueur=150, largeur=20, epaisseur=2.5):
    # Le lot du Relais compte 2 utilisations et pèse 8 kg : 2 planches de 4,5 kg chacune.
    return {"forme": "barre", "matiere": "bois", "pieces": pieces, "nom_piece": "planche de bac",
            "dimensions": {"longueur_cm": longueur, "largeur_cm": largeur, "epaisseur_cm": epaisseur,
                           "diametre_cm": 0, "hauteur_cm": 0}}


def relais_avec_planches():
    m = nouveau_defi(1985)
    m.joueur["salle"] = m.objets["planches"]["lieu"]
    m.data["mode_cases"] = False
    return m


def qualifier(m, id, physique):
    return preparer_faits(m, {"ajouts": [{"type": "qualification", "ancrage": id, "physique": physique}]})


class DescriptionTests(unittest.TestCase):
    def test_les_planches_du_relais_se_decrivent_et_le_restent_apres_rechargement(self):
        m = relais_avec_planches()
        travail, texte, _ = qualifier(m, "planches", planches())
        o = travail.objets["planches"]
        self.assertEqual(o["physique"]["pieces"], 2)
        # Le moteur déduit ce qui découle de la description : rôle, longueur, charge.
        self.assertEqual((o["ressource"], o["longueur_cm"]), ("perche", 150))
        self.assertEqual(o["charge_jeu_kg"], charge_deduite(o["physique"]))
        self.assertIn("2 pièces de 1,5 m × 20 cm × 2,5 cm", texte)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "partie.json"
            travail.sauver(chemin)
            recharge = Monde.charger(chemin)
        self.assertEqual(recharge.objets["planches"]["physique"], o["physique"])
        self.assertIn("2 pièces", decrire(recharge, "planches", detail=True))

    def test_une_description_qui_contredit_la_masse_est_refusee_avec_la_masse_deduite(self):
        m = relais_avec_planches()
        with self.assertRaises(ErreurMonde) as refus:
            qualifier(m, "planches", planches(longueur=250, largeur=30, epaisseur=4))
        self.assertIn("pèse 8 kg", refus.exception.attendu)
        self.assertIn("ajuste dimensions ou pieces", refus.exception.attendu)

    def test_la_matiere_doit_suivre_celle_de_l_objet(self):
        m = relais_avec_planches()
        with self.assertRaises(ErreurMonde) as refus:
            qualifier(m, "planches", {**planches(), "matiere": "fer"})
        self.assertIn("matiere = bois", refus.exception.attendu)

    def test_une_dimension_manquante_est_nommee(self):
        m = relais_avec_planches()
        sans_epaisseur = planches()
        sans_epaisseur["dimensions"]["epaisseur_cm"] = 0
        with self.assertRaises(ErreurMonde) as refus:
            qualifier(m, "planches", sans_epaisseur)
        self.assertIn("epaisseur_cm", refus.exception.attendu)

    def test_un_objet_deja_decrit_ne_se_redecrit_pas(self):
        m = relais_avec_planches()
        travail, _, _ = qualifier(m, "planches", planches())
        with self.assertRaises(ErreurMonde) as refus:
            qualifier(travail, "planches", planches(pieces=2, longueur=225))
        self.assertIn("déjà sa description physique", refus.exception.attendu)


class AtelierTests(unittest.TestCase):
    def test_les_materiaux_de_l_atelier_sont_decrits_et_gardent_leurs_grandeurs(self):
        m = nouveau_atelier()
        perche, ficelle = m.objets["perche_1"], m.objets["ficelle"]
        self.assertEqual((perche["longueur_cm"], perche["charge_jeu_kg"], perche["diametre_cm"]), (300, 110, 5))
        self.assertEqual((ficelle["longueur_cm"], ficelle["charge_jeu_kg"]), (2000, 110))
        # La masse déclarée s'accorde avec la description (conventions de densité).
        for o in (perche, ficelle):
            self.assertLessEqual(0.5, o["masse"] / masse_deduite(o["physique"]))
            self.assertLessEqual(o["masse"] / masse_deduite(o["physique"]), 2)

    def test_une_ficelle_en_bois_ou_une_perche_sans_diametre_sont_refusees(self):
        m = nouveau_atelier()
        o = {k: v for k, v in m.objets["perche_1"].items() if k != "physique"}
        with self.assertRaises(ErreurMonde):
            valider(o, {"forme": "barre", "matiere": "bois", "pieces": 1,
                        "dimensions": {"longueur_cm": 300, "diametre_cm": 0, "largeur_cm": 0,
                                       "epaisseur_cm": 0, "hauteur_cm": 0}})


if __name__ == "__main__":
    unittest.main()


class RecadrageTests(unittest.TestCase):
    def test_un_objet_pris_pour_un_personnage_est_recadre_vers_sa_description(self):
        # Cas du banc Luna : « elles font quelle taille, ces planches de bac ? » proposé en mode
        # enrichir, comme pour un personnage ; le refus partait tel quel au joueur.
        from unittest.mock import patch
        from donjon.mj import MJOpenAI
        m = relais_avec_planches()
        enrichir = {"mode": "enrichir", "texte": "", "faits": [], "proposition": {"ajouts": [
            {"personnage": "planches", "facette": "silhouette", "description": "Des planches longues."}]}}
        decrire_planches = {"mode": "etablir_faits", "texte": "", "faits": [], "proposition": {"ajouts": [
            {"type": "qualification", "ancrage": "planches", "physique": planches()}]}}
        dialogue = {"mode": "dialogue", "texte": "Elles font un mètre et demi.", "faits": [], "proposition": None}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_echanger", side_effect=[enrichir, decrire_planches, dialogue]) as appel:
            reponse = mj._echanger_prepare(m, "elles font quelle taille, ces planches de bac ?")
        retour = appel.call_args_list[1].kwargs["retour_moteur"]
        self.assertIn("est un objet", retour["attendu"])
        self.assertNotIn("personnage", reponse["texte"])
        self.assertIn("2 pièces", reponse["texte"])


class ContenuTests(unittest.TestCase):
    """Cas d'une partie : « il faut quoi comme combustible pour ma lanterne ? »."""

    def contenu(self, m, matiere):
        return preparer_faits(m, {"ajouts": [{"type": "qualification", "ancrage": "lanterne",
                                              "contenu": {"matiere": matiere}}]})

    def test_la_lanterne_brule_de_l_huile_et_le_garde(self):
        m = relais_avec_planches()
        travail, texte, _ = self.contenu(m, "huile")
        self.assertIn("brûle de l'huile", texte)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "partie.json"
            travail.sauver(chemin)
            recharge = Monde.charger(chemin)
        self.assertIn("brûle de l'huile", decrire(recharge, "lanterne", detail=True))

    def test_une_source_de_lumiere_ne_brule_pas_de_l_eau(self):
        with self.assertRaises(ErreurMonde) as refus:
            self.contenu(relais_avec_planches(), "eau")
        self.assertIn("huile", refus.exception.attendu)

    def test_un_contenu_etabli_ne_se_redonne_pas(self):
        travail, _, _ = self.contenu(relais_avec_planches(), "huile")
        with self.assertRaises(ErreurMonde) as refus:
            self.contenu(travail, "suif")
        self.assertIn("ne le redonne pas", refus.exception.attendu)


class LotTests(unittest.TestCase):
    """Un lot décrit fournit des pièces distinctes ; il ne se compte que d'une façon."""

    def lot_decrit(self):
        m = relais_avec_planches()
        travail, _, _ = qualifier(m, "planches", planches())
        travail.objets["planches"]["proprietaire"] = None
        return travail

    def test_le_nombre_de_pieces_suit_ce_qu_il_reste(self):
        with self.assertRaises(ErreurMonde) as refus:
            qualifier(relais_avec_planches(), "planches", planches(pieces=3, longueur=100))
        self.assertIn("pieces = 2", refus.exception.attendu)

    def test_prelever_une_planche_la_porte_et_diminue_le_lot(self):
        from unittest.mock import patch
        from donjon.moteur import Moteur
        from donjon.operations import etape, sequence
        m = self.lot_decrit()
        masse_avant = m.objets["planches"]["masse"]
        plan = Moteur(m).preparer(sequence(etape("prelever", "planches", "joueur")))
        with patch.object(Monde, "d20", return_value=20):
            Moteur(m).executer(plan)
        piece = m.objets["planches_1"]
        self.assertEqual((piece["nom"], piece["lieu"], piece["physique"]["pieces"]), ("planche de bac", "joueur", 1))
        self.assertEqual(piece["longueur_cm"], 150)
        lot = m.objets["planches"]
        self.assertEqual((lot["physique"]["pieces"], lot["charges"]), (1, 1))
        self.assertAlmostEqual(lot["masse"] + piece["masse"], masse_avant, places=2)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)
            recharge = Monde.charger(chemin)
        self.assertEqual(recharge.objets["planches_1"]["lieu"], "joueur")
        self.assertIn("1,5 m", decrire(recharge, "planches_1", detail=True))

    def test_un_objet_seul_ne_se_preleve_pas(self):
        from donjon.moteur import Moteur
        from donjon.operations import etape, sequence
        m = relais_avec_planches()
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(sequence(etape("prelever", "planches", "joueur")))
        self.assertIn("décris d'abord planches", refus.exception.attendu)

    def test_bruler_une_planche_retire_une_piece(self):
        from donjon.perception import alimenter
        m = self.lot_decrit()
        self.assertTrue(alimenter(m, "brasero", "planches"))
        self.assertEqual((m.objets["planches"]["charges"], m.objets["planches"]["physique"]["pieces"]), (1, 1))

    def test_un_lot_ne_sert_pas_de_montant_avant_le_prelevement(self):
        from donjon.artisanat import ressource
        m = self.lot_decrit()
        with self.assertRaises(ErreurMonde) as refus:
            ressource(m, "planches", "perche")
        self.assertIn("prélève d'abord une pièce", refus.exception.attendu)
