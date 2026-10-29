"""297 : attribution, parole de retrait et reprise sur croyances, dans deux mondes."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, echanges, ecoute, pnj
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire
from donjon.monde import Monde, ErreurMonde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.support import calme, presentes, regarder as orienter
from tests.test_avis_menace import relation
from tests.test_social import placer
from tests.test_tensions import recharger


class ReaffecterTests(unittest.TestCase):
    def recharge(self, m):
        data = copy.deepcopy(m.data)
        public = (regarder(m), scene_percue(m), ecoute.rendre(m, ecoute.entendus(m, -1, ecoute.ENTENDU)))
        n = recharger(m)
        self.assertEqual(n.data, data)
        self.assertEqual(public, (regarder(n), scene_percue(n), ecoute.rendre(n, ecoute.entendus(n, -1, ecoute.ENTENDU))))
        return n

    def scene(self, scenario='crue_hameau', sorte='amener'):
        m = presentes(creer(scenario, 1985, 'fixe'))
        ids = [q for q, o in m.objets.items() if o.get('profil')]
        calme(m, *ids)
        if scenario == 'mine':
            mandant, ancien, nouveau, cible = 'bram', 'josse', 'mathe', 'lucien'
            ici, la, cle, objet = 'baraquement', 'reserve', 'passe', 'paie'
        else:
            mandant, ancien, nouveau, cible = 'marchand', 'aubin', 'ilse', 'brune'
            ici, la, cle, objet = 'crypte', 'beffroi', 'cle', 'brasero'
        for q in ids:
            m.objets[q]['profil']['valeurs'].update(honnetete=100, douceur=100)
            lire(m, q)['libre'] = 1000000
        for q, pos in [(mandant, [1, 1]), (ancien, [2, 1]), (nouveau, [1, 2])]:
            placer(m, q, ici, pos)
        placer(m, cible, la, [1, 3])
        m.joueur.update(salle=ici, position=[2, 2], orientation='nord')
        m.data['connus'] = sorted(m.objets)
        m.data['visitees'] = sorted(m.data['salles'])
        m.data['voix_connues'] = ids
        m.objets[cle]['lieu'] = nouveau
        m.objets[cle]['proprietaire'] = nouveau
        for q in (mandant, ancien, nouveau):
            for autre in (mandant, ancien, nouveau, cible):
                salle = la if autre == cible else ici
                croire(m, q, autre, 'lieu', salle, 'savoir', salle=salle, case=None)
            croire(m, q, cle, 'lieu', nouveau, 'savoir', salle=ici, case=None)
            croire(m, q, objet, 'lieu', m.objets[objet]['lieu'], 'savoir', salle=ici, case=None)
            for autre in (mandant, ancien, nouveau):
                if autre != q:
                    relation(m, q, autre, confiance=100, affection=100)
        for q in list(lire(m, mandant)['croyances']):
            if q not in (mandant, ancien, nouveau, cible) and m.objets.get(q, {}).get('profil'):
                lire(m, mandant)['croyances'].pop(q)
        orienter(m, mandant, ancien)
        orienter(m, ancien, mandant)
        p = {'qui': [cible], 'lieu': ici} if sorte == 'amener' else {
            'qui': [cible], 'fait': {'type': 'affirmation', 'sujet': objet,
                                    'attribut': 'lieu', 'valeur': m.objets[objet]['lieu']}}
        m.objets[mandant]['profil']['agendas'] = [{'id': 'charge', 'sorte': sorte, 'parametres': p}]
        agendas.actualiser(m, mandant)
        # Date convenue explicite dans cette scène ; le moteur n'en déduit
        # aucune de l'incertain consentement de la personne à ramener.
        enfant = agendas.confier(m, mandant, 'charge', ancien, sorte, p,
                                 accepte=True, echeance=m.data['minutes'] + 1)
        m.data['minutes'] += 2
        return self.recharge(m), (mandant, ancien, nouveau, cible, enfant['id'])

    def parent(self, m, qui):
        return next(a for a in agendas.projets(m, qui) if a['id'] == 'charge')

    def plan(self, m, qui):
        avant = copy.deepcopy(m.data)
        r = agendas.planifier(m, qui, 'charge')
        self.assertEqual(m.data, avant)
        return r

    def executer(self, m, qui, plan):
        with patch.object(Monde, 'd20', return_value=20):
            for g in plan:
                self.assertIn(g['operation'], ('dire', 'confier'))
                self.assertTrue(echanges.executer(m, qui, g, []))

    def test_remplacement_reel_avertissement_attribution_et_laps(self):
        for scenario in ('crue_hameau', 'mine'):
            with self.subTest(scenario=scenario):
                m, (a, b, c, cible, enfant) = self.scene(scenario)
                r = self.plan(m, a)
                self.assertEqual(r[1][0]['contenu']['retrait_mandat']['agenda'], enfant)
                self.assertEqual(r[1][-1]['cible'], c)
                self.executer(m, a, r[1])
                m = self.recharge(m)
                stock = self.parent(m, a)['attributions']
                self.assertEqual([x['titulaire'] for x in stock if x['etat'] == 'active'], [c])
                self.assertTrue(stock[0]['avertissement']['entendu'])
                self.assertEqual(agendas.projets(m, b)[-1]['raison'], 'retrait entendu')
                self.assertIn('reprend la charge', str(m.data['chronique']))
                # Ni reconfier à l'ancien ni créer une seconde attribution avant échéance.
                p = self.parent(m, a)['parametres']
                with self.assertRaises(ErreurMonde) as refus:
                    agendas.confier(m, a, 'charge', b, 'amener', p, accepte=True)
                self.assertTrue(refus.exception.attendu)
                for _ in range(3):
                    self.assertEqual(self.plan(m, a)[1], [])
                for q in (a, b, c, cible):
                    lire(m, q)['libre'] = m.data['minutes'] * 600
                avant_laps = len(m.data['chronique'])
                x, y = m.copier(), m.copier()
                pnj.avancer(x, ecouler(x, 1200), [], 1200)
                for _ in range(2):
                    pnj.avancer(y, ecouler(y, 600), [], 600)
                self.assertEqual(x.data, y.data)
                self.assertGreater(len(x.data['chronique']), avant_laps)
                self.recharge(x)

    def test_absence_cachee_sans_annulation_a_distance(self):
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario)
            attendu = self.plan(m, a)
            autre = 'entree' if scenario == 'mine' else 'chambre_cloche'
            placer(m, b, autre, [1, 1])
            lire(m, b)['croyances'].clear()
            self.assertEqual(self.plan(self.recharge(m), a), attendu)
            self.executer(m, a, attendu[1])
            m = self.recharge(m)
            self.assertEqual(agendas.projets(m, b)[-1]['etat'], 'actif')
            stock = self.parent(m, a)['attributions']
            self.assertFalse(stock[0]['avertissement']['entendu'])
            self.assertEqual([x['titulaire'] for x in stock if x['etat'] == 'active'], [c])
            self.assertEqual(self.plan(m, a)[1], [])
            ici = m.objets[a]['lieu']
            placer(m, b, ici, [2, 1])
            croire(m, a, b, 'lieu', ici, 'vu', salle=ici, case=[2, 1])
            self.executer(m, a, self.plan(m, a)[1])
            self.assertEqual(agendas.projets(m, b)[-1]['raison'], 'retrait entendu')
            self.recharge(m)

    def test_resultat_appris_arrete_le_plan_en_route(self):
        for scenario in ('crue_hameau', 'mine'):
            for compte in (False, True):
                m, (a, b, c, cible, enfant) = self.scene(scenario)
                deliberation.choisir(m, a, m.data['minutes'])
                self.assertTrue(lire(m, a)['intention']['plan'])
                if compte:
                    charge = lire(m, b)['agendas'][-1]
                    charge.update(etat='atteint', raison='arrivee crue')
                    contenu = agendas.compte_a_rendre(m, b)
                    # Le mandant ignore la position réelle de la cible : une
                    # ancienne observation ne dément pas le rapport de réussite.
                    lire(m, a)['croyances'].pop(cible, None)
                    with patch.object(Monde, 'd20', return_value=20):
                        self.assertTrue(echanges.rendre_compte(m, b, contenu, []))
                else:
                    ici = m.objets[a]['lieu']
                    croire(m, a, cible, 'lieu', ici, 'vu', salle=ici, case=None)
                m = self.recharge(m)
                deliberation.choisir(m, a, m.data['minutes'])
                self.assertEqual(self.parent(m, a)['etat'], 'atteint')
                i = lire(m, a)['intention']
                self.assertFalse(i and any('mandat' in g.get('contenu', {}) or 'retrait_mandat' in g.get('contenu', {}) for g in i['plan']))
                self.assertEqual(len(agendas.enfants(m, a, 'charge')), 1)
                self.recharge(m)

    def test_refus_retenu_et_pas_de_navette_apres_second_retard(self):
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario)
            r = self.plan(m, a)
            mandat = r[1][-1]['contenu']['mandat']
            relation(m, c, a, confiance=0, rancune=100)
            self.executer(m, a, r[1][:-1])
            self.assertFalse(echanges.executer(m, a, r[1][-1], []))
            self.assertTrue(lire(m, a)['refus'])
            self.assertEqual(self.parent(m, a)['attributions'][0]['etat'], 'reprise')
            for _ in range(3):
                r = self.plan(self.recharge(m), a)
                self.assertFalse(r and any('mandat' in g.get('contenu', {}) for g in r[1]))
            deliberation.oublier_refus(m, a, c, 'confier', cible, mandat=mandat)
            p = self.parent(m, a)['parametres']
            agendas.confier(m, a, 'charge', c, 'amener', p, accepte=True, echeance=m.data['minutes'])
            m.data['minutes'] += 1
            for _ in range(3):
                r = self.plan(self.recharge(m), a)
                self.assertFalse(r and any('mandat' in g.get('contenu', {}) for g in r[1]))

    def test_echeance_inconnue_et_validation_du_registre(self):
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario)
            p = self.parent(m, a)['parametres']
            self.assertIsNone(agendas.echeance_observee(m, a, 'charge', b, 'amener', p))
            stock = lire(m, a)['agendas'][0]['attributions']
            stock[0].pop('echeance')
            self.assertEqual(self.plan(self.recharge(m), a)[1], [])
            stock[0]['echeance'] = 1
            agendas.confier(m, a, 'charge', c, 'amener', p, accepte=True)
            stock[0]['etat'] = 'active'
            with self.assertRaisesRegex(AssertionError, 'Plusieurs titulaires actifs'):
                agendas.verifier(m, a)

    def test_avertissement_differe_jusqu_aux_retrouvailles(self):
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario)
            loin = 'entree' if scenario == 'mine' else 'chambre_cloche'
            placer(m, b, loin, [1, 1])
            croire(m, a, b, 'lieu', loin, 'savoir', salle=loin, case=None)
            r = self.plan(m, a)
            self.assertFalse(any('retrait_mandat' in g.get('contenu', {}) for g in r[1]))
            self.executer(m, a, r[1])
            self.assertEqual(agendas.projets(m, b)[-1]['etat'], 'actif')
            m = self.recharge(m)
            ici = m.objets[a]['lieu']
            placer(m, b, ici, [2, 1])
            croire(m, a, b, 'lieu', ici, 'vu', salle=ici, case=[2, 1])
            r = self.plan(m, a)
            self.assertEqual(len(r[1]), 1)
            self.executer(m, a, r[1])
            self.assertEqual(agendas.projets(m, b)[-1]['raison'], 'retrait entendu')
            self.assertEqual(self.plan(self.recharge(m), a)[1], [])

    def test_tenacite_vol_sur_le_moyen_deja_entrepris(self):
        from donjon import relations
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario)
            r = self.plan(m, a)
            lire(m, a)['intention'] = {'but': r[0], 'plan': r[1], 'motif': 'agenda',
                                       'depuis': m.data['minutes'], 'attente': 0}
            propre = (r[0], [])
            # Coûts bornés explicites : 3 contre 3,18 minutes. La marge
            # commune vaut 5 % à VOL 1, 10 % à VOL 20.
            with patch.object(agendas, 'devis_observateur', return_value=((3.18 - 200 / 600) * .95, [])), \
                 patch.object(relations, 'chance_demande', return_value=1):
                for vol, attendu in [(20, c), (1, b)]:
                    m.objets[a]['profil']['caracteristiques']['VOL'] = vol
                    m = self.recharge(m)
                    with agendas.evaluation(m, a, publier=False):
                        choisi = agendas.choisir_mandataire(m, a, 'charge', propre, [3])
                    self.assertEqual(choisi[1][-1]['cible'], attendu)

    def test_echeance_calculee_sur_devis_ferme_et_non_sur_etat_prive(self):
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario, 'informer')
            p = self.parent(m, a)['parametres']
            echeance = agendas.echeance_observee(m, a, 'charge', c, 'informer', p)
            self.assertIsInstance(echeance, int)
            loin = 'entree' if scenario == 'mine' else 'chambre_cloche'
            placer(m, c, loin, [1, 1])
            lire(m, c)['croyances'].clear()
            m = self.recharge(m)
            self.assertEqual(agendas.echeance_observee(m, a, 'charge', c, 'informer', p), echeance)

    def test_resultat_appris_invalide_aussi_un_suffixe_deja_prepare(self):
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario)
            r = self.plan(m, a)
            ici = m.objets[a]['lieu']
            croire(m, a, cible, 'lieu', ici, 'vu', salle=ici, case=None)
            # Exécuter seulement les actes à effet du suffixe périmé : le
            # moteur les absorbe sans parole ni nouvelle charge.
            avant = len(m.data['chronique'])
            for g in (r[1][0], r[1][-1]):
                self.assertTrue(echanges.executer(m, a, g, []))
            self.assertEqual(len(agendas.enfants(m, a, 'charge')), 1)
            self.assertNotIn('avertissement', self.parent(m, a)['attributions'][0])
            self.assertFalse(any('reprend la charge' in x['texte'] for x in m.data['chronique'][avant:]))
            self.recharge(m)

    def test_information_reaffectee_et_nouvelle_echeance_physique(self):
        for scenario in ('crue_hameau', 'mine'):
            m, (a, b, c, cible, enfant) = self.scene(scenario, 'informer')
            r = self.plan(m, a)
            self.assertEqual(r[1][-1]['cible'], c)
            self.executer(m, a, r[1])
            m = self.recharge(m)
            actives = [x for x in self.parent(m, a)['attributions'] if x['etat'] == 'active']
            self.assertEqual([x['titulaire'] for x in actives], [c])
            self.assertIsInstance(actives[0]['echeance'], int)
            self.assertEqual(agendas.projets(m, b)[-1]['raison'], 'retrait entendu')


if __name__ == '__main__':
    unittest.main()
