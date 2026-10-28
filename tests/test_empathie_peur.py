"""Compagnie de secours : signes, approche, temps vécu et recharge du monde entier."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as d, planification as p, relations, signes
from donjon.banc_pnj import creer
from donjon.esprits import lire, percevoir_tous
from donjon.scene import scene_percue
from donjon.spatial import proche
from donjon.temps import MINUTE
from tests.support import calme, presentes, regarder
from tests.test_corps_blessable import passer
from tests.test_empathie import rendu
from tests.test_tensions import placer, recharger


def scene(scenario='relais'):
    m = presentes(creer(scenario, 1985, 'fixe'))
    ids = [i for i, o in m.objets.items() if o.get('profil')]
    calme(m, *ids)
    auteur, autre, salle, ailleurs = (('aubin', 'ilse', 'antichambre', 'echoppe')
                                    if scenario == 'relais' else
                                    ('mathe', 'lucien', 'baraquement', 'galerie'))
    for n, i in enumerate(ids):
        profil = m.objets[i]['profil']
        profil.update(pulsions=[], agendas=[], situation={}, protege=[], alerte=9)
        profil['valeurs'].update(altruisme=0, empathie=0)
        e = lire(m, i)
        e.update(pulsions=[], intention=None, libre=60000)
        e.pop('agendas', None)
        from donjon.geometrie import cases
        placer(m, i, ailleurs, sorted(cases(m.data['salles'][ailleurs]))[n])
    placer(m, auteur, salle, [2, 5])
    placer(m, autre, salle, [5, 5])
    m.joueur.update(salle=salle, position=[3, 6], orientation='nord')
    lire(m, auteur)['libre'] = 0
    m.objets[auteur]['profil']['valeurs'].update(altruisme=60, empathie=80)
    lire(m, auteur)['relations'][autre] = relations._nouvelle({'affection': 40})
    lire(m, autre)['relations'][auteur] = relations._nouvelle({'affection': 40, 'confiance': 70})
    lire(m, autre)['besoins']['securite'] = 85.
    regarder(m, auteur, autre)
    regarder(m, autre, [6, 5])  # Il l'entendra tout près, sans le voir arriver de loin.
    percevoir_tous(m)
    return recharger(m), auteur, autre


def peur(m, auteur):
    return [x for x in d.secours(m, auteur) if x[1] == 'peur']


def visible(m):
    return rendu(m), scene_percue(m)


class CompagnieTests(unittest.TestCase):
    def test_cinq_reprises_reelles_perte_et_retour_physiques_du_signe(self):
        from donjon.monde import Monde
        dossier = Path(__file__).parent / 'data' / 'scenes' / 'rester-266'
        fichiers = sorted(dossier.glob('suspect-*.json.gz'))
        self.assertEqual(len(fichiers), 5)
        for fichier in fichiers:
            with self.subTest(capture=fichier.name):
                charge = json.loads(gzip.decompress(fichier.read_bytes()))
                acteur, autre = charge['acteur'], charge['beneficiaire']
                empreintes = []
                for phase in ('interruption', 'reprise'):
                    m = Monde(copy.deepcopy(charge[phase]))
                    n = recharger(m)
                    self.assertEqual(m.data, n.data)
                    self.assertEqual(visible(m), visible(n))
                    avant = copy.deepcopy(m.data)
                    for _ in range(3):
                        self.assertEqual(autre in d.detresses_percues(m, acteur), phase == 'reprise')
                    self.assertEqual(m.data, avant)
                    self.assertTrue(d.calme_pour_secourir(m, acteur))
                    if phase == 'interruption':
                        demande = d.agendas.contrat_intention(m, acteur)['demande']
                        self.assertEqual(d._fin_demande(m, acteur, demande)[0], 'dementie')
                    else:
                        self.assertTrue(any(s['personnage'] == autre and s['signe'] == 'surveille'
                                            for s in signes.percus(m, acteur)))
                    # Même choix après recharge ; aucun secours réinstallé par une relecture seule.
                    for monde in (m, n):
                        d.choisir(monde, acteur, monde.data['minutes'])
                    self.assertEqual(m.data, n.data)
                    i = lire(m, acteur)['intention'] or {}
                    self.assertEqual(i.get('but') == {'type': 'pulsion', 'pres': autre}, phase == 'reprise')
                    self.assertEqual(m.data, recharger(m).data)
                    self.assertEqual(visible(m), visible(recharger(m)))
                    empreintes.append({x: {k: charge[phase]['objets'][x].get(k)
                                                for k in ('lieu', 'position', 'orientation')}
                                        for x in (acteur, autre)})
                self.assertNotEqual(*empreintes)  # Le monde perçu a réellement changé entre les deux.

    def test_gorm_attend_un_moyen_sur_pour_le_feu_mais_execute_encore_sa_ronde(self):
        from donjon.monde import Monde
        dossier = Path(__file__).parent / 'data' / 'scenes' / 'rester-266'
        for minute in (85, 208):
            with self.subTest(minute=minute):
                m = Monde(json.loads(gzip.decompress((dossier / f'gorm-{minute}.json.gz').read_bytes())))
                m = recharger(m)
                self.assertIn('devoir', d.urgents(m, 'marchand'))
                # Le brasero reste inaccessible sans séjour humide ; les bois eux existent.
                v = p.Vue(m, 'marchand')
                self.assertTrue(d._disponible_cru(m, 'marchand', 'bois'))
                self.assertIsNone(v.route(p.depart(m, 'marchand', v), 'echoppe'))
                self.assertIsNone(d._plan_pulsion(m, 'marchand', {'objet': 'brasero', 'allume': True}, True))
                self.assertTrue(d._delegue(m, 'marchand', m.objets['marchand']['profil']['pulsions'][0]))
                d.choisir(m, 'marchand', m.data['minutes'])
                if minute == 85:
                    self.assertIsNone(lire(m, 'marchand')['intention'])
                    self.assertEqual(d.inactivite(m, 'marchand'), 'attente')
                else:
                    self.assertEqual(lire(m, 'marchand')['intention']['plan'][0]['operation'], 'inspecter')
                    passer(m, MINUTE)
                    self.assertGreaterEqual(lire(m, 'marchand')['visites']['antichambre'], minute)
                self.assertEqual(m.data, recharger(m).data)
                self.assertEqual(visible(m), visible(recharger(m)))

    def test_compagnon_deja_a_portee_reste_sans_deplacement(self):
        m, auteur, autre = scene()
        placer(m, auteur, 'antichambre', [4, 5])
        percevoir_tous(m)
        m = recharger(m)
        avant = copy.deepcopy(m.objets[auteur]['position'])
        passer(m, 3 * MINUTE)
        self.assertEqual(m.objets[auteur]['position'], avant)
        self.assertTrue(proche(m, autre, auteur))
        self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
        self.assertEqual(visible(m), visible(recharger(m)))

    def test_ilse_et_mine_rejoint_reste_apaise_et_meme_laps(self):
        for scenario in ('relais', 'mine'):
            with self.subTest(scenario=scenario):
                m, auteur, autre = scene(scenario)
                self.assertTrue(peur(m, auteur))
                avant = copy.deepcopy(m.data)
                with patch.object(p, 'VERIFIER', True):
                    candidats = list(d._candidats(m, auteur))
                    resultat = next(c.methode(m, auteur) for c in candidats
                                    if c.demande and c.demande.get('raison', {}).get('besoin') == 'peur')
                self.assertEqual(m.data, avant)
                self.assertEqual(resultat[1][-1]['operation'], 'rester')
                b = recharger(m)
                passer(m, 4 * MINUTE)
                for dt in (13, 587, 111, 489, 1200):
                    passer(b, dt)
                    b = recharger(b)
                m = recharger(m)
                self.assertEqual(m.data, b.data)
                self.assertEqual(visible(m), visible(b))
                self.assertTrue(proche(m, autre, auteur))
                self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
                self.assertLess(lire(m, autre)['besoins']['securite'], 85)
                self.assertEqual(sum(s['type'] == 'compagnie' and s.get('qui') == autre
                                     for s in lire(m, auteur)['memoire']), 1)
                self.assertIn('reste près', str(m.data['chronique']))
                position = copy.deepcopy(m.objets[auteur]['position'])
                passer(m, MINUTE)
                self.assertEqual(m.objets[auteur]['position'], position)
                self.assertEqual(visible(m), visible(recharger(m)))

    def test_controles_et_fin_explicite_apres_recharge(self):
        for cas in ('sans_souci', 'rancune', 'dos', 'noir', 'apaisee', 'propre_peur', 'propre_faim'):
            with self.subTest(cas=cas):
                m, auteur, autre = scene()
                if cas in ('apaisee', 'propre_peur', 'propre_faim', 'rancune', 'dos', 'noir'):
                    d.choisir(m, auteur, m.data['minutes'])
                    self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
                if cas == 'sans_souci':
                    m.objets[auteur]['profil']['valeurs'].update(altruisme=0, empathie=0)
                elif cas == 'rancune':
                    lire(m, auteur)['relations'][autre] = relations._nouvelle({'rancune': 80, 'affection': 40})
                elif cas == 'dos':
                    regarder(m, auteur, [1, 3])
                elif cas == 'noir':
                    for o in m.objets.values():
                        if 'allume' in o:
                            o['allume'] = False
                elif cas == 'apaisee':
                    lire(m, autre)['besoins']['securite'] = 0.
                elif cas == 'propre_peur':
                    lire(m, auteur)['besoins']['securite'] = 90.
                else:
                    lire(m, auteur)['besoins']['faim'] = 90.
                    m.objets['vivres'].update(lieu=auteur, proprietaire=auteur)
                percevoir_tous(m)
                m = recharger(m)
                position = copy.deepcopy(m.objets[auteur]['position'])
                d.choisir(m, auteur, m.data['minutes'])
                intention = lire(m, auteur)['intention']
                self.assertFalse(intention and intention['motif'] == 'empathie')
                if cas in ('sans_souci', 'rancune', 'apaisee', 'dos', 'noir', 'propre_peur'):
                    self.assertFalse(peur(m, auteur))
                if cas == 'apaisee':
                    contrat = lire(m, auteur)['contrat_intention']['contrat']
                    self.assertEqual(contrat['sortie']['cause'], 'dementie')
                if cas in ('sans_souci', 'rancune'):
                    passer(m, MINUTE)
                    self.assertEqual(m.objets[auteur]['position'], position)
                self.assertEqual(m.data, recharger(m).data)
                self.assertEqual(visible(m), visible(recharger(m)))

    def test_ilse_effrayee_par_le_noir_puis_secourue_et_fin_naturelle(self):
        m, auteur, autre = scene()
        lire(m, auteur)['libre'] = 60000
        placer(m, auteur, 'echoppe', [4, 4])
        m.joueur.update(salle='echoppe', position=[5, 4])
        lire(m, autre)['besoins']['securite'] = d.seuils(m, autre)['securite'] - .1
        allumees = [o for o in m.objets.values() if o.get('allume')]
        for o in allumees:
            o['allume'] = False
        percevoir_tous(m)
        passer(m, 2 * MINUTE)
        self.assertGreater(lire(m, autre)['besoins']['securite'], d.seuils(m, autre)['securite'])
        for o in allumees:
            o['allume'] = True
        placer(m, auteur, 'antichambre', [2, 5])
        m.joueur.update(salle='antichambre', position=[3, 6])
        lire(m, auteur)['libre'] = 0
        regarder(m, auteur, autre)
        percevoir_tous(m)
        m = recharger(m)
        self.assertTrue(peur(m, auteur))
        d.choisir(m, auteur, m.data['minutes'])
        self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
        passer(m, 10 * MINUTE)
        m = recharger(m)
        self.assertLessEqual(lire(m, autre)['besoins']['securite'], d.seuils(m, autre)['securite'])
        self.assertFalse(peur(m, auteur))
        i = lire(m, auteur)['intention']
        self.assertFalse(i and i['motif'] == 'empathie')
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(visible(m), visible(recharger(m)))

    def test_lectures_et_couts_de_proximite_dans_la_memoire_commune(self):
        m, auteur, autre = scene()
        condition = {'pres': autre}
        with patch.object(p, 'VERIFIER', True):
            avant = p._pulsion(m, auteur, condition, False)
            b = recharger(m)
            # Réalité cachée : ni le plan ni son devis ne changent.
            placer(b, autre, 'echoppe', [4, 4])
            lire(b, autre)['besoins']['securite'] = 0.
            self.assertEqual(avant, p._pulsion(b, auteur, condition, False))
            # Localisation effectivement crue : nouvelle clé de recherche.
            from donjon.esprits import croire
            croire(b, auteur, autre, 'lieu', 'echoppe', 'dit:ilse', salle='echoppe', case=[4, 4])
            apres = p._pulsion(b, auteur, condition, False)
            self.assertIsNotNone(apres)
            self.assertNotEqual(avant, apres)
            self.assertTrue(any(e['operation'] == 'aller' and e['lieu'] == 'echoppe' for e in apres[2]))
        self.assertEqual(visible(b), visible(recharger(b)))

    def test_position_et_besoin_prives_hors_vue_ne_changent_pas_le_contact(self):
        m, auteur, autre = scene()
        # Un appel identifié reste le seul indice ; localisation inconnue.
        from donjon.voix import connaitre
        from donjon.ouie import retentir
        connaitre(m, auteur, autre)
        regarder(m, auteur, [1, 3])
        retentir(m, autre, 'appel')
        lire(m, auteur)['croyances'].pop(autre, None)
        m = recharger(m)
        self.assertTrue(peur(m, auteur))
        avant = p.planifier_pulsion(m, auteur, {'pres': autre})
        b = recharger(m)
        placer(b, autre, 'echoppe', [4, 4])
        lire(b, autre)['besoins']['securite'] = 0.
        self.assertEqual(peur(m, auteur), peur(b, auteur))
        self.assertEqual(avant, p.planifier_pulsion(b, auteur, {'pres': autre}))
        self.assertFalse(any(e['operation'] == 'rester' for e in avant[1]))
        self.assertEqual(visible(b), visible(recharger(b)))


if __name__ == '__main__':
    unittest.main()
