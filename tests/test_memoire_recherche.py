"""S1l : négatifs et indices consommés, copies et reprise complète."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon import appel, deliberation, memoire, pnj
from donjon.emissions import lire as emissions
from donjon.esprits import croire, lire, memoriser
from donjon.monde import Monde
from donjon.ouie import _bruit_inconnu
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_memoire_paroles import acces_dits
from tests.test_memoire_refus import inventaire
from tests.test_memoire_socle import AccesTests, RACINE
from tests.test_tensions import recharger, vivre
from tests.test_voix import aubin_cherche_gorm


REGISTRES = {'recherches', 'indices_recherche', 'presence_recherche'}


class RechercheMemoireTests(unittest.TestCase):
    def test_inventaire_ferme_et_contre_epreuves(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf8'))
        mesures = inventaire(REGISTRES)
        self.assertEqual(mesures['donjon/esprits.py'].pop('<module>/' + AccesTests.schema_champs()), 1)
        self.assertEqual({f: a for f, a in mesures.items() if a}, fixture['recherche_homonymes_s1l'])
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

    def test_vues_pures_et_copies_imbriquees_aux_deux_frontieres(self):
        m = aubin_cherche_gorm()
        croire(m, 'aubin', 'marchand', 'lieu', 'beffroi', 'entendu', salle='beffroi', case=[1, 1])
        indice = ['bruit', 3, 'marchand', [2, 2]]
        memoire.indice_recherche(m, 'aubin', 'beffroi', 'marchand', indice=indice)
        memoire.recherche_vaine(m, 'aubin', 'marchand', 'beffroi')
        avant = copy.deepcopy(m.data)
        indice[-1].clear()
        for qui in ('aubin', 'absent', 'joueur'):
            recherches = memoire.recherches_retenues(m, qui)
            if recherches:
                next(iter(recherches.values())).clear()
            memoire.lieux_ecartes(m, qui, 'marchand').clear()
            indices = memoire.indices_recherche_consommes(m, qui, 'marchand')
            for valeurs in indices.values():
                for valeur in valeurs:
                    if isinstance(valeur[-1], list):
                        valeur[-1].clear()
                valeurs.clear()
            presence = memoire.presence_recherche_retenue(m, qui, 'marchand')
            if presence:
                presence[-1].clear()
            memoire.appels_vains(m, qui, 'marchand').clear()
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)

    def test_negatifs_indices_et_hypothese_survivent_ensemble(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'entendu', salle='beffroi', case=[1, 1])
                m.data['minutes'] += 20
                memoire.consommer_hypothese(m, 'aubin', cible)
                self.assertTrue(memoire.hypothese_consommee(m, 'aubin', cible))
                deliberation.recherche_vaine(m, 'aubin', cible, 'beffroi')
                deliberation.recherche_vaine(m, 'aubin', cible, 'echoppe')
                indices = memoire.indices_recherche_consommes(m, 'aubin', cible)
                presence = memoire.presence_recherche_retenue(m, 'aubin', cible)
                for _ in range(45):
                    memoriser(m, 'aubin', {'type': 'attendu'})
                for _ in range(3):
                    croire(m, 'aubin', cible, 'lieu', None, 'essai', salle=None, case=None)
                    m = recharger(m)
                self.assertEqual(memoire.indices_recherche_consommes(m, 'aubin', cible), indices)
                self.assertEqual(memoire.presence_recherche_retenue(m, 'aubin', cible), presence)
                self.assertTrue(memoire.hypothese_consommee(m, 'aubin', cible))
                # Même contenu relayé : rien ne se rouvre.
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'dit:ilse', salle='beffroi', case=[1, 1],
                       origine={'source': 'entendu', 'minute': 0})
                m = recharger(m)
                self.assertEqual(memoire.appels_vains(m, 'aubin', cible), {'beffroi', 'echoppe'})
                self.assertTrue(memoire.hypothese_consommee(m, 'aubin', cible))
                # Une nouvelle case positive rouvre son lieu seul.
                croire(m, 'aubin', cible, 'lieu', 'beffroi', 'entendu', salle='beffroi', case=[2, 1])
                m = recharger(m)
                self.assertEqual(memoire.appels_vains(m, 'aubin', cible), {'echoppe'})
                self.assertFalse(memoire.hypothese_consommee(m, 'aubin', cible))

    def test_migration_ancienne_et_validation_sans_reapprentissage(self):
        m = aubin_cherche_gorm()
        croire(m, 'aubin', 'marchand', 'lieu', 'beffroi', 'entendu', salle='beffroi', case=[1, 1])
        _bruit_inconnu(m, 'aubin', 'beffroi', 'pas', 3)
        for minute in (3, 8, 5):
            memoriser(m, 'aubin', {'type': 'appel_sans_reponse', 'qui': 'marchand',
                                  'salle': 'beffroi', 'minute': minute})
        for registre in REGISTRES:
            lire(m, 'aubin').pop(registre)
        m = recharger(Monde(copy.deepcopy(m.data)))
        self.assertEqual(memoire.lieux_ecartes(m, 'aubin', 'marchand'), {'beffroi': 8})
        self.assertTrue(memoire.indices_recherche_consommes(m, 'aubin', 'marchand')['beffroi'])
        avant = copy.deepcopy(m.data)
        self.assertEqual(recharger(m).data, avant)
        for registre, valeur in (('recherches', {'marchand': {'beffroi': 1.5}}),
                                 ('indices_recherche', {'marchand': {'beffroi': [['presence', 3, None]]}}),
                                 ('presence_recherche', {'marchand': ['inconnu', None]})):
            copie = m.copier()
            lire(copie, 'aubin')[registre] = valeur
            with self.subTest(registre=registre), self.assertRaises(AssertionError):
                memoire.verifier_recherches(copie, 'aubin')

    def test_inspection_et_retrouvailles_ne_confondent_pas_audition_et_presence(self):
        for cible in ('marchand', 'joueur'):
            with self.subTest(cible=cible):
                m = aubin_cherche_gorm()
                salle = m.objets['aubin']['lieu']
                m.data['salles'][salle]['lumiere_naturelle'] = 2
                if cible != 'joueur':
                    from donjon.corps import endormir
                    endormir(m, cible)
                croire(m, 'aubin', cible, 'lieu', salle, 'entendu', salle=salle,
                       case=list(m.objets['aubin']['position']))
                pnj._inspecter(m, 'aubin', cible)
                m = recharger(m)
                self.assertIn(salle, memoire.appels_vains(m, 'aubin', cible))
                self.assertTrue(memoire.indices_recherche_consommes(m, 'aubin', cible))
                contact = m.joueur['salle'] if cible == 'joueur' else m.objets[cible]['lieu']
                memoire.recherche_vaine(m, 'aubin', cible, contact)
                appel.entendre(m, 'aubin', cible, appel.ARRIVE, [], appelant=True, entendu=False)
                self.assertIn(contact, memoire.appels_vains(m, 'aubin', cible))
                appel.entendre(m, 'aubin', cible, appel.ARRIVE, [], appelant=True)
                m = recharger(m)
                self.assertNotIn(contact, memoire.appels_vains(m, 'aubin', cible))
                self.assertIn(salle, memoire.appels_vains(m, 'aubin', cible))

    def test_deux_captures_historiques_etat_rendu_scene_paroles(self):
        for nom in ('mine-7-470', 'auberge-7-625'):
            with self.subTest(capture=nom):
                chemin = Path(__file__).with_name('data') / f'appels-restes-{nom}.json.gz'
                initial = recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))
                resultats = []
                for tranches in ((10,), (4, 6)):
                    m, lignes = recharger(initial), []
                    for dt in tranches:
                        m, nouvelles = vivre(m, dt)
                        lignes.extend(nouvelles)
                        m = recharger(m)
                    public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
                    recharge = recharger(m)
                    self.assertEqual(recharge.data, m.data)
                    self.assertEqual((regarder(recharge), scene_percue(recharge), emissions(recharge)), public)
                    resultats.append((copy.deepcopy(m.data), json.dumps(m.data), lignes, public))
                self.assertEqual(*resultats)


if __name__ == '__main__':
    unittest.main()
