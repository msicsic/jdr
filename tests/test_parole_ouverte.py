"""D0 : deux PNJ, vraie console et sauvegarde, sans connaissance ni engagement."""
import copy
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon import emissions, paroles
from donjon.dialogues import interlocuteurs
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.spatial import memoriser
from tests.support import presentes
from tests.test_repli_et_appel import jouer
from tests.test_tensions import recharger


def scene(scenario, auteur):
    m = presentes(creer(scenario, 1985, 'fixe'))
    o = m.objets[auteur]
    m.joueur.update(salle=o['lieu'], position=[o['position'][0], o['position'][1] + 1], orientation='nord')
    memoriser(m)
    assert auteur in interlocuteurs(m)
    return recharger(m)


def proposition(auteur, texte='Quand je débutais, le vent me faisait toujours perdre mon chapeau.'):
    return {'personnage': auteur, 'sujet': 'souvenir_personnel',
            'contenu': {'type': 'propos', 'texte': texte, 'sources': []}}


def reponse(p):
    return {'mode': 'parole_ouverte', 'texte': '', 'faits': [],
            'proposition': {k: p[k] for k in ('personnage', 'sujet')}}


def admission(types=('propos',), sources=(), compatible=True):
    return {'types': list(types), 'sources': list(sources), 'compatible': compatible, 'motif': ''}


class ParoleOuverteTests(unittest.TestCase):
    def scenes(self):
        for scenario, auteur in [('relais', 'marchand'), ('auberge', 'odile')]:
            yield scene(scenario, auteur), auteur

    def assertMondeInchange(self, avant, apres, exceptions=()):
        for cle in avant.data:
            if cle not in ('conversation', 'narrations_mj', *exceptions):
                self.assertEqual(avant.data[cle], apres.data[cle], cle)
        recharge = recharger(apres)
        self.assertEqual(apres.data, recharge.data)
        self.assertEqual(regarder(apres), regarder(recharge))
        self.assertEqual(scene_percue(apres), scene_percue(recharge))

    def test_souvenir_reel_et_autre_pnj_sauves_puis_restitues_sans_formulation(self):
        for m, auteur in self.scenes():
            with self.subTest(auteur=auteur):
                p = proposition(auteur)
                saisie = 'Quel souvenir personnel pourrait raconter cette personne ?'
                r, sortie, appels = jouer(m, saisie, [reponse(p), p['contenu'], admission()], [])
                self.assertIn(p['contenu']['texte'], sortie)
                flux = emissions.lire(r)
                self.assertEqual(len(flux), len(emissions.lire(m)) + 1)
                emission = flux[-1]
                self.assertEqual(emission['acte'], 'parole_ouverte')
                self.assertEqual(emission['locuteur'], auteur)
                self.assertIn('joueur', emission['auditeurs'])
                self.assertEqual(emission['parametres']['sujet'], p['sujet'])
                self.assertIn(p['contenu']['texte'], r.data['conversation'][-1]['reponse'])
                self.assertMondeInchange(m, r, ('revision', 'emissions_parole'))
                self.assertEqual(sum(f == 'admettre_parole_ouverte' for f, _ in appels), 1)
                self.assertEqual(sum(f == 'formuler_parole_ouverte' for f, _ in appels), 1)
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
                self.assertTrue(interlocuteurs(r)[auteur]['sujets_ouverts'][p['sujet']]['deja_entendu'])
                p['contenu']['texte'] = ''
                r2, sortie2, appels2 = jouer(recharger(r), saisie, [reponse(p)], [])
                self.assertIn(emission['texte'], sortie2)
                self.assertIn('Tu as entendu', sortie2)
                self.assertMondeInchange(r, r2)
                self.assertEqual([f for f, _ in appels2], ['repondre_au_joueur'])

    def test_secret_garde_et_promesse_non_typee_refuses_dans_la_boucle(self):
        for m, auteur in self.scenes():
            m.data['savoirs_pnj'][auteur]['confidence_fermee'] = {
                'texte': 'Je cachais autrefois mes économies sous mon oreiller.', 'origine': 'jeu', 'revision': 0}
            for verdict, message in ((admission(sources=['confidence_fermee']), 'garde ce savoir'),
                            (admission(types=['promesse']), 'engagement non admis'),
                            (admission(types=['accord']), 'engagement non admis'),
                            (admission(sources=['savoir_inexistant']), 'ne connaît pas'),
                            (admission(compatible=False), 'ne peut pas être admis')):
                with self.subTest(auteur=auteur, verdict=verdict):
                    mots = ('Tu peux compter sur moi pour te donner mes économies.'
                            if 'promesse' in verdict['types'] else
                            'Nous sommes convenus de cet échange.' if 'accord' in verdict['types'] else
                            'Je cachais autrefois mes économies sous mon oreiller.'
                            if verdict['sources'] == ['confidence_fermee'] else
                            proposition(auteur)['contenu']['texte'])
                    p = proposition(auteur, mots)
                    r, sortie, _ = jouer(m, 'Quel souvenir personnel pourrait raconter cette personne ?',
                                        [reponse(p), p['contenu'], verdict], [])
                    self.assertNotIn(mots, sortie)
                    self.assertIn(message, r.data['conversation'][-1]['reponse'])
                    self.assertMondeInchange(m, r)
                    self.assertFalse(emissions.lire(r))

    def test_refus_types_avec_attendu_et_aucune_mutation(self):
        for m, auteur in self.scenes():
            for type_contenu in ('promesse', 'accord'):
                p = proposition(auteur)
                p['contenu']['type'] = type_contenu
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as refus:
                    paroles.preparer_ouverte(m, p, m.data['revision'])
                self.assertIn(type_contenu, refus.exception.attendu)
                self.assertEqual(avant, m.data)

    def test_admission_liee_aux_mots_et_revision_rejouee(self):
        for m, auteur in self.scenes():
            p = proposition(auteur)
            p['_admission'] = {'proposition': copy.deepcopy(p), 'revision': m.data['revision'], 'verdict': admission()}
            p['contenu']['texte'] = 'Autres mots que ceux examinés.'
            with self.assertRaises(ErreurMonde) as refus:
                paroles.preparer_ouverte(m, p, m.data['revision'])
            self.assertIn('_admission', refus.exception.attendu)

    def test_autre_interlocuteur_n_herite_pas_du_sujet_entendu(self):
        m, auteur = next(self.scenes())
        r, _, _ = jouer(m, 'Quel souvenir personnel pourrait raconter cette personne ?',
                         [reponse(proposition(auteur)), proposition(auteur)['contenu'], admission()], [])
        self.assertIsNone(paroles.ouverte_connue(r, auteur, 'souvenir_personnel', 'brune'))
        self.assertIsNone(paroles.ouverte_connue(r, 'brune', 'souvenir_personnel'))

    def test_echec_sauvegarde_ne_publie_aucun_mot(self):
        for m, auteur in self.scenes():
            sauver = Monde.sauver
            def echec(copie, chemin):
                if any(p['acte'] == 'parole_ouverte' for p in emissions.lire(copie)):
                    raise OSError('disque indisponible')
                return sauver(copie, chemin)
            with patch.object(Monde, 'sauver', echec):
                r, sortie, _ = jouer(m, 'Quel souvenir personnel pourrait raconter cette personne ?',
                                     [reponse(proposition(auteur)), proposition(auteur)['contenu'], admission()], [])
            self.assertNotIn(proposition(auteur)['contenu']['texte'], sortie)
            self.assertFalse(emissions.lire(r))
            self.assertMondeInchange(m, r)


if __name__ == '__main__':
    unittest.main()
