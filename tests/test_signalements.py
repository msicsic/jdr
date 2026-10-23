"""Signalements : état, récit et perception après sauvegarde, sans appel au modèle."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as D
from donjon.banc_pnj import _oisifs_urgents
from donjon.ecoute import entendus, rendre, ENTENDU
from donjon.esprits import lire, memoriser, MEMOIRE_MAX
from donjon.monde import Monde
from donjon.recit_pnj import Recit
from donjon.temps import instant
from tests.test_tensions import recharger, relais, vivre
from tools.audit_nuits import _releve, analyser_nuit

DATA = Path(__file__).with_name('data')


def scene(nom):
    with gzip.open(DATA / ('signalements-' + nom + '.json.gz'), 'rt', encoding='utf-8') as f:
        return Monde(json.load(f))


def poursuivre(m, duree, pas):
    for _ in range(0, duree, pas):
        m, _ = vivre(m, pas)
    return m


def appels(m, qui):
    return [c for c in m.data['chronique'] if c['pnj'] == qui and c['texte'].endswith("appelle à l'aide.")]


class SecoursTests(unittest.TestCase):
    def test_relais_42_meme_desarroi_malgre_les_sorties_du_refuge(self):
        # Main 43fa7ac, minute 160, après le premier appel de Gorm à 154. Sans correction,
        # il appelle encore à 193 et 225 ; sa sécurité n'est jamais redescendue sous son seuil.
        m = scene('relais-42-160')
        debut = instant(m)
        nombre = len(appels(m, 'marchand'))
        bloc = poursuivre(recharger(m), 80, 80)
        coupe = poursuivre(recharger(m), 80, 5)
        self.assertEqual(bloc.data, coupe.data)
        self.assertEqual(len(appels(bloc, 'marchand')), nombre)
        # Avec les trajets réels, Gorm trouve désormais un abri et s'apaise.
        # Aucun appel supplémentaire n'a précédé cet apaisement.
        self.assertTrue(lire(bloc, 'marchand')['secours']['apaise'])
        self.assertNotIn('securite', D.urgents(bloc, 'marchand'))
        # Le rendu de l'ouïe ne peut afficher un nouvel appel absent du monde.
        nouveaux = [(b, n, v) for b, n, v in entendus(bloc, debut, ENTENDU)
                    if b['auteur'] == 'marchand' and b['nature'] == 'appel']
        self.assertEqual(rendre(recharger(bloc), nouveaux), [])

    def ilse(self):
        from tests.test_protection import seule_et_a_bout
        m = seule_et_a_bout(relais())
        m.objets['marchand']['profil']['protege'] = []
        m.objets['marchand']['profil']['pulsions'] = []
        lire(m, 'marchand')['pulsions'] = []
        m.joueur.update(salle='antichambre', position=[3, 4])
        return recharger(m)

    def test_sous_desespoir_ne_signifie_pas_rassuree(self):
        m = self.ilse()
        debut = instant(m)
        m, _ = vivre(m, 1)
        self.assertIn("appel à l'aide", '\n'.join(rendre(m, entendus(m, debut, ENTENDU))))
        lire(m, 'ilse')['besoins']['securite'] = 94.0
        m, _ = vivre(recharger(m), 1)
        self.assertIn('securite', D.urgents(m, 'ilse'))
        lire(m, 'ilse')['besoins']['securite'] = 99.0
        bloc = poursuivre(recharger(m), 15, 15)
        coupe = poursuivre(recharger(m), 15, 1)
        self.assertEqual(bloc.data, coupe.data)
        self.assertEqual(len(appels(bloc, 'ilse')), 1)
        debut = instant(bloc)
        # Un vrai apaisement, puis un nouveau désarroi, autorisent un nouvel appel audible.
        lire(bloc, 'ilse')['besoins']['securite'] = 0.0
        bloc, _ = vivre(recharger(bloc), 1)
        lire(bloc, 'ilse')['besoins']['securite'] = 99.0
        bloc, _ = vivre(recharger(bloc), 15)
        self.assertEqual(len(appels(bloc, 'ilse')), 2)
        self.assertIn("appel à l'aide", '\n'.join(rendre(bloc, entendus(bloc, debut, ENTENDU))))

    def test_le_recours_survit_a_la_memoire_bornee(self):
        m = self.ilse()
        m, _ = vivre(m, 1)
        for _ in range(MEMOIRE_MAX + 1):
            memoriser(m, 'ilse', {'type': 'observation'})
        self.assertFalse(any(s['type'] == 'appel' for s in lire(m, 'ilse')['memoire']))
        lire(m, 'ilse')['besoins']['securite'] = 99.0
        m = poursuivre(recharger(m), 15, 5)
        self.assertEqual(len(appels(m, 'ilse')), 1)
        self.assertFalse(lire(m, 'ilse')['secours']['apaise'])

    def test_migration_du_dernier_appel_des_anciennes_parties(self):
        m = scene('relais-42-160')
        data = copy.deepcopy(m.data)
        data['esprits']['marchand'].pop('secours')
        m = recharger(Monde(data))
        self.assertEqual(lire(m, 'marchand')['secours'], {'minute': 154, 'apaise': False})


class InactiviteTests(unittest.TestCase):
    def verifier_scene(self, nom, qui, cause, texte):
        m = scene(nom)
        avant = copy.deepcopy(m.data)
        self.assertEqual(D.inactivite(m, qui), cause)
        self.assertEqual(m.data, avant)  # Lire une cause ne fait ni rechercher ni agir.
        r = Recit(m)
        r._noter(m, qui, m.data['minutes'])
        self.assertIn(texte, '\n'.join(r.personnage(recharger(m), qui, m.data['chronique'])))
        bloc = poursuivre(recharger(m), 10, 10)
        coupe = poursuivre(recharger(m), 10, 1)
        self.assertEqual(bloc.data, coupe.data)
        self.assertEqual(D.inactivite(bloc, qui), cause)

    def test_mireille_auberge_11_travail_confie(self):
        self.verifier_scene('auberge-11-500', 'mireille', 'confiee', 'Charge confiée à autrui')

    def test_gorm_relais_1985_charge_confiee_au_joueur(self):
        self.verifier_scene('relais-1985-120', 'marchand', 'confiee', 'Charge confiée à autrui')

    def test_hugues_auberge_11_devoir_sans_tache_restante(self):
        self.verifier_scene('auberge-11-500', 'hugues', 'satisfaite', 'Charge déjà satisfaite')

    def test_attendre_un_moyen_reste_distinct_du_repit(self):
        from tests.support import calme
        m = calme(relais(), 'marchand', 'brune', 'ilse', 'aubin')
        # Aucun recours ne peut satisfaire une ronde de la crypte quand on n'en connaît
        # aucun passage. Fixture de même nature, sans personne ni ressource nommée par le moteur.
        p = m.objets['aubin']['profil']
        p['pulsions'] = []
        p['besoins']['devoir'] = {'depart': 100, 'derive_heure': 0, 'urgence': 60}
        lire(m, 'aubin')['besoins']['devoir'] = 100.0
        D.choisir(m, 'aubin', m.data['minutes'])
        m = recharger(m)
        self.assertEqual(D.inactivite(m, 'aubin'), 'attente')
        self.assertEqual(lire(m, 'aubin')['urgences']['devoir']['etat'], 'attente')
        self.assertEqual(_oisifs_urgents(m)[2], 1)


class RechercheTests(unittest.TestCase):
    def verifier_recherche(self, m, qui, minutes):
        from donjon import pnj
        debut = instant(m)
        cris = []
        derniers = {}
        heler = pnj.heler
        def observer(monde, id, cible, lignes):
            if id == qui:
                lieu = lire(monde, id)['croyances'].get(cible, {}).get('lieu') or {}
                t, salle, depuis = instant(monde), monde.objets[id]['lieu'], lieu.get('minute', -1)
                cris.append((t, cible, salle, depuis))
                avant = derniers.get((cible, salle))
                if avant is not None and t - avant < D.APPEL_OUBLI * 600:
                    self.assertGreater(depuis, avant // 600, cris)
                derniers[cible, salle] = t
            return heler(monde, id, cible, lignes)
        # Le journal du monde ne garde que 300 entrées ; observer la période entière évite
        # qu'une rafale d'échanges masque ses propres premiers appels.
        with patch.object(pnj, 'heler', observer):
            bloc = poursuivre(recharger(m), minutes, minutes)
        coupe = poursuivre(recharger(m), minutes, 5)
        self.assertEqual(bloc.data, coupe.data)
        self.assertTrue(cris)
        self.assertTrue(lire(bloc, qui).get('recherches'))
        # Une recherche infructueuse n'établit jamais la présence ni l'identité du répondant.
        for lieu in lire(bloc, qui)['recherches'].values():
            self.assertTrue(all(s in bloc.data['salles'] for s in lieu))
        self.assertEqual(rendre(recharger(bloc), entendus(bloc, debut, ENTENDU)),
                         rendre(recharger(coupe), entendus(coupe, debut, ENTENDU)))
        return bloc

    def test_auberge_3_un_rendez_vous_ne_relance_pas_la_tournee(self):
        self.verifier_recherche(scene('auberge-3-570'), 'anselme', 30)

    def test_relais_un_bien_porte_par_une_voix_non_identifiee(self):
        from tests.support import calme, lier
        from tests.test_tensions import placer
        from donjon.esprits import croire, percevoir_tous
        m = calme(relais(), 'marchand', 'brune', 'ilse', 'aubin')
        for o in m.objets.values():
            if 'allume' in o:
                o['allume'] = False
        placer(m, 'marchand', 'echoppe', (3, 3))
        placer(m, 'brune', 'antichambre', (3, 4))
        m.objets['marteau']['lieu'] = 'brune'
        m.objets['marchand']['profil']['pulsions'] = [
            {'besoin': 'biens', 'condition': {'objet': 'marteau', 'lieu': 'echoppe'}}]
        lire(m, 'marchand')['pulsions'] = []
        m.objets['marchand']['profil']['protege'] = []
        lier(m, 'marchand', 'brune', True)
        lier(m, 'brune', 'marchand', True)
        percevoir_tous(m)
        lire(m, 'marchand')['voix'] = []
        lire(m, 'marchand')['noms'] = []
        croire(m, 'marchand', 'brune', 'lieu', None, 'vu', salle=None, case=None)
        croire(m, 'marchand', 'marteau', 'lieu', 'brune', 'savoir', salle=None, case=None)
        lire(m, 'marchand')['besoins']['biens'] = 100.0
        self.verifier_recherche(recharger(m), 'marchand', 20)

    def test_recherche_retenue_apres_oubli_des_souvenirs(self):
        from donjon.pnj import _inspecter
        m = scene('auberge-3-570')
        _inspecter(m, 'anselme', 'joss')
        salle = m.objets['anselme']['lieu']
        for _ in range(MEMOIRE_MAX + 1):
            memoriser(m, 'anselme', {'type': 'observation'})
        m = recharger(m)
        self.assertIn(salle, D.appels_vains(m, 'anselme', 'joss'))
        avant = len(m.data['chronique'])
        _inspecter(m, 'anselme', 'joss')
        m = recharger(m)
        self.assertFalse(any(' appelle : « ' in c['texte'] for c in m.data['chronique'][avant:]))


class AnalyseTests(unittest.TestCase):
    def nuit(self, m):
        r = _releve(recharger(m))
        return {'scenario': 'fixture', 'graine': 1, 'heures': 12,
                'releves': [{**copy.deepcopy(r), 'm': minute} for minute in range(0, 130, 5)]}

    def test_ancien_fichier_reste_a_expliquer_sans_diagnostic(self):
        n = self.nuit(scene('auberge-11-500'))
        for r in n['releves']:
            for x in r['pnj'].values():
                x.pop('inactivite')
        c = next(c for c in analyser_nuit(n) if c['code'] == 'fige_presse' and c['pnj'] == 'mireille')
        self.assertEqual(c['niveau'], 'a_expliquer')

    def test_le_faux_fige_est_explique_sans_effacer_le_constat(self):
        n = self.nuit(scene('auberge-11-500'))
        c = next(c for c in analyser_nuit(n) if c['code'] == 'fige_presse' and c['pnj'] == 'mireille')
        self.assertEqual(c['niveau'], 'observation')
        self.assertIn('confiee', c['detail'])

    def test_un_temoin_attendu_manquant_reste_signale(self):
        p = {'conscient': True, 'exclu': False, 'voit': True, 'nature': None, 'entend': None, 'situe': True}
        n = {'scenario': 'fixture', 'graine': 1, 'heures': 12, 'gestes': [
            {'a': 'auteur', 't': 600, 'op': 'prendre', 'objet': 'bien', 'salle': 'lieu',
             'dans_la_salle': ['present'], 'temoins': [], 'entendus': [], 'perception': {'present': p}}]}
        self.assertEqual(analyser_nuit(n)[0]['niveau'], 'a_expliquer')
        p['voit'] = False
        self.assertEqual(analyser_nuit(n)[0]['niveau'], 'observation')
        del n['gestes'][0]['perception']
        self.assertEqual(analyser_nuit(n)[0]['niveau'], 'a_expliquer')


if __name__ == '__main__':
    unittest.main()
