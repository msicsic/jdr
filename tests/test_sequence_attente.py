"""A2 : mêmes contrats sur le schéma, les raccourcis, l'état et le plan relu."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.commandes import attente
from donjon.comprehension import plan_admis
from donjon.contrats_sequence import ATTENTES, COMPOSITION
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence, SCHEMA_SEQUENCE
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from donjon.temps import instant
from tests.test_comprehension import MJSimule, PontScript, action
from tests.test_tensions import recharger, relais
from tests.support import calme


class SequenceAttenteTests(unittest.TestCase):
    def test_cas_reel_autre_bien_et_faux_pendant_apres_reprise(self):
        for cible in ("crochets", "bourse_test"):
            for methode in ("finesse", "simple"):
                with self.subTest(cible=cible, methode=methode), tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
                    m = nouveau_monde()
                    m.joueur["salle"] = "echoppe"
                    # Même mécanisme, seconde cible présente dans la scène d'auteur.
                    if cible == "bourse_test":
                        m.objets[cible] = {**copy.deepcopy(m.objets["crochets"]), "id": cible,
                                           "nom": "bourse de cuir", "genre": "f", "pluriel": False,
                                           "aliases": ["bourse"]}
                        m.data["connus"].append(cible)
                    saisie = ("J'attends que Gorm ait le dos tourné pour prendre discrètement les crochets"
                              if cible == "crochets" and methode == "finesse" else
                              "je guette une occasion puis dérobe la bourse" if methode == "finesse" else
                              "je dérobe directement " + cible)
                    p = proposition("voler", cible, methode=methode)
                    initial = copy.deepcopy(m.data)
                    plan = Moteur(m).preparer(p)
                    self.assertEqual(m.data, initial)
                    attendu = plan_admis(m, plan)
                    operations = [e["operation"] for e in plan.etapes]
                    self.assertEqual(operations, ["patienter", "deplacer"] if methode == "finesse" else ["deplacer"])
                    self.assertEqual(plan.minutes, 3 if methode == "finesse" else 1)
                    self.assertEqual(plan.dd, 12 if methode == "finesse" else 14)
                    if methode == "finesse":
                        self.assertIn(ATTENTES["occasion"]["public"], attendu)
                    else:
                        self.assertNotIn("Guetter", attendu)
                    chemin = Path(tmp) / "partie.json"
                    m.sauver(chemin)
                    faux = MJSimule(action(p))
                    pont = PontScript(["mj " + saisie, "tenter", "quitter"], chemin)
                    with patch.object(jeu, "MJ", return_value=faux), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                         patch.object(Monde, "d20", return_value=20), patch("sys.stdout", io.StringIO()):
                        self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], interface=pont), 0)
                    recharge = Monde.charger(chemin)
                    self.assertEqual(recharge.objets[cible]["lieu"], "joueur")
                    self.assertEqual(recharge.data, json.loads(json.dumps(faux.monde.data)))
                    self.assertEqual(recharge.data["conversation"][-1]["compris"], attendu)
                    self.assertIn(attendu, "\n".join(pont.historique))
                    # Le raccourci et ses étapes explicites produisent le même monde complet.
                    explicite = Monde(copy.deepcopy(initial))
                    with patch.object(Monde, "d20", return_value=20):
                        Moteur(explicite).executer(Moteur(explicite).preparer(sequence(*plan.etapes), plan.origine))
                    for champ in ("objets", "joueur", "minutes", "dixiemes", "chronique", "relations_pnj", "jets"):
                        self.assertEqual(recharge.data.get(champ), explicite.data.get(champ))
                    reprise = PontScript(["quitter"], chemin)
                    with patch("sys.stdout", io.StringIO()):
                        self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise), 0)
                    self.assertIn(recharge.data["conversation"][-1]["reponse"], "\n".join(reprise.historique))
                    self.assertEqual(Monde.charger(chemin).data, recharge.data)
                    self.assertEqual((regarder(recharge), fiche(recharge), scene_percue(recharge)),
                                     (regarder(faux.monde), fiche(faux.monde), scene_percue(faux.monde)))

    def test_aucun_champ_voisin_ne_remplace_la_charge_attendue(self):
        for base in (proposition("attendre"), proposition("attendre", "30"), etape("patienter")):
            for champ, valeur in (("outil", "couteau"), ("methode", "finesse"), ("difficulte", 12)):
                m = nouveau_monde()
                p = {**base, champ: valeur}
                if "operation" in p:
                    p = sequence(p)
                avant = copy.deepcopy(m.data)
                with self.subTest(base=base, champ=champ), self.assertRaises(ErreurMonde) as refus:
                    Moteur(m).preparer(p)
                self.assertIn(champ, refus.exception.attendu)
                self.assertEqual(m.data, avant)
        for champ in ("cible", "destination", "condition"):
            p = sequence({**etape("patienter"), champ: "marchand"})
            with self.subTest(champ=champ), self.assertRaises(ErreurMonde) as refus:
                Moteur(nouveau_monde()).preparer(p)
            self.assertIn(champ, refus.exception.attendu)

    def test_duree_et_occasion_laps_decoupe_et_plan_sauve(self):
        def calme_sans_agenda():
            m = relais()
            calme(m, "marchand", "brune", "ilse", "aubin")
            for o in m.objets.values():
                if "profil" in o:
                    o["profil"]["agendas"] = []
            return m
        with patch("donjon.agendas._naissances", return_value=None):
            for p, secondes in ((attente("2 min"), 120), (sequence(etape("patienter")), 120),
                                (attente(""), 300), (proposition("attendre"), 300)):
                with self.subTest(p=p):
                    m = calme_sans_agenda()
                    decoupe = m.copier()
                    debut = instant(m)
                    moteur = Moteur(m)
                    plan = moteur.preparer(p)
                    compris = plan_admis(m, plan)
                    sortie = moteur.executer(plan)
                    m.memoriser("attente", sortie + "\n" + compris, "resultat_moteur", complet=True)
                    recharge = recharger(m)
                    self.assertEqual(recharge.data, m.data)
                    self.assertEqual(instant(recharge) - debut, secondes * 10)
                    self.assertIn(compris, recharge.data["conversation"][-1]["reponse"])
                    for _ in range(secondes // 15):
                        if p["action"] == "composer":
                            tranche = copy.copy(plan.plans[0])
                            tranche.minutes, tranche.dixiemes = 0, 150
                            Moteur._terminer_etape(decoupe, tranche, [], (), "patienter", "simple")
                        else:
                            moteur = Moteur(decoupe)
                            moteur.executer(moteur.preparer(attente("15 s")))
                        decoupe = recharger(decoupe)
                    # Les journaux portent le découpage ; le monde simulé reste entier.
                    exclus = {"journal", "revision", "conversation"}
                    self.assertEqual({k: v for k, v in recharge.data.items() if k not in exclus},
                                     {k: v for k, v in decoupe.data.items() if k not in exclus})
                    self.assertEqual((regarder(recharge), fiche(recharge), scene_percue(recharge)),
                                     (regarder(decoupe), fiche(decoupe), scene_percue(decoupe)))

    def test_schema_charge_occasion_fermee_et_sens_partage(self):
        schema = SCHEMA_SEQUENCE
        self.assertEqual(schema["properties"]["etapes"]["maxItems"], COMPOSITION["maximum"])
        autres, occasion, *_ = schema["properties"]["etapes"]["items"]["anyOf"]
        self.assertNotIn("patienter", autres["properties"]["operation"]["enum"])
        self.assertEqual(occasion["description"], ATTENTES["occasion"]["sens"])
        self.assertFalse(occasion["additionalProperties"])
        self.assertEqual(set(occasion["required"]), set(etape("patienter")))
        for champ, v in etape("patienter").items():
            self.assertEqual(occasion["properties"][champ]["enum"], [v])
        from donjon.mj import SCHEMA, SCHEMA_ATTENTE
        self.assertNotIn("attendre", SCHEMA["properties"]["action"]["enum"])
        for champ, v in proposition("attendre").items():
            if champ not in ("cible", "justification"):
                self.assertEqual(SCHEMA_ATTENTE["properties"][champ]["enum"], [v])

    def test_schema_effectif_et_suite_utilisent_la_meme_attente(self):
        from tests.test_cache_kv_local import PrefixeKVTests
        from donjon.mj import SCHEMA_ATTENTE
        _, _, _, schema = PrefixeKVTests()._capter_appel(nouveau_monde(), "Je guette une occasion.")
        branches = schema["properties"]["proposition"]["anyOf"]
        suite = next(s["properties"]["suite"] for s in branches if "suite" in s.get("properties", {}))
        for variantes in (branches, suite["anyOf"]):
            attentes = [s for s in variantes if "attendre" in s.get("properties", {}).get("action", {}).get("enum", [])]
            self.assertEqual(attentes, [SCHEMA_ATTENTE])
            self.assertIn(SCHEMA_SEQUENCE, variantes)


if __name__ == "__main__":
    unittest.main()
