"""Même admissibilité au choix et au départ, y compris après reprise."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon import eau, pnj, planification
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.obstacles import Route
from donjon.rendu import regarder
from donjon.route_admissible import refus, attendue
from tests.test_social import recharger
from tools.diagnostic_refuge_mouille import diagnostiquer


def scene(nom='crue500-160'):
    return recharger(Monde(json.loads(gzip.decompress((Path(__file__).parent /
        f'data/scenes/refuge-mouille-{nom}.json.gz').read_bytes()))))


class RoutesTests(unittest.TestCase):
    def test_captures_reelles_arrivee_au_sec_et_meme_monde_decoupe(self):
        with tempfile.TemporaryDirectory() as dossier:
            for nom, qui in [('crue500-160', 'brune'), ('auteur-100', 'ilse')]:
                with self.subTest(nom=nom):
                    r = diagnostiquer(nom, qui, dossier)
                    self.assertEqual(r['apres_20_minutes']['salle'], 'chambre_cloche')

    def test_traversee_trop_longue_refusee_des_la_recherche_et_dite_apres_reprise(self):
        for qui in ('brune', 'ilse'):
            with self.subTest(qui=qui):
                m = scene()
                # Même géométrie, une eau déjà près du seuil, vue monter vite.
                c = lire(m, qui)['croyances']
                c['echoppe'] = {'eau': copy.deepcopy(lire(m, 'brune')['croyances']['echoppe']['eau'])}
                c['echoppe']['eau'].update(valeur=99, niveau=-21, montee=600)
                m = recharger(m)
                avant = copy.deepcopy(m.objets[qui])
                v = planification.Vue(m, qui)
                self.assertIsNone(v.route(planification.depart(m, qui, v), 'chambre_cloche'))
                self.assertIsNone(pnj._marcher(m, qui, lambda s, c: s == 'chambre_cloche', []))
                self.assertEqual(m.objets[qui], avant)
                self.assertIn('passage', m.data['chronique'][-1]['texte'])
                texte = regarder(m)
                m = recharger(m)
                self.assertEqual(regarder(m), texte)
                self.assertIn('eau', m.data['chronique'][-1]['texte'])

    def test_porte_incertaine_ne_garantit_pas_le_retour(self):
        m = scene()
        v = planification.Vue(m, 'brune')
        e = planification.depart(m, 'brune', v)
        # Le passage simple reste possible, mais pas un détour de dix minutes
        # vers une porte inconnue quand le retour prend autant de temps.
        route = Route([{'vers': 'crypte'}, {'vers': 'beffroi', 'porte': 'porte'}],
                      depart=e.salle, fin=('beffroi', None),
                      sejours=((e.salle, 12 * 600), ('echoppe', 600)))
        self.assertIn('retour coupé', refus(v, e, route, 'beffroi'))
        # Si le déverrouillage est acquis, le doute n'interdit plus l'évacuation.
        self.assertIsNone(refus(v, e.apres(faits=[(('verrou', 'porte'), False)]), route, 'beffroi'))
        # Une ouverture certaine n'autorise pas à attendre la noyade au
        # point de départ du retour : son séjour pendant la porte compte aussi.
        haut = e.apres(salle='beffroi', faits=[(('verrou', 'porte'), False)])
        longue = Route([{'vers': 'chambre_cloche', 'porte': 'porte'}],
                       depart='beffroi', fin=('chambre_cloche', None), portes={'porte'},
                       sejours=(('beffroi', 120 * 600), ('chambre_cloche', 15)))
        self.assertIn('passage', refus(v, haut, longue, 'chambre_cloche', passage=True,
                                      delai=60, certain=True, depart_compris=True))

    def test_attente_porte_longue_refusee_et_reprise_decoupee(self):
        from tools.diagnostic_refuge_mouille import vivre, recharger as reprise
        for qui in ('brune', 'ilse'):
            with self.subTest(qui=qui), tempfile.TemporaryDirectory() as dossier, patch.dict(
                    pnj.DUREES, ouvrir=12 * 600):
                m = scene()
                # Les deux lecteurs voient la même eau ; aucune clé ni ouverture
                # certaine ne leur garantit cette sortie avant le retour coupé.
                eau_vue = copy.deepcopy(lire(m, 'brune')['croyances']['echoppe'])
                lire(m, qui)['croyances']['echoppe'] = eau_vue
                lire(m, qui)['croyances'].pop('porte', None)
                v = planification.Vue(m, qui)
                self.assertIsNone(v.route(planification.depart(m, qui, v), 'chambre_cloche'))
                avant = copy.deepcopy(m.objets[qui])
                self.assertIsNone(pnj._marcher(m, qui, lambda s, c: s == 'chambre_cloche', []))
                self.assertEqual(m.objets[qui], avant)
                self.assertIn('retour coupé', m.data['chronique'][-1]['texte'])
                m = reprise(m, dossier)
                bloc = vivre(reprise(m, dossier), 2, dossier)
                coupe = vivre(vivre(reprise(m, dossier), 1, dossier), 1, dossier)
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(regarder(bloc), regarder(coupe))
                self.assertTrue(any(c['pnj'] == qui and 'retour coupé' in c['texte']
                                    for c in bloc.data['chronique']))

    def test_une_traversee_en_cours_ne_devient_pas_un_sejour_a_la_minute(self):
        from tests.test_social import placer
        from tools.diagnostic_refuge_mouille import vivre, recharger as reprise
        for qui in ('brune', 'ilse'):
            with self.subTest(qui=qui), tempfile.TemporaryDirectory() as dossier:
                m = scene('auteur-100' if qui == 'ilse' else 'crue500-160')
                but, plan = planification.planifier(m, qui, 'chaleur')
                lire(m, qui)['intention'] = {'but': but, 'plan': plan, 'motif': 'chaleur',
                                            'depuis': m.data['minutes'], 'attente': 0}
                from donjon.geometrie import position_entree
                placer(m, qui, 'echoppe', position_entree(m, 'echoppe', 'antichambre'))
                m = reprise(m, dossier)
                self.assertTrue(eau.noyee_attendue(m, qui, 'echoppe'))
                self.assertFalse(eau.en_peril(m, qui))
                bloc = vivre(reprise(m, dossier), 2, dossier)
                coupe = vivre(vivre(reprise(m, dossier), 1, dossier), 1, dossier)
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(regarder(bloc), regarder(coupe))
                self.assertEqual(bloc.objets[qui]['lieu'], 'chambre_cloche')
                lire(m, qui)['intention'] = None
                self.assertTrue(eau.en_peril(reprise(m, dossier), qui))

    def test_prevision_affine_invalide_la_memoire_sans_changer_les_categories(self):
        m = scene()
        v = planification.Vue(m, 'brune')
        a = planification._entrees(v, {}, 8, 4000)
        for salle in v.salles:
            for delai in (0, .8, 60, 120):
                self.assertAlmostEqual(attendue(v, salle, delai), eau.attendue(m, 'brune', salle, delai))
        lire(m, 'brune')['croyances']['echoppe']['eau']['montee'] += 1
        v2 = planification.Vue(m, 'brune')
        self.assertEqual(v.menacees, v2.menacees)
        self.assertEqual(v.noyees, v2.noyees)
        self.assertNotEqual(a, planification._entrees(v2, {}, 8, 4000))
