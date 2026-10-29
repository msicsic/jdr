"""Un contact social inaccessible se négocie avant toute demande ou acquisition."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon import planification as p, pnj
from donjon.deliberation import appels_vains, recherche_vaine, retenir_refus
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.support import calme, sans_souci
from tests.test_tensions import recharger, vivre
from tests.test_voix import appels, hugues_cherche_anselme


def capture():
    with gzip.open(Path(__file__).with_name('data') / 'appeler-275-crue-7-270.json.gz',
                   'rt', encoding='utf8') as fichier:
        return Monde(json.load(fichier))


def venue_possible():
    m = capture()
    # Autre scène : porte réellement déverrouillée, mais Ilse la croit encore
    # verrouillée. Gorm la sait ouverte au passage et n'a plus de charge locale.
    calme(m, 'marchand', 'aubin', 'brune')
    sans_souci(m, 'marchand', 'aubin', 'brune')
    e = lire(m, 'marchand')
    e['intention'] = e['rejoindre'] = e['rejoint'] = None
    m.objets['marchand']['profil']['pulsions'] = []
    e['pulsions'] = []
    m.objets['porte']['verrouillee'] = False
    croire(m, 'marchand', 'porte', 'verrouillee', False, 'vu')
    return m


class AppelerDonneurTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_capture_reelle_appel_negocie_vain_sans_rappel_par_delai(self):
        m = self.recharge(capture())
        avant = copy.deepcopy(m.data)
        resultat = p.planifier(m, 'ilse', 'faim')
        self.assertEqual(m.data, avant)
        self.assertEqual(resultat[1][-1]['contenu'], {'cherche': 'marchand'})
        self.assertFalse(any(g['operation'] in ('demander', 'acheter') for g in resultat[1]))
        m, _ = vivre(m, 5)
        m = self.recharge(m)
        self.assertEqual(len([a for a in appels(m, 'ilse') if a[0] >= 270]), 1)
        textes = [c['texte'] for c in m.data['chronique'] if c['minute'] >= 270]
        self.assertIn('Gorm répond : « Ici, viens ! »', textes)
        self.assertIn('Ilse répond : « Ici, viens ! »', textes)
        self.assertNotIn("Gorm répond : « J'arrive ! »", textes)
        self.assertIn('chambre_cloche', appels_vains(m, 'ilse', 'marchand'))
        for delai in (0, 121, 1440):
            r = Monde(copy.deepcopy(m.data))
            r.data['minutes'] += delai
            r = self.recharge(r)
            v = p.Vue(r, 'ilse')
            self.assertIsNone(p._appeler(v, p.depart(r, 'ilse', v), 'marchand'))

    def test_venue_puis_demande_et_achat_apres_retrouvailles(self):
        m, _ = vivre(self.recharge(venue_possible()), 5)
        m = self.recharge(m)
        textes = [c['texte'] for c in m.data['chronique'] if c['minute'] >= 270]
        arrivee = textes.index('Ilse retrouve Gorm, comme convenu.')
        self.assertIn("Gorm répond : « J'arrive ! »", textes[:arrivee])
        demande = next(i for i, t in enumerate(textes) if t.startswith('Ilse demande une part'))
        achat = next(i for i, t in enumerate(textes) if t.startswith('Ilse achète une part'))
        self.assertLess(arrivee, demande)
        self.assertLess(demande, achat)
        self.assertTrue(any(t.startswith('Ilse, meunière évacuée mange') for t in textes[achat:]))
        self.assertEqual(len([a for a in appels(m, 'ilse') if a[0] >= 270]), 1)
        self.assertLess(lire(m, 'ilse')['besoins']['faim'], 71)

    def test_autre_scenario_achat_objet_porte_et_refus_de_pret(self):
        m = hugues_cherche_anselme(verrou=True)
        croire(m, 'hugues', 'anselme', 'lieu', 'chambre_chaude', 'vu',
               salle='chambre_chaude', case=[2, 2])
        m.objets['lanterne_hugues'].update(lieu='anselme', proprietaire='anselme', prix=1, allume=True)
        croire(m, 'hugues', 'lanterne_hugues', 'lieu', 'anselme', 'vu', salle=None, case=None)
        retenir_refus(m, 'hugues', 'anselme', 'demander', 'refus', objet='lanterne_hugues')
        m = self.recharge(m)
        resultat = p.chercher(m, 'hugues', lambda v, e: 'lanterne_hugues' in e.portes,
                             {'prendre': ['lanterne_hugues']}, emplois=())
        self.assertIsNotNone(resultat)
        self.assertEqual([g['operation'] for g in resultat[1]], ['inspecter', 'acheter'])
        self.assertEqual(len(p._couper(resultat[1])), 1)
        self.assertEqual(m.objets['lanterne_hugues']['lieu'], 'anselme')
        # Le préfixe émet réellement le même appel ; la méfiance d'Anselme
        # produit le silence, jamais une acquisition hypothétique.
        pnj._executer_effet(m, 'hugues', p._couper(resultat[1])[0], [], [])
        m = self.recharge(m)
        self.assertEqual(len(appels(m, 'hugues')), 1)
        self.assertEqual(m.objets['lanterne_hugues']['lieu'], 'anselme')
        self.assertIn('couloir', appels_vains(m, 'hugues', 'anselme'))

    def test_position_reelle_cachee_ne_change_pas_le_contact_propose(self):
        m = capture()
        attendu = p.planifier(m, 'ilse', 'faim')
        for lieu, case in (('crypte', [1, 1]), ('chambre_cloche', [1, 1])):
            r = Monde(copy.deepcopy(m.data))
            r.objets['marchand'].update(lieu=lieu, position=case, position_salle=lieu)
            self.assertEqual(p.planifier(self.recharge(r), 'ilse', 'faim'), attendu)

    def test_negociation_apres_refus_contact_sans_offre_presumee(self):
        from donjon.pnj_propositions import recours
        m = capture()
        retenir_refus(m, 'ilse', 'marchand', 'demander', 'refus', objet='vivres', besoin='faim')
        e = lire(m, 'ilse')
        e['demande_refusee'] = {'de': 'marchand', 'objet': 'vivres', 'besoin': 'faim'}
        avant = copy.deepcopy(m.data)
        contact = recours(m, 'ilse', 'faim', [])
        self.assertEqual(contact['contenu'], {'cherche': 'marchand'})
        self.assertEqual(m.data, avant)
        recherche_vaine(m, 'ilse', 'marchand', 'chambre_cloche')
        m.data['minutes'] += 121
        self.assertIsNone(recours(self.recharge(m), 'ilse', 'faim', []))

    def test_hors_portee_aucun_appel_et_lieu_inconnu_garde_sa_recherche(self):
        m = capture()
        # Scène d'auteur : une pièce sans ouverture acoustique vers l'acteur.
        for salle, donnees in m.data['salles'].items():
            donnees['sorties'] = {d: x for d, x in donnees['sorties'].items()
                                 if salle != 'antichambre' and x['vers'] != 'antichambre'}
        # La salle lointaine du scénario est hors de portée par le calcul commun.
        from donjon.ouie import propager, parvenu, INTENSITES, SEUIL
        niveaux = propager(p.monde_cru(m, 'ilse'), 'chambre_cloche', (3, 3), INTENSITES['hele'])
        lointaines = [s for s in m.data['salles'] if (parvenu(niveaux, s, None) or (-99,))[0] < SEUIL]
        self.assertTrue(lointaines)
        croire(m, 'ilse', 'marchand', 'lieu', lointaines[0], 'savoir', salle=lointaines[0], case=None)
        v = p.Vue(self.recharge(m), 'ilse')
        self.assertIsNone(p._appeler(v, p.depart(v.monde, 'ilse', v), 'marchand'))
        croire(m, 'ilse', 'marchand', 'lieu', None, 'essai', salle=None, case=None)
        v = p.Vue(self.recharge(m), 'ilse')
        e = p.depart(v.monde, 'ilse', v)
        self.assertIsNone(p._appeler(v, e, 'marchand'))
        self.assertIsNotNone(p._chercher(v, e, 'marchand'))

    def test_laps_entier_decoupe_avec_recharges(self):
        for scene in (capture, venue_possible):
            with self.subTest(scene=scene.__name__):
                bloc, _ = vivre(self.recharge(scene()), 5)
                morceaux = self.recharge(scene())
                for _ in range(5):
                    morceaux, _ = vivre(morceaux, 1)
                self.assertEqual(bloc.data, morceaux.data)
                self.assertEqual(regarder(bloc), regarder(morceaux))
                self.assertEqual(scene_percue(bloc), scene_percue(morceaux))
                self.recharge(bloc)
