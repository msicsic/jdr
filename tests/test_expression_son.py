"""A2 : contrat sonore, charge réelle, rendu public et partie rechargée."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    import jsonschema
except ImportError:
    jsonschema = None

import jeu
from donjon.commandes import analyser, heler, repondre
from donjon.comprehension import plan_admis
from donjon.contrats_son import AUDITION, FORMES_SONORES, RACCOURCIS_VOCAUX, emissions, raccourci
from donjon.improvisation import SCHEMA as SCHEMA_IMPROVISATION, effet, issue, proposition as improviser
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.operations import SCHEMA_SEQUENCE, etape, sequence
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from donjon.temps import instant
from tests.test_comprehension import MJSimule, PontScript, action
from tests.test_paroles import relais
from tests.test_tensions import recharger


def expression(forme=None, bruit=0):
    return improviser("Brouillon sans autorité sur le monde", issue("Une cloche cachée répond.",
                      [effet("son", "joueur", texte=forme, valeur=1)] if forme else []), bruit=bruit)


class ExpressionSonTests(unittest.TestCase):
    def test_cas_reel_autre_expression_et_faux_pendant_dans_la_boucle(self):
        for saisie, forme in (("je fredonne doucement", "voix_melodique"),
                              ("je frappe un rythme avec mes mains", "corps_rythmique"),
                              ("je m'étire en silence", None)):
            with self.subTest(saisie=saisie), tempfile.TemporaryDirectory() as tmp:
                m = relais()
                p = expression(forme)
                avant = copy.deepcopy(m.data)
                plan = Moteur(m).preparer(p)
                self.assertEqual(m.data, avant)
                self.assertEqual((plan.stat, plan.dd, plan.bruit), ("", 0, 1 if forme else 0))
                compris = plan_admis(m, plan)
                if forme:
                    self.assertIn(FORMES_SONORES[forme], compris)
                    self.assertIn(AUDITION, compris)
                else:
                    self.assertIn("aucun son prévu parmi les effets du geste", compris)
                self.assertNotIn("cloche cachée", compris)
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                mj = MJSimule(action(p))
                pont = PontScript(["mj " + saisie, "tenter", "quitter"], chemin)
                with patch.object(jeu, "MJ", return_value=mj), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                     patch.object(Monde, "d20", side_effect=AssertionError("Expression simple sans jet")), \
                     patch("sys.stdout", io.StringIO()):
                    self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], interface=pont), 0)
                recharge = Monde.charger(chemin)
                self.assertEqual(recharge.data, json.loads(json.dumps(mj.monde.data)))
                self.assertEqual(recharge.data["conversation"][-1]["compris"], compris)
                self.assertIn(compris, "\n".join(pont.historique))
                self.assertEqual(set(recharge.objets), set(avant["objets"]))
                self.assertEqual(len(recharge.data.get("sons", [])), 1 if forme else 0)
                if forme:
                    self.assertEqual(recharge.data["sons"][-1]["forme"], forme)
                    self.assertIn("marchand", recharge.data["sons"][-1]["auditeurs"])
                self.assertNotIn("Une cloche cachée répond", recharge.data["conversation"][-1]["reponse"])
                reprise = PontScript(["quitter"], chemin)
                with patch("sys.stdout", io.StringIO()):
                    self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise), 0)
                self.assertIn(recharge.data["conversation"][-1]["reponse"], "\n".join(reprise.historique))
                self.assertEqual(Monde.charger(chemin).data, recharge.data)
                self.assertEqual((regarder(recharge), fiche(recharge), scene_percue(recharge)),
                                 (regarder(mj.monde), fiche(mj.monde), scene_percue(mj.monde)))

    def test_son_retenu_apres_un_meme_laps_decoupe_et_recharges(self):
        # Même émission une fois, puis même activité de repos ; seul le découpage change.
        for forme in ("voix_melodique", "corps_rythmique", None):
            with self.subTest(forme=forme), patch("donjon.agendas._naissances", return_value=None):
                m = nouveau_monde()
                Moteur(m).executer(Moteur(m).preparer(expression(forme)))
                decoupe = recharger(m)
                debut = instant(m)
                for monde, tranches in ((m, [1200]), (decoupe, [150] * 8)):
                    for duree in tranches:
                        plan = Moteur(monde).preparer(proposition("attendre"))
                        plan.minutes, plan.dixiemes = 0, duree
                        Moteur._terminer_etape(monde, plan, [], (), "attendre", "simple")
                        monde.data = recharger(monde).data
                m = recharger(m)
                self.assertEqual(instant(m) - debut, 1200)
                self.assertEqual(m.data, decoupe.data)
                self.assertEqual(len(m.data.get("sons", [])), 1 if forme else 0)
                self.assertEqual((regarder(m), fiche(m), scene_percue(m)),
                                 (regarder(decoupe), fiche(decoupe), scene_percue(decoupe)))

    def test_raccourcis_emission_explicite_et_reponses_ont_le_meme_sens(self):
        for saisie, methode in RACCOURCIS_VOCAUX.items():
            with self.subTest(saisie=saisie):
                m = nouveau_monde()
                p = analyser(m, saisie)
                self.assertEqual(p, sequence(etape("emettre_son", "joueur", methode=methode)))
                explicite = recharger(m)
                plans = [Moteur(m).preparer(p), Moteur(explicite).preparer(raccourci("joueur", methode))]
                self.assertEqual(plan_admis(m, plans[0]), plan_admis(explicite, plans[1]))
                self.assertIn(AUDITION, plan_admis(m, plans[0]))
                sorties = [Moteur(m).executer(plans[0]), Moteur(explicite).executer(plans[1])]
                self.assertEqual(sorties[0], sorties[1])
                self.assertEqual(recharger(m).data, recharger(explicite).data)
                self.assertNotIn("Gorm", sorties[0])  # l'auditeur distant ne se révèle pas.
        m = relais()
        m.objets["cloche_test"] = objet("cloche_test", "cloche", "outil", "joueur", sonorite=2)
        self.assertEqual(analyser(m, "sonner cloche"), raccourci("cloche_test", "simple"))
        self.assertEqual(heler(m, "je crie « Gorm ? »"), raccourci("marchand", "heler"))
        from donjon import appel, pnj
        from donjon.noms import apprendre
        apprendre(m, "marchand", "joueur")
        pnj.heler(m, "marchand", "joueur", [])
        m = recharger(m)
        for methode, sorte in appel.METHODES.items():
            with self.subTest(methode=methode):
                p = repondre(m, appel.PHRASES[sorte])
                self.assertEqual(p, raccourci("marchand", methode))
                plan = Moteur(m).preparer(p)
                self.assertIn(appel.PHRASES[sorte], plan_admis(m, plan))
                self.assertEqual(plan.plans[0].effets, [(methode, "joueur", "marchand")])
                copie = recharger(m)
                texte = Moteur(copie).executer(Moteur(copie).preparer(p))
                copie = recharger(copie)
                self.assertIn(appel.PHRASES[sorte], texte)
                self.assertTrue(any(appel.PHRASES[sorte] in c["texte"] for c in copie.data["chronique"]))

    def test_champs_voisins_refuses_sans_mutation(self):
        for methode in emissions():
            cible = "joueur" if methode in ("appel", "cri", "sifflement") else "marchand"
            base = etape("emettre_son", cible, methode=methode)
            for champ, valeur in (("destination", "echoppe"), ("outil", "couteau"),
                                  ("difficulte", 12), ("methode", "percussion")):
                p = sequence({**base, champ: valeur})
                m = nouveau_monde()
                avant = copy.deepcopy(m.data)
                with self.subTest(methode=methode, champ=champ):
                    with self.assertRaises(ErreurMonde) as refus:
                        Moteur(m).preparer(p)
                    self.assertIn(champ, refus.exception.attendu)
                    self.assertEqual(m.data, avant)
        base = effet("son", "joueur", texte="voix_melodique", valeur=1)
        for champ, valeur in (("destination", "echoppe"), ("cible", "marchand"),
                              ("texte", "Une voix cachée répond."), ("valeur", 0), ("valeur", 4)):
            p = expression()
            p["reussite"]["effets"] = [{**base, champ: valeur}]
            with self.subTest(champ=champ, valeur=valeur):
                m = nouveau_monde()
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde):
                    Moteur(m).preparer(p)
                self.assertEqual(m.data, avant)
        # Une conséquence sonore est une charge, pas une intensité ambiante ou une prose.
        for p in (expression("voix_melodique"), expression("corps_bref"), expression(bruit=3)):
            m = nouveau_monde()
            plan = Moteur(m).preparer(p)
            sonore = bool(p["reussite"]["effets"])
            self.assertEqual(any(e[0] == "son_improvise" for e in plan.effets), sonore)
            if not sonore:
                self.assertIn("aucun son prévu parmi les effets du geste", plan_admis(m, plan))

    def test_schema_effectivement_emis_et_suite_conservent_la_famille(self):
        from tests.test_cache_kv_local import PrefixeKVTests
        _, _, _, schema = PrefixeKVTests()._capter_appel(nouveau_monde(), "je fredonne doucement")
        branches = schema["properties"]["proposition"]["anyOf"]
        suite = next(s["properties"]["suite"] for s in branches if "suite" in s.get("properties", {}))
        for variantes in (branches, suite["anyOf"]):
            self.assertIn(SCHEMA_SEQUENCE, variantes)
            self.assertIn(SCHEMA_IMPROVISATION, variantes)
            son = SCHEMA_IMPROVISATION["properties"]["reussite"]["properties"]["effets"]["items"]["anyOf"][1]
            self.assertEqual(son["properties"]["texte"]["enum"], list(FORMES_SONORES))
        autres, _, *sons = SCHEMA_SEQUENCE["properties"]["etapes"]["items"]["anyOf"]
        self.assertNotIn("emettre_son", autres["properties"]["operation"]["enum"])
        self.assertEqual({s["properties"]["methode"]["enum"][0] for s in sons}, set(emissions()))
        self.assertTrue(all(s["additionalProperties"] is False for s in sons))

    @unittest.skipIf(jsonschema is None, "jsonschema, dépendance facultative, absente")
    def test_schema_refuse_les_champs_voisins_et_accepte_les_charges(self):
        for methode in emissions():
            cible = "joueur" if methode in ("appel", "cri", "sifflement") else "marchand"
            base = etape("emettre_son", cible, methode=methode)
            jsonschema.validate(sequence(base), SCHEMA_SEQUENCE)
            for champ, valeur in (("destination", "echoppe"), ("outil", "couteau"),
                                  ("difficulte", 12), ("methode", "percussion")):
                with self.subTest(methode=methode, champ=champ), self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(sequence({**base, champ: valeur}), SCHEMA_SEQUENCE)
        for forme in [*FORMES_SONORES, None]:
            jsonschema.validate(expression(forme), SCHEMA_IMPROVISATION)
        base = effet("son", "joueur", texte="voix_melodique", valeur=1)
        for champ, valeur in (("destination", "echoppe"), ("cible", "marchand"),
                              ("texte", "Une voix cachée répond."), ("valeur", 0), ("valeur", 4)):
            p = expression()
            p["reussite"]["effets"] = [{**base, champ: valeur}]
            with self.subTest(champ=champ, valeur=valeur), self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(p, SCHEMA_IMPROVISATION)

    def test_sonner_un_objet_ne_devient_pas_un_coup_qui_le_blesse(self):
        for id, nom in (("cloche_test", "cloche"), ("gong_test", "gong")):
            with self.subTest(id=id):
                m = nouveau_monde()
                m.objets[id] = objet(id, nom, "outil", "joueur", sonorite=2)
                integrite = m.objets[id]["integrite"]
                p = analyser(m, "sonner " + nom)
                moteur = Moteur(m)
                plan = moteur.preparer(p)
                compris = plan_admis(m, plan)
                self.assertEqual(plan.plans[0].effets, [("emettre_son", id, "objet")])
                sortie = moteur.executer(plan)
                m.memoriser("sonner " + nom, sortie + "\n" + compris, "resultat_moteur", complet=True)
                m = recharger(m)
                self.assertEqual(m.objets[id]["integrite"], integrite)
                self.assertEqual(m.data["sons"][-1]["objet"], id)
                self.assertIn("Produire un son avec", m.data["conversation"][-1]["reponse"])
                self.assertIn(AUDITION, m.data["conversation"][-1]["reponse"])

    def test_reussite_et_echec_gardent_chacun_leur_propre_son(self):
        p = improviser("Essai sonore", issue("Succès.", [effet("son", "joueur", texte="voix_melodique", valeur=2)]),
                       issue("Échec.", [effet("son", "joueur", texte="souffle", valeur=1)]), stat="CHA", difficulte=12)
        for jet, forme in ((20, "voix_melodique"), (1, "souffle")):
            with self.subTest(jet=jet):
                m = nouveau_monde()
                plan = Moteur(m).preparer(p)
                compris = plan_admis(m, plan)
                self.assertIn("En cas de réussite : " + FORMES_SONORES["voix_melodique"], compris)
                self.assertIn("En cas d'échec : " + FORMES_SONORES["souffle"], compris)
                with patch.object(Monde, "d20", return_value=jet):
                    sortie = Moteur(m).executer(plan)
                m.memoriser("Essai sonore", sortie + "\n" + compris, "resultat_moteur", complet=True)
                m = recharger(m)
                self.assertEqual([s["forme"] for s in m.data["sons"]], [forme])
                self.assertIn(FORMES_SONORES[forme], sortie)
                self.assertIn(compris, m.data["conversation"][-1]["reponse"])


if __name__ == "__main__":
    unittest.main()
