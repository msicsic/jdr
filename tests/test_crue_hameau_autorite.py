"""302 : les données d'autorité n'attribuent aucune tâche ni décision."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, banc_pnj, echanges, esprits, relations
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests import test_agendas_jugement_mandat as jugement
from tests.test_social import recharger


def donnees():
    return json.loads((Path(__file__).parents[1] / 'donjon/scenario_crue_hameau.json').read_text(encoding='utf-8'))


def sans_autorite(d):
    d = copy.deepcopy(d)
    for o in d['objets'].values():
        p = o.get('profil', {})
        p.pop('statuts', None)
        for lien in p.get('liens', {}).values():
            lien.pop('ascendant', None)
    return d


class AutoriteHameauTests(unittest.TestCase):
    def persiste(self, m):
        m.verifier()
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(regarder(n), regarder(m))
        self.assertEqual(scene_percue(n), scene_percue(m))
        return n

    def test_statut_source_portees_connaisseurs_et_liens(self):
        m = self.persiste(banc_pnj.creer('crue_hameau', 1985, 'fixe'))
        statut = donnees()['objets']['marchand']['profil']['statuts'][0]
        for qui in esprits.pnjs(m):
            for lieu in m.data['salles']:
                for domaine in ('amener', 'informer', 'combat'):
                    lu = relations.statuts_reconnus(m, qui, 'marchand', lieu, domaine)
                    connu = qui in statut['connus'] and lieu in statut['lieux'] and domaine in statut['domaines']
                    self.assertEqual(lu is not None, connu, (qui, lieu, domaine))
                    if connu:
                        self.assertEqual(lu['source'], 'savoir')
        self.assertIsNone(esprits.croyance(m, 'joueur', 'marchand', 'statuts'))
        liens = {('aubin', 'marchand'): 60, ('mael', 'aubin'): 30, ('seve', 'aubin'): 40}
        for a in esprits.pnjs(m):
            for b in esprits.pnjs(m):
                if a != b:
                    self.assertEqual(relations.axes(m, a, b)['ascendant'], liens.get((a, b), 0))
        # Aucun mandat ni projet social n'est ajouté par ces données.
        self.assertEqual(banc_pnj.mesures_mandats(m)['mandats_proposes'], 0)
        self.assertFalse(any(a['sorte'] in ('amener', 'informer')
                             for q in esprits.pnjs(m) for a in agendas.projets(m, q)))

    def test_profil_incoherent_refuse_et_limite_statut(self):
        m = banc_pnj.creer('crue_hameau', 1985, 'fixe')
        m.objets['marchand']['profil']['pulsions'][0]['echeance'] = -1
        with self.assertRaises(ErreurMonde) as refus:
            m.verifier()
        self.assertIn('echeance', refus.exception.attendu)
        self.assertIn('-1', refus.exception.attendu)
        m = banc_pnj.creer('crue_hameau', 1985, 'fixe')
        m.objets['marchand']['profil']['statuts'][0]['lieux'] = ['absent']
        with self.assertRaises(AssertionError):
            esprits.verifier_statuts(m, m.objets['marchand']['profil']['statuts'], declares=True)
        # Le validateur historique du statut n'a pas encore de refus structuré.
        # Ne pas lui fabriquer un attendu dans ce test de données.

    def test_contre_epreuve_initiale_sans_attribution_forcee(self):
        d = donnees()
        a, b = Monde(copy.deepcopy(d)), Monde(sans_autorite(d))
        from donjon.spatial import installer
        for m in (a, b):
            installer(m)
            self.persiste(m)
        self.assertEqual(sans_autorite(a.data)['objets'], sans_autorite(b.data)['objets'])
        self.assertEqual(a.data['jets'], b.data['jets'])
        self.assertEqual(regarder(a), regarder(b))
        self.assertEqual(scene_percue(a), scene_percue(b))
        self.assertEqual(banc_pnj.mesures_mandats(a), banc_pnj.mesures_mandats(b))

    def test_deux_charges_seul_bonus_explique_accord_et_scene_hors_crue(self):
        support = jugement.JugementMandatTests()
        for sorte, cible in [('amener', 'brune'), ('informer', 'ilse')]:
            with self.subTest(sorte=sorte):
                # Scène commune du Relais, hors crue : mêmes actions et devis.
                m, mandat = support.scene(sorte, cible)
                n = m.copier()
                n.objets['marchand']['profil']['statuts'] = copy.deepcopy(
                    donnees()['objets']['marchand']['profil']['statuts'])
                esprits.installer_statuts(n, 'aubin')
                roll = support.roll_limite(m, mandat)
                avant = copy.deepcopy(n.data)
                self.assertEqual(agendas.devis_mandat(m, 'marchand', 'evacuer', 'aubin', sorte, mandat['parametres']),
                                 agendas.devis_mandat(n, 'marchand', 'evacuer', 'aubin', sorte, mandat['parametres']))
                self.assertEqual(n.data, avant)
                with patch.object(Monde, 'd20', return_value=roll):
                    self.assertEqual(echanges.confier(m, 'marchand', 'aubin', mandat=mandat), 'refus')
                    self.assertEqual(echanges.confier(n, 'marchand', 'aubin', mandat=mandat), 'accepte')
                jm, jn = support.jugement(m), support.jugement(n)
                self.assertEqual(jm['cout'], jn['cout'])
                self.assertEqual(jm['total'], jn['total'])
                self.assertEqual(jm['dd'] - jn['dd'], 3)
                self.assertEqual(jn['raison'], 'autorite')
                for monde in (m, n):
                    self.persiste(monde)
                # Une demande ordinaire hors mandat garde exactement son résultat.
                a, b = support.scene(sorte, cible)[0], support.scene(sorte, cible)[0]
                b.objets['marchand']['profil']['statuts'] = copy.deepcopy(n.objets['marchand']['profil']['statuts'])
                esprits.installer_statuts(b, 'aubin')
                with patch.object(Monde, 'd20', return_value=10):
                    condition = {'objet': 'aubin', 'lieu': 'chambre_cloche'}
                    self.assertEqual(echanges.confier(a, 'marchand', 'aubin', condition),
                                     echanges.confier(b, 'marchand', 'aubin', condition))
                self.assertEqual(agendas.en_cours(a, 'aubin'), agendas.en_cours(b, 'aubin'))
                self.persiste(a)
                self.persiste(b)

    def test_compteurs_purs_persistants_confirmation_et_refus(self):
        support = jugement.JugementMandatTests()
        m, mandat = support.scene()
        with patch.object(Monde, 'd20', return_value=1):
            echanges.confier(m, 'marchand', 'aubin', mandat=mandat)
        with patch.object(Monde, 'd20', return_value=20):
            echanges.confier(m, 'marchand', 'aubin', mandat=mandat)
            echanges.confier(m, 'marchand', 'aubin', mandat=mandat)
        avant = copy.deepcopy(m.data)
        mesures = banc_pnj.mesures_mandats(m)
        self.assertEqual(mesures['mandats_proposes'], 2)
        self.assertEqual(mesures['mandats_acceptes'], 1)
        self.assertEqual(mesures['mandats_refuses_refus'], 1)
        self.assertEqual(mesures['mandats_confirmes'], 1)
        self.assertEqual(m.data, avant)
        self.assertEqual(banc_pnj.mesures_mandats(self.persiste(m)), mesures)
        # Les comptes ne se répètent pas sur une tranche sans parole nouvelle.
        with patch.object(banc_pnj, '_executer', return_value=([], {})):
            _, tranche = banc_pnj.executer(m, m.data['minutes'])
        self.assertEqual(tranche['mandats_proposes'], 0)

    def test_compteurs_reaffectation_et_compte_rendu_deux_mondes(self):
        from tests import test_agendas_reaffecter as remplacement
        from tests import test_agendas_compte_rendu as compte_rendu
        for scenario in ('crue_hameau', 'mine'):
            support = remplacement.ReaffecterTests()
            m, (a, b, c, cible, enfant) = support.scene(scenario)
            self.assertEqual(banc_pnj.mesures_mandats(m)['reaffectations'], 0)
            support.executer(m, a, support.plan(m, a)[1])
            self.assertEqual(banc_pnj.mesures_mandats(self.persiste(m))['reaffectations'], 1)
        support = compte_rendu.CompteRenduTests()
        for sorte in ('amener', 'informer'):
            m, enfant = support.scene(sorte)
            support.terminer(m, enfant, sorte, 'reussi')
            contenu = agendas.compte_a_rendre(m, 'aubin')
            self.assertIsNotNone(contenu)
            self.assertTrue(echanges.rendre_compte(m, 'aubin', contenu, []))
            self.assertFalse(echanges.rendre_compte(m, 'aubin', contenu, []))
            self.assertEqual(banc_pnj.mesures_mandats(self.persiste(m))['comptes_rendus'], 1)
