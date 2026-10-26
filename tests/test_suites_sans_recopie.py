"""Composition des effets de route, successeurs et rendu persisté."""
import copy
import gzip
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger
from tools.comparer_gestes_noeud import captures


MESURER = p._mesurer


def oracle(v, e, ajout, suivant, duree):
    """Composition de la base dcd7b31, avec reconstruction systématique."""
    if v._cru_spatial is not None and len(ajout) == 1 and ajout[0]['operation'] == 'aller':
        mesure = v.mesure_aller(e, ajout[0]['lieu'])
        if mesure is None:
            return None
        temps, pression, portes = mesure
        faits = dict(suivant.faits)
        faits.update((k, x) for k, x in portes if suivant.faits.get(k) == e.faits.get(k))
        return temps, pression, suivant.apres(faits=faits.items())
    return p._mesurer_direct(v, e, ajout, suivant, duree)


class SuitesSansRecopieTests(unittest.TestCase):
    def test_composition_preserve_les_ecritures_du_destinataire(self):
        for origine, destination, effets in (
            ({}, {}, ()),
            ({('ouvert', 'p'): True}, {('ouvert', 'p'): True}, ((('ouvert', 'p'), True),)),
            ({}, {}, ((('ouvert', 'p'), True), (('verrou', 'p'), False))),
            ({}, {('ouvert', 'p'): False}, ((('ouvert', 'p'), True),)),
            ({}, {}, ((('ouvert', 'p'), None),)),
        ):
            with self.subTest(origine=origine, destination=destination, effets=effets):
                e = p.Etat('a', (), origine)
                suivant = p.Etat('b', (), destination)
                v = SimpleNamespace(_cru_spatial=True, mesure_aller=lambda *_: (0.1, 0.2, effets))
                ajout = [{'operation': 'aller', 'lieu': 'b'}]
                attendu = oracle(v, e, ajout, suivant, 1)
                obtenu = MESURER(v, e, ajout, suivant, 1)
                self.assertEqual(attendu, obtenu)
                self.assertEqual(attendu[2].faits, obtenu[2].faits)
                self.assertEqual(suivant.faits, destination)
                self.assertEqual(e.faits, origine)
                if obtenu[2].faits == suivant.faits:
                    self.assertIs(obtenu[2], suivant)

    def test_captures_successeurs_ordonnes_et_couts_hexadecimaux(self):
        racine = Path(__file__).parent / 'data/cout-12h'
        with patch.object(p, '_mesurer', oracle):
            attendu = captures(p, racine)
        self.assertEqual(attendu, captures(p, racine))

    def test_tour_moteur_et_rendu_apres_recharge(self):
        for scenario in ('auberge', 'mine'):
            with self.subTest(scenario=scenario):
                fichier = Path(__file__).parent / f'data/cout-12h/{scenario}-1985-480.json.gz'
                donnees = json.loads(gzip.decompress(fichier.read_bytes()))
                resultats = []
                for mesurer in (oracle, MESURER):
                    m = recharger(Monde(copy.deepcopy(donnees)))
                    with patch.object(p, '_mesurer', mesurer), patch.object(p, '_MEMOIRE', {}), \
                            patch.object(p, '_GRAPHES', {}), patch.object(p, '_IMPOSSIBLES', {}), \
                            p.diagnostics() as recherches:
                        moteur = Moteur(m)
                        lignes = moteur.executer(moteur.preparer(proposition('attendre')))
                    recharge = recharger(m)
                    self.assertEqual(m.data, recharge.data)
                    self.assertEqual(regarder(m), regarder(recharge))
                    self.assertEqual(scene_percue(m), scene_percue(recharge))
                    resultats.append((recharge.data, lignes, regarder(recharge), scene_percue(recharge),
                        [{k: x for k, x in r.items() if k != 'duree'} for r in recherches]))
                self.assertEqual(*resultats)
