"""Les niveaux revus ne rajeunissent pas une ancienne mesure de vitesse."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon import eau, planification, pnj
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.rendu import regarder
from tests.test_social import recharger
from tools.diagnostic_refuge_mouille import vivre, recharger as reprise


def scene(graine):
    minute = 368 if graine == 2024 else 247
    chemin = Path(__file__).parent / f'data/scenes/eau-plan-marche-crue{graine}-{minute}.json.gz'
    return recharger(Monde(json.loads(gzip.decompress(chemin.read_bytes()))))


class EauPlanMarcheTests(unittest.TestCase):
    def test_un_premier_repere_ne_date_pas_une_ancienne_pente(self):
        m = scene(2024)
        for c in lire(m, 'marchand')['croyances'].values():
            c.pop('eau', None)
        # Ancienne sauvegarde : le sol sec a effacé le repère, mais gardé
        # la pente d'avant. Revoir de l'eau ne l'a pas encore remesurée.
        lire(m, 'marchand')['croyances'].setdefault('beffroi', {})['eau'] = {
            'valeur': 0, 'minute': 360, 'source': 'vu', 'confiance': 1.0,
            'niveau': None, 'repere': None, 'montee': 24}
        eau.observer(m, 'marchand', 'beffroi')
        m = recharger(m)
        self.assertIsNone(eau.estimation(m, 'marchand'))
        self.assertIsNone(lire(m, 'marchand')['croyances']['beffroi']['eau']['montee'])
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_le_niveau_revu_garde_la_derniere_vitesse_mesuree(self):
        m = scene(2024)
        qui = 'marchand'
        # La capture contient deux pentes opposées mesurées à 354. L'ancienne
        # lecture choisissait -8 depuis la galerie, puis +8 depuis les vannes.
        pente = eau.estimation(m, qui)[2]
        self.assertGreater(pente, 0)
        v = planification.Vue(m, qui)
        e = planification.depart(m, qui, v)
        self.assertIsNone(v.route(e, 'echoppe'))
        entrees = planification._entrees(v, {}, 8, 4000)
        for salle in ('crypte', 'beffroi', 'crypte', 'beffroi'):
            eau.observer(m, qui, salle)
            m = recharger(m)
            self.assertEqual(eau.estimation(m, qui)[2], pente)
            v = planification.Vue(m, qui)
            self.assertIsNone(v.route(planification.depart(m, qui, v), 'echoppe'))
        # Un nouveau repère, en revanche, peut établir la baisse : aucun
        # interdit permanent ne remplace la connaissance de l'eau.
        m.data['minutes'] += eau.REPERE
        eau.observer(m, qui, 'beffroi')
        m = recharger(m)
        v = planification.Vue(m, qui)
        self.assertLess(eau.estimation(m, qui)[2], 0)
        self.assertIsNotNone(v.route(planification.depart(m, qui, v), 'echoppe'))
        self.assertNotEqual(entrees, planification._entrees(v, {}, 8, 4000))

    @patch("donjon.agendas._naissances", return_value=None)
    def test_captures_reelles_sans_la_boucle_meme_monde_et_rendu_decoupes(self, _naissance):
        # Rejouer l'oracle observation/prévision/marche sans nouveaux marchés.
        for graine, qui, maximum in ((2024, 'marchand', 2), (1985, 'ilse', 1)):
            with self.subTest(graine=graine), tempfile.TemporaryDirectory() as dossier:
                m = scene(graine)
                debut = m.data['minutes'] * 600 + m.data.get('dixiemes', 0)
                bloc = vivre(reprise(m, dossier), 20, dossier)
                coupe = reprise(m, dossier)
                for _ in range(20):
                    coupe = vivre(coupe, 1, dossier)
                self.assertEqual(bloc.data, coupe.data)
                self.assertEqual(regarder(bloc), regarder(coupe))
                # Où il finit dépend aussi des autres mécaniques (offres, constats partagés) :
                # seule l'absence de boucle entre la recherche et la marche est vérifiée ici.
                gestes = [c for c in bloc.data['chronique'] if c['pnj'] == qui and c['instant'] >= debut]
                refus = [c for c in gestes if 'reste dans :' in c['texte']]
                # Ancienne lecture : 9 refus / 44 passages pour Gorm,
                # 5 refus / 40 passages pour Ilse sur ces captures.
                self.assertLessEqual(len(refus), maximum)
                # Sortir d'un séjour humide ajoute désormais des passages
                # légitimes (après inspection ou livraison). Leur nombre
                # brut ne mesure pas une boucle de refus plan/marche.
                self.assertEqual(eau.profondeur(bloc, bloc.objets[qui]['lieu']), 0)

    def test_eau_decouverte_au_seuil_retenue_et_route_refusee_apres_reprise(self):
        from tests.test_social import placer
        from donjon.geometrie import position_entree
        for qui in ('marchand', 'ilse'):
            with self.subTest(qui=qui):
                m = scene(2024)
                # Une hauteur inconnue derrière une porte ; l'essai constate
                # la noyade, même sans attendre la perception de fin du pas.
                m.data['crue']['depart_cm'] = 0
                m.data['crue']['tirage']['hauteur_pic_cm'] = 100
                m.data['crue']['tirage']['minute_pic'] = 1000
                placer(m, qui, 'crypte', position_entree(m, 'crypte', 'echoppe'))
                for c in lire(m, qui)['croyances'].values():
                    c.pop('eau', None)
                v = planification.Vue(m, qui)
                self.assertIsNotNone(v.route(planification.depart(m, qui, v), 'echoppe'))
                avant = m.objets[qui]['lieu']
                self.assertIsNotNone(pnj._marcher(m, qui, lambda s, c: s == 'echoppe', []))
                m = recharger(m)
                c = lire(m, qui)['croyances']['echoppe']['eau']
                self.assertEqual((c['source'], c['minute']), ('essai', m.data['minutes']))
                self.assertGreaterEqual(c['valeur'], eau.NOYEE_CM)
                self.assertEqual(m.objets[qui]['lieu'], avant)
                v = planification.Vue(m, qui)
                self.assertIsNone(v.route(planification.depart(m, qui, v), 'echoppe'))
                self.assertEqual(regarder(m), regarder(recharger(m)))
