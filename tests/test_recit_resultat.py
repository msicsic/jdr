"""G4 : résultat public sauvegardé, sans récit ni audit après exécution."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon import corps
from donjon.config import MODELE_PAR_DEFAUT
from donjon.improvisation import issue, proposition as improviser
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, gestes_accomplis, proposition
from donjon.narration import rendre_resultat
from donjon.rendu import regarder, carte, fiche
from tools.banc_parties import preparer


ETIREMENT = improviser("S'étirer", issue("Brouillon non affiché.", []), approche="effort")


class RecitResultatTests(unittest.TestCase):
    def console(self, monde, p, demande, jet=20, confirmer=True):
        """Le faux MJ ne sait que proposer et revoir ; tout appel après tenter échoue."""
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "copie.json"
            monde.sauver(chemin)
            commandes = iter(["mj " + demande, *(["tenter"] if confirmer else []), "quitter"])
            appels, affiches, captures = [], [], []
            phase = {"execution": False}
            test = self

            class Pont:
                def rafraichir(self, m, *_):
                    self.monde = m

                def lire(self, *_):
                    saisie = next(commandes)
                    if saisie == "tenter" or (not confirmer and saisie.startswith("mj ")):
                        # Témoin moteur direct : mêmes jets, mêmes effets que la voie console.
                        self.temoin = self.monde.copier()
                        moteur = Moteur(self.temoin)
                        self.resultat = rendre_resultat(moteur.executer(moteur.preparer(p, "LLM : " + MODELE_PAR_DEFAUT)))
                        phase["execution"] = saisie == "tenter"
                    return saisie

                def ecrire(self, *valeurs, **_options):
                    texte = " ".join(str(v) for v in valeurs)
                    affiches.append(texte)
                    if hasattr(self, "resultat") and texte == self.resultat:
                        recharge = Monde.charger(chemin)
                        # Tout ce qui est montré existe déjà sur disque, texte compris.
                        test.assertEqual(recharge.data, self.monde.data)
                        test.assertEqual(recharge.data["conversation"][-1]["reponse"], texte)
                        test.assertEqual(recharge.data["conversation"][-1]["nature"], "resultat_moteur")
                        test.assertEqual((regarder(recharge), fiche(recharge), carte(recharge)),
                                         (regarder(self.monde), fiche(self.monde), carte(self.monde)))
                        captures.append(copy.deepcopy(recharge.data))

                def montrer(self, *_):
                    pass

            pont = Pont()
            def appeler(_instructions, _entree, _intention, fonction, _schema):
                self.assertFalse(phase["execution"], "Appel MJ après exécution : " + fonction)
                appels.append(fonction)
                if fonction == "auditer_action":
                    return {"conforme": True, "motif": ""}
                self.assertEqual(fonction, "repondre_au_joueur")
                return {"mode": "action", "texte": "", "faits": [], "proposition": copy.deepcopy(p)}

            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=appeler),
                  patch.object(MJOpenAI, "raconter_resultat", side_effect=AssertionError("Aucun récit")) as recit,
                  patch.object(Monde, "d20", return_value=jet),
                  patch("sys.stdout", io.StringIO())):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"],
                                          interface=pont), 0)
            recharge = Monde.charger(chemin)
            self.assertEqual(len(captures), 1)
            self.assertEqual(recharge.data, captures[0])
            recit.assert_not_called()
            self.assertEqual(appels, ["repondre_au_joueur", "auditer_action"])
            # Le journal de résultat peut être enrichi, jamais l'effet du geste.
            reel, temoin = copy.deepcopy(recharge.data), copy.deepcopy(pont.temoin.data)
            reel.pop("conversation", None)
            temoin.pop("conversation", None)
            self.assertEqual(reel, temoin)
            self.assertFalse(recharge.data.get("narrations_mj"))
            return recharge, pont.resultat, "\n".join(affiches)

    def scene_banc(self, nom):
        donnees = json.loads(Path("tests/data/bancs/" + nom + ".json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "scene.json"
            preparer(donnees, chemin)
            return Monde.charger(chemin)

    def test_assommer_reel_et_autre_coup_blessant(self):
        for methode, jet in (("assommer", 20), ("simple", 15)):
            with self.subTest(methode=methode):
                m = self.scene_banc("force-4b-assommer")
                pv = corps.pv(m, "marchand")
                m, resultat, texte = self.console(m, proposition("frapper", "marchand", "", methode),
                    "Puis-je " + ("assommer Gorm par derrière ?" if methode == "assommer" else "frapper Gorm ?"), jet)
                self.assertIn("« tenter »", texte)
                self.assertIn("le coup porte", resultat)
                self.assertNotIn("1d20(", resultat)
                self.assertIn(str(pv - corps.pv(m, "marchand")) + " PV", resultat)
                self.assertEqual(corps.conscient(m, "marchand"), methode != "assommer")
                if methode == "assommer":
                    self.assertIn("sans connaissance", resultat)

    def test_ligoter_reel_et_autre_contrainte(self):
        m = self.scene_banc("force-4f-ligoter")
        m, resultat, _ = self.console(m, proposition("ligoter", "brune", "corde_rixe"),
                                     "Puis-je la ligoter avec la corde ?")
        self.assertIn("maintenant ligotée", resultat)
        self.assertEqual(corps.corps(m, "brune")["lie"]["lien"], "corde_rixe")
        from tests.test_trainer import scene
        m, cible = scene()
        depart = m.joueur["position"][:]
        m, resultat, _ = self.console(m, proposition("trainer", cible, "est"),
                                     "Puis-je traîner Brune vers est ?")
        self.assertIn("Tu as traîné le corps d’une case.", resultat)
        self.assertEqual(m.objets[cible]["position"], depart)
        self.assertNotEqual(m.joueur["position"], depart)

    def test_depot_reel_et_autres_possessions_et_lumiere(self):
        for action in ("poser", "prendre", "allumer"):
            with self.subTest(action=action):
                m = self.scene_banc("poser-sol-relais")
                if action == "prendre":
                    from donjon.deplacement_objet import deplacer
                    deplacer(m, "torche", m.joueur["salle"])
                m, resultat, _ = self.console(m, proposition(action, "torche"),
                                             "Puis-je " + action + " ma torche ?")
                if action == "poser":
                    self.assertIn("au sol, à tes pieds", resultat)
                    self.assertEqual(m.objets["torche"]["lieu"], m.joueur["salle"])
                    self.assertEqual(m.objets["torche"]["position"], m.joueur["position"])
                else:
                    self.assertEqual(m.objets["torche"]["lieu"], "joueur")
                    self.assertIn("s'allume" if action == "allumer" else "Tu prends", resultat)
                    if action == "allumer":
                        self.assertTrue(m.objets["torche"]["allume"])

    def test_prise_et_coup_manque_rendent_leur_issue(self):
        from tests.test_tenir import situation
        for action, jet in (("saisir", 20), ("saisir", 1), ("frapper", 1)):
            with self.subTest(action=action, jet=jet):
                m = situation()
                pv = corps.pv(m, "brune")
                m, resultat, _ = self.console(m, proposition(action, "brune"),
                                             "Puis-je " + action + " Brune ?", jet)
                self.assertNotIn("1d20(", resultat)
                self.assertIn("Tu saisis cette personne." if jet == 20 else
                              "La personne échappe à ta prise." if action == "saisir" else
                              "le coup manque sa cible.", resultat)
                self.assertEqual(corps.pv(m, "brune"), pv)
                self.assertEqual(corps.corps(m, "brune").get("tenu_par"),
                                 "joueur" if jet == 20 else None)

    def test_geste_immediat_sans_second_appel(self):
        _, resultat, _ = self.console(nouveau_monde(), ETIREMENT, "je m'étire", confirmer=False)
        self.assertEqual(resultat, "Tu réalises ce geste.")

    def test_echec_et_reussite_du_jet_restent_affiches(self):
        p = improviser("Bondir", issue("Brouillon.", []), issue("Brouillon.", []),
                       approche="adresse", stat="DEX", difficulte=12)
        for jet in (1, 20):
            with self.subTest(jet=jet):
                m, resultat, _ = self.console(nouveau_monde(), p, "Puis-je bondir sur place ?", jet)
                self.assertNotIn("1d20(", resultat)
                self.assertIn("La tentative échoue." if jet == 1 else "La tentative réussit.", resultat)
                self.assertEqual(m.data["journal"][-1]["reussite"], jet == 20)

    def test_le_plan_garde_les_gestes_accomplis_pour_les_outils(self):
        m = nouveau_monde()
        from tests.test_poser_sol import sequence, etape
        moteur = Moteur(m)
        plan = moteur.preparer(sequence(etape("deplacer", "torche", "joueur")))
        moteur.executer(plan)
        self.assertEqual(gestes_accomplis(plan, m), [plan.plans[0].titre])


if __name__ == "__main__":
    unittest.main()
