"""Les nouveaux moyens passent par les échanges et la sauvegarde ordinaires."""
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon.echanges import garde, necessaire
from donjon.esprits import lire, percevoir_tous
from donjon.paroles import preparer_parole
from donjon.rendu import regarder, fiche
from tests.support import presentes, regarder as voir
from tests.test_tensions import recharger


class OccasionsScenariosTests(unittest.TestCase):
    def test_creation_et_recharge_des_variantes(self):
        for scenario in ('relais', 'mine', 'auberge', 'crue', 'crue_hameau', 'rixe', 'rixe_douce'):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, 'fixe')
                r = recharger(m)
                self.assertEqual(m.data, r.data)
                self.assertEqual(regarder(m), regarder(r))

    def test_galettes_negociables_sans_modifier_la_reserve_historique(self):
        cas = (('relais', 'marchand', 'galettes_route'),
               ('mine', 'mathe', 'galettes_cuisine'),
               ('auberge', 'odile', 'galettes_comptoir'))
        for scenario, owner, food in cas:
            with self.subTest(scenario=scenario):
                m = presentes(creer(scenario, 1985, 'fixe'))
                # Le joueur vient à l'interlocuteur ; aucun profil ou droit modifié.
                o = m.objets[owner]
                m.joueur.update(salle=o['lieu'], position=[o['position'][0] + 1, o['position'][1]])
                voir(m, 'joueur', owner)
                voir(m, owner, 'joueur')
                m.data['connus'].append(food)
                percevoir_tous(m)
                m = recharger(m)
                self.assertFalse(garde(m, owner, m.objets[food]))
                self.assertFalse(necessaire(m, owner, food))
                avant = m.objets['vivres']['portions']
                gardes = m.objets[owner]['profil']['pulsions'].copy()
                pieces = m.joueur['or']
                with patch.object(type(m), 'd20', return_value=20):
                    m, r = preparer_parole(m, {
                        'personnage': owner, 'replique': 'Deux pièces contre une galette.',
                        '_intention': 'Je dis à ' + o['aliases'][0] + ' : deux pièces contre une galette.',
                        'contenu': [{'type': 'proposition',
                                     'demande': {'type': 'part', 'objet': food},
                                     'contrepartie': {'type': 'pieces', 'montant': 2}}]})
                self.assertIn('accepte', ' '.join(r['faits']))
                self.assertEqual(m.objets[food]['portions'], 3)
                self.assertEqual(m.objets['vivres']['portions'], avant)
                self.assertEqual(m.objets[owner]['profil']['pulsions'], gardes)
                self.assertEqual(m.joueur['or'], pieces - 2)
                recus = [k for k, v in m.objets.items()
                         if v.get('lieu') == 'joueur' and v.get('type') == 'nourriture']
                self.assertTrue(recus)
                copie = recharger(m)
                self.assertEqual(m.data, copie.data)
                self.assertEqual(regarder(m), regarder(copie))
                self.assertEqual(fiche(m), fiche(copie))
                self.assertIn('galette', fiche(copie))
                self.assertTrue(any(s['type'] == 'parole' and 'galette' in s['texte']
                                    for s in lire(copie, owner)['memoire']))
