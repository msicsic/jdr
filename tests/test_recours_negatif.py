"""Recours négatifs des captures 208 : valeurs retenues, monde et rendu rechargés.

Captures avant le devis hypothétique d'Odon/Rémy à la minute 1 du lot 202.
La seule charge temporaire ajoutée pour ce devis est retirée des fixtures.
"""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import memoire, pnj_propositions as p
from donjon.esprits import lire, croire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger


class RecoursNegatifTests(unittest.TestCase):
    def scene(self, qui):
        f = Path(__file__).parent / f'data/recours-228-{qui}.json.gz'
        m = recharger(Monde(json.loads(gzip.decompress(f.read_bytes()))))
        if qui == 'remy':
            # La capture contient encore une offre monétaire possible. Épuiser
            # ces fonds isole le négatif du même service de fermeture ; le
            # préfixe de demande ordinaire a déjà eu sa chance.
            m.data['finances_pnj'][qui] = 0
            lire(m, qui)['intention']['plan'] = []
        return recharger(m)

    def appeler(self, m, qui):
        intention = lire(m, qui)['intention']
        # Le devis n'acquitte l'effort que dans un choix explicitement achevé.
        with memoire.choix_complet(m, qui):
            return p.recours(m, qui, intention['motif'], intention['plan'])

    def stable(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_captures_reelles_devis_negatif_retenu_sans_delai(self):
        for qui in ('odon', 'remy'):
            with self.subTest(qui=qui):
                m = self.scene(qui)
                avant = copy.deepcopy(m.data)
                with patch.object(p, '_contreparties', wraps=p._contreparties) as offres:
                    self.assertIsNone(self.appeler(m, qui))
                    self.assertEqual(offres.call_count, 1)
                    m = self.stable(m)
                    self.assertIsNone(self.appeler(m, qui))
                    self.assertEqual(offres.call_count, 1)
                    # Le temps et la date d'un regard confirmant le même fait
                    # ne constituent pas des moyens nouveaux.
                    # Si les liens évoluent naturellement, ce sont bien des
                    # entrées nouvelles ; isoler ici les dates d'observation.
                    from donjon import relations
                    liens = {q: relations.axes(m, qui, q) for q in relations.connus(m, qui)}
                    m.data['minutes'] += 60
                    for d in lire(m, qui)['croyances'].values():
                        for c in d.values():
                            c['minute'] = m.data['minutes']
                    self.appeler(m, qui)
                    apres = {q: relations.axes(m, qui, q) for q in relations.connus(m, qui)}
                    self.assertEqual(offres.call_count, 1 if liens == apres else 2)
                    # Le temps vécu brut est soldé par le moteur même lorsque
                    # ni besoin effectif ni caractéristique ne change.
                    avant_compte = offres.call_count
                    m.objets[qui]['corps']['repas'] += 1
                    m.objets[qui]['corps']['veille'] += 1
                    self.appeler(m, qui)
                    self.assertEqual(offres.call_count, avant_compte)
                    m.objets[qui]['corps']['repas'] -= 1
                    m.objets[qui]['corps']['veille'] -= 1
                self.assertEqual(avant['objets'], m.data['objets'])
                self.assertEqual(avant['finances_pnj'], m.data['finances_pnj'])
                self.stable(m)

    def test_le_devis_lui_meme_n_est_pas_redemande(self):
        from donjon import echanges
        for qui in ('odon', 'remy'):
            with self.subTest(qui=qui):
                m = self.scene(qui)
                with patch.object(echanges, '_devis_proposition', wraps=echanges._devis_proposition) as devis:
                    self.assertIsNone(self.appeler(m, qui))
                    premier = devis.call_count
                    self.assertGreater(premier, 0)
                    for _ in range(4):
                        m = self.stable(m)
                        self.assertIsNone(self.appeler(m, qui))
                    self.assertEqual(devis.call_count, premier)
                    from donjon.corps import vivre
                    vivre(m, qui, 0.01)
                    self.assertIsNone(self.appeler(m, qui))
                    self.assertEqual(devis.call_count, premier)
                    self.stable(m)

    def test_meme_demande_issue_du_plan_et_du_refus_ne_se_recalcule_pas(self):
        from donjon.deliberation import retenir_refus
        m = self.scene('odon')
        retenir_refus(m, 'odon', 'bram', 'demander', 'refus', objet='paie', besoin='agenda')
        with patch.object(p, '_contreparties', wraps=p._contreparties) as offres:
            self.assertIsNone(self.appeler(m, 'odon'))
            self.assertEqual(offres.call_count, 1)
        self.stable(m)

    def test_chaque_entree_changee_rouvre_le_jugement(self):
        for qui in ('odon', 'remy'):
            initial = self.scene(qui)
            self.assertIsNone(self.appeler(initial, qui))
            for variation in ('fonds', 'lien', 'capacite', 'doublon', 'besoin', 'droit', 'acces', 'engagement', 'but'):
                with self.subTest(qui=qui, variation=variation):
                    m = recharger(initial)
                    e = lire(m, qui)
                    autre = next(json.loads(k)[1] for k in e['attentes_bornees']
                                 if k.startswith('["recours_proposition",'))
                    if variation == 'fonds':
                        m.data['finances_pnj'][qui] = m.data['finances_pnj'].get(qui, 5) + 1
                    elif variation == 'lien':
                        from donjon import relations
                        e['relations'].setdefault(autre, relations._nouvelle())['confiance'] += 1
                    elif variation == 'capacite':
                        m.objets[qui]['profil']['capacites'].append('crochetage')
                    elif variation == 'doublon':
                        outil = 'crochets' if qui == 'odon' else 'lampe_remy'
                        m.objets['outil_double'] = {**copy.deepcopy(m.objets[outil]),
                                                   'id': 'outil_double', 'lieu': qui, 'proprietaire': qui}
                        from donjon.esprits import constater_possession
                        constater_possession(m, qui, 'outil_double', 'essai')
                    elif variation == 'besoin':
                        e['besoins']['faim'] = 100
                    elif variation == 'droit':
                        m.data.setdefault('permissions', []).append(
                            dict(objet='cle_paie', de='bram', a=qui, minute=m.data['minutes']))
                    elif variation == 'acces':
                        connu = e['croyances'].get('coffre_paie', {}).get('verrouillee', {}).get('valeur')
                        croire(m, qui, 'coffre_paie', 'verrouillee', not connu, 'essai')
                    elif variation == 'but':
                        e['intention']['but'] = {'type': 'argent'}
                    else:
                        from donjon import agendas
                        agendas.prendre(m, qui, dict(condition={'objet':'coffre_paie', 'verrouillee':True},
                                                    pour='bram', minute=m.data['minutes']))
                    with patch.object(p, '_contreparties', wraps=p._contreparties) as offres:
                        self.appeler(m, qui)
                        self.assertGreater(offres.call_count, 0)
                    self.stable(m)

    def test_memoire_negative_meme_laps_bloc_ou_decoupe(self):
        for qui in ('odon', 'remy'):
            a = self.scene(qui)
            self.assertIsNone(self.appeler(a, qui))
            b = recharger(a)
            a.data['minutes'] += 2
            self.assertIsNone(self.appeler(a, qui))
            for _ in range(2):
                b.data['minutes'] += 1
                self.assertIsNone(self.appeler(b, qui))
                b = self.stable(b)
            self.assertEqual(self.stable(a).data, b.data)
            self.assertEqual(regarder(a), regarder(b))

    def test_quantite_portee_change_meme_si_le_prix_du_lot_est_fixe(self):
        m = self.scene('remy')
        lot = m.objets['vivres_2']
        lot['prix'] = 50  # La valeur du lot ne révèle donc plus sa quantité.
        self.assertIsNone(self.appeler(m, 'remy'))
        lot['portions'] += 1
        with patch.object(p, '_contreparties', wraps=p._contreparties) as offres:
            self.appeler(m, 'remy')
            self.assertGreater(offres.call_count, 0)
        self.stable(m)

    def test_publication_transactionnelle_du_choix_et_annulation(self):
        from donjon import planification
        for qui in ('odon', 'remy'):
            with self.subTest(qui=qui):
                m = self.scene(qui)
                avant = copy.deepcopy(m.data)
                with patch.object(planification, 'VERIFIER', True):
                    with self.assertRaisesRegex(RuntimeError, 'annulation'):
                        with planification.vues_du_choix(m, qui):
                            self.assertIsNone(self.appeler(m, qui))
                            self.assertEqual(m.data, avant)
                            raise RuntimeError('annulation')
                    self.assertEqual(m.data, avant)
                    with memoire.choix_complet(m, qui), planification.vues_du_choix(m, qui):
                        self.assertIsNone(self.appeler(m, qui))
                        self.assertEqual(m.data, avant)
                self.assertNotEqual(lire(m, qui)['attentes_bornees'], avant['esprits'][qui]['attentes_bornees'])
                m = self.stable(m)
                with patch.object(p, '_contreparties', wraps=p._contreparties) as offres:
                    self.assertIsNone(self.appeler(m, qui))
                    self.assertEqual(offres.call_count, 0)

    def test_releve_des_services_expire_sans_cloture_pendant_le_choix(self):
        from donjon import biens, planification
        for qui in ('odon', 'remy'):
            with self.subTest(qui=qui):
                m = self.scene(qui)
                biens.retenir_service(m, qui, {'pour': 'bram',
                    'condition': {'objet': 'lampe_remy', 'allume': True}})
                croire(m, qui, 'lampe_remy', 'etat', {'allume': False, 'charge': True}, 'essai')
                avant = copy.deepcopy(m.data)
                with patch.object(planification, 'VERIFIER', True):
                    with planification.vues_du_choix(m, qui):
                        self.appeler(m, qui)
                        self.assertEqual(m.data, avant)
                self.assertEqual(m.data['services_rendus'], avant['services_rendus'])
                self.stable(m)

    def test_temps_moteur_et_rendu_recharges(self):
        from donjon.pnj import avancer
        for qui in ('odon', 'remy'):
            with self.subTest(qui=qui):
                a = self.scene(qui)
                self.assertIsNone(self.appeler(a, qui))
                b = recharger(a)
                a.data['minutes'] += 2
                avancer(a, 2, [])
                for _ in range(2):
                    b.data['minutes'] += 1
                    avancer(b, 1, [])
                    b = recharger(b)
                self.assertEqual(self.stable(a).data, self.stable(b).data)
                self.assertEqual(regarder(a), regarder(b))
                self.assertEqual(scene_percue(a), scene_percue(b))


if __name__ == '__main__':
    unittest.main()
