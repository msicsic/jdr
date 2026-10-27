"""Racheter par l'achat commun : état, parole et sauvegarde concordent."""
import unittest
from unittest.mock import patch

from donjon import agendas, planification
from donjon.biens import richesse, proprietaire
from donjon.echanges import demander, executer
from donjon.esprits import lire, percevoir_tous
from donjon.pnj_propositions import reclamation
from donjon.rendu import regarder as rendu
from tests.test_reclamer_vol import preparer
from tests.test_tensions import recharger, vivre


def scene(autre=True):
    m, victime, porteur, objet = preparer(autre)
    m.objets[porteur]['profil']['valeurs']['honnetete'] = 0
    m.objets[victime]['profil']['valeurs']['douceur'] = 100
    m.data['finances_pnj'][victime] = 100
    # Le projet naît alors que le bien vaut 70 ; son détenteur le revend
    # ensuite 7. L'estimation persistante du projet n'est pas réécrite.
    m.objets[objet]['prix'] = 70
    percevoir_tous(m)
    agendas.actualiser(m, victime)
    m.objets[objet]['prix'] = 7
    return recharger(m), victime, porteur, objet


class RacheterTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        return n

    def test_refus_puis_rachat_par_la_recherche_deux_scenarios(self):
        for autre in (False, True):
            with self.subTest(autre=autre):
                m, id, vendeur, objet = scene(autre)
                self.assertFalse(executer(m, id, reclamation(m, id, objet)[-1], []))
                m = self.recharge(m)
                with planification.vues_du_choix(m, id):
                    suite = agendas.planifier(m, id, 'a1')
                self.assertIsNotNone(suite)
                achat = suite[1][-1]
                self.assertEqual(achat['operation'], 'acheter')
                avant = richesse(m, id), richesse(m, vendeur)
                lignes = []
                self.assertTrue(executer(m, id, achat, lignes))
                self.assertEqual((richesse(m, id), richesse(m, vendeur)), (avant[0]-7, avant[1]+7))
                self.assertEqual(m.objets[objet]['lieu'], id)
                self.assertEqual(proprietaire(m, objet), id)
                self.assertFalse(any(p['objet'] == objet for p in m.data.get('permissions', [])))
                self.assertEqual(lire(m, id)['croyances'][objet]['lieu']['valeur'], id)
                agendas.actualiser(m, id)
                self.assertEqual(agendas.projets(m, id)[0]['etat'], 'atteint')
                self.assertTrue(any('achète' in c['texte'] for c in m.data['chronique']))
                self.recharge(m)

    def test_pauvre_sans_achat_et_sans_transfert(self):
        m, id, vendeur, objet = scene()
        m.data['finances_pnj'][id] = 0
        self.assertFalse(executer(m, id, reclamation(m, id, objet)[-1], []))
        with planification.vues_du_choix(m, id):
            suite = agendas.planifier(m, id, 'a1')
        self.assertFalse(suite and any(g['operation'] == 'acheter' for g in suite[1]))
        self.assertEqual(demander(m, id, vendeur, objet, prix=7), 'pauvre')
        self.assertEqual(self.recharge(m).objets[objet]['lieu'], vendeur)

    def test_refus_vente_retenu_sans_republier(self):
        m, id, vendeur, objet = scene()
        geste = {'operation': 'acheter', 'cible': vendeur, 'outil': objet,
                 'contenu': {'prix': 7}, 'lieu': '', 'condition': ''}
        # Le besoin commun du vendeur interdit la vente comme tout achat.
        with patch('donjon.echanges.necessaire', return_value=True):
            self.assertFalse(executer(m, id, geste, []))
        m = self.recharge(m)
        avant = len(m.data['chronique'])
        self.assertFalse(executer(m, id, geste, []))
        self.assertEqual(len(m.data['chronique']), avant)
        with planification.vues_du_choix(m, id):
            suite = agendas.planifier(m, id, 'a1')
        self.assertFalse(suite and any(g['operation'] == 'acheter' for g in suite[1]))
        self.assertEqual(m.objets[objet]['lieu'], vendeur)
        self.recharge(m)

    def test_prix_borne_le_rachat_sans_forcer_le_projet(self):
        for autre in (False, True):
            m, id, vendeur, objet = preparer(autre)
            m.objets[vendeur]['profil']['valeurs']['honnetete'] = 0
            m.objets[id]['profil']['valeurs']['douceur'] = 100
            m.data['finances_pnj'][id] = 100
            m.objets[objet]['prix'] = 7
            agendas.actualiser(m, id)
            self.assertFalse(executer(m, id, reclamation(m, id, objet)[-1], []))
            m = self.recharge(m)
            with planification.vues_du_choix(m, id):
                self.assertIsNone(agendas.planifier(m, id, 'a1'))
            self.assertEqual(self.recharge(m).objets[objet]['lieu'], vendeur)

    def test_joueur_acheteur_par_sa_parole_existante(self):
        from donjon.paroles import preparer_parole
        from donjon.deplacement_objet import deplacer
        from tests.test_echanges_suite import JoueurReclameTests
        from tests.support import lier
        support = JoueurReclameTests()
        m = support.devant('brune')
        m.objets['couteau'].update(proprietaire='joueur', prix=7)
        m.joueur['or'] = 20
        deplacer(m, 'couteau', 'brune')
        if 'couteau' not in m.data['connus']:
            m.data['connus'].append('couteau')
        m.objets['brune']['profil']['valeurs']['honnetete'] = 0
        lier(m, 'brune', 'joueur', True)
        p = support.parole('brune', 'couteau')
        p['contenu'] = [{'type': 'demande', 'sujet': 'couteau', 'attribut': '', 'valeur': '7'}]
        travail, rapport = preparer_parole(self.recharge(m), p)
        self.assertEqual(travail.objets['couteau']['lieu'], 'joueur')
        self.assertEqual(proprietaire(travail, 'couteau'), 'joueur')
        self.assertEqual(travail.joueur['or'], 13)
        self.assertIn('prend tes 7 pièces', ' '.join(rapport['faits']))
        self.recharge(travail)

    def test_laps_entier_decoupe(self):
        for autre in (False, True):
            m, id, vendeur, objet = scene(autre)
            self.assertFalse(executer(m, id, reclamation(m, id, objet)[-1], []))
            a, _ = vivre(self.recharge(m), 3, jet=20)
            b = self.recharge(m)
            for _ in range(3):
                b, _ = vivre(b, 1, jet=20)
            self.assertEqual(a.data, b.data)
            self.assertEqual(a.objets[objet]['lieu'], id)
            self.assertEqual(rendu(a), rendu(self.recharge(b)))

    def test_honnete_rend_sans_encaisser_et_prix_insuffisant_refuse(self):
        for honnetete, prix, attendu in ((100, 7, 'rendu'), (0, 1, 'refus')):
            m, id, vendeur, objet = scene()
            m.objets[vendeur]['profil']['valeurs']['honnetete'] = honnetete
            avant = richesse(m, id), richesse(m, vendeur)
            self.assertEqual(demander(m, id, vendeur, objet, prix=prix), attendu)
            self.assertEqual((richesse(m, id), richesse(m, vendeur)), avant)
            self.assertEqual(self.recharge(m).objets[objet]['lieu'], id if attendu == 'rendu' else vendeur)
