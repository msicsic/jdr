"""A2 passage : charge, raccourcis, Compris et état sauvegardé, sans Luna."""
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
from donjon.commandes import analyser
from donjon.comprehension import plan_admis
from donjon.contrats_passage import RACCOURCIS, PASSAGES, DEMANDE
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import SCHEMA_SEQUENCE, etape, sequence
from donjon.paroles import SCHEMA_PAROLE, preparer_parole
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from donjon.temps import instant
from tests.test_comprehension import MJSimule, PontScript, action, dire
from tests.test_sous_obstacle import scene, passage
from tests.test_tensions import recharger, placer
from tests.test_passage import refuge, SEUIL


class ContratsPassageTests(unittest.TestCase):
    def test_cas_reel_autre_cas_et_faisabilite_dans_la_vraie_boucle(self):
        for scenario, cible, nom in (("relais", "poutre_conduite", "poutre effondrée"),
                                     ("auberge", "table_longue", "longue table")):
            for question in (True, False):
                with self.subTest(scenario=scenario, question=question), tempfile.TemporaryDirectory() as tmp:
                    m = scene(scenario, cible)
                    avant = copy.deepcopy(m.data)
                    p = passage(cible)
                    plan = Moteur(m).preparer(p)
                    self.assertEqual(m.data, avant)
                    compris = plan_admis(m, plan)
                    self.assertIn("Ramper sous", compris)
                    self.assertIn("dessous", compris)
                    self.assertIn(PASSAGES["passer_obstacle"]["public"], compris)
                    saisie = (f"est-ce que je pourrais passer sous la {nom} ?" if question
                              else f"je voudrais passer sous la {nom}")
                    chemin = Path(tmp) / "partie.json"
                    m.sauver(chemin)
                    mj = MJSimule(action(p))
                    pont = PontScript(["mj " + saisie, *([] if question else ["tenter"]), "quitter"], chemin)
                    with patch.object(jeu, "MJ", return_value=mj), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                         patch.object(Monde, "d20", side_effect=AssertionError("Ramper sans jet")), \
                         patch("sys.stdout", io.StringIO()):
                        self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], interface=pont), 0)
                    r = Monde.charger(chemin)
                    self.assertEqual(r.data, json.loads(json.dumps(mj.monde.data)))
                    self.assertEqual(r.joueur["position"], [avant["joueur"]["position"][0] + (0 if question else 2),
                                                          avant["joueur"]["position"][1]])
                    self.assertEqual(instant(r), 0 if question else 120)
                    self.assertTrue(r.objets[cible]["bloque_passage"])
                    self.assertEqual(r.data["jets"], avant["jets"])
                    self.assertIn(compris, "\n".join(pont.historique))
                    self.assertEqual(r.data["conversation"][-1]["compris"], compris)
                    reprise = PontScript(["quitter"], chemin)
                    with patch("sys.stdout", io.StringIO()):
                        jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise)
                    self.assertIn(r.data["conversation"][-1]["reponse"], "\n".join(reprise.historique))
                    self.assertEqual(Monde.charger(chemin).data, r.data)

    def test_passages_dessous_dessus_laps_decoupe_et_recharges(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            for cote in ("dessous", "dessus"):
                with self.subTest(scenario=scenario, cote=cote), patch("donjon.agendas._naissances", return_value=None):
                    m = scene(scenario, cible)
                    m.objets[cible]["passage"].update(hauteur_cm=55, degagement_cm=35)
                    Moteur(m).executer(Moteur(m).preparer(passage(cible, cote)))
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
                    self.assertEqual((regarder(m), fiche(m), scene_percue(m)),
                                     (regarder(decoupe), fiche(decoupe), scene_percue(decoupe)))

    def test_raccourcis_et_charges_explicites_identiques(self):
        for prefixe, cote in RACCOURCIS.items():
            with self.subTest(prefixe=prefixe):
                m = scene()
                m.objets["poutre_conduite"]["passage"].update(hauteur_cm=55, degagement_cm=35)
                p = analyser(m, prefixe + "la poutre effondrée")
                self.assertEqual(p, passage(methode=cote))
                autre = recharger(m)
                a, b = Moteur(m).preparer(p), Moteur(autre).preparer(passage(methode=cote))
                self.assertEqual(plan_admis(m, a), plan_admis(autre, b))
                self.assertEqual(Moteur(m).executer(a), Moteur(autre).executer(b))
                self.assertEqual(recharger(m).data, recharger(autre).data)

    def test_champs_voisins_ne_remplacent_pas_la_charge(self):
        bases = [etape("passer_obstacle", "poutre_conduite", methode="dessous"),
                 etape("franchir", "echelle"),
                 etape("franchir_obstacle", "mur", "palier", "perche", "appui_mobile", 18)]
        for base in bases:
            mobile = base["operation"] == "franchir_obstacle"
            for champ, valeur in (("cible", ""), ("methode", "finesse"), ("outil", "" if mobile else "perche"),
                                  ("destination", "" if mobile else "dessous"), ("difficulte", 12)):
                if base[champ] == valeur:
                    continue
                with self.subTest(operation=base["operation"], champ=champ):
                    p = sequence({**base, champ: valeur})
                    if jsonschema:
                        with self.assertRaises(jsonschema.ValidationError):
                            jsonschema.validate(p, SCHEMA_SEQUENCE)
                    m = scene()
                    avant = copy.deepcopy(m.data)
                    with self.assertRaises(ErreurMonde) as refus:
                        Moteur(m).preparer(p)
                    self.assertIn(champ, refus.exception.attendu)
                    self.assertEqual(m.data, avant)
        # Même cible, mauvaise opération pourtant légale : aucune échelle inventée.
        m = scene()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(sequence(etape("franchir", "poutre_conduite")))
        self.assertEqual(recharger(m).data, avant)

    def test_schema_reel_et_suite_portent_tous_les_passages(self):
        from tests.test_cache_kv_local import PrefixeKVTests
        from donjon.mj import SCHEMA, SCHEMAS_PASSAGE
        from donjon.moteur import ACTIONS
        self.assertIn("franchir", ACTIONS)
        self.assertIn("pousser", ACTIONS)
        _, _, _, schema = PrefixeKVTests()._capter_appel(nouveau_monde(), "passer sous un obstacle")
        branches = schema["properties"]["proposition"]["anyOf"]
        suite = next(s["properties"]["suite"]["anyOf"] for s in branches if "suite" in s.get("properties", {}))
        for variantes in (branches, suite):
            self.assertIn(SCHEMA_SEQUENCE, variantes)
            for s in SCHEMAS_PASSAGE:
                self.assertIn(s, variantes)
        parole = next(s for s in branches if "contenu" in s.get("properties", {})
                      and "personnage" in s["properties"])
        demande = next(s for s in parole["properties"]["contenu"]["items"]["anyOf"]
                       if s["properties"]["type"]["enum"] == ["passage"])
        self.assertEqual(demande["description"], DEMANDE["sens"])
        self.assertEqual(demande["properties"]["attribut"]["enum"], [""])
        for op in ("passer_obstacle", "franchir", "franchir_obstacle"):
            self.assertNotIn(op, SCHEMA_SEQUENCE["properties"]["etapes"]["items"]["anyOf"][0]["properties"]["operation"]["enum"])
        for op in ("pousser", "franchir"):
            base = proposition(op, "cible")
            if jsonschema is None:
                continue
            schema_action = {"anyOf": [SCHEMA, *SCHEMAS_PASSAGE]}
            jsonschema.validate(base, schema_action)
            for champ, valeur in (("methode", "finesse"), ("difficulte", 12), ("cible", ""), ("outil", "poutre")):
                with self.subTest(op=op, champ=champ), self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate({**base, champ: valeur}, schema_action)

    def test_parole_passage_destinataire_prix_et_faux_pendant(self):
        for cible in ("brune", "ilse"):
            m = refuge()
            if cible == "ilse":
                placer(m, "brune", "antichambre", (5, 2))
                placer(m, "ilse", "antichambre", SEUIL)
            for sujet in ("", cible):
                p = {"personnage": cible, "replique": "Laisse-moi passer.",
                     "_intention": f"je dis à {cible} : Laisse-moi passer.",
                     "contenu": [{"type": "passage", "sujet": sujet, "attribut": "", "valeur": ""}]}
                if jsonschema:
                    jsonschema.validate({k: v for k, v in p.items() if k != "_intention"}, SCHEMA_PAROLE)
                avant = copy.deepcopy(m.data)
                with patch.object(Monde, "d20", return_value=20):
                    travail, rapport = preparer_parole(m, p)
                self.assertEqual(m.data, avant)
                travail = recharger(travail)
                self.assertNotEqual(travail.objets[cible]["position"], list(SEUIL))
                self.assertEqual(travail.joueur["position"], m.joueur["position"])
                self.assertTrue(rapport["faits"])
            for champ, valeur in (("sujet", "aubin"), ("attribut", "lieu"),
                                  ("valeur", "dessous"), ("valeur", "²")):
                q = copy.deepcopy(p)
                q["contenu"][0][champ] = valeur
                with self.subTest(cible=cible, champ=champ), self.assertRaises(ErreurMonde) as refus:
                    preparer_parole(m, q)
                self.assertIn(champ, refus.exception.attendu)
                self.assertEqual(recharger(m).data, avant)
            # Les mêmes mots sans acte typé ne déplacent personne.
            q = {**p, "contenu": [{"type": "propos", "sujet": "", "attribut": "", "valeur": ""}]}
            travail, rapport = preparer_parole(m, q)
            self.assertEqual(recharger(travail).objets[cible]["position"], list(SEUIL))
            self.assertEqual(rapport["faits"], [])

    def test_assemblage_appui_mobile_et_poussee_gardent_leurs_effets(self):
        from tests.test_passages_publics import atelier
        from donjon.commandes import passage_memorise
        for installe in (True, False):
            with self.subTest(installe=installe):
                m = atelier(echelle=installe)
                op = "franchir" if installe else "franchir_obstacle"
                raccourci = (analyser(m, "monter echelle_test") if installe
                             else passage_memorise(m, "mur_atelier", "perche_1"))
                explicite = (sequence(etape("franchir", "echelle_test")) if installe else
                             sequence(etape("deplacer", "perche_1", "joueur"),
                                      etape("franchir_obstacle", "mur_atelier", "terrasse", "perche_1", "appui_mobile", 19)))
                autre = recharger(m)
                a, b = Moteur(m).preparer(raccourci), Moteur(autre).preparer(explicite)
                self.assertIn(PASSAGES[op]["public"], plan_admis(m, a))
                self.assertEqual((a.stat, a.dd), ("DEX", 10 if installe else 19))
                with patch.object(Monde, "d20", return_value=20):
                    Moteur(m).executer(a)
                    Moteur(autre).executer(b)
                m, autre = recharger(m), recharger(autre)
                self.assertEqual(m.joueur["salle"], "terrasse")
                self.assertEqual(m.joueur, autre.joueur)
                self.assertEqual(m.objets, autre.objets)
                self.assertEqual(bool(m.objets.get("echelle_test", {}).get("installation")), installe)
                self.assertIn("Compris :", plan_admis(m, a))
        for cible in ("brune", "ilse"):
            m = refuge()
            if cible == "ilse":
                placer(m, "brune", "antichambre", (5, 2))
                placer(m, "ilse", "antichambre", SEUIL)
            p = analyser(m, "pousser " + cible)
            self.assertEqual(p, proposition("pousser", cible))
            plan = Moteur(m).preparer(p)
            self.assertEqual((plan.stat, plan.oppose, plan.dixiemes), ("FOR", cible, 30))
            self.assertIn(PASSAGES["pousser"]["public"], plan_admis(m, plan))
            joueur = copy.deepcopy(m.joueur["position"])
            with patch.object(Monde, "d20", side_effect=[20, 1, *([10] * 100)]):
                Moteur(m).executer(plan)
            m = recharger(m)
            self.assertEqual(m.joueur["position"], joueur)
            self.assertNotEqual(m.objets[cible]["position"], list(SEUIL))
            self.assertEqual(m.data["journal"][-1]["action"]["action"], "pousser")

    def test_demande_et_propos_persistes_avec_compris_avant_affichage(self):
        from donjon.emissions import joueur as emissions
        for cible, type_ in (("brune", "passage"), ("ilse", "passage"), ("brune", "propos")):
            with self.subTest(cible=cible, type_=type_), tempfile.TemporaryDirectory() as tmp:
                m = refuge()
                if cible == "ilse":
                    placer(m, "brune", "antichambre", (5, 2))
                    placer(m, "ilse", "antichambre", SEUIL)
                saisie = f"je dis à {cible} : Laisse-moi passer."
                with patch.object(Monde, "d20", return_value=20):
                    r = dire(m, saisie, "Laisse-moi passer.", [{"type": type_, "sujet": "", "attribut": "", "valeur": ""}])
                chemin = Path(tmp) / "partie.json"
                m.sauver(chemin)
                mj = MJSimule(r)
                pont = PontScript(["mj " + saisie, "tenter", "quitter"], chemin)
                with patch.object(jeu, "MJ", return_value=mj), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                     patch.object(Monde, "d20", return_value=20), patch("sys.stdout", io.StringIO()):
                    jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], interface=pont)
                recharge = Monde.charger(chemin)
                self.assertEqual(recharge.data, json.loads(json.dumps(mj.monde.data)))
                self.assertEqual(recharge.objets[cible]["position"] == list(SEUIL), type_ == "propos")
                self.assertTrue(emissions(recharge))
                compris = recharge.data["conversation"][-1]["compris"]
                self.assertIn(DEMANDE["public"] if type_ == "passage" else "propos sans effet mécanique typé", compris)
                self.assertIn(compris, "\n".join(pont.historique))
                reprise = PontScript(["quitter"], chemin)
                with patch("sys.stdout", io.StringIO()):
                    jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise)
                self.assertIn(recharge.data["conversation"][-1]["reponse"], "\n".join(reprise.historique))


if __name__ == "__main__":
    unittest.main()
