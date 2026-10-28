"""A5/252 : filiation publiée, bornée et rechargée sans conversion historique."""
import copy
import unittest

from donjon import agendas
from donjon.esprits import lire
from donjon.monde import ErreurMonde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_agendas_amener_fin import declarer
from tests.test_engagement_deplacement import scene
from tests.test_tensions import recharger


class MandatTests(unittest.TestCase):
    def monde(self):
        m, _ = scene()
        return declarer(m, "ilse", "chambre_cloche")

    def parametres(self, sorte):
        if sorte == "amener":
            return {"qui": "brune", "lieu": "chambre_cloche"}
        return {"qui": "brune", "avis": {"type": "avis", "objet": "antichambre",
                "attribut": "menace", "valeur": True}}

    def confier(self, m, sorte="amener", mandant="marchand", parent="evacuer",
                titulaire="aubin", accepte=True):
        return agendas.confier(m, mandant, parent, titulaire, sorte,
                               self.parametres(sorte), accepte=accepte)

    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        return n

    def test_deux_sortes_deux_niveaux_relance_et_recharge(self):
        for sorte in ("amener", "informer"):
            with self.subTest(sorte=sorte):
                m = self.monde()
                a = self.confier(m, sorte)
                self.assertEqual(a["origine"]["type"], "mandat")
                self.assertEqual(a["origine"]["parent"], "evacuer")
                b = self.confier(m, sorte, "aubin", a["id"], "ilse")
                chaine = agendas.filiation(m, "ilse", b["id"])
                self.assertEqual([r["titulaire"] for r in chaine], ["marchand", "aubin", "ilse"])
                m = self.recharge(m)
                self.assertEqual(agendas.filiation(m, "ilse", b["id"]), chaine)
                m.data["minutes"] += 1
                p = self.parametres(sorte)
                p["qui"] = ["brune", "brune"]
                relance = agendas.confier(m, "marchand", "evacuer", "aubin", sorte, p, accepte=True)
                self.assertEqual(relance["id"], a["id"])
                self.assertEqual(relance["origine"], a["origine"])
                self.assertEqual(relance["confirme"], m.data["minutes"])
                self.assertEqual(len(agendas.enfants(m, "marchand", "evacuer")), 1)
                # Les lectures n'accordent aucun accès mutable au registre.
                agendas.enfants(m, "marchand", "evacuer").clear()
                a["origine"].clear()
                self.recharge(m)

    def test_refus_cycle_et_troisieme_niveau_sans_mutation(self):
        for sorte in ("amener", "informer"):
            m = self.monde()
            avant = copy.deepcopy(m.data)
            self.assertIsNone(self.confier(m, sorte, accepte=False))
            self.assertEqual(m.data, avant)
            a = self.confier(m, sorte)
            avant = copy.deepcopy(m.data)
            self.assertIsNone(self.confier(m, sorte, accepte=False))
            self.assertEqual(m.data, avant)
            with self.assertRaises(ErreurMonde) as refus:
                self.confier(m, sorte, "aubin", a["id"], "marchand")
            self.assertIn("titulaire=marchand", refus.exception.attendu)
            self.assertEqual(m.data, avant)
            b = self.confier(m, sorte, "aubin", a["id"], "ilse")
            avant = copy.deepcopy(m.data)
            with self.assertRaises(ErreurMonde) as refus:
                self.confier(m, sorte, "ilse", b["id"], "brune")
            self.assertIn("profondeur=2", refus.exception.attendu)
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_ancien_engagement_inchange_et_devis_sans_effet(self):
        m = self.monde()
        ancien = {"condition": {"objet": "ilse", "lieu": "chambre_cloche"},
                  "pour": "marchand", "minute": m.data["minutes"]}
        agendas.prendre(m, "aubin", ancien)
        self.confier(m)
        m = self.recharge(m)
        self.assertEqual(agendas.en_cours(m, "aubin"), [ancien])
        avant = copy.deepcopy(m.data)
        with agendas.evaluation(m, "marchand", publier=False):
            with self.assertRaisesRegex(ValueError, "après le devis"):
                self.confier(m, titulaire="ilse")
        self.assertEqual(m.data, avant)

    def test_mandats_executables_par_les_agendas_communs(self):
        from donjon import echanges
        from donjon.esprits import croire
        from donjon.monde import Monde
        from unittest.mock import patch
        from tests.test_agendas_activation import declarer as informer, planifier_choix
        from tests.test_avis_menace import scene as scene_parole
        from tests.test_tensions import vivre
        # Un mandat de parole passe par le planificateur et la parole existants.
        m = informer(scene_parole(), "marchand", "ilse")
        a = agendas.confier(m, "marchand", "a1", "aubin", "informer",
                           {"qui": "ilse", "avis": {"type": "avis", "objet": "antichambre",
                            "attribut": "menace", "valeur": True}}, accepte=True)
        m = self.recharge(m)
        _, etapes = planifier_choix(m, "aubin", a["id"])
        self.assertTrue(echanges.executer(m, "aubin", etapes[-1], []))
        agendas.actualiser(m, "aubin")
        m = self.recharge(m)
        self.assertEqual(agendas.projets(m, "aubin")[0]["etat"], "atteint")
        # Un mandat de déplacement reste une marche réelle, jamais une téléportation.
        m, _ = scene()
        m.objets["aubin"]["profil"]["agendas"] = [
            {"id": "racine", "sorte": "amener", "parametres":
             {"qui": "ilse", "lieu": "chambre_cloche"}}]
        agendas.actualiser(m, "aubin")
        a = agendas.confier(m, "aubin", "racine", "marchand", "amener",
                           {"qui": "ilse", "lieu": "chambre_cloche"}, accepte=True)
        _, etapes = planifier_choix(m, "marchand", a["id"])
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(echanges.executer(m, "marchand", etapes[-1], []))
        self.assertEqual(m.objets["ilse"]["lieu"], "antichambre")
        for qui in ("marchand", "aubin", "brune"):
            lire(m, qui)["libre"] = 1000000
        m, _ = vivre(self.recharge(m), 3)
        self.assertEqual(m.objets["ilse"]["lieu"], "chambre_cloche")
        croire(m, "marchand", "ilse", "lieu", "chambre_cloche", "dit:ilse",
               salle="chambre_cloche", case=None)
        agendas.actualiser(m, "marchand")
        self.recharge(m)
        # La relance d'un enfant terminé conserve son identité et son résultat.
        retour = agendas.confier(m, "aubin", "racine", "marchand", "amener",
                                {"qui": ["ilse"], "lieu": "chambre_cloche"}, accepte=True)
        self.assertEqual(retour["id"], a["id"])
        self.assertEqual(retour["etat"], "atteint")

    def test_validation_rejette_filiation_alteree(self):
        for alteration in ("orphelin", "double", "condition", "parent", "cycle"):
            m = self.monde()
            a = self.confier(m)
            parent = lire(m, "marchand")["agendas"][0]
            enfant = next(x for x in lire(m, "aubin")["agendas"] if x["id"] == a["id"])
            if alteration == "orphelin":
                parent.pop("confies")
            elif alteration == "double":
                parent["confies"] *= 2
            elif alteration == "condition":
                doublon = copy.deepcopy(enfant)
                doublon["id"] = "autre"
                lire(m, "aubin")["agendas"].append(doublon)
                parent["confies"].append({"titulaire": "aubin", "agenda": "autre"})
            elif alteration == "parent":
                enfant["origine"]["parent"] = "absent"
            else:
                enfant["origine"].update(de="aubin", parent=a["id"])
            with self.assertRaises((AssertionError, ValueError)):
                self.recharge(m)


if __name__ == "__main__":
    unittest.main()
