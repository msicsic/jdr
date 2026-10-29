"""L'intention survit à sa naissance ; priorités et démentis restent effectifs."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, relations
from donjon.esprits import croire, lire, percevoir_tous, percus, constater
from donjon.planification import _etape
from donjon.monde import Monde
from tests.test_empathie import scene, scene_repas, executer, rendu
from tests.test_tensions import placer, recharger
from donjon.scene import scene_percue


class ContratEngagementTests(unittest.TestCase):
    def test_aide_attendue_autre_besoin_revalidation_et_abandon_entendu(self):
        from donjon import echanges
        from tests.test_gardien_detresse import GardienDetresseTests
        from donjon.planification import _MEMOIRE, _GRAPHES
        m = GardienDetresseTests().lumiere()
        with patch.object(Monde, 'd20', return_value=20):
            d.choisir(m, 'bram', m.data['minutes'])
            demande = copy.deepcopy(lire(m, 'bram')['intention'])
            self.assertEqual(demande['plan'][0]['operation'], 'confier')
            self.assertTrue(echanges.executer(m, 'bram', demande['plan'][0], []))
        for _ in range(3):
            m = recharger(m)
            _MEMOIRE.clear()
            _GRAPHES.clear()
            d.choisir(m, 'bram', m.data['minutes'])
            i = lire(m, 'bram')['intention']
            self.assertEqual(i['but'], demande['but'])
            self.assertEqual(i['plan'], [])
            self.assertEqual(agendas.contrat_intention(m, 'bram')['phase'], 'attendre')
            self.assertFalse(m.objets['chandelle']['allume'])
            self.assertEqual(rendu(m), rendu(recharger(m)))
        n = recharger(m.copier())
        executer(m, 2)
        for _ in range(2):
            executer(n, 1)
            n = recharger(n)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertTrue(m.objets['chandelle']['allume'])
        # Une annulation reçue retire bien la cause de l'attente. La lecture
        # de l'intention privée de Josse n'est pas nécessaire pour la terminer.
        m = GardienDetresseTests().lumiere()
        with patch.object(Monde, 'd20', return_value=20):
            d.choisir(m, 'bram', m.data['minutes'])
            echanges.executer(m, 'bram', lire(m, 'bram')['intention']['plan'][0], [])
        d.choisir(m, 'bram', m.data['minutes'])
        condition = {'objet': 'chandelle', 'allume': True}
        echanges.retenir_abandon(m, 'josse', {'pour': 'bram', 'condition': condition})
        m = recharger(m)
        d.choisir(m, 'bram', m.data['minutes'])
        self.assertNotIn('chandelle', lire(m, 'bram')['aides_attendues'])
        i = lire(m, 'bram')['intention']
        self.assertFalse(i and i['but'] == demande['but'] and not i['plan'])
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_relais_1985_de_211_ne_perd_pas_un_secours_sur_un_eveil(self):
        from donjon import banc_pnj
        creer = banc_pnj.creer
        choisir = d.choisir
        parties = []
        hors_vue = []

        def creation(*args, **kwargs):
            m = creer(*args, **kwargs)
            parties.append(m)
            return m

        def observer(m, auteur, minute):
            e = lire(m, auteur)
            avant = copy.deepcopy(e['intention'])
            contrat = agendas.contrat_intention(m, auteur)
            demande = (contrat or {}).get('demande') or {}
            raison = demande.get('raison')
            eligible = False
            if avant and raison:
                corps = e['croyances'].get(raison['qui'], {}).get('etat', {}).get('valeur', {})
                eligible = (raison['qui'] not in percus(m, auteur)[0] and corps.get(raison['besoin'])
                            and not corps.get('mort') and corps.get('conscient') is not False)
            resultat = choisir(m, auteur, minute)
            if eligible:
                hors_vue.append(auteur)
                apres = lire(m, auteur)['intention']
                if apres is None:
                    dormantes = lire(m, auteur)['demandes_suspendues'].values()
                    if any(s['demande'] == demande for s in dormantes):
                        self.assertIsNone(d._reprendre_demande(m, auteur, demande))
                        return resultat
                    # La part peut avoir été réellement servie avant que
                    # la croyance de faim du bénéficiaire soit rafraîchie.
                    self.assertTrue(d.satisfaite(m, auteur, demande['condition']))
                    dernier = agendas.dernier_contrat_intention(m, auteur)['contrat']
                    self.assertEqual(dernier['sortie']['cause'], 'accomplie')
                    return resultat
                self.assertIsNotNone(apres, (auteur, minute, avant))
                if apres['but'] != avant['but']:
                    if any(s['demande'] == demande for s in lire(m, auteur)['demandes_suspendues'].values()):
                        self.assertIsNone(d._reprendre_demande(m, auteur, demande))
                        return resultat
                    nouveau = agendas.contrat_intention(m, auteur)
                    self.assertIsNotNone(nouveau)
                    self.assertTrue(nouveau['palier'] < contrat['palier']
                                    or nouveau['palier'] == contrat['palier']
                                    and nouveau['valeur'] >= contrat['valeur'] + d.INERTIE)
            return resultat

        with patch.object(banc_pnj, 'creer', creation), patch.object(d, 'choisir', observer):
            banc_pnj.nuit('relais', 1985, 1 / 60, 'chambre_cloche', depart='tire')
        self.assertTrue(hors_vue, 'les secours hors de vue du Relais doivent être exercés')
        m = parties[0]
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))

    def test_captures_209_reelles_recharge_et_laps_decoupes(self):
        for nom, auteur, minutes in (('mine-42', 'remy', 4), ('auberge-1985', 'mireille', 10)):
            with self.subTest(capture=nom):
                # Mine : checkpoint réel sur 01ce467 immédiatement après le
                # choix de Rémy (725 dixièmes). Le contrat de ce test est la
                # persistance de l'aide adoptée, pas sa naissance fortuite
                # depuis le départ de la nuit. L'auberge exerce aussi sa naissance.
                capture = 'engagement-233-mine-42-adopte' if nom == 'mine-42' else f'engagement-213-{nom}'
                fichier = Path(__file__).parent / 'data' / f'{capture}.json.gz'
                m = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
                m = recharger(m)
                n = recharger(m.copier())
                demandes = []
                initial = agendas.contrat_intention(m, auteur)
                if nom == 'mine-42':
                    self.assertEqual(m.data['minutes'] * 600 + m.data.get('dixiemes', 0), 725)
                    self.assertEqual(initial['demande']['raison'], {'qui': 'odon', 'besoin': 'faim'})
                    self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
                    demandes.append(copy.deepcopy(initial['demande']))
                choisir = d.choisir

                def observer(monde, id, minute):
                    resultat = choisir(monde, id, minute)
                    if id == auteur:
                        contrat = agendas.contrat_intention(monde, id)
                        if contrat and contrat['demande'] and 'raison' in contrat['demande']:
                            demandes.append(contrat['demande'])
                    return resultat

                with patch.object(d, 'choisir', observer):
                    executer(m, minutes)
                self.assertTrue(demandes, 'le secours historique doit être réellement adopté')
                for _ in range(minutes):
                    executer(n, 1)
                    n = recharger(n)
                m = recharger(m)
                self.assertEqual(m.data, n.data)
                self.assertEqual(rendu(m), rendu(n))
                self.assertTrue(any(c['pnj'] == auteur for c in m.data['chronique']))

    def test_secours_adopte_hors_vue_et_dementi_apres_recharge(self):
        m, auteur, autre = scene()
        d.choisir(m, auteur, m.data['minutes'])
        but = copy.deepcopy(lire(m, auteur)['intention']['but'])
        contrat = agendas.contrat_intention(m, auteur)
        self.assertEqual(contrat['demande']['raison'], {'qui': autre, 'besoin': 'faim'})
        placer(m, autre, 'galerie', [3, 1])
        percevoir_tous(m)
        self.assertNotIn(autre, percus(m, auteur)[0])
        self.assertTrue(lire(m, auteur)['croyances'][autre]['etat']['valeur']['faim'])
        m = recharger(m)
        # Une coupure de plan ne termine pas la condition à servir.
        lire(m, auteur)['intention']['plan'] = []
        d.choisir(m, auteur, m.data['minutes'])
        self.assertEqual(lire(m, auteur)['intention']['but'], but)
        apres = agendas.contrat_intention(m, auteur)
        self.assertEqual(apres['demande'], contrat['demande'])
        self.assertEqual(apres['palier'], contrat['palier'])
        self.assertEqual(contrat['phase'], 'naitre')
        self.assertEqual(apres['phase'], 'continuer')
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        etat = dict(lire(m, auteur)['croyances'][autre]['etat']['valeur'], faim=False)
        croire(m, auteur, autre, 'etat', etat, 'vu')
        d.choisir(m, auteur, m.data['minutes'])
        self.assertIsNone(lire(m, auteur)['intention'])
        self.assertIsNone(agendas.contrat_intention(m, auteur))
        fin = agendas.dernier_contrat_intention(m, auteur)['contrat']
        self.assertEqual(fin['phase'], 'finir')
        self.assertEqual(fin['sortie']['cause'], 'accomplie')
        self.assertFalse(fin['sortie']['faits']['etat_cru']['faim'])
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))

    def test_preemption_ronde_par_secours_et_accomplissement_decoupe(self):
        m, auteur, autre = scene_repas()
        condition = {'lieu': 'galerie', 'periode': 30}
        m.objets[auteur]['profil']['pulsions'] = [{'besoin': 'devoir', 'condition': condition}]
        lire(m, auteur)['pulsions'] = []
        # La ronde était déjà adoptée avant la découverte du besoin d'autrui.
        lire(m, auteur)['intention'] = {'but': {'type': 'pulsion', **condition},
                                        'motif': 'devoir', 'plan': [], 'depuis': 0, 'attente': 0}
        d.choisir(m, auteur, 0)
        self.assertEqual(lire(m, auteur)['intention']['motif'], 'empathie')
        m = recharger(m)
        n = recharger(m.copier())
        executer(m, 6)
        for _ in range(3):
            executer(n, 2)
            n = recharger(n)
        m = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertLess(lire(m, autre)['besoins']['faim'], 70)
        self.assertEqual(sum(c['pnj'] == auteur and 'donne une part' in c['texte']
                             for c in m.data['chronique']), 1)

    def test_autre_secours_froid_hors_vue_et_accomplissement(self):
        m, auteur, autre = scene(True)
        d.choisir(m, auteur, 0)
        self.assertEqual(agendas.contrat_intention(m, auteur)['demande']['raison']['besoin'], 'chaleur')
        but = copy.deepcopy(lire(m, auteur)['intention']['but'])
        placer(m, autre, 'antichambre', [1, 3])
        percevoir_tous(m)
        self.assertNotIn(autre, percus(m, auteur)[0])
        m = recharger(m)
        d.choisir(m, auteur, 0)
        self.assertEqual(lire(m, auteur)['intention']['but'], but)
        n = recharger(m.copier())
        executer(m, 3)
        for _ in range(3):
            executer(n, 1)
            n = recharger(n)
        m = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertGreater(m.objets['brasero']['combustible'], 8)
        self.assertFalse(any(s['type'] == 'service_rendu' and s['de'] == auteur
                             for s in lire(m, autre)['memoire']))

    def test_garde_vide_marge_et_palier_superieur_apres_recharge(self):
        # INERTIE 5 + VOL/4 : à VOL 12 la marge vaut 8, à VOL 20 elle vaut 10.
        for vol, gain, change in ((12, 7, False), (12, 8, True), (20, 8, False),
                                  (4, 8, True), (20, 100, True)):
            m, auteur, _ = scene()
            m.objets[auteur]['profil']['caracteristiques']['VOL'] = vol
            garde = {'type': 'garder', 'lieu': m.objets[auteur]['lieu']}
            secours = {'type': 'voir', 'lieu': 'galerie'}
            lire(m, auteur)['intention'] = {'but': garde, 'motif': 'biens', 'plan': [],
                                            'depuis': 0, 'attente': 0}
            m = recharger(m)
            palier = d.Palier.SECOURS if gain == 100 else d.Palier.ROUTINE
            cs = [d.Candidat('devoir', lambda m, i: (secours, [_etape('inspecter', lieu='galerie')]),
                              True, True, d.Urgence(palier, 0 if gain == 100 else gain, ())),
                  d.Candidat('biens', lambda m, i: (garde, []), True, True,
                              d.Urgence(d.Palier.ROUTINE, 0, ()))]
            with patch.object(d, '_candidats', return_value=cs):
                d.choisir(m, auteur, 0)
            self.assertEqual(lire(m, auteur)['intention']['but'], secours if change else garde)
            contrat = agendas.contrat_intention(m, auteur)
            if not change:
                self.assertEqual(contrat['phase'], 'attendre')
            else:
                self.assertEqual(contrat['sortie']['cause'], 'palier' if gain == 100 else 'gain')
                with patch.object(d, '_candidats', return_value=cs):
                    d.choisir(m, auteur, 0)
                self.assertEqual(agendas.contrat_intention(m, auteur)['sortie'], contrat['sortie'])
            n = recharger(m)
            self.assertEqual(m.data, n.data)
            self.assertEqual(rendu(m), rendu(n))

    def test_echec_sans_demande_typee_libere_ses_preferences_de_cible(self):
        m, auteur, autre = scene()
        d.choisir(m, auteur, 0)
        lire(m, auteur)['contrat_intention']['contrat']['demande'] = None
        i = lire(m, auteur)['intention']
        self.assertTrue(i['plan'])
        lire(m, auteur)['manque'] = {'minute': 0,
                                    'etape': {k: i['plan'][0][k] for k in ('operation', 'cible', 'outil', 'lieu')}}
        m = recharger(m)
        observes = []

        def candidats(monde, id):
            observes.append(lire(monde, id)['intention'])
            return []

        with patch.object(d, '_candidats', candidats):
            d.choisir(m, auteur, 0)
        self.assertEqual(observes, [None])
        self.assertIsNone(lire(m, auteur)['intention'])
        fin = agendas.dernier_contrat_intention(m, auteur)['contrat']
        self.assertEqual(fin['phase'], 'finir')
        self.assertEqual(fin['sortie']['cause'], 'dementie')
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))

    def recharge_complete(self, m):
        avant = copy.deepcopy(m.data)
        texte, scene = rendu(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(avant, n.data)
        self.assertEqual(texte, rendu(n))
        self.assertEqual(scene, scene_percue(n))
        return n

    @staticmethod
    def marquer_echec(m, auteur):
        from donjon.pnj import _geste
        lire(m, auteur)['manque'] = {
            'minute': m.data['minutes'],
            'etape': _geste(lire(m, auteur)['intention']['plan'][0])}

    def test_capture_273_echec_ancien_revalide_hors_vue_sans_renaissance(self):
        fichier = Path(__file__).parent / 'data/demande-273-relais-2024-117503.json.gz'
        m = self.recharge_complete(Monde(json.loads(gzip.decompress(fichier.read_bytes()))))
        avant = copy.deepcopy(lire(m, 'aubin')['intention'])
        contrat = agendas.contrat_intention(m, 'aubin')
        self.assertNotIn('ilse', percus(m, 'aubin')[0])
        self.assertIsNone(d._fin_demande(m, 'aubin', contrat['demande']))
        with patch.object(d, '_reprendre_demande', wraps=d._reprendre_demande) as reprise:
            d.choisir(m, 'aubin', m.data['minutes'])
        reprise.assert_called_once_with(m, 'aubin', contrat['demande'])
        self.assertEqual(lire(m, 'aubin')['intention']['but'], avant['but'])
        self.assertEqual(lire(m, 'aubin')['intention']['depuis'], avant['depuis'])
        apres = agendas.contrat_intention(m, 'aubin')
        self.assertEqual(apres['demande'], contrat['demande'])
        self.assertEqual(apres['palier'], contrat['palier'])
        self.assertEqual(apres['phase'], 'continuer')
        self.assertIsNone(apres['sortie'])
        # Une part reçue est maintenant liée au but : le service concret peut
        # remplacer la demande refusée, sans retenter celle-ci dans la minute.
        from donjon.pnj import agir, ATTENTE
        from donjon.temps import instant
        sonde = self.recharge_complete(m)
        from donjon.pnj import _geste
        meme_geste = _geste(lire(sonde, 'aubin')['intention']['plan'][0]) == lire(sonde, 'aubin')['manque']['etape']
        issue = agir(sonde, 'aubin', instant(sonde), [])[1]
        if meme_geste:
            self.assertEqual(issue, ATTENTE)
        else:
            self.assertEqual(lire(m, 'aubin')['intention']['plan'][0]['operation'], 'servir')
        m = self.recharge_complete(m)
        n = self.recharge_complete(m)
        choix, phases = d.choisir, [apres['phase']]
        faim = lire(m, 'ilse')['besoins']['faim']

        def observer(monde, id, minute):
            choix(monde, id, minute)
            if id == 'aubin':
                c = agendas.contrat_intention(monde, id)
                if c and c['demande'] == contrat['demande']:
                    phases.append(c['phase'])
                    self.assertIsNone(c['sortie'])

        with patch.object(d, 'choisir', observer):
            executer(m, 2)
        for _ in range(2):
            executer(n, 1)
            n = self.recharge_complete(n)
        # La capture possède déjà la part ; le service aboutit avant un
        # prochain choix. L'ancienne attente d'un retour perceptif n'est plus
        # sa prémisse : vérifier la conséquence effective, pas seulement le plan.
        self.assertLess(lire(m, 'ilse')['besoins']['faim'], faim)
        self.assertTrue(any(c['pnj'] == 'aubin' and 'donne une part' in c['texte']
                            for c in m.data['chronique']))
        self.assertNotIn('naitre', phases)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        self.recharge_complete(m)

    def test_demande_adoptee_attend_obstacle_puis_reprend_hors_vue(self):
        m, auteur, autre = scene_repas()
        d.choisir(m, auteur, 0)
        avant = copy.deepcopy(lire(m, auteur)['intention'])
        contrat = agendas.contrat_intention(m, auteur)
        self.marquer_echec(m, auteur)
        placer(m, autre, 'galerie', [3, 1])
        percevoir_tous(m)
        croire(m, auteur, autre, 'lieu', 'galerie', 'entendu', salle='galerie', case=[3, 1])
        m.objets['vivres']['portions'] = 0
        constater(m, auteur, 'vivres', 'essai')
        m = self.recharge_complete(m)
        for _ in range(3):
            self.assertNotIn(autre, percus(m, auteur)[0])
            d.choisir(m, auteur, m.data['minutes'])
            self.assertNotEqual((lire(m, auteur)['intention'] or {}).get('but'), avant['but'])
            apres = next(iter(lire(m, auteur)['demandes_suspendues'].values()))
            self.assertEqual(apres['demande'], contrat['demande'])
            self.assertEqual(apres['palier'], contrat['palier'])
            self.assertEqual(apres['depuis'], avant['depuis'])
            self.assertIsNone(d._reprendre_demande(m, auteur, contrat['demande']))
            m = self.recharge_complete(m)
        n = self.recharge_complete(m)
        executer(m, 2)
        for _ in range(2):
            executer(n, 1)
            n = self.recharge_complete(n)
        self.assertEqual(m.data, n.data)
        self.assertTrue(lire(m, auteur)['demandes_suspendues'])
        m = self.recharge_complete(m)
        # Le seul constat nouveau est le moyen redevenu disponible ; la
        # cible reste hors de vue. Aucun délai ni nouvelle naissance requis.
        m.objets['vivres']['portions'] = 8
        constater(m, auteur, 'vivres', 'essai')
        d.choisir(m, auteur, m.data['minutes'])
        self.assertNotIn(autre, percus(m, auteur)[0])
        self.assertTrue(lire(m, auteur)['intention']['plan'])
        self.assertEqual(lire(m, auteur)['intention']['depuis'], avant['depuis'])
        self.assertEqual(agendas.contrat_intention(m, auteur)['phase'], 'continuer')
        m = self.recharge_complete(m)
        n = self.recharge_complete(m)
        executer(m, 6)
        for _ in range(6):
            executer(n, 1)
            n = self.recharge_complete(n)
        self.assertEqual(m.data, n.data)
        self.assertLess(lire(m, autre)['besoins']['faim'], 70)
        self.assertLess(m.objets['vivres']['portions'], 8)
        self.assertIn('donne une part', str(m.data['chronique']))
        self.recharge_complete(m)

    def test_plan_dementi_ne_recopie_pas_un_suffixe_perime(self):
        m, auteur, _ = scene()
        d.choisir(m, auteur, 0)
        i = lire(m, auteur)['intention']
        tete = copy.deepcopy(i['plan'][0])
        i['plan'].append(_etape('inspecter', lieu='bureau'))
        self.marquer_echec(m, auteur)
        m = self.recharge_complete(m)
        with patch.object(d, '_candidats', return_value=[]), patch.object(
                d, '_reprendre_demande', return_value=(i['but'], [tete])):
            d.choisir(m, auteur, 0)
        self.assertEqual(lire(m, auteur)['intention']['plan'], [tete])
        self.assertIsNone(agendas.contrat_intention(m, auteur)['sortie'])
        self.recharge_complete(m)

    def test_echec_ne_masque_ni_fin_attestee_ni_preemption(self):
        for cause in ('dementie', 'palier'):
            with self.subTest(cause=cause):
                m, auteur, autre = scene()
                d.choisir(m, auteur, 0)
                self.marquer_echec(m, auteur)
                if cause == 'dementie':
                    etat = dict(lire(m, auteur)['croyances'][autre]['etat']['valeur'], mort=True)
                    croire(m, auteur, autre, 'etat', etat, 'vu')
                else:
                    lire(m, auteur)['besoins']['faim'] = 90.
                m = self.recharge_complete(m)
                d.choisir(m, auteur, 0)
                c = agendas.dernier_contrat_intention(m, auteur)['contrat']
                self.assertEqual(c['sortie']['cause'], cause)
                self.assertNotIn('manque', c['sortie']['faits'])
                if cause == 'dementie':
                    self.assertTrue(c['sortie']['faits']['etat_cru']['mort'])
                else:
                    self.assertLess(c['sortie']['faits']['palier_nouveau'],
                                    c['sortie']['faits']['palier_actif'])
                    self.assertEqual(lire(m, auteur)['intention']['motif'], 'faim')
                self.recharge_complete(m)

    def test_disposition_nouvelle_dement_le_secours_sans_apaiser_la_cible(self):
        m, auteur, autre = scene()
        d.choisir(m, auteur, 0)
        lire(m, auteur)['relations'][autre] = relations._nouvelle({'rancune': 80, 'affection': 40})
        m = recharger(m)
        d.choisir(m, auteur, 0)
        self.assertTrue(lire(m, auteur)['croyances'][autre]['etat']['valeur']['faim'])
        self.assertIsNone(lire(m, auteur)['intention'])
        sortie = agendas.dernier_contrat_intention(m, auteur)['contrat']['sortie']
        self.assertEqual(sortie['cause'], 'dementie')
        self.assertTrue(sortie['faits']['disposition']['rancune'])
        executer(m, 1)
        self.assertEqual(m.objets['vivres']['portions'], 8)
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))


if __name__ == '__main__':
    unittest.main()
