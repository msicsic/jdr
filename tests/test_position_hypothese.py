"""Une ancienne localisation reste un indice à vérifier, jamais une présence acquise."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as d, planification as p, pnj
from donjon.esprits import (croire, croyance, lire, percevoir_tous, confiance_position,
                           position_a_verifier, constater)
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import instant, MINUTE
from tests.test_tensions import recharger, placer, vivre
from tests.test_voix import hugues_cherche_anselme


def capture():
    fichier = Path(__file__).parent / 'captures/position-374-auberge-7-240.json.gz'
    return Monde(json.loads(gzip.decompress(fichier.read_bytes())))


def mine():
    fichier = Path(__file__).parent / 'data/appels-restes-mine-7-470.json.gz'
    return Monde(json.loads(gzip.decompress(fichier.read_bytes())))


class HypothesePositionTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_captures_reelles_depart_et_presence_cachee(self):
        # 371 : Mathurine situe encore Lucien au couloir depuis la minute 174,
        # alors qu'il est au grenier à 240. 69 : Bram croit Rémy au baraquement.
        for fabrique, a, b, attendu in ((capture, 'mathurine', 'lucien', 'couloir'),
                                       (mine, 'bram', 'remy', 'baraquement')):
            with self.subTest(scenario=a):
                m = self.recharge(fabrique())
                self.assertNotEqual(m.objets[b]['lieu'], attendu)
                self.assertTrue(position_a_verifier(m, a, b))
                self.assertIsNone(d.salle_crue(m, a, b))
                self.assertEqual(lire(m, a)['croyances'][b]['lieu']['valeur'], attendu)
                etapes, trouve = p.rejoindre(m, a, b)
                self.assertFalse(trouve)
                self.assertTrue(any(x['operation'] in ('inspecter', 'demander') for x in etapes))
                # Le même indice et le même plan quand la cible est réellement restée.
                n = Monde(copy.deepcopy(m.data))
                placer(n, b, attendu, (2, 2))
                self.assertEqual(lire(m, a), lire(n, a))
                self.assertEqual((etapes, trouve), p.rejoindre(self.recharge(n), a, b))

    def test_confiance_horloge_regle_et_perception(self):
        m = hugues_cherche_anselme()
        for sujet in ('anselme', 'joueur', 'lanterne_hugues', 'hugues'):
            croire(m, 'hugues', sujet, 'lieu', 'couloir', 'vu', salle='couloir', case=None)
        date = m.data['minutes']
        m.data['minutes'] += 15
        self.assertEqual(confiance_position(m, 'hugues', 'anselme'), .5)
        self.assertTrue(position_a_verifier(m, 'hugues', 'anselme'))
        self.assertTrue(position_a_verifier(m, 'hugues', 'joueur'))
        for sujet in ('lanterne_hugues', 'hugues'):
            self.assertEqual(confiance_position(m, 'hugues', sujet), 1)
        m = self.recharge(m)
        # Le seuil, pas le nombre d'appels au lecteur, commande la clé du graphe.
        avant = p._entrees(p.Vue(m, 'hugues'), {}, p.PROFONDEUR, p.NOEUDS)
        m.data['minutes'] = date + 14
        frais = p._entrees(p.Vue(m, 'hugues'), {}, p.PROFONDEUR, p.NOEUDS)
        self.assertNotEqual(avant, frais)
        m.data['positions_hypotheses']['demi_vies']['mobile'] = 2
        self.assertTrue(position_a_verifier(m, 'hugues', 'anselme'))
        croire(m, 'hugues', 'anselme', 'lieu', 'chambre_chaude', 'entendu',
               salle='chambre_chaude', case=None)
        self.assertFalse(position_a_verifier(self.recharge(m), 'hugues', 'anselme'))

    def test_mobilite_connue_sans_lire_la_cible(self):
        m = hugues_cherche_anselme()
        date = m.data['minutes']
        for etat, attendu in (({}, 'mobile'), ({'assis': True}, 'pose'), ({'lie': True}, 'retenu')):
            m.data['minutes'] = date
            croire(m, 'hugues', 'anselme', 'etat', etat, 'vu')
            croire(m, 'hugues', 'anselme', 'lieu', 'chambre_chaude', 'vu',
                   salle='chambre_chaude', case=None)
            self.assertEqual(lire(m, 'hugues')['croyances']['anselme']['lieu']['mobilite'], attendu)
            m.data['minutes'] += 15
            self.assertEqual(position_a_verifier(m, 'hugues', 'anselme'), attendu == 'mobile')
        # Les verrous crus, même faux, suffisent à une hypothèse de captivité.
        croire(m, 'hugues', 'anselme', 'etat', {}, 'vu')
        croire(m, 'hugues', 'porte_chambre', 'verrouillee', True, 'vu')
        croire(m, 'hugues', 'anselme', 'lieu', 'chambre_chaude', 'vu',
               salle='chambre_chaude', case=None)
        self.assertEqual(lire(m, 'hugues')['croyances']['anselme']['lieu']['mobilite'], 'retenu')
        self.recharge(m)

    def test_repos_effectivement_observe(self):
        m = hugues_cherche_anselme()
        from donjon.vecu import noter
        noter(m, 'anselme', instant(m), 'repos')
        croire(m, 'hugues', 'anselme', 'lieu', 'chambre_chaude', 'vu',
               salle='chambre_chaude', case=None)
        constater(m, 'hugues', 'anselme', 'vu')
        self.assertTrue(croyance(m, 'hugues', 'anselme', 'etat')['valeur']['assis'])
        self.assertEqual(lire(m, 'hugues')['croyances']['anselme']['lieu']['mobilite'], 'pose')

    def test_ouidire_date_ne_rajeunissant_pas_une_observation(self):
        m = capture()
        c = copy.deepcopy(lire(m, 'mathurine')['croyances']['lucien']['lieu'])
        for _ in range(2):
            croire(m, 'mathurine', 'lucien', 'lieu', c['valeur'], 'dit:odile', .7,
                   salle=c['salle'], case=None, origine={'source': c['source'], 'minute': c['minute']})
            m = self.recharge(m)
            self.assertTrue(position_a_verifier(m, 'mathurine', 'lucien'))
        self.assertLess(croyance(m, 'mathurine', 'lucien', 'lieu')['confiance'], .1)

    def test_verification_executee_puis_recharge_present_ou_parti(self):
        for fabrique, a, b, salle in ((capture, 'mathurine', 'lucien', 'couloir'),
                                     (mine, 'bram', 'remy', 'baraquement')):
            for present in (False, True):
                with self.subTest(scenario=a, present=present):
                    m = fabrique()
                    m.data['salles'][salle]['lumiere_naturelle'] = 2
                    # Isoler le dernier geste du préfixe de recherche natif :
                    # l'acteur est arrivé au lieu cru, les autres n'agissent pas.
                    placer(m, a, salle, (2, 2))
                    if present:
                        placer(m, b, salle, (3, 2))
                    else:
                        # Le silence n'est pas un départ : empêcher la réponse
                        # seulement par un refus social cru, comme dans le jeu.
                        from tests.support import lier
                        lier(m, b, a, False, 'vu')
                    m.joueur.update(salle=salle, position=[2, 2], orientation='est')
                    e = lire(m, a)
                    e['intention'] = {'but': {'type': 'rejoindre', 'qui': b}, 'motif': 'devoir',
                                      'plan': [p._etape('inspecter', lieu=salle, contenu={'cherche': b})],
                                      'depuis': m.data['minutes'], 'attente': 0}
                    avant = copy.deepcopy(m.objets[b])
                    for _ in range(100):
                        duree, issue, _ = pnj.agir(m, a, instant(m), [])
                        percevoir_tous(m)
                        if not e['intention']['plan']:
                            break
                        t = instant(m) + max(1, duree)
                        m.data['minutes'], m.data['dixiemes'] = divmod(t, MINUTE)
                    else:
                        self.fail('La vérification ne termine pas')
                    m = self.recharge(m)
                    self.assertEqual(m.objets[b]['lieu'], avant['lieu'])
                    self.assertEqual(m.objets[b]['position'], avant['position'])
                    if present:
                        self.assertEqual(d.salle_crue(m, a, b), salle)
                        self.assertFalse(position_a_verifier(m, a, b))
                        from donjon.voix import nom_pour_joueur
                        self.assertTrue(m.visible(b))
                        self.assertIn(nom_pour_joueur(m, b).lower(), ' '.join(regarder(m).lower().split()))
                    else:
                        self.assertIn(salle, d.appels_vains(m, a, b))
                        self.assertNotEqual(d.salle_crue(m, a, b), salle)
                        self.assertFalse(m.visible(b))
                        self.assertNotIn(m.objets[b]['nom'].split(',')[0], regarder(m))
                        for s in m.data['salles']:
                            d.recherche_vaine(m, a, b, s)
                        m.data['minutes'] += 180
                        self.assertIsNone(p.rejoindre(self.recharge(m), a, b))

    def test_plan_discret_verifie_aussi_un_temoin_perime(self):
        m = capture()
        v = p.Vue(m, 'mathurine')
        e = p.depart(m, 'mathurine', v)
        geste = p._etape('prendre', 'lanterne_mathurine', condition='sans_temoin')
        etapes = p._normaliser_suites(v, e, {}, lambda v, e: True, [(0, 1, [geste], e)])
        self.assertTrue(etapes)
        self.assertTrue(all(g['operation'] in ('aller', 'inspecter', 'demander')
                            for suite in etapes for g in suite[2]))
        self.assertEqual(p._normaliser_suites(v, e, {}, lambda v, e: True,
                                             [(0, 1, [geste], e)], conclure=True), [])
        # Un suffixe sauvegardé avant le seuil repasse par ce même contrôle.
        lire(m, 'mathurine')['intention'] = {'but': {'type': 'manger'}, 'motif': 'faim',
            'plan': [geste], 'depuis': m.data['minutes'], 'attente': 0}
        executes = []
        original = pnj._executer
        def noter(monde, id, etape, *args, **kw):
            executes.append(etape['operation'])
            return original(monde, id, etape, *args, **kw)
        with patch.object(pnj, '_executer', noter):
            pnj.agir(m, 'mathurine', instant(m), [])
        self.assertNotIn('prendre', executes)
        self.assertNotEqual(lire(m, 'mathurine')['intention']['plan'], [geste])
        self.recharge(m)

    def test_laps_entier_decoupe_traverse_le_seuil(self):
        m = hugues_cherche_anselme()
        croire(m, 'hugues', 'anselme', 'lieu', 'chambre_chaude', 'vu',
               salle='chambre_chaude', case=None, minute=m.data['minutes'] - 14)
        entier, lignes = vivre(self.recharge(m), 2)
        coupe, a = vivre(self.recharge(m), 1)
        coupe, b = vivre(self.recharge(coupe), 1)
        self.assertEqual(entier.data, coupe.data)
        self.assertEqual(lignes, a + b)
        self.recharge(entier)
