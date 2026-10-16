import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.defi import nouveau_defi
from donjon.improvisation import effet, issue, proposition as improviser
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur
from donjon.narration import controler


def dialogue(texte):
    return {"mode": "dialogue", "texte": texte, "faits": [], "proposition": None}


def segment(verdict, sources=(), locuteur="", citation="", motif=""):
    return {"segments": [{"indice": 0, "verdict": verdict, "sources": list(sources),
                           "locuteur": locuteur, "citation": citation, "motif": motif}]}


class NarrationTests(unittest.TestCase):
    def test_couverture_et_references_du_controle(self):
        texte = "La porte est fermée. Une cloche apparaît."
        with self.assertRaises(ErreurMonde):
            controler(texte, segment("etabli", ["salle"]), {"salle": {}})
        with self.assertRaises(ErreurMonde):
            controler("La porte est fermée.", segment("etabli", ["source_inventee"]), {"salle": {}})

    def test_source_connue_ne_prouve_pas_une_nouvelle_affirmation(self):
        faits = {"objet:cloche": {"nom": "cloche"},
                 "attestations": ["La cloche est dans le beffroi."]}
        rapport = segment("etabli", ["attestations", "objet:cloche"])
        self.assertTrue(controler("Une seconde cloche est sous le plancher.", rapport, faits)["obstacles"])
        self.assertFalse(controler("La cloche est dans le beffroi.", rapport, faits)["obstacles"])

    def test_attribution_superflue_hors_parole_est_normalisee(self):
        phrase = "La cloche est dans le beffroi."
        faits = {"attestations": [phrase]}
        rapport = controler(phrase, segment("etabli", ["attestations"],
                                            locuteur="marchand", citation="Une autre phrase."), faits)
        self.assertFalse(rapport["obstacles"])
        self.assertEqual(rapport["segments"][0]["locuteur"], "")
        self.assertFalse(rapport["paroles"])

    def test_dialogue_invente_est_revise_puis_sauvegarde_avant_affichage(self):
        invention = "Une seconde cloche est cachée sous le plancher."
        corrige = "Tu te trouves dans : Refuge du relais."
        sorties = [dialogue(invention), segment("etabli", ["attestations"]),
                   dialogue(corrige), segment("etabli", ["attestations"])]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties) as appel,
                  patch("builtins.input", side_effect=["mj Que vois-je ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--defi", "--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertEqual(appel.call_count, 4)
        self.assertNotIn(invention, sortie.getvalue())
        self.assertIn(corrige, sortie.getvalue())
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], corrige)
        self.assertEqual(len([o for o in reprise.objets.values() if o["type"] == "tresor" and "cloche" in o["nom"]]), 1)
        self.assertEqual(reprise.data["objectif_partie"]["objet"], "cloche")

    def test_deux_propositions_rejetees_ne_creent_pas_un_echec_fictif(self):
        from donjon.moteur import proposition
        invalide = {"mode": "action", "texte": "", "faits": [],
                    "proposition": proposition("prendre", "objet_inexistant")}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", side_effect=[invalide, invalide,
                                                               ErreurMonde("narration indisponible")]),
                  patch("builtins.input", side_effect=["mj je prends la clé", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("Corvus n'a rien tenté", sortie.getvalue())
        self.assertNotIn("Ce geste n'est pas possible", sortie.getvalue())
        self.assertEqual(reprise.data["revision"], 0)
        self.assertFalse(reprise.data["journal"])
        self.assertEqual(reprise.data["narrations_mj"][-1]["sources"], ["moteur"])

    def test_explication_finale_ne_peut_pas_devenir_une_troisieme_action(self):
        from donjon.moteur import proposition
        invalide = {"mode": "action", "texte": "", "faits": [],
                    "proposition": proposition("prendre", "objet_inexistant")}
        action = {"mode": "action", "texte": "", "faits": [],
                  "proposition": proposition("observer", "scene")}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", side_effect=[invalide, invalide, action]),
                  patch("builtins.input", side_effect=["mj je prends la clé", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("Corvus n'a rien tenté", sortie.getvalue())
        self.assertFalse(reprise.data["journal"])
        self.assertEqual(reprise.data["revision"], 0)

    def test_dialogue_sans_controle_refuse_avant_affichage(self):
        phrase = "Une seconde cloche est sous le plancher."
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "echanger", return_value=dialogue(phrase)),
                  patch("builtins.input", side_effect=["mj Que vois-je ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertNotIn(phrase, sortie.getvalue())
        self.assertFalse(reprise.data.get("narrations_mj"))

    def test_avis_sans_action_passe_par_le_controle_et_la_sauvegarde(self):
        from donjon.moteur import proposition
        phrase = "Tu te trouves dans : Antichambre."
        avis = {"mode": "action", "texte": "", "faits": ["attestations"],
                "proposition": proposition("clarifier", justification=phrase)}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      avis, segment("etabli", ["attestations"])]),
                  patch("builtins.input", side_effect=["mj Où suis-je ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(phrase, sortie.getvalue())
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], phrase)
        self.assertFalse(reprise.data["journal"])

    def test_obstacles_expliques_apres_deux_refus_sans_action_fictive(self):
        from donjon.operations import etape, sequence
        from donjon.moteur import proposition
        from donjon.spatial import installer
        monde = nouveau_defi()
        installer(monde)
        for id in ("torche", "lanterne"):
            monde.objets[id].update(allume=False, combustible=0)
        explication = ("Il ne fait pas entièrement noir : une pénombre permet de distinguer les objets, "
                       "mais pas de lire les inscriptions. La torche n'a plus de combustible.")
        sorties = [
            {"mode": "action", "texte": "", "faits": [], "proposition": proposition("lire", "gravure")},
            {"mode": "action", "texte": "", "faits": [],
             "proposition": sequence(etape("allumer", "torche", outil="briquet"))},
            dialogue(explication),
            {"segments": [{"indice": i, "verdict": "etabli", "sources": ["attestations"],
                           "locuteur": "", "citation": "", "motif": ""} for i in range(2)]},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            monde.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties),
                  patch("builtins.input", side_effect=["je lis la consigne", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--defi", "--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(explication, sortie.getvalue())
        self.assertFalse(reprise.data["journal"])
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], explication)

    def test_refus_repetes_ne_montrent_aucune_invention(self):
        invention = "Une seconde cloche est cachée sous le plancher."
        sorties = [item for _ in range(3) for item in
                   (dialogue(invention), segment("nouveau", motif="Fait absent du monde."))]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties),
                  patch("builtins.input", side_effect=["mj Que vois-je ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertNotIn(invention, sortie.getvalue())
        self.assertNotIn("Le MJ n'a pas pu formuler", sortie.getvalue())
        self.assertEqual(reprise.data["narrations_mj"][-1]["sources"], ["moteur"])
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"],
                         "Je ne peux pas encore répondre avec certitude.")
        self.assertIn(reprise.data["narrations_mj"][-1]["texte"], sortie.getvalue())

    def test_avis_d_action_libre_ne_devient_pas_un_fait_affiche(self):
        from donjon.moteur import proposition
        invention = "Une seconde cloche est sous le plancher."
        reponse = {"mode": "action", "texte": "", "faits": [],
                   "proposition": proposition("observer", "scene", justification=invention)}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", return_value=reponse),
                  patch("builtins.input", side_effect=["mj je regarde", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertNotIn(invention, sortie.getvalue())
        self.assertNotIn(invention, str(reprise.data["conversation"]))
        self.assertNotIn(invention, str(reprise.data["journal"]))
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_intention_improvisee_libre_sans_effet_est_refusee(self):
        invention = "Une seconde cloche apparaît sous le plancher."
        reponse = {"mode": "action", "texte": "", "faits": [],
                   "proposition": improviser(invention, issue("Elle résonne.", []))}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", return_value=reponse),
                  patch("builtins.input", side_effect=["mj je tape des mains", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("Corvus n'a rien tenté", sortie.getvalue())
        self.assertEqual(reprise.data["revision"], 0)
        self.assertFalse(reprise.data.get("gestes_improvises"))
        self.assertNotIn(invention, sortie.getvalue())
        self.assertNotIn(invention, str(reprise.data["conversation"]))
        self.assertNotIn(invention, str(reprise.data.get("gestes_improvises", [])))
        self.assertNotIn(invention, str(reprise.data["journal"]))
        self.assertNotIn(invention, str(reprise.data["arbitrages"]))
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_brouillons_d_un_geste_sonore_ne_reviennent_pas_dans_le_contexte(self):
        from donjon.improvisation import contexte as contexte_improvisation
        invention = "Une seconde cloche apparaît sous le plancher."
        recit = "Elle sonne sous les pieds de Corvus."
        monde = nouveau_monde()
        monde.joueur["salle"] = "echoppe"
        p = improviser(invention, issue(recit, [effet("son", "joueur",
            texte="corps_rythmique", valeur=1)]), bruit=1)
        reponse = {"mode": "action", "texte": "", "faits": [], "proposition": p}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            monde.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=lambda *args: (
                      {"conforme": True, "motif": ""} if args[3] == "auditer_action" else reponse)),
                  patch("builtins.input", side_effect=["mj je tape des mains", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("geste d'expression", sortie.getvalue())
        self.assertIn("rythme avec ton corps", sortie.getvalue())
        self.assertTrue(reprise.data["sons"][-1]["auditeurs"])
        self.assertEqual(reprise.data["sons"][-1]["forme"], "corps_rythmique")
        self.assertNotIn("intention", reprise.objets["marchand"]["dernier_son_entendu"])
        for texte in (sortie.getvalue(), str(reprise.data["gestes_improvises"]),
                      str(reprise.data["sons"]), str(reprise.data["journal"]),
                      str(reprise.data["arbitrages"]), str(reprise.contexte()),
                      str(contexte_improvisation(reprise))):
            self.assertNotIn(invention, texte)
            self.assertNotIn(recit, texte)

    def test_brouillons_d_une_tentative_risquee_ne_restent_pas_dans_l_arbitrage(self):
        invention = "Une seconde cloche surgit derrière la porte."
        recit = "Une cloche chante dans la pierre."
        p = improviser(invention, issue(recit), issue("La cloche se brise."),
                       approche="adresse", stat="DEX", difficulte=12)
        reponse = {"mode": "action", "texte": "", "faits": [], "proposition": p}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=lambda *args: (
                      {"conforme": True, "motif": ""} if args[3] == "auditer_action" else reponse)),
                  patch("builtins.input", side_effect=["mj je tente un geste", "tenter", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("Geste d'adresse", sortie.getvalue())
        self.assertTrue(reprise.data["arbitrages"])
        self.assertTrue(reprise.data["journal"])
        for texte in (sortie.getvalue(), str(reprise.data), str(reprise.contexte())):
            self.assertNotIn(invention, texte)
            self.assertNotIn(recit, texte)
            self.assertNotIn("La cloche se brise.", texte)

    def test_parole_attribuee_devient_un_evenement_entendu_apres_rechargement(self):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        citation = "La seconde cloche est sous le plancher."
        texte = "Gorm dit : « " + citation + " »."
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      dialogue(texte), segment("parole", locuteur="marchand", citation=citation)]),
                  patch("builtins.input", side_effect=["mj Gorm, salut.", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("Gorm le marchand dit : « " + citation + " ».", sortie.getvalue())
        self.assertEqual(reprise.data["paroles_pnj"][-1]["texte"], citation)
        self.assertIn("joueur", reprise.data["paroles_pnj"][-1]["auditeurs"])
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_audit_de_parole_mal_forme_est_revise_avant_affichage(self):
        monde = nouveau_monde()
        monde.joueur["salle"] = "echoppe"
        citation = "La cloche se trouve sous le plancher."
        texte = "Gorm dit : « " + citation + " »."
        sorties = [dialogue(texte), segment("parole", locuteur="objet_inconnu", citation=citation),
                   dialogue(texte), segment("parole", locuteur="marchand", citation=citation)]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            monde.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties) as appel,
                  patch("builtins.input", side_effect=["mj Gorm, où est la cloche ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertEqual(appel.call_count, 4)
        self.assertEqual(sortie.getvalue().count("Gorm le marchand dit : « " + citation), 1)
        self.assertEqual(len(reprise.data["paroles_pnj"]), 1)
        self.assertEqual(reprise.data["paroles_pnj"][0]["texte"], citation)
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_recit_libre_d_improvisation_ne_cree_pas_de_fait(self):
        monde = nouveau_monde()
        p = improviser("je chante", issue("Une cloche surgit.", []))
        resultat = Moteur(monde).executer(Moteur(monde).preparer(p))
        self.assertNotIn("Une cloche surgit", resultat)
        self.assertIn("geste d'expression", resultat)
        self.assertNotIn("je chante", resultat)
        self.assertEqual(len([o for o in monde.objets.values() if "cloche" in o["nom"]]), 0)


if __name__ == "__main__":
    unittest.main()
