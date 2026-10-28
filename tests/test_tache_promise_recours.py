"""Une contrepartie future passe par le même marché et le même agenda."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, relations
from donjon.deliberation import retenir_refus
from donjon.echanges import ENGAGEMENT_MAX, annoncer_abandon
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import recours, executer
from donjon.spatial import installer, porte_par
from tests.support import calme, presentes, regarder
from tests.test_proposer_recours import scene
from tests.test_tensions import placer, recharger


def feu():
    m = scene(70)
    m.data['finances_pnj']['brune'] = 0
    m.objets['crochets'].update(lieu='joueur', proprietaire='joueur')
    placer(m, 'brune', 'echoppe', [3, 3])
    placer(m, 'marchand', 'echoppe', [4, 3])
    m.joueur.update(salle='echoppe', position=[4, 4])
    regarder(m, 'joueur', 'brune')
    m.objets['vivres'].update(lieu='marchand', portions=8)
    m.objets['brasero'].update(allume=True, combustible=20)
    regarder(m, 'marchand', 'brasero')
    m.objets['bois'].update(lieu='brune', proprietaire='brune')
    m.objets['marchand']['profil']['pulsions'] = [
        {'besoin': 'devoir', 'condition': {'objet': 'brasero', 'allume': True}}]
    lire(m, 'marchand')['pulsions'] = []
    percevoir_tous(m)
    for qui in ('brune', 'marchand'):
        croire(m, qui, 'brasero', 'etat', {'allume': True, 'faible': True, 'charge': False}, 'vu')
    return recharger(m), 'brune', 'marchand', {'objet': 'brasero', 'allume': True}


def reserve():
    from tests.scenarios_contractuels import nouveau_auberge
    m = presentes(nouveau_auberge(depart='fixe'))
    installer(m)
    calme(m, *[i for i, o in m.objets.items() if o.get('profil')])
    m.joueur.update(salle='cellier', position=[3, 3])
    placer(m, 'joss', 'cellier', [3, 2])
    placer(m, 'odile', 'cellier', [4, 2])
    regarder(m, 'joss', 'odile'); regarder(m, 'odile', 'joss')
    regarder(m, 'joueur', 'joss')
    m.data['finances_pnj']['joss'] = 0
    m.objets['vivres'].update(lieu='odile', portions=8)
    m.objets['garde_manger'].update(ouverte=True, verrouillee=False)
    m.objets['lanterne_couloir'].update(lieu='cellier', position=[3, 3],
                                      position_salle='cellier', allume=True, combustible=120)
    m.objets['cle_garde_manger'].update(lieu='joss')
    c = {'objet': 'garde_manger', 'verrouillee': True}
    m.objets['odile']['profil']['pulsions'] = [{'besoin': 'biens', 'condition': c}]
    lire(m, 'odile')['pulsions'] = []
    lire(m, 'odile')['relations']['joss'] = relations._nouvelle({'confiance': 80})
    lire(m, 'joss')['relations']['odile'] = relations._nouvelle({'confiance': 80})
    m.data['connus'].extend(['vivres', 'garde_manger'])
    lire(m, 'joss')['besoins']['faim'] = 95
    lire(m, 'joss')['intention'] = {'but': {'type': 'manger', 'objet': 'vivres'},
                                  'motif': 'faim', 'plan': [], 'depuis': 0, 'attente': 0}
    percevoir_tous(m)
    croire(m, 'joss', 'garde_manger', 'verrouillee', False, 'essai')
    retenir_refus(m, 'joss', 'odile', 'demander', 'refus', objet='vivres')
    return recharger(m), 'joss', 'odile', c


def offrir(fabrique):
    m, id, autre, c = fabrique()
    g = recours(m, id, 'faim', [])
    assert g and g['contenu']['contrepartie'] == {'type': 'tache', 'condition': c}, g
    lignes = []
    with patch.object(Monde, 'd20', return_value=20):
        assert executer(m, id, autre, g['contenu'], lignes)
    return recharger(m), id, autre, c, lignes


class TachePromiseTests(unittest.TestCase):
    def test_charge_inaccessible_equivaut_au_devis_reel_deux_sources_rechargees(self):
        from donjon.echanges import _devis_proposition, devis_service
        from donjon.rendu import regarder as rendu
        with gzip.open(Path(__file__).parent / 'data/devis-crue2024-17.json.gz',
                       'rt', encoding='utf8') as f:
            capture = json.load(f)
        reel = (Monde(capture['data']), capture['id'], capture['pour'], capture['condition'])
        m, id, autre, _ = reserve()
        source = 'bougeoir_mireille'
        m.objets[source].update(lieu=id, proprietaire=autre, allume=False, combustible=60)
        m.data['connus'].append(source)
        croire(m, id, source, 'lieu', id, 'vu', salle=None, case=None)
        m.data['minutes'] = 1
        second = (m, id, autre, {'objet': source, 'allume': True})
        for monde, id, autre, c in (reel, second):
            for charge, ancien in ((False, False), (True, True), (True, False)):
                with self.subTest(source=c['objet'], charge=charge, ancien=ancien):
                    m = recharger(monde.copier())
                    croire(m, id, c['objet'], 'etat',
                           {'allume': False, 'charge': charge, 'faible': False}, 'vu',
                           minute=m.data['minutes'] - int(ancien))
                    avant, visible = copy.deepcopy(m.data), rendu(m)
                    with patch('donjon.echanges._charge_irrealisable', return_value=False):
                        attendu = _devis_proposition(m, id, c, autre)
                    with patch('donjon.echanges.devis_service', wraps=devis_service) as devis:
                        obtenu = _devis_proposition(m, id, c, autre)
                    self.assertEqual(obtenu, attendu)
                    self.assertEqual(devis.call_count, int(charge and not ancien))
                    self.assertEqual(m.data, avant)
                    reprise = recharger(m)
                    self.assertEqual(reprise.data, avant)
                    self.assertEqual(rendu(reprise), visible)

    def test_un_refus_ancien_ne_supplante_pas_un_plan_ordinaire(self):
        for fabrique in (feu, reserve):
            m, id, autre, c = fabrique()
            self.assertIsNotNone(recours(m, id, 'faim', []))
            for operation in ('demander', 'acheter', 'manger'):
                g = {'operation': operation, 'cible': autre, 'outil': 'vivres',
                     'lieu': '', 'condition': ''}
                self.assertIsNone(recours(recharger(m), id, 'faim', [g]))
                if operation != 'manger':
                    faute = {**g, 'operation': 'prendre', 'cible': 'vivres', 'condition': 'sans_temoin'}
                    self.assertIsNone(recours(recharger(m), id, 'faim', [g, faute]))

    def test_offre_visible_dans_le_journal_moteur_recharge(self):
        for fabrique in (feu, reserve):
            m, id, autre, c = fabrique()
            # Les autres repas ne sont pas un moyen ordinaire dans cette scène.
            for o, x in m.objets.items():
                if x['type'] == 'nourriture' and o != 'vivres':
                    x['portions'] = 0
            percevoir_tous(m)
            # Plan de recours sauvegardé : publication par le moteur réel.
            g = recours(m, id, 'faim', [])
            self.assertIsNotNone(g)
            lire(m, id)['intention']['plan'] = [g]
            m = recharger(m)
            with patch.object(Monde, 'd20', return_value=20):
                Moteur(m).executer(Moteur(m).preparer(proposition('attendre')))
            m = recharger(m)
            journal = ' '.join(f for tour in m.data['journal'] for f in tour['faits'])
            self.assertIn('la promesse que', journal)
            self.assertIn("accepte l'échange", journal)
            self.assertTrue(any(s['type'] == 'engagement_tenu' for s in lire(m, id)['memoire']))

    def test_un_devis_et_aucune_lecture_du_but_prive(self):
        from donjon.echanges import devis_service
        m, id, autre, c = feu()
        with patch('donjon.echanges.devis_service', wraps=devis_service) as devis:
            g = recours(m, id, 'faim', [])
        self.assertEqual(devis.call_count, 1)
        m.objets[autre]['profil']['pulsions'] = []
        lire(m, autre)['pulsions'] = []
        self.assertEqual(recours(m, id, 'faim', []), g)

    def test_le_refus_reutilise_le_devis_du_candidat(self):
        from donjon.echanges import devis_service
        from donjon.pnj_propositions import entrees_refus
        m, id, autre, c = feu()
        terme = {'type': 'tache', 'condition': c}
        retenir_refus(m, id, autre, 'proposer', 'garde', objet='vivres',
                      offre=entrees_refus(m, id, autre, 'vivres', terme))
        with patch('donjon.echanges.devis_service', wraps=devis_service) as devis:
            recours(m, id, 'faim', [])
        self.assertEqual(devis.call_count, 1)

    def test_aucune_fourniture_future_d_un_tiers(self):
        m, id, autre, c = feu()
        m.objets['bois'].update(lieu=autre, proprietaire=autre)
        percevoir_tous(m)
        self.assertIsNone(recours(recharger(m), id, 'faim', []))

    def test_deux_services_remis_tenus_et_recharges_meme_laps(self):
        from donjon.commandes import analyser
        from donjon.temps import instant
        for fabrique in (feu, reserve):
            with self.subTest(scene=fabrique.__name__):
                a, id, autre, c, lignes = offrir(fabrique)
                self.assertEqual(agendas.en_cours(a, id)[0]['condition'], c)
                self.assertTrue(any(porte_par(a, o, id) for o in a.objets if o.startswith('vivres_')))
                self.assertIn('accepte', ' '.join(lignes))
                b = recharger(a.copier())
                with patch.object(Monde, 'd20', return_value=20):
                    Moteur(a).executer(Moteur(a).preparer(proposition('attendre')))
                    n = 0
                    while instant(b) < instant(a):
                        moteur = Moteur(b)
                        action = moteur.preparer(analyser(b, 'tourner est' if n % 2 else 'tourner ouest'))
                        reste = instant(a) - instant(b)
                        if action.dixiemes > reste:
                            from donjon.pnj import avancer
                            from donjon.temps import ecouler
                            avancer(b, ecouler(b, reste), [], reste)
                        else:
                            moteur.executer(action)
                        b = recharger(b)
                        n += 1
                a, b = recharger(a), recharger(b)
                for m in (a, b):
                    self.assertFalse(agendas.en_cours(m, id, condition=c, actifs=True))
                    self.assertTrue(any(s['type'] == 'engagement_tenu' for s in lire(m, id)['memoire']))
                    # Tenir la tâche n'impose pas une confidence dans les
                    # cinq minutes. Une conversation réelle transmet la suite.
                    from donjon.social import faire_entendre
                    from donjon.pnj import peuvent_se_parler
                    self.assertTrue(peuvent_se_parler(m, id, autre))
                    faire_entendre(m, id, autre, 'Le service est terminé.', [c['objet']], [])
                    recharge = recharger(m)
                    self.assertEqual(m.data, recharge.data)
                    from donjon.rendu import regarder as rendu
                    self.assertEqual(rendu(m), rendu(recharge))
                    self.assertTrue(any(s['type'] == 'engagement_tenu' and s.get('de') == id
                                        for s in lire(m, autre)['memoire']))
                    if 'allume' in c:
                        self.assertGreater(m.objets[c['objet']]['combustible'], 20)
                        vu = lire(m, autre)['croyances'][c['objet']]['etat']
                        self.assertEqual(vu['source'], 'vu')
                        self.assertTrue(vu['valeur']['allume'])
                        self.assertGreater(vu['minute'], 0)
                    else:
                        self.assertTrue(m.objets[c['objet']]['verrouillee'])
                    self.assertTrue(any('promesse' in x['texte'] or 'parole' in x['texte']
                                        for x in m.data['chronique']))
                self.assertEqual(a.data['chronique'], b.data['chronique'])
                self.assertEqual(a.data['esprits'][id], b.data['esprits'][id])

    def test_promesse_rompue_annoncee_sans_second_marche(self):
        for fabrique in (feu, reserve):
            m, id, autre, c, _ = offrir(fabrique)
            confiance = relations.axes(m, autre, id)['confiance']
            m.data['minutes'] += ENGAGEMENT_MAX + 1
            agendas.echoir(m, id)
            lignes = []
            self.assertTrue(annoncer_abandon(m, id, autre, c, lignes))
            m = recharger(m)
            self.assertFalse(agendas.en_cours(m, id, condition=c))
            self.assertTrue(any(s['type'] == 'engagement_abandonne' for s in lire(m, id)['memoire']))
            self.assertLess(relations.axes(m, autre, id)['confiance'], confiance)
            self.assertIn('promesse', ' '.join(lignes))
            self.assertIsNone(recours(m, id, 'faim', []))

    def test_impossible_et_plan_recharge_revalides_sans_parole(self):
        m, id, autre, c = feu()
        g = recours(m, id, 'faim', [])
        m.objets['bois']['charges'] = 0
        percevoir_tous(m)
        m = recharger(m)
        lignes = []
        self.assertFalse(executer(m, id, autre, g['contenu'], lignes))
        self.assertEqual(lignes, [])
        self.assertFalse(agendas.en_cours(m, id))
        from donjon.echanges import devis_service
        faute = {'operation': 'prendre', 'cible': 'vivres', 'outil': '',
                 'lieu': '', 'condition': 'sans_temoin'}
        with patch('donjon.echanges.devis_service', wraps=devis_service) as devis:
            self.assertIsNone(recours(m, id, 'faim', [faute]))
        self.assertEqual(devis.call_count, 1)

    def test_refus_de_tache_persiste_apres_recharge(self):
        m, id, autre, c = feu()
        g = recours(m, id, 'faim', [])
        with patch.object(Monde, 'd20', return_value=1):
            self.assertTrue(executer(m, id, autre, g['contenu'], []))
        m = recharger(m)
        self.assertFalse(agendas.en_cours(m, id))
        m.data['minutes'] += 60
        self.assertIsNone(recours(m, id, 'faim', []))
        lignes = []
        self.assertFalse(executer(m, id, autre, g['contenu'], lignes))
        self.assertEqual(lignes, [])
        self.assertFalse(agendas.en_cours(recharger(m), id))


if __name__ == '__main__':
    unittest.main()
