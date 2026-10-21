import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.carte import objets_visibles_cases
from donjon.defi import nouveau_defi
from donjon.faits_locaux import catalogue, preparer_faits
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire
from donjon.spatial import champ_visible, installer as installer_cases, position_cible
from donjon.spatial import memoriser


class TransactionsNarrativesTests(unittest.TestCase):
    def test_transition_deplace_objets_fixe_et_pose_sans_garder_leur_ancrage(self):
        m = nouveau_monde()
        installer_cases(m)
        m.joueur["orientation"] = "ouest"  # Placement d'auteur : il regarde le mur ouest.
        ajouts = [
            {"type": "objet", "ancrage": "antichambre_murs", "nom": "grelot de fer",
             "genre": "m", "texte": "Un petit grelot est fixé à la pierre.",
             "materiau": "fer", "masse": 0.1, "mobile": True, "relation": "fixe", "capacites": []},
            {"type": "objet", "ancrage": "antichambre_sol", "nom": "galet poli",
             "genre": "m", "texte": "Sa surface est lisse.",
             "materiau": "pierre", "masse": 0.2, "mobile": True, "relation": "pose", "capacites": []},
        ]
        m, _, etablis = preparer_faits(m, {"ajouts": ajouts})
        fixe, pose = (e["objet"] for e in etablis)
        memoriser(m)
        self.assertEqual(m.objets[fixe]["ancrage_carte"], [-1, 2])
        m.data["transitions_scenario"] = [{
            "id": "transport", "conditions": [{"objet": fixe, "champ": "lieu",
                                               "valeur": "antichambre_murs"}],
            "effets": [{"operation": "deplacer", "objet": id,
                        "depuis": source, "lieu": "echoppe", "position": [1, 2]}
                       for id, source in ((fixe, "antichambre_murs"),
                                          (pose, "antichambre_sol"))],
            "annonce": "Les deux objets ont été portés dans la conduite.",
        }]
        m.verifier()
        m, _, _ = preparer_faits(m, {"ajouts": [{"type": "evolution", "ancrage": "transport"}]})
        memoriser(m)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "transport.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        for id in (fixe, pose):
            self.assertEqual(reprise.objets[id]["lieu"], "echoppe")
            self.assertEqual(reprise.objets[id]["position"], [1, 2])
            self.assertEqual(reprise.objets[id]["relation_support"], "pose")
            self.assertNotIn("ancrage_carte", reprise.objets[id])
            self.assertNotIn("position_autonome", reprise.objets[id])
            souvenir = reprise.data["souvenirs_visuels"].get(id)
            if souvenir:
                self.assertEqual(souvenir["salle"], "echoppe")
                self.assertEqual(souvenir["position"], [1, 2])
        self.assertFalse(reprise.objets[fixe]["attache"])
        reprise.joueur.update(salle="echoppe", position=[1, 2])
        memoriser(reprise)
        self.assertEqual(position_cible(reprise, fixe), (1, 2))
        self.assertTrue(reprise.visible(fixe))

    def test_objet_autonome_cree_puis_ramasse_apres_rechargement(self):
        ajout = {"type": "objet", "ancrage": "antichambre_sol",
                 "nom": "pendentif de cuivre", "genre": "m",
                 "texte": "Sa surface porte une patine verte.",
                 "materiau": "cuivre", "masse": 0.1, "mobile": True, "relation": "pose", "capacites": []}
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [ajout]}}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", return_value=reponse),
                  patch("builtins.input", side_effect=["mj Que remarqué-je ici ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            cree = Monde.charger(chemin)
            id = cree.trouver("pendentif de cuivre")
            self.assertIn("pendentif de cuivre", sortie.getvalue())
            self.assertTrue(cree.objets[id]["mobile"])
            self.assertEqual(cree.objets[id]["masse"], 0.1)
            self.assertIn("patine verte", decrire(cree, id, detail=True))
            self.assertIn(id, [o["id"] for o, _, _ in objets_visibles_cases(cree, champ_visible(cree))])

            with (patch("builtins.input", side_effect=["prendre pendentif de cuivre", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
            repris = Monde.charger(chemin)
            self.assertEqual(repris.objets[id]["lieu"], "joueur")
            self.assertNotIn(id, [o["id"] for o, _, _ in objets_visibles_cases(repris, champ_visible(repris))])
            self.assertIn("Tu prends le pendentif", sortie.getvalue())

    def test_transition_conditionnelle_deplace_objet_et_change_objectif(self):
        m = nouveau_defi(depart="fixe")
        secours = objet("secours", "cloche de secours", "tresor", "chambre_cloche",
                       genre="f", materiau="bronze", masse=1, mobile=True)
        m.objets["secours"] = secours
        m.objets["cloche"]["integrite"] = 0
        # La condition est vraie, mais Corvus ne peut pas encore constater la casse.
        m.joueur.update(salle="chambre_cloche", position=[2, 3])
        m.data["transitions_scenario"] = [{
            "id": "relais_secours",
            "conditions": [{"objet": "cloche", "champ": "integrite", "valeur": 0}],
            "effets": [
                {"operation": "deplacer", "objet": "secours", "depuis": "chambre_cloche",
                 "lieu": "antichambre",
                 "position": [1, 3]},
                {"operation": "objectif", "objectif_avant": "cloche", "objectif": {
                    "objet": "secours", "lieu": "joueur", "salle": "antichambre",
                    "message": "OBJECTIF ATTEINT : la cloche de secours est au refuge."},
                 "resume": "Rapporter la cloche de secours au refuge."},
            ],
            "annonce": "La première cloche est brisée. Une cloche de secours est accessible au refuge.",
        }]
        m.verifier()
        self.assertIn("relais_secours", catalogue(m)["evolutions"])
        loin = m.copier()
        loin.joueur.update(salle="antichambre", position=[1, 3])
        self.assertNotIn("relais_secours", catalogue(loin)["evolutions"])
        deplace = m.copier()
        deplace.objets["secours"]["lieu"] = "antichambre"
        self.assertNotIn("relais_secours", catalogue(deplace)["evolutions"])
        change = m.copier()
        change.data["objectif_partie"]["objet"] = "secours"
        self.assertNotIn("relais_secours", catalogue(change)["evolutions"])
        reponse = {"mode": "etablir_faits", "texte": "",
                   "faits": ["faits_narratifs_proposables"],
                   "proposition": {"ajouts": [{"type": "evolution",
                                               "ancrage": "relais_secours"}]}}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", return_value=reponse),
                  patch("builtins.input", side_effect=["mj Que faire de la cloche brisée ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            repris = Monde.charger(chemin)
            self.assertIn("cloche de secours", sortie.getvalue())
            self.assertEqual(repris.objets["secours"]["lieu"], "antichambre")
            self.assertEqual(repris.objets["secours"]["position"], [1, 3])
            self.assertEqual(repris.data["objectif_partie"]["objet"], "secours")
            self.assertIn("relais_secours", repris.data["transitions_effectuees"])
            self.assertNotIn("relais_secours", catalogue(repris)["evolutions"])
            with self.assertRaises(ErreurMonde):
                preparer_faits(repris, reponse["proposition"])

    def test_evolution_non_declenchee_et_objet_mal_forme_restent_atomiques(self):
        m = nouveau_monde()
        m.data["transitions_scenario"] = [{
            "id": "deplacement", "conditions": [{"objet": "anneau", "champ": "integrite", "valeur": 0}],
            "effets": [{"operation": "deplacer", "objet": "anneau", "depuis": "porte",
                        "lieu": "antichambre",
                        "position": [1, 2]}], "annonce": "L'anneau tombe au sol.",
        }]
        m.verifier()
        self.assertNotIn("deplacement", catalogue(m)["evolutions"])
        for ajout in (
            {"type": "evolution", "ancrage": "deplacement"},
            {"type": "objet", "ancrage": "antichambre_murs", "nom": "bague",
             "genre": "f", "texte": "Une bague est posée là.",
             "materiau": "argent", "masse": -1, "mobile": True, "relation": "pose", "capacites": []},
        ):
            with self.subTest(ajout=ajout), self.assertRaises(ErreurMonde):
                preparer_faits(m, {"ajouts": [{"type": "detail", "ancrage": "antichambre_murs",
                                                "nom": "rayure", "genre": "f",
                                                "texte": "Une rayure suit la pierre."}, ajout]})
            self.assertFalse(any(o.get("origine_description") == "MJ" for o in m.objets.values()))

    def test_objet_sur_surface_etendue_ne_suit_pas_le_joueur(self):
        m = nouveau_monde()
        installer_cases(m)
        depart = tuple(m.joueur["position"])
        travail, _, etablis = preparer_faits(m, {"ajouts": [{
            "type": "objet", "ancrage": "antichambre_sol", "nom": "bouton de cuivre",
            "genre": "m", "texte": "Un petit bouton rond repose sur la pierre.",
            "materiau": "cuivre", "masse": 0.01, "mobile": True, "relation": "pose", "capacites": []}]})
        id = etablis[0]["objet"]
        self.assertEqual(position_cible(travail, id), depart)
        travail.joueur["position"] = [depart[0] + 1, depart[1]]
        self.assertEqual(position_cible(travail, id), depart)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            travail.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(position_cible(reprise, id), depart)

    def test_objet_contenu_est_cache_par_contenant_ferme_et_persiste(self):
        m = nouveau_monde()
        m.objets["coffre"]["lieu"] = m.joueur["salle"]
        m.objets["coffre"]["ouverte"] = True
        m.objets["coffre"]["verrouillee"] = False
        travail, annonce, etablis = preparer_faits(m, {"ajouts": [{
            "type": "objet", "ancrage": "coffre", "nom": "galet bleu", "genre": "m",
            "texte": "Sa surface est lisse.", "materiau": "pierre", "masse": 0.1,
            "mobile": True, "relation": "contenu", "capacites": []}]})
        id = etablis[0]["objet"]
        self.assertIn("dans le coffre", annonce)
        self.assertIn("dans le coffre", decrire(travail, id))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            travail.sauver(chemin)
            reprise = Monde.charger(chemin)
            reprise.objets["coffre"]["ouverte"] = False
            self.assertFalse(reprise.visible(id))
            reprise.objets["coffre"]["ouverte"] = True
            Moteur(reprise).executer(Moteur(reprise).preparer(proposition("prendre", id)))
            reprise.sauver(chemin)
            self.assertEqual(Monde.charger(chemin).objets[id]["lieu"], "joueur")

    def test_relation_incompatible_et_fixation_non_amovible(self):
        m = nouveau_monde()
        base = {"type": "objet", "ancrage": "antichambre_murs",
                "nom": "plaquette de fer", "genre": "f", "texte": "Le fer est terni.",
                "materiau": "fer", "masse": 0.2, "mobile": False,
                "relation": "fixe", "capacites": []}
        for relation in ("pose", "contenu"):
            with self.subTest(relation=relation), self.assertRaises(ErreurMonde):
                preparer_faits(m, {"ajouts": [{**base, "relation": relation}]})
        travail, _, etablis = preparer_faits(m, {"ajouts": [base]})
        id = etablis[0]["objet"]
        self.assertTrue(travail.objets[id]["attache"])
        for action in ("prendre", "detacher"):
            with self.subTest(action=action), self.assertRaises(ErreurMonde):
                Moteur(travail).preparer(proposition(action, id))
        self.assertEqual(travail.objets[id]["lieu"], "antichambre_murs")


if __name__ == "__main__":
    unittest.main()
