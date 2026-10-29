"""Occasion, marché réel et tâche tenue, avec recharge du monde et de la vue."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, occasion_protection as occasion
from donjon.banc_pnj import creer
from donjon.biens import richesse
from donjon.esprits import lire, croire, percevoir_tous
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import MINUTE
from tests.support import calme, presentes, regarder as orienter
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


def scene(scenario='auberge', joueur=False):
    m = presentes(creer(scenario, 1985, 'fixe'))
    a, b, salle, ailleurs = (('hugues', 'anselme', 'salle_commune', 'etable') if scenario == 'auberge'
                             else ('aubin', 'ilse', 'antichambre', 'echoppe'))
    ids = [i for i, o in m.objets.items() if o.get('profil')]
    calme(m, *ids)
    from donjon.geometrie import cases
    for n, i in enumerate(ids):
        p = m.objets[i]['profil']
        p.update(pulsions=[], agendas=[], protege=[], situation={}, alerte=9)
        p['valeurs'].update(ambition=0, empathie=0, altruisme=0)
        lire(m, i).update(pulsions=[], intention=None, libre=60000, eveil=None)
        placer(m, i, ailleurs, sorted(cases(m.data['salles'][ailleurs]))[n])
    y = 3 if scenario == 'auberge' else 5
    placer(m, a, salle, [2, y])
    placer(m, b, salle, [3, y])
    m.joueur.update(salle=salle, position=[2, y + 1], orientation='nord')
    p = m.objets[a]['profil']
    p['valeurs'].update(ambition=100, courage=100)
    p['caracteristiques'].update(FOR=20, CHA=20, ELO=20)
    p['situation'] = {'projet': 100}
    if joueur:
        b = 'joueur'
    else:
        lire(m, b)['besoins']['securite'] = 85.
        m.data['finances_pnj'][b] = 80
    from donjon import relations
    lire(m, a)['relations'][b] = relations._nouvelle({'confiance': 100})
    if b != 'joueur':
        lire(m, b)['relations'][a] = relations._nouvelle({'confiance': 100})
    orienter(m, a, b)
    percevoir_tous(m)
    croire(m, a, b, 'pieces', 80, 'savoir')
    if joueur:
        m.joueur['or'] = 80
        # Cause apprise : le joueur n'a pas de besoin privé de sécurité à lire.
        croire(m, a, 'lucien', 'lieu', ailleurs, 'dit:anselme',
               salle=ailleurs, case=m.objets['lucien']['position'])
        croire(m, a, 'lucien', 'violence', {'joueur': {
            'minute': 0, 'menace': True, 'operation': 'frapper', 'clos': False}}, 'dit:anselme')
    lire(m, a)['libre'] = 0
    return recharger(m), a, b


class OccasionProtectionTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        return n

    def laps(self, m, dt):
        a, b = self.recharge(m), self.recharge(m)
        with patch.object(type(m), 'd20', return_value=20):
            passer(a, dt)
            for duree in (17, 83, dt - 100):
                passer(b, duree)
                b = self.recharge(b)
        a = self.recharge(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(scene_percue(a), scene_percue(b))
        return a

    def test_auberge_et_relais_offre_autonome_paiement_et_protection(self):
        for scenario in ('auberge', 'relais'):
            with self.subTest(scenario=scenario):
                m, a, b = scene(scenario)
                self.assertTrue(occasion.peur_crue(m, a, b))
                avant = richesse(m, a), richesse(m, b)
                m = self.laps(m, 3 * MINUTE)
                offres = [s for s in lire(m, a)['memoire'] if s['type'] == 'proposition']
                self.assertEqual(len(offres), 1)
                self.assertEqual(offres[0]['issue'], 'accepte')
                prix = offres[0]['demande']['montant']
                self.assertEqual((richesse(m, a), richesse(m, b)), (avant[0] + prix, avant[1] - prix))
                self.assertIn(b, d.proteges(m, a))
                self.assertTrue(any(x.get('commence') is not None for x in agendas.en_cours(m, a)))
                self.assertTrue(any('sous protection' in x['texte'] and '(accepte)' in x['texte'] for x in m.data['chronique']))
                # Un calme réellement perçu clôt le service sans reprendre l'avance.
                lire(m, b)['besoins']['securite'] = 0.
                percevoir_tous(m)
                agendas.echoir(m, a)
                m = self.recharge(m)
                contrats = [x for x in agendas.projets(m, a) if x['origine']['type'] == 'contrat']
                self.assertEqual(contrats[0]['etat'], 'atteint')
                self.assertEqual(contrats[0]['raison'], 'danger cru passe')
                self.assertFalse(agendas.en_cours(m, a))
                self.assertEqual(richesse(m, a), avant[0] + prix)

    def test_pas_de_peur_de_fonds_d_interet_ou_de_capacite(self):
        for cas in ('peur', 'fonds', 'interet', 'courage', 'disponibilite'):
            with self.subTest(cas=cas):
                m, a, b = scene()
                if cas == 'peur':
                    lire(m, b)['besoins']['securite'] = 0.
                    percevoir_tous(m)
                elif cas == 'fonds':
                    croire(m, a, b, 'pieces', 0, 'savoir')
                elif cas == 'interet':
                    m.objets[a]['profil']['valeurs']['ambition'] = 0
                elif cas == 'courage':
                    m.objets[a]['profil']['valeurs']['courage'] = 0
                else:
                    lire(m, a)['besoins']['faim'] = 100.
                agendas.actualiser(m, a)
                self.assertFalse([x for x in agendas.projets(self.recharge(m), a) if x['sorte'] == 'offrir'])

    def test_naissance_differee_et_aucun_savoir_prive_lu(self):
        from donjon.planification import vues_du_choix
        m, a, b = scene()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(RuntimeError), vues_du_choix(m, a):
            agendas.actualiser(m, a)
            self.assertEqual(m.data, avant)
            raise RuntimeError()
        self.assertEqual(m.data, avant)
        offres = list(occasion.occasions(m, a))
        m.data['finances_pnj'][b] = 0
        lire(m, b)['besoins']['securite'] = 0.
        self.assertEqual(list(occasion.occasions(m, a)), offres)
        self.recharge(m)

    def test_plan_recharge_revalide_la_peur_et_la_solvabilite_crues(self):
        from donjon.echanges import executer
        for cas in ('calme', 'fonds'):
            with self.subTest(cas=cas):
                m, a, b = scene()
                d.choisir(m, a, 0)
                m = self.recharge(m)
                geste = lire(m, a)['intention']['plan'][-1]
                self.assertEqual(geste['operation'], 'proposer')
                avant = richesse(m, a), richesse(m, b)
                if cas == 'fonds':
                    croire(m, a, b, 'pieces', 0, 'savoir')
                else:
                    lire(m, b)['besoins']['securite'] = 0.
                    percevoir_tous(m)
                self.assertFalse(executer(m, a, geste, []))
                m = self.recharge(m)
                self.assertEqual((richesse(m, a), richesse(m, b)), avant)
                self.assertFalse(agendas.en_cours(m, a))

    def test_joueur_choisit_sans_paiement_implicite(self):
        from donjon.dialogues import commande_sociale, preparer_conversation
        m, a, b = scene(joueur=True)
        avant = richesse(m, a), richesse(m, b)
        m = self.laps(m, 2 * MINUTE)
        self.assertEqual((richesse(m, a), richesse(m, b)), avant)
        self.assertFalse(agendas.en_cours(m, a))
        from donjon.emissions import lire as emissions
        self.assertFalse([p for p in emissions(m) if p['locuteur'] == 'joueur'])
        p = commande_sociale(m, 'accepter offre')
        m, rapport = preparer_conversation(m, p)
        m = self.recharge(m)
        self.assertTrue(any('accepte' in t for t in rapport['faits']))
        self.assertIn('joueur', d.proteges(m, a))
        self.assertLess(richesse(m, 'joueur'), avant[1])

    def test_refus_retenu_sans_rearmement_par_le_delai(self):
        m, a, b = scene()
        from donjon import relations
        lire(m, b)['relations'][a] = relations._nouvelle({'confiance': 0})
        # Aucun gain pour l'auditeur : jugement commun, puis refus enregistré.
        m = self.laps(m, 3 * MINUTE)
        offres = [s for s in lire(m, a)['memoire'] if s['type'] == 'proposition']
        self.assertEqual(len(offres), 1)
        self.assertNotEqual(offres[0]['issue'], 'accepte')
        self.assertFalse(agendas.en_cours(m, a))
        m.data['minutes'] += 500
        agendas.actualiser(m, a)
        aoffre = next(x for x in agendas.projets(m, a) if x['sorte'] == 'offrir')
        self.assertIsNone(agendas.planifier(m, a, aoffre['id']))
        self.recharge(m)

    def test_fins_contractuelles_et_remboursement_commun(self):
        for fin in ('echeance', 'mort', 'parti'):
            with self.subTest(fin=fin):
                m, a, b = scene()
                avant = richesse(m, a), richesse(m, b)
                m = self.laps(m, 2 * MINUTE)
                contrat = next(x for x in agendas.projets(m, a) if x['origine']['type'] == 'contrat')
                if fin == 'echeance':
                    m = self.laps(m, (contrat['echeance'] - m.data['minutes'] + 1) * MINUTE)
                else:
                    # Fins crues : le corps réel et les ressources privées n'en sont pas la source.
                    croire(m, a, b, 'etat', {fin: True}, 'dit:odile')
                    agendas.echoir(m, a)
                m = self.recharge(m)
                contrat = next(x for x in agendas.projets(m, a) if x['origine']['type'] == 'contrat')
                self.assertEqual(contrat['etat'], 'atteint' if fin == 'echeance' else 'abandonne')
                self.assertFalse(agendas.en_cours(m, a))
                if fin != 'echeance':
                    from donjon.biens import dettes
                    dues = [x for x in dettes(m) if x['de'] == a and x['a'] == b]
                    self.assertEqual(len(dues), 1)
                    self.assertEqual(dues[0]['montant'], richesse(m, a) - avant[0])
                    self.assertEqual(dues[0]['quoi'], 'tache')

    def test_joueur_refuse_et_acceptation_tardive_revalidee(self):
        from donjon.dialogues import commande_sociale, preparer_conversation
        for choix in ('refuser offre', 'accepter offre'):
            with self.subTest(choix=choix):
                m, a, b = scene(joueur=True)
                avant = richesse(m, a), richesse(m, b)
                m = self.laps(m, 2 * MINUTE)
                if choix.startswith('accepter'):
                    m.data['minutes'] += 40
                m, rapport = preparer_conversation(m, commande_sociale(m, choix))
                m = self.recharge(m)
                self.assertFalse(agendas.en_cours(m, a))
                self.assertEqual((richesse(m, a), richesse(m, b)), avant)


if __name__ == '__main__':
    unittest.main()
