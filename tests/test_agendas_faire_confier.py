"""260 : choix cru, parole réelle, filiation et recharge des deux charges."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, echanges, pnj, relations
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests import test_agendas_devis_observateur as observateur
from tests.test_social import placer
from tests.test_avis_menace import relation
from tests.test_tensions import recharger


class FaireConfierTests(unittest.TestCase):
    def scene(self, sorte='amener', cible='brune'):
        m, p, _ = observateur.DevisObservateurTests().scene(sorte, cible)
        lire(m, 'marchand')['agendas'][0].update(sorte=sorte, parametres=p['parametres'])
        for q, salle in [('marchand', 'crypte'), ('aubin', 'crypte'), (cible, 'beffroi')]:
            placer(m, q, salle, [1, 3] if salle == 'beffroi' else [2, 1] if q == 'aubin' else [1, 1])
            croire(m, 'marchand', q, 'lieu', salle, 'savoir', salle=salle, case=None)
        m.objets['cle']['lieu'] = 'aubin'
        croire(m, 'marchand', 'cle', 'lieu', 'aubin', 'savoir', salle='crypte', case=None)
        m.objets['marchand']['profil']['valeurs'].update(honnetete=100, douceur=100)
        relation(m, 'aubin', 'marchand', confiance=100, affection=100)
        for q in list(lire(m, 'marchand')['croyances']):
            if q not in ('marchand', 'aubin', cible, 'cle', 'brasero') and m.objets.get(q, {}).get('type') == 'personnage':
                lire(m, 'marchand')['croyances'].pop(q)
        return self.recharge(m), p

    def recharge(self, m):
        avant, texte, scene = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual(regarder(n), texte)
        self.assertEqual(scene_percue(n), scene)
        return n

    def choix(self, m):
        avant = copy.deepcopy(m.data)
        r = agendas.planifier(m, 'marchand', 'evacuer')
        self.assertEqual(m.data, avant)
        return r

    def executer(self, m, plan, roll=20):
        with patch.object(Monde, 'd20', return_value=roll):
            for etape in plan:
                self.assertIn(etape['operation'], ('dire', 'confier'))
                echanges.executer(m, 'marchand', etape, [])

    def test_deux_charges_choix_publication_parole_et_laps(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            with self.subTest(sorte=sorte):
                m, p = self.scene(sorte, cible)
                r = self.choix(m)
                self.assertEqual(r[1][-1]['cible'], 'aubin')
                self.assertEqual(r[1][-1]['contenu']['mandat']['sorte'], sorte)
                deliberation.choisir(m, 'marchand', m.data['minutes'])
                self.assertEqual(lire(m, 'marchand')['intention']['plan'], r[1])
                lieu = m.objets[cible]['lieu']
                self.executer(m, r[1])
                self.assertEqual(m.objets[cible]['lieu'], lieu)
                self.assertEqual(lire(m, 'marchand')['agendas'][0]['jugements'][-1]['issue'], 'accepte')
                m = self.recharge(m)
                self.assertEqual(self.choix(m)[1], [])
                enfant = agendas.enfants(m, 'marchand', 'evacuer')[0]
                charge = agendas.planifier(m, 'aubin', enfant['agenda'])
                self.assertIsNotNone(charge)
                self.assertTrue(any(e['operation'] == ('confier' if sorte == 'amener' else 'dire') for e in charge[1]))
                a, b = m.copier(), m.copier()
                pnj.avancer(a, ecouler(a, 1800), [], 1800)
                for _ in range(3):
                    pnj.avancer(b, ecouler(b, 600), [], 600)
                self.assertEqual(a.data, b.data)
                self.recharge(a)

    def test_prive_sans_effet_croyance_avec_effet(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, _ = self.scene(sorte, cible)
            r = self.choix(m)
            placer(m, 'aubin', 'chambre_cloche', [1, 1])
            lire(m, 'aubin')['croyances'].clear()
            m.objets['cle']['lieu'] = 'antichambre'
            relation(m, 'aubin', 'marchand', confiance=0, rancune=100)
            self.assertEqual(self.choix(self.recharge(m)), r)
            lire(m, 'marchand')['croyances']['aubin'].pop('lieu')
            self.assertNotEqual(self.choix(self.recharge(m)), r)

    def test_refus_retenu_puis_faire_soi_meme(self):
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            m, _ = self.scene(sorte, cible)
            relation(m, 'aubin', 'marchand', confiance=0, rancune=100)
            self.executer(m, self.choix(m)[1])
            m = self.recharge(m)
            self.assertFalse(agendas.enfants(m, 'marchand', 'evacuer'))
            self.assertTrue(lire(m, 'marchand')['refus'])
            for _ in range(3):
                self.assertFalse(any('mandat' in e.get('contenu', {}) for e in self.choix(m)[1]))

    def test_egalite_identifiant_et_autorite_estimee(self):
        m, _ = self.scene()
        self.assertEqual(relations.autorite_estimee(m, 'marchand', 'aubin', 'crypte', 'amener')['bonus'], 0)
        with patch.object(agendas, 'devis_observateur', return_value=(0, [])), \
             patch.object(relations, 'chance_demande', return_value=1):
            # Route nulle + deux paroles de 100 dixièmes chacune.
            propre = ({'type': 'agenda', 'agenda': 'evacuer', 'qui': 'brune'}, [])
            choisi = agendas.choisir_mandataire(m, 'marchand', 'evacuer', propre, [200 / 600])
            self.assertEqual(choisi[1][-1]['cible'], 'aubin')  # aubin < marchand

    def test_avis_est_transmis_sans_mesure_inventee(self):
        m, _ = self.scene('informer', 'ilse')
        avis = {'type': 'avis', 'objet': 'antichambre', 'attribut': 'menace', 'valeur': True}
        lire(m, 'marchand')['agendas'][0]['parametres'] = {'qui': ['ilse'], 'avis': avis}
        croire(m, 'marchand', 'antichambre', 'prevision', True, 'savoir')
        r = self.choix(self.recharge(m))
        self.assertTrue(any('avis' in e.get('contenu', {}) for e in r[1]))
        self.assertIn('mandat', r[1][-1]['contenu'])
        self.executer(m, r[1])
        self.recharge(m)
        self.assertIs(type(lire(m, 'aubin')['croyances']['antichambre']['prevision']['valeur']), bool)

    def test_refus_distingue_les_mandats_et_ne_se_rearme_pas_sur_sa_propre_trace(self):
        m, _ = self.scene()
        mandat = self.choix(m)[1][-1]['contenu']['mandat']
        deliberation.retenir_refus(m, 'marchand', 'aubin', 'confier', 'impossible',
                                  objet='brune', mandat=mandat)
        m = self.recharge(m)
        self.assertIsNotNone(deliberation.refus_retenu(m, 'marchand', 'aubin', ('confier',), 'brune', mandat=mandat))
        autre = copy.deepcopy(mandat)
        autre['parametres']['lieu'] = 'echoppe'
        self.assertIsNone(deliberation.refus_retenu(m, 'marchand', 'aubin', ('confier',), 'brune', mandat=autre))
        self.assertIsNone(deliberation.refus_retenu(m, 'marchand', 'aubin', ('confier',), 'brune'))

    def test_acceptation_laisse_les_autres_destinataires_essayables(self):
        m, _ = self.scene()
        self.executer(m, self.choix(m)[1])
        lire(m, 'marchand')['agendas'][0]['parametres']['qui'] = ['brune', 'ilse']
        croire(m, 'marchand', 'ilse', 'lieu', 'antichambre', 'savoir', salle='antichambre', case=None)
        r = self.choix(self.recharge(m))
        self.assertEqual(r[0]['qui'], 'ilse')


if __name__ == '__main__':
    unittest.main()




