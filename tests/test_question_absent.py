"""La question porte sur un savoir ; le geste et la perception exigent l'accès à leur cible."""
from donjon.emissions import pnj as emissions_pnj
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon.commandes import analyser
from donjon.noms import apprendre, NomNonResolu, verifier_saisie
from donjon.monde import Monde
from donjon.rendu import regarder
from tests.test_audits_attendu import jouer
from tests.test_appel_negocie import gorm_hele_corvus
from tests.test_nom_non_relie import jouer_local
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, verdicts, NEUTRE
from tests.test_tensions import placer, recharger
from tests.support import question_sans_execution


def scene(nom):
    """Les captures réelles et leurs liens nominaux, sans modifier leur fichier."""
    base = Path(__file__).parent / 'data'
    script = json.loads((base / 'bancs' / f'{nom}.json').read_text(encoding='utf-8'))
    source = base.parents[1] / script['sauvegarde']
    brut = source.read_bytes()
    m = Monde(json.loads(gzip.decompress(brut) if source.suffix == '.gz' else brut))
    for qui in script.get('noms_connus', []):
        apprendre(m, 'joueur', qui)
    return recharger(m)


class QuestionAbsentTests(unittest.TestCase):
    def initialiser(self, m):
        # Même perception d'ouverture que le jeu, puis une vraie recharge.
        return recharger(jouer_local(recharger(m), 'regarder', True)[0])

    def assertRefuse(self, m, saisie, message):
        m = self.initialiser(m)
        avant, rendu = copy.deepcopy(m.data), regarder(m)
        for offline in (False, True):
            with self.subTest(saisie=saisie, offline=offline):
                r, sortie, appels = jouer_local(m, saisie, offline)
                self.assertEqual(appels, 0)
                self.assertIn(message, sortie)
                self.assertNotIn('Le MJ réfléchit', sortie)
                self.assertNotIn('reçu «', sortie)
                self.assertEqual(r.data, avant)
                self.assertEqual(regarder(r), rendu)

    def assertQuestionSauvee(self, r, avant, texte, rendu):
        self.assertEqual(r.data['conversation'][-1]['reponse'], question_sans_execution(texte))
        self.assertEqual(r.data['narrations_mj'][-1]['texte'], texte)
        self.assertEqual(emissions_pnj(r), emissions_pnj(avant))
        # Seuls l'échange et son récit audité sont nouveaux, aucun fait mécanique.
        apres = copy.deepcopy(r.data)
        for cle in ('conversation', 'narrations_mj', 'paroles_pnj'):
            if cle in avant:
                apres[cle] = avant[cle]
            else:
                apres.pop(cle, None)
        self.assertEqual(apres, avant)
        self.assertEqual(regarder(r), rendu)

    def test_questions_reelles_sur_les_absents_une_interpretation_auditee(self):
        for saisie in ('Que fait Brune ?', 'Que fait Gorm en ce moment ?',
                       'Où est Brune', 'Gorm est-il encore en bas ?'):
            with self.subTest(saisie=saisie):
                m = self.initialiser(scene('signes-guet'))
                self.assertFalse(m.accessible('brune'))
                self.assertTrue(m.designable('brune'))
                self.assertFalse(m.accessible('marchand'))
                self.assertTrue(m.designable('marchand'))
                self.assertIsNone(analyser(m, saisie))
                avant, rendu = copy.deepcopy(m.data), regarder(m)
                texte = 'Tu as entendu des pas en dessous, sans savoir qui les faisait.'
                r, sortie, appels = jouer(m, saisie, [dialogue(texte)],
                                          [verdicts(('mecanique', ('evenements_recents',), ''))])
                self.assertEqual([f for f, _ in appels], ['repondre_au_joueur', 'auditer_narration'])
                self.assertIn(texte, sortie)
                self.assertEqual(r.data['conversation'][-1]['joueur'], saisie)
                self.assertQuestionSauvee(r, avant, texte, rendu)
                # Le guet privé n'est pas devenu un fait public du seul fait de la question.
                faits = appels[0][1]['faits']
                self.assertEqual(faits['esprits_interlocuteurs'], {})
                for qui in ('brune', 'marchand'):
                    self.assertNotIn(f'objet:{qui}', faits)
                self.assertTrue(any('Tu entends des pas en dessous.' in e['faits']
                                    for e in faits['evenements_recents']))

    def test_question_reelle_dans_le_noir_ne_devient_pas_observation(self):
        m = self.initialiser(scene('signes-noir'))
        avant, rendu = copy.deepcopy(m.data), regarder(m)
        texte = "Tu ne peux pas lire son visage dans l'obscurité."
        r, sortie, appels = jouer(m, 'Ilse a-t-elle peur de Brune ?',
                                  [dialogue(texte)], [verdicts(NEUTRE)])
        self.assertEqual([f for f, _ in appels], ['repondre_au_joueur', 'auditer_narration'])
        self.assertIn(texte, sortie)
        self.assertQuestionSauvee(r, avant, texte, rendu)

    def test_gestes_sur_absents_restent_locaux_meme_en_faisabilite(self):
        m = banc('echanges')
        for qui, pos in (('brune', [3, 3]), ('aubin', [3, 4])):
            apprendre(m, 'joueur', qui)
            placer(m, qui, 'beffroi', pos)
        for saisie, nom in (('je pousse Brune', 'Brune'), ('je frappe Aubin', 'Aubin'),
                            ('puis-je pousser Brune ?', 'Brune'),
                            ('est-il possible de toucher Aubin ?', 'Aubin')):
            self.assertRefuse(m, saisie, f"Tu ne vois pas {nom} d'ici.")

    def test_perceptions_dans_le_noir_gardent_la_cause_du_moteur(self):
        for saisie in ('observer Ilse', 'observer Brune'):
            self.assertRefuse(scene('signes-noir'), saisie, 'cette personne')

    def test_questions_sur_noms_non_relies_restent_locales(self):
        for saisie, nom in (('Que fait Aubin ?', 'Aubin'), ('Où est Brune ?', 'Brune'),
                            ('puis-je pousser Aubin ?', 'Aubin')):
            self.assertRefuse(banc('echanges'), saisie,
                              f"Tu ne sais pas lequel d'entre eux est {nom}.")
            with self.assertRaises(NomNonResolu) as refus:
                verifier_saisie(banc('echanges'), saisie)
            self.assertIn('reference', refus.exception.attendu)
            self.assertIn('personne perçue' if 'puis-je' in saisie else 'même hors de vue',
                          refus.exception.attendu)

    def test_paroles_adressees_ne_deviennent_pas_questions_sur_absent(self):
        m = banc('echanges')
        for qui, pos in (('brune', [3, 3]), ('aubin', [3, 4])):
            apprendre(m, 'joueur', qui)
            placer(m, qui, 'beffroi', pos)
        for saisie, nom in (('Brune, où es-tu ?', 'Brune'),
                            ('je demande à Aubin : que fais-tu ?', 'Aubin')):
            self.assertRefuse(m, saisie, f"Tu ne vois pas {nom} d'ici")

    def test_reponses_a_un_appel_gardent_leur_mecanique_distante(self):
        from donjon.esprits import lire
        for saisie, engagement in (("Gorm, viens", 'rejoindre'),
                                   ("Gorm, j'arrive !", 'rejoint')):
            with self.subTest(saisie=saisie):
                m = recharger(gorm_hele_corvus(porte_ouverte=True))
                self.assertFalse(m.accessible('marchand'))
                self.assertTrue(m.designable('marchand'))
                r, sortie, appels = jouer(m, saisie, [], [])
                self.assertEqual(appels, [])
                self.assertNotIn('Tu ne vois pas Gorm', sortie)
                self.assertIn("J'arrive !", sortie)
                self.assertEqual(lire(recharger(r), 'marchand')[engagement]['qui'], 'joueur')


if __name__ == '__main__':
    unittest.main()
