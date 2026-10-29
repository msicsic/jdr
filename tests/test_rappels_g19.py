"""G19 : la restitution historique ne produit aucun nouvel événement du monde."""
import copy
import unittest

from donjon import emissions, narration
from donjon.dialogues import interlocuteurs
from donjon.monde import ErreurMonde
from donjon.noms import public
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_parole_corrections import ligne
from tests.test_repli_et_appel import dialogue, jouer
from tests.test_tensions import recharger


def dossier(m):
    faits = {'interlocuteurs': public(m, interlocuteurs(m))}
    faits['echanges_passes'] = narration.echanges_passes(m, faits['interlocuteurs'])
    return faits


def reponse(texte, faits):
    return {'texte': texte, '_audit': {'texte_initial': texte, 'faits': faits,
        'segments': narration.segments_etablis(texte, faits),
        'fondement': narration.fondement({'faits': faits})}}


class RappelsG19Tests(unittest.TestCase):
    def scenes(self):
        from tests.test_rappel_exact import RappelExactTests
        return RappelExactTests().scenes()

    def assertRestitution(self, m, texte, audits=()):
        from donjon.spatial import memoriser
        memoriser(m)  # La carte initiale est affichée avant la saisie de rappel.
        avant = copy.deepcopy(m.data)
        r, sortie, appels = jouer(m, 'mj rappelle-moi les mots entendus', [dialogue(texte)], audits)
        self.assertIn(texte, sortie)
        self.assertEqual(emissions.lire(r), emissions.lire(avant))
        # Seul le journal d'affichage est enrichi ; aucune mémoire, croyance,
        # ressource, horloge, orientation ou permission n'est acquise en relisant.
        for champ in avant:
            if champ not in ('conversation', 'narrations_mj'):
                self.assertEqual(r.data.get(champ), avant[champ], champ)
        recharge = recharger(r)
        self.assertEqual(recharge.data, r.data)
        self.assertEqual(regarder(recharge), regarder(r))
        self.assertEqual(scene_percue(recharge), scene_percue(r))
        self.assertEqual(recharge.data['conversation'][-1]['reponse'], texte)
        self.assertEqual(recharge.data['narrations_mj'][-1]['texte'], texte)
        return appels

    def test_rappel_reel_et_autre_locuteur_sans_audit_ni_apprentissage(self):
        for m in self.scenes():
            m = recharger(m)
            faits = dossier(m)
            parole = next(ps[0] for ps in faits['echanges_passes'].values() if ps)
            self.assertIn('id', parole)
            self.assertIn('ordre', parole)
            appels = self.assertRestitution(m, parole['rappel_exact'])
            self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))

    def test_locuteur_quitte_la_scene_reste_historique_sans_droit_de_reponse(self):
        for m in self.scenes():
            m = recharger(m)
            m.joueur['salle'] = 'chambre_cloche'
            m.joueur['position'] = [1, 1]
            m.data['entendus'] = []
            m = recharger(m)
            faits = dossier(m)
            ref = next(ref for ref, ps in faits['echanges_passes'].items() if ps)
            self.assertNotIn(ref, faits['interlocuteurs'])
            texte = faits['echanges_passes'][ref][0]['rappel_exact']
            appels = self.assertRestitution(m, texte)
            self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))

    def test_absence_de_mots_exacts_sans_inventer_une_parole(self):
        m = recharger(self.scenes()[1])
        for p in m.data['emissions_parole']:
            p['auditeurs'] = ['ilse']
        m = recharger(m)
        faits = dossier(m)
        textes = narration.preuves_rappels(faits)
        texte = next(t for t, ps in textes.items() if ps[0].get('absence'))
        appels = self.assertRestitution(m, texte)
        self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
        self.assertNotIn('La lune est verte.', str(textes))

    def test_source_retiree_ou_remplacee_refusee_avant_toute_ecriture(self):
        for mutation in ('auditeurs', 'id', 'ordre', 'texte', 'locuteur'):
            m = recharger(self.scenes()[1])
            faits = dossier(m)
            texte = faits['echanges_passes']['aubin'][0]['rappel_exact']
            p = next(p for p in m.data['emissions_parole'] if p['locuteur'] == 'aubin')
            p[mutation] = {'auditeurs': ['ilse'], 'id': 999, 'ordre': 999, 'texte': 'Autre chose.',
                           'locuteur': 'ilse'}[mutation]
            avant = copy.deepcopy(m.data)
            with self.assertRaisesRegex(ErreurMonde, 'rappel') as refus:
                narration.consigner(m, reponse(texte, faits))
            self.assertTrue(refus.exception.attendu)
            self.assertEqual(m.data, avant)

    def test_absence_reverifiee_si_des_mots_ont_ete_entendus_depuis(self):
        m = recharger(self.scenes()[1])
        p = m.data['emissions_parole'][0]
        p['auditeurs'] = ['ilse']
        faits = dossier(m)
        texte = next(t for t, ps in narration.preuves_rappels(faits).items()
                     if ps == [{'locuteur': 'aubin', 'absence': True}])
        p['auditeurs'] = ['joueur']
        avant = copy.deepcopy(m.data)
        with self.assertRaisesRegex(ErreurMonde, 'rappel'):
            narration.consigner(m, reponse(texte, faits))
        self.assertEqual(m.data, avant)

    def test_attribution_historique_ne_prouve_pas_une_identite_presente(self):
        m = recharger(self.scenes()[0])
        m.joueur['salle'] = 'chambre_cloche'
        m.data['entendus'] = []
        faits = dossier(m)
        texte = faits['echanges_passes']['voix_1'][0]['rappel_exact']
        self.assertFalse(narration.voix_inconnues(m, [], faits, texte))
        self.assertTrue(narration.voix_inconnues(m, [], faits, texte + ' Ilse est ici.'))

    def test_segment_exact_exclu_de_l_audit_d_un_texte_mixte(self):
        m = recharger(self.scenes()[1])
        texte = dossier(m)['echanges_passes']['aubin'][0]['rappel_exact']
        suite = 'L’air est lourd.'
        r, sortie, appels = jouer(m, 'mj rappelle-moi ses mots', [dialogue(texte + ' ' + suite)],
                                 [{'segments': {'1': ligne('ambiance')}}])
        audits = [e for f, e in appels if f == 'auditer_narration']
        self.assertEqual(len(audits), 1)
        self.assertEqual(audits[0]['segments'], {'1': suite})
        self.assertEqual(emissions.lire(r), emissions.lire(m))
        self.assertIn(texte, sortie)
        self.assertEqual(recharger(r).data, r.data)

    def test_occurrences_identiques_et_discours_indirect_ne_sont_pas_confondus(self):
        m = recharger(self.scenes()[1])
        p = copy.deepcopy(m.data['emissions_parole'][-1])
        p.update(id=p['id'] + 1, ordre=p['ordre'] + 1)
        m.data['emissions_parole'].append(p)
        faits = dossier(m)
        texte = faits['echanges_passes']['aubin'][0]['rappel_exact']
        self.assertEqual(len(narration.preuves_rappels(faits)[texte]), 2)
        avant = copy.deepcopy(m.data)
        narration.consigner(m, reponse(texte, faits))
        self.assertEqual(emissions.lire(m), emissions.lire(avant))
        m.data['emissions_parole'][-1]['forme'] = 'discours_rapporte'
        m.data['emissions_parole'][0]['forme'] = 'discours_rapporte'
        self.assertNotIn(texte, narration.rappels_exacts(dossier(m)))

