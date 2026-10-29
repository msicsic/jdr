"""Fourniture publiée, identité du but, sommeil et reprise sur moyen nouveau."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, echanges, poursuites
from donjon.esprits import lire, memoriser, constater
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_empathie import scene_repas, executer
from tests.test_tensions import recharger


def capture(nom):
    return Monde(json.loads(gzip.decompress((Path(__file__).parent/'data'/f'{nom}.json.gz').read_bytes())))


class PoursuiteFournituresTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        return n

    def test_capture_373_sert_la_part_recue_sans_naitre_ni_perdre_le_palier(self):
        m = self.recharge(capture('fourniture-273-mine-1985-373'))
        avant = copy.deepcopy(lire(m, 'josse')['intention'])
        contrat = agendas.contrat_intention(m, 'josse')
        self.assertIn('biscuits', lire(m, 'josse')['fournitures']['biscuits_1'])
        # La provenance doit survivre à l'éviction du reçu et à la recharge.
        lire(m, 'josse')['memoire'].clear()
        m = self.recharge(m)
        d.choisir(m, 'josse', m.data['minutes'])
        i, c = lire(m, 'josse')['intention'], agendas.contrat_intention(m, 'josse')
        self.assertEqual(i['but'], avant['but'])
        self.assertEqual(i['depuis'], avant['depuis'])
        self.assertEqual(c['palier'], contrat['palier'])
        self.assertEqual(c['demande'], contrat['demande'])
        self.assertEqual(c['phase'], 'continuer')
        self.assertEqual(i['plan'][0]['operation'], 'servir')
        self.assertEqual(i['plan'][0]['cible'], 'biscuits_1')
        n = self.recharge(m)
        faim = lire(m, 'odon')['besoins']['faim']
        executer(m, 2)
        for _ in range(2):
            executer(n, 1)
            n = self.recharge(n)
        self.assertEqual(m.data, n.data)
        self.assertLess(lire(m, 'odon')['besoins']['faim'], faim)
        self.assertTrue(any(c['pnj'] == 'josse' and 'donne une part' in c['texte'] for c in m.data['chronique']))
        self.recharge(m)

    def test_autre_pnj_provenances_en_chaine_et_mission_precise(self):
        m, auteur, autre = scene_repas()
        d.choisir(m, auteur, 0)
        avant = copy.deepcopy(lire(m, auteur)['intention'])
        demande = agendas.contrat_intention(m, auteur)['demande']
        part = echanges.detacher_part(m, 'vivres')
        memoriser(m, auteur, {'type': 'recu', 'de': auteur, 'objet': part, 'lot': 'vivres', 'livraison': True})
        suivante = echanges.detacher_part(m, part)
        memoriser(m, auteur, {'type': 'recu', 'de': auteur, 'objet': suivante, 'lot': part, 'livraison': True})
        constater(m, auteur, part, 'essai')
        self.assertIn('vivres', lire(m, auteur)['fournitures'][suivante])
        # Même raison sociale, mais la localisation d'un bien précis n'est
        # pas une fourniture : aucune substitution par sa part ni un autre bien.
        precise = {'condition': {'objet': 'vivres', 'lieu': 'galerie'}, 'raison': demande['raison']}
        self.assertEqual(list(poursuites.conditions(m, auteur, precise)), [precise['condition']])
        from types import SimpleNamespace
        self.assertFalse(d._meme_demande_adoptee(
            SimpleNamespace(demande=precise), avant, (avant['but'], []), {'demande': demande}))
        lire(m, auteur)['memoire'].clear()
        m = self.recharge(m)
        d.choisir(m, auteur, 0)
        self.assertEqual(lire(m, auteur)['intention']['but'], avant['but'])
        self.assertEqual(lire(m, auteur)['intention']['plan'][0]['cible'], suivante)
        n = self.recharge(m)
        executer(m, 2)
        for _ in range(2):
            executer(n, 1)
            n = self.recharge(n)
        self.assertEqual(m.data, n.data)
        self.assertLess(lire(m, autre)['besoins']['faim'], 70)
        self.recharge(m)

    def test_sommeil_libere_le_palier_reveil_sans_delai_sur_moyen_nouveau(self):
        m = self.recharge(capture('sommeil-273-anselme-120'))
        ancien = copy.deepcopy(lire(m, 'anselme')['intention'])
        d.choisir(m, 'anselme', m.data['minutes'])
        e = lire(m, 'anselme')
        self.assertNotEqual(e['intention']['but'], ancien['but'])
        self.assertEqual(e['intention']['motif'], 'securite')
        retenue = next(iter(e['demandes_suspendues'].values()))
        self.assertEqual(retenue['but'], ancien['but'])
        self.assertEqual(retenue['depuis'], ancien['depuis'])
        m = self.recharge(m)
        # Seul le temps change ; aucune replanification de la demande endormie.
        m.data['minutes'] += 60
        original, essais = d._reprendre_demande, []
        def suivre(monde, id, demande):
            if demande == retenue['demande']:
                essais.append(demande)
            return original(monde, id, demande)
        with patch.object(d, '_reprendre_demande', suivre):
            d.choisir(m, 'anselme', m.data['minutes'])
        self.assertEqual(essais, [])
        self.assertEqual(lire(m, 'anselme')['demandes_suspendues'], e['demandes_suspendues'])
        # Moyen réellement acquis et connu : le besoin corporel concurrent
        # est calmé pour laisser constater la continuation du même but.
        m.objets['bois_anselme'].update(lieu='anselme', charges=3)
        constater(m, 'anselme', 'bois_anselme', 'essai')
        # Le combustible seul ne rallume pas un foyer froid : recevoir aussi
        # une flamme fournit enfin les deux moyens manquants au plan réel.
        m.objets['bougeoir_mireille']['lieu'] = 'anselme'
        constater(m, 'anselme', 'bougeoir_mireille', 'essai')
        lire(m, 'anselme')['besoins']['securite'] = 0.
        lire(m, 'anselme')['intention'] = None
        d.choisir(m, 'anselme', m.data['minutes'])
        c = agendas.contrat_intention(m, 'anselme')
        self.assertEqual(c['demande'], retenue['demande'])
        self.assertEqual(c['palier'], retenue['palier'])
        self.assertEqual(c['phase'], 'continuer')
        self.assertEqual(lire(m, 'anselme')['intention']['depuis'], retenue['depuis'])
        n = self.recharge(m)
        executer(m, 3)
        for _ in range(3):
            executer(n, 1)
            n = self.recharge(n)
        self.assertEqual(m.data, n.data)
        self.assertTrue(m.objets['poele']['allume'])
        self.recharge(m)


if __name__ == '__main__':
    unittest.main()
