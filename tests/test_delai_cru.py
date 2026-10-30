"""E3 : un délai se juge sur le devis complet du seul contractant."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, echanges, planification as p
from donjon.esprits import croire, lire
from donjon.biens import bourse
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler, instant
from tests.test_lampes_parts import nuit_noire
from tests.test_tache_promise_recours import feu
from tests.test_tensions import recharger


def huile(scenario='auberge'):
    if scenario == 'auberge':
        q, b, source, lot, salle = 'odile', 'joss', 'lanterne_etable', 'pot_huile', 'etable'
    else:
        q, b, source, lot, salle = 'gaspard', 'remy', 'lampe_remy', 'bidon_huile', 'reserve'
    m = nuit_noire(scenario, b, q, source, lot, salle)
    m.data['finances_pnj'][b] = 5
    # Entrée réelle du marché commun : la part et son obligation existent.
    with patch.object(Monde, 'd20', return_value=20):
        assert echanges.demander(m, b, q, lot, prix=1, remettre_part=True) == 'vendu'
    x, = agendas.en_cours(m, q)
    return m, q, b, x['condition']


class DelaiCruTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(regarder(n), regarder(m))
        self.assertEqual(scene_percue(n), scene_percue(m))
        self.assertEqual(agendas.promesses_visibles(n), agendas.promesses_visibles(m))
        return n

    def juger(self, m, q, b, c, limite=6000):
        avant = copy.deepcopy(m.data)
        with patch.object(p, 'VERIFIER', True):
            r = echanges.juger_delai(m, q, c, b, limite)
        self.assertEqual(m.data, avant)  # Ni paiement, ni parole, ni engagement.
        n = self.recharge(m)
        with patch.object(p, 'VERIFIER', True):
            self.assertEqual(echanges.juger_delai(n, q, c, b, limite), r)
        if r['verdict'] != 'credible':
            self.assertIn('limite', r['attendu'])
            self.assertIn(str(limite), r['attendu'])
            self.assertTrue(r['cause'])
            self.assertTrue(r['message'])
        return r

    def test_huile_et_feu_trois_verdicts_date_inclusive(self):
        for fabrique in (huile, lambda: huile('mine'), feu):
            with self.subTest(fabrique=fabrique):
                m, q, b, c = fabrique()
                r = self.juger(m, q, b, c)
                self.assertEqual(r['verdict'], 'credible')
                fin = r['estimation']
                self.assertGreater(fin, instant(m))
                self.assertEqual(self.juger(m, q, b, c, fin)['verdict'], 'credible')
                court = self.juger(m, q, b, c, fin - 1)
                self.assertEqual(court['cause'], 'delai_trop_court')
                if 'remettre' in c:
                    lire(m, q)['croyances'][b].pop('lieu', None)
                else:
                    croire(m, q, 'bois', 'etat', {'disponible': False}, 'vu')
                incertain = self.juger(m, q, b, c)
                self.assertEqual(incertain['verdict'], 'indetermine')
                self.assertIsNone(incertain['duree'])
                self.assertIn('sans limite', incertain['attendu'])

    def test_changements_caches_et_savoir_prive_ne_changent_pas_le_devis(self):
        for fabrique in (huile, lambda: huile('mine'), feu):
            m, q, b, c = fabrique()
            if 'allume' in c:
                # Branche de l'ancien devis qui lisait l'esprit du payeur.
                lire(m, q)['croyances'][c['objet']]['etat']['source'] = 'savoir'
            r = self.juger(m, q, b, c)
            n = m.copier()
            lire(n, b)['croyances'].clear()
            if 'remettre' in c:
                salle = 'dortoir' if b == 'joss' else 'bureau'
                from donjon.geometrie import cases
                occupes = {tuple(o['position']) for o in n.objets.values()
                           if o.get('lieu') == salle and o.get('position')}
                position = next(pos for pos in sorted(cases(n.data['salles'][salle])) if pos not in occupes)
                n.objets[b].update(lieu=salle, position=list(position), position_salle=salle)
                n.objets[c['objet']]['charges'] = 0
            else:
                n.objets['bois']['charges'] = 0
                croire(n, b, c['objet'], 'etat', {'allume': False, 'charge': True}, 'vu')
            self.assertEqual(self.juger(n, q, b, c), r)

    def test_changement_connu_perime_le_cache_puis_retour_aux_moyens(self):
        for fabrique in (huile, lambda: huile('mine'), feu):
            m, q, b, c = fabrique()
            r = self.juger(m, q, b, c)
            croyances = copy.deepcopy(lire(m, q)['croyances'])
            if 'remettre' in c:
                lire(m, q)['croyances'][b].pop('lieu', None)
            else:
                croire(m, q, 'bois', 'etat', {'disponible': False}, 'vu')
            self.assertNotEqual(self.juger(m, q, b, c), r)
            lire(m, q)['croyances'] = croyances
            self.assertEqual(self.juger(m, q, b, c), r)

    def test_prix_pondere_et_duree_physique_distincts(self):
        m, q, b, c = huile()
        r = self.juger(m, q, b, c)
        self.assertNotAlmostEqual(r['cout'], r['duree'])
        # Le seuil dépend du temps physique, pas du coût social/moral.
        self.assertEqual(self.juger(m, q, b, c, r['estimation'])['verdict'], 'credible')

    def test_prefixe_coupe_ne_certifie_pas_la_realisation_complete(self):
        m, q, b, c = feu()
        # Demander du bois au bénéficiaire : la suite suppose une fourniture.
        m.objets['bois'].update(lieu=b, proprietaire=b)
        croire(m, q, 'bois', 'lieu', b, 'vu', salle='echoppe', case=[4, 3])
        r = self.juger(m, q, b, c)
        self.assertEqual(r['verdict'], 'indetermine')
        durees = []
        devis = p.devis_pulsion(m, q, c, b, duree=durees)
        self.assertIsNotNone(devis)
        self.assertEqual(durees, [None])

    def test_laps_decoupe_et_limite_absolue_non_deplacee(self):
        for fabrique in (huile, feu):
            m, q, b, c = fabrique()
            r = self.juger(m, q, b, c)
            limite = r['estimation']
            a, z = m.copier(), m.copier()
            ecouler(a, 20)
            for _ in range(4):
                ecouler(z, 5)
                z = self.recharge(z)
            self.assertEqual(a.data, z.data)
            ra, rz = (self.juger(n, q, b, c, limite) for n in (a, z))
            self.assertEqual(ra, rz)
            self.assertEqual(ra['cause'], 'delai_trop_court')
            self.assertEqual(ra['limite'], limite)

    def test_entree_jugement_effet_reel_comptes_paroles_et_recharge(self):
        from tests.test_realisation_datee import geste
        from tests.test_tensions import vivre
        for fabrique in (huile, lambda: huile('mine'), feu):
            m, q, b, c = fabrique()
            jugement = self.juger(m, q, b, c)
            self.assertEqual(jugement['verdict'], 'credible')
            if not agendas.en_cours(m, q):
                with patch.object(Monde, 'd20', return_value=20):
                    self.assertEqual(echanges.engager(m, b, q, c, 1), 'accepte')
            x, = agendas.en_cours(m, q)
            agendas.retirer_proposition(m, q, x)
            agendas.prendre(m, q, x, limite=jugement['limite'])
            comptes = bourse(m, q), bourse(m, b)
            m = self.recharge(m)
            if 'remettre' in c:
                source = 'lanterne_etable' if b == 'joss' else 'lampe_remy'
                combustible = m.objets[source]['combustible']
                self.assertTrue(geste(m, q, 'prendre', c['objet']))
                ecouler(m, 200)
                self.assertTrue(geste(m, q, 'remettre', b, c['objet']))
                self.assertEqual(m.objets[c['objet']]['lieu'], b)
                self.assertEqual(m.objets[source]['combustible'], combustible)
            else:
                m, mots = vivre(m, 1, jet=20)
                self.assertGreater(m.objets[c['objet']]['combustible'], 20)
                self.assertTrue(any('alimente' in mot for mot in mots))
            m = self.recharge(m)
            issue, = agendas.issues_temporelles(m)
            self.assertEqual(issue['verdict'], 'tenue_a_temps')
            self.assertLessEqual(issue['realisation'], jugement['limite'])
            self.assertEqual((bourse(m, q), bourse(m, b)), comptes)
            self.assertEqual(agendas.en_cours(m, q), [])

    def test_impossibilite_crue_et_limite_passee_causes_distinctes(self):
        m, q, b, c = huile()
        m.objets[c['objet']]['lieu'] = 'dortoir'
        lire(m, q)['croyances'].pop(c['objet'], None)
        self.assertEqual(self.juger(m, q, b, c)['cause'], 'moyens_insuffisants')
        ecouler(m, 2)
        self.assertEqual(self.juger(m, q, b, c, 1)['cause'], 'limite_passee')

    def test_limite_mal_formee_et_prestations_non_portees(self):
        m, q, b, c = feu()
        for limite in (None, True, -1, 1.5, 'demain'):
            with self.subTest(limite=limite), self.assertRaises(ErreurMonde) as err:
                echanges.juger_delai(m, q, c, b, limite)
            self.assertIn('limite', err.exception.attendu)
        with self.assertRaises(ErreurMonde) as err:
            echanges.juger_delai(m, q, {'objet': c['objet'], 'rendre': b}, b, 6000)
        self.assertIn('condition', err.exception.attendu)

    def test_recherche_bornee_ne_devient_pas_impossibilite(self):
        m, q, b, c = feu()
        chercher = p.chercher

        def borner(*args, **kw):
            return chercher(*args, **{**kw, 'noeuds': 1})

        with patch.object(p, 'chercher', side_effect=borner):
            r = self.juger(m, q, b, c)
        self.assertEqual(r['verdict'], 'indetermine')
        self.assertEqual(r['cause'], 'duree_indeterminee')


if __name__ == '__main__':
    unittest.main()
