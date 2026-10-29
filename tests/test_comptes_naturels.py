"""Dernier contrat 180 c : textes exacts du moteur, pas de comptes du narrateur."""
import copy
import unittest

from donjon.biens import offres_joueur
from donjon.comptes_narratifs import comptable
from tests.support import presentes, regarder
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_comptes_issue import audit
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class ComptesNaturelsTests(unittest.TestCase):
    def test_textes_reels_narrateur_refuses_et_compte_moteur_exact(self):
        cas = [('comptes', 'marchand', 'Gorm te rend les deux pièces.', 'Gorm te rend 2 pièces.', 2),
               ('comptes', 'marchand', 'Gorm te rend deux pièces, sans s’attarder.', 'Gorm te rend 2 pièces.', 2),
               ('comptes', 'brune', 'La dette de deux pièces demeure.', 'Brune te doit encore 2 pièces.', 0),
               ('soir-appel', 'aubin', 'Aubin te rend les deux pièces.', 'Aubin te rend 2 pièces.', 2)]
        for script, qui, faux, moteur, gain in cas:
            with self.subTest(faux=faux):
                m = presentes(banc(script), qui)
                regarder(m, 'joueur', qui)
                regarder(m, qui, 'joueur')
                avant = m.joueur['or']
                mots = 'Rends-moi ce que tu me dois.'
                r, sortie, appels = jouer(m, mots, [
                    parole(mots, ('reclamer', '', '', ''), personnage=qui),
                    dialogue(faux), dialogue('« Entendu. »')], [audit('Entendu.', [], qui)])
                nom = 'Brune' if qui == 'brune' else 'Gorm' if qui == 'marchand' else 'Aubin'
                citation = ('Je refuse de te rembourser. Je te dois encore 2 pièces.' if qui == 'brune'
                            else 'Je te rends 2 pièces.')
                attendu = f'{nom} : « {citation} »'
                self.assertEqual(r.data['narrations_mj'][-1]['texte'], attendu)
                self.assertIn(attendu, sortie)
                self.assertNotIn(faux, sortie)
                self.assertEqual(r.joueur['or'], avant + gain)
                self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
                rr = recharger(r)
                self.assertEqual(rr.data, r.data)
                self.assertIn(attendu, str(rr.data['conversation']))

    def test_presentatif_reel_et_autre_remboursement_apres_recharge(self):
        texte = 'Voilà tes deux pièces : la part des vivres ne t’a pas été servie.'
        for script, qui, moteur in [('comptes', 'marchand', 'Gorm te rend 2 pièces.'),
                                   ('soir-appel', 'aubin', 'Aubin te rend 2 pièces.')]:
            with self.subTest(qui=qui):
                m = banc(script)
                avant = m.joueur['or']
                mots = 'Rends-moi les deux pièces dues.'
                r, sortie, appels = jouer(m, mots, [
                    parole(mots, ('reclamer', '', '', ''), personnage=qui),
                    dialogue('« ' + texte + ' »')], [audit(texte, [], qui)])
                attendu = ('Gorm' if qui == 'marchand' else 'Aubin') + ' : « Je te rends 2 pièces. »'
                self.assertEqual(r.data['narrations_mj'][-1]['texte'], attendu)
                self.assertIn(attendu, sortie)
                self.assertEqual(r.joueur['or'], avant + 2)
                self.assertFalse(any('controle_narratif' in e for _, e in appels))
                self.assertEqual(recharger(r).data, r.data)

    def test_salle_dans_le_complement_du_geste_n_est_pas_un_compte(self):
        phrases = ["Le pied-de-biche n'est pas parmi les objets que tu as ici : tu ne peux pas le prendre dans cette pièce.",
                   'Tu ne peux pas le prendre dans la pièce.',
                   'Tu entres dans une pièce sans fenêtre.']
        for texte in phrases:
            with self.subTest(texte=texte):
                from tests.test_prime_offre import scene
                m = scene()
                avant = copy.deepcopy(m.objets)
                r, sortie, appels = jouer(m, 'que sais-je de cet endroit ?', [dialogue(texte)],
                    [rapport(ligne('mecanique', sources=['salle']))])
                self.assertIn(texte, sortie)
                self.assertEqual(r.objets, avant)
                self.assertFalse(any('controle_narratif' in e for _, e in appels))
                self.assertIn(texte, str(recharger(r).data['conversation']))
                self.assertFalse(comptable(texte, {}))

    def test_achat_et_autre_bien_phrase_unique_naturelle_apres_repli(self):
        from donjon.echanges import enqueter
        from donjon.banc_pnj import creer
        from tests.support import calme
        from tests.test_parts_achetees import antichambre_du_banc
        from tests.test_tensions import placer
        m = presentes(antichambre_du_banc(), 'aubin')
        enqueter(m, 'joueur', 'aubin', 'bois')
        a = presentes(calme(creer('auberge', 1985, 'fixe'), 'joss'), 'joss')
        a.objets['fagots_etable'].update(nom='fagots de bois', aliases=['fagots'], charges=3)
        placer(a, 'joss', 'etable', (5, 3))
        a.joueur.update(salle='etable', position=[5, 2])
        regarder(a, 'joueur', 'joss')
        regarder(a, 'joss', 'joueur')
        from donjon.esprits import percevoir_tous
        percevoir_tous(a)
        for monde, qui, lot, prix, moteur in [
            (m, 'aubin', 'planches', 3, 'Tu paies 3 pièces à Aubin, qui doit encore te remettre une part des planches de bac.'),
            (a, 'joss', 'fagots_etable', 1, 'Tu paies 1 pièce à Joss, qui doit encore te remettre une part des fagots de bois.')]:
            with self.subTest(lot=lot):
                monde = recharger(monde)
                avant = monde.joueur['or']
                mots = 'Je te paie pour une part.'
                p = parole(mots, personnage=qui)
                p['proposition']['contenu'] = [{'type':'proposition', 'demande':{'type':'part', 'objet':lot},
                    'contrepartie':{'type':'pieces', 'montant':prix}}]
                if qui == 'joss': p = parole(mots, ('demande', lot, '', str(prix)), personnage=qui)
                r, sortie, _ = jouer(monde, mots, [p, *[dialogue('Tu paies mille pièces.') for _ in range(3)]], [])
                citation = ("J'accepte cet échange. " if qui == 'aubin' else '')
                citation += f"Tu m'as payé {prix} pièce{'s' if prix > 1 else ''}. Je dois encore te remettre une part des "
                citation += 'planches de bac.' if qui == 'aubin' else 'fagots de bois.'
                if qui == 'aubin':
                    citation += " Tu m'offres 3 pièces contre une part de planches de bac."
                attendu = f"{qui.capitalize()} : « {citation} »"
                self.assertEqual(r.data['narrations_mj'][-1]['texte'], attendu)
                self.assertIn(attendu, sortie)
                self.assertEqual(r.joueur['or'], avant - prix)
                self.assertEqual(recharger(r).data, r.data)
                for interdit in ('Remise effectuée', 'Reste dû', '1 ×', 'engagement enregistré', ',,', 'Offre de'):
                    self.assertNotIn(interdit, r.data['narrations_mj'][-1]['texte'])

    def test_prime_phrase_naturelle_et_montant_source_conserve(self):
        from tests.test_prime_offre import scene
        m = scene()
        citation = 'Vingt pièces, si tu me rapportes l’anneau du veilleur ici.'
        mots = "Gorm, combien me donnes-tu pour l'anneau ?"
        r, sortie, _ = jouer(m, mots, [parole(mots, personnage='marchand'),
            dialogue('« ' + citation + ' »')], [audit(citation, [], 'marchand')])
        moteur = "Gorm le marchand t'offre 20 pièces contre l'anneau du veilleur."
        self.assertIn(moteur, sortie)
        self.assertIn(moteur, r.data['narrations_mj'][-1]['texte'])
        self.assertEqual(offres_joueur(recharger(r))[0]['contrepartie']['montant'], 20)

    def test_provenance_ne_supprime_pas_l_autre_operation_de_la_parole(self):
        m = banc('comptes')
        mots = 'Rends-moi les pièces dues et dis-moi si tu as du bois.'
        p = parole(mots, ('reclamer', '', '', ''), ('ressource', 'bois', '', ''), personnage='marchand')
        r, _, appels = jouer(m, mots, [p, *[dialogue('Gorm te rend deux pièces.') for _ in range(3)]], [])
        from donjon.emissions import pnj
        from donjon.paroles import preparer_parole, SCHEMA_PAROLE
        _, bloc = preparer_parole(m, {**{k: p['proposition'][k] for k in SCHEMA_PAROLE['required']}, '_intention': p['proposition']['replique']})
        autres = [t for t in pnj(r)[-1]['evenement']['faits'] if t not in bloc['faits_comptables']]
        self.assertTrue(autres)
        for texte in autres: self.assertIn(texte, r.data['narrations_mj'][-1]['texte'])
        self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
        self.assertEqual(recharger(r).data, r.data)
