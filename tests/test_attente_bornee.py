"""Un recours borné attend ; nouveaux moyens et paliers le réveillent, après recharge."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.esprits import croire, esprit
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_temps_etat import brune_affamee, decouper
from tests.test_tensions import recharger


def joss():
    return Monde(json.loads(gzip.decompress((Path(__file__).parent /
        "data/attente-bornee-joss.json.gz").read_bytes())))


def chercher_besoin(m, id, besoin):
    with p.vues_du_choix(m, id):
        return p.planifier(m, id, besoin)


class AttenteBorneeTests(unittest.TestCase):
    def setUp(self):
        for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
            remplacement = patch.object(p, nom, {})
            remplacement.start()
            self.addCleanup(remplacement.stop)

    def recharge_visible(self, m):
        avant = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        r = recharger(m)
        self.assertEqual(avant, (r.data, regarder(r), scene_percue(r)))
        return r

    def test_joss_sans_nouveau_ne_recherche_plus_meme_si_le_prix_baisse(self):
        m = joss()
        with p.diagnostics() as recherches:
            self.assertIsNone(chercher_besoin(m, "joss", "faim"))
            self.assertEqual(recherches[-1]["issue"], "borne")
            m = self.recharge_visible(m)
            esprit(m, "joss")["besoins"]["faim"] += .1
            with patch.object(p, "_explorer", side_effect=AssertionError("nouvelle recherche")):
                self.assertIsNone(chercher_besoin(m, "joss", "faim"))
            self.assertEqual(recherches[-1]["issue"], "attente")
        self.recharge_visible(m)

    def test_vivre_nouveau_et_refus_leve_reveillent_le_recours(self):
        for nouveau in ("vivre", "refus"):
            with self.subTest(nouveau=nouveau):
                m = joss()
                chercher_besoin(m, "joss", "faim")
                m = self.recharge_visible(m)
                if nouveau == "vivre":
                    m.objets["rations_hugues"].update(lieu="joss", proprietaire="joss", portions=1)
                    croire(m, "joss", "rations_hugues", "lieu", "joss", "vu", 1,
                           salle=m.objets["joss"]["lieu"], case=m.objets["joss"]["position"])
                    croire(m, "joss", "rations_hugues", "etat", {"disponible": True}, "vu", 1)
                else:
                    esprit(m, "joss")["refus"] = []
                with p.diagnostics() as recherches:
                    r = chercher_besoin(m, "joss", "faim")
                self.assertNotEqual(recherches[-1]["issue"], "attente")
                self.assertGreater(recherches[-1]["noeuds"], 0)
                if nouveau == "vivre":
                    self.assertIsNotNone(r)
                    avant = esprit(m, "joss")["besoins"]["faim"]
                    moteur = Moteur(m)
                    moteur.executer(moteur.preparer(proposition("attendre")))
                    self.assertLess(esprit(m, "joss")["besoins"]["faim"], avant)
                self.recharge_visible(m)

    def test_brune_le_desespoir_franchit_un_palier(self):
        m = brune_affamee()
        esprit(m, "brune")["besoins"]["faim"] = 94
        def chercher(m):
            with p.vues_du_choix(m, "brune"):
                return p.chercher(m, "brune", p.a_mange, nom="faim", memo=["besoin", "faim"],
                                 emplois=("manger",), motif="faim", noeuds=1)
        with p.diagnostics() as recherches:
            self.assertIsNone(chercher(m))
            self.assertEqual(recherches[-1]["issue"], "borne")
            m = self.recharge_visible(m)
            self.assertIsNone(chercher(m))
            self.assertEqual(recherches[-1]["issue"], "attente")
            esprit(m, "brune")["besoins"]["faim"] = 95
            chercher(m)
            self.assertNotEqual(recherches[-1]["issue"], "attente")
        self.recharge_visible(m)

    def test_non_bornee_ne_cree_pas_d_attente(self):
        fichier = Path(__file__).parent / "data/cout-12h/auberge-1985-480.json.gz"
        m = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
        with p.diagnostics() as recherches:
            chercher_besoin(m, "joss", "faim")
            self.assertNotEqual(recherches[-1]["issue"], "borne")
            self.assertFalse(esprit(m, "joss")["attentes_bornees"])
            m = self.recharge_visible(m)
            esprit(m, "joss")["besoins"]["faim"] += .1
            chercher_besoin(m, "joss", "faim")
            self.assertNotEqual(recherches[-1]["issue"], "attente")

    def test_recours_sans_motif_explicite_suit_les_paliers_des_besoins(self):
        m = brune_affamee()
        esprit(m, "brune")["besoins"]["faim"] = 94
        def chercher(m):
            with p.vues_du_choix(m, "brune"):
                return p.chercher(m, "brune", p.a_mange, memo=["condition"], noeuds=1)
        with p.diagnostics() as recherches:
            chercher(m)
            self.assertEqual(recherches[-1]["issue"], "borne")
            m = self.recharge_visible(m)
            chercher(m)
            self.assertEqual(recherches[-1]["issue"], "attente")
            esprit(m, "brune")["besoins"]["faim"] = 95
            chercher(m)
            self.assertNotEqual(recherches[-1]["issue"], "attente")
        self.recharge_visible(m)

    def test_meme_laps_decoupe_et_rendu_recharge(self):
        def scene():
            m = joss()
            m.joueur["orientation"] = "nord"
            return m
        a, b = decouper(scene, 601, recharger_tous=20)
        a, b = self.recharge_visible(a), self.recharge_visible(b)
        # Les rotations du joueur changent la révision et l'historique de ses
        # actions ; comparer toute la vie du monde, comme test_temps_etat.
        for champ in ("objets", "esprits", "chronique", "gestes_en_cours", "minutes", "instant", "jets",
                      "horloges_declenchees"):
            self.assertEqual(a.data.get(champ), b.data.get(champ), champ)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(scene_percue(a), scene_percue(b))

    def test_seul_le_choix_reel_enregistre_l_effort_apres_les_candidats(self):
        m = self.recharge_visible(brune_affamee())
        avant = copy.deepcopy(m.data)
        def requete():
            return p.chercher(m, "brune", p.a_mange, memo=["contrat"], noeuds=1)
        self.assertIsNone(requete())
        self.assertEqual(m.data, avant)
        with self.assertRaisesRegex(RuntimeError, "choix interrompu"):
            with p.vues_du_choix(m, "brune"):
                requete()
                raise RuntimeError("choix interrompu")
        self.assertEqual(m.data, avant)
        with patch.object(p, "VERIFIER", True), p.vues_du_choix(m, "brune"):
            # Contrôler ici la frontière de lecture seule, indépendamment du
            # contrôle de qualité de la recherche à un seul nœud.
            with patch.object(p, "VERIFIER", False):
                with p.vues_du_choix(m, "brune"):
                    self.assertIsNone(requete())
            self.assertEqual(m.data, avant)
        self.assertTrue(esprit(m, "brune")["attentes_bornees"])
        self.recharge_visible(m)
