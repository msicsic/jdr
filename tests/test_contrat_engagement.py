"""L'intention survit à sa naissance ; priorités et démentis restent effectifs."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, relations
from donjon.esprits import croire, lire, percevoir_tous, percus
from donjon.planification import _etape
from donjon.monde import Monde
from tests.test_empathie import scene, executer, rendu
from tests.test_tensions import placer, recharger


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
                manque = e['manque']
                echec = bool(manque and manque['minute'] == minute and avant['plan']
                             and manque['etape'] == {k: avant['plan'][0][k]
                                                    for k in ('operation', 'cible', 'outil', 'lieu')})
                eligible = (raison['qui'] not in percus(m, auteur)[0] and corps.get(raison['besoin'])
                            and not corps.get('mort') and corps.get('conscient') is not False and not echec)
            resultat = choisir(m, auteur, minute)
            if eligible:
                hors_vue.append(auteur)
                apres = lire(m, auteur)['intention']
                if apres is None:
                    # La part peut avoir été réellement servie avant que
                    # la croyance de faim du bénéficiaire soit rafraîchie.
                    self.assertTrue(d.satisfaite(m, auteur, demande['condition']))
                    dernier = agendas.dernier_contrat_intention(m, auteur)['contrat']
                    self.assertEqual(dernier['sortie']['cause'], 'accomplie')
                    return resultat
                self.assertIsNotNone(apres, (auteur, minute, avant))
                if apres['but'] != avant['but']:
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
        m, auteur, autre = scene()
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

    def test_echec_libere_le_moyen_et_ses_preferences_sans_clore_la_demande(self):
        m, auteur, autre = scene()
        d.choisir(m, auteur, 0)
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
        apres = lire(m, auteur)['intention']
        self.assertEqual(apres['but'], i['but'])
        self.assertEqual(apres['depuis'], i['depuis'])
        self.assertEqual(apres['plan'], [])
        contrat = agendas.contrat_intention(m, auteur)
        self.assertEqual(contrat['phase'], 'attendre')
        self.assertIsNone(contrat['sortie'])
        self.assertIsNotNone(contrat['demande'])
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))

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
