"""K2 : brouillons sans effet, vrai verdict, vues et monde rechargés."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon.accords_publics import AccordTerminal, accords_publics, termes_parametres
from donjon.mj import MJOpenAI
from donjon.negociation import ouvrir, OBSTACLES
from donjon import agendas
from tests.test_candidats_contrat import relais, huile_connue
from tests.test_editeur_marche import vues
from tests.test_tensions import recharger
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests import test_information_publique as support_web


def situations():
    yield relais(), {'destinataire': 'aubin', 'demande': {'type': 'part', 'objet': 'planches'},
        'contrepartie': {'type': 'tache', 'condition': {'objet': 'brasero', 'allume': True}}}
    m = huile_connue()
    m.objets['lanterne_etable']['proprietaire'] = 'joueur'
    yield recharger(m), {'destinataire': 'odile', 'demande': {'type': 'part', 'objet': 'pot_huile'},
        'contrepartie': {'type': 'objet', 'objet': 'lanterne_etable'}}


def aide(a):
    return {'mode': 'accord', 'texte': '', 'faits': [],
            'proposition': {'obstacle': '', 'alternatives': [copy.deepcopy(a)]}}


class NegociationAideTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(vues(m), vues(n))

    def test_demande_aide_editeur_verdict_et_recharge_deux_scenes(self):
        for m, a in situations():
            with self.subTest(qui=a['destinataire']):
                k0 = accords_publics(m)['suggestions']
                avant = copy.deepcopy(m.data)
                mj = MJOpenAI('gpt-6-luna', connexion='chatgpt')
                with patch.object(mj, '_appeler_brut', return_value=aide(a)) as compiler:
                    r = mj._echanger_prepare(m, 'Aide-moi à trouver un marché sans dépenser mes pièces.')
                compiler.assert_called_once()
                b = r['_formulaire_accord']
                self.assertEqual(len(b['public']['suggestions']), 1)
                s = b['public']['suggestions'][0]
                self.assertTrue(all(x['initial'] != s['initial'] for x in k0))
                f = AccordTerminal(b['public'], b['initial'])
                self.assertIn(s['nom'], f.rendre())
                f.saisir('suggestion 1')
                self.assertIsNone(f.etape)
                d = f.saisir('valider')
                self.assertEqual(termes_parametres(d.contenu['parametres']), (a['demande'], a['contrepartie']))
                # Le vrai callback web sélectionne aussi cette alternative.
                e = etat(m); e['brouillon_accord'] = b; e['sonde_suggestion'] = 0
                self.assertEqual(page(m, e)['suggestion']['envoye'], d.contenu)
                self.assertEqual(m.data, avant)
                self.recharge(m)
                n, lignes, _ = support_web.InformationPubliqueTests().boucle(m, [d, 'tenter'])
                verdict = 'accepte' if 'accepte' in '\n'.join(lignes) else 'refuse'
                self.assertIn(verdict, '\n'.join(lignes))
                self.assertEqual(n.joueur['or'], avant['joueur']['or'])
                self.assertTrue(n.data['emissions_parole'])
                if verdict == 'accepte':
                    if a['contrepartie']['type'] == 'tache':
                        self.assertTrue(agendas.en_cours(n, 'joueur', condition=a['contrepartie']['condition']))
                    else:
                        self.assertEqual(n.objets[a['contrepartie']['objet']]['proprietaire'], a['destinataire'])
                else:
                    self.assertEqual(n.objets[a['demande']['objet']], avant['objets'][a['demande']['objet']])
                print(json.dumps({'scene': a['destinataire'], 'hors_k0': 1,
                    'verdict': verdict}, ensure_ascii=False))
                self.recharge(n)

    def test_admission_refusee_pas_de_clause_reparee_ni_possession_revelee(self):
        m, a = next(situations())
        avant = copy.deepcopy(m.data)
        mauvais = copy.deepcopy(a); mauvais['demande']['objet'] = 'cloche'
        r = ouvrir(m, {'obstacle': '', 'alternatives': [mauvais, a]})
        self.assertEqual([s['initial'] for s in r['_formulaire_accord']['public']['suggestions']], [a])
        for modification in ('clause', 'date', 'secret', 'fonds'):
            b = copy.deepcopy(a)
            if modification == 'clause':
                b['demande']['si'] = 'succès'
            elif modification == 'date':
                b['demande']['limite'] = 9999
            elif modification == 'secret':
                b['demande']['objet'] = 'briquet_aubin'
            else:
                b['contrepartie'] = {'type': 'pieces', 'montant': 999999}
            self.assertNotIn('_formulaire_accord', ouvrir(m, {'obstacle': '', 'alternatives': [b]}))
        with patch('donjon.echanges.candidat_proposition', return_value=False):
            self.assertNotIn('_formulaire_accord', ouvrir(m, aide(a)['proposition']))
        from donjon.esprits import lire
        sans_preuve = m.copier()
        lire(sans_preuve, 'joueur')['croyances'].pop('planches', None)
        self.assertNotIn('_formulaire_accord', ouvrir(sans_preuve, aide(a)['proposition']))
        self.recharge(sans_preuve)
        self.assertEqual(m.data, avant)
        self.recharge(m)

    def test_condition_succes_et_autres_clauses_arretent_tout_le_marche(self):
        m, a = next(situations())
        avant = copy.deepcopy(m.data)
        mj = MJOpenAI('gpt-6-luna', connexion='chatgpt')
        for obstacle in OBSTACLES:
            p = {'obstacle': obstacle, 'alternatives': [a]}
            with patch.object(mj, '_compiler_libre', return_value={**aide(a), 'proposition': p}):
                r = mj._echanger_prepare(m, 'Ramène Brune avant la crue, je paie seulement si tu réussis.')
            self.assertIn(OBSTACLES[obstacle], r['texte'])
            self.assertNotIn('_formulaire_accord', r)
        self.assertEqual(m.data, avant)
        self.recharge(m)

    def test_contexte_public_pas_de_besoin_prive_et_schema_commun(self):
        from donjon.esprits import lire
        from donjon.spatial import installer
        m, a = next(situations()); installer(m)
        mj = MJOpenAI('gpt-6-luna', connexion='chatgpt')
        entrees = []
        def appeler(instructions, entree, intention, fonction, schema):
            entrees.append(copy.deepcopy(entree))
            self.assertIn('accords_negociables', entree['faits'])
            self.assertIn('alternatives', json.dumps(schema))
            return aide(a)
        for faim in (0, 99):
            lire(m, 'aubin')['besoins']['faim'] = faim
            with patch.object(mj, '_appeler', side_effect=appeler):
                mj._echanger(m, 'Aide-moi à négocier avec Aubin sans pièces.', None, True)
        self.assertEqual(entrees[0], entrees[1])
        self.assertNotIn('besoins_pressants', json.dumps(entrees[0]))
        self.assertNotIn('but_actuel', json.dumps(entrees[0]))

    def test_limite_typee_compilee_avant_affichage_et_soumission(self):
        from donjon.temps import instant
        from donjon.monde import ErreurMonde
        m, a = list(situations())[1]
        a['contrepartie'] = {'type': 'pieces', 'montant': 3}
        a['demande']['limite'] = {'dans_secondes': 600}
        avant = copy.deepcopy(m.data)
        r = ouvrir(m, {'obstacle': '', 'alternatives': [a, a]})
        b = r['_formulaire_accord']
        self.assertEqual(len(b['public']['suggestions']), 1)
        initial = b['public']['suggestions'][0]['initial']
        self.assertEqual(initial['demande']['limite'], instant(m) + 6000)
        self.assertNotIn('sans limite', b['public']['suggestions'][0]['nom'])
        f = AccordTerminal(b['public']); f.saisir('suggestion 1')
        d = f.saisir('valider')
        self.assertEqual(termes_parametres(d.contenu['parametres'])[0], initial['demande'])
        self.assertEqual(m.data, avant)
        n, lignes, _ = support_web.InformationPubliqueTests().boucle(m, [d, 'tenter'])
        self.assertIn('accepte', '\n'.join(lignes))
        self.assertEqual(n.joueur['or'], avant['joueur']['or'] - 3)
        self.recharge(n)
        with self.assertRaises(ErreurMonde) as exc:
            ouvrir(m, {'obstacle': '', 'alternatives': [a, a, a]})
        self.assertTrue(exc.exception.attendu)

