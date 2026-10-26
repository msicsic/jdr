"""Une déclaration refusée reste candidate ; une revue lisible oblige les corrections."""
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
    def verifier_parole(self, m, saisie, faux, bon, revues=()):
        r, sortie, appels = jouer(m, saisie, [faux, bon, dialogue('Ta question est entendue.')],
            [rapport(ligne('mecanique', sources=['conversation_validee']))], revues=revues)
        self.assertIn('Tu dis', sortie)
        self.assertNotIn("Tu n'as encore rien dit", sortie)
        rr = recharger(r)
        self.assertEqual([p['texte'] for p in rr.data['paroles_joueur']],
                         [p['texte'] for p in m.data.get('paroles_joueur', [])] + [saisie.strip('«» ')])
        self.assertEqual(rr.joueur['or'], m.joueur['or'])
        self.assertEqual({i: o['lieu'] for i, o in rr.objets.items()},
                         {i: o['lieu'] for i, o in m.objets.items()})
        self.assertEqual(regarder(rr), regarder(r))
        self.assertEqual(rr.data, r.data)
        self.assertIn('Ta question est entendue.', str(rr.data['conversation']))
        return appels

    def test_n9_propositions_historiques_apres_preparation_refusee(self):
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
        appels = self.verifier_parole(m, saisie, faux, bon)
        self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 1)

    def test_revue_illisible_ne_confirme_pas_la_declaration(self):
        m = banc('noms-dialogue')
        saisie = 'Aubin, bonsoir'
        faux = parole('Bonsoir', ('qui', '', '', ''), personnage='aubin')
        bon = parole(saisie, personnage='aubin')
        self.verifier_parole(m, saisie, faux, bon, revues=[{}, {}])

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
        self.assertFalse(rr.data.get('paroles_joueur'))
        self.assertEqual(rr.objets, m.objets)
        self.assertEqual(rr.joueur['or'], m.joueur['or'])
        self.assertEqual(regarder(rr), regarder(r))
        self.assertIn("Tu n'as encore rien dit", str(rr.data['conversation']))
