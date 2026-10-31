"""Lot 388 : dette volontaire, effets, paroles et vues après recharge."""
import copy
import unittest

from donjon.biens import bourse, rembourser, rembourser_dette
from donjon.emissions import joueur, pnj
from donjon.esprits import croire
from donjon.monde import ErreurMonde
from donjon.paroles import OPERATIONS, preparer_parole, verifier_contenus
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.spatial import memoriser as memoriser_vue
from tests.support import sans_le_sou
from tests.test_audits_attendu import jouer
from tests.test_echanges_suite import ensemble, memoires
from tests.test_parole_corrections import banc
from tests.test_parole_commune import paroles_retenues
from tests.test_tensions import placer, recharger, vivre


def scene(qui='brune', montant=4):
    m = banc('comptes')
    m.data['dettes'] = []
    rembourser(m, 'joueur', qui, montant, 'vivres')
    memoriser_vue(m)  # La scène affichée au chargement est déjà connue avant l'aperçu.
    return recharger(m)


def reponse(qui, montant=''):
    return {'mode': 'parole_joueur', 'texte': '', 'faits': [], 'proposition': {
        'personnage': qui, 'replique': 'Je te rembourse ce que je te dois.',
        'operations_demandees': {t: t == 'rembourser' for t in OPERATIONS},
        'contenu': [{'type': 'rembourser', 'montant': montant}]}}


class RemboursementVolontaireTests(unittest.TestCase):
    def assertRecharge(self, m):
        r = recharger(m)
        self.assertEqual(r.data, m.data)
        self.assertEqual((fiche(r), regarder(r), scene_percue(r)),
                         (fiche(m), regarder(m), scene_percue(m)))
        self.assertEqual((joueur(r), pnj(r)), (joueur(m), pnj(m)))
        return r

    def test_corvus_rembourse_brune_et_un_autre_creancier_partiellement(self):
        for qui, montant, verse, reste in [('brune', '', 4, 0), ('marchand', '2', 2, 2)]:
            with self.subTest(qui=qui):
                m = scene(qui)
                avant = m.joueur['or'], bourse(m, qui)
                r, sortie, appels = jouer(m, f'{m.objets[qui]["nom"]}, je te rembourse.',
                                          [reponse(qui, montant)], [], suite=('tenter',))
                self.assertEqual((r.joueur['or'], bourse(r, qui)), (avant[0]-verse, avant[1]+verse))
                self.assertEqual(sum(d['montant'] for d in r.data['dettes']), reste)
                self.assertIn('Compris :', sortie)
                self.assertIn('rembourser', sortie)
                self.assertTrue(joueur(r))
                self.assertTrue(any(auteur == 'joueur' and qui in destinataires
                                    for auteur, destinataires, _ in paroles_retenues(r, qui)))
                self.assertEqual(memoires(r, qui, 'dette_honoree')[-1]['montant'], verse)
                self.assertIn(f"Tu m'as payé {verse} pièces.", pnj(r)[-1]['texte'])
                self.assertEqual(bool('Tu dois' in fiche(r)), bool(reste))
                self.assertRecharge(r)
                entier, _ = vivre(recharger(r), 2)
                coupe, _ = vivre(recharger(r), 1)
                coupe, _ = vivre(recharger(coupe), 1)
                for etat in (entier, coupe):
                    self.assertRecharge(etat)
                self.assertEqual((entier.joueur['or'], bourse(entier, qui), entier.data['dettes'], pnj(entier)),
                                 (coupe.joueur['or'], bourse(coupe, qui), coupe.data['dettes'], pnj(coupe)))

    def test_apercu_et_annulation_ne_paient_ni_ne_font_entendre(self):
        for suite in [(), ('annuler',)]:
            m = scene()
            r, sortie, _ = jouer(m, 'Brune, je te rembourse.', [reponse('brune')], [], suite=suite)
            self.assertEqual((r.joueur['or'], r.data['dettes'], joueur(r), pnj(r)),
                             (m.joueur['or'], m.data['dettes'], joueur(m), pnj(m)))
            self.assertIn('Compris :', sortie)
            self.assertEqual({k: v for k, v in r.data.items() if k != 'conversation'},
                             {k: v for k, v in m.data.items() if k != 'conversation'})
            self.assertRecharge(r)

    def test_refus_distincts_et_atomiques(self):
        for cas, attendu in [('trop', 'dû exact=4'), ('inconnue', 'montant=0'),
                              ('absent', 'même salle'), ('pauvre', 'fonds=0'), ('inaudible', 'saisit')]:
            with self.subTest(cas=cas):
                m = scene()
                montant = 5 if cas == 'trop' else 2
                if cas == 'inconnue':
                    m.data['dettes'] = []
                if cas == 'absent':
                    placer(m, 'brune', 'antichambre', (2, 3))
                if cas == 'pauvre':
                    m.joueur['or'] = 0
                if cas == 'inaudible':
                    m.objets['brune']['entend'] = False
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as refus:
                    rembourser_dette(m, 'joueur', 'brune', montant)
                self.assertIn(attendu, refus.exception.attendu)
                self.assertEqual(m.data, avant)
                self.assertRecharge(m)

    def test_plusieurs_lignes_sont_soldees_dans_l_ordre(self):
        m = scene(montant=2)
        rembourser(m, 'joueur', 'brune', 3, 'vivres', 'tache')
        p = reponse('brune', '4')['proposition']
        p.pop('operations_demandees')
        travail, rapport = preparer_parole(m, {**p, '_intention': 'Brune, je te rembourse quatre pièces.'})
        self.assertEqual([(d['quoi'], d['montant']) for d in travail.data['dettes']], [('tache', 1)])
        self.assertIn('Tu dois 1 pièce à Brune.', fiche(travail))
        self.assertEqual(m.data['dettes'][0]['montant'], 2)
        self.assertRecharge(travail)

    def test_contrat_montant_et_audience_individuelle(self):
        for montant in ['0', '-2', 'deux', 2, None]:
            with self.subTest(montant=montant), self.assertRaises(ErreurMonde):
                verifier_contenus(scene(), [{'type': 'rembourser', 'montant': montant}])
        m = scene()
        p = reponse('brune')['proposition']
        p.pop('operations_demandees')
        p['contenu'].append({'type': 'rembourser', 'montant': '1'})
        with self.assertRaises(ErreurMonde):
            preparer_parole(m, p)

    def test_le_temps_ne_debite_jamais_corvus(self):
        m = scene()
        avant = m.joueur['or'], bourse(m, 'brune'), copy.deepcopy(m.data['dettes'])
        r, _ = vivre(m, 2)
        self.assertEqual((r.joueur['or'], bourse(r, 'brune'), r.data['dettes']), avant)
        self.assertRecharge(r)

    def test_pnj_honnete_sans_reclamation_entier_ou_decoupe(self):
        for a in ('joueur', 'ilse'):
            etats = []
            for decoupe in ((2,), (1, 1)):
                m = scene()
                m.data['dettes'] = []
                m.objets['brune']['profil']['valeurs']['honnetete'] = 100
                # La dette personnelle de départ est un autre souci, qui peut
                # déclencher une vente concurrente : seule la créance testée reste.
                m.objets['brune']['profil'].setdefault('situation', {})['dette'] = 0
                if a == 'ilse':
                    ensemble(m, 'brune', 'ilse')
                    m.joueur.update(salle='antichambre', position=[3, 5])
                rembourser(m, 'brune', a, 2, 'vivres')
                avant = bourse(m, 'brune'), bourse(m, a)
                # Une réclamation n'est pas nécessaire : créancier non averti.
                m.data['dettes'][0]['a_prevenir'] = True
                for n in decoupe:
                    m, _ = vivre(recharger(m), n)
                self.assertEqual(m.data['dettes'], [])
                self.assertEqual((bourse(m, 'brune'), bourse(m, a)), (avant[0]-2, avant[1]+2))
                self.assertEqual(len(memoires(m, 'brune', 'rembourse')), 1)
                self.assertEqual(len([p for p in pnj(m) if p['acte'] == 'remboursement']), 1)
                if a != 'joueur':
                    self.assertEqual(len(memoires(m, a, 'dette_honoree')), 1)
                etats.append((m.data['dettes'], bourse(m, 'brune'), bourse(m, a), pnj(m)))
                self.assertRecharge(m)
            self.assertEqual(etats[0], etats[1])

    def test_pnj_se_deplace_pour_rendre_et_ne_repaye_pas_sans_fonds(self):
        from donjon.planification import rembourser as planifier
        m = scene()
        m.data['dettes'] = []
        m.objets['brune']['profil']['valeurs']['honnetete'] = 100
        m.objets['brune']['profil'].setdefault('situation', {})['dette'] = 0
        sans_le_sou(m, 'marchand', 'aubin', 'ilse')  # Aucun achat concurrent ne finance un second versement.
        m.data['finances_pnj']['brune'] = 1
        rembourser(m, 'brune', 'joueur', 4, 'vivres')
        placer(m, 'brune', 'antichambre', (2, 3))
        croire(m, 'brune', 'joueur', 'lieu', 'echoppe', 'vu', salle='echoppe', case=[2, 1])
        m.data['dettes'][0]['a_prevenir'] = True
        plan = planifier(recharger(m), 'brune')
        self.assertIsNotNone(plan)
        self.assertEqual(plan[1][-1]['operation'], 'rembourser')
        self.assertTrue(any(e['operation'] == 'aller' for e in plan[1]))
        avant = m.joueur['or']
        m, _ = vivre(recharger(m), 5)
        self.assertEqual(m.joueur['or'], avant + 1)
        self.assertEqual(m.data['dettes'][0]['montant'], 3)
        self.assertEqual(len(memoires(m, 'brune', 'rembourse')), 1)
        m, _ = vivre(recharger(m), 2)
        self.assertEqual(m.joueur['or'], avant + 1)
        self.assertEqual(len(memoires(m, 'brune', 'rembourse')), 1)
        self.assertRecharge(m)


if __name__ == '__main__':
    unittest.main()
