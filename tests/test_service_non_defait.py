"""Résultat d'une parole, présence crue, gestes autonomes et sauvegarde."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, planification
from donjon.biens import retenir_service, services_proteges
from donjon.deliberation import menager_flamme
from donjon.echanges import engager
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.support import calme
from tests.test_tache_promise_recours import reserve
from tests.test_tensions import recharger, vivre


def cas_217():
    with gzip.open(Path(__file__).parent / 'fixtures/changements_avis/service-217.json.gz',
                   'rt', encoding='utf8') as f:
        return Monde(json.load(f)['etats']['reussite'])


def serrure(payeur=None):
    m, id, autre, c = reserve()
    calme(m, id, autre)
    # La clé et le contenu sont à Joss : sans protection, son propre plan
    # peut les employer sans demander de permission ni lire l'esprit d'Odile.
    m.objets['cle_garde_manger']['proprietaire'] = id
    if payeur == 'joueur':
        with patch.object(Monde, 'd20', return_value=20):
            assert engager(m, 'joueur', id, c, 10) == 'accepte'
    else:
        agendas.prendre(m, id, {'condition': c, 'pour': autre, 'minute': m.data['minutes']})
    m, _ = vivre(m, 2)
    assert m.objets['garde_manger']['verrouillee']
    m.objets['cle_garde_manger'].update(lieu=id, proprietaire=id)
    m.objets['garde_manger']['proprietaire'] = id
    m.objets['odile']['profil']['pulsions'] = []
    lire(m, 'odile')['pulsions'] = []
    croire(m, id, 'cle_garde_manger', 'lieu', id, 'vu', salle=None, case=None)
    m.objets['vivres'].update(lieu='garde_manger', proprietaire=id)
    percevoir_tous(m)
    croire(m, id, 'vivres', 'lieu', 'garde_manger', 'vu', salle=None, case=None)
    return m, id, payeur or autre, c


class ServiceNonDefaitTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_cas_reel_217_bloc_decoupe_et_depart_cru(self):
        initial = cas_217()  # Capture réelle à l'instant 4584, allumage à 7 min.
        bloc, _ = vivre(self.recharge(initial.copier()), 3)
        decoupe, _ = vivre(self.recharge(initial.copier()), 1)
        decoupe, _ = vivre(self.recharge(decoupe), 2)
        self.assertEqual(bloc.data, decoupe.data)
        m = self.recharge(bloc)
        gestes = [x for x in m.data['chronique'] if x['pnj'] == 'brune' and x['nature'] == 'geste']
        self.assertTrue(any('allume la torche' in x['texte'] for x in gestes))
        self.assertFalse(any('éteint la torche' in x['texte'] for x in gestes))
        self.assertTrue(m.objets['torche']['allume'])
        self.assertIn({'objet': 'torche', 'allume': True}, services_proteges(m, 'brune'))
        # Partir réellement, sans que Brune l'apprenne, ne libère pas le service.
        m.objets['mael']['lieu'] = 'chambre_cloche'
        self.assertTrue(services_proteges(m, 'brune'))
        croire(m, 'brune', 'mael', 'lieu', 'chambre_cloche', 'vu', salle='chambre_cloche', case=None)
        m = self.recharge(m)
        lire(m, 'brune')['intention'] = None
        menager_flamme(m, 'brune', m.data['minutes'])
        self.assertEqual(lire(m, 'brune')['intention']['plan'][0]['operation'], 'eteindre')
        m, _ = vivre(m, 1)
        self.assertFalse(self.recharge(m).objets['torche']['allume'])

    def test_serrure_promise_et_payee_par_joueur(self):
        for payeur in (None, 'joueur'):
            with self.subTest(payeur=payeur):
                m, id, autre, c = serrure(payeur)
                m = self.recharge(m)
                lire(m, id)['memoire'] = []  # La trace ne dépend pas du souvenir borné.
                self.assertIn(c, services_proteges(m, id))
                # Même but et mêmes moyens ; seule la croyance du départ change.
                cible = {'objet': 'vivres', 'lieu': 'dortoir'}
                self.assertIsNone(planification.planifier_pulsion(m, id, cible))
                # Le besoin privé du bénéficiaire n'est jamais lu.
                if autre != 'joueur':
                    m.objets[autre]['profil']['pulsions'] = []
                    lire(m, autre)['pulsions'] = []
                    lire(m, autre)['intention'] = None
                    self.assertIn(c, services_proteges(m, id))
                croire(m, id, autre, 'lieu', 'dortoir', 'vu', salle='dortoir', case=None)
                m = self.recharge(m)
                plan = planification.planifier_pulsion(m, id, cible)
                self.assertIsNotNone(plan)
                self.assertTrue(any(g['operation'] == 'deverrouiller' for g in plan[1]))
                lire(m, id)['intention'] = {'but': plan[0], 'plan': plan[1], 'motif': 'devoir',
                                          'depuis': m.data['minutes'], 'attente': 0}
                m.objets[id]['profil']['pulsions'] = [{'besoin': 'devoir', 'condition': cible}]
                lire(m, id)['pulsions'] = []
                lire(m, id)['besoins']['devoir'] = 90
                m, _ = vivre(m, 4)
                self.assertFalse(self.recharge(m).objets['garde_manger']['verrouillee'])

    def test_etat_cesse_sans_entretien_ni_rupture_et_trace_validee(self):
        m, id, autre, c = serrure()
        avant = copy.deepcopy(lire(m, id)['relations'])
        # Un tiers, ou le bénéficiaire, défait l'état : constat ordinaire.
        m.objets['garde_manger'].update(verrouillee=False, ouverte=True)
        croire(m, id, 'garde_manger', 'verrouillee', False, 'vu')
        m = self.recharge(m)
        self.assertNotIn(c, services_proteges(m, id))
        self.assertEqual(lire(m, id)['relations'], avant)
        self.assertFalse(agendas.en_cours(m, id))
        self.assertFalse(m.data.get('dettes'))
        # Revenir à l'état réussi ne ressuscite pas une protection terminée.
        m.objets['garde_manger'].update(verrouillee=True, ouverte=False)
        croire(m, id, 'garde_manger', 'verrouillee', True, 'vu')
        self.assertNotIn(c, services_proteges(self.recharge(m), id))
        m.data['services_rendus'].append({'de': id, 'pour': autre, 'condition': {'objet': 'inconnu', 'allume': True}})
        with self.assertRaisesRegex(ErreurMonde, 'Trace de service'):
            m.verifier()

    def test_combustible_epuise_ne_rouvre_pas_la_parole(self):
        m, _ = vivre(cas_217(), 1)
        self.assertTrue(m.objets['torche']['allume'])
        self.assertIn({'objet': 'torche', 'allume': True}, services_proteges(m, 'brune'))
        # Épuisement par l'horloge, sans geste d'extinction de la prestataire.
        m.objets['torche']['combustible'] = 1
        m = self.recharge(m)
        m, _ = vivre(m, 1)
        m = self.recharge(m)
        self.assertFalse(m.objets['torche']['allume'])
        self.assertNotIn({'objet': 'torche', 'allume': True}, services_proteges(m, 'brune'))
        self.assertFalse(any(x['condition'] == {'objet': 'torche', 'allume': True}
                             for x in agendas.en_cours(m, 'brune')))
        self.assertFalse(any(s['type'] == 'engagement_abandonne' and s.get('pour') == 'mael'
                             for s in lire(m, 'brune')['memoire']))
        self.assertFalse(any(x['pnj'] == 'brune' and 'éteint la torche' in x['texte']
                             for x in m.data['chronique']))

    def test_resultat_protege_avant_constat_de_cloture(self):
        m = self.recharge(cas_217())
        self.assertFalse(m.data.get('services_rendus'))
        self.assertTrue(agendas.en_cours(m, 'brune'))
        menager_flamme(m, 'brune', m.data['minutes'])
        self.assertFalse(any(x['operation'] == 'eteindre' for x in lire(m, 'brune')['intention']['plan']))
        m, _ = vivre(m, 1)
        m = self.recharge(m)
        gestes = [x['texte'] for x in m.data['chronique'] if x['pnj'] == 'brune' and x['nature'] == 'geste']
        self.assertTrue(any('allume la torche' in x for x in gestes))
        self.assertFalse(any('éteint la torche' in x for x in gestes))

    def test_filtre_porte_franchie_et_objet_pose(self):
        m, id, autre, _ = serrure()
        porte = 'porte_cellier'
        m.objets[porte].update(ouverte=False, verrouillee=True)
        m.objets['cle_garde_manger']['ouvre'].append(porte)
        croire(m, id, porte, 'etat', {'ouverte': False}, 'vu')
        croire(m, id, porte, 'verrouillee', True, 'vu')
        croire(m, id, autre, 'lieu', 'cuisine', 'vu', salle='cuisine', case=None)
        c = {'objet': porte, 'verrouillee': True}
        retenir_service(m, id, {'condition': c, 'pour': autre})
        m = self.recharge(m)
        cible = {'objet': id, 'lieu': 'cuisine'}
        self.assertIsNone(planification.planifier_pulsion(m, id, cible))
        croire(m, id, autre, 'lieu', 'dortoir', 'vu', salle='dortoir', case=None)
        m = self.recharge(m)
        self.assertIsNotNone(planification.planifier_pulsion(m, id, cible))
        # Une clé posée pour autrui reste manipulable à son départ, mais ne
        # peut être reprise avant. Même filtre, sans interdire tout l'objet.
        cle = 'cle_garde_manger'
        m.objets[cle]['lieu'] = 'cellier'
        croire(m, id, cle, 'lieu', 'cellier', 'vu', salle='cellier', case=None)
        croire(m, id, autre, 'lieu', 'cellier', 'vu', salle='cellier', case=None)
        retenir_service(m, id, {'condition': {'objet': cle, 'lieu': 'cellier'}, 'pour': autre})
        m = self.recharge(m)
        self.assertIsNone(planification.planifier_pulsion(m, id, cible))
        croire(m, id, autre, 'lieu', 'dortoir', 'vu', salle='dortoir', case=None)
        self.assertIsNotNone(planification.planifier_pulsion(self.recharge(m), id, cible))


if __name__ == '__main__':
    unittest.main()
