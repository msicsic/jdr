"""Les défauts de parole du banc Luna du soir (``docs/banc-luna-soir.md``), corrigés par des règles
communes et vérifiés sur le cas réel du banc et un autre de même nature, ce que lit le joueur et
l'état après rechargement.

- Un nom détaché par une virgule désigne le destinataire où qu'il soit dans la phrase : « as-tu de
  quoi manger, Ilse ? » allait à Aubin, en face, et la réplique était réécrite.
- Interpeller un nom que Corvus ne connaît pas donne le refus juste : « « Brune, tu me dois… » »
  partait à Gorm.
- Une question à la cantonade est entendue par qui en saisit les mots, qui décide d'y répondre :
  dans le noir, Ilse à trois cases n'a jamais répondu à « Qui est là ? ».
- Un refus de forme d'une proposition du MJ ne s'affiche jamais comme une impossibilité (« La
  difficulté de ce geste sort des limites d'un arbitrage sommaire. »).
- Ce que reçoit l'auditeur dit qui répond (``repondent``, ``issue``) et ce que mesure chaque champ
  (portée de main, portée de voix) ; la parole à la cantonade y figure comme dite.
- On n'atteste pas l'absence d'une sortie qu'on ne connaît pas.
- Se dire quelqu'un d'autre est enregistré comme une imposture : le nom que disent les mots."""
from donjon.emissions import pnj as emissions_pnj, joueur as emissions_joueur
import json
from pathlib import Path
import tempfile
import unittest

from donjon.dialogues import interlocuteurs
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.narration import controler, voix_auteur
from donjon.paroles import analyser
from donjon.rendu import regarder
from tests.test_parole_commune import paroles_retenues
from tests.test_repli_et_appel import NEUTRE, dialogue, jouer, mj, parole, verdicts
from tools.banc_parties import preparer

BANCS = Path(__file__).parent / "data" / "bancs"


def banc(nom, *, noms_connus=None):
    """L'état de départ d'un banc ciblé du rapport, préparé comme le banc le prépare."""
    donnees = json.loads((BANCS / f"{nom}.json").read_text(encoding="utf-8"))
    if noms_connus is not None:
        donnees.setdefault("preparation", {})["noms_connus"] = noms_connus
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "banc.json"
        preparer(donnees, chemin)
        return Monde.charger(chemin)


def ligne(verdict, locuteur="", citation="", sources=()):
    return {"portee_mecanique": "aucune", "verdict": verdict, "sources": list(sources), "locuteur": locuteur, "citation": citation,
            "entites": [], "comptes": [], "motif": ""}


def audit(*lignes):
    return {"segments": {str(i): l for i, l in enumerate(lignes)}}


def narration(appels):
    """L'entrée de l'appel qui raconte la parole validée."""
    return next(e for e in mj(appels) if "conversation_validee" in e["faits"])


def action(proposition):
    return {"mode": "action", "texte": "", "faits": [], "proposition": proposition}


def heler(cible):
    return action({"action": "composer", "justification": "", "etapes": [
        {"operation": "emettre_son", "cible": cible, "destination": "", "outil": "", "methode": "heler",
         "difficulte": 0}]})


class VocatifTests(unittest.TestCase):
    def test_formes(self):
        m = banc("soir-appel")
        cas = {
            "as-tu de quoi manger, Ilse ?": ("ilse", False),
            "dis-moi, Ilse, as-tu faim ?": ("ilse", False),
            "« Tu as du bois, Ilse ? »": ("ilse", True),
            "je dis : il fait froid, Ilse": ("ilse", True),
            "Ilse, tu viens ?": ("ilse", False),
            # Après « moi », c'est celui qui parle qui se nomme : pas un vocatif.
            "« C'est moi, Brune. »": (None, True),
            "j'ai vu Aubin, il dort": (None, False),
        }
        for saisie, (nomme, explicite) in cas.items():
            forme = analyser(m, saisie)
            self.assertEqual((forme["nomme"], forme["explicite"], forme["inconnu"]), (nomme, explicite, None), saisie)
        # « je réponds », sans mots ni destinataire, ne dit encore rien : pas une parole sans conteste.
        self.assertFalse(analyser(m, "je réponds")["explicite"])
        self.assertTrue(analyser(m, "je réponds à Ilse : oui")["explicite"])

    def test_cas_reel_le_nom_en_fin_de_phrase_designe_le_destinataire(self):
        m = banc("soir-appel")
        saisie = "as-tu de quoi manger, Ilse ?"
        reprise, sortie, appels = jouer(m, saisie, [
            # Luna propose d'abord Aubin, en face : le moteur fixe Ilse, celle que le joueur nomme.
            parole("As-tu de quoi manger ?", ("ressource", "faim", "", ""), personnage="aubin"),
            parole("As-tu de quoi manger, Aubin ?", ("ressource", "faim", "", ""), personnage="ilse"),
            dialogue("Ilse secoue la tête : « Non, rien. »")],
            [audit(ligne("parole", "ilse", "Non, rien."))])
        self.assertEqual(mj(appels)[0]["faits"]["parole_prevue"]["personnage"], "ilse")
        self.assertIn("personnage = ilse", mj(appels)[1]["faits"]["retour_moteur"]["attendu"])
        # Les mots du joueur sont dits tels quels : la réplique n'est pas réécrite.
        self.assertIn(f"Tu dis à Ilse : « {saisie} »", sortie)
        self.assertNotIn("Tu dis à Aubin", sortie)
        validee = appels.rapports[-1]
        self.assertEqual((validee["destinataires"], validee["repondent"], validee["temoins"]),
                         (["ilse"], [], ["aubin", "brune"]))
        # Après rechargement : Ilse a reçu la question, Aubin l'a entendue sans qu'elle lui soit adressée.
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1], ("joueur", ["ilse"], saisie))
        self.assertEqual(paroles_retenues(reprise, "aubin")[-1], ("joueur", ["ilse"], saisie))
        self.assertEqual(emissions_joueur(reprise)[-1]["auditeurs"], ["ilse"])

    def test_meme_nature_le_nom_au_milieu_entre_guillemets(self):
        m = banc("soir-appel")
        reprise, sortie, appels = jouer(m, "« Dis-moi, Ilse, tu as du bois ? »", [
            parole("Dis-moi, Ilse, tu as du bois ?", ("ressource", "chaleur", "", ""), personnage="ilse"),
            dialogue("Ilse hausse les épaules : « Pas une bûche. »")],
            [audit(ligne("parole", "ilse", "Pas une bûche."))])
        self.assertEqual(mj(appels)[0]["faits"]["parole_prevue"]["personnage"], "ilse")
        self.assertIn("Tu dis à Ilse : « Dis-moi, Ilse, tu as du bois ? »", sortie)
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][1], ["ilse"])


class NomInconnuTests(unittest.TestCase):
    def test_cas_reel_un_nom_que_corvus_ne_connait_pas(self):
        # Le banc des comptes : Brune, jamais vue, est dans le dos de Corvus ; Gorm est en face.
        m = banc("comptes", noms_connus=[])
        reprise, sortie, appels = jouer(m, "« Brune, tu me dois deux pièces, rends-les-moi. »", [], [])
        self.assertEqual(mj(appels), [])  # Le moteur répond seul, sans appel.
        self.assertIn("Tu ne connais personne du nom de Brune ici.", sortie)
        self.assertNotIn("Tu dis à Gorm", sortie)
        # Rien n'a été dit, à personne.
        self.assertEqual(emissions_joueur(reprise), [])
        self.assertEqual(paroles_retenues(reprise, "marchand"), [])
        self.assertEqual(paroles_retenues(reprise, "brune"), [])

    def test_meme_nature_un_verbe_de_parole_et_une_interpellation_libre(self):
        m = banc("comptes", noms_connus=[])
        _, sortie, appels = jouer(m, "je dis à Brune : rends-moi mes pièces", [], [])
        self.assertEqual(mj(appels), [])
        self.assertIn("Tu ne connais personne du nom de Brune ici.", sortie)
        # Sans guillemets, le MJ interprète ; s'il en fait une parole à Gorm, le moteur la refuse.
        from donjon.voix import designation
        reprise, sortie, appels = jouer(m, "Brune, rends-moi mes pièces", [
            parole("Brune, rends-moi mes pièces.", ("reclamer", "", "", ""), personnage=designation(m,'marchand'))], [])
        self.assertEqual(len(mj(appels)), 0)
        self.assertIn("Tu ne connais personne du nom de Brune ici.", sortie)
        self.assertEqual(emissions_joueur(reprise), [])
        self.assertEqual(paroles_retenues(reprise, "marchand"), [])


class CantonadeTests(unittest.TestCase):
    def test_cas_reel_qui_est_la_dans_le_noir(self):
        # Le Palier des vannes sans lumière ; Ilse, à trois cases, jamais vue ni entendue.
        m = banc("soir-noir")
        reprise, sortie, appels = jouer(m, "« Qui est là ? »", [
            parole("Qui est là ?", ("qui", "", "", ""), personnage="personne"),
            dialogue("Une voix de femme répond, tout près : « Ilse. »")],
            [audit(ligne("parole", "voix_1", "Ilse."))])
        self.assertEqual(mj(appels)[0]["faits"]["parole_prevue"]["personnage"], "personne")
        faits = appels.contextes[-1]
        validee = appels.rapports[-1]
        # Ilse a saisi la question et répond : la voix qu'il ne savait pas là se nomme.
        self.assertEqual((validee["destinataires"], validee["repondent"]), ([], []))
        self.assertIn("Une voix inconnue se nomme : « Ilse ».", validee["faits"])
        self.assertFalse(any(f == "auditer_narration" for f, _ in appels))
        self.assertTrue(validee["issue"].startswith("Tu as dit à voix haute, à la cantonade : « Qui est là ? »."))
        self.assertEqual(faits["interlocuteurs"]["voix_1"]["voix_inconnue"], True)
        self.assertIn("Tu dis : « Qui est là ? »", sortie)
        self.assertIn("« Je m'appelle Ilse. »", sortie)
        # Après rechargement : Ilse a retenu la question ; Corvus entend une voix qui se dit Ilse, et peut
        # lui parler ; la suite de l'échange va à elle.
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][0::2], ("joueur", "Qui est là ?"))
        self.assertEqual(reprise.data["voix_entendues"]["ilse"]["se_dit"], "ilse")
        self.assertIn("voix_1", interlocuteurs(reprise))
        self.assertEqual(emissions_pnj(reprise)[-1]["locuteur"], "ilse")
        reprise, sortie, appels = jouer(reprise, "« Tu as de quoi manger ? »", [
            parole("Tu as de quoi manger ?", ("ressource", "faim", "", ""), personnage="voix_1"),
            dialogue("La voix répond : « Rien du tout. »")], [audit(ligne("parole", "voix_1", "Rien du tout."))])
        self.assertEqual(mj(appels)[0]["faits"]["parole_prevue"]["personnage"], "voix_1")
        self.assertIn("Tu dis à une voix qui se dit Ilse : « Tu as de quoi manger ? »", sortie)

    def test_meme_nature_une_question_sans_guillemets(self):
        m = banc("soir-noir")
        reprise, sortie, appels = jouer(m, "il y a quelqu'un ?", [
            parole("Il y a quelqu'un ?", ("propos", "", "", ""), personnage="personne"),
            dialogue("Une voix répond dans le noir : « Oui, ici. »")], [audit(ligne("parole", "voix_1", "Oui, ici."))])
        # Seul dans le noir, Corvus peut poser sa question à voix haute : le mode parole lui est offert.
        self.assertEqual(mj(appels)[0]["faits"]["parole_prevue"]["personnage"], "personne")
        self.assertEqual(appels.rapports[-1]["repondent"], ["voix_1"])
        self.assertIn("Tu dis : « il y a quelqu'un ? »", sortie)
        self.assertIn("« Oui, ici. »", sortie)
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][2], "il y a quelqu'un ?")

    def test_qui_se_mefie_de_la_voix_ne_repond_pas(self):
        m = banc("soir-noir")
        # Placement d'auteur : Ilse a déjà entendu cette voix mentir.
        lire(m, "ilse")["voix_entendues"]["joueur"] = {"minute": 0, "se_dit": None, "mefiance": True, "n": 1}
        reprise, sortie, appels = jouer(m, "« Qui est là ? »", [
            parole("Qui est là ?", ("qui", "", "", ""), personnage="personne"),
            dialogue("Ta question se perd dans le noir.")], [verdicts(("mecanique", ("conversation_validee",), ""))])
        validee = appels.rapports[-1]
        self.assertEqual(validee["repondent"], [])
        self.assertIn("Aucune réponse ne te parvient.", validee["issue"])
        # Elle l'a entendue sans répondre : elle la retient, Corvus ne la sait pas là.
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][2], "Qui est là ?")
        self.assertNotIn("ilse", reprise.data.get("voix_entendues", {}))
        self.assertEqual(interlocuteurs(reprise), {})

    def test_une_affirmation_a_la_cantonade_n_appelle_pas_de_reponse(self):
        m = banc("soir-noir")
        reprise, _, appels = jouer(m, "« Il fait froid ici. »", [
            parole("Il fait froid ici.", ("propos", "", "", ""), personnage="personne"),
            dialogue("Ta voix se perd dans le noir.")], [verdicts(("mecanique", ("conversation_validee",), ""))])
        self.assertEqual(appels.rapports[-1]["repondent"], [])
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][2], "Il fait froid ici.")

    def test_seuls_ceux_qui_repondent_parlent(self):
        faits = {"interlocuteurs": {"voix_1": {"voix_inconnue": True}, "aubin": {}},
                 "conversation_validee": {"personnage": "personne", "destinataires": [], "repondent": ["voix_1"],
                                          "faits": []}}
        self.assertFalse(controler("La voix : « Ici. »", audit(ligne("parole", "voix_1", "Ici.")), faits)["obstacles"])
        refus = controler("Aubin : « Ici. »", audit(ligne("parole", "aubin", "Ici.")), faits)["obstacles"]
        self.assertIn("(conversation_validee.repondent) ; aubin se tait", refus[0]["attendu"])


class FaisabiliteTests(unittest.TestCase):
    def test_cas_reel_un_refus_de_forme_n_est_pas_montre(self):
        # « est-ce que je pourrais passer sous la poutre effondrée ? » : Luna concluait « impossible », puis
        # proposait un arbitrage sommaire hors de ses bornes ; le joueur lisait la borne.
        from donjon.improvisation import issue, proposition
        from donjon.mj import demande_precision
        from tests.test_paroles import relais
        m = relais()
        mal_borne = proposition("passer sous la poutre", issue("Tu passes."), cibles=["poutre_conduite"],
                                approche="effort", stat="DEX", difficulte=0)
        impossible = action({"action": "impossible", "cible": "", "outil": "", "methode": "simple", "difficulte": 0,
                             "justification": "Tu ne peux pas."})
        reprise, sortie, appels = jouer(m, "est-ce que je pourrais passer sous la poutre effondrée ?", [
            impossible, action(mal_borne), action(mal_borne)], [])
        self.assertNotIn("sort des limites", sortie)
        self.assertNotIn("Réexamine", sortie)
        self.assertIn(demande_precision(), sortie)
        from tests.support import question_sans_execution
        self.assertEqual(reprise.data['conversation'][-1]['reponse'], question_sans_execution(demande_precision()))
        self.assertEqual(reprise.data['narrations_mj'][-1]['sources'], ['moteur'])
        self.assertEqual([f for f, _ in appels], ['repondre_au_joueur'] * 3)
        self.assertEqual((reprise.objets, reprise.joueur), (m.objets, m.joueur))
        # Chaque refus de forme est revenu au MJ, avec ce qu'il attend.
        retours = [e["faits"]["retour_moteur"] for e in mj(appels) if "retour_moteur" in e["faits"]]
        self.assertIn("difficulte : entier de 10 à 18", retours[1]["attendu"])
        self.assertEqual(reprise.data["journal"], [])

    def test_apres_un_refus_de_type_l_avis_ne_devient_pas_une_raison_du_monde(self):
        # Franchir une poutre n'est pas franchir un assemblage. Ce refus de type ne
        # prouve pas qu'une échelle est nécessaire pour le mouvement demandé.
        from tests.test_paroles import relais
        m = relais()
        m.joueur["position"] = [6, 2]
        def impossible():
            return action({"action": "impossible", "cible": "", "outil": "", "methode": "simple",
                           "difficulte": 0, "justification": "Tu demandes si tu peux passer."})
        franchir = action({"action": "franchir", "cible": "poutre_conduite", "outil": "", "methode": "simple",
                           "difficulte": 0, "justification": ""})
        reprise, sortie, appels = jouer(m, "est-ce que je pourrais passer sous la poutre effondrée ?", [
            impossible(), franchir, impossible()], [verdicts(NEUTRE), verdicts(NEUTRE)])
        refus = [e["faits"]["retour_moteur"]["obstacle"] for e in mj(appels) if "retour_moteur" in e["faits"]][-1]
        self.assertNotIn(refus, sortie)
        self.assertNotIn("Il faut une échelle", sortie)
        self.assertIn("Tu demandes si tu peux passer.", sortie)
        self.assertEqual(reprise.data["journal"], [])

    def test_meme_nature_heler_sans_nom_puis_la_question(self):
        m = banc("soir-noir")
        reprise, sortie, appels = jouer(m, "il y a quelqu'un ?", [
            heler("joueur"), parole("Il y a quelqu'un ?", ("propos", "", "", ""), personnage="personne"),
            dialogue("Une voix répond : « Moi. »")], [audit(ligne("parole", "voix_1", "Moi."))])
        self.assertNotIn("Dis qui tu appelles par son nom", sortie)
        self.assertIn("emettre_son heler", mj(appels)[1]["faits"]["retour_moteur"]["attendu"])
        self.assertIn("« Moi. »", sortie)
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][2], "il y a quelqu'un ?")


class ChampsTests(unittest.TestCase):
    def test_portee_de_main_et_de_voix(self):
        m = banc("soir-appel")
        _, _, appels = jouer(m, "as-tu de quoi manger, Ilse ?", [
            parole("as-tu de quoi manger, Ilse ?", ("ressource", "faim", "", ""), personnage="ilse"),
            dialogue("Ilse : « Non. »")], [audit(ligne("parole", "ilse", "Non."))])
        ilse = mj(appels)[0]["faits"]["objet:ilse"]
        self.assertNotIn("a_portee", ilse)
        self.assertEqual((ilse["a_portee_de_main"], ilse["a_portee_de_voix"]), (False, True))


class SortiesTests(unittest.TestCase):
    def test_cas_reel_dans_le_noir_aucune_sortie_connue(self):
        m = banc("soir-noir")
        texte = regarder(m)
        self.assertIn("Sorties que tu connais : aucune pour l'instant.", texte)
        self.assertNotIn("aucun passage directement praticable", texte)
        _, _, appels = jouer(m, "il y a quelqu'un ?", [
            parole("Il y a quelqu'un ?", ("propos", "", "", ""), personnage="personne"),
            dialogue("Une voix : « Moi. »")], [audit(ligne("parole", "voix_1", "Moi."))])
        salle = mj(appels)[0]["faits"]["salle"]
        self.assertEqual(salle["sorties_connues"], {})
        self.assertNotIn("sorties", salle)
        self.assertFalse(any("aucun passage" in a for a in mj(appels)[0]["faits"]["attestations"]))

    def test_meme_nature_une_sortie_foulee(self):
        from donjon.spatial import _case_interieure, memoriser
        from tests.test_paroles import relais
        from tests.test_tensions import recharger
        m = relais()
        salle, position = m.joueur["salle"], m.joueur["position"]
        self.assertIn("Sorties que tu connais : aucune pour l'instant.", regarder(m))
        # Placement d'auteur : Corvus a foulé le seuil de la sortie est, puis est revenu à sa place.
        m.joueur["position"] = list(_case_interieure(m, salle, m.data["salles"][salle]["sorties"]["est"]))
        memoriser(m)
        m.joueur["position"] = position
        m = recharger(m)
        self.assertIn("Sorties que tu connais : est (Refuge du relais).", regarder(m))
        self.assertEqual(list(m.contexte()["salle"]["sorties"]), ["est"])


class ImpostureTests(unittest.TestCase):
    def appelee(self):
        """Le banc des voix : Corvus a hélé Ilse dans le noir ; une voix qui se dit Ilse a répondu."""
        reprise, sortie, appels = jouer(banc("soir-voix"), "j'appelle Ilse", [], [])
        self.assertIn("voix_1", interlocuteurs(reprise))
        return reprise

    def test_cas_reel_c_est_moi_brune(self):
        m = self.appelee()
        reprise, sortie, appels = jouer(m, "« C'est moi, Brune. »", [
            parole("C'est moi, Brune.", ("nom", "joueur", "", ""), personnage="voix_1"),
            dialogue("La voix répond : « Brune ? Je ne te reconnais pas. »")],
            [audit(ligne("parole", "voix_1", "Brune ? Je ne te reconnais pas."))])
        # Typé « Corvus se nomme », le moteur lit le nom dans les mots, Brune, sans relancer le MJ
        # (branche relances-luna : avant, un refus et une seconde proposition).
        self.assertEqual(len(mj(appels)), 1)
        self.assertFalse(any(f == "auditer_narration" for f, _ in appels))
        faits = appels.rapports[-1]["faits"]
        self.assertIn("Une voix qui se dit Ilse sait que tu n'es pas « Brune ».", faits)
        # Après rechargement : Ilse, qui connaît la voix de Brune, retient l'imposture et se méfie de la voix.
        self.assertIn({"type": "imposture", "se_disait": "brune"},
                      [{k: s[k] for k in ("type", "se_disait")} for s in lire(reprise, "ilse")["memoire"]
                       if s["type"] == "imposture"])
        self.assertTrue(lire(reprise, "ilse")["voix_entendues"]["joueur"]["mefiance"])

    def test_meme_nature_le_nom_que_disent_les_mots_sans_contenu_type(self):
        m = self.appelee()
        reprise, _, appels = jouer(m, "« Je suis Corvus. »", [
            parole("Je suis Corvus.", ("propos", "", "", ""), personnage="voix_1"),
            dialogue("La voix : « Corvus… »")], [audit(ligne("parole", "voix_1", "Corvus…"))])
        # Le moteur lit le nom dans les mots : Corvus se nomme, même sans contenu typé.
        faits = appels.rapports[-1]["faits"]
        self.assertIn("te croit sur parole : pour elle, c'est « Corvus » qui parle", faits[0])
        self.assertEqual(lire(reprise, "ilse")["voix_entendues"]["joueur"]["se_dit"], "joueur")


    def test_un_nom_type_que_les_mots_ne_disent_pas(self):
        # Banc de la branche : à « « Qui est là ? » », Luna typait « Corvus se nomme » ; la voix le croyait.
        m = self.appelee()
        faux = parole("Qui est là ?", ("nom", "joueur", "", ""), personnage="voix_1")
        # L'opération demandée est l'identité d'autrui, pas se nommer soi-même.
        faux["proposition"]["operations_demandees"].update(nom=False, qui=True)
        reprise, _, appels = jouer(m, "« Qui est là ? »", [faux,
            parole("Qui est là ?", ("qui", "", "", ""), personnage="voix_1"),
            dialogue("La voix : « Ilse. »")], [audit(ligne("parole", "voix_1", "Ilse."))])
        self.assertIn("contenu[0] : retire l'élément nom", mj(appels)[1]["faits"]["retour_moteur"]["attendu"])
        faits = appels.rapports[-1]["faits"]
        self.assertFalse(any("c'est Corvus" in f for f in faits))
        self.assertNotEqual(lire(reprise, "ilse")["voix_entendues"].get("joueur", {}).get("se_dit"), "joueur")


class NommerUneVoixTests(unittest.TestCase):
    """La présence se juge à ce que Corvus sait, sa voix comprise : nommer la voix par le nom qu'elle s'est
    donné, c'est s'adresser à elle (``voix.porteur_du_nom``), pour une parole comme pour un don."""

    def appelee(self, ilse=None):
        m = banc("soir-voix")
        if ilse:
            from tests.test_tensions import placer, recharger
            placer(m, "ilse", "beffroi", ilse)
            m = recharger(m)
        reprise, _, _ = jouer(m, "j'appelle Ilse", [], [])
        self.assertEqual(reprise.data["voix_entendues"]["ilse"]["se_dit"], "ilse")
        return reprise

    def test_cas_reel_donner_a_la_voix_qui_se_dit_ilse(self):
        m = self.appelee()
        reprise, sortie, appels = jouer(m, "je donne le briquet à Ilse", [], [])
        self.assertEqual(mj(appels), [])
        # Elle est là, à trois cases, dans le noir : il faut s'approcher de la voix, sans la nommer au-delà.
        reponse = sortie.split("Accords :")[-1]
        self.assertIn("Approche-toi d'une voix qui se dit Ilse", reponse)
        self.assertNotIn("n'est pas là", reponse)
        self.assertNotIn("meunière", reponse)
        self.assertEqual(reprise.objets["briquet"]["lieu"], "joueur")

    def test_meme_nature_au_contact_et_par_la_parole(self):
        m = self.appelee(ilse=(4, 3))
        reprise, sortie, _ = jouer(m, "je donne le briquet à Ilse", [], [])
        self.assertEqual(reprise.objets["briquet"]["lieu"], "ilse")
        self.assertIn("Tu donnes le briquet à silex à une voix qui se dit Ilse.", sortie.split("Accords :")[-1])
        _, sortie, appels = jouer(m, "Ilse, tu as faim ?", [
            parole("Ilse, tu as faim ?", ("ressource", "faim", "", ""), personnage="voix_1"),
            dialogue("La voix : « Un peu. »")], [audit(ligne("parole", "voix_1", "Un peu."))])
        self.assertEqual(mj(appels)[0]["faits"]["parole_prevue"]["personnage"], "voix_1")
        self.assertIn("Tu dis à une voix qui se dit Ilse : « Ilse, tu as faim ? »", sortie)


class VoixAuteurTests(unittest.TestCase):
    def test_le_mj_ne_dit_pas_je(self):
        # Banc de l'atelier : « mais je ne vois pas d'autres outils traîner dans la cour ».
        self.assertTrue(voix_auteur("Tu fouilles la cour, mais je ne vois pas d'autres outils traîner."))
        self.assertTrue(voix_auteur("J'ignore ce qu'il contient."))
        self.assertFalse(voix_auteur("Gorm grogne : « Je n'en sais rien. »"))
        self.assertFalse(voix_auteur("Aujourd'hui, la conduite est calme."))


if __name__ == "__main__":
    unittest.main()
