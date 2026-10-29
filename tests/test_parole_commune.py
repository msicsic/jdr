"""À qui parle le joueur, et qui l'entend (``donjon/paroles.py``, ``donjon/ouie.py``, ``social``).

Le moteur fixe le destinataire : celui que le joueur nomme, sinon celui qui est en face de lui ;
« à tous » s'adresse à tous ceux qui l'entendent ; un chuchotement, à un seul, au contact. Tous
ceux qui saisissent les mots d'une parole à voix haute la retiennent, destinataires ou non, et
ce qu'elle transmet les touche par la même règle ; seuls les destinataires répondent.

Cas réel : « je dis : pouvez-vous m'aider à faire bouger Brune ? » devant Ilse et Aubin ; Luna
choisissait un seul destinataire, et l'autre n'enregistrait rien. Chaque cas vérifie l'état après
rechargement et ce que lit le joueur."""
from donjon.emissions import joueur as emissions_joueur

from tests.support import lier, relation
import unittest
from unittest.mock import patch

from donjon.esprits import croire, lire, memoriser
from donjon.monde import Monde
from donjon.narration import controler
from donjon.paroles import analyser
from donjon.social import bavarder, nouvelles
from tests.test_marche import tranquilles
from tests.test_paroles import jouer, parole, reponse_pnj
from tests.support import regarder
from tests.test_tensions import placer, recharger


def scene(ilse=(2, 4), aubin=(1, 5), brune=(7, 1)):
    """Le refuge : Corvus en (2, 2) regarde vers le sud ; Gorm est dans la conduite."""
    m = tranquilles()
    m.joueur.update(salle="antichambre", position=[2, 2], orientation="sud")
    placer(m, "ilse", "antichambre", ilse)
    placer(m, "aubin", "antichambre", aubin)
    placer(m, "brune", "antichambre", brune)
    placer(m, "marchand", "echoppe", (4, 1))
    return recharger(m)


def paroles_retenues(m, id):
    return [(s["locuteur"], s.get("a"), s["texte"]) for s in lire(m, id)["memoire"] if s["type"] == "parole"]


def action(nom, cible="", outil=""):
    return {"mode": "action", "texte": "", "faits": [],
            "proposition": {"action": nom, "cible": cible, "outil": outil, "methode": "simple", "difficulte": 0,
                            "justification": ""}}


class FormeTests(unittest.TestCase):
    """Les formes de la parole, lues dans la saisie : données de l'analyse, en un seul endroit."""

    def test_formes(self):
        m = scene(brune=(2, 3))
        cas = {
            "je dis : pouvez-vous m'aider ?": (False, None, "voix", "pouvez-vous m'aider ?", True),
            "à tous : il faut monter": (True, None, "voix", "il faut monter", True),
            "je dis à tous qu'il faut monter": (True, None, "voix", None, True),
            "« Brune, pousse-toi »": (False, "brune", "voix", "Brune, pousse-toi", True),
            "« Bonsoir »": (False, None, "voix", "Bonsoir", True),
            "je chuchote à Brune : viens": (False, "brune", "chuchote", "viens", True),
            "je murmure que la cloche est en haut": (False, None, "chuchote", None, True),
            # Sans guillemets, une interpellation reste du texte libre pour le MJ.
            "Ilse, tu viens ?": (False, "ilse", "voix", "Ilse, tu viens ?", False),
            "Brune, Ilse et Aubin sont où ?": (False, "brune", "voix", "Brune, Ilse et Aubin sont où ?", False),
            # Un verbe de parole en tête annonce une parole ; « lance » dit aussi un geste.
            "je demande à la meunière de venir": (False, "ilse", "voix", None, True),
            "je lui dis que la cloche est en haut": (False, None, "voix", None, True),
            "je lance la pierre": (False, None, "voix", None, False),
            "je lance à tous : on monte": (True, None, "voix", "on monte", True),
            "je prends la torche": (False, None, "voix", None, False),
        }
        for saisie, attendu in cas.items():
            f = analyser(m, saisie)
            self.assertEqual((f["groupe"], f["nomme"], f["maniere"], f["mots"], f["explicite"]), attendu, saisie)


class DestinataireTests(unittest.TestCase):
    def test_cas_reel_celui_d_en_face_repond_l_autre_retient(self):
        m = scene()
        saisie = "je dis : pouvez-vous m'aider à faire bouger Brune ?"
        reprise, sortie, appels = jouer(m, saisie, [
            parole("Pouvez-vous m'aider ?", ("propos", "", "", ""), personnage="ilse"),
            reponse_pnj("Ilse : « Je ne sais pas. »")])
        mots = "pouvez-vous m'aider à faire bouger Brune ?"
        # Le moteur fixe le destinataire avant Luna, et le lui dit.
        self.assertEqual(appels[0]["faits"]["parole_prevue"]["personnage"], "ilse")
        validee = appels[1]["faits"]["conversation_validee"]
        self.assertEqual((validee["destinataires"], validee["temoins"]), (["ilse"], ["aubin"]))
        self.assertIn(f"Tu dis à Ilse : « {mots} »", sortie)
        # Après rechargement : Ilse a reçu la parole, Aubin l'a entendue sans qu'elle lui soit adressée.
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1], ("joueur", ["ilse"], mots))
        self.assertEqual(paroles_retenues(reprise, "aubin")[-1], ("joueur", ["ilse"], mots))
        # Luna voit ce qu'Aubin a entendu, pour lui donner voix plus tard.
        from donjon.paroles import paroles_retenues as vues
        self.assertEqual(vues(reprise, "aubin")[-1], {"de": "Corvus", "a": ["Ilse"], "mots": mots})

    def test_deux_a_egalite_le_joueur_precise(self):
        # Tous deux sous ses yeux, à la même distance réelle, de part et d'autre de son regard.
        m = scene(ilse=(5, 4), aubin=(7, 4), brune=(1, 5))
        m.joueur["position"] = [6, 2]
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "je dis : pouvez-vous m'aider ?", [
            parole("Pouvez-vous m'aider ?", ("propos", "", "", ""), personnage="ilse")])
        self.assertEqual(len(appels), 0)  # Le joueur précise ; le moteur le dit sans appeler le MJ.
        self.assertIn("Aubin et Ilse sont aussi près de toi l'un que l'autre : précise à qui tu parles", sortie)
        self.assertNotIn("Tu dis", sortie)
        self.assertEqual((paroles_retenues(reprise, "ilse"), paroles_retenues(reprise, "aubin")), ([], []))

    def test_a_meme_distance_celui_qui_est_droit_devant(self):
        """Banc Luna : « bonsoir, vous tenez le coup ? », Brune droit devant, Aubin à son côté, tous
        deux au contact ; le moteur demandait de préciser alors que Corvus fait face à Brune."""
        m = scene(brune=(2, 3), aubin=(1, 2), ilse=(6, 5))
        reprise, sortie, appels = jouer(m, "bonsoir, vous tenez le coup ?", [
            parole("Bonsoir, vous tenez le coup ?", ("propos", "", "", ""), personnage="brune"),
            reponse_pnj("Brune hausse les épaules.")])
        self.assertEqual(appels[0]["faits"]["parole_prevue"]["personnage"], "brune")
        self.assertIn("Tu dis à Brune : « bonsoir, vous tenez le coup ? »", sortie)
        self.assertEqual(paroles_retenues(reprise, "brune")[-1][1], ["brune"])

    def test_celui_qu_il_nomme_dans_son_dos_le_tourne_d_abord(self):
        """Banc Luna : « Ilse, qu'est-ce que tu vas en faire ? », Ilse dans le refuge mais derrière
        Corvus ; Luna répondait qu'elle n'était pas dans le refuge. Comme pour tout geste, il se
        tourne d'abord vers celui qu'il nomme."""
        from donjon.dialogues import interlocuteurs
        from donjon.spatial import memoriser
        m = scene(ilse=(2, 1), aubin=(6, 5), brune=(7, 1))
        # Il l'a vue en entrant, puis s'est tourné vers le sud.
        m.joueur["orientation"] = "nord"
        memoriser(m)
        m.joueur["orientation"] = "sud"
        m = recharger(m)
        self.assertNotIn("ilse", interlocuteurs(m))
        reprise, sortie, appels = jouer(m, "Ilse, tu viens ?", [
            parole("Ilse, tu viens ?", ("propos", "", "", ""), personnage="ilse"),
            reponse_pnj("Ilse : « J'arrive. »")])
        prevue = appels[0]["faits"]["parole_prevue"]
        self.assertEqual((prevue["personnage"], prevue["regard"]), ("ilse", "nord"))
        self.assertIn("ilse", appels[0]["faits"]["esprits_interlocuteurs"])
        self.assertIn("Tu te tournes vers le nord.\nTu dis à Ilse : « Ilse, tu viens ? »", sortie)
        self.assertEqual(reprise.joueur["orientation"], "nord")
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][1], ["ilse"])

    def test_luna_ne_choisit_pas_un_autre_destinataire(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "je dis : bonsoir", [
            parole("Bonsoir.", ("propos", "", "", ""), personnage="aubin"),
            parole("Bonsoir.", ("propos", "", "", ""), personnage="ilse"),
            reponse_pnj("Ilse hoche la tête.")])
        self.assertIn("personnage = ilse", appels[1]["faits"]["retour_moteur"]["attendu"])
        self.assertIn("Tu dis à Ilse : « bonsoir »", sortie)
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][1], ["ilse"])

    def test_a_tous_chacun_decide_par_le_moteur(self):
        m = scene()
        # Placement d'auteur : Ilse se méfie de Corvus, Aubin non.
        lier(m, "ilse", "joueur", False, "vu")
        reprise, sortie, appels = jouer(m, "à tous : écartez-vous", [
            parole("écartez-vous", ("passage", "", "", ""), personnage="tous"),
            reponse_pnj("Aubin s'écarte ; Ilse ne bouge pas.")], jet=20)
        validee = appels[1]["faits"]["conversation_validee"]
        self.assertEqual((validee["personnage"], validee["destinataires"], validee["temoins"]),
                         ("tous", ["aubin", "ilse"], []))
        faits = " ".join(validee["faits"])
        # Chacun en a décidé comme d'une demande individuelle : pas de décision collective.
        self.assertIn("Ilse, meunière évacuée refuse de s'écarter : elle ne te fait pas confiance.", faits)
        self.assertIn("Aubin, vieux passeur", faits)
        self.assertIn("Tu dis à tous : « écartez-vous »", sortie)
        for id in ("ilse", "aubin"):
            self.assertEqual(paroles_retenues(reprise, id)[-1], ("joueur", ["aubin", "ilse"], "écartez-vous"))

    def test_a_tous_il_faut_monter(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "à tous : il faut monter", [
            parole("il faut monter", ("propos", "", "", ""), personnage="tous"),
            reponse_pnj("Ilse et Aubin échangent un regard.")])
        self.assertIn("Tu dis à tous : « il faut monter »", sortie)
        for id in ("ilse", "aubin"):
            self.assertEqual(paroles_retenues(reprise, id)[-1], ("joueur", ["aubin", "ilse"], "il faut monter"))
        # Un propos n'engage personne à rien : ni intention ni engagement nouveaux.
        self.assertEqual([lire(reprise, id)["engagements"] for id in ("ilse", "aubin")], [[], []])

    def test_derriere_le_pilier_a_la_cantonade_ceux_qui_entendent_retiennent(self):
        # La sauvegarde réelle : Ilse et Aubin à trois cases, derrière le pilier ; Corvus ne les voit pas.
        m = scene(ilse=(5, 2), aubin=(5, 3), brune=(0, 3))
        m.joueur.update(position=[2, 3], orientation="est")
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "à tous : il faut monter", [
            {"mode": "dialogue", "texte": "Ta voix porte dans le refuge : « Il faut monter ! »", "faits": [],
             "proposition": None},
            parole("il faut monter", ("propos", "", "", ""), personnage="tous"),
            reponse_pnj("Ta voix résonne contre la pierre.")])
        # Luna racontait la parole elle-même : le moteur la lui fait proposer, puis la fait entendre.
        self.assertIn("mode parole_joueur", appels[1]["faits"]["retour_moteur"]["attendu"])
        validee = appels[2]["faits"]["conversation_validee"]
        self.assertEqual((validee["destinataires"], validee["temoins"]), ([], []))
        self.assertIn("Tu dis à tous : « il faut monter »", sortie)
        for id in ("ilse", "aubin", "brune"):
            self.assertEqual(paroles_retenues(reprise, id)[-1], ("joueur", [], "il faut monter"), id)

    def test_seuls_les_destinataires_repondent(self):
        faits = {"interlocuteurs": {"ilse": {}, "aubin": {}},
                 "conversation_validee": {"personnage": "ilse", "destinataires": ["ilse"], "temoins": ["aubin"],
                                          "faits": []}}

        def audit(locuteur):
            return {"segments": [{"portee_mecanique": "aucune", "indice": 0, "verdict": "parole", "sources": [], "locuteur": locuteur,
                                  "citation": "Non.", "entites": [], "comptes": [], "motif": ""}]}
        self.assertTrue(controler("Aubin : « Non. »", audit("aubin"), faits)["obstacles"])
        self.assertFalse(controler("Ilse : « Non. »", audit("ilse"), faits)["obstacles"])


class GuillemetsTests(unittest.TestCase):
    def test_guillemets_et_vocatif_restent_une_parole(self):
        m = scene()
        placer(m, "marchand", "antichambre", (1, 3))
        m.objets["cloche"].update(lieu="joueur")
        m.objets["cloche"].pop("position", None)
        m.objets["cloche"].pop("position_salle", None)
        m.data["connus"].append("marchand")
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "« Gorm, je te donne la cloche »", [
            action("remettre", "cloche", "marchand"),
            parole("Gorm, je te donne la cloche", ("propos", "", "", ""), personnage="marchand"),
            reponse_pnj("Gorm tend la main.")])
        # Luna proposait le don : le moteur le refuse, la saisie est une parole.
        self.assertIn("mode parole_joueur", appels[1]["faits"]["retour_moteur"]["attendu"])
        self.assertIn("Tu dis à Gorm : « Gorm, je te donne la cloche »", sortie)
        self.assertEqual(reprise.objets["cloche"]["lieu"], "joueur")
        self.assertEqual(paroles_retenues(reprise, "marchand")[-1], ("joueur", ["marchand"], "Gorm, je te donne la cloche"))
        # Ilse et Aubin, à portée, l'ont entendu.
        self.assertEqual(paroles_retenues(reprise, "ilse")[-1][2], "Gorm, je te donne la cloche")


class SuiteTests(unittest.TestCase):
    """Des mots entre guillemets sans interpellation, « je lui dis », « je leur dis » : la suite de
    l'échange, à qui Corvus parlait s'il l'entend encore ; sinon la règle commune."""

    def a_qui(self, m, saisie):
        from donjon.paroles import destinataires
        return destinataires(m, analyser(m, saisie))

    def test_des_guillemets_poursuivent_l_echange_avec_le_dernier_interlocuteur(self):
        m = scene()
        reprise, sortie, appels = jouer(m, "Aubin, bonsoir", [
            parole("bonsoir", ("propos", "", "", ""), personnage="aubin"), reponse_pnj("Aubin hoche la tête.")])
        self.assertIn("Tu dis à Aubin", sortie)
        # Ilse est en face, mais Corvus parlait à Aubin : les guillemets s'adressent à lui.
        reprise, sortie, appels = jouer(reprise, "« tu viens avec moi ? »", [
            parole("tu viens avec moi ?", ("propos", "", "", ""), personnage="aubin"),
            reponse_pnj("Aubin acquiesce.")])
        self.assertEqual(len(appels), 2)
        self.assertIn("Tu dis à Aubin : « tu viens avec moi ? »", sortie)
        self.assertEqual(paroles_retenues(reprise, "aubin")[-1], ("joueur", ["aubin"], "tu viens avec moi ?"))

    def test_apres_a_tous_les_guillemets_et_je_leur_dis_vont_au_groupe(self):
        m = scene()
        m.data["paroles_joueur"] = [{"revision": 0, "auditeur": "tous", "auditeurs": ["aubin", "ilse"],
                                     "texte": "il faut monter", "minute": 0}]
        self.assertEqual(self.a_qui(m, "« on y va »"), ["aubin", "ilse"])
        self.assertEqual(self.a_qui(m, "je leur dis qu'on part"), ["aubin", "ilse"])
        # « je lui dis » vise un seul : à deux, c'est celui d'en face.
        self.assertEqual(self.a_qui(m, "je lui dis qu'on part"), ["ilse"])

    def test_sans_echange_en_cours_ou_s_il_n_entend_plus_la_regle_commune(self):
        m = scene()
        self.assertEqual(self.a_qui(m, "« bonsoir »"), ["ilse"])  # Personne avant : celle d'en face.
        m.data["paroles_joueur"] = [{"revision": 0, "auditeur": "brune", "auditeurs": ["brune"],
                                     "texte": "bonsoir", "minute": 0}]
        placer(m, "brune", "echoppe", (7, 1))  # Partie dans la conduite : hors de portée de voix.
        self.assertEqual(self.a_qui(recharger(m), "« tu es là ? »"), ["ilse"])
        # Une interpellation dans les guillemets l'emporte sur la suite de l'échange.
        emissions_joueur(m)[0].update(auditeur="aubin", auditeurs=["aubin"])
        self.assertEqual(self.a_qui(m, "« Ilse, tu viens ? »"), ["ilse"])


class ChuchoterTests(unittest.TestCase):
    def test_au_contact_seul_le_destinataire_saisit_les_mots(self):
        # Brune au contact ; Ilse à trois cases, hors du regard de Corvus.
        m = scene(brune=(2, 3), ilse=(5, 2))
        m.data["connus"].append("brune")
        reprise, sortie, appels = jouer(m, "je chuchote à Brune : Gorm n'est pas fiable", [
            parole("Gorm n'est pas fiable", ("affirmation", "marchand", "fiable", "non"), personnage="brune"),
            reponse_pnj("Brune plisse les yeux.")], jet=20)
        self.assertEqual(appels[1]["faits"]["conversation_validee"]["temoins"], [])
        self.assertIn("Tu chuchotes à Brune : « Gorm n'est pas fiable »", sortie)
        self.assertEqual(paroles_retenues(reprise, "brune")[-1], ("joueur", ["brune"], "Gorm n'est pas fiable"))
        self.assertEqual(relation(reprise, "brune", "marchand")["source"], "dit:joueur")
        # Ilse n'en saisit pas les mots : ni souvenir de parole, ni croyance.
        self.assertEqual(paroles_retenues(reprise, "ilse"), [])
        self.assertEqual(relation(reprise, "ilse", "marchand")["source"], "savoir")

    def test_a_distance_refuse(self):
        m = scene(brune=(2, 5))
        m.data["connus"].append("brune")
        reprise, sortie, appels = jouer(m, "je chuchote à Brune : viens", [
            parole("viens", ("propos", "", "", ""), personnage="brune")])
        self.assertIn("Brune est trop loin : approche-toi pour lui chuchoter", sortie)
        # Le moteur le dit avant tout appel : aucune proposition n'y changerait rien.
        self.assertEqual(len(appels), 0)
        self.assertEqual(paroles_retenues(reprise, "brune"), [])
        self.assertEqual(emissions_joueur(reprise), [])

    def test_jamais_a_un_groupe(self):
        m = scene(brune=(2, 3))
        _, sortie, _ = jouer(m, "je chuchote à tous : on file", [
            parole("on file", ("propos", "", "", ""), personnage="tous")])
        self.assertIn("On ne chuchote qu'à une seule personne", sortie)


class AveuTests(unittest.TestCase):
    def test_un_aveu_a_voix_haute_devant_un_temoin(self):
        m = scene()
        # Placement d'auteur : Corvus a pris la clé de la réserve de Gorm, qui ne le sait pas.
        cle = m.objets["cle_reserve"]
        cle["lieu"] = "joueur"
        m.data["connus"].append("cle_reserve")
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "je dis à Ilse : c'est moi qui ai pris la clé de la réserve", [
            parole("c'est moi qui ai pris la clé de la réserve", ("aveu", "cle_reserve", "", "prendre"),
                   personnage="ilse"),
            reponse_pnj("Ilse recule d'un pas.")])
        self.assertIn("Ilse, meunière évacuée retient ton aveu.",
                      appels[1]["faits"]["conversation_validee"]["faits"])
        noyau = {"type": "vu_agir", "auteur": "joueur", "operation": "prendre", "objet": "cle_reserve"}
        for id in ("ilse", "aubin"):
            self.assertFalse(relation(reprise, id, "joueur")["valeur"])
            rumeurs = [s for s in lire(reprise, id)["memoire"] if s["type"] == "rumeur"]
            self.assertEqual((rumeurs[-1]["de"], rumeurs[-1]["rang"], rumeurs[-1]["evenement"]), ("joueur", 0, noyau))
        # Le témoin s'en sert plus tard par les mécanismes existants : il le confie au propriétaire.
        # La date d'observation (lot 64) accompagne le fait sans en changer l'identité.
        self.assertIn(noyau, [{k: v for k, v in x[1].items() if k != "observe"} for x in nouvelles(reprise, "aubin")])
        placer(reprise, "marchand", "antichambre", (1, 4))
        # Il peut désormais rattacher la confidence au joueur qu'il connaît.
        lire(reprise, "marchand")["voix"] = sorted(set(lire(reprise, "marchand")["voix"]) | {"joueur"})
        # Brune, à cinq cases derrière le pilier, l'a entendu aussi, d'une voix qu'elle ne connaît pas
        # et sans le voir : elle se méfie de cette voix, sans savoir à qui l'imputer ; elle n'en fait
        # pas une nouvelle qui nommerait Corvus (``voix``).
        self.assertNotIn("joueur", [s["de"] for s in lire(reprise, "brune")["memoire"] if s["type"] == "rumeur"])
        self.assertTrue(lire(reprise, "brune")["voix_entendues"]["joueur"]["mefiance"])
        self.assertNotIn("fiable", lire(reprise, "brune")["croyances"].get("joueur", {}))
        lier(reprise, "aubin", "ilse", False, "vu")   # Placement d'auteur : à Gorm, pas à Ilse.
        with patch.object(Monde, "d20", return_value=20):
            # Brune le sait déjà et se tient trop loin pour une confidence : il le confie à Gorm.
            self.assertTrue(bavarder(reprise, "aubin", []))
        reprise = recharger(reprise)
        gorm = lire(reprise, "marchand")
        self.assertEqual(relation(reprise, "marchand", "joueur")["source"], "dit:aubin")
        self.assertIn(noyau, [{k: v for k, v in s["evenement"].items() if k != "observe"} for s in gorm["memoire"] if s["type"] == "rumeur"])

    def test_avouer_un_geste_permis_n_apprend_rien(self):
        m = scene()
        m.objets["cle_reserve"].update(lieu="joueur", proprietaire="joueur")
        m.data["connus"].append("cle_reserve")
        m = recharger(m)
        reprise, _, appels = jouer(m, "je dis à Ilse : j'ai pris cette clé", [
            parole("j'ai pris cette clé", ("aveu", "cle_reserve", "", "prendre"), personnage="ilse"),
            reponse_pnj("Ilse hausse les épaules.")])
        self.assertEqual(appels[1]["faits"]["conversation_validee"]["faits"], [])
        self.assertNotIn("joueur", lire(reprise, "aubin")["croyances"])


class EntreEuxTests(unittest.TestCase):
    """Les PNJ entendent les paroles des autres PNJ par la même règle."""

    def test_une_confidence_surprise_devient_une_rumeur(self):
        m = scene(ilse=(5, 5), aubin=(4, 5), brune=(7, 1))
        placer(m, "marchand", "antichambre", (3, 5))
        noyau = {"type": "vu_agir", "auteur": "brune", "operation": "crocheter", "objet": "reserve"}
        memoriser(m, "aubin", noyau)
        lier(m, "aubin", "brune", False, "vu")
        lier(m, "aubin", "ilse", False, "vu")   # Placement d'auteur : il se confie à Gorm.
        regarder(m, "aubin", "marchand")                   # qu'il voit, à côté de lui.
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(bavarder(m, "aubin", []))
        m = recharger(m)
        # Ilse, à côté, a saisi les mots : elle retient la parole et adopte la rumeur, de seconde main.
        self.assertEqual(paroles_retenues(m, "ilse")[-1][:2], ("aubin", ["marchand"]))
        rumeur = [s for s in lire(m, "ilse")["memoire"] if s["type"] == "rumeur"][-1]
        self.assertEqual((rumeur["de"], rumeur["rang"], {k: v for k, v in rumeur["evenement"].items() if k not in ("preuve", "observe")}), ("aubin", 1, noyau))
        self.assertEqual(relation(m, "ilse", "brune")["source"], "dit:aubin")
        # Brune, l'accusée, trop loin pour saisir les mots ou non, ne la colporte pas.
        self.assertNotIn(noyau, [x[1] for x in nouvelles(m, "brune")])
        self.assertIn("Ilse surprend les mots d'Aubin à Gorm (crue).", [c["texte"] for c in m.data["chronique"]])


if __name__ == "__main__":
    unittest.main()
