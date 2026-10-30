"""Les catalogues attestent une connaissance, pas une coïncidence de mots."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon.accords_publics import AccordTerminal, accords_publics, parole_accord
from donjon.banc_pnj import creer
from donjon.dialogues import information_publique, parole_information, preparer_information
from donjon.commandes import DescripteurPublic
from donjon.esprits import croire
from donjon.gestes_publics import gestes_du_monde, rendre_liste
from donjon.monde import ErreurMonde, Monde, objet
from donjon.paroles import _connu_du_joueur, resoudre
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.voix import reel
from tests.test_accords_publics import situation
from tests.test_inventaire_public import etat
from tests.test_parole_corrections import banc
from tests.test_tensions import recharger


class CatalogueConnuTests(unittest.TestCase):
    def verifier_recharge(self, m):
        avant = copy.deepcopy(m.data)
        public = etat(m)
        vues = regarder(m), fiche(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(n.data, avant)
        self.assertEqual(m.data, avant)  # Consulter n'apprend rien.
        self.assertEqual(etat(n), public)
        self.assertEqual((regarder(n), fiche(n), scene_percue(n)), vues)
        return n

    def sujets(self, m):
        return {reel(m, x['id']) for x in information_publique(m)['sujets']}

    def test_scenes_reelles_e6_et_autre_scenario(self):
        for nom, m, secrets, connus in (
            ('huile', situation(False)[0],
             ('atre', 'paillasse_joss', 'coffre_marchand', 'foin', 'bourse_anselme'), ('pot_huile',)),
            ('verrou', situation(True)[0],
             ('atre', 'coffre_marchand', 'foin', 'bourse_anselme'), ('garde_manger',)),
            ('relais', creer('relais', 1985, 'fixe'), ('anneau', 'coffre'), ('porte',)),
        ):
            with self.subTest(scene=nom):
                for id in secrets:
                    self.assertFalse(m.visible(id))
                    self.assertNotIn(id, m.data['connus'])
                    self.assertNotIn(id, m.data.get('souvenirs_visuels', {}))
                    self.assertFalse(_connu_du_joueur(m, id))
                    self.assertIsNone(resoudre(m, id))
                self.assertTrue(set(connus) <= self.sujets(m))
                public = etat(m)
                accord = accords_publics(m)
                terminal = AccordTerminal(accord)
                terminal.etape = 'prestation'
                menus = json.dumps([public['information'], public['accord']], ensure_ascii=False)
                gestes = rendre_liste(gestes_du_monde(m))
                for id in secrets:
                    self.assertNotIn(id, menus)
                    self.assertNotIn(m.objets[id]['nom'], terminal.rendre())
                    self.assertNotIn(m.objets[id]['nom'], gestes)
                n = self.verifier_recharge(m)
                self.assertTrue(set(connus) <= self.sujets(n))
                self.assertTrue(set(secrets).isdisjoint(self.sujets(n)))

    def test_mots_prives_cles_techniques_et_conversation_n_apprennent_rien(self):
        for scenario in ('relais', 'auberge'):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, 'fixe')
                # Même un alias unique, exactement présent dans un dossier
                # public, ne désigne pas ce nouvel objet caché du monde.
                m.objets['secret_365'] = objet('secret_365', 'secret du catalogue',
                    'outil', 'coffre' if scenario == 'relais' else 'coffre_marchand',
                    aliases=['revision'], mobile=True)
                m.data.setdefault('conversation', []).append({
                    'joueur': 'Je suppose un secret du catalogue.',
                    'reponse': 'Une impression de secret du catalogue.', 'nature': 'dialogue'})
                self.assertFalse(_connu_du_joueur(m, 'secret_365'))
                self.assertNotIn('secret_365', json.dumps(etat(m)))
                n = self.verifier_recharge(m)
                self.assertFalse(_connu_du_joueur(n, 'secret_365'))
                # Une connaissance déclarée reste valide, sans donner accès.
                n.data['connus'].append('secret_365')
                n = self.verifier_recharge(n)
                self.assertIn('secret_365', self.sujets(n))
                self.assertFalse(n.accessible('secret_365'))

    def test_reference_physique_et_savoir_prive_ne_sont_pas_des_sources(self):
        m = banc('ressources')
        m.objets['secret_365'] = objet('secret_365', 'opale hors de vue', 'outil', 'crypte')
        croire(m, 'aubin', 'secret_365', 'lieu', 'crypte', 'vu')
        # Un lien d'auteur sur une entité visible n'est pas une perception.
        m.objets['cloche']['support'] = 'secret_365'
        self.assertFalse(_connu_du_joueur(m, 'secret_365'))
        self.assertNotIn('secret_365', self.sujets(m))
        n = self.verifier_recharge(m)
        self.assertFalse(_connu_du_joueur(n, 'secret_365'))

    def test_renseignement_entendu_reste_propose_sans_devenir_presence(self):
        m = banc('noms-dialogue')
        id = 'ressource_365'
        m.objets[id] = {**copy.deepcopy(m.objets['planches']), 'id': id,
                       'nom': 'copeaux du bac', 'aliases': ['bois']}
        m = recharger(m)
        # Le joueur demande une catégorie sans connaître les biens du témoin.
        self.assertFalse(_connu_du_joueur(m, id))
        d = DescripteurPublic({'geste': 'information', 'cible': 'aubin',
                              'parametres': {'acte': 'ressource', 'sujet': 'bois'}})
        with patch.object(Monde, 'd20', return_value=20):
            dossier = preparer_information(m, d)
        n = dossier.travail
        self.assertIn(id, self.sujets(n))
        self.assertIn('copeaux du bac', dossier.reponse['texte'])
        self.assertEqual(n.objets[id], m.objets[id])
        self.assertFalse(n.visible(id))
        # La connaissance ne dépend pas des dix dernières paroles du contexte.
        n.data['conversation'] = []
        for i in range(12):
            from donjon.emissions import enregistrer
            enregistrer(n, 'aubin', acte='parole_archivee', parametres={},
                modalite='constat', evenement={'type': 'parole'}, auditeurs=['joueur'], texte='Oui.')
        n = self.verifier_recharge(n)
        self.assertIn(id, self.sujets(n))

    def test_choix_forge_refuse_et_mission_publique_conservee(self):
        m, d = situation(False)
        avant = copy.deepcopy(m.data)
        cible = d.contenu['cible']
        with self.assertRaises(ErreurMonde) as refus:
            parole_information(m, {'geste': 'information', 'cible': cible,
                'parametres': {'acte': 'ressource', 'sujet': 'bourse_anselme'}})
        self.assertTrue(refus.exception.attendu)
        faux = copy.deepcopy(d.contenu)
        faux['parametres']['prestation'] = {'type': 'part', 'objet': 'foin'}
        with self.assertRaises(ErreurMonde) as refus:
            parole_accord(m, faux)
        self.assertTrue(refus.exception.attendu)
        self.assertEqual(m.data, avant)
        self.verifier_recharge(m)
        from donjon.monde import nouveau_monde
        crypte = nouveau_monde()
        # La prémisse déclare le nom de l'anneau sans l'avoir montré.
        self.assertIn('anneau', self.sujets(crypte))
        self.assertFalse(crypte.visible('anneau'))
        crypte.objets['marchand']['lieu'] = 'crypte'
        self.verifier_recharge(crypte)
        self.assertIn('anneau', self.sujets(crypte))
