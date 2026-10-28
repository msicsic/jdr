"""La commission, la fourniture et sa remise suivent les contrats ordinaires."""
import unittest
from unittest.mock import patch

from donjon import agendas, relations
from donjon.deliberation import retenir_refus
from donjon.echanges import executer, confier
from donjon.esprits import lire, croire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import plan_recours, devis_intermediaire
from tests.support import regarder
from tests.test_proposer_recours import scene as crue
from tests.test_tache_promise_recours import reserve
from tests.test_tensions import placer, recharger


def scene(auberge=False):
    if auberge:
        m, id, cible, _ = reserve()
        via, salle = 'mireille', 'cellier'
    else:
        m, id, cible, via, salle = crue(25), 'brune', 'marchand', 'ilse', 'antichambre'
    placer(m, via, salle, [4, 3] if auberge else [6, 3])
    m.objets['vivres'].update(lieu=cible, proprietaire=cible, portions=8)
    for o, x in m.objets.items():
        if x['type'] == 'nourriture' and o != 'vivres':
            x['portions'] = 0
    for qui in (id, cible, via):
        m.objets[qui]['profil']['pulsions'] = []
        lire(m, qui)['pulsions'] = []
        for autre in (id, cible, via, 'joueur'):
            if qui != autre:
                regarder(m, qui, autre)
    for qui, autre, confiance in ((cible, id, 25), (via, id, 80), (cible, via, 80), (via, cible, 80)):
        lire(m, qui)['relations'][autre] = relations._nouvelle({'confiance': confiance})
    m.data['finances_pnj'][id] = 0
    lire(m, id)['besoins']['faim'] = 95
    percevoir_tous(m)
    croire(m, id, cible, 'attitude:' + via, 'attachement', 'devine', signe='sourit')
    retenir_refus(m, id, cible, 'demander', 'mefiance', objet='vivres')
    direct = {'operation': 'demander', 'cible': cible, 'outil': 'vivres', 'lieu': '', 'condition': ''}
    assert not executer(m, id, direct, [])
    assert any(s['de'] == cible and s['raison'] == 'mefiance' for s in lire(m, id)['refus'])
    return recharger(m), id, cible, via


def attendre(m, decoupe=False):
    from donjon.temps import instant
    from donjon.commandes import analyser
    if not decoupe:
        moteur = Moteur(m)
        return moteur.executer(moteur.preparer(proposition('attendre'))), recharger(m)
    cible = instant(m) + 5 * 600
    texte, n = '', 0
    while instant(m) < cible:
        moteur = Moteur(m)
        texte += moteur.executer(moteur.preparer(analyser(m, 'tourner est' if n % 2 else 'tourner ouest')))
        m = recharger(m)
        n += 1
    return texte, m


class IntermediairesTests(unittest.TestCase):
    def test_bien_durable_livre_par_le_meme_contrat(self):
        m, id, cible, via = scene()
        m.objets['crochets'].update(lieu=cible, proprietaire=cible)
        for qui in (id, cible, via):
            croire(m, qui, 'crochets', 'lieu', cible, 'entendu',
                   salle=m.objets[cible]['lieu'], case=m.objets[cible]['position'])
        c = {'objet': 'crochets', 'remettre': id}
        with patch.object(Monde, 'd20', return_value=20):
            self.assertEqual(confier(m, id, via, c), 'accepte')
            self.assertEqual(m.objets['crochets']['lieu'], cible)
            _, m = attendre(recharger(m))
        self.assertEqual(m.objets['crochets']['lieu'], id)
        self.assertEqual(m.objets['crochets']['proprietaire'], cible)
        from donjon.biens import permis
        self.assertFalse(permis(m, id, 'crochets'))
        self.assertFalse(agendas.en_cours(m, via, condition=c))
        self.assertTrue(any('remet' in f for t in m.data['journal'] for f in t['faits']))

    def test_le_devis_moins_cher_choisit_le_recours(self):
        from donjon.pnj_propositions import rendre_service
        from tests.test_rendre_service import scene as service_scene
        from tests.test_tache_promise_recours import feu
        m, id, cible, _ = service_scene(feu)
        placer(m, 'ilse', 'echoppe', [3, 4])
        regarder(m, id, 'ilse')
        # Tourner les yeux n'enregistre pas encore ce qu'il voit : le devis
        # doit partir de la perception d'Ilse, pas de sa position d'auteur.
        percevoir_tous(m)
        croire(m, id, cible, 'attitude:ilse', 'attachement', 'devine', signe='sourit')
        devis = devis_intermediaire(m, id, 'faim', [])
        self.assertTrue(devis)
        # Même devis, deux coûts de commission : aucun jet dans le choix.
        for cout, operation in ((0, 'confier'), (1000, 'alimenter')):
            copie = recharger(m.copier())
            with patch('donjon.pnj_propositions.devis_intermediaire', return_value=(cout, devis[1], devis[2])):
                plan = plan_recours(copie, id, 'faim', None)
            self.assertEqual(plan[-1]['operation'], operation)
            if operation == 'confier':
                self.assertEqual(lire(copie, id)['recours_services'], [])

    def test_deux_chaines_rechargees_et_meme_laps(self):
        for auberge in (False, True):
            with self.subTest(auberge=auberge):
                m, id, cible, via = scene(auberge)
                # Ni le fournisseur ni un tiers ne nourrit gratuitement le demandeur :
                # ce test vérifie la livraison unique de la commission acceptée.
                from tests.support import sans_souci
                sans_souci(m)
                plan = plan_recours(m, id, 'faim', None)
                self.assertEqual(plan[-1]['operation'], 'confier')
                self.assertEqual(plan[-1]['cible'], via)
                lire(m, id)['intention']['plan'] = plan
                m = recharger(m)
                b = recharger(m.copier())
                with patch.object(Monde, 'd20', return_value=20):
                    texte, m = attendre(m)
                    _, b = attendre(b, True)
                self.assertEqual(m.data['chronique'], b.data['chronique'])
                self.assertEqual(lire(m, id), lire(b, id))
                self.assertLess(lire(m, id)['besoins']['faim'], 95)
                self.assertTrue(relations.se_mefie(m, cible, id))
                self.assertEqual(m.objets['vivres']['portions'], 7)
                s = lire(m, id)['recours_intermediaires'][0]
                self.assertEqual(s['issue'], 'accepte')
                self.assertTrue(s['abouti'])
                self.assertNotEqual(s['livraison'], 'vivres')
                self.assertEqual(m.objets[s['livraison']]['portions'], 0)
                self.assertEqual(m.objets[s['livraison']]['lieu'], via)
                faits = ' '.join(f for t in m.data['journal'] for f in t['faits'])
                self.assertIn('demande', faits)
                self.assertIn('donne une part', faits)
                self.assertTrue(texte)
                self.assertFalse(agendas.en_cours(m, via, actifs=True))

    def test_choix_sans_lecture_privee_et_croyance_necessaire(self):
        m, id, cible, via = scene()
        avant = devis_intermediaire(m, id, 'faim', [])
        for a, b in ((cible, via), (via, id)):
            lire(m, a)['relations'][b] = relations._nouvelle({'confiance': 0, 'rancune': 90})
        self.assertEqual(avant, devis_intermediaire(recharger(m), id, 'faim', []))
        del lire(m, id)['croyances'][cible]['attitude:' + via]
        self.assertIsNone(devis_intermediaire(recharger(m), id, 'faim', []))

    def test_commission_refusee_et_une_tentative_durable(self):
        m, id, cible, via = scene()
        plan = plan_recours(m, id, 'faim', None)
        lire(m, via)['relations'][id] = relations._nouvelle({'confiance': 0})
        with patch.object(Monde, 'd20') as jet:
            self.assertFalse(executer(m, id, plan[-1], []))
            jet.assert_not_called()
        m = recharger(m)
        self.assertEqual(lire(m, id)['recours_intermediaires'][0]['issue'], 'mefiance')
        self.assertFalse(agendas.en_cours(m, via))
        self.assertEqual(m.objets['vivres']['portions'], 8)
        self.assertIsNone(devis_intermediaire(m, id, 'faim', []))
        self.assertTrue(any('(mefiance)' in x['texte'] for x in m.data['chronique']))

    def test_cible_mefiante_echoue_sans_boucle(self):
        m, id, cible, via = scene()
        # Un don libre ne doit pas contourner la commission réellement refusée.
        from tests.support import sans_souci
        sans_souci(m)
        plan = plan_recours(m, id, 'faim', None)
        # La méfiance privée existe déjà à l'acceptation, mais le porteur
        # l'ignore encore : son devis n'a pas le droit de lire ce verdict.
        lire(m, cible)['relations'][via] = relations._nouvelle({'confiance': 0})
        with patch.object(Monde, 'd20', return_value=20):
            self.assertTrue(executer(m, id, plan[-1], []))
            _, m = attendre(recharger(m))
        self.assertEqual(m.objets['vivres']['portions'], 8)
        self.assertFalse(lire(m, id)['recours_intermediaires'][0]['abouti'])
        self.assertIsNone(devis_intermediaire(m, id, 'faim', []))
        self.assertLessEqual(sum('demande une part' in x['texte'] and x['pnj'] == via
                                 for x in m.data['chronique']), 1)

    def test_les_moyens_ordinaires_et_les_attitudes_connues_priment(self):
        m, id, cible, via = scene()
        ordinaire = [{'operation': 'manger', 'cible': 'vivres', 'outil': '', 'lieu': '', 'condition': ''}]
        self.assertIsNone(devis_intermediaire(m, id, 'faim', ordinaire))
        croire(m, id, via, 'attitude:' + id, 'mefiance', 'devine', signe='surveille')
        self.assertIsNone(devis_intermediaire(recharger(m), id, 'faim', []))

    def test_acceptation_sans_remise_et_sans_jet_supplementaire(self):
        m, id, cible, via = scene()
        plan = plan_recours(m, id, 'faim', None)
        with patch.object(Monde, 'd20', return_value=20) as jet:
            self.assertTrue(executer(m, id, plan[-1], []))
        self.assertEqual(jet.call_count, 1)
        m = recharger(m)
        self.assertEqual(m.objets['vivres']['lieu'], cible)
        self.assertEqual(m.objets['vivres']['portions'], 8)
        self.assertEqual(plan_recours(m, id, 'faim', None)[-1]['operation'], 'inspecter')
        self.assertEqual(lire(m, id)['besoins']['faim'], 95)


if __name__ == '__main__':
    unittest.main()
