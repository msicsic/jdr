"""394 : dons et restitutions suivent la gravité U-C, sans modèle."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import jeu
from donjon.biens import preter
from donjon.commandes import DescripteurPublic, analyser
from donjon.consentement import plan_lourd
from donjon.dialogues import comptes_publics
from donjon.geometrie import cases, distance, position_objet
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.noms import reference
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer, orientation_vers
from donjon.web.pont import PontWeb
from tests.test_promesses import aupres_de_gorm, refuge
from tests.support import mj_simule


def etat(m):
    return json.loads(json.dumps({k: v for k, v in m.data.items() if k != 'conversation'}))


def vues(m):
    return fiche(m), regarder(m), scene_percue(m), comptes_publics(m)


class DonConsentementTests(unittest.TestCase):
    def test_dons_et_restitutions_console_web_avant_effet_et_apres_recharge(self):
        for transport in ('console', 'web'):
            for restitution in (False, True):
                for fabrique, objet, qui, saisie in (
                    (aupres_de_gorm, 'cloche', 'marchand', 'je donne la cloche à Gorm'),
                    (refuge, 'couteau', 'brune', 'je remets le couteau à Brune'),
                ):
                    with self.subTest(transport=transport, restitution=restitution, objet=objet):
                        m = fabrique()
                        # Mettre Corvus au contact du destinataire et face à lui,
                        # dans le vrai mode spatial utilisé par le navigateur.
                        cible = position_objet(m, m.objets[qui])
                        position = next(p for p in sorted(cases(m.data['salles'][m.joueur['salle']]))
                                        if distance(p, cible) == 1)
                        m.joueur.update(position=list(position), position_salle=m.joueur['salle'],
                                        orientation=orientation_vers(position, cible))
                        if restitution:
                            m.objets[objet]['proprietaire'] = qui
                            preter(m, objet, 'joueur')
                        installer(m)
                        if restitution:
                            d = next(x['descripteur'] for x in comptes_publics(m)['choix']
                                     if x['descripteur']['geste'] == 'remettre'
                                     and x['descripteur']['cible'] == reference(m, objet))
                        else:
                            d = {'geste': 'remettre', 'cible': reference(m, objet),
                                 'parametres': {'destinataire': reference(m, qui)}}
                        entree = DescripteurPublic(d) if transport == 'web' else saisie
                        plan = Moteur(m).preparer(entree if transport == 'web' else analyser(m, saisie))
                        # U-C classe « donner » lourd (effet absent d'EFFETS_LEGERS),
                        # y compris quand cet effet règle un prêt plutôt qu'un don.
                        self.assertEqual(plan.effets, [('donner', objet, qui)])
                        self.assertTrue(plan_lourd(plan))
                        self.assertTrue(plan.confirmation)
                        self.parcours(m, entree, objet, qui, restitution, transport)

    def parcours(self, m, entree, objet, qui, restitution, transport):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / 'partie.json'
            m.sauver(chemin)
            saisies = iter([entree, 'annuler', entree, 'tenter', 'quitter'])
            avant, vivant, tour = None, None, 0
            preparer = Moteur.preparer
            faux = MagicMock(connexion='api', erreur_auth=None)
            faux.echanger.side_effect = AssertionError('Appel au modèle')
            faux.raconter_resultat.side_effect = AssertionError('Récit au modèle')

            def capture(moteur, *args, **kwargs):
                nonlocal avant, vivant
                vivant = moteur.monde
                if avant is None:
                    avant = etat(vivant)
                return preparer(moteur, *args, **kwargs)

            def lire(*_):
                nonlocal tour
                if tour:
                    recharge = Monde.charger(chemin)
                    self.assertEqual(recharge.data, json.loads(json.dumps(vivant.data)))
                    self.assertEqual(vues(recharge), vues(vivant))
                    if tour < 4:
                        self.assertEqual(etat(recharge), avant)
                        self.assertEqual(recharge.objets[objet]['lieu'], 'joueur')
                    if tour in (1, 3):
                        dernier = recharge.data['conversation'][-1]
                        self.assertEqual(dernier['nature'], 'proposition_non_executee')
                        self.assertIn('Compris :', dernier['reponse'])
                        self.assertIn('Restituer' if restitution else 'Donner', dernier['reponse'])
                    if tour == 4:
                        self.assertEqual(recharge.objets[objet]['lieu'], qui)
                        self.assertEqual(recharge.objets[objet]['proprietaire'], qui)
                        self.assertEqual(recharge.joueur['or'], avant['joueur']['or'])
                        self.assertFalse(any(p['objet'] == objet for p in recharge.data.get('permissions', [])))
                tour += 1
                return next(saisies)

            class Pont(PontWeb):
                def lire(self, *_):
                    return lire()

            pont = Pont() if transport == 'web' else None
            with mj_simule(faux), patch.object(Moteur, 'preparer', capture), \
                    patch('builtins.input', side_effect=lire), patch('sys.stdout', io.StringIO()) as flux:
                self.assertEqual(jeu.main(['--console', '--connexion', 'api', '--save', str(chemin)], pont), 0)
            faux.echanger.assert_not_called()
            faux.raconter_resultat.assert_not_called()
            texte = '\n'.join(pont.historique) if pont else flux.getvalue()
            resultat = 'Tu restitues' if restitution else 'Tu donnes'
            self.assertLess(texte.index('Compris :'), texte.index(resultat))
            recharge = Monde.charger(chemin)
            self.assertIn(resultat, recharge.data['conversation'][-1]['reponse'])
            # Une reprise réelle réaffiche le résultat enregistré, sans rejouer l'acte.
            sauvegarde = copy.deepcopy(recharge.data)
            reprise = Pont() if pont else None
            with patch('builtins.input', return_value='quitter'), patch('sys.stdout', io.StringIO()) as flux:
                if reprise:
                    reprise.lire = lambda *_: 'quitter'
                self.assertEqual(jeu.main(['--console', '--offline', '--save', str(chemin)], reprise), 0)
            affichage = '\n'.join(reprise.historique) if reprise else flux.getvalue()
            self.assertIn(recharge.data['conversation'][-1]['reponse'], affichage)
            self.assertEqual(Monde.charger(chemin).data, sauvegarde)
