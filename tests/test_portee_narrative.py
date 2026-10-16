import unittest
from unittest.mock import patch

from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde
from donjon.portee_narrative import controler, descriptions


class PorteeNarrativeTests(unittest.TestCase):
    def test_savoir_pnj_revu_comme_point_de_vue_et_non_comme_fait_du_monde(self):
        souvenir = "Gorm se rappelle les longues veilles de son enfance."
        reponse = {"mode": "enrichir_savoirs", "proposition": {
            "personnage": "marchand", "savoirs": [{"sujet": "souvenir_personnel",
                                                "texte": souvenir}]}}
        entrees = descriptions(reponse)
        self.assertEqual(len(entrees), 1)
        self.assertEqual(entrees[0]["representations_autorisees"], ["savoir_pnj"])
        rapport = {"descriptions": [{"representation": "savoir_pnj", "mobilite": [],
            "placement": "aucun", "impact_scenario": "aucun", "capacites": [],
            "fragments": [{"texte": souvenir, "portee": "sujet", "preuve": "", "motif": ""}]}]}
        self.assertFalse(controler(entrees, rapport))
        rapport["descriptions"][0]["impact_scenario"] = "solution"
        self.assertTrue(controler(entrees, rapport))
        rapport["descriptions"][0]["impact_scenario"] = "aucun"
        rapport["descriptions"][0]["fragments"][0]["portee"] = "sans_preuve"
        self.assertTrue(controler(entrees, rapport))

    def test_capacites_affirmees_et_declares_doivent_coincider(self):
        base = {"type": "objet", "ancrage": "mur", "nom": "clochette de cuivre",
                "genre": "f", "texte": "Le cuivre est martelé.",
                "materiau": "cuivre", "masse": 0.2, "mobile": True,
                "relation": "pose", "capacites": [{"nature": "son", "intensite": 2}]}
        def rapport(capacites_nom):
            return {"descriptions": [
                {"representation": "objet", "mobilite": [], "placement": "aucun",
                 "impact_scenario": "aucun", "capacites": capacites_nom,
                 "fragments": [{"texte": base["nom"], "portee": "sujet",
                                "preuve": "", "motif": ""}]},
                {"representation": "aspect", "mobilite": [], "placement": "aucun",
                 "impact_scenario": "aucun", "capacites": [],
                 "fragments": [{"texte": base["texte"], "portee": "sujet",
                                "preuve": "", "motif": ""}]},
            ]}
        def entrees(ajout):
            return descriptions({"mode": "etablir_faits", "proposition": {"ajouts": [ajout]}})
        self.assertFalse(controler(entrees(base), rapport(["son"])))
        self.assertTrue(controler(entrees({**base, "capacites": []}), rapport(["son"])))
        self.assertTrue(controler(entrees(base), rapport([])))
        self.assertTrue(controler(entrees({**base, "capacites": [
            {"nature": "lumiere", "niveau": 2, "combustible": 20}]}), rapport([])))
        self.assertTrue(controler(entrees({**base, "capacites": []}), rapport(["tranchable"])))
        self.assertTrue(controler(entrees({**base, "capacites": [
            {"nature": "tranchable", "seuil": 1, "tenacite": 2}]}), rapport([])))

    def test_couverture_et_preuves_du_controle(self):
        entree = [{"sujet": {"nature": "facette d'un personnage"},
                   "texte": "Une porte secrète est derrière lui.",
                   "representations_autorisees": ["portrait"]}]
        with self.assertRaises(ErreurMonde):
            controler(entree, {"descriptions": []})
        with self.assertRaises(ErreurMonde):
            controler(entree, {"descriptions": [{"fragments": [
                {"texte": "Une porte secrète", "portee": "sujet", "preuve": "", "motif": ""}]}]})
        rapport = {"descriptions": [{"representation": "portrait", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [
            {"texte": "Une porte secrète est derrière lui.", "portee": "sans_preuve",
             "preuve": "", "motif": "Une autre entité est affirmée."}]}]}
        self.assertEqual(controler(entree, rapport)[0]["motif"], "Une autre entité est affirmée.")
        rapport["descriptions"][0]["fragments"][0].update(portee="attestation",
                                                             preuve="Une porte existe.")
        self.assertTrue(controler(entree, rapport, ["Une porte existe."]))
        rapport["descriptions"][0]["fragments"][0]["preuve"] = entree[0]["texte"]
        self.assertFalse(controler(entree, rapport, [entree[0]["texte"]]))

    def test_contre_revue_decoupe_une_phrase_malgre_un_sujet_valide(self):
        texte = "Ses yeux sont gris et une autre porte apparaît."
        entree = [{"sujet": {"nature": "facette d'un personnage"}, "texte": texte,
                   "representations_autorisees": ["portrait"]}]
        rapport = {"descriptions": [{"representation": "portrait", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [
            {"texte": "Ses yeux sont gris", "portee": "sujet", "preuve": "", "motif": ""},
            {"texte": " et une autre porte apparaît.", "portee": "sans_preuve",
             "preuve": "", "motif": "Une nouvelle porte exige un autre fait."}]}]}
        obstacles = controler(entree, rapport)
        self.assertEqual(len(obstacles), 1)
        self.assertEqual(obstacles[0]["texte"], " et une autre porte apparaît.")

    def test_un_sujet_entierement_couvert_reste_refuse_si_sa_representation_differe(self):
        for requise in ("objet", "texte_lisible", "etat_du_monde", "indetermine"):
            with self.subTest(requise=requise):
                entree = [{"sujet": {"support": "mur", "nom": "marque"},
                           "texte": "Une marque est visible.",
                           "representations_autorisees": ["aspect"]}]
                rapport = {"descriptions": [{"representation": requise, "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [],
                    "fragments": [{"texte": entree[0]["texte"], "portee": "sujet",
                                   "preuve": "", "motif": ""}]}]}
                self.assertEqual(len(controler(entree, rapport)), 1)

    def test_objet_portable_decrit_comme_fixe_est_refuse(self):
        reponse = {"mode": "etablir_faits", "proposition": {"ajouts": [{
            "type": "objet", "ancrage": "mur", "nom": "crochet de cuivre",
            "genre": "m", "texte": "Il est fixé au mur.", "materiau": "cuivre",
            "masse": 0.05, "mobile": True, "relation": "pose", "capacites": []}]}}
        entrees = descriptions(reponse)
        rapport = {"descriptions": [
            {"representation": "objet", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [{
                "texte": "crochet de cuivre", "portee": "sujet", "preuve": "", "motif": ""}]},
            {"representation": "objet", "mobilite": ["fixe"], "placement": "fixe", "impact_scenario": "aucun", "capacites": [], "fragments": [{
                "texte": "Il est fixé au mur.", "portee": "sujet", "preuve": "", "motif": ""}]},
        ]}
        self.assertEqual(len(controler(entrees, rapport)), 1)
        fixe = {**reponse["proposition"]["ajouts"][0], "relation": "fixe"}
        entrees = descriptions({"mode": "etablir_faits", "proposition": {"ajouts": [fixe]}})
        self.assertFalse(controler(entrees, rapport))

    def test_objet_qui_fournit_une_solution_de_quete_ne_passe_pas_comme_decor(self):
        reponse = {"mode": "etablir_faits", "proposition": {"ajouts": [{
            "type": "objet", "ancrage": "mur", "nom": "autre objet recherché",
            "genre": "m", "texte": "Sa surface est ternie.", "materiau": "bronze",
            "masse": 1, "mobile": True, "relation": "pose", "capacites": []}]}}
        entrees = descriptions(reponse)
        rapport = {"descriptions": [
            {"representation": "objet", "mobilite": [], "placement": "aucun", "impact_scenario": "solution", "capacites": [],
             "fragments": [{"texte": "autre objet recherché", "portee": "sujet",
                            "preuve": "", "motif": ""}]},
            {"representation": "aspect", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [],
             "fragments": [{"texte": "Sa surface est ternie.", "portee": "sujet",
                            "preuve": "", "motif": ""}]},
        ]}
        self.assertEqual(len(controler(entrees, rapport)), 1)

    def test_facette_de_personnage_passe_par_le_meme_controle(self):
        def reponse(texte):
            return {"mode": "enrichir", "texte": "", "faits": [],
                    "proposition": {"ajouts": [{"personnage": "marchand", "facette": "visage",
                                               "description": texte}]}}
        refuse = reponse("Une autre pièce est cachée derrière son visage.")
        corrige = reponse("Son visage est creusé de rides fines.")
        self.assertEqual(descriptions(refuse)[0]["sujet"]["personnage"], "marchand")
        sorties = [refuse,
                   {"descriptions": [{"representation": "etat_du_monde", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [
                       {"texte": "Une autre pièce est cachée derrière son visage.",
                        "portee": "sans_preuve", "preuve": "", "motif": "Autre lieu."}]}]},
                   corrige,
                   {"descriptions": [{"representation": "portrait", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [
                       {"texte": "Son visage est creusé de rides fines.",
                        "portee": "sujet", "preuve": "", "motif": ""}]}]}]
        with patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties) as appel:
            resultat = MJOpenAI()._appeler("", {"faits": {}}, "Décris Gorm",
                                          "repondre_au_joueur", {})
        self.assertEqual(appel.call_count, 4)
        self.assertEqual(resultat, corrige)


if __name__ == "__main__":
    unittest.main()
