"""283 : charge terminée → parole attribuée → croyance, sauvegarde et démenti."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, echanges, social, pnj
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire, poids_source
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from donjon.planification import _etape
from donjon import ecoute
from tests.support import calme, presentes, regarder as orienter
from tests.test_avis_menace import relation
from tests.test_social import placer
from tests.test_tensions import recharger


class CompteRenduTests(unittest.TestCase):
    def recharge(self, m):
        avant, texte, scene = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual(regarder(n), texte)
        self.assertEqual(scene_percue(n), scene)
        self.assertEqual(ecoute.rendre(m, ecoute.entendus(m, -1, ecoute.ENTENDU)),
                         ecoute.rendre(n, ecoute.entendus(n, -1, ecoute.ENTENDU)))
        return n

    def scene(self, sorte='amener', mandant='marchand', titulaire='aubin'):
        m = presentes(creer('crue_hameau', 1985, 'fixe'))
        ids = [q for q, o in m.objets.items() if o.get('profil')]
        calme(m, *ids)
        for q in ids:
            m.objets[q]['profil']['valeurs']['honnetete'] = 100
            lire(m, q)['libre'] = 1000000
        for q, pos in [(mandant, [2, 4]), (titulaire, [3, 4]), ('brune', [2, 5])]:
            placer(m, q, 'antichambre', pos)
        m.joueur.update(salle='antichambre', position=[2, 3], orientation='sud')
        m.data['connus'] = sorted(m.objets)
        m.data['visitees'] = sorted(m.data['salles'])
        m.data['voix_connues'] = ids
        orienter(m, mandant, titulaire)
        orienter(m, titulaire, mandant)
        for a, b in [(mandant, titulaire), (titulaire, mandant)]:
            croire(m, a, b, 'lieu', 'antichambre', 'vu', salle='antichambre', case=m.objets[b]['position'])
            relation(m, a, b, confiance=100, affection=100)
        p = {'qui': ['brune'], 'lieu': 'chambre_cloche'} if sorte == 'amener' else {
            'qui': ['brune'], 'fait': {'type': 'affirmation', 'sujet': 'brasero',
                                     'attribut': 'lieu', 'valeur': 'antichambre'}}
        m.objets[mandant]['profil']['agendas'] = [{'id': 'charge', 'sorte': sorte, 'parametres': p}]
        agendas.actualiser(m, mandant)
        enfant = agendas.confier(m, mandant, 'charge', titulaire, sorte, p, accepte=True)
        # Le mandant n'a pas constaté l'issue de la charge.
        lire(m, mandant)['croyances'].pop('brune', None)
        return self.recharge(m), enfant['id']

    def agenda(self, m, q, id):
        return next(a for a in lire(m, q)['agendas'] if a['id'] == id)

    def terminer(self, m, id, sorte, issue, titulaire='aubin'):
        a = self.agenda(m, titulaire, id)
        if issue == 'reussi':
            if sorte == 'amener':
                placer(m, 'brune', 'chambre_cloche', [1, 3])
                croire(m, titulaire, 'brune', 'lieu', 'chambre_cloche', 'vu',
                       salle='chambre_cloche', case=[1, 3])
            else:
                # Exécution réelle de l'information ; le mandant n'est pas à portée.
                mandant = a['origine']['de']
                placer(m, mandant, 'beffroi', [1, 3])
                orienter(m, titulaire, 'brune')
                croire(m, titulaire, 'brasero', 'lieu', 'antichambre', 'savoir', salle='antichambre', case=None)
                with patch.object(Monde, 'd20', return_value=20):
                    self.assertTrue(echanges.executer(m, titulaire,
                        _etape('dire', 'brune', contenu=a['parametres']['fait']), []))
                placer(m, mandant, 'antichambre', [2, 4])
                orienter(m, titulaire, mandant)
                orienter(m, mandant, titulaire)
                lire(m, mandant)['croyances'].pop('brune', None)
            agendas.actualiser(m, titulaire)
            self.assertEqual(a['etat'], 'atteint')
        elif issue == 'echoue':
            a['echeance'] = m.data['minutes']
            m.data['minutes'] += 1
            agendas.actualiser(m, titulaire)
            self.assertEqual(a['etat'], 'abandonne')
        else:
            # Trois autres charges plus fortes ont supplanté celle-ci.
            a.update(etat='abandonne', raison='supplante')

    def annoncer(self, m, titulaire='aubin'):
        lignes = []
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(social.bavarder(m, titulaire, lignes))
        self.assertTrue(any('rend compte' in x['texte'] for x in m.data['chronique']))
        self.assertIn('rend compte', str(lignes) + str(ecoute.rendre(m, ecoute.entendus(m, -1, ecoute.ENTENDU))))
        return self.recharge(m)

    def test_deux_charges_trois_issues_et_aucune_fin_a_distance(self):
        for sorte in ('amener', 'informer'):
            for issue in agendas.ISSUES_COMPTE_RENDU:
                with self.subTest(sorte=sorte, issue=issue):
                    m, id = self.scene(sorte)
                    self.terminer(m, id, sorte, issue)
                    agendas.actualiser(m, 'marchand')
                    self.assertEqual(self.agenda(m, 'marchand', 'charge')['etat'], 'actif')
                    m = self.annoncer(self.recharge(m))
                    parent = self.agenda(m, 'marchand', 'charge')
                    r = parent['comptes_recus'][0]
                    self.assertEqual(r['contenu']['issue'], issue)
                    self.assertEqual(r['croyance']['source'], 'dit:aubin')
                    self.assertEqual(r['croyance']['poids'], poids_source(m, 'marchand', r['croyance']))
                    agendas.actualiser(m, 'marchand')
                    self.assertEqual(parent['etat'], 'atteint' if issue == 'reussi' else 'actif')
                    self.assertIsNone(agendas.compte_a_rendre(self.recharge(m), 'aubin'))

    def test_mensonge_sans_effet_sur_le_monde_et_dementi_posterieur(self):
        for sorte in ('amener', 'informer'):
            m, id = self.scene(sorte)
            self.terminer(m, id, sorte, 'echoue')
            m.objets['aubin']['profil']['valeurs']['honnetete'] = 0
            objets = copy.deepcopy(m.objets)
            transmis = social.transmission_attestee(m, 'aubin', 'brune',
                {'type': 'affirmation', 'sujet': 'brasero', 'attribut': 'lieu', 'valeur': 'antichambre'})
            m = self.annoncer(self.recharge(m))
            self.assertEqual(m.objets, objets)
            r = self.agenda(m, 'marchand', 'charge')['comptes_recus'][0]
            self.assertEqual(r['contenu']['issue'], 'reussi')
            self.assertEqual(r['croyance']['source'], 'dit:aubin')
            agendas.actualiser(m, 'marchand')
            self.assertEqual(self.agenda(m, 'marchand', 'charge')['etat'], 'atteint')
            if sorte == 'amener':
                croire(m, 'marchand', 'brune', 'lieu', 'antichambre', 'vu', salle='antichambre', case=[2, 5])
                agendas.actualiser(m, 'marchand')
                self.assertEqual(r['croyance']['source'], 'vu')
                self.assertEqual(r['croyance']['valeur'], 'echoue')
                self.assertNotEqual(self.agenda(m, 'marchand', 'charge')['etat'], 'atteint')
                self.assertTrue(any(s['type'] == 'mensonge_decouvert' for s in lire(m, 'marchand')['memoire']))
            else:
                self.assertEqual(social.transmission_attestee(m, 'aubin', 'brune',
                    {'type': 'affirmation', 'sujet': 'brasero', 'attribut': 'lieu', 'valeur': 'antichambre'}), transmis)
            self.recharge(m)

    def test_constat_anterieur_ou_posterieur_des_deux_charges(self):
        for sorte in ('amener', 'informer'):
            for avant in (True, False):
                m, id = self.scene(sorte)
                self.terminer(m, id, sorte, 'echoue')
                contenu = agendas.compte_a_rendre(m, 'aubin')
                # Une fausse annonce d'échec est démentie par la réussite constatée.
                def constater():
                    if sorte == 'amener':
                        croire(m, 'marchand', 'brune', 'lieu', 'chambre_cloche', 'vu', salle='chambre_cloche', case=None)
                    else:
                        social.retenir_dit(m, 'marchand', 'brune', contenu['charge']['parametres']['fait'])
                if avant:
                    constater()
                with patch.object(Monde, 'd20', return_value=20):
                    self.assertTrue(echanges.rendre_compte(m, 'aubin', contenu, []))
                m = self.recharge(m)
                if not avant:
                    constater()
                agendas.actualiser(m, 'marchand')
                c = self.agenda(m, 'marchand', 'charge')['comptes_recus'][0]['croyance']
                self.assertEqual((c['valeur'], c['source']), ('reussi', 'entendu' if sorte == 'informer' else 'vu'))
                self.recharge(m)

    def test_hors_portee_puis_reception_apres_recharge(self):
        for sorte in ('amener', 'informer'):
            m, id = self.scene(sorte)
            self.terminer(m, id, sorte, 'echoue')
            contenu = agendas.compte_a_rendre(m, 'aubin')
            placer(m, 'marchand', 'beffroi', [1, 3])
            avant = copy.deepcopy(lire(m, 'marchand'))
            self.assertFalse(echanges.rendre_compte(m, 'aubin', contenu, []))
            self.assertEqual(lire(m, 'marchand'), avant)
            self.assertNotIn('compte_rendu', self.agenda(m, 'aubin', id))
            m = self.recharge(m)
            placer(m, 'marchand', 'antichambre', [2, 4])
            orienter(m, 'marchand', 'aubin')
            self.annoncer(m)

    def test_doute_attribution_et_idempotence(self):
        for sorte in ('amener', 'informer'):
            m, id = self.scene(sorte)
            self.terminer(m, id, sorte, 'echoue')
            m.objets['aubin']['profil']['valeurs']['honnetete'] = 0
            contenu = agendas.compte_a_rendre(m, 'aubin')
            # Une voix non attribuée établit la parole, pas un résultat du titulaire.
            with patch('donjon.voix.identifie', return_value=False):
                self.assertIsNone(social.recevoir(m, 'marchand', 'aubin', contenu))
            self.assertNotIn('comptes_recus', self.agenda(m, 'marchand', 'charge'))
            self.assertTrue(any(s['type'] == 'compte_rendu' and s['de'] == 'dit:voix:aubin'
                                for s in lire(m, 'marchand')['memoire']))
            # Le jugement commun peut refuser le même contenu même attribué.
            with patch('donjon.echanges.jet_persuasion', return_value=(False, 0, 0)):
                self.assertEqual(social.recevoir(m, 'marchand', 'aubin', contenu), 'doute')
            agendas.actualiser(m, 'marchand')
            self.assertEqual(self.agenda(m, 'marchand', 'charge')['etat'], 'actif')
            m = self.annoncer(self.recharge(m))
            avant = copy.deepcopy(m.data)
            self.assertFalse(echanges.rendre_compte(m, 'aubin', contenu, []))
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_marche_reelle_avant_compte_de_reussite(self):
        m, id = self.scene()
        relation(m, 'brune', 'aubin', confiance=100, affection=100)
        croire(m, 'aubin', 'brune', 'lieu', 'antichambre', 'vu', salle='antichambre', case=[2, 5])
        orienter(m, 'aubin', 'brune')
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(echanges.executer(m, 'aubin', _etape('confier', 'brune',
                contenu={'objet': 'brune', 'lieu': 'chambre_cloche'}), []))
        self.assertEqual(m.objets['brune']['lieu'], 'antichambre')
        lire(m, 'brune')['libre'] = 0
        with patch.object(Monde, 'd20', return_value=20):
            pnj.avancer(m, ecouler(m, 1800), [], 1800)
        self.assertEqual(m.objets['brune']['lieu'], 'chambre_cloche')
        # Aubin constate ensuite l'arrivée ; Gorm ne la constate pas.
        croire(m, 'aubin', 'brune', 'lieu', 'chambre_cloche', 'vu', salle='chambre_cloche', case=m.objets['brune']['position'])
        agendas.actualiser(m, 'aubin')
        self.assertEqual(self.agenda(m, 'aubin', id)['etat'], 'atteint')
        m = self.annoncer(self.recharge(m))
        agendas.actualiser(m, 'marchand')
        self.assertEqual(self.agenda(m, 'marchand', 'charge')['etat'], 'atteint')
        self.recharge(m)

    def test_autre_mandant_et_laps_entier_decoupe(self):
        for sorte in ('amener', 'informer'):
            m, id = self.scene(sorte, 'ilse', 'marchand')
            self.terminer(m, id, sorte, 'echoue', 'marchand')
            lire(m, 'marchand')['libre'] = 0
            lire(m, 'marchand')['intention'] = None
            a, b = self.recharge(m), self.recharge(m)
            with patch.object(Monde, 'd20', return_value=20):
                pnj.avancer(a, ecouler(a, 600), [], 600)
                for _ in range(2):
                    pnj.avancer(b, ecouler(b, 300), [], 300)
            self.assertEqual(a.data, b.data)
            self.assertTrue(self.agenda(a, 'ilse', 'charge').get('comptes_recus'))
            self.recharge(a)


if __name__ == '__main__':
    unittest.main()
