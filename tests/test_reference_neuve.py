"""433 : inscription transactionnelle avant rendu, qualification et geste."""
import copy
import unittest

from donjon import narration, noms, rendu
from donjon.enrichissement import preparer_complements
from donjon.faits_locaux import preparer_faits
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.voix import reel
from tests import test_creation_interactive as creation
from tests.test_refus_rendu import capture
from tests.test_tensions import recharger


class ReferenceNeuveTests(unittest.TestCase):
    def assertRegistre(self, monde):
        registre = copy.deepcopy(monde.data['references_personnes'])
        self.assertEqual(len(set(registre.values())), len(registre))
        for id in monde.objets:
            self.assertIn(id, registre)
            ref = noms.reference(monde, id)
            self.assertEqual(reel(monde, ref), id)
        # Ni la lecture, ni la réinstallation n'attribue un nouveau numéro.
        self.assertEqual(monde.data['references_personnes'], registre)
        noms.installer(monde)
        self.assertEqual(monde.data['references_personnes'], registre)

    def test_plusieurs_complements_inscrits_sans_renumerotation(self):
        m = Monde(capture()['monde'])
        avant = copy.deepcopy(m.data)
        travail = preparer_complements(m, {'ajouts': [
            dict(personnage='aubin', facette=f, description=texte)
            for f, texte in (('yeux', 'Ses yeux sont gris clair.'),
                             ('mains', 'Ses mains sont noueuses.'))]})
        self.assertRegistre(travail)
        refs = {id: noms.reference(travail, id) for id in
                ('detail_aubin_yeux', 'detail_aubin_mains')}
        # Un second ajout dont l'id précède les premiers ne les décale pas.
        travail = preparer_complements(travail, {'ajouts': [dict(
            personnage='aubin', facette='cheveux', description='Ses cheveux sont courts.')]})
        self.assertRegistre(travail)
        for id, ref in refs.items():
            self.assertTrue(ref.startswith('element_'))
            self.assertEqual(noms.reference(travail, id), ref)
            self.assertEqual(reel(travail, ref), id)
            self.assertEqual(rendu.decrire(travail, ref), rendu.decrire(travail, id))
        recharge = recharger(travail)
        self.assertRegistre(recharge)
        self.assertEqual(recharge.data['references_personnes'], travail.data['references_personnes'])
        self.assertEqual(rendu.regarder(recharge), rendu.regarder(travail))
        self.assertEqual(m.data, avant)

    def test_detail_et_inscription_inscrits_avant_rendu_et_recharge(self):
        for nature in ('detail', 'inscription'):
            with self.subTest(nature=nature):
                m = Monde(capture()['monde'])
                avant = copy.deepcopy(m.data)
                travail, _, etablis = preparer_faits(m, {'ajouts': [dict(
                    type=nature, ancrage='briquet', nom='surface mate' if nature == 'detail' else '',
                    genre='f' if nature == 'detail' else '', texte='La surface est mate.')]})
                id = etablis[0]['objet']
                ref = noms.reference(travail, id)
                self.assertRegistre(travail)
                self.assertEqual(reel(travail, ref), id)
                self.assertEqual(rendu.decrire(travail, ref), rendu.decrire(travail, id))
                narration.attestations(travail, travail.contexte())
                recharge = recharger(travail)
                self.assertEqual(noms.reference(recharge, id), ref)
                self.assertEqual(reel(recharge, ref), id)
                self.assertEqual(rendu.regarder(travail), rendu.regarder(recharge))
                # Un numéro inscrit ne confère ni vue, ni droit de manipulation.
                recharge.objets['briquet']['lieu'] = 'crypte'
                with self.assertRaises(ErreurMonde):
                    rendu.decrire(recharge, ref)
                with self.assertRaises(ErreurMonde):
                    Moteur(recharge).preparer(proposition('examiner', ref))
                self.assertNotIn(id, {o['id'] for o in recharge.contexte()['objets_perceptibles']})
                self.assertEqual(m.data, avant)

    def test_qualification_du_nouvel_objet_conserve_sa_reference(self):
        for m, support, nom, matiere in creation.CreationInteractiveTests().scenes():
            with self.subTest(nom=nom):
                travail, _, etablis = preparer_faits(m, {'ajouts': [dict(
                    type='objet', ancrage=support, nom=nom, genre='m', texte='Sa surface est mate.',
                    materiau=matiere, masse=0.2, mobile=True, relation='pose', capacites=[])]})
                id = etablis[0]['objet']
                self.assertRegistre(travail)
                registre = copy.deepcopy(travail.data['references_personnes'])
                ref = noms.reference(travail, id)
                qualifie, _, _ = preparer_faits(travail, {'ajouts': [dict(
                    type='qualification', ancrage=id, ecartees=['lumiere'])]})
                self.assertEqual(qualifie.data['references_personnes'], registre)
                self.assertEqual(reel(qualifie, ref), id)
                moteur = Moteur(qualifie)
                moteur.executer(moteur.preparer(proposition('prendre', ref)))
                recharge = recharger(qualifie)
                self.assertEqual(recharge.objets[id]['lieu'], 'joueur')
                self.assertEqual({i: recharge.data['references_personnes'][i] for i in registre}, registre)
                self.assertEqual(reel(recharge, ref), id)
                self.assertEqual(rendu.regarder(recharge), rendu.regarder(qualifie))

    def test_echec_apres_premier_ajout_n_inscrit_rien(self):
        m = Monde(capture()['monde'])
        avant = copy.deepcopy(m.data)
        ajout = dict(personnage='aubin', facette='mains', description='Ses mains sont noueuses.')
        with self.assertRaises(ErreurMonde):
            preparer_complements(m, {'ajouts': [ajout, ajout]})
        ajout = dict(type='detail', ancrage='planches', nom='surface mate', genre='f',
                     texte='La surface est mate.')
        with self.assertRaises(ErreurMonde):
            preparer_faits(m, {'ajouts': [ajout, ajout]})
        self.assertEqual(m.data, avant)
        recharge = recharger(m)
        self.assertEqual(recharge.data['references_personnes'], avant['references_personnes'])
        self.assertEqual(set(recharge.objets), set(m.objets))
        self.assertEqual(rendu.regarder(recharge), rendu.regarder(m))


if __name__ == '__main__':
    unittest.main()
