"""E6 : compilation libre, consentement, parité directe et recharge réelle."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas
from donjon.accords_publics import parole_accord
from donjon.consentement import preparer
from donjon.dialogues import preparer_information
from donjon.emissions import pnj
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.paroles import OPERATIONS, operations_contenu, preparer_parole
from donjon.propositions import compiler_limites
from donjon.rendu import regarder, decrire_comptes
from donjon.scene import scene_percue
from donjon.temps import ecouler, instant
from tests.test_accords_publics import situation
from tests.test_audits_attendu import jouer
from tests.test_repli_et_appel import dialogue, verdicts, NEUTRE
from tests.test_tensions import recharger


def interpretation(m, d, saisie, relative=True):
    p = parole_accord(m, d.contenu)
    p.pop('_adresse', None)
    p['replique'] = saisie.split(', ', 1)[1]
    if relative:
        p['contenu'][0]['demande']['limite'] = {'dans_secondes': 600}
    codes = operations_contenu(p['contenu'])
    p['operations_demandees'] = {t: t in codes for t in OPERATIONS}
    return {'mode': 'parole_joueur', 'texte': '', 'faits': [], 'proposition': p}


def phrase(d):
    return ('Odile, je te paie trois pièces si tu me livres une part d’huile dans dix minutes'
            if d.contenu['cible'] == 'odile' else
            'Joss, je te paie dix pièces si tu verrouilles le garde-manger dans dix minutes')


class AccordLibreDateTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual((regarder(n), decrire_comptes(n), scene_percue(n), pnj(n)),
                         (regarder(m), decrire_comptes(m), scene_percue(m), pnj(m)))
        return n

    def test_libre_et_direct_memes_termes_comptes_paroles_et_rendu_recharges(self):
        for tache in (False, True):
            with self.subTest(tache=tache):
                m, d = situation(tache)
                s = phrase(d)
                # Même réplique dans le témoin direct : sa formulation libre ne
                # change ni le contrat, ni les mots de réponse fixés par le moteur.
                r = interpretation(m, d, s)
                sorties = []
                def revue(entree):
                    dossier = entree['plan']['parole']
                    sorties.append(dossier)
                    self.assertEqual(dossier['contenu'][0]['demande']['limite'], 6000)
                    self.assertIn('10 minutes restantes', str(dossier['sens_contenu']))
                    self.assertIn('présent', str(dossier['sens_contenu']))
                    return {'conforme': True, 'motif': ''}
                n, texte, appels = jouer(m, s, [r], [], [revue], suite=('tenter',))
                self.assertEqual(len(sorties), 1)
                self.assertIn('Compris :', texte)
                self.assertIn('payées maintenant', texte)
                self.assertIn('minute de jeu 10', texte)
                self.assertNotIn('dans_secondes', texte)
                self.assertEqual(n.joueur['or'], 50 - d.contenu['parametres']['prix'])
                x, = agendas.en_cours(n, d.contenu['cible'])
                self.assertEqual(agendas.reference_temporelle(x)['limite'], 6000)
                with patch.object(Monde, 'd20', return_value=20):
                    direct = preparer_information(m, d)
                a = direct.travail
                for cle in ('objets', 'finances_pnj', 'dettes', 'permissions', 'services_rendus'):
                    self.assertEqual(n.data.get(cle), a.data.get(cle), cle)
                self.assertEqual(pnj(n), pnj(a))
                self.recharge(n)

    def test_annuler_libre_ne_parle_ne_paie_ne_promet(self):
        for tache in (False, True):
            m, d = situation(tache)
            n, texte, _ = jouer(m, phrase(d), [interpretation(m, d, phrase(d))], [], suite=('annuler',))
            self.assertIn('Compris :', texte)
            self.assertEqual(n.joueur['or'], 50)
            self.assertFalse(agendas.en_cours(n, d.contenu['cible']))
            self.assertEqual(pnj(n), pnj(m))
            self.assertEqual(n.objets, m.objets)
            self.recharge(n)

    def test_delai_fige_avant_transaction_et_revalidation_sans_modele(self):
        for tache in (False, True):
            m, d = situation(tache)
            ecouler(m, 123)
            s = phrase(d)
            mj = MJOpenAI('gpt-6-luna', connexion='chatgpt')
            with patch.object(mj, '_auditer_action'), patch.object(Monde, 'd20', return_value=20):
                r = mj._echanger_prepare(m, s, reponse=interpretation(m, d, s))
                dossier = preparer(m, r, s)
                self.assertTrue(dossier.confirmation)
                self.assertEqual(r['_transactions'][0]['proposition']['contenu'][0]['demande']['limite'], 6123)
                ecouler(m, 100)
                suivant = dossier.revalider(m)
            self.assertFalse(suivant.erreur)
            self.assertEqual(suivant.reponse['_transactions'][0]['proposition']['contenu'][0]['demande']['limite'], 6123)
            self.assertIn('minute de jeu 10', suivant.compris)
            self.recharge(suivant.travail)

    def test_omission_ou_deformation_refusee_sans_execution_partielle(self):
        for tache in (False, True):
            for clause in ('limite', 'paiement', 'maintien', 'alternative', 'pret', 'repere'):
                with self.subTest(tache=tache, clause=clause):
                    m, d = situation(tache)
                    base = phrase(d)
                    s = {'limite': base, 'paiement': base + ', mais je te paierai demain',
                         'maintien': base + ' et garde cet état jusqu’à mon retour',
                         'alternative': base + ' ou rends-moi six pièces',
                         'pret': base + ' et prête-moi ta lampe jusqu’à cette date',
                         'repere': base.replace('dans dix minutes', 'demain')}[clause]
                    r = interpretation(m, d, s)
                    if clause in ('limite', 'repere'):
                        r['proposition']['contenu'][0]['demande'].pop('limite')
                    # La revue existante reste indispensable : des mots exacts
                    # ne prouvent pas la couverture des clauses par les termes.
                    def revue(entree):
                        self.assertIn('termes_executables', str(entree))
                        return {'conforme': False, 'motif': 'Une clause de cet accord n’est pas représentée.',
                                'operations_demandees': ['proposition']}
                    refus = dialogue('Cet accord entier exige une précision ou une clause que le jeu ne prend pas en charge.')
                    n, texte, _ = jouer(m, s, [r, refus], [verdicts(NEUTRE)], [revue])
                    self.assertEqual(n.joueur['or'], 50)
                    self.assertFalse(agendas.en_cours(n, d.contenu['cible']))
                    self.assertEqual(pnj(n), pnj(m))
                    self.assertNotIn('payées maintenant', texte)
                    self.recharge(n)

    def test_entree_relative_ne_franchit_pas_le_contrat_execution(self):
        m, d = situation()
        p = interpretation(m, d, phrase(d))['proposition']
        p.pop('operations_demandees')
        p['_intention'] = phrase(d)
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as exc:
            preparer_parole(m, p)
        self.assertIn('.limite', exc.exception.attendu)
        self.assertEqual(m.data, avant)
        for valeur in ({'dans_secondes': True}, {'dans_secondes': -1}, {'demain': 1}, {'dans_secondes': 2, 'autre': 1}):
            p['contenu'][0]['demande']['limite'] = valeur
            with self.assertRaises(ErreurMonde) as exc:
                compiler_limites(p['contenu'], instant(m))
            self.assertTrue(exc.exception.attendu)
        self.recharge(m)
