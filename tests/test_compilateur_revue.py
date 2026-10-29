"""G1 d : le sens précède le refus public ; les sources ne décident pas du mode."""
import copy
import unittest

from donjon.couverture_action import verifier, RapportInvalide
from donjon.improvisation import proposition as improviser, issue, effet, schema_proposition
from donjon.monde import nouveau_monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.narration import REGLE_AMBIANCE
from donjon.compilateur import prompt_compilateur
from donjon.rendu import regarder
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_gardes_justes import crypte
from tests.test_repli_et_appel import dialogue
from tests.test_relances_luna import action, loin_de_la_poutre
from tests.test_tensions import recharger


class RevueCompilateurTests(unittest.TestCase):
    def test_ecoute_refusee_par_la_revue_sur_admission_reste_fidele_et_executee(self):
        m = nouveau_monde()
        r, texte, appels = jouer(m, "mj j'écoute à la porte pour savoir s'il y a quelque chose derrière",
            [action(proposition('ecouter'))], [], revues=[{
                'conforme': False, 'perimetre': 'admission',
                'motif': 'Le plan ne garantit pas que ce voisinage soit accessible.'}])
        self.assertEqual([f for f, _ in appels], ['repondre_au_joueur', 'auditer_action'])
        self.assertEqual(r.data['minutes'], m.data['minutes'] + 3)
        self.assertEqual(r.data['journal'][-1]['action']['action'], 'ecouter')
        self.assertEqual(r.joueur['position'], m.joueur['position'])
        self.assertIn(r.data['conversation'][-1]['reponse'], texte)
        rr = recharger(r)
        self.assertEqual(rr.data, r.data)
        self.assertEqual(regarder(rr), regarder(r))

    def test_deux_refus_de_portee_ne_relancent_ni_sens_ni_compilation(self):
        for p, saisie in (
            (improviser('Coup', issue('Brouillon.'), cibles=['poutre_conduite'], approche='effort'),
             'je donne un coup de pied dans la poutre'),
            (proposition('prendre', 'crochets'), 'je prends les crochets')):
            m = loin_de_la_poutre()
            avant = copy.deepcopy(m.data)
            with self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(p)
            r, texte, appels = jouer(m, 'mj ' + saisie, [action(p)], [], revues=[{
                'conforme': False, 'perimetre': 'admission',
                'motif': "Le candidat n'est pas exécuté, donc le geste manque."}])
            self.assertEqual([f for f, _ in appels], ['repondre_au_joueur', 'auditer_action'])
            self.assertIn(str(refus.exception), texte)
            self.assertNotIn('ne couvre pas', texte)
            dossier = appels[1][1]['plan']
            self.assertNotIn('proposition_non_admise', dossier)
            self.assertNotIn('non admis', dossier['titre'])
            for k in ('objets', 'joueur', 'minutes', 'jets', 'journal'):
                self.assertEqual(r.data[k], avant[k])
            self.assertEqual(r.data['narrations_mj'][-1]['sources'], ['moteur'])
            self.assertEqual(recharger(r).data, r.data)

    def test_perimetre_ne_supprime_pas_un_vrai_ecart_de_sens(self):
        with self.assertRaisesRegex(ErreurMonde, 'Autre geste'):
            verifier({'conforme': False, 'motif': 'Autre geste.', 'perimetre': 'sens'})
        for perimetre in ('inconnu', None):
            with self.assertRaises(RapportInvalide):
                verifier({'conforme': False, 'motif': '', 'perimetre': perimetre})

    def test_deux_expressions_sans_epreuve_sont_emises_et_rechargees(self):
        for forme, mots in (('voix_melodique', 'je fredonne doucement'),
                            ('corps_rythmique', 'je frappe un rythme avec mes mains')):
            m = nouveau_monde()
            p = improviser('Expression', issue('Brouillon.', [effet('son', 'joueur', texte=forme, valeur=1)]), minutes=0)
            r, texte, appels = jouer(m, 'mj ' + mots, [action(p)], [], revues=[{
                'conforme': True, 'motif': '', 'perimetre': 'sens', 'evenements_requis': ['son']}])
            self.assertEqual(r.data['sons'][-1]['forme'], forme)
            self.assertEqual(r.data['jets'], m.data['jets'])
            self.assertNotIn('tenter', texte)
            self.assertEqual(len(appels), 2)
            self.assertEqual(recharger(r).data['sons'], r.data['sons'])
        variantes = schema_proposition()['anyOf']
        jet = next(v for v in variantes if '' not in v['properties']['stat']['enum'])
        self.assertNotIn('expression', jet['properties']['approche']['enum'])

    def test_ambiance_commune_et_deux_sensations_sans_faits_mecaniques(self):
        self.assertIn(REGLE_AMBIANCE, prompt_compilateur(type('F', (), {'schema_lu': True})()))
        for mots, texte, sensation in (
            ('ça sent quoi ici ?', 'Une odeur de pierre humide flotte ici.', 'odeur de pierre humide'),
            ('quelle impression donne cet endroit ?', 'Une impression de calme enveloppe les lieux.', 'impression de calme')):
            m = nouveau_monde()
            avant = copy.deepcopy(m.data)
            r, sortie, _ = jouer(m, 'mj ' + mots, [dialogue(texte)],
                [rapport(ligne('ambiance', entites=[sensation]))])
            self.assertIn(texte, sortie)
            self.assertEqual(r.objets, avant['objets'])
            self.assertEqual(r.data['minutes'], avant['minutes'])
            rr = recharger(r)
            self.assertEqual(rr.data['ambiances'][m.joueur['salle']][-1]['texte'], texte)
            self.assertEqual(rr.data.get('paroles_joueur'), avant.get('paroles_joueur'))

    def test_deux_questions_mj_ne_recoivent_pas_une_parole_deja_decidee(self):
        for mots in ("qu'est-ce qu'il y a derrière la porte, selon toi ?", 'que sais-je de cet endroit ?'):
            m = crypte()
            texte = 'Tu ne sais pas ce qui se trouve au-delà de ce que tu peux voir.'
            r, sortie, appels = jouer(m, 'mj ' + mots, [dialogue(texte)],
                [rapport(ligne('mecanique', sources=['perception']))])
            faits = appels[0][1]['faits']
            self.assertNotIn('parole_prevue', faits)
            self.assertEqual(faits['parole_possible']['si_mode'], 'parole_joueur')
            self.assertFalse(faits['saisie']['parole_explicite'])
            self.assertIn(texte, sortie)
            self.assertEqual(r.data.get('paroles_joueur'), m.data.get('paroles_joueur'))
            self.assertEqual(recharger(r).objets, m.objets)


if __name__ == '__main__':
    unittest.main()
