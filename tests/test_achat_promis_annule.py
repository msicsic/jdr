"""Une annulation en attente d'annonce ne confirme pas une nouvelle livraison."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, echanges
from donjon.biens import bourse
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_lampes_parts import nuit_noire
from tests.test_tensions import recharger, vivre


def capture():
    # Archive 306/reprise-309, 0038-23110-aubin : avant les achats t=36582.
    p = Path(__file__).parent / 'captures/achat-314-hameau-7.json.gz'
    return Monde(json.loads(gzip.decompress(p.read_bytes())))


def auberge():
    m = nuit_noire('auberge', 'joss', 'odile', 'lanterne_etable', 'pot_huile', 'etable')
    # Laisser assez de charges pour que la réserve minimale ne masque pas l'annulation.
    m.objets['pot_huile']['charges'] = 6
    m.data['finances_pnj']['joss'] = 5
    with patch.object(Monde, 'd20', return_value=20):
        assert echanges.demander(m, 'joss', 'odile', 'pot_huile', remettre_part=True) == 'promis'
    part = agendas.en_cours(m, 'odile')[0]['condition']['objet']
    deplacer(m, part, 'joueur')
    croire(m, 'odile', part, 'lieu', 'joueur', 'vu', salle='etable', case=[1, 2])
    agendas.echoir(m, 'odile')
    return m


class AchatPromisAnnuleTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_capture_reelle_avant_36582_bloc_et_decoupe(self):
        m = self.recharge(capture())
        debut = max(c['instant'] for c in m.data['chronique'])
        argent = (bourse(m, 'aubin'), bourse(m, 'marchand'))
        stock = m.objets['vivres']['portions']
        bloc, lignes = vivre(self.recharge(m), 30)
        morceaux, visibles = self.recharge(m), []
        for _ in range(30):
            morceaux, texte = vivre(morceaux, 1)
            visibles.extend(texte)
        self.assertEqual(bloc.data, morceaux.data)
        # Le bilan des présences est regroupé à la fin de chaque action joueur.
        # Les observations et leur multiplicité, puis le rendu final, restent les mêmes.
        self.assertCountEqual(lignes, visibles)
        offres = [c for c in bloc.data['chronique']
                  if c['instant'] > debut and c['pnj'] == 'aubin' and 'une part des vivres' in c['texte']]
        self.assertEqual(len(offres), 1, offres)
        # 374 : Aubin doit d'abord retrouver Gorm. Brune le renseigne à
        # 60, puis sa fausse localisation est démentie à 67 ; le contact
        # explique le retard et ne doit ni recréer un achat ni perdre le refus.
        enquetes = [s for s in lire(bloc, 'aubin')['memoire']
                    if s['type'] == 'enquete_lieu' and s['objet'] == 'marchand'
                    and s['minute'] * 600 > debut]
        self.assertEqual(len(enquetes), 1)
        self.assertEqual(enquetes[0]['issue'], 'dit')
        self.assertLess(enquetes[0]['minute'] * 600, offres[0]['instant'])
        self.assertTrue(any(s['type'] == 'mensonge_decouvert' and s['sujet'] == 'marchand'
                            and s['minute'] * 600 <= offres[0]['instant']
                            for s in lire(bloc, 'aubin')['memoire']))
        self.assertIn('(impossible)', offres[0]['texte'])
        self.assertFalse(any(c['instant'] > debut and c['pnj'] == 'aubin' and 'achète' in c['texte']
                             for c in bloc.data['chronique']))
        self.assertEqual((bourse(bloc, 'aubin'), bourse(bloc, 'marchand')), argent)
        self.assertEqual(bloc.objets['vivres']['portions'], stock)
        self.assertFalse(agendas.en_cours(bloc, 'marchand'))
        self.assertTrue(any(s['de'] == 'marchand' and s.get('objet') == 'vivres'
                            and s['raison'] == 'impossible' for s in lire(bloc, 'aubin')['refus']))
        self.recharge(bloc)
        self.recharge(morceaux)

    def test_autre_scenario_huile_annulee_refus_retenu_et_recharge(self):
        m = self.recharge(auberge())
        self.assertEqual(agendas.en_cours(m, 'odile')[0]['annule'], 'impossible')
        argent = (bourse(m, 'joss'), bourse(m, 'odile'))
        objets = set(m.objets)
        geste = {'operation': 'acheter', 'cible': 'odile', 'outil': 'pot_huile',
                 'contenu': {'prix': 1, 'remettre_part': True}}
        self.assertFalse(echanges.executer(m, 'joss', geste, []))
        self.assertTrue(any(s['operation'] == 'acheter' and s['raison'] == 'impossible'
                            for s in lire(m, 'joss')['refus']))
        depart = self.recharge(m)
        bloc, lignes = vivre(self.recharge(depart), 5, jet=20)
        morceaux, visibles = self.recharge(depart), []
        for _ in range(5):
            morceaux, texte = vivre(morceaux, 1, jet=20)
            visibles.extend(texte)
        self.assertEqual(bloc.data, morceaux.data)
        self.assertEqual(lignes, visibles)
        achats = [c for c in bloc.data['chronique'] if c['pnj'] == 'joss' and 'achète' in c['texte']]
        self.assertEqual(len(achats), 1, achats)
        self.assertIn('(impossible)', achats[0]['texte'])
        self.assertEqual((bourse(bloc, 'joss'), bourse(bloc, 'odile')), argent)
        self.assertEqual(bloc.objets['pot_huile']['charges'], 5)
        self.assertEqual(set(bloc.objets), objets)
        self.assertFalse(bloc.objets['lanterne_etable']['allume'])
        self.recharge(bloc)

    def test_chaque_cause_d_annulation_est_transmise_sans_accord(self):
        for raison in ('impossible', 'refus'):
            for prix in (0, 1):
                with self.subTest(raison=raison, prix=prix):
                    m = auberge()
                    lire(m, 'odile')['engagements'][0]['annule'] = raison
                    m = self.recharge(m)
                    avant = json.loads(json.dumps(m.data))
                    self.assertEqual(echanges.demander(m, 'joss', 'odile', 'pot_huile',
                                                       prix=prix, remettre_part=True), raison)
                    # Aucun paiement, prélèvement, renouvellement ou nouveau souvenir « promis ».
                    self.assertEqual(m.data, avant)
                    self.recharge(m)

    def test_livraison_active_puis_soldee_ne_ressert_pas_l_ancien_accord(self):
        m = auberge()
        engagement = lire(m, 'odile')['engagements'][0]
        engagement.pop('annule')
        piece = engagement['condition']['objet']
        deplacer(m, piece, 'odile')
        m = self.recharge(m)
        self.assertEqual(echanges.demander(m, 'joss', 'odile', 'pot_huile',
                                           remettre_part=True), 'promis')
        self.assertEqual(m.objets['pot_huile']['charges'], 5)
        echanges.remettre(m, 'odile', 'joss', piece)
        m = self.recharge(m)
        self.assertFalse(agendas.en_cours(m, 'odile'))
        m, _ = vivre(m, 3, jet=20)
        self.assertFalse(any(c['pnj'] == 'joss' and '(promis)' in c['texte']
                             for c in m.data['chronique']))
        self.assertEqual(m.objets['pot_huile']['charges'], 5)
        self.recharge(m)
