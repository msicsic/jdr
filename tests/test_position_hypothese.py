"""Une ancienne localisation reste un indice à vérifier, jamais une présence acquise."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as d, planification as p, pnj
from donjon.esprits import (croire, croyance, lire, percevoir_tous, confiance_position,
                           position_a_verifier, constater, consommer_hypothese, hypothese_consommee)
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

    def test_piste_consommee_seule_une_nouvelle_preuve_la_rouvre(self):
        for fabrique, a, b in ((capture, 'mathurine', 'lucien'), (mine, 'bram', 'remy')):
            with self.subTest(scenario=a):
                m = self.recharge(fabrique())
                ancienne = copy.deepcopy(lire(m, a)['croyances'][b]['lieu'])
                v = p.Vue(m, a)
                avant = p._entrees(v, {}, p.PROFONDEUR, p.NOEUDS)
                consommer_hypothese(m, a, b)
                self.assertNotEqual(avant, p._entrees(p.Vue(m, a), {}, p.PROFONDEUR, p.NOEUDS))
                date = m.data['minutes']
                for delai in (0, 16, 60, 180):
                    m.data['minutes'] = date + delai
                    croire(m, a, b, 'lieu', ancienne['valeur'], 'dit:joueur', .7,
                           salle=ancienne['salle'], case=None,
                           origine={'source': ancienne['source'], 'minute': ancienne['minute']})
                    m = self.recharge(m)
                    self.assertTrue(hypothese_consommee(m, a, b))
                    self.assertIsNone(p.rejoindre(m, a, b))
                    self.assertIsNone(p.s_enquerir(m, a, sujet=b))
                    geste = p._etape('prendre', 'lanterne_' + a, condition='sans_temoin')
                    # Le témoin consommé ne peut plus engendrer de nouvelle
                    # vérification furtive (les autres croyances sont écartées).
                    with patch.object(p, 'position_a_verifier', side_effect=lambda m, i, s: s == b), \
                            patch.object(p, '_chercher', side_effect=AssertionError('Piste consommée relancée')):
                        suites = p._normaliser_suites(p.Vue(m, a), p.depart(m, a), {}, lambda v,e: True,
                                                     [(0, 1, [geste], p.depart(m, a))])
                    self.assertFalse(any(g['operation'] == 'inspecter' for s in suites for g in s[2]))
                croire(m, a, b, 'lieu', None, 'vu', salle=None, case=None)
                self.assertTrue(hypothese_consommee(self.recharge(m), a, b))
                # Une voix effectivement reconnue constitue une entrée nouvelle.
                croire(m, a, b, 'lieu', ancienne['valeur'], 'entendu', salle=ancienne['salle'], case=None)
                self.assertFalse(hypothese_consommee(self.recharge(m), a, b))
                self.assertIsNotNone(p.rejoindre(m, a, b))
                m.data['minutes'] += 15
                consommer_hypothese(m, a, b)
                m.data['minutes'] += 1
                croire(m, a, b, 'lieu', ancienne['valeur'], 'dit:joueur', .7,
                       salle=ancienne['salle'], case=None,
                       origine={'source': 'vu', 'minute': m.data['minutes']})
                self.assertFalse(hypothese_consommee(self.recharge(m), a, b))

    def test_bruit_attribue_ne_rouvre_pas_une_piste_sans_voix_reconnue(self):
        from donjon.ouie import _attribuer
        for fabrique, a, b in ((capture, 'mathurine', 'lucien'), (mine, 'bram', 'remy')):
            with self.subTest(scenario=a):
                m = fabrique()
                consommer_hypothese(m, a, b)
                c = copy.deepcopy(lire(m, a)['croyances'][b]['lieu'])
                for _ in range(2):
                    m.data['minutes'] += 60
                    _attribuer(m, a, [b], c['salle'], c.get('case'))
                    m = self.recharge(m)
                    self.assertTrue(hypothese_consommee(m, a, b))
                    self.assertTrue(position_a_verifier(m, a, b))
                    self.assertEqual(lire(m, a)['croyances'][b]['lieu']['minute'], c['minute'])

    def test_capture_contact_requis_ne_repart_pas_dans_les_autres_salles(self):
        fichier = Path(__file__).parent / 'captures/position-374-auberge-42-42-consommee.json.gz'
        m = self.recharge(Monde(json.loads(gzip.decompress(fichier.read_bytes()))))
        self.assertTrue(hypothese_consommee(m, 'lucien', 'hugues'))
        for minute in (42, 60, 180):
            m.data['minutes'] = minute
            m = self.recharge(m)
            self.assertIsNone(p.rejoindre(m, 'lucien', 'hugues'))
            self.assertIsNone(p.contacter(m, 'lucien', 'hugues'))
            self.assertIsNone(p.s_enquerir(m, 'lucien', sujet='hugues'))
        croire(m, 'lucien', 'hugues', 'lieu', 'grenier', 'entendu', salle='grenier', case=None)
        m = self.recharge(m)
        self.assertIsNotNone(p.rejoindre(m, 'lucien', 'hugues'))

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
                        self.assertTrue(hypothese_consommee(m, a, b))
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

    def test_capture_crue_42_termine_inspection_avant_de_reprendre_les_preparatifs(self):
        fichier = Path(__file__).parent / 'captures/position-374-crue-42-18.json.gz'
        m = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
        self.assertTrue(position_a_verifier(m, 'aubin', 'ilse'))
        bloc, lignes = vivre(self.recharge(m), 6)
        coupe = self.recharge(m)
        decoupees = []
        for _ in range(6):
            coupe, texte = vivre(self.recharge(coupe), 1)
            decoupees.extend(texte)
        self.assertEqual(bloc.data, coupe.data)
        self.assertEqual(lignes, decoupees)
        self.recharge(bloc)
        self.recharge(coupe)
        # Le parent demeure servir Brune, mais la piste d'Ilse est consommée :
        # sur 6614e692, le préparatif à la réserve la précédait de nouveau à
        # chaque minute, produisant plus de trente passages pendant ces 6 min.
        c = lire(bloc, 'aubin')['croyances']['ilse']['lieu']
        self.assertTrue(hypothese_consommee(bloc, 'aubin', 'ilse'))
        passages = [c for c in bloc.data['chronique'] if c['pnj'] == 'aubin'
                    and c['nature'] == 'deplacement' and c['minute'] >= 18]
        self.assertLessEqual(len(passages), 10)

    def test_capture_agenda_ne_se_reveille_pas_par_expiration_du_resultat_de_sa_propre_inspection(self):
        fichier = Path(__file__).parent / 'captures/position-374-crue-1985-190.json.gz'
        m = self.recharge(Monde(json.loads(gzip.decompress(fichier.read_bytes()))))
        d.choisir(m, 'brune', m.data['minutes'])
        # Le 419 conserve les offres possibles derrière les vérifications :
        # le moyen choisi peut changer. Le contrat du 374 porte sur la piste
        # effectivement vérifiée, pas sur l'interdiction de tout autre contact.
        sujet = lire(m, 'brune')['intention']['plan'][-1]['contenu']['cherche']
        self.assertTrue(position_a_verifier(m, 'brune', sujet))
        pnj._inspecter(m, 'brune', sujet, [])
        m = self.recharge(m)
        self.assertEqual(lire(m, 'brune')['croyances'][sujet]['lieu']['minute'], 190)
        self.assertTrue(hypothese_consommee(m, 'brune', sujet))
        for minute in (205, 220, 235):
            m.data['minutes'] = minute
            m.data['dixiemes'] = 0
            d.choisir(m, 'brune', minute)
            m = self.recharge(m)
            plan = (lire(m, 'brune')['intention'] or {}).get('plan', [])
            self.assertFalse(any(g['operation'] == 'inspecter'
                                 and (g.get('contenu') or {}).get('verification')
                                 and g['contenu'].get('cherche') == sujet for g in plan))
