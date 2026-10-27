"""Fins constatées : perception, geste, choix, sauvegarde et rendu."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, defense, deliberation, planification
from donjon.commandes import analyser
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.moteur import Moteur
from donjon.pnj import _executer, _etape
from donjon.rendu import regarder
from tests.support import regarder as orienter
from tests.test_interposition import epreuve
from tests.test_tensions import recharger, vivre


def garde(objet="cle_reserve"):
    m = epreuve()
    deplacer(m, objet, "antichambre", [4, 5])
    p = m.objets["marchand"]["profil"]
    p.update(pulsions=[], agendas=[{"sorte": "garder", "parametres": {"objet": objet}}])
    lire(m, "marchand")["pulsions"] = []
    orienter(m, "marchand", objet)
    percevoir_tous(m)
    agendas.actualiser(m, "marchand")
    return recharger(m)


class FinsTests(unittest.TestCase):
    def verifier_fin(self, m, objet, cause):
        avant = copy.deepcopy(m.data)
        self.assertNotIn(objet, [x.get("objet") for x in agendas.gardes(m, "marchand")])
        with planification.vues_du_choix(m, "marchand"):
            agendas.actualiser(m, "marchand")
            self.assertEqual(m.data, avant)
        m = recharger(m)
        a = agendas.projets(m, "marchand")[0]
        self.assertEqual((a["etat"], a["raison"]), ("abandonne", "bien cru " + cause))
        self.assertNotIn(objet, defense.charges(m, "marchand"))
        # Même une nouvelle croyance positive ne ressuscite pas un agenda fini,
        # y compris lors d'un devis direct sur son identifiant.
        croire(m, "marchand", objet, "lieu", "antichambre", "vu", salle="antichambre", case=[4, 5])
        agendas.actualiser(m, "marchand")
        self.assertIsNone(agendas.planifier(m, "marchand", a["id"]))
        self.assertEqual(agendas.projets(m, "marchand")[0], a)
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(regarder(m), regarder(recharger(m)))
        return m

    def test_deux_biens_detruits_vus_fin_differee_et_recharge(self):
        for objet in ("cle_reserve", "couteau"):
            with self.subTest(objet=objet):
                m = garde(objet)
                m.objets[objet]["integrite"] = 0
                percevoir_tous(m)
                self.assertEqual(lire(m, "marchand")["croyances"][objet]["fin"]["source"], "vu")
                self.verifier_fin(m, objet, "detruit")

    def test_deux_reserves_consommees_vues_sans_modifier_etat_historique(self):
        for objet, champ in (("vivres", "portions"), ("bois", "charges")):
            with self.subTest(objet=objet):
                m = garde(objet)
                m.objets[objet][champ] = 0
                percevoir_tous(m)
                self.assertEqual(lire(m, "marchand")["croyances"][objet]["etat"]["valeur"], {"disponible": False})
                self.verifier_fin(m, objet, "consomme")

    def test_fin_non_vue_et_position_inconnue_ne_terminent_rien(self):
        for objet in ("cle_reserve", "couteau"):
            m = garde(objet)
            deplacer(m, objet, "echoppe", [8, 5])
            m.objets[objet]["integrite"] = 0
            croire(m, "marchand", objet, "lieu", None, "vu", salle=None, case=None)
            percevoir_tous(m)
            deliberation.choisir(m, "marchand", m.data["minutes"])
            m = recharger(m)
            self.assertNotIn("fin", lire(m, "marchand")["croyances"][objet])
            self.assertIn(agendas.projets(m, "marchand")[0]["etat"], ("actif", "sommeil"))
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_suppression_distante_nefface_pas_le_savoir_et_ne_prouve_pas_la_fin(self):
        for objet in ("couteau", "crochets"):
            m = garde(objet)
            avant = copy.deepcopy(lire(m, "marchand")["croyances"][objet])
            del m.objets[objet]
            percevoir_tous(m)
            self.assertEqual(lire(m, "marchand")["croyances"][objet], avant)
            agendas.actualiser(m, "marchand")
            m = recharger(m)
            self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "actif")
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_geste_joueur_et_pnj_meme_preuve_consommation_dans_le_noir(self):
        for acteur in ("joueur", "marchand"):
            for objet in ("vivres", "ration_epreuve"):
                m = garde("vivres")
                if objet != "vivres":
                    m.objets[objet] = copy.deepcopy(m.objets["vivres"])
                    m.objets[objet].update(id=objet, nom="ration d'épreuve", aliases=["ration d'épreuve"])
                deplacer(m, objet, acteur)
                m.objets[objet].update(portions=1, proprietaire=acteur)
                if acteur == "joueur":
                    m.joueur.update(salle="chambre_cloche", position=[1, 3])
                    texte = Moteur(m).executer(Moteur(m).preparer(analyser(m, "manger " + objet)))
                    self.assertIn("Tu manges", texte)
                else:
                    self.assertTrue(_executer(m, acteur, _etape("manger", objet), [], []))
                m = recharger(m)
                self.assertEqual(m.objets[objet]["portions"], 0)
                self.assertEqual(lire(m, acteur)["croyances"][objet]["fin"]["source"], "essai")
                self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_fin_datee_persiste_hors_memoire_et_apres_retrait_des_restes(self):
        m = garde("couteau")
        m.objets["couteau"]["integrite"] = 0
        percevoir_tous(m)
        preuve = copy.deepcopy(lire(m, "marchand")["croyances"]["couteau"]["fin"])
        m.data["minutes"] += 1
        percevoir_tous(m)
        self.assertEqual(lire(m, "marchand")["croyances"]["couteau"]["fin"], preuve)
        lire(m, "marchand")["memoire"] = []
        del m.objets["couteau"]
        percevoir_tous(m)
        self.verifier_fin(m, "couteau", "detruit")

    def test_outil_detruit_par_un_geste_manque_est_connu_de_son_auteur(self):
        for outil in ("marteau", "pied_de_biche"):
            m = garde(outil)
            deplacer(m, outil, "marchand")
            deplacer(m, "coffre", "antichambre", [4, 5])
            m.objets["coffre"].update(verrouillee=True, ouverte=False)
            m.objets[outil]["integrite"] = 1
            with patch.object(type(m), "d20", return_value=1):
                _executer(m, "marchand", _etape("frapper", "coffre", outil=outil), [], [])
            m = recharger(m)
            self.assertEqual(m.objets[outil]["integrite"], 0)
            self.assertEqual(lire(m, "marchand")["croyances"][outil]["fin"]["source"], "essai")
            self.verifier_fin(m, outil, "detruit")

    def test_reparation_constatee_dement_la_fin_sans_renaissance_de_la_garde(self):
        m = garde("couteau")
        m.objets["couteau"]["integrite"] = 0
        percevoir_tous(m)
        m = self.verifier_fin(m, "couteau", "detruit")
        m.objets["couteau"]["integrite"] = 3
        percevoir_tous(m)
        self.assertNotIn("fin", lire(m, "marchand")["croyances"]["couteau"])
        self.assertNotIn("fin", lire(m, "joueur")["croyances"]["couteau"])
        agendas.actualiser(m, "marchand")
        m = recharger(m)
        self.assertEqual(agendas.projets(m, "marchand")[0]["etat"], "abandonne")
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_meme_laps_entier_decoupe_et_choix_interrompu(self):
        m = garde("couteau")
        m.objets["couteau"]["integrite"] = 0
        percevoir_tous(m)
        avant = copy.deepcopy(m.data)
        with self.assertRaises(RuntimeError):
            with planification.vues_du_choix(m, "marchand"):
                agendas.actualiser(m, "marchand")
                raise RuntimeError("choix interrompu")
        self.assertEqual(m.data, avant)
        entier, _ = vivre(recharger(m), 2)
        morceaux, _ = vivre(recharger(m), 1)
        morceaux, _ = vivre(morceaux, 1)
        self.assertEqual(entier.data, morceaux.data)
        self.assertEqual(regarder(entier), regarder(recharger(morceaux)))
        self.assertEqual(agendas.projets(entier, "marchand")[0]["raison"], "bien cru detruit")
