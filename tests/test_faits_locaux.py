import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.defi import nouveau_defi
from donjon.faits_locaux import preparer_faits, supports
from donjon.geometrie import placer
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire, regarder
from donjon.spatial import installer as installer_cases
from donjon.transactions import du_type


PROPOSITION = {"support": "antichambre_murs", "inscription": "Veille au niveau des eaux."}
FAITS = {"ajouts": [{"type": "inscription", "ancrage": "antichambre_murs",
                     "nom": "", "genre": "", "texte": PROPOSITION["inscription"]}]}


def preparer_inscription(monde, proposition, revision=None):
    travail, _, etablis = preparer_faits(monde, {"ajouts": [{
        "type": "inscription", "ancrage": proposition.get("support", ""),
        "nom": "", "genre": "", "texte": proposition.get("inscription", "")}]}, revision)
    return travail, etablis[0]["objet"]


class FaitsLocauxTests(unittest.TestCase):
    def test_fausse_portee_sujet_ne_cree_ni_objet_autonome_ni_indice_de_quete(self):
        for nom, texte, representation in (
            ("seconde cloche", "Sa surface de bronze est ternie.", "objet"),
            ("lettres gravées", "Ces lettres indiquent que la cloche a été déplacée vers une cave.",
             "etat_du_monde"),
        ):
            with self.subTest(nom=nom), tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / "partie.json"
                def proposition_mj(nom_propose, description):
                    return {"mode": "etablir_faits", "texte": "",
                            "faits": ["faits_narratifs_proposables"],
                            "proposition": {"ajouts": [{"type": "detail",
                                "ancrage": "antichambre_murs", "nom": nom_propose,
                                "genre": "f", "texte": description}]}}
                def audit(nom_propose, description, nom_requis, texte_requis):
                    return {"descriptions": [
                        {"representation": nom_requis, "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [{
                            "texte": nom_propose, "portee": "sujet", "preuve": "", "motif": ""}]},
                        {"representation": texte_requis, "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [{
                            "texte": description, "portee": "sujet", "preuve": "", "motif": ""}]},
                    ]}
                correction = "Une trace claire marque la pierre."
                sorties = [
                    proposition_mj(nom, texte),
                    audit(nom, texte, representation if representation == "objet" else "aspect",
                          "aspect" if representation == "objet" else representation),
                    proposition_mj("trace claire", correction),
                    audit("trace claire", correction, "aspect", "aspect"),
                ]
                with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                      patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties),
                      patch("builtins.input", side_effect=["mj Que vois-je sur les murs ?", "quitter"]),
                      patch("sys.stdout", io.StringIO()) as sortie):
                    self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                               "--connexion", "api"]), 0)
                reprise = Monde.charger(chemin)
                self.assertNotIn(nom, sortie.getvalue())
                self.assertNotIn(texte, sortie.getvalue())
                with self.assertRaises(ErreurMonde):
                    reprise.trouver(nom)
                self.assertNotIn(texte, str(reprise.data["faits_vus"]))
                detail = reprise.trouver("trace claire")
                self.assertIn(correction, decrire(reprise, detail, detail=True))

    def test_description_hors_sujet_est_revisee_avant_sauvegarde_et_affichage(self):
        for nom, invention, description in (
            ("tache d'humidité", "Une seconde cloche est cachée sous le plancher.",
             "Une tache sombre couvre quelques pierres."),
            ("rainure", "Un passage mène à une pièce inconnue.",
             "Une rainure étroite traverse la pierre."),
        ):
            with self.subTest(nom=nom), tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / "partie.json"
                base = {"type": "detail", "ancrage": "antichambre_murs",
                        "nom": nom, "genre": "f"}
                def proposition_mj(texte):
                    return {"mode": "etablir_faits", "texte": "",
                            "faits": ["faits_narratifs_proposables"],
                            "proposition": {"ajouts": [{**base, "texte": texte}]}}
                def portee(texte, douteux=False):
                    return {"descriptions": [
                        {"representation": "aspect", "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [], "fragments": [
                            {"texte": nom, "portee": "sujet", "preuve": "", "motif": ""}]},
                        {"representation": "etat_du_monde" if douteux else "aspect",
                         "mobilite": [], "placement": "aucun", "impact_scenario": "aucun", "capacites": [],
                         "fragments": [{"texte": texte,
                                        "portee": "sans_preuve" if douteux else "sujet",
                                        "preuve": "",
                                        "motif": "Le texte ajoute un fait autonome." if douteux else ""}]},
                    ]}
                sorties = [proposition_mj(invention),
                           portee(invention, douteux=True),
                           proposition_mj(description),
                           portee(description),
                           ]
                with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                      patch.object(MJOpenAI, "_appeler_brut", side_effect=sorties) as appel,
                      patch("builtins.input", side_effect=["mj Que vois-je sur le mur ?", "quitter"]),
                      patch("sys.stdout", io.StringIO()) as sortie):
                    self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                               "--connexion", "api"]), 0)
                reprise = Monde.charger(chemin)
                detail = reprise.trouver(nom)
                self.assertEqual(appel.call_count, 4)
                self.assertTrue(appel.call_args_list[2].args[1]["controle_narratif"][0]["motif"])
                self.assertNotIn(invention, sortie.getvalue())
                self.assertIn(description, sortie.getvalue())
                self.assertEqual(reprise.objets[detail]["description_visuelle"], description)
                self.assertIn(description, decrire(reprise, detail, detail=True))
                self.assertNotIn(invention, str(reprise.data["faits_vus"]))

    def test_inscription_persistante_et_lisible_comme_objet(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        travail, id = preparer_inscription(m, PROPOSITION, m.data["revision"])
        self.assertEqual(m.data, avant)
        self.assertEqual(travail.objets[id]["lieu"], PROPOSITION["support"])
        with self.assertRaises(ErreurMonde):
            preparer_inscription(travail, PROPOSITION)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            travail.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.trouver("inscription sur les murs"), id)
        self.assertIn(PROPOSITION["inscription"], decrire(reprise, id, detail=True))
        moteur = Moteur(reprise)
        plan = moteur.preparer(proposition("lire", id))
        with patch.object(Monde, "d20", return_value=20):
            self.assertIn(PROPOSITION["inscription"], moteur.executer(plan))
        self.assertIn(id, reprise.data["lus"])

    def test_support_invisible_lointain_ou_absent_refuse_sans_mutation(self):
        m = nouveau_monde()
        m.objets["poutre"] = objet("poutre", "poutre", "surface", "crypte",
                                    materiau="bois")
        self.assertNotIn("poutre", supports(m))
        avant = copy.deepcopy(m.data)
        for p in ({**PROPOSITION, "support": "poutre"},
                  {**PROPOSITION, "support": "seconde_cloche"},
                  {**PROPOSITION, "inscription": ""}):
            with self.subTest(p=p), self.assertRaises(ErreurMonde):
                preparer_inscription(m, p)
            self.assertEqual(m.data, avant)
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, {"ajouts": [{**FAITS["ajouts"][0], "mobile": True}]})
        m.objets["lanterne"]["allume"] = False
        self.assertNotIn("antichambre_murs", supports(m))
        with self.assertRaises(ErreurMonde) as refus:
            preparer_inscription(m, PROPOSITION)
        self.assertEqual(str(refus.exception), "Il fait trop sombre pour en distinguer les détails.")

    def test_un_support_trop_loin_se_dit_sans_en_proposer_un_autre(self):
        """Banc Luna : « à quoi ressemble le mur de l'atelier ? », le mur trop loin ; le refus
        mêlait distance et lumière, et Luna détaillait à la place une perche voisine."""
        m = nouveau_defi(depart="fixe")
        installer_cases(m)
        self.assertTrue(m.visible("fanal"))
        self.assertNotIn("fanal", supports(m))
        with self.assertRaises(ErreurMonde) as refus:
            preparer_faits(m, {"ajouts": [{"type": "detail", "ancrage": "fanal", "nom": "éclat", "genre": "m",
                                           "texte": "Un éclat manque au verre."}]})
        self.assertEqual(str(refus.exception), "Tu es trop loin pour en distinguer les détails.")
        self.assertIn("ne le remplace pas par un autre support", refus.exception.attendu)

    def test_en_cases_le_detail_exige_proximite_et_lumiere(self):
        m = nouveau_defi(depart="fixe")
        installer_cases(m)
        travail, id = preparer_inscription(m, PROPOSITION)
        self.assertTrue(travail.visible(id))
        travail.joueur["position"] = [7, 5]
        self.assertFalse(travail.visible(id))
        travail.joueur["position"] = [1, 3]
        for source in ("lanterne", "torche"):
            travail.objets[source]["allume"] = False
        self.assertFalse(travail.visible(id))
        with self.assertRaises(ErreurMonde):
            Moteur(travail).preparer(proposition("lire", id))

    def test_gravure_sur_poutre_existante(self):
        m = nouveau_defi(depart="fixe")
        installer_cases(m)
        poutre = objet("poutre", "poutre du refuge", "surface", "antichambre",
                       genre="f", materiau="chêne")
        placer(poutre, "antichambre", [1, 2])
        m.objets["poutre"] = poutre
        proposition_mj = {"support": "poutre", "inscription": "Veille au niveau des eaux."}
        travail, id = preparer_inscription(m, proposition_mj)
        self.assertTrue(travail.visible(id))
        self.assertEqual(travail.objets[id]["lieu"], "poutre")
        self.assertEqual(travail.trouver("gravure sur la poutre du refuge"), id)

    def test_detail_concret_et_parole_suivent_la_meme_transaction(self):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        m.objets["marchand"]["lieu"] = "echoppe"
        m.objets["echoppe_murs"]["lieu"] = "echoppe"
        m.objets["temoin"] = objet("temoin", "Mira", "personnage", "echoppe")
        avant = copy.deepcopy(m.data)
        p = {"ajouts": [
            {"type": "detail", "ancrage": "echoppe_murs", "nom": "tache d'humidité",
             "genre": "f",
             "texte": "Une tache sombre couvre quelques pierres."},
            {"type": "parole", "ancrage": "marchand", "nom": "", "genre": "",
             "texte": "La seconde cloche est sous le plancher."},
        ]}
        travail, rendu, etablis = preparer_faits(m, p)
        self.assertEqual(m.data, avant)
        self.assertEqual(len(etablis), 2)
        self.assertIn("tache sombre", rendu)
        self.assertIn("Gorm", rendu)
        self.assertIn("tache d'humidité", regarder(travail))
        self.assertEqual(travail.objets[etablis[0]["objet"]]["lieu"], "echoppe_murs")
        self.assertIn("joueur", travail.data["paroles_pnj"][0]["auditeurs"])
        self.assertIn("temoin", travail.data["paroles_pnj"][0]["auditeurs"])
        self.assertNotIn("seconde_cloche", travail.objets)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            travail.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.trouver("tache d'humidité"), etablis[0]["objet"])
        self.assertIn("tache sombre", decrire(reprise, etablis[0]["objet"], detail=True))
        self.assertEqual(reprise.contexte()["paroles_entendues"][0]["texte"], p["ajouts"][1]["texte"])
        self.assertIn("tache sombre", reprise.contexte()["souvenirs_faits"][0]["description"])
        self.assertEqual(reprise.contexte()["interlocuteurs"]["temoin"]["paroles_entendues"][0]["locuteur"], "marchand")

    def test_faits_multiples_atomiques_en_cas_de_reference_refusee(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        p = {"ajouts": [
            {"type": "detail", "ancrage": "antichambre_murs", "nom": "tache d'humidité",
             "genre": "f",
             "texte": "Une tache sombre couvre quelques pierres."},
            {"type": "inscription", "ancrage": "poutre_inexistante", "nom": "", "genre": "",
             "texte": "Veille au niveau des eaux."},
        ]}
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, p)
        self.assertEqual(m.data, avant)

    def test_mj_propose_sans_texte_et_le_moteur_redige_la_reponse(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        reponse = {"mode": "etablir_faits", "texte": "", "faits": ["faits_narratifs_proposables"],
                   "proposition": FAITS}
        with patch.object(MJOpenAI, "_appeler", return_value=reponse) as appel:
            resultat = MJOpenAI().echanger(m, "Y a-t-il une inscription sur les murs ?")
        self.assertEqual(appel.call_count, 1)
        self.assertEqual(m.data, avant)
        self.assertIn(PROPOSITION["inscription"], resultat["texte"])
        self.assertEqual(du_type(resultat, "faits")["proposition"], FAITS)

    def test_mj_recoit_le_refus_et_corrige_un_support_invente(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        premier = {"mode": "etablir_faits", "texte": "", "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [{**FAITS["ajouts"][0], "ancrage": "poutre_inexistante"}]}}
        second = {"mode": "etablir_faits", "texte": "", "faits": ["faits_narratifs_proposables"],
                  "proposition": FAITS}
        with patch.object(MJOpenAI, "_appeler", side_effect=[premier, second]) as appel:
            resultat = MJOpenAI().echanger(m, "Que vois-je sur le mur ?")
        self.assertEqual(appel.call_count, 2)
        self.assertEqual("poutre_inexistante", appel.call_args_list[1].args[1]["faits"]["retour_moteur"]["proposition_refusee"]["ajouts"][0]["ancrage"])
        self.assertIn(PROPOSITION["inscription"], resultat["texte"])
        self.assertEqual(m.data, avant)

    def test_enrichissement_refuse_un_recit_joint_non_valide(self):
        reponse = {"mode": "etablir_faits",
                   "texte": "Une seconde cloche est cachée sous le plancher.",
                   "faits": ["faits_narratifs_proposables"], "proposition": FAITS}
        with patch.object(MJOpenAI, "_appeler", return_value=reponse):
            with self.assertRaises(ErreurMonde):
                MJOpenAI().echanger(nouveau_monde(), "Que vois-je sur les murs ?")

    def test_console_sauvegarde_avant_affichage_et_relecture(self):
        reponse = {"mode": "etablir_faits", "texte": "", "faits": ["faits_narratifs_proposables"],
                   "proposition": FAITS}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", return_value=reponse),
                  patch("builtins.input", side_effect=["mj y a-t-il une inscription sur les murs ?",
                                                      "lire inscription sur les murs", "quitter"]),
                  patch.object(Monde, "d20", return_value=20),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            recharge = Monde.charger(chemin)
        id = recharge.trouver("inscription sur les murs")
        self.assertIn(id, recharge.data["lus"])
        self.assertIn(PROPOSITION["inscription"], sortie.getvalue())
        self.assertEqual(len([o for o in recharge.objets.values() if o.get("origine_description") == "MJ"]), 1)

    def test_console_detail_et_parole_persistent_ensemble(self):
        p = {"ajouts": [
            {"type": "detail", "ancrage": "echoppe_murs", "nom": "éclat de peinture",
             "genre": "m", "texte": "Un éclat bleu marque la pierre."},
            {"type": "parole", "ancrage": "marchand", "nom": "", "genre": "",
             "texte": "La seconde cloche est sous le plancher."},
        ]}
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"], "proposition": p}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m = nouveau_monde()
            m.joueur["salle"] = "echoppe"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", return_value=reponse),
                  patch("builtins.input", side_effect=["mj que remarqué-je ici ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("un éclat de peinture", sortie.getvalue().lower())
        self.assertIn("La seconde cloche est sous le plancher.", sortie.getvalue())
        self.assertEqual(reprise.objets[reprise.trouver("éclat de peinture")]["genre"], "m")
        self.assertEqual(reprise.data["paroles_pnj"][0]["locuteur"], "marchand")
        self.assertNotIn("seconde_cloche", reprise.objets)

    def test_echec_de_sauvegarde_ne_montre_pas_l_inscription(self):
        reponse = {"mode": "etablir_faits", "texte": "", "faits": ["faits_narratifs_proposables"],
                   "proposition": FAITS}
        original = Monde.sauver
        def sauver(monde, chemin):
            if any(o.get("origine_description") == "MJ" for o in monde.objets.values()):
                raise OSError("Disque plein")
            return original(monde, chemin)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", return_value=reponse),
                  patch.object(Monde, "sauver", sauver),
                  patch("builtins.input", side_effect=["mj y a-t-il une inscription sur les murs ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                jeu.main(["--console", "--save", str(chemin), "--connexion", "api"])
            self.assertNotIn(PROPOSITION["inscription"], sortie.getvalue())
            self.assertFalse(any(o.get("origine_description") == "MJ"
                                 for o in Monde.charger(chemin).objets.values()))


if __name__ == "__main__":
    unittest.main()
