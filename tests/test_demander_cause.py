"""Question, parole datée, réaction autonome et sauvegarde, sans modèle."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import causes, deliberation as d, combat, defense, relations
from donjon.emissions import lire as emissions
from donjon.esprits import lire, croire, memoriser, percevoir_tous
from donjon.monde import Monde
from donjon.scene import scene_percue
from donjon.rendu import regarder
from donjon.temps import MINUTE
from tests.test_empathie_peur import scene
from tests.test_corps_blessable import passer
from tests.test_tensions import recharger, placer
from tests.support import regarder as orienter


def agression(scenario):
    m, aide, proche = scene(scenario)
    auteur = 'brune' if scenario == 'relais' else 'josse'
    ici = m.objets[aide]['lieu']
    y = 5 if scenario == 'relais' else 2
    ailleurs = 'echoppe' if scenario == 'relais' else 'galerie'
    # Le futur questionneur est ailleurs pendant le coup réellement joué.
    placer(m, aide, ailleurs, [8, 5])
    placer(m, proche, ici, [5, y])
    placer(m, auteur, ici, [6, y])
    orienter(m, proche, auteur)
    percevoir_tous(m)
    m.objets[aide]['entend'] = False  # Il n'a pas entendu le cri depuis son lieu isolé.
    with patch.object(type(m), 'd20', side_effect=[20, 1]):
        combat.frapper(m, auteur, proche)
    m.objets[aide]['entend'] = True
    # Retrouvailles après la fin du geste, pas témoin tardif d'un coup en cours.
    from donjon.temps import ecouler, instant
    from donjon.pnj import finir_gestes
    ecouler(m, MINUTE + 1)
    finir_gestes(m, instant(m))
    assert auteur in defense.auteurs(m, proche)
    assert auteur not in defense.auteurs(m, aide)
    # Il retrouve le proche qui s'éloigne vraiment de l'agresseur.
    from donjon.pnj import _avancer_de, _etape
    lire(m, proche)['intention'] = dict(but={'type': 'fuir', 'qui': auteur}, motif='securite',
                                      plan=[_etape('fuite')], depuis=0, attente=0)
    _avancer_de(m, proche, [(ici, (4, y), None, (-1, 0))], False, [])
    placer(m, aide, ici, [3, y])
    orienter(m, aide, proche)
    # La violence doit rester inconnue de l'aide jusqu'à la réponse.
    percevoir_tous(m)
    for qui in (proche, auteur):
        lire(m, qui).update(libre=60000, eveil=None)
    return recharger(m), aide, proche, auteur


class DemanderCauseTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        self.assertEqual(emissions(m), emissions(n))
        return n

    def comparer_laps(self, m, dt=2 * MINUTE):
        a, b = self.recharge(m), self.recharge(m)
        lignes_a = passer(a, dt)
        lignes_b = []
        for duree in (13, 87, 311, dt - 411):
            lignes_b.extend(passer(b, duree))
            b = self.recharge(b)
        a = self.recharge(a)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(scene_percue(a), scene_percue(b))
        # Les aperçus intermédiaires dépendent des points d'affichage du joueur ;
        # les paroles enregistrées et le rendu final sont comparés intégralement.
        return a

    def test_agression_relais_et_mine_demande_puis_reaction_commune(self):
        for scenario in ('relais', 'mine'):
            with self.subTest(scenario=scenario):
                m, aide, proche, auteur = agression(scenario)
                self.assertTrue(causes.demander_possible(m, aide, proche))
                d.choisir(m, aide, m.data['minutes'])
                self.assertEqual(lire(m, aide)['intention']['plan'][0]['contenu'], {'cause_detresse': True})
                passer(m, 1)  # Parole au début du geste, avant une éventuelle riposte.
                m = self.recharge(m)
                self.assertIn(auteur, defense.auteurs(m, aide))
                c = lire(m, aide)['croyances'][auteur]['violence']
                self.assertEqual(c['source'], 'dit:' + proche)
                self.assertEqual(c['valeur'][proche]['minute'], 0)
                self.assertEqual(c['origine'], {'source': 'vu', 'minute': 0})
                m = self.comparer_laps(m)
                demandes = [e for e in m.data['chronique'] if e.get('demande_cause') and e['pnj'] == aide]
                self.assertEqual(len(demandes), 1)
                self.assertEqual(demandes[0]['demande_cause']['issue'], 'dit')
                self.assertTrue(any(e['id'] == aide and e['type'] in ('fuite', 'riposte', 'intervention')
                                    for e in m.data.get('historique_corps', [])))
                self.assertTrue(any(p['locuteur'] == proche and any(
                    c.get('type') == 'cause_detresse' for c in p.get('parametres', {}).get('contenu', []))
                    for p in emissions(m)))

    def test_capture_reelle_crue_recharge_et_demande_sans_cause_cachee(self):
        fichier = Path(__file__).parent / 'data/scenes/rester-266/suspect-1.json.gz'
        charge = json.loads(gzip.decompress(fichier.read_bytes()))
        m = self.recharge(Monde(charge['reprise']))
        a, b = charge['acteur'], charge['beneficiaire']
        self.assertTrue(causes.demander_possible(m, a, b))
        d.choisir(m, a, m.data['minutes'])
        m = self.comparer_laps(m, MINUTE)
        self.assertTrue(any(e.get('demande_cause') for e in m.data['chronique']))

    def test_cause_deja_connue_et_absence_de_detresse(self):
        m, a, b, auteur = agression('relais')
        c = lire(m, b)['croyances'][auteur]['violence']
        croire(m, a, auteur, 'violence', copy.deepcopy(c['valeur']), 'vu')
        self.assertFalse(causes.demander_possible(m, a, b))
        self.recharge(m)
        m, a, b = scene()
        lire(m, b)['besoins']['securite'] = 0.
        percevoir_tous(m)
        self.assertFalse(causes.demander_possible(m, a, b))

    def test_ignorance_et_mefiance_retenues_hors_memoire_sans_delai(self):
        for mefiant in (False, True):
            with self.subTest(mefiant=mefiant):
                m, a, b = scene()
                if mefiant:
                    lire(m, b)['relations'][a] = relations._nouvelle({'confiance': 0, 'rancune': 50})
                self.assertTrue(causes.demander_possible(m, a, b))
                from donjon.echanges import executer
                from donjon.planification import _etape
                executer(m, a, _etape('demander', b, contenu={'cause_detresse': True}), [])
                retenu = next(s for s in lire(m, a)['refus'] if s['operation'] == 'enqueter_cause')
                self.assertIn(retenu['raison'], ('rien', 'mefiance', 'rancune'))
                for _ in range(45):
                    memoriser(m, a, dict(type='attente'))
                m.data['minutes'] += 121
                m = self.recharge(m)
                self.assertFalse(causes.demander_possible(m, a, b))
                self.assertFalse(any('reponse_cause' in e for e in m.data['chronique']))

    def test_inconscient_ne_repond_pas(self):
        m, a, b = scene()
        from donjon.corps import endormir, conscient
        endormir(m, b)
        self.assertFalse(conscient(m, b))
        # La connaissance du corps, comme la perception ordinaire, arrête le secours.
        croire(m, a, b, 'etat', {'conscient': False}, 'vu')
        self.assertFalse(causes.demander_possible(m, a, b))
        avant = copy.deepcopy(emissions(m))
        causes.demander(m, a, b, [])
        self.assertEqual(emissions(m), avant)
        self.recharge(m)

    def test_croyance_fausse_transmise_sans_lire_la_realite(self):
        m, a, b = scene('mine')
        auteur = 'josse'
        croyance = {b: dict(minute=0, menace=True, operation='frapper', clos=False)}
        croire(m, b, auteur, 'violence', croyance, 'vu')
        avant_corps = copy.deepcopy(m.data.get('historique_corps', []))
        causes.demander(m, a, b, [])
        self.assertEqual(lire(m, a)['croyances'][auteur]['violence']['valeur'], croyance)
        self.assertEqual(m.data.get('historique_corps', []), avant_corps)
        self.recharge(m)

    def test_tiers_entend_la_meme_reponse_et_n_apprend_aucune_position(self):
        m, a, b = scene()
        temoin, auteur = 'marchand', 'brune'
        placer(m, temoin, m.objets[a]['lieu'], [6, 5])
        orienter(m, temoin, b)
        croire(m, b, auteur, 'violence',
               {b: dict(minute=0, menace=True, operation='pousser', clos=False)}, 'vu')
        lire(m, temoin)['croyances'].setdefault(auteur, {}).pop('lieu', None)
        causes.demander(m, a, b, [])
        c = lire(m, temoin)['croyances'][auteur]
        self.assertEqual(c['violence']['source'], 'dit:' + b)
        self.assertEqual(c['violence']['valeur'][b]['operation'], 'pousser')
        self.assertNotIn('lieu', c)
        self.recharge(m)

    def test_un_nouveau_signe_percu_rearme_mais_pas_une_date_seule(self):
        m, a, b = scene()
        causes.demander(m, a, b, [])
        self.assertTrue(d.tient(m, a, lire(m, a)['refus'][-1]))
        # Une nouvelle observation s'ajoute au dossier du demandeur, sans consulter le proche.
        c = copy.deepcopy(lire(m, a)['croyances'][b]['detresse'])
        c['valeur'] = True
        c['preuve']['signe'] = 'nouveau-signe-percu'
        c['preuve']['valeur'] = 'fuit'
        lire(m, a)['croyances'][b]['detresse'] = c
        self.assertFalse(d.tient(m, a, lire(m, a)['refus'][-1]))
        self.recharge(m)

    def test_eau_fausse_transmise_avec_confiance_et_date(self):
        m, a, b = scene()
        salle = m.objets[b]['lieu']
        croire(m, b, salle, 'prevision', True, 'savoir', .8, minute=-1, rang=0)
        self.assertEqual(next(causes.connues(m, b))['sorte'], 'eau')
        causes.demander(m, a, b, [])
        c = lire(m, a)['croyances'][salle]['prevision']
        self.assertTrue(c['valeur'])
        self.assertEqual(c['source'], 'dit:' + b)
        self.assertEqual(c['minute'], -1)
        self.assertAlmostEqual(c['confiance'], .56)
        self.recharge(m)

    def test_bruit_inconnu_temoins_et_constat_plus_fort(self):
        m, a, b = scene()
        salle = 'echoppe'
        memoriser(m, b, dict(type='bruit', salle=salle, nature='voix', niveau=2))
        c = next(causes.connues(m, b))
        self.assertEqual(c['sorte'], 'bruit')
        causes.demander(m, a, b, [])
        self.assertTrue(any(s['type'] == 'bruit' and s.get('source') == 'dit:' + b
                            and s['salle'] == salle for s in lire(m, a)['memoire']))
        self.recharge(m)
        # Un constat direct plus récent ne se fait pas écraser par une réponse ancienne.
        croire(m, a, 'brune', 'violence',
               {b: dict(minute=1, menace=False, operation='frapper', clos=True)}, 'vu', minute=1)
        refus = causes.recevoir(m, a, b, dict(type='cause_detresse', sorte='violence', sujet='brune',
            victime=b, valeur=dict(minute=0, menace=True, operation='frapper', clos=False),
            minute=0, source='vu', confiance=1.))
        self.assertEqual(refus, 'doute')
        self.assertTrue(lire(m, a)['croyances']['brune']['violence']['valeur'][b]['clos'])
        self.recharge(m)


if __name__ == '__main__':
    unittest.main()
