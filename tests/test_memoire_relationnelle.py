"""S1n : preuves relationnelles stables, vues détachées et autorité des axes."""
import copy
import json
import tempfile
from pathlib import Path
import unittest

from donjon import memoire, relations
from donjon.esprits import lire, memoriser
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.emissions import lire as emissions
from tests import test_memoire_socle
from tests.test_memoire_refus import inventaire
from tests.test_memoire_paroles import acces_dits
from tests.test_constater_soupcon import scene, disparition
from tests.test_tensions import recharger, relais

REGISTRES = {'relations', 'preuves_relations', 'portages', 'compagnie',
             'compagnie_minute', 'suites', 'indices_soupcon', 'constats_biens', 'soupcons'}
RACINE = test_memoire_socle.RACINE


class SuivisRelationnelsTests(unittest.TestCase):
    def recharge(self, m):
        public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(json.dumps(n.data), json.dumps(m.data))
        self.assertEqual((regarder(n), scene_percue(n), emissions(n)), public)
        return n

    def test_inventaire_ferme_et_alias(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf8'))
        mesures = inventaire(REGISTRES)
        self.assertEqual(mesures['donjon/esprits.py'].pop('<module>/' + test_memoire_socle.AccesTests.schema_champs()), 1)
        # Les exceptions restantes sont des productions de diagnostics,
        # capacités locales et préparation d'auteur, jamais des esprits vivants.
        self.assertEqual({f: a for f, a in mesures.items() if a}, fixture['relationnels_homonymes_s1n'])
        for registre in REGISTRES:
            for source in (
                f'e["{registre}"]', f'e.get("{registre}")', f'e.setdefault("{registre}", {{}})',
                f'cle = "{registre}"; stock = e[cle]; alias = stock; alias[0]["minute"] = 8',
                f'stock = e["{registre}"]; ajouter = stock.append; ajouter(s)',
                f'for entree in e["{registre}"]:\n entree.clear()',
                f'def fuite(e):\n stock = e["{registre}"]; return stock',
                f'del e["{registre}"]', f'e.pop("{registre}")',
                f'e.update({registre}=[])', f'e.update(**{{"{registre}": stock}})',
                f'e.__setitem__("{registre}", [])', f'e = {{"{registre}": stock}}',
            ):
                with self.subTest(source=source):
                    self.assertTrue(acces_dits(source, registres={registre}))

    def test_vues_pures_et_admissions_detachees(self):
        m = relais()
        r = relations.envers(m, 'marchand', 'brune')
        memoire.retenir_relation(m, 'marchand', 'brune', r)
        effets = {'confiance': -12}
        memoire.retenir_epreuve(m, 'marchand', 'brune', 'preuve-test', .4, effets)
        suite = {'type': 'engagement_tenu', 'de': 'marchand', 'pour': 'brune',
                 'condition': {'objet': 'brasero', 'allume': True}, 'minute': 0, 'preuve': 'suite-test'}
        memoire.retenir_suite_relationnelle(m, 'marchand', suite)
        memoire.retenir_portage(m, 'marchand', 'vivres', 'brune', 'preuve-test')
        avant = copy.deepcopy(m.data)
        r['ancrages']['peur'][0] = 100
        effets.clear(); suite['condition'].clear()
        vues = [memoire.relations_retenues(m, 'marchand'),
                memoire.relation_retenue(m, 'marchand', 'brune'),
                memoire.epreuve_retenue(m, 'marchand', 'brune', 'preuve-test'),
                memoire.portages_retenus(m, 'marchand'),
                memoire.portage_retenu(m, 'marchand', 'vivres'),
                memoire.suites_relationnelles(m, 'marchand', 'brune'),
                memoire.liens_initiaux(m, 'marchand'), relations.suivis_decision(m, 'marchand')]
        vues[1]['ancrages']['peur'].clear()
        vues[2]['effets'].clear()
        vues[5][0]['condition'].clear()
        for vue in vues:
            vue.clear()
        for qui in ('absent', 'joueur'):
            self.assertEqual(memoire.relations_retenues(m, qui), {})
            self.assertIsNone(memoire.relation_retenue(m, qui, 'brune'))
            self.assertIsNone(memoire.epreuve_retenue(m, qui, 'brune', 'test'))
            self.assertEqual(memoire.portages_retenus(m, qui), {})
            self.assertIsNone(memoire.portage_retenu(m, qui, 'vivres'))
            self.assertEqual(memoire.suites_relationnelles(m, qui, 'brune'), [])
            self.assertEqual(memoire.compagnie_retenue(m, qui, 'brune'), 0)
            self.assertEqual(memoire.soupcons_retenus(m, qui), {})
            self.assertEqual(memoire.constats_retenus(m, qui), {})
        self.assertEqual(m.data, avant)
        self.recharge(m)

    def test_soupcons_copies_concomitants_et_levee_unique(self):
        for autre in (False, True):
            s = scene(autre)
            m, victime, suspect, coffre, bien, *_ = s
            confiance = relations.envers(m, victime, suspect)['confiance']
            disparition(s)
            soupcons = memoire.soupcons_retenus(m, victime)
            self.assertEqual(len(soupcons), 1)
            preuve, soupcon = next(iter(soupcons.items()))
            self.assertIn(bien, soupcon['indices'])
            self.assertLessEqual(set(soupcon['indices']), {coffre, bien})
            # Un contenant peut garder d'autres biens : seule sa vacuité
            # réellement constatée constitue un second indice concomitant.
            if memoire.constats_retenus(m, victime)[coffre]['vide']['valeur']:
                self.assertIn(coffre, soupcon['indices'])
            avant = copy.deepcopy(m.data)
            soupcon['indices'].clear(); soupcon['candidats'].clear()
            memoire.constats_retenus(m, victime)[bien]['present'].clear()
            self.assertEqual(m.data, avant)
            for _ in range(45):
                memoriser(m, victime, {'type': 'attendu'})
            m = self.recharge(m)
            self.assertIn(preuve, memoire.soupcons_retenus(m, victime))
            relations.reviser_soupcons(m, victime, bien, rendu=True)
            self.assertEqual(relations.envers(m, victime, suspect)['confiance'], confiance)
            avant = copy.deepcopy(m.data)
            relations.reviser_soupcons(m, victime, bien, rendu=True)
            self.assertEqual(m.data, avant)
            self.recharge(m)

    def test_candidats_admis_sans_alias(self):
        m, victime, suspect, coffre, _, *_ = scene()
        avant = memoire.constats_retenus(m, victime)[coffre]['vide']
        candidats = {suspect: 1.0}
        relations.deduire_soupcon(m, victime, candidats, coffre, 'vide', avant)
        attendu = copy.deepcopy(m.data)
        candidats.clear(); avant.clear()
        self.assertEqual(m.data, attendu)
        self.recharge(m)

    def test_epreuve_completee_sans_reapplication_apres_oubli(self):
        for temoin, auteur, objet in (('marchand', 'brune', 'vivres'), ('aubin', 'ilse', 'planches')):
            m = relais()
            fait = {'type': 'vu_agir', 'auteur': auteur, 'operation': 'prendre',
                    'objet': objet, 'victime': temoin, 'preuve': 'geste-stable'}
            memoriser(m, temoin, dict(fait, par='ouie'))
            faible = memoire.epreuve_retenue(m, temoin, auteur, fait['preuve'])
            self.assertEqual(faible['niveau'], .8)
            for _ in range(45):
                memoriser(m, temoin, {'type': 'attendu'})
            m = self.recharge(m)
            memoriser(m, temoin, fait)
            m = self.recharge(m)
            forte = memoire.epreuve_retenue(m, temoin, auteur, fait['preuve'])
            self.assertEqual(forte['niveau'], 1)
            self.assertEqual(forte['effets']['confiance'], -40)
            avant = relations.envers(m, temoin, auteur)
            memoriser(m, temoin, fait)
            self.assertEqual(relations.envers(m, temoin, auteur), avant)
            self.recharge(m)

    def test_validation_des_registres_historiques(self):
        for cle, valeur in (('compagnie', {'brune': 60}), ('compagnie_minute', False),
                            ('preuves_relations', {'x': {'niveau': .7, 'effets': {}}}),
                            ('portages', {'vivres': {'auteur': 'brune'}}),
                            ('suites', [{'type': 'faux'}]),
                            ('indices_soupcon', {'presences': [], 'gestes': [], 'constats': {}, 'soupcons': {}, 'oublis': {'inconnu': 0}})):
            with self.subTest(cle=cle):
                m = relais()
                lire(m, 'marchand')[cle] = valeur  # corruption explicite de sauvegarde
                with self.assertRaises(ErreurMonde):
                    recharger(m)

    def test_migration_des_anciens_suivis_conserve_les_preuves(self):
        m = disparition(scene())
        e = lire(m, 'marchand')
        soupcons = memoire.soupcons_retenus(m, 'marchand')
        constats = memoire.constats_retenus(m, 'marchand')
        axes = relations.envers(m, 'marchand', 'brune')
        # Fixture explicite du format antérieur au registre perceptif borné.
        del e['indices_soupcon']
        e['constats_biens'] = constats
        e['soupcons'] = soupcons
        # Une ancienne sauvegarde se charge comme fichier brut ; le moteur
        # courant refuse à raison de sauver un esprit encore non migré.
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / 'ancienne.json'
            chemin.write_text(json.dumps(m.data, ensure_ascii=False), encoding='utf8')
            n = Monde.charger(chemin)
        self.assertNotIn('constats_biens', lire(n, 'marchand'))
        self.assertNotIn('soupcons', lire(n, 'marchand'))
        self.assertEqual(memoire.constats_retenus(n, 'marchand'), constats)
        self.assertEqual(memoire.soupcons_retenus(n, 'marchand'), soupcons)
        self.assertEqual(relations.envers(n, 'marchand', 'brune'), axes)
        self.recharge(n)
