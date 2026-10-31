"""396 : mêmes comptes au web et dans les deux vrais terminaux, jusqu'à la recharge."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import jeu
from donjon.biens import comptes_joueur, rembourser
from donjon.commandes import DescripteurPublic
from donjon.comptes_terminal import ComptesTerminal
from donjon.dialogues import comptes_publics, preparer_direct
from donjon.emissions import lire as emissions
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer
from tests import test_comptes_publics as web
from tests import test_tui as tui
from tests.test_gestes_terminal import sans_saisie
from tests.test_messages_decoupage import vivre
from tests.test_parole_corrections import banc
from tests.test_tensions import recharger


def parcours(m, x):
    public = comptes_publics(m)
    numero = str(public['choix'].index(x) + 1)
    d = ComptesTerminal(public).saisir(numero)
    assert d.contenu == x['descripteur']
    return ['comptes', numero]


def vues(m):
    return fiche(m), regarder(m), scene_percue(m), comptes_joueur(m), emissions(m)


def perimer(m, d):
    p = d['parametres']
    if d['geste'] == 'remettre':
        m.data['permissions'] = []
    elif p['operation'] == 'payer':
        m.data['offres_joueur'][p['compte']['offre']]['demande']['montant'] += 1
    else:
        m.data['dettes'][0]['montant'] += 1


def scenes():
    m = banc('ressources')
    rembourser(m, 'aubin', 'joueur', 2, 'vivres')
    pret, objet, _ = web.emprunt()
    offre, _ = web.offre()
    return [(m, web.choix(m, 'reclamer', 'aubin')),
            (pret, web.choix(pret, 'restituer', objet)),
            (offre, web.choix(offre, 'payer', 'aubin'))]


class FormulaireComptesTests(unittest.TestCase):
    def test_projection_figee_publique_et_choix_sans_interpretation(self):
        m = banc('ressources')
        rembourser(m, 'aubin', 'brune', 937, 'vivres')
        rembourser(m, 'aubin', 'joueur', 851, 'vivres', informer=False)
        # Le remboursement du 388 est une parole typée, pas un raccourci public.
        rembourser(m, 'joueur', 'brune', 4, 'vivres')
        public = comptes_publics(m)
        f = ComptesTerminal(public)
        rendu = f.rendre()
        self.assertEqual(f.public['lignes'], comptes_joueur(m))
        self.assertNotIn('937', rendu)
        self.assertNotIn('851', rendu)
        self.assertIn('Tu dois 4 pièces', rendu)
        self.assertNotIn('rembourser', json.dumps(f.public['choix']))
        public['choix'].clear()
        public['lignes'].clear()
        self.assertEqual(f.rendre(), rendu)
        for texte in ('', '0', '-1', '1 2', '1,2', 'aubin', '9' * 5000):
            with self.assertRaises(ValueError):
                f.saisir(texte)
            self.assertFalse(f.terminee)
        self.assertEqual(f.saisir('01').contenu, f.public['choix'][0]['descripteur'])
        with self.assertRaises(ValueError):
            f.saisir('1')
        vide = ComptesTerminal({'lignes': [], 'choix': []})
        self.assertIn('Aucun geste comptable', vide.rendre())
        self.assertIsNone(vide.saisir('annuler'))
        with self.assertRaises(ValueError):
            vide.saisir('1')

    def test_homonymes_et_termes_exactement_ceux_du_web(self):
        m, objet, autre = web.emprunt()
        public = comptes_publics(m)
        f = ComptesTerminal(public)
        restitutions = [x for x in public['choix'] if x['descripteur']['geste'] == 'remettre']
        self.assertEqual({x['descripteur']['cible'] for x in restitutions}, {objet, autre})
        for x in restitutions:
            d = x['descripteur']
            self.assertIn('[' + d['cible'] + ', ' + d['parametres']['destinataire'] + ']', f.rendre())
        for m, x in scenes():
            avant = copy.deepcopy(m.data)
            self.assertEqual(ComptesTerminal(comptes_publics(m)).saisir(parcours(m, x)[-1]),
                             web.ComptesPublicsTests().clic(m, x))
            self.assertEqual(m.data, avant)


class ParcoursComptes:
    async def jouer(self, m, entrees, *, mutation=None, reception=False):
        """Vraie boucle et pilote Textual ; contrôle aussi la voie locale des prêts."""
        installer(m)  # Même perception initiale que l'ouverture réelle du jeu.
        attente = m.copier()
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / 'copie.json'
            m.sauver(fichier)
            faux = MagicMock(connexion='api', erreur_auth=None)
            faux.echanger.side_effect = AssertionError('Appel au modèle')
            faux.raconter_resultat.side_effect = AssertionError('Récit au modèle')
            lignes, captures, vivant, publications = [], [], [], []
            preparer = Moteur.preparer

            def capturer(monde, d):
                vivant[:] = [monde]
                if not captures:
                    captures.append(copy.deepcopy(d.contenu))
                    if reception:
                        mutation(monde)
                        mutation(attente)
                self.assertEqual(d.contenu, captures[0])

            def parole(monde, d):
                capturer(monde, d)
                return preparer_direct(monde, d)

            def local(moteur, d, *args, **kwargs):
                if isinstance(d, DescripteurPublic):
                    capturer(moteur.monde, d)
                return preparer(moteur, d, *args, **kwargs)

            def verifier(texte):
                if vivant and vivant[0].data.get('conversation'):
                    dernier = vivant[0].data['conversation'][-1]
                    if texte.strip() == dernier['reponse'].strip():
                        recharge = Monde.charger(fichier)
                        self.assertEqual(recharge.data, json.loads(json.dumps(vivant[0].data)))
                        self.assertEqual(vues(recharge), vues(vivant[0]))
                        publications.append(texte)
                        if dernier['nature'] == 'proposition_non_executee':
                            self.assertEqual(sans_saisie(recharge.data) | {'conversation': []},
                                             sans_saisie(attente.data) | {'conversation': []})

            def avant_saisie(texte):
                if texte == 'tenter' and mutation and not reception:
                    mutation(vivant[0])
                    mutation(attente)

            with (patch('jeu.MJ', return_value=faux),
                  patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                  patch('jeu.analyser', side_effect=AssertionError('Analyse du choix')),
                  patch('donjon.paroles.analyser', side_effect=AssertionError('Analyse de parole')),
                  patch('donjon.dialogues.preparer_direct', side_effect=parole),
                  patch.object(Moteur, 'preparer', local),
                  patch.object(Monde, 'd20', return_value=20)):
                if self.interface == 'console':
                    saisies = iter([*entrees, 'quitter'])

                    def lire(*_):
                        texte = next(saisies)
                        avant_saisie(texte)
                        return texte

                    def ecrire(*args, **_):
                        texte = ' '.join(map(str, args))
                        lignes.append(texte)
                        verifier(texte)

                    with patch('builtins.input', side_effect=lire), patch('builtins.print', side_effect=ecrire):
                        self.assertEqual(jeu.main(['--console', '--connexion', 'api', '--save', str(fichier)]), 0)
                    self.assertIn('comptes. Consulter', '\n'.join(lignes))
                else:
                    from donjon.tui import SeuilApp
                    from textual.widgets import Input, Static
                    app = SeuilApp(['--connexion', 'api', '--save', str(fichier)])
                    ecrire_app = app.ecrire

                    def ecrire(texte):
                        verifier(texte)
                        ecrire_app(texte)

                    app.ecrire = ecrire
                    async with app.run_test(size=(120, 40)) as pilot:
                        support = tui.TUITests()
                        await support.pret(app)
                        await pilot.press('f7')
                        self.assertEqual(app.derniere_vue['comptes'], comptes_publics(m))
                        for texte in entrees:
                            avant_saisie(texte)
                            vue = app.derniere_vue
                            app.query_one('#commande', Input).value = texte
                            await pilot.press('enter')
                            if app.recette is not None:
                                self.assertIs(app.derniere_vue, vue)
                                self.assertEqual(str(app.query_one('#gestes', Static).render()), app.recette.rendre())
                                self.assertTrue(app.pont.commandes.empty())
                                self.assertFalse(app.occupe)
                                self.assertEqual(Monde.charger(fichier).data, m.data)
                                await pilot.press('ctrl+right', 'shift+left')
                                self.assertTrue(app.pont.commandes.empty())
                            elif app.occupe:
                                await support.attendre(lambda: app.derniere_vue is not vue and not app.occupe,
                                                       lambda: repr(app.sorties[-5:]))
                        lignes = list(app.sorties)
                        vue = app.derniere_vue
                        await support.fermer(app)
                        self.assertEqual(vue['fiche'], fiche(Monde.charger(fichier)))
                        self.assertEqual(vue['scene'], regarder(Monde.charger(fichier)))
            faux.echanger.assert_not_called()
            faux.raconter_resultat.assert_not_called()
            return Monde.charger(fichier), lignes, captures, publications

    async def comparer(self, m, x, *, annuler=False, perime=None, laps=False):
        installer(m)
        suite = [] if perime == 'reception' else ['annuler' if annuler else 'tenter']
        entrees = [*parcours(m, x), *suite]
        d = web.ComptesPublicsTests().clic(m, x)
        mutation = (lambda monde: perimer(monde, d.contenu)) if perime else None
        if perime == 'reception':
            # Le choix public est figé avant la mutation pour les deux transports.
            original = Moteur.preparer

            def parole(monde, descripteur):
                mutation(monde)
                return preparer_direct(monde, descripteur)

            def local(moteur, descripteur, *args, **kwargs):
                if isinstance(descripteur, DescripteurPublic):
                    mutation(moteur.monde)
                return original(moteur, descripteur, *args, **kwargs)

            with patch('donjon.dialogues.preparer_direct', side_effect=parole), patch.object(Moteur, 'preparer', local):
                attendu, _, _ = web.ComptesPublicsTests().boucle(m.copier(), [d, *suite])
        else:
            attendu, _, _ = web.ComptesPublicsTests().boucle(m.copier(), [d, *suite], mutation=mutation)
        obtenu, lignes, captures, publications = await self.jouer(m, entrees, mutation=mutation,
                                                                 reception=perime == 'reception')
        self.assertEqual(captures, [d.contenu])
        self.assertEqual(sans_saisie(obtenu.data), sans_saisie(attendu.data))
        self.assertEqual(recharger(obtenu).data, obtenu.data)
        self.assertEqual(vues(obtenu), vues(attendu))
        if not perime:
            self.assertTrue(publications)
            self.assertIn('Compris :', '\n'.join(lignes))
        if annuler or perime:
            self.assertEqual(obtenu.joueur['or'], m.joueur['or'])
            self.assertEqual(obtenu.objets, m.objets)
            self.assertEqual(emissions(obtenu), emissions(m))
        if perime:
            self.assertIn('Ce choix de compte a changé', '\n'.join(lignes))
        if laps:
            entier, _ = vivre(obtenu.copier(), [60])
            decoupe, _ = vivre(obtenu.copier(), [13, 29, 18])
            for etat in (entier, decoupe):
                self.assertEqual(recharger(etat).data, etat.data)
                self.assertEqual(vues(recharger(etat)), vues(etat))
            for k in ('dettes', 'permissions', 'finances_pnj'):
                self.assertEqual(entier.data.get(k), decoupe.data.get(k), k)
            self.assertEqual(entier.joueur['or'], decoupe.joueur['or'])
            self.assertEqual(comptes_joueur(entier), comptes_joueur(decoupe))
        print('MESURE_UT_396=' + json.dumps({'interface': self.interface, 'descripteur': d.contenu,
            'annule': annuler, 'perime': perime, 'saisies': entrees,
            'touches_jusqua_verdict': sum(len(x) + 1 for x in entrees),
            'touches_avec_f7': sum(len(x) + 1 for x in entrees) + (self.interface == 'tui'),
            'appels_modele': 0}, ensure_ascii=False))
        return obtenu, lignes

    async def test_creances_deux_personnes_verdict_et_questions(self):
        for qui, montant, paye in (('aubin', 2, True), ('brune', 3, False)):
            m = banc('ressources')
            rembourser(m, qui, 'joueur', montant, 'vivres')
            r, _ = await self.comparer(m, web.choix(m, 'reclamer', qui), laps=True)
            self.assertEqual(r.joueur['or'], m.joueur['or'] + (montant if paye else 0))
            self.assertEqual(bool(r.data['dettes']), not paye)
            self.assertEqual(f'te doit {montant} pièces' in fiche(r), not paye)
        for montant in (0, 2):
            m = banc('ressources')
            if montant:
                rembourser(m, 'aubin', 'joueur', montant, 'vivres')
            r, _ = await self.comparer(m, web.choix(m, 'question', 'aubin'))
            self.assertEqual(r.joueur['or'], m.joueur['or'] + montant)
            self.assertFalse(r.data.get('dettes'))

    async def test_prets_homonymes_restitues_separement(self):
        for second in (False, True):
            m, objet, autre = web.emprunt()
            if second:
                objet, autre = autre, objet
            r, lignes = await self.comparer(m, web.choix(m, 'restituer', objet), laps=True)
            self.assertIn('Tu restitues', '\n'.join(lignes))
            self.assertEqual(r.objets[objet]['lieu'], 'marchand')
            self.assertEqual(r.objets[autre]['lieu'], 'joueur')
            self.assertEqual([p['objet'] for p in r.data['permissions']], [autre])
            self.assertEqual(r.joueur['or'], m.joueur['or'])

    async def test_offres_deux_prix_et_refus_sans_argent(self):
        for qui, prix, argent in (('aubin', 2, True), ('brune', 3, True), ('aubin', 2, False)):
            m, objet = web.offre(qui, prix)
            if not argent:
                m.joueur['or'] = 0
            r, _ = await self.comparer(m, web.choix(m, 'payer', qui), laps=argent)
            self.assertEqual(r.joueur['or'], m.joueur['or'] - (prix if argent else 0))
            self.assertEqual(r.objets[objet]['lieu'], 'joueur' if argent else qui)
            self.assertEqual(r.data['offres_joueur']['marche_test']['statut'], 'accepte' if argent else 'pauvre')

    async def test_annulations_et_comptes_perimes_avant_et_apres_apercu(self):
        m = banc('ressources')
        r, _, captures, _ = await self.jouer(m, ['comptes', '0', '1 2', 'aubin', 'annuler'])
        self.assertEqual(captures, [])
        self.assertEqual(r.data, m.data)
        for m, x in scenes():
            await self.comparer(m.copier(), x, annuler=True)
            for instant in ('reception', 'confirmation'):
                await self.comparer(m.copier(), x, perime=instant)


class ConsoleComptesTests(ParcoursComptes, unittest.IsolatedAsyncioTestCase):
    interface = 'console'


@unittest.skipUnless(tui.TEXTUAL, 'Installer requirements-tui.txt')
class TuiComptesTests(ParcoursComptes, unittest.IsolatedAsyncioTestCase):
    interface = 'tui'
