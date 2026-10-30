"""G18 : jugement, audition, consentement et rendu persistants dans la console."""
import copy
import unittest

from donjon import ecoute, emissions, social
from donjon.esprits import croire, lire, prevision
from donjon.monde import ErreurMonde
from donjon.narration import consigner
from donjon.repliques_moteur import reponse, sceller
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.consentement_support import jouer
from tests.test_avis_joueur import preparer, dire
from tests.test_avis_menace import relation
from tests.test_disputes import dispute
from tests.test_repli_et_appel import parole, dialogue
from tests.test_social import recharger


class AvisParlesTests(unittest.TestCase):
    def assertRecharge(self, m, sortie):
        r = recharger(m)
        self.assertEqual(r.data, m.data)
        self.assertEqual(regarder(r), regarder(m))
        self.assertEqual(scene_percue(r), scene_percue(m))
        self.assertEqual(emissions.lire(r), emissions.lire(m))
        for p in emissions.pnj(r):
            if 'joueur' in p['auditeurs'] and p.get('rendu_public'):
                self.assertIn(p['rendu_public'], sortie)
                self.assertIn(p['texte'], str(r.data['conversation']))
        return r

    def dire(self, m, salle='echoppe', valeur='oui', *autres, reponses=(), audits=()):
        mots = f"l'eau {'menace' if valeur == 'oui' else 'ne menace pas'} {m.data['salles'][salle]['nom']}"
        saisie = f'je dis à Gorm : {mots}'
        return jouer(m, saisie, [parole(mots, ('avis', salle, 'menace', valeur),
            *autres, personnage='marchand'), *reponses], audits)

    def assertSansNarration(self, appels):
        self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 1)
        self.assertFalse(any(f in ('auditer_narration', 'repondre_dialogue') for f, _ in appels))

    def test_avis_positif_negatif_deux_lieux_sans_reformulation(self):
        for salle, valeur in (('echoppe', 'oui'), ('chambre_cloche', 'non')):
            with self.subTest(salle=salle):
                m = preparer()
                crue = copy.deepcopy(m.data['crue'])
                r, sortie, appels = self.dire(m, salle, valeur)
                self.assertSansNarration(appels)
                r = self.assertRecharge(r, sortie)
                self.assertEqual(r.data['crue'], crue)
                c = prevision(r, 'marchand', salle)
                self.assertEqual(c['source'], 'dit:joueur')
                self.assertEqual(c['valeur'], valeur == 'oui')
                p = emissions.pnj(r)[-1]
                self.assertEqual(p['acte'], 'reponse_avis')
                self.assertEqual(p['modalite'], 'croyance')
                self.assertIn('Je retiens ton avis : selon toi,', p['texte'])
                self.assertEqual(p['evenement']['resolutions_parlees'][0]['contenu']['evenement']['conviction'], .4)

    def test_doute_ne_devient_pas_adoption(self):
        m = preparer()
        croire(m, 'marchand', 'echoppe', 'prevision', [m.data['minutes'], 10000, 1], 'vu', 1, rang=0)
        avant = copy.deepcopy(prevision(m, 'marchand', 'echoppe'))
        r, sortie, appels = self.dire(m)
        self.assertSansNarration(appels)
        r = self.assertRecharge(r, sortie)
        self.assertEqual(prevision(r, 'marchand', 'echoppe'), avant)
        self.assertIn('Je doute de ton avis', emissions.pnj(r)[-1]['texte'])

    def test_avis_contraire_dispute_sans_replique_supplementaire(self):
        for salle in ('echoppe', 'chambre_cloche'):
            with self.subTest(salle=salle):
                m = preparer()
                croire(m, 'marchand', salle, 'prevision', [m.data['minutes'], -10000, 1], 'vu', 1, rang=0)
                for qui in ('aubin', 'ilse'):
                    relation(m, qui, 'marchand', confiance=100, affection=100)
                    relation(m, qui, 'joueur', confiance=1, affection=0)
                crue = copy.deepcopy(m.data['crue'])
                r, sortie, appels = self.dire(m, salle)
                self.assertSansNarration(appels)
                r = self.assertRecharge(r, sortie)
                self.assertEqual(r.data['crue'], crue)
                self.assertTrue(any(c.get('dispute') for c in r.data['chronique']))
                self.assertTrue(all(p['acte'] == 'dispute' for p in emissions.pnj(r)))
                self.assertIn("Non, l'eau ne menace pas", sortie)
                self.assertNotIn('Je maintiens', sortie)
                self.assertTrue(social.transmission_attestee(r, 'joueur', 'marchand',
                    {'type': 'avis', 'sujet': salle, 'attribut': 'menace', 'valeur': True}))
                self.assertEqual(prevision(r, 'ilse', salle)['source'], 'dit:marchand')
                self.assertTrue(any(s['type'] == 'dispute_perdue' for s in lire(r, 'joueur')['memoire']))

    def test_avis_pnj_entendus_et_dispute_deux_lieux(self):
        for auteur, autre, salle in (('aubin', 'ilse', 'antichambre'), ('ilse', 'aubin', 'beffroi')):
            with self.subTest(salle=salle):
                m = dispute(auteur, autre, salle)
                crue = copy.deepcopy(m.data['crue'])
                self.assertTrue(social.bavarder(m, auteur, []))
                rapport = {'emissions': emissions.publiques(m, emissions.lire(m))}
                sortie = sceller(reponse(rapport), rapport)
                self.assertTrue(sortie['_texte_moteur'])
                consigner(m, sortie)
                r = recharger(m)
                self.assertEqual(r.data, m.data)
                self.assertEqual(regarder(r), regarder(m))
                sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
                self.assertEqual(ecoute.rendre(r, sons), ecoute.rendre(m, sons))
                self.assertEqual(r.data['crue'], crue)
                self.assertEqual(prevision(r, 'marchand', salle)['source'], 'dit:' + autre)
                dits = emissions.pnj(r)
                self.assertGreater(len(dits), 1)
                for p in dits:
                    if 'joueur' in p['auditeurs']:
                        self.assertIn(p['rendu_public'], sortie['texte'])

    def test_avis_et_information_composes_dans_ordre(self):
        m = preparer()
        m.objets['marchand']['profil']['caracteristiques']['INT'] = 14
        r, sortie, appels = self.dire(m, 'echoppe', 'oui', ('ressource', 'diamant', '', ''))
        self.assertSansNarration(appels)
        texte = emissions.pnj(r)[-1]['texte']
        self.assertLess(texte.index('ton avis'), texte.index("Je n'en ai pas."))
        self.assertRecharge(r, sortie)

    def test_propos_residuel_conserve_son_audit(self):
        from tests.test_audits_attendu import ligne, rapport
        m = preparer()
        m.objets['marchand']['profil']['caracteristiques']['INT'] = 14
        libre = 'Je préfère le calme.'
        r, sortie, appels = self.dire(m, 'echoppe', 'oui', ('propos', '', '', ''),
            reponses=[dialogue(f'« {libre} »')],
            audits=[rapport(ligne('parole', locuteur='marchand', citation=libre))])
        audits = [e for f, e in appels if f == 'auditer_narration']
        self.assertEqual(len(audits), 1)
        self.assertEqual(list(audits[0]['segments'].values()), [f'« {libre} »'])
        self.assertIn(libre, sortie)
        self.assertRecharge(r, sortie)

    def test_publication_refuse_omission_reformulation_et_double(self):
        for contraire in (False, True):
            m = preparer()
            if contraire:
                croire(m, 'marchand', 'echoppe', 'prevision', [m.data['minutes'], -10000, 1], 'vu', 1, rang=0)
            m, rapport = dire(m)
            exacte = sceller(reponse(rapport), rapport)
            consigner(m, exacte)
            for texte in ('', 'La conduite sera noyée.', exacte['texte'] + ' ' + exacte['texte']):
                with self.subTest(contraire=contraire, texte=texte):
                    with self.assertRaises(ErreurMonde) as e:
                        consigner(m, {**exacte, 'texte': texte})
                    self.assertTrue(e.exception.attendu)


if __name__ == '__main__':
    unittest.main()
