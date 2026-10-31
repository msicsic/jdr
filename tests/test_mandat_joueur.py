"""341 : la parole du joueur publie le contrat commun, sans jeu forcé."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, echanges, emissions, paroles, pnj
from donjon.esprits import croire, lire, percevoir
from donjon.monde import Monde, ErreurMonde
from donjon.planification import _etape
from donjon.rendu import fiche, decrire_comptes, regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_agendas_amener_fin import declarer
from tests.test_avis_menace import relation
from tests.test_engagement_deplacement import scene
from tests.test_social import placer
from tests.test_tensions import recharger
from tests.support import regarder as orienter


class MandatJoueurTests(unittest.TestCase):
    def scene(self, sorte='amener'):
        m, _ = scene('aubin')
        placer(m, 'brune', 'antichambre', [3, 5])
        placer(m, 'ilse', 'echoppe', [1, 1])
        orienter(m, 'joueur', 'aubin')
        orienter(m, 'aubin', 'joueur')
        orienter(m, 'marchand', 'joueur')
        relation(m, 'aubin', 'joueur', confiance=100, affection=100)
        relation(m, 'marchand', 'joueur', confiance=100, affection=100)
        for q in ('aubin', 'marchand'):
            percevoir(m, q)
            croire(m, q, 'brune', 'lieu', 'antichambre', 'vu', salle='antichambre', case=[3, 5])
        c = {'type': 'mandat', 'sorte': sorte, 'qui': ['brune']}
        if sorte == 'amener':
            c['lieu'] = 'chambre_cloche'
        else:
            c['fait'] = {'type': 'affirmation', 'sujet': 'brasero', 'attribut': 'lieu', 'valeur': 'antichambre'}
            for q in ('aubin', 'marchand'):
                croire(m, q, 'brasero', 'lieu', 'antichambre', 'savoir', salle='antichambre', case=None)
        return m, c

    def dire(self, m, c, cible='aubin', mots='Je te confie cette charge.'):
        mots = paroles._nom_court(m, cible) + ', ' + mots
        with patch.object(Monde, 'd20', return_value=20):
            return paroles.preparer_parole(m, {'personnage': cible, 'replique': mots,
                'contenu': [c], '_intention': f'« {mots} »'})

    def persiste(self, m):
        avant = copy.deepcopy(m.data)
        textes = fiche(m), decrire_comptes(m), regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual((fiche(n), decrire_comptes(n), regarder(n), scene_percue(n)), textes)
        return n

    def offrir(self, m, sorte='amener'):
        m = declarer(m, 'brune', 'chambre_cloche')
        p = {'qui': ['brune'], 'lieu': 'chambre_cloche'}
        if sorte == 'informer':
            p = {'qui': ['brune'], 'fait': {'type': 'affirmation', 'sujet': 'brasero',
                 'attribut': 'lieu', 'valeur': 'antichambre'}}
        mandat = {'parent': 'evacuer', 'sorte': sorte, 'parametres': p, 'echeance': m.data['minutes'] + 5}
        self.assertFalse(echanges.executer(m, 'marchand',
            _etape('confier', 'joueur', contenu={'mandat': mandat, 'objet': 'brune'}), []))
        return m, mandat

    def test_confier_deux_charges_jugement_execution_et_compte_rendu(self):
        for sorte in ('amener', 'informer'):
            with self.subTest(sorte=sorte):
                m, c = self.scene(sorte)
                m, r = self.dire(m, c)
                self.assertIn("J'accepte cette charge", str(r['faits']))
                self.assertFalse(emissions.reponses(r))
                enfant = agendas.projets(m, 'aubin')[0]
                self.assertEqual(enfant['origine']['type'], 'mandat')
                self.assertEqual(enfant['origine']['de'], 'joueur')
                parent = agendas.projets(m, 'joueur')[0]
                self.assertEqual(parent['jugements'][-1]['issue'], 'accepte')
                m = self.persiste(m)
                # Aubin n'a pas de mandataire connu disponible dans cette scène.
                for q in ('marchand', 'ilse'):
                    placer(m, q, 'echoppe', [1, 1] if q == 'marchand' else [3, 1])
                    lire(m, 'aubin')['croyances'].pop(q, None)
                # Aubin agit réellement ; les autres ne prennent pas de nouvelles initiatives.
                for q in ('brune', 'marchand', 'ilse'):
                    lire(m, q)['libre'] = 1000000
                with patch.object(Monde, 'd20', return_value=20):
                    pnj.avancer(m, ecouler(m, 6000), [], 6000)
                if sorte == 'amener':
                    self.assertEqual(agendas.en_cours(m, 'brune')[0]['condition']['lieu'], 'chambre_cloche')
                    lire(m, 'brune')['libre'] = 0
                    with patch.object(Monde, 'd20', return_value=20):
                        pnj.avancer(m, ecouler(m, 6000), [], 6000)
                    self.assertEqual(m.objets['brune']['lieu'], 'chambre_cloche')
                if sorte == 'amener':
                    placer(m, 'aubin', 'chambre_cloche', [1, 2])
                    orienter(m, 'aubin', 'brune')
                    percevoir(m, 'aubin')
                    croire(m, 'aubin', 'brune', 'lieu', m.objets['brune']['lieu'], 'vu',
                           salle=m.objets['brune']['lieu'], case=m.objets['brune']['position'])
                agendas.actualiser(m, 'aubin')
                # Retour en portée pour la voie commune 283.
                placer(m, 'aubin', m.joueur['salle'], [3, 4])
                orienter(m, 'aubin', 'joueur')
                percevoir(m, 'aubin')
                croire(m, 'aubin', 'joueur', 'lieu', m.joueur['salle'], 'entendu',
                       salle=m.joueur['salle'], case=m.joueur['position'])
                compte = agendas.compte_a_rendre(m, 'aubin')
                if compte is not None:
                    self.assertTrue(echanges.rendre_compte(m, 'aubin', compte, []))
                self.assertIn('compte_rendu', agendas.projets(m, 'aubin')[0])
                m = self.persiste(m)
                self.assertIn('déclare une réussite', fiche(m))
                self.assertTrue(agendas.projets(m, 'joueur')[0]['comptes_recus'])

    def test_offre_acceptee_ou_refusee_sans_execution_forcee(self):
        for sorte in ('amener', 'informer'):
            for accepter in (True, False):
                with self.subTest(sorte=sorte, accepter=accepter):
                    m, _ = self.scene()
                    m, _ = self.offrir(m, sorte)
                    m = self.persiste(m)
                    self.assertIn('Mandat m1 de Gorm', fiche(m))
                    self.assertEqual(agendas.projets(m, 'joueur'), [])
                    objets = copy.deepcopy(m.objets)
                    m, r = self.dire(m, {'type': 'reponse_mandat', 'offre': 'm1', 'accepter': accepter},
                                     'marchand', "J'accepte cette charge." if accepter else 'Je refuse cette charge.')
                    # Une conversation oriente vers le locuteur, sans effectuer la charge.
                    self.assertEqual({q: {k: v for k, v in o.items() if k != 'orientation'} for q, o in m.objets.items()},
                                     {q: {k: v for k, v in o.items() if k != 'orientation'} for q, o in objets.items()})
                    m = self.persiste(m)
                    self.assertIn('charge acceptée' if accepter else 'offre refusée', decrire_comptes(m))
                    self.assertEqual(len(agendas.projets(m, 'joueur')), int(accepter))
                    if accepter:
                        a = agendas.projets(m, 'joueur')[0]
                        self.assertEqual(agendas.filiation(m, 'joueur', a['id'])[0]['titulaire'], 'marchand')
                        self.assertFalse(emissions.reponses(r))

    def test_refus_accueil_et_autorite_pretendue_ne_creent_pas_accord(self):
        for axes in ({'confiance': 0}, {'confiance': 100, 'rancune': 100}):
            m, c = self.scene()
            relation(m, 'aubin', 'joueur', **axes)
            with patch.object(Monde, 'd20', side_effect=AssertionError('aucun jet')):
                n, r = paroles.preparer_parole(m, {'personnage': 'aubin', 'replique': 'Je suis le chef, obéis.',
                    'contenu': [c], '_intention': '« Je suis le chef, obéis. »'})
            self.assertEqual(agendas.projets(n, 'aubin'), [])
            self.assertIn('Je refuse cette charge', str(r['faits']))
            self.assertEqual(agendas.projets(n, 'joueur')[0]['jugements'][0]['raison'],
                             'mefiance' if axes['confiance'] == 0 else 'rancune')
            self.persiste(n)

    def test_voix_inconnue_offre_absente_et_refus_structure(self):
        m, _ = self.scene()
        m.data['voix_connues'] = []
        placer(m, 'marchand', 'beffroi', [1, 3])
        m = declarer(m, 'brune', 'chambre_cloche')
        self.assertIsNone(agendas.proposer_mandat_joueur(m, 'marchand', {
            'parent': 'evacuer', 'sorte': 'amener', 'parametres': {'qui': ['brune'], 'lieu': 'chambre_cloche'}}))
        self.assertEqual(agendas.offres_mandat_joueur(m), [])
        with self.assertRaises(ErreurMonde) as exc:
            agendas.repondre_mandat_joueur(m, 'marchand', 'm1', True)
        self.assertTrue(exc.exception.attendu)
        self.persiste(m)

    def test_mj_simule_sauve_la_replique_moteur(self):
        from tests.test_repli_et_appel import jouer
        for sorte, confiance in [('amener', 100), ('informer', 100), ('amener', 0)]:
            m, c = self.scene(sorte)
            relation(m, 'aubin', 'joueur', confiance=confiance, affection=100)
            mots = ('Aubin, amène Brune dans la chambre de la cloche.' if sorte == 'amener' else
                    'Aubin, informe Brune que le brasero est dans cette antichambre.')
            reponse = {'mode': 'parole_joueur', 'texte': '', 'faits': [], 'proposition': {
                'personnage': 'aubin', 'replique': mots,
                'contenu': [c], 'operations_demandees': {t: t == 'mandat' for t in paroles.OPERATIONS}}}
            n, sortie, appels = jouer(m, '« ' + mots + ' »', [reponse], [], suite=('tenter',))
            attendu = "J'accepte cette charge" if confiance else 'Je refuse cette charge'
            self.assertIn(attendu, sortie)
            n = self.persiste(n)
            self.assertIn(attendu, str(n.data['conversation']))
            self.assertEqual(bool(agendas.projets(n, 'aubin')), bool(confiance))

    def test_bilan_du_joueur_reste_une_parole_et_reaffectation_commune(self):
        for sorte in ('amener', 'informer'):
            m, _ = self.scene(sorte)
            m, mandat = self.offrir(m, sorte)
            m, _ = self.dire(m, {'type': 'reponse_mandat', 'offre': 'm1', 'accepter': True}, 'marchand')
            a = agendas.projets(m, 'joueur')[0]
            avant = copy.deepcopy(m.objets['brune'])
            m, r = self.dire(m, {'type': 'bilan_mandat', 'agenda': a['id'], 'issue': 'renonce'}, 'marchand')
            self.assertEqual(m.objets['brune'], avant)
            self.assertIn('compte rendu', str(r['faits']))
            self.assertEqual(agendas.projets(m, 'marchand')[0]['comptes_recus'][0]['contenu']['issue'], 'renonce')
            m = self.persiste(m)
            # Le retard est calculé sur les seules connaissances du mandant.
            parent = agendas.projets(m, 'marchand')[0]
            self.assertIn('echeance', parent['attributions'][0])
            m.data['minutes'] = parent['attributions'][0]['echeance'] + 1
            mandat['echeance'] = m.data['minutes'] + 5
            with patch.object(Monde, 'd20', return_value=20):
                self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'accepte')
            self.assertTrue(echanges.avertir_mandat(m, 'marchand', 'joueur', {
                'parent': 'evacuer', 'agenda': a['id']}, []))
            parent = agendas.projets(self.persiste(m), 'marchand')[0]
            self.assertEqual([x['titulaire'] for x in parent['attributions'] if x['etat'] == 'active'], ['aubin'])

    def test_union_structuree_refuse_champs_etrangers_et_recharge_corrompue(self):
        m, c = self.scene()
        for contenu in ({**c, 'valeur': 'autorite'}, {'type': 'reponse_mandat', 'offre': 'm1', 'accepter': 'oui'},
                        {**c, 'qui': ['inconnu']}):
            with self.assertRaises(ErreurMonde) as exc:
                self.dire(m, contenu)
            self.assertTrue(exc.exception.attendu)
        m, _ = self.offrir(m)
        m.data['offres_mandat_joueur'][0]['parent'] = 'agenda-secret-inexistant'
        with self.assertRaises(ErreurMonde):
            self.persiste(m)

    def test_voix_audible_inconnue_ou_pretendue_ne_revele_pas_un_mandant(self):
        from donjon.voix import identifie, se_nommer
        from donjon.ouie import saisit
        for pretend in (False, True):
            m, _ = self.scene()
            m = declarer(m, 'brune', 'chambre_cloche')
            m.data['voix_connues'] = []
            for o in m.objets.values():
                if 'allume' in o:
                    o['allume'] = False
            self.assertFalse(m.visible('marchand'))
            self.assertTrue(saisit(m, 'marchand', 'joueur', 'dire'))
            if pretend:
                se_nommer(m, 'joueur', 'marchand', 'aubin')
            self.assertFalse(identifie(m, 'joueur', 'marchand'))
            mandat = {'parent': 'evacuer', 'sorte': 'amener',
                      'parametres': {'qui': ['brune'], 'lieu': 'chambre_cloche'}}
            echanges.executer(m, 'marchand', _etape('confier', 'joueur',
                contenu={'mandat': mandat, 'objet': 'brune'}), [])
            self.assertEqual(agendas.offres_mandat_joueur(m), [])
            self.assertNotIn('Mandat m1', fiche(self.persiste(m)))

    def test_devis_du_joueur_sans_lire_ses_capacites_privees(self):
        m, _ = self.scene('informer')
        m, mandat = self.offrir(m, 'informer')
        transmis = [('brune', 'lieu'), ('brasero', 'lieu')]
        avant = copy.deepcopy(m.data)
        duree = []
        devis = agendas.devis_observateur(m, 'marchand', 'evacuer', 'joueur', 'informer',
                                         mandat['parametres'], transmis=transmis, duree=duree)
        self.assertIsNotNone(devis)
        self.assertEqual(m.data, avant)
        m.joueur['stats'].update(INT=1, CHA=1, FOR=20)
        autre_duree = []
        self.assertEqual(agendas.devis_observateur(m, 'marchand', 'evacuer', 'joueur', 'informer',
            mandat['parametres'], transmis=transmis, duree=autre_duree), devis)
        self.assertEqual(duree, autre_duree)
        self.persiste(m)

    def test_charge_du_banc_apres_information_sans_jet_force(self):
        from tests.test_parole_corrections import banc
        m = banc('mandat-joueur')
        def prononcer(c, mots):
            nonlocal m
            m, r = paroles.preparer_parole(m, {'personnage': 'aubin', 'replique': mots,
                'contenu': [c], '_intention': mots})
            return r
        prononcer({'type': 'mandat', 'sorte': 'informer', 'qui': ['brune'], 'fait': {
            'type': 'affirmation', 'sujet': 'brasero', 'attribut': 'lieu', 'valeur': 'antichambre'}},
            "Aubin, je te confie la charge d'informer Brune que le brasero est dans l'antichambre.")
        self.assertEqual(agendas.projets(m, 'joueur')[0]['jugements'][-1]['issue'], 'impossible')
        prononcer({'type': 'affirmation', 'sujet': 'brune', 'attribut': 'lieu', 'valeur': 'antichambre'},
                  'Aubin, Brune est ici, dans le refuge du relais.')
        r = prononcer({'type': 'mandat', 'sorte': 'informer', 'qui': ['brune'], 'fait': {
            'type': 'affirmation', 'sujet': 'fanal', 'attribut': 'lieu', 'valeur': 'antichambre'}},
            "Aubin, je te confie la charge d'informer Brune que le fanal est dans le refuge du relais.")
        jugement = agendas.projets(m, 'joueur')[-1]['jugements'][-1]
        self.assertEqual(jugement['issue'], 'accepte')
        self.assertIn('autorite', jugement)
        self.assertIn("J'accepte cette charge", str(r['faits']))
        m = self.persiste(m)
        self.assertEqual(agendas.projets(m, 'aubin')[0]['origine']['type'], 'mandat')
        self.assertIn("J'accepte cette charge", emissions.pnj(m)[-1]['texte'])
        from tools.banc_parties import resume_etat
        self.assertEqual(resume_etat(m)['charges_joueur'][-1]['jugements'][-1]['issue'], 'accepte')

    def test_references_du_banc_connues_explicitement_et_refusees_sans_souvenir(self):
        from tests.test_parole_corrections import banc
        for reference, contenu in (
            ('brasero', {'type': 'mandat', 'sorte': 'informer', 'qui': ['brune'], 'fait': {
                'type': 'affirmation', 'sujet': 'brasero', 'attribut': 'lieu', 'valeur': 'antichambre'}}),
            ('echoppe', {'type': 'mandat', 'sorte': 'amener', 'qui': ['brune'], 'lieu': 'echoppe'}),
        ):
            with self.subTest(reference=reference):
                m = banc('mandat-joueur')
                self.assertIn(reference, m.data['connus'])
                m.data['connus'].remove(reference)
                m = self.persiste(m)
                self.assertFalse(paroles._connu_du_joueur(m, reference))
                self.assertIsNone(paroles.resoudre(m, reference))
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as refus:
                    self.dire(m, contenu)
                self.assertTrue(refus.exception.attendu)
                self.assertEqual(m.data, avant)
                self.assertFalse(agendas.projets(m, 'joueur'))
                m = self.persiste(m)
                # Un souvenir donne le droit de désigner, sans établir ni
                # la position du bien ni la réussite de la charge.
                m.data['connus'].append(reference)
                m = self.persiste(m)
                self.assertEqual(paroles.resoudre(m, reference), reference)
                objets = copy.deepcopy(m.objets)
                n, r = self.dire(m, contenu)
                self.assertTrue(agendas.projets(n, 'joueur'))
                self.assertIn('charge', str(r['faits']))
                self.assertEqual(n.objets[reference] if reference in n.objets else n.data['salles'][reference],
                                 objets[reference] if reference in objets else m.data['salles'][reference])
                n = self.persiste(n)
                self.assertEqual(paroles.resoudre(n, reference), reference)

    def test_fait_confie_distinct_de_l_affirmation_directe_apres_recharge(self):
        from tests.test_repli_et_appel import jouer
        for sujet in ('brasero', 'fanal'):
            m, c = self.scene('informer')
            c['fait']['sujet'] = sujet
            croire(m, 'aubin', sujet, 'lieu', 'echoppe', 'savoir', salle='echoppe', case=None)
            mots = f"Aubin, je te confie la charge d'informer Brune que le {sujet} est dans l'antichambre."
            bonne = {'mode': 'parole_joueur', 'texte': '', 'faits': [], 'proposition': {
                'personnage': 'aubin', 'replique': mots, 'contenu': [c],
                'operations_demandees': {t: t == 'mandat' for t in paroles.OPERATIONS}}}
            mauvaise = copy.deepcopy(bonne)
            mauvaise['proposition']['operations_demandees']['affirmation'] = True
            n, sortie, appels = jouer(m, mots, [mauvaise, bonne], [], suite=('tenter',))
            retours = [e.get('faits', {}).get('retour_moteur', {}) for _, e in appels]
            self.assertTrue(any('affirmation' in str(r.get('attendu', '')) for r in retours))
            self.assertIn('Je refuse cette charge', sortie)
            n = self.persiste(n)
            self.assertEqual(lire(n, 'aubin')['croyances'][sujet]['lieu']['valeur'], 'echoppe')
            self.assertEqual(agendas.projets(n, 'joueur')[0]['jugements'][-1]['issue'], 'impossible')

    def test_revue_nomme_les_references_aux_deux_profondeurs(self):
        from tests.test_repli_et_appel import jouer
        for sorte in ('informer', 'amener'):
            with self.subTest(sorte=sorte):
                m, c = self.scene(sorte)
                destination = c['fait']['valeur'] if sorte == 'informer' else c['lieu']
                nom = m.data['salles'][destination]['nom']
                charge = (f'informer Brune que le brasero est dans {nom}' if sorte == 'informer'
                          else f'amener Brune dans {nom}')
                mots = 'Aubin, je te confie la charge de ' + charge + '.'
                p = {'mode': 'parole_joueur', 'texte': '', 'faits': [], 'proposition': {
                    'personnage': 'aubin', 'replique': mots, 'contenu': [c],
                    'operations_demandees': {t: t == 'mandat' for t in paroles.OPERATIONS}}}
                n, sortie, appels = jouer(m, mots, [p], [], suite=('tenter',))
                self.assertIn("J'accepte cette charge", sortie)
                n = self.persiste(n)
                self.assertIn("J'accepte cette charge", str(n.data['conversation']))
                self.assertEqual(agendas.projets(n, 'joueur')[0]['jugements'][-1]['issue'], 'accepte')
                revue = next(e for f, e in appels if f == 'auditer_action')
                contenu = revue['plan']['parole']['contenu'][0]
                lieu_revu = contenu['fait']['valeur'] if sorte == 'informer' else contenu['lieu']
                self.assertEqual(lieu_revu, f'{nom} ({destination})')
                self.assertIn('(brune)', contenu['qui'][0])


if __name__ == '__main__':
    unittest.main()
