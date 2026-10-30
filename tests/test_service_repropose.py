"""Présences d'un geste : admission, reprise, exécution et recharge."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation, planification, pnj
from donjon.esprits import croire, lire
from donjon.geometrie import position_entree
from donjon.monde import Monde
from donjon.rendu import regarder
from tests.test_empathie import scene
from tests.test_tensions import placer, recharger, vivre


def capture():
    chemin = Path(__file__).parent / 'captures/service-251-auberge-235.json.gz'
    return Monde(json.loads(gzip.decompress(chemin.read_bytes())))


class ServiceReproposeTests(unittest.TestCase):
    def verifier_absence(self, m, auteur, pour, repas):
        etape = planification._etape('servir', repas, contenu={'pour': pour})
        self.assertNotEqual(m.objets[auteur]['lieu'], m.objets[pour]['lieu'])
        self.assertEqual(lire(m, auteur)['croyances'][pour]['lieu']['valeur'], m.objets[pour]['lieu'])
        self.assertFalse(pnj._executer(m, auteur, etape, [], []))
        for _ in range(3):
            m = recharger(m)
            v = planification.Vue(m, auteur)
            e = planification.depart(m, auteur, v)
            self.assertIsNone(planification._mesurer_direct(v, e, [etape], e, 1))
            self.assertIsNotNone(pnj.refus_etape(m, auteur, [etape]))
            deliberation.choisir(m, auteur, m.data['minutes'])
            intention = lire(m, auteur)['intention']
            self.assertFalse(intention and intention['plan'] == [etape])
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))
        # Une croyance neuve de retour libère le même geste, sans délai.
        placer(m, pour, m.objets[auteur]['lieu'], [4, 3])
        croire(m, auteur, pour, 'lieu', m.objets[auteur]['lieu'], 'vu',
               salle=m.objets[auteur]['lieu'], case=[4, 3])
        self.assertIsNone(pnj.refus_etape(recharger(m), auteur, [etape]))

    def test_capture_235_mireille_mathurine(self):
        self.verifier_absence(capture(), 'mireille', 'mathurine', 'marmite')

    def test_mine_autre_repas_et_beneficiaire(self):
        m, auteur, pour = scene()
        case = list(position_entree(m, 'galerie'))
        placer(m, pour, 'galerie', case)
        croire(m, auteur, pour, 'lieu', 'galerie', 'vu', salle='galerie', case=case)
        self.verifier_laps(m)
        self.verifier_absence(m, auteur, pour, 'vivres')

    def test_capture_laps_decoupes_et_aucune_execution_invalide(self):
        self.verifier_laps(capture())

    def verifier_laps(self, depart):
        rejets = []
        propositions_invalides = []
        executer = pnj._executer
        choisir = deliberation.choisir
        def choix(m, auteur, *args, **kwargs):
            resultat = choisir(m, auteur, *args, **kwargs)
            i = lire(m, auteur)['intention']
            if i and i['plan'] and i['plan'][0]['operation'] == 'servir':
                if pnj.refus_etape(m, auteur, i['plan']) is not None:
                    propositions_invalides.append((auteur, i['plan']))
            return resultat
        def observer(m, auteur, etape, *args, **kwargs):
            resultat = executer(m, auteur, etape, *args, **kwargs)
            if etape['operation'] == 'servir' and resultat is False:
                rejets.append((auteur, etape))
            return resultat
        with patch.object(pnj, '_executer', observer), patch.object(deliberation, 'choisir', choix):
            bloc, _ = vivre(recharger(depart), 4)
            morceaux = recharger(depart)
            for _ in range(4):
                morceaux, _ = vivre(morceaux, 1)
        self.assertEqual(rejets, [])
        self.assertEqual(propositions_invalides, [])
        self.assertEqual(bloc.data, morceaux.data)
        self.assertEqual(regarder(bloc), regarder(morceaux))
        self.assertEqual(regarder(bloc), regarder(recharger(bloc)))
        from donjon.scene import scene_percue
        self.assertEqual(scene_percue(bloc), scene_percue(recharger(bloc)))

    def test_beneficiaire_present_sans_exiger_le_contact(self):
        m, auteur, pour = scene()
        etape = planification._etape('servir', 'vivres', contenu={'pour': pour})
        self.assertNotIn(pour, pnj._a_toucher(m, auteur, etape))
        self.assertIn(pour, pnj._a_reunir(m, auteur, etape))
        self.assertIsNone(pnj.refus_etape(m, auteur, [etape]))
        self.assertTrue(pnj._executer(m, auteur, etape, [], []))


if __name__ == '__main__':
    unittest.main()
