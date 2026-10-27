"""Une recherche retient chaque lieu vain jusqu'à un nouvel indice local, même après recharge."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation, pnj
from donjon.deliberation import appels_vains, recherche_vaine
from donjon.ecoute import ENTENDU, entendus, rendre
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.ouie import _bruit_inconnu
from donjon.temps import instant
from tests.test_appel_negocie import suivre
from tests.test_tensions import chronique, recharger, vivre
from tests.test_voix import appels, aubin_cherche_gorm, hugues_cherche_anselme


def scene(nom):
    with gzip.open(Path(__file__).with_name('data') / f'chercher-appeler-{nom}.json.gz',
                   'rt', encoding='utf-8') as f:
        return Monde(json.load(f))


class RechercheTests(unittest.TestCase):
    def verifier_scene(self, nom, qui, cible):
        m = scene(nom)
        debut = instant(m)
        cris = []
        indices = []
        passages_recherche = []
        heler = pnj.heler
        chroniquer = pnj._chroniquer
        indice_recherche = deliberation.indice_recherche

        def indice(monde, id, salle, personne=None, **k):
            vain = salle in appels_vains(monde, id, cible)
            change = indice_recherche(monde, id, salle, personne, **k)
            if change and id == qui and personne in (None, cible) and vain:
                indices.append(salle)
            return change

        def observer(monde, id, cherche, lignes):
            if id == qui and cherche == cible:
                salle = monde.objets[id]['lieu']
                self.assertNotIn(salle, appels_vains(monde, id, cherche))
                cris.append(salle)
            return heler(monde, id, cherche, lignes)

        def noter(monde, id, texte, nature='geste', **k):
            # Le plafond de la recherche ne compte pas les trajets vers les
            # marchés d'un projet indépendant. La capture A6 en ajoute 17,
            # contre 14 passages des recours historiques ; mêmes monde et ouïe.
            if (id == qui and nature == 'deplacement' and ' passe dans :' in texte
                    and (lire(monde, id)['intention'] or {}).get('motif') != 'agenda'):
                passages_recherche.append(texte)
            return chroniquer(monde, id, texte, nature, **k)

        with patch.object(pnj, 'heler', observer), patch.object(deliberation, 'indice_recherche', indice), \
                patch.object(pnj, '_chroniquer', noter):
            bloc, _ = vivre(recharger(m), 10)
        coupe = recharger(m)
        for _ in range(10):
            coupe, _ = vivre(coupe, 1)
        self.assertEqual(bloc.data, coupe.data)
        self.assertLessEqual(len(cris), len(m.data['salles']) + len(indices))
        self.assertLessEqual(len(passages_recherche), 4 * len(m.data['salles']))
        self.assertEqual(rendre(bloc, entendus(bloc, debut, ENTENDU)),
                         rendre(coupe, entendus(coupe, debut, ENTENDU)))

    def test_crue_3_brune_cherche_gorm(self):
        self.verifier_scene('crue', 'brune', 'marchand')

    def test_mine_7_odon_cherche_mathe(self):
        self.verifier_scene('mine', 'odon', 'mathe')

    def test_absence_et_temps_ne_rouvrent_pas_les_salles(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                for salle in m.data['salles']:
                    recherche_vaine(m, 'aubin', cible, salle)
                m.data['minutes'] += 121
                croire(m, 'aubin', cible, 'lieu', None, 'essai', salle=None, case=None)
                m = recharger(m)
                self.assertEqual(appels_vains(m, 'aubin', cible), set(m.data['salles']))
                avant = len(appels(m, 'aubin'))
                pnj._inspecter(m, 'aubin', cible)
                self.assertEqual(len(appels(recharger(m), 'aubin')), avant)

    def test_indice_meme_minute_rouvre_son_lieu_seul_et_survit_a_la_recharge(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                for salle in ('beffroi', 'echoppe'):
                    recherche_vaine(m, 'aubin', cible, salle)
                # Le souvenir ancien reste présent lors de la sauvegarde.
                from donjon.esprits import memoriser
                memoriser(m, 'aubin', {'type': 'appel_sans_reponse', 'qui': cible, 'salle': 'beffroi'})
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'entendu', salle='beffroi', case=None)
                m = recharger(m)
                self.assertEqual(appels_vains(m, 'aubin', cible), {'echoppe'})
                croire(m, 'aubin', cible, 'lieu', None, 'essai', salle=None, case=None)
                pnj._inspecter(m, 'aubin', cible)
                m = recharger(m)
                self.assertEqual(appels_vains(m, 'aubin', cible), {'beffroi', 'echoppe'})
                self.assertEqual(len(appels(m, 'aubin')), 1)

    def test_bruit_nouveau_local_et_bruit_deja_attendu(self):
        m = aubin_cherche_gorm()
        for cible in ('marchand', 'joueur'):
            for salle in ('beffroi', 'echoppe'):
                recherche_vaine(m, 'aubin', cible, salle)
        _bruit_inconnu(m, 'aubin', 'echoppe', 'pas', 3)
        m = recharger(m)
        for cible in ('marchand', 'joueur'):
            self.assertEqual(appels_vains(m, 'aubin', cible), {'beffroi'})
            recherche_vaine(m, 'aubin', cible, 'echoppe')
        _bruit_inconnu(m, 'aubin', 'echoppe', 'pas', 3)
        m = recharger(m)
        for cible in ('marchand', 'joueur'):
            self.assertEqual(appels_vains(m, 'aubin', cible), {'beffroi', 'echoppe'})

    def test_reponse_retrouve_la_personne_et_le_joueur_l_entend(self):
        for fabriquer, qui, cible, phrase in (
                (aubin_cherche_gorm, 'aubin', 'marchand', 'Gorm répond'),
                (hugues_cherche_anselme, 'hugues', 'anselme', 'Anselme répond')):
            with self.subTest(qui=qui):
                m = fabriquer()
                m.joueur.update(salle=m.objets[qui]['lieu'], position=[1, 2])
                m = recharger(m)
                debut = instant(m)
                m = suivre(m, 10, lambda monde: bool(appels(monde, qui)))
                self.assertEqual(len(appels(m, qui)), 1)
                self.assertTrue(any(t.startswith(phrase) for t in chronique(m)))
                m = suivre(m, 10, lambda monde: any('retrouve' in t and 'comme convenu' in t
                                                   for t in chronique(monde)))
                self.assertTrue(any('retrouve' in t and 'comme convenu' in t for t in chronique(m)))
                self.assertTrue(rendre(m, entendus(m, debut, ENTENDU)))
