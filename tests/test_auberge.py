"""L'auberge du Col-Pendu : le scénario se charge, se vérifie, se sauve, se recharge, et sa nuit
se vit sans violation de l'état, avant comme après rechargement."""
import tempfile
import unittest
from collections import deque
from pathlib import Path

from donjon.auberge import DEPART, nouveau_auberge
from donjon.banc_pnj import creer, executer
from donjon.esprits import lire, pnjs
from donjon.monde import Monde
from donjon.spatial import installer as installer_cases


class AubergeTests(unittest.TestCase):
    def setUp(self):
        self.m = creer("auberge", 1985, "fixe")

    def test_chargement_et_verification(self):
        self.m.verifier()
        self.assertEqual(self.m.joueur["salle"], DEPART)
        self.assertEqual(len(pnjs(self.m)), 8)
        # Chacun a un profil complet, un corps (faim, fatigue, froid) et des croyances de départ.
        for id in pnjs(self.m):
            self.assertTrue(self.m.objets[id].get("profil"), id)
            self.assertTrue(lire(self.m, id)["croyances"], id)
            self.assertTrue(set(lire(self.m, id)["besoins"]) >= {"faim", "repos", "chaleur"}, id)

    def test_toutes_les_salles_communiquent(self):
        salles = self.m.data["salles"]
        vus, file = {DEPART}, deque([DEPART])
        while file:
            for sortie in salles[file.popleft()]["sorties"].values():
                if sortie["vers"] not in vus:
                    vus.add(sortie["vers"])
                    file.append(sortie["vers"])
        self.assertEqual(vus, set(salles))
        self.assertEqual(len(salles), 8)

    def test_ressources_comptees_et_cles(self):
        o = self.m.objets
        # Les vivres sont comptés et sous clé ; le bois est compté ; chaque serrure a sa clé, portée.
        self.assertTrue(o["garde_manger"]["verrouillee"] and "garde_manger" in o["cle_garde_manger"]["ouvre"])
        self.assertEqual(o["cle_garde_manger"]["lieu"], "odile")
        self.assertEqual(o["vivres"]["lieu"], "garde_manger")
        self.assertTrue(all(o[b]["charges"] > 0 for b in ("bois_cuisine", "bois_anselme", "fagots_etable", "bois_reserve")))
        self.assertEqual(o["bois_reserve"]["proprietaire"], "odile")
        self.assertTrue(all(o[f].get("foyer") and o[f]["allume"] for f in ("atre", "fourneau", "poele")))

    def test_la_nuit_se_vit_avant_et_apres_rechargement(self):
        executer(self.m, 100)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "auberge.json"
            self.m.sauver(chemin)
            repris = Monde.charger(chemin)
        installer_cases(repris)
        self.assertEqual(repris.data, self.m.data)
        # La suite de la nuit, rafale comprise (minute 200), est la même partie reprise ou non ;
        # le banc vérifie l'état à chaque pas.
        chronique, mesures = executer(self.m, 210)
        chronique_reprise, mesures_reprise = executer(repris, 210)
        self.assertEqual(chronique_reprise, chronique)
        self.assertEqual(mesures_reprise, mesures)
        self.assertEqual(repris.data["esprits"], self.m.data["esprits"])
        self.assertEqual(self.m.data["horloges_declenchees"], ["rafale"])
        repris.verifier()
        # Ce que la nuit produit : des demandes et leurs issues, des gestes illicites vus, des
        # nouvelles qui circulent, et pas seulement des rondes.
        self.assertEqual(mesures["usurpations"], 0)
        self.assertGreater(mesures["echanges"], 5)
        # Les relations graduées réduisent cette tranche de onze à neuf : Lucien
        # n'appelle plus à l'aide et ne fait plus « reste dans la lumière » ici.
        # Le contrôle de diversité conserve un plancher de huit ;
        # l'égalité complète avant/après reprise ci-dessus reste l'invariant de ce test.
        self.assertGreaterEqual(mesures["evenements_distincts"], 8)
        acteurs = {c["pnj"] for c in chronique if c.get("nature", "geste") in ("geste", "social")}
        self.assertGreaterEqual(len(acteurs), 6)

    def test_tout_geste_illicite_vu_peut_se_raconter(self):
        # Une rumeur porte sur n'importe quel geste d'un PNJ sur le bien d'un autre : allumer, éteindre
        # ou recharger un feu, servir une part, comme prendre ou ouvrir.
        from donjon.social import phrase
        for op in ("prendre", "poser", "ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter", "forcer",
                   "manger", "servir", "alimenter", "allumer", "eteindre"):
            texte = phrase(self.m, {"type": "vu_agir", "auteur": "lucien", "operation": op, "objet": "poele"})
            self.assertTrue(texte.startswith("Lucien a "), (op, texte))

    def test_graine_propre_au_scenario(self):
        autre = nouveau_auberge(7, "fixe")
        self.assertEqual(autre.data["seed"], 7)
        self.assertEqual(autre.data["scenario_id"], "auberge_du_col")


if __name__ == "__main__":
    unittest.main()
