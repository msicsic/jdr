"""E5 : menu réel, terminaux, U-C, termes E4 et recharge."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from donjon import agendas
from donjon.accords_publics import AccordTerminal, accords_publics, parole_accord
from donjon.commandes import DescripteurPublic
from donjon.dialogues import preparer_information
from donjon.emissions import pnj
from donjon.esprits import croire, lire
from donjon.monde import Monde, ErreurMonde
from donjon.paroles import preparer_parole
from donjon.rendu import fiche, regarder, decrire_comptes
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_accord_date import huile, travail
from tests.test_tache_promise_recours import reserve
from tests.test_tensions import recharger
from tests import test_information_publique as information_support
from tests import test_gestes_terminal as terminal_support
from tests.test_gestes_terminal import sans_saisie
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests.support import mj_simule


def situation(tache=False):
    from tests.support import regarder as voir
    m, b, q, t, _ = travail(reserve) if tache else huile()
    m.joueur['or'] = 50
    # La rencontre reste celle du scénario ; Corvus achète la prestation.
    if not tache:
        m.joueur['position'] = [2, 1]
        m.objets['lanterne_etable'].update(allume=True, combustible=120)
        m.objets['lanterne_etable']['lieu'] = 'joueur'
    m.data['connus'].extend([t.get('objet') or t['condition']['objet']])
    voir(m, 'joueur', q)
    voir(m, q, 'joueur')
    lire(m, q)['relations']['joueur'] = copy.deepcopy(lire(m, q)['relations'][b])
    croire(m, q, 'joueur', 'lieu', m.joueur['salle'], 'vu',
           salle=m.joueur['salle'], case=m.joueur['position'])
    m = recharger(m)
    return m, DescripteurPublic({'geste': 'accord', 'cible': q,
        'parametres': {'prestation': {k: v for k, v in t.items() if k != 'limite'}, 'prix': 10 if tache else 3, 'limite': 6000}})


def parcours(m, d):
    p = d.contenu['parametres']
    public = accords_publics(m)
    n = [str(next(i for i, x in enumerate(public['destinataires'], 1) if x['id'] == d.contenu['cible'])),
         str(next(i for i, x in enumerate(public['prestations'], 1) if x['terme'] == p['prestation'])),
         str(p['prix']), str((p.get('limite', 0) - public['instant']) // 600) if 'limite' in p else '0']
    return ['accord', *n, 'valider']


class AccordsPublicsTests(unittest.TestCase):
    def vues(self, m):
        return fiche(m), regarder(m), decrire_comptes(m), scene_percue(m), pnj(m)

    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(self.vues(n), self.vues(m))
        return n

    def clic(self, m, d, **sonde):
        public = etat(m)
        p = d.contenu['parametres']
        a = public['accord']
        public['sonde_accord'] = {'Destinataire': next(i for i, x in enumerate(a['destinataires']) if x['id'] == d.contenu['cible']),
            'Prestation': next(i for i, x in enumerate(a['prestations']) if x['terme'] == p['prestation']),
            'Prix payé maintenant': p['prix'], 'Délai en minutes (0 = sans limite)': 10 if 'limite' in p else 0, **sonde}
        return page(m, public)['accord']

    def test_web_console_et_termes_types_memes_accords_comptes_paroles_recharges(self):
        for tache in (False, True):
            with self.subTest(tache=tache):
                m, d = situation(tache)
                from donjon.spatial import installer
                installer(m)  # Même mémoire perceptive que la vraie ouverture du jeu.
                avant = copy.deepcopy(m.data)
                clic = self.clic(m, d)
                self.assertEqual(clic['envoye'], d.contenu)
                self.assertEqual((clic['incomplet'], clic['occupe'], clic['envois']), (0, 0, 1))
                self.assertIn('minute de jeu 10', clic['resume'])
                self.assertEqual(m.data, avant)
                with patch.object(Monde, 'd20', return_value=20):
                    dossier = preparer_information(m, d)
                    self.assertTrue(dossier.confirmation)
                    self.assertIn('payées maintenant', dossier.compris)
                    self.assertIn('10 minutes restantes', dossier.compris)
                    self.assertEqual(m.data, avant)
                    # E4 : mêmes mots et contenu typé, sans le transport direct.
                    parole = parole_accord(m, d.contenu)
                    parole['_intention'] = 'je propose cet échange'
                    temoin, _ = preparer_parole(m.copier(), parole)
                from donjon.narration import consigner
                consigner(temoin, dossier.reponse)
                temoin = self.recharge(temoin)
                etat(temoin)
                self.assertTrue(agendas.en_cours(temoin, d.contenu['cible']))
                web, lignes, _ = information_support.InformationPubliqueTests().boucle(m.copier(), [d, 'tenter'])
                console, sorties, _ = terminal_support.ConsoleTests().jouer_console(m.copier(), [*parcours(m, d), 'tenter'])
                self.assertEqual(sans_saisie(web.data), sans_saisie(console.data))
                self.assertEqual(self.vues(web), self.vues(console))
                # La transaction E4 et U-C ont le même état mécanique et les mêmes émissions.
                for k in ('joueur', 'objets', 'esprits', 'finances_pnj', 'dettes', 'permissions', 'services_rendus', 'emissions'):
                    if k in temoin.data:
                        self.assertEqual(web.data[k], temoin.data[k], k)
                self.assertEqual(self.vues(web), self.vues(temoin))
                self.assertEqual({k: v for k, v in web.data.items() if k != 'conversation'},
                                 {k: v for k, v in temoin.data.items() if k != 'conversation'})
                self.assertEqual(web.joueur['or'], 50 - d.contenu['parametres']['prix'])
                self.assertIn('minute de jeu 10', '\n'.join(lignes))
                self.assertNotIn('attendu', '\n'.join(lignes))
                self.recharge(web)
                print(json.dumps({'mesure': 'e5', 'tache': tache, 'clics_confirmation_comprise': clic['clics'] + 1,
                                  'entrees_console_confirmation_comprise': len(parcours(m, d)) + 1, 'appels_modele': 0}))

    def test_corriger_annuler_sans_effet_et_date_sans_repere(self):
        for tache in (False, True):
            m, d = situation(tache)
            avant = copy.deepcopy(m.data)
            r = AccordTerminal(accords_publics(m))
            for n in parcours(m, d)[1:-1]:
                self.assertIsNone(r.saisir(n))
            self.assertIn('minute de jeu 10', r.rendre())
            r.saisir('corriger prix'); r.saisir('4')
            r.saisir('corriger delai')
            with self.assertRaises(ValueError):
                r.saisir('demain')
            r.saisir('12')
            change = r.saisir('valider')
            self.assertEqual(change.contenu['parametres']['limite'], 7200)
            self.assertEqual(change.contenu['parametres']['prix'], 4)
            clic = self.clic(m, d, correction={'Prix payé maintenant': 4, 'Délai en minutes (0 = sans limite)': 12})
            self.assertEqual(clic['envoye'], change.contenu)
            self.assertEqual(self.clic(m, d, annuler=True)['envois'], 0)
            r = AccordTerminal(accords_publics(m)); r.saisir('annuler')
            self.assertTrue(r.terminee)
            self.assertEqual(m.data, avant)
            abandon, _, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'annuler'])
            self.assertEqual(abandon.joueur['or'], 50)
            self.assertEqual(pnj(abandon), pnj(m))
            self.assertEqual(abandon.objets, m.objets)
            self.recharge(abandon)

    def test_peremption_revalidation_et_parametres_injectes_sans_effet(self):
        for tache in (False, True):
            m, d = situation(tache)
            dossier = preparer_information(m, d)
            ecouler(m, 6001)
            avant = copy.deepcopy(m.data)
            nouveau = dossier.revalider(m)
            self.assertIn('périmée', nouveau.erreur)
            self.assertEqual(m.data, avant)
            self.recharge(m)
            m, d = situation(tache)
            for changer in (lambda x: x['parametres'].update(prix=51),
                            lambda x: x['parametres'].update(limite='demain'),
                            lambda x: x['parametres'].update(paiement_futur=True),
                            lambda x: x.update(cible='cache'),
                            lambda x: x['parametres'].update(prestation={'type': 'part', 'objet': 'cache'})):
                x = copy.deepcopy(d.contenu); changer(x)
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as exc:
                    preparer_information(m, DescripteurPublic(x))
                self.assertTrue(exc.exception.attendu)
                self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_refus_delai_public_et_accord_sans_limite(self):
        for tache in (False, True):
            m, d = situation(tache)
            d.contenu['parametres']['limite'] = 1
            refus, lignes, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'tenter'])
            self.assertEqual(refus.joueur['or'], 50)
            self.assertFalse(agendas.en_cours(refus, d.contenu['cible']))
            self.assertIn('refuse cet échange', '\n'.join(lignes))
            self.assertNotIn('attendu', '\n'.join(lignes))
            self.recharge(refus)
            del d.contenu['parametres']['limite']
            sans, _, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'tenter'])
            self.assertEqual(sans.joueur['or'], 50 - d.contenu['parametres']['prix'])
            self.assertTrue(agendas.en_cours(sans, d.contenu['cible']))
            self.recharge(sans)

    def test_projection_publique_identites_et_brouillon_fige(self):
        from donjon.noms import reference
        m, d = situation()
        m.data['noms_connus'].remove('odile')
        ref = reference(m, 'odile')
        self.assertNotEqual(ref, 'odile')
        a = accords_publics(m)
        self.assertIn(ref, [x['id'] for x in a['destinataires']])
        self.assertNotIn('odile', json.dumps(a))
        known = {x.get('objet') or x.get('condition', {}).get('objet') for x in (p['terme'] for p in a['prestations'])}
        self.assertNotIn('briquet_odile', known)
        r = AccordTerminal(a)
        premier = r.rendre(); a['destinataires'].clear()
        self.assertEqual(r.rendre(), premier)

    def test_revalidation_reelle_peremption_depart_et_fonds_sans_revision(self):
        for tache in (False, True):
            for cause in ('temps', 'depart', 'fonds'):
                with self.subTest(tache=tache, cause=cause):
                    m, d = situation(tache)
                    apres = []
                    def mutation(n):
                        if cause == 'temps':
                            ecouler(n, 6001)
                        elif cause == 'fonds':
                            n.joueur['or'] = 0
                        else:
                            from donjon.geometrie import placer, cases
                            from donjon.pnj import occupants
                            prises = occupants(n, sauf=d.contenu['cible'])
                            case = next(c for c in cases(n.data['salles']['dortoir']) if ('dortoir', c) not in prises)
                            n.objets[d.contenu['cible']]['lieu'] = 'dortoir'
                            placer(n.objets[d.contenu['cible']], 'dortoir', case)
                        apres.append(copy.deepcopy(n.data))
                    obtenu, lignes, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'tenter'], mutation)
                    self.assertEqual({k: v for k, v in obtenu.data.items() if k != 'conversation'},
                                     {k: v for k, v in apres[0].items() if k != 'conversation'})
                    self.assertEqual(pnj(obtenu), pnj(m))
                    self.assertFalse(agendas.en_cours(obtenu, d.contenu['cible']))
                    self.assertIn('Plan indisponible', '\n'.join(lignes))
                    self.recharge(obtenu)

    def test_duree_indeterminee_sans_limite_et_limite_inclusive_conservee(self):
        m, d = situation()
        lire(m, 'odile')['croyances']['joueur'].pop('lieu', None)
        refus, lignes, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'tenter'])
        self.assertIn('durée est incertaine', '\n'.join(lignes))
        self.assertEqual(refus.joueur['or'], 50)
        self.assertFalse(agendas.en_cours(refus, 'odile'))
        self.recharge(refus)
        del d.contenu['parametres']['limite']
        sans, _, _ = information_support.InformationPubliqueTests().boucle(m, [d, 'tenter'])
        self.assertEqual(sans.joueur['or'], 47)
        self.assertTrue(agendas.en_cours(sans, 'odile'))
        self.recharge(sans)
        # À T inclus, seul le jugement E4 décide si la prestation est encore
        # réalisable ; le transport ne déclare pas prématurément l'offre périmée.
        m, d = situation()
        mots = parole_accord(m, d.contenu)
        ecouler(m, 6000)
        self.assertEqual(parole_accord(m, d.contenu), mots)
        self.assertEqual(d.contenu['parametres']['limite'], 6000)

    def test_corriger_prestation_et_destinataire_garde_les_autres_termes(self):
        for tache in (False, True):
            m, d = situation(tache)
            avant = copy.deepcopy(m.data)
            a = accords_publics(m)
            qui = next(i for i, x in enumerate(a['destinataires']) if x['id'] != d.contenu['cible'])
            terme = next(i for i, x in enumerate(a['prestations']) if x['terme'] != d.contenu['parametres']['prestation'])
            r = AccordTerminal(a)
            for n in parcours(m, d)[1:-1]:
                r.saisir(n)
            r.saisir('corriger destinataire'); r.saisir(str(qui + 1))
            r.saisir('corriger prestation'); r.saisir(str(terme + 1))
            change = r.saisir('valider')
            clic = self.clic(m, d, correction={'Destinataire': qui, 'Prestation': terme})
            self.assertEqual(clic['envoye'], change.contenu)
            self.assertEqual(change.contenu, {'geste': 'accord', 'cible': a['destinataires'][qui]['id'],
                'parametres': {**d.contenu['parametres'], 'prestation': a['prestations'][terme]['terme']}})
            self.assertEqual(m.data, avant)
            self.recharge(m)


class AccordTuiTests(unittest.IsolatedAsyncioTestCase):
    async def test_tui_reelle_meme_accord_et_annulation(self):
        from donjon.tui import SeuilApp
        from textual.widgets import Input
        from tests.test_gestes_terminal import TerminalTests
        for tache in (False, True):
            m, d = situation(tache)
            for annuler in (False, True):
                with self.subTest(tache=tache, annuler=annuler), tempfile.TemporaryDirectory() as tmp:
                    f = Path(tmp) / 'partie.json'; m.sauver(f)
                    faux = MagicMock(connexion='api', erreur_auth=None)
                    faux.echanger.side_effect = AssertionError('Appel au modèle')
                    with (mj_simule(faux),
                          patch('jeu.analyser', side_effect=AssertionError('Analyse du choix')),
                          patch.object(Monde, 'd20', return_value=20)):
                        app = SeuilApp(['--connexion', 'api', '--save', str(f)])
                        async with app.run_test(size=(120, 40)) as pilot:
                            support = TerminalTests()
                            await support.pret(app)
                            await pilot.press('f7')
                            initial = app.derniere_vue
                            for texte in parcours(m, d)[:-1]:
                                app.query_one('#commande', Input).value = texte
                                await pilot.press('enter')
                                self.assertIs(app.derniere_vue, initial)
                                self.assertTrue(app.pont.commandes.empty())
                                self.assertEqual(Monde.charger(f).data, m.data)
                            app.query_one('#commande', Input).value = 'valider'
                            await pilot.press('enter')
                            await support.attendre(lambda: app.derniere_vue is not initial and not app.occupe,
                                                   lambda: repr(app.sorties[-5:]))
                            self.assertIn('minute de jeu 10', app.derniere_vue['proposition'])
                            self.assertEqual(Monde.charger(f).joueur['or'], 50)
                            vue = app.derniere_vue
                            app.query_one('#commande', Input).value = 'annuler' if annuler else 'tenter'
                            await pilot.press('enter')
                            await support.attendre(lambda: app.derniere_vue is not vue and not app.occupe,
                                                   lambda: repr(app.sorties[-5:]))
                            vue = app.derniere_vue
                            await support.fermer(app)
                    obtenu = Monde.charger(f)
                    self.assertEqual(vue['fiche'], fiche(obtenu))
                    self.assertEqual(vue['scene'], regarder(obtenu))
                    self.assertEqual(obtenu.joueur['or'], 50 if annuler else 50 - d.contenu['parametres']['prix'])
                    if annuler:
                        self.assertEqual(obtenu.objets, m.objets)
                        self.assertEqual(pnj(obtenu), pnj(m))
                    else:
                        web, _, _ = information_support.InformationPubliqueTests().boucle(m.copier(), [d, 'tenter'])
                        self.assertEqual(sans_saisie(obtenu.data), sans_saisie(web.data))
                    faux.echanger.assert_not_called()
                    faux.raconter_resultat.assert_not_called()
