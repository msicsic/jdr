"""Le service utile et constaté rouvre une demande, jusque dans le rendu rechargé."""
import unittest
from unittest.mock import patch

from donjon import relations
from donjon.deliberation import retenir_refus
from donjon.esprits import lire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import plan_recours
from tests.support import regarder
from tests.test_tache_promise_recours import feu, reserve
from tests.test_tensions import recharger, placer


def scene(fabrique):
    m, id, autre, c = fabrique()
    if 'verrouillee' in c:
        # Une réserve commune, avec sa propre clé : aucun mandat implicite
        # du bénéficiaire méfiant n'autorise à toucher son bien privé.
        m.objets[c['objet']]['proprietaire'] = None
        m.objets[c['objet']]['ouverte'] = False
        m.objets['cle_garde_manger']['proprietaire'] = id
        placer(m, id, 'cellier', [4, 2])
        placer(m, autre, 'cellier', [4, 3])
        m.joueur['position'] = [3, 3]
    lire(m, autre)['relations'][id] = relations._nouvelle({'confiance': 25})
    regarder(m, autre, id)
    regarder(m, autre, c['objet'])
    regarder(m, id, autre)
    for o, x in m.objets.items():
        if x['type'] == 'nourriture' and o != 'vivres':
            x['portions'] = 0
            from donjon.esprits import croire
            croire(m, id, o, 'etat', {'disponible': False}, 'essai')
    percevoir_tous(m)
    from donjon.esprits import constater
    constater(m, id, c['objet'], 'essai')
    retenir_refus(m, id, autre, 'demander', 'mefiance', objet='vivres')
    return recharger(m), id, autre, c


class RendreServiceTests(unittest.TestCase):
    def test_deux_services_et_redemande_apres_recharge(self):
        for fabrique in (feu, reserve):
            with self.subTest(scene=fabrique.__name__):
                m, id, autre, c = scene(fabrique)
                plan = plan_recours(m, id, 'faim', [])
                self.assertTrue(plan)
                self.assertNotIn('proposer', [g['operation'] for g in plan])
                lire(m, id)['intention']['plan'] = plan
                m = recharger(m)
                b = recharger(m.copier())
                with patch.object(Monde, 'd20', return_value=20):
                    texte = Moteur(m).executer(Moteur(m).preparer(proposition('attendre')))
                    from donjon.temps import instant
                    from donjon.commandes import analyser
                    n = 0
                    while instant(b) < instant(m):
                        moteur = Moteur(b)
                        moteur.executer(moteur.preparer(analyser(b, 'tourner est' if n % 2 else 'tourner ouest')))
                        b = recharger(b)
                        n += 1
                m = recharger(m)
                self.assertEqual(m.data['chronique'], b.data['chronique'])
                self.assertEqual(lire(m, id), lire(b, id))
                self.assertGreaterEqual(relations.axes(m, autre, id)['confiance'], 40)
                self.assertFalse(relations.envers(m, autre, id)['bandes']['mefiance'])
                self.assertTrue(any(s['type'] == 'service_rendu' for s in lire(m, autre)['memoire']))
                self.assertLess(lire(m, id)['besoins']['faim'], 95)
                self.assertTrue(any('alimente' in f or 'verrouille' in f
                                    for t in m.data['journal'] for f in t['faits']))
                self.assertTrue(texte)

    def test_impossible_une_seule_tentative_et_pas_de_supplantation(self):
        m, id, autre, c = scene(feu)
        m.objets['bois']['charges'] = 0
        percevoir_tous(m)
        self.assertIsNone(plan_recours(m, id, 'faim', []))
        m = recharger(m)
        from donjon.echanges import devis_service
        with patch('donjon.echanges.devis_service', wraps=devis_service) as devis:
            self.assertIsNone(plan_recours(m, id, 'faim', []))
        # Le recours commercial peut encore deviser ; le service gratuit ne recommence pas.
        self.assertEqual(len(lire(m, id)['recours_services']), 1)
        m, id, autre, c = scene(feu)
        ordinaire = {'operation': 'manger', 'cible': 'vivres', 'outil': '', 'lieu': '', 'condition': ''}
        self.assertIsNone(plan_recours(m, id, 'faim', [ordinaire]))
        self.assertEqual(lire(m, id)['recours_services'], [])

    def test_service_non_constate_et_joueur(self):
        from donjon.operations import sequence, etape
        for absent in (False, True):
            m, id, autre, c = scene(feu)
            avant = relations.axes(m, autre, 'joueur')['confiance']
            m.objets['bois'].update(lieu='joueur', proprietaire='joueur')
            regarder(m, autre, 'joueur')
            regarder(m, autre, c['objet'])
            if absent:
                placer(m, autre, 'antichambre', [6, 4])
            regarder(m, 'joueur', c['objet'])
            moteur = Moteur(m)
            texte = moteur.executer(moteur.preparer(sequence(etape('alimenter', c['objet'], outil='bois'))))
            m = recharger(m)
            self.assertEqual(relations.axes(m, autre, 'joueur')['confiance'], avant + (0 if absent else 20))
            self.assertGreater(m.objets[c['objet']]['combustible'], 20)
            self.assertIn('recharg', texte)
            self.assertIn('recharg', ' '.join(f for t in m.data['journal'] for f in t['faits']))

    def test_une_preuve_ne_leve_pas_un_refus_posterieur(self):
        from donjon.esprits import memoriser
        m, id, autre, c = scene(feu)
        souvenir = {'type': 'service_rendu', 'de': id, 'objet': c['objet'], 'preuve': 'meme-service'}
        memoriser(m, autre, souvenir)
        confiance = relations.axes(m, autre, id)['confiance']
        m = recharger(m)
        retenir_refus(m, id, autre, 'demander', 'mefiance', objet='vivres')
        memoriser(m, autre, souvenir)
        m = recharger(m)
        self.assertEqual(relations.axes(m, autre, id)['confiance'], confiance)
        self.assertTrue(any(s['raison'] == 'mefiance' for s in lire(m, id)['refus']))

    def test_rancune_et_faute_envers_un_autre(self):
        from donjon.pnj_propositions import rendre_service
        m, id, autre, c = scene(feu)
        lire(m, autre)['relations'][id] = relations._nouvelle({'confiance': 60, 'rancune': 42})
        retenir_refus(m, id, autre, 'demander', 'rancune', objet='vivres')
        faute = {'operation': 'prendre', 'cible': 'crochets', 'outil': '', 'lieu': '', 'condition': 'sans_temoin'}
        self.assertIsNone(rendre_service(m, id, 'faim', [faute]))
        self.assertEqual(lire(m, id)['recours_services'], [])
        self.assertTrue(rendre_service(m, id, 'faim', []))

    def test_sans_mandat_pas_de_droit_sur_un_bien_prive(self):
        from donjon.pnj_propositions import rendre_service
        m, id, autre, c = scene(reserve)
        m.objets[c['objet']]['proprietaire'] = autre
        self.assertIsNone(rendre_service(m, id, 'faim', []))
        self.assertEqual(relations.axes(recharger(m), autre, id)['confiance'], 25)

    def test_prestation_convenue_sans_double_service(self):
        from donjon import agendas
        from donjon.echanges import servir
        m, id, autre, c = scene(feu)
        m.objets['vivres'].update(lieu=id, proprietaire=id)
        agendas.prendre(m, id, {'pour': autre, 'condition': {'objet': 'vivres', 'servir': autre},
                              'minute': m.data['minutes'],
                              'paye': {'objet': 'vivres', 'prix': 1, 'quoi': 'tache'}})
        self.assertTrue(servir(m, id, 'vivres', autre, []))
        m = recharger(m)
        self.assertFalse(any(c.get('cause') == 'service_rendu' for c in m.data['chronique']))

    def test_un_refus_resolu_ne_reprend_pas_un_ancien_service(self):
        m, id, autre, c = scene(feu)
        self.assertTrue(plan_recours(m, id, 'faim', []))
        self.assertIsNotNone(lire(m, id)['service_en_cours'])
        # Le moyen ordinaire nouveau a abouti : sa réponse refusée n'existe plus.
        lire(m, id)['refus'].clear()
        lire(m, id)['demande_refusee'] = None
        m = recharger(m)
        self.assertIsNone(plan_recours(m, id, 'faim', []))
        self.assertIsNone(lire(m, id)['service_en_cours'])


if __name__ == '__main__':
    unittest.main()
