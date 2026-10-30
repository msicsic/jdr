"""E1 : métadonnée interne facultative, sans nouveau contrat jouable."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon import agendas
from donjon.monde import ErreurMonde, Monde
from donjon.paroles import preparer_parole, engagements_enregistres
from donjon.rendu import regarder as rendu
from donjon.scene import scene_percue
from donjon.temps import instant, MINUTE
from tests.test_parts_achetees import antichambre_du_banc, parole
from tests.test_tensions import recharger, vivre


class ReferenceTemporelleTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(rendu(m), rendu(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        self.assertEqual(agendas.promesses_visibles(m), agendas.promesses_visibles(r))
        return r

    def scene(self):
        m = antichambre_du_banc()
        m.data['dixiemes'] = 137
        return m

    def inscrire(self, m, objet='brasero', *, titulaire='joueur', limite=None):
        agendas.prendre(m, titulaire, {
            'condition': {'objet': objet, 'allume': True},
            'pour': 'aubin' if titulaire == 'joueur' else 'joueur',
            'minute': m.data['minutes']}, limite=limite)
        return agendas.en_cours(m, titulaire)[-1]

    def test_ancienne_livraison_reelle_sans_date_meme_decision_apres_recharge(self):
        # Cas réel du banc ressources, utilisé aussi par le socle A1.
        m, rapport = preparer_parole(antichambre_du_banc(), parole(
            'aubin', 'Je te paie trois pièces pour une de tes planches.',
            'demande', 'planches', '3'))
        avant = copy.deepcopy(m.data)
        self.assertTrue(rapport['faits'])
        self.assertIsNone(agendas.reference_temporelle(agendas.en_cours(m, 'aubin')[0]))
        self.assertEqual(m.data, avant)  # Une lecture n'invente ni identité ni date.
        self.assertNotIn('sequence_obligations', m.data)
        a, lignes_a = vivre(self.recharge(m), 3)
        b, lignes_b = vivre(m, 3)
        self.assertEqual(a.data, b.data)
        self.assertEqual(lignes_a, lignes_b)
        self.assertIn("Aubin te remet les planches de bac : tu l'avais payé.", lignes_a)
        self.assertEqual(a.objets['planches_1']['lieu'], 'joueur')
        self.assertEqual(a.objets['planches_1']['proprietaire'], 'joueur')
        self.assertEqual(a.joueur['or'], 21)
        self.assertEqual(agendas.en_cours(self.recharge(a), 'aubin'), [])

    def test_deux_obligations_meme_minute_une_seule_datee_laps_et_recharge(self):
        m = self.scene()
        datee = self.inscrire(m, limite=instant(m) + 10 * MINUTE)
        ordinaire = self.inscrire(m, 'torche')
        ref = agendas.reference_temporelle(datee)
        self.assertEqual(ref, {'id': 1, 'version': 1, 'creation': 137, 'limite': 6137})
        self.assertEqual(datee['minute'], ordinaire['minute'])
        self.assertIsNone(agendas.reference_temporelle(ordinaire))
        visibles = agendas.promesses_visibles(m)
        self.assertIn('10 minutes restantes', visibles[0])
        a, lignes_a = vivre(self.recharge(m), 3)
        b = self.recharge(m)
        lignes_b = []
        for _ in range(3):
            b, lignes = vivre(b, 1)
            lignes_b.extend(lignes)
        self.assertEqual(a.data, b.data)
        self.assertEqual(lignes_a, lignes_b)
        for monde in (self.recharge(a), self.recharge(b)):
            x, y = agendas.en_cours(monde, 'joueur')
            self.assertEqual(agendas.reference_temporelle(x), ref)
            self.assertIsNone(agendas.reference_temporelle(y))
            actuelles = agendas.promesses_visibles(monde)
            self.assertEqual(actuelles[1:], visibles[1:])
            self.assertEqual(actuelles, agendas.promesses_visibles(a))
            self.assertIn('7 minutes restantes', actuelles[0])
            self.assertIn('minute de jeu 10 et 13,7 secondes', actuelles[0])
            self.assertFalse(x.get('realisee', False))
            self.assertFalse(y.get('realisee', False))
        self.assertLess(instant(a), ref['limite'])

    def test_identites_distinctes_meme_instant_et_memes_termes_sans_reemploi(self):
        m = self.scene()
        a = self.inscrire(m, limite=1000)
        b = self.inscrire(m, limite=1000)
        c = self.inscrire(m, titulaire='aubin', limite=1000)
        refs = [agendas.reference_temporelle(x) for x in (a, b, c)]
        self.assertEqual([r['id'] for r in refs], [1, 2, 3])
        self.assertEqual([r['creation'] for r in refs], [137] * 3)
        m = self.recharge(m)
        agendas.retirer_proposition(m, 'joueur', a)
        agendas.retirer_proposition(m, 'joueur', b)
        agendas.retirer_proposition(m, 'aubin', c)
        m = self.recharge(m)
        d = self.inscrire(m, limite=1000)
        self.assertEqual(agendas.reference_temporelle(d)['id'], 4)
        self.recharge(m)

    def test_lecture_copiee_et_renouvellement_ne_deplacent_pas_la_reference(self):
        m = self.scene()
        a = self.inscrire(m, limite=10000)
        ref = agendas.reference_temporelle(a)
        agendas.reference_temporelle(a)['limite'] = 5000
        m, _ = vivre(m, 2)
        b = agendas.renouveler(m, 'joueur', a, m.data['minutes'])
        self.assertEqual(b['minute'], 2)
        self.assertEqual(agendas.reference_temporelle(b), ref)
        self.assertEqual(agendas.reference_temporelle(
            agendas.en_cours(self.recharge(m), 'joueur')[0]), ref)

    def test_admission_mal_formee_atomique_et_limite_a_la_creation_incluse(self):
        m = self.scene()
        avant = copy.deepcopy(m.data)
        for limite in (True, '1000', 1000.0, -1, 136):
            with self.subTest(limite=limite):
                with self.assertRaises(ErreurMonde) as erreur:
                    self.inscrire(m, limite=limite)
                self.assertIn('limite', erreur.exception.attendu)
                self.assertEqual(m.data, avant)
        a = self.inscrire(m, limite=instant(m))
        self.assertEqual(agendas.reference_temporelle(a)['limite'], 137)
        with self.assertRaises(ErreurMonde) as erreur:
            agendas.prendre(m, 'joueur', a)
        self.assertIn('reference_temporelle', erreur.exception.attendu)
        self.assertEqual(len(agendas.en_cours(self.recharge(m), 'joueur')), 1)

    def charger_brut(self, data):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / 'partie.json'
            chemin.write_text(json.dumps(data), encoding='utf-8')
            return Monde.charger(chemin)

    def test_refus_a_la_recharge_attendu_precis_une_cause(self):
        m = self.scene()
        self.inscrire(m, limite=1000)
        m = self.recharge(m)
        for champ, valeur, attendu in (
                ('limite', '1000', 'un entier'), ('limite', True, 'un entier'),
                ('limite', 1000.0, 'un entier'), ('limite', None, 'un entier'),
                ('limite', -1, 'positif ou nul'), ('limite', 136, '>= creation=137'),
                ('version', 0, 'termes initiaux'), ('version', 2, 'termes initiaux'),
                ('version', True, 'termes initiaux'), ('version', '1', 'termes initiaux'),
                ('creation', -1, 'positif ou nul'), ('creation', 138, '<= 137'),
                ('creation', True, 'un entier'), ('id', True, 'un entier'),
                ('id', 0, 'entre 1 et'), ('id', 2, 'entre 1 et')):
            with self.subTest(champ=champ, valeur=valeur):
                data = copy.deepcopy(m.data)
                data['promesses_joueur'][0]['reference_temporelle'][champ] = valeur
                with self.assertRaises(ErreurMonde) as erreur:
                    self.charger_brut(data)
                self.assertIn(f'obligations.joueur[0].reference_temporelle.{champ}',
                              erreur.exception.attendu)
                self.assertIn(repr(valeur), erreur.exception.attendu)
                self.assertIn(attendu, erreur.exception.attendu)
                self.assertEqual(erreur.exception.attendu.count('accepté :'), 1)

    def test_forme_sequence_et_unicite_validees_a_la_recharge(self):
        m = self.scene()
        a = self.inscrire(m, limite=1000)
        self.inscrire(m, titulaire='aubin', limite=1000)
        m = self.recharge(m)
        for valeur in (None, [], 12, {}, {'id': 1}):
            with self.subTest(reference=valeur):
                data = copy.deepcopy(m.data)
                data['promesses_joueur'][0]['reference_temporelle'] = valeur
                with self.assertRaises(ErreurMonde) as erreur:
                    self.charger_brut(data)
                self.assertIn('reference_temporelle', erreur.exception.attendu)
        for valeur in (None, True, -1, 1.0, '2'):
            with self.subTest(sequence=valeur):
                data = copy.deepcopy(m.data)
                data['sequence_obligations'] = valeur
                with self.assertRaises(ErreurMonde) as erreur:
                    self.charger_brut(data)
                self.assertIn('sequence_obligations', erreur.exception.attendu)
        data = copy.deepcopy(m.data)
        data['esprits']['aubin']['engagements'][0]['reference_temporelle'] = agendas.reference_temporelle(a)
        with self.assertRaises(ErreurMonde) as erreur:
            self.charger_brut(data)
        self.assertIn('distinct de toute autre obligation', erreur.exception.attendu)

    def test_autre_cas_reel_tache_payee_sans_date_ni_rendu_nouveau(self):
        from tests.test_agendas_socle import ChaineTests
        # Le parcours réel de Tilo comprend devis, paiement, impossibilité, remboursement et recharge.
        m, _ = ChaineTests().abandon_paye()
        self.assertNotIn('sequence_obligations', m.data)
        self.assertFalse(any('engagement pris' in t for t in engagements_enregistres(m, 'tilo')))
        self.recharge(m)

    def test_huile_auberge_reference_interne_sans_effet_sur_la_livraison(self):
        from donjon import echanges
        from donjon.biens import bourse
        from tests.test_lampes_parts import nuit_noire
        m = nuit_noire('auberge', 'joss', 'odile', 'lanterne_etable', 'pot_huile', 'etable')
        m.objets['pot_huile']['charges'] = 6
        m.data['finances_pnj']['joss'] = 5
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.demander(m, 'joss', 'odile', 'pot_huile',
                                              remettre_part=True), 'promis')
        x = agendas.en_cours(m, 'odile')[0]
        self.assertIsNone(agendas.reference_temporelle(x))
        ordinaire = self.recharge(m)
        # Seul le test établit cette métadonnée : aucun appelant du jeu ne le fait en E1.
        agendas.retirer_proposition(m, 'odile', x)
        agendas.prendre(m, 'odile', x, limite=instant(m) + 10 * MINUTE)
        datee = self.recharge(m)
        self.assertEqual(rendu(datee), rendu(ordinaire))
        self.assertEqual(scene_percue(datee), scene_percue(ordinaire))
        self.assertEqual(engagements_enregistres(datee, 'odile'),
                         engagements_enregistres(ordinaire, 'odile'))
        a, lignes_a = vivre(datee, 3)
        b, lignes_b = vivre(ordinaire, 3)
        a, b = self.recharge(a), self.recharge(b)
        piece = x['condition']['objet']
        self.assertEqual(a.objets[piece]['lieu'], 'joss')
        self.assertEqual(a.objets[piece]['proprietaire'], 'joss')
        self.assertEqual(agendas.en_cours(a, 'odile'), [])
        self.assertEqual(lignes_a, lignes_b)
        self.assertEqual(a.objets, b.objets)
        self.assertEqual((bourse(a, 'joss'), bourse(a, 'odile')),
                         (bourse(b, 'joss'), bourse(b, 'odile')))
        self.assertEqual(rendu(a), rendu(b))
        self.assertEqual(scene_percue(a), scene_percue(b))


if __name__ == '__main__':
    unittest.main()
