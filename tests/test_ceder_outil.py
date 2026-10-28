"""Valeur marginale commune, cessions et prêts après sauvegarde."""
import copy
import unittest
from unittest.mock import patch

from donjon.biens import valeur_bien
from donjon.echanges import offre_sensee, executer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.rendu import regarder
from tests import test_contreparties
from tests.test_tensions import recharger


class CederOutilTests(unittest.TestCase):
    def scene(self):
        m = test_contreparties.ContrepartiesTests().auberge()
        lire(m, 'lucien')['intention'] = None
        # La besace ordinaire ne contient ni pièces ni capacité mécanique.
        m.objets['ballot']['prix'] = 2
        lire(m, 'lucien')['besoins']['faim'] = 65
        return recharger(m)

    def test_lucien_garde_sa_capacite_hors_plan_et_sans_pieces(self):
        m = self.scene()
        demande = {'type': 'objet', 'objet': 'ballot'}
        contre = {'type': 'objet', 'objet': 'crochets_lucien'}
        self.assertGreater(valeur_bien(m, 'lucien', contre['objet']), valeur_bien(m, 'lucien', 'ballot'))
        self.assertFalse(offre_sensee(m, 'lucien', 'anselme', demande, contre))
        avant = copy.deepcopy(m.data)
        lignes = []
        self.assertFalse(executer(m, 'lucien', dict(operation='proposer', cible='anselme',
            outil='ballot', lieu='', condition='', contenu=dict(demande=demande, contrepartie=contre)), lignes))
        self.assertEqual(m.data, avant)
        recharge = recharger(m)
        self.assertEqual(recharge.data, m.data)
        self.assertEqual(regarder(recharge), regarder(m))
        self.assertEqual(recharge.objets['crochets_lucien']['lieu'], 'lucien')
        self.assertEqual(lignes, [])
        lire(m, 'lucien')['besoins']['faim'] = 100
        self.assertFalse(offre_sensee(recharger(m), 'lucien', 'anselme', demande, contre))

    def test_doublon_reduit_la_perte_sans_devalorisation_aveugle(self):
        m = self.scene()
        seul = valeur_bien(m, 'lucien', 'crochets_lucien')
        m.objets['second_outil'] = {**m.objets['crochets_lucien'], 'id': 'second_outil'}
        croire(m, 'lucien', 'second_outil', 'lieu', 'lucien', 'savoir', salle='salle_commune', case=[3, 3])
        self.assertLess(valeur_bien(recharger(m), 'lucien', 'crochets_lucien'), seul)
        del m.objets['second_outil']
        lire(m, 'lucien')['croyances'].pop('second_outil')
        lire(m, 'lucien')['besoins']['faim'] = 100
        self.assertEqual(valeur_bien(recharger(m), 'lucien', 'crochets_lucien'), seul)

    def test_gaspard_et_autre_outil_meme_estimation(self):
        from donjon.mine import nouveau_mine
        from tests.support import presentes, calme
        from donjon.spatial import installer
        m = presentes(nouveau_mine(depart='fixe'))
        installer(m)
        calme(m, 'gaspard')
        percevoir_tous(m)
        lire(m, 'gaspard')['intention'] = None
        # Le seul moyen durable d'allumer ; la lampe est éteinte.
        for k, o in m.objets.items():
            if 'allume' in o:
                croire(m, 'gaspard', k, 'etat', {'allume': False, 'charge': True}, 'savoir')
        for usages in (['allumage'], ['couper_bois']):
            with self.subTest(usages=usages):
                m.objets['briquet']['usages'] = usages
                lire(m, 'gaspard')['besoins']['faim'] = 65
                m = recharger(m)
                outil = {'type': 'objet', 'objet': 'briquet'}
                repas = {'type': 'part', 'objet': 'vivres'}
                # Le jugement inversé qui protège toute contrepartie est commun.
                from donjon.echanges import valeur_proposition
                self.assertGreater(valeur_proposition(m, 'gaspard', outil, 'mathe'),
                                   valeur_proposition(m, 'gaspard', repas, 'gaspard'))
                lire(m, 'gaspard')['besoins']['faim'] = 100
                self.assertLess(valeur_proposition(recharger(m), 'gaspard', outil, 'mathe'),
                                valeur_proposition(m, 'gaspard', repas, 'gaspard'))

    def test_pas_de_capacite_inutilisable_ni_contenu_cache(self):
        m = self.scene()
        m.objets['lucien']['profil']['capacites'] = []
        from donjon.caractere import valeur_pieces
        m.objets['crochets_lucien'].pop('prix', None)
        self.assertEqual(valeur_bien(m, 'lucien', 'crochets_lucien'), valeur_pieces(m, 'lucien', 1))
        avant = valeur_bien(m, 'lucien', 'bourse_anselme')
        m.objets['bourse_anselme']['pieces'] += 10000
        self.assertEqual(valeur_bien(recharger(m), 'lucien', 'bourse_anselme'), avant)

    def test_estimation_adverse_ne_decouvre_pas_un_outil_cache(self):
        from donjon.echanges import anticiper_valeur
        m = self.scene()
        m.objets['crochets_lucien']['usages'] = ['allumage']
        demande = {'type': 'objet', 'objet': 'ballot'}
        contre = {'type': 'objet', 'objet': 'crochets_lucien'}
        avant = anticiper_valeur(m, 'lucien', 'anselme', demande, contre)
        m.objets['allumage_cache'] = {**m.objets['crochets_lucien'], 'id': 'allumage_cache',
                                    'lieu': 'anselme', 'proprietaire': 'anselme'}
        self.assertEqual(anticiper_valeur(recharger(m), 'lucien', 'anselme', demande, contre), avant)

    def test_vente_ordinaire_compte_la_capacite_perdue(self):
        from donjon.echanges import demander
        m = self.scene()
        self.assertEqual(demander(m, 'anselme', 'lucien', 'crochets_lucien', prix=1), 'necessaire')
        recharge = recharger(m)
        self.assertEqual(recharge.objets['crochets_lucien']['lieu'], 'lucien')
        self.assertEqual(regarder(recharge), regarder(m))
        avant = m.data['finances_pnj']['anselme']
        self.assertEqual(demander(m, 'anselme', 'lucien', 'crochets_lucien', prix=3), 'vendu')
        recharge = recharger(m)
        self.assertEqual(recharge.objets['crochets_lucien']['proprietaire'], 'anselme')
        self.assertEqual(recharge.data['finances_pnj']['anselme'], avant - 3)
        self.assertEqual(regarder(recharge), regarder(m))

    def test_cession_compensee_et_laps_decoupe(self):
        from donjon.monde import Monde
        from donjon import relations
        m = self.scene()
        lire(m, 'lucien')['besoins']['faim'] = 100
        m.objets['ballot']['prix'] = 5
        m.objets['crochets_lucien']['prix'] = 5
        lire(m, 'anselme')['relations']['lucien'] = relations._nouvelle({'confiance': 70})
        m.objets['anselme']['profil']['pulsions'] = []
        lire(m, 'anselme')['pulsions'] = []
        demande = {'type': 'objet', 'objet': 'ballot'}
        contre = {'type': 'objet', 'objet': 'crochets_lucien'}
        geste = dict(operation='proposer', cible='anselme', outil='ballot', lieu='', condition='',
                     contenu=dict(demande=demande, contrepartie=contre))
        self.assertTrue(offre_sensee(m, 'lucien', 'anselme', demande, contre))
        lire(m, 'lucien')['intention'] = dict(but={'type': 'argent', 'objet': 'ballot'},
            motif='argent', plan=[geste], depuis=0, attente=0)
        lignes = []
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(executer(m, 'lucien', geste, lignes))
        m = recharger(m)
        self.assertEqual(m.objets['crochets_lucien']['proprietaire'], 'anselme')
        self.assertEqual(m.objets['ballot']['proprietaire'], 'lucien')
        self.assertTrue(any(s['type'] == 'proposition' and s['issue'] == 'accepte'
                        for s in lire(m, 'lucien')['memoire']))
        entier, decoupe = recharger(m), recharger(m)
        from donjon.pnj import avancer
        with patch.object(Monde, 'd20', return_value=20):
            # avancer rejoue jusqu'à l'heure courante : l'horloge doit avoir
            # avancé, sinon les deux appels découpés rejouent le même passé.
            entier.data['minutes'] += 2
            avancer(entier, 2, [])
            for _ in range(2):
                decoupe.data['minutes'] += 1
                avancer(decoupe, 1, [])
                decoupe = recharger(decoupe)
        entier = recharger(entier)
        for k in ('crochets_lucien', 'ballot'):
            self.assertEqual(entier.objets[k], decoupe.objets[k])
        self.assertEqual(entier.data['finances_pnj'], decoupe.data['finances_pnj'])
        for monde in (entier, decoupe):
            self.assertEqual(recharger(monde).data, monde.data)
            self.assertEqual(regarder(recharger(monde)), regarder(monde))
        self.assertEqual(regarder(entier), regarder(decoupe))

    def test_gaspard_marche_reel_refus_puis_doublon_ou_desespoir(self):
        from donjon.mine import nouveau_mine
        from donjon.monde import Monde
        from donjon import relations
        from donjon.spatial import installer
        from tests.support import presentes, calme, regarder as orienter
        from tests.test_tensions import placer
        for variante in ('seul', 'doublon', 'autre_flamme', 'desespoir'):
            with self.subTest(variante=variante):
                m = presentes(nouveau_mine(depart='fixe'))
                installer(m)
                calme(m, *(i for i, o in m.objets.items() if o.get('profil')))
                placer(m, 'gaspard', 'baraquement', [3, 5])
                placer(m, 'mathe', 'baraquement', [3, 4])
                m.joueur.update(salle='baraquement', position=[4, 4], orientation='ouest')
                orienter(m, 'gaspard', 'mathe')
                orienter(m, 'mathe', 'gaspard')
                for o in m.objets.values():
                    if 'allume' in o:
                        o['allume'] = False
                m.objets['vivres'].update(lieu='mathe', portions=8)
                m.objets['mathe']['profil']['pulsions'] = []
                lire(m, 'mathe')['pulsions'] = []
                lire(m, 'mathe')['relations']['gaspard'] = relations._nouvelle({'confiance': 70})
                if variante == 'doublon':
                    m.objets['second_briquet'] = {**m.objets['briquet'], 'id': 'second_briquet'}
                if variante == 'autre_flamme':
                    m.objets['lampe_gaspard']['allume'] = True
                percevoir_tous(m)
                lire(m, 'gaspard')['intention'] = None
                lire(m, 'gaspard')['besoins']['faim'] = 100 if variante == 'desespoir' else 65
                m = recharger(m)
                demande = {'type': 'part', 'objet': 'vivres'}
                contre = {'type': 'objet', 'objet': 'briquet'}
                possible = variante != 'seul'
                self.assertEqual(offre_sensee(m, 'gaspard', 'mathe', demande, contre), possible)
                lire(m, 'gaspard')['intention'] = dict(but={'type': 'manger', 'objet': 'vivres'},
                    motif='faim', plan=[], depuis=0, attente=0)
                lignes = []
                with patch.object(Monde, 'd20', return_value=20):
                    fait = executer(m, 'gaspard', dict(operation='proposer', cible='mathe', outil='vivres',
                        lieu='', condition='', contenu=dict(demande=demande, contrepartie=contre)), lignes)
                self.assertEqual(fait, possible)
                recharge = recharger(m)
                self.assertEqual(recharge.objets['briquet']['proprietaire'], 'mathe' if possible else 'gaspard')
                self.assertEqual(recharge.data, m.data)
                self.assertEqual(regarder(recharge), regarder(m))
                if possible:
                    self.assertTrue(any(s['type'] == 'proposition' and s['issue'] == 'accepte'
                                        for s in lire(m, 'gaspard')['memoire']))
                else:
                    self.assertEqual(lignes, [])

    def test_pret_conserve_la_capacite_et_obligation_de_rendre(self):
        from donjon.echanges import demander
        from donjon.biens import prete_a
        from donjon.monde import Monde
        m = self.scene()
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(demander(m, 'anselme', 'lucien', 'crochets_lucien'), 'remis')
        m = recharger(m)
        self.assertEqual(m.objets['crochets_lucien']['proprietaire'], 'lucien')
        self.assertEqual(prete_a(m, 'crochets_lucien'), 'anselme')
        from donjon import agendas
        self.assertTrue(agendas.en_cours(m, 'anselme', condition={'objet': 'crochets_lucien', 'rendre': 'lucien'}))
        self.assertEqual(regarder(recharger(m)), regarder(m))

    def test_doublon_reste_fonde_sur_le_lieu_cru(self):
        m = self.scene()
        seul = valeur_bien(m, 'lucien', 'crochets_lucien')
        m.objets['double'] = {**m.objets['crochets_lucien'], 'id': 'double', 'lieu': 'anselme'}
        croire(m, 'lucien', 'double', 'lieu', 'lucien', 'savoir', salle='salle_commune', case=[3, 3])
        estimee = valeur_bien(m, 'lucien', 'crochets_lucien')
        self.assertLess(estimee, seul)
        m.objets['double']['lieu'] = 'lucien'
        self.assertEqual(valeur_bien(recharger(m), 'lucien', 'crochets_lucien'), estimee)

    def test_crue_couteau_cession_refusee_puis_bien_inutile_donne(self):
        from tests.test_proposer_recours import scene
        from donjon.echanges import proposer
        from donjon.monde import Monde
        m = scene(70)
        m.objets['couteau'].update(lieu='brune', proprietaire='brune')
        m.data['connus'].append('couteau')
        percevoir_tous(m)
        lire(m, 'brune')['intention'] = None
        m = recharger(m)
        don = {'type': 'objet', 'objet': 'couteau'}
        rien = {'type': 'rien'}
        self.assertEqual(proposer(m, 'joueur', 'brune', don, rien)['cause'], 'necessaire')
        self.assertEqual(recharger(m).objets['couteau']['lieu'], 'brune')
        m.objets['couteau']['usages'] = []
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(proposer(m, 'joueur', 'brune', don, rien)['accepte'])
        recharge = recharger(m)
        self.assertEqual(recharge.objets['couteau']['proprietaire'], 'joueur')
        self.assertEqual(recharge.data, m.data)
        self.assertEqual(regarder(recharge), regarder(m))

    def test_cle_connue_et_source_ne_lisent_pas_les_etats_caches(self):
        from donjon.biens import capacites_crues
        m = self.scene()
        outil = m.objets['crochets_lucien']
        outil.update(usages=[], ouvre=['ballot'], allume=False, charge=0)
        self.assertIn('cle:ballot', capacites_crues(m, 'lucien', outil['id']))
        lire(m, 'lucien')['croyances'].pop('ballot', None)
        self.assertNotIn('cle:ballot', capacites_crues(m, 'lucien', outil['id']))
        croire(m, 'lucien', outil['id'], 'etat', {'allume': False, 'charge': True}, 'savoir')
        estimee = capacites_crues(m, 'lucien', outil['id'])
        self.assertIn('lumiere', estimee)
        self.assertNotIn('allumage', estimee)
        outil.update(allume=True, charge=100)
        self.assertEqual(capacites_crues(recharger(m), 'lucien', outil['id']), estimee)

    def test_remplacement_equivalent_conserve_la_capacite_dans_le_troc(self):
        from donjon.echanges import proposer
        from donjon.monde import Monde
        m = self.scene()
        m.objets['ballot']['usages'] = ['crochetage']
        croire(m, 'anselme', 'crochets_lucien', 'lieu', 'lucien', 'savoir', salle='salle_commune', case=[3, 3])
        demande = {'type': 'objet', 'objet': 'crochets_lucien'}
        contre = {'type': 'objet', 'objet': 'ballot'}
        with patch.object(Monde, 'd20', return_value=20):
            bilan = proposer(m, 'anselme', 'lucien', demande, contre)
        self.assertTrue(bilan.get('accepte'), bilan)
        recharge = recharger(m)
        self.assertEqual(recharge.objets['crochets_lucien']['proprietaire'], 'anselme')
        self.assertEqual(recharge.objets['ballot']['proprietaire'], 'lucien')
        self.assertEqual(recharge.data, m.data)
        self.assertEqual(regarder(recharge), regarder(m))


if __name__ == '__main__':
    unittest.main()


