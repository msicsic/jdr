"""Un mandat vise une identité persistante, son admissibilité reste crue."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, corps, deliberation, planification
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_agendas_faire_confier as choix
from tests.test_tensions import recharger


class DestinatairesTests(unittest.TestCase):
    def recharge(self, m):
        data, texte, scene = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(n.data, data)
        self.assertEqual(regarder(n), texte)
        self.assertEqual(scene_percue(n), scene)
        return n

    def test_deux_deces_reels_recharges_puis_action_joueur(self):
        for cible in ('brune', 'ilse'):
            with self.subTest(cible=cible):
                m = creer('crue')
                corps.mourir(m, cible)
                m = self.recharge(m)
                moteur = Moteur(m)
                moteur.executer(moteur.preparer(proposition('attendre')))
                m = self.recharge(m)
                self.assertEqual(m.objets[cible]['type'], 'depouille')
                self.assertNotIn(cible, m.data['esprits'])

    def test_destinataire_cru_indisponible_termine_les_deux_charges(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            for etat in ('mort', 'parti'):
                with self.subTest(sorte=sorte, etat=etat):
                    m, _ = choix.FaireConfierTests().scene(sorte, cible)
                    croire(m, 'marchand', cible, 'etat', {etat: True}, 'savoir')
                    m = self.recharge(m)
                    # Une croyance suffit : la personne est réellement vivante.
                    self.assertEqual(m.objets[cible]['type'], 'personnage')
                    with patch.object(agendas, 'devis_observateur', side_effect=AssertionError('devis interdit')):
                        deliberation.choisir(m, 'marchand', m.data['minutes'])
                    m = self.recharge(m)
                    self.assertEqual(agendas.projets(m, 'marchand')[0]['etat'], 'abandonne')
                    self.assertFalse(agendas.enfants(m, 'marchand', 'evacuer'))

    def test_deces_cache_ne_change_ni_projection_ni_choix(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            for defunt in (cible, 'aubin'):
                with self.subTest(sorte=sorte, defunt=defunt):
                    m, p = choix.FaireConfierTests().scene(sorte, cible)
                    avant = agendas.planifier(m, 'marchand', 'evacuer')
                    transmis = [(cible, 'lieu')]
                    if sorte == 'informer':
                        transmis.append(('brasero', 'lieu'))
                    contexte = planification.ContexteDevis('marchand', 'aubin', transmis)
                    projection = contexte.projeter(m).data
                    devis = agendas.devis_observateur(m, 'marchand', 'evacuer', 'aubin', sorte,
                                                      p['parametres'], transmis=transmis)
                    esprit = copy.deepcopy(lire(m, 'marchand'))
                    corps.mourir(m, defunt)
                    self.assertEqual(lire(m, 'marchand'), esprit)
                    m = self.recharge(m)
                    self.assertEqual(contexte.projeter(m).data, projection)
                    self.assertEqual(agendas.devis_observateur(m, 'marchand', 'evacuer', 'aubin', sorte,
                                     p['parametres'], transmis=transmis), devis)
                    self.assertEqual(agendas.planifier(m, 'marchand', 'evacuer'), avant)

    def test_filiation_et_jugements_survivent_au_deces_du_destinataire(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            with self.subTest(sorte=sorte):
                aide = choix.FaireConfierTests()
                m, _ = aide.scene(sorte, cible)
                aide.executer(m, aide.choix(m)[1])
                enfants = agendas.enfants(m, 'marchand', 'evacuer')
                self.assertTrue(enfants)
                corps.mourir(m, cible)
                m = self.recharge(m)
                self.assertEqual(agendas.enfants(m, 'marchand', 'evacuer'), enfants)
                croire(m, 'marchand', cible, 'etat', {'mort': True}, 'savoir')
                deliberation.choisir(m, 'marchand', m.data['minutes'])
                self.recharge(m)

    def test_cible_inconnue_et_candidat_cru_indisponible_sans_exception(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, p = choix.FaireConfierTests().scene(sorte, cible)
            lire(m, 'marchand')['croyances'].pop(cible)
            m = self.recharge(m)
            self.assertIsNone(agendas.devis_observateur(m, 'marchand', 'evacuer', 'aubin', sorte,
                                                      p['parametres']))
            self.assertIsNone(agendas.planifier(m, 'marchand', 'evacuer'))
            for etat in ('mort', 'parti'):
                n, _ = choix.FaireConfierTests().scene(sorte, cible)
                croire(n, 'marchand', 'aubin', 'etat', {etat: True}, 'savoir')
                n = self.recharge(n)
                with patch.object(agendas, 'devis_observateur', side_effect=AssertionError('candidat interdit')):
                    r = agendas.planifier(n, 'marchand', 'evacuer')
                self.assertTrue(r)
                self.assertFalse(any('mandat' in e.get('contenu', {}) for e in r[1]))

    def test_groupe_garde_les_destinataires_encore_crus_disponibles(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, _ = choix.FaireConfierTests().scene(sorte, cible)
            autre = 'ilse' if cible == 'brune' else 'brune'
            lire(m, 'marchand')['agendas'][0]['parametres']['qui'] = [cible, autre]
            croire(m, 'marchand', autre, 'lieu', 'antichambre', 'savoir', salle='antichambre', case=None)
            croire(m, 'marchand', cible, 'etat', {'mort': True}, 'savoir')
            m = self.recharge(m)
            deliberation.choisir(m, 'marchand', m.data['minutes'])
            m = self.recharge(m)
            self.assertNotEqual(agendas.projets(m, 'marchand')[0]['etat'], 'abandonne')
            self.assertEqual(agendas.planifier(m, 'marchand', 'evacuer')[0]['qui'], autre)
