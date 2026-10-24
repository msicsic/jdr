"""La transaction partage ses lectures ; état et affichage survivent à la recharge."""
from contextlib import contextmanager
from copy import deepcopy
import unittest
from unittest.mock import patch

from donjon import spatial
from donjon.banc_pnj import creer
from donjon.carte import carte
from donjon.moteur import Moteur, proposition
from donjon.noms import texte
from donjon.operations import etape, sequence
from donjon.rendu import regarder
from tests.test_tensions import recharger


@contextmanager
def sans_vue(m):
    with spatial.sans_memoire(m):
        yield


class VueActionTests(unittest.TestCase):
    def test_actions_et_sequence_identiques_au_calcul_pur_apres_recharge(self):
        for scenario in ("mine", "relais"):
            for action in (proposition("attendre"), proposition("attendre", "1"),
                           sequence(etape("patienter"))):
                with self.subTest(scenario=scenario, action=action):
                    origine = creer(scenario, 42)
                    resultats = []
                    for pur in (True, False):
                        m = recharger(origine)
                        contexte = patch.object(spatial, "vue_memorisee", sans_vue) if pur else patch.object(spatial, "VERIFICATION", 1)
                        with contexte:
                            moteur = Moteur(m)
                            rendu = moteur.executer(moteur.preparer(deepcopy(action)))
                        self.assertNotIn("_cache_vue", m.__dict__)
                        m = recharger(m)
                        self.assertNotIn("_cache_vue", m.__dict__)
                        resultats.append((m.data, rendu, regarder(m), carte(m),
                                          texte(m, "Gorm Rémy Aubin Brune")))
                    self.assertEqual(resultats[0], resultats[1])

    def test_exception_ne_garde_ni_transaction_ni_cache(self):
        m = creer("mine", 42)
        avant = deepcopy(m.data)
        copies = []
        def interrompre(moteur, plan, travail):
            copies.append(travail)
            self.assertIn("_cache_vue", travail.__dict__)
            raise RuntimeError("arrêt de transaction")
        with patch.object(Moteur, "_executer_simple", interrompre):
            moteur = Moteur(m)
            with self.assertRaisesRegex(RuntimeError, "arrêt de transaction"):
                moteur.executer(moteur.preparer(proposition("attendre")))
        self.assertEqual(m.data, avant)
        self.assertNotIn("_cache_vue", copies[0].__dict__)

