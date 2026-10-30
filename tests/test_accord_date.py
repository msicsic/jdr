"""E4 : termes typés, marché atomique, état et paroles après recharge."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, echanges
from donjon.biens import bourse, solder
from donjon.emissions import pnj
from donjon.esprits import lire, croire
from donjon.monde import ErreurMonde, Monde
from donjon.paroles import preparer_parole
from donjon.propositions import SCHEMA, verifier
from donjon.rendu import regarder, decrire_comptes
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_lampes_parts import nuit_noire
from tests.test_realisation_datee import geste
from tests.test_tache_promise_recours import feu, reserve
from tests.test_tensions import recharger, vivre


def huile(scenario='auberge'):
    q, b, source, lot, salle = (('odile', 'joss', 'lanterne_etable', 'pot_huile', 'etable')
                               if scenario == 'auberge' else
                               ('gaspard', 'remy', 'lampe_remy', 'bidon_huile', 'reserve'))
    m = nuit_noire(scenario, b, q, source, lot, salle)
    m.data['finances_pnj'][b] = 50
    return m, b, q, {'type': 'part', 'objet': lot, 'limite': 6000}, {'type': 'pieces', 'montant': 3}


def travail(fabrique=feu):
    m, q, b, c = fabrique()
    m.data['finances_pnj'][b] = 50
    m.objets[q]['profil']['valeurs']['honnetete'] = 100
    return m, b, q, {'type': 'tache', 'condition': c, 'limite': 6000}, {'type': 'pieces', 'montant': 10}


class AccordDateTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(regarder(n), regarder(m))
        self.assertEqual(decrire_comptes(n), decrire_comptes(m))
        self.assertEqual(scene_percue(n), scene_percue(m))
        self.assertEqual(pnj(n), pnj(m))
        return n

    def conclure(self, m, b, q, t, prix):
        with patch.object(Monde, 'd20', return_value=20):
            r = echanges.proposer(m, b, q, t, prix)
        self.assertIsNone(r['cause'], r)
        return self.recharge(m)

    def test_acceptation_exacte_et_double_soumission_sans_second_paiement(self):
        for fabrique in (huile, lambda: huile('mine'), travail, lambda: travail(reserve)):
            m, b, q, t, prix = fabrique()
            fonds = bourse(m, b), bourse(m, q)
            m = self.conclure(m, b, q, t, prix)
            x, = agendas.en_cours(m, q)
            self.assertEqual(agendas.reference_temporelle(x)['limite'], t['limite'])
            self.assertEqual((bourse(m, b), bourse(m, q)), (fonds[0] - prix['montant'], fonds[1] + prix['montant']))
            avant = copy.deepcopy(m.data)
            self.assertEqual(echanges.proposer(m, b, q, t, prix)['cause'], 'deja')
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_refus_ordinaire_aucune_reservation_ni_avance(self):
        for fabrique in (huile, travail):
            m, b, q, t, prix = fabrique()
            lire(m, q)['relations'][b]['confiance'] = 0
            avant = copy.deepcopy(m.data)
            self.assertEqual(echanges.proposer(m, b, q, t, prix)['cause'], 'mefiance')
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_delai_impossible_et_indetermine_ne_sont_jamais_effaces(self):
        for fabrique in (huile, lambda: huile('mine'), travail):
            m, b, q, t, prix = fabrique()
            for incertain in (False, True):
                n = m.copier()
                terme = copy.deepcopy(t)
                if incertain:
                    if t['type'] == 'part':
                        lire(n, q)['croyances'][b].pop('lieu', None)
                    else:
                        croire(n, q, 'bois', 'etat', {'disponible': False}, 'vu')
                else:
                    terme['limite'] = 1
                avant = copy.deepcopy(n.data)
                with patch('donjon.echanges.jet_persuasion') as jet:
                    r = echanges.proposer(n, b, q, terme, prix)
                self.assertEqual(r['cause'], 'impossible', r)
                self.assertEqual(r['delai']['verdict'], 'indetermine' if incertain else 'impossible')
                self.assertIn('sans limite' if incertain else 'limite', r['delai']['attendu'])
                jet.assert_not_called()
                self.assertEqual(n.data, avant)
                self.recharge(n)

    def test_brouillon_jugement_et_abandon_sans_effet(self):
        for fabrique in (huile, travail):
            m, b, q, t, prix = fabrique()
            avant = copy.deepcopy(m.data)
            r = echanges.evaluer_proposition(m, b, q, t, prix)
            self.assertIsNone(r['cause'])
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_clauses_non_portees_refus_precis_sans_effet(self):
        m, b, q, t, prix = huile()
        clauses = [(t, {**prix, 'limite': 6000}, 'contrepartie.limite'),
                   (t, {**prix, 'paiement_futur': True}, 'contrepartie.paiement_futur'),
                   ({'type': 'objet', 'objet': t['objet'], 'limite': 6000}, prix, 'demande.limite'),
                   ({'type': 'tache', 'condition': {'objet': q, 'proteger': True, 'echeance': 10},
                     'limite': 6000}, prix, 'demande.condition'),
                   ({'type': 'tache', 'condition': {'objet': 'lanterne_etable', 'allume': True, 'periode': 10},
                     'limite': 6000}, prix, 'demande.condition'),
                   (t, {'type': 'rien'}, 'contrepartie.type')]
        clauses += [({**t, 'limite': v}, prix, 'demande.limite') for v in (None, True, -1, 1.5, 'demain')]
        for demande, contre, champ in clauses:
            avant = copy.deepcopy(m.data)
            with self.assertRaises(ErreurMonde) as err:
                echanges.proposer(m, b, q, demande, contre)
            self.assertIn(champ, err.exception.attendu)
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_part_tache_reelles_a_temps_et_retard_remboursement_unique(self):
        for fabrique in (huile, lambda: huile('mine'), lambda: travail(reserve)):
            for t in (5999, 6000, 6001):
                m, b, q, terme, prix = fabrique()
                fonds = bourse(m, b), bourse(m, q)
                m = self.conclure(m, b, q, terme, prix)
                x, = agendas.en_cours(m, q)
                if terme['type'] == 'part':
                    self.assertTrue(geste(m, q, 'prendre', x['condition']['objet']))
                else:
                    self.assertTrue(geste(m, q, 'fermer', x['condition']['objet']))
                ecouler(m, t)
                if terme['type'] == 'part':
                    self.assertTrue(geste(m, q, 'remettre', b, x['condition']['objet']))
                    self.assertEqual(m.objets[x['condition']['objet']]['lieu'], b)
                else:
                    self.assertTrue(geste(m, q, 'verrouiller', 'garde_manger', 'cle_garde_manger'))
                    self.assertTrue(m.objets['garde_manger']['verrouillee'])
                m = self.recharge(m)
                issue, = agendas.issues_temporelles(m)
                self.assertEqual(issue['verdict'], 'tenue_a_temps' if t <= 6000 else 'en_retard')
                self.assertEqual(issue['realisation'], t if t <= 6000 else None)
                avant = copy.deepcopy(m.data)
                self.assertEqual(echanges.proposer(m, b, q, terme, prix)['cause'], 'deja')
                self.assertEqual(m.data, avant)
                for _ in range(2):
                    agendas.echoir(m, q)
                    solder(m, [])
                    m = self.recharge(m)
                self.assertEqual((bourse(m, b), bourse(m, q)), fonds if t > 6000 else
                                 (fonds[0] - prix['montant'], fonds[1] + prix['montant']))
                self.assertEqual(len(agendas.issues_temporelles(m)), 1)

    def test_entree_joueur_parole_complete_et_laps_decoupe(self):
        from tests.test_parts_achetees import antichambre_du_banc
        m = antichambre_du_banc()
        demande = {'type': 'part', 'objet': 'planches', 'limite': 6000}
        p = {'personnage': 'aubin', 'replique': 'Trois pièces pour une planche livrée avant la minute dix.',
             '_intention': 'je propose cet échange', 'contenu': [{'type': 'proposition', 'demande': demande,
              'contrepartie': {'type': 'pieces', 'montant': 3}}]}
        with patch.object(Monde, 'd20', return_value=20):
            m, rapport = preparer_parole(m, p)
        mots = pnj(m)[-1]['texte']
        self.assertIn('minute de jeu 10', mots)
        self.assertIn('10 minutes restantes', mots)
        self.assertIn('payées maintenant', mots)
        self.assertIn("Tu m'as payé 3 pièces", mots)
        self.assertIn('planches', mots)
        self.assertTrue(rapport['emissions'])
        from donjon.comptes_parles import reponse
        self.assertIn(pnj(m)[-1]['rendu_public'], reponse(rapport)['texte'])
        self.assertIn('minute de jeu 10', decrire_comptes(m))
        m = self.recharge(m)
        a, la = vivre(m.copier(), 3)
        b, lb = m.copier(), []
        for _ in range(3):
            b, lignes = vivre(b, 1)
            lb.extend(lignes)
            b = self.recharge(b)
        self.assertEqual(a.data, b.data)
        self.assertEqual(la, lb)
        self.assertEqual(agendas.issues_temporelles(a)[0]['verdict'], 'tenue_a_temps')
        self.assertEqual(a.objets['planches_1']['lieu'], 'joueur')
        self.recharge(a)

    def test_schema_et_validation_partagent_les_termes_dates(self):
        import jsonschema
        for fabrique in (huile, travail):
            m, b, q, t, prix = fabrique()
            contenu = {'type': 'proposition', 'demande': t, 'contrepartie': prix}
            jsonschema.validate(contenu, SCHEMA)
            verifier(m, contenu, proposant=b)

    def test_recharge_refuse_un_accord_corrompu(self):
        m, b, q, t, prix = huile()
        m = self.conclure(m, b, q, t, prix)
        for champ, valeur in (('limite', 7000), ('montant', 4), ('auditeur', []), ('proposant', q)):
            n = m.copier()
            accord = n.data['esprits'][q]['engagements'][0]['accord_initial']
            if champ == 'limite':
                accord['demande'][champ] = valeur
            elif champ == 'montant':
                accord['contrepartie'][champ] = valeur
            else:
                accord[champ] = valeur
            with self.assertRaises(ErreurMonde) as err:
                recharger(n)
            self.assertIn('accord_initial', err.exception.attendu)

    def test_offre_inversee_et_attente_du_joueur_sans_paiement(self):
        from tests.test_parts_achetees import antichambre_du_banc
        m = antichambre_du_banc()
        demande = {'type': 'pieces', 'montant': 3}
        service = {'type': 'part', 'objet': 'planches', 'limite': 6000}
        from donjon.deplacement_objet import deplacer
        deplacer(m, 'planches', 'aubin')
        croire(m, 'aubin', 'planches', 'lieu', 'aubin', 'vu', salle=None, case=None)
        avant = copy.deepcopy(m.data)
        self.assertEqual(echanges.proposer(m, 'aubin', 'joueur', demande, service)['cause'], 'attente')
        self.assertEqual(m.data, avant)
        m = self.recharge(m)
        r = echanges.proposer(m, 'aubin', 'joueur', demande, service, accord_joueur=True)
        self.assertIsNone(r['cause'], r)
        issue, = agendas.issues_temporelles(m)
        self.assertEqual(agendas.reference_temporelle(issue['engagement'])['limite'], 6000)
        self.assertEqual(issue['verdict'], 'tenue_a_temps')
        m = self.recharge(m)
        apres = copy.deepcopy(m.data)
        self.assertEqual(echanges.proposer(m, 'aubin', 'joueur', demande, service,
                                         accord_joueur=True)['cause'], 'deja')
        self.assertEqual(m.data, apres)

    def test_paiement_sur_source_convenue(self):
        from tests.test_parts_achetees import antichambre_du_banc
        m = antichambre_du_banc()
        m.objets['bourse_e4'] = {**copy.deepcopy(m.objets['cloche']),
                                'id': 'bourse_e4', 'type': 'objet', 'nom': 'bourse de cuivre', 'mobile': True,
                                'lieu': 'joueur', 'proprietaire': 'joueur', 'pieces': 8}
        m.data['connus'].append('bourse_e4')
        terme = {'type': 'part', 'objet': 'planches', 'limite': 6000}
        prix = {'type': 'pieces', 'objet': 'bourse_e4', 'montant': 3}
        fonds = m.joueur['or']
        m = self.conclure(m, 'joueur', 'aubin', terme, prix)
        self.assertEqual(m.joueur['or'], fonds)
        self.assertEqual(m.objets['bourse_e4']['pieces'], 5)
        self.assertIn('bourse de cuivre', decrire_comptes(m))

    def test_refus_date_entendu_et_passe_ne_recalcule_pas_la_limite(self):
        from tests.test_parts_achetees import antichambre_du_banc
        m = antichambre_du_banc()
        p = {'personnage': 'aubin', 'replique': 'Une planche immédiatement pour trois pièces.',
             '_intention': 'je propose cet échange', 'contenu': [{'type': 'proposition',
              'demande': {'type': 'part', 'objet': 'planches', 'limite': 1},
              'contrepartie': {'type': 'pieces', 'montant': 3}}]}
        or_avant = m.joueur['or']
        for temps, cause in ((0, 'delai_trop_court'), (2, 'limite_passee')):
            ecouler(m, temps)
            m, rapport = preparer_parole(m, p)
            self.assertIn('Je refuse cet échange', pnj(m)[-1]['texte'])
            self.assertIn('minute de jeu 0 et 0,1 seconde', pnj(m)[-1]['texte'])
            self.assertEqual(m.joueur['or'], or_avant)
            self.assertFalse(agendas.en_cours(m, 'aubin'))
            resolution = pnj(m)[-1]['evenement']['resolutions_comptables'][0]['resolution']
            self.assertEqual(resolution['delai']['cause'], cause)
            self.assertIn('attendu', resolution['delai'])
            self.assertNotIn('attendu', str(rapport))
            m = self.recharge(m)

    def test_expiration_par_ordonnanceur_identique_en_bloc_et_decoupee(self):
        from donjon.pnj import avancer
        for fabrique in (huile, lambda: travail(reserve)):
            m, b, q, terme, prix = fabrique()
            m = self.conclure(m, b, q, terme, prix)
            for e in m.data['esprits'].values():
                e['libre'], e['eveil'], e['veille'] = 100000, None, None
            def jouer(pas):
                n, lignes = m.copier(), []
                for dt in pas:
                    ecouler(n, dt)
                    avancer(n, 0, lignes, dixiemes=dt)
                    n = self.recharge(n)
                return n, lignes
            a, la = jouer([6002])
            z, lz = jouer([5999, 1, 1, 1])
            self.assertEqual(a.data, z.data)
            self.assertEqual(la, lz)
            self.assertEqual(agendas.issues_temporelles(a)[0]['cloture'], 6001)

    def test_part_du_joueur_remise_presente_ou_duree_future_indeterminee(self):
        from tests.test_propositions import scene
        for portee in (True, False):
            m = scene()
            m.objets['vivres'].update(lieu='joueur' if portee else 'antichambre', proprietaire='joueur')
            m.data['finances_pnj']['marchand'] = 50
            t = {'type': 'part', 'objet': 'vivres', 'limite': 6000}
            prix = {'type': 'pieces', 'montant': 3}
            avant = copy.deepcopy(m.data)
            r = echanges.proposer(m, 'marchand', 'joueur', t, prix, accord_joueur=True)
            if portee:
                self.assertIsNone(r['cause'], r)
                issue, = agendas.issues_temporelles(m)
                self.assertEqual(issue['titulaire'], 'joueur')
                self.assertEqual(issue['realisation'], 0)
                self.assertEqual(issue['verdict'], 'tenue_a_temps')
                self.assertFalse(agendas.en_cours(m, 'joueur'))
                self.assertEqual(m.joueur['or'], avant['joueur']['or'] + 3)
                m = self.recharge(m)
                apres = copy.deepcopy(m.data)
                self.assertEqual(echanges.proposer(m, 'marchand', 'joueur', t, prix,
                                                 accord_joueur=True)['cause'], 'deja')
                self.assertEqual(m.data, apres)
            else:
                self.assertEqual(r['delai']['verdict'], 'indetermine')
                self.assertEqual(m.data, avant)
            self.recharge(m)


if __name__ == '__main__':
    unittest.main()
