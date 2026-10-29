"""Preuve historique exacte, console et recharge."""
from donjon.emissions import pnj as emissions_pnj
import copy
import unittest

from donjon.narration import echanges_passes, rappels_exacts, segments_etablis, consigner
from donjon.noms import public
from donjon.dialogues import interlocuteurs
from donjon.monde import ErreurMonde
from tests import test_redire_passe
from tests.test_parole_corrections import banc, ligne, audit
from tests.test_repli_et_appel import jouer, dialogue
from tests.test_tensions import recharger


class RappelExactTests(unittest.TestCase):
    def scenes(self):
        helper = test_redire_passe.RedirePasseTests()
        noir = helper.dire(banc('soir-noir'), 'personne', 'Qui est là ?',
                          'Je m’appelle Ilse. Et toi, qui es-tu ?', ('qui', '', '', ''))
        from tests.test_parole_commune import scene
        autre = scene()
        # Autre scène, autre locuteur : la parole entendue ne prouve pas son contenu.
        autre.data.setdefault('paroles_pnj', []).append(dict(locuteur='aubin',
            texte='La lune est verte.', auditeurs=['joueur'], revision=autre.data['revision'], minute=0, salle='antichambre'))
        return [noir, autre]

    def test_console_exacte_sans_audit_sur_deux_scenes(self):
        for m in self.scenes():
            m = recharger(m)
            faits = {'interlocuteurs': public(m, interlocuteurs(m))}
            faits['echanges_passes'] = echanges_passes(m, faits['interlocuteurs'])
            phrase = next(iter(rappels_exacts(faits)))
            avant = copy.deepcopy(m.data)
            r, sortie, appels = jouer(m, 'mj que vient-on de me dire ?', [dialogue(phrase)], [])
            self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
            dossier = appels[0][1]['faits']
            for evenement in dossier.get('paroles_entendues', []):
                self.assertIn(evenement['texte'], [p['texte'] for p in emissions_pnj(avant)])
            self.assertIn(phrase, sortie)
            self.assertEqual(r.data['conversation'][-1]['reponse'], phrase)
            self.assertEqual(r.data['narrations_mj'][-1]['texte'], phrase)
            self.assertEqual(emissions_pnj(r), emissions_pnj(avant))
            for champ in ('objets', 'joueur', 'minutes', 'jets'):
                self.assertEqual(r.data[champ], avant[champ])
            self.assertEqual(recharger(r).data['conversation'], r.data['conversation'])

    def test_projection_ne_change_que_la_reference(self):
        m = self.scenes()[0]
        entree = {'echanges_passes': {'ilse': [{'texte': 'Ilse', 'revision': 1} ]},
                  'description': 'Aubin est ici.'}
        projetee = public(m, entree)
        self.assertEqual(projetee['echanges_passes']['voix_1'][0]['texte'], 'Ilse')
        self.assertNotIn('Aubin', projetee['description'])
        self.assertEqual(entree['echanges_passes']['ilse'][0]['texte'], 'Ilse')
        evenement = dict(locuteur='ilse', texte='Je m’appelle Ilse.', presentation='Ilse',
                         auditeurs=['joueur'], revision=1)
        rendu = public(m, evenement)
        self.assertEqual(rendu['locuteur'], 'voix_1')
        self.assertEqual(rendu['texte'], evenement['texte'])
        self.assertEqual(rendu['presentation'], 'Ilse')
        prive = public(m, {**evenement, 'auditeurs': ['aubin']})
        self.assertNotEqual(prive['texte'], evenement['texte'])

    def test_rappel_deforme_refuse_puis_exact_affiche_apres_recharge(self):
        for m in self.scenes():
            m = recharger(m)
            faits = {'interlocuteurs': public(m, interlocuteurs(m))}
            faits['echanges_passes'] = echanges_passes(m, faits['interlocuteurs'])
            bon, ref = next(iter(rappels_exacts(faits).items()))
            mauvais = bon[:bon.index('«')] + '« Je ne te donnerai rien. ».'
            l = ligne('mecanique', sources=['echanges_passes'])
            l['rappels'] = [dict(locuteur=ref, affirmation='Je ne te donnerai rien.',
                                 compatibilite='contradictoire')]
            r, sortie, appels = jouer(m, 'mj que vient-on de me dire ?',
                [dialogue(mauvais), dialogue(bon)], [audit(l)])
            self.assertEqual(sum(f == 'auditer_narration' for f, _ in appels), 1)
            self.assertNotIn(mauvais, sortie)
            self.assertIn(bon, sortie)
            self.assertEqual(emissions_pnj(r), emissions_pnj(m))
            self.assertEqual(recharger(r).data['conversation'][-1]['reponse'], bon)

    def test_preuve_refusee_si_historique_retire_a_la_sauvegarde(self):
        m = self.scenes()[0]
        faits = {'interlocuteurs': public(m, interlocuteurs(m))}
        faits['echanges_passes'] = echanges_passes(m, faits['interlocuteurs'])
        phrase = next(iter(rappels_exacts(faits)))
        reponse = {'texte': phrase, '_audit': {'texte_initial': phrase,
                    'segments': segments_etablis(phrase, faits), 'faits': faits}}
        emissions_pnj(m).clear()
        with self.assertRaisesRegex(ErreurMonde, 'rappel'):
            consigner(m, reponse)

    def test_citation_modifiee_ou_mauvais_locuteur_non_prouves(self):
        m = self.scenes()[0]
        faits = {'interlocuteurs': public(m, interlocuteurs(m))}
        faits['echanges_passes'] = echanges_passes(m, faits['interlocuteurs'])
        phrase = next(iter(rappels_exacts(faits)))
        self.assertFalse(segments_etablis(phrase.replace('Ilse. Et', 'Aubin. Et'), faits))
        self.assertFalse(segments_etablis(phrase + ' Tu reçois une pièce.', faits).get('1'))

    def test_phrase_historique_entiere_sans_audit_apres_recharge(self):
        for m in self.scenes():
            m = recharger(m)
            # Premier segment exact, sans enlever de mots à l'intérieur.
            from donjon.narration import segments
            mots = segments(emissions_pnj(m)[0]['texte'])[0]
            phrase = f'« {mots} »'
            r, sortie, appels = jouer(m, 'mj rappelle-moi ses mots', [dialogue(phrase)], [])
            self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
            self.assertIn(phrase, sortie)
            self.assertEqual(emissions_pnj(r), emissions_pnj(m))
            self.assertEqual(recharger(r).data['conversation'][-1]['reponse'], phrase)
            faits = {'interlocuteurs': public(m, interlocuteurs(m))}
            faits['echanges_passes'] = echanges_passes(m, faits['interlocuteurs'])
            self.assertFalse(segments_etablis(f'« {mots[3:]} »', faits))

