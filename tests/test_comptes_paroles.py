"""Lot 180 b : paroles compatibles, offres et polysémie, jusqu'à la recharge."""
import copy
import unittest

from donjon.biens import offres_joueur
from donjon.comptes_narratifs import completer, controler, lire, phrases, nombre
from donjon.narration import consigner
from donjon.monde import ErreurMonde
from donjon.rendu import decrire_comptes
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_comptes_issue import audit
from tests.test_parole_corrections import banc
from tests.test_prime_offre import scene
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger
from tests.support import presentes, regarder


class ComptesParolesTests(unittest.TestCase):
    def test_piece_salle_et_autre_description_apres_recharge(self):
        for m, texte in [(scene(), 'Tu te trouves dans une pièce sans fenêtre.'),
                         (banc('ressources'), 'Tu regardes la pièce autour de toi.')]:
            with self.subTest(texte=texte):
                avant = copy.deepcopy(m.objets)
                r, sortie, _ = jouer(m, 'décris-moi cet endroit', [dialogue(texte)],
                    [rapport(ligne('mecanique', sources=['salle']))])
                self.assertIn(texte, sortie)
                self.assertEqual(r.objets, avant)
                self.assertEqual(recharger(r).data, r.data)
                self.assertIn(texte, str(recharger(r).data['conversation']))

    def test_repliques_reelles_compatibles_sans_relance(self):
        cas = [('comptes', 'marchand', "La part des vivres ne t'a pas été servie ; prends ces pièces.", 2),
               ('comptes', 'brune', 'Je ne te rendrai pas ces pièces.', 0),
               ('ressources', 'aubin', 'Non. Je ne te dois rien.', 0),
               ('ressources', 'aubin', 'Aucune dette entre nous.', 0),
               ('soir-appel', 'aubin', 'Je te rends les deux pièces.', 2)]
        for script, qui, citation, gain in cas:
            with self.subTest(citation=citation):
                m = presentes(banc(script), qui)
                regarder(m, 'joueur', qui)
                regarder(m, qui, 'joueur')
                avant = m.joueur['or']
                mots = 'Rends-moi ce que tu me dois.'
                r, sortie, appels = jouer(m, mots, [
                    parole(mots, ('reclamer', '', '', ''), personnage=qui),
                    dialogue('« ' + citation + ' »')], [audit(citation, [], qui)])
                self.assertIn(citation, sortie)
                self.assertEqual(r.joueur['or'], avant + gain)
                self.assertFalse(any('controle_narratif' in e for _, e in appels))
                rr = recharger(r)
                self.assertEqual(rr.data, r.data)
                self.assertIn(citation, str(rr.data['conversation']))
                self.assertEqual(rr.data['paroles_pnj'][-1]['texte'], citation)
                if qui == 'brune': self.assertIn('Brune te doit 2 pièces', decrire_comptes(rr))

    def test_prime_reelle_et_autre_montant_invente_refuse(self):
        for prime, mot, faux in [(20, 'Vingt', 10), (30, 'Trente', 12)]:
            with self.subTest(prime=prime):
                m = scene()
                for mission in m.data['missions'].values(): mission['prime_base'] = prime
                m = recharger(m)
                texte = f'{mot} pièces, si tu me rapportes l’anneau du veilleur ici.'
                mauvais = str(faux) + texte[len(mot):]
                mots = "Gorm, combien me donnes-tu pour l'anneau ?"
                r, sortie, appels = jouer(m, mots, [parole(mots, personnage='marchand'),
                    dialogue('« ' + mauvais + ' »'), dialogue('« ' + texte + ' »')],
                    [audit(texte, [], 'marchand')])
                self.assertIn(texte, sortie)
                self.assertNotIn(mauvais, sortie)
                self.assertEqual(r.joueur['or'], m.joueur['or'])
                self.assertEqual(offres_joueur(recharger(r))[0]['contrepartie']['montant'], prime)
                self.assertIn(texte, str(recharger(r).data['conversation']))
                faits = next(e['faits'] for _, e in appels if 'conversation_validee' in e.get('faits', {}))
                for phrase in phrases(faits): self.assertIn(phrase, sortie)
                refus = next(e['controle_narratif'] for _, e in appels if 'controle_narratif' in e)
                self.assertIn('comptes.offres', str(refus))
                self.assertNotIn(str(refus), sortie)

    def test_absence_moteur_accordee_et_non_doublee(self):
        for nom in ['Aubin, vieux passeur', 'Éloi, gardien']:
            with self.subTest(nom=nom):
                faits = {'interlocuteurs': {'p': {'nom': nom}}, 'comptes': {'issue': [
                    {'debiteur':'p', 'creancier':'joueur', 'objet':'', 'montant':0, 'etat':'absent'}]},
                    'conversation_validee': {'faits': [f'{nom} ne te doit aucune pièce.']}}
                ancien = faits['conversation_validee']['faits'][0]
                texte = completer(ancien, faits)
                self.assertNotIn(ancien, texte)
                self.assertEqual(texte.count('Aucune dette'), 1)
                self.assertIn("d'" + nom + ', envers', texte)
                self.assertEqual(completer(texte, faits), texte)
                self.assertFalse(controler(texte, faits))

    def test_question_pas_assertion_et_inversion_non_prouvee(self):
        faits = {'interlocuteurs': {'p': {'nom': 'le gardien'}}, 'comptes': {'issue': [
            {'debiteur':'p', 'creancier':'joueur', 'objet':'', 'montant':2, 'etat':'rendu'}]}}
        self.assertEqual(lire('Tu me dois deux pièces ?', faits, 'p'), [])
        bon = completer('« Je te rends deux pièces. »', faits)
        mauvais = completer('« Tu me rends deux pièces. »', faits)
        self.assertFalse(controler(bon, faits))
        self.assertTrue(controler(mauvais, faits))
        for sans_compte in ('Je dois partir.', 'Tu dois te reposer.',
                            'Je connais ce pays.', 'Tu entres dans une pièce.'):
            with self.subTest(texte=sans_compte):
                self.assertEqual(lire(sans_compte, faits, 'p'), [])

    def test_roles_condition_objet_et_montant_de_l_offre(self):
        faits = {'interlocuteurs': {'p': {'nom': 'le gardien'}},
                 'objet:anneau': {'nom': 'anneau'}, 'objet:couteau': {'nom': 'couteau'},
                 'comptes': {'offres': [{'debiteur':'p', 'creancier':'joueur', 'etat':'offre',
                    'condition': {'type':'objet', 'objet':'anneau'},
                    'contrepartie': {'type':'pieces', 'montant':20}}]}}
        bon = '« Vingt pièces, si tu me rapportes l’anneau. »'
        self.assertFalse(controler(completer(bon, faits), faits))
        for faux in (bon.replace('Vingt', 'Dix'), bon.replace('tu me', 'je te'),
                     bon.replace('anneau', 'couteau')):
            with self.subTest(faux=faux):
                self.assertTrue(controler(completer(faux, faits), faits))

    def test_cardinaux_communs_et_signe(self):
        for mots, valeur in [('vingt et un', 21), ('quatre-vingts', 80),
                             ('deux cent quatre-vingts', 280), ('un million', 1_000_000),
                             ('moins vingt', -20), ('-20', -20)]:
            with self.subTest(mots=mots): self.assertEqual(nombre(mots), valeur)

    def test_plusieurs_offres_et_doublon_ne_decalent_pas_leurs_montants(self):
        a = {'debiteur':'p', 'creancier':'joueur', 'etat':'offre',
             'condition': {'type':'objet', 'objet':'anneau'},
             'contrepartie': {'type':'pieces', 'montant':20}}
        b = {**a, 'condition': {'type':'objet', 'objet':'couteau'},
             'contrepartie': {'type':'pieces', 'montant':30}}
        textes = ['Offre de vingt pièces contre un anneau.', 'Offre de trente pièces contre un couteau.']
        faits = {'comptes': {'offres':[a, a, b],
                            'formulations_offres':[textes[0], textes[0], textes[1]]},
                 'objet:anneau': {'nom':'anneau'}, 'objet:couteau': {'nom':'couteau'}}
        rendus = phrases(faits)
        self.assertEqual(len(rendus), 2)
        self.assertIn('20 pièces contre l’anneau'.replace('’', "'"), rendus[0])
        self.assertIn('30 pièces contre le couteau', rendus[1])
        self.assertEqual(completer(rendus[0], faits), ' '.join(rendus))
        self.assertEqual(completer(rendus[0], faits).count('20 pièces'), 1)
        libre = 'Une odeur de résine.\n\nTu prends ton temps.'
        self.assertEqual(completer(libre, {}), libre)

    def test_offre_de_service_preparee_et_affichee_pour_le_joueur(self):
        from donjon.biens import compte, livraisons_dues
        from tests.test_propositions import scene as marche_scene
        from tests.test_part_proposee import marche
        for nom in ('Corvus', 'Alix'):
            with self.subTest(nom=nom):
                m = marche_scene('aubin')
                m.joueur['nom'] = nom
                m.objets['vivres'].update(nom='soupe', aliases=['soupe'])
                condition = {'objet':'vivres', 'servir':'joueur'}
                avant = m.joueur['or']
                r, sortie, appels = marche(m, 'vivres', demande={'type':'tache', 'condition':condition},
                    comptes=[compte('joueur', 'aubin', montant=3, etat='rendu'),
                             compte('aubin', 'joueur', 'vivres', 1)])
                faits = next(e['faits'] for _, e in appels
                             if 'conversation_validee' in e.get('faits', {}))
                for texte in faits['comptes']['formulations_offres']:
                    self.assertIn('pour toi', texte)
                    self.assertNotIn(nom, texte)
                    self.assertIn(texte, sortie)
                self.assertEqual(r.joueur['or'], avant - 3)
                self.assertTrue(livraisons_dues(recharger(r)))
                self.assertEqual(recharger(r).data, r.data)
                self.assertNotIn(nom, r.data['narrations_mj'][-1]['texte'])
