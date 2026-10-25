import copy
import json
import unittest

from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire


class PersonnagesTests(unittest.TestCase):
    def test_portrait_connu_sans_personnage_accessible_ni_fuite_a_distance(self):
        m = nouveau_monde()
        souvenir = copy.deepcopy(m.contexte()["souvenirs_personnages"]["marchand"])
        self.assertIn("grisonnante", souvenir["details"][0]["description"])
        self.assertEqual(len(souvenir["details"]), 2)
        self.assertNotIn("marchand", [o["id"] for o in m.contexte()["objets_perceptibles"]])
        # Un nom connu se désigne, sans rendre le corps présent ni accessible.
        self.assertEqual(m.trouver("Gorm"), "marchand")
        self.assertTrue(m.designable("marchand"))
        self.assertFalse(m.accessible("marchand"))
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(proposition("examiner", m.trouver("Gorm")))
        m.objets["marchand"].update(humeur="inquiet", portrait="Un nouveau portrait.", secret="cachette secrète")
        m.objets["barbe_gorm"]["description_visuelle"] = "Sa barbe a été rasée."
        Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        avant = copy.deepcopy(m.data)
        contexte = m.contexte()
        self.assertEqual(contexte["souvenirs_personnages"]["marchand"], souvenir)
        self.assertNotIn("cachette secrète", json.dumps(contexte))
        self.assertEqual(m.data, avant)
        contexte["souvenirs_personnages"]["marchand"]["portrait"] = "Mutation externe"
        self.assertEqual(m.data["souvenirs_personnages"]["marchand"], souvenir)

    def test_rencontre_actualise_les_details_qui_sont_examinables(self):
        m = nouveau_monde()
        m.objets["barbe_gorm"]["description_visuelle"] = "Sa barbe a été rasée."
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition("aller", "ouest")))
        self.assertEqual(m.trouver("barbe"), "barbe_gorm")
        self.assertIn("rasée", decrire(m, "barbe_gorm", detail=True))
        self.assertIn("barbe de Gorm", decrire(m, "marchand", detail=True))
        souvenir = m.contexte()["souvenirs_personnages"]["marchand"]
        self.assertIn("rasée", souvenir["details"][0]["description"])
        self.assertNotIn("humeur", souvenir)
        with self.assertRaises(ErreurMonde):
            moteur.preparer(proposition("frapper", "mains_gorm", "couteau"))
        moteur.executer(moteur.preparer(proposition("aller", "est")))
        self.assertEqual(m.contexte()["souvenirs_personnages"]["marchand"], souvenir)

    def test_penombre_ne_cree_pas_de_nouveaux_souvenirs_visuels(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data["souvenirs_personnages"])
        m.joueur["salle"] = "echoppe"
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        m.data["salles"]["echoppe"]["lumiere_naturelle"] = 1
        m.objets["marchand"]["portrait"] = "Une nouvelle apparence."
        m.actualiser_souvenirs_personnages()
        self.assertEqual(m.data["souvenirs_personnages"], avant)
        for o in m.contexte()["objets_perceptibles"]:
            self.assertNotIn("portrait", o)
            self.assertNotIn("description_visuelle", o)
        self.assertNotIn("nouvelle apparence", decrire(m, "marchand", detail=True))

    def test_migration_et_persistance_sans_reinitialiser_la_partie(self):
        m = nouveau_monde()
        ancien = copy.deepcopy(m.data)
        for cle in ("personnages_version", "souvenirs_personnages"):
            ancien.pop(cle)
        for cle in ("portrait", "maniere_de_parler"):
            ancien["objets"]["marchand"].pop(cle)
        for id in ("barbe_gorm", "mains_gorm"):
            ancien["objets"].pop(id)
        ancien["objets"]["marchand"]["humeur"] = "inquiet"
        ancien["objets"]["cle"]["lieu"] = "joueur"
        ancien["minutes"] = 27
        ancien["joueur"]["or"] = 8
        migre = Monde(ancien)
        self.assertEqual(migre.objets["marchand"]["humeur"], "inquiet")
        self.assertEqual(migre.objets["cle"]["lieu"], "joueur")
        self.assertEqual(migre.data["minutes"], 27)
        self.assertEqual(migre.joueur["or"], 8)
        migre.objets["marchand"]["portrait"] = "Portrait personnalisé."
        recharge = Monde(json.loads(json.dumps(migre.data)))
        self.assertEqual(recharge.data, migre.data)


if __name__ == "__main__":
    unittest.main()
