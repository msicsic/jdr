"""Un résultat tenu n'est pas l'absence de moyens pour une ancienne demande."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as d
from donjon.esprits import lire, percevoir_tous
from donjon.monde import Monde
from donjon.pnj_propositions import plan_recours
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_contre_offre import refus
from tests.test_proposer_recours import scene
from tests.test_tensions import recharger, vivre


def historique():
    chemin = Path(__file__).parent / 'fixtures/auberge7-garde-435-4306c14.json.gz'
    return recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))


class NavettesGardeTests(unittest.TestCase):
    def verifier_laps(self, capture, id, salle, minutes):
        bloc, _ = vivre(recharger(capture), minutes)
        decoupe = recharger(capture)
        for _ in range(minutes):
            decoupe, _ = vivre(decoupe, 1)
        self.assertEqual(bloc.data, decoupe.data)
        recharge = recharger(bloc)
        self.assertEqual(bloc.data, recharge.data)
        self.assertEqual(regarder(bloc), regarder(recharge))
        self.assertEqual(scene_percue(bloc), scene_percue(recharge))
        self.assertEqual(recharge.objets[id]['lieu'], salle)
        return recharge

    def test_capture_historique_rechargee_ne_repart_pas_acheter(self):
        m = historique()
        self.assertEqual(lire(m, 'anselme')['demande_refusee']['objet'], 'burette_huile')
        m = self.verifier_laps(m, 'anselme', 'chambre_chaude', 6)
        passages = [x for x in m.data['chronique'] if x['pnj'] == 'anselme'
                    and x['minute'] >= 435 and x.get('nature') == 'deplacement']
        # Le suffixe de retour déjà engagé s'achève ; aucun nouveau départ.
        self.assertLessEqual(len(passages), 3)
        self.assertEqual(lire(m, 'anselme')['intention']['but'],
                         {'type': 'garder', 'lieu': 'chambre_chaude'})
        self.assertFalse(lire(m, 'anselme')['intention']['plan'])
        m.joueur.update(salle='chambre_chaude', position=[2, 2])
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_autre_gardienne_meme_besoin_contre_offre_sans_greffe(self):
        m = scene(70)
        e = lire(m, 'brune')
        e['intention']['motif'] = 'biens'
        m, _ = refus(m, 'vivres')
        p = m.objets['brune']['profil']
        p['besoins']['biens'] = {'depart': 95, 'derive_heure': 0, 'urgence': 60}
        m.objets['crochets'].update(lieu='antichambre', position=[7, 3], position_salle='antichambre')
        p['pulsions'] = [{'besoin': 'biens', 'condition': {'objet': 'crochets', 'lieu': 'antichambre'}}]
        e = lire(m, 'brune')
        e['besoins'].update(biens=95, faim=0)
        e['pulsions'] = []
        percevoir_tous(m)
        d.choisir(m, 'brune', m.data['minutes'])
        self.assertEqual(e['intention']['but'], {'type': 'garder', 'lieu': 'antichambre'})
        self.assertEqual(e['intention']['plan'], [])
        avant = copy.deepcopy(m.data['finances_pnj'])
        m = self.verifier_laps(recharger(m), 'brune', 'antichambre', 3)
        self.assertEqual(m.data['finances_pnj']['brune'], avant['brune'])
        self.assertEqual(lire(m, 'brune')['demande_refusee']['objet'], 'vivres')

    def test_contre_offre_utilisee_quand_le_but_n_a_pas_de_solution_ordinaire(self):
        # Une autre gardienne, une autre demande : la clé est toujours un
        # moyen de fermer sa réserve ; le marché reste exécutable après recharge.
        m = scene(70)
        m, _ = refus(m, 'cle_reserve')
        self.assertIsNone(plan_recours(recharger(m), 'brune', 'faim', []))
        plan = plan_recours(recharger(m), 'brune', 'faim', None)
        self.assertEqual(plan[-1]['operation'], 'acheter')
        from donjon.echanges import executer
        with patch('donjon.echanges.jet_persuasion', side_effect=AssertionError('second jet')):
            self.assertTrue(executer(m, 'brune', plan[-1], []))
        m = recharger(m)
        self.assertEqual(m.objets['cle_reserve']['lieu'], 'brune')
        self.assertEqual(regarder(m), regarder(recharger(m)))


if __name__ == '__main__':
    unittest.main()
