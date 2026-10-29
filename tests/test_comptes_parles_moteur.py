"""G17 : vraie console simulée, état, mots et rendu après sauvegarde."""
import copy
import unittest

from donjon.biens import livraisons_dues
from donjon.comptes_parles import reponse, sceller
from donjon.dialogues import preparer_conversation
from donjon.emissions import pnj
from donjon.monde import ErreurMonde
from donjon.narration import consigner
from donjon.paroles import SCHEMA_PAROLE, preparer_parole
from donjon.rendu import decrire_comptes, fiche
from tests.support import presentes, regarder
from tests.test_audits_attendu import jouer
from tests.test_dialogues import conversation, reponse as conversation_mj
from tests.test_parole_corrections import banc
from tests.test_prime_offre import scene
from tests.test_repli_et_appel import parole
from tests.test_tensions import recharger


class ComptesParlesMoteurTests(unittest.TestCase):
    def assertRecharge(self, m, sortie):
        rr = recharger(m)
        self.assertEqual(rr.data, m.data)
        self.assertEqual(fiche(rr), fiche(m))
        self.assertEqual(decrire_comptes(rr), decrire_comptes(m))
        self.assertEqual(pnj(rr), pnj(m))
        for p in pnj(m):
            if p['acte'] == 'reponse_comptable':
                self.assertIn(p['rendu_public'], sortie)
                self.assertIn(p['texte'], str(rr.data['conversation']))
        return rr

    def test_gorm_et_autre_dette_sans_redaction_ni_audit(self):
        for script, qui in [('comptes', 'marchand'), ('soir-appel', 'aubin')]:
            with self.subTest(qui=qui):
                m = banc(script)
                mots = 'Rends-moi les deux pièces dues.'
                r, sortie, appels = jouer(m, mots, [parole(mots,
                    ('reclamer', '', '', ''), personnage=qui)], [])
                self.assertEqual(r.joueur['or'], m.joueur['or'] + 2)
                self.assertFalse(any(d['de'] == qui for d in r.data['dettes']))
                self.assertEqual(pnj(r)[-1]['texte'], 'Je te rends 2 pièces.')
                self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 1)
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
                self.assertRecharge(r, sortie)

    def test_refus_partiel_et_absence_sans_inventer_un_paiement(self):
        for qui, fonds, gain, attendu in [
            ('brune', None, 0, 'Je refuse de te rembourser. Je te dois encore 2 pièces.'),
            ('marchand', 1, 1, 'Je te dois encore 1 pièce. Je te rends 1 pièce.'),
            ('marchand', 0, 0, "Je n'ai pas de quoi te rembourser davantage. Je te dois encore 2 pièces.")]:
            with self.subTest(qui=qui, fonds=fonds):
                m = presentes(banc('comptes'), qui)
                regarder(m, 'joueur', qui)
                regarder(m, qui, 'joueur')
                if fonds is not None:
                    m.data['finances_pnj'][qui] = fonds
                mots = 'Rends-moi les pièces dues.'
                r, sortie, appels = jouer(recharger(m), mots, [parole(mots,
                    ('reclamer', '', '', ''), personnage=qui)], [])
                self.assertEqual(r.joueur['or'], m.joueur['or'] + gain)
                self.assertEqual(pnj(r)[-1]['texte'], attendu)
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
                self.assertRecharge(r, sortie)

    def test_achat_planche_et_autre_offre_termes_et_livraison(self):
        from donjon.echanges import enqueter
        from tests.test_parts_achetees import antichambre_du_banc
        from tests.test_propositions import scene as marche
        bois = presentes(antichambre_du_banc(), 'aubin')
        enqueter(bois, 'joueur', 'aubin', 'bois')
        soupe = marche('aubin')
        soupe.objets['vivres'].update(nom='soupe', prix_part=2)
        for m, lot, prix in [(bois, 'planches', 3), (soupe, 'vivres', 2)]:
            with self.subTest(lot=lot):
                mots = f'Je te paie {prix} pièces pour une part.'
                p = parole(mots, personnage='aubin')
                p['proposition']['contenu'] = [{'type': 'proposition',
                    'demande': {'type': 'part', 'objet': lot},
                    'contrepartie': {'type': 'pieces', 'montant': prix}}]
                r, sortie, appels = jouer(recharger(m), mots, [p], [])
                self.assertEqual(r.joueur['or'], m.joueur['or'] - prix)
                self.assertIn(f"Tu m'as payé {prix} pièces.", pnj(r)[-1]['texte'])
                self.assertIn(m.objets[lot]['nom'], pnj(r)[-1]['texte'])
                self.assertTrue(livraisons_dues(r) or r.objets[lot]['portions'] < m.objets[lot]['portions'])
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
                self.assertRecharge(r, sortie)

    def test_offres_de_mission_deux_montants_sans_paiement_brouillon(self):
        for prime in [20, 30]:
            with self.subTest(prime=prime):
                m = scene()
                m.data['missions']['anneau_veilleur']['prime_base'] = prime
                mots = "Gorm, combien me donnes-tu pour l'anneau ?"
                r, sortie, appels = jouer(recharger(m), mots,
                    [conversation_mj(conversation(sujet=mots))], [])
                self.assertEqual(r.joueur['or'], m.joueur['or'])
                self.assertEqual(r.data['finances_pnj'], m.data['finances_pnj'])
                self.assertEqual(r.data['engagements']['anneau_veilleur']['statut'], 'propose')
                self.assertIn(f"Je t'offre {prime} pièces contre l'anneau du veilleur.", pnj(r)[-1]['texte'])
                self.assertIn("Aucun paiement n'a eu lieu.", pnj(r)[-1]['texte'])
                self.assertEqual(len(appels), 1)
                self.assertRecharge(r, sortie)

    def test_plusieurs_operations_gardent_leurs_effets_et_les_autres_faits(self):
        m = banc('comptes')
        mots = 'Rends-moi les pièces dues et dis-moi si tu as du bois.'
        p = parole(mots, ('reclamer', '', '', ''), ('ressource', 'bois', '', ''), personnage='marchand')
        prepare, rapport = preparer_parole(m, {**{k: p['proposition'][k] for k in SCHEMA_PAROLE['required']}, '_intention': p['proposition']['replique']})
        autres = [t for t in pnj(prepare)[-1]['evenement']['faits']
                  if t not in rapport['faits_comptables']]
        self.assertTrue(autres)
        r, sortie, _ = jouer(m, mots, [p], [])
        for texte in autres:
            self.assertIn(texte, sortie)
        self.assertEqual(r.joueur['or'], m.joueur['or'] + 2)
        self.assertRecharge(r, sortie)

    def test_propos_libre_residuel_garde_sa_redaction_et_son_audit(self):
        from tests.test_audits_attendu import ligne, rapport
        from tests.test_repli_et_appel import dialogue
        m = banc('comptes')
        mots = 'Rends-moi les pièces dues. Que penses-tu du calme ?'
        libre = 'Le calme me plaît.'
        p = parole(mots, ('reclamer', '', '', ''), ('propos', '', '', ''), personnage='marchand')
        r, sortie, appels = jouer(m, mots, [p, dialogue(f'« {libre} »')],
            [rapport(ligne('parole', locuteur='marchand', citation=libre))])
        self.assertEqual(r.joueur['or'], m.joueur['or'] + 2)
        self.assertIn('Je te rends 2 pièces.', sortie)
        self.assertIn(libre, sortie)
        self.assertTrue(any(f == 'auditer_narration' for f, _ in appels))
        for f, e in appels:
            if f == 'auditer_narration':
                self.assertEqual(list(e['segments'].values()), [f'« {libre} »'])
        self.assertRecharge(r, sortie)

    def test_deux_reglements_cumules_sont_deux_operations(self):
        m = banc('comptes')
        # Deux créances distinctes sont réglées dans la même opération.
        m.data['dettes'].append({**m.data['dettes'][0], 'montant': 3})
        mots = 'Rends-moi les cinq pièces dues.'
        r, sortie, _ = jouer(m, mots, [parole(mots,
            ('reclamer', '', '', ''), personnage='marchand')], [])
        self.assertEqual(r.joueur['or'], m.joueur['or'] + 5)
        self.assertEqual(pnj(r)[-1]['texte'], 'Je te rends 5 pièces.')
        self.assertRecharge(r, sortie)

    def test_deux_achats_ne_perdent_pas_le_second_paiement_cumule(self):
        from donjon.monde import objet
        from donjon.esprits import percevoir_tous
        from tests.test_propositions import scene as marche
        m = marche('aubin')
        for ref, nom in [('galet_test', 'galet poli'), ('ruban_test', 'ruban bleu')]:
            m.objets[ref] = objet(ref, nom, 'objet', 'aubin', prix=2, proprietaire='aubin')
            m.data['connus'].append(ref)
        percevoir_tous(m)
        mots = 'Je te paie deux pièces pour le galet et deux pièces pour le ruban.'
        p = parole(mots, ('demande', 'galet_test', '', '2'),
                   ('demande', 'ruban_test', '', '2'), personnage='aubin')
        r, sortie, _ = jouer(m, mots, [p], [])
        self.assertEqual(r.joueur['or'], m.joueur['or'] - 4)
        for ref in ('galet_test', 'ruban_test'):
            self.assertEqual(r.objets[ref]['lieu'], 'joueur')
            self.assertEqual(r.objets[ref]['proprietaire'], 'joueur')
        self.assertEqual(pnj(r)[-1]['texte'].count("Tu m'as payé 2 pièces."), 2)
        self.assertNotIn("Tu m'as payé 4 pièces.", pnj(r)[-1]['texte'])
        self.assertRecharge(r, sortie)

    def test_sceau_interdit_inversion_et_montant_faux_avant_publication(self):
        m = banc('comptes')
        p = parole('Rends-moi les pièces dues.', ('reclamer', '', '', ''), personnage='marchand')
        travail, rapport = preparer_parole(m, {**{k: p['proposition'][k] for k in SCHEMA_PAROLE['required']}, '_intention': p['proposition']['replique']})
        self.assertEqual(m.joueur['or'], 24)  # La copie n'est pas publiée.
        r = sceller(reponse(rapport), rapport)
        for faux in [r['texte'].replace('Je te rends', 'Tu me rends'),
                     r['texte'].replace('2 pièces', '10 pièces'), r['texte'] * 2,
                     r['texte'] + ' Tu me dois 20 pièces.']:
            with self.subTest(faux=faux):
                avant = copy.deepcopy(travail.data)
                with self.assertRaises(ErreurMonde) as exc:
                    consigner(travail, {**r, 'texte': faux})
                self.assertTrue(exc.exception.attendu)
                self.assertEqual(travail.data, avant)
        consigner(travail, r)
        self.assertEqual(recharger(travail).data, travail.data)

    def test_accepter_refuser_negocier_ne_paie_jamais_la_mission(self):
        for op in ['accepter', 'refuser', 'negocier']:
            with self.subTest(operation=op):
                m, _ = preparer_conversation(scene(), conversation())
                m = recharger(m)
                avant = copy.deepcopy(m.data['finances_pnj'])
                travail, rapport = preparer_conversation(m, conversation(op,
                    montant=100 if op == 'negocier' else 0))
                r = sceller(reponse(rapport), rapport)
                consigner(travail, r)
                self.assertEqual(travail.joueur['or'], m.joueur['or'])
                self.assertEqual(travail.data['finances_pnj'], avant)
                self.assertIn('paiement', r['texte'])
                self.assertEqual(recharger(travail).data, travail.data)
