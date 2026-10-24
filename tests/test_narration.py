from tests.support import presentes
import json
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
from donjon.esprits import dernier_son


def dialogue(texte):
    return {"mode": "dialogue", "texte": texte, "faits": [], "proposition": None}


def segment(verdict, sources=(), locuteur="", citation="", motif="", entites=()):
    return {"segments": [{"portee_mecanique": "aucune", "indice": 0, "verdict": verdict, "sources": list(sources),
                           "locuteur": locuteur, "citation": citation, "entites": list(entites),
                           "motif": motif}]}


class NarrationTests(unittest.TestCase):
    def test_couverture_et_references_du_controle(self):
        texte = "La porte est fermée. Une cloche apparaît."
        with self.assertRaises(ErreurMonde):
            controler(texte, segment("mecanique", ["salle"]), {"salle": {}})
        rapport = controler("La porte est fermée.", segment("mecanique", ["source_inventee"]), {"salle": {}})
        self.assertTrue(rapport["obstacles"])
        self.assertEqual(rapport["segments"][0]["sources"], [])

    def test_schema_d_audit_limite_les_sources_aux_cles_fournies(self):
        from donjon.narration import schema_audit
        schema = schema_audit({"salle": {}, "objet:cloche": {}}, 2)
        segments = schema["properties"]["segments"]
        # Une entrée obligatoire par segment, sous la clé de son indice.
        self.assertEqual(segments["required"], ["0", "1"])
        sources = segments["properties"]["1"]["properties"]["sources"]["items"]
        self.assertEqual(sources["enum"], ["objet:cloche", "salle"])

    def test_rapport_par_cle_d_indice(self):
        from donjon.narration import AuditIllisible
        texte = "La porte est fermée. Une odeur de cire flotte."
        ligne = {"portee_mecanique": "aucune", "verdict": "ambiance", "sources": [], "locuteur": "", "citation": "", "entites": [], "motif": ""}
        rapport = controler(texte, {"segments": {"0": ligne, "1": ligne}}, {})
        self.assertEqual([l["indice"] for l in rapport["segments"]], [0, 1])
        # Un segment sauté ou ajouté rend le rapport illisible : une faute de l'auditeur.
        for cles in (["0"], ["0", "1", "2"], ["1", "2"]):
            with self.subTest(cles=cles), self.assertRaises(AuditIllisible):
                controler(texte, {"segments": {c: ligne for c in cles}}, {})

    def test_audit_illisible_redemande_avant_de_refuser_le_texte(self):
        texte = "Une odeur de cire flotte."
        illisible = {"segments": {}}
        lisible = {"segments": {"0": {"portee_mecanique": "aucune", "verdict": "ambiance", "sources": [], "locuteur": "", "citation": "",
                                      "entites": [], "motif": ""}}}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler_brut", side_effect=[dialogue(texte), illisible, lisible]) as appel:
            reponse = mj._appeler("instr", {"faits": {}, "conversation": [], "message": "je sens ?"},
                                  "je sens ?", "repondre_au_joueur", {})
        self.assertEqual(appel.call_count, 3)
        self.assertEqual(reponse["texte"], texte)

    def test_dialogue_vide_corrige_sans_audit(self):
        texte = "Une odeur de cire flotte."
        lisible = {"segments": {"0": {"portee_mecanique": "aucune", "verdict": "ambiance", "sources": [], "locuteur": "", "citation": "",
                                      "entites": [], "motif": ""}}}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler_brut", side_effect=[dialogue(""), dialogue(texte), lisible]) as appel:
            reponse = mj._appeler("instr", {"faits": {}, "conversation": [], "message": "je sens ?"},
                                  "je sens ?", "repondre_au_joueur", {})
        # Aucun audit du texte vide : la révision reçoit un motif qui dit quoi corriger.
        fonctions = [c.args[3] for c in appel.call_args_list]
        self.assertEqual(fonctions, ["repondre_au_joueur", "repondre_au_joueur", "auditer_narration"])
        self.assertIn("Le texte est vide", json.dumps(appel.call_args_list[1].args[1], ensure_ascii=False))
        self.assertEqual(reponse["texte"], texte)

    def test_une_reponse_auditee_avec_les_croyances_du_locuteur_s_enregistre(self):
        # Cas du banc Luna : Gorm nomme un lieu qu'il est seul à connaître ; l'audit l'acceptait
        # avec ses croyances, l'enregistrement le refusait sans elles.
        from donjon.defi import nouveau_defi
        from donjon import lexique
        from donjon.narration import consigner
        m = presentes(nouveau_defi(1985, "fixe"))
        m.joueur["salle"] = m.objets["marchand"]["lieu"]
        citation = "La cloche est dans la galerie de ronde."
        texte = f"Gorm répond : « {citation} »"
        faits = {"interlocuteurs": {"marchand": {"nom": "Gorm"}}}
        ligne = {"portee_mecanique": "aucune", "indice": 0, "verdict": "parole", "sources": [], "locuteur": "marchand", "citation": citation,
                 "entites": [], "motif": ""}
        reponse = {"texte": texte, "_audit": {"segments": [ligne], "faits": faits, "texte_initial": texte,
                                              "fondement": lexique.corpus("Gorm, la cloche"),
                                              "fondement_paroles": lexique.corpus("galerie de ronde")}}
        sans = {**reponse, "_audit": {**reponse["_audit"], "fondement_paroles": ""}}
        with self.assertRaisesRegex(ErreurMonde, "Aucun changement enregistré"):
            consigner(m, sans)
        consigner(m, reponse)
        self.assertEqual(m.data["paroles_pnj"][-1]["texte"], citation)
        # Une nouvelle attribution reste contrôlée, même si ces mots ont déjà été dits.
        with self.assertRaisesRegex(ErreurMonde, "Aucun changement enregistré"):
            consigner(m, sans)

    def test_voix_d_auteur_refusee_hors_citation(self):
        from donjon.narration import voix_auteur
        # Textes réels du banc Haiku : des notes internes affichées au joueur.
        for texte in ("Corvus doit d'abord s'en approcher avant tout coup. Aucune cible n'est engagée.",
                      "Le joueur doit d'abord le localiser sur place avant de le prendre.",
                      "Il faudrait t'approcher, et le moteur déterminera alors si Gorm la remarque."):
            with self.subTest(texte=texte):
                self.assertTrue(voix_auteur(texte))
        # La deuxième personne et une réplique citée restent libres.
        self.assertFalse(voix_auteur("Tu dois d'abord t'approcher de la poutre."))
        self.assertFalse(voix_auteur("Gorm répond : « Corvus, reviens demain. »"))

    def test_voix_d_auteur_renvoyee_en_revision(self):
        texte = "Une odeur de cire flotte."
        lisible = {"segments": {"0": {"portee_mecanique": "aucune", "verdict": "ambiance", "sources": [], "locuteur": "", "citation": "",
                                      "entites": [], "motif": ""}}}
        auteur = {"segments": {"0": {**lisible["segments"]["0"]}}}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler_brut", side_effect=[
                dialogue("Le joueur sent une odeur de cire."), auteur, dialogue(texte), lisible]) as appel:
            reponse = mj._appeler("instr", {"faits": {}, "conversation": [], "message": "je sens ?"},
                                  "je sens ?", "repondre_au_joueur", {})
        self.assertIn("deuxième personne", json.dumps(appel.call_args_list[2].args[1], ensure_ascii=False))
        self.assertEqual(reponse["texte"], texte)

    def test_mecanique_exige_une_source_et_invention_refusee(self):
        faits = {"objet:cloche": {"nom": "cloche"}}
        phrase = "La cloche est dans le beffroi."
        self.assertTrue(controler(phrase, segment("mecanique"), faits)["obstacles"])
        self.assertFalse(controler(phrase, segment("mecanique", ["objet:cloche"]), faits)["obstacles"])
        self.assertTrue(controler("Une seconde cloche est sous le plancher.",
                                  segment("invention_protegee", motif="Seconde cloche."), faits)["obstacles"])

    def test_texte_accepte_affiche_tel_quel(self):
        texte = "Prends ton temps. Une odeur de vase monte du sol. Peut-être que l'eau a reflué ici."
        rapport = {"segments": [
            {"portee_mecanique": "aucune", "indice": 0, "verdict": "neutre", "sources": [], "locuteur": "", "citation": "",
             "entites": [], "motif": ""},
            {"portee_mecanique": "aucune", "indice": 1, "verdict": "ambiance", "sources": [], "locuteur": "", "citation": "",
             "entites": ["odeur de vase"], "motif": ""},
            {"portee_mecanique": "aucune", "indice": 2, "verdict": "hypothese", "sources": [], "locuteur": "", "citation": "",
             "entites": [], "motif": ""}]}
        resultat = controler(texte, rapport, {})
        self.assertFalse(resultat["obstacles"])
        self.assertEqual(resultat["texte_controle"], texte)
        self.assertEqual(resultat["ambiances"], [{"texte": "Une odeur de vase monte du sol.",
                                                   "entites": ["odeur de vase"]}])

    def test_attribution_superflue_hors_parole_est_normalisee(self):
        phrase = "La cloche est dans le beffroi."
        faits = {"attestations": [phrase]}
        rapport = controler(phrase, segment("mecanique", ["attestations"],
                                            locuteur="marchand", citation="Une autre phrase."), faits)
        self.assertFalse(rapport["obstacles"])
        self.assertEqual(rapport["segments"][0]["locuteur"], "")
        self.assertFalse(rapport["paroles"])

    def test_dialogue_invente_est_revise_puis_sauvegarde_avant_affichage(self):
        invention = "Une seconde cloche est cachée sous le plancher."
        corrige = "Tu te trouves dans : Refuge du relais."
        sorties = [dialogue(invention), segment("invention_protegee", motif="Aucune seconde cloche."),
                   dialogue(corrige), segment("mecanique", ["attestations"])]
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
        # Sans explication du MJ, le joueur lit le refus du monde (branche relances-luna), jamais un échec.
        self.assertIn("Tu ne vois rien de tel ici.", sortie.getvalue())
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
        self.assertIn("Tu ne vois rien de tel ici.", sortie.getvalue())
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
                      avis, segment("mecanique", ["attestations"])]),
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
        monde = nouveau_defi(depart="fixe")
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
            {"segments": [{"portee_mecanique": "aucune", "indice": i, "verdict": "mecanique", "sources": ["attestations"],
                           "locuteur": "", "citation": "", "entites": [], "motif": ""} for i in range(2)]},
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
                   (dialogue(invention), segment("invention_protegee", motif="Fait absent du monde."))]
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
        # Le repli dit ce qui manque, sans rien inventer.
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"],
                         "Rien de ce que tu perçois ou sais ne permet d'y répondre avec certitude. "
                         "Précise ce que tu veux regarder, examiner ou tenter.")
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

    def test_intention_improvisee_libre_n_etablit_rien(self):
        # Un geste sans effet est permis ; son brouillon libre n'établit rien :
        # le libellé affiché et enregistré vient des seuls champs structurés.
        invention = "Une seconde cloche apparaît sous le plancher."
        reponse = {"mode": "action", "texte": "", "faits": [],
                   "proposition": improviser(invention, issue("Elle résonne.", []))}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=lambda *a: (
                      {"conforme": True, "motif": ""} if a[3] == "auditer_action" else reponse)),
                  patch("builtins.input", side_effect=["mj je tape des mains", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("Tu réalises ce geste.", sortie.getvalue())
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
        monde = presentes(nouveau_monde())
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
        self.assertIn("geste", sortie.getvalue())
        self.assertIn("rythme avec ton corps", sortie.getvalue())
        self.assertTrue(reprise.data["sons"][-1]["auditeurs"])
        self.assertEqual(reprise.data["sons"][-1]["forme"], "corps_rythmique")
        # Gorm le voit faire : il n'en garde aucun bruit (``ouie``), et rien d'inventé.
        self.assertNotIn("intention", dernier_son(reprise, "marchand") or {})
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
        self.assertIn("Geste", sortie.getvalue())
        self.assertTrue(reprise.data["arbitrages"])
        self.assertTrue(reprise.data["journal"])
        for texte in (sortie.getvalue(), str(reprise.data), str(reprise.contexte())):
            self.assertNotIn(invention, texte)
            self.assertNotIn(recit, texte)
            self.assertNotIn("La cloche se brise.", texte)

    def test_parole_attribuee_devient_un_evenement_entendu_apres_rechargement(self):
        m = presentes(nouveau_monde())
        m.joueur["salle"] = "echoppe"
        citation = "La seconde cloche est sous le plancher."
        texte = "Gorm dit : « " + citation + " »."
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      dialogue(texte), segment("parole", locuteur="marchand", citation=citation)]),
                  patch("builtins.input", side_effect=["mj je regarde Gorm.", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(texte, sortie.getvalue())
        self.assertEqual(reprise.data["paroles_pnj"][-1]["texte"], citation)
        self.assertIn("joueur", reprise.data["paroles_pnj"][-1]["auditeurs"])
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_une_citation_recopiee_avec_ses_guillemets_reste_la_parole(self):
        """Banc Luna : « D'accord, vas-y », te répond-elle ; l'auditeur citait « « D'accord, vas-y » »
        et le contrôle refusait la parole deux fois, jusqu'au repli. La parole retenue est le texte
        entre les guillemets."""
        m = presentes(nouveau_monde())
        m.joueur["salle"] = "echoppe"
        citation = "D’accord, je te laisse la place."
        texte = "« " + citation + " », te répond Gorm."
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      dialogue(texte), segment("parole", locuteur="marchand", citation="« " + citation + " »")]),
                  patch("builtins.input", side_effect=["mj je regarde Gorm.", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(texte, sortie.getvalue())
        self.assertEqual(reprise.data["paroles_pnj"][-1]["texte"], citation)

    def test_parole_longue_d_un_pnj_sauvegardee_et_rechargee(self):
        # Cas réel du banc : une réponse de Gorm de plus de 240 caractères faisait échouer la sauvegarde.
        m = presentes(nouveau_monde())
        m.joueur["salle"] = "echoppe"
        citation = ("Je connais la porte de chêne au nord de l'antichambre. Des crochets permettent d'en "
                    "tenter le crochetage, sans garantie ; ses axes, eux, se retirent avec un bon levier. "
                    "Je n'y suis pas entré depuis longtemps, et je ne sais pas ce que le veilleur y a laissé.")
        self.assertGreater(len(citation), 240)
        texte = "Gorm répond d'une voix grave : « " + citation + " »"
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      dialogue(texte), segment("parole", locuteur="marchand", citation=citation)]),
                  patch("builtins.input", side_effect=["mj que fait Gorm ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(texte, sortie.getvalue())
        self.assertNotIn("invalide", sortie.getvalue())
        self.assertEqual(reprise.data["paroles_pnj"][-1]["texte"], citation)

    def test_audit_de_parole_mal_forme_est_revise_avant_affichage(self):
        monde = presentes(nouveau_monde())
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
                  patch("builtins.input", side_effect=["mj et Gorm ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertEqual(appel.call_count, 4)
        self.assertEqual(sortie.getvalue().count(texte), 1)
        self.assertEqual(len(reprise.data["paroles_pnj"]), 1)
        self.assertEqual(reprise.data["paroles_pnj"][0]["texte"], citation)
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_ambiance_affichee_enregistree_et_reprise_apres_rechargement(self):
        # Cas réel du banc de référence : « ça sent quoi, ici ? » finissait en repli.
        texte = "L'air est humide et sent la vase. Une odeur de pierre mouillée flotte autour de toi."
        rapport = {"segments": [
            {"portee_mecanique": "aucune", "indice": i, "verdict": "ambiance", "sources": [], "locuteur": "", "citation": "",
             "entites": [e], "motif": ""} for i, e in enumerate(("odeur de vase", "pierre mouillée"))]}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[dialogue(texte), rapport]),
                  patch("builtins.input", side_effect=["ça sent quoi, ici ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--defi", "--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn(texte, sortie.getvalue())
        self.assertNotIn("Je ne peux pas encore", sortie.getvalue())
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], texte)
        self.assertEqual([a["entites"] for a in reprise.contexte()["ambiance_etablie"]],
                         [["odeur de vase"], ["pierre mouillée"]])
        self.assertEqual(set(reprise.objets), set(nouveau_defi(depart="fixe").objets))

    def test_ambiance_d_un_autre_lieu_n_est_pas_fournie(self):
        m = presentes(nouveau_monde())
        m.data["ambiances"] = {"echoppe": [{"texte": "Ça sent le fer.", "entites": ["fer"], "revision": 0}]}
        m.verifier()
        self.assertEqual(m.contexte()["ambiance_etablie"], [])
        m.joueur["salle"] = "echoppe"
        self.assertEqual(m.contexte()["ambiance_etablie"], [{"texte": "Ça sent le fer.", "entites": ["fer"]}])

    def test_nom_d_entite_cachee_refuse_meme_si_l_auditeur_le_laisse_passer(self):
        # Le marteau est dans l'échoppe, hors de vue depuis l'antichambre.
        fuite = "Un marteau traîne contre le mur."
        corrige = "La pierre est froide sous tes doigts."
        sorties = [dialogue(fuite), segment("ambiance", entites=["marteau"]),
                   dialogue(corrige), segment("ambiance", entites=["pierre froide"])]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties) as appel,
                  patch("builtins.input", side_effect=["mj je tâte le mur", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertEqual(appel.call_count, 4)
        self.assertIn("marteau", str(appel.call_args_list[2].args[1]["controle_narratif"]))
        self.assertNotIn(fuite, sortie.getvalue())
        self.assertIn(corrige, sortie.getvalue())
        self.assertNotIn(fuite, str(reprise.data))
        self.assertNotIn("marteau", str(reprise.data.get("ambiances", {})))

    def test_nom_cite_par_le_joueur_reste_fonde(self):
        texte = "Tu ne vois aucun marteau ici."
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      dialogue(texte), segment("mecanique", ["perception"])]),
                  patch("builtins.input", side_effect=["y a-t-il un marteau ici ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
        self.assertIn(texte, sortie.getvalue())

    def test_recit_libre_d_improvisation_ne_cree_pas_de_fait(self):
        monde = presentes(nouveau_monde())
        p = improviser("je chante", issue("Une cloche surgit.", []))
        resultat = Moteur(monde).executer(Moteur(monde).preparer(p))
        self.assertNotIn("Une cloche surgit", resultat)
        self.assertIn("geste", resultat)
        self.assertNotIn("je chante", resultat)
        self.assertEqual(len([o for o in monde.objets.values() if "cloche" in o["nom"]]), 0)


if __name__ == "__main__":
    unittest.main()
