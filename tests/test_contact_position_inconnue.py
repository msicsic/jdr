"""Contact matériel : héritage cru, observation et démenti réellement constaté."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, planification as p, pnj
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_empathie import scene
from tests.test_tensions import placer, recharger, vivre


def capture():
    chemin = Path(__file__).parent / 'captures/contact-313-relais-7.json.gz'
    return Monde(json.loads(gzip.decompress(chemin.read_bytes())))


def source_ailleurs():
    m, a, b = scene()
    # Scène d'auteur : une source dans un contenant fixe d'une autre salle.
    contenant = copy.deepcopy(m.objets['vivres'])
    contenant.update(id='coffre_contact', nom='coffre de provisions', type='contenant',
                     mobile=False, lieu='galerie', position=[2, 2], position_salle='galerie',
                     ouverte=True, proprietaire=a)
    contenant.pop('portions', None)
    m.objets['coffre_contact'] = contenant
    m.objets['vivres'].update(lieu='coffre_contact', proprietaire=a)
    croire(m, a, 'coffre_contact', 'lieu', 'galerie', 'vu', salle='galerie', case=[2, 2])
    croire(m, a, 'coffre_contact', 'etat', {'ouverte': True}, 'vu')
    croire(m, a, 'vivres', 'lieu', 'coffre_contact', 'vu', salle=None, case=None)
    m.objets[a]['profil']['pulsions'] = [{'besoin': 'devoir', 'condition': {'objet': 'vivres', 'servir': b}}]
    lire(m, a)['pulsions'] = []
    lire(m, a)['besoins']['devoir'] = 80.
    return recharger(m)


class ContactPositionInconnueTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def verifier_service(self, m, a, b):
        depart = self.recharge(m)
        self.assertIsNone(lire(depart, a)['croyances']['vivres']['lieu']['case'])
        salle = d.salle_crue(depart, a, 'vivres')
        v = p.Vue(depart, a)
        e = p.depart(depart, a, v).apres(salle=salle)
        self.assertEqual(pnj._case_crue(depart, a, 'vivres', salle), v.case_objet(e, 'vivres'))
        self.assertIsNotNone(v.case_objet(e, 'vivres'))
        gestes = []
        executer = pnj._executer

        def observer(m, qui, etape, *args, **kwargs):
            r = executer(m, qui, etape, *args, **kwargs)
            if qui == a and etape['operation'] == 'servir':
                gestes.append((copy.deepcopy(etape), r))
            return r

        with patch.object(pnj, '_executer', observer):
            bloc, lignes = vivre(self.recharge(depart), 6)
        self.assertTrue(any(g['contenu']['pour'] == b and r for g, r in gestes), gestes)
        self.assertTrue(all(r for _, r in gestes), gestes)
        self.assertTrue(any(c['pnj'] == a and 'donne une part' in c['texte'] for c in bloc.data['chronique']))
        self.assertLess(bloc.objets['vivres']['portions'], depart.objets['vivres']['portions'])
        morceaux = self.recharge(depart)
        decoupees = []
        for _ in range(6):
            morceaux, texte = vivre(morceaux, 1)
            decoupees.extend(texte)
        self.assertEqual(bloc.data, morceaux.data)
        self.assertEqual(lignes, decoupees)
        self.recharge(bloc)
        self.recharge(morceaux)

    def test_capture_relais_7_gorm_sert_brune(self):
        m = self.recharge(capture())
        charges = copy.deepcopy(agendas.en_cours(m, 'marchand'))
        self.assertTrue(charges)
        etape = lire(m, 'marchand')['intention']['plan'][0]
        self.assertEqual(pnj._approcher(m, 'marchand', etape, []), 30)
        self.assertEqual(charges, agendas.en_cours(m, 'marchand'))
        self.verifier_service(capture(), 'marchand', 'brune')

    def test_contenant_dans_une_autre_salle(self):
        self.verifier_service(source_ailleurs(), 'mathe', 'lucien')

    def test_disparition_constatee_au_contact_sans_repetition(self):
        m = source_ailleurs()
        from donjon.geometrie import cases
        placer(m, 'vivres', 'filon', min(cases(m.data['salles']['filon'])))
        depart = self.recharge(m)
        refus = []
        original = pnj._hors_d_atteinte

        def observer(m, qui, objet):
            r = original(m, qui, objet)
            if qui == 'mathe' and objet == 'vivres':
                refus.append(d.salle_crue(m, qui, objet))
            return r

        with patch.object(pnj, '_hors_d_atteinte', observer):
            fin, _ = vivre(self.recharge(depart), 6)
        self.assertEqual(refus, [None])
        self.assertIsNone(d.salle_crue(fin, 'mathe', 'vivres'))
        self.assertEqual(fin.objets['vivres']['portions'], depart.objets['vivres']['portions'])
        self.assertFalse(any(c['pnj'] == 'mathe' and 'donne une part' in c['texte']
                             for c in fin.data['chronique']))
        self.recharge(fin)

    def test_source_sans_case_prepare_observation_dans_son_lieu_cru(self):
        m = source_ailleurs()
        placer(m, 'vivres', 'galerie', [6, 2])
        croire(m, 'mathe', 'vivres', 'lieu', 'galerie', 'savoir', salle='galerie', case=None)
        # Lumière de la scène d'auteur ; aucune position mobile fournie au PNJ.
        m.objets['lampe_remy'].update(lieu='mathe', allume=True, combustible=720)
        croire(m, 'mathe', 'lampe_remy', 'lieu', 'mathe', 'vu', salle=None, case=None)
        depart = self.recharge(m)
        v = p.Vue(depart, 'mathe')
        e = p.depart(depart, 'mathe', v).apres(salle='galerie')
        g = p._etape('prendre', 'vivres')
        self.assertIsNone(v.case_objet(e, 'vivres'))
        avant = copy.deepcopy(depart.data)
        route = v.approche(e, g)
        from donjon.obstacles import cout_route
        self.assertIsNotNone(route)
        self.assertGreater(cout_route(route), 0)
        self.assertEqual(depart.data, avant)
        self.assertIsNone(v.approche(p.depart(depart, 'mathe', v), g))
        # Le premier pas prépare l'observation dans l'autre salle sans démentir
        # la source. La perception peut la trouver avant d'atteindre le centre.
        essai = self.recharge(depart)
        self.assertGreater(pnj._approcher(essai, 'mathe', g, []), 0)
        self.assertEqual(d.salle_crue(essai, 'mathe', 'vivres'), 'galerie')
        observation = self.recharge(depart)
        placer(observation, 'mathe', 'galerie', [4, 1])
        centre = pnj._centre(observation, 'mathe')
        placer(observation, 'mathe', 'galerie', centre)
        cible = [centre[0] - 2, centre[1]]
        placer(observation, 'vivres', 'galerie', cible)
        self.assertEqual(pnj._approcher(observation, 'mathe', g, []), pnj.TOUR)
        self.assertEqual(pnj._case_crue(observation, 'mathe', 'vivres'), tuple(cible))
        self.recharge(observation)
        fin, _ = vivre(self.recharge(depart), 6)
        self.assertTrue(any(c['pnj'] == 'mathe' and 'donne une part' in c['texte']
                            for c in fin.data['chronique']))
        self.recharge(fin)

    def test_distance_et_case_inconnue_ne_dementent_pas(self):
        m = self.recharge(capture())
        avant = copy.deepcopy(lire(m, 'marchand')['croyances']['vivres'])
        self.assertFalse(pnj._hors_d_atteinte(m, 'marchand', 'vivres'))
        self.assertEqual(avant, lire(m, 'marchand')['croyances']['vivres'])
        croire(m, 'marchand', 'reserve', 'lieu', 'echoppe', 'vu', salle='echoppe', case=None)
        # La réserve fixe a une position connue ; une source mobile n'en a pas.
        croire(m, 'marchand', 'vivres', 'lieu', 'echoppe', 'vu', salle='echoppe', case=None)
        avant = copy.deepcopy(lire(m, 'marchand')['croyances']['vivres'])
        self.assertFalse(pnj._hors_d_atteinte(m, 'marchand', 'vivres'))
        self.assertEqual(avant, lire(m, 'marchand')['croyances']['vivres'])
        self.recharge(m)

    def test_heritage_sans_positions_reelles_et_cycles(self):
        m = source_ailleurs()
        a = 'mathe'
        croire(m, a, 'coffre_contact', 'lieu', 'lucien', 'savoir', salle=None, case=None)
        croire(m, a, 'lucien', 'lieu', 'galerie', 'savoir', salle='galerie', case=[2, 2])
        for case in ([1, 1], [5, 5]):
            placer(m, 'lucien', 'baraquement', case)
            placer(m, 'vivres', 'baraquement', case)
            # Sa croyance conserve le lien au contenant, malgré le déplacement réel.
            self.assertEqual(pnj._case_crue(m, a, 'vivres', 'galerie'), (2, 2))
            v = p.Vue(m, a)
            e = p.depart(m, a, v).apres(salle='galerie')
            self.assertEqual(v.case_objet(e, 'vivres'), (2, 2))
        croire(m, a, 'lucien', 'lieu', None, 'vu', salle=None, case=None)
        self.assertIsNone(pnj._case_crue(m, a, 'vivres', 'galerie'))
        croire(m, a, 'coffre_contact', 'lieu', 'vivres', 'savoir', salle=None, case=None)
        self.assertIsNone(pnj._case_crue(m, a, 'vivres', 'galerie'))

    def test_approche_ignore_le_deplacement_cache_de_la_source(self):
        marches = []
        for case in ([0, 0], [7, 0]):
            m = self.recharge(capture())
            placer(m, 'vivres', 'echoppe', case)
            self.assertFalse(pnj.percoit(m, 'marchand', 'vivres'))
            avant = copy.deepcopy(lire(m, 'marchand')['croyances']['vivres'])
            g = lire(m, 'marchand')['intention']['plan'][0]
            duree = pnj._approcher(m, 'marchand', g, [])
            marches.append((duree, m.objets['marchand']['position']))
            self.assertEqual(avant, lire(m, 'marchand')['croyances']['vivres'])
            self.recharge(m)
        self.assertEqual(marches[0], marches[1])
        self.assertEqual(marches[0][0], 30)

    def test_contact_perdu_est_observe_avant_interruption(self):
        from donjon.esprits import percevoir
        from donjon.echanges import executer
        from tests.test_pas_compagnons import scene as compagnons
        for scenario in ('relais', 'crue_hameau'):
            with self.subTest(scenario=scenario):
                m = self.recharge(compagnons(scenario, 'aubin', 'marchand'))
                placer(m, 'aubin', 'antichambre', (2, 5))
                m.objets['aubin']['orientation'] = 'sud-ouest'
                self.assertFalse(pnj.percoit(m, 'aubin', 'marchand'))
                percevoir(m, 'aubin')
                self.assertIsNone(d.salle_crue(m, 'aubin', 'marchand'))
                m = self.recharge(m)
                geste = {'operation': 'demander', 'cible': 'marchand', 'outil': 'vivres',
                         'lieu': '', 'condition': ''}
                self.assertEqual(pnj._approcher(m, 'aubin', geste, []), pnj.TOUR)
                self.assertEqual(pnj._case_crue(m, 'aubin', 'marchand'), (1, 3))
                m = self.recharge(m)
                for _ in range(10):
                    if pnj._approcher(m, 'aubin', geste, []) == 0:
                        break
                else:
                    self.fail('Contact retrouvé mais jamais atteint')
                self.assertTrue(executer(m, 'aubin', geste, []))
                m = self.recharge(m)
                self.assertTrue(any(c['pnj'] == 'aubin' and 'demande une part' in c['texte']
                                    and '(promis)' in c['texte'] for c in m.data['chronique']))
                self.assertTrue(any(s['type'] == 'engagement_pris' and s.get('pour') == 'aubin'
                                    for s in lire(m, 'marchand')['memoire']))

    def test_case_projetee_prime_sur_le_contenant_ancien(self):
        m = self.recharge(source_ailleurs())
        v = p.Vue(m, 'mathe')
        e = p.depart(m, 'mathe', v)
        # L'état projeté ne conserve aucune case de l'acteur. Un objet pris
        # n'hérite donc plus du point de son ancien coffre dans la galerie.
        porte = e.apres(salle='galerie', portes=e.portes | {'vivres'})
        self.assertIsNone(v.case_objet(porte, 'vivres'))
        pose = e.apres(salle='galerie', faits=[(('lieu', 'vivres'), 'galerie'),
                             (('case_objet', 'vivres'), (3, 2))])
        self.assertEqual(v.case_objet(pose, 'vivres'), (3, 2))
        self.assertEqual(v.case_objet(e.apres(salle='galerie'), 'vivres'), (2, 2))
        self.recharge(m)


if __name__ == '__main__':
    unittest.main()
