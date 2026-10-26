"""La préparation d'un choix ne change ni les recherches ni la partie rechargée."""
from contextlib import ExitStack, nullcontext
from collections import OrderedDict
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import obstacles, planification as p
from donjon.esprits import croire
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_planification import relais
from tests.test_tensions import recharger


class CoutFixeTests(unittest.TestCase):
    def test_captures_memes_recherches_noeuds_monde_et_rendu_recharges(self):
        for scenario, minute in (("mine", 480), ("auberge", 480), ("auberge", 600)):
            chemin = Path(__file__).parent / f"data/cout-12h/{scenario}-1985-{minute}.json.gz"
            donnees = json.loads(gzip.decompress(chemin.read_bytes()))
            resultats, comptes = [], []
            for partage in (False, True):
                m = recharger(Monde(copy.deepcopy(donnees)))
                recherches, creations, releves = [], [], []
                chercher, init, entrees = p.chercher, p.Vue.__init__, p._entrees_communes

                def observer(*a, **k):
                    r = chercher(*a, **k)
                    recherches.append((a[1], k.get("nom"), r))
                    return r

                def construire(v, *a, **k):
                    creations.append(1)
                    init(v, *a, **k)

                def relever(v):
                    releves.append(1)
                    return entrees(v)

                with ExitStack() as pile:
                    for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                        pile.enter_context(patch.object(p, nom, {}))
                    pile.enter_context(patch.object(p, "chercher", observer))
                    pile.enter_context(patch.object(p.Vue, "__init__", construire))
                    pile.enter_context(patch.object(p, "_entrees_communes", relever))
                    pile.enter_context(patch.object(p, "VERIFIER", False))
                    if not partage:
                        pile.enter_context(patch.object(p, "vues_du_choix", lambda *a: nullcontext()))
                    with p.diagnostics() as diagnostics:
                        moteur = Moteur(m)
                        lignes = moteur.executer(moteur.preparer(proposition("attendre")))
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))
                resultats.append((recherches, [{k: x for k, x in d.items() if k != "duree"}
                                               for d in diagnostics],
                                  recharge.data, lignes, regarder(recharge), scene_percue(recharge)))
                comptes.append((len(creations), len(releves)))
            self.assertEqual(resultats[0], resultats[1], scenario)
            self.assertLess(comptes[1][0], comptes[0][0], scenario)
            self.assertLess(comptes[1][1], comptes[0][1], scenario)

    def test_aucune_vue_ne_survit_au_choix_objet_et_croyance(self):
        for mutation in ("objet", "croyance"):
            m = recharger(relais())
            with p.vues_du_choix(m, "brune"):
                a, b = p.vue(m, "brune"), p.vue(m, "brune")
                self.assertIs(a.proprietaire, b.proprietaire)
                self.assertIsNot(a._crus, b._crus)
                for table in p.TABLES_DU_CHOIX:
                    self.assertIs(getattr(a, table), getattr(b, table), table)
                cle = p._entrees(a, {}, 8, 4000)
                # Une recherche ne transmet ni ses découvertes ni ses prix.
                a.motif, a._lumiere_lue = "faim", True
                a._crus["local"] = 1
                self.assertIsNone(b.motif)
                self.assertFalse(b._lumiere_lue)
                self.assertNotIn("local", b._crus)
            if mutation == "objet":
                from donjon.deplacement_objet import deplacer
                deplacer(m, "crochets", "brune")
            else:
                croire(m, "brune", "reserve", "verrouillee", False, "savoir")
            with p.vues_du_choix(m, "brune"):
                c = p.vue(m, "brune")
                self.assertIsNot(a.proprietaire, c.proprietaire)
                self.assertNotEqual(cle, p._entrees(c, {}, 8, 4000))
            self.assertIsNone(m._vues_du_choix)
            recharge = recharger(m)
            self.assertEqual(m.data, recharge.data)
            self.assertEqual(regarder(m), regarder(recharge))

    def test_controle_de_la_frontiere_et_restauration_apres_exception(self):
        m = relais()
        with patch.object(p, "VERIFIER", True):
            with self.assertRaisesRegex(AssertionError, "méthode candidate"):
                with p.vues_du_choix(m, "brune"):
                    p.vue(m, "brune")
                    croire(m, "brune", "reserve", "verrouillee", False, "savoir")
        self.assertIsNone(m._vues_du_choix)
        with self.assertRaises(ValueError):
            with p.vues_du_choix(m, "brune"):
                raise ValueError()
        self.assertIsNone(m._vues_du_choix)

    def test_parametres_du_candidat_restent_prives(self):
        m = relais()
        with p.vues_du_choix(m, "brune"):
            for motif, emplois, vises in (("faim", {"manger"}, {}),
                                           ("securite", set(), {"eclairer": True}),
                                           ("biens", None, {"danger": ["marchand"]})):
                partagee, neuve = p.vue(m, "brune"), p.Vue(m, "brune")
                for v in (partagee, neuve):
                    v.motif, v.emplois, v.eclairer = motif, emplois, bool(vises.get("eclairer"))
                self.assertEqual(p._entrees(partagee, vises, 8, 4000),
                                 p._entrees(neuve, vises, 8, 4000))

    def test_carte_contenu_et_ordre_edites_en_place(self):
        m = relais()
        cle = obstacles.cle_carte(m)
        with patch.object(obstacles.json, "dumps", wraps=json.dumps) as encoder:
            self.assertIs(cle, obstacles.cle_carte(m))
            self.assertEqual(encoder.call_count, 0)
        salle = next(s for s, d in m.data["salles"].items() if len(d["sorties"]) > 1)
        m.data["salles"][salle]["jour"] = not m.data["salles"][salle].get("jour")
        autre = obstacles.cle_carte(m)
        self.assertNotEqual(cle, autre)
        sorties = m.data["salles"][salle]["sorties"]
        direction = next(iter(sorties))
        sorties[direction]["porte"] = "reserve"
        self.assertNotEqual(autre, obstacles.cle_carte(m))
        cle = obstacles.cle_carte(m)
        m.data["salles"][salle] = m.data["salles"].pop(salle)
        self.assertNotEqual(cle, obstacles.cle_carte(m))
        local = obstacles.cle_carte(m, salle)
        sorties[direction]["porte"] = "porte"
        self.assertNotEqual(local, obstacles.cle_carte(m, salle))
        local = obstacles.cle_carte(m, salle)
        sorties[direction] = sorties.pop(direction)
        self.assertNotEqual(local, obstacles.cle_carte(m, salle))

    def test_obstacle_et_salle_invalident_le_calcul_geometrique(self):
        from tests.test_sous_obstacle import corridor
        m = recharger(corridor())
        with patch.object(obstacles, "_GEOMETRIES_CRUES", OrderedDict()), \
                patch.object(obstacles, "_metrique_necessaire", wraps=obstacles._metrique_necessaire) as calcul:
            obstacles.metrique_necessaire(m, "marchand")
            obstacles.metrique_necessaire(m, "marchand")
            self.assertEqual(calcul.call_count, 1)
            # Les obstacles sont dans la partie dynamique, même carte.
            croire(m, "marchand", "poutre_conduite", "lieu", "echoppe", "savoir",
                   salle="echoppe", case=[5, 2])
            obstacles.metrique_necessaire(m, "marchand")
            self.assertEqual(calcul.call_count, 2)
            m.data["salles"]["echoppe"]["jour"] = not m.data["salles"]["echoppe"].get("jour")
            obstacles.metrique_necessaire(m, "marchand")
            self.assertEqual(calcul.call_count, 3)
