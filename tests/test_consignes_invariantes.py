"""L3 : même contrat d'interprétation, quel que soit le dossier ou le refus."""
import unittest

from donjon.atelier import nouveau_atelier
from donjon.rendu import regarder
from donjon.spatial import installer
from tests import test_cache_kv_local as prefixe
from tests.test_dossiers_proches import console
from tests.test_sous_obstacle import scene, passage
from tests.test_tensions import recharger


class ConsignesInvariantesTests(unittest.TestCase):
    def test_regles_mutualisees_presentes_une_seule_fois(self):
        instructions, _, _, _ = prefixe.PrefixeKVTests()._capter_appel(scene(), 'Explique.')
        # Inventaire des contrats déplacés ou dédoublonnés : une occurrence dans
        # le texte réellement assemblé, pas seulement dans chaque constante.
        for regle in (
            'Une saisie qui commence par des guillemets',
            'Une interpellation sans guillemets',
            'pieces:{montants:',
            'largeur_cm 25 à 60',
            'un lot se prélève d’abord',
            'Sans urgence ni préférence du joueur',
            'sauf demande contraire',
            'Le moteur calcule barreaux',
            'operation passer_obstacle',
            'la cible est loin ou seulement en souvenir',
            'Une question sur la faisabilité d’un geste de Corvus',
        ):
            with self.subTest(regle=regle):
                normalise = instructions.replace("'", '’')
                self.assertEqual(normalise.count(regle.replace("'", '’')), 1)

    def test_scenes_console_proches_eloignees_et_recharge(self):
        consignes = []
        for type_scene in ('relais', 'atelier'):
            for proche in (True, False):
                m = scene() if type_scene == 'relais' else nouveau_atelier()
                installer(m)
                if type_scene == 'relais':
                    x, y = m.objets['poutre_conduite']['position']
                    m.joueur['position'] = [x - (1 if proche else 2), y]
                    p = passage('poutre_conduite')
                else:
                    m.joueur.update(position=[2, 2 if proche else 3], orientation='nord')
                    p = {'action': 'decouper', 'cible': 'perche_2', 'outil': 'hache',
                         'longueur_cm': 100, 'justification': 'Prélever un morceau.'}
                m = recharger(m)
                requetes = []
                resultat, rendu, _ = console(m, p, requetes=requetes)
                consignes.extend(i for i, _ in requetes)
                self.assertEqual(resultat.joueur['position'], m.joueur['position'])
                if type_scene == 'atelier':
                    self.assertEqual(resultat.objets['perche_2']['longueur_cm'], 300)
                self.assertIn(('Ramper sous' if type_scene == 'relais' else 'Couper la perche')
                              if proche else 'Approche-toi', rendu)
                self.assertEqual(recharger(resultat).data, resultat.data)
                self.assertEqual(regarder(recharger(resultat)), regarder(resultat))
        self.assertEqual(len(consignes), 4)
        self.assertEqual(len(set(consignes)), 1)

    def test_retour_et_refus_dans_entree_sur_toutes_les_voies(self):
        capter = prefixe.PrefixeKVTests()._capter_appel
        m = scene()
        for enrichir in (True, False):
            i, entree, _, _ = capter(m, 'Explique.', enrichir=enrichir)
            j, retour, _, _ = capter(m, 'Explique.', enrichir=enrichir,
                                    retour_moteur={'obstacle': 'refus', 'attendu': 'champ=cible'})
            self.assertEqual(i, j)
            self.assertNotIn('consigne_retour_moteur', entree)
            self.assertIn('consigne_retour_moteur', retour)
            self.assertEqual(retour['faits']['retour_moteur']['attendu'], 'champ=cible')
