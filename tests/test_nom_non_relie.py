"""Désignation nominale avant le MJ : état et affichage après rechargement."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from donjon.moteur import proposition
from donjon.noms import apprendre, NomNonResolu, verifier_saisie
from donjon.rendu import regarder
from donjon.voix import se_nommer
from tests.test_audits_attendu import jouer
from tests.test_luna_noms import action
from tests.test_parole_corrections import banc
from tests.test_tensions import placer, recharger


def jouer_local(m, saisie, offline=False):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / 'partie.json'
        m.sauver(chemin)
        with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
              patch.object(MJOpenAI, '_appeler_brut') as appeler,
              patch('builtins.input', side_effect=[saisie, 'quitter']),
              patch('sys.stdout', io.StringIO()) as sortie):
            args = ['--console', '--recit-moteur', '--save', str(chemin)]
            args += ['--offline'] if offline else ['--connexion', 'api']
            assert jeu.main(args) == 0
        return Monde.charger(chemin), sortie.getvalue(), appeler.call_count


class NomNonRelieTests(unittest.TestCase):
    def assertRefuse(self, m, saisie, message):
        m, _, _ = jouer_local(recharger(m), 'regarder', True)
        avant = copy.deepcopy(m.data)
        for offline in (False, True):
            with self.subTest(saisie=saisie, offline=offline):
                r, sortie, appels = jouer_local(m, saisie, offline)
                self.assertEqual(appels, 0)
                self.assertIn(message, sortie)
                self.assertNotIn('Le MJ réfléchit', sortie)
                self.assertEqual(r.data, avant)
                self.assertEqual(regarder(r), regarder(m))
                self.assertNotIn('reçu «', sortie)

    def test_cas_reel_pousser_aubin_sans_lien(self):
        m = banc('echanges')
        self.assertNotIn('aubin', m.data['noms_connus'])
        self.assertRefuse(m, 'je pousse Aubin', "Tu ne sais pas lequel d'entre eux est Aubin.")

    def test_don_a_brune_non_reliee(self):
        m = banc('echanges')
        m.objets['cloche'].update(lieu='joueur', position_salle='antichambre')
        self.assertRefuse(m, 'je donne la cloche à Brune', "Tu ne sais pas lequel d'entre eux est Brune.")

    def test_meme_controle_pour_les_autres_gestes_et_le_mj_force(self):
        m = banc('echanges')
        for saisie in ('pousser Aubin', 'frapper Aubin avec la cloche', 'observer Aubin',
                       'je bouscule Aubin', 'mj je pousse Aubin', 'puis-je pousser Aubin ?', 'je pousse Aubin ?', 'qui est Aubin ?'):
            self.assertRefuse(m, saisie, "Tu ne sais pas lequel d'entre eux est Aubin.")

    def test_nom_relie_a_un_absent(self):
        m = banc('echanges')
        apprendre(m, 'joueur', 'aubin')
        placer(m, 'aubin', 'beffroi', [3, 3])
        self.assertRefuse(m, 'je pousse Aubin', "Tu ne vois pas Aubin d'ici.")
        apprendre(m, 'joueur', 'brune')
        placer(m, 'brune', 'beffroi', [3, 4])
        self.assertRefuse(m, 'je donne la cloche à Brune', "Tu ne vois pas Brune d'ici.")

    def test_nom_sans_lien_et_sans_inconnu_percu(self):
        m = banc('echanges')
        for x, qui in enumerate(('aubin', 'brune', 'ilse'), 2):
            placer(m, qui, 'beffroi', [x, 3])
        self.assertRefuse(m, 'je pousse Aubin', 'Tu ne connais personne du nom de Aubin ici.')

    def test_nom_relie_le_geste_part_au_mj_et_la_fiche_persiste(self):
        for qui, saisie, p in (
            ('aubin', 'je pousse Aubin', proposition('pousser', 'aubin')),
            ('brune', 'je donne la cloche à Brune', proposition('remettre', 'cloche', 'brune'))):
            with self.subTest(qui=qui):
                m = banc('echanges')
                apprendre(m, 'joueur', qui)
                m.objets['cloche'].update(lieu='joueur', position_salle='antichambre')
                avant = copy.deepcopy(m.objets[qui])
                r, sortie, appels = jouer(m, saisie, [action(p)], [])
                if qui == 'aubin':
                    self.assertEqual(r.objets[qui], avant)  # fiche seulement, sans « tenter »
                    self.assertIn('pousser', sortie.lower())
                else:
                    self.assertEqual(r.objets['cloche']['lieu'], qui)
                    self.assertIn('Brune', sortie)
                self.assertIn(qui, r.data['noms_connus'])
                if qui == 'aubin':
                    self.assertTrue(any(f == 'repondre_au_joueur' for f, _ in appels))

    def test_la_frontiere_mj_refuse_avant_tout_appel_meme_direct(self):
        m = banc('echanges')
        avant = copy.deepcopy(m.data)
        with patch.object(MJOpenAI, '_appeler_brut') as appeler:
            with self.assertRaises(NomNonResolu) as refus:
                MJOpenAI(connexion='api').echanger(m, 'je pousse Aubin')
        appeler.assert_not_called()
        self.assertIn('reference', refus.exception.attendu)
        self.assertEqual(m.data, avant)

    def test_les_mots_de_la_parole_ne_visent_pas_un_corps(self):
        m = banc('echanges')
        for saisie in ('je dis à tous : je me méfie d’Aubin', '« C’est moi, Brune. »',
                       'je grave « Aubin » sur la cire'):
            with self.subTest(saisie=saisie):
                avant = copy.deepcopy(m.data)
                verifier_saisie(m, saisie)
                self.assertEqual(recharger(m).data, avant)

    def test_une_voix_qui_porte_un_nom_ne_donne_pas_le_corps_reel(self):
        m = banc('echanges')
        # Imposture : la voix de Brune se dit Ilse, le vrai corps d'Ilse est ailleurs.
        placer(m, 'ilse', 'beffroi', [3, 3])
        se_nommer(m, 'joueur', 'brune', 'ilse')
        m = recharger(m)
        verifier_saisie(m, 'je donne la cloche à Ilse')
        verifier_saisie(m, 'je donne la cloche à la voix toute proche qui se dit Ilse')
        self.assertNotIn('ilse', recharger(m).data['noms_connus'])


if __name__ == '__main__':
    unittest.main()
