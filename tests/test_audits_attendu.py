"""Les refus d'audit guident le MJ comme ceux du moteur : un ``attendu`` par refus.

Depuis `messages-refus`, un refus du moteur dit au MJ le champ fautif, la valeur reçue et ce qui serait
accepté. Les refus d'audit (contrôles déterministes de ``narration``, verdicts de l'auditeur narratif,
contre-revues de portée, de capacités et d'action) ne donnaient qu'un motif : la phrase entière, sans
dire laquelle, ni ce qui passerait. Chacun porte désormais ``attendu`` (``refus.audit``) : la partie et
le segment en cause, la phrase ou la valeur reçue citée telle qu'écrite, le verdict de l'auditeur s'il
vient de lui (donné pour un jugement, sans plus), et ce qui serait accepté. Une cause par refus. Le
joueur ne lit jamais ``attendu`` : un texte refusé n'est pas affiché.

Cas réels : « Tu demandes à Ilse de t'aider. « Pas maintenant », te répond-elle. » (bancs Luna,
``mj-restes``) ; « Je vais me pousser » de Brune (``don-et-promesses``) ; « les faits ne disent… »
(``narration-fidele``) ; la voix qui se disait Brune (``voix``) ; « Prise non demandée » de la
contre-revue (``contre-revue``). Chaque voie est vérifiée sur un autre cas de même nature, et les
chaînes complètes après rechargement."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.coherence_physique import controler as controler_physique
from donjon.couverture_action import verifier as verifier_couverture
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.narration import controler, mentions, paroles_sans_moteur, voix_auteur, voix_inconnues
from donjon.portee_narrative import controler as controler_portee
from donjon.refus import audit_illisible
from tests.test_parole_commune import paroles_retenues, scene
from tests.test_repli_et_appel import NEUTRE, dialogue, mj, parole, verdicts

CHAMPS = {"partie", "segment", "texte", "motif", "attendu"}


def ligne(verdict, sources=(), motif="", locuteur="", citation="", entites=()):
    return {"verdict": verdict, "sources": list(sources), "locuteur": locuteur, "citation": citation,
            "entites": list(entites), "motif": motif}


def rapport(*lignes):
    return {"segments": {str(i): l for i, l in enumerate(lignes)}}


def jouer(monde, saisie, reponses, audits, revues=()):
    """La vraie boucle de jeu, le fournisseur simulé appel par appel (MJ, auditeur, contre-revue)."""
    reponses, audits, revues, appels = list(reponses), list(audits), list(revues), []

    def appel(instructions, entree, intention, fonction, schema):
        appels.append((fonction, entree))
        if fonction == "auditer_action":
            revue = revues.pop(0) if revues else {"conforme": True, "motif": ""}
            if "contenu_conforme" in schema["properties"] and "conforme" in revue:
                return {"contenu_conforme": revue["conforme"], "motif": revue["motif"]}
            return revue
        return (audits if fonction == "auditer_narration" else reponses).pop(0)
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_appeler_brut", side_effect=appel),
              patch.object(Monde, "d20", return_value=20),
              patch("builtins.input", side_effect=[saisie, "quitter"]),
              patch("sys.stdout", io.StringIO()) as sortie):
            assert jeu.main(["--console", "--connexion", "api", "--save", str(chemin)]) == 0
        return Monde.charger(chemin), sortie.getvalue(), appels


class Commun:
    def assertJamaisAffiche(self, sortie, refus):
        """Ni ``attendu`` ni ses marques ne parviennent au joueur."""
        for r in refus:
            self.assertNotIn(r["attendu"], sortie)
        for marque in ("accepté :", "selon l'auditeur", "reçu «"):
            self.assertNotIn(marque, sortie)


class DeterministesTests(unittest.TestCase):
    def test_voix_d_auteur_un_refus_par_mot_dans_son_segment(self):
        # Cas réel (narration-fidele) et un autre mot, dans un autre segment.
        texte = "Elle dispose déjà de 60 minutes de combustible ; les faits ne disent rien de plus. Corvus attend."
        refus = voix_auteur(texte)
        self.assertEqual([set(r) for r in refus], [CHAMPS] * 2)
        self.assertEqual([(r["segment"], r["texte"]) for r in refus],
                         [(0, "Elle dispose déjà de 60 minutes de combustible ; les faits ne disent rien de plus."),
                          (1, "Corvus attend.")])
        self.assertEqual(refus[0]["attendu"],
                         "texte, segment 0, reçu « les faits » ; accepté : le passage à la deuxième personne (tu), "
                         "dans la fiction, sans « les faits » hors d'une réplique entre guillemets : dis ce que Corvus "
                         "perçoit, sait ou ignore, sans parler du jeu")
        self.assertTrue(refus[1]["attendu"].startswith("texte, segment 1, reçu « Corvus » ;"))
        # La justification d'un avis est une autre partie, nommée comme telle.
        self.assertTrue(voix_auteur("Le joueur hésite.", "justification")[0]["attendu"]
                        .startswith("justification, segment 0, reçu « Le joueur » ;"))

    def test_nom_sans_fondement_cite_tel_qu_ecrit_sans_trahir_l_entite(self):
        m = nouveau_monde()
        # Le marteau est dans l'échoppe, hors de vue depuis l'antichambre (cas de test_narration).
        refus = mentions(m, "La torche fume. Un Marteau traîne contre le mur.", "torche")
        self.assertEqual(len(refus), 1)
        self.assertEqual((refus[0]["segment"], refus[0]["texte"]), (1, "Un Marteau traîne contre le mur."))
        self.assertEqual(refus[0]["attendu"],
                         "texte, segment 1, reçu « Marteau » ; accepté : le passage sans « Marteau » : ni ce que "
                         "Corvus perçoit ou sait, ni ce que croient les personnages présents ne le nomment")
        # Aucun identifiant de l'entité cachée n'est donné au MJ.
        self.assertNotIn(next(i for i, o in m.objets.items() if o["nom"].startswith("marteau")),
                         refus[0]["attendu"].replace("Marteau", ""))
        # Un nom que seul un personnage présent croit : sa réplique le peut, pas le récit.
        refus = mentions(m, "Un marteau traîne là.", "", paroles="le marteau de gorm")
        self.assertIn("seulement entre guillemets, dans la réplique d'un personnage présent", refus[0]["attendu"])

    def test_cas_reel_ilse_parole_racontee_et_reponse_sans_moteur(self):
        texte = "Tu demandes à Ilse de t'aider. « Pas maintenant », te répond-elle."
        refus = paroles_sans_moteur(texte, {"parole_prevue": {"personnage": "ilse"}}, adresse=True)
        self.assertEqual([(r["segment"], r["texte"]) for r in refus],
                         [(0, "Tu demandes à Ilse de t'aider."), (1, "« Pas maintenant », te répond-elle.")])
        self.assertEqual(refus[0]["attendu"],
                         "texte, segment 0, reçu « Tu demandes à Ilse » ; accepté : mode parole_joueur (personnage "
                         "= ilse) si Corvus parle, le moteur la fait entendre ; mode action s'il agit ; sinon un "
                         "récit où Corvus ne parle pas")
        self.assertEqual(refus[1]["attendu"],
                         "texte, segment 1, reçu « Pas maintenant » ; accepté : mode parole_joueur (personnage = "
                         "ilse) si Corvus parle (le personnage répondra ensuite) ; sinon le passage sans cette citation")

    def test_apres_un_refus_chaque_citation_nouvelle_est_un_refus(self):
        texte = "Tu ne peux pas l'ouvrir. « Non », grogne Gorm. « Jamais », ajoute Ilse."
        refus = paroles_sans_moteur(texte, {"retour_moteur": {"obstacle": "La porte est fermée."}})
        self.assertEqual([(r["segment"], r["attendu"].split(" ; ")[0]) for r in refus],
                         [(1, "texte, segment 1, reçu « Non »"), (2, "texte, segment 2, reçu « Jamais »")])
        self.assertIn("tu expliques toi-même l'obstacle de retour_moteur", refus[0]["attendu"])

    def test_voix_inconnue_le_recit_et_la_replique(self):
        from tests.test_voix import VoixInconnueTests
        m = VoixInconnueTests().gorm_dans_le_noir()
        nommee = {"interlocuteurs": {"voix_1": {"nom": "une voix qui se dit Brune", "voix_inconnue": True}}}
        # Cas réel (Luna) : « Brune répond tout près de toi ».
        texte = "Il fait noir. Brune répond tout près de toi : « Oui. »"
        refus = voix_inconnues(m, [], nommee, texte)
        self.assertEqual(len(refus), 1)
        self.assertEqual(refus[0]["segment"], 1)
        self.assertEqual(refus[0]["attendu"],
                         "texte, segment 1, reçu « Brune » ; accepté : dans le récit, cette voix (voix_1) se désigne "
                         "comme dans interlocuteurs.voix_1.nom, « une voix qui se dit Brune », jamais par « Brune » seul")
        # Cas réel (Luna) : la voix demandait « Tu dis t'appeler Corvus ? » sans qu'il se soit nommé.
        texte = "La voix hésite. « Tu dis t'appeler Corvus ? »"
        refus = voix_inconnues(m, [{"locuteur": "voix_1", "texte": "Tu dis t'appeler Corvus ?"}], nommee, texte)
        self.assertEqual((refus[0]["segment"], refus[0]["texte"]), (1, "« Tu dis t'appeler Corvus ? »"))
        self.assertTrue(refus[0]["attendu"].startswith("texte, segment 1, reçu « Corvus » ; accepté : une réplique "
                                                       "de voix_1 sans « Corvus »"))


class VerdictsTests(unittest.TestCase):
    """Le verdict d'un auditeur est un jugement : le moteur dit le segment, la phrase, la catégorie et le
    motif de l'auditeur tels quels, et ce qui passerait, sans prétendre davantage."""

    def test_cas_reel_brune_promet_de_se_pousser(self):
        texte = "Brune soupire : « Je vais me pousser. »"
        promesse = rapport(ligne("engagement", locuteur="brune", citation="Je vais me pousser."))
        refus = controler(texte, promesse, {"interlocuteurs": {"brune": {}}})["obstacles"]
        self.assertEqual(refus[0]["attendu"],
                         "texte, segment 0, reçu « Je vais me pousser. » ; selon l'auditeur (verdict engagement) ; "
                         "accepté : aucun engagement n'est prévu pour brune : une réponse sans promesse (répondre, "
                         "hésiter, refuser, se taire)")
        # Même nature : un engagement que le moteur prévoit ailleurs est cité mot pour mot.
        faits = {"interlocuteurs": {"brune": {}},
                 "esprits_interlocuteurs": {"brune": {"engagements": ["Brune s'écartera du seuil."]}}}
        refus = controler(texte, promesse, faits)["obstacles"]
        self.assertTrue(refus[0]["attendu"].endswith("accepté : seulement ce que le moteur a prévu pour brune : "
                                                     "« Brune s'écartera du seuil. » ; sinon une réponse sans promesse"))

    def test_invention_et_affirmation_sans_source(self):
        texte = "Le brasero est allumé. Une trappe dort sous tes pieds."
        refus = controler(texte, rapport(ligne("mecanique"), ligne("invention_protegee", motif="Trappe absente des faits.")),
                          {"objet:brasero": {"nom": "brasero en fer"}})["obstacles"]
        self.assertEqual(refus[0]["attendu"],
                         "texte, segment 0, reçu « Le brasero est allumé. » ; selon l'auditeur (verdict mecanique) ; "
                         "accepté : une affirmation que soutient un fait fourni, dite comme lui (clés qui nomment ce "
                         "qu'elle vise : objet:brasero), ou le passage sans elle")
        self.assertEqual(refus[1]["motif"], "Trappe absente des faits.")
        self.assertTrue(refus[1]["attendu"].startswith(
            "texte, segment 1, reçu « Une trappe dort sous tes pieds. » ; selon l'auditeur (verdict "
            "invention_protegee) : « Trappe absente des faits. » ; accepté : le passage sans cet élément"))

    def test_qui_peut_parler(self):
        texte = "« Va-t'en », lance Gorm."
        faits = {"interlocuteurs": {"ilse": {}, "brune": {}},
                 "conversation_validee": {"destinataires": ["ilse"], "faits": []}}
        absent = controler(texte, rapport(ligne("parole", locuteur="gorm", citation="Va-t'en")), faits)["obstacles"]
        self.assertIn("reçu « locuteur gorm »", absent[0]["attendu"])
        self.assertIn("un locuteur parmi les interlocuteurs présents (ilse, brune)", absent[0]["attendu"])
        texte = "« Va-t'en », lance Brune."
        temoin = controler(texte, rapport(ligne("parole", locuteur="brune", citation="Va-t'en")), faits)["obstacles"]
        self.assertTrue(temoin[0]["attendu"].endswith("accepté : une réponse de ilse seulement "
                                                      "(conversation_validee.repondent) ; brune se tait"))


class ContreRevuesTests(unittest.TestCase):
    def test_portee_une_cause_par_refus(self):
        entree = {"sujet": {"nature": "élément proposé sur un support", "support": "porte", "nom": "éraflure"},
                  "texte": "Une éraflure fraîche.", "representations_autorisees": ["aspect"]}
        lu = {"representation": "objet", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun",
              "capacites": [], "fragments": [{"texte": "Une éraflure fraîche.", "portee": "sans_preuve",
                                              "preuve": "", "motif": "Indice non établi."}]}
        refus = controler_portee([entree], {"descriptions": [lu]})
        self.assertEqual([set(r) for r in refus], [CHAMPS] * 2)
        self.assertEqual(refus[0]["attendu"],
                         "description 0 (nom « éraflure »), reçu « Une éraflure fraîche. » ; selon l'auditeur "
                         "(verdict représentation objet) ; accepté : une phrase qui décrit ce sujet comme aspect, "
                         "et rien d'autre")
        self.assertIn("(verdict sans_preuve) : « Indice non établi. »", refus[1]["attendu"])

    def test_capacites_incompatibles(self):
        entrees = [{"objet": {"id": "torche"}, "capacites_proposees": [], "constats_proposes": [],
                    "coupe_possible": None, "physique_proposee": {"materiau": "fer"}, "contenu_propose": None}]
        refus = controler_physique(entrees, {"jugements": [{"compatible": False, "motif": "Une torche n'est pas en fer."}]})
        self.assertEqual(refus[0]["attendu"],
                         "qualification 0 (objet torche), reçu « physique = {\"materiau\": \"fer\"} » ; selon "
                         "l'auditeur (verdict incompatible) : « Une torche n'est pas en fer. » ; accepté : une "
                         "qualification accordée à ce que l'objet est déjà (matière, description, masse, état), ou aucune")

    def test_contre_revue_d_action_cite_le_plan(self):
        m = nouveau_monde()
        plan = Moteur(m).preparer(proposition("detacher", "axe_haut", "couteau", "levier", 18))
        with self.assertRaises(ErreurMonde) as refus:
            verifier_couverture({"conforme": False, "motif": "Prise non demandée."}, plan)
        self.assertEqual(str(refus.exception), "La manœuvre proposée ne couvre pas la demande : Prise non demandée.")
        self.assertEqual(refus.exception.attendu,
                         f"proposition, reçu « {plan.titre} (action detacher, cible axe_haut) » ; selon l'auditeur "
                         "(verdict non conforme) : « Prise non demandée. » ; accepté : le même geste, dont les "
                         "changements durables sont ceux de la demande : retire celui qu'elle ne demande pas, ou "
                         "ajoute l'étape qui manque")

    def test_un_ajout_mal_forme_garde_l_attendu_du_moteur(self):
        from donjon.refus import depuis_refus
        r = depuis_refus(ErreurMonde("Description proposée mal formée.", "chaque ajout est un objet JSON."), "description")
        self.assertEqual((r["motif"], r["attendu"]),
                         ("Description proposée mal formée.", "description : chaque ajout est un objet JSON."))

    def test_nom_sans_fondement_dans_le_texte_d_un_ajout(self):
        from donjon.narration import mentions_proposees
        m = nouveau_monde()
        ajout = {"mode": "etablir_faits", "texte": "", "faits": [], "proposition": {"ajouts": [
            {"type": "detail", "ancrage": "porte", "nom": "éraflure", "texte": "Une éraflure. Un marteau l'a faite."}]}}
        refus = mentions_proposees(m, ajout, "porte")
        self.assertEqual(refus[0]["attendu"].split(" ; ")[0],
                         "proposition.ajouts[0].texte, segment 1, reçu « marteau »")

    def test_un_rapport_illisible_ne_reproche_rien_au_texte(self):
        r = audit_illisible("Contrôle narratif incomplet.", texte="Tu attends.")
        self.assertEqual(r["attendu"], "texte : aucune phrase n'est en cause, le contrôle n'a pas pu lire son propre "
                                       "rapport ; accepté : la même réponse, renvoyée telle quelle, ou une autre.")


class ChaineTests(Commun, unittest.TestCase):
    """La relance du MJ reçoit chaque refus avec son attendu ; le joueur n'en lit rien ; l'état rechargé
    ne garde que ce que le moteur a fait."""

    def test_cas_reel_ilse_la_relance_recoit_les_attendus(self):
        m = scene()
        saisie = "Ilse, tu peux m'aider à déplacer les planches ?"
        raconte = dialogue("Tu demandes à Ilse de t'aider. « Pas maintenant », te répond-elle.")
        reprise, sortie, appels = jouer(m, saisie, [
            raconte, raconte, parole(saisie, ("propos", "", "", ""), personnage="ilse"),
            dialogue("Ilse hésite.")], [verdicts(NEUTRE, NEUTRE), verdicts(NEUTRE)])
        refus = mj(appels)[2]["controle_narratif"]
        self.assertTrue(all(set(r) == CHAMPS for r in refus))
        self.assertEqual([r["attendu"].split(" ; ")[0] for r in refus],
                         ["texte, segment 0, reçu « Tu demandes à Ilse »", "texte, segment 1, reçu « Pas maintenant »"])
        self.assertIn("mode parole_joueur (personnage = ilse)", refus[0]["attendu"])
        self.assertIn(f"Tu dis à Ilse : « {saisie} »", sortie)
        self.assertNotIn("Pas maintenant", sortie)
        self.assertJamaisAffiche(sortie, refus)
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1], ("joueur", ["ilse"], saisie))

    def test_invention_refusee_trois_fois_le_repli_ne_montre_aucun_attendu(self):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        admise, invention = "Le brasero est allumé.", "Une trappe dort sous tes pieds."
        refus_audit = ("invention_protegee", (), "Trappe absente des faits.")
        reprise, sortie, appels = jouer(m, "mj qu'y a-t-il autour du brasero ?",
                                        [dialogue(admise + " " + invention)] * 3,
                                        [verdicts(("mecanique", ("objet:brasero",), ""), refus_audit)] * 3)
        refus = mj(appels)[2]["controle_narratif"]
        self.assertEqual(len(refus), 1)
        self.assertEqual((refus[0]["segment"], refus[0]["texte"]), (1, invention))
        self.assertIn("(verdict invention_protegee) : « Trappe absente des faits. »", refus[0]["attendu"])
        self.assertIn(admise, sortie)
        self.assertNotIn("trappe", sortie.lower())
        self.assertJamaisAffiche(sortie, refus)
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], admise)

    def test_audit_illisible_la_relance_sait_que_le_texte_n_est_pas_en_cause(self):
        m = nouveau_monde()
        texte = "La torche est posée au sol."
        reprise, sortie, appels = jouer(m, "mj où est la torche ?", [dialogue(texte), dialogue(texte)],
                                        [{}, {}, verdicts(("mecanique", ("objet:torche",), ""))])
        refus = mj(appels)[1]["controle_narratif"]
        self.assertEqual(refus[0]["attendu"].split(" ; ")[0],
                         "texte : aucune phrase n'est en cause, le contrôle n'a pas pu lire son propre rapport")
        self.assertIn(texte, sortie)
        self.assertJamaisAffiche(sortie, refus)
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], texte)

    def test_contre_revue_non_conforme_la_correction_recoit_le_plan_et_le_motif(self):
        m = nouveau_monde()
        examiner = {"mode": "action", "texte": "", "faits": [],
                    "proposition": proposition("examiner", "torche", justification="")}
        recit = dialogue("Tu examines la torche.")
        reprise, sortie, appels = jouer(m, "j'examine la torche", [examiner, examiner, recit],
                                        [verdicts(("mecanique", ("resultat_resolu",), ""))],
                                        [{"conforme": False, "motif": "Le joueur veut aussi la prendre."},
                                         {"conforme": True, "motif": ""}])
        retour = mj(appels)[1]["faits"]["retour_moteur"]
        self.assertEqual(retour["obstacle"],
                         "La manœuvre proposée ne couvre pas la demande : Le joueur veut aussi la prendre.")
        self.assertIn("(action examiner, cible torche) » ; selon l'auditeur (verdict non conforme) : « Le joueur "
                      "veut aussi la prendre. »", retour["attendu"])
        self.assertJamaisAffiche(sortie, [retour])
        self.assertNotIn(retour["obstacle"], sortie)
        self.assertEqual(reprise.objets["torche"]["lieu"], "antichambre")


if __name__ == "__main__":
    unittest.main()
