"""Valeur marginale commune, marchés et acquisitions après sauvegarde."""
import copy
import unittest
from unittest.mock import patch

from donjon.biens import valeur_bien
from donjon.echanges import offre_sensee, executer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.planification import devis_enrichissement
from donjon.rendu import regarder
from tests import test_contreparties
from tests.test_tensions import recharger


class ValeurBiensTests(unittest.TestCase):
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
        self.assertEqual(valeur_bien(m, 'lucien', 'crochets_lucien'), 0)
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
        from donjon.moteur import Moteur, proposition
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
        self.assertTrue(any(s['type'] == 'proposition' and s['issue'] == 'accepte'
                            for s in lire(m, 'lucien')['memoire']))
        entier, decoupe = recharger(m), recharger(m)
        from donjon.pnj import avancer
        with patch.object(Monde, 'd20', return_value=20):
            avancer(entier, 2, [])
            for _ in range(2):
                avancer(decoupe, 1, [])
                decoupe = recharger(decoupe)
        entier = recharger(entier)
        for k in ('crochets_lucien', 'ballot'):
            self.assertEqual(entier.objets[k], decoupe.objets[k])
        self.assertEqual(entier.data['finances_pnj'], decoupe.data['finances_pnj'])
        for monde in (entier, decoupe):
            self.assertEqual(recharger(monde).data, monde.data)
            self.assertEqual(regarder(recharger(monde)), regarder(monde))

    def test_gaspard_marche_reel_refus_puis_doublon_ou_desespoir(self):
        from donjon.mine import nouveau_mine
        from donjon.monde import Monde
        from donjon import relations
        from donjon.spatial import installer
        from tests.support import presentes, calme, regarder as orienter
        from tests.test_tensions import placer
        for variante in ('seul', 'doublon', 'desespoir'):
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

    def test_convoitise_bien_sans_pieces_et_pas_de_confusion_projet_monetaire(self):
        m = self.scene()
        m.objets['ballot'].update(lieu='salle_commune', prix=200)
        croire(m, 'lucien', 'ballot', 'lieu', 'salle_commune', 'savoir', salle='salle_commune', case=[3, 3])
        m = recharger(m)
        devis = devis_enrichissement(m, 'lucien')
        self.assertIsNotNone(devis)
        self.assertEqual(devis[1]['objet'], 'ballot')
        self.assertNotIn('pieces', m.objets['ballot'])
        self.assertFalse(any(e['cible'] == 'ballot' for e in
            (devis_enrichissement(m, 'lucien', pieces_seules=True) or (0, {}, []))[2]))
        self.assertEqual(regarder(recharger(m)), regarder(m))

    def test_pret_non_monetaire_ne_devient_pas_un_enrichissement(self):
        m = self.scene()
        m.objets['ballot']['prix'] = 200
        m.objets['lucien']['profil']['valeurs']['honnetete'] = 100
        # Les autres acquisitions monétaires sont retirées des connaissances
        # de cette scène ; seule demeure la tentation d'un prêt du ballot.
        for d in lire(m, 'lucien')['croyances'].values():
            d.pop('pieces', None)
        m = recharger(m)
        self.assertIsNone(devis_enrichissement(m, 'lucien'))
        self.assertEqual(m.objets['ballot']['lieu'], 'anselme')
        self.assertEqual(regarder(recharger(m)), regarder(m))

    def test_prise_ne_deplace_pas_une_installation_meme_chere(self):
        from donjon.banc_pnj import creer
        from donjon.planification import chercher
        m = creer('relais', depart='fixe')
        o = m.objets['echelle_relais']
        o['installation'] = {'support': 'appui_clocher'}
        o['prix'] = 200
        o['lieu'] = m.objets['appui_clocher']['appui_vertical']['bas']
        croire(m, 'marchand', 'echelle_relais', 'lieu', o['lieu'], 'savoir', salle=o['lieu'], case=o['position'])
        m = recharger(m)
        avant = copy.deepcopy(m.objets['echelle_relais'])
        devis = chercher(m, 'marchand', lambda v, e: 'echelle_relais' in e.portes,
                         {'prendre': ('echelle_relais',)}, nom='installation-transport')
        self.assertIsNone(devis)
        recharge = recharger(m)
        self.assertEqual(recharge.objets['echelle_relais'], avant)
        self.assertEqual(regarder(recharge), regarder(m))


if __name__ == '__main__':
    unittest.main()
