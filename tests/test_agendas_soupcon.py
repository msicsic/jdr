"""Une enquête sur une disparition perçue, jamais un portage inventé."""
import copy
import json
import os
from pathlib import Path
import unittest

from donjon import agendas, planification, relations
from donjon.emissions import lire as emissions
from donjon.esprits import lire, croire, memoriser, percevoir, verifier
from donjon.rendu import regarder as rendu
from donjon.recit_pnj import Recit
from tests.test_constater_soupcon import scene, disparition
from tests.test_tensions import placer, recharger, vivre
from tests.support import regarder


class AgendaSoupconTests(unittest.TestCase):
    def recharge(self, m, nom=None):
        from donjon.scene import scene_percue
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(json.dumps(m.data), json.dumps(n.data))
        self.assertEqual(emissions(m), emissions(n))
        self.assertEqual(rendu(m), rendu(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        self.assertEqual(Recit(m).entre_eux(m, m.data.get('chronique', [])),
                         Recit(n).entre_eux(n, n.data.get('chronique', [])))
        verifier(n)
        if nom and os.environ.get('SEUIL_PREUVES_SOUPCON'):
            p = Path(os.environ['SEUIL_PREUVES_SOUPCON']) / (nom + '.json')
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({'monde': n.data, 'rendu': rendu(n),
                'scene': scene_percue(n), 'paroles': emissions(n), 'recit': Recit(n).entre_eux(n, n.data['chronique'])},
                ensure_ascii=False, indent=2), encoding='utf-8')
        return n

    def test_deux_disparitions_vol_reel_enquete_et_laps_decoupe(self):
        from donjon.pnj import _executer
        from tests.test_temps_etat import plan
        for autre in (False, True):
            s = scene(autre)
            m, victime, suspect, coffre, bien, salle, loin, case = s
            # Le bien est réellement pris hors de la vue de sa victime.
            placer(m, victime, loin, [3, 2])
            m.objets[coffre].update(ouverte=True, verrouillee=False)
            placer(m, suspect, salle, m.objets[coffre]['position'])
            regarder(m, suspect, bien)
            percevoir(m, suspect)
            self.assertTrue(_executer(m, suspect, plan('prendre', bien), [], []))
            self.assertNotIn(bien, lire(m, victime)['portages'])
            placer(m, suspect, loin, [2, 2])
            m.data['minutes'] += 2
            placer(m, victime, salle, case)
            regarder(m, victime, coffre)
            percevoir(m, victime)
            agendas.actualiser(m, victime)
            m = self.recharge(m, 'disparition-' + ('auberge' if autre else 'relais'))
            a = next(a for a in agendas.projets(m, victime) if a['sorte'] == 'récupérer')
            self.assertEqual(a['parametres']['qui'], suspect)
            self.assertNotIn(bien, lire(m, victime)['portages'])
            self.assertIsNone(lire(m, victime)['croyances'][bien]['lieu']['valeur'])
            # Le suspect revient sans le bien, déposé hors du regard : ce retour
            # ne prouve ni la culpabilité ni l'innocence.
            m.objets[bien].update(lieu=loin, position=[4, 2], position_salle=loin)
            placer(m, suspect, salle, [case[0] + 1, case[1]])
            regarder(m, victime, suspect)
            percevoir(m, victime)
            # La question commune se formule sans accuser ni prétendre au portage.
            with planification.vues_du_choix(m, victime):
                resultat = agendas.planifier(m, victime, a['id'])
            self.assertIsNotNone(resultat)
            self.assertEqual(resultat[1][-1]['contenu'], {'localisation': bien})
            # Interlocuteur remis à portée, réponse négative : le soupçon survit,
            # mais la question n'est pas répétée sans indice nouveau.
            m.joueur.update(salle=salle, position=[1, 1])
            lignes = []
            _executer(m, victime, resultat[1][-1], lignes, [])
            self.assertTrue(any('où se trouve' in c['texte'] for c in m.data['chronique']))
            self.assertTrue(lire(m, victime)['indices_soupcon']['soupcons'])
            with planification.vues_du_choix(m, victime):
                suivant = agendas.planifier(m, victime, a['id'])
            self.assertFalse(suivant and any(g.get('contenu') == {'localisation': bien} for g in suivant[1]))
            m = self.recharge(m, 'question-' + ('auberge' if autre else 'relais'))
            entier, lignes = vivre(self.recharge(m), 2, jet=20)
            decoupe = self.recharge(m)
            suite = []
            for _ in range(2):
                decoupe, nouvelles = vivre(decoupe, 1, jet=20)
                suite.extend(nouvelles)
                decoupe = self.recharge(decoupe)
            entier = self.recharge(entier, 'laps-' + ('auberge' if autre else 'relais'))
            self.assertEqual(lignes, suite)
            self.assertEqual(entier.data, decoupe.data)
            self.assertEqual(json.dumps(entier.data), json.dumps(decoupe.data))
            self.assertEqual(rendu(entier), rendu(decoupe))
            from donjon.scene import scene_percue
            self.assertEqual(scene_percue(entier), scene_percue(decoupe))
            self.assertEqual(emissions(entier), emissions(decoupe))
            self.assertEqual(Recit(entier).entre_eux(entier, entier.data['chronique']),
                             Recit(decoupe).entre_eux(decoupe, decoupe.data['chronique']))

    def test_ponderation_signes_antecedents_et_pas_profils_secrets(self):
        for indice in ('guet', 'garde', 'ancien', 'secret'):
            s = scene()
            m, victime, suspect, coffre, bien, salle, _, case = s
            placer(m, 'ilse', salle, [case[0] + 1, case[1] + 1])
            regarder(m, victime, 'ilse')
            percevoir(m, victime)
            if indice in ('guet', 'garde'):
                croire(m, victime, suspect, 'intention', indice, 'devine', .8,
                       signe='lecture-test', envers=bien)
            elif indice == 'ancien':
                memoriser(m, victime, {'type': 'vu_agir', 'auteur': suspect,
                    'objet': 'marteau', 'operation': 'prendre', 'victime': 'aubin'})
            else:
                m.objets[suspect]['profil']['valeurs']['honnetete'] = 0
                m.objets[suspect]['profil']['pulsions'] = []
            disparition(s)
            agendas.actualiser(m, victime)
            m = self.recharge(m)
            soupcon = next(iter(lire(m, victime)['indices_soupcon']['soupcons'].values()))
            self.assertEqual(set(soupcon['candidats']), {suspect, 'ilse'})
            if indice in ('guet', 'ancien'):
                self.assertEqual(soupcon['auteur'], suspect)
                self.assertGreater(soupcon['candidats'][suspect], soupcon['candidats']['ilse'])
                self.assertGreater(soupcon['conviction'], .2)
                self.assertLess(soupcon['conviction'], .4)
                self.assertTrue(any(a['sorte'] == 'récupérer' for a in agendas.projets(m, victime)))
            else:
                self.assertIsNone(soupcon['auteur'])
                self.assertFalse(any(a['sorte'] == 'récupérer' for a in agendas.projets(m, victime)))

    def test_retrouve_ailleurs_ou_autre_auteur_retire_projet_et_mefiance(self):
        for autre in (False, True):
            for cause in ('retrouve', 'auteur'):
                s = scene(autre)
                m, victime, suspect, _, bien, salle, loin, case = s
                confiance = relations.envers(m, victime, suspect)['confiance']
                disparition(s)
                agendas.actualiser(m, victime)
                m = self.recharge(m)
                if cause == 'retrouve':
                    placer(m, victime, loin, [3, 2])
                    regarder(m, victime, bien)
                    percevoir(m, victime)
                else:
                    m.joueur.update(salle=salle, position=[case[0] + 1, case[1]])
                    m.objets[bien]['lieu'] = 'joueur'
                    regarder(m, victime, 'joueur')
                    percevoir(m, victime)
                    self.assertEqual(lire(m, victime)['portages'][bien]['auteur'], 'joueur')
                agendas.actualiser(m, victime)
                m = self.recharge(m)
                self.assertFalse(lire(m, victime)['indices_soupcon']['soupcons'])
                a = agendas.projets(m, victime)[0]
                self.assertEqual((a['etat'], a['raison']), ('abandonne', 'soupcon leve'))
                self.assertEqual(relations.envers(m, victime, suspect)['confiance'], confiance)
                agendas.actualiser(m, victime)
                self.assertEqual(len([a for a in agendas.projets(m, victime) if a['origine'].get('soupcon')]), 1)

    def test_meme_croyances_meme_soupcon_malgre_auteur_reel_et_memoire_videe(self):
        s = scene()
        m, victime, _, _, bien, *_ = s
        a, b = self.recharge(m), self.recharge(m)
        b.data['chronique'] = []
        b.objets['ilse']['profil']['valeurs']['honnetete'] = 0
        disparition((a, *s[1:])); disparition((b, *s[1:]))
        # Le bien a un porteur réel différent, sans perception nouvelle.
        b.objets[bien]['lieu'] = 'ilse'
        for n in (a, b):
            lire(n, victime)['memoire'].clear()
            agendas.actualiser(n, victime)
            self.recharge(n)
        self.assertEqual(lire(a, victime)['indices_soupcon'], lire(b, victime)['indices_soupcon'])
        self.assertEqual(agendas.projets(a, victime), agendas.projets(b, victime))

    def test_ancien_format_et_ponderation_invalide(self):
        from donjon.monde import ErreurMonde
        m = disparition(scene())
        s = next(iter(lire(m, 'marchand')['indices_soupcon']['soupcons'].values()))
        ancien = copy.deepcopy(m)
        t = next(iter(lire(ancien, 'marchand')['indices_soupcon']['soupcons'].values()))
        del t['candidats']; del t['conviction']
        self.recharge(ancien)
        s['conviction'] = 1.0
        with self.assertRaises(ErreurMonde):
            recharger(m)

    def test_presence_entendue_et_penalite_a_la_conviction(self):
        pertes = []
        for plusieurs in (False, True):
            s = scene()
            m, victime, suspect, _, bien, salle, *_ = s
            r = lire(m, victime)['indices_soupcon']
            r['presences'].clear()
            croire(m, victime, suspect, 'lieu', salle, 'entendu', salle=salle, case=None)
            if plusieurs:
                croire(m, victime, 'ilse', 'lieu', salle, 'entendu', salle=salle, case=None)
                croire(m, victime, suspect, 'intention', 'guet', 'devine', .8,
                       signe='lecture-test', envers=bien)
            lire(m, victime)['relations'][suspect] = relations._nouvelle({'confiance': 40})
            disparition(s)
            agendas.actualiser(m, victime)
            m = self.recharge(m)
            self.assertTrue(any(a['sorte'] == 'récupérer' for a in agendas.projets(m, victime)))
            pertes.append(40 - relations.envers(m, victime, suspect)['confiance'])
        self.assertGreater(pertes[0], pertes[1])
        self.assertGreater(pertes[1], 0)

    def test_reputation_sans_occasion_et_signe_perime_ne_designent_pas(self):
        for cas in ('sans_presence', 'perime'):
            s = scene()
            m, victime, suspect, _, bien, salle, *_ = s
            if cas == 'sans_presence':
                lire(m, victime)['indices_soupcon']['presences'].clear()
                memoriser(m, victime, {'type': 'vu_agir', 'auteur': suspect,
                    'objet': 'marteau', 'operation': 'prendre', 'victime': 'aubin'})
            else:
                croire(m, victime, 'ilse', 'lieu', salle, 'entendu', salle=salle, case=None)
            croire(m, victime, suspect, 'intention', 'guet', 'devine', .8,
                   signe='lecture-test', envers=bien)
            if cas == 'perime':
                m.data['minutes'] += 31
            disparition(s)
            agendas.actualiser(m, victime)
            m = self.recharge(m)
            self.assertFalse(any(a['sorte'] == 'récupérer' for a in agendas.projets(m, victime)))
