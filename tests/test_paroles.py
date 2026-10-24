"""Paroles du joueur : réplique selon INT et CHA, croyances transmises, après rechargement."""
import io
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from tests.support import refusee, regarder, sans_evacues
from donjon.defi import nouveau_defi
from donjon.esprits import lire
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.paroles import REGLES as REGLES_PAROLE, bande_expression, capacite_transmission, preparer_parole
from donjon.spatial import installer


def relais():
    from tests.support import presentes
    m = presentes(sans_evacues(nouveau_defi(depart="fixe")))
    installer(m)
    # Placement d'auteur : Brune a déjà mangé ; le joueur se tient près de Gorm dans la conduite.
    lire(m, "brune")["besoins"]["faim"] = 0
    m.joueur.update(salle="echoppe", position=[1, 2])
    # Placement d'auteur : Gorm vient de faire ses rondes et reste à son poste.
    lire(m, "marchand")["visites"].update(antichambre=0, crypte=0)
    return m


def parole(replique, *contenu, personnage="marchand"):
    return {"mode": "parole_joueur", "texte": "", "faits": ["interlocuteurs"],
            "proposition": {"personnage": personnage, "replique": replique,
                            "contenu": [dict(zip(("type", "sujet", "attribut", "valeur"), c)) for c in contenu]}}


def reponse_pnj(texte):
    return {"mode": "dialogue", "texte": texte, "faits": ["conversation_validee"],
            "proposition": None, "_texte_moteur": True}


def jouer(monde, saisie, sorties, jet=20):
    """Une saisie passée au MJ simulé, dans la vraie boucle de jeu ; renvoie la partie rechargée."""
    appels = []

    def appel(instructions, entree, intention, fonction, schema):
        appels.append(entree)
        return sorties[len(appels) - 1]
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_auditer_action"),
              patch.object(MJOpenAI, "_appeler", side_effect=appel),
              patch.object(Monde, "d20", return_value=jet),
              patch("builtins.input", side_effect=[saisie, "quitter"]),
              patch("sys.stdout", io.StringIO()) as sortie):
            self_code = jeu.main(["--console", "--connexion", "api", "--save", str(chemin)])
        assert self_code == 0
        return Monde.charger(chemin), sortie.getvalue(), appels


def croyance(monde, sujet, attribut="lieu", pnj="marchand"):
    return lire(monde, pnj)["croyances"].get(sujet, {}).get(attribut)


class CitationTests(unittest.TestCase):
    def test_les_blocs_nommes_par_les_regles_sont_des_faits_citables(self):
        # Cas du banc Haiku : la règle des paroles nommait esprits_interlocuteurs, rangé sous
        # paroles ; seule une clé de premier niveau peut être citée dans faits ou sources.
        appels = []

        def appel(instructions, entree, intention, fonction, schema):
            appels.append((instructions, entree, schema))
            return [parole("Tout va bien, Gorm ?", ("propos", "", "", "")),
                    reponse_pnj("Gorm : « Ça ira. »")][len(appels) - 1]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            relais().sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", side_effect=appel),
                  patch("builtins.input", side_effect=["je demande à Gorm s'il va bien", "quitter"]),
                  patch("sys.stdout", io.StringIO())):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)]), 0)
        self.assertEqual(len(appels), 2)
        for instructions, entree, schema in appels:
            citables = schema["properties"]["faits"]["items"]["enum"]
            self.assertEqual(citables, list(entree["faits"]))
            # Les blocs du contexte de parole, et tout sous-bloc que leurs règles nomment, se citent.
            self.assertLessEqual({"expression_joueur", "esprits_interlocuteurs"}, set(citables))
            sous_blocs = {cle for bloc in entree["faits"].values() if isinstance(bloc, dict)
                          for cle, valeur in bloc.items() if isinstance(valeur, dict)}
            nommes = {cle for cle in sous_blocs - set(citables)
                      if re.search(r"(?<!\w)" + re.escape(cle) + r"(?!\w)", REGLES_PAROLE)}
            self.assertEqual(nommes, set(), "bloc nommé par les règles mais non citable")


class ExpressionTests(unittest.TestCase):
    def test_bande_et_capacite_suivent_int_et_cha(self):
        self.assertTrue(bande_expression({"INT": 14, "CHA": 12})["precision"].startswith("précise"))
        self.assertTrue(bande_expression({"INT": 14, "CHA": 12})["aisance"].startswith("ordinaire"))
        self.assertTrue(bande_expression({"INT": 6, "CHA": 17})["precision"].startswith("très pauvre"))
        self.assertTrue(bande_expression({"INT": 6, "CHA": 17})["aisance"].startswith("brillante"))
        self.assertEqual([capacite_transmission(i) for i in (6, 9, 10, 12, 13, 18)], [1, 1, 2, 2, 3, 3])

    def test_luna_recoit_la_bande_et_les_croyances_pas_la_verite(self):
        m = relais()
        _, sortie, appels = jouer(m, "je demande à Gorm s'il va bien", [
            parole("Tout va bien, Gorm ?", ("propos", "", "", "")),
            reponse_pnj("Gorm : « Ça ira. »")])
        paroles = appels[0]["faits"]
        self.assertTrue(paroles["expression_joueur"]["precision"].startswith("précise"))
        gorm = paroles["esprits_interlocuteurs"]["marchand"]
        self.assertIn("croit que la cloche d'alarme est dans la galerie de ronde", gorm["croit"])
        self.assertIn("Bourru", gorm["traits"])
        self.assertNotIn("brune", paroles["esprits_interlocuteurs"])
        self.assertEqual(appels[1]["faits"]["conversation_validee"]["replique_joueur"], "Tout va bien, Gorm ?")
        self.assertIn("Tu dis à Gorm : « Tout va bien, Gorm ? »", sortie)
        self.assertLess(sortie.index("Tu dis à Gorm :"), sortie.index("Gorm : « Ça ira. »"))

    def test_mots_entre_guillemets_dits_tels_quels(self):
        m = relais()
        reprise, sortie, _ = jouer(m, "je lui dis « Bonsoir, vieux grincheux. »", [
            parole("Bonsoir à toi, Gorm.", ("propos", "", "", "")), reponse_pnj("Gorm grogne.")])
        self.assertIn("Tu dis à Gorm : « Bonsoir, vieux grincheux. »", sortie)
        self.assertEqual(reprise.data["paroles_joueur"][-1]["texte"], "Bonsoir, vieux grincheux.")
        self.assertEqual(lire(reprise, "marchand")["memoire"][-1]["texte"], "Bonsoir, vieux grincheux.")


class CroyancesTransmisesTests(unittest.TestCase):
    def surpris(self):
        m = relais()
        m.objets["marteau"]["proprietaire"] = "marchand"
        m.joueur["position"] = [7, 4]
        m.objets["marchand"]["position"] = [6, 2]
        regarder(m, "marchand", "joueur")  # Placement d'auteur : Gorm le regarde faire.
        with patch.object(Monde, "d20", return_value=1):
            Moteur(m).executer(Moteur(m).preparer(
                sequence(etape("deplacer", "marteau", "joueur", methode="discret"))))
        m.joueur["position"] = [7, 1]
        # Placement d'auteur : Corvus est déjà passé par la salle des vannes ; Gorm presse le retour de la cloche.
        m.data["visitees"].append("crypte")
        lire(m, "marchand")["besoins"].update(devoir=95, biens=0)
        lire(m, "marchand")["intention"] = None
        m.objets["marchand"].update(lieu="echoppe", position_salle="echoppe", position=[6, 2])
        regarder(m, "joueur", "marchand")  # On parle à qui l'on perçoit : Corvus se tourne vers lui.
        return m

    def test_mensonge_credible_change_son_plan_puis_se_decouvre(self):
        m = self.surpris()
        reprise, sortie, appels = jouer(m, "je lui dis que la cloche est déjà dans la salle des vannes", [
            parole("La cloche ? Elle est déjà en bas, dans la salle des vannes.",
                   ("affirmation", "cloche", "lieu", "crypte")),
            reponse_pnj("Gorm : « Alors je vais la chercher. »")])
        self.assertEqual(croyance(reprise, "cloche")["source"], "dit:joueur")
        self.assertEqual(croyance(reprise, "cloche")["valeur"], "crypte")
        self.assertIn("retient ce que tu lui dis", " ".join(appels[1]["faits"]["conversation_validee"]["faits"]))
        # Gorm se met en route vers la salle des vannes, n'y trouve rien et comprend.
        for _ in range(2):
            Moteur(reprise).executer(Moteur(reprise).preparer(proposition("attendre")))
        decouvertes = [s for s in lire(reprise, "marchand")["memoire"] if s["type"] == "mensonge_decouvert"]
        self.assertEqual((decouvertes[0]["locuteur"], decouvertes[0]["sujet"]), ("joueur", "cloche"))
        self.assertIn("Gorm, gardien du relais passe dans : Salle des vannes.",
                      [c["texte"] for c in reprise.data["chronique"]])
        self.assertIsNone(croyance(reprise, "cloche")["valeur"])

    def test_mensonge_dementi_par_ce_qu_il_voit(self):
        m = relais()
        m.objets["cloche"]["lieu"] = "joueur"
        m.objets["cloche"].pop("position")
        m.data["visitees"].append("chambre_cloche")
        Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        self.assertEqual(croyance(m, "cloche")["valeur"], "joueur")
        jets = m.data["jets"]
        reprise, _, appels = jouer(m, "je lui dis que la cloche est restée dans la galerie", [
            parole("La cloche est restée là-haut.", ("affirmation", "cloche", "lieu", "chambre_cloche")),
            reponse_pnj("Gorm fronce les sourcils.")])
        self.assertEqual(croyance(reprise, "cloche")["valeur"], "joueur")
        from donjon.relations import envers
        self.assertEqual(envers(reprise, "marchand", "joueur")["confiance"], 30)
        self.assertEqual(envers(reprise, "marchand", "joueur")["motifs"][-1]["type"], "mensonge_dementi")
        self.assertEqual(reprise.data["jets"], jets)
        self.assertIn("de ses propres yeux", " ".join(appels[1]["faits"]["conversation_validee"]["faits"]))

    def test_jet_rate_il_ne_te_croit_pas(self):
        m = relais()
        reprise, _, appels = jouer(m, "je lui dis que la cloche est déjà au refuge", [
            parole("La cloche est déjà au refuge.", ("affirmation", "cloche", "lieu", "antichambre")),
            reponse_pnj("Gorm secoue la tête.")], jet=2)
        self.assertEqual(croyance(reprise, "cloche")["source"], "savoir")
        self.assertIn("ne te croit pas", " ".join(appels[1]["faits"]["conversation_validee"]["faits"]))

    def test_int_faible_une_seule_idee_transmise(self):
        m = relais()
        m.joueur["stats"]["INT"] = 8
        # Placement d'auteur : Corvus a déjà croisé Brune et visité la salle des vannes.
        m.data["visitees"].append("crypte")
        m.data["connus"].append("brune")
        reprise, _, appels = jouer(m, "je lui dis que Brune n'est pas fiable et que la cloche est en bas", [
            parole("Brune... pas bien. Cloche... en bas.",
                   ("affirmation", "brune", "fiable", "non"), ("affirmation", "cloche", "lieu", "crypte")),
            reponse_pnj("Gorm plisse les yeux.")])
        from donjon.relations import envers
        self.assertEqual(envers(reprise, "marchand", "brune")["confiance"], 57)
        self.assertEqual(envers(reprise, "marchand", "brune")["motifs"][-1]["type"], "rumeur")
        self.assertEqual(croyance(reprise, "cloche")["source"], "savoir")
        self.assertIn("se perd", " ".join(appels[1]["faits"]["conversation_validee"]["faits"]))

    def test_on_ne_parle_que_de_ce_qu_on_connait(self):
        m = relais()
        # Les vivres sont enfermés : Corvus ne les a jamais vus ni entendu nommer.
        with self.assertRaisesRegex(ErreurMonde, "ne connaît pas"):
            preparer_parole(m, {"personnage": "marchand", "replique": "Tes vivres sont dans la galerie.",
                                "contenu": []})
        travail, rapport = preparer_parole(m, {"personnage": "marchand", "replique": "Tout est rangé là-haut.",
                                               "contenu": [{"type": "affirmation", "sujet": "vivres",
                                                            "attribut": "lieu", "valeur": "chambre_cloche"}]})
        self.assertEqual(rapport["faits"], [])
        self.assertEqual(croyance(travail, "vivres")["source"], "savoir")

    def test_references_par_nom_resolues(self):
        m = relais()
        reprise, _, _ = jouer(m, "je lui dis que la cloche est déjà au refuge", [
            parole("La cloche est déjà au refuge.", ("affirmation", "cloche d'alarme", "lieu", "refuge")),
            reponse_pnj("Gorm hoche la tête.")])
        self.assertEqual((croyance(reprise, "cloche")["valeur"], croyance(reprise, "cloche")["source"]),
                         ("antichambre", "dit:joueur"))


class DemandesTests(unittest.TestCase):
    def test_gorm_refuse_la_cle_qui_garde_sa_reserve(self):
        m = relais()
        # Placement d'auteur : Gorm a montré à Corvus la clé de la réserve.
        m.data["connus"].append("cle_reserve")
        reprise, _, appels = jouer(m, "je demande à Gorm la clé de la réserve", [
            parole("Gorm, tu me prêterais la clé de la réserve ?", ("demande", "cle_reserve", "", "")),
            reponse_pnj("Gorm : « Non. »")])
        self.assertEqual(reprise.objets["cle_reserve"]["lieu"], "marchand")
        self.assertIn("refuse de se séparer", " ".join(appels[1]["faits"]["conversation_validee"]["faits"]))

    def test_brune_rend_les_crochets_seulement_si_elle_n_en_a_plus_besoin(self):
        for faim, attendu in ((0, "joueur"), (90, "brune")):
            m = relais()
            # Placement d'auteur : Corvus a vu Brune empocher la trousse, trop petite pour se voir ensuite.
            m.objets["crochets"]["lieu"] = "brune"
            m.objets["crochets"].pop("position")
            m.data["connus"].append("crochets")
            m.joueur.update(salle="antichambre", position=[6, 1])
            lire(m, "brune")["besoins"]["faim"] = faim
            refusee(m)  # Placement d'auteur : Gorm vient de lui refuser une part.
            Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
            reprise, _, _ = jouer(m, "je demande à Brune de me prêter la trousse de crochets", [
                parole("Brune, tu me prêtes ta trousse de crochets ?", ("demande", "crochets", "", ""),
                       personnage="brune"),
                reponse_pnj("Brune hésite.")])
            self.assertEqual(reprise.objets["crochets"]["lieu"], attendu)


if __name__ == "__main__":
    unittest.main()


class DestinataireTests(unittest.TestCase):
    """Le joueur choisit à qui Corvus parle, et ses mots directs sont la réplique."""

    def test_un_autre_destinataire_que_celui_interpelle_est_refuse(self):
        from donjon.defi import nouveau_defi
        from donjon.paroles import preparer_parole
        from tests.support import presentes
        m = presentes(nouveau_defi(1985, "fixe"))
        m.joueur["salle"] = m.objets["brune"]["lieu"]
        m.objets["marchand"]["lieu"] = m.objets["brune"]["lieu"]   # Placement d'auteur : Gorm est là aussi.
        p = {"personnage": "brune", "replique": "Brune, tu connais le beffroi ?", "contenu": [],
             "_intention": "Gorm, tu peux me décrire le beffroi ?"}
        with self.assertRaises(ErreurMonde) as refus:
            preparer_parole(m, p)
        self.assertIn("personnage = marchand", refus.exception.attendu)
        self.assertNotIn("brune", refus.exception.attendu)

    def test_un_destinataire_absent_ne_suggere_personne_d_autre(self):
        from donjon.defi import nouveau_defi
        from donjon.paroles import preparer_parole
        from tests.support import presentes
        m = presentes(nouveau_defi(1985, "fixe"))
        m.joueur["salle"] = m.objets["brune"]["lieu"]
        p = {"personnage": "marchand", "replique": "Gorm ?", "contenu": [], "_intention": "Gorm, tu es là ?"}
        from donjon.dialogues import interlocuteurs
        self.assertNotIn("marchand", interlocuteurs(m))
        with self.assertRaises(ErreurMonde) as refus:
            preparer_parole(m, p)
        self.assertIn("mode dialogue", refus.exception.attendu)
        self.assertNotIn("brune", refus.exception.attendu)
