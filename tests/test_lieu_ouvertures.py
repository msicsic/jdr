"""Attache initiale des ouvertures, perception des deux côtés et recharge."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest

from donjon.monde import ErreurMonde, Monde, depuis_scenario
from donjon import spatial
from donjon.deliberation import _lieu_cru
from donjon.esprits import lire, percevoir_tous, percus
from donjon.pnj import _executer
from donjon.rendu import regarder as rendu
from tests.support import regarder

RACINE = Path(__file__).resolve().parents[1]


def scenario(nom):
    return depuis_scenario(RACINE / 'donjon' / f'scenario_{nom}.json', depart='fixe')


class LieuOuverturesTests(unittest.TestCase):
    def recharger(self, m):
        avant = rendu(m)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / 'partie.json'
            m.sauver(chemin)
            n = Monde.charger(chemin)
        self.assertEqual(n.data, m.data)
        self.assertEqual(rendu(n), avant)
        return n

    def test_tous_les_scenarios_et_savoirs_fixes(self):
        for chemin in (RACINE / 'donjon').glob('scenario_*.json'):
            with self.subTest(scenario=chemin.name):
                m = depuis_scenario(chemin, depart='fixe')
                for id, o in m.objets.items():
                    if 'relie' in o:
                        self.assertIn(o['lieu'], o['relie'])
                if chemin.stem in ('scenario_relais', 'scenario_crue', 'scenario_rixe', 'scenario_rixe_douce'):
                    for qui in m.data['esprits']:
                        self.assertEqual(_lieu_cru(m, qui, 'porte'), 'crypte')

    def test_refus_commun_independant_du_type_et_du_nom(self):
        for type_objet in ('porte', 'trappe', 'meuble'):
            d = scenario('relais').data
            o = d['objets'].pop('porte')
            o.update(id='ouverture_forgee', type=type_objet, lieu='antichambre')
            d['objets']['ouverture_forgee'] = o
            with tempfile.TemporaryDirectory() as dossier:
                p = Path(dossier) / 'scenario.json'
                p.write_text(json.dumps(d), encoding='utf8')
                with self.assertRaises(ErreurMonde) as erreur:
                    depuis_scenario(p)
            for texte in (str(erreur.exception), erreur.exception.attendu):
                for mot in ('ouverture_forgee.lieu', 'antichambre', 'crypte', 'beffroi'):
                    self.assertIn(mot, texte)

    def test_capture_reelle_et_relais_presence_et_geste_recharges(self):
        with gzip.open(RACINE / 'tests/data/promesse-crue11-210.json.gz', 'rt', encoding='utf8') as f:
            capture = json.load(f)
        # Rejouer la scène historique avec la donnée corrigée ; aucune migration
        # des croyances acquises pendant les 210 minutes précédentes.
        capture['objets']['porte']['lieu'] = 'crypte'
        for m, qui in ((Monde(capture), 'ilse'), (scenario('relais'), 'marchand')):
            with self.subTest(scene=m.data.get('crue') is not None):
                spatial.installer(m)
                self.assertFalse(m.present_physique('porte', salle='antichambre'))
                self.assertNotIn('porte', percus(m, qui)[0])
                m = self.recharger(m)
                # Même ouverture manipulée depuis chacun de ses deux côtés.
                for salle, case, acteur, joueur in (
                        ('crypte', (8, 3), [7, 3], [8, 2]),
                        ('beffroi', (0, 3), [1, 3], [0, 2])):
                    self.assertTrue(m.present_physique('porte', salle=salle))
                    self.assertEqual(spatial.position_cible(m, 'porte', salle), case)
                    m.objets[qui].update(lieu=salle, position=acteur, position_salle=salle)
                    m.joueur.update(salle=salle, position=joueur)
                    m.data['salles'][salle]['lumiere_naturelle'] = 2
                    regarder(m, qui, 'porte'); regarder(m, 'joueur', 'porte')
                    m.objets['porte'].update(ouverte=False, verrouillee=False)
                    # La capture contient une porte déjà brisée ; le parcours
                    # d'ouverture porte ici sur une porte intacte accessible.
                    m.objets['porte']['integrite'] = m.objets['porte']['maximum']
                    percevoir_tous(m)
                    self.assertIn('porte', percus(m, qui)[0])
                    lignes = []
                    self.assertTrue(_executer(m, qui, {
                        'operation': 'ouvrir', 'cible': 'porte', 'outil': '',
                        'lieu': salle, 'condition': ''}, lignes, []))
                    self.assertTrue(m.objets['porte']['ouverte'])
                    self.assertIn('ouvre', ' '.join(lignes))
                    percevoir_tous(m)
                    m = self.recharger(m)
                    self.assertTrue(lire(m, qui)['croyances']['porte']['etat']['valeur']['ouverte'])
                    self.assertIn('porte étanche', ' '.join(rendu(m).split()))


if __name__ == '__main__':
    unittest.main()
