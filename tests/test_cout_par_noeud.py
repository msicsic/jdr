"""Table géométrique exacte : tarifs directs et parties réellement rechargées."""
from contextlib import contextmanager, nullcontext
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p, trajet_estime, route_admissible, spatial
from donjon.esprits import croire
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.obstacles import sejours_route
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import MINUTE
from tests.test_tensions import recharger
from tests.test_trajets_reels import flammes, savoir


def route_directe(v, e, salle, ouvertes=None):
    ouvertes = v.ouvertes(e) if ouvertes is None else ouvertes
    # Clé volontairement complète pour la mesure témoin, sans fusion d'états.
    cle = ("temoin", e, ouvertes)
    if cle not in v._parcours:
        v._parcours[cle] = trajet_estime.parcours(v, e, ouvertes)
    route = v._parcours[cle].get(salle)
    return route if route is not None and not route_admissible.refus(v, e, route, salle) else None


def prix_direct(v, e, route):
    return sum(d / MINUTE * v.pression(e.apres(salle=s))
               for s, d in sejours_route(route, e.orientation) if d)


def arrivee_directe(v, e, salle, route):
    faits = [(k, x) for porte in sorted(route.portes)
             if not v.ouvert(e, porte) or v.verrouille(e, porte)
             for k, x in ((("ouvert", porte), True), (("verrou", porte), False))]
    return e.apres(salle=salle, faits=faits)


@contextmanager
def sans_tables():
    init = p.Vue.__init__
    def construire(v, *a):
        init(v, *a)
        v._pression_fixe = None
    with patch.object(p.Vue, "__init__", construire), \
            patch.object(p.Vue, "route", route_directe), \
            patch.object(p.Vue, "prix_route", prix_direct), \
            patch.object(p.Vue, "arrivee", arrivee_directe), \
            patch.object(p, "_mesurer", p._mesurer_direct):
        yield


class TableTests(unittest.TestCase):
    def comparer(self, monde, qui):
        v = p.Vue(recharger(monde), qui)
        e = p.depart(v.monde, qui, v)
        for allure in (15, 30):
            for faits in ([], [(("ouvert", "porte"), True)], [(("verrou", "porte"), True)],
                          [(("verrou", "porte"), False)], [(("inspecte", e.salle), True)]):
                # Les scènes du Relais déclarent cette porte ; les autres
                # exercent les mêmes tarifs avec leurs propres faits de plan.
                if any(k[1] == "porte" for k, x in faits) and "porte" not in v.objets:
                    continue
                etat = e.apres(allure=allure, faits=faits)
                for salle in sorted(v.salles):
                    ajout = [p._etape("aller", lieu=salle)]
                    suivant = etat.apres(salle=salle, faits=[(("inspecte", salle), True)])
                    a = p._mesurer(v, etat, ajout, suivant, 1)
                    with sans_tables():
                        temoin = p.Vue(v.monde, qui)
                        b = p._mesurer(temoin, etat, ajout, suivant, 1)
                    self.assertEqual(a, b, (qui, salle, allure, faits))
                    if a is not None:
                        self.assertEqual(float(a[0]).hex(), float(b[0]).hex())
                        self.assertEqual(float(a[1]).hex(), float(b[1]).hex())
                    # Une seconde lecture, même avec un effet terminal de plus,
                    # conserve ce fait et ne reprend pas un état complet.
                    suite = suivant.apres(faits=[(("mange", "test"), True)])
                    c = p._mesurer(v, etat, ajout, suite, 1)
                    if c:
                        self.assertTrue(c[2].fait("mange", "test"))
        return v

    def test_portes_cles_allures_et_reutilisation(self):
        m, qui, _, _ = flammes("relais")
        m.objets["cle"]["lieu"] = qui
        savoir(m, qui, "cle")
        croire(m, qui, "porte", "etat", {"ouverte": False}, "savoir")
        croire(m, qui, "porte", "verrouillee", True, "savoir")
        v = self.comparer(m, qui)
        e = p.depart(v.monde, qui, v)
        self.assertIsNotNone(v.route(e, "beffroi"))
        self.assertIsNone(v.route(e.apres(portes=e.portes - {"cle"}), "beffroi"))
        with patch.object(v, "route", wraps=v.route) as route:
            v.mesure_aller(e, "beffroi")
            n = route.call_count
            v.mesure_aller(e.apres(faits=[(("inspecte", e.salle), True)]), "beffroi")
            self.assertEqual(route.call_count, n)

    def test_obstacle_equipement_et_eau_attendue(self):
        from tests.test_sous_obstacle import corridor
        from tests.test_route_admissible import scene
        m = corridor()
        self.comparer(m, "marchand")
        self.comparer(scene(), "brune")

    def test_approches_et_lumiere_ne_confondent_pas_les_tarifs(self):
        for scenario in ("relais", "mine"):
            m, qui, source, feux = flammes(scenario)
            m.objets[qui]["profil"]["valeurs"]["courage"] = 0
            croire(m, qui, m.objets[qui]["lieu"], "etat",
                   {"eclairee": False, "niveau": 0, "propre": 0}, "savoir")
            v = p.Vue(m, qui)
            # Le noir est une donnée crue ; le plan peut allumer la source.
            v.peur = 1
            v._pression_fixe = None
            e = p.depart(m, qui, v)
            for etat in (e, e.apres(faits=[(("allume", source), True)]),
                         e.apres(portes=e.portes - {source})):
                for cible in feux:
                    route = v.approche(etat, p._etape("allumer", source, outil=cible))
                    if route is not None:
                        self.assertEqual(v.prix_route(etat, route), prix_direct(v, etat, route))
                        self.assertEqual(v.prix_route(etat, route), prix_direct(v, etat, route))
            self.assertGreater(v.pression(e), v.pression(e.apres(faits=[(("allume", source), True)])))

    def test_controle_spatial_refait_la_table(self):
        m, qui, _, _ = flammes("relais")
        v = p.Vue(m, qui)
        e = p.depart(m, qui, v).apres(faits=[(("ouvert", "porte"), False), (("verrou", "porte"), False)])
        with patch.object(spatial, "VERIFICATION", 1):
            v.mesure_aller(e, "beffroi")
            identique = p.Etat(e.salle, e.portes, reversed(list(e.faits.items())))
            v.mesure_aller(identique, "beffroi")
            v._mesures_allers[next(iter(v._mesures_allers))] = None
            with self.assertRaisesRegex(AssertionError, "Table des trajets périmée"):
                v.mesure_aller(e, "beffroi")
        # Un témoin indexé par la projection à contrôler masquerait cette
        # omission de verrou. Le témoin par état complet doit la détecter.
        v = p.Vue(m, qui)
        with patch.object(spatial, "VERIFICATION", 1), \
                patch.object(v, "contexte_route", return_value=("projection_incomplete",)):
            v.mesure_aller(e, "beffroi")
            with self.assertRaisesRegex(AssertionError, "Table des trajets périmée"):
                v.mesure_aller(e.apres(faits=[(("verrou", "porte"), True)]), "beffroi")

    def test_captures_reelles_memes_noeuds_et_monde_visible_apres_recharge(self):
        for scenario in ("auberge", "mine"):
            fichier = Path(__file__).parent / f"data/cout-12h/{scenario}-1985-480.json.gz"
            donnees = json.loads(gzip.decompress(fichier.read_bytes()))
            resultats = []
            for direct in (True, False):
                m = recharger(Monde(copy.deepcopy(donnees)))
                with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                        patch.object(p, "_IMPOSSIBLES", {}), p.diagnostics() as recherches:
                    with sans_tables() if direct else nullcontext():
                        moteur = Moteur(m)
                        lignes = moteur.executer(moteur.preparer(proposition("attendre")))
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))
                resultats.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge),
                                  [{k: x for k, x in r.items() if k != "duree"} for r in recherches]))
            self.assertEqual(resultats[0], resultats[1], scenario)
