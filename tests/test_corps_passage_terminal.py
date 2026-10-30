"""U-T corps/passage : vraies saisies, callbacks web et vues rechargées."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from donjon import corps, defense, gestes_publics as catalogue
from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.gestes_publics import GESTES_CORPS, GESTES_PASSAGE, REACTIONS, gestes_du_monde, rendre_liste
from donjon.monde import ErreurMonde, Monde, objet
from donjon.moteur import Moteur
from donjon.noms import reference
from tests import test_corps_publics as web_corps
from tests import test_gestes_terminal as terminal
from tests import test_passages_publics as web_passage
from tests.test_descripteur_public import vues
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tools.banc_parties import preparer


def numero(m, d):
    return next(str(i) for i, c in enumerate(gestes_du_monde(m), 1) if c.descripteur == d)


def corporels(m):
    return [c.descripteur.contenu for c in gestes_du_monde(m)
            if c.descripteur.contenu['geste'] in GESTES_CORPS
            and c.descripteur.contenu['cible'] in
            {reference(m, i) for i, o in m.objets.items() if o['type'] == 'personnage'}]


@unittest.skipUnless(shutil.which('node'), 'Node requis pour les callbacks réels')
class ProjectionTests(unittest.TestCase):
    def test_tous_les_passages_des_deux_scenes_et_des_paliers_identiques_au_web(self):
        mondes = [web_passage.normaliser(web_passage.scene(s, c)) for s, c in
                  (('relais', 'poutre_conduite'), ('auberge', 'table_longue'))]
        mondes += [web_passage.atelier(echelle=True, haut=h) for h in (False, True)]
        mondes += [web_passage.atelier(porte=p) for p in (False, True)]
        for m in mondes:
            attendus = [c['envoye'] for c in page(m)['envoisClic'] if c['envoye']['geste'] in GESTES_PASSAGE]
            obtenus = [c.descripteur.contenu for c in gestes_du_monde(m) if c.descripteur.contenu['geste'] in GESTES_PASSAGE]
            self.assertTrue(attendus)
            self.assertCountEqual(obtenus, attendus)

    def test_catalogue_complet_deux_scenes_memes_descripteurs_que_le_web(self):
        for variante in (0, 1):
            m, cible, _ = web_corps.monde_geste('riposter', variante)
            attendu = [c['envoye'] for c in page(m)['corps']]
            self.assertCountEqual(corporels(m), attendu)
            self.assertEqual({c['geste'] for c in attendu}, GESTES_CORPS)
            liste = gestes_du_monde(m)
            self.assertEqual(len(liste), len({c.libelle for c in liste}))
            self.assertIn('(2/2)', rendre_liste(liste))
            self.assertNotIn('[personne_', rendre_liste(liste))
            # Un formulaire modifié doit piloter les deux interfaces immédiatement.
            f = [{'geste': 'frapper', 'libelle': 'Geste du catalogue', 'champs': [
                {'champ': 'methode', 'libelle': 'Méthode', 'type': 'choix', 'choix': ['simple']}]}]
            with patch.object(catalogue, 'formulaires_corps', return_value=f):
                self.assertCountEqual(corporels(m), [c['envoye'] for c in page(m)['corps']])
                self.assertTrue(any(c.libelle.startswith('Geste du catalogue') for c in gestes_du_monde(m)))

    def test_danger_ressources_privees_et_forme_inconnue_ne_sont_pas_inventes(self):
        m, cible, _ = web_corps.monde_geste('frapper')
        self.assertFalse([d for d in corporels(m) if d['geste'] in REACTIONS])
        for id, lieu in (('prive', cible), ('secret', 'reserve')):
            m.objets[id] = objet(id, 'moyen caché', 'outil', lieu, usages=['lien'])
        e = etat(m)
        self.assertCountEqual(corporels(m), [c['envoye'] for c in page(m, e)['corps']])
        self.assertFalse(any(d.get('parametres', {}).get('outil') in ('prive', 'secret') for d in corporels(m)))
        defense.noter_coup(m, cible, 'joueur', True)
        self.assertTrue([d for d in corporels(m) if d['geste'] in REACTIONS])
        web_corps.placer(m.objets[cible], 'reserve', [1, 1])
        self.assertFalse([d for d in corporels(m) if d['geste'] in REACTIONS])
        m = web_passage.atelier(memorise=False)
        self.assertFalse([c for c in gestes_du_monde(m) if c.descripteur.contenu['geste'] == 'franchir_obstacle'])
        m = web_passage.normaliser(web_passage.scene())
        m.objets['poutre_conduite'].pop('passage')
        self.assertFalse([c for c in gestes_du_monde(m) if c.descripteur.contenu['geste'] in GESTES_PASSAGE])


class Parcours:
    async def jouer(self, m, d, suite=None, mutation=None, invalides=False):
        liste, n = gestes_du_monde(m), numero(m, d)
        temoin = m.copier()
        if mutation:
            mutation(temoin)
        try:
            plan = Moteur(temoin).preparer(d)
        except ErreurMonde as exc:
            refus, plan = str(exc), None
        else:
            refus = None
        if suite is None:
            suite = ['tenter'] if plan and (plan.confirmation or plan.stat) else []
        preparer_moteur = Moteur.preparer
        reception = []

        def preparation_temoin(moteur, p, *args, **kw):
            if isinstance(p, DescripteurPublic) and not reception:
                if mutation:
                    mutation(moteur.monde)
                reception.append(p)
            return preparer_moteur(moteur, p, *args, **kw)

        # Même instant de mutation : après la vue initiale et juste à réception,
        # afin de comparer aussi les souvenirs perceptifs, sans les écarter.
        with patch.object(Moteur, 'preparer', preparation_temoin):
            attendu, textes, _ = web_corps.CorpsPublicsTests().boucle(m.copier(), [d, *suite])
        plans, soumis = [], []

        def preparation(moteur, p, *args, **kw):
            direct = isinstance(p, DescripteurPublic)
            if direct:
                self.assertEqual(p, d)
                if not soumis and mutation:
                    mutation(moteur.monde)
                soumis.append(copy.deepcopy(p))
            resultat = preparer_moteur(moteur, p, *args, **kw)
            if direct:
                plans.append(copy.deepcopy(resultat.__dict__))
            return resultat

        with patch.object(Moteur, 'preparer', preparation):
            if self.interface == 'console':
                obtenu, lignes, menus = terminal.ConsoleTests().jouer_console(
                    m, [*(['99999', '1 2'] if invalides else []), n, *suite])
                self.assertEqual(menus[0], rendre_liste(liste))
            else:
                obtenu, lignes = await self.tui(m, liste, n, suite, invalides)
        self.assertTrue(soumis)
        self.assertEqual(terminal.sans_saisie(obtenu.data), terminal.sans_saisie(attendu.data))
        self.assertEqual(vues(obtenu), vues(attendu))
        self.assertEqual(etat(obtenu), etat(attendu))
        self.assertEqual(vues(obtenu), vues(Monde(copy.deepcopy(obtenu.data))))
        if plan:
            self.assertEqual(plans[0], plan.__dict__)
        else:
            self.assertIn(refus, lignes)
            self.assertFalse(plans)
        # Le témoin ferme avec « quitter » ; la TUI est encore ouverte ici.
        # Comparer les sorties affichées, y compris aperçu et annulation, et
        # non les traces de conversation dont le cadrage peut être différent.
        self.assertEqual(textes[-1], 'Partie sauvegardée. A bientôt.')
        for texte in textes[:-1]:
            self.assertIn(texte.strip(), [ligne.strip() for ligne in lignes])
        if invalides:
            self.assertIn('Numéro inconnu dans la liste affichée.', lignes)
            self.assertIn('Choix ambigu : saisis un seul numéro de la liste affichée.', lignes)
        return obtenu, {'interface': self.interface, 'descripteur': d.contenu, 'numero': n,
            'touches_depuis_liste': len(n) + 1 + sum(len(s) + 1 for s in suite),
            'touches_avec_f7': len(n) + 2 + sum(len(s) + 1 for s in suite), 'appels_modele': 0}

    async def tui(self, m, liste, n, suite, invalides):
        from donjon.tui import PontTerminal
        from textual.widgets import Input, TabbedContent
        aide = terminal.TerminalTests()
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / 'copie.json'
            m.sauver(fichier)
            mj = MagicMock(connexion='api', erreur_auth=None)
            mj.echanger.side_effect = AssertionError('Appel au modèle')
            ecrire = PontTerminal.ecrire

            def publication(pont, *args, **kw):
                texte = ' '.join(map(str, args))
                sauvegarde = Monde.charger(fichier)
                if sauvegarde.data['conversation'] and texte.strip() == sauvegarde.data['conversation'][-1]['reponse'].strip():
                    publications.append(texte)
                ecrire(pont, *args, **kw)

            publications = []
            with (patch('jeu.MJ', return_value=mj), patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                  patch('jeu.analyser', side_effect=AssertionError('Analyse de texte')),
                  patch.object(Monde, 'd20', return_value=20), patch.object(PontTerminal, 'ecrire', publication)):
                app = terminal.tui.SeuilApp(['--connexion', 'api', '--save', str(fichier)])
                async with app.run_test(size=(120, 40)) as pilot:
                    await aide.pret(app)
                    self.assertEqual(app.derniere_vue['gestes'], liste)
                    await pilot.press('f7')
                    self.assertEqual(app.query_one('#etat', TabbedContent).active, 'onglet-gestes')
                    self.assertEqual(str(app.query_one('#gestes').render()), rendre_liste(liste))
                    if invalides:
                        for texte in ('99999', '1 2'):
                            app.query_one('#commande', Input).value = texte
                            await pilot.press('enter')
                            self.assertTrue(app.pont.commandes.empty())
                        self.assertEqual(Monde.charger(fichier).data, m.data)
                    for texte in ([n, *suite] if n is not None else []):
                        ancien = app.derniere_vue
                        app.query_one('#commande', Input).value = ''
                        await pilot.press(*texte, 'enter')
                        await aide.attendre(lambda: app.derniere_vue is not ancien and not app.occupe,
                                            lambda: repr(app.sorties[-5:]))
                    vue, lignes = app.derniere_vue, list(app.sorties)
                    await aide.fermer(app)
            mj.echanger.assert_not_called()
            mj.raconter_resultat.assert_not_called()
            obtenu = Monde.charger(fichier)
            self.assertEqual((vue['carte'], vue['fiche'], vue['scene']), vues(obtenu)[1:])
            if obtenu.data['conversation']:
                self.assertTrue(publications)
            return obtenu, lignes

    async def test_corps_tous_les_gestes_methodes_armes_et_deux_scenes(self):
        mesures = []
        variantes = [(g, {}) for g in sorted(GESTES_CORPS)] + [
            ('frapper', {'methode': 'assommer', 'outil': ''}),
            ('frapper', {'methode': 'simple', 'outil': 'moyen_deux'})]
        for i, (variante, geste, p) in enumerate((v, g, p) for v in (0, 1) for g, p in variantes):
            if geste == 'ligoter':
                p = {'outil': 'moyen_deux'}
            elif geste in ('trainer', 'pousser'):
                p = {'direction': 'est'}
            elif geste in ('delier', 'tuer', 'riposter') or geste == 'frapper' and not p:
                p = {'outil': '', **({'methode': 'simple'} if geste == 'frapper' else {})}
            with self.subTest(variante=variante, geste=geste, p=p):
                m, cible, autre = web_corps.monde_geste(geste, variante)
                d = DescripteurPublic(web_corps.clic(m, cible, geste, p)['envoye'])
                self.assertEqual(proposition_descripteur(m, d), analyser(m, web_corps.commande(geste, reference(m, cible), p)))
                obtenu, mesure = await self.jouer(m, d, invalides=i == 0)
                mesure['variante'] = variante
                mesures.append(mesure)
                self.assertTrue(obtenu.data['journal'])
                if geste == 'frapper':
                    self.assertLess(corps.pv(obtenu, cible), corps.pv(m, cible))
                    self.assertEqual(corps.pv(obtenu, autre), corps.pv(m, autre))
                elif geste == 'ligoter':
                    self.assertEqual(corps.corps(obtenu, cible)['lie']['lien'], 'moyen_deux')
        print('MESURES_UT_353=' + json.dumps(mesures, ensure_ascii=False))

    async def test_passages_reels_dessous_dessus_trop_bas_encombre_et_inconnu(self):
        mesures = []
        for script in sorted((Path(__file__).parent / 'data/bancs').glob('sous-obstacle-*.json')):
            with self.subTest(script=script.name), tempfile.TemporaryDirectory() as tmp:
                fichier = Path(tmp) / 'scene.json'
                preparer(json.loads(script.read_text(encoding='utf-8')), fichier)
                m = web_passage.normaliser(Monde.charger(fichier))
                cible = 'poutre_conduite' if 'poutre_conduite' in m.objets else 'table_longue'
                if 'enjamber' in script.name:
                    cible = next(i for i, o in m.objets.items() if 'lit à rideaux' in o['nom'])
                if 'inconnu' in script.name:
                    self.assertFalse([c for c in gestes_du_monde(m) if c.descripteur.contenu['geste'] in GESTES_PASSAGE])
                    # La vraie interface affiche cette absence, sans effet.
                    if self.interface == 'console':
                        a, _, menus = terminal.ConsoleTests().jouer_console(m, [])
                        self.assertEqual(menus[0], rendre_liste(gestes_du_monde(m)))
                    else:
                        a, _ = await self.tui(m, gestes_du_monde(m), None, [], False)
                    self.assertEqual(a.data, m.data)
                    continue
                methode = 'dessus' if any(s in script.name for s in ('trop-haut', 'enjamber')) else 'dessous'
                d = DescripteurPublic(web_passage.clic(m, cible, 'passer_obstacle', methode=methode)['envoye'])
                _, mesure = await self.jouer(m, d)
                mesures.append(mesure)
        print('MESURES_UT_353=' + json.dumps(mesures, ensure_ascii=False))

    async def test_echelles_deux_sens_et_perches_portees_ou_au_sol(self):
        mesures = []
        for haut in (False, True):
            m = web_passage.atelier(echelle=True, haut=haut)
            d = DescripteurPublic(web_passage.clic(m, 'echelle_test', 'franchir')['envoye'])
            self.assertEqual(proposition_descripteur(m, d), analyser(m, ('descendre ' if haut else 'monter ') + 'echelle_test'))
            a, mesure = await self.jouer(m, d)
            mesures.append(mesure)
            self.assertEqual(a.joueur['salle'], 'cour' if haut else 'terrasse')
        for porte in (False, True):
            m = web_passage.atelier(porte=porte)
            d = DescripteurPublic(web_passage.clic(m, 'mur_atelier', 'franchir_obstacle', outil='perche_1')['envoye'])
            self.assertEqual(proposition_descripteur(m, d), analyser(m, 'franchir mur_atelier avec perche_1'))
            a, mesure = await self.jouer(m, d)
            mesures.append(mesure)
            self.assertEqual(a.joueur['salle'], 'terrasse')
        print('MESURES_UT_353=' + json.dumps(mesures, ensure_ascii=False))

    async def test_scenes_reelles_force_frapper_assommer_et_fuir(self):
        for script, geste, cible, p in (
            ('force-4b-frapper', 'frapper', 'brune', {'methode': 'simple', 'outil': ''}),
            ('force-4b-assommer', 'frapper', 'marchand', {'methode': 'assommer', 'outil': ''}),
            ('force-4c-fuir', 'fuir', 'brune', {})):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                fichier = Path(tmp) / 'scene.json'
                donnees = json.loads((Path(__file__).parent / 'data/bancs' / (script + '.json')).read_text(encoding='utf-8'))
                with patch.object(Monde, 'd20', side_effect=[20, 1]):
                    preparer(donnees, fichier)
                m = web_passage.normaliser(Monde.charger(fichier))
                d = DescripteurPublic(web_corps.clic(m, cible, geste, p)['envoye'])
                a, _ = await self.jouer(m, d)
                if script.endswith('assommer'):
                    self.assertFalse(corps.conscient(a, cible))
                elif geste == 'fuir':
                    self.assertNotEqual(a.joueur['salle'], m.joueur['salle'])
                else:
                    self.assertLess(corps.pv(a, cible), corps.pv(m, cible))

    async def test_moyen_qualification_et_danger_perimes_sans_substitution(self):
        m, cible, _ = web_corps.monde_geste('frapper')
        d = DescripteurPublic(web_corps.clic(m, cible, 'frapper', {'methode': 'simple', 'outil': 'moyen_deux'})['envoye'])
        await self.jouer(m, d, mutation=lambda m: web_corps.placer(m.objets['moyen_deux'], 'reserve', [1, 1]))
        m = web_passage.normaliser(web_passage.scene())
        d = DescripteurPublic(web_passage.clic(m, 'poutre_conduite', 'passer_obstacle', methode='dessous')['envoye'])
        await self.jouer(m, d, mutation=lambda m: m.objets['poutre_conduite'].pop('passage'))
        m, cible, _ = web_corps.monde_geste('riposter')
        d = DescripteurPublic(web_corps.clic(m, cible, 'riposter', {'outil': ''})['envoye'])
        await self.jouer(m, d, mutation=lambda m: m.data.update(violences_joueur=[]))

    async def test_annuler_corps_et_passage_et_reference_perimee(self):
        m, cible, _ = web_corps.monde_geste('frapper')
        corps_d = DescripteurPublic(web_corps.clic(m, cible, 'frapper', {'methode': 'simple', 'outil': 'moyen_deux'})['envoye'])
        passage = web_passage.normaliser(web_passage.scene())
        passage_d = DescripteurPublic(web_passage.clic(passage, 'poutre_conduite', 'passer_obstacle', methode='dessous')['envoye'])
        for monde, d in ((m, corps_d), (passage, passage_d)):
            with self.subTest(geste=d.contenu['geste']):
                a, _ = await self.jouer(monde.copier(), d, suite=['annuler'])
                self.assertEqual({k: v for k, v in a.data.items() if k != 'conversation'},
                                 {k: v for k, v in monde.data.items() if k != 'conversation'})
                def retirer(m):
                    cible = d.contenu['cible']
                    if cible in m.objets:
                        web_corps.placer(m.objets[cible], 'reserve', [1, 1])
                await self.jouer(monde.copier(), d, mutation=retirer)


@unittest.skipUnless(shutil.which('node'), 'Node requis')
class ConsoleTests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = 'console'


@unittest.skipUnless(terminal.tui.TEXTUAL and shutil.which('node'), 'Textual et Node requis')
class TUITests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = 'tui'
