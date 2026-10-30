"""Rejeu du fil 102 : mots inchangés, localisation:false ajouté au format 221."""
from donjon.emissions import joueur as emissions_joueur
import copy
import json
from pathlib import Path
import unittest

from donjon.paroles import prevue
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger
from tests.paroles_support import porter_operations_archive


class N3Tests(unittest.TestCase):
    def test_correction_contestee_aussi_le_secours_prononce_les_mots(self):
        fil = porter_operations_archive(json.loads(
            (Path(__file__).parent / 'data/n3-lot102.json').read_text(encoding='utf-8')))
        faux, revue = fil[0]['reponse'], fil[1]['reponse']
        saisie = "il y a quelqu'un ?"
        r, sortie, traces = jouer(banc('soir-noir'), saisie,
            [faux, faux, dialogue('Ta question est entendue.')],
            [rapport(ligne('mecanique', sources=['conversation_validee']))],
            revues=[copy.deepcopy(revue), copy.deepcopy(revue)])
        self.assertIn('Tu dis', sortie)
        self.assertNotIn('Reformule', sortie)
        self.assertEqual(len([a for a in traces if a[0] == 'auditer_action']), 2)
        self.assertEqual([p['texte'] for p in emissions_joueur(recharger(r))], [saisie])

    def test_fil_reel_et_question_dans_une_salle_eclairee(self):
        fil = porter_operations_archive(json.loads(
            (Path(__file__).parent / 'data/n3-lot102.json').read_text(encoding='utf-8')))
        for scenario, saisie in [('soir-noir', "il y a quelqu'un ?"),
                                 ('echanges', 'Vous m’entendez ?')]:
            with self.subTest(scenario=scenario):
                m = banc(scenario)
                cible = prevue(m, saisie)['personnage']
                appels = copy.deepcopy(fil)
                for appel in appels:
                    if appel['fonction'] == 'repondre_au_joueur':
                        appel['reponse']['proposition'].update(personnage=cible)
                        if scenario != 'soir-noir':
                            appel['reponse']['proposition']['replique'] = saisie
                r, sortie, traces = jouer(m, saisie,
                    [a['reponse'] for a in appels if a['fonction'] == 'repondre_au_joueur']
                    + [dialogue('Ta question est entendue.')],
                    [rapport(ligne('mecanique', sources=['conversation_validee']))],
                    revues=[a['reponse'] for a in appels if a['fonction'] == 'auditer_action'])
                self.assertIn('Tu dis', sortie)
                self.assertIn(saisie, sortie)
                self.assertNotIn('Reformule', sortie)
                self.assertEqual(len([a for a in traces if a[0] == 'auditer_action']), 1)
                r = recharger(r)
                self.assertEqual([p['texte'] for p in emissions_joueur(r)], [saisie])
                self.assertEqual(r.joueur['or'], m.joueur['or'])
                self.assertEqual(r.data['journal'], m.data['journal'])
                self.assertIn('Ta question est entendue.', str(r.data['conversation']))

    def test_saisie_inintelligible_ne_fait_pas_parler_corvus(self):
        r, sortie, _ = jouer(banc('soir-noir'), '??? zxq',
            [dialogue('Que veux-tu faire ?')], [rapport(ligne('neutre'))])
        self.assertNotIn('Tu dis', sortie)
        self.assertFalse(emissions_joueur(recharger(r)))
        self.assertIn('Que veux-tu faire ?', sortie)


if __name__ == '__main__':
    unittest.main()
