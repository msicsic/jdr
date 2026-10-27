"""Paroles sans effet typé : mots, portée mécanique, sauvegarde et affichage."""
import copy
import unittest

from donjon import agendas
from donjon.narration import AuditIllisible, controler
from donjon.paroles import prevue
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import placer, recharger


class ContenuVideTests(unittest.TestCase):
    def test_questions_reelles_sans_type_restent_dites_et_entendues(self):
        for nom, saisie in [('soir-noir', "il y a quelqu'un ?"),
                            ('echanges', '« Tu sais où est passé le gardien ? »')]:
            for contenu in ([], [('propos', '', '', '')]):
                with self.subTest(nom=nom, contenu=contenu):
                    m = banc(nom)
                    cible = prevue(m, saisie)['personnage']
                    r, sortie, appels = jouer(m, saisie, [
                        parole(saisie, *contenu, personnage=cible), dialogue('Ta question a été entendue.')],
                        [rapport(ligne('mecanique', sources=['conversation_validee']))])
                    self.assertNotIn('Précise ce que tu veux dire', sortie)
                    self.assertIn('Tu dis', sortie)
                    self.assertEqual(len(r.data['paroles_joueur']), 1)
                    self.assertTrue(r.data['paroles_joueur'][0]['auditeurs'])
                    self.assertIn('Ta question a été entendue.', str(r.data['conversation']))
                    self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 0)

    def test_deux_typages_refuses_repartent_des_mots_sans_effet(self):
        for nom, saisie in [('soir-noir', "il y a quelqu'un ?"),
                            ('echanges', '« Tu sais où est passé le gardien ? »')]:
            with self.subTest(nom=nom):
                m = banc(nom)
                cible = prevue(m, saisie)['personnage']
                avant = m.joueur['or']
                faux = parole(saisie, ('ressource', 'présence', '', ''), personnage=cible)
                # La saisie ordinaire ne demande pas la ressource ajoutée par le contenu.
                faux['proposition']['operations_demandees'] = dict.fromkeys(faux['proposition']['operations_demandees'], False)
                r, sortie, appels = jouer(m, saisie, [faux] * 2 +
                    [dialogue('Ta question a été entendue.')],
                    [rapport(ligne('mecanique', sources=['conversation_validee']))],
                    revues=[{'conforme': False, 'motif': 'Ce n’est pas une demande de bien.'}] * 2)
                self.assertNotIn('Précise ce que tu veux dire', sortie)
                self.assertIn('Tu dis', sortie)
                self.assertEqual(len(r.data['paroles_joueur']), 1)
                self.assertEqual(r.joueur['or'], avant)
                validee = next(e['faits']['conversation_validee'] for f, e in appels if f == 'repondre_au_joueur' and 'conversation_validee' in e['faits'])
                self.assertEqual(validee['faits'], [])
                self.assertEqual(sum(f == 'auditer_action' for f, _ in appels), 2)

    def test_prime_et_autre_condition_mecanique_refusees_meme_classees_parole(self):
        for nom, saisie, citation, audit_faux in [
            ('crypte', "Gorm, combien me donnes-tu pour l'anneau ?", "Je te donnerai 10 pièces d'or si tu me rapportes l'anneau.", False),
            ('sous-obstacle-auberge', 'Quel est le prix du repas ?', 'Le repas coûte 73 pièces.', False)]:
            with self.subTest(nom=nom):
                from donjon.monde import nouveau_monde
                m = nouveau_monde() if nom == 'crypte' else banc(nom)
                if nom == 'crypte':
                    m.joueur.update(salle='echoppe', position=[3, 1], orientation='est')
                    placer(m, 'marchand', 'echoppe', [4, 1])
                    m = recharger(m)
                else:
                    m.joueur['orientation'] = 'ouest'
                cible = prevue(m, saisie)['personnage']
                avant = copy.deepcopy((m.data['missions'], agendas.contrats(m), m.joueur['or']))
                faux = ligne('parole', locuteur=cible, citation=citation)
                faux.update(portee_mecanique='sans_fondement', motif='Condition mécanique sans décision du moteur.')
                bonne = 'Je ne peux pas te donner ces conditions.'
                # Le montant monétaire et l'offre incompatibles sont refusés
                # par la garde comptable avant l'audit ordinaire.
                audits = ([rapport(faux)] if audit_faux else []) + [
                    rapport(ligne('parole', locuteur=cible, citation=bonne))]
                r, sortie, appels = jouer(m, saisie, [parole(saisie, personnage=cible),
                    dialogue(f'« {citation} »'), dialogue(f'« {bonne} »')],
                    audits)
                self.assertNotIn(citation, sortie)
                self.assertNotIn(citation, str(r.data.get('paroles_pnj')))
                self.assertIn(bonne, sortie)
                self.assertEqual(r.data['paroles_pnj'][-1]['texte'], bonne)
                self.assertEqual((r.data['missions'], agendas.contrats(r), r.joueur['or']), avant)

    def test_portee_independante_du_verdict_et_rapport_incomplet_refuse(self):
        for verdict in ('parole', 'neutre', 'ambiance'):
            l = ligne(verdict, locuteur='pnj', citation='Le prix est dix pièces.')
            l['portee_mecanique'] = 'etablie'
            r = controler('« Le prix est dix pièces. »', rapport(l), {'interlocuteurs': {'pnj': {}}})
            self.assertTrue(r['obstacles'])
        l.pop('portee_mecanique')
        with self.assertRaises(AuditIllisible):
            controler('Bonjour.', rapport(l), {})
