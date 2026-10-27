"""Nouveauté et utilité jugées par le seul locuteur, conservées au rechargement."""
import copy
import unittest

from donjon import social
from donjon.esprits import croire, lire, percevoir_tous
from donjon.rendu import regarder as rendu
from tests.test_constats_partages import scene
from tests.test_deja_dit import confier
from tests.test_social import recharger


class NouvellesUtilesTests(unittest.TestCase):
    def test_registre_plein_ne_laisse_pas_boucler_une_mesure_non_suivie(self):
        m = scene()
        lire(m, 'ilse')['faits_dits'] = {
            social._cle([f'objet_{k}', 'etat', 'allume']): {'valeur': False, 'dit_a': {}}
            for k in range(social.DITS_MAX)}
        croire(m, 'ilse', 'echoppe', 'eau', 10, 'vu', niveau=10, montee=30)
        for _ in range(2):
            m, dit, texte = confier(recharger(m))
            self.assertFalse(dit)
            self.assertEqual(texte, '')
        self.assertEqual(len(lire(m, 'ilse')['faits_dits']), social.DITS_MAX)
        self.assertEqual(m.data, recharger(m).data)

    def test_un_point_commun_ne_partage_pas_la_vitesse_privee(self):
        m = scene()
        n = {'type': 'constat', 'objet': 'echoppe', 'attribut': 'eau',
             'valeur': 20, 'details': {'montee': -30}}
        social.observation_commune(m, 'ilse', n, ['marchand'], vus={'marchand'})
        cle = social.faits_dits(n)[0][0]
        self.assertEqual(lire(recharger(m), 'ilse')['faits_dits'][cle]['portee_a']['marchand'], [1, 0])
        self.assertTrue(social._nouveau(recharger(m), 'ilse', 'marchand', n))
        # Une seconde mesure plus basse, observée ensemble, rend la décrue commune.
        social.observation_commune(m, 'ilse', {**n, 'valeur': 19}, ['marchand'], vus={'marchand'})
        self.assertEqual(lire(recharger(m), 'ilse')['faits_dits'][cle]['portee_a']['marchand'], [1, -1])
        self.assertFalse(social._nouveau(recharger(m), 'ilse', 'marchand', {**n, 'valeur': 19}))
        # La mesure entière ne bouge pas à chaque regard : ne pas effacer ce sens acquis.
        social.observation_commune(m, 'ilse', {**n, 'valeur': 19}, ['marchand'], vus={'marchand'})
        self.assertEqual(lire(recharger(m), 'ilse')['faits_dits'][cle]['portee_a']['marchand'], [1, -1])
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_le_meme_geste_n_est_pas_nouveau_par_son_lese_ou_sa_precision(self):
        from donjon.esprits import memoriser
        m = scene()
        n = {'type': 'vu_agir', 'auteur': 'brune', 'objet': 'vivres',
             'operation': 'prendre', 'victime': 'ilse'}
        social.retenir_dit(m, 'ilse', 'marchand', n)
        memoriser(m, 'marchand', n)
        autre_jugement = {**n, 'victime': 'marchand'}
        self.assertTrue(social.deja_dit(recharger(m), 'ilse', 'marchand', autre_jugement))
        precision = {**autre_jugement, 'lieu': {'valeur': 'echoppe', 'minute': 0,
                                              'salle': 'echoppe', 'case': [4, 3]}}
        self.assertTrue(social._connait_reception(recharger(m), 'marchand', precision))

    def test_mesures_confiees_ne_se_redisent_qu_au_changement_de_consequence(self):
        from donjon.eau import NOYEE_CM
        from donjon.temps import ecouler
        from tests.test_sait_observations import mots_enregistres
        m = scene()
        lire(m, 'ilse')['memoire'].append({'type': 'engagement_pris',
            'minute': m.data['minutes'], 'pour': 'marchand',
            'condition': {'objet': 'vivres', 'lieu': 'echoppe'}})
        for hauteur, attendu in ((10, True), (11, False), (NOYEE_CM, True),
                                  (NOYEE_CM + 1, False), (0, True)):
            croire(m, 'ilse', 'echoppe', 'eau', hauteur, 'vu', niveau=hauteur,
                   montee=30 if hauteur else -30, repere=[m.data['minutes'], hauteur])
            m, dit, texte = confier(recharger(m))
            self.assertEqual(dit, attendu, (hauteur, texte))
            if attendu:
                self.assertIn(f'{hauteur} cm', texte)
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(rendu(m), rendu(recharger(m)))
            self.assertEqual(mots_enregistres(m, 'ilse'), mots_enregistres(recharger(m), 'ilse'))
            ecouler(m, 600)
        self.assertEqual(sum(bool(c.get('constat_confie')) for c in m.data['chronique']), 3)

    def test_besoin_prive_ignore_et_besoin_observe_utile(self):
        m = scene()
        m.objets['vivres']['proprietaire'] = 'joueur'
        n = {'type': 'constat', 'objet': 'vivres', 'attribut': 'etat',
             'valeur': {'disponible': False}, 'observe': m.data['minutes']}
        croire(m, 'ilse', 'vivres', 'etat', n['valeur'], 'essai')
        croire(m, 'ilse', 'marchand', 'etat', {'faim': False}, 'vu')
        avant = copy.deepcopy(lire(m, 'ilse'))
        lire(m, 'marchand')['besoins']['faim'] = 100
        self.assertFalse(social._utile(m, 'ilse', 'marchand', n))
        self.assertEqual(avant, lire(m, 'ilse'))
        croire(m, 'ilse', 'marchand', 'etat', {'faim': True}, 'vu')
        m, dit, texte = confier(recharger(m))
        self.assertTrue(dit)
        self.assertIn('épuisés', texte)
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_projet_convenu_suffit_sans_lire_le_plan_prive(self):
        m = scene()
        n = {'type': 'constat', 'objet': 'brasero', 'attribut': 'etat',
             'valeur': {'allume': False}}
        croire(m, 'ilse', 'marchand', 'etat', {'chaleur': False}, 'vu')
        self.assertFalse(social._utile(m, 'ilse', 'marchand', n))
        lire(m, 'ilse')['memoire'].append({'type': 'engagement_pris',
            'minute': m.data['minutes'], 'pour': 'marchand',
            'condition': {'objet': 'brasero', 'allume': True}})
        self.assertTrue(social._utile(recharger(m), 'ilse', 'marchand', n))
        lire(m, 'ilse')['memoire'].append({'type': 'engagement_tenu',
            'minute': m.data['minutes'], 'pour': 'marchand',
            'condition': {'objet': 'brasero', 'allume': True}})
        self.assertFalse(social._utile(recharger(m), 'ilse', 'marchand', n))

    def test_hauteurs_successives_seuil_et_decrue_sur_deux_nuits(self):
        from donjon.banc_pnj import creer
        from donjon.eau import NOYEE_CM
        # Deux nuits qui produisaient des confirmations à chaque mesure au lot 206.
        for scenario, graine in (('crue', 1985), ('crue_hameau', 7)):
            with self.subTest(scenario=scenario):
                m = creer(scenario, graine, 'tire')
                percevoir_tous(m)
                n = {'type': 'constat', 'objet': 'conduite', 'attribut': 'eau',
                     'valeur': 10, 'details': {'montee': 30}}
                # L'identité de salle est prise dans le monde, pas un nom d'auteur.
                n['objet'] = next(s for s, d in lire(m, 'brune')['croyances'].items()
                                   if s in m.data['salles'] and 'eau' in d)
                social.retenir_dit(m, 'brune', 'marchand', n)
                m = recharger(m)
                self.assertFalse(social._nouveau(m, 'brune', 'marchand', {**n, 'valeur': 11}))
                self.assertTrue(social._nouveau(m, 'brune', 'marchand', {**n, 'valeur': NOYEE_CM}))
                social.retenir_dit(m, 'brune', 'marchand', {**n, 'valeur': NOYEE_CM})
                baisse = {**n, 'valeur': NOYEE_CM + 1, 'details': {'montee': -30}}
                self.assertTrue(social._nouveau(recharger(m), 'brune', 'marchand', baisse))
                social.retenir_dit(m, 'brune', 'marchand', baisse)
                self.assertFalse(social._nouveau(recharger(m), 'brune', 'marchand',
                                                {**baisse, 'valeur': NOYEE_CM + 2}))
                self.assertEqual(m.data, recharger(m).data)
                self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_environnement_acquis_ensemble_meme_hors_champ_directionnel(self):
        from donjon.banc_pnj import creer
        from tests.support import regarder
        from tests.test_social import placer
        m = creer('crue', 1985, 'fixe')
        placer(m, 'brune', 'antichambre', [2, 4])
        placer(m, 'marchand', 'antichambre', [3, 4])
        regarder(m, 'brune', 'marchand')
        percevoir_tous(m)
        communs = set(lire(m, 'brune')['croyances']) & set(lire(m, 'marchand')['croyances'])
        for s in communs & set(m.data['salles']):
            a = lire(m, 'brune')['croyances'][s].get('eau')
            b = lire(m, 'marchand')['croyances'][s].get('eau')
            if a and b and a['minute'] == b['minute']:
                n = {'type': 'constat', 'objet': s, 'attribut': 'eau', 'valeur': a['valeur']}
                self.assertTrue(social.deja_dit(recharger(m), 'brune', 'marchand', n))
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))
