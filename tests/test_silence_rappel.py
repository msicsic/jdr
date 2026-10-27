"""L'issue courante se contrôle sur ses sources, sans réécrire le passé."""
import copy
import unittest

from donjon import narration, rendu
from tests.test_parole_corrections import banc, audit, ligne, narration as entree
from tests.test_repli_et_appel import dialogue, jouer, parole
from tests.test_tensions import recharger


def actuelle():
    l = ligne('mecanique', sources=['conversation_validee'])
    l.update(portee_mecanique='etablie', rappels=[])
    return l


class SilenceRappelTests(unittest.TestCase):
    def test_absence_de_reponse_courante_apres_recharge(self):
        from donjon.esprits import lire
        m = banc('soir-noir')
        lire(m, 'ilse')['voix_entendues']['joueur'] = dict(
            minute=0, se_dit=None, mefiance=True, n=1)
        m = recharger(m)
        r, sortie, appels = jouer(m, '« Qui est là ? »', [
            parole('Qui est là ?', ('qui', '', '', ''), personnage='personne'),
            dialogue('Aucune réponse ne te parvient.')], [audit(actuelle())])
        self.assertIn('Aucune réponse ne te parvient.', sortie)
        self.assertEqual(entree(appels)['faits']['conversation_validee']['repondent'], [])
        recharge = recharger(r)
        self.assertEqual(recharge.data, r.data)
        self.assertEqual(rendu.regarder(recharge), rendu.regarder(r))
        self.assertIn('Aucune réponse ne te parvient.', recharge.data['conversation'][-1]['reponse'])
        self.assertFalse(recharge.data.get('paroles_pnj'))

    def test_temoins_du_cas_reel_et_autre_scene_apres_recharge(self):
        cas = [
            ('echanges', 'personne_2', 'Tu sais où est passé le gardien ?',
             'La femme sèche répond : « Je ne sais pas. »',
             'Le vieil homme voûté, qui a entendu ta question sans être interpellé, se tait.',
             'personne_1'),
            ('noms-dialogue', 'brune', 'Brune, bonsoir.',
             'Brune répond : « Bonsoir. »',
             'Aubin et Ilse, qui ont entendu ta demande sans être interpellés, gardent le silence.',
             'aubin'),
        ]
        for nom, qui, mots, reponse, silence, temoin in cas:
            with self.subTest(nom=nom):
                m = recharger(banc(nom))
                if nom == 'noms-dialogue':
                    m.data.setdefault('paroles_pnj', []).append(dict(
                        locuteur=temoin, texte='Je suis ici.', auditeurs=['joueur'],
                        revision=m.data['revision'], minute=m.data['minutes'],
                        salle=m.joueur['salle']))
                    m = recharger(m)
                avant = copy.deepcopy(m.data)
                l = ligne('parole', qui, 'Je ne sais pas.' if nom == 'echanges' else 'Bonsoir.')
                l['rappels'] = []
                r, sortie, appels = jouer(m, '« ' + mots + ' »', [
                    parole(mots, ('propos', '', '', ''), personnage=qui),
                    dialogue(reponse + ' ' + silence)], [audit(l, actuelle())])
                self.assertIn(silence, sortie)
                faits = entree(appels)['faits']
                self.assertIn(temoin, faits['conversation_validee']['temoins'])
                self.assertIn('se tai', faits['conversation_validee']['issue'])
                anciennes = [p for p in avant.get('paroles_pnj', []) if p['locuteur'] == temoin]
                self.assertEqual([p['texte'] for p in faits['echanges_passes'][temoin]],
                                 [p['texte'] for p in anciennes])
                recharge = recharger(r)
                self.assertEqual(recharge.data, r.data)
                self.assertEqual(rendu.regarder(recharge), rendu.regarder(r))
                self.assertIn(silence, recharge.data['conversation'][-1]['reponse'])
                self.assertEqual(recharge.data['jets'], avant['jets'])
                for identifiant, objet in avant['objets'].items():
                    for champ in ('salle', 'position', 'porteur', 'portions'):
                        self.assertEqual(recharge.objets[identifiant].get(champ), objet.get(champ))
                self.assertEqual([p for p in recharge.data['paroles_pnj'] if p['locuteur'] == temoin],
                                 anciennes)

    def test_sources_courantes_et_rappels_restent_deux_controles(self):
        faits = {'echanges_passes': {'aubin': []},
                 'conversation_validee': {'issue': 'Aubin te répond.'}}
        l = actuelle()
        l.update(verdict='contradictoire', portee_mecanique='contradictoire',
                 motif="L'issue établit une réponse.")
        self.assertTrue(narration.controler('Aubin se tait.', audit(l), faits)['obstacles'])
        l = actuelle()
        l['rappels'] = [dict(locuteur='aubin', affirmation='Il a déjà refusé.',
                            compatibilite='sans_fondement')]
        self.assertTrue(narration.controler('Il a déjà refusé.', audit(l), faits)['obstacles'])

