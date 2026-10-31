"""L'estimation s'arrête à l'accord ; seuls les gestes réels changent le monde."""
import unittest
from unittest.mock import patch

from donjon import planification as p, pnj
from donjon.deplacement_objet import deplacer
from donjon.echanges import executer as echanger
from donjon.esprits import croire, percevoir_tous
from donjon.geometrie import cases
from donjon.monde import Monde
from donjon.rendu import decrire_perception
from tests import test_lampes_buts as lampes
from tests.test_tensions import recharger


class PartEstimeeTests(unittest.TestCase):
    def scene(self):
        return lampes.LumiereDuButTests().scene("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")

    def test_accord_et_recherche_ne_changent_rien_avant_la_part_reelle(self):
        m = self.scene()
        but = lambda v, e: e.fait("inspecte", "reserve") and v.lumiere(e)
        # Le parcours réel, comme celui de l'auberge dans test_lampes_buts,
        # conserve propriété, ressources et rendu à travers chaque rechargement.
        lampes.LumiereDuButTests().accomplir(m, "remy", "lampe_remy", "bidon_huile", but,
                                    {"inspecter": ("reserve",)})

    def test_bois_remis_pour_un_feu_puis_recharge_allumage_et_chaleur(self):
        m = self.scene()
        deplacer(m, "poele", "reserve", position=[2, 1])
        m.objets["poele"].update(proprietaire="remy", allume=False, combustible=0)
        m.objets["poele"].pop("contenu", None)
        m.objets["bidon_huile"]["contenu"] = {"matiere": "bois"}
        m.objets["lampe_remy"]["contenu"] = {"matiere": "cire"}
        m.objets["bois_gaspard"]["charges"] = 0
        percevoir_tous(m)
        croire(m, "remy", "bois_gaspard", "etat", {"disponible": False}, "savoir")
        croire(m, "remy", "poele", "etat", {"allume": False, "charge": False}, "savoir")
        m = recharger(m)
        but = lambda v, e: bool(e.fait("chauffe", "poele"))
        with patch.object(Monde, "d20", return_value=20), patch.object(p, "VERIFIER", True):
            r = p.chercher(m, "remy", but, {"entretenir": ("poele",)}, emplois=("feu",))
            self.assertIsNotNone(r)
            demande = p._couper(r[1])[0]
            self.assertTrue(demande["contenu"]["remettre_part"])
            self.assertTrue(echanger(m, "remy", demande, []))
            m = recharger(m)
            self.assertFalse(m.objets["poele"]["allume"])
            piece = next(k for k in m.objets if k.startswith("bidon_huile_"))
            self.assertEqual(m.objets[piece]["proprietaire"], "remy")
            r = p.chercher(m, "remy", but, {"entretenir": ("poele",)}, emplois=("feu",))
            self.assertEqual([x["operation"] for x in p._couper(r[1])], ["alimenter", "allumer", "chauffer"])
            lignes = []
            for etape in p._couper(r[1]):
                self.assertTrue(pnj._executer(m, "remy", etape, lignes, []))
                m = recharger(m)
        self.assertTrue(m.objets["poele"]["allume"])
        self.assertGreater(m.objets["poele"]["combustible"], 0)
        self.assertEqual(m.objets["bidon_huile"]["charges"], 2)
        self.assertEqual(m.objets[piece]["charges"], 0)
        self.assertIn("éclaire la pièce", decrire_perception(m))

    def test_part_de_bois_recue_reste_moyen_du_feu_avec_ou_sans_contact(self):
        from donjon import memoire
        from donjon.esprits import lire
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        for verifier_contact in (False, True):
            with self.subTest(contact=verifier_contact):
                m = self.scene()
                deplacer(m, 'poele', 'reserve', position=[2, 1])
                m.objets['poele'].update(proprietaire='remy', allume=False, combustible=0)
                m.objets['poele'].pop('contenu', None)
                m.objets['bidon_huile']['contenu'] = {'matiere': 'bois'}
                m.objets['lampe_remy']['contenu'] = {'matiere': 'cire'}
                m.objets['bois_gaspard']['charges'] = 0
                percevoir_tous(m)
                croire(m, 'remy', 'bois_gaspard', 'etat', {'disponible': False}, 'savoir')
                croire(m, 'remy', 'poele', 'etat', {'allume': False, 'charge': False}, 'savoir')
                condition = {'objet': 'poele', 'allume': True}
                with patch.object(Monde, 'd20', return_value=20):
                    r = p.chercher(m, 'remy', lambda v,e: bool(e.fait('chauffe','poele')),
                                   {'entretenir': ('poele',)}, emplois=('feu',))
                    self.assertTrue(echanger(m, 'remy', p._couper(r[1])[0], []))
                piece = next(s['objet'] for s in memoire.episodes_parts_promises(m, 'remy')
                             if s['type'] == 'recu' and s.get('lot') == 'bidon_huile')
                self.assertEqual(m.objets[piece]['lot_origine'], 'bidon_huile')
                memoire.evincer_episodes(m, 'remy', lambda s: True)
                if verifier_contact:
                    pnj._inspecter(m, 'remy', 'gaspard', [])
                m = recharger(m)
                but, plan = p.planifier_pulsion(m, 'remy', condition)
                self.assertEqual(but, {'type': 'pulsion', **condition})
                self.assertTrue(any(g['operation'] == 'alimenter' and g['outil'] == piece for g in plan))
                self.assertFalse(any(g['operation'] in ('demander','acheter') for g in plan))
                for geste in plan:
                    self.assertTrue(pnj._executer(m, 'remy', geste, [], []))
                    m = recharger(m)
                self.assertTrue(m.objets['poele']['allume'])
                self.assertGreater(m.objets['poele']['combustible'], 0)
                self.assertEqual(m.objets[piece]['charges'], 0)
                n = recharger(m)
                self.assertEqual(m.data, n.data)
                self.assertEqual(regarder(m), regarder(n))
                self.assertEqual(scene_percue(m), scene_percue(n))

    def test_un_lieu_deja_eclaire_coute_moins_que_demander_et_allumer(self):
        m = self.scene()
        m.data["salles"]["bureau"]["lumiere_naturelle"] = 2
        croire(m, "remy", "bureau", "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "savoir")
        # La porte ouverte est connue : le trajet lumineux est réellement accessible.
        for k, x in m.objets.items():
            if x["type"] == "porte":
                x["verrouillee"] = False
                croire(m, "remy", k, "verrouillee", False, "savoir")
        m = recharger(m)
        with patch.object(p, "VERIFIER", True):
            r = p.chercher(m, "remy", p.eclaire, {"eclairer": True}, emplois=())
        self.assertIsNotNone(r)
        self.assertLess(r[0], 1 + p.DEMANDE / p.Vue(m, "remy").chances_demandes["gaspard"] + 2)
        self.assertTrue(all(x["operation"] == "aller" for x in r[1]))
        for etape in r[1]:
            for _ in range(100):
                if pnj._executer(m, "remy", etape, [], []):
                    break
            else:
                self.fail("Le trajet prévu n'aboutit pas")
            m = recharger(m)
        self.assertEqual(m.objets["bidon_huile"]["charges"], 3)
        self.assertFalse(m.objets["lampe_remy"]["allume"])
        self.assertEqual(m.objets["remy"]["lieu"], "bureau")
        prises = {tuple(x.get("position", ())) for x in m.objets.values()
                  if x["type"] == "personnage" and x.get("lieu") == "bureau"}
        position = next(c for c in sorted(cases(m.data["salles"]["bureau"])) if c not in prises)
        m.joueur.update(salle="bureau", position=list(position))
        m = recharger(m)
        self.assertIn("la lumière est suffisante", decrire_perception(m))

    def test_sans_flamme_pas_de_source_allumee_estimee(self):
        m = self.scene()
        for k, x in m.objets.items():
            if "allumage" in x.get("usages", ()):
                deplacer(m, k, "joueur")
                croire(m, "remy", k, "lieu", "joueur", "savoir", salle="reserve", case=[1, 2])
        m = recharger(m)
        with patch.object(p, "VERIFIER", True):
            self.assertIsNone(p.chercher(m, "remy", p.eclaire, {"eclairer": True}, emplois=()))
        self.assertEqual(m.objets["bidon_huile"]["charges"], 3)
        self.assertFalse(m.objets["lampe_remy"]["allume"])
        self.assertNotIn("éclaire la pièce", decrire_perception(recharger(m)))

    def test_une_source_empruntee_reste_rechargeable_apres_la_remise(self):
        m = self.scene()
        deplacer(m, "lampe_remy", "gaspard")
        m.objets["lampe_remy"]["proprietaire"] = "gaspard"
        percevoir_tous(m)
        croire(m, "remy", "lampe_remy", "lieu", "gaspard", "savoir", salle="reserve", case=[3, 2])
        m = recharger(m)
        with patch.object(Monde, "d20", return_value=20), patch.object(p, "VERIFIER", True):
            r = p.chercher(m, "remy", p.eclaire, {"eclairer": True}, emplois=())
            self.assertIsNotNone(r)
            # L'estimation peut commencer par la part ou par l'emprunt. Chaque
            # accord est exécuté séparément, puis le monde rechargé et replanifié.
            lignes = []
            for _ in range(12):
                r = p.chercher(m, "remy", p.eclaire, {"eclairer": True}, emplois=())
                self.assertIsNotNone(r)
                etapes = p._couper(r[1])
                if not etapes:
                    break
                for etape in etapes:
                    self.assertTrue(pnj._executer(m, "remy", etape, lignes, []), etape)
                    m = recharger(m)
                if m.objets["lampe_remy"]["allume"]:
                    break
        self.assertTrue(m.objets["lampe_remy"]["allume"])
        self.assertEqual(m.objets["lampe_remy"]["proprietaire"], "gaspard")
        self.assertEqual(m.objets["lampe_remy"]["lieu"], "remy")
        self.assertEqual(m.objets["bidon_huile"]["charges"], 2)
        self.assertIn("éclaire la pièce", decrire_perception(recharger(m)))


if __name__ == "__main__":
    unittest.main()
