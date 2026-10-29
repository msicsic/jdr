"""G5 : contrat public de perception, boucle réelle et sauvegarde comprise."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu

from donjon.auberge import nouveau_auberge
from donjon.carte import carte
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import non_perception, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer, memoriser
from tests.test_audits_attendu import jouer
from tests.test_relances_luna import action
from tests.test_tensions import recharger


class PerceptionCanoniqueTests(unittest.TestCase):
    def verifier_recharge(self, m):
        # Les consultations peuvent entretenir la mémoire : stabiliser avant
        # de comparer le monde complet, puis répéter après recharge.
        vue, scene, plan = regarder(m), scene_percue(m), carte(m)
        avant = copy.deepcopy(m.data)
        r = recharger(m)
        self.assertEqual(regarder(r), vue)
        self.assertEqual(scene_percue(r), scene)
        self.assertEqual(carte(r), plan)
        self.assertEqual(r.data, avant)
        return r

    def faire(self, m, commande, p=None):
        # Toute tentative d'appel supplémentaire épuise le double et échoue.
        r, texte, appels = jouer(m, commande, [action(p)] if p else [], [])
        self.assertEqual([f for f, _ in appels], ["repondre_au_joueur"] if p else [])
        resultat = r.data["conversation"][-1]
        self.assertEqual(resultat["nature"], "resultat_moteur")
        self.assertIn(resultat["reponse"], texte)
        self.verifier_recharge(r)
        return r, resultat["reponse"]

    def test_captures_reelles_guet_et_noir_sans_modele(self):
        for fichier, cible in (("guet_relais7.json.gz", "marchand"),
                               ("signes_ecart_relais_noir.json", "ilse")):
            with self.subTest(fichier=fichier):
                chemin = Path("tests/data/scenes") / fichier
                brut = chemin.read_bytes()
                m = Monde(json.loads(gzip.decompress(brut) if fichier.endswith("gz") else brut))
                m.data["noms_connus"] = ["brune", "marchand", "ilse", "aubin"]
                m = recharger(m)
                self.assertFalse(m.visible(cible))
                avant = copy.deepcopy(m.data["objets"])
                r, texte = self.faire(m, "observer " + cible)
                self.assertIn("Tu ne vois pas", texte)
                self.assertNotIn("n'est pas ici", texte)
                self.assertEqual(r.data["objets"], avant)

    def test_absence_constatee_auberge_et_autre_scenario(self):
        for m in (nouveau_auberge(depart="fixe"), nouveau_monde()):
            m.data.pop("mode_cases", None)
            m.data["salles"][m.joueur["salle"]]["lumiere_naturelle"] = 2
            cible = next(i for i, o in m.objets.items() if o["type"] == "personnage"
                         and o["lieu"] != m.joueur["salle"])
            m.data["noms_connus"] = list(dict.fromkeys([*m.data["noms_connus"], cible]))
            with self.subTest(cible=cible):
                r, texte = self.faire(m, "observer " + cible)
                self.assertIn("absence dans la partie visible", texte)
                self.assertIn("contenus cachés", texte)
                self.assertEqual(r.objets[cible]["lieu"], m.objets[cible]["lieu"])

    def test_souvenir_de_position_passee_sans_position_reelle(self):
        m = nouveau_monde()
        installer(m)
        memoriser(m)
        cible = next(i for i in m.data["souvenirs_visuels"] if m.visible(i)
                     and m.objets[i]["type"] != "porte")
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        m.data["salles"][m.joueur["salle"]]["lumiere_naturelle"] = 0
        m.data["connus"] = list(dict.fromkeys([*m.data["connus"], cible]))
        r, texte = self.faire(m, "examiner " + cible)
        self.assertIn("Dernière observation", texte)
        self.assertIn("ne garantit pas sa position actuelle", texte)
        autre = r.copier()
        autre.objets[cible]["lieu"] = next(s for s in autre.data["salles"] if s != autre.joueur["salle"])
        self.assertEqual(non_perception(r, cible), non_perception(autre, cible))

    def test_visible_et_regarder_sont_sauvegardes(self):
        m = nouveau_monde()
        installer(m)
        cible = next(i for i in m.objets if m.visible(i))
        self.faire(m, "examiner " + cible)
        self.faire(m, "regarder")

    def test_libre_interprete_une_fois_aucun_audit_de_perception(self):
        m = nouveau_monde()
        installer(m)
        self.faire(m, "mj je regarde autour de moi", proposition("observer", "scene"))

    def test_texte_enregistre_sur_disque_avant_affichage(self):
        m = nouveau_monde()
        moteur = Moteur(m.copier())
        attendu = moteur.executer(moteur.preparer(proposition("examiner", "torche")))
        publications = []
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)

            def afficher(*args, **kwargs):
                if args == (attendu,):
                    sauve = Monde.charger(chemin)
                    self.assertEqual(sauve.data["conversation"][-1]["reponse"], attendu)
                    publications.append(attendu)

            with (patch("builtins.input", side_effect=["examiner torche", "quitter"]),
                  patch("builtins.print", side_effect=afficher),
                  patch("donjon.mj.MJOpenAI._appeler_brut", side_effect=AssertionError("Appel modèle interdit"))):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
        self.assertEqual(publications, [attendu])

    def test_les_plans_a_effets_gardent_la_revue(self):
        from donjon.moteur import Plan
        for p in (Plan(proposition("prendre", "torche"), 0, "Prendre"),
                  Plan(proposition("composer"), 0, "Plusieurs gestes"),
                  Plan(proposition("examiner", "torche"), 0, "Fausse perception",
                       effets=[("deplacer", "torche", "joueur")])):
            self.assertFalse(p.perception_canonique)


if __name__ == "__main__":
    unittest.main()
