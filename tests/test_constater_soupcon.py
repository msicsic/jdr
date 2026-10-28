"""Deux constats propres, des présences bornées et un indice révisable."""
import copy
import json
import os
import tempfile
from pathlib import Path
import unittest

from donjon import agendas, relations
from donjon.esprits import (lire, percevoir, memoriser, constater_possession, verifier, croire,
                           _retenir_presence, _purger_indices_soupcon, PRESENCES_MAX)
from donjon.recit_pnj import Recit
from donjon.rendu import regarder as rendu
from tests.test_constater_rumeurs import auberge
from tests.test_tensions import relais, placer, recharger, vivre
from tests.support import calme, regarder


def scene(autre=False):
    m = auberge() if autre else relais()
    victime, suspect, coffre, bien, salle, loin, case = (
        ('anselme', 'lucien', 'coffre_marchand', 'ballot', 'chambre_chaude', 'etable', [1, 3]) if autre else
        ('marchand', 'brune', 'reserve', 'vivres', 'antichambre', 'crypte', [6, 3]))
    calme(m, *m.data['esprits'])
    from donjon.geometrie import cases
    libres = iter(c for c in cases(m.data['salles'][loin])
                  if list(c) not in ([1, 1], [2, 2], [3, 2], [4, 2]))
    for qui in m.data['esprits']:
        placer(m, qui, loin, next(libres))
    placer(m, victime, salle, case)
    m.joueur.update(salle=loin, position=[1, 1])
    m.objets[coffre].update(ouverte=True, verrouillee=False)
    e = lire(m, victime)
    e['memoire'].clear()
    e['indices_soupcon']['presences'].clear()
    e['indices_soupcon']['constats'].clear()
    e['indices_soupcon']['soupcons'].clear()
    e['portages'].clear()
    regarder(m, victime, coffre)
    percevoir(m, victime)
    assert e['indices_soupcon']['constats'][coffre]['vide']['valeur'] is False
    m.objets[coffre].update(ouverte=False, verrouillee=True)
    m.data['minutes'] += 1
    placer(m, suspect, salle, [case[0] + 1, case[1]])
    regarder(m, victime, suspect)
    percevoir(m, victime)
    return m, victime, suspect, coffre, bien, salle, loin, case


def disparition(s, *, vider=True):
    m, victime, suspect, coffre, bien, salle, loin, case = s
    m.data['minutes'] += 1
    placer(m, victime, loin, [3, 2])
    # L'auteur réel ne sera jamais consulté par l'inférence : bien caché ailleurs.
    m.objets[bien].update(lieu=loin, position=[4, 2], position_salle=loin)
    if vider:
        m.objets[coffre].update(ouverte=True, verrouillee=False)
    placer(m, suspect, loin, [2, 2])
    m.data['minutes'] += 1
    placer(m, victime, salle, case)
    regarder(m, victime, coffre)
    percevoir(m, victime)
    return m


class SoupconTests(unittest.TestCase):
    def recharge(self, m, nom=None):
        from donjon.scene import scene_percue as scene_vue
        avant = copy.deepcopy(m.data), rendu(m), scene_vue(m)
        n = recharger(m)
        self.assertEqual(avant, (n.data, rendu(n), scene_vue(n)))
        verifier(n)
        if nom and os.environ.get('SEUIL_PREUVES_SOUPCON'):
            p = Path(os.environ['SEUIL_PREUVES_SOUPCON']) / (nom + '.json')
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({'monde': n.data, 'rendu': rendu(n), 'scene': scene_vue(n),
                                     'recit': Recit(n).entre_eux(n, n.data['chronique'])},
                                    ensure_ascii=False, indent=2), encoding='utf-8')
        return n

    def test_deux_scenes_rechargees_et_indice_seulement(self):
        for autre in (False, True):
            s = scene(autre)
            m, victime, suspect, coffre, bien, *_ = s
            s = (self.recharge(m), *s[1:])
            avant = relations.envers(m, victime, suspect)['confiance']
            m = self.recharge(disparition(s), 'auberge' if autre else 'relais')
            self.assertEqual({x['auteur'] for x in lire(m, victime)['indices_soupcon']['soupcons'].values()}, {suspect})
            self.assertEqual(len(lire(m, victime)['indices_soupcon']['soupcons']), 1)
            self.assertLess(relations.envers(m, victime, suspect)['confiance'], avant)
            self.assertEqual(relations.envers(m, victime, suspect)['source'], 'devine')
            self.assertIn('soupcon_deduit', '\n'.join(Recit(m).entre_eux(m, m.data['chronique'])))
            self.assertNotIn(bien, lire(m, victime)['portages'])
            agendas.actualiser(m, victime)
            self.assertFalse(any(x['sorte'] == 'récupérer' for x in agendas.projets(m, victime)))
            self.recharge(m)

    def test_zero_deux_et_presence_oubliee(self):
        for cas in ('zero', 'deux', 'oubliee'):
            s = scene()
            m, victime, _, _, _, salle, _, case = s
            if cas == 'zero':
                lire(m, victime)['indices_soupcon']['presences'].clear()
            elif cas == 'deux':
                placer(m, 'ilse', salle, [case[0] + 1, case[1] + 1])
                regarder(m, victime, 'ilse')
                percevoir(m, victime)
            else:
                for i in range(PRESENCES_MAX + 1):
                    _retenir_presence(m, victime, 'passant-' + str(i), salle)
            m = self.recharge(disparition(s))
            self.assertFalse(lire(m, victime)['indices_soupcon']['soupcons'], cas)

    def test_geste_vu_ou_entendu_reste_seul(self):
        for par in ('vue', 'ouie'):
            s = scene()
            m, victime, suspect, _, bien, *_ = s
            memoriser(m, victime, {'type': 'vu_agir', 'auteur': suspect,
                'objet': bien, 'operation': 'prendre', 'victime': victime, 'par': par})
            m = self.recharge(disparition(s))
            self.assertFalse(lire(m, victime)['indices_soupcon']['soupcons'])
            self.assertTrue(any(x['type'] == 'vu_agir' for x in relations.envers(m, victime, suspect)['motifs']))

    def test_retour_et_auteur_appris_levent_sans_effacer_les_autres_epreuves(self):
        for cause in ('rendu', 'remis', 'temoin', 'nouvelle'):
            s = scene()
            m, victime, suspect, coffre, bien, *_ = s
            avant = relations.envers(m, victime, suspect)['confiance']
            m = disparition(s)
            memoriser(m, victime, {'type': 'refus', 'auteur': suspect, 'raison': 'refus'})
            if cause in ('rendu', 'remis'):
                m.objets[bien]['lieu'] = coffre if cause == 'rendu' else victime
                if cause == 'remis':
                    constater_possession(m, victime, bien, 'essai')
                else:
                    percevoir(m, victime)
                self.assertEqual(relations.envers(m, victime, suspect)['confiance'], avant)
            else:
                evt = {'type': 'vu_agir', 'auteur': 'ilse', 'objet': bien,
                       'operation': 'prendre', 'victime': victime}
                memoriser(m, victime, evt if cause == 'temoin' else
                          {'type': 'rumeur', 'de': 'ilse', 'evenement': evt})
            m = self.recharge(m)
            self.assertFalse(lire(m, victime)['indices_soupcon']['soupcons'])
            self.assertTrue(any(x['type'] == 'refus' for x in relations.envers(m, victime, suspect)['motifs']))
            self.assertIn('soupcon_leve', '\n'.join(Recit(m).entre_eux(m, m.data['chronique'])))

    def test_psy_et_plancher_de_confiance(self):
        pertes = []
        for psy in (2, 10, 20):
            s = scene()
            m, victime, suspect, *_ = s
            m.objets[victime]['profil']['caracteristiques']['PSY'] = psy
            lire(m, victime)['relations'][suspect] = relations._nouvelle({'confiance': 40})
            disparition(s)
            pertes.append(40 - relations.envers(m, victime, suspect)['confiance'])
            self.recharge(m)
        self.assertEqual(pertes, [6, 12, 18])
        self.assertLess(max(pertes), abs(relations.EPREUVES['rumeur']['confiance']))

    def test_ni_position_cachee_ni_chronique_ni_nom_inconnu(self):
        s = scene()
        m, victime, suspect, *_ = s
        lire(m, victime)['noms'] = []
        m.objets[victime]['connait_noms'] = []
        m.objets[victime]['profil']['liens'].pop(suspect, None)
        lire(m, victime)['croyances'][suspect] = {
            a: c for a, c in lire(m, victime)['croyances'][suspect].items() if c['source'] != 'savoir'}
        a, b = self.recharge(m), self.recharge(m)
        b.data['chronique'] = []
        placer(b, 'ilse', 'chambre_cloche', [3, 3])
        disparition((a, *s[1:])); disparition((b, *s[1:]))
        self.assertEqual(lire(a, victime)['indices_soupcon']['soupcons'], lire(b, victime)['indices_soupcon']['soupcons'])
        for c in a.data['chronique']:
            if c.get('cause') == 'soupcon_deduit':
                self.assertNotIn('Brune', c['texte'])
        self.assertNotIn(suspect, lire(a, victime)['noms'])
        self.recharge(a)

    def test_laps_entier_et_decoupe(self):
        m = disparition(scene())
        a, _ = vivre(self.recharge(m), 3, jet=20)
        b = self.recharge(m)
        for _ in range(3):
            b, _ = vivre(b, 1, jet=20)
        self.assertEqual(a.data, b.data)
        self.assertEqual(rendu(a), rendu(self.recharge(b)))

    def test_bien_disparu_seul_et_remise(self):
        s = scene()
        m, victime, suspect, coffre, bien, *_ = s
        # Le coffre n'est plus une entité mécanique de la scène : bien posé.
        m.objets[bien].update(lieu=s[5], position=m.objets[coffre]['position'], position_salle=s[5])
        m.objets[coffre]['ouverte'] = False
        percevoir(m, victime)
        m = disparition(s, vider=False)
        self.assertEqual(len(lire(m, victime)['indices_soupcon']['soupcons']), 1)
        m.objets[bien]['lieu'] = victime
        constater_possession(m, victime, bien, 'essai')
        self.assertFalse(lire(m, victime)['indices_soupcon']['soupcons'])
        self.recharge(m)

    def test_integrite_et_extinction_autre_bien(self):
        for dommage in ('casse', 'eteint', 'epuise', 'propre'):
            s = scene()
            m, victime, suspect, coffre, _, salle, *_ = s
            cible = coffre
            if dommage in ('eteint', 'epuise'):
                cible = 'brasero'
                m.objets[cible].update(lieu=salle, position=[8, 4], position_salle=salle,
                                       proprietaire=victime, allume=True, combustible=30)
            regarder(m, victime, cible)
            percevoir(m, victime)
            m.data['minutes'] += 1
            # Présence perçue à l'oreille : elle ne dévoile pas de nom.
            croire(m, victime, suspect, 'lieu', salle, 'entendu', salle=salle, case=None)
            m.data['minutes'] += 1
            if dommage in ('casse', 'propre'):
                m.objets[cible]['integrite'] -= 1
            else:
                m.objets[cible]['allume'] = False
                if dommage == 'epuise':
                    m.objets[cible]['combustible'] = 0
            if dommage == 'propre':
                m._agit = victime
            percevoir(m, victime)
            if hasattr(m, '_agit'):
                del m._agit
            self.assertEqual(bool(lire(m, victime)['indices_soupcon']['soupcons']), dommage in ('casse', 'eteint'), dommage)
            self.recharge(m)

    def test_confiance_saturee_et_refus_commun(self):
        for confiance in (0, 5, 40):
            s = scene()
            m, victime, suspect, coffre, bien, *_ = s
            lire(m, victime)['relations'][suspect] = relations._nouvelle({'confiance': confiance})
            m = disparition(s)
            self.assertTrue(relations.mefiance(relations.envers(m, victime, suspect)))
            m.objets[bien]['lieu'] = coffre
            percevoir(m, victime)
            self.assertEqual(relations.envers(m, victime, suspect)['confiance'], confiance)
            self.recharge(m)

    def test_ressource_videe_et_reconstituee(self):
        s = scene()
        m, victime, _, coffre, bien, *_ = s
        m.data['minutes'] += 1
        m.objets[bien]['portions'] = 0
        m.objets[coffre]['ouverte'] = True
        regarder(m, victime, bien)
        percevoir(m, victime)
        m = self.recharge(m)
        self.assertTrue(lire(m, victime)['indices_soupcon']['soupcons'])
        m.objets[bien]['portions'] = 4
        percevoir(m, victime)
        self.assertFalse(lire(m, victime)['indices_soupcon']['soupcons'])
        self.recharge(m)

    def test_registre_borne_sans_eviction_des_souvenirs_communs(self):
        for autre in (False, True):
            m, victime, _, _, _, salle, *_ = scene(autre)
            for i in range(40):
                memoriser(m, victime, {'type': 'abrite' if i == 0 else 'son', 'indice': i})
            avant = copy.deepcopy(lire(m, victime)['memoire'])
            for i in range(PRESENCES_MAX + 5):
                _retenir_presence(m, victime, 'passant-' + str(i), salle)
            e = lire(m, victime)
            self.assertEqual(e['memoire'], avant)
            self.assertEqual(len(e['indices_soupcon']['presences']), PRESENCES_MAX)
            self.assertTrue(e['indices_soupcon']['oublis'])
            n = self.recharge(m)
            self.assertEqual(lire(n, victime)['memoire'], avant)

    def test_purge_des_presences_hors_intervalle_utile(self):
        m, victime, _, coffre, _, salle, *_ = scene()
        r = lire(m, victime)['indices_soupcon']
        r['presences'] = [{'qui': 'brune', 'salle': salle, 'instant': 1},
                          {'qui': 'ilse', 'salle': salle, 'instant': 600}]
        r['constats'] = {coffre: {'vide': {'valeur': False, 'salle': salle, 'instant': 600,
                                          'lieu': salle, 'proprietaire': victime}}}
        _purger_indices_soupcon(m, victime)
        self.assertEqual([s['qui'] for s in r['presences']], ['ilse'])
        self.recharge(m)
        m.data['minutes'] += 1
        r['constats'][coffre]['vide']['instant'] = 1200
        _purger_indices_soupcon(m, victime)
        self.assertEqual(r['presences'], [])
        self.recharge(m)

    def test_registre_invalide_refuse_au_chargement(self):
        from donjon.monde import Monde, ErreurMonde
        for faute in ('date', 'lieu', 'taille'):
            m, victime, *_ = scene()
            r = lire(m, victime)['indices_soupcon']
            if faute == 'date':
                r['presences'][0]['instant'] = -1
            elif faute == 'lieu':
                r['presences'][0]['salle'] = 'lieu-inexistant'
            else:
                r['presences'] *= PRESENCES_MAX + 1
            with tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / 'invalide.json'
                chemin.write_text(json.dumps(m.data, ensure_ascii=False), encoding='utf-8')
                with self.assertRaises(ErreurMonde):
                    Monde.charger(chemin)
