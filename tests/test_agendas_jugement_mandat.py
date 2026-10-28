"""256 : jugement commun, autorité perçue et publication avant récit."""
import copy
import math
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, echanges, pnj, relations
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_agendas_amener_fin import declarer
from tests.test_avis_menace import relation
from tests.test_engagement_deplacement import scene
from tests.test_social import placer
from tests.test_tensions import recharger


class JugementMandatTests(unittest.TestCase):
    def scene(self, sorte='amener', cible='brune'):
        m, _ = scene('aubin')
        placer(m, cible, 'antichambre', [0, 1])
        croire(m, 'aubin', cible, 'lieu', 'antichambre', 'vu', salle='antichambre', case=[0, 1])
        relation(m, 'aubin', 'marchand', confiance=50, affection=0)
        m = declarer(m, cible, 'chambre_cloche')
        p = {'qui': cible, 'lieu': 'chambre_cloche'}
        if sorte == 'informer':
            croire(m, 'aubin', 'brasero', 'lieu', 'antichambre', 'savoir', salle='antichambre', case=None)
            p = {'qui': cible, 'fait': {'type': 'affirmation', 'sujet': 'brasero',
                                      'attribut': 'lieu', 'valeur': 'antichambre'}}
        return m, {'parent': 'evacuer', 'sorte': sorte, 'parametres': p}

    def statut(self, m, domaine='amener', lieu='antichambre'):
        from donjon.esprits import installer_statuts
        m.objets['marchand']['profil']['statuts'] = [
            {'titre': 'responsable', 'lieux': [lieu], 'domaines': [domaine], 'connus': ['aubin']}]
        installer_statuts(m, 'aubin')

    def jugement(self, m):
        return agendas.projets(m, 'marchand')[0]['jugements'][-1]

    def persiste(self, m):
        avant = copy.deepcopy(m.data)
        texte, vue = regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual(regarder(n), texte)
        self.assertEqual(scene_percue(n), vue)
        return n

    def roll_limite(self, m, mandat):
        # Mesurer le vrai DD commun, sans modifier ni consommer le monde testé.
        n = m.copier()
        with patch.object(Monde, 'd20', return_value=1):
            echanges.confier(n, 'marchand', 'aubin', mandat=mandat)
        j = self.jugement(n)
        return math.ceil(j['dd'] - (j['total'] - 1)) - 1

    def test_statut_portee_et_autre_sorte_apres_recharge(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, mandat = self.scene(sorte, cible)
            roll = self.roll_limite(m, mandat)
            self.assertIn(roll, range(1, 21))
            for domaine, lieu, attendu in [(sorte, 'antichambre', 'accepte'),
                                           (sorte, 'echoppe', 'refus'),
                                           ('combat', 'antichambre', 'refus')]:
                n = m.copier()
                self.statut(n, domaine, lieu)
                with patch.object(Monde, 'd20', return_value=roll) as jet:
                    self.assertEqual(echanges.confier(n, 'marchand', 'aubin', mandat=mandat), attendu)
                self.assertEqual(jet.call_count, 1)
                j = self.jugement(self.persiste(n))
                self.assertEqual(j['raison'], 'autorite' if attendu == 'accepte' else 'refus')
                self.assertEqual(bool(agendas.enfants(n, 'marchand', 'evacuer')), attendu == 'accepte')

    def test_dette_ascendant_adhesion_et_pas_obligation(self):
        m, mandat = self.scene()
        roll = self.roll_limite(m, mandat)
        for axes, jet, raison in [({'dette': 100}, roll, 'dette'),
                                  ({'ascendant': 100}, roll, 'autorite'),
                                  ({}, 20, 'adhesion')]:
            n = m.copier()
            relation(n, 'aubin', 'marchand', confiance=50, affection=0, **axes)
            with patch.object(Monde, 'd20', return_value=jet):
                self.assertEqual(echanges.confier(n, 'marchand', 'aubin', mandat=mandat), 'accepte')
            self.assertEqual(self.jugement(self.persiste(n))['raison'], raison)
        self.statut(m)
        relation(m, 'aubin', 'marchand', confiance=50, ascendant=100)
        self.assertEqual(relations.autorite_mandat(m, 'aubin', 'marchand', 'antichambre', 'amener')['bonus'], 5)
        with patch.object(Monde, 'd20', return_value=1):
            self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'refus')
        self.persiste(m)

    def test_accueil_et_impossibilite_avant_jet(self):
        for cause, axes in [('mefiance', {'confiance': 0}), ('rancune', {'confiance': 100, 'rancune': 100})]:
            m, mandat = self.scene()
            self.statut(m)
            relation(m, 'aubin', 'marchand', **axes)
            with patch.object(Monde, 'd20', side_effect=AssertionError('jet interdit')):
                self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), cause)
            self.assertEqual(self.jugement(self.persiste(m))['raison'], cause)
            self.assertEqual(agendas.enfants(m, 'marchand', 'evacuer'), [])
        m, mandat = self.scene()
        lire(m, 'aubin')['croyances'].pop('brune', None)
        with patch.object(Monde, 'd20', side_effect=AssertionError('jet interdit')):
            self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'impossible')
        self.persiste(m)

    def test_raison_avant_chronique_et_confirmation_sans_nouveau_jet(self):
        m, mandat = self.scene()
        original = pnj._chroniquer
        def chroniquer(monde, id, *args, **kwargs):
            if monde is m and id == 'aubin':
                self.assertEqual(self.jugement(monde)['raison'], 'adhesion')
            return original(monde, id, *args, **kwargs)
        with patch.object(pnj, '_chroniquer', side_effect=chroniquer), patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'accepte')
        m = self.persiste(m)
        with patch.object(Monde, 'd20', side_effect=AssertionError('relance sans jet')):
            self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'accepte')
        self.assertEqual(len(agendas.enfants(m, 'marchand', 'evacuer')), 1)
        self.persiste(m)

    def test_devis_pur_demande_ordinaire_inchangee(self):
        m, mandat = self.scene()
        avant = copy.deepcopy(m.data)
        self.assertIsNotNone(agendas.devis_mandat(m, 'marchand', 'evacuer', 'aubin', 'amener', mandat['parametres']))
        self.assertEqual(m.data, avant)
        n = m.copier()
        self.statut(n)
        relation(n, 'aubin', 'marchand', confiance=50, affection=0, ascendant=100)
        condition = {'objet': 'aubin', 'lieu': 'chambre_cloche'}
        with patch.object(Monde, 'd20', return_value=10):
            a = echanges.confier(m, 'marchand', 'aubin', condition)
            b = echanges.confier(n, 'marchand', 'aubin', condition)
        self.assertEqual(a, b)
        self.assertEqual(agendas.en_cours(m, 'aubin'), agendas.en_cours(n, 'aubin'))
        self.assertNotIn('jugements', agendas.projets(m, 'marchand')[0])

    def test_desespoir_et_execution_laps_decoupes(self):
        m, mandat = self.scene()
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'accepte')
        lire(m, 'aubin')['besoins']['faim'] = 99
        candidats = deliberation._candidats(m, 'aubin')
        faim = next(c for c in candidats if c.besoin == 'faim')
        agenda = next(c for c in candidats if c.besoin == 'agenda')
        self.assertLess(faim.urgence.palier, agenda.urgence.palier)
        a, b = self.persiste(m), self.persiste(m)
        for qui in ('marchand', 'brune', 'ilse'):
            lire(a, qui)['libre'] = lire(b, qui)['libre'] = 1000000
        with patch.object(Monde, 'd20', return_value=20):
            pnj.avancer(a, ecouler(a, 600), [], 600)
            for _ in range(2):
                pnj.avancer(b, ecouler(b, 300), [], 300)
        a, b = self.persiste(a), self.persiste(b)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))

    def test_deux_mandats_acceptes_executent_leur_parole_apres_recharge(self):
        from donjon import ecoute
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, mandat = self.scene(sorte, cible)
            self.statut(m, sorte)
            roll = self.roll_limite(self.scene(sorte, cible)[0], mandat)
            with patch.object(Monde, 'd20', return_value=roll):
                self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'accepte')
            self.assertEqual(self.jugement(m)['raison'], 'autorite')
            a, b = self.persiste(m), self.persiste(m)
            for qui in ('marchand', 'brune', 'ilse'):
                lire(a, qui)['libre'] = lire(b, qui)['libre'] = 1000000
            # Le destinataire de la demande écoute Aubin, puis marche par lui-même.
            for n in (a, b):
                relation(n, cible, 'aubin', confiance=100, affection=100)
            with patch.object(Monde, 'd20', return_value=20):
                pnj.avancer(a, ecouler(a, 1800), [], 1800)
                for _ in range(6):
                    pnj.avancer(b, ecouler(b, 300), [], 300)
            a, b = self.persiste(a), self.persiste(b)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))
            self.assertTrue(any(x['pnj'] == 'aubin' and
                                ('demande' in x['texte'] if sorte == 'amener' else 'dit' in x['texte'])
                                for x in a.data['chronique']))
            if sorte == 'amener':
                self.assertTrue(agendas.en_cours(a, cible))
                self.assertEqual(a.objets[cible]['lieu'], 'antichambre')
            else:
                self.assertEqual(lire(a, cible)['croyances']['brasero']['lieu']['valeur'], 'antichambre')
            self.assertEqual(ecoute.rendre(a, ecoute.entendus(a, -1, ecoute.ENTENDU)),
                             ecoute.rendre(b, ecoute.entendus(b, -1, ecoute.ENTENDU)))


if __name__ == '__main__':
    unittest.main()
