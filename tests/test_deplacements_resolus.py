"""G7 : gestes réellement accomplis, sons séparés, trajet partiel et disque."""
import copy
import io
import json
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import jeu
from donjon.commandes import DescripteurPublic
from donjon.deplacements import phrases
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.narration import attestations, segments_etablis, rendre_resultat, segments
from donjon.rendu import regarder
from donjon.carte import carte
from donjon.scene import scene_percue
from donjon.temps import instant
from tests import test_recit_resultat as recit
from tests.test_trainer import scene as corps_a_trainer
from tests.test_tensions import recharger


def pas(direction, restants, identifiant='trajet-343'):
    return DescripteurPublic({'geste': 'marcher', 'cible': direction,
                              'parametres': {'parcours': {'id': identifiant, 'pas': restants}}})


class DeplacementsResolusTests(unittest.TestCase):
    def recharge(self, m, texte):
        vues = regarder(m), scene_percue(m), carte(m)
        data = copy.deepcopy(m.data)
        r = recharger(m)
        self.assertEqual(r.data, data)
        self.assertEqual((regarder(r), scene_percue(r), carte(r)), vues)
        self.assertEqual(rendre_resultat('\n'.join(r.data['journal'][-1]['faits'])), rendre_resultat(texte))
        rendu = phrases(r.data['journal'][-1]['deplacements'])
        for phrase in rendu:
            self.assertIn(phrase, texte)
            self.assertTrue(set(segments(phrase)) <= set(attestations(r, r.contexte())))
            self.assertTrue(segments_etablis(phrase, {'attestations': rendu}))
        return r

    def executer(self, m, p):
        moteur = Moteur(m)
        texte = moteur.executer(moteur.preparer(p))
        return self.recharge(m, texte), texte

    def test_fuite_reelle_et_autre_depart_sons_distincts(self):
        for position, nombre in (([1, 5], 3), ([1, 4], 2)):
            with self.subTest(position=position):
                m = recit.RecitResultatTests().scene_banc('force-4c-fuir')
                m.joueur['position'] = position
                from donjon.defense import chemin_fuite
                destination = chemin_fuite(m, '')[-1][:2]
                debut = instant(m)
                m, texte = self.executer(m, proposition('fuir'))
                d = m.data['journal'][-1]['deplacements']
                self.assertEqual(sum(g['quantite'] for g in d['mouvements']), nombre)
                self.assertTrue(all(g['acteur'] == 'joueur' and g['unite'] == 'pas' for g in d['mouvements']))
                self.assertEqual((d['mouvements'][0]['debut'], d['mouvements'][-1]['fin']), (debut, instant(m)))
                self.assertEqual(len(phrases(d)), 1)
                self.assertIn(f'Tu as avancé de {nombre} pas', texte)
                self.assertIn("Tu entends des pas à l'ouest.", texte.splitlines())
                self.assertNotIn("Tu avances d'un pas.", texte)
                self.assertEqual((m.joueur['salle'], tuple(m.joueur['position'])), (destination[0], tuple(destination[1])))

    def test_trois_pas_arretes_au_deuxieme_et_nouveau_geste(self):
        m, _ = corps_a_trainer()
        debut = instant(m)
        for directions in (['est', 'est', 'est'], ['est', 'est']):
            m, texte = self.executer(m, pas('est', directions))
        d = m.data['journal'][-1]['deplacements']
        self.assertEqual(len(d['mouvements']), 1)
        self.assertEqual(len(d['total']), 2)
        self.assertEqual(d['reste'], 1)
        self.assertEqual(d['cumul'][0]['quantite'], 2)
        self.assertEqual((d['cumul'][0]['debut'], d['cumul'][0]['fin']), (debut, instant(m)))
        self.assertIn('1 étape de déplacement non exécutée', texte)
        self.assertEqual(m.joueur['position'], [5, 5])
        m, texte = self.executer(m, pas('est', ['est'], 'autre-clic'))
        self.assertIn('Tu as avancé de 1 pas', texte)
        self.assertEqual(len(m.data['journal'][-1]['deplacements']['total']), 1)

    def test_refus_et_faisabilite_ne_deplacent_pas(self):
        m, _ = corps_a_trainer()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(pas('inconnu', ['inconnu']))
        # Le nord-est coupe ici un véritable mur : trajet bien formé, refus
        # physique avant le premier mouvement, sans journal accompli.
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(pas('nord-est', ['nord-est']))
        self.assertEqual(m.data, avant)
        p = Moteur(m).preparer(pas('est', ['est'])); p.resume(m)
        self.assertEqual(m.data, avant)
        self.assertFalse(phrases({}))
        from tests.test_audits_attendu import jouer
        from tests.test_relances_luna import action
        r, texte, _ = jouer(m, 'puis-je avancer vers est ?', [action(proposition('marcher', 'est'))], [])
        self.assertEqual(r.joueur, m.joueur)
        self.assertEqual(r.data['journal'], m.data['journal'])
        self.assertNotIn('Tu as avancé', texte)

    def test_trainer_et_obstacle_metres_reels(self):
        for scenario in ('relais', 'auberge'):
            m, cible = corps_a_trainer(scenario)
            depart = m.joueur['position'][:]
            m, texte = self.executer(m, proposition('trainer', cible, 'est'))
            self.assertEqual(m.objets[cible]['position'], depart)
            d = m.data['journal'][-1]['deplacements']
            self.assertEqual([(x['acteur'], x['quantite'], x['unite']) for x in d['mouvements']], [('joueur', 1.0, 'mètre')])
            self.assertIn('Tu as avancé de 1 mètre vers est en 4,5 secondes.', texte)
        from tests.test_sous_obstacle import scene, passage
        m = scene()
        m, texte = self.executer(m, passage())
        self.assertEqual(m.data['journal'][-1]['deplacements']['cumul'][0]['quantite'], 2)
        self.assertIn('Tu as avancé de 2 mètres vers est', texte)

    def test_console_g4_sauvee_avant_affichage_sans_recit(self):
        t = recit.RecitResultatTests()
        m = t.scene_banc('force-4c-fuir')
        r, resultat, _ = t.console(m, proposition('fuir'), 'Puis-je fuir par la sortie connue ?')
        self.assertIn('Tu as avancé de 3 pas', resultat)
        self.recharge(r, resultat)

    def test_ponts_web_terminal_meme_cumul_sur_disque(self):
        from donjon.web.pont import PontWeb
        from donjon.tui import PontTerminal
        for pont in (PontWeb(), PontTerminal(MagicMock(is_running=False))):
            with self.subTest(pont=type(pont).__name__), tempfile.TemporaryDirectory() as tmp:
                m, _ = corps_a_trainer()
                fichier = Path(tmp) / 'clic.json'; m.sauver(fichier)
                commandes = iter([pas('est', ['est', 'est', 'est']), pas('est', ['est', 'est']), 'quitter'])
                captures = []
                def afficher(*valeurs, **options):
                    texte = ' '.join(map(str, valeurs))
                    if 'Tu as avancé' in texte:
                        r = Monde.charger(fichier)
                        self.assertIn(texte, '\n'.join(r.data['journal'][-1]['faits']))
                        captures.append(texte)
                with (patch.object(pont, 'lire', side_effect=lambda *_: next(commandes)),
                      patch.object(pont, 'ecrire', side_effect=afficher),
                      patch('sys.stdout', io.StringIO())):
                    jeu.main(['--offline', '--save', str(fichier)], interface=pont)
                r = Monde.charger(fichier)
                self.assertEqual(len(captures), 2)
                self.assertIn('Tu as avancé de 2 pas', captures[-1])
                self.recharge(r, '\n'.join(r.data['journal'][-1]['faits']))

    def test_clic_reel_interrompu_par_une_nouvelle_personne(self):
        from donjon.gestes_publics import catalogue_public
        from donjon.spatial import memoriser
        from tests.test_tensions import placer
        m, _ = corps_a_trainer()
        # Un autre personnage reste hors du cône initial, puis la marche le
        # fait entrer dans le champ. Aucun effet du navigateur.
        placer(m, 'marchand', 'antichambre', (4, 1))
        for orientation in ('nord', 'sud', 'est', 'ouest'):
            m.joueur['orientation'] = orientation; memoriser(m)
        m.joueur['orientation'] = 'est'
        def etat():
            return dict(type='etat', salle='', pv=1, or_=0, minutes=0, connexion='', fiche='',
                        proposition='', scene=scene_percue(m), catalogue_gestes=catalogue_public())
        initial = etat()
        def page(etat):
            r = subprocess.run(['node', 'tests/clic_page.js', 'donjon/web/page.html'], input=json.dumps(etat),
                               text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            return json.loads(r.stdout)
        choix = page(initial)
        trajet, destination = choix['chemin'], choix['cible']
        self.assertGreater(len(trajet), 1)
        initiaux = {o['id'] for n in initial['scene']['niveaux'] for o in n['objets'] if o['type'] == 'personnage'}
        etats = []
        for i, direction in enumerate(trajet):
            reste = trajet[i:]
            m, texte = self.executer(m, pas(direction, reste, 'clic-reel'))
            etats.append(etat())
            presents = {o['id'] for n in etats[-1]['scene']['niveaux'] for o in n['objets'] if o['type'] == 'personnage'}
            if presents - initiaux:
                break
        finaux = {o['id'] for n in etats[-1]['scene']['niveaux'] for o in n['objets'] if o['type'] == 'personnage'}
        self.assertTrue(finaux - initiaux)
        self.assertLess(len(etats), len(trajet))
        # Le vrai algorithme JS reçoit les états issus de ses propres commandes.
        initial['sonde_marche'] = {'cible': destination, 'etats': etats}
        marche = page(initial)['marche']
        self.assertTrue(marche['interrompue'])
        self.assertEqual(len(marche['envois']), len(etats))
        self.assertEqual([e['cible'] for e in marche['envois']], trajet[:len(etats)])
        self.assertIn('parcours', marche['envois'][0]['parametres'])
        self.assertEqual(m.data['journal'][-1]['deplacements']['reste'], len(trajet) - len(etats))
        self.assertIn('de déplacement non exécutée', texte)

    def test_reprise_exacte_sans_audit_et_faux_total_non_prouve(self):
        from tests.test_audits_attendu import jouer
        from tests.test_repli_et_appel import dialogue
        m, _ = corps_a_trainer()
        m, _ = self.executer(m, pas('est', ['est']))
        phrase = phrases(m.data['journal'][-1]['deplacements'])[0]
        r, sortie, appels = jouer(m, 'rappelle mon déplacement', [dialogue(phrase)], [])
        self.assertEqual([f for f, _ in appels], ['repondre_au_joueur'])
        self.assertIn(phrase, sortie)
        self.assertEqual(r.joueur, m.joueur)
        self.assertFalse(segments_etablis(phrase.replace('1 pas', '9 pas'),
                                          {'attestations': attestations(m, m.contexte())}))
