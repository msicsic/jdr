"""Le préalable est jugé séparément du geste, puis persiste avant son affichage."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon.defi import nouveau_defi
from donjon.moteur import proposition
from donjon.operations import etape, sequence
from donjon.portee_narrative import (SCHEMA, SCHEMA_FAITS, contexte_admission,
                                     controler, controler_usages, descriptions, schema_admission)
from donjon.refus import RapportIllisible
from donjon.rendu import decrire, regarder
from donjon.scene import scene_percue
from tests.test_audits_attendu import jouer
from tests.test_ciblage_ambiance import publier
from tests import test_creation_interactive as creation
from tests.test_fouille_faits import faits, revue
from tests.test_matiere import planches, relais_avec_planches
from tests.test_qualification import PHYSIQUE_OK, qualification
from tests.test_relances_luna import action
from tests.test_tensions import recharger


class AdmissionPrealableTests(unittest.TestCase):
    def test_dossier_public_proprietes_suite_et_cardinalites_avant_appel(self):
        r = qualification("torche", planches(pieces=1), proposition("examiner", "torche"))
        r["proposition"]["ajouts"].append(dict(type="detail", ancrage="sol", nom="teinte",
                                             genre="f", texte="La teinte est mate."))
        f = {"objet:torche": {"id": "torche", "nom": "torche", "masse": 0.3},
             "secret": {"id": "cache"}, "savoirs_prives": ["cache"]}
        avant = copy.deepcopy((f, r, SCHEMA, SCHEMA_FAITS))
        d = contexte_admission(f, r["proposition"])
        a = d["admissions"][0]
        self.assertEqual(a["proprietes_etablies"], f["objet:torche"])
        self.assertNotIn("physique", a["proprietes_etablies"])
        self.assertEqual(a["proprietes_a_etablir"], {"physique": planches(pieces=1)})
        self.assertEqual(a["suite_non_executee"], r["proposition"]["suite"])
        self.assertNotIn("cache", str(d))
        entrees = descriptions(r)
        self.assertEqual(len(entrees), 3)  # Une propriété, puis nom et texte du détail.
        self.assertEqual(json.loads(entrees[0]["texte"]), a["proprietes_a_etablir"])
        s = schema_admission(entrees, r["proposition"])
        for champ, n in (("descriptions", 3), ("usages", 2)):
            self.assertEqual((s["properties"][champ]["minItems"], s["properties"][champ]["maxItems"]), (n, n))
        self.assertEqual((f, r, SCHEMA, SCHEMA_FAITS), avant)
        ancien = {"faits_narratifs_proposables": {"qualifiables": {
            "torche": {"nom": "torche", "masse": 0.3, "physique": "inconnue"}}}}
        etabli = contexte_admission(ancien, r["proposition"])["admissions"][0]["proprietes_etablies"]
        self.assertEqual(etabli, {"id": "torche", "nom": "torche", "masse": 0.3})
        d["admissions"][0]["proprietes_a_etablir"]["physique"]["pieces"] = 50
        self.assertEqual(r, avant[1])

    def test_pierre_et_eclat_pris_sans_ressaisie_et_sauvegardes(self):
        for index, (m, support, nom, matiere) in enumerate(creation.CreationInteractiveTests().scenes()):
            nom = "pierre mouillée" if index == 0 else nom
            with self.subTest(nom=nom):
                m, _, _, _ = publier(m, support, nom)
                ajout = dict(type="objet", ancrage=support, nom=nom, genre="m",
                    texte="Sa surface est mate, assez petite pour tenir dans la main.",
                    materiau=matiere, masse=0.2, mobile=True, relation="pose", capacites=[])
                r = faits(ajout, proposition("prendre", nom))
                with patch("donjon.portee_narrative.schema_admission", wraps=schema_admission) as contrat:
                    monde, texte, appels = jouer(m, "mj je ramasse " + nom,
                                                 [r, revue(r)], [], suite=("tenter",))
                contrat.assert_called_once()
                dossier = appels[1][1]["monde"]["admissions"][0]
                self.assertNotIn("demande", appels[1][1])
                self.assertNotIn("suite", appels[1][1]["proposition_faits"])
                self.assertEqual(dossier["proprietes_a_etablir"]["capacites"], [])
                self.assertEqual(dossier["suite_non_executee"]["action"], "prendre")
                id = next(id for id, o in monde.objets.items() if o["nom"] == nom)
                self.assertEqual(monde.objets[id]["lieu"], "joueur")
                self.assertNotIn(id, m.objets)
                self.assertIn("Compris :", texte)
                self.assertIn(nom, texte)
                self.assertEqual([f for f, _ in appels],
                                 ["repondre_au_joueur", "auditer_portee", "auditer_action"])
                recharge = recharger(monde)
                self.assertEqual(monde.data, recharge.data)
                self.assertIn(ajout["texte"], decrire(recharge, id, detail=True))
                self.assertEqual((regarder(monde), scene_percue(monde)),
                                 (regarder(recharge), scene_percue(recharge)))

    def test_torche_et_planches_qualifiees_puis_geste_sans_ressaisie(self):
        torche = {"forme": "barre", "matiere": "bois", "pieces": 1, "nom_piece": "",
                  "dimensions": {"longueur_cm": 50, "diametre_cm": 3, "largeur_cm": 0,
                                 "epaisseur_cm": 0, "hauteur_cm": 0}}
        for m, cible, physique, p, saisie in (
                (nouveau_defi(1985, "fixe"), "torche", torche, proposition("examiner", "torche"),
                 "et la torche, elle mesure combien ?"),
                (relais_avec_planches(), "planches", planches(),
                 sequence(etape("prelever", "planches", "joueur")), "je prends une planche du tas")):
            with self.subTest(cible=cible):
                m.data["mode_cases"] = False
                m.objets[cible]["proprietaire"] = "joueur"
                r = qualification(cible, physique, p)
                audit = revue(r)
                if cible == "torche":
                    audit["descriptions"][0]["capacites"] = ["lumiere"]
                monde, texte, appels = jouer(m, "mj " + saisie, [r, audit, PHYSIQUE_OK], [], suite=("tenter",))
                self.assertEqual([f for f, _ in appels].count("repondre_au_joueur"), 1)
                self.assertEqual([f for f, _ in appels].count("auditer_capacites"), 1)
                dossier = appels[1][1]["monde"]["admissions"][0]
                self.assertEqual(dossier["proprietes_etablies"]["masse"], m.objets[cible]["masse"])
                self.assertNotIn("physique", dossier["proprietes_etablies"])
                self.assertEqual(dossier["proprietes_a_etablir"], {"physique": physique})
                self.assertEqual(len(appels[1][1]["descriptions"]), 1)
                recharge = recharger(monde)
                self.assertEqual(recharge.objets[cible], monde.objets[cible])
                self.assertEqual(recharge.objets[cible]["physique"]["matiere"], physique["matiere"])
                for champ, valeur in physique["dimensions"].items():
                    if valeur:
                        self.assertEqual(recharge.objets[cible]["physique"]["dimensions"][champ], valeur)
                self.assertNotIn("physique", m.objets[cible])
                if cible == "planches":
                    self.assertEqual(recharge.objets["planches_1"]["lieu"], "joueur")
                    self.assertEqual(sum(recharge.objets[id]["physique"]["pieces"]
                                         for id in ("planches", "planches_1")), physique["pieces"])
                    self.assertIn("Compris :", texte)
                else:
                    self.assertIn(decrire(recharge, cible, detail=True), texte)
                    self.assertIn("50 cm", texte)
                self.assertEqual((regarder(monde), scene_percue(monde)),
                                 (regarder(recharge), scene_percue(recharge)))

    def test_suite_ne_dispense_jamais_d_un_refus_indice_absence_ou_capacite(self):
        for m, support, nom, matiere in creation.CreationInteractiveTests().scenes():
            m = recharger(m)
            temoin, _, _ = jouer(m, "mj j'examine ce support",
                                 [action(proposition("examiner", support))], [])
            for cause in ("indice", "absence", "capacite"):
                with self.subTest(support=support, cause=cause):
                    ajout = dict(type="objet", ancrage=support, nom=nom, genre="m",
                        texte={"indice": "Cette marque révèle un passage caché.",
                               "absence": "Il n'y a rien derrière la porte.",
                               "capacite": "Son bord permet de couper."}[cause],
                        materiau=matiere, masse=0.2, mobile=True, relation="pose", capacites=[])
                    r = faits(ajout, proposition("prendre", nom))
                    audit = revue(r, perception=cause == "absence", indice=cause == "indice")
                    if cause == "capacite":
                        audit["descriptions"][-1]["capacites"] = ["couper"]
                    monde, texte, appels = jouer(m, "mj je ramasse " + nom,
                        [r, audit, action(proposition("examiner", support))], [])
                    self.assertEqual(monde.objets, temoin.objets)
                    self.assertEqual(recharger(monde).objets, temoin.objets)
                    self.assertNotIn(ajout["texte"], texte)
                    self.assertNotIn(ajout["texte"], str(monde.data))
                    self.assertIn(decrire(recharger(monde), support, detail=True), texte)
                    refus = appels[2][1]["controle_narratif"][0]
                    self.assertTrue(refus["attendu"])
                    if cause != "capacite":
                        self.assertIn("conserver proposition.suite", refus["attendu"])
                        self.assertNotIn("sans nouvel ajout", refus["attendu"])

    def test_rapport_incoherent_reste_illisible_meme_avec_suite(self):
        r = qualification("torche", planches(), proposition("examiner", "torche"))
        bon = revue(r)
        for cle in ("usages", "descriptions"):
            for lignes in ([], bon[cle] * 2):
                mauvais = {**bon, cle: lignes}
                with self.subTest(cle=cle, n=len(lignes)), self.assertRaises(RapportIllisible):
                    controler_usages(r["proposition"], mauvais)
                    controler(descriptions(r), mauvais)

    def test_capacite_etablie_distinguee_de_la_propriete_nouvelle(self):
        r = qualification("torche", planches(pieces=1), proposition("examiner", "torche"))
        public = {"objet:torche": {"id": "torche", "nom": "torche", "luminosite": 2}}
        public["objet:torche"]["constats_capacites"] = [
            {"capacite": "son", "issue": "etablie", "etat_objet_actuel": True}]
        entrees = descriptions(r, public)
        audit = revue(r)
        # Le jugement réel de la passe 431 lit la lumière du sujet établi.
        audit["descriptions"][0]["capacites"] = ["lumiere"]
        self.assertFalse(controler(entrees, audit))
        audit["descriptions"][0]["capacites"] = []
        self.assertFalse(controler(entrees, audit))  # Elle n'a pas à être réannoncée.
        audit["descriptions"][0]["capacites"] = ["couper"]
        self.assertTrue(controler(entrees, audit))
        self.assertNotIn("luminosite", r["proposition"]["ajouts"][0])


if __name__ == "__main__":
    unittest.main()
