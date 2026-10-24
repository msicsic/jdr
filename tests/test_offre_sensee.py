"""Offres jugées avant parole, refus sauvegardés et fournitures d'une tâche.

La scène crue 7 est prise juste avant l'offre de 5 pièces à Ilse, minute 353,
sur 5c2ce81 ; elle dépendait d'une part que le payeur ne pouvait pas livrer.
"""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas
from donjon.deliberation import choisir, retenir_refus, tient
from donjon.echanges import executer, offre_sensee
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import _contreparties, recours
from tests.test_proposer_recours import scene
from tests.test_tensions import recharger


FAUTE = {"operation": "manger", "cible": "vivres", "outil": "", "lieu": "", "condition": "sans_temoin"}


class OffreSenseeTests(unittest.TestCase):
    def test_seul_le_montant_effectivement_plus_fort_relance(self):
        m = scene(10)
        m.data["finances_pnj"]["brune"] = 1
        m.objets["crochets"]["prix"] = 100
        choisir(m, "brune", 0)
        offre = copy.deepcopy(lire(m, "brune")["intention"]["plan"][0])
        self.assertEqual(offre["contenu"]["contrepartie"], {"type": "pieces", "montant": 1})
        executer(m, "brune", offre, [])
        m = recharger(m)
        self.assertIsNone(recours(m, "brune", "faim", [FAUTE]))
        m.data["finances_pnj"]["brune"] = 2
        offre = recours(recharger(m), "brune", "faim", [FAUTE])
        self.assertEqual(offre["contenu"]["contrepartie"], {"type": "pieces", "montant": 2})
        lignes = []
        executer(m, "brune", offre, lignes)
        m = recharger(m)
        self.assertIn("2 pièces", " ".join(lignes))
        self.assertIsNone(recours(m, "brune", "faim", [FAUTE]))

    def test_refus_recharge_ne_repart_pas_avec_fortune_ou_biens_retrouves(self):
        for autre in ("marchand", "aubin"):
            with self.subTest(autre=autre):
                m = scene(10, autre)
                choisir(m, "brune", 0)
                offre = copy.deepcopy(lire(m, "brune")["intention"]["plan"][0])
                lignes = []
                executer(m, "brune", offre, lignes)
                self.assertIn("refuse l'échange", " ".join(lignes))
                m = recharger(m)
                refus = next(s for s in lire(m, "brune")["refus"] if s["operation"] == "proposer")
                self.assertEqual(refus["offre"]["gain"], 2)
                m.data["minutes"] += 180
                m.data["finances_pnj"]["brune"] += 10
                m.objets["crochets"].update(lieu="brune", proprietaire="brune")
                self.assertIsNone(recours(recharger(m), "brune", "faim", [FAUTE]))
                # Une ressource réellement nouvellement disponible lève le refus.
                croire(m, "brune", "vivres", "lieu", autre, "vu", salle="antichambre", case=[7, 4])
                self.assertIsNotNone(recours(recharger(m), "brune", "faim", [FAUTE]))

    def test_achat_refuse_meme_prix_tient_mais_meilleure_offre_possible(self):
        for cause in ("refus", "mefiance", "necessaire"):
            with self.subTest(cause=cause):
                m = scene()
                retenir_refus(m, "brune", "marchand", "acheter", cause, objet="vivres", prix=2)
                m = recharger(m)
                refus = lire(m, "brune")["refus"][-1]
                m.data["minutes"] += 180
                m.data["finances_pnj"]["brune"] += 10
                self.assertTrue(tient(recharger(m), "brune", refus))
                from donjon.pnj_propositions import refus_tient
                self.assertFalse(refus_tient(m, "brune", refus, {"type": "pieces", "montant": 3}))
                # Le planificateur commun doit lui aussi écarter le même achat.
                from donjon.planification import Vue
                self.assertTrue(Vue(m, "brune").refuse_achat("marchand", "vivres"))

    def test_ce_qu_il_garde_et_ce_qui_vaut_plus_ne_se_proposent_pas(self):
        from donjon.mine import nouveau_mine
        from donjon.spatial import installer
        from tests.support import calme, presentes, regarder
        from tests.test_tensions import placer
        for qui, cle in (("bram", "cle_paie"), ("josse", "passe"), ("odon", "crochets")):
            with self.subTest(qui=qui):
                m = presentes(nouveau_mine(depart="fixe"))
                installer(m)
                calme(m, *(i for i, o in m.objets.items() if o.get("profil")))
                placer(m, qui, "baraquement", [3, 5])
                placer(m, "mathe", "baraquement", [3, 4])
                m.joueur.update(salle="baraquement", position=[4, 4], orientation="ouest")
                regarder(m, qui, "mathe")
                m.objets[cle].update(lieu=qui, proprietaire=qui, prix=1 if qui == "bram" else 100)
                m.data["finances_pnj"][qui] = 0
                lire(m, qui)["besoins"]["faim"] = 95
                percevoir_tous(m)
                m = recharger(m)
                demande = {"type": "part", "objet": "vivres"}
                termes = [t for t, _, _ in _contreparties(m, qui, "mathe", demande)]
                self.assertFalse(any(t.get("objet") == cle for t in termes))
                self.assertFalse(offre_sensee(m, qui, "mathe", demande, {"type": "objet", "objet": cle}))
                with patch.object(Monde, "d20", return_value=20):
                    moteur = Moteur(m)
                    moteur.executer(moteur.preparer(proposition("attendre", cible="20")))
                m = recharger(m)
                self.assertEqual(m.objets[cle]["proprietaire"], qui)
                self.assertFalse(any(s["type"] == "proposition" and s["contrepartie"].get("objet") == cle
                                     for s in lire(m, qui)["memoire"]))
                self.assertNotIn(m.objets[cle]["nom"] + " contre", " ".join(m.data["journal"][-1]["faits"]))

    def test_ilse_cas_reel_et_autre_fourniture_refuses_avant_paiement(self):
        from donjon.echanges import engager
        with gzip.open(Path(__file__).parent / "data/offre-sensee-crue7-353.json.gz", "rt", encoding="utf-8") as f:
            initial = json.load(f)
        for objet in ("bois_guet", "planches"):
            with self.subTest(objet=objet):
                m = Monde(copy.deepcopy(initial))
                if objet == "planches":
                    # Même mécanisme, un autre lot nécessaire à la recharge.
                    m.objets["bois_guet"]["charges"] = 0
                    m.objets[objet].update(lieu="brune", proprietaire="marchand", charges=2)
                    croire(m, "ilse", objet, "lieu", "brune", "vu", salle="antichambre", case=[5, 4])
                    croire(m, "ilse", objet, "etat", {"disponible": True}, "vu")
                m = recharger(m)
                finances = copy.deepcopy(m.data["finances_pnj"])
                self.assertEqual(engager(m, "marchand", "ilse", {"objet": "brasero", "allume": True}, 5), "impossible")
                self.assertEqual(m.data["finances_pnj"], finances)
                self.assertFalse(agendas.en_cours(m, "ilse", actifs=True))
                m.joueur.update(salle="antichambre", position=[6, 4], orientation="nord-ouest")
                m.objets["fanal"].update(allume=True, combustible=60)
                from tests.support import presentes
                presentes(m)
                m.data["connus"].append("brasero")
                lignes = []
                geste = {"operation": "engager", "cible": "ilse", "outil": "", "lieu": "", "condition": "",
                         "contenu": {"condition": {"objet": "brasero", "allume": True}, "prix": 5}}
                self.assertFalse(executer(m, "marchand", geste, lignes))
                m = recharger(m)
                self.assertIn("Ilse refuse", " ".join(lignes))
                self.assertTrue(any("refuse" in b.get("texte", "") for b in m.data["bruits"]))
                self.assertFalse(any(s["type"] in ("engagement_pris", "engagement_abandonne")
                                     and s["minute"] == 353 for s in lire(m, "ilse")["memoire"]))


if __name__ == "__main__":
    unittest.main()
