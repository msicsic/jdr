"""Recours sur place : captures, monde et rendu, recharge et découpage du même laps."""
import gzip
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon import deliberation as d, planification as p
from donjon.banc_pnj import creer
from donjon.esprits import lire, croire, percevoir_tous
from donjon.monde import Monde
from tests.support import calme, lier
from tests.test_tensions import placer, recharger, vivre


def capture():
    with tempfile.TemporaryDirectory() as dossier:
        chemin = Path(dossier) / 'partie.json'
        chemin.write_bytes(gzip.decompress((Path(__file__).parent / 'data/mine_42_minute_470.json.gz').read_bytes()))
        return Monde.charger(chemin)


class GardienDetresseTests(unittest.TestCase):
    def meme_laps(self, monde, duree):
        bloc, texte = vivre(recharger(monde), duree, jet=20)
        pas, lignes = recharger(monde), []
        for _ in range(duree):
            pas, lu = vivre(pas, 1, jet=20)
            lignes.extend(lu)
        self.assertEqual(bloc.data, pas.data)
        # Les aperçus intermédiaires sont échantillonnés par chaque saisie. Les actes
        # entendus et le rendu final, eux, doivent survivre au même laps et à la recharge.
        def actes(lus):
            return [t for t in lus if any(mot in t for mot in ("appelle", "demande", "allume", "apporte", "accepte", "refuse"))]
        self.assertEqual(actes(texte), actes(lignes))
        from donjon.rendu import decrire_contexte
        self.assertEqual(decrire_contexte(recharger(bloc)), decrire_contexte(recharger(pas)))
        bloc.verifier()
        from donjon.ecoute import entendus, rendre, ENTENDU
        # ``avancer`` produit les gestes vus ; l'ouïe est rendue par l'appelant du moteur.
        return recharger(bloc), '\n'.join(texte + rendre(bloc, entendus(bloc, monde.data['minutes'] * 600, ENTENDU)))

    def test_capture_reelle_appel_deja_lance_biscuits_epuises_et_pas_de_boucle(self):
        m = capture()
        self.assertEqual(lire(m, 'bram')['secours'], {'minute': 462, 'apaise': False})
        self.assertFalse(lire(m, 'bram')['croyances']['biscuits']['etat']['valeur']['disponible'])
        avant = len([c for c in m.data['chronique'] if c['pnj'] == 'bram' and "appelle à l'aide" in c['texte']])
        m, _ = self.meme_laps(m, 4)
        self.assertEqual(m.objets['bram']['lieu'], 'bureau')
        self.assertEqual(lire(m, 'bram')['secours']['minute'], 462)
        self.assertGreater(avant, 0)
        self.assertEqual(avant, len([c for c in m.data['chronique'] if c['pnj'] == 'bram' and "appelle à l'aide" in c['texte']]))

    def lumiere(self):
        m = capture()
        calme(m, *[k for k, o in m.objets.items() if o.get('profil') and k != 'bram'])
        m.data['gestes_en_cours'] = []
        for k, o in m.objets.items():
            if o.get('profil'):
                lire(m, k).update(intention=None, veille=None)
        placer(m, 'josse', 'bureau', (3, 1))
        # L'aidant de cette scène ne cherche pas lui-même la lumière avant la demande.
        m.objets['josse']['profil'].setdefault('securite', {})['noir'] = 0
        m.objets['josse']['profil']['pulsions'] = []
        lire(m, 'josse')['pulsions'] = []
        m.objets['briquet'].update(lieu='josse')
        m.objets['chandelle'].update(allume=False, combustible=200)
        m.joueur.update(salle='bureau', position=[2, 1])
        lier(m, 'josse', 'bram', True, 'vu')
        percevoir_tous(m)
        croire(m, 'bram', 'josse', 'lieu', 'bureau', 'entendu', salle='bureau', case=[3, 1])
        croire(m, 'josse', 'chandelle', 'etat', {'allume': False, 'charge': True}, 'vu')
        return recharger(m)

    def test_bram_demande_une_source_allumee_sans_partir(self):
        m = self.lumiere()
        plan = d._plan_lumiere(m, 'bram')
        self.assertIsNotNone(plan)
        self.assertEqual(plan[1][0]['operation'], 'confier')
        self.assertFalse(any(x['operation'] == 'aller' for x in plan[1]))
        m, texte = self.meme_laps(m, 8)
        self.assertEqual(m.objets['bram']['lieu'], 'bureau')
        self.assertTrue(m.objets['chandelle']['allume'])
        self.assertIn('allume', texte)
        self.assertTrue(any(c['pnj'] == 'bram' and 'demande à Josse' in c['texte'] for c in m.data['chronique']))

    def test_demander_un_moyen_pour_un_autre_besoin(self):
        m = self.lumiere()
        m.objets['bram']['profil'].setdefault('securite', {})['noir'] = 0
        e = lire(m, 'bram')
        e['besoins'].update(securite=0., faim=100.)
        e['urgences']['faim'] = {'etat': 'attente', 'depuis': 470}
        m.objets['biscuits'].update(lieu='reserve', position=[2, 1], position_salle='reserve', portions=3)
        for qui in ('bram', 'josse'):
            croire(m, qui, 'biscuits', 'lieu', 'reserve', 'savoir', salle='reserve', case=[2, 1])
            croire(m, qui, 'biscuits', 'etat', {'disponible': True}, 'vu')
        plan = d._plan_faim(m, 'bram')
        self.assertEqual(plan[1][0]['operation'], 'confier')
        self.assertEqual(plan[1][0]['contenu'], {'objet': 'biscuits', 'remettre': 'bram'})
        m, texte = self.meme_laps(recharger(m), 8)
        self.assertEqual(m.objets['bram']['lieu'], 'bureau')
        self.assertLess(lire(m, 'bram')['besoins']['faim'], 100.)
        self.assertLess(m.objets['biscuits']['portions'], 3)
        self.assertTrue(any(c['pnj'] == 'bram' and 'demande à Josse' in c['texte'] for c in m.data['chronique']))

    def test_promesse_connue_cache_et_aucun_effet_avant_realisation(self):
        from donjon.echanges import executer
        m = self.lumiere()
        with patch.object(p, 'VERIFIER', True), patch.object(Monde, 'd20', return_value=20):
            plan = d._plan_lumiere(m, 'bram')
            self.assertTrue(executer(m, 'bram', plan[1][0], []))
            self.assertFalse(m.objets['chandelle']['allume'])
            m = recharger(m)
            self.assertEqual(d._plan_lumiere(m, 'bram')[1], [])
            # Sa mémoire ne lit pas l'abandon privé de l'autre, encore inannoncé.
            lire(m, 'josse')['engagements'].clear()
            m = recharger(m)
            self.assertEqual(d._plan_lumiere(m, 'bram')[1], [])

    def test_autre_besoin_autre_gardien_appel_sans_reponse_une_fois(self):
        m = creer('auberge', 42, 'fixe')
        calme(m, *[k for k, o in m.objets.items() if o.get('profil')])
        m.data['gestes_en_cours'] = []
        for k, o in m.objets.items():
            if o.get('profil'):
                lire(m, k).update(intention=None, veille=None)
        # Scène d'auteur : sa charge est au grenier ; aucun aliment disponible connu.
        placer(m, 'lucien', 'grenier', (2, 2))
        m.objets['lucien']['profil']['pulsions'] = [
            x for x in m.objets['lucien']['profil']['pulsions']
            if x['besoin'] == 'biens' and d.salle_crue(m, 'lucien', x['condition'].get('objet')) == 'grenier']
        lire(m, 'lucien')['pulsions'] = [True] * len(m.objets['lucien']['profil']['pulsions'])
        for k, o in m.objets.items():
            if o['type'] == 'nourriture':
                o['portions'] = 0
        e = lire(m, 'lucien')
        e['besoins'].update(faim=100., biens=100.)
        e['urgences']['faim'] = {'etat': 'attente', 'depuis': 0}
        m.joueur.update(salle='grenier', position=[3, 2])
        percevoir_tous(m)
        # Tous les vivres ont été vérifiés épuisés, aucune enquête ne peut le renseigner.
        for k, o in m.objets.items():
            if o['type'] == 'nourriture':
                croire(m, 'lucien', k, 'etat', {'disponible': False}, 'vu')
        for autre, o in m.objets.items():
            if autre != 'lucien' and o.get('profil'):
                d.retenir_refus(m, 'lucien', autre, 'enqueter', 'rien', besoin='faim')
        m, texte = self.meme_laps(recharger(m), 12)
        self.assertEqual(m.objets['lucien']['lieu'], 'grenier')
        self.assertIn('faim', lire(m, 'lucien')['detresses_appelees'])
        self.assertIn('aide', texte)
        self.assertEqual(sum(c['pnj'] == 'lucien' and 'appelle à l\'aide' in c['texte'] for c in m.data['chronique']), 1)


if __name__ == '__main__':
    unittest.main()
