"""Contrôles courts de la règle et de son isolation, sans modèle."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import mesure_saillance_210 as s


class RegleTests(unittest.TestCase):
    def vue(self):
        self.esprit = dict(croyances={
            'ancien': {'lieu': dict(source='vu', minute=0)},
            'recent': {'lieu': dict(source='entendu', minute=80)},
            'hors_monde': {'lieu': dict(source='vu', minute=100)}},
            memoire=[dict(type='enquete', besoin='chaleur', objets=['lie'])])
        self.etat = SimpleNamespace(salle='ici', portes={'porte'})
        objets = {o: {} for o in ('ancien', 'recent', 'local', 'lie', 'porte', 'cle')}
        objets['cle']['ouvre'] = 'coffre'
        return SimpleNamespace(monde=SimpleNamespace(data={'minutes': 100}), id='acteur',
                               motif='chaleur', connus=list(objets), objets=objets,
                               salle=lambda e, o: 'ici' if o == 'local' else 'ailleurs')

    def test_regle_connus_recence_local_portage_et_lien(self):
        v = self.vue()
        with patch.object(s, 'lire', return_value=self.esprit), patch.object(s.p, 'depart', return_value=self.etat):
            self.assertEqual(s.esprit_saillant(v, {'ouvrir': ['coffre']}),
                             {'recent', 'local', 'lie', 'porte', 'cle'})

    def test_expiration_et_aucune_ecriture(self):
        v = self.vue()
        avant = copy.deepcopy(self.esprit)
        with patch.object(s, 'lire', return_value=self.esprit), patch.object(s.p, 'depart', return_value=self.etat):
            self.assertIn('recent', s.esprit_saillant(v, {}))
            v.monde.data['minutes'] = 111
            del v._saillance_210  # Nouvelle photographie de recherche.
            self.assertNotIn('recent', s.esprit_saillant(v, {}))
        self.assertEqual(self.esprit, avant)

    def test_presence_sans_utilite_ne_suffit_pas(self):
        v = self.vue()
        v.besoin = dict.fromkeys(v.connus, False)
        v.pertinent = lambda o, vises: o != 'local'
        with patch.object(s, 'AGISSABLES', return_value=(v.connus, set(v.connus))), \
             patch.object(s, 'lire', return_value=self.esprit), patch.object(s.p, 'depart', return_value=self.etat), \
             s.variante('saillant'):
            objets, _ = s.agissables(v, {})
            self.assertNotIn('local', objets)
            self.assertNotIn('ancien', objets)
            self.assertIn('lie', objets)

    def test_desactive_par_defaut_et_restauration_exception(self):
        self.assertEqual(s.MODE, 'complete')
        with self.assertRaises(RuntimeError):
            with s.variante('saillant'):
                raise RuntimeError()
        self.assertEqual(s.MODE, 'complete')

    def test_temoin_conserve_exactement_les_entrees_du_moteur(self):
        original = ('communes', 'candidat')
        with patch.object(s, 'ENTREES', return_value=original):
            self.assertIs(s.entrees(None, None, 8, 4000), original)

    def test_cle_change_quand_le_moyen_sort_de_la_recence(self):
        v = self.vue()
        with patch.object(s, 'ENTREES', return_value=('stable',)), \
             patch.object(s, 'lire', return_value=self.esprit), patch.object(s.p, 'depart', return_value=self.etat), \
             s.variante('saillant'):
            avant = s.entrees(v, {}, 8, 4000)
            v.monde.data['minutes'] = 111
            del v._saillance_210
            self.assertNotEqual(avant, s.entrees(v, {}, 8, 4000))


if __name__ == '__main__':
    s.ceder()
    unittest.main()
