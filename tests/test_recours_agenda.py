"""338 : coût fini, continuité du moyen et constat persistants."""
import copy
import gzip
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, planification, pnj
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests import test_agendas_faire_confier as faire
from tests.test_social import placer
from tests.test_tensions import recharger


class RecoursAgendaTests(unittest.TestCase):
    def recharge(self, m):
        avant = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual((n.data, regarder(n), scene_percue(n)), avant)
        return n

    def test_capture_317_constat_et_laps_apres_recharge(self):
        with gzip.open(Path(__file__).with_name('data') / 'recours-338-crue-3-160.json.gz',
                       'rt', encoding='utf-8') as f:
            m = self.recharge(Monde(json.load(f)))
        fins = []
        for laps in ([15], [1] * 15):
            n = self.recharge(m.copier())
            for minutes in laps:
                duree = minutes * 600
                pnj.avancer(n, ecouler(n, duree), [], duree)
                n = self.recharge(n)
            e = lire(n, 'marchand')
            self.assertGreaterEqual(e['visites'].get('chambre_cloche', -1), 170)
            self.assertEqual(e['croyances']['ilse']['lieu']['valeur'], 'chambre_cloche')
            self.assertGreaterEqual(e['croyances']['ilse']['lieu']['minute'], 170)
            self.assertFalse([x for x in n.data['chronique'] if x.get('pnj') == 'marchand'
                              and x['minute'] > 170 and 'passe dans' in x['texte']])
            fins.append(n)
        self.assertEqual(fins[0].data, fins[1].data)
        self.assertEqual(regarder(fins[0]), regarder(fins[1]))
        self.assertEqual(scene_percue(fins[0]), scene_percue(fins[1]))

    def test_inspection_et_attente_devises_sans_delegation(self):
        m, _ = faire.FaireConfierTests().scene()
        placer(m, 'marchand', 'chambre_cloche', [1, 1])
        e = lire(m, 'marchand')
        e['aides_attendues']['brune'] = {'qui': 'brune', 'minute': 0,
            'condition': {'objet': 'brune', 'lieu': 'chambre_cloche'}}
        for visite in (-1, 0):
            with self.subTest(visite=visite):
                e['visites']['chambre_cloche'] = visite
                n = self.recharge(m.copier())
                cout = []
                propre = agendas.planifier(n, 'marchand', 'evacuer', cout=cout)
                self.assertTrue(math.isfinite(cout[0]))
                self.assertEqual([x['operation'] for x in propre[1]], ['inspecter'] if visite < 0 else [])
                self.assertEqual(agendas.planifier(n, 'marchand', 'evacuer'), propre)
                self.assertGreater(cout[0], 0) if visite < 0 else self.assertEqual(cout[0], 0)

    def test_moyen_tenu_deplacement_seul_nouvelle_entree_le_rouvre(self):
        m, _ = faire.FaireConfierTests().scene('informer', 'ilse')
        deliberation.choisir(m, 'marchand', m.data['minutes'])
        m = self.recharge(m)
        i = copy.deepcopy(lire(m, 'marchand')['intention'])
        self.assertTrue(i['plan'])
        # La méthode recalculerait d'autres moyens à ce nouveau départ. Sans
        # événement, elle ne doit pas remplacer le suffixe encore admissible.
        placer(m, 'marchand', 'antichambre', [2, 4])
        croire(m, 'marchand', 'marchand', 'lieu', 'antichambre', 'vu',
               salle='antichambre', case=[2, 4])
        m = self.recharge(m)
        with patch.object(agendas, 'planifier', wraps=agendas.planifier) as calcul:
            deliberation.choisir(m, 'marchand', m.data['minutes'])
            self.assertEqual(calcul.call_count, 0)
        self.assertEqual(lire(m, 'marchand')['intention']['plan'], i['plan'])
        croire(m, 'marchand', 'ilse', 'lieu', 'chambre_cloche', 'dit:ilse',
               salle='chambre_cloche', case=None)
        m = self.recharge(m)
        with patch.object(agendas, 'planifier', wraps=agendas.planifier) as calcul:
            deliberation.choisir(m, 'marchand', m.data['minutes'])
            self.assertGreater(calcul.call_count, 0)
        self.recharge(m)

    def test_autre_scenario_agenda_garder_attente_et_laps(self):
        from donjon.banc_pnj import creer
        from tests.support import calme
        m = creer('auberge', 42, 'fixe')
        for acteur, objet in m.objets.items():
            if objet.get('profil'):
                calme(m, acteur)
                objet['profil']['agendas'] = []
                lire(m, acteur).pop('agendas', None)
        acteur = 'anselme'
        lieu = m.objets[acteur]['lieu']
        m.objets[acteur]['profil']['agendas'] = [
            {'id': 'veille', 'sorte': 'garder', 'parametres': {'lieu': lieu}}]
        agendas.actualiser(m, acteur)
        cout = []
        r = agendas.planifier(m, acteur, 'veille', cout=cout)
        self.assertEqual(r[1], [])
        self.assertTrue(math.isfinite(cout[0]))
        fins = []
        for laps in ([3], [1] * 3):
            n = self.recharge(m.copier())
            for minutes in laps:
                duree = minutes * 600
                pnj.avancer(n, ecouler(n, duree), [], duree)
                n = self.recharge(n)
            self.assertEqual(n.objets[acteur]['lieu'], lieu)
            self.assertEqual(lire(n, acteur)['intention']['plan'], [])
            self.assertEqual(lire(n, acteur)['intention']['but']['agenda'], 'veille')
            fins.append(n)
        self.assertEqual(fins[0].data, fins[1].data)

    def test_infini_reserve_a_absence_de_recours(self):
        m, _ = faire.FaireConfierTests().scene()
        propre = ({'type': 'agenda', 'agenda': 'evacuer', 'qui': 'brune'}, [])
        for mesure in ([], [float('inf')], [float('nan')]):
            with self.assertRaises(ValueError):
                agendas.choisir_mandataire(m, 'marchand', 'evacuer', propre, mesure)


if __name__ == '__main__':
    unittest.main()
