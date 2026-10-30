"""U-M comptes : vrais callbacks web, transactions, consentement et recharge."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon.biens import preter, rembourser, comptes_joueur
from donjon.commandes import DescripteurPublic, geste_local
from donjon.dialogues import (comptes_publics, preparer_direct, parole_compte,
                             preparer_conversation, conversation_compte)
from donjon.emissions import pnj
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur
from donjon.narration import consigner
from donjon.paroles import preparer_parole
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from tests import test_information_publique as information_support
from tests.test_inventaire_public import etat, besace
from tests.test_outils_publics import page
from tests.test_parole_corrections import banc
from tests.test_tensions import recharger
from tests.test_messages_decoupage import vivre


def choix(m, operation, cible=None):
    return next(x for x in comptes_publics(m)['choix']
                if (x['descripteur']['geste'] == 'remettre' if operation == 'restituer' else
                    x['descripteur']['parametres'].get('operation') == operation)
                and (cible is None or x['descripteur']['cible'] == cible))


def emprunt():
    m, objet, autre = besace('remettre')
    for id in (objet, autre):
        m.objets[id]['proprietaire'] = 'marchand'
        preter(m, id, 'joueur')
    return recharger(m), objet, autre


def offre(qui='aubin', prix=2):
    m = banc('ressources')
    objet = 'couteau'
    m.objets[objet].update(lieu=qui, proprietaire=qui)
    for k in ('position', 'position_salle'):
        m.objets[objet].pop(k, None)
    m.data['connus'].append(objet)
    m.data['offres_joueur'] = {'marche_test': {'de': qui, 'statut': 'propose',
        'demande': {'type': 'pieces', 'montant': prix},
        'contrepartie': {'type': 'objet', 'objet': objet}}}
    return recharger(m), objet


class ComptesPublicsTests(unittest.TestCase):
    boucle = information_support.InformationPubliqueTests.boucle

    def vues(self, m):
        return fiche(m), regarder(m), comptes_joueur(m), scene_percue(m), pnj(m)

    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(n.data, json.loads(json.dumps(m.data)))
        self.assertEqual(self.vues(n), self.vues(m))
        return n

    def clic(self, m, x, annuler=False):
        public = etat(m)
        public['sonde_comptes'] = {'choix': public['comptes']['choix'].index(x), 'annuler': annuler}
        r = page(m, public)['comptes']
        self.assertEqual((r['incomplet'], r['clavier'], r['occupe']), (0, 0, 0))
        self.assertEqual(r['envois'], 0 if annuler else 1)
        self.assertTrue(r['ferme_apres_etat'])
        self.assertEqual(r['resume'], x['nom'])
        if not annuler:
            self.assertEqual(r['envoye'], x['descripteur'])
            self.assertEqual(r['clics'], 4)
        return DescripteurPublic(r.get('envoye'))

    def parite_parole(self, m, x):
        from donjon.spatial import installer
        installer(m)
        d = self.clic(m, x)
        avant = copy.deepcopy(m.data)
        p = parole_compte(m, d.contenu)
        with patch.object(Monde, 'd20', return_value=20):
            temoin, rapport = preparer_parole(m, {**p,
                '_intention': f'je dis à {p["personnage"]} : « {p["replique"]} »'})
            with patch('donjon.paroles.analyser', side_effect=AssertionError('Analyse du clic')):
                dossier = preparer_direct(m, d)
        self.assertEqual(m.data, avant)
        self.assertTrue(dossier.confirmation)
        self.assertEqual(dossier.travail.data, temoin.data)
        self.assertEqual(dossier.rapports, [rapport])
        consigner(temoin, dossier.reponse)
        etat(temoin)
        r, lignes, _ = self.boucle(m, [d, 'tenter'])
        self.assertEqual({k: v for k, v in r.data.items() if k != 'conversation'},
                         {k: v for k, v in temoin.data.items() if k != 'conversation'})
        self.assertEqual(self.vues(r), self.vues(temoin))
        self.assertIn(p['replique'], '\n'.join(lignes))
        self.recharge(r)
        # Même compte et mêmes vues après un laps entier ou découpé, avec recharge.
        entier, _ = vivre(r.copier(), [120])
        decoupe, _ = vivre(r.copier(), [40, 80])
        self.recharge(entier); self.recharge(decoupe)
        for k in ('dettes', 'permissions', 'finances_pnj'):
            self.assertEqual(entier.data.get(k), decoupe.data.get(k), k)
        self.assertEqual(entier.joueur['or'], decoupe.joueur['or'])
        self.assertEqual(comptes_joueur(entier), comptes_joueur(decoupe))
        return r, lignes

    def test_cas_reel_et_autre_dette_acceptee_ou_refusee(self):
        for qui, paye in (('aubin', True), ('brune', False)):
            with self.subTest(qui=qui):
                m = banc('ressources')
                rembourser(m, qui, 'joueur', 2, 'vivres', 'part')
                m = self.recharge(m)
                x = choix(m, 'reclamer', qui)
                self.assertIn('2 pièces', x['nom'])
                r, lignes = self.parite_parole(m, x)
                self.assertEqual(r.joueur['or'], m.joueur['or'] + (2 if paye else 0))
                self.assertEqual(bool(r.data['dettes']), not paye)
                self.assertEqual('te doit 2 pièces' in fiche(r), not paye)
                self.assertTrue(pnj(r))

    def test_question_sans_dette_et_question_pouvant_declencher_reglement(self):
        for qui, montant in (('aubin', 0), ('brune', 0), ('aubin', 2)):
            with self.subTest(qui=qui, montant=montant):
                m = banc('ressources')
                if montant:
                    rembourser(m, qui, 'joueur', montant, 'vivres')
                r, _ = self.parite_parole(m, choix(m, 'question', qui))
                self.assertEqual(r.joueur['or'], m.joueur['or'] + montant)
                self.assertFalse(r.data.get('dettes'))

    def test_restitutions_homonymes_memes_plans_typed_et_recharge(self):
        for second in (False, True):
            with self.subTest(second=second):
                m, objet, autre = emprunt()
                if not second:
                    objet, autre = autre, objet
                x = choix(m, 'restituer', objet)
                d = self.clic(m, x)
                with patch.object(Monde, 'd20', return_value=20):
                    plan = Moteur(m).preparer(d)
                    temoin = Moteur(m).preparer(geste_local('remettre', objet, 'marchand'))
                self.assertTrue(plan.confirmation)
                self.assertIn('Restituer', plan.compris)
                self.assertTrue(temoin.confirmation)
                self.assertEqual(plan.effets, temoin.effets)
                self.assertEqual(plan.compris, temoin.compris)
                r, lignes, _ = self.boucle(m, [d, 'tenter'])
                self.assertIn('Tu restitues', '\n'.join(lignes))
                self.assertEqual(r.objets[objet]['lieu'], 'marchand')
                self.assertEqual(r.objets[autre]['lieu'], 'joueur')
                self.assertEqual([p['objet'] for p in r.data['permissions']], [autre])
                self.assertEqual(r.joueur['or'], m.joueur['or'])
                self.recharge(r)

    def test_offres_prix_exact_parite_transaction_et_recharge(self):
        for qui, prix in (('aubin', 2), ('brune', 3)):
            with self.subTest(qui=qui, prix=prix):
                m, objet = offre(qui, prix)
                from donjon.spatial import installer
                installer(m)
                x = choix(m, 'payer', qui)
                d = self.clic(m, x)
                avant = copy.deepcopy(m.data)
                dossier = preparer_direct(m, d)
                self.assertEqual(m.data, avant)
                self.assertTrue(dossier.confirmation)
                self.assertIn(f'{prix} pièces', dossier.compris)
                temoin, rapport = preparer_conversation(m, conversation_compte(m, d.contenu))
                self.assertEqual(dossier.travail.data, temoin.data)
                self.assertEqual(dossier.rapports, [rapport])
                consigner(temoin, dossier.reponse); etat(temoin)
                r, _, _ = self.boucle(m, [d, 'tenter'])
                self.assertEqual({k: v for k, v in r.data.items() if k != 'conversation'},
                                 {k: v for k, v in temoin.data.items() if k != 'conversation'})
                self.assertEqual(r.objets[objet]['lieu'], 'joueur')
                self.assertEqual(r.joueur['or'], m.joueur['or'] - prix)
                self.assertEqual(r.data['offres_joueur']['marche_test']['statut'], 'accepte')
                self.recharge(r)

    def test_annuler_local_et_consentement_sans_transfert(self):
        m = banc('ressources'); rembourser(m, 'aubin', 'joueur', 2, 'vivres')
        cas = [(m, choix(m, 'reclamer', 'aubin'))]
        m, objet, _ = emprunt(); cas.append((m, choix(m, 'restituer', objet)))
        m, _ = offre(); cas.append((m, choix(m, 'payer', 'aubin')))
        for m, x in cas:
            with self.subTest(nom=x['nom']):
                self.clic(m, x, annuler=True)
                d = self.clic(m, x)
                r, _, _ = self.boucle(m, [d, 'annuler'])
                for k in ('joueur', 'objets', 'permissions', 'dettes', 'finances_pnj', 'offres_joueur', 'emissions'):
                    self.assertEqual(r.data.get(k), m.data.get(k), k)
                self.recharge(r)

    def test_projection_sans_comptes_prives_ni_dette_non_apprise(self):
        m = banc('ressources')
        rembourser(m, 'aubin', 'brune', 937, 'vivres')
        rembourser(m, 'aubin', 'joueur', 851, 'vivres', informer=False)
        public = comptes_publics(m)
        self.assertEqual(public['lignes'], comptes_joueur(m))
        self.assertNotIn('937', json.dumps(public))
        self.assertNotIn('851', json.dumps(public))
        for x in public['choix']:
            c = x['descripteur']['parametres']['compte']
            self.assertIn('joueur', (c['debiteur'], c['creancier']))

    def test_injections_refusees_sans_effet_et_attendu(self):
        m = banc('ressources'); rembourser(m, 'aubin', 'joueur', 2, 'vivres')
        d = choix(m, 'reclamer', 'aubin')['descripteur']
        for champ, valeur in (('montant', 3), ('montant', 2.0), ('debiteur', 'brune'), ('creancier', 'brune'), ('objet', 'lanterne')):
            faux = copy.deepcopy(d); faux['parametres']['compte'][champ] = valeur
            avant = copy.deepcopy(m.data)
            with self.subTest(champ=champ, valeur=valeur), self.assertRaises(ErreurMonde) as e:
                preparer_direct(m, DescripteurPublic(faux))
            self.assertTrue(e.exception.attendu)
            self.assertEqual(m.data, avant)
        for m, x in ((emprunt()[0], None), (offre()[0], None)):
            x = choix(m, 'restituer') if m.data.get('permissions') else choix(m, 'payer')
            faux = copy.deepcopy(x['descripteur']); faux['parametres']['compte']['montant' if faux['geste'] == 'remettre' else 'debiteur'] = False
            with self.assertRaises(ErreurMonde):
                if faux['geste'] == 'remettre': Moteur(m).preparer(DescripteurPublic(faux))
                else: preparer_direct(m, DescripteurPublic(faux))

    def test_comptes_changes_entre_choix_et_confirmation(self):
        m = banc('ressources'); rembourser(m, 'aubin', 'joueur', 2, 'vivres')
        d = DescripteurPublic(choix(m, 'reclamer', 'aubin')['descripteur'])
        dossier = preparer_direct(m, d)
        m.data['dettes'][0]['montant'] = 3
        self.assertTrue(dossier.revalider(m).erreur)
        m, objet, _ = emprunt()
        d = DescripteurPublic(choix(m, 'restituer', objet)['descripteur'])
        moteur = Moteur(m); plan = moteur.preparer(d)
        m.data['permissions'] = []
        with self.assertRaises(ErreurMonde): moteur.executer(plan)
        self.assertEqual(m.objets[objet]['lieu'], 'joueur')
        m, objet = offre(); d = DescripteurPublic(choix(m, 'payer')['descripteur'])
        dossier = preparer_direct(m, d)
        m.data['offres_joueur']['marche_test']['demande']['montant'] += 1
        self.assertTrue(dossier.revalider(m).erreur)
        self.assertEqual(m.objets[objet]['lieu'], 'aubin')

    def test_offre_refusee_par_moteur_sans_argent_et_recharge(self):
        m, objet = offre(); m.joueur['or'] = 0
        d = self.clic(m, choix(m, 'payer'))
        r, _, _ = self.boucle(m, [d, 'tenter'])
        self.assertEqual(r.joueur['or'], 0)
        self.assertEqual(r.objets[objet]['lieu'], 'aubin')
        self.assertEqual(r.data['offres_joueur']['marche_test']['statut'], 'pauvre')
        self.recharge(r)

    def test_restitution_ne_devient_pas_une_remise_remuneree(self):
        m, objet, _ = emprunt()
        d = self.clic(m, choix(m, 'restituer', objet))
        avant = copy.deepcopy(m.data)
        with patch('donjon.dialogues.remise_convenue', return_value='accord'):
            with self.assertRaises(ErreurMonde) as e:
                Moteur(m).preparer(d)
        self.assertTrue(e.exception.attendu)
        self.assertEqual(m.data, avant)
