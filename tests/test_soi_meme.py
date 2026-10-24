"""Une accusation reçue ne devient pas une confidence sur soi, après recharge."""
import copy
import unittest
from unittest.mock import patch

from donjon import signes, social
from donjon.esprits import lire, memoriser
from donjon.paroles import aveu
from donjon.recit_pnj import Recit
from tests.support import calme, regarder
from tests.test_social import attendre, placer, recharger, relais


def scene(accuse, locuteur, objet):
    m = calme(relais(), 'marchand', 'aubin', 'brune', 'ilse')
    for id, p in zip(('aubin', 'brune', 'marchand', 'ilse'),
                     ([3, 4], [4, 5], [3, 5], [2, 5])):
        placer(m, id, 'antichambre', p)
        regarder(m, id, 'joueur')
    m.joueur.update(salle='antichambre', position=[2, 4], orientation='est')
    m.objets[objet].update(lieu=accuse, proprietaire=locuteur)
    m.objets[objet].pop('position', None)
    regarder(m, locuteur, accuse)
    regarder(m, accuse, locuteur)
    return recharger(m)


class AccusationTests(unittest.TestCase):
    cas = (('brune', 'aubin', 'planches'), ('ilse', 'marchand', 'marteau'))

    def test_accusation_directe_et_surprise_passent_par_la_meme_reception(self):
        for accuse, locuteur, objet in self.cas:
            for type in ('vu_porter', 'intention_lue'):
                with self.subTest(accuse=accuse, type=type):
                    self.accusation_directe(accuse, locuteur, objet, type)

    def accusation_directe(self, accuse, locuteur, objet, type):
        m = scene(accuse, locuteur, objet)
        noyau = {'type': type, 'auteur': accuse, 'objet': objet}
        if type == 'intention_lue':
            from donjon.esprits import croire
            # Le grief porte sur le guet, sans vol concurrent à regrouper.
            m.objets[objet]['proprietaire'] = accuse
            noyau.update(signe='lecture', confiance=.6)
            croire(m, locuteur, accuse, 'intention', 'guet', 'devine', .6,
                   signe='lecture', envers=objet)
        memoriser(m, locuteur, noyau)
        signes.eprouver(m, locuteur, accuse, 'vu_porter', {'rancune': 40})
        self.assertEqual(social._auditeur(m, locuteur, lire(m, locuteur)['memoire'][-1],
                                          noyau, None), accuse)
        # La vraie minute du moteur prononce la confidence et la fait entendre.
        m, texte = attendre(recharger(m), jet=20)
        nom = m.objets[locuteur]['nom'].split(',')[0]
        cible = m.objets[accuse]['nom'].split(',')[0]
        dit = f'{cible} ' + ('porte' if type == 'vu_porter' else 'semble guetter')
        self.assertIn(f'{nom} glisse à {cible} que {dit}', texte)
        self.assertEqual(m.objets[objet]['lieu'], accuse)
        self.assertFalse(any(s['type'] == 'rumeur' and social.accuse(s['evenement']) == accuse
                             for s in lire(m, accuse)['memoire']))
        self.assertFalse(any(social.accuse(n) == accuse for _, n, *_ in social.nouvelles(m, accuse)))
        # Le récit rechargé conserve l'accusateur ; l'accusé n'a rien répété sur lui.
        recit = '\n'.join(Recit(m).entre_eux(m, m.data['chronique']))
        self.assertIn(f'{nom} dit à {cible} que {dit}', recit)
        self.assertNotIn(f'{cible} dit à', recit)
        tiers = next(x for x in ('ilse', 'aubin') if x not in (accuse, locuteur))
        self.assertTrue(any(s['type'] == 'parole' and s['locuteur'] == locuteur
                            for s in lire(m, tiers)['memoire']))

    def test_ancienne_rumeur_contre_soi_ne_se_retransmet_pas(self):
        for accuse, locuteur, objet in self.cas:
            for type in ('vu_porter', 'intention_lue', 'mensonge_dementi'):
                with self.subTest(accuse=accuse, type=type):
                    m = scene(accuse, locuteur, objet)
                    n = ({'type': type, 'locuteur': accuse, 'sujet': objet, 'attribut': 'lieu'}
                         if type == 'mensonge_dementi' else
                         {'type': type, 'auteur': accuse, 'objet': objet})
                    if type == 'intention_lue':
                        n.update(signe='ancien', confiance=.6)
                    memoriser(m, accuse, {'type': 'rumeur', 'de': locuteur, 'rang': 1, 'evenement': n})
                    m, texte = attendre(recharger(m), jet=20)
                    self.assertEqual(m.objets[objet]['lieu'], accuse)
                    nom = m.objets[accuse]['nom'].split(',')[0]
                    self.assertFalse(any(c['nature'] == 'social' and c['pnj'] == accuse
                                         for c in m.data.get('chronique', [])))
                    self.assertNotIn(f'{nom} glisse', texte)
                    self.assertFalse(any(social.accuse(n) == accuse for _, n, *_ in social.nouvelles(m, accuse)))

    def test_seul_un_aveu_explicitement_type_accuse_son_locuteur(self):
        for locuteur, auditeur, objet in (('joueur', 'marchand', 'marteau'),
                                         ('brune', 'aubin', 'planches')):
            with self.subTest(locuteur=locuteur):
                m = scene('brune', auditeur, objet)
                # La voix du joueur est déjà identifiée dans cette scène d'auteur.
                if locuteur not in lire(m, auditeur)['voix']:
                    lire(m, auditeur)['voix'].append(locuteur)
                contenu = aveu(m, locuteur, objet, 'prendre')
                self.assertIsNotNone(contenu)
                faux = dict(contenu, type='rumeur', rang=0)
                self.assertIsNone(social.recevoir(m, auditeur, locuteur, faux))
                self.assertEqual(social.recevoir(m, auditeur, locuteur, contenu), 'crue')
                m = recharger(m)
                s = next(s for s in lire(m, auditeur)['memoire'] if s['type'] == 'rumeur')
                self.assertTrue(s['aveu'])
                self.assertEqual(social.accuse(s['evenement']), locuteur)
                from donjon.relations import envers
                self.assertIn('aveu', [x['type'] for x in envers(m, auditeur, locuteur)['motifs']])


class SignesPropresTests(unittest.TestCase):
    def test_ni_les_signes_visuels_ni_les_tons_ne_se_lisent_soi_meme(self):
        for id in ('joueur', 'brune'):
            with self.subTest(id=id):
                m = scene('brune', 'aubin', 'planches')
                for canal in ('convoite', 'hesite'):
                    signe = signes._signe(m, id, canal, 'reserve', 'guet')
                    signe.update(niveau=2, distance=0)
                    avant = copy.deepcopy(m.data)
                    with patch('donjon.signes._jet', return_value=20) as jet:
                        signes.lire(m, id, [signe])
                    jet.assert_not_called()
                    self.assertEqual(m.data.get('lectures'), avant.get('lectures'))
                    self.assertFalse(any(x == id for x, *_ in signes.actives(m, id)))
                    self.assertFalse(any(s['personnage'] == id for s in signes.percus(m, id, tons=[signe])))
                    m = recharger(m)
                    self.assertFalse(any(x == id for x, *_ in signes.actives(m, id)))
                    self.assertFalse(any(s['personnage'] == id for s in signes.publics(m, id)))
