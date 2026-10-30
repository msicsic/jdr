"""Une créance va au contact et garde sa réponse au-delà des souvenirs bornés."""
import unittest
from pathlib import Path
import gzip
import json

from donjon.biens import (bourse, entrees_creance, reponse_creance_retenue, reclamer_dette,
                          rembourser, solder)
from donjon import deliberation, planification
from donjon.echanges import executer
from donjon.monde import Monde
from donjon.esprits import croire, lire
from donjon.rendu import regarder as rendu
from donjon.scene import scene_percue
from tests.scenarios_contractuels import creer
from tests.support import calme
from tests.test_echanges_suite import ensemble
from tests.test_tensions import placer, recharger, relais, vivre


class ReclamationsRepeteesTests(unittest.TestCase):
    def test_capture_reelle_306_seve_2024_avant_83(self):
        # Capture 306 t=22057 rejouée avec le moteur de base jusqu'à la minute 82.
        chemin = Path(__file__).parent / 'captures/reclamations-315-hameau-2024.json.gz'
        m = Monde(json.loads(gzip.decompress(chemin.read_bytes())))
        self.assertEqual(m.data['minutes'], 82)
        self.assertEqual(len([d for d in m.data['dettes'] if d['a'] == 'seve']), 2)
        x, lx = vivre(self.recharge(m), 16)
        y, ly = self.recharge(m), []
        for _ in range(16):
            y, lignes = vivre(y, 1)
            ly += lignes
        self.assertEqual(x.data, y.data)
        self.assertEqual(lx, ly)
        self.assertFalse(any(d['a'] == 'seve' for d in x.data['dettes']))
        # Les débiteurs solvables rendent : il n'y avait aucun refus dans l'archive.
        demandes = [c for c in x.data['chronique'] if c['pnj'] == 'seve' and c['nature'] == 'compte']
        self.assertEqual(len(demandes), 2)
        # Le contact commun du 313 peut conclure une minute plus tôt. Les
        # deux créances sont réglées au plus tard à l'ancienne borne, dans
        # l'ordre réel des actes ; aucune relance n'est admise ensuite.
        self.assertGreater(demandes[1]['instant'], demandes[0]['instant'])
        self.assertGreaterEqual(demandes[0]['minute'], m.data['minutes'])
        self.assertLessEqual(demandes[-1]['minute'], 84)
        self.recharge(x)

    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        self.assertEqual(scene_percue(m), scene_percue(n))
        return n

    def preparer(self, autre=False, honnete=False, sans_fonds=False):
        if autre:
            m = calme(creer('auberge', 1985, 'fixe'), 'joss', 'lucien', 'mireille', 'odile')
            a, de, objet, salle = 'odile', 'lucien', 'bois_anselme', 'salle_commune'
        else:
            m = calme(relais(), 'marchand', 'brune', 'ilse', 'aubin')
            a, de, objet, salle = 'ilse', 'brune', 'vivres', 'antichambre'
        m.objets[de]['profil']['valeurs']['honnetete'] = 100 if honnete else 0
        if sans_fonds:
            m.data.setdefault('finances_pnj', {})[de] = 0
        rembourser(m, de, a, 2, objet, 'tache')
        ensemble(m, de, a, salle)
        return self.recharge(m), a, de, objet

    def test_deux_scenarios_refus_reel_durable_et_recharge(self):
        for autre in (False, True):
            for sans_fonds in (False, True):
                with self.subTest(autre=autre, sans_fonds=sans_fonds):
                    m, a, de, objet = self.preparer(autre, sans_fonds=sans_fonds)
                    projet = planification.reclamer(m, a)
                    geste = projet[1][-1]
                    self.assertEqual(geste['contenu'], {'type': 'reclamer_dette'})
                    lignes = []
                    self.assertFalse(executer(m, a, geste, lignes))
                    self.assertEqual(m.data['dettes'][0]['montant'], 2)
                    if not sans_fonds:
                        from donjon.relations import envers
                        self.assertEqual(envers(m, a, de)['motifs'][-1]['type'], 'dette_niee')
                        self.assertFalse(any(s['type'] == 'refus' for s in lire(m, a)['memoire']))
                    self.assertEqual(deliberation.refus_retenu(m, a, de, ('reclamer_dette',))['raison'],
                                     'sans_le_sou' if sans_fonds else 'garde')
                    m = self.recharge(m)
                    # Ni le délai ni l'éviction de la mémoire des souvenirs ne réarment la demande.
                    lire(m, a)['memoire'] = []
                    m.data['minutes'] += deliberation.REDEMANDE * 2
                    avant = len(m.data['chronique'])
                    self.assertIsNone(planification.reclamer(m, a))
                    self.assertTrue(executer(m, a, geste, []))  # Ancien plan déjà répondu.
                    solder(m, [])
                    self.assertEqual(len(m.data['chronique']), avant)
                    self.recharge(m)

    def test_debiteur_entendu_par_le_passage_n_est_pas_declare_absent(self):
        from donjon.pnj import pourraient_se_parler
        m, a, de, objet = self.preparer(honnete=True)
        # Même configuration de passage que le rejeu Ilse/Gorm : le débiteur
        # a passé la porte après le dernier regard, sa parole reste audible.
        placer(m, a, 'crypte', (3, 0))
        placer(m, de, 'echoppe', (4, 3))
        from tests.support import regarder
        m.joueur.update(salle='echoppe', position=[3, 3])
        regarder(m, 'joueur', de)
        croire(m, a, de, 'lieu', 'crypte', 'vu', salle='crypte', case=[4, 0])
        self.assertTrue(pourraient_se_parler(m, a, de))
        geste = planification.reclamer(m, a)[1][-1]
        avant = bourse(m, a)
        lignes = []
        self.assertTrue(executer(m, a, geste, lignes))
        self.assertEqual(bourse(m, a), avant + 2)
        self.assertFalse(any(d['montant'] for d in m.data['dettes']))
        self.assertIsNotNone(lire(m, a)['croyances'][de]['lieu']['valeur'])
        self.assertTrue(any('rend' in x for x in lignes))
        self.recharge(m)

    def test_bourse_privee_et_dates_ne_levent_pas_la_reponse(self):
        m, a, de, objet = self.preparer(sans_fonds=True)
        reclamer_dette(m, a, de, [])
        avant = entrees_creance(m, a, de)
        m.data['finances_pnj'][de] = 50  # Caché au créancier.
        c = lire(m, a)['croyances'][de]['lieu']
        croire(m, a, de, 'lieu', c['valeur'], 'vu', salle=c['salle'], case=c['case'])
        self.assertEqual(entrees_creance(m, a, de), avant)
        self.assertTrue(reponse_creance_retenue(self.recharge(m), a, de))
        # L'autorité du débiteur sur son règlement spontané est conservée.
        m.objets[de]['profil']['valeurs']['honnetete'] = 100
        solder(m, [])
        self.assertEqual(m.data['dettes'], [])
        self.recharge(m)

    def test_nouvelle_obligation_et_moyen_appris_autorisent_une_reprise(self):
        m, a, de, objet = self.preparer(sans_fonds=True)
        reclamer_dette(m, a, de, [])
        self.assertTrue(reponse_creance_retenue(m, a, de))
        rembourser(m, de, a, 1, objet, 'part')
        self.assertFalse(reponse_creance_retenue(self.recharge(m), a, de))
        reclamer_dette(m, a, de, [])
        # Un contenu monétaire cru porté par le débiteur constitue un moyen nouveau.
        bourse_objet = objet
        m.objets[bourse_objet]['pieces'] = 4
        croire(m, a, bourse_objet, 'lieu', de, 'essai', salle=m.objets[de]['lieu'], case=None)
        croire(m, a, bourse_objet, 'pieces', 4, 'essai')
        self.assertFalse(reponse_creance_retenue(self.recharge(m), a, de))
        reclamer_dette(m, a, de, [])
        croire(m, a, bourse_objet, 'pieces', 2, 'essai')
        self.assertTrue(reponse_creance_retenue(self.recharge(m), a, de))

    def test_contact_et_reglement_laps_entier_ou_decoupe(self):
        m, a, de, objet = self.preparer(honnete=True)
        salle = m.objets[a]['lieu']
        placer(m, de, salle, (8, 3))
        croire(m, a, de, 'lieu', salle, 'savoir', salle=salle, case=[8, 3])
        projet = planification.reclamer(m, a)
        self.assertEqual(projet[1][-1]['operation'], 'demander')
        # Même dans sa salle, le créancier garde une étape de contact, jamais un plan vide.
        self.assertEqual(projet[1][-1]['cible'], de)
        x, lx = vivre(self.recharge(m), 4)
        y = self.recharge(m)
        ly = []
        for _ in range(4):
            y, lignes = vivre(y, 1)
            ly += lignes
        self.assertEqual(x.data, y.data)
        self.assertEqual(lx, ly)
        self.assertEqual(x.data['dettes'], [])
        self.assertEqual(bourse(x, a), bourse(m, a) + 2)
        self.recharge(x)


if __name__ == '__main__':
    unittest.main()

