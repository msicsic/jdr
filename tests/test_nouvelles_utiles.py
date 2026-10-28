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
    def test_capture_reelle_tilo_previent_mireille_du_bois_epuise(self):
        import gzip
        import json
        from pathlib import Path
        from donjon.monde import Monde
        from tests.support import regarder
        from tests.test_sait_observations import mots_enregistres
        p = Path(__file__).parent / 'data/signalements-auberge-3-570.json.gz'
        m = Monde(json.loads(gzip.decompress(p.read_bytes())))
        # Capture conservée à 570 : ni besoins, ni projets, ni croyances
        # réécrits. Seul le joueur vient écouter la confidence dans la cuisine.
        m.joueur.update(salle='cuisine', position=[3, 1])
        regarder(m, 'joueur', 'tilo')
        m.data['connus'] = sorted(m.objets)
        m.data['noms_connus'] = [k for k, o in m.objets.items() if o['type'] == 'personnage']
        n = next(n for _, n, _, _ in social.nouvelles(m, 'tilo') if n.get('objet') == 'bois_reserve_2')
        self.assertTrue(social._utile(recharger(m), 'tilo', 'mireille', n))
        m, dit, texte = confier(recharger(m), 'tilo')
        self.assertTrue(dit)
        self.assertIn('épuisé', texte)
        self.assertTrue(social.deja_dit(m, 'tilo', 'mireille', n))
        self.assertEqual(m.objets['bois_reserve_2']['charges'], 0)
        self.assertIn('épuisé', mots_enregistres(m, 'tilo'))
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(rendu(m), rendu(recharger(m)))
        self.assertFalse(social._nouveau(recharger(m), 'tilo', 'mireille', n))
        from donjon import pnj
        from donjon.temps import ecouler
        from unittest.mock import patch
        resultats = []
        for tranches in ((600,), (150,) * 4):
            suite, lignes = recharger(m), []
            with patch.object(Monde, 'd20', return_value=20):
                for dt in tranches:
                    minutes = ecouler(suite, dt)
                    pnj.avancer(suite, minutes, lignes, dt)
                    suite = recharger(suite)
            self.assertEqual(suite.objets['bois_reserve_2']['charges'], 0)
            self.assertEqual(suite.data, recharger(suite).data)
            self.assertEqual(rendu(suite), rendu(recharger(suite)))
            resultats.append((suite.data, rendu(suite), mots_enregistres(suite, 'tilo')))
        self.assertEqual(*resultats)

    def test_bien_connu_utile_sans_detresse_et_redite_tue(self):
        from donjon import pnj
        from donjon.monde import Monde
        from donjon.temps import ecouler
        from unittest.mock import patch
        from tests.test_sait_observations import mots_enregistres
        # Même situation que les extinctions perdues au 206 : le propriétaire
        # est dans une salle éclairée et n'a annoncé aucun projet de rallumage.
        for objet, valeur, mot in (('brasero', {'allume': False}, 'éteint'),
                                   ('vivres', {'disponible': False}, 'épuisés')):
            with self.subTest(objet=objet):
                initial = scene()
                initial.objets[objet]['proprietaire'] = 'marchand'
                o = initial.objets[objet]
                croire(initial, 'ilse', objet, 'lieu', o['lieu'], 'vu',
                       salle=o['lieu'], case=o.get('position'))
                if objet == 'brasero':
                    initial.objets[objet]['allume'] = False
                croire(initial, 'ilse', 'marchand', 'etat', {'faim': False, 'chaleur': False}, 'vu')
                croire(initial, 'ilse', objet, 'etat', valeur, 'essai')
                lire(initial, 'marchand')['libre'] = 10000
                # Les autres constats ne sont pas la nouvelle testée.
                resultats = []
                for tranches in ((1200,), (150,) * 8):
                    m, lignes = recharger(initial), []
                    with patch.object(Monde, 'd20', return_value=20):
                        for dt in tranches:
                            minutes = ecouler(m, dt)
                            pnj.avancer(m, minutes, lignes, dt)
                            m = recharger(m)
                    dits = [c for c in m.data['chronique'] if c.get('constat_confie')
                            and mot in c['texte']]
                    self.assertEqual(len(dits), 1, dits)
                    self.assertTrue(social.deja_dit(m, 'ilse', 'marchand',
                        {'type': 'constat', 'objet': objet, 'attribut': 'etat', 'valeur': valeur}))
                    self.assertIn(mot, mots_enregistres(m, 'ilse'))
                    self.assertEqual(m.data, recharger(m).data)
                    self.assertEqual(rendu(m), rendu(recharger(m)))
                    resultats.append((m.data, rendu(m), mots_enregistres(m, 'ilse')))
                self.assertEqual(*resultats)

    def test_support_cru_du_bien_et_non_son_support_reel(self):
        m = scene()
        m.objets['vivres']['proprietaire'] = 'marchand'
        croire(m, 'ilse', 'vivres', 'lieu', 'reserve', 'vu', salle='echoppe', case=[4, 3])
        n = {'type': 'constat', 'objet': 'reserve', 'attribut': 'verrouillee', 'valeur': True}
        self.assertTrue(social._utile(recharger(m), 'ilse', 'marchand', n))
        # Une relocalisation privée du monde ne révise pas le lien cru.
        m.objets['vivres']['lieu'] = 'crypte'
        self.assertTrue(social._utile(recharger(m), 'ilse', 'marchand', n))
        croire(m, 'ilse', 'vivres', 'lieu', 'crypte', 'vu', salle='crypte', case=[4, 3])
        self.assertFalse(social._utile(recharger(m), 'ilse', 'marchand', n))

    def test_don_distant_ne_change_pas_le_proprietaire_cru(self):
        m = scene()
        m.objets['vivres']['proprietaire'] = 'marchand'
        croire(m, 'ilse', 'vivres', 'lieu', 'echoppe', 'vu', salle='echoppe', case=[4, 3])
        n = {'type': 'constat', 'objet': 'vivres', 'attribut': 'etat', 'valeur': {'disponible': False}}
        croire(m, 'ilse', 'marchand', 'etat', {'faim': False}, 'vu')
        m.objets['vivres']['proprietaire'] = 'brune'
        self.assertTrue(social._utile(recharger(m), 'ilse', 'marchand', n))
        croire(m, 'ilse', 'vivres', 'lieu', 'echoppe', 'vu', salle='echoppe', case=[4, 3])
        self.assertFalse(social._utile(recharger(m), 'ilse', 'marchand', n))
        # Constater une absence n'apprend pas à qui l'objet a été donné.
        croire(m, 'ilse', 'vivres', 'lieu', None, 'vu', salle=None, case=None)
        self.assertNotIn('possession', lire(recharger(m), 'ilse')['croyances']['vivres']['lieu'])

    def test_danger_sur_le_lieu_cru_du_bien_concerne_son_proprietaire(self):
        m = scene()
        m.objets['vivres']['proprietaire'] = 'marchand'
        croire(m, 'ilse', 'vivres', 'lieu', 'echoppe', 'vu', salle='echoppe', case=[4, 3])
        n = {'type': 'avis', 'objet': 'echoppe', 'attribut': 'menace', 'valeur': True}
        self.assertTrue(social._utile(recharger(m), 'ilse', 'marchand', n))
        social.retenir_dit(m, 'ilse', 'marchand', n)
        self.assertFalse(social._nouveau(recharger(m), 'ilse', 'marchand', n))

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
        self.assertEqual(lire(recharger(m), 'ilse')['faits_dits'][cle]['portee_a']['marchand'], [1, None])
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
