"""Le recours de restitution reste une parole réelle et une remise sauvegardée."""
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, planification, relations
from donjon.esprits import lire, percevoir_tous, croire
from donjon.rendu import regarder as rendu
from donjon.pnj_propositions import reclamation
from tests.test_agendas_evenement import scene
from tests.test_tensions import recharger, vivre
from tests.support import regarder


def preparer(autre=False):
    m, victime, porteur, objet = scene(autre)
    for qui in (victime, porteur):
        m.objets[qui]['profil']['pulsions'] = []
        lire(m, qui)['pulsions'] = []
        lire(m, qui)['intention'] = None
    regarder(m, porteur, victime)
    regarder(m, victime, porteur)
    m.objets[porteur]['profil']['valeurs']['honnetete'] = 100
    percevoir_tous(m)
    return recharger(m), victime, porteur, objet


class ReclamerVolTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        return n

    def test_deux_restitutions_autonomes(self):
        for autre in (False, True):
            with self.subTest(autre=autre):
                m, victime, porteur, objet = preparer(autre)
                deliberation.choisir(m, victime, m.data['minutes'])
                geste = lire(m, victime)['intention']['plan'][-1]
                self.assertEqual(geste['contenu'], {'type': 'reclamer', 'sujet': objet})
                m, lignes = vivre(self.recharge(m), 3, jet=20)
                self.assertEqual(m.objets[objet]['lieu'], victime)
                self.assertEqual(m.objets[objet]['proprietaire'], victime)
                agendas.actualiser(m, victime)
                self.assertEqual(agendas.projets(m, victime)[0]['etat'], 'atteint')
                self.assertTrue(any(c['pnj'] == victime and 'réclame' in c['texte']
                                    and '(rendu)' in c['texte'] for c in m.data['chronique']))
                if autre:
                    self.assertIn('lui rend le marteau', ' '.join(lignes))
                self.recharge(m)

    def test_refus_et_peur_empechent_le_recours(self):
        for cause in ('necessaire', 'mefiance', 'peur'):
            with self.subTest(cause=cause):
                m, victime, porteur, objet = preparer()
                self.assertIsNotNone(reclamation(m, victime, objet))
                if cause == 'peur':
                    for n in range(4):
                        relations.souvenir(m, victime, {'type': 'subi', 'auteur': porteur,
                                                       'operation': 'frapper', 'preuve': f'coup:{n}'})
                    self.assertTrue(relations.craint(m, victime, porteur))
                else:
                    deliberation.retenir_refus(m, victime, porteur, 'demander', cause, objet=objet)
                m = self.recharge(m)
                self.assertIsNone(reclamation(m, victime, objet))

    def test_recours_hors_recherche(self):
        m, victime, porteur, objet = preparer()
        agendas.actualiser(m, victime)
        with patch('donjon.planification.chercher', side_effect=AssertionError('recherche')):
            with planification.vues_du_choix(m, victime):
                self.assertIsNotNone(agendas.planifier(m, victime, 'a1'))
        self.recharge(m)

    def test_laps_entier_et_decoupe(self):
        m, victime, porteur, objet = preparer(True)
        a, _ = vivre(self.recharge(m), 3, jet=20)
        b = self.recharge(m)
        for _ in range(3):
            b, _ = vivre(b, 1, jet=20)
        self.assertEqual(a.data, b.data)
        self.assertEqual(rendu(a), rendu(self.recharge(b)))

    def test_absence_crue_sans_lecture_de_position_reelle(self):
        m, victime, porteur, objet = preparer(True)
        croire(m, victime, porteur, 'lieu', 'crypte', 'savoir', salle='crypte', case=None)
        self.assertIsNone(reclamation(self.recharge(m), victime, objet))
        croire(m, victime, porteur, 'lieu', m.objets[victime]['lieu'], 'savoir',
               salle=m.objets[victime]['lieu'], case=list(m.objets[porteur]['position']))
        # La proposition utilise la croyance ; l'exécution commune revalide
        # l'absence réelle, sans remise à distance.
        m.objets[porteur]['lieu'] = 'crypte'
        geste = reclamation(m, victime, objet)[-1]
        from donjon.echanges import executer
        self.assertFalse(executer(m, victime, geste, []))
        self.assertEqual(m.objets[objet]['lieu'], porteur)
        self.recharge(m)

    def test_porteur_cru_inconscient_n_est_pas_un_interlocuteur(self):
        m, victime, porteur, objet = preparer(True)
        etat = dict(lire(m, victime)['croyances'][porteur]['etat']['valeur'])
        etat['conscient'] = False
        croire(m, victime, porteur, 'etat', etat, 'essai')
        self.assertIsNone(reclamation(self.recharge(m), victime, objet))

    def test_refus_reel_retenu_puis_reprise_existante(self):
        from donjon.echanges import executer
        from donjon.pnj import _executer
        from tests.test_temps_etat import plan
        for autre in (False, True):
            m, victime, porteur, objet = preparer(autre)
            m.objets[porteur]['profil']['valeurs']['honnetete'] = 0
            agendas.actualiser(m, victime)
            geste = reclamation(m, victime, objet)[-1]
            lignes = []
            self.assertFalse(executer(m, victime, geste, lignes))
            self.assertEqual(m.objets[objet]['lieu'], porteur)
            m = self.recharge(m)
            self.assertEqual(deliberation.refus_retenu(
                m, victime, porteur, ('demander',), objet=objet)['raison'], 'refus')
            self.assertIsNone(reclamation(m, victime, objet))
            # L'occasion change : le porteur dépose le bien. Le refus n'a
            # jamais interdit les moyens ordinaires de reprise.
            self.assertTrue(_executer(m, porteur, plan('poser', objet,
                lieu=m.objets[porteur]['lieu']), [], []))
            regarder(m, victime, objet)
            percevoir_tous(m)
            with planification.vues_du_choix(m, victime):
                suite = agendas.planifier(m, victime, 'a1')
            self.assertEqual(suite[1][-1]['operation'], 'prendre')
            for g in suite[1]:
                self.assertTrue(_executer(m, victime, g, [], []))
            from donjon.esprits import constater_possession
            constater_possession(m, victime, objet, 'essai')
            agendas.actualiser(m, victime)
            self.assertEqual(agendas.projets(self.recharge(m), victime)[0]['etat'], 'atteint')

    def test_joueur_porteur_recoit_et_choisit(self):
        from donjon.echanges import executer
        from donjon.deplacement_objet import deplacer
        from donjon.moteur import Moteur, proposition
        from tests.test_tensions import placer
        for rendre in (False, True):
            m, victime, porteur, objet = preparer(True)
            salle = m.objets[victime]['lieu']
            m.joueur.update(salle=salle, position=[7, 3])
            placer(m, porteur, 'crypte', (2, 2))
            deplacer(m, objet, 'joueur')
            regarder(m, victime, 'joueur'); regarder(m, 'joueur', victime)
            percevoir_tous(m)
            agendas.actualiser(m, victime)
            m = self.recharge(m)
            lignes = []
            self.assertFalse(executer(m, victime, reclamation(m, victime, objet)[-1], lignes))
            self.assertIn('te réclame le marteau', ' '.join(lignes))
            self.assertEqual(m.objets[objet]['lieu'], 'joueur')
            m = self.recharge(m)
            self.assertIsNone(reclamation(m, victime, objet))
            if rendre:
                moteur = Moteur(m)
                texte = moteur.executer(moteur.preparer(proposition('remettre', objet, victime)))
                self.assertIn('marteau', texte)
                agendas.actualiser(m, victime)
                self.assertEqual(m.objets[objet]['lieu'], victime)
                projet = next(a for a in agendas.projets(m, victime) if a['sorte'] == 'récupérer')
                self.assertEqual(projet['etat'], 'atteint')
            else:
                m, _ = vivre(m, 1, jet=20)
                self.assertEqual(m.objets[objet]['lieu'], 'joueur')
            self.recharge(m)

    def test_refus_puis_violence_au_cout_commun(self):
        from donjon.echanges import executer
        from tests.test_tensions import placer
        m, victime, porteur, objet = preparer(True)
        # Scène d'auteur : enjeu suffisant, victime prête à la force, aucun
        # témoin cru. Aucun coût ni autorisation de la recherche n'est changé.
        m.objets[objet]['prix'] = 100
        m.objets[porteur]['profil']['valeurs']['honnetete'] = 0
        m.objets[victime]['profil']['valeurs'].update(
            honnetete=0, douceur=0, ambition=100, fierte=100, courage=100)
        m.objets[victime]['profil']['caracteristiques']['FOR'] = 20
        colonne = 2
        for qui, x in m.objets.items():
            if x['type'] == 'personnage' and qui not in (victime, porteur):
                placer(m, qui, 'crypte', (colonne, 2))
                croire(m, victime, qui, 'lieu', 'crypte', 'savoir', salle='crypte', case=[colonne, 2])
                colonne += 1
        m.joueur.update(salle='crypte', position=[1, 1])
        croire(m, victime, 'joueur', 'lieu', 'crypte', 'savoir', salle='crypte', case=[1, 1])
        agendas.actualiser(m, victime)
        self.assertFalse(executer(m, victime, reclamation(m, victime, objet)[-1], []))
        m = self.recharge(m)
        regarder(m, porteur, (8, 3)); percevoir_tous(m)
        deliberation.choisir(m, victime, m.data['minutes'])
        self.assertIn('assommer', [g['operation'] for g in lire(m, victime)['intention']['plan']])
        from donjon.pnj import _executer
        from donjon.monde import Monde
        gestes = list(lire(m, victime)['intention']['plan'])
        m = self.recharge(m)
        # Exécuter les gestes réellement validés et recharger entre eux ; les
        # interruptions externes de l'autonomie ne font pas partie de ce lot.
        with patch.object(Monde, 'd20', return_value=20):
            for geste in gestes:
                self.assertTrue(_executer(m, victime, geste, [], []))
                m = self.recharge(m)
        self.assertEqual(m.objets[objet]['lieu'], victime)
        from donjon.esprits import constater_possession
        constater_possession(m, victime, objet, 'essai')
        agendas.actualiser(m, victime)
        self.assertEqual(agendas.projets(self.recharge(m), victime)[0]['etat'], 'atteint')

    def test_rendu_joueur_selon_cause_reelle(self):
        from donjon.paroles import preparer_parole
        from donjon.deplacement_objet import deplacer
        from tests.test_echanges_suite import JoueurReclameTests
        from tests.support import lier
        for cause, fragment in [('refus', 'refuse de te rendre'),
                                ('mefiance', 'ne te fait pas confiance'),
                                ('rancune', "t'en veut encore"),
                                ('necessaire', "s'en sert encore"),
                                ('absent', 'ne porte rien à toi'),
                                ('rendu', 'te rend le couteau')]:
            with self.subTest(cause=cause):
                support = JoueurReclameTests()
                m = support.devant('brune')
                m.objets['couteau']['proprietaire'] = 'joueur'
                m.data['connus'].append('couteau')
                deplacer(m, 'couteau', 'brune')
                m.objets['brune']['profil']['valeurs']['honnetete'] = 100 if cause != 'refus' else 0
                lier(m, 'brune', 'joueur', cause != 'mefiance')
                if cause == 'rancune':
                    r = lire(m, 'brune')['relations']['joueur']
                    r['rancune'] = 80; r['bandes']['rancune'] = True
                    r['ancrages']['rancune'] = [80, m.data['minutes']]
                if cause == 'necessaire':
                    m.objets['brune']['profil']['pulsions'] = [
                        {'besoin': 'faim', 'condition': {'objet': 'couteau', 'lieu': 'crypte'}}]
                    lire(m, 'brune')['pulsions'] = [None]
                if cause == 'absent':
                    deplacer(m, 'couteau', 'echoppe')
                m = self.recharge(m)
                travail, rapport = preparer_parole(m, support.parole('brune', 'couteau'))
                self.assertIn(fragment, ' '.join(rapport['faits']))
                self.assertEqual(travail.objets['couteau']['lieu'],
                                 'joueur' if cause == 'rendu' else 'echoppe' if cause == 'absent' else 'brune')
                self.recharge(travail)
