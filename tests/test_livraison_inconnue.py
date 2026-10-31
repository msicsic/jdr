"""La remise garde sa charge pendant le contact, sans lieu réel ni délai de reprise."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, echanges, planification as p, pnj
from donjon.esprits import croire, lire
from donjon.geometrie import cases
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_empathie import executer, scene
from tests.test_tensions import placer, recharger


def relais():
    # Relais 7, instant 856, avant echoir : reprise du premier défaut du 308.
    fichier = Path(__file__).parent / 'captures/livraison-312-relais-7.json.gz'
    return Monde(json.loads(gzip.decompress(fichier.read_bytes()))), 'marchand', 'aubin', 'vivres_1'


def mine():
    m, a, b = scene()
    c = {'objet': 'vivres', 'remettre': b}
    agendas.prendre(m, a, {'condition': c, 'pour': b, 'minute': 0})
    d.choisir(m, a, 0)
    placer(m, b, 'galerie', [2, 2])
    croire(m, a, b, 'lieu', None, 'vu', salle=None, case=None)
    return m, a, b, 'vivres'


class LivraisonInconnueTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def chaine(self, fabrique):
        m, a, b, objet = fabrique()
        m = self.recharge(m)
        c = {'objet': objet, 'remettre': b}
        initial = copy.deepcopy(lire(m, a)['intention'])
        self.assertEqual(initial['but'], {'type': 'pulsion', **c})
        self.assertIsNone(d.salle_crue(m, a, b))
        engagement = next(x for x in agendas.en_cours(m, a) if x['condition'] == c)
        self.assertFalse(echanges.empeche(m, a, engagement))
        agendas.echoir(m, a)
        self.assertIn(engagement, agendas.en_cours(m, a))
        self.assertNotIn('annule', engagement)
        d.choisir(m, a, m.data['minutes'])
        i = lire(m, a)['intention']
        self.assertEqual(i['but'], initial['but'])
        self.assertEqual(i['depuis'], initial['depuis'])
        self.assertEqual(i.get('charges_suspendues'), initial.get('charges_suspendues'))
        self.assertFalse(any(g['operation'] == 'remettre' for g in i['plan']))
        self.assertTrue(any(g.get('contenu', {}).get('localisation') == b
                            or g.get('contenu', {}).get('cherche') == b for g in i['plan']))
        depart = self.recharge(m)
        gestes = []
        original = pnj._executer

        def observer(m, qui, g, *args, **kwargs):
            connu = d.salle_crue(m, qui, b)
            resultat = original(m, qui, g, *args, **kwargs)
            if qui == a:
                gestes.append((copy.deepcopy(g), resultat, connu))
            return resultat

        bloc = self.recharge(depart)
        with patch.object(pnj, '_executer', observer):
            lignes = executer(bloc, 8)
        remises = [(g, r, s) for g, r, s in gestes
                   if g['operation'] == 'remettre' and g['outil'] == objet]
        self.assertTrue(remises)
        self.assertTrue(all(r and s is not None for _, r, s in remises))
        self.assertEqual(bloc.objets[objet]['lieu'], b)
        self.assertFalse(any(x['condition'] == c for x in agendas.en_cours(bloc, a)))
        self.assertTrue(any(x['type'] == 'engagement_tenu' and x['condition'] == c
                            for x in lire(bloc, a)['memoire']))
        self.assertFalse(any(x['type'] == 'engagement_abandonne' and x['condition'] == c
                             for x in lire(bloc, a)['memoire']))
        self.assertTrue(any(x['pnj'] == a and 'remet ' in x['texte']
                            for x in bloc.data['chronique']))
        morceaux = self.recharge(depart)
        textes = []
        for _ in range(8):
            textes.extend(executer(morceaux, 1))
            morceaux = self.recharge(morceaux)
        self.assertEqual(bloc.data, morceaux.data)
        self.assertEqual(lignes, textes)
        self.recharge(bloc)

    def test_capture_relais_7_gorm_aubin(self):
        self.chaine(relais)

    def test_mine_mathe_lucien(self):
        self.chaine(mine)

    def test_devis_plan_et_empeche_purs_independants_du_lieu_cache(self):
        for fabrique in (relais, mine):
            m, a, b, objet = fabrique()
            c = {'objet': objet, 'remettre': b}
            e = next(x for x in agendas.en_cours(m, a) if x['condition'] == c)
            avant = copy.deepcopy(m.data)
            devis = p.devis_pulsion(m, a, c, b)
            self.assertIsNotNone(devis)
            self.assertEqual(p.planifier_tache(m, a, c, b)[1], devis[1])
            self.assertEqual(echanges.devis_service(m, a, c, b), devis)
            self.assertFalse(echanges.empeche(m, a, e))
            self.assertEqual(m.data, avant)
            for salle in m.data['salles']:
                n = Monde(copy.deepcopy(avant))
                # Placement d'auteur sur le sol déclaré, même dans une salle
                # dont le plan n'inclut pas (1, 1). Aucun savoir n'est rafraîchi.
                placer(n, b, salle, min(cases(n.data['salles'][salle])))
                n = self.recharge(n)
                avant_devis = copy.deepcopy(n.data)
                self.assertEqual(p.devis_pulsion(n, a, c, b), devis)
                self.assertFalse(echanges.empeche(n, a, e))
                self.assertEqual(n.data, avant_devis)

    def test_depart_cru_annule_encore_meme_si_le_destinataire_est_reellement_present(self):
        for fabrique in (relais, mine):
            for localise in (False, True):
                with self.subTest(source=fabrique.__name__, localise=localise):
                    m, a, b, objet = fabrique()
                    c = {'objet': objet, 'remettre': b}
                    if localise:
                        croire(m, a, b, 'lieu', m.objets[a]['lieu'], 'vu',
                               salle=m.objets[a]['lieu'], case=None)
                    croire(m, a, b, 'etat', {'parti': True}, 'vu')
                    m = self.recharge(m)
                    e = next(x for x in agendas.en_cours(m, a) if x['condition'] == c)
                    self.assertIsNone(p.planifier_tache(m, a, c, b))
                    self.assertIsNone(p.rejoindre(m, a, b))
                    self.assertTrue(echanges.empeche(m, a, e))
                    agendas.echoir(m, a)
                    self.assertTrue(any(x['type'] == 'engagement_abandonne' and x['condition'] == c
                                        for x in lire(m, a)['memoire']))
                    self.recharge(m)

    def test_acquisition_avant_contact_et_bien_cru_perdu(self):
        m, a, b, objet = mine()
        c = {'objet': objet, 'remettre': b}
        placer(m, objet, m.objets[a]['lieu'], [3, 3])
        croire(m, a, objet, 'lieu', m.objets[a]['lieu'], 'vu',
               salle=m.objets[a]['lieu'], case=[3, 3])
        plan = p.planifier_tache(self.recharge(m), a, c, b)
        self.assertIsNotNone(plan)
        self.assertEqual(plan[1][0]['operation'], 'prendre')
        self.assertFalse(any(g['operation'] == 'remettre' for g in plan[1]))
        croire(m, a, objet, 'lieu', None, 'vu', salle=None, case=None)
        croire(m, a, objet, 'fin', 'detruit', 'vu')
        m = self.recharge(m)
        self.assertIsNone(p.planifier_tache(m, a, c, b))
        e = next(x for x in agendas.en_cours(m, a) if x['condition'] == c)
        self.assertTrue(echanges.empeche(m, a, e))

    def test_aucun_moyen_admissible_le_temps_ne_rouvre_pas_la_recherche(self):
        m, a, b, objet = mine()
        c = {'objet': objet, 'remettre': b}
        for qui in p.vue(m, a).personnes():
            croire(m, a, qui, 'lieu', None, 'vu', salle=None, case=None)
        for salle in p.vue(m, a).salles:
            d.recherche_vaine(m, a, b, salle)
        m = self.recharge(m)
        e = next(x for x in agendas.en_cours(m, a) if x['condition'] == c)
        for minutes in (0, 10, 100):
            m.data['minutes'] = minutes
            self.assertIsNone(p.planifier_tache(m, a, c, b))
            self.assertTrue(echanges.empeche(m, a, e))
            self.recharge(m)
        agendas.echoir(m, a)
        self.assertTrue(any(x['type'] == 'engagement_abandonne' and x['condition'] == c
                            for x in lire(m, a)['memoire']))
        self.recharge(m)


if __name__ == '__main__':
    unittest.main()
