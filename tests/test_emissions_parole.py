"""G15 : une occurrence entendue, un auteur, une source, un ordre sauvegardé."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon import ecoute, emissions, narration, paroles, social
from donjon.esprits import lire, croire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_avis_joueur import dire
from tests.test_disputes import dispute
from tests.test_parole_corrections import audit, ligne
from tests.test_repli_et_appel import jouer, parole, dialogue, verdicts, NEUTRE
from tests.test_social import recharger
from tests.test_avis_menace import relation


class EmissionsTests(unittest.TestCase):
    def assertRecharge(self, m):
        reprise = recharger(m)
        self.assertEqual(m.data, reprise.data)
        self.assertEqual(regarder(m), regarder(reprise))
        self.assertEqual(scene_percue(m), scene_percue(reprise))
        self.assertEqual(emissions.lire(m), emissions.lire(reprise))
        return reprise

    def test_archive_86_87_rejouee_sans_reseau(self):
        archive = json.loads(gzip.decompress(Path('tests/data/emissions-320-86-87.json.gz').read_bytes()))
        m = Monde(json.loads(gzip.decompress(Path('tests/data/avis-joueur-124.json.gz').read_bytes())))
        sorties = []
        for index, tour in enumerate(archive['tours']):
            # Le premier tour prépare réellement les croyances du second.
            dialogues = [tour['dialogues'][-1]] if index == 0 else tour['dialogues'][:2]
            audits = [tour['audits'][-1]] if index == 0 else tour['audits'][:2]
            m, sortie, appels = jouer(m, tour['saisie'], [tour['proposition'], *dialogues], audits)
            sorties.append(sortie)
            self.assertRecharge(m)
        rapport = next(e['faits']['conversation_validee'] for f, e in appels
                       if f == 'repondre_au_joueur' and 'conversation_validee' in e['faits'])
        self.assertEqual(rapport['repondent'], ['marchand'])
        self.assertNotIn('se taisent', rapport['issue'])
        dites = emissions.entendues(rapport)
        self.assertEqual([p['locuteur'] for p in dites], ['marchand', 'aubin', 'ilse'])
        self.assertEqual([p['rendu'] for p in dites], archive['tours'][1]['rapport']['faits'])
        for p in dites:
            self.assertIn(p['rendu'], sorties[-1])
        # La tentative 86 reste rejetée ; la reprise des citations de 87 est
        # admise sans transformer Aubin et Ilse en nouveaux répondants.
        self.assertEqual(sum(f == 'auditer_narration' for f, _ in appels), 2)
        fin = m.data['narrations_mj'][-1]['texte']
        self.assertNotIn('gardent le silence', fin)
        self.assertEqual(fin, ' '.join(p['rendu'] for p in dites))
        for p in dites:
            occurrences = [e for e in emissions.lire(m)
                           if e['locuteur'] == p['locuteur'] and emissions.memes_mots(e['texte'], p['texte'])]
            self.assertEqual(len(occurrences), 1)

    def test_capture_avis_joueur_mj_simule_sans_multiplier_les_repondants(self):
        # Capture de départ du script réel, avec preuve contraire d'auteur pour
        # reproduire la contradiction décrite. Ce n'est pas l'archive 86/87.
        m = Monde(json.loads(gzip.decompress(Path('tests/data/avis-joueur-124.json.gz').read_bytes())))
        croire(m, 'marchand', 'echoppe', 'prevision', [m.data['minutes'], -10000, 1], 'vu', 1, rang=0)
        for qui in ('aubin', 'ilse'):
            relation(m, qui, 'marchand', confiance=100, affection=100)
            relation(m, qui, 'joueur', confiance=1, affection=0)
        saisie = "je dis à Gorm : l'eau va gagner la conduite basse"
        prepare, rapport = paroles.preparer_parole(m, {"personnage": "marchand",
            "_intention": saisie, "replique": "l'eau va gagner la conduite basse",
            "contenu": [{"type": "avis", "sujet": "echoppe", "attribut": "menace", "valeur": "oui"}]})
        self.assertEqual(rapport['repondent'], ['marchand'])
        self.assertNotIn('se taisent', rapport['issue'])
        prononcees = emissions.entendues(rapport)
        self.assertTrue(prononcees)
        self.assertTrue(any(p['locuteur'] != 'marchand' for p in prononcees))
        self.assertEqual(rapport['faits'], emissions.faits(rapport))
        avant = copy.deepcopy(m.data['crue'])
        # Luna omet les réactions entre PNJ : le raccord commun les conserve.
        reprise, sortie, appels = jouer(m, saisie, [
            parole("l'eau va gagner la conduite basse", ('avis', 'echoppe', 'menace', 'oui'), personnage='marchand'),
            {**dialogue('Gorm t’écoute.'), 'faits': ['conversation_validee']}], [verdicts(NEUTRE)])
        self.assertEqual(reprise.data['crue'], avant)
        for p in prononcees:
            self.assertIn(p.get('rendu_public', p['rendu']), sortie)
        self.assertIn('Gorm t’écoute.', reprise.data['narrations_mj'][-1]['texte'])
        for cle in ('paroles_joueur', 'paroles_pnj'):
            self.assertNotIn(cle, reprise.data)
        ids = [p['id'] for p in emissions.lire(reprise)]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertRecharge(reprise)

    def test_autre_dispute_et_repetitions_texte_sont_des_occurrences(self):
        m = dispute('ilse', 'aubin', 'beffroi')
        lignes = []
        social.bavarder(m, 'ilse', lignes)
        flux = emissions.pnj(m)
        self.assertTrue(any(p['acte'] == 'dispute' for p in flux))
        for p in flux:
            self.assertTrue(p['evenement']['type'])
            self.assertIsInstance(p['parametres'], dict)
            self.assertIn(p['modalite'], emissions.MODALITES)
        social.faire_entendre(m, 'ilse', 'aubin', 'Ilse : « Encore. »', [], [])
        social.faire_entendre(m, 'ilse', 'aubin', 'Ilse : « Encore. »', [], [])
        occurrences = [p for p in emissions.pnj(m) if p['texte'] == 'Encore.']
        self.assertEqual(len(occurrences), 2)
        self.assertLess(occurrences[0]['ordre'], occurrences[1]['ordre'])
        self.assertRecharge(m)

    def test_ecoute_distante_et_inconscients(self):
        from donjon.ouie import auditeurs_parole
        m = dispute()
        m.joueur.update(salle='echoppe', position=[1, 2])
        # Un inconscient ne prononce et n'entend aucune parole.
        from donjon.corps import endormir
        endormir(m, 'brune')
        social.bavarder(m, 'aubin', [])
        flux = emissions.pnj(m)
        self.assertTrue(any('joueur' in p['auditeurs'] and p['salle'] != m.joueur['salle'] for p in flux))
        self.assertFalse(any('brune' in p['auditeurs'] for p in flux))
        sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
        self.assertTrue(any('emission' in b for b, _, _ in sons))
        texte = ecoute.rendre(m, sons)
        self.assertIn('menace', ' '.join(texte))
        reprise = self.assertRecharge(m)
        self.assertEqual(texte, ecoute.rendre(reprise, sons))
        n = len(emissions.lire(m))
        social.faire_entendre(m, 'brune', 'aubin', 'Brune : « Faux. »', [], [])
        self.assertEqual(len(emissions.lire(m)), n)
        endormir(m, 'joueur')
        self.assertNotIn('joueur', auditeurs_parole(m, 'aubin'))

    def test_garde_lit_les_autorisations_et_pas_la_liste_repondent(self):
        m = dispute()
        m, rapport = dire(m)
        # Une projection contradictoire ne confère pas le droit de parler à Corvus.
        rapport['repondent'] = ['marchand', 'ilse']
        faits = {'interlocuteurs': {'marchand': {'nom': 'Gorm'}, 'ilse': {'nom': 'Ilse'}},
                 'conversation_validee': rapport}
        texte = 'Ilse répond : « Je te le promets. »'
        r = narration.controler(texte, audit(ligne('parole', 'ilse', 'Je te le promets.')), faits)
        self.assertTrue(r['obstacles'])
        # Les mots exacts de la dispute sont déjà prononcés : aucun nouvel acte.
        fixes = [p.get('rendu_public', p['rendu']) for p in emissions.entendues(rapport)]
        if fixes:
            r = narration.controler(' '.join(fixes), {'segments': {}}, faits)
            self.assertFalse(r['obstacles'])
            self.assertEqual(r['paroles'], [])

    def test_reponse_admise_conserve_source_et_ordre(self):
        m = dispute()
        saisie = 'je dis à Gorm : bonsoir'
        citation = 'Bonsoir à toi.'
        r, sortie, _ = jouer(m, saisie, [parole('bonsoir', ('propos', '', '', ''), personnage='marchand'),
            {**dialogue('Gorm : « Bonsoir à toi. »'), 'faits': ['conversation_validee']}],
            [audit(ligne('parole', 'marchand', citation))])
        flux = emissions.lire(r)
        reponse = next(p for p in reversed(flux) if p['texte'] == citation)
        origine = next(p for p in flux if p['id'] == reponse['evenement']['emission_joueur'])
        self.assertEqual(origine['locuteur'], 'joueur')
        self.assertEqual(reponse['acte'], 'reponse_corvus')
        self.assertLess(origine['ordre'], reponse['ordre'])
        self.assertIn('joueur', reponse['auditeurs'])
        self.assertIn(citation, sortie)
        self.assertRecharge(r)

    def test_projection_ne_revele_pas_les_auditeurs_caches(self):
        m = dispute()
        m.data['noms_connus'].remove('brune')
        # Brune est ailleurs et n'est ni vue ni connue du joueur.
        social.faire_entendre(m, 'aubin', 'ilse', 'Aubin : « Écoute. »', [], [])
        p = emissions.pnj(m)[-1]
        p['auditeurs'].append('brune')  # preuve de transport : auditeur caché
        p['parametres']['secret'] = 'brune'
        public = emissions.publiques(m, [p])[0]
        self.assertNotIn('brune', public['auditeurs'])
        self.assertNotIn('secret', public['parametres'])

    def test_migration_historique_sans_inventer_un_ordre_ancien(self):
        m = dispute()
        m.data['paroles_joueur'] = [{'texte': 'Bonsoir.', 'auditeur': 'ilse', 'auditeurs': ['ilse'],
                                    'minute': m.data['minutes'], 'revision': m.data['revision']}]
        m.data['paroles_pnj'] = [{'locuteur': 'ilse', 'texte': 'Bienvenue.', 'auditeurs': ['joueur'],
                                'salle': 'antichambre', 'minute': m.data['minutes'], 'revision': m.data['revision']}]
        m = recharger(m)
        self.assertNotIn('paroles_joueur', m.data)
        self.assertNotIn('paroles_pnj', m.data)
        flux = emissions.lire(m)
        self.assertEqual([p['texte'] for p in flux], ['Bonsoir.', 'Bienvenue.'])
        self.assertTrue(all(p['ordre_historique_inconnu'] for p in flux))
        self.assertEqual(self.assertRecharge(m).data, m.data)

    def test_reprise_exige_le_meme_auteur_et_les_memes_mots(self):
        m = dispute()
        social.faire_entendre(m, 'aubin', 'ilse', 'Aubin : « L’eau monte. »', [], [])
        rapport = {'emissions': emissions.publiques(m, emissions.pnj(m))}
        self.assertIsNotNone(emissions.reprise(rapport, 'aubin', "L'eau monte."))
        self.assertIsNone(emissions.reprise(rapport, 'ilse', "L'eau monte."))
        self.assertIsNone(emissions.reprise(rapport, 'aubin', "L'eau ne monte pas."))
        self.assertRecharge(m)

    def test_auteur_visible_sans_nom_ne_fuit_pas_dans_le_rendu(self):
        m = dispute()
        m.data['noms_connus'].remove('aubin')
        social.faire_entendre(m, 'aubin', 'ilse', 'Aubin : « Écoute-moi. »', [], [])
        p = emissions.pnj(m)[-1]
        self.assertNotIn('Aubin', p['rendu_public'])
        self.assertIn('Écoute-moi.', p['rendu_public'])
        self.assertRecharge(m)


if __name__ == '__main__':
    unittest.main()
