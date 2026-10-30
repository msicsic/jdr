"""306 : responsabilité déclarée, sans attribution ni évacuation imposée."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, banc_pnj, echanges, ecoute, esprits, pnj, planification
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.support import calme
from tests.test_avis_menace import relation
from tests.test_social import placer, recharger


RACINE = Path(__file__).parents[1]
CIBLES = ['ilse', 'brune', 'mael', 'seve']


class AgendaHameauTests(unittest.TestCase):
    def recharge(self, m):
        m.verifier()
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(regarder(n), regarder(m))
        self.assertEqual(scene_percue(n), scene_percue(m))
        sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
        self.assertEqual(ecoute.rendre(n, sons), ecoute.rendre(m, sons))
        return n

    def test_meme_charge_que_crue_et_extension_aux_evacués(self):
        def donnees(nom):
            return json.loads((RACINE / 'donjon' / nom).read_text(encoding='utf-8'))
        crue = donnees('scenario_crue.json')['objets']['marchand']['profil']['agendas'][0]
        hameau = donnees('scenario_crue_hameau.json')
        declarations = hameau['objets']['marchand']['profil']['agendas']
        attendu = copy.deepcopy(crue)
        attendu['parametres']['qui'] = CIBLES
        self.assertEqual(declarations, [attendu])
        self.assertFalse(any(o.get('profil', {}).get('agendas')
                             for q, o in hameau['objets'].items() if q != 'marchand'))
        self.assertFalse(hameau['engagements'])

    def test_activation_unique_sauvee_sans_mouvement_ni_mandat(self):
        for graine in (1985, 7, 42, 2024):
            with self.subTest(graine=graine):
                m = banc_pnj.creer('crue_hameau', graine)
                places = {q: m.objets[q]['lieu'] for q in CIBLES}
                agendas.actualiser(m, 'marchand')
                m = self.recharge(m)
                projet, = agendas.projets(m, 'marchand')
                self.assertEqual(projet['id'], 'evacuer_crue')
                self.assertEqual(projet['etat'], 'actif')
                self.assertEqual(projet['origine']['type'], 'scenario')
                self.assertEqual(projet['parametres']['qui'], CIBLES)
                self.assertFalse(agendas.enfants(m, 'marchand', projet['id']))
                self.assertEqual(banc_pnj.mesures_mandats(m)['mandats_proposes'], 0)
                avant = copy.deepcopy(m.data)
                agendas.actualiser(m, 'marchand')
                self.assertEqual(m.data, avant)
                self.assertEqual({q: m.objets[q]['lieu'] for q in CIBLES}, places)

    def test_nouveaux_evacués_demandent_un_accord_et_marchent_apres_recharge(self):
        # Scènes d'auteur : route ouverte, lumière, besoins calmes ; les autres
        # évacués sont déjà arrivés. La déclaration reste celle du scénario.
        for cible in ('mael', 'seve'):
            with self.subTest(cible=cible):
                m = banc_pnj.creer('crue_hameau', 1985, 'fixe')
                calme(m, *esprits.pnjs(m))
                m.objets['porte'].update(ouverte=True, verrouillee=False)
                placer(m, 'marchand', 'antichambre', [0, 2])
                placer(m, cible, 'antichambre', [0, 3])
                from donjon.deplacement_objet import deplacer
                deplacer(m, 'lanterne', cible)
                for index, q in enumerate(CIBLES):
                    if q != cible:
                        placer(m, q, 'chambre_cloche', [3 + index, 3])
                    salle = m.objets[q]['lieu']
                    esprits.croire(m, 'marchand', q, 'lieu', salle, 'vu',
                                   salle=salle, case=m.objets[q]['position'])
                relation(m, cible, 'marchand', confiance=100, affection=100)
                agendas.actualiser(m, 'marchand')
                m = self.recharge(m)
                with planification.vues_du_choix(m, 'marchand'):
                    resultat = agendas.planifier(m, 'marchand', 'evacuer_crue', cout=[])
                self.assertIsNotNone(resultat)
                demande = resultat[1][-1]
                self.assertEqual(demande['operation'], 'confier')
                self.assertEqual(demande['cible'], cible)
                with patch.object(Monde, 'd20', return_value=20):
                    self.assertTrue(echanges.executer(m, 'marchand', demande, []))
                m = self.recharge(m)
                self.assertEqual(m.objets[cible]['lieu'], 'antichambre')
                self.assertEqual(agendas.en_cours(m, cible)[0]['condition'],
                                 {'objet': cible, 'lieu': 'chambre_cloche'})
                for q in esprits.pnjs(m):
                    if q != cible:
                        esprits.lire(m, q)['libre'] = 1000000
                a, b = self.recharge(m), self.recharge(m)
                for n, tranches in ((a, (1800,)), (b, (300,) * 6)):
                    for dt in tranches:
                        pnj.avancer(n, ecouler(n, dt), [], dt)
                        self.recharge(n)
                self.assertEqual(a.data, b.data)
                self.assertEqual(a.objets[cible]['lieu'], 'chambre_cloche')
                esprits.croire(a, 'marchand', cible, 'lieu', 'chambre_cloche', 'dit:' + cible,
                               salle='chambre_cloche', case=None)
                agendas.actualiser(a, 'marchand')
                self.assertEqual(agendas.projets(self.recharge(a), 'marchand')[0]['etat'], 'atteint')
