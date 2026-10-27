"""205 : péril invariant, transit sûr et même abri au choix et au séjour."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation, eau, pnj, planification
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import MINUTE
from tests.test_corps_blessable import passer
from tests.test_survie_en_route import sejour
from tests.test_tensions import placer, recharger


def hameau():
    m = creer('crue_hameau', 1985, 'fixe')
    # Scène d'auteur : une eau stable dans la conduite, les étages au sec.
    m.data['crue']['depart_cm'] = -90
    m.data['crue']['tirage'].update(montee_cm_heure=1, hauteur_pic_cm=-90)
    placer(m, 'ilse', 'echoppe', (5, 2))
    m.objets['porte'].update(ouverte=True, verrouillee=False)
    croire(m, 'ilse', 'porte', 'etat', {'ouverte': True}, 'vu')
    croire(m, 'ilse', 'porte', 'verrouillee', False, 'vu')
    croire(m, 'ilse', 'chambre_cloche', 'etat', {'eclairee': True}, 'savoir')
    eau.percevoir(m, 'ilse')
    e = lire(m, 'ilse')
    e['intention'] = None
    e['besoins']['securite'] = 0
    return recharger(m)


class EvacuationTests(unittest.TestCase):
    def test_capture_213_hameau_42_ne_repropose_pas_un_preparatif_dans_l_eau(self):
        source = Path(__file__).parent / 'data/engagement-213-hameau-42-peril.json.gz'
        m = recharger(Monde(json.loads(gzip.decompress(source.read_bytes()))))
        self.assertEqual(m.objets['brune']['lieu'], 'crypte')
        self.assertTrue(eau.en_peril(m, 'brune'))
        deliberation.choisir(m, 'brune', m.data['minutes'])
        i = lire(m, 'brune')['intention']
        self.assertIsNotNone(i)
        self.assertEqual(i['but']['type'], 'abri')
        self.assertEqual(i['plan'][0]['operation'], 'aller')
        self.assertIsNone(pnj.refus_etape(m, 'brune', i['plan']))
        from donjon import agendas
        self.assertEqual(agendas.contrat_intention(m, 'brune')['palier'], deliberation.Palier.PERIL_EAU)
        a = self.meme_suite(m, 3)
        self.assertFalse(eau.en_peril(a, 'brune'))
        self.assertNotEqual(a.objets['brune']['lieu'], 'crypte')

    def test_meme_refus_du_preparatif_au_palier_absolu_et_a_l_execution(self):
        m = sejour('ilse')
        plan = [planification._etape('prendre', 'vivres'),
                planification._etape('aller', lieu='chambre_cloche')]
        but = {'type': 'abri', 'lieu': 'chambre_cloche'}
        candidat = deliberation.Candidat(
            'securite', lambda m, i: (but, plan), False, True,
            deliberation.Urgence(deliberation.Palier.PERIL_EAU, 0, ()))
        self.assertIsNotNone(pnj.refus_etape(m, 'ilse', plan))
        with patch.object(deliberation, '_candidats', return_value=[candidat]):
            deliberation.choisir(m, 'ilse', m.data['minutes'])
        self.assertIsNone(lire(m, 'ilse')['intention'])
        lire(m, 'ilse')['intention'] = {'but': but, 'motif': 'securite', 'plan': plan,
                                      'depuis': m.data['minutes'], 'attente': 0}
        m = recharger(m)
        avant = dict(m.objets['vivres'])
        _, issue, etape = pnj.agir(m, 'ilse', m.data['minutes'] * MINUTE, [])
        self.assertEqual(issue, pnj.MANQUE)
        self.assertEqual(etape, plan[0])
        self.assertEqual(m.objets['vivres'], avant)
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))

    def meme_suite(self, m, duree=5):
        a, b = recharger(m), recharger(m)
        passer(a, duree * MINUTE)
        for _ in range(duree * 4):
            passer(b, MINUTE // 4)
            b = recharger(b)
        a = recharger(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(regarder(a), regarder(recharger(a)))
        return a

    def test_evacuation_ne_perd_pas_son_peril_en_adoptant_sa_sortie(self):
        for m, qui in ((sejour('brune'), 'brune'), (hameau(), 'ilse')):
            with self.subTest(qui=qui):
                salle = m.objets[qui]['lieu']
                self.assertTrue(eau.en_peril(m, qui))
                for _ in range(3):
                    deliberation.choisir(m, qui, m.data['minutes'])
                    self.assertEqual(lire(m, qui)['intention']['but']['type'], 'abri')
                    self.assertTrue(eau.en_peril(m, qui))
                    self.assertEqual(m.objets[qui]['lieu'], salle)
                    m = recharger(m)
                a = self.meme_suite(m)
                self.assertFalse(eau.en_peril(a, qui))
                self.assertEqual(eau.profondeur(a, a.objets[qui]['lieu']), 0)

    def test_recours_refuse_le_sejour_humide_et_permet_le_transit_vers_le_sec(self):
        m = hameau()
        placer(m, 'ilse', 'antichambre', (5, 2))
        m = recharger(m)
        v = planification.Vue(m, 'ilse')
        e = planification.depart(m, 'ilse', v)
        self.assertIsNone(v.route(e, 'echoppe'))
        route = v.route(e, 'chambre_cloche')
        self.assertIsNotNone(route)
        self.assertIn('echoppe', [s for s, _ in route.sejours])
        lire(m, 'ilse')['besoins']['securite'] = 85
        lire(m, 'ilse')['intention'] = {
            'but': {'type': 'abri', 'lieu': 'chambre_cloche'}, 'motif': 'securite',
            'plan': [planification._etape('aller', lieu='chambre_cloche')],
            'depuis': m.data['minutes'], 'attente': 0}
        a = self.meme_suite(m)
        self.assertEqual(a.objets['ilse']['lieu'], 'chambre_cloche')
        self.assertFalse(eau.en_peril(a, 'ilse'))

    def test_captures_reelles_ilse_destination_tenue_sans_entree_nouvelle(self):
        for seed in (7, 2024):
            with self.subTest(seed=seed):
                p = Path(__file__).parent / f'data/scenes/evacuation-205-hameau-{seed}-ilse.json.gz'
                m = recharger(Monde(json.loads(gzip.decompress(p.read_bytes()))))
                cible = lire(m, 'ilse')['intention']['but']['lieu']
                self.assertTrue(deliberation.abri_valide(m, 'ilse', cible))
                for _ in range(3):
                    resultat = deliberation._plan_abri(m, 'ilse')
                    self.assertEqual(resultat[0], {'type': 'abri', 'lieu': cible})
                    deliberation.choisir(m, 'ilse', m.data['minutes'])
                    self.assertEqual(lire(m, 'ilse')['intention']['but'], resultat[0])
                    m = recharger(m)
                self.meme_suite(m, 2)

    def test_evacuation_sans_issue_ne_reautorise_pas_un_recours_local_humide(self):
        m = sejour('ilse')
        from donjon.deplacement_objet import deplacer
        deplacer(m, 'vivres', 'ilse')
        croire(m, 'ilse', 'vivres', 'lieu', 'ilse', 'vu', salle=m.objets['ilse']['lieu'], case=None)
        croire(m, 'ilse', 'vivres', 'etat', {'disponible': True}, 'vu')
        lire(m, 'ilse')['besoins']['faim'] = 100
        m = recharger(m)
        # Le générateur ne trouve ici aucune évacuation ; le contrôle commun
        # doit encore interdire le repas sur place, sans fabriquer de sortie.
        with patch.object(deliberation, '_plan_abri', return_value=None), patch.dict(
                deliberation.PROGRES, securite=(lambda m, i: None, deliberation.SECURITE_FIN)):
            deliberation.choisir(m, 'ilse', m.data['minutes'])
        intention = lire(m, 'ilse')['intention']
        if intention:
            destinations = [x['lieu'] for x in intention['plan'] if x['operation'] == 'aller']
            self.assertTrue(destinations)
            self.assertFalse(eau.en_peril(m, 'ilse', destinations[-1]))
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_un_but_sec_ne_certifie_pas_une_action_locale_humide_avant_le_depart(self):
        m = sejour('ilse')
        lire(m, 'ilse')['besoins']['faim'] = 100
        plan = [planification._etape('manger', 'vivres'),
                planification._etape('aller', lieu='chambre_cloche')]
        candidat = deliberation.Candidat(
            'faim', lambda m, i: ({'type': 'manger', 'objet': 'vivres'}, plan), False, True,
            deliberation.Urgence(deliberation.Palier.BESOIN_PRESSANT, 100, ()))
        with patch.object(deliberation, '_candidats', return_value=[candidat]):
            deliberation.choisir(m, 'ilse', m.data['minutes'])
        self.assertIsNone(lire(m, 'ilse')['intention'])
        self.assertEqual(lire(m, 'ilse')['urgences']['faim']['etat'], 'attente')
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_le_premier_pas_sec_ne_certifie_pas_un_but_final_humide(self):
        m = sejour('brune')
        lire(m, 'brune')['intention'] = {
            'but': {'type': 'abri', 'lieu': 'echoppe'}, 'motif': 'securite',
            'plan': [planification._etape('aller', lieu='chambre_cloche'),
                     planification._etape('aller', lieu='echoppe')],
            'depuis': m.data['minutes'], 'attente': 0}
        m = recharger(m)
        self.assertTrue(eau.en_peril(m, 'brune'))
        self.assertFalse(eau.traversee_sure(m, 'brune'))
        deliberation.choisir(m, 'brune', m.data['minutes'])
        self.assertEqual(lire(m, 'brune')['intention']['but'],
                         {'type': 'abri', 'lieu': 'chambre_cloche'})
        self.assertFalse(eau.en_peril(self.meme_suite(m), 'brune'))

    def test_le_joueur_partage_le_peril_cru_sans_lire_une_intention(self):
        m = sejour('brune')
        salle = m.objets['brune']['lieu']
        m.joueur.update(salle=salle, position=[4, 2])
        eau.percevoir(m, 'joueur')
        m = recharger(m)
        self.assertTrue(eau.en_peril(m, 'joueur'))
        self.assertEqual(regarder(m), regarder(recharger(m)))
        self.assertIn('eau', regarder(m).lower())

    def test_repli_de_secours_vers_moins_d_eau_sans_abri_cru_sec(self):
        m = hameau()
        e = lire(m, 'ilse')
        for c in e['croyances'].values():
            c.pop('eau', None)
            c.pop('prevision', None)
        for salle in m.data['salles']:
            croire(m, 'ilse', salle, 'eau', 30 if salle == 'echoppe' else 10,
                   'vu', niveau=None, repere=None, montee=None)
        m = recharger(m)
        v = planification.Vue(m, 'ilse')
        self.assertIsNotNone(v.route(planification.depart(m, 'ilse', v), 'chambre_cloche'))
        plan = [planification._etape('aller', lieu='chambre_cloche')]
        self.assertFalse(eau.traversee_sure(m, 'ilse', plan))
        deliberation.choisir(m, 'ilse', m.data['minutes'])
        i = lire(m, 'ilse')['intention']
        self.assertEqual(i['but']['type'], 'abri')
        self.assertTrue(i['plan'])
        self.assertNotIn('abriter', [x['operation'] for x in i['plan']])
        a = self.meme_suite(m)
        self.assertEqual(eau.profondeur(a, a.objets['ilse']['lieu']), 0)

    def test_captures_209_peril_maintenu_sur_trois_pnj(self):
        for qui in ('aubin', 'ilse', 'marchand'):
            with self.subTest(qui=qui):
                source = Path(__file__).parent / f'data/scenes/evacuation-205-209-eau-{qui}.json.gz'
                m = recharger(Monde(json.loads(gzip.decompress(source.read_bytes()))))
                self.assertGreater(eau.eau_crue(m, qui, m.objets[qui]['lieu']), 0)
                for _ in range(3):
                    self.assertTrue(eau.en_peril(m, qui))
                    self.assertTrue(any(c.urgence.palier == deliberation.Palier.PERIL_EAU
                                        for c in deliberation._candidats(m, qui)))
                    deliberation.choisir(m, qui, m.data['minutes'])
                    self.assertEqual(lire(m, qui)['intention']['but']['type'], 'abri')
                    m = recharger(m)
                a = self.meme_suite(m, 2)
                self.assertEqual(eau.profondeur(a, a.objets[qui]['lieu']), 0)

    def test_capture_209_cible_ilse_sans_entree_nouvelle(self):
        source = Path(__file__).parent / 'data/scenes/evacuation-205-209-cible-ilse.json.gz'
        m = recharger(Monde(json.loads(gzip.decompress(source.read_bytes()))))
        cible = lire(m, 'ilse')['intention']['but']
        for _ in range(3):
            deliberation.choisir(m, 'ilse', m.data['minutes'])
            self.assertEqual(lire(m, 'ilse')['intention']['but'], cible)
            m = recharger(m)
        self.meme_suite(m, 2)

    def test_choix_et_accomplissement_refusent_le_meme_abri_humide(self):
        m = hameau()
        self.assertFalse(deliberation.abri_valide(m, 'ilse', 'echoppe'))
        self.assertIsNone(planification.abri(m, 'ilse', ['echoppe']))
        self.assertFalse(pnj._abriter(m, 'ilse', 'echoppe', []))
        self.assertEqual(regarder(m), regarder(recharger(m)))


if __name__ == '__main__':
    unittest.main()
