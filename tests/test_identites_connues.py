"""Un nom public ne révèle pas les homonymes cachés du monde privé."""
import copy
import json
import unittest

from donjon.atelier import nouveau_atelier
from donjon.defi import nouveau_defi
from donjon.dialogues import information_publique
from donjon.monde import Monde
from donjon.paroles import resoudre
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.spatial import installer
from tests.test_inventaire_public import etat
from tests.test_tensions import recharger


class IdentitesConnuesTests(unittest.TestCase):
    def test_homonymes_caches_non_proposes_ni_resolus_apres_recharge(self):
        for creer in (nouveau_defi, nouveau_atelier):
            with self.subTest(scene=creer.__name__):
                m = creer()
                installer(m)
                modele = nouveau_defi()
                coffre = copy.deepcopy(modele.objets['coffre'])
                coffre.update(id='contenant_ferme', lieu='joueur', ouverte=False, masse=1)
                m.objets[coffre['id']] = coffre
                outil = copy.deepcopy(modele.objets['couteau'])
                outil.update(id='outil_connu', lieu='joueur', nom='outil témoin', aliases=['instrument témoin'])
                m.objets[outil['id']] = outil
                secret = {**copy.deepcopy(outil), 'id': 'homonyme_cache', 'lieu': coffre['id']}
                m.objets[secret['id']] = secret
                m = recharger(Monde(copy.deepcopy(m.data)))
                avant = copy.deepcopy(m.data)
                self.assertEqual(resoudre(m, 'outil_connu'), 'outil_connu')
                self.assertIsNone(resoudre(m, 'homonyme_cache'))
                self.assertEqual(resoudre(m, outil['nom']), 'outil_connu')
                self.assertNotIn('homonyme_cache', json.dumps(etat(m)))
                public = information_publique(m)
                self.assertIn('outil_connu', {s['id'] for s in public['sujets']})
                self.assertNotIn('homonyme_cache', json.dumps(public))
                n = recharger(m)
                self.assertEqual(m.data, avant)
                self.assertEqual(n.data, m.data)
                self.assertEqual(etat(n), etat(m))
                self.assertEqual(regarder(n), regarder(m))
                self.assertEqual(scene_percue(n), scene_percue(m))
                self.assertIsNone(resoudre(n, 'homonyme_cache'))
                # Un souvenir explicite autorise à le nommer sans prétendre
                # qu'il est accessible ni révéler une position actuelle.
                n.data['connus'].append('homonyme_cache')
                self.assertEqual(resoudre(n, 'homonyme_cache'), 'homonyme_cache')
                self.assertFalse(n.accessible('homonyme_cache'))
