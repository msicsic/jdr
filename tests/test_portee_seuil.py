"""La portée manuelle suit les pas, pour tous les acteurs et après recharge."""
from pathlib import Path
import tempfile
import unittest

from donjon import pnj, spatial
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.monde import Monde, ErreurMonde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder, fiche
from donjon.esprits import lire, croire
from donjon.temps import ecouler
from tests.support import calme
from tests.test_temps_etat import intention, plan


class PorteeSeuilTests(unittest.TestCase):
    def recharge(self, m):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "monde.json"
            m.sauver(chemin)
            etat = m.copier().data
            rendu = regarder(m), fiche(m)
            n = Monde.charger(chemin)
        self.assertEqual(etat, n.data)
        self.assertEqual(rendu, (regarder(n), fiche(n)))
        return n

    def relais(self, cible):
        m = nouveau_defi(depart="fixe")
        spatial.installer(m)
        m.joueur.update(salle="antichambre", position=[0, 3], orientation="ouest")
        m.objets[cible].update(lieu="echoppe", position_salle="echoppe", position=[8, 3],
                               proprietaire=None)
        return self.recharge(m)

    def test_saisie_reelle_torche_et_crochets_au_seuil(self):
        for cible, nom in (("torche", "torche"), ("crochets", "trousse de crochets")):
            with self.subTest(cible=cible):
                m = self.relais(cible)
                self.assertTrue(m.visible(cible))
                self.assertTrue(spatial.proche(m, cible))
                moteur = Moteur(m)
                moteur.executer(moteur.preparer(analyser(m, "je prends " + nom)))
                n = self.recharge(m)
                self.assertEqual(n.objets[cible]["lieu"], "joueur")
                self.assertEqual(n.joueur["salle"], "antichambre")
                self.assertIn(n.objets[cible]["nom"], fiche(n))

    def crypte(self):
        m = nouveau_monde()
        spatial.installer(m)
        m.joueur.update(salle="antichambre", position=[3, 0])
        m.joueur.pop("orientation", None)
        m.objets["porte"].update(ouverte=True, verrouillee=False)
        m.objets["coffret_seuil"] = objet("coffret_seuil", "coffret du seuil", "contenant", "crypte",
            position_salle="crypte", position=[3, 6], ouverte=False, verrouillee=False, mobile=True)
        m.data["connus"].append("coffret_seuil")
        return self.recharge(m)

    def test_autre_scenario_ouvrir_dans_le_noir_et_porte_fermee(self):
        m = self.crypte()
        # Le souvenir tactile suffit à portée, même sans visibilité.
        self.assertTrue(m.accessible("coffret_seuil"))
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition("ouvrir", "coffret_seuil")))
        self.assertTrue(self.recharge(m).objets["coffret_seuil"]["ouverte"])
        m = self.crypte()
        m.objets["porte"]["ouverte"] = False
        m = self.recharge(m)
        self.assertFalse(spatial.proche(m, "coffret_seuil"))
        self.assertFalse(m.accessible("coffret_seuil"))
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(proposition("ouvrir", "coffret_seuil"))
        self.assertFalse(self.recharge(m).objets["coffret_seuil"]["ouverte"])

    def test_contenant_ferme_et_angle_de_mur(self):
        m = self.crypte()
        m.objets["cle"]["lieu"] = "coffret_seuil"
        self.assertFalse(spatial.proche(m, "cle"))
        m.objets["coffret_seuil"]["ouverte"] = True
        self.assertTrue(spatial.proche(m, "cle"))
        m.joueur["position"] = [2, 1]
        m.objets["cle"].update(lieu="antichambre", position_salle="antichambre", position=[3, 2])
        m.objets["mur"] = objet("mur", "mur", "decoration", "antichambre",
            position_salle="antichambre", position=[3, 1], bloque_passage=True)
        m = self.recharge(m)
        # Un seul côté fermé suffit : exactement la règle des pas.
        self.assertFalse(spatial.proche(m, "cle"))
        self.assertFalse(pnj._a_portee_de(m, "antichambre", (2, 1), (3, 2)))

    def test_mur_sans_sortie_et_cible_plus_lointaine(self):
        m = self.relais("torche")
        m.joueur["position"] = [0, 2]
        m.objets["torche"]["position"] = [8, 2]
        m = self.recharge(m)
        self.assertFalse(spatial.proche(m, "torche"))
        m.joueur["position"] = [0, 3]
        m.objets["torche"]["position"] = [7, 3]
        m = self.recharge(m)
        self.assertFalse(spatial.proche(m, "torche"))

    def test_le_contact_au_seuil_ne_cede_pas_la_propriete(self):
        m = self.relais("torche")
        m.objets["torche"]["proprietaire"] = "marchand"
        m = self.recharge(m)
        self.assertTrue(spatial.proche(m, "torche"))
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(analyser(m, "je prends la torche"))
        self.assertEqual(self.recharge(m).objets["torche"]["lieu"], "echoppe")

    def test_pnj_refuse_la_porte_fermee_et_le_contenant_ferme(self):
        m = self.crypte()
        m.joueur["position"] = [1, 1]
        m.objets["marchand"].update(lieu="antichambre", position=[3, 0])
        m.objets["cle"]["lieu"] = "coffret_seuil"
        m = self.recharge(m)
        self.assertTrue(pnj._accessible(m, "marchand", "coffret_seuil"))
        self.assertFalse(pnj._accessible(m, "marchand", "cle"))
        m.objets["porte"]["ouverte"] = False
        m = self.recharge(m)
        self.assertFalse(pnj._accessible(m, "marchand", "coffret_seuil"))

    def test_le_volume_de_la_cible_ne_bloque_pas_son_propre_contact(self):
        m = self.crypte()
        m.objets["coffret_seuil"]["bloque_passage"] = True
        m = self.recharge(m)
        self.assertTrue(spatial.proche(m, "coffret_seuil"))
        self.assertTrue(pnj._a_portee_de(m, "crypte", (3, 5), (3, 6)))
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition("ouvrir", "coffret_seuil")))
        self.assertTrue(self.recharge(m).objets["coffret_seuil"]["ouverte"])
        m.objets["cle"]["lieu"] = "coffret_seuil"
        self.assertTrue(spatial.proche(self.recharge(m), "cle"))
        m.objets["coffret_seuil"]["ouverte"] = False
        self.assertFalse(spatial.proche(self.recharge(m), "cle"))
        # Une obstruction distincte reste un obstacle ; la cible seule est ignorée.
        m.objets["ecran"] = objet("ecran", "écran", "decoration", "crypte",
            position_salle="crypte", position=[3, 6], bloque_passage=True)
        self.assertFalse(spatial.proche(self.recharge(m), "coffret_seuil"))

    def test_attache_du_cote_voisin_accessible_seulement_par_seuil_ouvert(self):
        m = self.crypte()
        m.objets["axe_haut"]["cote"] = "crypte"
        m = self.recharge(m)
        self.assertTrue(spatial.proche(m, "axe_haut"))
        m.objets["porte"]["ouverte"] = False
        self.assertFalse(spatial.proche(self.recharge(m), "axe_haut"))

    def test_cible_a_plusieurs_extremites_depuis_un_secteur_voisin(self):
        m = self.crypte()
        m.objets["appui"] = objet("appui", "appui", "surface", "crypte",
            position_salle="crypte", position=[3, 6],
            appui_vertical=dict(bas="crypte", haut="echoppe",
                                position_bas=[3, 6], position_haut=[1, 1]))
        m = self.recharge(m)
        self.assertTrue(spatial.proche(m, "appui"))
        m.objets["porte"]["ouverte"] = False
        self.assertFalse(spatial.proche(self.recharge(m), "appui"))

    def test_pnj_prepare_et_execute_sans_franchir_le_seuil(self):
        m = self.relais("torche")
        m.joueur["position"] = [1, 1]
        m.objets["brune"].update(lieu="antichambre", position=[0, 3])
        etape = dict(operation="prendre", cible="torche", outil="", lieu="echoppe", condition="")
        self.assertTrue(pnj._accessible(m, "brune", "torche"))
        self.assertEqual(pnj._approcher(m, "brune", etape, []), 0)
        self.assertTrue(pnj._executer(m, "brune", etape, [], []))
        n = self.recharge(m)
        self.assertEqual(n.objets["torche"]["lieu"], "brune")
        self.assertEqual(n.objets["brune"]["lieu"], "antichambre")

    def test_approche_vers_case_crue_du_secteur_voisin(self):
        m = self.relais("torche")
        m.joueur["position"] = [1, 1]
        m.objets["brune"].update(lieu="antichambre", position=[1, 3])
        croire(m, "brune", "torche", "lieu", "echoppe", "vu",
               salle="echoppe", case=[8, 3])
        e = plan("prendre", "torche", lieu="echoppe")
        intention(m, "brune", e)
        duree = pnj._approcher(m, "brune", e, [])
        self.assertGreater(duree, 0)
        self.assertEqual(m.objets["brune"]["lieu"], "antichambre")
        self.assertEqual(m.objets["brune"]["position"], [0, 3])
        self.assertEqual(pnj._approcher(m, "brune", e, []), 0)
        self.assertTrue(pnj._executer(m, "brune", e, [], []))
        self.assertEqual(self.recharge(m).objets["torche"]["lieu"], "brune")

    def test_meme_laps_entier_ou_decoupe_avec_recharge(self):
        m = self.relais("torche")
        m.joueur["position"] = [1, 1]
        calme(m, "marchand", "brune", "ilse", "aubin")
        m.objets["brune"].update(lieu="antichambre", position=[0, 3])
        croire(m, "brune", "torche", "lieu", "echoppe", "vu",
               salle="echoppe", case=[8, 3])
        intention(m, "brune", plan("prendre", "torche", lieu="echoppe"))
        a, b = m.copier(), m.copier()
        for monde, intervalles in ((a, [100]), (b, [10] * 10)):
            for dt in intervalles:
                minutes = ecouler(monde, dt)
                pnj.avancer(monde, minutes, [], dixiemes=dt)
                recharge = self.recharge(monde)
                monde.data = recharge.data
        self.assertEqual(a.data, b.data)
        self.assertEqual((regarder(a), fiche(a)), (regarder(b), fiche(b)))
        self.assertEqual(a.objets["torche"]["lieu"], "brune")


if __name__ == "__main__":
    unittest.main()
