"""S1m : obstacles causaux et efforts privés jusqu'au choix complet réussi."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon import deliberation as d, memoire, planification as p, pnj_propositions
from donjon.emissions import lire as emissions
from donjon.esprits import lire, memoriser
from donjon.pnj import tour_d_horizon
from donjon.monde import ErreurMonde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_attente_bornee as bornes, test_reessai_obstacle as captures
from tests import test_memoire_socle, test_recours_negatif as negatifs, test_temps_reel as temps
from tests.test_memoire_paroles import acces_dits
from tests.test_memoire_refus import inventaire
from tests.test_tensions import placer, recharger, vivre

REGISTRES = {'renoncements', 'attentes_bornees'}
RACINE = test_memoire_socle.RACINE


class ObstaclesMemoireTests(unittest.TestCase):
    def setUp(self):
        for nom in ('_MEMOIRE', '_GRAPHES', '_IMPOSSIBLES'):
            remplacement = patch.object(p, nom, {})
            remplacement.start()
            self.addCleanup(remplacement.stop)

    def recharge(self, m):
        public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual((regarder(n), scene_percue(n), emissions(n)), public)
        return n

    def test_inventaire_ferme_et_contre_epreuves(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf8'))
        mesures = inventaire(REGISTRES)
        self.assertEqual(mesures['donjon/esprits.py'].pop('<module>/' + test_memoire_socle.AccesTests.schema_champs()), 1)
        self.assertEqual({f: a for f, a in mesures.items() if a}, fixture['obstacles_homonymes_s1m'])
        for registre in REGISTRES:
            for source in (
                f'e["{registre}"]', f'e.get("{registre}")', f'e.setdefault("{registre}", {{}})',
                f'cle = "{registre}"; stock = e[cle]; alias = stock; alias[q][s] = 8',
                f'stock = e["{registre}"]; prendre = stock.get; prendre(q)',
                f'for entree in e["{registre}"].values():\n entree.clear()',
                f'def fuite(e):\n stock = e["{registre}"]; return stock',
                f'del e["{registre}"]', f'e.pop("{registre}")',
                f'e.update({registre}={{}})', f'e.update(**{{"{registre}": stock}})',
                f'e.__setitem__("{registre}", {{}})', f'e = {{"{registre}": stock}}',
            ):
                with self.subTest(source=source):
                    self.assertTrue(acces_dits(source, registres=REGISTRES))

    def test_vues_et_admissions_copiees_causes_distinctes_et_anciens_delais(self):
        m = captures.odon()
        r = memoire.obstacles_du_motif(m, 'odon', 'agenda')[0]
        for qui in ('odon', 'absent', 'joueur'):
            avant = copy.deepcopy(m.data)
            memoire.renoncements_retenus(m, qui).clear()
            for obstacle in memoire.obstacles_du_motif(m, qui, 'agenda'):
                obstacle['cause']['etape'].clear()
                obstacle['cause'].get('temoins', {}).clear()
            self.assertIsNone(memoire.effort_retenu(m, qui, 'inconnu'))
            self.assertEqual(avant, m.data)
        cause, but = copy.deepcopy(r['cause']), copy.deepcopy(r['but'])
        cause['etape']['operation'] = 'ouvrir'
        memoire.retenir_renoncement(m, 'odon', 'agenda', but, cause)
        but.clear()
        cause['temoins'].clear()
        self.assertEqual(len(memoire.obstacles_du_motif(m, 'odon', 'agenda')), 2)
        self.assertTrue(memoire.obstacles_du_motif(m, 'odon', 'agenda')[1]['cause']['temoins'])
        lire(m, 'odon')['renoncements']['ancien'] = 42  # fixture historique explicite
        self.assertEqual(memoire.obstacles_du_motif(m, 'odon', 'ancien'), [])
        m = self.recharge(m)
        self.assertEqual(memoire.renoncements_retenus(m, 'odon')['ancien'], 42)
        for _ in range(45):
            memoriser(m, 'odon', {'type': 'son', 'salle': 'bureau', 'nature': 'pas'})
        self.assertEqual(len(memoire.obstacles_du_motif(self.recharge(m), 'odon', 'agenda')), 2)

    def test_devis_isoles_et_choix_imbriques_interrompus_ne_publient_rien(self):
        m = self.recharge(bornes.joss())
        avant = copy.deepcopy(m.data)
        with p.vues_du_choix(m, 'joss'):
            p.planifier(m, 'joss', 'faim')
        self.assertEqual(m.data, avant)
        with self.assertRaisesRegex(RuntimeError, 'interrompu'):
            with memoire.choix_complet(m, 'joss'):
                with p.vues_du_choix(m, 'joss'):
                    p.planifier(m, 'joss', 'faim')
                self.assertEqual(m.data, avant)
                raise RuntimeError('interrompu après sélection')
        self.assertEqual(self.recharge(m).data, avant)
        with memoire.choix_complet(m, 'joss'):
            memoire.retenir_effort_du_choix(m, 'joss', 'parent', 'conservé')
            with self.assertRaises(RuntimeError):
                with memoire.choix_complet(m, 'joss'):
                    memoire.retenir_effort_du_choix(m, 'joss', 'parent', 'jeté')
                    raise RuntimeError()
            self.assertEqual(memoire.effort_retenu(m, 'joss', 'parent'), 'conservé')
            self.assertEqual(m.data, avant)
        self.assertEqual(memoire.effort_retenu(self.recharge(m), 'joss', 'parent'), 'conservé')

    def test_devis_negatifs_reels_isoles_purs_et_choisis_persistants(self):
        for qui in ('odon', 'remy'):
            with self.subTest(qui=qui):
                m = negatifs.RecoursNegatifTests().scene(qui)
                avant = copy.deepcopy(m.data)
                intention = lire(m, qui)['intention']
                self.assertIsNone(pnj_propositions.recours(m, qui, intention['motif'], intention['plan']))
                self.assertEqual(self.recharge(m).data, avant)
                with memoire.choix_complet(m, qui):
                    self.assertIsNone(pnj_propositions.recours(m, qui, intention['motif'], intention['plan']))
                    self.assertEqual(m.data, avant)
                self.assertNotEqual(m.data, avant)
                self.recharge(m)

    def test_choix_reel_interrompu_au_classement_jette_effort_et_cloture(self):
        # Effort réellement borné à l'auberge, puis cause de témoin réellement levée à la mine.
        for famille in ('effort', 'obstacle'):
            with self.subTest(famille=famille):
                m = bornes.joss() if famille == 'effort' else captures.odon()
                qui = 'joss' if famille == 'effort' else 'odon'
                if famille == 'obstacle':
                    placer(m, 'bram', 'filon', (4, 2))
                    d.choisir(m, qui, m.data['minutes'])
                    tour_d_horizon(m, qui)
                m = self.recharge(m)
                depart_reussi = self.recharge(m)
                avant = copy.deepcopy(lire(m, qui))
                classer = d._classer
                def interrompre(*args, **kwargs):
                    classer(*args, **kwargs)
                    for cle in REGISTRES:
                        self.assertEqual(lire(m, qui)[cle], avant[cle])
                    raise RuntimeError('classement interrompu')
                with patch.object(d, '_classer', side_effect=interrompre):
                    with self.assertRaisesRegex(RuntimeError, 'classement interrompu'):
                        d.choisir(m, qui, m.data['minutes'])
                m = self.recharge(m)
                for cle in REGISTRES:
                    self.assertEqual(lire(m, qui)[cle], avant[cle])
                # Les autres effets opérationnels du choix ne sont pas annulés.
                # La publication réussie se contrôle depuis le même état initial.
                m = depart_reussi
                d.choisir(m, qui, m.data['minutes'])
                m = self.recharge(m)
                if famille == 'effort':
                    self.assertTrue(lire(m, qui)['attentes_bornees'])
                else:
                    self.assertFalse(memoire.obstacles_du_motif(m, qui, 'agenda'))

    def test_corruptions_refusees_et_absence_de_brouillon_sauvegarde(self):
        m = captures.odon()
        for cle, valeur in (('attentes_bornees', {'recours': []}),
                            ('renoncements', {'agenda': [{'instant': 0, 'but': {}, 'cause': {}}]}),
                            ('renoncements', {'agenda': True})):
            with self.subTest(cle=cle), self.assertRaises(ErreurMonde):
                n = m.copier()
                lire(n, 'odon')[cle] = valeur
                recharger(n)
        avant = copy.deepcopy(m.data)
        with memoire.choix_complet(m, 'odon'):
            memoire.retenir_effort_du_choix(m, 'odon', 'recours', 'signature')
            self.assertEqual(self.recharge(m).data, avant)

    def test_captures_reelles_laps_entier_decoupe_et_public_complet(self):
        for creer, tranches in ((captures.odon, ((2,), (1, 1))),
                                (temps.brune_guette, ((34,), (17, 17)))):
            with self.subTest(capture=creer.__name__):
                initial, fins = self.recharge(creer()), []
                for laps in tranches:
                    m, lignes = self.recharge(initial), []
                    for dt in laps:
                        m, nouvelles = vivre(m, dt)
                        lignes.extend(nouvelles)
                        m = self.recharge(m)
                    fins.append((copy.deepcopy(m.data), json.dumps(m.data), lignes,
                                 regarder(m), scene_percue(m), copy.deepcopy(emissions(m))))
                self.assertEqual(*fins)


if __name__ == '__main__':
    unittest.main()
