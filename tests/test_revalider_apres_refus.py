"""358 : la réponse reçue après préparation d'un plan vaut aussi à son exécution."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import deliberation as d, echanges, pnj
from donjon.ecoute import ECOUTE, entendus, rendre
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.planification import _etape
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import MINUTE, ecouler, instant
from tests.test_refus_retenus import fourneau_mort
from tests.test_tensions import recharger


def executer(m, minutes):
    dt = round(minutes * MINUTE)
    ecoulees = ecouler(m, dt)
    lignes = []
    pnj.avancer(m, ecoulees, lignes, dt)
    return lignes


class RevalidationRefusTests(unittest.TestCase):
    def public(self, m):
        return regarder(m), scene_percue(m), rendre(m, entendus(m, 0, ECOUTE))

    def persiste(self, m):
        public = self.public(m)
        n = recharger(m)
        self.assertEqual(n.data, m.data)
        self.assertEqual(self.public(n), public)
        return n

    def capture(self):
        fichier = Path(__file__).parent / 'data/refus-358-hameau-1985-4200.json.gz'
        return self.persiste(Monde(json.loads(gzip.decompress(fichier.read_bytes()))))

    def tache(self, raison='impossible'):
        m = fourneau_mort()
        etape = _etape('engager', 'mathurine', contenu={
            'condition': {'objet': 'fourneau', 'allume': True}, 'prix': 2})
        e = lire(m, 'mireille')
        e['intention'] = {'but': {'type': 'pulsion', 'objet': 'fourneau', 'allume': True},
                          'motif': 'devoir', 'plan': [etape], 'depuis': 0, 'attente': 0}
        e['libre'] = instant(m)
        if raison == 'impossible':
            self.assertFalse(echanges.executer(m, 'mireille', etape, []))
        else:
            d.retenir_refus(m, 'mireille', 'mathurine', 'engager', raison,
                           objet='fourneau', tache='allume', prix=2)
        # La préparation précède la réponse ; ce suffixe est toujours conservé.
        self.assertEqual(e['intention']['plan'], [etape])
        return self.persiste(m), etape

    def test_capture_306_refus_avant_tout_effet_et_sans_effacer_le_passe(self):
        m = self.capture()
        self.assertEqual(instant(m), 4200)
        e = lire(m, 'marchand')
        self.assertEqual(e['intention']['depuis'], 4)
        etape = e['intention']['plan'][0]
        self.assertEqual((etape['operation'], etape['cible']), ('confier', 'mael'))
        refus = d.refus_retenu(m, 'marchand', 'mael', ('confier',), 'seve',
                              mandat=etape['contenu']['mandat'])
        self.assertEqual((refus['minute'], refus['raison']), (6, 'impossible'))
        avant = copy.deepcopy(m.data)
        self.assertIsNotNone(pnj.refus_etape(m, 'marchand', [etape]))
        self.assertEqual(m.data, avant, 'revalider ne perçoit rien et ne produit aucun effet')
        lignes, gestes = [], []
        _, issue, rate = pnj.agir(m, 'marchand', instant(m), lignes, gestes)
        self.assertEqual((issue, rate), (pnj.MANQUE, etape))
        self.assertEqual((lignes, gestes), ([], []))
        self.assertEqual(m.data, avant)
        self.persiste(m)

    def test_capture_306_reprise_complete_recharge_et_laps_decoupe(self):
        m = self.capture()
        n = self.persiste(m.copier())
        passe = copy.deepcopy(m.data['chronique'])
        refus = copy.deepcopy(lire(m, 'marchand')['refus'][-1])
        confier = echanges.confier
        reprises = []

        def verifier(monde, demandeur, auditeur, condition=None, *, mandat=None):
            if (demandeur == 'marchand' and auditeur == 'mael' and mandat == refus['mandat']):
                self.assertIsNone(d.refus_retenu(monde, demandeur, auditeur, ('confier',),
                                                'seve', mandat=mandat))
                reprises.append(instant(monde))
            return confier(monde, demandeur, auditeur, condition, mandat=mandat)

        with patch.object(echanges, 'confier', side_effect=verifier):
            lignes = executer(m, 2)
        decoupe = []
        for _ in range(4):
            decoupe += executer(n, .5)
            n = self.persiste(n)
        m = self.persiste(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(self.public(m), self.public(n))
        self.assertEqual(lignes, decoupe)
        # L'historique acquis jusqu'à 4200 est conservé ; la même réponse
        # n'est pas obtenue de nouveau tant que ses moyens restent identiques.
        anciens = [c for c in m.data['chronique'] if c in passe]
        self.assertTrue(anciens)
        self.assertEqual(anciens, passe[-len(anciens):])  # La chronique est bornée.
        self.assertNotIn(4200, reprises)

    def test_tache_payee_differee_auberge_ne_reparle_pas_pour_la_meme_cause(self):
        m, etape = self.tache()
        m.data['minutes'] += d.REDEMANDE + 1
        m = self.persiste(m)
        retenu = copy.deepcopy(lire(m, 'mireille')['refus'])
        finances = copy.deepcopy(m.data['finances_pnj'])
        self.assertIsNotNone(pnj.refus_etape(m, 'mireille', [etape]))
        lignes = []
        self.assertEqual(pnj.agir(m, 'mireille', instant(m), lignes)[1], pnj.MANQUE)
        self.assertEqual(lignes, [])
        self.assertEqual(lire(m, 'mireille')['refus'], retenu)
        self.assertEqual(m.data['finances_pnj'], finances)
        n = self.persiste(m.copier())
        executer(m, 2)
        for _ in range(4):
            executer(n, .5)
            n = self.persiste(n)
        m = self.persiste(m)
        self.assertEqual(m.data, n.data)
        offres = [c for c in m.data['chronique'] if c['pnj'] == 'mireille'
                  and 'offre 2 pièces à Mathurine' in c['texte']]
        self.assertEqual(len(offres), 1)

    def test_moyen_nouveau_permet_la_reprise_pas_la_seule_date(self):
        m, etape = self.tache()
        self.assertTrue(d.refus_geste(m, 'mireille', etape))
        m.data['minutes'] += 1
        c = lire(m, 'mireille')['croyances']['fourneau']['etat']
        croire(m, 'mireille', 'fourneau', 'etat', c['valeur'], 'vu')
        self.assertTrue(d.refus_geste(self.persiste(m), 'mireille', etape))
        m.objets['bois_anselme']['charges'] = 2
        croire(m, 'mireille', 'bois_anselme', 'lieu', 'chambre_chaude', 'dit:hugues', .7,
               salle='chambre_chaude', case=None)
        croire(m, 'mireille', 'bois_anselme', 'etat', {'disponible': True}, 'dit:hugues', .7)
        m = self.persiste(m)
        self.assertFalse(d.refus_geste(m, 'mireille', etape))
        self.assertIsNone(pnj.refus_etape(m, 'mireille', [etape]))
        # La même tâche est réellement redite : l'autre ignore encore ce bois.
        self.assertFalse(echanges.executer(m, 'mireille', etape, []))
        self.assertEqual(len([c for c in m.data['chronique'] if 'offre 2 pièces à Mathurine'
                              in c['texte']]), 2)
        self.persiste(m)

    def test_autre_mandat_autre_destinataire_et_meilleur_prix_restent_admissibles(self):
        m = self.capture()
        etape = copy.deepcopy(lire(m, 'marchand')['intention']['plan'][0])
        etape['contenu']['mandat']['parametres']['lieu'] = 'antichambre'
        self.assertFalse(d.refus_geste(m, 'marchand', etape))
        etape = copy.deepcopy(lire(m, 'marchand')['intention']['plan'][0])
        etape['cible'] = 'aubin'
        self.assertFalse(d.refus_geste(m, 'marchand', etape))
        m, etape = self.tache('cher')
        self.assertTrue(d.refus_geste(m, 'mireille', etape))
        etape['contenu']['prix'] = 3
        self.assertIsNone(pnj.refus_etape(self.persiste(m), 'mireille', [etape]))

    def test_seul_le_prochain_geste_est_revalide_puis_le_suffixe(self):
        m = self.capture()
        etape = copy.deepcopy(lire(m, 'marchand')['intention']['plan'][0])
        ici = m.objets['marchand']['lieu']
        self.assertIsNotNone(pnj.refus_etape(m, 'marchand', [_etape('aller', lieu=ici), etape]))
        # Un préparatif d'observation peut apprendre le moyen qui lèvera le refus.
        self.assertIsNone(pnj.refus_etape(m, 'marchand', [_etape('inspecter', lieu=ici), etape]))

    def test_enquete_et_demande_de_bien_ne_partagent_pas_le_meme_refus(self):
        from tests.test_refus_retenus import PartImpossibleTests
        m = PartImpossibleTests().ilse_affamee()
        demande = _etape('demander', 'marchand', outil='vivres')
        question = _etape('demander', 'marchand', contenu={'ressource': 'faim'})
        d.retenir_refus(m, 'ilse', 'marchand', 'demander', 'impossible', objet='vivres')
        m = self.persiste(m)
        self.assertTrue(d.refus_geste(m, 'ilse', demande))
        self.assertFalse(d.refus_geste(m, 'ilse', question))
        d.retenir_refus(m, 'ilse', 'marchand', 'enqueter', 'rien', besoin='faim')
        m = self.persiste(m)
        self.assertTrue(d.refus_geste(m, 'ilse', question))
        autre = _etape('demander', 'marchand', contenu={'ressource': 'chaleur'})
        self.assertFalse(d.refus_geste(m, 'ilse', autre))

    def test_achat_meilleur_et_proposition_nouvelle_gardent_le_jugement_commun(self):
        from tests.test_proposer_recours import scene
        m = scene()
        achat = _etape('acheter', 'marchand', outil='vivres', contenu={'prix': 2})
        # Le prêt refusé par humeur ne ferme pas la voie payante.
        self.assertFalse(d.refus_geste(m, 'brune', achat))
        d.retenir_refus(m, 'brune', 'marchand', 'acheter', 'refus', objet='vivres', prix=2)
        m = self.persiste(m)
        self.assertTrue(d.refus_geste(m, 'brune', achat))
        achat['contenu']['prix'] = 3
        self.assertFalse(d.refus_geste(m, 'brune', achat))
        proposition = _etape('proposer', 'marchand', outil='vivres', contenu={
            'demande': {'type': 'part', 'objet': 'vivres'},
            'contrepartie': {'type': 'pieces', 'montant': 2}})
        self.assertTrue(d.refus_geste(m, 'brune', proposition))
        proposition['contenu']['contrepartie']['montant'] = 3
        self.assertFalse(d.refus_geste(m, 'brune', proposition))


if __name__ == '__main__':
    unittest.main()
