"""Contrat force : MJ simulé, console, corps et rendu relus depuis la sauvegarde."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon import corps
from donjon.dialogues import interlocuteurs
from donjon.esprits import percevoir_tous
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.narration import consigner, controler
from donjon.rendu import regarder
from tests.test_tenir import situation
from tests.test_trainer import scene as scene_trainer
from tests.test_enfermer import scene as scene_enfermer
from tests.test_tensions import recharger
from donjon.deplacement_objet import deplacer


def console(m, p, demande, scenario='--rixe', audit=None):
    reponse = {'mode': 'action', 'texte': '', 'faits': [], 'proposition': p}
    def appeler(*args):
        if args[3] == 'auditer_action':
            return (audit(args[1]) if callable(audit) else audit) if audit is not None else {'conforme': True, 'motif': ''}
        return copy.deepcopy(reponse)
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / 'copie.json'
        m.sauver(chemin)
        with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
              patch.object(MJOpenAI, '_appeler_brut', side_effect=appeler),
              patch.object(type(m), 'd20', return_value=20),
              patch('builtins.input', side_effect=['mj ' + demande, 'tenter', 'quitter']),
              patch('sys.stdout', io.StringIO()) as sortie):
            assert jeu.main(['--console', scenario, '--save', str(chemin), '--connexion', 'api']) == 0
        return Monde.charger(chemin), sortie.getvalue()


class ForceLunaTests(unittest.TestCase):
    def test_deplacement_d_un_tiers_non_demande_reste_refuse(self):
        from tests.test_tensions import placer
        for scenario in ('relais', 'auberge'):
            m, cible = scene_trainer(scenario)
            tiers = next(i for i, o in m.objets.items()
                         if o['type'] == 'personnage' and i != cible)
            placer(m, tiers, m.joueur['salle'], (3, 4))
            corps.endormir(m, tiers)
            percevoir_tous(m)
            avant = copy.deepcopy(m.joueur), copy.deepcopy(m.objets[tiers])
            revues = []
            def refuser(dossier):
                revues.append(dossier)
                self.assertIn(tiers, dossier['plan']['deplacements'][1]['acteur'])
                return {'conforme': False, 'motif': 'déplacement d’un tiers non demandé'}
            m, texte = console(m, proposition('trainer', tiers, 'est'),
                               'je traîne ' + m.objets[cible]['nom'] + ' vers l’est',
                               '--defi' if scenario == 'relais' else '--auberge', audit=refuser)
            self.assertTrue(revues)
            self.assertEqual((m.joueur, m.objets[tiers]), avant)
            self.assertNotIn('Tu as traîné', texte)
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_etat_deja_vrai_ne_demande_pas_de_deplacer_la_personne(self):
        from donjon.couverture_action import entree
        for cible, salle in (('bram', 'bureau'), ('remy', 'reserve')):
            with self.subTest(cible=cible):
                m, porte = scene_enfermer(cible, salle)
                m.objets[porte].update(ouverte=True, verrouillee=False)
                from donjon.spatial import memoriser
                from tests.test_tensions import placer
                placer(m, cible, salle, (1, 1))
                position = copy.deepcopy(m.joueur)
                m.joueur.update(salle=salle, position=[2, 1], orientation='ouest')
                memoriser(m)
                m.joueur.update(position)
                percevoir_tous(m)
                m = recharger(m)
                p = proposition('fermer', porte)
                plan = Moteur(m).preparer(p)
                avant = copy.deepcopy(m.data)
                dossier = entree('j’enferme cette personne', plan, m)
                self.assertEqual(m.data, avant)
                revues = []
                def admettre(recu):
                    revues.append(recu)
                    piece = next(x for x in recu['plan']['passages']
                                 if x['lieu'].endswith('(' + salle + ')'))
                    self.assertTrue(any(cible in x for x in piece['personnes_connues']))
                    self.assertEqual(piece['etat_apres_operation'], {'ouverte': False})
                    self.assertEqual(recu['plan']['effets_reussite'],
                                     dossier['plan']['effets_reussite'])
                    return {'conforme': True, 'motif': ''}
                m, texte = console(m, p, 'j’enferme cette personne', '--mine', audit=admettre)
                self.assertTrue(revues)
                self.assertFalse(m.objets[porte]['ouverte'])
                self.assertEqual(m.objets[cible]['lieu'], salle)
                self.assertIn('ferm', texte)
                self.assertEqual(m.data, recharger(m).data)
                self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_gestes_non_conformes_refuses_avant_execution_console(self):
        for scenario in ('relais', 'auberge'):
            m, c = scene_trainer(scenario)
            avant = copy.deepcopy(m.joueur['position']), copy.deepcopy(m.objets[c]['position'])
            revues = []
            def refuser(dossier):
                revues.append(dossier)
                self.assertEqual(dossier['plan']['deplacements'][0]['arrivee']['position'],
                                 [avant[0][0], avant[0][1] - 1])
                return {'conforme': False, 'motif': 'nord au lieu de est'}
            p = proposition('trainer', c, 'nord')
            Moteur(m).preparer(p)  # Mécaniquement possible, mais mauvaise direction.
            m, texte = console(m, p, 'je traîne ce corps vers l’est',
                               '--defi' if scenario == 'relais' else '--auberge',
                               audit=refuser)
            self.assertTrue(revues)
            self.assertEqual((m.joueur['position'], m.objets[c]['position']), avant)
            self.assertNotIn('Tu as traîné', texte)
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))
        for salle in ('bureau', 'reserve'):
            m, porte = scene_enfermer(salle=salle)
            revues = []
            def refuser(dossier):
                revues.append(dossier)
                self.assertEqual(dossier['plan']['passages'][0]['etat_apres_operation'],
                                 {'ouverte': True})
                return {'conforme': False, 'motif': 'ouvrir au lieu de fermer'}
            m.objets[porte].update(ouverte=False, verrouillee=False)
            p = proposition('ouvrir', porte)
            Moteur(m).preparer(p)
            m, texte = console(m, p, 'j’enferme cette personne dans cette pièce', '--mine',
                               audit=refuser)
            self.assertTrue(revues)
            self.assertFalse(m.objets[porte]['ouverte'])
            self.assertEqual(m.objets['remy']['lieu'], salle)
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_destination_du_corps_dans_la_fiche_et_la_contre_revue(self):
        import json
        from tools.banc_parties import preparer
        from donjon.couverture_action import entree
        from tests.test_tensions import placer
        scenes = []
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / 'scene.json'
            preparer(json.loads(Path('tests/data/bancs/force-4f-trainer.json').read_text(encoding='utf-8')), chemin)
            scenes.append((Monde.charger(chemin), 'brune', 'sud', '--rixe'))
        m, c = scene_trainer()
        m.joueur.update(salle='echoppe', position=[8, 3], orientation='ouest')
        placer(m, c, 'antichambre', (0, 3))
        percevoir_tous(m)
        scenes.append((m, c, 'ouest', '--defi'))
        for m, c, direction, scenario in scenes:
            salle = m.joueur['salle']
            plan = Moteur(m).preparer(proposition('trainer', c, direction))
            nom = m.data['salles'][salle]['nom']
            self.assertIn(nom, plan.information)
            self.assertIn(nom, plan.titre)
            avant_dossier = copy.deepcopy(m.data)
            dossier = entree('je traîne ce corps ici', plan, m)
            self.assertEqual(m.data, avant_dossier)
            mouvements = dossier['plan']['deplacements']
            self.assertEqual(len(mouvements), 2)
            self.assertEqual(mouvements[0]['depart'], mouvements[1]['arrivee'])
            self.assertIn(c, mouvements[1]['acteur'])
            self.assertEqual(mouvements[0]['depart']['position'], m.joueur['position'])
            # Même trajet, lieu d'arrivée encore inconnu : aucune géographie privée.
            cache = copy.deepcopy(plan)
            inconnue = next(s for s in m.data['salles'] if s != salle)
            cache.deplacements[0]['arrivee']['salle'] = inconnue
            visites = m.data['visitees']
            m.data['visitees'] = [salle]
            try:
                mouvement_cache = entree('je traîne ce corps', cache, m)['plan']['deplacements'][0]
                self.assertEqual(mouvement_cache['arrivee'],
                                 {'passage': "de l'autre côté, lieu non visité"})
            finally:
                m.data['visitees'] = visites
            destination_joueur = copy.deepcopy(plan.deplacements[0]['arrivee'])
            self.assertNotIn('\"' + salle + '\"', json.dumps(dossier, ensure_ascii=False))
            self.assertIn(nom, entree('je traîne ce corps ici', plan, m)['plan']['information'])
            revues = []
            def admettre(recu):
                revues.append(recu)
                self.assertEqual(recu['plan']['deplacements'], mouvements)
                return {'conforme': True, 'motif': ''}
            m, texte = console(m, proposition('trainer', c, direction),
                               'je la traîne dans la crypte' if scenario == '--rixe' else 'je traîne ce corps ici',
                               scenario, audit=admettre)
            self.assertTrue(revues)
            self.assertEqual(m.joueur['salle'], destination_joueur['salle'])
            self.assertEqual(m.joueur['position'], destination_joueur['position'])
            self.assertEqual(m.objets[c]['position'], plan.deplacements[1]['arrivee']['position'])
            self.assertEqual(m.objets[c]['lieu'], salle)
            self.assertIn('traîné', texte)
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_dossier_portes_personnes_et_lieux_sans_mutation(self):
        from donjon.couverture_action import entree, verifier, _nommer_lieux
        self.assertEqual(_nommer_lieux({"texte": "bureau", "nom": "bureau"}, scene_enfermer()[0]),
                         {"texte": "bureau", "nom": "bureau"})
        from donjon.operations import etape
        for cible, salle in (("bram", "bureau"), ("remy", "reserve")):
            m, porte = scene_enfermer(cible, salle)
            deplacer(m, "passe", "joueur")
            m.objets[porte].update(ouverte=True, verrouillee=False)
            from tests.test_tensions import placer
            from donjon.spatial import memoriser
            placer(m, cible, salle, (1, 1))
            position = copy.deepcopy(m.joueur)
            m.joueur.update(salle=salle, position=[2, 1])
            memoriser(m)
            m.joueur.update(position)
            percevoir_tous(m)
            m = recharger(m)
            p = {"action": "composer", "justification": ""}
            p["etapes"] = [etape("fermer", porte), etape("verrouiller", porte, outil="passe")]
            plan = Moteur(m).preparer(p)
            avant = copy.deepcopy(m.data)
            dossier = entree("j’enferme cette personne", plan, m)
            self.assertEqual(m.data, avant)
            fermeture = dossier["plan"]["etapes"][0]
            self.assertEqual(fermeture["effets_reussite"][0][0], "fermer")
            self.assertEqual(fermeture["passages"][0]["operation"], "fermer")
            self.assertEqual(fermeture['passages'][0]['etat_apres_operation'], {'ouverte': False})
            passages = dossier["plan"]["etapes"][1]["passages"]
            piece = next(x for x in passages if x["lieu"].endswith("(" + salle + ")"))
            self.assertIn(m.objets[porte]["nom"].lower(), piece["porte"].lower())
            self.assertTrue(any(cible in x for x in piece["personnes_connues"]))
            self.assertNotEqual(piece['lieu_corvus'], piece['lieu'])
            self.assertEqual(piece['etat_apres_operation'], {'verrouillee': True})
            self.assertEqual(piece["issues_connues_avant"], [{"porte": piece["porte"], "verrouillee": False}])
            self.assertEqual(piece['personnes_retenues_apres_operation'],
                             [x for x in piece['personnes_connues'] if cible in x])
            self.assertEqual(fermeture['passages'][0]['personnes_retenues_apres_operation'], [])
            verifier({"conforme": True, "motif": "porte fermée et verrouillée"}, plan)
            with self.assertRaises(ErreurMonde):
                verifier({"conforme": False, "motif": "la demande exige de rouvrir"}, plan)
            def admettre(recu):
                verrou = recu['plan']['etapes'][1]['passages']
                self.assertTrue(any(any(cible in i for i in x['personnes_retenues_apres_operation'])
                                    for x in verrou))
                return {'conforme': True, 'motif': ''}
            m, texte = console(m, p, "j’enferme cette personne", "--mine", audit=admettre)
            self.assertTrue(m.objets[porte]["verrouillee"])
            self.assertFalse(m.objets[porte]["ouverte"])
            self.assertEqual(m.objets[cible]["lieu"], salle)
            self.assertIn("verrouill", texte)
            self.assertEqual([e['id'] for e in m.data.get('historique_corps', [])
                              if e['type'] == 'enfermer'], [cible])
            self.assertEqual(m.data, recharger(m).data)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_autre_issue_libre_ou_inconnue_ne_retient_personne(self):
        from donjon.couverture_action import entree
        from donjon.spatial import memoriser
        from donjon.tenir import retenus_apres, enfermer
        from tests.test_tensions import placer
        from donjon.esprits import croire
        for cible, salle in (('bram', 'bureau'), ('remy', 'reserve')):
            for issue in ('libre', 'inconnue'):
                with self.subTest(salle=salle, issue=issue):
                    m, porte = scene_enfermer(cible, salle)
                    deplacer(m, 'passe', 'joueur')
                    m.objets[porte].update(ouverte=False, verrouillee=False)
                    placer(m, cible, salle, (1, 1))
                    position = copy.deepcopy(m.joueur)
                    m.joueur.update(salle=salle, position=[2, 1])
                    memoriser(m)
                    m.joueur.update(position)
                    autre = 'porte_reserve' if salle == 'bureau' else 'porte_bureau'
                    destination = 'reserve' if salle == 'bureau' else 'bureau'
                    ajout = {'escalier': True, 'case': [1, 1],
                             'porte': autre if issue == 'inconnue' else None}
                    m.data['salles'][salle]['sorties']['est'] = {**ajout, 'vers': destination}
                    m.data['salles'][destination]['sorties']['ouest'] = {**ajout, 'vers': salle}
                    m.objets[autre]['verrouillee'] = True
                    m.data.get('verrous_joueur', {}).pop(autre, None)
                    m = recharger(m)
                    self.assertFalse(any(retenus_apres(m, 'joueur', porte).values()))
                    croire(m, 'josse', cible, 'lieu', salle, 'savoir', salle=salle, case=None)
                    m.data['esprits']['josse']['croyances'].pop(autre, None)
                    etat = copy.deepcopy(m.data)
                    self.assertFalse(any(retenus_apres(m, 'josse', porte).values()))
                    self.assertEqual(m.data, etat)
                    enfermer(m, 'josse', porte, 50)
                    self.assertFalse(any(e['type'] == 'enfermer' for e in m.data.get('historique_corps', [])))
                    p = proposition('verrouiller', porte, 'passe')
                    plan = Moteur(m).preparer(p)
                    etat = copy.deepcopy(m.data)
                    dossier = entree('j’enferme cette personne', plan, m)
                    self.assertEqual(m.data, etat)
                    self.assertTrue(all(not x['personnes_retenues_apres_operation']
                                        for x in dossier['plan']['passages']))
                    revues = []
                    def refuser(recu):
                        revues.append(recu)
                        self.assertTrue(all(not x['personnes_retenues_apres_operation']
                                            for x in recu['plan']['passages']))
                        return {'conforme': False, 'motif': 'une autre issue reste praticable'}
                    m, texte = console(m, p, 'j’enferme cette personne', '--mine', audit=refuser)
                    self.assertTrue(revues)
                    self.assertFalse(m.objets[porte]['verrouillee'])
                    self.assertNotIn('Tu verrouilles', texte)
                    self.assertEqual(m.data, recharger(m).data)
                    self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_prendre_lier_delier_liberer_et_tuer_via_console(self):
        for cible in ('brune', 'aubin'):
            for action in ('saisir', 'ligoter', 'delier', 'liberer', 'tuer'):
                with self.subTest(cible=cible, action=action):
                    m = situation(cible)
                    m.joueur['stats']['FOR'] = 20
                    for i, o in m.objets.items():
                        if o['type'] == 'personnage' and (action != 'saisir' or i != cible):
                            corps.endormir(m, i)
                    if action in ('delier', 'liberer'):
                        from donjon.banc_pnj import appliquer_etats
                        appliquer_etats(m, [cible + ':ligote'])
                    if action == 'liberer':
                        lien = corps.corps(m, cible).pop('lie')
                        corps.corps(m, 'joueur')['lie'] = lien
                        m.objets[lien['lien']]['lieu'] = 'joueur'
                    percevoir_tous(m)
                    outil = 'corde_test' if action == 'ligoter' else ''
                    p = proposition(action, 'joueur' if action == 'liberer' else cible, outil)
                    plan = Moteur(m).preparer(p)
                    self.assertTrue(plan.confirmation)
                    m, texte = console(m, p, action + ' ' + m.objets[cible]['nom'])
                    if action == 'tuer':
                        self.assertEqual(m.objets[cible]['type'], 'depouille')
                        self.assertIn('tué', texte)
                        self.assertIn('corps', regarder(m))
                    elif action == 'ligoter':
                        self.assertIn('lie', corps.corps(m, cible))
                        self.assertIn('ligot', regarder(m))
                        self.assertIn('maintenant ligotée', texte)
                    elif action == 'saisir':
                        self.assertEqual(corps.corps(m, cible).get('tenu_par'), 'joueur')
                        self.assertIn('saisi', texte.lower())
                    else:
                        self.assertNotIn('lie', corps.corps(m, 'joueur' if action == 'liberer' else cible))
                        self.assertIn('liens', texte)
                    self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_trainer_et_verrouiller_deux_scenes_console(self):
        for scenario in ('relais', 'auberge'):
            m, c = scene_trainer(scenario)
            avant = list(m.joueur['position'])
            m, texte = console(m, proposition('trainer', c, 'est'), 'je traîne ce corps vers l’est',
                               '--defi' if scenario == 'relais' else '--auberge')
            self.assertEqual(m.objets[c]['position'], avant)
            self.assertIn('traîné', texte)
            self.assertEqual(regarder(m), regarder(recharger(m)))
        for salle in ('bureau', 'reserve'):
            m, porte = scene_enfermer(salle=salle)
            deplacer(m, 'passe', 'joueur')
            m.objets[porte]['verrouillee'] = False
            m, texte = console(m, proposition('verrouiller', porte, 'passe'), 'je verrouille la porte', '--mine')
            self.assertTrue(m.objets[porte]['verrouillee'])
            self.assertIn('verrouill', texte)
            self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_corps_invente_refuse_avant_enregistrement_apres_recharge(self):
        for texte in ('Brune est morte.', 'Brune perd connaissance.', 'Brune est ligotée.', 'Brune est blessée.'):
            m = recharger(situation())
            avant = copy.deepcopy(m.data)
            ligne = {'indice': 0, 'verdict': 'invention_protegee', 'portee_mecanique': 'sans_fondement',
                     'sources': [], 'motif': 'Le corps ne l’établit pas.'}
            faits = {'objet:brune': {'etat_corps': corps.visible(m, 'brune')}}
            self.assertTrue(controler(texte, {'segments': [ligne]}, faits)['obstacles'])
            with self.assertRaises(ErreurMonde):
                consigner(m, {'texte': texte, '_audit': {'texte_initial': texte, 'segments': [ligne], 'faits': faits}})
            m = recharger(m)
            self.assertEqual(m.data, avant)
            self.assertNotIn(texte, str(m.data))
            self.assertTrue(corps.conscient(m, 'brune'))

    def test_invention_corporelle_ne_parvient_pas_a_la_console(self):
        from tests.test_narration import dialogue, segment
        for cible, invention in (('brune', 'Brune est morte.'), ('aubin', 'Aubin perd connaissance.')):
            m = situation(cible)
            with tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / 'copie.json'
                m.sauver(chemin)
                sorties = [x for _ in range(3) for x in
                           (dialogue(invention), segment('invention_protegee', motif='État du corps absent.'))]
                with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                      patch.object(MJOpenAI, '_appeler_brut', side_effect=sorties),
                      patch('builtins.input', side_effect=['mj Que vois-je ?', 'quitter']),
                      patch('sys.stdout', io.StringIO()) as sortie):
                    self.assertEqual(jeu.main(['--console', '--rixe', '--save', str(chemin), '--connexion', 'api']), 0)
                reprise = Monde.charger(chemin)
            self.assertNotIn(invention, sortie.getvalue())
            self.assertTrue(corps.conscient(reprise, cible))
            self.assertEqual(corps.visible(m, cible), corps.visible(reprise, cible))
            self.assertNotIn(invention, str(reprise.data.get('narrations_mj', [])))
            self.assertEqual(regarder(reprise), regarder(recharger(reprise)))

    def test_locuteur_devenu_inconscient_ou_mort_refuse_meme_audit_favorable(self):
        for cible in ('brune', 'aubin'):
            for mort in (False, True):
                m = situation(cible)
                faits = {'interlocuteurs': interlocuteurs(m)}
                self.assertIn(cible, faits['interlocuteurs'])
                texte = '« Bonjour à toi. »'
                ligne = {'indice': 0, 'verdict': 'parole', 'portee_mecanique': 'aucune',
                         'sources': [], 'locuteur': cible, 'citation': 'Bonjour à toi.', 'entites': [], 'motif': ''}
                corps.mourir(m, cible) if mort else corps.endormir(m, cible)
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                self.assertNotIn(cible, interlocuteurs(m))
                with self.assertRaises(ErreurMonde):
                    consigner(m, {'texte': texte, '_audit': {'texte_initial': texte, 'segments': [ligne],
                                                          'faits': faits, 'fondement': '', 'fondement_paroles': ''}})
                m = recharger(m)
                self.assertEqual(m.data, avant)
                self.assertNotIn(texte, str(m.data))
                self.assertEqual(regarder(m), regarder(recharger(m)))
