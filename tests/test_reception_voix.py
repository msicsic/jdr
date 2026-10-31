"""Une voix entendue est admise avant son rendu, y compris en plein laps PNJ."""
import copy
import unittest
from unittest.mock import patch

from donjon import ecoute
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import MINUTE
from tests.test_messages_decoupage import vivre
from tests.test_tensions import recharger
from tests.test_voix import aubin_cherche_gorm, hugues_cherche_anselme


class ReceptionVoixTests(unittest.TestCase):
    def test_appels_relais_et_auberge_admis_avant_affichage_et_recharges(self):
        for fabrique, qui, nom, designation in (
                (aubin_cherche_gorm, 'aubin', 'Aubin', 'une voix inconnue'),
                (hugues_cherche_anselme, 'hugues', 'Hugues', 'une personne inconnue')):
            with self.subTest(scenario=fabrique.__name__):
                depart = fabrique()
                if qui == 'hugues':
                    depart.joueur.update(salle='couloir', position=[1, 2])
                # Le joueur ne connaît ni le nom ni la voix de l'appelant.
                self.assertNotIn(qui, depart.data.get('voix_connues', []))
                recus = []
                original = ecoute.rendre_evenement

                def observer(m, parvenu, precedent=None):
                    b, niveau, _ = parvenu
                    premiere = not recus and b['auteur'] == qui and ecoute.nette(b, niveau)
                    if b['auteur'] == qui and ecoute.nette(b, niveau):
                        if qui not in m.data.get('voix_connues', []):
                            voix = m.data['voix_entendues'][qui]
                            self.assertEqual(voix['minute'], b['instant'] // MINUTE)
                        recus.append(b['texte'])
                    lignes = original(m, parvenu, precedent)
                    if premiere:
                        self.assertFalse(any(nom in l for l in lignes), lignes)
                        # Hugues peut être aperçu au couloir sans que Corvus
                        # connaisse son nom ; Aubin reste hors de sa vue.
                        self.assertTrue(any(designation in l for l in lignes), lignes)
                    return lignes

                with patch.object(ecoute, 'rendre_evenement', observer):
                    bloc, lignes = vivre(depart.copier(), [1800])
                self.assertTrue(recus)
                morceaux, decoupe = vivre(depart.copier(), [600, 600, 600])
                self.assertEqual(bloc.data, morceaux.data)
                self.assertEqual(lignes, decoupe)
                avant = copy.deepcopy(bloc.data)
                recharge = recharger(bloc)
                self.assertEqual(recharge.data, avant)
                self.assertEqual((regarder(recharge), scene_percue(recharge)),
                                 (regarder(bloc), scene_percue(bloc)))
                self.assertIn(qui, recharge.data['voix_entendues'])


if __name__ == '__main__':
    unittest.main()
