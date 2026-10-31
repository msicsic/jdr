"""S1o : suivis subjectifs et références aux archives autoritaires, sans copie persistante."""
import copy
import json
import unittest

from donjon import agendas, appel, memoire
from donjon.emissions import lire as emissions
from donjon.esprits import lire, memoriser
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.monde import ErreurMonde
from donjon.temps import ecouler
from tests import test_memoire_socle
from tests.test_memoire_paroles import acces_dits
from tests.test_memoire_refus import inventaire
from tests import test_realisation_datee as realisations
from tests import test_rendez_vous_tenu as rendez_vous
from tests.test_tensions import recharger, relais, vivre

RACINE = test_memoire_socle.RACINE
SUIVIS = {'aides_attendues', 'rejoint', 'rejoindre', 'mandats_percus',
          'services_rendus', 'restitutions'}
ARCHIVES = {'engagements', 'promesses_joueur', 'reference_temporelle',
            'sequence_obligations', 'accord_initial', 'issues_obligations',
            'dettes', 'permissions'}


class MemoireContratsTests(unittest.TestCase):
    def recharge(self, m):
        public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(json.dumps(n.data), json.dumps(m.data))
        self.assertEqual((regarder(n), scene_percue(n), emissions(n)), public)
        return n

    def test_inventaire_ferme_et_alias(self):
        fixture = json.loads((RACINE/'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf8'))
        for nom, registres in (('suivis_s1o', SUIVIS), ('archives_s1o', ARCHIVES)):
            mesures = inventaire(registres)
            if nom == 'suivis_s1o':
                self.assertEqual(mesures['donjon/esprits.py'].pop(
                    '<module>/' + test_memoire_socle.AccesTests.schema_champs()), 1)
            self.assertEqual({f: a for f, a in mesures.items() if a}, fixture[nom])
        # Les deux restes subjectifs sont des dictionnaires produits pour
        # le diagnostic, jamais des accès au stockage d'un esprit vivant.
        self.assertEqual(set(fixture['suivis_s1o']),
                         {'tools/audit_nuits.py', 'tools/detecter_changements_avis.py'})
        self.assertEqual(sum(len(a) for a in fixture['suivis_s1o'].values()), 2)
        for registre in SUIVIS | ARCHIVES:
            for source in (
                f'e["{registre}"]', f'e.get("{registre}")',
                f'cle = "{registre}"; stock = e[cle]; alias = stock; alias[0]["minute"] = 8',
                f'stock = e["{registre}"]; ajouter = stock.append; ajouter(s)',
                f'def fuite(e):\n return e["{registre}"]',
                f'e.update(**{{"{registre}": stock}})', f'del e["{registre}"]',
            ):
                with self.subTest(source=source):
                    self.assertTrue(acces_dits(source, registres={registre}))

    def test_lectures_pures_et_admissions_sans_alias(self):
        m = relais()
        aide = {'qui': 'aubin', 'condition': {'objet': 'brasero', 'allume': True}, 'minute': 0}
        attente = {'qui': 'aubin', 'depuis': 0, 'jusqu_a': 4, 'vient': True}
        venue = {'qui': 'marchand', 'salle': 'crypte', 'depuis': 0, 'jusqu_a': 4}
        memoire.retenir_aide(m, 'marchand', 'brasero', aide)
        memoire.retenir_attente(m, 'marchand', attente)
        memoire.retenir_venue(m, 'aubin', venue)
        avant = copy.deepcopy(m.data)
        aide['condition'].clear(); attente.clear(); venue.clear()
        memoire.aides_attendues(m, 'marchand')['brasero']['condition'].clear()
        memoire.attente_convenue(m, 'marchand').clear()
        memoire.venue_convenue(m, 'aubin').clear()
        for qui in ('absent', 'joueur'):
            self.assertEqual(memoire.aides_attendues(m, qui), {})
            self.assertEqual(memoire.mandats_connus(m, qui), [])
            self.assertEqual(memoire.engagements_connus(m, qui), [])
            self.assertEqual(memoire.issues_connues(m, qui), [])
            self.assertIsNone(memoire.attente_convenue(m, qui))
            self.assertIsNone(memoire.venue_convenue(m, qui))
        self.assertEqual(m.data, avant)
        self.recharge(m)

    def test_reference_archivee_copie_et_oubli_des_episodes(self):
        m = relais()
        engagement = {'pour': 'joueur', 'minute': 0, 'condition': {'objet': 'brasero', 'allume': True}}
        agendas.prendre(m, 'aubin', engagement, limite=6000)
        x, = memoire.engagements_connus(m, 'aubin')
        ref = agendas.reference_temporelle(x)
        avant = copy.deepcopy(m.data)
        x['condition'].clear()
        memoire.reference_contrat(m, 'aubin', ref)['reference_temporelle'].clear()
        self.assertIsNone(memoire.reference_contrat(m, 'brune', ref))
        self.assertEqual(m.data, avant)
        for _ in range(45):
            memoriser(m, 'aubin', {'type': 'attendu'})
        m = self.recharge(m)
        self.assertEqual(memoire.reference_contrat(m, 'aubin', ref)['condition'], engagement['condition'])
        self.assertEqual(m.data['sequence_obligations'], 1)
        self.assertNotIn('contrats_connus', m.data)

    def test_services_restitutions_et_permissions_detaches(self):
        m = relais()
        trace = {'de': 'aubin', 'pour': 'joueur', 'condition': {'objet': 'brasero', 'allume': True}}
        retour = {'a': 'marchand', 'entrees': {'besoins': [], 'moyens': ['briquet'],
                  'pieces': 5, 'contenu': 0, 'proprietaire': 'marchand', 'prix': None}}
        memoire.retenir_service(m, trace)
        memoire.retenir_restitution(m, 'aubin', 'torche', retour)
        # Fixture de prêt réel : les deux participants connaissent leur permission.
        m.data['permissions'] = [{'objet': 'torche', 'a': 'aubin', 'de': 'marchand', 'minute': 0}]
        avant = copy.deepcopy(m.data)
        trace['condition'].clear(); retour['entrees']['moyens'].clear()
        memoire.services_retenus(m, 'aubin')[0]['condition'].clear()
        memoire.restitutions_retenues(m, 'aubin')['torche']['entrees'].clear()
        memoire.permissions_connues(m, 'aubin')[0].clear()
        self.assertEqual(memoire.permissions_connues(m, 'brune'), [])
        self.assertEqual(memoire.services_retenus(m, 'brune'), [])
        self.assertEqual(m.data, avant)
        self.recharge(m)

    def test_mandats_brouillons_imbriques_et_interruption(self):
        m = relais()
        # Fixture explicite : l'épreuve vise l'alias et la frontière de publication,
        # sans inventer un mandat réel dans une partie validée.
        mandat = {'de': 'aubin', 'charge': {'mandant': 'marchand', 'parent': 'a1',
                  'agenda': 'a2', 'sorte': 'amener', 'parametres': {'qui': ['brune'], 'lieu': 'crypte'}},
                  'minute': 0, 'source': 'entendu'}
        avant = copy.deepcopy(m.data)
        with self.assertRaises(RuntimeError):
            with agendas.evaluation(m, 'ilse'):
                memoire.retenir_mandat_percu(m, 'ilse', mandat)
                with agendas.evaluation(m, 'ilse'):
                    recu = memoire.mandats_connus(m, 'ilse')[0]
                    # Une issue révise le même mandat ; ses paramètres font
                    # partie de son identité et ne peuvent servir de détail mutable.
                    recu['croyance'] = {'valeur': 'reussi', 'source': 'vu', 'minute': 0,
                                        'confiance': 1, 'poids': 1}
                    memoire.retenir_mandat_percu(m, 'ilse', recu)
                self.assertEqual(memoire.mandats_connus(m, 'ilse')[0]['croyance']['valeur'], 'reussi')
                raise RuntimeError('choix interrompu')
        self.assertEqual(m.data, avant)
        with agendas.evaluation(m, 'ilse', publier=False):
            memoire.retenir_mandat_percu(m, 'ilse', mandat)
        self.assertEqual(m.data, avant)
        with agendas.evaluation(m, 'ilse'):
            memoire.retenir_mandat_percu(m, 'ilse', mandat)
        attendu = copy.deepcopy(m.data)
        mandat['charge']['parametres']['qui'].clear()
        memoire.mandats_connus(m, 'ilse')[0]['charge'].clear()
        self.assertEqual(m.data, attendu)

    def test_cloture_reelle_distante_ne_devient_pas_connue(self):
        cas = realisations.RealisationDateeTests()
        m, qui, pour, x = cas.verrou()
        from donjon.deplacement_objet import deplacer
        from donjon.moteur import Moteur
        deplacer(m, 'cle_garde_manger', 'joueur')
        ecouler(m, 99)
        avant = agendas.etat_promis(m)
        Moteur._appliquer(m, ('verrouiller', 'garde_manger', 'cle_garde_manger'), [])
        agendas.constater_geste_joueur(m, avant)
        m = self.recharge(m)
        self.assertTrue(agendas.issues_temporelles(m))
        self.assertEqual(memoire.issues_connues(m, qui), [])
        self.assertEqual(memoire.issues_connues(m, pour), [])
        from donjon.biens import rembourser
        rembourser(m, qui, pour, 1, x['condition']['objet'], quoi='tache', informer=False)
        m = self.recharge(m)
        self.assertEqual(memoire.dettes_connues(m, pour), [])
        self.assertTrue(m.data['dettes'])

    def test_deux_cas_reels_meme_laps_et_public_apres_recharge(self):
        from tests.test_gardien_detresse import GardienDetresseTests
        for creer, duree in ((GardienDetresseTests().lumiere, 2),
                             (rendez_vous.RendezVousTenuTests().rendez_vous, 2)):
            with self.subTest(cas=creer.__name__):
                m = self.recharge(creer())
                entier, lignes = vivre(m.copier(), duree, jet=20)
                coupe, suite = m.copier(), []
                for _ in range(duree):
                    coupe, ajout = vivre(self.recharge(coupe), 1, jet=20)
                    suite.extend(ajout)
                self.assertEqual(entier.data, coupe.data)
                self.assertEqual(json.dumps(entier.data), json.dumps(coupe.data))
                # L'aperçu peut dépendre de la saisie ; actes et paroles persistent.
                self.assertEqual(emissions(entier), emissions(coupe))
                self.assertEqual((regarder(entier), scene_percue(entier)),
                                 (regarder(coupe), scene_percue(coupe)))
                self.recharge(entier)
                self.recharge(coupe)

    def test_validations_corruptions_historiques(self):
        for cle, valeur in (('aides_attendues', []), ('rejoint', {}),
                            ('rejoindre', {}), ('mandats_percus', {})):
            m = relais()
            lire(m, 'aubin')[cle] = valeur  # fixture de corruption explicite
            with self.subTest(cle=cle), self.assertRaises(ErreurMonde):
                m.verifier()
