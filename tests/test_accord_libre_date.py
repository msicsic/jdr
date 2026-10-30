"""E6 reprise : aucun accord depuis le libre ; formulaire E5 puis U-C."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from donjon import agendas
from donjon.accords_libres import ouvrir, REFUS, secondes_ecrites
from donjon.accords_publics import AccordTerminal
from donjon.consentement import preparer
from donjon.emissions import pnj
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import regarder, decrire_comptes
from donjon.scene import scene_percue
from donjon.temps import ecouler
from donjon.transactions import ajouter
from tests.test_accords_publics import situation
from tests.test_audits_attendu import jouer
from tests.test_tensions import recharger
from tests import test_information_publique as information_support
from tests.test_gestes_terminal import sans_saisie
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page


def phrase(d):
    return ('Odile, je te paie trois pièces si tu me livres une part d’huile dans dix minutes'
            if d.contenu['cible'] == 'odile' else
            'Joss, je te paie dix pièces si tu verrouilles le garde-manger dans dix minutes')


def interpretation(m, d, saisie=None):
    p = d.contenu['parametres']
    return {'mode': 'accord', 'texte': '', 'faits': [], 'proposition': {
        'destinataire': d.contenu['cible'], 'prestation': copy.deepcopy(p['prestation']),
        'prix': p['prix'], 'duree_ecrite': 'dans dix minutes', 'obstacle': ''}}


class AccordLibreDateTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual((regarder(n), decrire_comptes(n), scene_percue(n), pnj(n)),
                         (regarder(m), decrire_comptes(m), scene_percue(m), pnj(m)))
        return n

    def test_libre_formulaire_et_direct_memes_accords_comptes_paroles_recharges(self):
        for tache in (False, True):
            with self.subTest(tache=tache):
                m, d = situation(tache)
                n, texte, appels = jouer(m.copier(), phrase(d), [interpretation(m, d)], [], suite=('valider', 'tenter'))
                direct, _, _ = information_support.InformationPubliqueTests().boucle(m.copier(), [d, 'tenter'])
                self.assertEqual(sans_saisie(n.data), sans_saisie(direct.data))
                self.assertEqual(pnj(n), pnj(direct))
                self.assertEqual(n.joueur['or'], 50 - d.contenu['parametres']['prix'])
                x, = agendas.en_cours(n, d.contenu['cible'])
                self.assertEqual(agendas.reference_temporelle(x)['limite'], 6000)
                self.assertIn('minute de jeu 10', texte)
                self.assertIn('rien n’a été dit ni engagé', texte)
                self.assertEqual([f for f, _ in appels], ['repondre_au_joueur'])
                self.recharge(n)

    def test_annuler_formulaire_et_consentement_sans_effet(self):
        for tache in (False, True):
            for suite in (('annuler',), ('valider', 'annuler')):
                m, d = situation(tache)
                n, texte, _ = jouer(m, phrase(d), [interpretation(m, d)], [], suite=suite)
                self.assertEqual(n.joueur['or'], 50)
                self.assertFalse(agendas.en_cours(n, d.contenu['cible']))
                self.assertEqual(pnj(n), pnj(m))
                self.assertEqual(n.objets, m.objets)
                self.assertNotIn('D’accord', texte)
                self.recharge(n)

    def test_demain_ou_nombre_invente_laisse_limite_vide_jusquau_choix(self):
        for tache in (False, True):
            for fragment in ('demain', '86400 secondes', ''):
                m, d = situation(tache)
                s = phrase(d).replace('dans dix minutes', 'demain')
                r = interpretation(m, d); r['proposition']['duree_ecrite'] = fragment
                b = ouvrir(m, r['proposition'], s)['_formulaire_accord']
                self.assertNotIn('limite', b['initial'])
                recette = AccordTerminal(b['public'], b['initial'])
                self.assertEqual(recette.etape, 'delai')
                self.assertNotIn('1440', recette.rendre())
                n, texte, _ = jouer(m, s, [r], [], suite=('10', 'valider', 'tenter'))
                self.assertIn('minute de jeu 10', texte)
                self.assertEqual(n.joueur['or'], 50 - d.contenu['parametres']['prix'])
                self.recharge(n)

    def test_clauses_non_portees_refus_moteur_sans_parole_ni_formulaire(self):
        for tache in (False, True):
            for cause, raison in REFUS.items():
                m, d = situation(tache)
                r = interpretation(m, d); r['proposition']['obstacle'] = cause
                n, texte, appels = jouer(m, phrase(d), [r], [])
                self.assertIn(raison, texte)
                self.assertNotIn('D’accord', texte)
                self.assertNotIn('Tu dis', texte)
                self.assertEqual(n.joueur['or'], 50)
                self.assertEqual(n.objets, m.objets)
                self.assertEqual(pnj(n), pnj(m))
                self.assertEqual(len(appels), 1)
                self.recharge(n)

    def test_prefill_admissible_seulement_et_duree_figee_sans_effet(self):
        for tache in (False, True):
            m, d = situation(tache)
            ecouler(m, 123)
            r = interpretation(m, d)
            avant = copy.deepcopy(m.data)
            b = ouvrir(m, r['proposition'], phrase(d))['_formulaire_accord']
            self.assertEqual(b['initial']['limite'], 6123)
            self.assertEqual(m.data, avant)
            recette = AccordTerminal(b['public'], b['initial'])
            ecouler(m, 100)
            choix = recette.saisir('valider')
            self.assertEqual(choix.contenu['parametres']['limite'], 6123)
            p = r['proposition']; p.update(destinataire='secret', prestation={'type': 'part', 'objet': 'secret'}, prix=99)
            b = ouvrir(m, p, phrase(d))['_formulaire_accord']
            for k in ('destinataire', 'prestation', 'prix'):
                self.assertNotIn(k, b['initial'])
            self.recharge(m)

    def test_ancienne_compilation_datee_ne_peut_plus_executer_ni_rejouer(self):
        from donjon.accords_publics import parole_accord
        for tache in (False, True):
            m, d = situation(tache)
            p = parole_accord(m, d.contenu)
            p.pop('_adresse', None)
            p['_intention'] = phrase(d)
            r = {'mode': 'dialogue', 'texte': '', 'faits': [], 'proposition': None}
            ajouter(r, 'parole', m.data['revision'], p)
            avant = copy.deepcopy(m.data)
            with self.assertRaises(ErreurMonde) as exc:
                preparer(m, r, 'LLM')
            self.assertTrue(exc.exception.attendu)
            self.assertEqual(m.data, avant)
            mj = MJOpenAI('gpt-6-luna', connexion='chatgpt')
            rep = mj._echanger_prepare(m, phrase(d), reponse={'mode': 'parole_joueur', 'proposition': p})
            self.assertIn('_formulaire_accord', rep)
            self.assertNotIn('_transactions', rep)
            self.assertNotIn('limite', rep['_formulaire_accord']['initial'])
            self.recharge(m)

    def test_grammaire_durees_explicites_et_inconnues(self):
        for fragment, n in (('dans dix minutes', 600), ('avant 3 heures', 10800),
                            ('vingt et une minutes', 1260), ('2 minutes 30 secondes', 150),
                            ('une heure', 3600), ('demain', None), ('minuit', None), ('trois jours', None)):
            self.assertEqual(secondes_ecrites(fragment, 'Prestation ' + fragment), n)
        self.assertIsNone(secondes_ecrites('86400 secondes', 'Prestation demain'))

    def test_schema_brouillon_ne_transporte_aucun_instant_calcule(self):
        from donjon.accords_libres import SCHEMA
        def verifier(x):
            if isinstance(x, dict):
                self.assertFalse({'limite', 'echeance'} & set(x.get('properties', {})))
                for v in x.values():
                    verifier(v)
            elif isinstance(x, list):
                for v in x:
                    verifier(v)
        verifier(SCHEMA)

    def test_page_web_ouvre_prefill_corrige_valide_et_annule(self):
        for tache in (False, True):
            m, d = situation(tache)
            b = ouvrir(m, interpretation(m, d)['proposition'], phrase(d))['_formulaire_accord']
            e = etat(m); e['brouillon_accord'] = b
            e['sonde_accord_libre'] = True
            r = page(m, e)['accord_libre']
            self.assertFalse(r['cache'])
            self.assertEqual(r['envois_avant'], 0)
            self.assertEqual(r['champs']['Délai en minutes (0 = sans limite)'], '10')
            self.assertEqual(r['envoye'], d.contenu)
            self.assertEqual(r['envois_apres_annuler'], 1)


class AccordLibreTerminalTests(unittest.IsolatedAsyncioTestCase):
    async def test_tui_ouvre_formulaire_et_valide_sans_nouvel_appel(self):
        from donjon.tui import SeuilApp
        from textual.widgets import Input
        from tests.test_gestes_terminal import TerminalTests
        for tache in (False, True):
            m, d = situation(tache)
            with tempfile.TemporaryDirectory() as tmp:
                f = Path(tmp) / 'partie.json'; m.sauver(f)
                faux = MagicMock(connexion='api', erreur_auth=None)
                faux.echanger.return_value = ouvrir(m, interpretation(m, d)['proposition'], phrase(d))
                with patch('jeu.MJ', return_value=faux), patch.object(Monde, 'd20', return_value=20):
                    app = SeuilApp(['--connexion', 'api', '--save', str(f)])
                    async with app.run_test(size=(120, 40)) as pilot:
                        support = TerminalTests(); await support.pret(app)
                        app.query_one('#commande', Input).value = phrase(d)
                        await pilot.press('enter')
                        await support.attendre(lambda: app.recette is not None and not app.occupe,
                                               lambda: repr(app.sorties[-5:]))
                        self.assertEqual(Monde.charger(f).joueur['or'], 50)
                        self.assertIn('minute de jeu 10', app.recette.rendre())
                        vue = app.derniere_vue
                        app.query_one('#commande', Input).value = 'valider'
                        await pilot.press('enter')
                        await support.attendre(lambda: app.derniere_vue is not vue and not app.occupe,
                                               lambda: repr(app.sorties[-5:]))
                        vue = app.derniere_vue
                        app.query_one('#commande', Input).value = 'tenter'
                        await pilot.press('enter')
                        await support.attendre(lambda: app.derniere_vue is not vue and not app.occupe,
                                               lambda: repr(app.sorties[-5:]))
                        await support.fermer(app)
                self.assertEqual(faux.echanger.call_count, 1)
                self.assertEqual(Monde.charger(f).joueur['or'], 50 - d.contenu['parametres']['prix'])
