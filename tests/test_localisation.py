import copy
import unittest
from unittest.mock import patch

from donjon.defi import nouveau_defi, BEFFROI
from donjon.mj import MJOpenAI
from donjon.monde import nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.spatial import installer


class LocalisationTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_defi()
        installer(self.m)

    def objets(self):
        return {o['id']: o for o in self.m.contexte()['objets_perceptibles']}

    def test_obstacle_visible_au_nord_dans_la_conduite(self):
        self.m.joueur.update(salle='echoppe', position=[5, 4])
        avant = copy.deepcopy(self.m.data)
        c = self.m.contexte()
        self.assertEqual(c['salle']['id'], c['joueur']['salle'])
        self.assertEqual(c['lieux_connus']['echoppe'], 'Conduite basse')
        self.assertEqual(c['joueur']['salle_nom'], 'Conduite basse')
        poutre = self.objets()['poutre_conduite']
        self.assertTrue(poutre['visible'] and poutre['a_portee'] and poutre['bloque_passage'])
        self.assertEqual(poutre['localisation']['salle_nom'], 'Conduite basse')
        self.assertTrue(poutre['localisation']['meme_salle'])
        self.assertEqual(poutre['localisation']['position_relative'], '1 case vers nord')
        self.assertNotIn('colonne_vannes', self.objets())
        self.assertEqual(self.m.data, avant)

    def test_prise_a_portee_apres_rapprochement_et_historique_errone(self):
        self.m.joueur.update(salle='echoppe', position=[5, 4])
        self.m.memoriser('je prend le pied de biche', "Il est dans l'échoppe, tu es dans la Conduite basse.")
        self.assertFalse(self.objets()['pied_de_biche']['a_portee'])
        moteur = Moteur(self.m)
        for direction in ('sud', 'est'):
            moteur.executer(moteur.preparer(proposition('marcher', direction)))
        o = self.objets()['pied_de_biche']
        self.assertTrue(o['a_portee'])
        self.assertEqual(o['localisation']['salle_nom'], 'Conduite basse')
        self.assertEqual(o['localisation']['position_relative'], '1 case vers est')
        moteur.executer(moteur.preparer(proposition('prendre', 'pied_de_biche')))
        self.assertEqual(self.objets()['pied_de_biche']['localisation']['position_relative'], 'dans tes affaires')

    def test_vue_transmise_au_llm_contient_les_reperes_actuels(self):
        self.m.joueur.update(salle='echoppe', position=[6, 5])
        self.m.memoriser('je prend le pied de biche', "Retourne à l'échoppe.")
        reponse = {'mode': 'action', 'texte': '', 'faits': ['objet:pied_de_biche'],
                   'proposition': proposition('prendre', 'pied_de_biche')}
        mj = MJOpenAI()
        with patch.object(mj, '_appeler', return_value=reponse) as appel:
            resultat = mj._echanger(self.m, 'je prend le pied de biche', None, True)
        instructions, entree, *_ = appel.call_args.args
        faits = entree['faits']
        self.assertEqual(faits['salle']['id'], 'echoppe')
        self.assertEqual(faits['salle']['nom'], 'Conduite basse')
        self.assertEqual(faits['joueur']['salle'], 'Conduite basse')
        self.assertNotIn('position', faits['joueur'])
        self.assertNotIn('lieux_connus', faits)
        self.assertEqual(entree['conversation'], [])
        self.assertIn({'nom': 'la consigne émaillée', 'derniere_salle': 'Refuge du relais'},
                      faits['souvenirs_visuels'])
        self.assertTrue(faits['objet:pied_de_biche']['a_portee'])
        self.assertTrue(faits['objet:pied_de_biche']['localisation']['meme_salle'])
        for champ in ('lieu', 'position', 'position_salle', 'case_percue'):
            self.assertNotIn(champ, faits['objet:pied_de_biche'])
        self.assertNotIn('salle_id', faits['objet:pied_de_biche']['localisation'])
        self.assertIn('clés opaques', instructions)
        self.assertIn("L'état actuel prime", instructions)
        Moteur(self.m).preparer(resultat['proposition'])

    def test_voisin_visible_a_travers_sortie_sans_reveler_nom_inconnu(self):
        self.m = nouveau_monde()
        self.m.data['visitees'] = ['antichambre']
        installer(self.m)
        self.m.joueur.update(position=[0, 1], orientation='ouest')  # Il regarde par la sortie.
        self.m.objets['marteau'].update(position=[4, 3], position_salle='echoppe')
        o = self.objets()['marteau']
        self.assertFalse(o['a_portee'])
        self.assertFalse(o['localisation']['meme_salle'])
        self.assertEqual(o['localisation']['direction'], 'ouest')
        self.assertEqual(o['localisation']['position_relative'], '2 cases vers ouest')
        self.assertNotIn('echoppe', self.m.contexte()['lieux_connus'])
        self.assertEqual(self.m.contexte()['salle']['sorties']['ouest']['nom_destination'], 'inexploré')
        self.m.data['visitees'].append('echoppe')
        self.assertEqual(self.objets()['marteau']['localisation']['salle_nom'], self.m.data['salles']['echoppe']['nom'])

    def test_vue_mj_garde_le_support_des_composants(self):
        m = nouveau_monde()
        installer(m)
        mj = MJOpenAI()
        reponse = {'mode': 'dialogue', 'texte': 'La gravure est sur la porte.',
                   'faits': ['objet:gravure'], 'proposition': None}
        with patch.object(mj, '_appeler', return_value=reponse) as appel:
            mj._echanger(m, 'Que vois-je sur la porte ?', None, True)
        gravure = appel.call_args.args[1]['faits']['objet:gravure']
        self.assertEqual(gravure['rattache_a'], {'id': 'porte', 'nom': m.objets['porte']['nom']})
        self.assertNotIn('lieu', gravure)

    def test_echelle_depuis_sommet_a_bonne_localisation(self):
        self.m.joueur['position'] = [7, 4]
        moteur = Moteur(self.m)
        moteur.executer(moteur.preparer(proposition('installer', 'echelle_relais', 'appui_clocher')))
        self.m.joueur.update(salle=BEFFROI, position=[0, 3])
        o = self.objets()['echelle_relais']
        self.assertEqual(o['lieu'], 'antichambre')  # pied de l'installation
        self.assertEqual(o['localisation']['salle_id'], BEFFROI)  # extrémité accessible ici
        self.assertTrue(o['localisation']['meme_salle'] and o['a_portee'])
        self.assertEqual(o['localisation']['position_relative'], 'sur ta case')


if __name__ == '__main__':
    unittest.main()
