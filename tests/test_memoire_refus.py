"""S1k, première partie : réponses historiques, copies et reprise complète."""
import copy
import gzip
import json
import subprocess
import unittest

from donjon import memoire, pnj
from donjon.deliberation import retenir_refus, refus_retenu, tient
from donjon.echanges import executer
from donjon.emissions import lire as emissions
from donjon.esprits import croire, lire, memoriser
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_memoire_paroles import acces_dits
from tests import test_memoire_socle
from tests.test_proposer_recours import scene
from tests.test_tensions import recharger

REGISTRES = {'refus'}
RACINE = test_memoire_socle.RACINE
RECOURS = {'demande_refusee', 'recours_propositions', 'recours_services',
           'recours_intermediaires', 'service_en_cours'}


def inventaire(registres, revision=None):
    mesures = {}
    for p in [*RACINE.glob('*.py'), *(RACINE / 'donjon').rglob('*.py'), *(RACINE / 'tools').rglob('*.py')]:
        relatif = p.relative_to(RACINE).as_posix()
        if relatif == 'donjon/memoire.py':
            continue
        source = (subprocess.check_output(['git', 'show', f'{revision}:{relatif}'], cwd=RACINE).decode('utf-8-sig')
                  if revision else p.read_text(encoding='utf-8-sig'))
        acces = acces_dits(source, registres=registres)
        if acces:
            mesures[relatif] = {f'{f}/{e}': n for (f, e), n in sorted(acces.items())}
    return mesures


class RefusTests(unittest.TestCase):
    def test_inventaire_ferme_et_contre_epreuves(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf-8'))
        mesures = inventaire(REGISTRES)
        self.assertEqual(mesures['donjon/esprits.py'].pop('<module>/' + test_memoire_socle.AccesTests.schema_champs()), 1)
        self.assertEqual({f: a for f, a in mesures.items() if a}, fixture['refus_homonymes_s1k'])
        self.assertEqual(inventaire(RECOURS), fixture['recours_restants_s1k'])
        for registre in REGISTRES | RECOURS:
            for source in (
                f'e["{registre}"]', f'e.get("{registre}")', f'e.setdefault("{registre}", [])',
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

    def test_vues_pures_admissions_copiees_et_projection(self):
        m = scene()
        offre = {'etat': 'offre', 'debiteur': 'marchand', 'creancier': 'brune',
                 'condition': {'type': 'pieces', 'montant': 3},
                 'contrepartie': {'type': 'objet', 'objet': 'vivres'}}
        retenir_refus(m, 'brune', 'marchand', 'demander', 'mefiance', objet='vivres', contre_offre=offre)
        avant = copy.deepcopy(m.data)
        offre['condition']['montant'] = 999
        for qui in ('brune', 'absent', 'joueur'):
            reponses = memoire.reponses_retenues(m, qui)
            if reponses:
                reponses[0]['contre_offre']['condition'].clear()
            reponses.clear()
        refus_retenu(m, 'brune', 'marchand', ('demander',), 'vivres')['contre_offre'].clear()
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)
        projection = m.copier()
        reponses = memoire.reponses_retenues(m, 'brune')
        memoire.installer_refus_projetes(projection, 'marchand', reponses)
        reponses[0]['contre_offre'].clear()
        self.assertEqual(memoire.reponses_retenues(projection, 'marchand'), memoire.reponses_retenues(m, 'brune'))
        self.assertEqual(m.data, avant)

    def test_ordre_plafond_et_predicats_historiques(self):
        m = scene()
        retenir_refus(m, 'brune', 'marchand', 'demander', 'necessaire', objet='vivres')
        retenir_refus(m, 'brune', 'marchand', 'acheter', 'refus', objet='vivres', prix=2)
        reponses = memoire.reponses_retenues(m, 'brune')
        self.assertEqual([r['operation'] for r in reponses], ['acheter'])
        self.assertEqual(reponses[0]['raison'], 'persuasion')
        for _ in range(45):
            memoriser(m, 'brune', {'type': 'attendu'})
        m.data['minutes'] += 180
        m.data['finances_pnj']['brune'] = 0
        m = recharger(m)
        self.assertEqual(memoire.reponses_retenues(m, 'brune'), reponses)
        self.assertTrue(tient(m, 'brune', reponses[0]))
        # Le délai historique d'un refus d'humeur reste distinct des causes/offres.
        retenir_refus(m, 'brune', 'aubin', 'demander', 'mefiance', objet='vivres')
        humeur = memoire.reponses_retenues(m, 'brune')[-1]
        m.data['minutes'] += 120
        self.assertFalse(tient(recharger(m), 'brune', humeur))

    def test_cause_et_corruptions(self):
        m = scene()
        retenir_refus(m, 'brune', 'marchand', 'enqueter_cause', 'rien', souvenir=False)
        cause = [['signe', 'marchand', 'peur', 0]]
        memoire.retenir_cause_derniere_reponse(m, 'brune', cause)
        cause[0].clear()
        self.assertEqual(memoire.reponses_retenues(m, 'brune')[-1]['cause'], [['signe', 'marchand', 'peur', 0]])
        memoire.verifier_refus(m, 'brune')
        for champ, valeur in (('minute', 1.5), ('condition_tenue', 1), ('cause', [[1]]), ('offre', {})):
            corrompu = m.copier()
            lire(corrompu, 'brune')['refus'][-1][champ] = valeur
            with self.subTest(champ=champ), self.assertRaises(AssertionError):
                memoire.verifier_refus(corrompu, 'brune')

    def verifier_continuite(self, initial):
        resultats = []
        for tranches in ((1200,), (300,) * 4):
            m, lignes = recharger(initial), []
            for dt in tranches:
                pnj.avancer(m, ecouler(m, dt), lignes, dt)
                m = recharger(m)
            public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
            recharge = recharger(m)
            self.assertEqual(recharge.data, m.data)
            self.assertEqual((regarder(recharge), scene_percue(recharge), emissions(recharge)), public)
            resultats.append((copy.deepcopy(m.data), json.dumps(m.data), lignes, public))
        self.assertEqual(*resultats)

    def test_capture_reelle_ilse_et_autre_fourniture(self):
        with gzip.open(RACINE / 'tests/data/offre-sensee-crue7-353.json.gz', 'rt', encoding='utf-8') as f:
            initial = json.load(f)
        for objet in ('bois_guet', 'planches'):
            with self.subTest(objet=objet):
                m = Monde(copy.deepcopy(initial))
                if objet == 'planches':
                    m.objets['bois_guet']['charges'] = 0
                    m.objets[objet].update(lieu='brune', proprietaire='marchand', charges=2)
                    croire(m, 'ilse', objet, 'lieu', 'brune', 'vu', salle='antichambre', case=[5, 4])
                    croire(m, 'ilse', objet, 'etat', {'disponible': True}, 'vu')
                m = recharger(m)
                m.joueur.update(salle='antichambre', position=[6, 4], orientation='nord-ouest')
                m.objets['fanal'].update(allume=True, combustible=60)
                from tests.support import presentes
                presentes(m)
                if 'brasero' not in m.data['connus']:
                    m.data['connus'].append('brasero')
                lignes = []
                geste = {'operation': 'engager', 'cible': 'ilse', 'outil': '', 'lieu': '', 'condition': '',
                         'contenu': {'condition': {'objet': 'brasero', 'allume': True}, 'prix': 5}}
                self.assertFalse(executer(m, 'marchand', geste, lignes))
                m = recharger(m)
                self.assertIn('Ilse refuse', ' '.join(lignes))
                self.assertTrue(refus_retenu(m, 'marchand', 'ilse', ('engager',), 'brasero'))
                self.assertTrue(emissions(m))
                self.verifier_continuite(m)


if __name__ == '__main__':
    unittest.main()
