"""L'économie de combustible conserve la lumière nécessaire devant une cible."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation, pnj, planification
from donjon.banc_pnj import executer
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire, memoriser
from donjon.monde import Monde
from donjon.rendu import regarder
from tests.test_marche import tranquilles, intention, placer, ecarter_tous, gestes
from tests.test_tensions import recharger


class FlammeNecessaireTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(regarder(n), regarder(m))
        return n

    def test_capture_1985_avant_premier_allumage_sans_cycle(self):
        with gzip.open(Path(__file__).parent / 'data/amener-1985-avant-allumer.json.gz',
                       'rt', encoding='utf8') as f:
            donnees = json.load(f)
        # 360 : la capture porte déjà le levier chez Ilse (t=102), mais
        # Aubin le croit encore au sol depuis t=98. Isoler le plan de flamme
        # de cette découverte tardive, désormais racontable selon 337.
        # Seul ce savoir initial change ; objets, besoins et assertions restent.
        connu = donnees['esprits']['aubin']['croyances']['pied_de_biche']['lieu']
        ilse = donnees['objets']['ilse']
        connu.update(valeur='ilse', source='savoir', salle=ilse['lieu'], case=ilse['position'])
        m = self.recharge(Monde(donnees))
        # On isole la lumière nécessaire au propre plan de Brune : aucun
        # repas de secours livré par un tiers ne vient achever ce plan.
        from tests.support import sans_souci
        sans_souci(m, 'marchand', 'ilse', 'aubin')
        chronique, _ = executer(m, 240)
        m = self.recharge(m)
        allumages = [c for c in chronique if c['pnj'] == 'brune'
                     and 'allume la torche' in c['texte']]
        extinctions = [c for c in chronique if c['pnj'] == 'brune'
                       and 'éteint la torche' in c['texte']]
        self.assertLessEqual(len(allumages), 4)
        self.assertLessEqual(len(extinctions), 3)
        self.assertFalse(any(c['minute'] >= 213 for c in extinctions))

    def test_autre_personne_lanterne_cible_sombre_et_salle_claire(self):
        m = tranquilles()
        ecarter_tous(m, 'ilse', 'brune', 'aubin')
        placer(m, 'marchand', 'antichambre', [7, 3])
        deplacer(m, 'lanterne', 'marchand')
        deplacer(m, 'crochets', 'marchand')
        m.objets['lanterne'].update(allume=True, combustible=60)
        m.objets['reserve'].update(verrouillee=True, ouverte=False)
        croire(m, 'marchand', 'reserve', 'lieu', 'antichambre', 'vu',
               salle='antichambre', case=m.objets['reserve']['position'])
        croire(m, 'marchand', 'reserve', 'lumiere', 0, 'vu', allumees=[])
        croire(m, 'marchand', 'antichambre', 'etat',
               {'eclairee': True, 'niveau': 2, 'propre': 2}, 'vu')
        memoriser(m, 'marchand', {'type': 'flamme_employee', 'objet': 'lanterne'})
        intention(m, 'marchand', [{'operation': 'crocheter', 'cible': 'reserve',
                                 'outil': 'crochets', 'contenu': {'lumiere': 2}}])
        m = self.recharge(m)
        # Le plan et son entretien jugent la même cible, sans la source portée.
        v = planification.vue(m, 'marchand')
        e = planification.depart(m, 'marchand', v)
        sans = e.apres(portes=e.portes - {'lanterne'})
        self.assertEqual(v.lumiere_devant(sans, 'reserve'), 0)
        self.assertTrue(deliberation.lumiere_utile(m, 'marchand'))
        deliberation.menager_flamme(m, 'marchand', m.data['minutes'])
        self.assertEqual(lire(m, 'marchand')['intention']['plan'][0]['operation'], 'crocheter')
        with patch.object(Monde, 'd20', return_value=20):
            gestes(m, 'marchand', 30)
        m = self.recharge(m)
        self.assertFalse(m.objets['reserve']['verrouillee'])
        self.assertTrue(m.objets['lanterne']['allume'])
        self.assertFalse(any('éteint la lanterne' in c['texte'] for c in m.data['chronique']))
