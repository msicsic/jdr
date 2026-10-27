"""Les attributions du récit exigent un appui perçu, conservé après recharge."""
import copy
import unittest

from donjon import narration, rendu
from donjon.monde import ErreurMonde
from tests.test_parole_corrections import banc, audit, ligne
from tests.test_repli_et_appel import dialogue, jouer, mj
from tests.test_tensions import recharger


def attribution(appui, **changements):
    return dict(personnage=appui['personnage'], envers=appui['envers'],
                affirmation=appui['texte'], source=appui['id'],
                compatibilite='etablie') | changements


def rapport(appui, **changements):
    l = ligne('mecanique', sources=['signes_percus'])
    l['attitudes'] = [attribution(appui, **changements)]
    return audit(l)


class AttitudesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = banc('attitudes')

    def monde(self):
        return recharger(self.scene)

    def test_scene_et_projections_rechargees(self):
        m = self.monde()
        faits = m.contexte()
        self.assertTrue(any(s['personnage'] == 'ilse' and s['signe'] == 'ecart'
                            for s in faits['signes_percus']))
        self.assertTrue(any(s['personnage'] == 'marchand' and s['signe'] == 'surveille'
                            for s in faits['signes_percus']))
        self.assertTrue(any(c.get('dispute') for c in m.data['chronique']))
        self.assertTrue(faits['impressions'])
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(rendu.regarder(m), rendu.regarder(r))
        self.assertEqual(faits['signes_percus'], r.contexte()['signes_percus'])
        self.assertEqual(faits['impressions'], r.contexte()['impressions'])

    def test_console_refus_puis_signe_admis_deux_personnages(self):
        for qui in ('ilse', 'marchand'):
            with self.subTest(qui=qui):
                m = self.monde()
                appui = next(s for s in m.contexte()['signes_percus'] if s['personnage'] == qui)
                invente = ('Ilse rêve de te trahir.' if qui == 'ilse' else 'Gorm veut te dépouiller.')
                mauvais = rapport(appui, source='', affirmation=invente,
                                   compatibilite='sans_fondement')
                # Même déguisée en ambiance, l'attribution est refusée.
                mauvais['segments']['0']['verdict'] = 'ambiance'
                avant = copy.deepcopy(m.data)
                r, sortie, appels = jouer(m, 'décris les personnes',
                    [dialogue(invente), dialogue(appui['texte'])],
                    [mauvais, rapport(appui)], options=('--crue',))
                self.assertNotIn(invente, sortie)
                self.assertIn(appui['texte'], sortie)
                self.assertIn('signes_percus', str(mj(appels)[1]))
                self.assertIn('impressions', str(mj(appels)[1]))
                recharge = recharger(r)
                self.assertEqual(r.data, recharge.data)
                self.assertEqual(rendu.regarder(r), rendu.regarder(recharge))
                self.assertEqual(avant['objets'], recharge.data['objets'])
                self.assertIn(appui['texte'], recharge.data['conversation'][-1]['reponse'])
                self.assertNotIn(invente, str(recharge.data.get('narrations_mj')))

    def test_appui_exact_personnage_cible_et_sens(self):
        faits = self.monde().contexte()
        appui = faits['signes_percus'][0]
        for changement in ({'source': 'absent'}, {'personnage': 'brune'},
                           {'envers': 'joueur'}, {'compatibilite': 'sans_fondement'}):
            with self.subTest(changement=changement):
                r = narration.controler(appui['texte'], rapport(appui, **changement), faits)
                self.assertTrue(r['obstacles'])
                self.assertIn(appui['id'], str(r['obstacles'][0]['attendu']))
        impression = faits['impressions'][0]
        self.assertFalse(narration.controler(impression['texte'], rapport(impression), faits)['obstacles'])

    def test_parole_seule_ne_prouve_pas_emotion_et_schema_extrait(self):
        faits = self.monde().contexte()
        appui = faits['signes_percus'][0]
        faits['echanges_passes'] = {'ilse': [{'texte': 'Je suis heureuse.'}]}
        self.assertTrue(narration.controler('Ilse est heureuse.',
            rapport(appui, source='echanges_passes'), faits)['obstacles'])
        schema = narration.schema_audit(faits, 1)
        variantes = schema['properties']['segments']['properties']['0']['anyOf']
        self.assertTrue(all('attitudes' in v['required'] for v in variantes))
        parole = ligne('parole', 'ilse', 'Je suis heureuse.')
        parole['attitudes'] = []
        faits['interlocuteurs'] = {'ilse': {'nom': 'Ilse'}}
        self.assertFalse(narration.controler('Ilse dit : « Je suis heureuse. »',
                                            audit(parole), faits)['obstacles'])

    def test_dossier_reduit_ne_dispense_pas_du_controle(self):
        appui = self.monde().contexte()['signes_percus'][0]
        faits = {'resultat_resolu': {'faits': ['Tu poses la torche.']}}
        schema = narration.schema_audit(faits, 1)
        variantes = schema['properties']['segments']['properties']['0']['anyOf']
        self.assertTrue(all('attitudes' in v['required'] for v in variantes))
        self.assertTrue(narration.controler(appui['texte'], rapport(appui), faits)['obstacles'])

    def test_appui_revalide_avant_enregistrement(self):
        m = self.monde()
        faits = m.contexte()
        appui = next(s for s in faits['signes_percus'] if s['personnage'] == 'marchand')
        texte = appui['texte']
        controle = narration.controler(texte, rapport(appui), faits)
        reponse = {'texte': texte, '_audit': dict(texte_initial=texte,
            segments=controle['segments'], faits=faits, fondement=texte)}
        m.joueur['orientation'] = 'nord'
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as refus:
            narration.consigner(m, reponse)
        self.assertIn('signes_percus', refus.exception.attendu)
        self.assertEqual(avant, m.data)

