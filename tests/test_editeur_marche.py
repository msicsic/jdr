"""K1 : les deux termes parcourent les interfaces, l'accord et la recharge."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from donjon.accords_publics import (AccordTerminal, accords_publics, parole_accord,
                                    parametres_termes, termes_parametres)
from donjon.accords_libres import depuis_parole
from donjon.commandes import DescripteurPublic
from donjon.monde import ErreurMonde, Monde
from donjon.mj import MJOpenAI
from donjon.emissions import pnj
from donjon.rendu import fiche, regarder, decrire_comptes
from donjon.scene import scene_percue
from tests.test_candidats_contrat import relais, huile_connue
from tests.test_tensions import recharger
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests import test_information_publique as support_web
from tests import test_gestes_terminal as support_console
from tests.support import mj_simule


def cas():
    m = relais()
    yield m, 'aubin', {'type': 'part', 'objet': 'planches'}, {'type': 'pieces', 'montant': 10}
    m = relais()
    yield m, 'aubin', {'type': 'tache', 'condition': {'objet': 'brasero', 'allume': True}}, {'type': 'objet', 'objet': 'cloche'}
    m = huile_connue()
    m.objets['lanterne_etable']['proprietaire'] = 'joueur'
    yield recharger(m), 'odile', {'type': 'part', 'objet': 'pot_huile'}, {'type': 'objet', 'objet': 'lanterne_etable'}


def descripteur(qui, demande, donne):
    return DescripteurPublic({'geste': 'accord', 'cible': qui, 'parametres': parametres_termes(demande, donne)})


def entrees(a, qui, demande, donne):
    index = lambda t: next(i for i, x in enumerate(a['prestations'], 1) if x['terme'] == t)
    n = str(next(i for i, x in enumerate(a['destinataires'], 1) if x['id'] == qui))
    return [n, str(index(demande)), str(donne['montant']) if donne['type'] == 'pieces' else f'terme {index(donne)}', '0']


def vues(m):
    return fiche(m), regarder(m), decrire_comptes(m), scene_percue(m), pnj(m)


class EditeurMarcheTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(vues(n), vues(m))
        return n

    def test_web_console_termes_soumis_verdict_et_recharge(self):
        from donjon.spatial import installer
        for m, qui, demande, donne in cas():
            with self.subTest(qui=qui, demande=demande):
                installer(m)
                a = accords_publics(m)
                avant = copy.deepcopy(m.data)
                r = AccordTerminal(a)
                choix = entrees(a, qui, demande, donne)
                for s in choix:
                    r.saisir(s)
                self.assertIn('Corvus donne', r.rendre())
                self.assertIn('Corvus demande', r.rendre())
                d = r.saisir('valider')
                self.assertEqual(d, descripteur(qui, demande, donne))
                e = etat(m)
                e['sonde_accord'] = {'Destinataire': next(i for i, x in enumerate(a['destinataires']) if x['id'] == qui),
                    'Prestation': next(i for i, x in enumerate(a['prestations']) if x['terme'] == demande),
                    'Délai en minutes (0 = sans limite)': 0}
                if donne['type'] == 'pieces':
                    e['sonde_accord']['Prix payé maintenant'] = donne['montant']
                else:
                    e['sonde_accord']['Contrepartie (Corvus donne)'] = next(i for i, x in enumerate(a['prestations']) if x['terme'] == donne)
                clic = page(m, e)['accord']
                self.assertEqual(clic['envoye'], d.contenu)
                self.assertIn('Corvus donne', clic['resume'])
                self.assertEqual(m.data, avant)
                from donjon import echanges
                original, soumis = echanges.proposer, []
                def proposer(monde, proposant, auditeur, demande, contrepartie, **kw):
                    soumis.append((copy.deepcopy(demande), copy.deepcopy(contrepartie)))
                    return original(monde, proposant, auditeur, demande, contrepartie, **kw)
                with patch('donjon.echanges.proposer', side_effect=proposer):
                    web, lignes, _ = support_web.InformationPubliqueTests().boucle(m.copier(), [d, 'tenter'])
                    console, _, _ = support_console.ConsoleTests().jouer_console(m.copier(), ['accord', *choix, 'valider', 'tenter'])
                self.assertTrue(soumis)
                self.assertTrue(all(t == (demande, donne) for t in soumis))
                self.assertEqual(support_console.sans_saisie(web.data), support_console.sans_saisie(console.data))
                self.assertEqual(vues(web), vues(console))
                self.assertRegex('\n'.join(lignes), 'accepte|refuse')
                print(json.dumps({'cas': qui, 'demande': demande, 'contrepartie': donne,
                    'verdict': 'accepte' if 'accepte' in '\n'.join(lignes) else 'refuse',
                    'termes_exacts': True, 'interfaces_identiques': True}, ensure_ascii=False))
                self.recharge(web)

    def test_libre_meme_apercu_et_fidelite_conservee(self):
        from donjon.spatial import installer
        for m, qui, demande, donne in cas():
            installer(m)
            p = parole_accord(m, descripteur(qui, demande, donne).contenu)
            from donjon.paroles import OPERATIONS
            p['operations_demandees'] = {t: t == 'proposition' for t in OPERATIONS}
            mj = MJOpenAI('gpt-6-luna', connexion='chatgpt')
            avant = copy.deepcopy(m.data)
            # Le compilateur et la revue sont simulés ; la vraie orchestration reste exécutée.
            with patch.object(mj, '_verifier_fidelite_parole') as revue, patch.object(
                    mj, '_compiler_libre', side_effect=AssertionError('Aucun appel modèle')):
                reponse = mj._echanger_prepare(m, p['replique'], reponse={'mode': 'parole_joueur', 'proposition': p})
            revue.assert_called_once()
            b = reponse['_formulaire_accord']
            r = AccordTerminal(b['public'], b['initial'])
            self.assertIsNone(r.etape)
            d = r.saisir('valider')
            self.assertEqual(d, descripteur(qui, demande, donne))
            e = etat(m); e['brouillon_accord'] = b; e['sonde_accord_libre'] = True
            self.assertEqual(page(m, e)['accord_libre']['envoye'], d.contenu)
            self.assertEqual(m.data, avant)
            n, _, _ = support_web.InformationPubliqueTests().boucle(m, [d, 'tenter'])
            self.recharge(n)

    def test_clause_inconnue_melange_et_revalidation_sans_perte(self):
        for m, qui, demande, donne in cas():
            avant = copy.deepcopy(m.data)
            for nom in ('demande', 'contrepartie'):
                p = {'demande': copy.deepcopy(demande), 'contrepartie': copy.deepcopy(donne)}
                p[nom]['si'] = 'clause non exécutable'
                with self.assertRaises(ErreurMonde) as exc:
                    parole_accord(m, {'geste': 'accord', 'cible': qui, 'parametres': p})
                self.assertIn(nom + '.si', exc.exception.attendu)
            parole = parole_accord(m, descripteur(qui, demande, donne).contenu)
            parole['contenu'].append({'type': 'propos', 'sujet': '', 'attribut': '', 'valeur': ''})
            with self.assertRaises(ErreurMonde) as exc:
                depuis_parole(m, parole, 'marché et autre acte', marches=True)
            self.assertTrue(exc.exception.attendu)
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_pieces_sources_rien_et_limite_exacte_dans_les_deux_interfaces(self):
        m = relais()
        m.objets['cloche']['pieces'] = 20
        a = accords_publics(m)
        for demande, donne in (({'type': 'pieces', 'montant': 7}, {'type': 'rien'}),
                ({'type': 'part', 'objet': 'planches'}, {'type': 'pieces', 'montant': 7, 'objet': 'cloche'}),
                ({'type': 'pieces', 'montant': 7}, {'type': 'part', 'objet': 'planches', 'limite': 6123})):
            initial = {'destinataire': 'aubin', 'demande': demande, 'contrepartie': donne}
            r = AccordTerminal(a, initial)
            d = r.saisir('valider')
            self.assertEqual(termes_parametres(d.contenu['parametres']), (demande, donne))
            e = etat(m); e['brouillon_accord'] = {'public': a, 'initial': initial}; e['sonde_accord_libre'] = True
            self.assertEqual(page(m, e)['accord_libre']['envoye'], d.contenu)
            self.assertEqual(parole_accord(m, d.contenu)['contenu'][0], {'type': 'proposition', 'demande': demande, 'contrepartie': donne})
        self.recharge(m)


class EditeurMarcheTuiTests(unittest.IsolatedAsyncioTestCase):
    async def test_tui_reelle_deux_termes_sauves_avant_rendu(self):
        from donjon.tui import SeuilApp
        from textual.widgets import Input
        from tests.test_gestes_terminal import TerminalTests
        for m, qui, demande, donne in list(cas())[1:]:
            with tempfile.TemporaryDirectory() as tmp:
                f = Path(tmp) / 'partie.json'; m.sauver(f)
                faux = MagicMock(connexion='api', erreur_auth=None)
                with mj_simule(faux), patch.object(Monde, 'd20', return_value=20):
                    app = SeuilApp(['--connexion', 'api', '--save', str(f)])
                    async with app.run_test(size=(120, 40)) as pilot:
                        support = TerminalTests(); await support.pret(app)
                        await pilot.press('f7')
                        initial = app.derniere_vue
                        for texte in ['accord', *entrees(initial['accord'], qui, demande, donne)]:
                            app.query_one('#commande', Input).value = texte
                            await pilot.press('enter')
                            self.assertIs(app.derniere_vue, initial)
                            self.assertEqual(Monde.charger(f).data, m.data)
                        for texte in ['valider', 'tenter']:
                            precedente = app.derniere_vue
                            app.query_one('#commande', Input).value = texte
                            await pilot.press('enter')
                            await support.attendre(lambda: app.derniere_vue is not precedente and not app.occupe,
                                                   lambda: repr(app.sorties[-5:]))
                        vue = app.derniere_vue
                        await support.fermer(app)
                faux.echanger.assert_not_called()
                n = Monde.charger(f)
                self.assertTrue(pnj(n))
                self.assertEqual(vue['fiche'], fiche(n))
                self.assertEqual(vue['scene'], regarder(n))
                self.assertEqual(vues(n), vues(recharger(n)))
                web, _, _ = support_web.InformationPubliqueTests().boucle(
                    m.copier(), [descripteur(qui, demande, donne), 'tenter'])
                self.assertEqual(support_console.sans_saisie(n.data), support_console.sans_saisie(web.data))
