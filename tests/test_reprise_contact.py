"""Une interruption sans nouvelle entrée n'est pas une échéance de réessai."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, planification as p, pnj
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.positions_crues import contact_interrompu_tient
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import instant
from tests.test_empathie import scene
from tests.test_marche import intention
from tests.test_tensions import placer, recharger, vivre
from tests.test_contact_position_inconnue import source_ailleurs


def capture():
    fichier = Path(__file__).parent / 'captures/contact-313-relais-1985-235.json.gz'
    return Monde(json.loads(gzip.decompress(fichier.read_bytes())))


class RepriseContactTests(unittest.TestCase):
    def recharge(self, m):
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_percue(m), scene_percue(r))
        return r

    def test_ilse_capture_141000_pas_de_reprise_par_la_minute(self):
        depart = self.recharge(capture())
        self.assertEqual(instant(depart), 141000)
        essais = []
        original = pnj._approcher

        def observer(m, qui, etape, *args, **kwargs):
            if qui == 'ilse':
                # La revalidation commune doit arrêter toute reprise dont le
                # contact interrompu n'a reçu aucune entrée positive nouvelle.
                self.assertIsNone(pnj.refus_etape(m, qui, [etape]))
            r = original(m, qui, etape, *args, **kwargs)
            if qui == 'ilse' and r is None:
                essais.append(instant(m))
            return r

        with patch.object(pnj, '_approcher', observer):
            bloc, texte = vivre(self.recharge(depart), 5)
        self.assertTrue(essais)
        self.assertFalse({142200, 142800, 143400} & set(essais), essais)
        self.assertTrue(any(c['pnj'] == 'marchand' and 'donne une part' in c['texte']
                            for c in bloc.data['chronique']))
        morceaux = self.recharge(depart)
        decoupe = []
        for _ in range(5):
            morceaux, lignes = vivre(morceaux, 1)
            decoupe.extend(lignes)
        self.assertEqual(bloc.data, morceaux.data)
        self.assertEqual(texte, decoupe)
        self.recharge(bloc)

    def test_autre_contact_retenu_recharge_puis_nouvelle_localisation(self):
        m, a, b = scene()
        m.objets[a]['profil']['valeurs'].update(altruisme=0, empathie=0)
        placer(m, b, 'galerie', [11, 1])
        croire(m, a, b, 'lieu', None, 'vu', salle=None, case=None)
        g = p._etape('demander', b, outil='vivres')
        intention(m, a, [g], but={'type': 'rejoindre', 'lieu': 'baraquement'})
        depart = self.recharge(m)
        tentatives = []
        original = pnj._approcher

        def observer(m, qui, etape, *args, **kwargs):
            if qui == a and etape['cible'] == b:
                tentatives.append(instant(m))
            return original(m, qui, etape, *args, **kwargs)

        with patch.object(pnj, '_approcher', observer):
            fin, _ = vivre(self.recharge(depart), 3)
        self.assertEqual(len(tentatives), 1, tentatives)
        retenus = [r for rs in lire(fin, a)['renoncements'].values() for r in rs
                   if r['cause']['type'] == 'contact']
        self.assertTrue(retenus)
        cause = copy.deepcopy(retenus[0]['cause'])
        self.assertTrue(contact_interrompu_tient(fin, a, cause))
        self.assertEqual(pnj.refus_etape(fin, a, [g]), 'contact interrompu sans entrée nouvelle')
        self.recharge(fin)
        morceaux = self.recharge(depart)
        for _ in range(3):
            morceaux, _ = vivre(morceaux, 1)
        self.assertEqual(fin.data, morceaux.data)
        # Une nouvelle date du même lieu inconnu ne constitue pas un indice.
        croire(fin, a, b, 'lieu', None, 'vu', salle=None, case=None)
        self.assertTrue(contact_interrompu_tient(fin, a, cause))
        # L'observateur reçoit cette fois une localisation positive.
        placer(fin, b, 'baraquement', [6, 3])
        croire(fin, a, b, 'lieu', 'baraquement', 'vu', salle='baraquement', case=[6, 3])
        self.assertFalse(contact_interrompu_tient(fin, a, cause))
        self.assertIsNone(pnj.refus_etape(fin, a, [g]))
        intention(fin, a, [g], but={'type': 'rejoindre', 'lieu': 'baraquement'})
        fin, _ = vivre(self.recharge(fin), 2)
        self.assertTrue(any(c['pnj'] == a and 'demande' in c['texte'] for c in fin.data['chronique']))
        self.recharge(fin)

    def test_source_non_localisee_garde_la_charge_et_sa_presence_crue(self):
        m = source_ailleurs()
        a, b = 'mathe', 'lucien'
        for o in m.objets.values():
            if 'allume' in o:
                o['allume'] = False
        m.objets['coffre_contact']['mobile'] = True
        placer(m, a, 'galerie', [5, 1])
        croire(m, a, 'coffre_contact', 'lieu', 'galerie', 'vu', salle='galerie', case=None)
        croire(m, a, 'galerie', 'etat', {'niveau': 0, 'propre': 0, 'eclairee': False}, 'vu')
        condition = {'objet': 'vivres', 'servir': b}
        agendas.prendre(m, a, {'condition': condition, 'objet': 'vivres', 'pour': b, 'minute': 0})
        g = p._etape('servir', 'vivres', contenu={'pour': b})
        intention(m, a, [g], but={'type': 'pulsion', **condition}, motif='engagement')
        depart = self.recharge(m)
        fin, _ = vivre(self.recharge(depart), 3)
        self.assertTrue(any(x['condition'] == condition and not x.get('annule')
                            for x in agendas.en_cours(fin, a)))
        self.assertEqual(lire(fin, a)['croyances']['vivres']['lieu']['valeur'], 'coffre_contact')
        self.assertEqual(fin.objets['vivres']['portions'], depart.objets['vivres']['portions'])
        self.assertTrue(any(r['cause']['type'] == 'contact'
                            for rs in lire(fin, a)['renoncements'].values() for r in rs))
        self.recharge(fin)
        morceaux = self.recharge(depart)
        for _ in range(3):
            morceaux, _ = vivre(morceaux, 1)
        self.assertEqual(fin.data, morceaux.data)


if __name__ == '__main__':
    unittest.main()
