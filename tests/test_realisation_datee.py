"""E2 : effet réel, date inclusive, compte unique et connaissance séparée."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon import agendas, echanges
from donjon.biens import bourse, solder
from donjon.deplacement_objet import deplacer
from donjon.esprits import constater, lire, percevoir_tous
from donjon.monde import Monde, ErreurMonde
from donjon.pnj import _executer, agir, avancer
from donjon.rendu import regarder as rendu
from donjon.scene import scene_percue
from donjon.temps import ecouler, instant
from tests.support import regarder
from tests.test_lampes_parts import nuit_noire
from tests.test_tache_promise_recours import reserve
from tests.test_tensions import recharger


def geste(m, qui, op, objet, outil=''):
    return _executer(m, qui, {'operation': op, 'cible': objet, 'outil': outil,
                              'lieu': '', 'condition': ''}, [], [])


class RealisationDateeTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(json.dumps(m.data, ensure_ascii=False), json.dumps(r.data, ensure_ascii=False))
        self.assertEqual(rendu(m), rendu(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        self.assertEqual(agendas.promesses_visibles(m), agendas.promesses_visibles(r))
        self.assertEqual(m.data.get('emissions_parole'), r.data.get('emissions_parole'))
        return r

    def dater(self, m, qui, limite=100):
        x = agendas.en_cours(m, qui)[0]
        agendas.retirer_proposition(m, qui, x)
        agendas.prendre(m, qui, x, limite=limite)
        return agendas.en_cours(m, qui)[0]

    def huile(self):
        # Cas réel 347/1.2 : une part d'huile remise ne recharge pas la lanterne.
        m = nuit_noire('auberge', 'joss', 'odile', 'lanterne_etable', 'pot_huile', 'etable')
        m.objets['pot_huile']['charges'] = 6
        m.data['finances_pnj']['joss'] = 5
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.demander(m, 'joss', 'odile', 'pot_huile',
                                              prix=1, remettre_part=True), 'vendu')
        x = self.dater(m, 'odile')
        deplacer(m, x['condition']['objet'], 'odile')
        return self.recharge(m), x

    def verrou(self):
        m, qui, pour, c = reserve()
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(echanges.engager(m, pour, qui, c, 1), 'accepte')
        x = self.dater(m, qui)
        self.assertTrue(geste(m, qui, 'fermer', c['objet']))
        return self.recharge(m), qui, pour, x

    def test_huile_remise_aux_trois_bornes_et_jamais_rechargee_par_la_livraison(self):
        for t in (99, 100, 101):
            with self.subTest(t=t):
                m, x = self.huile()
                avant = (bourse(m, 'joss'), bourse(m, 'odile'))
                combustible = m.objets['lanterne_etable']['combustible']
                ecouler(m, t)
                echanges.remettre(m, 'odile', 'joss', x['condition']['objet'])
                m = self.recharge(m)
                issue, = agendas.issues_temporelles(m)
                self.assertEqual(issue['verdict'], 'tenue_a_temps' if t <= 100 else 'en_retard')
                self.assertEqual(issue['realisation'], t if t <= 100 else None)
                self.assertEqual(m.objets[x['condition']['objet']]['lieu'], 'joss')
                self.assertEqual(m.objets['lanterne_etable']['combustible'], combustible)
                self.assertEqual(agendas.en_cours(m, 'odile'), [])
                # Une remise volontaire après clôture ne réécrit pas le contrat remboursable.
                for _ in range(2):
                    agendas.echoir(m, 'odile')
                    solder(m, [])
                    m = self.recharge(m)
                self.assertEqual(len(agendas.issues_temporelles(m)), 1)
                self.assertEqual((bourse(m, 'joss'), bourse(m, 'odile')),
                                 avant if t <= 100 else (avant[0] + 1, avant[1] - 1))

    def test_tache_ponctuelle_aux_trois_bornes_remboursement_unique(self):
        for t in (99, 100, 101):
            with self.subTest(t=t):
                m, qui, pour, x = self.verrou()
                avant = (bourse(m, qui), bourse(m, pour))
                ecouler(m, t)
                self.assertTrue(geste(m, qui, 'verrouiller', 'garde_manger', 'cle_garde_manger'))
                m = self.recharge(m)
                issue, = agendas.issues_temporelles(m)
                self.assertEqual(issue['realisation'], t if t <= 100 else None)
                self.assertEqual(issue['verdict'], 'tenue_a_temps' if t <= 100 else 'en_retard')
                self.assertTrue(m.objets['garde_manger']['verrouillee'])
                self.assertEqual(agendas.en_cours(m, qui), [])
                for _ in range(2):
                    agendas.echoir(m, qui)
                    solder(m, [])
                    m = self.recharge(m)
                self.assertEqual(len(agendas.issues_temporelles(m)), 1)
                self.assertEqual((bourse(m, qui), bourse(m, pour)),
                                 avant if t <= 100 else (avant[0] - 1, avant[1] + 1))

    def test_constat_tardif_ne_change_pas_la_date_d_un_effet_de_tiers(self):
        m, qui, pour, x = self.verrou()
        # Le propriétaire réalise lui-même la tâche ; le prestataire ne l'apprend que plus tard.
        deplacer(m, 'cle_garde_manger', 'joueur')
        ecouler(m, 99)
        avant = agendas.etat_promis(m)
        from donjon.moteur import Moteur
        Moteur._appliquer(m, ('verrouiller', 'garde_manger', 'cle_garde_manger'), [])
        agendas.constater_geste_joueur(m, avant)
        m = self.recharge(m)
        self.assertEqual(agendas.issues_temporelles(m)[0]['realisation'], 99)
        ecouler(m, 601)
        # La fermeture est visible ; le verrou ne s'apprend qu'en l'essayant.
        self.assertFalse(geste(m, qui, 'ouvrir', 'garde_manger'))
        agendas.echoir(m, qui)
        m = self.recharge(m)
        self.assertEqual(agendas.issues_temporelles(m)[0]['verdict'], 'tenue_a_temps')
        self.assertTrue(any(s['type'] == 'engagement_tenu' and s.get('condition') == x['condition']
                            for s in lire(m, qui)['memoire']))

    def test_etat_seulement_trouve_vrai_ne_recoit_pas_une_date_inventee(self):
        m, qui, _, _ = self.verrou()
        m.objets['garde_manger']['verrouillee'] = True
        ecouler(m, 601)
        constater(m, qui, 'garde_manger', 'vu')
        agendas.echoir(m, qui)
        issue, = agendas.issues_temporelles(self.recharge(m))
        self.assertIsNone(issue['realisation'])
        self.assertEqual(issue['verdict'], 'en_retard')

    def test_expiration_arrete_le_plan_et_ne_previent_pas_un_absent(self):
        m, qui, pour, x = self.verrou()
        from donjon.planification import planifier_engagement
        but, plan = planifier_engagement(m, qui, x)
        e = lire(m, qui)
        e['intention'] = {'but': but, 'motif': 'engagement', 'plan': plan,
                          'depuis': 0, 'attente': 0}
        m.objets[pour]['lieu'] = 'cellier' if m.objets[qui]['lieu'] != 'cellier' else 'salle_commune'
        avant = copy.deepcopy(lire(m, pour)['relations'])
        ecouler(m, 101)
        agir(m, qui, instant(m), [])
        m = self.recharge(m)
        self.assertFalse(m.objets['garde_manger']['verrouillee'])
        self.assertIsNone(lire(m, qui)['intention'])
        self.assertEqual(lire(m, pour)['relations'], avant)
        self.assertFalse(any(s['type'] in ('creance', 'engagement_abandonne')
                             for s in lire(m, pour)['memoire']))

    def test_laps_continu_decoupe_recharge_et_mots_identiques(self):
        m, qui, _, _ = self.verrou()
        # Ils restent occupés : seule l'échéance contractuelle doit réveiller l'ordonnanceur.
        for e in m.data['esprits'].values():
            e['libre'], e['eveil'], e['veille'] = 1000, None, None
        def jouer(pas):
            a, lignes = self.recharge(m), []
            for dt in pas:
                ecouler(a, dt)
                avancer(a, 0, lignes, dixiemes=dt)
                a = self.recharge(a)
            return a, lignes
        a, la = jouer([102])
        b, lb = jouer([99, 1, 1, 1])
        self.assertEqual(a.data, b.data)
        self.assertEqual(la, lb)
        self.assertEqual(agendas.issues_temporelles(a)[0]['cloture'], 101)
        self.assertEqual(rendu(a), rendu(b))
        self.assertEqual(scene_percue(a), scene_percue(b))
        self.assertEqual(json.dumps(a.data, ensure_ascii=False), json.dumps(b.data, ensure_ascii=False))

    def test_part_reelle_du_relais_livree_memes_paroles_et_monde_en_bloc_ou_decoupe(self):
        from donjon.paroles import preparer_parole
        from tests.test_parts_achetees import antichambre_du_banc, parole
        from tests.test_tensions import vivre
        m, rapport = preparer_parole(antichambre_du_banc(), parole(
            'aubin', 'Je te paie trois pièces pour une de tes planches.', 'demande', 'planches', '3'))
        self.assertTrue(rapport['faits'])
        self.dater(m, 'aubin', limite=6000)
        a, la = vivre(self.recharge(m), 3)
        b, lb = self.recharge(m), []
        for _ in range(3):
            b, lignes = vivre(b, 1)
            lb.extend(lignes)
        self.assertEqual(a.data, b.data)
        self.assertEqual(la, lb)
        self.assertIn("Aubin te remet les planches de bac : tu l'avais payé.", la)
        a = self.recharge(a)
        b = self.recharge(b)
        self.assertEqual(scene_percue(a), scene_percue(b))
        self.assertEqual(rendu(a), rendu(b))
        self.assertEqual(json.dumps(a.data, ensure_ascii=False), json.dumps(b.data, ensure_ascii=False))
        self.assertEqual(a.objets['planches_1']['lieu'], 'joueur')
        self.assertEqual(agendas.issues_temporelles(a)[0]['verdict'], 'tenue_a_temps')

    def test_promesse_joueur_datee_constatee_plus_tard_une_seule_fois(self):
        from donjon.moteur import Moteur
        m, qui, pour, x = self.verrou()
        agendas.retirer_proposition(m, qui, x)
        agendas.prendre(m, 'joueur', {'condition': x['condition'], 'pour': pour, 'minute': 0}, limite=100)
        deplacer(m, 'cle_garde_manger', 'joueur')
        ecouler(m, 100)
        Moteur._appliquer(m, ('verrouiller', 'garde_manger', 'cle_garde_manger'), [])
        m = self.recharge(m)
        self.assertEqual(agendas.issues_temporelles(m)[0]['realisation'], 100)
        self.assertEqual(agendas.promesses_visibles(m), [])
        self.assertFalse(any(s['type'] == 'engagement_tenu' for s in lire(m, pour)['memoire']))
        ecouler(m, 600)
        regarder(m, pour, 'garde_manger')
        constater(m, pour, 'garde_manger', 'vu')
        self.assertFalse(geste(m, pour, 'ouvrir', 'garde_manger'))
        lignes = []
        agendas.observer_promesses(m, lignes)
        m = self.recharge(m)
        agendas.observer_promesses(m, lignes)
        self.assertEqual(len(lignes), 1)
        self.assertIn('Tu as tenu ta promesse', lignes[0])
        self.recharge(m)

    def test_issue_corrompue_refusee_a_la_recharge(self):
        m, qui, _, _ = self.verrou()
        ecouler(m, 100)
        geste(m, qui, 'verrouiller', 'garde_manger', 'cle_garde_manger')
        m = self.recharge(m)
        for champ, valeur in (('realisation', True), ('realisation', 101),
                               ('verdict', 'en_retard'), ('cloture', -1), ('constatee', 1)):
            with self.subTest(champ=champ):
                copie = copy.deepcopy(m)
                copie.data['issues_obligations'][0][champ] = valeur
                with self.assertRaises(ErreurMonde) as erreur:
                    recharger(copie)
                self.assertIn(champ, erreur.exception.attendu)

    def test_limite_remplace_le_maximum_generique_sans_migration(self):
        m, qui, pour, x = self.verrou()
        agendas.retirer_proposition(m, qui, x)
        ancien_max = echanges.ENGAGEMENT_MAX * 600
        x.pop('reference_temporelle')
        agendas.prendre(m, qui, x, limite=ancien_max + 6000)
        agendas.prendre(m, 'joueur', {'condition': x['condition'], 'pour': pour, 'minute': 0},
                        limite=ancien_max + 6000)
        ecouler(m, ancien_max + 1)
        agendas.echoir(m, qui)
        agendas.observer_promesses(m, [])
        m = self.recharge(m)
        self.assertEqual(len(agendas.en_cours(m, qui)), 1)
        self.assertEqual(len(agendas.en_cours(m, 'joueur')), 1)
        self.assertEqual(agendas.issues_temporelles(m), [])

    def test_compte_reel_cache_a_distance_puis_remboursement_visible(self):
        from donjon.biens import comptes_joueur
        from donjon.paroles import preparer_parole
        from tests.test_parts_achetees import antichambre_du_banc, parole
        m, _ = preparer_parole(antichambre_du_banc(), parole(
            'aubin', 'Je te paie trois pièces pour une de tes planches.', 'demande', 'planches', '3'))
        self.dater(m, 'aubin')
        m.joueur.update(salle='chambre_cloche', position=[1, 3])
        ecouler(m, 101)
        agendas.echoir(m, 'aubin')
        self.assertEqual(m.data['dettes'][0]['montant'], 3)
        self.assertFalse(any('te doit 3 pièces' in t for t in comptes_joueur(m)))
        m = self.recharge(m)
        m.joueur.update(salle='antichambre', position=[1, 3])
        regarder(m, 'aubin', 'joueur')
        percevoir_tous(m)
        lignes = []
        solder(m, lignes)
        m = self.recharge(m)
        self.assertTrue(any('te rend 3 pièces' in t for t in lignes), lignes)
        self.assertEqual(m.joueur['or'], 24)
        self.assertEqual(m.data['dettes'], [])
        self.assertEqual(agendas.issues_temporelles(m)[0]['verdict'], 'en_retard')

    def test_silence_du_joueur_ne_prouve_pas_un_manquement_meme_a_portee_de_parole(self):
        m, qui, pour, x = self.verrou()
        agendas.retirer_proposition(m, qui, x)
        agendas.prendre(m, 'joueur', {'condition': x['condition'], 'pour': pour, 'minute': 0}, limite=100)
        avant = copy.deepcopy(lire(m, pour)['relations'])
        ecouler(m, 101)
        lignes = []
        agendas.observer_promesses(m, lignes)
        m = self.recharge(m)
        self.assertEqual(lignes, [])
        self.assertEqual(lire(m, pour)['relations'], avant)
        self.assertFalse(agendas.issues_temporelles(m)[0]['constatee'])
        ecouler(m, 600)
        self.assertTrue(geste(m, pour, 'ouvrir', 'garde_manger'))
        agendas.observer_promesses(m, lignes)
        self.assertEqual(len(lignes), 1)
        self.assertIn('Tu as abandonné ta promesse', lignes[0])
        self.recharge(m)


if __name__ == '__main__':
    unittest.main()
