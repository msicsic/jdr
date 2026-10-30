"""340 : contrat perçu → issue sourcée → épreuve durable, sans lecture privée."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, echanges, pnj, relations, social, planification
from donjon.caractere import prix_faute, FAUTE
from donjon.esprits import croire, lire, memoriser
from donjon.monde import Monde
from donjon.planification import _etape
from donjon.temps import ecouler
from donjon.voix import connaitre
from tests import test_agendas_compte_rendu as compte
from tests import test_agendas_reaffecter as reaffecter
from tests import test_agendas_faire_confier as faire
from tests.test_avis_menace import relation
from tests.test_social import placer
from tests.support import regarder as orienter


class AscendantEvolueTests(unittest.TestCase):
    def setUp(self):
        self.fixture = compte.CompteRenduTests()

    def charge(self, m, titulaire, identifiant):
        a = self.fixture.agenda(m, titulaire, identifiant)
        return {'mandant': a['origine']['de'], 'parent': a['origine']['parent'],
                'agenda': a['id'], 'sorte': a['sorte'], 'parametres': a['parametres']}

    def temoin(self, m, charge, titulaire='aubin', q='ilse', entendu=True):
        placer(m, q, 'antichambre', [3, 5] if q == 'ilse' else [4, 5])
        for x in (titulaire, charge['mandant']):
            connaitre(m, q, x)
            relation(m, q, x, confiance=100, affection=100, ascendant=40)
        lire(m, q)['croyances'].pop('brune', None)
        if entendu:
            social.recevoir(m, q, charge['mandant'], {
                'type': 'ordre_mandat', 'titulaire': titulaire, 'charge': charge})

    def test_gorm_aubin_reussite_echec_abus_et_estompement_sans_double(self):
        m, identifiant = self.fixture.scene()
        relation(m, 'aubin', 'marchand', confiance=100, affection=100, ascendant=55)
        self.fixture.terminer(m, identifiant, 'amener', 'reussi')
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 65)
        self.assertTrue(relations.axes(m, 'aubin', 'marchand')['bandes']['ascendant'])
        # Une deuxième charge réellement échue, sous le même mandant.
        parent = self.fixture.agenda(m, 'marchand', 'charge')
        parent2 = copy.deepcopy(parent)
        parent2.update(id='suite', etat='actif')
        for k in ('confies', 'attributions', 'comptes_recus'):
            parent2.pop(k, None)
        lire(m, 'marchand')['agendas'].append(parent2)
        enfant = agendas.confier(m, 'marchand', 'suite', 'aubin', parent2['sorte'], parent2['parametres'],
                                 accepte=True, echeance=m.data['minutes'])
        self.fixture.agenda(m, 'aubin', enfant['id'])['echeance'] = m.data['minutes']
        m.data['minutes'] += 1
        agendas.actualiser(m, 'aubin')
        self.assertEqual(self.fixture.agenda(m, 'aubin', enfant['id'])['etat'], 'abandonne')
        # L'ancre initiale (60) et l'estompement exact font franchir un arrondi.
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 54)
        # L'eau crue au rendez-vous constitue un péril, sans eau réelle inventée.
        parent3 = copy.deepcopy(parent2)
        parent3.update(id='peril', etat='actif')
        for k in ('confies', 'attributions'):
            parent3.pop(k, None)
        lire(m, 'marchand')['agendas'].append(parent3)
        croire(m, 'aubin', parent3['parametres']['lieu'], 'eau', 300, 'vu')
        enfant = agendas.confier(m, 'marchand', 'peril', 'aubin', parent3['sorte'], parent3['parametres'], accepte=True)
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 34)
        self.assertEqual(self.fixture.agenda(m, 'aubin', enfant['id'])['abus']['cause'], 'peril')
        m = self.fixture.recharge(m)
        # Écarter l'échec de cette troisième charge pour isoler l'abus déjà acquis.
        avant = copy.deepcopy(lire(m, 'aubin')['preuves_relations'])
        with agendas.evaluation(m, 'aubin', publier=False):
            agendas.actualiser(m, 'aubin')
        self.assertEqual(lire(m, 'aubin')['preuves_relations'], avant)
        self.fixture.recharge(m)

    def test_autre_scenario_mine_fin_de_charge_et_recharge(self):
        m, (mandant, titulaire, _, _, identifiant) = reaffecter.ReaffecterTests().scene('mine')
        relation(m, titulaire, mandant, confiance=100, ascendant=40)
        self.fixture.agenda(m, titulaire, identifiant)['echeance'] = m.data['minutes'] - 1
        agendas.actualiser(m, titulaire)
        self.assertEqual(relations.autorite_reconnue(m, titulaire, mandant), 30)
        m = self.fixture.recharge(m)
        for _ in range(3):
            agendas.actualiser(m, titulaire)
        self.assertEqual(relations.autorite_reconnue(m, titulaire, mandant), 30)
        self.assertEqual(self.fixture.agenda(m, titulaire, identifiant)['etat'], 'abandonne')
        self.fixture.recharge(m)

    def test_mine_reussite_puis_abus_sur_un_autre_contrat(self):
        m, (mandant, titulaire, _, cible, identifiant) = reaffecter.ReaffecterTests().scene('mine')
        relation(m, titulaire, mandant, confiance=100, ascendant=40)
        placer(m, cible, 'baraquement', [3, 3])
        croire(m, titulaire, cible, 'lieu', 'baraquement', 'vu', salle='baraquement', case=[3, 3])
        agendas.actualiser(m, titulaire)
        self.assertEqual(relations.autorite_reconnue(m, titulaire, mandant), 50)
        m = self.fixture.recharge(m)
        parent = copy.deepcopy(self.fixture.agenda(m, mandant, 'charge'))
        parent.update(id='mentir', sorte='informer', etat='actif', parametres={
            'qui': [cible], 'fait': {'type': 'affirmation', 'sujet': 'paie',
                                   'attribut': 'lieu', 'valeur': 'reserve'}})
        for k in ('confies', 'attributions'):
            parent.pop(k, None)
        lire(m, mandant)['agendas'].append(parent)
        croire(m, titulaire, 'paie', 'lieu', 'baraquement', 'vu', salle='baraquement', case=None)
        agendas.confier(m, mandant, 'mentir', titulaire, 'informer', parent['parametres'], accepte=True)
        self.assertEqual(relations.autorite_reconnue(m, titulaire, mandant), 30)
        self.fixture.recharge(m)

    def test_temoin_contrat_sans_issue_ignorant_et_constat(self):
        m, identifiant = self.fixture.scene()
        charge = self.charge(m, 'aubin', identifiant)
        self.temoin(m, charge)
        self.temoin(m, charge, q='seve', entendu=False)
        agendas.actualiser(m, 'ilse')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 40)
        self.fixture.terminer(m, identifiant, 'amener', 'reussi')
        # Le résultat privé d'Aubin et l'arrivée réelle ne sont pas des perceptions d'Ilse.
        agendas.actualiser(m, 'ilse')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 40)
        for q in ('ilse', 'seve'):
            croire(m, q, 'brune', 'lieu', 'chambre_cloche', 'vu', salle='chambre_cloche', case=[1, 3])
            agendas.actualiser(m, q)
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 50)
        self.assertEqual(relations.autorite_reconnue(m, 'seve', 'marchand'), 40)
        m = self.fixture.recharge(m)
        # Un déplacement ultérieur n'annule pas le mandat accompli constaté.
        croire(m, 'ilse', 'brune', 'lieu', 'antichambre', 'vu', salle='antichambre', case=[2, 5])
        agendas.actualiser(m, 'ilse')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 50)
        self.fixture.recharge(m)

    def test_compte_reel_temoin_ouidire_puis_constat_sans_double_gain(self):
        m, identifiant = self.fixture.scene()
        charge = self.charge(m, 'aubin', identifiant)
        self.temoin(m, charge, entendu=False)
        self.fixture.terminer(m, identifiant, 'amener', 'reussi')
        m = self.fixture.annoncer(m)
        indirect = relations.autorite_reconnue(m, 'ilse', 'marchand')
        self.assertGreater(indirect, 40)
        self.assertLess(indirect, 50)
        self.assertEqual(agendas.mandats_percus(m, 'ilse')[0]['croyance']['source'], 'dit:aubin')
        for _ in range(45):
            memoriser(m, 'ilse', {'type': 'bruit', 'salle': 'antichambre', 'nature': 'pas', 'niveau': 1})
        m = self.fixture.recharge(m)
        agendas.actualiser(m, 'ilse')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), indirect)
        croire(m, 'ilse', 'brune', 'lieu', 'chambre_cloche', 'vu', salle='chambre_cloche', case=[1, 3])
        agendas.actualiser(m, 'ilse')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 50)
        m = self.fixture.recharge(m)
        m.data['minutes'] += 60
        for _ in range(3):
            agendas.actualiser(m, 'ilse')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 49)
        self.fixture.recharge(m)

    def test_doute_voix_inconnue_et_echec_entendu(self):
        m, identifiant = self.fixture.scene()
        charge = self.charge(m, 'aubin', identifiant)
        self.temoin(m, charge, entendu=False)
        self.fixture.terminer(m, identifiant, 'amener', 'echoue')
        contenu = agendas.compte_a_rendre(m, 'aubin')
        with patch('donjon.voix.identifie', return_value=False):
            self.assertIsNone(social.recevoir(m, 'ilse', 'aubin', contenu))
        with patch('donjon.echanges.jet_persuasion', return_value=(False, 0, 0)):
            self.assertEqual(social.recevoir(m, 'ilse', 'aubin', contenu), 'doute')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 40)
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(social.recevoir(m, 'ilse', 'aubin', contenu), 'crue')
        self.assertGreater(relations.autorite_reconnue(m, 'ilse', 'marchand'), 30)
        self.assertLess(relations.autorite_reconnue(m, 'ilse', 'marchand'), 40)
        self.fixture.recharge(m)

    def test_ordre_contraire_au_savoir_prix_commun_et_aucune_faute_inventee(self):
        for honnetete in (0, 20, 100):
            m, _ = self.fixture.scene()
            relation(m, 'aubin', 'marchand', confiance=100, ascendant=50)
            m.objets['aubin']['profil']['valeurs']['honnetete'] = honnetete
            croire(m, 'aubin', 'brasero', 'lieu', 'beffroi', 'vu', salle='beffroi', case=None)
            parent = copy.deepcopy(self.fixture.agenda(m, 'marchand', 'charge'))
            parent.update(id='mensonge', sorte='informer', parametres={
                'qui': ['brune'], 'fait': {'type': 'affirmation', 'sujet': 'brasero',
                                          'attribut': 'lieu', 'valeur': 'antichambre'}})
            for k in ('confies', 'attributions'):
                parent.pop(k, None)
            lire(m, 'marchand')['agendas'].append(parent)
            prix = prix_faute(m, 'aubin')
            enfant = agendas.confier(m, 'marchand', 'mensonge', 'aubin', 'informer', parent['parametres'], accepte=True)
            agendas.actualiser(m, 'aubin')
            perte = 20 if prix is None else round(20 * min(1, prix / FAUTE))
            self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 50 - perte)
            self.fixture.recharge(m)
        m, identifiant = self.fixture.scene()
        relation(m, 'aubin', 'marchand', ascendant=50)
        lire(m, 'aubin')['croyances'].pop('brasero', None)
        agendas.actualiser(m, 'aubin')
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 50)
        self.assertNotIn('abus', self.fixture.agenda(m, 'aubin', identifiant))
        self.fixture.recharge(m)

    def test_evaluation_interrompue_et_publication_imbriquee(self):
        m, identifiant = self.fixture.scene()
        relation(m, 'aubin', 'marchand', ascendant=50)
        a = self.fixture.agenda(m, 'aubin', identifiant)
        a['echeance'] = m.data['minutes']
        m.data['minutes'] += 1
        avant = copy.deepcopy(m.data)
        with self.assertRaisesRegex(RuntimeError, 'interrompu'):
            with planification.vues_du_choix(m, 'aubin'):
                agendas.actualiser(m, 'aubin')
                self.assertEqual(m.data, avant)
                raise RuntimeError('interrompu')
        self.assertEqual(m.data, avant)
        with planification.vues_du_choix(m, 'aubin'):
            with planification.vues_du_choix(m, 'aubin'):
                agendas.actualiser(m, 'aubin')
                self.assertEqual(m.data, avant)
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 40)
        self.fixture.recharge(m)

    def test_laps_entier_decoupe_sur_fin_reelle_et_temoin(self):
        m, identifiant = self.fixture.scene()
        relation(m, 'aubin', 'marchand', ascendant=40)
        self.temoin(m, self.charge(m, 'aubin', identifiant))
        self.fixture.agenda(m, 'aubin', identifiant)['echeance'] = m.data['minutes']
        lire(m, 'aubin')['libre'] = 0
        lire(m, 'aubin')['intention'] = None
        a, b = self.fixture.recharge(m), self.fixture.recharge(m)
        with patch.object(Monde, 'd20', return_value=20):
            pnj.avancer(a, ecouler(a, 1200), [], 1200)
            for _ in range(4):
                pnj.avancer(b, ecouler(b, 300), [], 300)
        self.assertEqual(a.data, b.data)
        self.assertLess(relations.autorite_reconnue(a, 'aubin', 'marchand'), 40)
        self.fixture.recharge(a)

    def test_mandat_prononce_transporte_au_temoin_sans_nouvelle_parole(self):
        f = faire.FaireConfierTests()
        m, _ = f.scene('amener', 'brune')
        placer(m, 'ilse', 'crypte', [1, 2])
        connaitre(m, 'ilse', 'marchand')
        relation(m, 'ilse', 'marchand', ascendant=40)
        f.executer(m, f.choix(m)[1])
        percus = agendas.mandats_percus(m, 'ilse')
        self.assertEqual(len(percus), 1)
        self.assertEqual(percus[0]['de'], 'aubin')
        self.assertEqual(percus[0]['source'], 'entendu')
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 40)
        self.fixture.recharge(m)

    def test_ordre_abusif_refuse_et_temoin_sans_penalite_repetee(self):
        f = faire.FaireConfierTests()
        m, _ = f.scene('amener', 'brune')
        plan = f.choix(m)[1]
        placer(m, 'ilse', 'crypte', [1, 2])
        connaitre(m, 'ilse', 'marchand')
        for q in ('aubin', 'ilse'):
            relation(m, q, 'marchand', confiance=40 if q == 'aubin' else 100, ascendant=40)
            croire(m, q, plan[-1]['contenu']['mandat']['parametres']['lieu'], 'eau', 300, 'vu')
        f.executer(m, plan, roll=1)
        self.assertFalse(agendas.enfants(m, 'marchand', 'evacuer'))
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 20)
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 24)
        self.assertEqual(agendas.mandats_percus(m, 'ilse')[0]['charge']['agenda'], None)
        m = self.fixture.recharge(m)
        f.executer(m, plan, roll=1)
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 20)
        self.assertEqual(relations.autorite_reconnue(m, 'ilse', 'marchand'), 24)
        self.fixture.recharge(m)

    def test_marche_et_parole_reelles_fin_du_mandat(self):
        m, identifiant = self.fixture.scene()
        relation(m, 'aubin', 'marchand', confiance=100, ascendant=40)
        relation(m, 'brune', 'aubin', confiance=100, affection=100)
        croire(m, 'aubin', 'brune', 'lieu', 'antichambre', 'vu', salle='antichambre', case=[2, 5])
        orienter(m, 'aubin', 'brune')
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(echanges.executer(m, 'aubin', _etape('confier', 'brune', contenu={
                'objet': 'brune', 'lieu': 'chambre_cloche'}), []))
            lire(m, 'brune')['libre'] = 0
            pnj.avancer(m, ecouler(m, 1800), [], 1800)
        self.assertEqual(m.objets['brune']['lieu'], 'chambre_cloche')
        croire(m, 'aubin', 'brune', 'lieu', 'chambre_cloche', 'vu', salle='chambre_cloche', case=m.objets['brune']['position'])
        agendas.actualiser(m, 'aubin')
        self.assertEqual(relations.autorite_reconnue(m, 'aubin', 'marchand'), 50)
        self.assertEqual(self.fixture.agenda(m, 'aubin', identifiant)['etat'], 'atteint')
        m = self.fixture.annoncer(m)
        self.fixture.recharge(m)

    def test_mine_laps_entier_decoupe(self):
        m, (mandant, titulaire, _, _, identifiant) = reaffecter.ReaffecterTests().scene('mine')
        relation(m, titulaire, mandant, confiance=100, ascendant=40)
        self.fixture.agenda(m, titulaire, identifiant)['echeance'] = m.data['minutes'] - 1
        lire(m, titulaire)['libre'] = 0
        lire(m, titulaire)['intention'] = None
        a, b = self.fixture.recharge(m), self.fixture.recharge(m)
        with patch.object(Monde, 'd20', return_value=20):
            pnj.avancer(a, ecouler(a, 1200), [], 1200)
            for _ in range(4):
                pnj.avancer(b, ecouler(b, 300), [], 300)
        self.assertEqual(a.data, b.data)
        self.assertEqual(relations.autorite_reconnue(a, titulaire, mandant), 30)
        self.fixture.recharge(a)


if __name__ == '__main__':
    unittest.main()
