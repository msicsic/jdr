"""L'emploi perçu d'un moyen reste pertinent hors d'une tâche active."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import banc_pnj, echanges, esprits, social, pnj
from donjon.monde import Monde, ErreurMonde
from donjon.rendu import regarder as rendu
from donjon.temps import ecouler
from tests.support import regarder, lier
from tests.test_constats_partages import scene
from tests.test_deja_dit import confier
from tests.test_social import placer, recharger


class PreuveUsageTests(unittest.TestCase):
    def stable(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        return n

    def test_capture_141_mine_preuve_du_service_reel_puis_biscuits(self):
        # La capture 249 est antérieure au schéma. Rejouer la vraie acquisition
        # à 1 min, sans interpréter ses anciens souvenirs textuels à 141.
        debut = banc_pnj.creer('mine', 1985, 'tire')
        banc_pnj.executer(debut, 2)
        preuve = esprits.lire(debut, 'josse')['croyances']['mathe']['usage:vivres']
        self.assertTrue(preuve['valeur'])
        self.assertEqual(preuve['source'], 'dit:mathe')
        self.assertTrue(any(c['pnj'] == 'mathe' and 'à Rémy' in c['texte']
                            for c in debut.data['chronique']))
        m = Monde(json.loads(gzip.decompress((Path(__file__).parent /
                    'data/usage-250-mine141.json.gz').read_bytes())))
        n = {'type': 'constat', 'objet': 'biscuits_1', 'attribut': 'etat',
             'valeur': {'disponible': False}, 'observe': 141}
        self.assertFalse(social._utile(m, 'josse', 'mathe', n))
        esprits.lire(m, 'josse')['croyances']['mathe']['usage:vivres'] = copy.deepcopy(preuve)
        m = self.stable(m)
        self.assertTrue(social._utile(m, 'josse', 'mathe', n))
        m.joueur.update(salle=m.objets['josse']['lieu'], position=[4, 4])
        regarder(m, 'joueur', 'josse')
        m.data['connus'] = sorted(m.objets)
        m.data['noms_connus'] = [x for x, o in m.objets.items() if o['type'] == 'personnage']
        textes = []
        for _ in range(4):
            m, dit, texte = confier(self.stable(m), 'josse')
            textes.append(texte)
            if social.deja_dit(m, 'josse', 'mathe', n):
                break
            ecouler(m, 600)  # Un créneau de confidence par minute.
        self.assertTrue(social.deja_dit(m, 'josse', 'mathe', n))
        self.assertIn('biscuits de secours sont épuisés', '\n'.join(textes))
        self.assertFalse(esprits.lire(m, 'mathe')['croyances']['biscuits_1']['etat']['valeur']['disponible'])
        self.assertEqual(m.objets['biscuits_1']['portions'], 0)
        resultats = []
        restant = (193 - m.data['minutes']) * 600
        for tranches in ((restant,), (restant // 4,) * 4):
            suite = self.stable(m)
            choix = []
            from donjon import deliberation
            original = deliberation.choisir
            def observer(monde, qui, minute):
                r = original(monde, qui, minute)
                if qui == 'mathe' and 191 <= minute <= 193:
                    choix.append(copy.deepcopy(esprits.lire(monde, qui)['intention']))
                return r
            with patch.object(deliberation, 'choisir', observer):
                for dt in tranches:
                    pnj.avancer(suite, ecouler(suite, dt), [], dt)
                    suite = self.stable(suite)
            self.assertTrue(choix)
            self.assertFalse(any(g['operation'] == 'demander' and g.get('outil') == 'biscuits_1'
                                 for i in choix if i for g in i.get('plan', [])))
            resultats.append((suite.data, rendu(suite)))
        self.assertEqual(*resultats)

    def test_autre_moyen_service_vu_support_cru_dementi_et_pas_de_fuite(self):
        m = scene()
        # Gorm, sans froid visible, entretient le feu pour un tiers. Le geste
        # public établit l'emploi du combustible, pas le besoin de ce tiers.
        esprits.croire(m, 'ilse', 'marchand', 'etat', {'faim': False, 'chaleur': False}, 'vu')
        m.objets['bois'].update(lieu='marchand', proprietaire='brune')
        m.objets['brasero'].update(lieu='antichambre', position=[3, 4], position_salle='antichambre')
        placer(m, 'marchand', 'antichambre', [3, 4])
        regarder(m, 'ilse', 'marchand')
        self.assertTrue(esprits.percoit(m, 'ilse', 'marchand'))
        self.assertTrue(esprits.percoit(m, 'ilse', 'bois'))
        placer(m, 'brune', 'antichambre', [3, 5])
        esprits.lire(m, 'brune')['besoins']['chaleur'] = 90
        regarder(m, 'marchand', 'brasero')
        avant = m.objets['brasero']['combustible']
        self.assertTrue(pnj._executer(m, 'marchand', {'operation': 'alimenter',
            'cible': 'brasero', 'outil': 'bois', 'lieu': '', 'condition': ''}, [], []))
        self.assertGreater(m.objets['brasero']['combustible'], avant)
        self.assertTrue(esprits.lire(m, 'ilse')['croyances']['marchand']['usage:bois']['valeur'])
        esprits.croire(m, 'ilse', 'bois', 'lieu', 'reserve', 'vu', salle='echoppe', case=[4, 3])
        n = {'type': 'constat', 'objet': 'reserve', 'attribut': 'verrouillee', 'valeur': True}
        self.assertTrue(social._utile(self.stable(m), 'ilse', 'marchand', n))
        m.objets['bois']['lieu'] = 'crypte'  # Aucun savoir distant sur le support.
        self.assertTrue(social._utile(self.stable(m), 'ilse', 'marchand', n))
        self.assertNotIn('usage:bois', esprits.lire(m, 'brune')['croyances'].get('marchand', {}))
        esprits.retenir_usage(m, 'ilse', 'marchand', 'bois', 'dit:marchand', actif=False)
        self.assertFalse(social._utile(self.stable(m), 'ilse', 'marchand', n))
        # La reprise d'emploi rouvre l'information matérielle ; transmission,
        # monde et rendu suivent le même laps entier ou découpé.
        esprits.retenir_usage(m, 'ilse', 'marchand', 'bois', 'dit:marchand')
        m.objets['bois']['charges'] = 0
        esprits.croire(m, 'ilse', 'bois', 'etat', {'disponible': False}, 'essai')
        esprits.lire(m, 'marchand')['libre'] = 10000
        m, dit, texte = confier(self.stable(m))
        self.assertTrue(dit)
        self.assertIn('fagots', texte)
        self.assertIn('épuisés', texte)
        resultats = []
        for tranches in ((600,), (150,) * 4):
            suite = self.stable(m)
            with patch.object(Monde, 'd20', return_value=20):
                for dt in tranches:
                    pnj.avancer(suite, ecouler(suite, dt), [], dt)
                    suite = self.stable(suite)
            self.assertEqual(suite.objets['bois']['charges'], 0)
            resultats.append((suite.data, rendu(suite)))
        self.assertEqual(*resultats)

    def test_demande_entendue_identifiee_et_dementie_sans_analyse_du_texte(self):
        m = scene()
        esprits.croire(m, 'ilse', 'marchand', 'etat', {'faim': False, 'chaleur': False}, 'vu')
        moyen = 'bois'
        n = {'type': 'constat', 'objet': moyen, 'attribut': 'etat', 'valeur': {'disponible': False}}
        self.assertFalse(social._utile(m, 'ilse', 'marchand', n))
        lier(m, 'ilse', 'marchand', True)
        m.objets[moyen]['proprietaire'] = 'ilse'
        esprits.croire(m, 'ilse', moyen, 'lieu', 'crypte', 'savoir', salle='crypte', case=[7, 2])
        echanges.executer(m, 'marchand', {'operation': 'demander', 'cible': 'ilse',
            'outil': moyen, 'lieu': '', 'condition': ''}, [])
        self.assertTrue(social._utile(self.stable(m), 'ilse', 'marchand', n))
        # La demande a pu créer aussi une promesse. Isoler le démenti de
        # l'emploi dans une scène sans cet autre lien légitime de pertinence.
        m = scene()
        esprits.croire(m, 'ilse', 'marchand', 'etat', {'faim': False, 'chaleur': False}, 'vu')
        for actif in (True, False):
            social.faire_entendre(m, 'marchand', 'ilse', 'Une demande typée.', [moyen], [],
                [{'type': 'usage', 'moyen': moyen, 'emplois': esprits.emplois_usage(m, moyen), 'actif': actif}])
            self.assertEqual(social._utile(self.stable(m), 'ilse', 'marchand', n), actif)

    def test_sauvegarde_refuse_preuve_mal_formee_et_geste_sans_effet(self):
        m = scene()
        with esprits.constats_geste(m, 'marchand', 'bois'):
            pass
        self.assertNotIn('usage:bois', esprits.lire(m, 'ilse')['croyances'].get('marchand', {}))
        esprits.retenir_usage(m, 'ilse', 'marchand', 'bois', 'vu')
        esprits.lire(m, 'ilse')['croyances']['marchand']['usage:bois']['valeur'] = 'oui'
        with self.assertRaisesRegex(ErreurMonde, "Preuve d'usage invalide"):
            m.verifier()
