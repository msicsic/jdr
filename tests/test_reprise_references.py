"""A5 : conserver l'identité d'une cible à travers ses représentations."""
import copy
import unittest

from donjon.banc_pnj import creer
from donjon.comprehension import invariants_reprise, verifier_reprise
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.francais import designer
from donjon.noms import public, reference, verifier_references
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.voix import connait_nom
from tests.support import calme
from tests.test_audits_attendu import jouer
from tests.test_noms import relais, recharge
from tests.test_relances_luna import action
from tests.test_tensions import placer


class RepriseReferencesTests(unittest.TestCase):
    def test_references_publiques_corrigees_console_et_recharge(self):
        autre = creer('auberge', 1985, 'fixe')
        calme(autre, *[i for i, o in autre.objets.items() if o.get('profil')])
        autre.joueur.update(salle='cuisine', position=[1, 2], orientation='nord')
        placer(autre, 'joss', 'cuisine', [1, 1])
        for m, cible, proprietaire, nom in ((relais(), 'mains_gorm', 'marchand', 'Gorm'),
                                          (recharge(autre), 'joss', 'joss', 'Joss')):
            with self.subTest(cible=cible):
                alias = reference(m, cible)
                self.assertNotEqual(alias, cible)
                self.assertTrue(m.visible(cible))
                avant = copy.deepcopy(m.data)
                attendu = copy.deepcopy(m)
                moteur = Moteur(attendu)
                texte = moteur.executer(moteur.preparer(proposition('examiner', cible)))
                charge, sortie, appels = jouer(m, 'mj je regarde ' + designer(public(m, m.objets[cible])),
                    [action(proposition('examiner', cible)), action(proposition('examiner', alias))], [])
                self.assertEqual([f for f, _ in appels], ['repondre_au_joueur'] * 2)
                self.assertIn('proposition.cible', str(appels[1][1]['controle_narratif']))
                self.assertNotIn(nom, sortie)
                self.assertIn(texte, sortie)
                self.assertFalse(connait_nom(charge, 'joueur', proprietaire))
                self.assertEqual(charge.objets, attendu.objets)
                self.assertEqual(m.data, avant)
                self.assertIn(texte, charge.data['conversation'][-1]['reponse'])
                self.assertEqual(charge.data['journal'][-1]['action']['cible'], cible)
                self.assertEqual(charge.data['journal'][-1]['action']['action'], 'examiner')
                n = recharge(charge)
                self.assertEqual(n.data, charge.data)
                self.assertEqual((regarder(n), scene_percue(n)), (regarder(charge), scene_percue(charge)))

    def test_identites_et_listes_conservent_ordre_et_autres_parametres(self):
        m = relais()
        from donjon.noms import CHAMPS_REFERENCES, LISTES_REFERENCES
        for champ in ('cible', 'outil', 'destination', 'cibles'):
            with self.subTest(champ=champ):
                def valeur(id_):
                    return [id_, 'joueur'] if champ in LISTES_REFERENCES else id_
                p = {'action': 'improviser', champ: valeur('marchand'), 'methode': 'discret'}
                invariants = invariants_reprise(p, ErreurMonde())
                bon = {**p, champ: valeur(reference(m, 'marchand'))}
                verifier_reprise(bon, invariants, m)
                for mauvais in ({**bon, champ: valeur('brune')}, {**bon, 'methode': 'simple'}):
                    with self.assertRaises(ErreurMonde):
                        verifier_reprise(mauvais, invariants, m)
                if champ in LISTES_REFERENCES:
                    with self.assertRaises(ErreurMonde):
                        verifier_reprise({**bon, champ: list(reversed(bon[champ]))}, invariants, m)
        # Deux références indécodables ne deviennent pas équivalentes par leur résolution None.
        with self.assertRaises(ErreurMonde):
            verifier_reprise({'cible': 'element_9998'}, {'cible': 'element_9999'}, m)
        # L'identité conservée n'admet pas une référence privée ni une référence non fournie.
        with self.assertRaises(ErreurMonde):
            verifier_references(m, {'cible': 'marchand'}, m.contexte())
        with self.assertRaises(ErreurMonde):
            verifier_references(m, {'cible': reference(m, 'marchand')}, {})
        self.assertNotIn('cible', LISTES_REFERENCES)
        self.assertIn('cible', CHAMPS_REFERENCES)

