import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.enrichissement import catalogue, preparer_complements
from donjon.mj import MJOpenAI
from tests.support import simuler_couverture
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire, regarder
from donjon.transactions import du_type


def ajout(id="marchand", facette="yeux", description="Ses yeux sont gris clair."):
    return {"personnage": id, "facette": facette, "description": description}


def completer(*ajouts):
    return {"ajouts": list(ajouts)}


def reponse_enrichir(*ajouts):
    return {"mode": "enrichir", "texte": "", "faits": ["descriptions_a_completer"],
            "proposition": completer(*ajouts)}


DIALOGUE = {"mode": "dialogue", "texte": "Tu te souviens de ses yeux gris clair.",
            "faits": ["souvenirs_personnages"], "proposition": None,
            "_texte_moteur": True}


class EnrichissementTests(unittest.TestCase):
    def setUp(self):
        simuler_couverture(self)

    def test_autre_personnage_sans_portrait_et_detail_examinable_apres_rechargement(self):
        m = nouveau_monde()
        m.objets["mira"] = objet("mira", "Mira", "personnage", "antichambre", aliases=["mira"])
        from tests.support import presentes
        presentes(m,'mira')  # Cette conversation porte sur une personne déjà présentée.
        avant = copy.deepcopy(m.data)
        travail = preparer_complements(m, completer(ajout("mira"), ajout("mira", "silhouette", "Mira est élancée.")))
        self.assertEqual(m.data, avant)
        for champ in ("minutes", "jets", "bruit", "joueur", "journal"):
            self.assertEqual(travail.data[champ], avant[champ])
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            travail.sauver(chemin)
            travail = Monde.charger(chemin)
        cible = travail.trouver("yeux de Mira")
        self.assertIn("gris clair", decrire(travail, cible, detail=True))
        self.assertIn("élancée", regarder(travail))
        self.assertIn("gris clair", regarder(travail))
        for action in ("prendre", "frapper"):
            with self.assertRaises(ErreurMonde):
                Moteur(travail).preparer(proposition(action, cible, "couteau" if action == "frapper" else ""))
        self.assertIn("tissu vivant", Moteur(travail).executer(Moteur(travail).preparer(proposition("toucher", cible))))
        self.assertNotIn("yeux", catalogue(travail)["mira"]["facettes_disponibles"])
        with self.assertRaises(ErreurMonde):
            preparer_complements(travail, completer(ajout("mira", description="Ses yeux sont bleus.")))

    def test_souvenir_distant_enrichi_sans_fuite_humeur_ni_acces_physique(self):
        m = nouveau_monde()
        m.objets["marchand"]["humeur"] = "inquiet"
        m.objets["marchand"]["portrait"] = "Portrait changé en secret."
        travail = preparer_complements(m, completer(ajout()))
        souvenir = travail.contexte()["souvenirs_personnages"]["marchand"]
        self.assertIn("gris clair", json.dumps(souvenir))
        self.assertNotIn("inquiet", json.dumps(souvenir))
        self.assertNotIn("secret", json.dumps(souvenir))
        with self.assertRaises(ErreurMonde):
            travail.trouver("yeux")
        moteur = Moteur(travail)
        moteur.executer(moteur.preparer(proposition("aller", "ouest")))
        self.assertEqual(travail.trouver("yeux"), "detail_marchand_yeux")

    def test_inconnus_et_penombre_ne_permettent_pas_invention_visuelle(self):
        m = nouveau_monde()
        m.objets["mira"] = objet("mira", "Mira", "personnage", "crypte")
        self.assertNotIn("mira", catalogue(m))
        with self.assertRaises(ErreurMonde):
            preparer_complements(m, completer(ajout("mira")))
        m.objets["mira"]["lieu"] = "antichambre"
        m.objets["lanterne"]["allume"] = False
        self.assertNotIn("mira", catalogue(m))
        # Les souvenirs déjà établis restent consultables dans la pénombre.
        self.assertIn("marchand", catalogue(m))

    def test_rejet_atomique_des_remplacements_doublons_et_effets_mecaniques(self):
        for proposition_invalide in (
            completer(ajout(), ajout(facette="barbe")),
            completer(ajout(), ajout()),
            completer(ajout(facette="portrait")),
            completer(ajout(facette="FOR")),
            completer({**ajout(), "mobile": True}),
            completer(ajout("inconnu")),
            completer(ajout(description="")),
            completer(ajout(description="a" * 301)),
            completer(ajout(description="Texte\x1b[0m")),
            {"ajouts": "incorrect"},
        ):
            with self.subTest(proposition=proposition_invalide):
                m = nouveau_monde()
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde):
                    preparer_complements(m, proposition_invalide)
                self.assertEqual(m.data, avant)

    def test_revision_perimee_refusee(self):
        with self.assertRaises(ErreurMonde):
            preparer_complements(nouveau_monde(), completer(ajout()), revision=99)

    def test_details_de_plusieurs_personnages_demandent_une_cible_precise(self):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        m.objets["mira"] = objet("mira", "Mira", "personnage", "echoppe")
        from tests.support import presentes
        presentes(m,'mira')
        m = preparer_complements(m, completer(ajout(), ajout("mira")))
        with self.assertRaisesRegex(ErreurMonde, "Précisez"):
            m.trouver("yeux")
        self.assertEqual(m.trouver("yeux de Mira"), "detail_mira_yeux")
        self.assertEqual(m.trouver("yeux de Gorm"), "detail_marchand_yeux")

    def test_deux_appels_narration_recoit_les_faits_valides_monde_original_intact(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        def appel(instructions, entree, intention, fonction, schema):
            if "descriptions_a_completer" in entree["faits"] and entree["faits"]["descriptions_a_completer"]:
                return reponse_enrichir(ajout())
            self.assertIn("gris clair", json.dumps(entree["faits"]["souvenirs_personnages"]))
            self.assertNotIn("enrichir", schema["properties"]["mode"]["enum"])
            return copy.deepcopy(DIALOGUE)
        with patch.object(MJOpenAI, "_appeler", side_effect=appel) as appels:
            resultat = MJOpenAI().echanger(m, "De quelle couleur sont les yeux de Gorm ?")
        self.assertEqual(appels.call_count, 2)
        self.assertEqual(m.data, avant)
        self.assertEqual(du_type(resultat, "complements")["proposition"], completer(ajout()))

    def test_echec_second_appel_ou_boucle_sans_enregistrement(self):
        for seconde in (ErreurMonde("Réseau indisponible"), reponse_enrichir(ajout(facette="cheveux")),
                        {"mode": "action", "texte": "", "faits": [], "proposition": proposition("prendre", "cle")}):
            with self.subTest(seconde=seconde):
                m = nouveau_monde()
                avant = copy.deepcopy(m.data)
                with patch.object(MJOpenAI, "_appeler", side_effect=[reponse_enrichir(ajout()), seconde]) as appels:
                    with self.assertRaises(ErreurMonde):
                        MJOpenAI().echanger(m, "Ses yeux ?")
                self.assertEqual(m.data, avant)
                self.assertEqual(appels.call_count, 2)

    def test_boucle_jeu_enregistre_et_conserve_action_en_attente(self):
        p = proposition("detacher", "axe_haut", "couteau", "levier", 18)
        reponses = [{"mode": "action", "texte": "", "faits": [], "proposition": p},
                    reponse_enrichir(ajout()), copy.deepcopy(DIALOGUE)]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "_appeler", side_effect=reponses), patch.object(Monde, "d20", return_value=20), patch("builtins.input", side_effect=["mj je retire l'axe", "Ses yeux sont comment ?", "tenter", "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                self.assertEqual(jeu.main(["--recit-moteur", "--console", "--save", str(chemin), "--connexion", "api"]), 0)
            m = Monde.charger(chemin)
            self.assertIn("detail_marchand_yeux", m.objets)
            self.assertIn("gris clair", sortie.getvalue())
            self.assertFalse(m.objets["axe_haut"]["attache"])
            self.assertEqual(len(m.data["enrichissements"]), 1)

    def test_echec_sauvegarde_ne_montre_pas_la_fiction_non_enregistree(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            original = Monde.sauver
            def sauver(m, path):
                if m.data.get("enrichissements"):
                    raise OSError("Disque plein")
                return original(m, path)
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "_appeler", side_effect=[reponse_enrichir(ajout()), copy.deepcopy(DIALOGUE)]), patch.object(Monde, "sauver", sauver), patch("builtins.input", side_effect=["Ses yeux sont comment ?", "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                jeu.main(["--console", "--save", str(chemin), "--connexion", "api"])
            self.assertNotIn(DIALOGUE["texte"], sortie.getvalue())
            self.assertNotIn("detail_marchand_yeux", Monde.charger(chemin).objets)


if __name__ == "__main__":
    unittest.main()
