"""Une parole sans conteste reste une parole ; un repli du contrôle narratif reste utile.

Cas réels : « pousse toi ça prend trop de temps » finissait sur « Je ne peux pas encore répondre
avec certitude. » quand les trois réponses de Luna étaient refusées ; « Aubin, viens m'aider à
porter l'échelle » (Aubin derrière le pilier) finissait en dix appels. Une saisie qui commence par
des guillemets, par un verbe de parole (« je dis… », « je demande à Gorm… ») ou par « à tous » est
une parole : le moteur la fait entendre, et la prononce lui-même si le MJ s'obstine à la raconter ou
à en faire un geste. Une interpellation sans guillemets (« Aubin, … ») reste du texte libre pour le
MJ ; s'il en fait une parole, le moteur en fixe le destinataire. Quand aucune réponse n'est admise,
le joueur lit ce que le moteur a établi, les phrases admises de la réponse, ou ce que Corvus perçoit
de ce qu'il vise et ce qui manque. Chaque cas vérifie ce que lit le joueur et l'état après
rechargement."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.esprits import lire
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import proposition
from tests.test_parole_commune import paroles_retenues, scene
from tests.test_tensions import recharger


def dialogue(texte):
    return {"mode": "dialogue", "texte": texte, "faits": [], "proposition": None}


def parole(replique, *contenu, personnage):
    return {"mode": "parole_joueur", "texte": "", "faits": [],
            "proposition": {"personnage": personnage, "replique": replique,
                            "contenu": [dict(zip(("type", "sujet", "attribut", "valeur"), c)) for c in contenu]}}


def verdicts(*lignes):
    """Un rapport d'audit : une ligne (verdict, sources, motif) par segment."""
    return {"segments": {str(i): {"portee_mecanique": "aucune", "verdict": v, "sources": list(s), "locuteur": "", "citation": "",
                                  "entites": [], "comptes": [], "motif": m} for i, (v, s, m) in enumerate(lignes)}}


NEUTRE = ("neutre", (), "")


def jouer(monde, saisie, reponses, audits, jet=20, options=()):
    """Une saisie dans la vraie boucle de jeu, le fournisseur simulé appel par appel : ``reponses``
    pour le MJ, ``audits`` pour l'auditeur narratif ; la contre-revue d'une action est conforme."""
    reponses, audits, appels = list(reponses), list(audits), []

    def appel(instructions, entree, intention, fonction, schema):
        appels.append((fonction, entree))
        if fonction == "auditer_action":
            if "contenu_conforme" in schema["properties"]:
                from donjon.paroles import operations_contenu
                return {"contenu_conforme": True, "motif": "", "perimetre": "sens",
                        "operations_demandees": sorted(operations_contenu(entree["plan"]["parole"]["contenu"]))}
            return {"conforme": True, "motif": ""}
        return (audits if fonction == "auditer_narration" else reponses).pop(0)
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_appeler_brut", side_effect=appel),
              patch.object(Monde, "d20", return_value=jet),
              patch("builtins.input", side_effect=[saisie, "quitter"]),
              patch("sys.stdout", io.StringIO()) as sortie):
            assert jeu.main(["--console", "--connexion", "api", "--save", str(chemin), *options]) == 0
        return Monde.charger(chemin), sortie.getvalue(), appels


def mj(appels):
    return [entree for fonction, entree in appels if fonction == "repondre_au_joueur"]


class ParoleExpliciteTests(unittest.TestCase):
    def test_le_mj_raconte_une_parole_explicite_le_moteur_la_prononce(self):
        m = scene()
        saisie, mots = "je dis à Aubin : viens m'aider à porter l'échelle", "viens m'aider à porter l'échelle"
        reprise, sortie, appels = jouer(m, saisie, [
            dialogue("Tu appelles Aubin et lui demandes son aide."),
            dialogue("Tu demandes à Aubin de t'aider à porter l'échelle."),
            dialogue("Aubin hoche la tête.")], [verdicts(NEUTRE)] * 3)
        # La première réponse en dialogue est renvoyée au MJ avec ce qu'attend le moteur.
        self.assertIn("parole_joueur", mj(appels)[1]["faits"]["retour_moteur"]["attendu"])
        self.assertEqual(mj(appels)[0]["faits"]["parole_prevue"]["personnage"], "aubin")
        # Le MJ s'obstine : le moteur prononce les mots du joueur, et Aubin répond.
        self.assertIn(f"Tu dis à Aubin : « {mots} »", sortie)
        self.assertIn("Aubin hoche la tête.", sortie)
        self.assertNotIn("Tu appelles Aubin", sortie)
        self.assertNotIn("Tu demandes à Aubin", sortie)
        # Après rechargement : Aubin a reçu la parole, Ilse l'a entendue sans qu'elle lui soit adressée.
        self.assertEqual(paroles_retenues(reprise, "aubin")[-1], ("joueur", ["aubin"], mots))
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1], ("joueur", ["aubin"], mots))
        self.assertEqual(reprise.data["conversation"][-1]["nature"], "parole_joueur")

    def test_un_geste_propose_pour_une_parole_explicite_laisse_parler_le_moteur(self):
        m = scene()
        saisie = "« Aubin, aide-moi à porter l'échelle »"
        attendre = {"mode": "action", "texte": "", "faits": [], "proposition": proposition("attendre", "")}
        reprise, sortie, appels = jouer(m, saisie, [attendre, attendre, dialogue("Aubin te regarde.")],
                                        [verdicts(NEUTRE)])
        self.assertIn("le geste annoncé attend que le joueur le fasse",
                      mj(appels)[1]["faits"]["retour_moteur"]["attendu"])
        self.assertIn("Tu dis à Aubin : « Aubin, aide-moi à porter l'échelle »", sortie)
        self.assertEqual(paroles_retenues(reprise, "aubin")[-1][1], ["aubin"])
        self.assertFalse(reprise.data["journal"])  # Aucun geste n'a eu lieu.

    def test_sans_mots_le_moteur_ne_les_invente_pas(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "je demande à Ilse de m'aider à déplacer les planches", [
            dialogue("Tu demandes son aide à Ilse."), dialogue("Tu demandes son aide à Ilse.")],
            [verdicts(NEUTRE)] * 2)
        self.assertIn("Dis ce que Corvus dit à Ilse, entre guillemets ou après un deux-points.", sortie)
        self.assertNotIn("Tu demandes son aide", sortie)
        self.assertEqual(reprise.data.get("paroles_joueur", []), [])
        self.assertEqual(paroles_retenues(reprise, "ilse"), [])


class InterpellationTests(unittest.TestCase):
    """Sans guillemets ni verbe de parole, une interpellation est du texte libre pour le MJ."""

    def test_le_mj_peut_repondre_sans_parole(self):
        # Aubin l'entendrait : un premier dialogue est renvoyé une fois (rien n'est encore dit,
        # branche mj-restes) ; s'il revient, contrôlé, il s'affiche.
        m = scene()
        reprise, sortie, appels = jouer(m, "Aubin, viens m'aider à porter l'échelle",
                                        [dialogue("Aubin est à quelques pas.")] * 2, [verdicts(NEUTRE)])
        self.assertEqual(len(mj(appels)), 2)
        self.assertNotIn("retour_moteur", mj(appels)[0]["faits"])
        self.assertEqual(mj(appels)[1]["faits"]["retour_moteur"]["obstacle"], "Rien n'a encore été dit à Aubin.")
        self.assertIn("Aubin est à quelques pas.", sortie)
        self.assertEqual(reprise.data.get("paroles_joueur", []), [])

    def test_s_il_en_fait_une_parole_le_moteur_fixe_le_destinataire_et_garde_les_mots(self):
        m = scene()
        saisie = "Ilse, tu peux m'aider à déplacer les planches ?"
        reprise, sortie, appels = jouer(m, saisie, [
            parole("Tu peux m'aider ?", ("propos", "", "", ""), personnage="aubin"),
            parole("Tu peux m'aider ?", ("propos", "", "", ""), personnage="ilse"),
            dialogue("Ilse hésite.")], [verdicts(NEUTRE)])
        self.assertIn("personnage = ilse", mj(appels)[1]["faits"]["retour_moteur"]["attendu"])
        self.assertIn(f"Tu dis à Ilse : « {saisie} »", sortie)
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1], ("joueur", ["ilse"], saisie))

    def test_celui_qu_on_ne_voit_pas(self):
        # La sauvegarde réelle : Ilse et Aubin derrière le pilier, Corvus tourné vers eux.
        m = scene(ilse=(5, 2), aubin=(5, 3), brune=(0, 3))
        m.joueur.update(position=[2, 3], orientation="est")
        m.data["connus"].extend(["aubin", "ilse"])
        m = recharger(m)
        manque = "Tu ne vois pas Aubin d'ici : approche-toi pour lui parler."
        # Une parole explicite : le moteur le dit sans appel.
        reprise, sortie, appels = jouer(m, "je dis à Aubin : viens m'aider à porter l'échelle", [], [])
        self.assertEqual(appels, [])
        self.assertIn(manque, sortie)
        self.assertEqual(reprise.data["conversation"], m.data["conversation"])
        # L'adresse nommée garde le même accès, même sans verbe de parole explicite.
        reprise, sortie, appels = jouer(m, "Aubin, viens m'aider à porter l'échelle", [], [])
        self.assertEqual(appels, [])
        self.assertIn(manque, sortie)
        self.assertEqual(reprise.data["conversation"], m.data["conversation"])
        self.assertEqual(reprise.data.get("paroles_joueur", []), [])


class ReplisTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        self.m.joueur["salle"] = "echoppe"

    def test_les_phrases_admises_restent_et_chaque_relance_voit_tous_les_refus(self):
        inventions = ["Une seconde cloche est cachée sous le plancher.",
                      "Un passage s'ouvre derrière le brasero.",
                      "Une trappe dort sous tes pieds."]
        admise = "Le brasero est allumé."
        refus = ("invention_protegee", (), "Élément absent des faits.")
        reprise, sortie, appels = jouer(
            self.m, "mj qu'y a-t-il autour du brasero ?",
            [dialogue(admise + " " + i) for i in inventions],
            [verdicts(("mecanique", ("objet:brasero",), ""), refus)] * 3)
        # La troisième réponse est demandée avec les phrases refusées des deux premières.
        refusees = [o["texte"] for o in mj(appels)[2]["controle_narratif"]]
        self.assertTrue(any(inventions[0] in t for t in refusees))
        self.assertTrue(any(inventions[1] in t for t in refusees))
        # Aucune réponse entière n'est admise : le joueur lit la phrase admise, rien d'inventé.
        self.assertIn(admise, sortie)
        for i in inventions:
            self.assertNotIn(i, sortie)
        self.assertNotIn("Je ne peux pas encore", sortie)
        self.assertEqual(reprise.data["narrations_mj"][-1], {"texte": admise, "revision": 0,
                                                              "sources": ["objet:brasero"]})

    def test_sans_phrase_admise_le_moteur_dit_ce_que_corvus_percoit_et_ce_qui_manque(self):
        refus = verdicts(("invention_protegee", (), "Chaleur non établie."))
        reprise, sortie, _ = jouer(self.m, "mj le brasero, il chauffe à quel point ?",
                                   [dialogue("Le brasero ferait fondre du fer.")] * 3, [refus] * 3)
        attendu = ("Le brasero éclaire la pièce. Un brasero en fer est allumé. Ce que tu perçois et ce que tu "
                   "sais n'en disent pas davantage.")
        self.assertIn(attendu, sortie)
        self.assertNotIn("fondre", sortie)
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], attendu)
        self.assertEqual(reprise.data["narrations_mj"][-1]["sources"], ["moteur"])

    def test_cas_reel_pousse_toi_l_issue_du_moteur_plutot_qu_un_repli_vide(self):
        # Brune au contact ; les trois réponses lui font promettre de bouger sans que le moteur l'ait prévu.
        m = scene(brune=(2, 3))
        saisie = "Brune, pousse-toi, ça prend trop de temps"
        promesse = dialogue("Brune soupire : « Je vais me pousser. »")
        engagement = {"segments": {"0": {"portee_mecanique": "aucune", "verdict": "engagement", "sources": [], "locuteur": "brune",
                                         "citation": "Je vais me pousser.", "entites": [], "comptes": [], "motif": ""}}}
        reprise, sortie, appels = jouer(m, saisie, [parole(saisie, ("passage", "", "", ""), personnage="brune"),
                                                    promesse, promesse, promesse], [engagement] * 3)
        validee = mj(appels)[1]["faits"]["conversation_validee"]
        self.assertTrue(validee["faits"])
        self.assertIn(f"Tu dis à Brune : « {saisie} »", sortie)
        self.assertIn(" ".join(validee["faits"]), sortie)
        self.assertNotIn("Je vais me pousser", sortie)
        self.assertNotIn("Je ne peux pas encore", sortie)
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], " ".join(validee["faits"]))
        self.assertEqual(paroles_retenues(reprise, "brune")[-1], ("joueur", ["brune"], saisie))

    def test_une_parole_sans_issue_ni_phrase_admise(self):
        m = scene()
        saisie = "Ilse, il fait froid ce soir"
        refus = verdicts(("contradictoire", ("perception",), "Contraire aux faits."))
        reprise, sortie, _ = jouer(m, saisie, [parole(saisie, ("propos", "", "", ""), personnage="ilse"),
                                               *[dialogue("Ilse s'envole.")] * 3], [refus] * 3)
        self.assertIn("Ilse t'a entendu, sans te répondre.", sortie)
        self.assertNotIn("s'envole", sortie)
        self.assertEqual(reprise.data["narrations_mj"][-1]["sources"], ["moteur"])
        self.assertEqual(lire(reprise, "ilse")["memoire"][-1]["texte"], saisie)


if __name__ == "__main__":
    unittest.main()
