"""399 : remboursement direct commun au web, à la console et à Textual."""
import copy
import unittest

from donjon.biens import bourse, comptes_joueur, rembourser
from donjon.commandes import DescripteurPublic
from donjon.comptes_terminal import ComptesTerminal
from donjon.dialogues import comptes_publics, preparer_direct, valider_choix_compte
from donjon.emissions import lire as emissions
from donjon.monde import ErreurMonde
from donjon.spatial import installer
from tests import test_comptes_publics as web
from tests import test_comptes_terminal as terminal
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests.test_rembourser_dette import scene
from tests.test_tensions import placer, recharger


class RembourserPublicTests(unittest.TestCase):
    def test_meme_parole_typee_du_388_total_et_partiel(self):
        for qui, verse in (('brune', None), ('marchand', 2)):
            m = scene(qui)
            r, _ = web.ComptesPublicsTests().parite_parole(
                m, web.choix(m, 'rembourser', qui), montant=verse)
            paye = 4 if verse is None else verse
            self.assertEqual((r.joueur['or'], bourse(r, qui)),
                             (m.joueur['or'] - paye, bourse(m, qui) + paye))

    def test_projection_solde_cumule_absent_et_confidentialite(self):
        m = scene()
        rembourser(m, 'joueur', 'brune', 3, 'vivres')
        rembourser(m, 'aubin', 'brune', 937, 'vivres')
        rembourser(m, 'aubin', 'joueur', 851, 'vivres', informer=False)
        placer(m, 'brune', 'antichambre', (2, 3))
        public = comptes_publics(m)
        x = web.choix(m, 'rembourser', 'brune')
        self.assertEqual(x['descripteur']['parametres']['montant'], 7)
        self.assertEqual(x['descripteur']['parametres']['compte']['montant'], 7)
        self.assertIn('7 pièces', x['nom'])
        self.assertEqual(public['lignes'], comptes_joueur(m))
        self.assertNotIn('937', str(public)); self.assertNotIn('851', str(public))
        self.assertEqual(comptes_publics(recharger(m)), public)

    def test_montant_web_terminal_et_annulations_locales(self):
        m = scene()
        x = web.choix(m, 'rembourser', 'brune')
        public = etat(m)
        index = public['comptes']['choix'].index(x)
        for montant in (None, 2, 5, 0, -1, '1.5', '', '1e2'):
            with self.subTest(montant=montant):
                public['sonde_comptes'] = {'choix': index}
                if montant is not None:
                    public['sonde_comptes']['montant'] = montant
                r = page(m, public)['comptes']
                self.assertEqual(r['montant_defaut'], '4')
                self.assertTrue(r['montant_visible'])
                self.assertEqual(r['envois'], int(montant in (None, 2, 5)))
                if r['envois']:
                    attendu = copy.deepcopy(x['descripteur'])
                    attendu['parametres']['montant'] = 4 if montant is None else montant
                    self.assertEqual(r['envoye'], attendu)
        f = ComptesTerminal(comptes_publics(m))
        self.assertIsNone(f.saisir(str(index + 1)))
        self.assertIn('Entrée : 4', f.rendre())
        for texte in ('0', '-1', '1.5', '1e2', 'deux', '9' * 5000):
            with self.assertRaises(ValueError):
                f.saisir(texte)
            self.assertFalse(f.terminee)
        self.assertEqual(f.saisir('').contenu, x['descripteur'])
        for apres in (False, True):
            f = ComptesTerminal(comptes_publics(m))
            if apres:
                f.saisir(str(index + 1))
            self.assertIsNone(f.saisir('annuler'))
            self.assertTrue(f.terminee)
        self.assertIsNone(web.ComptesPublicsTests().clic(m, x, annuler=True).contenu)

    def test_validation_stricte_des_termes_et_refus_du_388_sans_mutation(self):
        for cas, message in (('trop', 'Le dû est de 4 pièces seulement.'),
                             ('absent', "Le créancier n'est pas présent"),
                             ('pauvre', 'La bourse ne suffit pas')):
            m = scene()
            d = copy.deepcopy(web.choix(m, 'rembourser', 'brune')['descripteur'])
            if cas == 'trop':
                d['parametres']['montant'] = 5
            if cas == 'absent':
                placer(m, 'brune', 'antichambre', (2, 3))
            if cas == 'pauvre':
                m.joueur['or'] = 0
            avant = copy.deepcopy(m.data)
            with self.subTest(cas=cas), self.assertRaises(ErreurMonde) as refus:
                preparer_direct(m, DescripteurPublic(d))
            self.assertIn(message, str(refus.exception))
            self.assertTrue(refus.exception.attendu)
            self.assertEqual(m.data, avant)
            self.assertEqual(terminal.vues(recharger(m)), terminal.vues(m))
        m = scene()
        original = web.choix(m, 'rembourser', 'brune')['descripteur']
        for champ, valeur in (('montant', True), ('montant', 2.0), ('montant', '2'),
                               ('compte', {}), ('operation', 'payer'), ('injection', 'oui')):
            d = copy.deepcopy(original)
            d['parametres'][champ] = valeur
            with self.subTest(champ=champ, valeur=valeur), self.assertRaises(ErreurMonde):
                valider_choix_compte(m, d)
        d = copy.deepcopy(original)
        d['parametres']['compte']['montant'] = 4.0
        with self.assertRaises(ErreurMonde):
            valider_choix_compte(m, d)


class ParcoursRemboursement:
    jouer = terminal.ParcoursComptes.jouer
    comparer = terminal.ParcoursComptes.comparer

    async def test_total_brune_partiel_autre_creancier_recharge_laps(self):
        for qui, verse in (('brune', None), ('marchand', 2)):
            m = scene(qui)
            avant = m.joueur['or'], bourse(m, qui)
            r, lignes = await self.comparer(m, web.choix(m, 'rembourser', qui), montant=verse, laps=True)
            paye = 4 if verse is None else verse
            self.assertEqual((r.joueur['or'], bourse(r, qui)), (avant[0] - paye, avant[1] + paye))
            self.assertEqual(sum(d['montant'] for d in r.data['dettes']), 4 - paye)
            self.assertIn(f"Tu m'as payé {paye} pièces.", '\n'.join(lignes))
            self.assertEqual('Tu dois' in '\n'.join(comptes_joueur(r)), paye != 4)

    async def test_annuler_et_peremption_reception_confirmation(self):
        for mode in ('annuler', 'reception', 'confirmation'):
            m = scene()
            await self.comparer(m, web.choix(m, 'rembourser', 'brune'), montant=2,
                                annuler=mode == 'annuler', perime=None if mode == 'annuler' else mode)
        m = scene()
        numero = str(comptes_publics(m)['choix'].index(web.choix(m, 'rembourser', 'brune')) + 1)
        r, _, captures, _ = await self.jouer(m, ['comptes', numero, 'annuler'])
        self.assertFalse(captures)
        self.assertEqual(r.data, m.data)

    async def test_fonds_et_presence_revalides_a_confirmation(self):
        for cas, message in (('absent', "Le créancier n'est pas présent"),
                             ('pauvre', 'La bourse ne suffit pas')):
            m = scene()
            installer(m)
            x = web.choix(m, 'rembourser', 'brune')
            def mutation(monde):
                if cas == 'absent':
                    placer(monde, 'brune', 'antichambre', (2, 3))
                else:
                    monde.joueur['or'] = 0
            d = web.ComptesPublicsTests().clic(m, x, montant=2)
            attendu, sorties, _ = web.ComptesPublicsTests().boucle(m.copier(), [d, 'tenter'], mutation=mutation)
            r, lignes, _, _ = await self.jouer(m, [*terminal.parcours(m, x, 2), 'tenter'], mutation=mutation)
            self.assertIn(message, '\n'.join(sorties))
            self.assertIn(message, '\n'.join(lignes))
            self.assertEqual(terminal.sans_saisie(r.data), terminal.sans_saisie(attendu.data))
            self.assertEqual((bourse(r, 'brune'), r.data['dettes'], emissions(r)),
                             (bourse(m, 'brune'), m.data['dettes'], emissions(m)))
            self.assertEqual(terminal.vues(recharger(r)), terminal.vues(r))

    async def test_refus_distincts_sur_les_trois_interfaces(self):
        for cas, message in (('trop', 'Le dû est de 4 pièces seulement.'),
                             ('absent', "Le créancier n'est pas présent"),
                             ('pauvre', 'La bourse ne suffit pas')):
            m = scene()
            installer(m)
            if cas == 'absent':
                placer(m, 'brune', 'antichambre', (2, 3))
            if cas == 'pauvre':
                m.joueur['or'] = 0
            x = web.choix(m, 'rembourser', 'brune')
            montant = 5 if cas == 'trop' else 2
            d = web.ComptesPublicsTests().clic(m, x, montant=montant)
            attendu, sorties, _ = web.ComptesPublicsTests().boucle(m.copier(), [d])
            r, lignes, captures, _ = await self.jouer(m, terminal.parcours(m, x, montant))
            self.assertIn(message, '\n'.join(sorties))
            self.assertIn(message, '\n'.join(lignes))
            self.assertEqual(captures, [d.contenu])
            self.assertEqual(terminal.sans_saisie(r.data), terminal.sans_saisie(attendu.data))
            self.assertEqual((r.joueur['or'], bourse(r, 'brune'), r.data['dettes'], emissions(r)),
                             (m.joueur['or'], bourse(m, 'brune'), m.data['dettes'], emissions(m)))
            self.assertEqual(terminal.vues(recharger(r)), terminal.vues(r))


class ConsoleRemboursementTests(ParcoursRemboursement, unittest.IsolatedAsyncioTestCase):
    interface = 'console'


@unittest.skipUnless(terminal.tui.TEXTUAL, 'Installer requirements-tui.txt')
class TuiRemboursementTests(ParcoursRemboursement, unittest.IsolatedAsyncioTestCase):
    interface = 'tui'
