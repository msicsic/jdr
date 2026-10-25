"""Repères du regard courant : console, MJ simulé, sauvegarde et seconde lecture."""
import copy
import unittest

from donjon.localisation import orientation_relative
from donjon.monde import ErreurMonde
from donjon.narration import consigner, controler, orientations, voix_auteur
from donjon.spatial import memoriser
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_regard_joueur import faire, relais
from tests.test_repli_et_appel import dialogue
from tests.test_sous_obstacle import scene
from tests.test_tensions import recharger


class OrientationNarrativeTests(unittest.TestCase):
    def derriere(self, m, cible):
        memoriser(m)
        souvenir = copy.deepcopy(m.data['souvenirs_visuels'][cible])
        faire(m, 'tourner ouest')
        m = recharger(m)
        self.assertEqual(m.joueur['orientation'], 'ouest')
        self.assertFalse(m.visible(cible))
        self.assertEqual(m.data['souvenirs_visuels'][cible], souvenir)
        return m

    def verifier_chaine(self, m, cible, nom):
        m = self.derriere(m, cible)
        mauvais = f'{nom} se trouve à un mètre vers l’est de toi, devant toi.'
        bon = f'{nom} était à un mètre vers l’est ; cette dernière position connue est derrière toi, hors de vue.'
        # L'auditeur admet volontairement la contradiction comme dans le cas réel.
        r, sortie, appels = jouer(m, f'où est {nom} ?', [dialogue(mauvais), dialogue(bon)], [
            rapport(ligne('mecanique', sources=['souvenirs_visuels'])),
            rapport(ligne('mecanique', sources=['souvenirs_visuels']))])
        self.assertNotIn(mauvais, sortie)
        self.assertNotIn(mauvais, str(r.data['conversation']))
        self.assertIn(bon, sortie)
        self.assertIn(bon, str(r.data['narrations_mj']))
        self.assertEqual(r.joueur['orientation'], 'ouest')
        self.assertEqual(r.joueur['position'], m.joueur['position'])
        self.assertEqual(r.objets[cible], m.objets[cible])
        correction = next(e['controle_narratif'] for _, e in appels if 'controle_narratif' in e)
        self.assertIn('derriere', correction[0]['attendu'])
        self.assertNotIn(correction[0]['attendu'], sortie)
        faits = next(e['faits'] for f, e in appels if f == 'repondre_au_joueur')
        s = next(o for o in faits['souvenirs_visuels'] if o['id'] == cible)
        self.assertEqual(s['orientation_relative'], ['derriere'])
        # L'absolu reste libre, sans dépendre d'une ancienne orientation.
        absolu = f'{nom} a été vu à un mètre vers l’est.'
        rr, texte, _ = jouer(r, f'où est {nom} ?', [dialogue(absolu)], [
            rapport(ligne('mecanique', sources=['souvenirs_visuels']))])
        self.assertIn(absolu, texte)
        self.assertIn(absolu, str(rr.data['conversation']))
        self.assertEqual(rr.objets[cible], r.objets[cible])

    def test_cas_reel_poutre_apres_demi_tour(self):
        self.verifier_chaine(scene(), 'poutre_conduite', 'La poutre effondrée')

    def test_pronom_relie_a_la_cible_unique_de_la_demande(self):
        for m, cible, nom in ((scene(), 'poutre_conduite', 'la poutre effondrée'),
                              (self.personnage(), 'ilse', 'Ilse')):
            with self.subTest(cible=cible):
                m = self.derriere(m, cible)
                mauvais = 'Tu l’avais vue à environ un mètre vers l’est, devant toi.'
                bon = 'Tu l’avais vue à environ un mètre vers l’est, derrière toi.'
                r, sortie, appels = jouer(m, f'où est {nom} ?', [dialogue(mauvais), dialogue(bon)], [
                    rapport(ligne('mecanique', sources=['souvenirs_visuels'])),
                    rapport(ligne('mecanique', sources=['souvenirs_visuels']))])
                self.assertNotIn(mauvais, sortie)
                self.assertIn(bon, sortie)
                self.assertIn(bon, str(r.data['conversation']))
                self.assertEqual(appels[0][1]['faits']['reperes_demandes'], [cible])
                self.assertEqual(r.objets[cible], m.objets[cible])

    def personnage(self):
        m = relais()
        m.joueur.update(position=[2, 5], orientation='est')
        m.objets['ilse'].update(lieu='antichambre', position_salle='antichambre', position=[3, 5])
        return m

    def test_personnage_vu_de_face_puis_dans_le_dos(self):
        m = relais()
        m.joueur.update(position=[2, 5], orientation='est')
        m.objets['ilse'].update(lieu='antichambre', position_salle='antichambre', position=[3, 5])
        if 'ilse' not in m.data.setdefault('noms_connus', []):
            m.data['noms_connus'].append('ilse')
        self.verifier_chaine(m, 'ilse', 'Ilse')

    def test_huit_regards_et_quatre_demi_plans_apres_recharge(self):
        m = recharger(scene())
        from donjon.spatial import VECTEURS
        salle = m.joueur['salle']
        x, y = m.joueur['position']
        for regard, (fx, fy) in VECTEURS.items():
            m.joueur['orientation'] = regard
            for dx, dy, attendu in ((fx, fy, 'devant'), (-fx, -fy, 'derriere'),
                                    (fy, -fx, 'gauche'), (-fy, fx, 'droite')):
                with self.subTest(regard=regard, attendu=attendu):
                    self.assertEqual(orientation_relative(m, salle, [x+dx, y+dy]), [attendu])

    def test_gauche_droite_visibles_console_et_recharge(self):
        for regard, cote, contraire in (('nord', 'droite', 'gauche'), ('sud', 'gauche', 'droite')):
            with self.subTest(regard=regard):
                m = scene()
                memoriser(m)
                faire(m, 'tourner ' + regard)
                m = recharger(m)
                bon = f'La poutre effondrée est à ta {cote}.'
                mauvais = f'La poutre effondrée est à ta {contraire}.'
                r, sortie, _ = jouer(m, 'où est la poutre effondrée ?', [dialogue(mauvais), dialogue(bon)], [
                    rapport(ligne('mecanique', sources=['objet:poutre_conduite'])),
                    rapport(ligne('mecanique', sources=['objet:poutre_conduite']))])
                self.assertIn(bon, sortie)
                self.assertNotIn(mauvais, sortie)
                self.assertIn(bon, str(r.data['conversation']))
                self.assertEqual(r.objets['poutre_conduite'], m.objets['poutre_conduite'])
                self.assertEqual(r.joueur['orientation'], regard)

    def test_verdict_ambiance_neutralite_citations_et_cible_ambigue(self):
        m = self.derriere(scene(), 'poutre_conduite')
        faits = m.contexte()
        faux = 'La poutre effondrée est devant toi.'
        for verdict in ('ambiance', 'neutre', 'mecanique'):
            self.assertTrue(controler(faux, rapport(ligne(verdict, sources=['souvenirs_visuels'])), faits)['obstacles'])
        self.assertFalse(orientations('La poutre effondrée est dans ton dos.', faits))
        self.assertFalse(orientations('Quelqu’un dit : « La poutre effondrée est devant toi. »', faits))
        self.assertFalse(orientations('Elle est devant toi.', faits))
        self.assertFalse(orientations('La poutre effondrée et la lanterne sont devant toi.', faits))
        negatif = orientations('La poutre effondrée n’est pas derrière toi.', faits)
        self.assertFalse(negatif)  # La portée d'une négation appartient à l'audit sémantique.

    def test_souvenir_mobile_ne_revele_pas_la_position_cachee(self):
        m = relais()
        m.joueur.update(position=[2, 5], orientation='est')
        m.objets['ilse'].update(lieu='antichambre', position_salle='antichambre', position=[3, 5])
        memoriser(m)
        m.joueur['orientation'] = 'ouest'
        avant = m.contexte()['souvenirs_visuels']
        m.objets['ilse']['position'] = [4, 4]
        self.assertEqual(m.contexte()['souvenirs_visuels'], avant)

    def test_garde_refait_si_le_regard_change_avant_enregistrement(self):
        m = scene()
        faits = m.contexte()
        texte = 'La poutre effondrée est devant toi.'
        a = controler(texte, rapport(ligne('mecanique', sources=['salle'])), faits)
        self.assertFalse(a['obstacles'])
        a.update(texte_initial=texte, faits=faits, fondement='poutre effondrée')
        m.joueur['orientation'] = 'ouest'
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            consigner(m, {**dialogue(texte), '_audit': a})
        self.assertEqual(m.data, avant)

    def test_meta_refus_et_refus_dans_la_fiction_parlee(self):
        self.assertTrue(voix_auteur('Le refus du moteur ne signifie pas qu’il y en a un ici.'))
        self.assertFalse(voix_auteur('Aubin dit : « Mon refus tient toujours. »'))

    def test_meta_refus_corrige_console_et_rechargement(self):
        for mauvais in ('Le refus du MJ ne signifie pas qu’il y en a un ici.',
                         'Ce refus du moteur ne prouve rien sur ce qui se trouve ici.'):
            with self.subTest(mauvais=mauvais):
                bon = 'Tu peux regarder autour de toi.'
                r, sortie, appels = jouer(recharger(scene()), 'où est le pied-de-biche ?',
                    [dialogue(mauvais), dialogue(bon)],
                    [rapport(ligne('neutre')), rapport(ligne('neutre'))])
                self.assertNotIn(mauvais, sortie)
                self.assertNotIn(mauvais, str(r.data['conversation']))
                self.assertIn(bon, sortie)
                self.assertIn(bon, str(r.data['narrations_mj']))
                self.assertTrue(any('controle_narratif' in e for _, e in appels))
