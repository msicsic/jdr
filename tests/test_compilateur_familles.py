"""G1 c : fidélité avant réparation, prix sans engagement et événements typés."""
import copy
import unittest

from donjon.agendas import contrats
from donjon.dialogues import preparer_conversation, prix_mission
from donjon.improvisation import proposition as improviser, issue, effet
from donjon.monde import nouveau_monde
from donjon.moteur import proposition
from donjon.operations import sequence, etape
from donjon.rendu import regarder, decrire_accords
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_dialogues import conversation
from tests.test_gardes_justes import crypte
from tests.test_repli_et_appel import dialogue
from tests.test_relances_luna import action
from tests.test_tensions import recharger


class FamillesTests(unittest.TestCase):
    def test_consultation_mission_par_action_pure_et_meme_cotation(self):
        m = crypte()
        avant = copy.deepcopy(m.data)
        r, sortie, _ = jouer(m, 'mj quel est le prix annoncé pour cette mission ?',
            [action(proposition('prix', 'anneau_veilleur'))], [])
        self.assertIn('20 pièces', sortie)
        for cle in ('joueur', 'objets', 'engagements', 'minutes', 'jets', 'journal', 'finances_pnj'):
            self.assertEqual(r.data[cle], avant[cle])
        self.assertEqual(recharger(r).data, r.data)

    def test_correction_ne_substitue_pas_un_objet_au_bien_inconnu(self):
        from tests.test_relances_luna import loin_de_la_poutre
        for demande, remplacement in (('pied-de-biche', 'brasero'), ('outil inconnu', 'lanterne')):
            m = loin_de_la_poutre()
            p = proposition('prendre', demande)
            faux = proposition('prendre', remplacement, justification='Le même objet est conservé.')
            r, sortie, appels = jouer(m, 'mj je prends ' + demande, [action(p), action(faux)], [],
                revues=[{'conforme': True, 'motif': ''},
                        {'conforme': False, 'motif': 'Le bien demandé a été remplacé.'}])
            self.assertIn('Tu ne vois rien de tel ici.', sortie)
            self.assertNotIn('Approche-toi', sortie)
            self.assertEqual(r.objets, m.objets)
            candidat = [e['plan']['proposition_non_admise'] for f, e in appels if f == 'auditer_action'][-1]
            self.assertNotIn('justification', candidat)
            self.assertEqual(recharger(r).data, r.data)

    def test_negociation_non_chiffree_explicite_reste_disponible(self):
        from donjon.dialogues import commande_sociale
        m = crypte()
        p = commande_sociale(m, 'negocier Gorm')
        self.assertEqual(p['operation'], 'ameliorer')
        r, _ = preparer_conversation(m, p)
        self.assertEqual(contrats(recharger(r))['anneau_veilleur']['montant'], 22)

    def test_prix_mission_deux_entrees_sans_accord_ni_reservation_apres_recharge(self):
        for operation in ('prix', 'negocier'):
            for accord in (False, True):
                with self.subTest(operation=operation, accord=accord):
                    m = crypte()
                    if accord:
                        m, _ = preparer_conversation(m, conversation('negocier', 24))
                    avant = copy.deepcopy(m.data)
                    p = conversation(operation)
                    r, sortie, _ = jouer(m, 'mj Gorm combien me donnes-tu pour l’anneau ?',
                        [dict(mode='conversation_pnj', texte='', faits=[], proposition=p),
                         dialogue('Le prix annoncé reste disponible.')],
                        [rapport(ligne('mecanique', sources=['conversation_validee']))])
                    attendu = 22 if accord else 20
                    self.assertEqual(contrats(r), contrats(m))
                    self.assertEqual(r.data['finances_pnj'], avant['finances_pnj'])
                    self.assertEqual(r.joueur['or'], m.joueur['or'])
                    self.assertEqual(r.objets, m.objets)
                    self.assertEqual(prix_mission(r, 'anneau_veilleur')['montant'], attendu)
                    self.assertIn(str(attendu), sortie)
                    rr = recharger(r)
                    self.assertEqual(decrire_accords(rr), decrire_accords(m))
                    self.assertEqual(regarder(rr), regarder(r))

    def test_autre_prix_en_vente_question_sans_achat_apres_recharge(self):
        from donjon.rendu import prix, decrire
        for objet in ('crochets', 'marteau'):
            m = crypte()
            o = m.objets[objet]
            # Même contrat de consultation pour deux biens configurés en vente.
            o.update(en_vente=True, vendeur='marchand', prix=9, visible=True)
            from donjon.geometrie import placer
            placer(o, m.joueur['salle'], [1, 1])
            attendu = prix(m, o)
            texte = f'Prix annoncé : {attendu} pièces.'
            avant = copy.deepcopy(m.data)
            r, sortie, appels = jouer(m, f'mj combien coûte {o["nom"]} ?', [action(proposition('prix', objet))], [])
            self.assertIn(texte, sortie)
            self.assertEqual(r.objets, avant['objets'])
            self.assertEqual(r.joueur['or'], m.joueur['or'])
            self.assertEqual(r.data['minutes'], avant['minutes'])
            self.assertEqual(r.data['finances_pnj'], avant['finances_pnj'])
            self.assertEqual(r.joueur, m.joueur)
            self.assertEqual(r.data['journal'], avant['journal'])
            self.assertNotIn('auditer_narration', [f for f, _ in appels])
            rr = recharger(r)
            self.assertEqual(prix(rr, rr.objets[objet]), attendu)
            self.assertEqual(decrire(rr, objet), decrire(r, objet))

    def test_candidat_invalide_etranger_refuse_avant_son_obstacle(self):
        for cible in ('crochets', 'marteau'):
            m = nouveau_monde()
            # Rejeu du défaut : proposition étrangère, puis le vrai geste.
            faux = sequence(etape('eteindre', 'lanterne'), etape('fermer'))
            vrai = sequence(etape('patienter'), etape('deplacer', cible, 'joueur', methode='discret'))
            from donjon.moteur import Moteur
            Moteur(m).executer(Moteur(m).preparer(proposition('aller', 'ouest')))
            avant = copy.deepcopy(m.data)
            r, sortie, appels = jouer(m, f'mj j’attends une occasion pour prendre discrètement {cible}',
                [action(faux), action(vrai)], [],
                revues=[{'conforme': False, 'motif': 'La proposition ne contient ni attente ni vol.'},
                        {'conforme': True, 'motif': ''}])
            retour = [e['faits']['retour_moteur'] for f, e in appels
                      if f == 'repondre_au_joueur' and 'retour_moteur' in e['faits']][0]
            self.assertIn('non conforme', retour['attendu'])
            self.assertNotIn('cible vide', sortie)
            self.assertIn('tenter', sortie)
            self.assertEqual(r.objets, avant['objets'])
            self.assertEqual(r.joueur, avant['joueur'])
            self.assertEqual(recharger(r).data, r.data)

    def test_revue_positive_ne_couvre_pas_evenement_omis(self):
        for requis, effets, libelle in (
            ('son', [effet('son', 'joueur', texte='voix_melodique', valeur=1)], 'notes de ta voix'),
            ('son', [effet('son', 'joueur', texte='corps_rythmique', valeur=1)], 'rythme avec ton corps')):
            m = nouveau_monde()
            omis = improviser('Expression', issue('Un récit cosmétique.'))
            bon = improviser('Expression', issue('Brouillon.', effets))
            revue = {'conforme': True, 'motif': '', 'evenements_requis': [requis]}
            r, sortie, appels = jouer(m, 'mj je produis cet air ou ce rythme',
                [action(omis), action(bon)], [], revues=[revue, revue])
            self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 2)
            self.assertIn(libelle, sortie)
            self.assertEqual(len(r.data['sons']), 1)
            self.assertEqual(r.data['sons'], recharger(r).data['sons'])


if __name__ == '__main__':
    unittest.main()
