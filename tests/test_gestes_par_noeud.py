"""Même graphe ordonné que la base, clés exactes et monde visible rechargé."""
from contextlib import contextmanager, nullcontext
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger
from tools.comparer_gestes_noeud import captures

DONNEES = Path(__file__).parent / "data/cout-12h"


@contextmanager
def sans_preparation():
    # Refaire toutes les lectures, sans employer la projection à contrôler.
    def situations(v, e, agissables):
        return v._situations_gestes_calculer(e, agissables)
    def droits(v, e):
        return v._droits_gestes_calculer(e)
    with patch.object(p.Vue, "situations_gestes", situations), \
            patch.object(p.Vue, "droits_gestes", droits), \
            patch.object(p.Vue, "lot_partageable", return_value=True):
        yield


class GestesTests(unittest.TestCase):
    def test_successeurs_ordre_couts_et_noeuds_de_la_base(self):
        # Empreintes produites par 02c8e8b avec le même outil, avant modification.
        attendus = json.loads((DONNEES / "gestes-attendus.json").read_text(encoding="utf8"))
        self.assertEqual(captures(p, DONNEES), attendus)

    def test_cles_lieux_contenants_porteurs_et_permissions(self):
        for scenario, qui in (("mine", "remy"), ("auberge", "joss")):
            m = Monde(json.loads(gzip.decompress((DONNEES / f"{scenario}-1985-480.json.gz").read_bytes())))
            v = p.Vue(m, qui)
            e = p.depart(m, qui, v)
            objets, _ = v.agissables({})
            situations, droits = v.situations_gestes(e, objets), v.droits_gestes(e)
            autre = e.apres(faits=[(("inspecte", e.salle), True), (("depense",), 3), (("promis", objets[0]), qui)])
            self.assertIs(situations, v.situations_gestes(autre, objets))
            self.assertIs(droits, v.droits_gestes(autre))
            variations = [e.apres(salle=s) for s in v.salles]
            for o in objets:
                variations += [e.apres(portes=e.portes | {o}), e.apres(portes=e.portes - {o})]
                for cle, valeur in (("lieu", e.salle), ("lieu", qui), ("ouvert", True),
                                    ("ouvert", False), ("assomme", True), ("permis", True),
                                    ("achete", True), ("acquis", True)):
                    variations.append(e.apres(faits=[((cle, o), valeur)]))
                owner = v.proprietaire[o]
                variations.append(e.apres(faits=[(("faute", owner, "honnetete"), True)]))
            for etat in variations:
                self.assertEqual(v.situations_gestes(etat, objets), v._situations_gestes_calculer(etat, objets))
                self.assertEqual(v.droits_gestes(etat), v._droits_gestes_calculer(etat))

    def test_monde_et_texte_joueur_apres_rechargement(self):
        for scenario in ("mine", "auberge"):
            donnees = json.loads(gzip.decompress((DONNEES / f"{scenario}-1985-480.json.gz").read_bytes()))
            resultats = []
            for direct in (True, False):
                m = recharger(Monde(copy.deepcopy(donnees)))
                with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                        patch.object(p, "_IMPOSSIBLES", {}), p.diagnostics() as recherches:
                    with sans_preparation() if direct else nullcontext():
                        moteur = Moteur(m)
                        lignes = moteur.executer(moteur.preparer(proposition("attendre")))
                recharge = recharger(m)
                self.assertEqual(m.data, recharge.data)
                self.assertEqual(regarder(m), regarder(recharge))
                self.assertEqual(scene_percue(m), scene_percue(recharge))
                resultats.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge),
                                  [{k: x for k, x in r.items() if k != "duree"} for r in recherches]))
            self.assertEqual(*resultats, scenario)
