"""G4 : défenses perçues dans le fil de l'action, état et rendu sauvegardés."""
import unittest
from itertools import cycle
from unittest.mock import patch

from donjon import combat, corps
from donjon.esprits import lire, percevoir_tous
from donjon.francais import sujet
from donjon.monde import Monde
from donjon.moteur import proposition
from donjon.pnj import _etape
from tests import test_recit_resultat as contrat
from tests.test_tenir import situation
from tests.test_tensions import placer


def scene(operation, vue='vue', cible='brune'):
    m = situation(cible)
    m.objets[cible]['orientation'] = 'ouest'
    percevoir_tous(m)
    if operation == 'se_rendre':
        # Le danger est réellement subi et perçu avant la scène du test.
        with patch.object(Monde, 'd20', side_effect=[20, 1]):
            combat.frapper(m, 'joueur', cible)
    elif operation == 'degager':
        # Le joueur peut poser son objet sans lâcher lui-même cette prise.
        placer(m, 'ilse', m.joueur['salle'], (2, 4))
        corps.corps(m, cible)['tenu_par'] = 'ilse'
    # Une défense commandée, sans autres décisions autonomes pendant la scène.
    for id, o in m.objets.items():
        if o['type'] != 'personnage':
            continue
        o.pop('profil', None)
        e = lire(m, id)
        e.update(intention=None, pulsions=[], eveil=None, veille=None)
        e['besoins'] = {b: v for b, v in e['besoins'].items() if b in ('faim', 'repos', 'chaleur')}
    if vue == 'dos':
        m.joueur['orientation'] = 'ouest'
    elif vue == 'noir':
        for o in m.objets.values():
            if 'allume' in o:
                o['allume'] = False
        for salle in m.data['salles'].values():
            salle['lumiere_naturelle'] = 0
    percevoir_tous(m)
    e = lire(m, cible)
    but = {'type': 'degager'} if operation == 'degager' else {'type': 'reddition' if operation == 'se_rendre' else 'fuir', 'qui': 'joueur'}
    e.update(libre=0, eveil=None, intention={'but': but, 'motif': 'securite', 'depuis': m.data['minutes'],
             'attente': 0, 'plan': [_etape(operation, 'joueur' if operation != 'degager' else '')]})
    return m


class DefensesPubliquesTests(unittest.TestCase):
    def test_defenses_pendant_action_vue_dos_et_noir(self):
        for operation, fin in (('degager', ' se dégage.'), ('se_rendre', ' se rend.'), ('fuite', ' a fui.')):
            for vue in ('vue', 'dos', 'noir'):
                with self.subTest(operation=operation, vue=vue):
                    m = scene(operation, vue)
                    self.assertEqual(m.visible('brune'), vue == 'vue')
                    phrase = sujet(m.objets['brune']) + fin
                    m, resultat, _ = contrat.RecitResultatTests().console(m, proposition('poser', 'cire'),
                        'Puis-je poser la cire ?', jet=cycle([20, 1]).__next__)
                    if vue == 'vue':
                        self.assertIn(phrase, resultat)
                        self.assertLess(resultat.index('au sol'), resultat.index(phrase))
                    else:
                        self.assertNotIn(phrase, resultat)
                    if operation == 'degager':
                        self.assertNotIn('tenu_par', corps.corps(m, 'brune'))
                    elif operation == 'se_rendre':
                        self.assertEqual(corps.corps(m, 'brune')['reddition']['a'], 'joueur')
                    else:
                        self.assertTrue(any(e['type'] == 'fuite' and e['id'] == 'brune'
                                            for e in m.data['historique_corps']))


if __name__ == '__main__':
    unittest.main()
