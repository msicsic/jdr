"""A4 : le sens proposé et l'expansion sont relus sans devenir des faits."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.comprehension import sens_propose, plan_admis
from donjon.contrats_sequence import ATTENTES, COMPOSITION
from donjon.contrats_son import SON_IMPROVISE, FORMES_SONORES
from donjon.couverture_action import entree, verifier
from donjon.improvisation import effet, issue, proposition as improviser
from donjon.mj import MJ
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from donjon.temps import instant
from tests.test_comprehension import PontScript
from tests.test_paroles import relais
from tests.test_tensions import recharger


def expression(maniere, forme=None, bruit=0):
    return improviser(maniere, issue(maniere, [effet("son", "joueur", texte=forme, valeur=1)]
                                    if forme else []), bruit=bruit)


class DossierRevueTests(unittest.TestCase):
    def test_proposition_et_effets_distincts_sans_mutation_ni_publication(self):
        for forme in (None, "voix_melodique", "corps_rythmique"):
            with self.subTest(forme=forme):
                m = nouveau_monde()
                p = expression("Une cloche cachée répond à mon geste.", forme, bruit=3)
                avant = copy.deepcopy(m.data)
                plan = Moteur(m).preparer(p)
                copie = copy.deepcopy(plan)
                dossier = entree("je fredonne doucement", plan, m)
                s = dossier["plan"]["sens_propose"]
                self.assertEqual(s["operation"], "improviser")
                self.assertEqual(s["parametres"], p)
                self.assertEqual(s["maniere_proposee"]["intention"], p["intention"])
                self.assertEqual(s["maniere_proposee"]["reussite"], p["reussite"]["recit"])
                self.assertIn(SON_IMPROVISE["sens"], s["contrats"])
                self.assertEqual(dossier["plan"]["effets_reussite"],
                                 [["son_improvise", "joueur", {"intensite": 1, "forme": forme}]] if forme else [])
                self.assertEqual(m.data, avant)
                self.assertEqual(plan, copie)
                # Une proposition et un bruit ne créent pas un fait ou une entité.
                self.assertNotIn("cloche cachée", regarder(m))
                s["parametres"]["intention"] = "altéré"
                self.assertEqual(plan, copie)

    def test_plan_fidele_admis_omission_refusee_et_attendu_nomme_effet(self):
        m = nouveau_monde()
        for forme in (None, "voix_melodique"):
            plan = Moteur(m).preparer(expression("Fredonner doucement", forme))
            avant = copy.deepcopy(m.data)
            mj = MJ(connexion="chatgpt")
            recus = []
            def revue(instructions, dossier, *args):
                recus.append(dossier)
                # Oracle de protocole, pas une simulation de compréhension du français.
                porte_son = any(e[0] == "son_improvise" for e in dossier["plan"]["effets_reussite"])
                return {"conforme": porte_son, "motif": "" if porte_son else
                        "proposition.reussite.effets : effet son manquant (son_improvise à l'exécution)."}
            with patch.object(mj, "_appeler_brut", side_effect=revue):
                if forme:
                    mj._auditer_action("je fredonne doucement", plan, m.data["revision"], m)
                else:
                    with self.assertRaises(ErreurMonde) as refus:
                        mj._auditer_action("je fredonne doucement", plan, m.data["revision"], m)
                    self.assertIn("effet son manquant", refus.exception.attendu)
                    self.assertIn("son_improvise", refus.exception.attendu)
            self.assertEqual(len(recus), 1)
            self.assertEqual(m.data, avant)

    def test_composition_developpee_et_attente_retrouvees_sans_inferer_admission(self):
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        plan = Moteur(m).preparer(proposition("voler", "crochets", methode="finesse"))
        d = entree("j'attends puis prends discrètement les crochets", plan, m)["plan"]
        self.assertEqual(d["sens_propose"]["operation"], "voler")
        self.assertEqual([s["sens_propose"]["operation"] for s in d["etapes"]], ["patienter", "deplacer"])
        self.assertIn(ATTENTES["occasion"]["sens"], d["etapes"][0]["sens_propose"]["contrats"])
        self.assertIn("crochets", d["etapes"][1]["sens_propose"]["parametres"]["cible"])
        self.assertIn("aucune orientation", str(d))
        # Le verdict de fidélité n'exécute rien et ne garantit pas le vol.
        avant = copy.deepcopy(m.data)
        verifier({"conforme": True, "motif": ""}, plan)
        self.assertEqual(m.data, avant)
        composition = Moteur(m).preparer(sequence(etape("patienter")))
        self.assertIn(COMPOSITION["sens"], str(sens_propose(composition)))

    def test_maniere_litterale_references_nommees_et_branches_completes(self):
        m = nouveau_monde()
        p = expression("pousser du pied vers echoppe", "corps_bref")
        p.update(stat="CHA", difficulte=10)
        p["echec"] = issue("garder le pied immobile", [effet("son", "joueur", texte="souffle", valeur=1)])
        plan = Moteur(m).preparer(p)
        plan.echec_critique = [("endommager", "couteau", 1)]
        d = entree("je pousse du pied", plan, m)["plan"]
        self.assertEqual(d["sens_propose"]["maniere_proposee"]["intention"], p["intention"])
        self.assertEqual(d["sens_propose"]["maniere_proposee"]["echec"], p["echec"]["recit"])
        self.assertEqual(d["effets_echec"][0][2]["forme"], "souffle")
        self.assertEqual(d["effets_echec_critique"][0][0], "endommager")
        self.assertEqual(d["conditions_execution"]["stat"], "CHA")

    def test_methode_canonique_presente_et_precisions_partagees_avec_le_joueur(self):
        m = nouveau_monde()
        for p in (sequence(etape("emettre_son", "joueur", methode="sifflement")),
                  sequence(etape("patienter"))):
            with self.subTest(p=p):
                plan = Moteur(m).preparer(p)
                s = entree("la demande entière reste littérale", plan, m)["plan"]["etapes"][0]["sens_propose"]
                self.assertEqual(s["maniere_proposee"]["methode"], p["etapes"][0]["methode"])
                self.assertEqual(s["maniere_proposee"]["outil"], "")
                self.assertTrue(s["precisions_moteur"])
                for precision in s["precisions_moteur"]:
                    self.assertIn(precision, plan_admis(m, plan))

    def test_la_prose_ne_masque_pas_la_modalite_sonore_calculee(self):
        for forme in ("voix_melodique", "souffle", "corps_rythmique"):
            with self.subTest(forme=forme):
                m = nouveau_monde()
                p = expression("Une autre forme est annoncée dans ce brouillon.", forme)
                plan = Moteur(m).preparer(p)
                avant = copy.deepcopy(m.data)
                s = entree("une saisie différente", plan, m)["plan"]["sens_propose"]
                self.assertEqual(s["maniere_proposee"]["reussite"], p["reussite"]["recit"])
                self.assertIn(FORMES_SONORES[forme], " ".join(s["precisions_moteur"]))
                self.assertNotIn(p["reussite"]["recit"], " ".join(s["precisions_moteur"]))
                self.assertIn(s["precisions_moteur"][0], plan_admis(m, plan))
                self.assertEqual(m.data, avant)

    def test_omission_corrigee_dans_la_boucle_sauvee_et_reprise_avec_laps_decoupe(self):
        for saisie, forme in (("je fredonne doucement", "voix_melodique"),
                              ("je frappe un rythme avec mes mains", "corps_rythmique")):
            with self.subTest(saisie=saisie), tempfile.TemporaryDirectory() as tmp:
                m = relais()
                chemin = Path(tmp) / "copie.json"
                m.sauver(chemin)
                mj = MJ(connexion="chatgpt")
                plans = iter([expression(saisie), expression(saisie, forme)])
                recus = []
                def appel(instructions, dossier, intention, fonction, schema):
                    if fonction == "repondre_au_joueur":
                        return {"mode": "action", "texte": "", "faits": [], "proposition": next(plans)}
                    self.assertEqual(fonction, "auditer_action")
                    recus.append(copy.deepcopy(dossier))
                    porte_son = any(e[0] == "son_improvise" for e in dossier["plan"]["effets_reussite"])
                    return {"conforme": porte_son, "motif": "" if porte_son else "effet son manquant"}
                pont = PontScript(["mj " + saisie, "tenter", "quitter"], chemin)
                with patch.object(jeu, "MJ", return_value=mj), patch.object(mj, "_appeler_brut", side_effect=appel), \
                     patch("sys.stdout", io.StringIO()), patch.object(Monde, "d20", side_effect=AssertionError("Sans jet")):
                    self.assertEqual(jeu.main(["--console", "--connexion", "chatgpt", "--save", str(chemin)], interface=pont), 0)
                self.assertEqual(len(recus), 2)
                self.assertEqual(recus[0]["demande"], recus[1]["demande"])
                charge = Monde.charger(chemin)
                self.assertEqual([s["forme"] for s in charge.data["sons"]], [forme])
                compris = charge.data["conversation"][-1]["compris"]
                self.assertIn("Compris :", compris)
                self.assertNotIn("aucun son prévu", compris)
                self.assertIn(compris, "\n".join(pont.historique))
                reprise = PontScript(["quitter"], chemin)
                with patch("sys.stdout", io.StringIO()):
                    jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise)
                self.assertEqual(Monde.charger(chemin).data, charge.data)
                self.assertIn(charge.data["conversation"][-1]["reponse"], "\n".join(reprise.historique))
                decoupe = recharger(charge)
                debut = instant(charge)
                with patch("donjon.agendas._naissances", return_value=None):
                    for monde, tranches in ((charge, [1200]), (decoupe, [150] * 8)):
                        for duree in tranches:
                            plan = Moteur(monde).preparer(proposition("attendre"))
                            plan.minutes, plan.dixiemes = 0, duree
                            Moteur._terminer_etape(monde, plan, [], (), "attendre", "simple")
                            monde.data = recharger(monde).data
                self.assertEqual(instant(charge) - debut, 1200)
                self.assertEqual(charge.data, decoupe.data)
                self.assertEqual((regarder(charge), fiche(charge), scene_percue(charge)),
                                 (regarder(decoupe), fiche(decoupe), scene_percue(decoupe)))


if __name__ == "__main__":
    unittest.main()
