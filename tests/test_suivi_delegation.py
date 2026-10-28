"""Échéances de paroles connues : aucune échéance reconstruite ni savoir distant."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, echanges, planification as p
from donjon.banc_pnj import creer
from donjon.esprits import lire, croire, percevoir_tous
from donjon.monde import Monde, ErreurMonde
from tests.test_tensions import recharger, placer, vivre
from tests.test_empathie import rendu


class SuiviDelegationTests(unittest.TestCase):
    def aide(self):
        from tests.test_gardien_detresse import GardienDetresseTests
        m = GardienDetresseTests().lumiere()
        with patch.object(Monde, 'd20', return_value=20):
            d.choisir(m, 'bram', m.data['minutes'])
            self.assertTrue(echanges.executer(m, 'bram', lire(m, 'bram')['intention']['plan'][0], []))
        return recharger(m)

    def scene_joueur(self):
        from tests.support import calme
        m = creer('relais', 1985, 'fixe')
        calme(m, *[k for k, o in m.objets.items() if o.get('profil')])
        pulsion = copy.deepcopy(next(x for x in m.objets['marchand']['profil']['pulsions'] if x.get('delegue_a')))
        pulsion['echeance'] = 2
        m.objets['marchand']['profil']['pulsions'] = [pulsion]
        lire(m, 'marchand')['pulsions'] = [None]
        placer(m, 'marchand', 'echoppe', [4, 5])
        m.joueur.update(salle='echoppe', position=[4, 4])
        percevoir_tous(m)
        return self.recharge(m)

    def test_controle_joueur_execute_et_laps_decoupe(self):
        m = self.scene_joueur()
        a, texte = vivre(recharger(m), 6, jet=20)
        b = recharger(m)
        for _ in range(6):
            b, _ = vivre(b, 1, jet=20)
        self.assertEqual(a.data, b.data)
        self.assertGreater(lire(a, 'marchand')['visites'].get('antichambre', -1), 2)
        self.assertFalse(list(agendas.suivis_delegations(a, 'marchand')))
        self.assertIn('Gorm', '\n'.join(texte))
        self.recharge(a)

    def test_controle_abandonne_sur_realisation_apprise_en_route(self):
        m = self.scene_joueur()
        m.data['minutes'] = 3
        d.choisir(m, 'marchand', 3)
        i = lire(m, 'marchand')['intention']
        self.assertIsNotNone(i)
        self.assertEqual(i['but'], {'type': 'voir', 'lieu': 'antichambre'})
        self.assertTrue(i['plan'])
        # Nouvelle crédible : on ne lit pas la vérité distante pour arrêter le contrôle.
        croire(m, 'marchand', 'cloche', 'lieu', 'antichambre', 'entendu', salle='antichambre', case=None)
        m = self.recharge(m)
        d.choisir(m, 'marchand', 3)
        self.assertFalse(list(agendas.suivis_delegations(m, 'marchand')))
        i = lire(m, 'marchand')['intention']
        self.assertFalse(i and i['but'] == {'type': 'voir', 'lieu': 'antichambre'})
        self.recharge(m)

    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        return n

    def test_confier_conserve_duree_mesurable_sans_modifier_engagement(self):
        m = self.aide()
        aide = lire(m, 'bram')['aides_attendues']['chandelle']
        self.assertIn('echeance', aide)
        self.assertGreaterEqual(aide['echeance'], aide['minute'])
        self.assertNotIn('echeance', agendas.en_cours(m, 'josse')[0])
        self.recharge(m).verifier()

    def test_devis_sans_duree_ne_fabrique_pas_echeance(self):
        with patch.object(p, 'duree_devis', return_value=None):
            m = self.aide()
        aide = lire(m, 'bram')['aides_attendues']['chandelle']
        self.assertNotIn('echeance', aide)
        m.data['minutes'] += 10
        self.assertFalse(list(agendas.suivis_delegations(self.recharge(m), 'bram')))

    def test_ancienne_aide_sans_echeance_ne_declenche_pas_de_visite(self):
        m = self.aide()
        aide = lire(m, 'bram')['aides_attendues']['chandelle']
        aide.pop('echeance', None)
        m.data['minutes'] += 10
        m = self.recharge(m)
        self.assertEqual(list(agendas.suivis_delegations(m, 'bram')), [])
        self.assertTrue(p.vue(m, 'bram').aides)

    def test_attente_avant_echeance_puis_controle_sur_croyances(self):
        m = self.aide()
        aide = lire(m, 'bram')['aides_attendues']['chandelle']
        m.data['minutes'] = aide['echeance']
        self.assertEqual(list(agendas.suivis_delegations(self.recharge(m), 'bram')), [])
        m.data['minutes'] += 1
        m = self.recharge(m)
        self.assertEqual(list(agendas.suivis_delegations(m, 'bram')), ['bureau'])
        self.assertFalse(p.vue(m, 'bram').aides)
        # La réalisation réelle distante seule ne clôt aucune attente.
        m.objets['chandelle']['allume'] = True
        self.assertEqual(list(agendas.suivis_delegations(m, 'bram')), ['bureau'])
        percevoir_tous(m)
        self.assertEqual(list(agendas.suivis_delegations(self.recharge(m), 'bram')), [])

    def test_realisation_a_temps_sans_controle_et_laps_decoupe(self):
        m = self.aide()
        a, _ = vivre(recharger(m), 3, jet=20)
        b = recharger(m)
        for _ in range(3):
            b, _ = vivre(b, 1, jet=20)
            b = recharger(b)
        self.assertEqual(a.data, b.data)
        self.assertTrue(a.objets['chandelle']['allume'])
        self.assertEqual(list(agendas.suivis_delegations(a, 'bram')), [])
        self.recharge(a)

    def test_autre_charge_en_retard_reprend_un_geste_apres_recharge(self):
        m = self.aide()
        aide = lire(m, 'bram')['aides_attendues']['chandelle']
        m.data['minutes'] = aide['echeance'] + 1
        m = self.recharge(m)
        d.choisir(m, 'bram', m.data['minutes'])
        i = lire(m, 'bram')['intention']
        self.assertIsNotNone(i)
        self.assertTrue(i['plan'])
        n, _ = vivre(m, 2, jet=20)
        self.assertTrue(n.objets['chandelle']['allume'])
        # La lampe est allumée derrière Bram : sa réalisation physique ne
        # lui apprend pas magiquement son état. Il le constate en la regardant.
        from tests.support import regarder
        regarder(n, 'bram', 'chandelle')
        percevoir_tous(n)
        self.assertFalse(list(agendas.suivis_delegations(n, 'bram')))
        self.recharge(n)

    def test_duree_physique_distincte_du_prix_et_prefixe_indetermine(self):
        m = self.aide()
        etapes = [p._etape('inspecter', lieu='bureau')]
        a = p.duree_devis(m, 'josse', etapes)
        self.assertIsNotNone(a)
        with patch.dict(p.pnj.DUREES, inspecter=200):
            self.assertAlmostEqual(p.duree_devis(m, 'josse', etapes) - a, 100 / 600)
        self.assertIsNone(p.duree_devis(m, 'josse', [{**etapes[0], 'suppose': True}]))
        self.assertIsNone(p.duree_devis(m, 'josse', [p._etape('crocheter', 'porte_bureau')]))

    def test_echeances_aide_mal_formees_refus_avec_attendu(self):
        m = self.aide()
        for valeur in (True, -1, 1.5, 'demain', None):
            with self.subTest(valeur=valeur):
                n = m.copier()
                lire(n, 'bram')['aides_attendues']['chandelle']['echeance'] = valeur
                with self.assertRaises(ErreurMonde) as erreur:
                    n.verifier()
                self.assertIn('echeance', erreur.exception.attendu)

    def test_delegation_joueur_sans_echeance_puis_scene_avec_accord(self):
        m = creer('relais', 1985, 'fixe')
        pulsion = next(x for x in m.objets['marchand']['profil']['pulsions'] if x.get('delegue_a'))
        m.data['minutes'] = 220
        self.assertTrue(d._delegue(m, 'marchand', pulsion))
        self.assertEqual(agendas.en_cours(m, 'joueur'), [])
        # Scène d'auteur : accord explicite « avant la minute 221 ».
        pulsion['echeance'] = 221
        self.assertTrue(d._delegue(self.recharge(m), 'marchand', pulsion))
        m.data['minutes'] = 222
        m = self.recharge(m)
        self.assertFalse(d._delegue(m, 'marchand', pulsion))
        self.assertEqual(list(agendas.suivis_delegations(m, 'marchand')), ['antichambre'])
        lire(m, 'marchand')['visites']['antichambre'] = 222
        self.assertEqual(list(agendas.suivis_delegations(self.recharge(m), 'marchand')), [])

    def test_delegation_initiale_invalide_refuse_avec_attendu(self):
        for valeur in (True, -1, 'demain'):
            m = creer('relais', 1985, 'fixe')
            pulsion = next(x for x in m.objets['marchand']['profil']['pulsions'] if x.get('delegue_a'))
            pulsion['echeance'] = valeur
            with self.assertRaises(ErreurMonde) as erreur:
                m.verifier()
            self.assertIn('echeance', erreur.exception.attendu)

    def test_realisation_clot_definitivement_sans_reactivation_par_perte(self):
        m = self.scene_joueur()
        m.data['minutes'] = 1
        croire(m, 'marchand', 'cloche', 'lieu', 'antichambre', 'entendu', salle='antichambre', case=None)
        d.choisir(m, 'marchand', 1)
        pulsion = m.objets['marchand']['profil']['pulsions'][0]
        self.assertNotIn('delegue_a', pulsion)
        self.assertNotIn('echeance', pulsion)
        m.data['minutes'] = 4
        croire(m, 'marchand', 'cloche', 'lieu', 'chambre_cloche', 'entendu', salle='chambre_cloche', case=None)
        m = self.recharge(m)
        self.assertFalse(list(agendas.suivis_delegations(m, 'marchand')))
        self.assertFalse(d._delegue(m, 'marchand', pulsion))

        m = self.aide()
        m.data['minutes'] += 1
        croire(m, 'bram', 'chandelle', 'etat', {'allume': True, 'charge': True}, 'entendu')
        d.choisir(m, 'bram', m.data['minutes'])
        self.assertNotIn('chandelle', lire(m, 'bram')['aides_attendues'])
        m.data['minutes'] += 2
        croire(m, 'bram', 'chandelle', 'etat', {'allume': False, 'charge': True}, 'entendu')
        self.assertFalse(list(agendas.suivis_delegations(self.recharge(m), 'bram')))

    def test_echeance_amener_ouvre_constat_sans_nouvelle_delegation(self):
        from tests.test_engagement_deplacement import scene
        from tests.test_agendas_amener_fin import declarer
        from tests.test_agendas_amener_social import prochain
        m, condition = scene('ilse', 'chambre_cloche')
        m = declarer(m, 'ilse', 'chambre_cloche')
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.confier(m, 'marchand', 'ilse', condition), 'accepte')
        aide = lire(m, 'marchand')['aides_attendues']['ilse']
        self.assertIn('echeance', aide)
        accord = copy.deepcopy(aide)
        m.data['minutes'] = aide['echeance'] + 1
        placer(m, 'marchand', 'chambre_cloche', [1, 3])
        lire(m, 'marchand')['visites']['chambre_cloche'] = aide['echeance']
        m = self.recharge(m)
        but, etapes = prochain(m)
        self.assertTrue(etapes)
        self.assertEqual(etapes[-1]['operation'], 'inspecter')
        self.assertFalse(any(g['operation'] == 'confier' for g in etapes))
        self.assertEqual(lire(m, 'marchand')['aides_attendues']['ilse'], accord)
        self.assertEqual(len(agendas.en_cours(m, 'ilse')), 1)
        lire(m, 'marchand')['visites']['chambre_cloche'] = m.data['minutes']
        self.assertEqual(prochain(self.recharge(m))[1], [])

    def test_relance_ne_duplique_pas_engagement_en_cours(self):
        m = self.aide()
        self.assertEqual(len(agendas.en_cours(m, 'josse')), 1)
        aide = lire(m, 'bram')['aides_attendues']['chandelle']
        m.data['minutes'] = aide['echeance'] + 1
        d.choisir(m, 'bram', m.data['minutes'])
        etape = lire(m, 'bram')['intention']['plan'][0]
        self.assertEqual(etape['operation'], 'confier')
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(echanges.executer(m, 'bram', etape, []))
        self.assertEqual(len(agendas.en_cours(self.recharge(m), 'josse')), 1)
        self.assertEqual(agendas.en_cours(m, 'josse')[0]['minute'], m.data['minutes'])
        self.assertGreater(lire(m, 'bram')['aides_attendues']['chandelle']['echeance'], aide['echeance'])

    def test_relance_autre_condition_conserve_deux_obligations_distinctes(self):
        from tests.test_engagement_deplacement import scene
        m, c1 = scene('ilse', 'chambre_cloche')
        c2 = {'objet': 'ilse', 'lieu': 'echoppe'}
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.confier(m, 'marchand', 'ilse', c1), 'accepte')
            self.assertEqual(echanges.confier(m, 'marchand', 'ilse', c2), 'accepte')
        avant = agendas.en_cours(m, 'ilse')
        self.assertEqual(len(avant), 2)
        m.data['minutes'] += 1
        m = self.recharge(m)
        with patch.object(echanges, 'jet_persuasion', side_effect=AssertionError('accord deja actif')):
            self.assertEqual(echanges.confier(m, 'marchand', 'ilse', c1), 'accepte')
        apres = agendas.en_cours(self.recharge(m), 'ilse')
        self.assertEqual([x['condition'] for x in apres], [c1, c2])
        self.assertEqual(apres[1], avant[1])
        self.assertEqual(apres[0]['minute'], m.data['minutes'])

    def test_engagement_annule_ou_clos_n_est_pas_renouvele(self):
        m = self.aide()
        ancien = agendas.en_cours(m, 'josse')[0]
        agendas.retirer_proposition(m, 'josse', ancien)
        annule = {**ancien, 'annule': 'refus'}
        agendas.prendre(m, 'josse', annule)
        m.data['minutes'] += 1
        m = self.recharge(m)
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.confier(m, 'bram', 'josse', ancien['condition']), 'accepte')
        engagements = agendas.en_cours(self.recharge(m), 'josse')
        self.assertEqual(engagements[0], annule)
        self.assertEqual(len(engagements), 2)
        actif = agendas.en_cours(m, 'josse', actifs=True)[0]
        agendas.annoncer_abandon(m, 'josse', annule)
        agendas.retirer_proposition(m, 'josse', actif)
        m.data['minutes'] += 1
        m = self.recharge(m)
        with patch.object(Monde, 'd20', return_value=20), patch.object(agendas, 'renouveler', side_effect=AssertionError('parole close')):
            self.assertEqual(echanges.confier(m, 'bram', 'josse', ancien['condition']), 'accepte')
        self.assertEqual(len(agendas.en_cours(self.recharge(m), 'josse')), 1)
