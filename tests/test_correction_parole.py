"""Une déclaration refusée reste candidate ; une revue lisible oblige les corrections."""
from donjon.emissions import joueur as emissions_joueur
import json
from pathlib import Path
import unittest

from donjon.paroles import prevue
from donjon.rendu import regarder
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class CorrectionParoleTests(unittest.TestCase):
    def verifier_parole(self, m, saisie, faux, bon, revues=(), reponse='Ta question est entendue.'):
        r, sortie, appels = jouer(m, saisie, [faux, bon, dialogue('Ta question est entendue.')],
            [rapport(ligne('mecanique', sources=['conversation_validee']))], revues=revues)
        self.assertIn('Tu dis', sortie)
        self.assertNotIn("Tu n'as encore rien dit", sortie)
        rr = recharger(r)
        self.assertEqual([p['texte'] for p in emissions_joueur(rr)],
                         [p['texte'] for p in emissions_joueur(m)] + [saisie.strip('«» ')])
        self.assertEqual(rr.joueur['or'], m.joueur['or'])
        self.assertEqual({i: o['lieu'] for i, o in rr.objets.items()},
                         {i: o['lieu'] for i, o in m.objets.items()})
        self.assertEqual(regarder(rr), regarder(r))
        self.assertEqual(rr.data, r.data)
        self.assertIn(reponse, rr.data['conversation'][-1]['reponse'])
        return appels

    def test_n9_propositions_historiques_apres_preparation_refusee(self):
        # Format 221 : localisation:false complète le protocole, sans changer les mots archivés.
        propositions = json.loads((Path(__file__).parent / 'data/n9-lot141.json').read_text(encoding='utf-8-sig'))
        m = banc('soir-noir')
        # Le tour précédent a fait entendre une voix, comme dans le fil réel.
        m, _, _ = jouer(m, "il y a quelqu'un ?", [
            parole("il y a quelqu'un ?", personnage='personne'),
            dialogue('Une voix : « Moi. »')],
            [rapport(ligne('parole', locuteur='voix_1', citation='Moi.'))])
        reponses = [dict(mode='parole_joueur', texte='', faits=[], proposition=p) for p in propositions]
        appels = self.verifier_parole(m, '« Qui est là ? »', *reponses)
        self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 1)

    def test_autre_script_declaration_fausse_omise_localement(self):
        m = banc('noms-dialogue')
        saisie = 'Aubin, as-tu faim ?'
        faux = parole(saisie, ('ressource', 'faim', '', ''), personnage='aubin')
        faux['proposition']['operations_demandees']['proposition'] = True
        bon = parole(saisie, ('ressource', 'faim', '', ''), personnage='aubin')
        # G16 / rapport 345 : ressource négative formulée par le moteur.
        appels = self.verifier_parole(m, saisie, faux, bon, reponse="Aubin : « Je n'en ai pas. »")
        self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 1)

    def test_revue_illisible_ne_confirme_pas_la_declaration(self):
        m = banc('noms-dialogue')
        saisie = 'Aubin, bonsoir'
        faux = parole('Bonsoir', ('qui', '', '', ''), personnage='aubin')
        bon = parole(saisie, personnage='aubin')
        appels = self.verifier_parole(m, saisie, faux, bon, revues=[{}, {}, {'conforme': True, 'motif': ''}])
        self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 3)

    def test_omission_candidate_ecartee_par_revue_sur_mots_exacts(self):
        for script, saisie in [('noms-dialogue', 'Aubin, bonsoir'),
                               ('echanges', 'Vous me voyez ?')]:
            with self.subTest(script=script):
                m = banc(script)
                cible = prevue(m, saisie)['personnage']
                faux = parole(saisie, personnage=cible)
                faux['proposition']['operations_demandees']['proposition'] = True
                bon = parole(saisie, personnage=cible)
                appels = self.verifier_parole(m, saisie, faux, bon)
                self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 1)

    def test_achat_reconnu_reste_exige_apres_correction_et_secours(self):
        m = banc('noms-dialogue')
        saisie = '« Je te paie trois pièces pour une planche. »'
        cible = prevue(m, saisie)['personnage']
        faux = parole(saisie.strip('«» '), ('ressource', 'faim', '', ''), personnage=cible)
        correction = parole(saisie.strip('«» '), personnage=cible)
        # La revue refuse le faux type et reconnaît l'achat omis.
        r, sortie, appels = jouer(m, saisie, [faux, correction], [],
            revues=[{'contenu_conforme': False, 'motif': 'Achat omis, pas une demande de nourriture.',
                     'operations_demandees': ['proposition']}])
        self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 1)
        self.assertNotIn('Tu dis', sortie)
        self.assertIn("Tu n'as encore rien dit", sortie)
        rr = recharger(r)
        self.assertFalse(emissions_joueur(rr))
        self.assertEqual(rr.objets, m.objets)
        self.assertEqual(rr.joueur['or'], m.joueur['or'])
        self.assertEqual(regarder(rr), regarder(r))
        self.assertIn("Tu n'as encore rien dit", str(rr.data['conversation']))
