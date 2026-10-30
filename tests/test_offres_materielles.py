"""Capacités des couples publics, cas réel conduite et second cas, après recharge."""
import copy
import json
import unittest

from donjon.commandes import DescripteurPublic
from donjon.gestes_publics import GESTES_CORPS, gestes_du_monde, rendre_liste
from donjon.moteur import Moteur
from tests import test_attendu_designable as designable
from tests import test_gestes_terminal as terminal
from tests import test_outils_publics as web
from tests.test_tensions import recharger


def materiels(m):
    return [c.descripteur.contenu for c in gestes_du_monde(m)
            if c.descripteur.contenu["geste"] not in GESTES_CORPS
            and c.descripteur.contenu.get("parametres", {}).keys() & {"outil", "destination"}]


class OffresMateriellesTests(unittest.TestCase):
    def test_conduite_reelle_et_lampe_choix_effet_et_vues_apres_recharge(self):
        mesures = []
        for cas in ("conduite", "lampe"):
            with self.subTest(cas=cas):
                if cas == "conduite":
                    m = designable.AttenduDesignableTests().conduite()
                    d = DescripteurPublic({"geste": "eteindre", "cible": "lanterne"})
                    # Dans cette capture aucun combustible compatible, contenant
                    # ouvert ou outil d'impact/crochetage/clé n'est disponible.
                    self.assertEqual(materiels(m), [])
                    # 353 porte les gestes du corps au terminal ; ce comptage
                    # bornait les offres d'objets, avant leur ajout documenté.
                    self.assertLess(sum(c.descripteur.contenu["geste"] not in GESTES_CORPS
                                        for c in gestes_du_monde(m)), 39)
                else:
                    m, cible, _ = web.situation("alimenter", 1)
                    d = DescripteurPublic(web.choisir(m, "alimenter", cible)["envoye"])
                    offres = materiels(m)
                    self.assertIn(d.contenu, offres)
                    self.assertFalse(any(p["geste"] == "mettre" and p["cible"] == "outil_deux"
                                         and p["parametres"]["destination"] == "outil_un" for p in offres))
                liste = gestes_du_monde(m)
                numero = next(str(i) for i, c in enumerate(liste, 1) if c.descripteur == d)
                texte = rendre_liste(liste)
                self.assertNotIn("personne_", texte)
                self.assertNotIn("carte (", texte)
                self.assertNotIn("[", texte)
                reprise = recharger(m)
                self.assertEqual(m.data, reprise.data)
                self.assertEqual(gestes_du_monde(reprise), liste)
                self.assertEqual(web.vues(m), web.vues(reprise))
                attendu, _ = web.OutilsPublicsTests().boucle(m.copier(), d)
                obtenu, lignes, menus = terminal.ConsoleTests().jouer_console(m, [numero])
                self.assertEqual(menus[0], texte)
                self.assertEqual(terminal.sans_saisie(obtenu.data), terminal.sans_saisie(attendu.data))
                self.assertEqual(web.vues(obtenu), web.vues(attendu))
                self.assertEqual(web.vues(obtenu), web.vues(recharger(obtenu)))
                if cas == "conduite":
                    self.assertFalse(obtenu.objets["lanterne"]["allume"])
                else:
                    self.assertEqual(obtenu.objets["outil_deux"]["charges"], 1)
                mesures.append({"cas": cas, "offres": len(liste), "numero": numero,
                                "touches": len(numero) + 1, "appels_modele": 0})
        print("MESURES_CORRECTION_307=" + json.dumps(mesures, ensure_ascii=False))

    def test_capacites_absentes_inconnues_et_destinations_fermees_absentes_des_deux_interfaces(self):
        for geste in ("deverrouiller", "crocheter", "frapper", "alimenter", "mettre"):
            for variante in (0, 1):
                with self.subTest(geste=geste, variante=variante):
                    m, cible, _ = web.situation(geste, variante)
                    d = web.choisir(m, geste, cible, "autre_cible" if geste == "mettre" else "outil_deux")["envoye"]
                    if geste == "mettre":
                        m.objets["autre_cible"]["ouverte"] = False
                    else:
                        m.objets["outil_deux"].update(usages=[], ouvre=[])
                    self.assertNotIn(d, materiels(m))
                    page = web.page(m)
                    self.assertNotIn(d, [c["envoye"] for c in page["outils"] + page["inventaire"]])
                    reprise = recharger(m)
                    self.assertEqual(materiels(m), materiels(reprise))
                    self.assertEqual(web.vues(m), web.vues(reprise))

    def test_matiere_incompatible_et_forme_inconnue_non_inventees(self):
        for variante in (0, 1):
            m, cible, _ = web.situation("alimenter", variante)
            d = web.choisir(m, "alimenter", cible)["envoye"]
            m.objets["outil_deux"]["charges"] = 0
            self.assertNotIn(d, materiels(m))
            m.objets["outil_deux"]["charges"] = 2
            m.objets["outil_deux"]["contenu"] = {"matiere": "vin"}
            self.assertNotIn(d, materiels(m))
            m, cible, _ = web.situation("frapper", variante)
            d = web.choisir(m, "frapper", cible)["envoye"]
            m.objets["outil_deux"]["usages"] = ["couper"]
            m.objets[cible].pop("seuil_coupe", None)
            avant = copy.deepcopy(m.data)
            self.assertNotIn(d, materiels(m))
            self.assertEqual(m.data, avant)
            self.assertEqual(recharger(m).data, avant)

    def test_nouvel_usage_moteur_sans_nouveau_verbe_et_surfaces_fixes_exclues(self):
        m, cible, _ = web.situation("frapper")
        m.objets["outil_deux"]["usages"] = []
        d = {"geste": "frapper", "cible": cible, "parametres": {"outil": "outil_deux"}}
        self.assertNotIn(d, materiels(m))
        m.objets["outil_deux"]["usages"] = ["percussion"]
        self.assertIn(d, materiels(m))
        self.assertTrue(Moteur(m.copier()).preparer(DescripteurPublic(d)).effets)
        m.objets["outil_deux"]["mobile"] = False
        self.assertNotIn(d, materiels(m))
