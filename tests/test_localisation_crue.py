"""Les localisations mobiles ont une source, y compris après sauvegarde."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon import deliberation as d
from donjon.esprits import croire, lire, percus
from donjon.geometrie import cases, placer
from donjon.monde import Monde, mobile_par_nature
from donjon.pnj import occupants
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.spatial import _case_libre
from tests.test_tensions import recharger, vivre
from tests.test_voix import hugues_cherche_anselme


def capture():
    with gzip.open(Path(__file__).with_name('data') / 'localisation-211-crue.json.gz',
                   'rt', encoding='utf8') as f:
        return Monde(json.load(f))


class LocalisationTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_position_cachee_ne_change_pas_la_croyance_ni_le_plan(self):
        for m, acteur, cible, salles in [
                (capture(), 'ilse', 'aubin', ('crypte', 'echoppe')),
                (hugues_cherche_anselme(), 'hugues', 'anselme', ('chambre_chaude', 'etable'))]:
            with self.subTest(acteur=acteur):
                lire(m, acteur)['croyances'].setdefault(cible, {}).pop('lieu', None)
                esprit = copy.deepcopy(lire(m, acteur))
                plans = []
                for salle in salles:
                    n = Monde(copy.deepcopy(m.data))
                    occupees = occupants(n, cible)
                    for case in sorted(cases(n.data['salles'][salle])):
                        if (salle, case) in occupees or not _case_libre(n, salle, case):
                            continue
                        placer(n.objets[cible], salle, case)
                        if cible not in percus(n, acteur)[0]:
                            break
                    else:
                        self.fail(f'Aucune case libre non perçue dans {salle}')
                    n = self.recharge(n)
                    self.assertNotIn(cible, percus(n, acteur)[0])
                    self.assertEqual(esprit, lire(n, acteur))
                    self.assertIsNone(d._lieu_cru(n, acteur, cible))
                    self.assertIsNone(d.salle_crue(n, acteur, cible))
                    d.choisir(n, acteur, n.data['minutes'])
                    n = self.recharge(n)
                    plans.append(copy.deepcopy(lire(n, acteur)['intention']))
                self.assertEqual(plans[0], plans[1])

    def test_sources_declarees_absence_et_emboitement(self):
        m = capture()
        for source in ('savoir', 'vu', 'entendu'):
            croire(m, 'ilse', 'aubin', 'lieu', 'echoppe', source, salle='echoppe', case=None)
            m.objets['aubin']['lieu'] = 'crypte'
            m = self.recharge(m)
            self.assertEqual(d.salle_crue(m, 'ilse', 'aubin'), 'echoppe')
        croire(m, 'ilse', 'aubin', 'lieu', None, 'essai', salle=None, case=None)
        m = self.recharge(m)
        self.assertIsNone(d.salle_crue(m, 'ilse', 'aubin'))
        fixe = next(k for k, o in m.objets.items() if not mobile_par_nature(o)
                    and o['lieu'] in m.data['salles'])
        lire(m, 'ilse')['croyances'].pop(fixe, None)
        self.assertEqual(d.salle_crue(self.recharge(m), 'ilse', fixe), m.objets[fixe]['lieu'])
        mobile = next(k for k, o in m.objets.items() if o.get('mobile'))
        lire(m, 'ilse')['croyances'].pop(mobile, None)
        self.assertIsNone(d._lieu_cru(self.recharge(m), 'ilse', mobile))
        croire(m, 'ilse', mobile, 'lieu', 'aubin', 'savoir', salle='crypte', case=None)
        self.assertIsNone(d.salle_crue(self.recharge(m), 'ilse', mobile))
        croire(m, 'ilse', 'aubin', 'lieu', 'echoppe', 'entendu', salle='echoppe', case=None)
        self.assertEqual(d.salle_crue(self.recharge(m), 'ilse', mobile), 'echoppe')

    def test_temps_entier_ou_decoupe_apres_recharge(self):
        for m in (capture(), hugues_cherche_anselme()):
            entier, _ = vivre(self.recharge(m), 2)
            morceaux, _ = vivre(self.recharge(m), 1)
            morceaux, _ = vivre(self.recharge(morceaux), 1)
            self.assertEqual(entier.data, morceaux.data)
            self.assertEqual(regarder(entier), regarder(morceaux))
            self.assertEqual(scene_percue(entier), scene_percue(morceaux))
