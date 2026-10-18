import copy
import io
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import patch

import jeu
from donjon.comparaison import Comparateur, texte_comparaison
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from tests.support import simuler_couverture


def extraire(id):
    return etape("detacher", id, outil="couteau", methode="levier", difficulte=18)


def action(p):
    return {"mode": "action", "texte": "", "faits": [], "proposition": p}


def narration(texte="Tu ranges la clé dans ta besace."):
    return {"mode": "dialogue", "texte": texte, "faits": ["resultat_resolu"], "proposition": None}


class OperationsTests(unittest.TestCase):
    def setUp(self):
        simuler_couverture(self)
        self.m = nouveau_monde()
        self.moteur = Moteur(self.m)

    def executer(self, p, jets=(20,)):
        with patch.object(Monde, "d20", side_effect=jets):
            return self.moteur.executer(self.moteur.preparer(p))

    def test_anciens_raccourcis_utilisent_les_memes_operations(self):
        for ancien, nouveau in (
            (proposition("prendre", "cle"), sequence(etape("deplacer", "cle", "joueur"))),
            (proposition("detacher", "axe_haut", "couteau", "levier", 18), sequence(extraire("axe_haut"), etape("deplacer", "axe_haut", "joueur"))),
        ):
            a, b = nouveau_monde(), nouveau_monde()
            with patch.object(Monde, "d20", return_value=20):
                for m, p in ((a, ancien), (b, nouveau)):
                    moteur = Moteur(m)
                    self.assertTrue(moteur.preparer(p).etapes)
                    moteur.executer(moteur.preparer(p))
            for champ in ("objets", "joueur", "minutes", "bruit", "arbitrages"):
                self.assertEqual(a.data[champ], b.data[champ])

    def test_prendre_allumer_puis_eteindre_poser(self):
        self.executer(sequence(etape("deplacer", "torche", "joueur"), etape("allumer", "torche")), ())
        self.assertEqual(self.m.objets["torche"]["lieu"], "joueur")
        self.assertTrue(self.m.objets["torche"]["allume"])
        self.assertEqual(self.m.objets["torche"]["combustible"], 29)
        self.assertEqual(self.m.data["minutes"], 2)
        self.assertEqual(self.m.data["jets"], 0)
        self.executer(sequence(etape("eteindre", "torche"), etape("deplacer", "torche", "antichambre")), ())
        self.assertFalse(self.m.objets["torche"]["allume"])
        self.assertEqual(self.m.objets["torche"]["combustible"], 29)
        self.assertEqual(self.m.objets["torche"]["lieu"], "antichambre")

    def test_allumage_impossible_refuse_la_sequence_avant_la_prise(self):
        initial = copy.deepcopy(self.m.data)
        for id, champ, valeur in (("briquet", "lieu", "echoppe"), ("briquet", "integrite", 0),
                                  ("torche", "combustible", 0), ("torche", "integrite", 0)):
            self.m.data = copy.deepcopy(initial)
            self.m.objets[id][champ] = valeur
            # Aucune autre flamme : une source allumée suffirait à allumer la torche.
            for o in self.m.objets.values():
                if o["id"] != "torche" and o.get("allume"):
                    o["allume"] = False
            avant = copy.deepcopy(self.m.data)
            with self.assertRaises(ErreurMonde):
                self.moteur.preparer(sequence(etape("deplacer", "torche", "joueur"), etape("allumer", "torche")))
            self.assertEqual(self.m.data, avant)

    def test_une_flamme_portee_allume_la_torche_sans_briquet(self):
        self.m.objets["briquet"]["lieu"] = "echoppe"
        self.assertTrue(self.m.objets["lanterne"]["allume"])
        plan = self.moteur.preparer(sequence(etape("deplacer", "torche", "joueur"), etape("allumer", "torche")))
        self.assertEqual(plan.plans[1].titre, "Allumer la torche avec la lanterne.")
        self.moteur.executer(plan)
        self.assertTrue(self.m.objets["torche"]["allume"])
        self.assertTrue(self.m.objets["lanterne"]["allume"])

    def test_allumer_permet_ensuite_une_extraction_dans_le_noir(self):
        for salle in self.m.data["salles"].values():
            salle["lumiere_naturelle"] = 0
        for o in self.m.objets.values():
            if "allume" in o:
                o["allume"] = False
        self.m.data["connus"].append("axe_haut")
        self.executer(sequence(etape("allumer", "lanterne", outil="briquet"), extraire("axe_haut")), (20,))
        self.assertTrue(self.m.objets["lanterne"]["allume"])
        self.assertFalse(self.m.objets["axe_haut"]["attache"])

    def test_degonder_deux_axes_avec_deux_operations_sans_verbe_nouveau(self):
        self.executer(sequence(extraire("axe_haut"), extraire("axe_bas")), (20, 20))
        self.assertTrue(self.m.objets["porte"]["detachee"])
        self.assertTrue(self.m.objets["porte"]["ouverte"])
        self.assertEqual(self.m.objets["axe_haut"]["lieu"], "antichambre")
        self.assertEqual(self.m.objets["axe_bas"]["lieu"], "antichambre")
        self.assertEqual(self.m.data["minutes"], 6)
        self.assertEqual(len(self.m.data["journal"][-1]["etapes"]), 2)

    def test_echec_partiel_conserve_premier_axe_arrete_suite_et_persiste(self):
        p = sequence(extraire("axe_haut"), etape("deplacer", "axe_haut", "joueur"),
                     extraire("axe_bas"), etape("deplacer", "axe_bas", "joueur"))
        self.executer(p, (20, 1))
        self.assertEqual(self.m.objets["axe_haut"]["lieu"], "joueur")
        self.assertTrue(self.m.objets["axe_bas"]["attache"])
        self.assertFalse(self.m.objets["porte"]["ouverte"])
        self.assertEqual(self.m.objets["couteau"]["integrite"], 2)
        self.assertEqual(self.m.data["minutes"], 6)
        self.assertFalse(self.m.data["journal"][-1]["reussite"])
        self.assertEqual(len(self.m.data["journal"][-1]["etapes"]), 3)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            self.m.sauver(path)
            self.assertEqual(Monde.charger(path).data, self.m.data)

    def test_sequence_invalide_rejetee_avant_tout_effet(self):
        for p in (sequence(etape("deplacer", "cle", "joueur"), etape("deplacer", "porte", "joueur")),
                  sequence(extraire("axe_haut"), extraire("axe_haut")),
                  sequence(etape("deplacer", "cle", "crypte")),
                  sequence(etape("deplacer", "anneau", "joueur")),
                  sequence(etape("patienter", "marchand")),
                  sequence(etape("deplacer", "cle", "joueur"), {"effet": "or", "valeur": 999}),
                  sequence(*[etape("patienter")] * 7)):
            avant = copy.deepcopy(self.m.data)
            with self.assertRaises(ErreurMonde):
                self.moteur.preparer(p)
            self.assertEqual(self.m.data, avant)

    def test_vol_inference_propriete_et_attente_non_cumulative(self):
        self.m.joueur["salle"] = "echoppe"
        avec = sequence(etape("patienter"), etape("deplacer", "crochets", "joueur", methode="discret"))
        plan = self.moteur.preparer(avec)
        self.assertEqual((plan.dd, plan.minutes), (12, 3))
        self.assertEqual(self.moteur.preparer(sequence(etape("patienter"), *avec["etapes"])).dd, 12)
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(sequence(etape("deplacer", "crochets", "joueur")))
        self.executer(avec, (1,))
        self.assertEqual(self.m.objets["crochets"]["lieu"], "echoppe")
        self.assertEqual(self.m.data["relations_pnj"]["marchand"]["vols_surpris"], 1)

    def test_geste_discret_avec_ses_affaires_ne_devient_pas_un_vol(self):
        self.m.joueur["salle"] = "echoppe"
        texte = self.executer(sequence(etape("deplacer", "couteau", "echoppe", methode="discret")), (1,))
        self.assertIn("remarque", texte)
        self.assertEqual(self.m.objets["couteau"]["lieu"], "joueur")
        self.assertEqual(self.m.data["relations_pnj"]["marchand"]["vols_surpris"], 0)

    def test_ranger_dans_contenant_ouvert_et_poids_imbrique(self):
        self.m.objets["sac"] = objet("sac", "sac", "contenant", "joueur", ouverte=True, verrouillee=False, mobile=True, masse=.2)
        masse = self.m.charge()
        self.executer(sequence(etape("deplacer", "couteau", "sac"), etape("deplacer", "cle", "sac")))
        self.assertEqual(self.m.objets["cle"]["lieu"], "sac")
        self.assertAlmostEqual(self.m.charge(), masse + .1)
        self.m.objets["sac"]["ouverte"] = False
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(sequence(etape("deplacer", "cire", "sac")))
        self.m.objets["sac"]["ouverte"] = True
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(sequence(etape("deplacer", "sac", "sac")))

    def test_pas_de_contournement_portage_par_contenant(self):
        self.m.objets["caisse"] = objet("caisse", "caisse", "contenant", "antichambre", ouverte=True, verrouillee=False, mobile=True, masse=1)
        self.m.objets["lest"] = objet("lest", "lest", "outil", "caisse", mobile=True, masse=20)
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(sequence(etape("deplacer", "caisse", "joueur")))

    def test_lumiere_future_verifiee_sans_consommation_en_preparation(self):
        self.m.objets["lanterne"]["combustible"] = 1
        # Supprimer la contribution de lumière venue de l'échoppe.
        self.m.data["salles"]["echoppe"]["lumiere_naturelle"] = 0
        for o in self.m.objets.values():
            if o.get("luminosite") and o["id"] != "lanterne":
                o["allume"] = False
        avant = copy.deepcopy(self.m.data)
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(sequence(etape("patienter"), extraire("axe_haut")))
        self.assertEqual(self.m.data, avant)

    def test_arbitrage_ne_change_pas_avec_formulation_ou_savoir_narratif(self):
        self.executer(sequence({**extraire("axe_haut"), "difficulte": 17}, justification="Premier avis"), (2,))
        self.m.objets["couteau"]["description_visuelle"] = "Une petite lame brillante."
        p = self.moteur.preparer(sequence({**extraire("axe_haut"), "difficulte": 22}, justification="Autre formulation"))
        self.assertEqual(p.dd, 17)
        self.assertEqual(p.origine, "arbitrage mémorisé")

    def test_plan_recompile_et_revision_verifiee(self):
        p = self.moteur.preparer(sequence(etape("deplacer", "cle", "joueur")))
        p.plans[0].effets = [("deplacer", "anneau", "joueur")]
        self.moteur.executer(p)
        self.assertEqual(self.m.objets["cle"]["lieu"], "joueur")
        self.assertEqual(self.m.objets["anneau"]["lieu"], "coffre")
        with self.assertRaises(ErreurMonde):
            self.moteur.executer(p)

    def test_resultat_compose_vient_du_moteur_et_est_sauvegarde(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            nouveau_monde().sauver(path)
            reponse = action(sequence(etape("deplacer", "cle", "joueur")))
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                 patch.object(MJOpenAI, "_appeler", return_value=reponse) as appel, \
                 patch("builtins.input", side_effect=["je range la clé", "tenter", "quitter"]), \
                 patch("sys.stdout", io.StringIO()) as sorties:
                jeu.main(["--recit-moteur", "--console", "--connexion", "api", "--save", str(path)])
            sauvegarde = Monde.charger(path)
            self.assertEqual(appel.call_count, 1)
            self.assertEqual(sauvegarde.objets["cle"]["lieu"], "joueur")
            self.assertEqual(sauvegarde.data["minutes"], 1)
            self.assertEqual(len(sauvegarde.data["journal"]), 1)
            self.assertIn("la clé", sorties.getvalue().lower())
            self.assertEqual(sauvegarde.data["conversation"][-1]["nature"], "resultat_moteur")

    def test_composition_proposee_a_une_question_non_executee(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "echanger", return_value=action(sequence(etape("deplacer", "cle", "joueur")))), patch("builtins.input", side_effect=["Puis-je prendre la clé ?", "quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--console", "--connexion", "api", "--save", str(path)])
            self.assertEqual(Monde.charger(path).objets["cle"]["lieu"], "antichambre")

    def test_comparateur_valide_plan_sans_effet_et_compare_narrations(self):
        termine = Event()
        c = Comparateur(MJOpenAI("principal"), MJOpenAI("secondaire"),
                        publier=lambda f: termine.set() if f["secondaire"]["statut"] == "Terminé" else None)
        p = sequence(extraire("axe_haut"), extraire("axe_bas"))
        avant = copy.deepcopy(self.m.data)
        try:
            with patch.object(c.principal, "_appeler", return_value=action(p)), patch.object(c.secondaire, "_appeler", return_value=action(p)):
                c.echanger(self.m, "Je retire les deux axes")
                self.assertTrue(termine.wait(2))
            self.assertEqual(self.m.data, avant)
            self.assertIn("OPÉRATIONS PROPOSÉES", texte_comparaison(c.fiches[1]))
            self.executer(p, (20, 1))
            avant = copy.deepcopy(self.m.data)
            termine.clear()
            with patch.object(c.principal, "_appeler", return_value=narration()), patch.object(c.secondaire, "_appeler", return_value=narration()):
                c.raconter_resultat(self.m, self.m.data["journal"][-1])
                self.assertTrue(termine.wait(2))
            self.assertEqual(self.m.data, avant)
            self.assertFalse(c.fiches[2]["resultat_resolu"]["reussite"])
            self.assertEqual(c.fiches[2]["principal"]["appels"][0]["empreinte_requete"], c.fiches[2]["secondaire"]["appels"][0]["empreinte_requete"])
        finally:
            c.fermer()
