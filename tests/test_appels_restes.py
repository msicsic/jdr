"""Indices consommés : recharges, changement de but et vrais contacts."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import appel, deliberation, pnj
from donjon.ecoute import ENTENDU, entendus, rendre
from donjon.esprits import croire, esprit, lire, memoriser
from donjon.monde import Monde
from donjon.ouie import _bruit_inconnu
from donjon.rendu import regarder
from donjon.temps import instant
from tests.test_tensions import recharger, vivre
from tests.test_voix import aubin_cherche_gorm


class IndicesTests(unittest.TestCase):
    def test_retour_positivement_appris_vers_un_ancien_lieu_ou_une_ancienne_case(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                deliberation.recherche_vaine(m, 'aubin', cible, 'beffroi')
                _bruit_inconnu(m, 'aubin', 'beffroi', 'pas', 3)
                esprit(m, 'aubin')['memoire'] = []
                for salle, case in [('beffroi', [1, 1]), ('echoppe', [2, 2]),
                                    ('beffroi', [1, 1]), ('beffroi', [2, 1]), ('beffroi', [1, 1])]:
                    # Chaque recherche consomme cet indice, puis constate l'absence.
                    croire(m, 'aubin', cible, 'lieu', salle, 'entendu', salle=salle, case=case)
                    self.assertNotIn(salle, deliberation.appels_vains(m, 'aubin', cible))
                    deliberation.recherche_vaine(m, 'aubin', cible, salle)
                    croire(m, 'aubin', cible, 'lieu', None, 'essai', salle=None, case=None)
                    m = recharger(m)
                # Une réécoute à la dernière position connue n'est toujours pas un déplacement.
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'entendu', salle='beffroi', case=[1, 1])
                m = recharger(m)
                self.assertIn('beffroi', deliberation.appels_vains(m, 'aubin', cible))
                _bruit_inconnu(m, 'aubin', 'beffroi', 'pas', 3)
                m = recharger(m)
                self.assertIn('beffroi', deliberation.appels_vains(m, 'aubin', cible))
                self.assertTrue(regarder(m))

    def test_examen_consomme_la_presence_crue_avant_le_constat_d_absence(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                salle = m.objets['aubin']['lieu']
                # Le personnage est ailleurs ; la croyance antérieure à l'examen sera démentie.
                m.data['salles'][salle]['lumiere_naturelle'] = 2
                if cible != 'joueur':
                    from donjon.corps import endormir
                    endormir(m, cible)
                case = list(m.objets['aubin']['position'])
                croire(m, 'aubin', cible, 'lieu', salle, 'entendu', salle=salle, case=case)
                pnj._inspecter(m, 'aubin', cible)
                m = recharger(m)
                self.assertIsNone(lire(m, 'aubin')['croyances'][cible]['lieu']['valeur'])
                self.assertIn(salle, deliberation.appels_vains(m, 'aubin', cible))
                croire(m, 'aubin', cible, 'lieu', salle, 'entendu', salle=salle, case=case)
                m = recharger(m)
                self.assertIn(salle, deliberation.appels_vains(m, 'aubin', cible))
                self.assertTrue(regarder(m))

    def test_voix_repetee_absence_autre_but_et_memoire_evincee(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                recherche = lambda: deliberation.appels_vains(m, 'aubin', cible)
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'entendu', salle='beffroi', case=None)
                deliberation.recherche_vaine(m, 'aubin', cible, 'beffroi')
                deliberation.recherche_vaine(m, 'aubin', cible, 'echoppe')
                for _ in range(45):
                    memoriser(m, 'aubin', {'type': 'appel_sans_reponse', 'qui': cible, 'salle': 'beffroi'})
                esprit(m, 'aubin')['intention'] = None
                croire(m, 'aubin', cible, 'lieu', None, 'essai', salle=None, case=None)
                m = recharger(m)
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'entendu', salle='beffroi', case=None)
                m = recharger(m)
                self.assertEqual(recherche(), {'beffroi', 'echoppe'})
                avant = len(m.data.get('chronique', []))
                pnj._inspecter(m, 'aubin', cible)
                m = recharger(m)
                self.assertFalse(any(' appelle :' in c['texte'] for c in m.data.get('chronique', [])[avant:]))
                self.assertTrue(regarder(m))
                # Une nouvelle localisation précise rouvre ce lieu seul.
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'entendu', salle='beffroi', case=[2, 2])
                self.assertEqual(deliberation.appels_vains(recharger(m), 'aubin', cible), {'echoppe'})

    def test_bruit_reexplique_ne_recommence_pas_la_tournee(self):
        m = aubin_cherche_gorm()
        for cible in ('marchand', 'joueur'):
            deliberation.recherche_vaine(m, 'aubin', cible, 'echoppe')
        _bruit_inconnu(m, 'aubin', 'echoppe', 'pas', 3)
        for cible in ('marchand', 'joueur'):
            deliberation.recherche_vaine(m, 'aubin', cible, 'echoppe')
        # L'explication du son et l'éviction de sa mémoire ne sont pas un nouveau son.
        esprit(m, 'aubin')['memoire'] = []
        m = recharger(m)
        _bruit_inconnu(m, 'aubin', 'echoppe', 'feutre', 1)
        m = recharger(m)
        for cible in ('marchand', 'joueur'):
            self.assertIn('echoppe', deliberation.appels_vains(m, 'aubin', cible))
        esprit(m, 'aubin')['memoire'] = []
        _bruit_inconnu(m, 'aubin', 'echoppe', 'bruyant', 7)
        m = recharger(m)
        for cible in ('marchand', 'joueur'):
            self.assertNotIn('echoppe', deliberation.appels_vains(m, 'aubin', cible))
        self.assertTrue(regarder(m))

    def test_reponse_saisie_et_reapparition_sont_des_contacts_nouveaux(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                salle = m.joueur['salle'] if cible == 'joueur' else m.objets[cible]['lieu']
                croire(m, 'aubin', cible, 'lieu', salle, 'entendu', salle=salle, case=None)
                deliberation.recherche_vaine(m, 'aubin', cible, salle)
                appel.entendre(m, 'aubin', cible, appel.ARRIVE, [], appelant=True, entendu=False)
                self.assertIn(salle, deliberation.appels_vains(m, 'aubin', cible))
                appel.entendre(m, 'aubin', cible, appel.ARRIVE, [], appelant=True)
                m = recharger(m)
                self.assertNotIn(salle, deliberation.appels_vains(m, 'aubin', cible))
                deliberation.recherche_vaine(m, 'aubin', cible, salle)
                croire(m, 'aubin', cible, 'lieu', None, 'essai', salle=None, case=None)
                croire(m, 'aubin', cible, 'lieu', salle, 'vu', salle=salle, case=[1, 1])
                self.assertNotIn(salle, deliberation.appels_vains(recharger(m), 'aubin', cible))


class CapturesTests(unittest.TestCase):
    def verifier_capture(self, nom, qui, cible):
        chemin = Path(__file__).with_name('data') / f'appels-restes-{nom}.json.gz'
        m = recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))
        debut = instant(m)
        cris, nouveaux = [], []
        indice, heler = deliberation.indice_recherche, pnj.heler

        def noter(monde, id, salle, personne=None, **k):
            change = indice(monde, id, salle, personne, **k)
            if change and id == qui and personne in (None, cible):
                nouveaux.append(salle)
            return change

        def crier(monde, id, cherche, lignes):
            if id == qui and cherche == cible:
                salle = monde.objets[id]['lieu']
                self.assertNotIn(salle, deliberation.appels_vains(monde, id, cible))
                cris.append(salle)
            return heler(monde, id, cherche, lignes)

        with patch.object(deliberation, 'indice_recherche', noter), patch.object(pnj, 'heler', crier):
            bloc, _ = vivre(recharger(m), 10)
        coupe = recharger(m)
        for duree in (4, 6):
            coupe, _ = vivre(coupe, duree)
        self.assertEqual(bloc.data, coupe.data)
        self.assertEqual(regarder(bloc), regarder(coupe))
        self.assertEqual(rendre(bloc, entendus(bloc, debut, ENTENDU)),
                         rendre(coupe, entendus(coupe, debut, ENTENDU)))
        self.assertLessEqual(len(cris), len(m.data['salles']) + len(nouveaux))

    def test_mine_7_odon_lucien(self):
        self.verifier_capture('mine-7-470', 'odon', 'lucien')

    def test_auberge_7_odile_joss(self):
        self.verifier_capture('auberge-7-625', 'odile', 'joss')
