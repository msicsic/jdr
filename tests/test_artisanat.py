import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.artisanat import fabrication, dossier
from donjon.atelier import nouveau_atelier
from donjon.carte import carte
from donjon.config import MODELE_PAR_DEFAUT
from donjon.mj import MJOpenAI
from tests.support import simuler_couverture
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence


def fabriquer(**options):
    return fabrication(["perche_1", "perche_2"], "perche_3", "ficelle", "hache", **options)


def action(p):
    return {"mode": "action", "texte": "", "faits": ["atelier"], "proposition": p}


class ArtisanatTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_atelier()
        self.moteur = Moteur(self.m)

    def jouer(self, p, jet=20):
        with patch.object(Monde, "d20", return_value=jet):
            return self.moteur.executer(self.moteur.preparer(p))

    def echelle(self):
        self.jouer(fabriquer())
        return self.m.trouver("echelle")

    def test_fabrication_conserve_matiere_et_n_applique_rien_avant_resolution(self):
        avant = copy.deepcopy(self.m.data)
        masse = sum(o["masse"] for o in self.m.objets.values())
        plan = self.moteur.preparer(fabriquer())
        self.assertEqual(avant, self.m.data)
        self.assertEqual(plan.minutes, 26)
        self.jouer(fabriquer())
        o = self.m.objets[self.m.trouver("echelle")]
        self.assertEqual(o["barreaux"], 8)
        self.assertEqual(o["lieu"], "cour")
        self.assertEqual(self.m.objets["perche_3"]["longueur_cm"], 12)
        self.assertEqual(self.m.objets["ficelle"]["longueur_cm"], 1040)
        self.assertFalse(self.m.accessible("perche_1"))
        self.assertAlmostEqual(masse, sum(o["masse"] for o in self.m.objets.values()), places=5)
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(fabriquer())

    def test_echec_coute_temps_et_lien_sans_creer_et_arbitrage_memorise(self):
        self.jouer(fabriquer(difficulte=15), jet=1)
        self.assertFalse(any(o.get("assemblage") for o in self.m.objets.values()))
        self.assertEqual(self.m.objets["ficelle"]["longueur_cm"], 1880)
        self.assertEqual(self.m.objets["perche_1"]["longueur_cm"], 300)
        self.assertEqual(self.m.data["minutes"], 26)
        self.assertEqual(self.moteur.preparer(fabriquer(difficulte=10)).dd, 15)

    def test_travail_soigne_apres_trois_echecs_sans_jet_et_sans_effacer_pertes(self):
        for jet in (5, 8, 5):
            self.jouer(fabriquer(), jet)
        self.assertEqual(self.m.objets["ficelle"]["longueur_cm"], 1640)
        donnees = dossier(self.m)["suggestion"]
        self.assertEqual(donnees["lien_restant_apres_fabrication_cm"], 680)
        plan = self.moteur.preparer(donnees["travail_soigne"]["proposition"])
        self.assertFalse(plan.stat)
        self.assertEqual(plan.minutes, 52)
        arbitrages = copy.deepcopy(self.m.data["arbitrages"])
        with patch.object(Monde, "d20", side_effect=AssertionError("Aucun dé en travail soigné")):
            resultat = self.moteur.executer(plan)
        self.assertIn("52 minutes", resultat)
        self.assertEqual(self.m.data["minutes"], 130)
        self.assertEqual(self.m.objets["ficelle"]["longueur_cm"], 680)
        self.assertEqual(self.m.data["arbitrages"], arbitrages)
        self.assertEqual(self.m.objets[self.m.trouver("echelle")]["barreaux"], 8)

    def test_soigne_verifie_calme_urgence_materiaux_et_lumiere_durable(self):
        for cas in ("calme", "urgence", "ficelle", "lumiere"):
            with self.subTest(cas=cas):
                m = nouveau_atelier()
                if cas == "calme":
                    m.data["salles"]["cour"]["travail_calme"] = False
                elif cas == "urgence":
                    m.data["salles"]["cour"]["urgence_minutes"] = 30
                elif cas == "ficelle":
                    m.objets["ficelle"]["longueur_cm"] = 100
                else:
                    m.data["salles"]["cour"]["lumiere_naturelle"] = 0
                    m.objets["lanterne"].update(allume=True, combustible=20)
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde):
                    Moteur(m).preparer(fabriquer(rythme="soigne", difficulte=0))
                self.assertEqual(m.data, avant)

    def test_ancienne_proposition_garde_son_jet(self):
        p = fabriquer()
        del p["rythme"]
        plan = self.moteur.preparer(p)
        self.assertEqual((plan.stat, plan.dd, plan.minutes), ("DEX", 12, 26))

    def test_ressources_manquantes_et_mesures_inconnues_sans_mutation(self):
        for champ, valeur in (("longueur_cm", 200), ("charge_jeu_kg", None)):
            with self.subTest(champ=champ):
                m = nouveau_atelier()
                if valeur is None:
                    del m.objets["perche_3"][champ]
                else:
                    m.objets["perche_3"][champ] = valeur
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde):
                    Moteur(m).preparer(fabriquer())
                self.assertEqual(m.data, avant)
                self.assertIn("obstacle", dossier(m)["suggestion"])

    def test_sources_distinctes_propriete_outil_et_quantite(self):
        for variante in ("doublon", "autrui", "outil", "ficelle"):
            with self.subTest(variante=variante):
                m = nouveau_atelier()
                p = fabriquer()
                if variante == "doublon":
                    p["traverses"] = "perche_1"
                elif variante == "autrui":
                    m.objets["perche_1"]["proprietaire"] = "marchand"
                elif variante == "outil":
                    p["outil"] = "couteau"
                else:
                    m.objets["ficelle"]["longueur_cm"] = 100
                with self.assertRaises(ErreurMonde):
                    Moteur(m).preparer(p)

    def test_installer_monter_redescendre_retirer_et_persister(self):
        id = self.echelle()
        self.jouer(proposition("installer", id, "mur_atelier"))
        self.assertIn("accès vertical", carte(self.m))
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("prendre", id))
        self.jouer(proposition("franchir", id))
        self.assertEqual(self.m.joueur["salle"], "terrasse")
        self.assertTrue(self.m.accessible(id))
        self.assertIn("Terrasse", carte(self.m))
        self.assertNotIn("Cour de", carte(self.m))
        self.assertIn("remonter", self.moteur.preparer(proposition("desinstaller", id)).titre)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "atelier.json"
            self.m.sauver(path)
            charge = Monde.charger(path)
            self.assertEqual(self.m.data, charge.data)
            self.m, self.moteur = charge, Moteur(charge)
        self.jouer(proposition("franchir", id))
        self.assertEqual(self.m.joueur["salle"], "cour")
        self.jouer(proposition("desinstaller", id))
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("franchir", id))
        self.jouer(proposition("prendre", id))
        self.assertEqual(self.m.objets[id]["lieu"], "joueur")

    def test_trop_court_et_trop_lourd_ne_sont_pas_des_jets(self):
        id = self.echelle()
        self.m.objets["mur_atelier"]["appui_vertical"]["hauteur_cm"] = 400
        with self.assertRaisesRegex(ErreurMonde, "trop courte"):
            self.moteur.preparer(proposition("installer", id, "mur_atelier"))
        self.m.objets["mur_atelier"]["appui_vertical"]["hauteur_cm"] = 240
        self.jouer(proposition("installer", id, "mur_atelier"))
        self.m.joueur["masse_kg"] = 100
        with self.assertRaisesRegex(ErreurMonde, "charge"):
            self.moteur.preparer(proposition("franchir", id))

    def test_appui_detruit_structure_abimee_et_echec_montee(self):
        id = self.echelle()
        self.jouer(proposition("installer", id, "mur_atelier"))
        self.jouer(proposition("franchir", id), jet=1)
        self.assertEqual(self.m.joueur["salle"], "cour")
        self.m.objets[id]["integrite"] -= 1
        with self.assertRaisesRegex(ErreurMonde, "endommagé"):
            self.moteur.preparer(proposition("franchir", id))
        self.m.objets[id]["integrite"] = self.m.objets[id]["maximum"]
        self.m.objets["mur_atelier"]["integrite"] = 0
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(proposition("franchir", id))

    def test_proposition_perimee_refusee(self):
        plan = self.moteur.preparer(fabriquer())
        self.jouer(proposition("attendre"))
        with self.assertRaisesRegex(ErreurMonde, "monde a changé"):
            self.moteur.executer(plan)

    def test_scene_exterieure_outil_et_passage_visibles(self):
        from donjon.rendu import regarder
        self.assertIn("découper du bois", self.jouer(proposition("examiner", "hache")))
        self.assertNotIn("Aucune fenêtre", regarder(self.m))
        self.assertIn("2.4 m", regarder(self.m))
        id = self.echelle()
        self.jouer(proposition("installer", id, "mur_atelier"))
        self.assertIn("monter par l'échelle", regarder(self.m))
        self.jouer(proposition("franchir", id))
        self.assertIn("descendre par l'échelle", regarder(self.m))


class HarnaisTests(unittest.TestCase):
    def setUp(self):
        simuler_couverture(self)

    def test_reprise_identifiee_sans_appel_llm_ni_changement_de_methode(self):
        from donjon.harnais import derniere_tentative
        m = nouveau_atelier()
        moteur = Moteur(m)
        with patch.object(Monde, "d20", return_value=5):
            moteur.executer(moteur.preparer(fabriquer()))
        dernier = derniere_tentative(m)
        self.assertEqual(dernier["proposition_pour_reprise"]["action"], "fabriquer")
        self.assertFalse(dernier["reussite"])
        with patch.object(MJOpenAI, "_appeler", side_effect=AssertionError("La reprise est locale")) as api:
            reponse = MJOpenAI().echanger(m, "je retente")
        self.assertEqual(api.call_count, 0)
        attendue = fabriquer()
        attendue["justification"] = ""
        self.assertEqual(reponse["proposition"], attendue)
        self.assertIsNotNone(moteur.preparer(reponse["proposition"]))
        self.assertTrue(reponse["_reprise_locale"])
        self.assertEqual(m.data["revision"], 1)
        m.objets["ficelle"]["longueur_cm"] = 100
        with patch.object(MJOpenAI, "_appeler", side_effect=AssertionError("La reprise est locale")):
            reponse = MJOpenAI().echanger(m, "je retente")
        self.assertEqual(reponse["mode"], "dialogue")
        self.assertIn("100", reponse["texte"])

    def test_reprise_partielle_ne_rejoue_pas_les_etapes_reussies(self):
        from donjon.harnais import derniere_tentative
        from donjon.monde import nouveau_monde
        m = nouveau_monde()
        p = sequence(etape("deplacer", "cle", "joueur"),
                     etape("detacher", "axe_haut", outil="couteau", methode="levier", difficulte=18))
        moteur = Moteur(m)
        with patch.object(Monde, "d20", return_value=2):
            moteur.executer(moteur.preparer(p))
        self.assertEqual(len(derniere_tentative(m)["proposition_pour_reprise"]["etapes"]), 1)
        with patch.object(MJOpenAI, "_appeler", side_effect=AssertionError("Pas d'appel")):
            r = MJOpenAI().echanger(m, "je réessaie")
        self.assertEqual(r["proposition"]["etapes"][0]["operation"], "detacher")
        self.assertEqual(m.objets["cle"]["lieu"], "joueur")

    def test_question_de_reprise_ne_devient_pas_une_action_locale(self):
        m = nouveau_atelier()
        moteur = Moteur(m)
        with patch.object(Monde, "d20", return_value=5):
            moteur.executer(moteur.preparer(fabriquer()))
        dialogue = {"mode": "dialogue", "texte": "Tu peux recommencer avec les matériaux restants.",
                    "faits": ["derniere_tentative"], "proposition": None}
        with patch.object(MJOpenAI, "_appeler", return_value=dialogue) as api:
            r = MJOpenAI().echanger(m, "Je retente ?")
        self.assertEqual(api.call_count, 1)
        self.assertEqual(r["mode"], "dialogue")
        self.assertEqual(m.data["revision"], 1)

    def test_correction_une_fois_avec_obstacle_sans_modifier_monde(self):
        m = nouveau_atelier()
        avant = copy.deepcopy(m.data)
        appels = []
        def appeler(instructions, entree, *args):
            appels.append((instructions, entree))
            return action(fabriquer(largeur_cm=50 if len(appels) == 1 else 35))
        with patch.object(MJOpenAI, "_appeler", side_effect=appeler):
            r = MJOpenAI().echanger(m, "je fabrique une échelle")
        self.assertEqual(len(appels), 2)
        self.assertIn("408 cm", appels[1][1]["faits"]["retour_moteur"]["obstacle"])
        self.assertIn("atelier", appels[0][1]["faits"])
        self.assertNotIn("objet:anneau", appels[0][1]["faits"])
        self.assertEqual(r["proposition"]["largeur_cm"], 35)
        self.assertEqual(m.data, avant)

    def test_double_refus_sans_boucle_et_question_sans_action(self):
        m = nouveau_atelier()
        for message, p in (("je fabrique une échelle", fabriquer(largeur_cm=50)),
                           ("Puis-je fabriquer une échelle ?", fabriquer())):
            with patch.object(MJOpenAI, "_appeler", return_value=action(p)) as api:
                r = MJOpenAI().echanger(m, message)
            self.assertEqual(api.call_count, 3)
            self.assertEqual(r["mode"], "dialogue")
            self.assertEqual(m.data["revision"], 0)

    def test_narration_contexte_reduit_et_modele_unique_par_defaut(self):
        m = nouveau_atelier()
        self.assertEqual(MODELE_PAR_DEFAUT, "gpt-6-luna")
        def appeler(instructions, entree, *args):
            self.assertEqual(set(entree["faits"]), {"resultat_resolu", "joueur", "salle", "perception", "attestations", "ambiance_etablie"})
            return {"mode": "dialogue", "texte": "Tu poses ton échelle au sol.", "faits": ["resultat_resolu"], "proposition": None}
        with patch.object(MJOpenAI, "_appeler", side_effect=appeler):
            MJOpenAI().raconter_resultat(m, {"faits": ["Une échelle a été créée au sol."]})

    def test_console_confirmation_fabrication_et_reprise(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "atelier.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "echanger", return_value=action(fabriquer())), patch.object(MJOpenAI, "raconter_resultat", side_effect=AssertionError("Le résultat vient du moteur")), patch.object(Monde, "d20", return_value=20), patch("builtins.input", side_effect=["je fabrique une échelle", "tenter", "quitter"]), patch("sys.stdout", io.StringIO()) as out:
                jeu.main(["--recit-moteur", "--console", "--atelier", "--connexion", "api", "--save", str(path)])
            self.assertIn("échelle", out.getvalue())
            self.assertIn("26 min", out.getvalue())
            m = Monde.charger(path)
            self.assertEqual(m.objets[m.trouver("echelle")]["barreaux"], 8)
            self.assertEqual(len(m.data["journal"]), 1)


if __name__ == "__main__":
    unittest.main()
