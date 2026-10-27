"""Une localisation demandée reste un renseignement sourcé, jamais une vérité cachée."""
import gzip
import json
from pathlib import Path
import unittest

from donjon import deliberation as d, planification as p
from donjon.echanges import enqueter, executer, reponse_localisation
from donjon.esprits import croire, croyance, lire, memoriser
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger, vivre
from tests.test_voix import aubin_cherche_gorm, hugues_cherche_anselme


def capture():
    with gzip.open(Path(__file__).with_name('data') / 'ou-est-221-aubin.json.gz', 'rt', encoding='utf8') as f:
        return Monde(json.load(f))


class LocalisationDemandeeTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_question_autonome_trajet_verification_et_retrouvailles(self):
        from tests.test_tensions import placer
        from tests.support import lier
        from donjon.esprits import connaitre
        m = aubin_cherche_gorm()
        # Scène d'auteur : le témoin présent a vu Gorm, qui repart pendant le trajet.
        placer(m, 'brune', 'beffroi', (2, 2))
        croire(m, 'aubin', 'brune', 'lieu', 'beffroi', 'vu', salle='beffroi', case=[2, 2])
        connaitre(m, 'brune', 'aubin')
        lier(m, 'brune', 'aubin', True, 'vu')
        lier(m, 'aubin', 'brune', True, 'vu')
        croire(m, 'brune', 'marchand', 'lieu', 'crypte', 'vu', salle='crypte', case=None)
        m, _ = vivre(self.recharge(m), 5)
        textes = [c['texte'] for c in m.data['chronique']]
        questions = [s for s in textes if 'Aubin demande à Brune où se trouve Gorm' in s]
        self.assertEqual(len(questions), 1)
        self.assertTrue(any('Aubin' in s and 'passe dans : Salle des vannes' in s for s in textes))
        self.assertTrue(any('Aubin retrouve Gorm' in s for s in textes))
        self.assertTrue(any(s['operation'] == 'enqueter_lieu' and s['de'] == 'brune'
                            for s in lire(m, 'aubin')['refus']))
        self.recharge(m)

    def test_capture_aubin_question_commune_et_reponse_ancienne(self):
        m = self.recharge(capture())
        etapes, trouve = p.rejoindre(m, 'aubin', 'marchand')
        self.assertFalse(trouve)
        self.assertEqual(etapes[0]['contenu'], {'localisation': 'marchand'})
        self.assertEqual(etapes[0]['cible'], 'ilse')
        lignes = []
        self.assertTrue(executer(m, 'aubin', etapes[0], lignes))
        m = self.recharge(m)
        c = croyance(m, 'aubin', 'marchand', 'lieu')
        self.assertEqual(c['valeur'], 'antichambre')
        self.assertTrue(c['source'].endswith('ilse'))
        self.assertEqual(c['origine']['minute'], 195)
        self.assertEqual(m.objets['marchand']['lieu'], 'chambre_cloche')
        self.assertTrue(any('où se trouve' in s['texte'] for s in m.data['chronique']))
        self.assertIn('minute 195', reponse_localisation(m, 'ilse', 'marchand', 'dit', [('marchand', 'antichambre')]))
        self.assertIsNotNone(p.rejoindre(m, 'aubin', 'marchand'))

    def test_indication_dementie_hors_memoire_et_sans_delai(self):
        m = capture()
        enqueter(m, 'aubin', 'ilse', sujet='marchand')
        croire(m, 'aubin', 'marchand', 'lieu', None, 'vu', salle=None, case=None)
        d.recherche_vaine(m, 'aubin', 'marchand', 'antichambre')
        for n in range(50):
            memoriser(m, 'aubin', {'type': 'preuve_eviction', 'numero': n})
        m.data['minutes'] += 200
        m = self.recharge(m)
        s = next(s for s in lire(m, 'aubin')['refus'] if s['operation'] == 'enqueter_lieu')
        self.assertTrue(d.tient(m, 'aubin', s))
        recours = p.s_enquerir(m, 'aubin', sujet='marchand')
        self.assertTrue(recours is None or recours[0]['qui'] != 'ilse')
        d.indice_recherche(m, 'aubin', 'echoppe', 'marchand', indice=['bruit', 2, 'marchand', [1, 1]])
        self.assertFalse(d.tient(self.recharge(m), 'aubin', s))

    def test_inconnu_et_refus_restent_sans_information_nouvelle(self):
        from tests.support import lier
        for refus in (False, True):
            m = capture()
            lire(m, 'ilse')['croyances'].pop('marchand', None)
            if refus:
                lier(m, 'ilse', 'aubin', False, 'vu')
            issue, dit = enqueter(m, 'aubin', 'ilse', sujet='marchand')
            self.assertEqual(issue, 'mefiance' if refus else 'rien')
            self.assertEqual(dit, [])
            self.assertIsNone(d.salle_crue(m, 'aubin', 'marchand'))
            m.data['minutes'] += 500
            m = self.recharge(m)
            s = next(s for s in lire(m, 'aubin')['refus'] if s['operation'] == 'enqueter_lieu')
            self.assertTrue(d.tient(m, 'aubin', s))

    def test_relais_et_dates_ne_rearment_pas_une_indication_verifiee(self):
        m = capture()
        enqueter(m, 'aubin', 'ilse', sujet='marchand')
        s = next(s for s in lire(m, 'aubin')['refus'] if s['operation'] == 'enqueter_lieu')
        d.recherche_vaine(m, 'aubin', 'marchand', 'antichambre')
        for source in ('dit:mael', 'dit:ilse', 'dit:mael'):
            m.data['minutes'] += 100
            croire(m, 'aubin', 'marchand', 'lieu', 'antichambre', source, salle='antichambre', case=None)
            croire(m, 'aubin', 'marchand', 'lieu', None, 'vu', salle=None, case=None)
            self.assertTrue(d.tient(self.recharge(m), 'aubin', s))

    def test_reponse_nefface_pas_un_constat_propre_recent(self):
        m = capture()
        croire(m, 'aubin', 'marchand', 'lieu', 'chambre_cloche', 'vu', salle='chambre_cloche', case=None)
        issue, dit = enqueter(m, 'aubin', 'ilse', sujet='marchand')
        self.assertEqual(issue, 'dit')
        self.assertEqual(dit, [('marchand', 'antichambre')])
        c = croyance(self.recharge(m), 'aubin', 'marchand', 'lieu')
        self.assertEqual(c['valeur'], 'chambre_cloche')
        self.assertEqual(c['source'], 'vu')

    def test_memoire_du_plan_invalidee_par_la_reponse(self):
        m = capture()
        self.assertEqual(p.rejoindre(m, 'aubin', 'marchand')[0][0]['cible'], 'ilse')
        enqueter(m, 'aubin', 'ilse', sujet='marchand')
        croire(m, 'aubin', 'marchand', 'lieu', None, 'vu', salle=None, case=None)
        etapes, _ = p.rejoindre(self.recharge(m), 'aubin', 'marchand')
        self.assertFalse(any(e['cible'] == 'ilse' and e.get('contenu', {}).get('localisation') == 'marchand'
                             for e in etapes))

    def test_autre_scenario_croyance_du_temoin_independante_du_reel(self):
        m = hugues_cherche_anselme()
        from tests.support import lier
        from donjon.esprits import connaitre
        lier(m, 'lucien', 'hugues', True, 'vu')
        connaitre(m, 'lucien', 'hugues')
        croire(m, 'lucien', 'anselme', 'lieu', 'etable', 'dit:odile', salle='etable', case=None)
        issue, dit = enqueter(m, 'hugues', 'lucien', sujet='anselme')
        self.assertEqual(issue, 'dit')
        self.assertEqual(dit, [('anselme', 'etable')])
        c = croyance(self.recharge(m), 'hugues', 'anselme', 'lieu')
        self.assertEqual(c['valeur'], 'etable')
        self.assertEqual(c['origine']['source'], 'dit:odile')
        self.assertEqual(m.objets['anselme']['lieu'], 'chambre_chaude')
        self.assertIn('minute 2', reponse_localisation(m, 'lucien', 'anselme', issue, dit))

    def test_auberge_question_executee_puis_indication_suivie(self):
        from tests.test_tensions import placer
        from tests.support import lier
        from donjon.esprits import connaitre
        m = hugues_cherche_anselme()
        # Scène d'auteur : Odile, présente, conserve une ancienne localisation.
        placer(m, 'odile', 'couloir', (2, 2))
        croire(m, 'hugues', 'odile', 'lieu', 'couloir', 'vu', salle='couloir', case=[2, 2])
        connaitre(m, 'odile', 'hugues')
        lier(m, 'odile', 'hugues', True, 'vu')
        lier(m, 'hugues', 'odile', True, 'vu')
        croire(m, 'odile', 'anselme', 'lieu', 'etable', 'vu', salle='etable', case=None)
        recours = p.s_enquerir(m, 'hugues', sujet='anselme')
        self.assertEqual(recours[0]['qui'], 'odile')
        self.assertTrue(executer(m, 'hugues', recours[1][0], []))
        m = self.recharge(m)
        self.assertEqual(d.salle_crue(m, 'hugues', 'anselme'), 'etable')
        m, _ = vivre(m, 3)
        textes = [c['texte'] for c in m.data['chronique']]
        self.assertTrue(any('Hugues' in s and 'passe dans : Étable' in s for s in textes), textes)
        self.recharge(m)

    def test_position_cachee_ne_change_ni_question_ni_reponse(self):
        plans, reponses = [], []
        for salle in ('crypte', 'echoppe'):
            m = capture()
            m.objets['marchand'].update(lieu=salle, position_salle=salle, position=[1, 1])
            plans.append(p.rejoindre(m, 'aubin', 'marchand'))
            reponses.append(enqueter(m, 'aubin', 'ilse', sujet='marchand'))
        self.assertEqual(plans[0], plans[1])
        self.assertEqual(reponses[0], reponses[1])

    def test_laps_entier_et_decoupe(self):
        m = self.recharge(capture())
        entier, _ = vivre(self.recharge(m), 3)
        decoupe, _ = vivre(self.recharge(m), 1)
        decoupe, _ = vivre(self.recharge(decoupe), 2)
        self.assertEqual(entier.data, decoupe.data)
        self.recharge(entier)
        self.assertEqual(regarder(entier), regarder(decoupe))

    def test_joueur_contenu_type_console_et_sauvegarde(self):
        from tests.test_parole_corrections import banc
        from tests.test_audits_attendu import jouer, ligne, rapport
        from tests.test_repli_et_appel import dialogue, parole
        m = banc('noms-dialogue')
        croire(m, 'aubin', 'marchand', 'lieu', 'crypte', 'vu', salle='crypte', case=None)
        mots = 'Aubin, où est Gorm ?'
        r, texte, appels = jouer(m, mots,
            [parole(mots, ('localisation', 'marchand', '', ''), personnage='aubin'),
             dialogue('Aubin dit avoir vu Gorm dans la crypte.')],
            [rapport(ligne('mecanique', sources=['conversation_validee']))])
        self.assertIn('Aubin dit avoir vu', texte)
        rechargee = self.recharge(r)
        self.assertIn('Aubin dit avoir vu Gorm dans la crypte.', str(rechargee.data['conversation']))
        c = croyance(rechargee, 'joueur', 'marchand', 'lieu')
        self.assertIsNotNone(c)
        self.assertEqual(c['origine']['source'], 'vu')
        faits = [e['faits']['conversation_validee']['faits'] for f, e in appels
                 if f == 'repondre_au_joueur' and 'conversation_validee' in e['faits']]
        self.assertTrue(any('minute' in str(f) and 'salle des vannes' in str(f) for f in faits), faits)
