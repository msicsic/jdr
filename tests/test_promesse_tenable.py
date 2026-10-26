"""La présence matérielle requise au devis est celle du geste et de l'échéance."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, echanges
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.planification import Vue, depart
from donjon.rendu import regarder
from tests.test_tache_promise_recours import reserve, offrir
from tests.test_tensions import recharger


def capture():
    with gzip.open(Path(__file__).parent / 'data/promesse-crue11-210.json.gz',
                   'rt', encoding='utf8') as f:
        return Monde(json.load(f)), 'ilse', 'aubin', {'objet': 'porte', 'verrouillee': True}


class PromesseTenableTests(unittest.TestCase):
    def test_capture_reelle_et_autre_presence_impossible_avant_accord(self):
        for fabrique in (capture, reserve):
            with self.subTest(scene=fabrique.__name__):
                m, id, autre, c = fabrique()
                objet = 'pied_de_biche' if fabrique == capture else 'vivres'
                if fabrique == reserve:
                    # L'intégration au décor est une autre cause de non-présence,
                    # même si le lieu déclaré et les coordonnées sont corrects.
                    m.objets[c['objet']]['incorpore'] = True
                m = recharger(m)
                avant, visible = copy.deepcopy(m.data), regarder(m)
                terme = {'type': 'tache', 'condition': c}
                self.assertIsNone(echanges._devis_proposition(m, id, c, autre))
                self.assertFalse(echanges.promesse_autonome(m, id, autre, terme))
                self.assertTrue(echanges.empeche(m, id, {'condition': c, 'pour': autre}))
                self.assertEqual(echanges.proposer(m, id, autre,
                    {'type': 'objet' if fabrique == capture else 'part', 'objet': objet}, terme)['cause'], 'impossible')
                self.assertEqual(m.data, avant)
                m = recharger(m)
                self.assertEqual(regarder(m), visible)
                self.assertFalse(agendas.en_cours(m, id, condition=c))
                a, b = recharger(m.copier()), recharger(m.copier())
                resultats = []
                for monde, durees in ((a, (120,)), (b, (30, 40, 50))):
                    for duree in durees:
                        moteur = Moteur(monde)
                        moteur.executer(moteur.preparer(proposition('attendre', str(duree / 10))))
                        monde = recharger(monde)
                    types = [s['type'] for s in lire(monde, id)['memoire']]
                    self.assertNotIn('engagement_pris', types)
                    self.assertNotIn('engagement_abandonne', types)
                    self.assertFalse(agendas.en_cours(monde, id, condition=c))
                    resultats.append(monde)
                a, b = resultats
                self.assertEqual(a.data['chronique'], b.data['chronique'])
                self.assertEqual(regarder(a), regarder(b))

    def test_presence_projetee_contenance_possession_et_croyances(self):
        m, id, autre, c = reserve()
        source = c['objet']
        v = Vue(m, id)
        e = depart(m, id, v)
        self.assertTrue(v.present(e, source))
        # Aucune lecture du lieu réel d'un bien mobile non perçu.
        m.objets['cle_garde_manger']['lieu'] = 'dortoir'
        v = Vue(m, id)
        self.assertTrue(v.present(e, 'cle_garde_manger'))
        self.assertTrue(v.present(e.apres(portes=e.portes | {'cle_garde_manger'}), 'cle_garde_manger'))
        m.objets['vivres']['lieu'] = source
        from donjon.esprits import croire
        croire(m, id, 'vivres', 'lieu', source, 'vu')
        croire(m, id, source, 'etat', {'ouverte': False}, 'vu')
        v = Vue(m, id)
        self.assertFalse(v.present(e, 'vivres'))
        self.assertTrue(v.present(e.apres(faits=[(('ouvert', source), True)]), 'vivres'))

    def test_presence_verifiee_aussi_sans_cases(self):
        m, id, autre, c = capture()
        m.data['mode_cases'] = False
        self.assertIsNone(echanges._devis_proposition(m, id, c, autre))

    def test_promesse_tenable_acceptee_et_tenue_apres_recharge(self):
        m, id, autre, c, lignes = offrir(reserve)
        self.assertIn('accepte', ' '.join(lignes))
        self.assertFalse(echanges.empeche(m, id, agendas.en_cours(m, id)[0]))
        with patch.object(Monde, 'd20', return_value=20):
            moteur = Moteur(m)
            moteur.executer(moteur.preparer(proposition('attendre')))
        m = recharger(m)
        self.assertTrue(m.objets[c['objet']]['verrouillee'])
        self.assertTrue(any(s['type'] == 'engagement_tenu' for s in lire(m, id)['memoire']))
        self.assertFalse(agendas.en_cours(m, id, condition=c))
        self.assertEqual(regarder(m), regarder(recharger(m)))


if __name__ == '__main__':
    unittest.main()
