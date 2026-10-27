"""Les occasions restantes préservent la rareté et les sauvegardes."""
import unittest

from donjon.banc_pnj import creer
from donjon.ecoute import ENTENDU, entendus, rendre
from donjon.geometrie import position_entree
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder, fiche
from tests.test_tensions import recharger

SCENARIOS = ('relais', 'mine', 'auberge', 'crue', 'crue_hameau', 'rixe', 'rixe_douce')


# État alimentaire déclaré de 12a936d, indépendant des fabriques courantes.
NOURRITURES_AVANT_186 = {'relais': {'vivres': {'lieu': 'reserve', 'proprietaire': 'marchand', 'portions': 4}},
 'mine': {'biscuits': {'lieu': 'coffre_paie', 'proprietaire': 'bram', 'portions': 2},
          'pain_lucien': {'lieu': 'baraquement', 'proprietaire': 'lucien', 'portions': 1},
          'vivres': {'lieu': 'garde_manger', 'proprietaire': 'mathe', 'portions': 4}},
 'auberge': {'marmite': {'lieu': 'cuisine', 'proprietaire': 'mireille', 'portions': 3},
             'vivres': {'lieu': 'garde_manger', 'proprietaire': 'odile', 'portions': 4},
             'provisions_anselme': {'lieu': 'besace_anselme',
                                    'proprietaire': 'anselme',
                                    'portions': 2},
             'rations_hugues': {'lieu': 'hugues', 'proprietaire': 'hugues', 'portions': 1}},
 'crue': {'vivres': {'lieu': 'reserve', 'proprietaire': 'marchand', 'portions': 4}},
 'crue_hameau': {'vivres': {'lieu': 'reserve', 'proprietaire': 'marchand', 'portions': 7}},
 'rixe': {'vivres': {'lieu': 'reserve', 'proprietaire': 'marchand', 'portions': 4}},
 'rixe_douce': {'vivres': {'lieu': 'reserve', 'proprietaire': 'marchand', 'portions': 4}}}


class OccasionsScenariosTests(unittest.TestCase):
    def test_creation_et_recharge_des_variantes(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, 'fixe')
                salle = {'mine': 'galerie', 'auberge': 'dortoir'}.get(scenario, 'chambre_cloche')
                m.joueur.update(salle=salle, position=list(position_entree(m, salle)))
                moteur = Moteur(m)
                moteur.executer(moteur.preparer(proposition('attendre')))
                r = recharger(m)
                self.assertEqual(m.data, r.data)
                self.assertEqual(regarder(m), regarder(r))
                self.assertEqual(fiche(m), fiche(r))
                self.assertEqual(rendre(m, entendus(m, -1, ENTENDU)),
                                 rendre(r, entendus(r, -1, ENTENDU)))

    def test_rarete_alimentaire_conservee(self):
        def nourritures(m):
            return {k: {p: o.get(p) for p in ('lieu', 'proprietaire', 'portions')}
                    for k, o in m.objets.items() if o['type'] == 'nourriture'}
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, 'fixe')
                attendu = NOURRITURES_AVANT_186[scenario]
                self.assertEqual(nourritures(m), attendu)
                self.assertEqual(nourritures(recharger(m)), attendu)
