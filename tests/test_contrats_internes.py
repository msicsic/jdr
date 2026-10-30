"""N10 : mêmes gardes sur l'avis impossible et l'explication d'un refus."""
import copy
import unittest

from donjon.narration import voix_auteur, controler, consigner, segments
from donjon.rendu import regarder
from tests.test_audits_attendu import jouer, ligne, rapport
from pathlib import Path
import json
import tempfile
from donjon.monde import Monde, ErreurMonde
from tools.banc_parties import preparer
from tests.test_relances_luna import action, avis
from tests.test_repli_et_appel import dialogue


ATELIER = ("Tu cherches une pierre mobile pour caler une échelle, mais rien dans ce que tu vois ne permet d’en identifier une. "
           "Examiner le sol ne constitue pas une recherche ; il faudrait que le moteur fournisse un geste de fouille ou de recherche adapté.")
RELAIS = ("Tu ne vois aucun pied-de-biche ici. Le moteur n’en reconnaît pas comme un objet présent ; "
          "tu peux seulement prendre un objet que tu vois ou dont tu connais précisément l’identifiant.")


def banc(nom):
    donnees = json.loads((Path(__file__).parent / 'data' / 'bancs' / f'{nom}.json').read_text(encoding='utf-8'))
    donnees.setdefault('preparation', {})
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / 'partie.json'
        preparer(donnees, chemin)
        m = Monde.charger(chemin)
    if nom == 'atelier':
        m.joueur.update(salle='cour', position=[3, 2], orientation='est')
    return m


class ContratsInternesTests(unittest.TestCase):
    def assertMonde(self, avant, reprise):
        self.assertEqual(reprise.objets, avant.objets)
        self.assertEqual(reprise.joueur, avant.joueur)
        self.assertEqual(reprise.data['minutes'], avant.data['minutes'])
        self.assertEqual(reprise.data['journal'], avant.data['journal'])
        self.assertEqual(regarder(reprise), regarder(avant))
        self.assertFalse(any(voix_auteur(n['texte']) for n in reprise.data.get('narrations_mj', [])))

    def test_atelier_avis_apres_contre_revue(self):
        m = banc('atelier')
        avant = copy.deepcopy(m)
        bon = "Tu ne distingues pas de pierre mobile ici."
        reprise, sortie, appels = jouer(m, "je cherche une pierre pour caler une échelle", [
            # G5 / rapport 323 : une perception seule n'est plus contre-revue.
            # Un geste physique infidèle garde ce contrôle et les mêmes refus d'avis.
            action({'action': 'prendre', 'cible': 'ficelle', 'outil': '', 'methode': 'simple',
                    'difficulte': 0, 'justification': ''}),
            avis('impossible', ATELIER), avis('impossible', bon)],
            [rapport(ligne('neutre'), ligne('neutre')), rapport(ligne('neutre'))],
            [{'conforme': False, 'motif': 'Ce plan prend la ficelle sans chercher une pierre.'}])
        self.assertNotIn(ATELIER, sortie)
        self.assertIn(bon, sortie)
        correction = [e for f, e in appels if f == 'repondre_au_joueur'][-1]
        self.assertTrue(any(r['partie'] == 'justification' and 'moteur' in r['attendu']
                            for r in correction['controle_narratif']))
        self.assertMonde(avant, reprise)

    def test_relais_dialogue_apres_refus_du_monde(self):
        m = banc('relais')
        avant = copy.deepcopy(m)
        reprise, sortie, appels = jouer(m, 'je prends le pied-de-biche', [
            action({'action': 'composer', 'justification': '', 'etapes': [
                {'operation': 'deplacer', 'cible': 'pied-de-biche', 'destination': 'joueur',
                 'outil': '', 'methode': 'simple', 'difficulte': 0}]}),
            dialogue(RELAIS), dialogue('Tu ne vois rien de tel ici.')],
            [rapport(ligne('neutre'), ligne('neutre'))])
        self.assertNotIn(RELAIS, sortie)
        self.assertNotIn('moteur', sortie.split('Le MJ réfléchit')[-1].lower())
        self.assertNotIn('identifiant', sortie.lower())
        self.assertIn('Tu ne vois rien de tel ici.', sortie)
        # G2 : le dialogue de correction n'est ni audité ni lu ; le refus public répond.
        self.assertEqual([f for f, _ in appels], ['repondre_au_joueur'] * 2)
        correction = [e for f, e in appels if f == 'repondre_au_joueur'][-1]
        self.assertIn('retour_moteur', correction['faits'])
        self.assertNotIn('controle_narratif', correction)
        self.assertMonde(avant, reprise)

    def test_categorie_et_emplois_ordinaires(self):
        for texte in (ATELIER, RELAIS, 'Le moteur ne peut pas accepter cette proposition.',
                      'Ce champ interne manque.', 'Le schéma JSON exige une cible.'):
            with self.subTest(texte=texte):
                self.assertTrue(voix_auteur(texte))
        for texte in ('Le moteur du moulin fournit la force.', 'Le champ est couvert de fleurs.',
                      'Tu lis un identifiant sur le registre.', 'Tu dessines un schéma sur le sable.',
                      '« Le moteur exige un identifiant interne. »'):
            with self.subTest(texte=texte):
                self.assertFalse(voix_auteur(texte))

    def test_ecriture_refait_le_garde_malgre_audit_favorable(self):
        for texte in (ATELIER, RELAIS):
            with self.subTest(texte=texte):
                m = banc('atelier')
                avant = copy.deepcopy(m.data)
                audit = controler(texte, rapport(*(ligne('neutre') for _ in segments(texte))), {})
                audit.update(texte_initial=texte, faits={}, fondement='')
                with self.assertRaises(ErreurMonde):
                    consigner(m, {'texte': texte, '_audit': audit})
                self.assertEqual(m.data, avant)

    def test_obstacle_et_mot_ordinaire_persistent(self):
        for texte in ('Tu ne distingues rien de plus dans cette lumière.',
                      'Le champ est couvert de fleurs.'):
            with self.subTest(texte=texte):
                m = banc('atelier')
                avant = copy.deepcopy(m)
                reprise, sortie, _ = jouer(m, 'que vois-tu ?', [dialogue(texte)],
                                           [rapport(ligne('neutre'))])
                self.assertIn(texte, sortie)
                self.assertEqual(reprise.data['narrations_mj'][-1]['texte'], texte)
                self.assertMonde(avant, reprise)
