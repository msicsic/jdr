import copy
import json
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import patch

from donjon.comparaison import Comparateur, texte_resultat
from donjon.enrichissement import preparer_complements
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.moteur import Moteur, proposition


def dialogue(texte="Réponse."):
    return {"mode": "dialogue", "texte": texte, "faits": [], "proposition": None}


def enrichissement(couleur, facette="yeux"):
    return {"mode": "enrichir", "texte": "", "faits": ["descriptions_a_completer"],
            "proposition": {"ajouts": [{"personnage": "marchand", "facette": facette,
                                        "description": f"Ses yeux sont {couleur}."}]}}


class ComparaisonTests(unittest.TestCase):
    def creer(self, dossier=None, publier=None):
        fini = Event()
        def recevoir(fiche):
            if publier:
                publier(fiche)
            if fiche["secondaire"]["statut"] in ("Terminé", "Erreur"):
                fini.set()
        c = Comparateur(MJOpenAI("principal"), MJOpenAI("secondaire"), recevoir, dossier)
        self.addCleanup(c.fermer)
        return c, fini

    def test_parallele_et_secondaire_lent_ne_bloque_pas_principal(self):
        commence, liberer = Event(), Event()
        c, fini = self.creer()
        m = nouveau_monde()
        vues = {}
        def appel_secondaire(*args):
            vues["secondaire"] = copy.deepcopy(args[1])
            commence.set()
            liberer.wait(3)
            return {"mode": "action", "texte": "", "faits": [], "proposition": proposition("aller", "ouest")}
        def appel_principal(*args):
            self.assertTrue(commence.wait(2), "Le second modèle doit démarrer avant la fin du principal")
            vues["principal"] = copy.deepcopy(args[1])
            return {"mode": "action", "texte": "", "faits": [], "proposition": proposition("prendre", "cle")}
        with patch.object(c.principal, "_appeler", side_effect=appel_principal), patch.object(c.secondaire, "_appeler", side_effect=appel_secondaire):
            try:
                reponse = c.echanger(m, "Je prends la clé.")
                self.assertFalse(fini.is_set())
                self.assertEqual(vues["principal"], vues["secondaire"])
                self.assertEqual(m.objets["cle"]["lieu"], "antichambre")
                moteur = Moteur(m)
                moteur.executer(moteur.preparer(reponse["proposition"]))
            finally:
                liberer.set()
            self.assertTrue(fini.wait(2))
        self.assertEqual(m.objets["cle"]["lieu"], "joueur")
        self.assertEqual(m.joueur["salle"], "antichambre")
        self.assertEqual(m.data["minutes"], 1)
        self.assertEqual(c.fiches[1]["principal"]["appels"][0]["empreinte_requete"],
                         c.fiches[1]["secondaire"]["appels"][0]["empreinte_requete"])

    def test_inventions_independantes_et_cumul_tokens_deux_appels(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, fini = self.creer(Path(tmp))
            m = nouveau_monde()
            avant = copy.deepcopy(m.data)
            def repondre(mj, couleur):
                def appel(*args):
                    mj.derniere_utilisation = {"input_tokens": 100, "output_tokens": 20}
                    faits = args[1]["faits"]
                    if faits["descriptions_a_completer"]:
                        return enrichissement(couleur)
                    self.assertIn(couleur, json.dumps(faits["souvenirs_personnages"]))
                    return dialogue("Ses yeux sont " + couleur + ".")
                return appel
            with patch.object(c.principal, "_appeler", side_effect=repondre(c.principal, "gris")), patch.object(c.secondaire, "_appeler", side_effect=repondre(c.secondaire, "bruns")):
                reponse = c.echanger(m, "Ses yeux ?")
                self.assertTrue(fini.wait(2))
            self.assertEqual(m.data, avant)
            m = preparer_complements(m, reponse["_enrichissement"]["proposition"])
            self.assertEqual(m.objets["detail_marchand_yeux"]["description_visuelle"], "Ses yeux sont gris.")
            fiche = c.fiches[1]
            self.assertIn("bruns", texte_resultat(fiche["secondaire"]))
            self.assertIn("200 entrée / 40 sortie", texte_resultat(fiche["principal"]))
            self.assertEqual(fiche["principal"]["appels"][0]["empreinte_requete"], fiche["secondaire"]["appels"][0]["empreinte_requete"])
            self.assertNotEqual(fiche["principal"]["appels"][1]["empreinte_requete"], fiche["secondaire"]["appels"][1]["empreinte_requete"])
            lignes = [json.loads(ligne) for ligne in c.chemin.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(lignes[-1]["principal"]["statut"], "Terminé")
            self.assertEqual(lignes[-1]["secondaire"]["statut"], "Terminé")

    def test_erreur_secondaire_isolee_et_visible(self):
        c, fini = self.creer()
        with patch.object(c.principal, "_appeler", return_value=dialogue()), patch.object(c.secondaire, "_appeler", side_effect=ErreurMonde("Modèle indisponible")):
            self.assertEqual(c.echanger(nouveau_monde(), "Bonjour"), dialogue())
            self.assertTrue(fini.wait(2))
        self.assertIn("Modèle indisponible", texte_resultat(c.fiches[1]["secondaire"]))

    def test_erreur_principale_ne_promeut_pas_le_secondaire(self):
        c, fini = self.creer()
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        with patch.object(c.principal, "_appeler", side_effect=ErreurMonde("Principal indisponible")), patch.object(c.secondaire, "_appeler", return_value=dialogue("Le second répond.")):
            with self.assertRaisesRegex(ErreurMonde, "Principal indisponible"):
                c.echanger(m, "Bonjour")
            self.assertTrue(fini.wait(2))
        self.assertEqual(m.data, avant)

    def test_faits_refuses_restent_visibles_dans_la_trace(self):
        c, fini = self.creer()
        with patch.object(c.principal, "_appeler", return_value=dialogue()), patch.object(c.secondaire, "_appeler", return_value=enrichissement("verts", "barbe")):
            c.echanger(nouveau_monde(), "Sa barbe ?")
            self.assertTrue(fini.wait(2))
        secondaire = c.fiches[1]["secondaire"]
        self.assertEqual(secondaire["statut"], "Erreur")
        self.assertIn("FAITS PROPOSÉS", texte_resultat(secondaire))
        self.assertIn("verts", texte_resultat(secondaire))

    def test_journal_indisponible_ne_bloque_pas_le_jeu(self):
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "pas_un_dossier"
            fichier.write_text("test", encoding="utf-8")
            c, fini = self.creer(fichier)
            with patch.object(c.principal, "_appeler", return_value=dialogue()), patch.object(c.secondaire, "_appeler", return_value=dialogue()):
                self.assertEqual(c.echanger(nouveau_monde(), "Bonjour"), dialogue())
                self.assertTrue(fini.wait(2))
            self.assertIn("indisponible", c.fiches[1]["erreur_journal"])

    def test_fermeture_abandonne_la_file_sans_attendre_le_reseau(self):
        commence, liberer = Event(), Event()
        c, fini = self.creer()
        def appel(*args):
            commence.set()
            liberer.wait(3)
            return dialogue()
        with patch.object(c.principal, "_appeler", return_value=dialogue()), patch.object(c.secondaire, "_appeler", side_effect=appel) as second:
            try:
                c.echanger(nouveau_monde(), "Premier")
                self.assertTrue(commence.wait(2))
                c.echanger(nouveau_monde(), "Deuxième")
                c.fermer()
                self.assertTrue(c.ferme)
                self.assertIn("Interrompu", c.fiches[2]["secondaire"]["statut"])
            finally:
                liberer.set()
                c.thread.join(2)
            self.assertEqual(second.call_count, 1)


if __name__ == "__main__":
    unittest.main()
