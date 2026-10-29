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

    def test_inverse_ne_retire_que_les_occasions_du_lot(self):
        """Les projets 184/192 de la base actuelle restent dans les scènes."""
        import hashlib
        import json
        from tests.scenarios_contractuels import donnees
        # Empreintes JSON avant construction de Monde : base 23aba63 ; pour
        # le hameau, plus le statut/trois ascendants 302 et l'agenda 306.
        # Ces données restent présentes après l'inverse des seules occasions.
        attendus = {
            'relais': '23ba952f562f9bf0de5a3cfebc976443644e02193c31b0c2130d7193c837cb0c',
            'mine': 'cb52faa7ba7241d4d145b1bd0f5148b777147b4798c91281cf9e5aae44b115c7',
            'auberge': '848ac337dd2990a94641c69f77f8ac9f27d033124c39033b88563b691327facb',
            'crue': '6ff6d9e7a1ac1ee934470bf20d7bbc9c648da5decdecb2dfcf58110c1ed63a89',
            'crue_hameau': '85955d0edd5cf76a223ef56ddde5103d65bde1eb75f367d599d3a70440c62f10',
            'rixe': '711c3f594711e036b0e60630489d58866708ca34da70913146bc15f0618efc9e',
            'rixe_douce': 'd3cd7ce5b7309bcdd203f9767e150d229b057da6007dcdc266cc3308b62feb92',
        }
        for nom, attendu in attendus.items():
            with self.subTest(scenario=nom):
                contenu = json.dumps(donnees(nom), sort_keys=True, ensure_ascii=False)
                self.assertEqual(hashlib.sha256(contenu.encode()).hexdigest(), attendu)

    def test_moyens_propres_liens_et_observations_persistent(self):
        for scenario, bois, porteur, intermediaire, protege in (
                ('relais', 'bois_bateliere', 'brune', 'marchand', 'aubin'),
                ('mine', 'chutes_serrurier', 'odon', 'mathe', 'josse'),
                ('auberge', 'copeaux_palefrenier', 'joss', 'odile', 'mireille'),
                ('crue', 'bois_bateliere', 'brune', 'marchand', 'aubin')):
            with self.subTest(scenario=scenario):
                m = recharger(creer(scenario, 1985, 'fixe'))
                objet = m.objets[bois]
                self.assertEqual((objet['lieu'], objet['proprietaire'], objet['charges']),
                                 (porteur, porteur, 2))
                from donjon.esprits import lire
                from donjon.relations import envers
                self.assertEqual(envers(m, intermediaire, protege)['affection'], 60)
                self.assertEqual(lire(m, porteur)['croyances'][intermediaire]
                                 ['attitude:'+protege]['valeur'], 'attachement')
                if scenario == 'crue':
                    self.assertEqual(m.objets['ilse']['lieu'], 'chambre_cloche')
                    self.assertEqual(m.objets['aubin']['lieu'], 'crypte')
