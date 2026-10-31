"""S1i : preuves subjectives détachées et reprises complètes des signes/dangers."""
import ast
import copy
import gzip
import json
import unittest
from unittest.mock import patch

from donjon import defense, esprits, memoire, signes
from donjon.emissions import lire as paroles
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_memoire_localisation import acces_croyances, RACINE
from tests.test_signes import scene, ecarter
from tests.test_tensions import recharger, vivre


SUIVIS = {"lectures", "signes_lus", "signes_lus_joueur", "suivi_signes", "violences_joueur"}


def acces_suivis(source):
    """Même suivi d'alias que S1f, appliqué aux registres subjectifs S1i.

    Les compteurs homonymes restent inventoriés à l'expression exacte.
    Ne masque ni une clé indirecte ni un accès sous une création de stock.
    """
    class Cles(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value in SUIVIS:
                return ast.copy_location(ast.Constant(value="croyances"), node)
            return node
    return acces_croyances(ast.unparse(Cles().visit(ast.parse(source)))) - acces_croyances(source)


class SignesDangersTests(unittest.TestCase):
    def test_inventaire_suivis_et_contre_epreuves(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf-8'))
        mesures = {}
        for p in [*RACINE.glob('*.py'), *(RACINE / 'donjon').rglob('*.py'), *(RACINE / 'tools').rglob('*.py')]:
            relatif = p.relative_to(RACINE).as_posix()
            if relatif == 'donjon/memoire.py':
                continue
            acces = acces_suivis(p.read_text(encoding='utf-8-sig'))
            if acces:
                mesures[relatif] = {f'{f}/{e}': n for (f, e), n in sorted(acces.items())}
        self.assertEqual(mesures, fixture['suivis_restants_s1i'])
        for cle in SUIVIS | {'detresse', 'violence', 'emotion', 'intention', 'parole_doutee', 'attitude:autre'}:
            source = f'cle = {cle!r}; stock = e[cle]; alias = stock; alias[s]["minute"] = 8'
            self.assertTrue(acces_suivis(source) if cle in SUIVIS else acces_croyances(
                f'cle = {cle!r}; stock = e["croyances"]; c = stock[s][cle]; c["valeur"] = None'))
        self.assertTrue(acces_suivis('for c in m.data["lectures"].values():\n c.clear()'))
        self.assertTrue(acces_suivis('def fuite(m):\n s = m.data["suivi_signes"]; return s'))

    def test_vues_pures_copies_imbriquees_et_bornes_historiques(self):
        m = ecarter(scene())
        with patch('donjon.signes._jet', return_value=20):
            signes.lire(m, 'joueur')
            signes.lire(m, 'marchand')
        esprits.croire(m, 'marchand', 'ilse', 'emotion', 'peur', 'devine', .7, signe='peur')
        memoire.retenir_danger(m, 'marchand', 'brune', 'ilse', m.data['minutes'], True, 'frapper', 'vu')
        memoire.retenir_coup_joueur(m, 'brune', 'frapper')
        avant = copy.deepcopy(m.data)
        self.assertEqual(memoire.lectures_actives(m, 'absent'), [])
        self.assertIsNone(memoire.detresse_retenue(m, 'absent', 'ilse'))
        self.assertEqual(memoire.auteurs_dangereux(m, 'absent'), [])
        for qui in ('joueur', 'marchand'):
            for _, _, c in signes.actives(m, qui):
                c['valeur'] = 'mensonge'
            for c in memoire.lectures_joueur(m).values():
                c['minute'] = -1
        esprits.croyance(m, 'marchand', 'brune', 'violence')['valeur']['ilse']['clos'] = True
        esprits.croyance(m, 'marchand', 'ilse', 'emotion')['valeur'] = 'froid'
        memoire.detresse_retenue(m, 'marchand', 'ilse')['preuve']['valeur'] = 'froid'
        defense.souvenirs(m, 'joueur')[0]['clos'] = True
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)
        date = m.data['minutes']
        for age in (29, 30):
            m.data['minutes'] = date + age
            self.assertEqual(esprits.croyance(m, 'marchand', 'ilse', 'emotion') is not None, age < 30)
            self.assertEqual('brune' in defense.auteurs(m, 'marchand'), age < 30)
            # La détresse héritée du signe ne s'efface pas avec sa péremption.
            self.assertIsNotNone(memoire.detresse_retenue(m, 'marchand', 'ilse'))

    def test_cloture_du_danger_persiste_et_nouveau_geste_seul_reouvre(self):
        m = scene()
        for qui in ('joueur', 'marchand'):
            if qui == 'joueur':
                memoire.retenir_coup_joueur(m, 'brune', 'frapper')
            else:
                memoire.retenir_danger(m, qui, 'brune', 'ilse', m.data['minutes'], True, 'frapper', 'vu')
                self.assertEqual(defense.auteurs(m, qui, 'aubin'), [])
                self.assertIn('brune', defense.auteurs(m, qui, 'ilse'))
            defense.constater_fin(m, qui, 'brune')
            m = recharger(m)
            self.assertEqual(defense.auteurs(m, qui), [])
            # Le réel seul ne modifie pas la clôture subjective.
            m.objets['brune']['corps']['inconscient'] = 0
            self.assertEqual(defense.auteurs(m, qui), [])
            if qui == 'joueur':
                memoire.retenir_coup_joueur(m, 'brune', 'pousser')
            else:
                memoire.retenir_danger(m, qui, 'brune', 'ilse', m.data['minutes'], True, 'pousser', 'vu')
            self.assertIn('brune', defense.auteurs(recharger(m), qui))

    def test_captures_reelles_mine_et_relais_laps_entier_decoupe_publication(self):
        for fichier in ('mine7-lucien-signes.json.gz', 'guet_relais7.json.gz'):
            with self.subTest(fichier=fichier):
                m = Monde(json.loads(gzip.decompress((RACINE / 'tests/data/scenes' / fichier).read_bytes())))
                bloc, lignes = vivre(recharger(m), 2)
                coupe, suite = recharger(m), []
                for _ in range(2):
                    coupe, nouvelles = vivre(coupe, 1)
                    suite.extend(nouvelles)
                    coupe = recharger(coupe)
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(json.dumps(bloc.data), json.dumps(coupe.data))
                self.assertEqual(lignes, suite)
                public = regarder(bloc), scene_percue(bloc), copy.deepcopy(paroles(bloc))
                for reprise in (recharger(bloc), coupe):
                    self.assertEqual(reprise.data, bloc.data)
                    self.assertEqual((regarder(reprise), scene_percue(reprise), paroles(reprise)), public)

    def test_sauvegardes_corrompues_refusees_et_suivi_ancien_migre_sans_jet(self):
        m = ecarter(scene())
        with patch('donjon.signes._jet', return_value=20):
            signes.lire(m, 'joueur')
        for corrompre in (
            lambda d: d.update(violences_joueur=[dict(type='subi', auteur='brune', operation='frapper', minute=0, clos='non')]),
            lambda d: d.update(signes_lus_joueur={'signe': True}),
            lambda d: d['lectures'][next(iter(d['lectures']))].update(confiance=float('nan')),
            lambda d: d['suivi_signes']['joueur']['retenus'].update(signe=[]),
        ):
            n = m.copier()
            corrompre(n.data)
            with self.assertRaises(ErreurMonde):
                recharger(n)
        m.data['suivi_signes']['joueur'] = {'version': 1}
        avant = copy.deepcopy(m.data)
        with patch('donjon.signes._jet', side_effect=AssertionError('jet à la lecture')):
            signes.actives(m, 'joueur')
            self.assertEqual(m.data, avant)
            memoire.preparer_suivi_signes(m, 'joueur', {})
        self.assertEqual(m.data['suivi_signes']['joueur'], dict(version=2, retenus={}, conclusions={}))


if __name__ == '__main__':
    unittest.main()
