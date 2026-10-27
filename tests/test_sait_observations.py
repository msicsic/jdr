"""Le savoir privé de l'auditeur ne décide jamais des paroles du locuteur."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import ecoute, social
from donjon.esprits import croire, lire, constater, percoit
from donjon.monde import Monde
from donjon.rendu import regarder as rendu
from tests.support import regarder
from tests.test_constats_partages import scene
from tests.test_deja_dit import confier
from tests.test_social import recharger


class SavoirSubjectifTests(unittest.TestCase):
    def test_absences_deduites_de_places_privees_ne_sont_pas_une_vue_commune(self):
        from donjon.esprits import percevoir_tous
        m = scene()
        m.objets['ilse']['position'] = [2, 5]
        regarder(m, 'ilse', 'marchand')
        regarder(m, 'marchand', 'ilse')
        m.objets['torche'].update(lieu='echoppe', position=[4, 3], position_salle='echoppe',
                                 mobile=True, allume=False)
        for qui in ('ilse', 'marchand'):
            self.assertFalse(percoit(m, qui, 'torche'))
        for qui, case in (('ilse', [3, 4]), ('marchand', [2, 5])):
            croire(m, qui, 'torche', 'lieu', 'antichambre', 'savoir',
                   salle='antichambre', case=case)
        percevoir_tous(m)
        for qui in ('ilse', 'marchand'):
            self.assertIsNone(lire(m, qui)['croyances']['torche']['lieu']['valeur'])
        noyau = {'type': 'absence', 'objet': 'torche'}
        # Chacun a constaté une absence à une autre place qu'il attendait
        # privément : aucun objet commun n'a été vu par ces deux regards.
        self.assertFalse(social.deja_dit(recharger(m), 'ilse', 'marchand', noyau))
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_acquisition_de_salle_partagee_par_la_perception_commune(self):
        from donjon.banc_pnj import creer
        from donjon.esprits import percevoir_tous
        from tests.test_social import placer
        m = creer('crue', 1985, 'fixe')
        placer(m, 'ilse', 'antichambre', [2, 5])
        placer(m, 'marchand', 'antichambre', [3, 4])
        regarder(m, 'ilse', 'marchand')
        percevoir_tous(m)
        c = lire(m, 'ilse')['croyances']['antichambre']['eau']
        noyau = {'type': 'constat', 'objet': 'antichambre',
                 'attribut': 'eau', 'valeur': c['valeur']}
        self.assertTrue(social.deja_dit(recharger(m), 'ilse', 'marchand', noyau))
        self.assertIsNone(m._observations_communes)
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_temoins_du_meme_geste_connus_sans_confidence(self):
        from donjon import combat
        from donjon.esprits import percevoir_tous
        from tests.test_combat import scene as combat_scene
        from tests.test_social import placer
        m = combat_scene('aubin', False)
        placer(m, 'marchand', 'antichambre', [3, 4])
        regarder(m, 'marchand', 'brune')
        percevoir_tous(m)
        with patch.object(type(m), 'd20', side_effect=[20, 1]):
            combat.frapper(m, 'brune', 'aubin')
        n = next(s for s in lire(m, 'marchand')['memoire'] if s['type'] == 'vu_agir')
        self.assertTrue(social.deja_dit(recharger(m), 'marchand', 'aubin', n))
        self.assertFalse(social.deja_dit(recharger(m), 'marchand', 'ilse', n))
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_nouvelle_privee_confirmee_sur_capture_reelle_mine3(self):
        m = Monde.charger(Path(__file__).parent / 'data/mine3-josse-deja-dit.json')
        nouvelle = next(copy.deepcopy(n) for _, n, _, _ in social.nouvelles(m, 'josse')
                         if n['type'] == 'intention_lue')
        # Rémy a sa propre lecture du guet. Josse ignore cette acquisition.
        self.assertTrue(social._connait_reception(m, 'remy', nouvelle))
        self.assertFalse(social.deja_dit(m, 'josse', 'remy', nouvelle))
        debut = len(m.data['chronique'])
        m.joueur.update(salle='baraquement', position=[4, 4])
        regarder(m, 'joueur', 'josse')
        m.data['connus'] = sorted(m.objets)
        m.data['noms_connus'] = [k for k, o in m.objets.items() if o['type'] == 'personnage']
        m, dit, texte = confier(recharger(m), 'josse')
        self.assertTrue(dit)
        self.assertTrue(social.deja_dit(m, 'josse', 'remy', nouvelle))
        self.assertTrue(any(c['pnj'] == 'josse' and 'connu' in c['texte']
                            for c in m.data['chronique'][debut:]))
        self.assertIn('Odon', texte)
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))
        sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
        mots = ecoute.rendre(m, sons)
        self.assertIn('Odon', '\n'.join(mots))
        self.assertEqual(mots, ecoute.rendre(recharger(m), sons))

    def test_constat_prive_confirme_sans_effacer_la_preuve_propre(self):
        m = scene()
        for qui in ('ilse', 'marchand'):
            croire(m, qui, 'vivres', 'etat', {'disponible': False}, 'essai')
        preuve = copy.deepcopy(lire(m, 'marchand')['croyances']['vivres']['etat'])
        m, dit, texte = confier(recharger(m))
        self.assertTrue(dit)
        self.assertIn('épuisés', texte)
        self.assertEqual(preuve, lire(m, 'marchand')['croyances']['vivres']['etat'])
        self.assertEqual(m.objets['vivres']['portions'], 0)
        self.assertTrue(social.deja_dit(m, 'ilse', 'marchand',
                        {'type': 'constat', 'objet': 'vivres', 'attribut': 'etat',
                         'valeur': {'disponible': False}}))
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))
        sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
        mots = ecoute.rendre(m, sons)
        self.assertIn('épuisés', '\n'.join(mots))
        self.assertEqual(mots, ecoute.rendre(recharger(m), sons))

    def test_observation_commune_et_auditeur_hors_du_regard(self):
        for cache in (False, True):
            with self.subTest(cache=cache):
                m = scene()
                m.objets['vivres'].update(lieu='antichambre', position=[3, 3])
                m.objets['ilse']['position'] = [2, 5]
                m.objets['marchand']['position'] = [3, 4]
                regarder(m, 'ilse', 'vivres')
                regarder(m, 'marchand', 'vivres')
                if cache:
                    m.objets['ilse']['orientation'] = 'sud'
                else:
                    self.assertTrue(percoit(m, 'ilse', 'marchand'))
                    self.assertTrue(percoit(m, 'marchand', 'vivres'))
                constater(m, 'ilse', 'vivres', 'vu')
                noyau = {'type': 'constat', 'objet': 'vivres', 'attribut': 'etat',
                         'valeur': {'disponible': False}}
                self.assertEqual(social.deja_dit(recharger(m), 'ilse', 'marchand', noyau), not cache)
                self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_changement_prive_ne_rouvre_pas_le_registre_d_un_autre(self):
        m = scene()
        noyau = {'type': 'constat', 'objet': 'vivres', 'attribut': 'etat',
                 'valeur': {'disponible': False}}
        social.retenir_dit(m, 'ilse', 'marchand', noyau)
        avant = copy.deepcopy(lire(m, 'ilse')['faits_dits'])
        croire(m, 'marchand', 'vivres', 'etat', {'disponible': True}, 'essai')
        self.assertEqual(avant, lire(recharger(m), 'ilse')['faits_dits'])

    def test_changement_observe_ensemble_rouvre_l_ancienne_valeur(self):
        m = scene()
        m.objets['vivres'].update(lieu='antichambre', position=[3, 3])
        m.objets['ilse']['position'] = [2, 5]
        regarder(m, 'ilse', 'vivres')
        regarder(m, 'marchand', 'vivres')
        noyau = {'type': 'constat', 'objet': 'vivres', 'attribut': 'etat',
                 'valeur': {'disponible': False}}
        social.retenir_dit(m, 'ilse', 'marchand', noyau)
        m.objets['vivres']['portions'] = 2
        constater(m, 'ilse', 'vivres', 'vu')
        m = recharger(m)
        self.assertFalse(social.deja_dit(m, 'ilse', 'marchand', noyau))
        self.assertTrue(social.deja_dit(m, 'ilse', 'marchand',
                        {**noyau, 'valeur': {'disponible': True}}))
        # Le retour au vide appris par Ilse seule est une nouvelle pour Gorm.
        m.objets['vivres'].update(lieu='echoppe', position=[4, 3], portions=0)
        croire(m, 'ilse', 'vivres', 'etat', {'disponible': False}, 'essai')
        m, dit, texte = confier(recharger(m))
        self.assertTrue(dit)
        self.assertIn('épuisés', texte)
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))
