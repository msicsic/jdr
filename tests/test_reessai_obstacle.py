"""Renoncements causaux : chaîne choix/exécution, sauvegarde et rendu."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as d
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.pnj import _patienter, tour_d_horizon
from donjon.planification import bruit_crochetage
from donjon.rendu import regarder as rendu
from donjon.temps import MINUTE
from tests.support import calme, regarder
from tests.test_tensions import placer, recharger, vivre


def odon():
    m = Monde(json.loads(gzip.decompress(
        (Path(__file__).parent / 'data/reessai-225-mine-31.json.gz').read_bytes())))
    # Capture juste avant le renoncement réel : passer par son chemin d'exécution.
    intention = lire(m, 'odon')['intention']
    cause = {'type': 'temoins', 'salle': m.objets['odon']['lieu'],
             'etape': copy.deepcopy(intention['plan'][0]),
             'nature': bruit_crochetage(m, 'odon', d.lumiere_crue(m, 'odon', 'bureau')),
             'temoins': {'bram': 'bureau'}}
    _patienter(m, 'odon', intention, cause=cause)
    return recharger(m)


class ReessaiObstacleTests(unittest.TestCase):
    def recharge(self, m):
        avant, texte = copy.deepcopy(m.data), rendu(m)
        apres = recharger(m)
        self.assertEqual(avant, apres.data)
        self.assertEqual(texte, rendu(apres))
        return apres

    def test_faim_renoncee_attend_un_moyen_dans_les_deux_captures_reelles(self):
        from donjon.recit_pnj import Recit
        from donjon.banc_pnj import _oisifs_urgents
        # Base intégration 3c0e1ca, départ tiré, joueur galerie ; graine 7
        # à 539:599, après le dernier renoncement de cette minute.
        for graine, minute in ((500, 107), (7, 539)):
            with self.subTest(graine=graine):
                m = Monde(json.loads(gzip.decompress((Path(__file__).parent / 'data' /
                    f'renonce-239-mine-{graine}-{minute}.json.gz').read_bytes())))
                e = lire(m, 'odon')
                retenus = copy.deepcopy(e['renoncements'])
                r = retenus['faim'][0]
                # Repartir de l'ancien classement pour exercer le choix complet.
                e['urgences']['faim'] = {'etat': 'presse', 'depuis': 0}
                d.choisir(m, 'odon', minute)
                m = self.recharge(m)
                self.assertEqual(d.inactivite(m, 'odon'), 'attente')
                self.assertEqual(lire(m, 'odon')['renoncements'], retenus)
                self.assertTrue(d.renoncement_tient(m, 'odon', r, (r['but'], [r['cause']['etape']])))
                recit = Recit(m)
                recit._noter(m, 'odon', minute)
                self.assertIn("en attente d'un moyen", '\n'.join(recit.personnage(m, 'odon', m.data['chronique'])))
                self.assertEqual(_oisifs_urgents(m)[1], 0)
                bloc, _ = vivre(self.recharge(m), 2)
                coupe = self.recharge(m)
                for _ in range(2):
                    coupe, _ = vivre(coupe, 1)
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(rendu(bloc), rendu(coupe))
                self.assertEqual(d.inactivite(bloc, 'odon'), 'attente')
                # Un constat enlève les témoins des vivres. Un témoin reste
                # devant la paie : ouvrir aussi cet autre recours ferait passer
                # l'agenda d'argent avant la faim, sans invalider sa reprise.
                from donjon.corps import endormir, visible
                placer(m, 'gaspard', 'bureau', (4, 2))
                croire(m, 'odon', 'gaspard', 'lieu', 'bureau', 'vu', salle='bureau', case=[4, 2])
                for qui, objet in m.objets.items():
                    if qui not in ('odon', 'gaspard') and objet.get('type') == 'personnage':
                        endormir(m, qui)
                        croire(m, 'odon', qui, 'etat', visible(m, qui), 'vu')
                tour_d_horizon(m, 'odon')
                self.assertFalse(d.renoncement_tient(m, 'odon', r, (r['but'], [r['cause']['etape']])))
                d.choisir(m, 'odon', minute)
                m = self.recharge(m)
                self.assertEqual(lire(m, 'odon')['intention']['but'], r['but'])
                self.assertEqual(lire(m, 'odon')['urgences']['faim']['etat'], 'presse')

    def test_odon_pas_de_reprise_par_delai_ni_date_de_regard(self):
        m = odon()
        retenu = copy.deepcopy(lire(m, 'odon')['renoncements']['agenda'][0])
        for minute in (91, 182, 500):
            m.data.update(minutes=minute, dixiemes=0)
            tour_d_horizon(m, 'odon')
            d.choisir(m, 'odon', minute)
            m = self.recharge(m)
            self.assertNotEqual((lire(m, 'odon')['intention'] or {}).get('but'), retenu['but'])
            self.assertEqual(lire(m, 'odon')['renoncements']['agenda'][0], retenu)
        self.assertTrue(m.objets['coffre_paie']['verrouillee'])
        self.assertEqual(m.objets['paie']['lieu'], 'coffre_paie')

    def test_odon_reprend_sur_absence_constatee_pas_sur_la_verite_cachee(self):
        m = odon()
        but = lire(m, 'odon')['renoncements']['agenda'][0]['but']
        placer(m, 'bram', 'filon', (4, 2))
        # Le départ d'auteur est hors de sa perception : il ne le sait pas.
        d.choisir(m, 'odon', m.data['minutes'])
        self.assertNotEqual((lire(m, 'odon')['intention'] or {}).get('but'), but)
        tour_d_horizon(m, 'odon')
        self.assertIsNone(lire(m, 'odon')['croyances']['bram']['lieu']['valeur'])
        d.choisir(m, 'odon', m.data['minutes'])
        m = self.recharge(m)
        self.assertEqual(lire(m, 'odon')['intention']['but'], but)
        self.assertTrue(lire(m, 'odon')['intention']['plan'])

    def test_un_autre_moyen_et_un_autre_but_ne_sont_pas_interdits(self):
        m = odon()
        r = lire(m, 'odon')['renoncements']['agenda'][0]
        self.assertTrue(d.renoncement_tient(m, 'odon', r, (r['but'], [r['cause']['etape']])))
        autre = copy.deepcopy(r['cause']['etape'])
        autre['operation'] = 'ouvrir'
        self.assertTrue(d.renoncement_tient(m, 'odon', r, (r['but'], [autre])))
        # La demande par la parole est un moyen qui évite le geste clandestin.
        autre.update(operation='demander', cible='paie', condition='')
        self.assertFalse(d.renoncement_tient(m, 'odon', r, (r['but'], [autre])))
        self.assertFalse(d.renoncement_tient(m, 'odon', r, ({'type': 'autre'}, [r['cause']['etape']])))

    def test_essayer_un_autre_moyen_ne_fait_pas_oublier_le_premier_obstacle(self):
        m = odon()
        calme(m, 'odon')
        retenus = copy.deepcopy(lire(m, 'odon')['renoncements']['agenda'])
        lire(m, 'odon')['visites']['bureau'] = m.data['minutes']
        r = retenus[0]
        autre = dict(r['cause']['etape'], operation='demander', cible='paie', condition='')
        candidat = d.Candidat('agenda', lambda m, i: (r['but'], [autre]),
                               False, False, d.Urgence(d.Palier.ARGENT, 0, ()))
        with patch.object(d, '_candidats', return_value=[candidat]):
            d.choisir(m, 'odon', m.data['minutes'])
        m = self.recharge(m)
        self.assertEqual(lire(m, 'odon')['intention']['plan'], [autre])
        self.assertEqual(lire(m, 'odon')['renoncements']['agenda'], retenus)
        # Même si ce second moyen échoue ensuite, il n'efface pas le premier.
        lire(m, 'odon')['intention']['attente'] = 31 * MINUTE
        cause = dict(r['cause'], etape=autre)
        _patienter(m, 'odon', lire(m, 'odon')['intention'], cause=cause)
        m = self.recharge(m)
        self.assertEqual(len(lire(m, 'odon')['renoncements']['agenda']), 2)
        d.choisir(m, 'odon', m.data['minutes'])
        self.assertNotEqual((lire(m, 'odon')['intention'] or {}).get('but'), r['but'])

    def test_gorm_passage_obstrue_autre_cause_et_scenario(self):
        from tests.test_passage import JoueurSurLePassageTests
        m = JoueurSurLePassageTests.palier(None)
        # Isoler cette ronde de l'entretien du brasero, qui sera sinon échu
        # lui aussi après le saut de temps de cette scène d'auteur.
        m.objets['marchand']['profil']['pulsions'] = [
            x for x in m.objets['marchand']['profil']['pulsions'] if 'periode' in x['condition']]
        lire(m, 'marchand')['pulsions'] = []
        e = lire(m, 'marchand')
        e['intention'] = None
        e['besoins']['devoir'] = 75.
        e['visites']['crypte'] = -1000
        d.choisir(m, 'marchand', 0)
        m, _ = vivre(m, 2)
        lire(m, 'marchand')['intention']['attente'] = 31 * MINUTE
        m, _ = vivre(m, 2)
        r = lire(m, 'marchand')['renoncements']['devoir'][0]
        self.assertEqual(r['cause']['type'], 'passage')
        self.assertEqual(r['cause']['obstacle'], 'joueur')
        m.data['minutes'] += 61
        d.choisir(m, 'marchand', m.data['minutes'])
        m = self.recharge(m)
        self.assertNotEqual((lire(m, 'marchand')['intention'] or {}).get('but'), r['but'])
        self.assertEqual(lire(m, 'marchand')['urgences']['devoir']['etat'], 'attente')
        bloc, _ = vivre(self.recharge(m), 2)
        coupe = self.recharge(m)
        for _ in range(2):
            coupe, _ = vivre(coupe, 1)
        self.assertEqual(bloc.data, coupe.data)
        self.assertEqual(rendu(bloc), rendu(coupe))
        self.recharge(bloc)
        m.joueur['position'] = [6, 3]
        tour_d_horizon(m, 'marchand')
        d.choisir(m, 'marchand', m.data['minutes'])
        m = self.recharge(m)
        self.assertFalse(d.renoncement_tient(m, 'marchand', r, (r['but'], [r['cause']['etape']])))
        m, _ = vivre(m, 3)
        m = self.recharge(m)
        self.assertEqual(m.objets['marchand']['lieu'], 'crypte')

    def test_la_ronde_ordinaire_reverifie_sans_reprendre_le_coffre(self):
        m = odon()
        calme(m, 'odon')
        # Bram part derrière lui, sans lui fournir de nouvelle. Le regard
        # ordinaire ne corrige pas encore sa croyance ; la ronde le pourra.
        placer(m, 'bram', 'filon', (4, 2))
        m.objets['odon']['orientation'] = 'sud'
        lire(m, 'odon')['visites']['bureau'] = m.data['minutes'] - d.PATIENCE
        d.choisir(m, 'odon', m.data['minutes'])
        self.assertEqual(lire(m, 'odon')['intention']['but']['type'], 'pulsion')
        self.assertTrue(any(p['operation'] == 'inspecter' for p in lire(m, 'odon')['intention']['plan']))
        # Les autres personnages sont laissés à leur simulation ordinaire.
        a, _ = vivre(recharger(m), 2)
        b = recharger(m)
        from donjon.pnj import avancer
        for _ in range(4):
            # Même laps via l'API en dixièmes, rechargé à chaque demi-minute.
            t = b.data['minutes'] * MINUTE + b.data.get('dixiemes', 0) + MINUTE // 2
            b.data['minutes'], b.data['dixiemes'] = divmod(t, MINUTE)
            avancer(b, 0, [], dixiemes=MINUTE // 2)
            b = recharger(b)
        self.assertEqual(a.data, b.data)
        self.assertIsNone(lire(a, 'odon')['croyances']['bram']['lieu']['valeur'])
        self.recharge(a)


if __name__ == '__main__':
    unittest.main()
