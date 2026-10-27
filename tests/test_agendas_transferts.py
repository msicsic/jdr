"""Transferts constatés : droits, choix différé et recharge."""
import copy
import unittest

from donjon import agendas, deliberation, planification
from donjon.biens import preter
from donjon.deplacement_objet import deplacer
from donjon.echanges import remettre
from donjon.esprits import croire, lire, percevoir_tous, constater_possession
from donjon.rendu import fiche, regarder
from tests.support import regarder as orienter
from tests import test_agendas_fins as fins
from tests.test_tensions import recharger, vivre


class TransfertsTests(unittest.TestCase):
    objets = ("cle_reserve", "couteau")

    def verifier_fin(self, m, objet, cause):
        m = fins.FinsTests.verifier_fin(self, m, objet, cause)
        self.assertTrue(any("abandonne (bien cru " + cause + ")" in c["texte"]
                            for c in m.data["chronique"]))
        if m.objets[objet]["lieu"] == "joueur":
            self.assertIn(m.objets[objet]["nom"].casefold(), fiche(m).casefold())
            self.assertEqual(fiche(m), fiche(recharger(m)))
        return m

    def test_remise_propre_au_proprietaire_et_recharge(self):
        for objet in self.objets:
            with self.subTest(objet=objet):
                m = fins.garde(objet)
                m.objets[objet]["proprietaire"] = "joueur"
                deplacer(m, objet, "marchand")
                remettre(m, "marchand", "joueur", objet)
                m = recharger(m)
                self.assertEqual(m.objets[objet]["lieu"], "joueur")
                for participant in ("marchand", "joueur"):
                    preuve = lire(m, participant)["croyances"][objet]["lieu"]
                    self.assertEqual(preuve["source"], "essai")
                    self.assertEqual(preuve["possession"]["remis_par"], "marchand")
                self.verifier_fin(m, objet, "remis")

    def test_remise_propre_a_un_destinataire_mandate(self):
        for objet in self.objets:
            m = fins.garde(objet)
            m.objets[objet]["proprietaire"] = "joueur"
            deplacer(m, objet, "marchand")
            agendas.prendre(m, "marchand", {"condition": {"objet": objet, "remettre": "brune"},
                                            "pour": "joueur", "minute": m.data["minutes"]})
            remettre(m, "marchand", "brune", objet)
            # Le mandat est clos ; revoir le destinataire ne doit pas effacer
            # la preuve de sa remise autorisée.
            constater_possession(m, "marchand", objet, "vu")
            m = recharger(m)
            self.assertEqual(m.objets[objet]["lieu"], "brune")
            self.verifier_fin(m, objet, "remis")

    def test_possession_vue_sans_permission(self):
        for objet in self.objets:
            m = fins.garde(objet)
            m.objets[objet]["proprietaire"] = "marchand"
            deplacer(m, objet, "joueur")
            m.objets[objet]["longueur_cm"] = 100
            orienter(m, "marchand", "joueur")
            percevoir_tous(m)
            m = recharger(m)
            preuve = lire(m, "marchand")["croyances"][objet]["lieu"]
            self.assertEqual(preuve["valeur"], "joueur")
            self.assertFalse(preuve["possession"]["permis"])
            self.verifier_fin(m, objet, "perdu")

    def test_retour_vu_chez_le_proprietaire(self):
        for objet in self.objets:
            m = fins.garde(objet)
            m.objets[objet]["proprietaire"] = "joueur"
            deplacer(m, objet, "joueur")
            m.objets[objet]["longueur_cm"] = 100
            orienter(m, "marchand", "joueur")
            percevoir_tous(m)
            self.verifier_fin(recharger(m), objet, "rendu")

    def test_pret_et_garde_confiee_ne_terminent_pas(self):
        for objet in self.objets:
            for confie in (False, True):
                m = fins.garde(objet)
                m.objets[objet]["proprietaire"] = "marchand"
                if confie:
                    agendas.prendre(m, "brune", {"condition": {"objet": objet, "lieu": "antichambre"}, "pour": "marchand",
                                                "minute": m.data["minutes"]})
                    deplacer(m, objet, "brune")
                    constater_possession(m, "marchand", objet, "vu")
                else:
                    deplacer(m, objet, "marchand")
                    remettre(m, "marchand", "joueur", objet)
                m = recharger(m)
                agendas.actualiser(m, "marchand")
                self.assertIn(agendas.projets(m, "marchand")[0]["etat"], ("actif", "sommeil"))
                self.assertIn(objet, [p.get("objet") for p in agendas.gardes(m, "marchand")])
                self.assertEqual(m.data, recharger(m).data)
                self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_position_inconnue_et_mutation_distante_des_droits(self):
        for objet in self.objets:
            m = fins.garde(objet)
            m.objets[objet]["proprietaire"] = "marchand"
            preter(m, objet, "joueur")
            deplacer(m, objet, "joueur")
            constater_possession(m, "marchand", objet, "vu")
            # La révocation réelle distante n'est pas une information.
            m.data["permissions"] = []
            agendas.actualiser(m, "marchand")
            self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")
            croire(m, "marchand", objet, "lieu", None, "vu", salle=None, case=None)
            agendas.actualiser(m, "marchand")
            m = recharger(m)
            self.assertNotEqual(agendas.projets(m, "marchand")[0]["etat"], "abandonne")
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_gardien_non_proprietaire_remet_a_un_emprunteur_autorise_sans_fin(self):
        for objet in self.objets:
            m = fins.garde(objet)
            m.objets[objet]["proprietaire"] = "aubin"
            preter(m, objet, "joueur")
            deplacer(m, objet, "marchand")
            remettre(m, "marchand", "joueur", objet)
            m = recharger(m)
            agendas.actualiser(m, "marchand")
            self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")
            self.assertIn(objet, [a.get("objet") for a in agendas.gardes(m, "marchand")])
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_preuve_sans_objet_reel_laps_et_choix_interrompu(self):
        for objet in self.objets:
            m = fins.garde(objet)
            m.objets[objet]["proprietaire"] = "joueur"
            deplacer(m, objet, "marchand")
            remettre(m, "marchand", "joueur", objet)
            avant = copy.deepcopy(m.data)
            with self.assertRaises(RuntimeError):
                with planification.vues_du_choix(m, "marchand"):
                    agendas.actualiser(m, "marchand")
                    raise RuntimeError("interrompu")
            self.assertEqual(m.data, avant)
            entier, _ = vivre(recharger(m), 2)
            morceaux, _ = vivre(recharger(m), 1)
            morceaux, _ = vivre(morceaux, 1)
            self.assertEqual(entier.data, morceaux.data)
            self.assertEqual(regarder(entier), regarder(recharger(morceaux)))
            # La décision reste fondée sur la preuve même si le réel a changé.
            deplacer(m, objet, "echoppe", [8, 5])
            m.objets[objet]["proprietaire"] = "brune"
            self.verifier_fin(recharger(m), objet, "remis")

    def test_ballot_anselme_et_second_bien_garde_perte_vue_rechargee(self):
        from donjon.banc_pnj import creer
        for objet in ("ballot", "cle_coffre"):
            m = creer("auberge", 1985, "fixe")
            p = m.objets["anselme"]["profil"]
            p.update(agendas=[{"sorte": "garder", "parametres": {"objet": objet}}], pulsions=[])
            lire(m, "anselme")["pulsions"] = []
            agendas.actualiser(m, "anselme")
            m.joueur.update(salle=m.objets["anselme"]["lieu"], position=[2, 1])
            m.objets[objet].update(proprietaire="anselme", longueur_cm=100)
            deplacer(m, objet, "joueur")
            orienter(m, "anselme", "joueur")
            percevoir_tous(m)
            deliberation.choisir(m, "anselme", m.data["minutes"])
            m = recharger(m)
            self.assertEqual(agendas.projets(m, "anselme")[0]["raison"], "bien cru perdu")
            self.assertEqual(m.objets[objet]["lieu"], "joueur")
            self.assertIn(m.objets[objet]["nom"].casefold(), fiche(m).casefold())
            self.assertEqual(fiche(m), fiche(recharger(m)))
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_preuve_hors_memoire_et_pas_de_double_prix(self):
        from tests.test_agendas_garder import declarer
        from tests.test_interposition import epreuve
        for objet in self.objets:
            m = epreuve()
            m.objets[objet]["proprietaire"] = "marchand"
            # Pulsion et agenda visant la même charge : toujours un maximum.
            pulsion = copy.deepcopy(m.objets["marchand"]["profil"]["pulsions"][0])
            pulsion["condition"] = {"objet": objet, "lieu": "antichambre"}
            m.objets["marchand"]["profil"]["pulsions"] = [pulsion]
            lire(m, "marchand")["pulsions"] = [None]
            prix = planification.prix_gardes(m, "marchand", ["antichambre"])
            m = declarer(m, "marchand", objet, pulsion=True)
            self.assertEqual(planification.prix_gardes(m, "marchand", ["antichambre"]), prix)
            m.objets[objet]["proprietaire"] = "joueur"
            deplacer(m, objet, "marchand")
            remettre(m, "marchand", "joueur", objet)
            preuve = copy.deepcopy(lire(m, "marchand")["croyances"][objet]["lieu"])
            lire(m, "marchand")["memoire"] = []
            m.data["minutes"] += 5
            m = recharger(m)
            self.assertEqual(lire(m, "marchand")["croyances"][objet]["lieu"], preuve)
            agendas.actualiser(m, "marchand")
            self.assertEqual(agendas.projets(m, "marchand")[0]["raison"], "bien cru remis")
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))



if __name__ == "__main__":
    unittest.main()


