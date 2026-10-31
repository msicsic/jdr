"""K0 : suggestion sans effet, formulaire réel, verdict et vue rechargés."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon import agendas
from donjon.accords_publics import accords_publics, AccordTerminal
from donjon.dialogues import preparer_direct
from donjon.esprits import lire, constater_possession
from donjon.monde import Monde, ErreurMonde
from donjon.rendu import fiche, regarder, decrire_comptes
from donjon.scene import scene_percue
from tests.test_accords_publics import situation
from tests.test_propositions import scene
from tests.test_tensions import placer, recharger
from tests.support import regarder as voir
from tests.test_outils_publics import page
from tests.test_inventaire_public import etat
from tests import test_information_publique as information_support
from tests import test_gestes_terminal as terminal_support
from tests.test_gestes_terminal import sans_saisie


def relais():
    m = scene('aubin')
    m.joueur['or'] = 50
    m.objets['planches']['lieu'] = 'aubin'
    constater_possession(m, 'joueur', 'planches', 'vu')
    placer(m, 'planches', 'antichambre', [2, 2])
    voir(m, 'joueur', 'planches')
    return recharger(m)


def huile_connue():
    m, _ = situation()
    # Corvus a vu le pot porté par Odile avant qu'elle le pose.
    lieu = m.objets['pot_huile']['lieu']
    m.objets['pot_huile']['lieu'] = 'odile'
    constater_possession(m, 'joueur', 'pot_huile', 'vu')
    m.objets['pot_huile']['lieu'] = lieu
    return recharger(m)


class CandidatsContratTests(unittest.TestCase):
    def vues(self, m):
        return fiche(m), regarder(m), decrire_comptes(m), scene_percue(m), accords_publics(m)

    def recharge(self, m):
        avant, vue = copy.deepcopy(m.data), self.vues(m)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual(self.vues(n), vue)
        return n

    def choix(self, m, objet, qui):
        a = accords_publics(m)
        i = next(i for i, x in enumerate(a['suggestions'])
                 if x['initial']['destinataire'] == qui
                 and (x['initial']['prestation'].get('objet')
                      or x['initial']['prestation']['condition']['objet']) == objet)
        return a, i

    def test_relais_et_huile_selection_web_console_accord_et_recharge(self):
        for m, objet, qui in ((relais(), 'planches', 'aubin'),
                              (huile_connue(), 'pot_huile', 'odile')):
            with self.subTest(objet=objet):
                a, i = self.choix(m, objet, qui)
                avant = copy.deepcopy(m.data)
                r = AccordTerminal(a)
                self.assertIn('Suggestions à discuter', r.rendre())
                self.assertIsNone(r.saisir(f'suggestion {i + 1}'))
                self.assertIsNone(r.etape)
                self.assertIn('sans limite négociée', r.rendre())
                d = r.saisir('valider')
                e = etat(m); e['sonde_suggestion'] = i
                clic = page(m, e)['suggestion']
                self.assertEqual((clic['avant'], clic['envois']), (0, 1))
                self.assertEqual(clic['envoye'], d.contenu)
                self.assertEqual(clic['champs']['Délai en minutes (0 = sans limite)'], '0')
                self.assertEqual(m.data, avant)
                # Le formulaire reste libre de négocier son prix avant l'aperçu.
                r = AccordTerminal(a, a['suggestions'][i]['initial'])
                r.saisir('corriger prix'); r.saisir('10')
                d = r.saisir('valider')
                web, lignes, _ = information_support.InformationPubliqueTests().boucle(m.copier(), [d, 'tenter'])
                console, sorties, _ = terminal_support.ConsoleTests().jouer_console(
                    m.copier(), ['accord', f'suggestion {i + 1}', 'corriger prix', '10', 'valider', 'tenter'])
                self.assertEqual(sans_saisie(web.data), sans_saisie(console.data))
                self.assertEqual(self.vues(web), self.vues(console))
                self.assertEqual(web.joueur['or'], 40)
                self.assertIn('accepte', '\n'.join(lignes))
                self.assertIn('Suggestions à discuter', '\n'.join(sorties))
                self.recharge(web)

    def test_tache_publique_moyens_doublon_et_recharge(self):
        m, _ = situation(True)
        a, i = self.choix(m, 'garde_manger', 'joss')
        sans_moyen = m.copier()
        sans_moyen.objets['cle_garde_manger']['lieu'] = 'dortoir'
        lire(sans_moyen, 'joss')['croyances'].pop('cle_garde_manger', None)
        self.assertNotIn(a['suggestions'][i], accords_publics(sans_moyen)['suggestions'])
        self.recharge(sans_moyen)
        avant = copy.deepcopy(m.data)
        r = AccordTerminal(a)
        r.saisir(f'suggestion {i + 1}')
        r.saisir('corriger prix'); r.saisir('10')
        d = r.saisir('valider')
        self.assertEqual(m.data, avant)
        n, lignes, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'tenter'])
        self.assertEqual(n.joueur['or'], 40)
        self.assertIn('accepte', '\n'.join(lignes))
        self.assertTrue(agendas.en_cours(n, 'joss', condition={'objet': 'garde_manger', 'verrouillee': True}))
        self.assertNotIn(a['suggestions'][i], accords_publics(n)['suggestions'])
        self.recharge(n)

    def test_determinisme_sans_besoins_secrets_ni_jet_ni_effet(self):
        m = relais()
        avant = copy.deepcopy(m.data)
        with patch('donjon.echanges.jet_persuasion', side_effect=AssertionError('Jet de négociation')):
            a = accords_publics(m)
            self.assertEqual(a, accords_publics(m))
        self.assertEqual(m.data, avant)
        for faim in (0, 99):
            n = m.copier()
            lire(n, 'aubin')['besoins']['faim'] = faim
            n.objets['aubin']['profil']['pulsions'] = []
            self.assertEqual(accords_publics(n)['suggestions'], a['suggestions'])
        self.recharge(m)

    def test_pas_de_possession_inconnue_et_references_publiques(self):
        m = huile_connue()
        m.data['noms_connus'].remove('odile')
        a = accords_publics(m)
        texte = json.dumps(a['suggestions'])
        self.assertNotIn('odile', texte)
        self.assertNotIn('briquet_odile', texte)
        sans_preuve = m.copier()
        lire(sans_preuve, 'joueur')['croyances'].pop('pot_huile', None)
        self.assertNotIn('pot_huile', json.dumps(accords_publics(sans_preuve)['suggestions']))
        self.recharge(sans_preuve)
        # Un bien déjà nommé mais désormais caché ne révèle pas sa possession.
        m.objets['pot_huile']['lieu'] = 'dortoir'
        self.assertNotIn('pot_huile', json.dumps(accords_publics(m)['suggestions']))
        self.recharge(m)

    def test_fonds_ressource_epuisee_droits_et_depart(self):
        for cause in ('fonds', 'epuise', 'propriete', 'depart'):
            m = relais()
            a, i = self.choix(m, 'planches', 'aubin')
            initial = a['suggestions'][i]['initial']
            if cause == 'fonds':
                m.joueur['or'] = 0
            elif cause == 'epuise':
                m.objets['planches']['charges'] = 0
            elif cause == 'propriete':
                m.objets['planches']['proprietaire'] = 'brune'
            else:
                placer(m, 'aubin', 'crypte', [2, 3])
            self.assertNotIn(initial, [s['initial'] for s in accords_publics(m)['suggestions']], cause)
            self.recharge(m)

    def test_brouillon_perime_revalide_et_refus_pnj_sans_paiement(self):
        m = relais()
        a, i = self.choix(m, 'planches', 'aubin')
        r = AccordTerminal(a, a['suggestions'][i]['initial'])
        d = r.saisir('valider')
        # L'existence d'une suggestion ne préjuge jamais le verdict social.
        lire(m, 'aubin')['relations']['joueur']['confiance'] = 0
        n, lignes, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'tenter'])
        self.assertEqual(n.joueur['or'], 50)
        self.assertIn('refuse', '\n'.join(lignes))
        self.recharge(n)
        m.joueur['or'] = 0
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as exc:
            preparer_direct(m, d)
        self.assertTrue(exc.exception.attendu)
        self.assertEqual(m.data, avant)
        self.recharge(m)

    def test_annuler_et_numero_inconnu_sans_effet(self):
        m = relais()
        a = accords_publics(m)
        avant = copy.deepcopy(m.data)
        r = AccordTerminal(a)
        with self.assertRaises(ValueError):
            r.saisir('suggestion 9999')
        r.saisir('suggestion 1'); r.saisir('annuler')
        self.assertTrue(r.terminee)
        self.assertEqual(m.data, avant)
        self.recharge(m)
