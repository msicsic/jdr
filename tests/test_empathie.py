"""Secours sur perceptions, moyens ordinaires et sauvegardes complètes."""
import copy
import unittest

from donjon.deliberation import _candidats, choisir, Palier, secours
from donjon.esprits import lire, percevoir_tous
from donjon import relations
from donjon.banc_pnj import creer
from tests.support import calme, regarder
from tests.test_tensions import placer, recharger


def scene(froid=False, joueur=False):
    m = creer('relais' if froid else 'mine', 1985, 'fixe')
    ids = [i for i, o in m.objets.items() if o.get('profil')]
    calme(m, *ids)
    for i in ids:
        m.objets[i]['profil']['pulsions'] = []
        m.objets[i]['profil']['agendas'] = []
        m.objets[i]['profil']['situation'] = {}
        e = lire(m, i)
        e['pulsions'] = []
        e.pop('agendas', None)
        e['intention'] = None
        e['libre'] = 60000
        m.objets[i]['profil']['valeurs'].update(altruisme=0, empathie=0)
    auteur, autre = ('brune', 'marchand') if froid else ('mathe', 'lucien')
    salle = 'echoppe' if froid else 'baraquement'
    placer(m, auteur, salle, [3, 3])
    placer(m, autre, salle, [4, 3])
    m.joueur.update(salle=salle, position=[3, 4])
    if joueur:
        autre = 'joueur'
    m.objets[auteur]['profil']['valeurs'].update(altruisme=60, empathie=80)
    lire(m, auteur)['libre'] = 0
    lire(m, auteur)['relations'][autre] = relations._nouvelle({'affection': 40})
    besoins = m.joueur['besoins'] if joueur else lire(m, autre)['besoins']
    besoins['chaleur' if froid else 'faim'] = 85.
    if froid:
        m.objets['brasero'].update(allume=True, combustible=8)
        m.objets['bois'].update(lieu=auteur, proprietaire=auteur)
    else:
        m.objets['vivres'].update(lieu=auteur, proprietaire=auteur, portions=8)
    regarder(m, auteur, autre)
    regarder(m, autre, auteur)
    regarder(m, 'joueur', auteur)
    percevoir_tous(m)
    return recharger(m), auteur, autre


def scene_repas(joueur=False):
    """Service depuis les vivres portés, sans premier but d'achat distinct."""
    from donjon.esprits import constater
    m, auteur, autre = scene(joueur=joueur)
    for objet, o in m.objets.items():
        if o['type'] == 'nourriture' and objet != 'vivres':
            o['portions'] = 0
            if objet in lire(m, auteur)['croyances']:
                constater(m, auteur, objet, 'essai')
    return recharger(m), auteur, autre


def rendu(m):
    from donjon.rendu import regarder
    from donjon.carte import carte
    return regarder(m), carte(m)


def executer(m, minutes):
    from donjon.temps import ecouler, MINUTE
    from donjon.pnj import avancer
    dt = minutes * MINUTE
    ecoulees = ecouler(m, dt)
    lignes = []
    avancer(m, ecoulees, lignes, dt)
    return lignes


class EmpathieTests(unittest.TestCase):
    def test_credit_du_froid_sans_charge_joueur_et_pnj_sans_double(self):
        from donjon.moteur import Moteur, proposition
        from donjon.operations import sequence, etape
        for auteur_joueur in (False, True):
            with self.subTest(auteur_joueur=auteur_joueur):
                m, auteur, autre = scene(True)
                if auteur_joueur:
                    auteur = 'joueur'
                    m.objets['bois'].update(lieu=auteur, proprietaire=auteur)
                    regarder(m, autre, auteur)
                    regarder(m, auteur, 'brasero')
                percevoir_tous(m)
                avant = relations.envers(m, autre, auteur)['confiance']
                m = recharger(m)
                if auteur_joueur:
                    moteur = Moteur(m)
                    texte = moteur.executer(moteur.preparer(sequence(etape('alimenter', 'brasero', outil='bois'))))
                    self.assertIn('recharg', texte)
                else:
                    executer(m, 3)
                m = recharger(m)
                preuves = [s for s in lire(m, autre)['memoire'] if s['type'] == 'service_rendu' and s['de'] == auteur]
                self.assertEqual(len(preuves), 1)
                self.assertEqual(relations.envers(m, autre, auteur)['confiance'], avant + 20)
                self.assertGreater(m.objets['brasero']['combustible'], 8)
                self.assertEqual(rendu(m), rendu(recharger(m)))
                from donjon.esprits import memoriser
                memoriser(m, autre, preuves[0])
                self.assertEqual(relations.envers(recharger(m), autre, auteur)['confiance'], avant + 20)

    def test_credit_froid_exige_manque_local_et_effet_constate(self):
        from donjon import services
        from donjon.esprits import constater
        for cas in ('utile', 'allumage', 'chaud', 'distant', 'sans_effet', 'non_vu', 'pulsion_egalement'):
            with self.subTest(cas=cas):
                m, auteur, autre = scene(True)
                if cas == 'allumage':
                    m.objets['brasero']['allume'] = False
                if cas == 'chaud':
                    lire(m, autre)['besoins']['chaleur'] = 0
                if cas == 'distant':
                    placer(m, autre, 'antichambre', [1, 3])
                if cas == 'non_vu':
                    regarder(m, autre, [5, 3])
                if cas == 'pulsion_egalement':
                    m.objets[autre]['profil']['pulsions'] = [{'besoin': 'devoir', 'condition': {'objet': 'brasero', 'allume': True}}]
                    lire(m, autre)['pulsions'] = []
                percevoir_tous(m)
                constater(m, autre, 'brasero', 'essai')
                avant = services.preparer(m, auteur, 'brasero', 'alimenter')
                if cas != 'sans_effet':
                    m.objets['brasero']['combustible'] += 120
                    m.objets['brasero']['allume'] = True
                services.constater(m, auteur, 'brasero', avant)
                m = recharger(m)
                preuves = [s for s in lire(m, autre)['memoire'] if s['type'] == 'service_rendu' and s['de'] == auteur]
                self.assertEqual(len(preuves), int(cas in ('utile', 'allumage', 'pulsion_egalement')))
                self.assertNotIn('allume', lire(m, autre)['croyances']['brasero'])
                self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_feu_convenu_pas_de_second_credit_du_froid(self):
        from donjon import agendas
        m, auteur, autre = scene(True)
        agendas.prendre(m, auteur, {'pour': autre, 'condition': {'objet': 'brasero', 'allume': True},
                                  'minute': m.data['minutes']})
        m = recharger(m)
        executer(m, 3)
        m = recharger(m)
        self.assertGreater(m.objets['brasero']['combustible'], 8)
        self.assertFalse(any(s['type'] == 'service_rendu' and s['de'] == auteur
                             for s in lire(m, autre)['memoire']))
        self.assertTrue(any(s['type'] == 'engagement_tenu' and s['pour'] == autre
                            for s in lire(m, auteur)['memoire']))
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_repas_visible_dans_le_journal_joueur_compris(self):
        from donjon.moteur import Moteur, proposition
        for joueur in (False, True):
            with self.subTest(joueur=joueur):
                m, auteur, autre = scene_repas(joueur=joueur)
                moteur = Moteur(m)
                texte = moteur.executer(moteur.preparer(proposition('attendre')))
                m = recharger(m)
                besoins = m.joueur['besoins'] if joueur else lire(m, autre)['besoins']
                self.assertLess(besoins['faim'], 70)
                visible = 'te sert une part' if joueur else 'parle à voix basse'
                self.assertIn(visible, texte)
                self.assertIn(visible, str(m.data['journal']))
                self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_mathe_sert_sans_charge_une_fois_et_recharge(self):
        m, auteur, autre = scene_repas()
        self.assertTrue(list(secours(m, auteur)))
        b = recharger(m.copier())
        executer(m, 6)
        for _ in range(3):
            executer(b, 2)
            b = recharger(b)
        m = recharger(m)
        self.assertEqual(m.data, b.data)
        self.assertEqual(rendu(m), rendu(b))
        repas = [c for c in m.data['chronique'] if c['pnj'] == auteur and 'donne une part' in c['texte']]
        self.assertEqual(len(repas), 1)
        self.assertLess(lire(m, autre)['besoins']['faim'], 70)
        self.assertFalse(list(secours(m, auteur)))
        self.assertIn('donne une part', str(m.data['chronique']))
        services = [s for s in m.data['chronique'] if s.get('cause') == 'service_rendu' and s.get('relation') == auteur]
        self.assertEqual(len(services), 1)

    def test_transi_et_joueur_feu_entretenu_sans_charge(self):
        for joueur in (False, True):
            with self.subTest(joueur=joueur):
                m, auteur, autre = scene(True, joueur)
                self.assertTrue(list(secours(m, auteur)))
                b = recharger(m.copier())
                executer(m, 3)
                for _ in range(3):
                    executer(b, 1)
                    b = recharger(b)
                m = recharger(m)
                self.assertEqual(m.data, b.data)
                self.assertEqual(rendu(m), rendu(b))
                self.assertGreater(m.objets['brasero']['combustible'], 8)
                self.assertEqual(sum('alimente le brasero' in c['texte'] for c in m.data['chronique']), 1)
                self.assertFalse(list(secours(m, auteur)))

    def test_hostile_sans_souci_dos_noir_absent_et_apaisement(self):
        for cas in ('hostile', 'sans_souci', 'dos', 'noir', 'absent', 'apaise'):
            with self.subTest(cas=cas):
                m, auteur, autre = scene()
                if cas == 'hostile':
                    lire(m, auteur)['relations'][autre] = relations._nouvelle({'rancune': 80, 'affection': 40})
                elif cas == 'sans_souci':
                    m.objets[auteur]['profil']['valeurs'].update(altruisme=0, empathie=5)
                elif cas == 'dos':
                    regarder(m, auteur, [2, 3])
                elif cas == 'noir':
                    for o in m.objets.values():
                        if 'allume' in o:
                            o['allume'] = False
                elif cas == 'absent':
                    choisir(m, auteur, m.data['minutes'])
                    self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
                    placer(m, autre, 'galerie', [3, 1])
                else:
                    choisir(m, auteur, m.data['minutes'])
                    self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
                    lire(m, autre)['besoins']['faim'] = 0.
                percevoir_tous(m)
                m = recharger(m)
                self.assertFalse(list(secours(m, auteur)))
                executer(m, 1)
                m = recharger(m)
                self.assertFalse(any(c['pnj'] == auteur and 'donne une part' in c['texte'] for c in m.data.get('chronique', [])))
                self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_propre_faim_prioritaire_et_choix_pur(self):
        m, auteur, _ = scene()
        avant = copy.deepcopy(m.data)
        cs = list(_candidats(m, auteur))
        self.assertEqual(m.data, avant)
        self.assertTrue(any(c.urgence.palier == Palier.SECOURS for c in cs))
        lire(m, auteur)['besoins']['faim'] = 90.
        choisir(m, auteur, m.data['minutes'])
        self.assertEqual(lire(m, auteur)['intention']['motif'], 'faim')
        executer(m, 1)
        m = recharger(m)
        self.assertLess(lire(m, auteur)['besoins']['faim'], 70)


if __name__ == '__main__':
    unittest.main()
